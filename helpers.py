import numpy as np
import os
import PIL.Image
import io
import base64


def convert_to_bytes(file_or_bytes, resize=None):
    """
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    """
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()


def stft(data, window, nfft, shift):
    n = (len(data) - window - 1) // shift
    out1 = np.zeros((nfft, n), dtype=complex)

    for i in range(n):
        tmp1 = data[i * shift: i * shift + window].T
        tmp2 = np.hanning(window)
        tmp3 = tmp1 * tmp2
        tmp = np.fft.fft(tmp3, n=nfft)
        out1[:, i] = tmp
    return out1


class radarSampleHeader:
    def __init__(self):
        self.version = -1
        self.n_rx = -1
        self.n_tx = -1
        self.n_range_bins = -1
        self.n_pulses = -1
        self.timestamp = -1
        self.data = -1

    def getNumberOfValues(self):
        return self.n_range_bins * self.n_rx * self.n_pulses * 2


class radar_sample_reader:
    def __init__(self, filename):
        self.filename = filename
        self.statinfo = os.stat(filename)
        self.file_size = self.statinfo.st_size
        self.offset = 0
        self.f = open(self.filename, "r")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()

    def __iter__(self):
        self.reset()
        return self

    def __next__(self):
        if self.endOfFile():
            raise StopIteration
        return self.getNextSample()

    def endOfFile(self):

        if (self.offset) > self.file_size - 208896:
            return 1
        else:
            return 0

    def getNextSample(self):
        header = self.readFormat()
        if header == 0:
            values = 0
            return header, values
        n_values = header.getNumberOfValues()
        values = np.fromfile(self.filename, dtype=np.int16, count=n_values, offset=self.offset)
        self.offset = self.offset + n_values * np.dtype(np.int16).itemsize

        return header, values

    def reset(self):
        self.offset = 0

    def readFormat(self):
        n_vals = 6
        first_vals = np.fromfile(self.filename, dtype=np.int64, count=n_vals, offset=self.offset)
        self.offset = self.offset + n_vals * np.dtype(np.int64).itemsize
        header = radarSampleHeader()
        if len(first_vals) == 0:
            header = 0
            return header
        header.version = first_vals[0].astype(np.int64)
        header.n_rx = first_vals[1].astype(np.int64)
        header.n_tx = first_vals[2].astype(np.int64)
        header.n_range_bins = first_vals[3].astype(np.int64)
        header.n_pulses = first_vals[4].astype(np.int64)
        header.timestamp = first_vals[5].astype(np.int64)

        return header


import socket
import struct
import numpy as np
import threading


class my_UDP_Receiver(threading.Thread):
    def __init__(self, is_running_event, output_pipe, static_ip='192.168.33.30', adc_ip='192.168.33.180',
                 data_port=4098, n_chirps=255, n_rx=4, n_tx=1, n_samples=256, isComplex=0):
        threading.Thread.__init__(self)
        # Create configuration and data destinations
        self.is_running_event = is_running_event
        self.output_pipe = output_pipe
        self.data_recv = (static_ip, data_port)
        # Create sockets)
        self.data_socket = socket.socket(socket.AF_INET,
                                         socket.SOCK_DGRAM,
                                         0)
        # Bind data socket to fpga
        self.data_socket.bind(self.data_recv)

        self.last_bytes = 0
        self.data = []
        self.packet_count = []
        self.byte_count = []
        self.frame_buff = []
        self.curr_buff = None
        self.last_frame = None
        self.lost_packets = None
        self.BYTES_IN_PACKET = 1456  # ref cli sw dev guide

        self.adc_parameters = {'chirps': n_chirps,  # 32
                               'rx': n_rx,
                               'tx': n_tx,
                               'samples': n_samples,
                               'bytes': 2,
                               'complex': isComplex}

        # DYNAMIC
        self.bytes_per_frame = (self.adc_parameters['chirps'] * self.adc_parameters['rx'] * self.adc_parameters['tx'] *
                                self.adc_parameters['samples'] * self.adc_parameters['bytes'] *
                                self.adc_parameters['complex'])
        self.bytes_in_frame = (self.bytes_per_frame // self.BYTES_IN_PACKET) * self.BYTES_IN_PACKET
        self.packets_in_frame = self.bytes_per_frame / self.BYTES_IN_PACKET
        self.PACKETS_IN_FRAME_CLIPPED = self.bytes_per_frame // self.BYTES_IN_PACKET
        self.uint16_in_packet = self.BYTES_IN_PACKET // 2
        # print('self.uint16_in_packet', self.uint16_in_packet)  # , 728*258 =260624
        self.uint16_in_frame = self.bytes_per_frame // 2
        # print('self.uint16_in_frame', self.uint16_in_frame)  # 261120, 0.19148284313% lose
        self.ret_frame = np.zeros(self.uint16_in_frame, dtype=np.int16)

    def close(self):
        self.data_socket.close()

    def run(self):
        self.read()
        # print("UDP receiver quit!")

    def read(self, timeout=1):
        # Wait for start of next frame
        # ct = 0
        while self.is_running_event.is_set():

            data, addr = self.data_socket.recvfrom(4096)
            byte_count = struct.unpack('>Q', b'\x00\x00' + data[4:10][::-1])[0]
            packet_data = np.frombuffer(data[10:], dtype=np.int16)
            # packet_data = np.frombuffer(data[4:], dtype=np.int16)

            # print(byte_count - last_byte_count)
            # ct += 1
            if byte_count % self.bytes_in_frame == 0:  # byte_count = 23344612928
                # print('byte_count:', byte_count)
                # print('ct:', ct)
                self.ret_frame[0:self.uint16_in_packet] = packet_data
                # self.ret_frame[0:self.uint16_in_packet+3] = packet_data
                break

        # Read in the rest of the frame
        while self.is_running_event.is_set():
            # Read the packet
            data, addr = self.data_socket.recvfrom(4096)
            sequence_number = struct.unpack('<1l', data[:4])[0]
            curr_idx = ((sequence_number - 1) % self.PACKETS_IN_FRAME_CLIPPED)

            if sequence_number % self.PACKETS_IN_FRAME_CLIPPED == 0:
                # if  curr_idx==0:
                self.output_pipe.send(self.ret_frame)
            # print('curr_idx:', curr_idx)  # 0-357
            self.ret_frame[curr_idx * self.uint16_in_packet:(curr_idx + 1) * self.uint16_in_packet] = np.frombuffer(
                data[10:], dtype=np.int16)
        # self.ret_frame[curr_idx * self.uint16_in_packet+3:(curr_idx + 1) * self.uint16_in_packet+6] = np.frombuffer(
        #     data[4:], dtype=np.int16)


class my_UDP_Receiver2(threading.Thread):
    def __init__(self, is_running_event, output_pipe, static_ip='192.168.33.30', adc_ip='192.168.33.180',
                 data_port=4098, n_chirps=255, n_rx=4, n_tx=1, n_samples=256, isComplex=0):
        threading.Thread.__init__(self)
        # Create configuration and data destinations
        self.is_running_event = is_running_event
        self.output_pipe = output_pipe
        self.data_recv = (static_ip, data_port)
        # Create sockets)
        self.data_socket = socket.socket(socket.AF_INET,
                                         socket.SOCK_DGRAM,
                                         socket.IPPROTO_UDP)  # socket.IPPROTO_UDP
        # Bind data socket to fpga
        self.data_socket.bind(self.data_recv)

        self.last_bytes = 0
        self.data = []
        self.packet_count = []
        self.byte_count = []
        self.frame_buff = []
        self.curr_buff = None
        self.last_frame = None
        self.lost_packets = None
        self.BYTES_IN_PACKET = 1456

        self.adc_parameters = {'chirps': n_chirps,  # 32
                               'rx': n_rx,
                               'tx': n_tx,
                               'samples': n_samples,
                               'bytes': 2,
                               'complex': isComplex}

        # DYNAMIC
        self.bytes_per_frame = (self.adc_parameters['chirps'] * self.adc_parameters['rx'] * self.adc_parameters['tx'] *
                                self.adc_parameters['samples'] * self.adc_parameters['bytes'] *
                                self.adc_parameters['complex'])
        self.bytes_in_frame = (self.bytes_per_frame // self.BYTES_IN_PACKET) * self.BYTES_IN_PACKET
        self.packets_in_frame = self.bytes_per_frame / self.BYTES_IN_PACKET
        self.PACKETS_IN_FRAME_CLIPPED = self.bytes_per_frame // self.BYTES_IN_PACKET
        self.uint16_in_packet = self.BYTES_IN_PACKET // 2
        self.uint16_in_frame = self.bytes_per_frame // 2
        # self.ret_frame = np.zeros(self.uint16_in_frame, dtype=np.int16)
        self.ret_frame = np.zeros(self.uint16_in_frame, dtype=np.int16)

    def close(self):
        self.data_socket.close()

    def run(self):
        self.read()
        print("UDP receiver quit!")

    def read(self):
        # Wait for start of next frame
        cnt = 0
        while self.is_running_event.is_set():

            data, addr = self.data_socket.recvfrom(4096)
            cnt += 1
            # print('Data_shape:', np.array(data))
            print('Data_cnt:', cnt)
            # byte_count = struct.unpack('>Q', b'\x00\x00' + data[4:10][::-1])[0]
            byte_count = struct.unpack('>Q', b'\x00\x00' + data[4:10][::-1])[0]
            print('Byte_cnt:', byte_count)
            # packet_data = np.frombuffer(data[10:], dtype=np.uint16)
            packet_data = np.frombuffer(data, dtype=np.int16)

            # print(byte_count - last_byte_count)
            if byte_count % self.bytes_in_frame == 0:
                # self.ret_frame[0:self.uint16_in_packet] = packet_data
                self.ret_frame = packet_data
                break

        # Read in the rest of the frame
        while self.is_running_event.is_set():
            # Read the packet
            data, addr = self.data_socket.recvfrom(4096)
            sequence_number = struct.unpack('<1l', data[:4])[0]
            print('Seq_num: ', sequence_number)
            curr_idx = ((sequence_number - 1) % self.PACKETS_IN_FRAME_CLIPPED)
            print('Curr_idx: ', curr_idx)
            if sequence_number % self.PACKETS_IN_FRAME_CLIPPED == 0:
                # if  curr_idx==0:
                self.output_pipe.send(self.ret_frame)
            print(self.ret_frame.flags)
            self.ret_frame[curr_idx * self.uint16_in_packet:(curr_idx + 1) * self.uint16_in_packet] = np.frombuffer(
                data[10:], dtype=np.uint16)


import numpy as np
import os


class radar_sample_writer:
    def __init__(self, filename):
        self.filename = filename
        self.offset = 0
        self.f = open(self.filename, "wb")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()

    def __iter__(self):
        self.reset()
        return self

    def __next__(self):
        if self.endOfFile():
            raise StopIteration
        return self.getNextSample()

    # def writeNextSample(self, header, data):
    #     header.tofile(self.f)
    #     data.tofile(self.f)

    def writeNextSample(self, data):
        data.tofile(self.f)

    def reset(self):
        self.offset = 0


def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import cv2
    from PIL import Image
    fig.savefig('temp_img.png')
    pil_image = Image.open('temp_img.png')
    opencvImage = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    return opencvImage
