import sys
from helpers import my_UDP_Receiver, radar_sample_writer, stft
import numpy as np
import threading
from multiprocessing import Pipe
from dca1000 import DCA1000
import time
from datetime import datetime

numADCSamples = 256
numTxAntennas = 1
numRxAntennas = 4
numLoopsPerFrame = 255
NPpF = numTxAntennas * numLoopsPerFrame
SweepTime = 40e-3
sampleFreq = 6.25e6

isComplex = 2  # 1 for real, 2 for complex, real is not added yet
plot_rangedoppler = 0
save_rd_map = 0
rangelim = 4  # in meters
plot_microdoppler = 1
plot_motion = 0

numChirpsPerFrame = numTxAntennas * numLoopsPerFrame

numRangeBins = numADCSamples / 2
numDopplerBins = numLoopsPerFrame

count = 0
if __name__ == '__main__':
    now = datetime.now()
    main_data = '/home/emre/Desktop/77ghz/open_radar/temp/data/my_receiver/'
    date_time = now.strftime(main_data+"%Y_%m_%d_%H_%M_%S")
    filename = str(date_time) + ".bin"

    logger = radar_sample_writer(filename)

    is_running_event = threading.Event()
    output_p, input_p = Pipe(False)
    # sampling_thread = my_UDP_Receiver(is_running_event, input_p, n_chirps=numLoopsPerFrame,
    #                                   n_samples=numADCSamples, isComplex=isComplex)
    is_running_event.set()
    # sampling_thread.start()

    last_timestamp = datetime.now()
    cnt = 0

    try:
        while True:
            # np_raw_frame = output_p.recv()
            np_raw_frame = DCA1000().read(timeout=0.1)
            timestamp = datetime.now()
            # logging_header[-1] = time.mktime(timestamp.timetuple()) * 1e3 + timestamp.microsecond / 1e3
            # logger.writeNextSample(logging_header, np_raw_frame)
            logger.writeNextSample(np_raw_frame)
            # print(timestamp - last_timestamp)
            last_timestamp = timestamp
            cnt += 1

            if cnt == 1:
                # params
                idletime = 100e-6
                adcStartTime = 5e-6
                rampEndTime = 50e-6
                c = 299792458
                slope = 80e12
                fstart = 77e9
                Bw = 4e9
                fstop = fstart + Bw
                fc = (fstart + fstop) / 2
                lamda = c / fc
                Rmax = sampleFreq * c / (2 * slope)
                Tc = idletime + adcStartTime + rampEndTime
                Tf = SweepTime
                dT = SweepTime / NPpF
                prf = 1 / dT
                velmax = lamda / (Tc * 4)
                DFmax = velmax / (c / fc / 2)
                rResol = c / (2 * Bw)
                vResol = lamda / (2 * Tf)
                RNGD2_GRID = np.linspace(0, Rmax, numADCSamples)
                DOPP_GRID = np.linspace(DFmax, -DFmax, numLoopsPerFrame)
                V_GRID = (c / fc / 2) * DOPP_GRID
                md_plot_len = 2  # sec

            if plot_rangedoppler:
                from matplotlib import colors
                import matplotlib.pyplot as plt

                data = np.array(np_raw_frame, dtype=np.int16)
                numChirps = int(np.ceil(len(data) / 2 / numADCSamples / numRxAntennas))

                # zero pad
                zerostopad = int(numADCSamples * numChirps * numRxAntennas * 2 - len(data))
                data = np.concatenate([data, np.zeros((zerostopad,))])
                # print('zeropad:', zerostopad)

                # Organize data per RX
                data = data.reshape(numRxAntennas * 2, -1, order='F')
                data = data[0:4, :] + data[4:8, :] * 1j
                data = data.T
                data = data.reshape(numADCSamples, numChirps, numRxAntennas, order='F')

                rd_frame = data[:, :, 0].T - np.mean(data[:, :, 0], 1)
                rd_frame = np.fft.fftshift(np.fft.fft2(rd_frame.T, axes=(0, 1)), 1)
                maxval = np.max(np.abs(rd_frame))

                if cnt == 1:

                    fig = plt.figure()
                    vmin = 190
                    vmax = None
                    norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
                    im = plt.imshow((20 * np.log10((np.abs(rd_frame) / maxval))).astype(np.uint8), cmap='jet',
                                    norm=norm, aspect="auto", extent=[-velmax, velmax, 0, Rmax])
                    plt.xlabel('Velocity (m/s)')
                    plt.ylabel('Range (m)')
                    plt.title('Range-Doppler map')
                    plt.ylim([rangelim, 0])
                    plt.colorbar()
                    plt.draw()
                    plt.pause(1e-3)
                    if save_rd_map:
                        import cv2
                        from PIL import Image

                        norm_pool = np.zeros((256, 254))
                        fps = int(1 / SweepTime)
                        size = im.get_array().shape[:2]
                        out = cv2.VideoWriter(filename.replace('bin', 'avi'),
                                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                              fps, (size[1], size[0]), isColor=1)
                        final = im.get_array()
                        final[final < vmin] = vmin
                        final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
                                                                None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                        out.write(final)

                else:
                    if not plt.fignum_exists(1):
                        sys.exit('Figure closed, hence stopped.')
                    im.set_data((20 * np.log10((np.abs(rd_frame) / maxval))).astype(np.uint8))
                    plt.draw()
                    plt.pause(1e-3)
                    if save_rd_map:
                        final = im.get_array()
                        final[final < vmin] = vmin
                        final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
                                                                None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                        out.write(final)

            if plot_microdoppler:
                from matplotlib import colors
                import matplotlib.pyplot as plt

                data = np.array(np_raw_frame, dtype=np.int16)
                numChirps = int(np.ceil(len(data) / 2 / numADCSamples / numRxAntennas))

                # zero pad
                zerostopad = int(numADCSamples * numChirps * numRxAntennas * 2 - len(data))
                if zerostopad:
                    data = np.concatenate([data, np.zeros((zerostopad,))])
                # print('zeropad:', zerostopad)

                # Organize data per RX
                data = data.reshape(numRxAntennas * 2, -1, order='F')
                data = data[0:4, :] + data[4:8, :] * 1j
                data = data.T
                data = data.reshape(numADCSamples, numChirps, numRxAntennas, order='F')
                # data = np.fft.fft(data[:, :, 0])

                if cnt == 1:
                    # params
                    rBin = np.arange(15, 18)
                    nfft = 2 ** 9  # 12
                    window = 256
                    noverlap = 200  # 200
                    shift = window - noverlap

                    data_whole = np.zeros((numADCSamples, md_plot_len * NPpF * int(1/SweepTime)),
                                          dtype='complex')
                    data_whole[:, -numChirps:] = data[:, :, 0]
                    print('data_whole part', data_whole[:, -numChirps:].shape)
                    # rp = np.fft.fftshift(np.fft.fft(data_whole), 1)
                    rp = np.fft.fft(data_whole)
                    print(rp.shape)
                    # print('maxdata', np.max(np.abs(data)))
                    y2 = np.sum(rp[rBin, :], 0)
                    # print('max_y2', np.max(np.abs(y2)))
                    # sx = stft(np.expand_dims(y2, -1), window, nfft, shift)
                    sx = stft(y2, window, nfft, shift)
                    # print('max_sx', np.max(np.abs(sx)))
                    # sx2 = np.abs((np.fft.fftshift(sx, 0)))
                    sx2 = np.flip(np.abs((np.fft.fftshift(sx, 1))).T, -1)
                    # sx2 = np.abs(sx).T
                    # print('max_sx2', np.max(sx2))

                    maxval = np.max(sx2)
                    norm = colors.Normalize(vmin=220, vmax=None, clip=True)

                    fig = plt.figure()
                    im = plt.imshow((20 * np.log10(sx2 / maxval)).astype(np.uint8), cmap='jet', norm=norm,
                                    aspect="auto", extent=[-md_plot_len, 0, -prf/2, prf/2])
                    plt.xlabel('Time (sec)')
                    plt.ylabel('Frequency (Hz)')
                    # plt.ylim([-prf/6, prf/6])
                    plt.title('Live Micro-Doppler Spectrogram')
                    plt.colorbar()
                    plt.draw()
                    plt.pause(1e-3)

                else:
                    if not plt.fignum_exists(1):
                        sys.exit('Figure closed, hence stopped.')
                    data_whole[:, : -numChirps] = data_whole[:, numChirps:]
                    data_whole[:, -numChirps:] = data[:, :, 0]
                    # rp = np.fft.fftshift(np.fft.fft(data_whole), 1)
                    rp = np.fft.fft(data_whole)
                    y2 = np.sum(rp[rBin, :], 0)
                    # sx = stft(np.expand_dims(y2, -1), window, nfft, shift)
                    sx = stft(y2, window, nfft, shift)
                    sx2 = np.flip(np.abs((np.fft.fftshift(sx, 1))).T, -1)
                    # sx2 = np.abs(sx)
                    maxval = np.max(sx2)
                    print('frame: ', cnt)
                    print(sx2.shape)
                    # print('max: ', maxval)
                    # print('maxim, ', np.max((20 * np.log10(sx2 / maxval)).astype(np.uint8)))

                    im.set_data((20 * np.log10(sx2 / maxval)).astype(np.uint8))
                    plt.draw()
                    plt.pause(1e-3)

            if plot_motion:
                import matplotlib.pyplot as plt

                data = np.array(np_raw_frame, dtype=np.int16)
                numChirps = int(np.ceil(len(data) / 2 / numADCSamples / numRxAntennas))

                # zero pad
                zerostopad = int(numADCSamples * numChirps * numRxAntennas * 2 - len(data))
                if zerostopad:
                    data = np.concatenate([data, np.zeros((zerostopad,))])
                # print('zeropad:', zerostopad)

                # Organize data per RX
                data = data.reshape(numRxAntennas * 2, -1, order='F')
                data = data[0:4, :] + data[4:8, :] * 1j
                data = data.T
                data = data.reshape(numADCSamples, numChirps, numRxAntennas, order='F')
                # data = np.fft.fft(data[:, :, 0])

                if cnt == 1:

                    mot_whole = np.zeros((md_plot_len * NPpF * int(1 / SweepTime)))
                    mot_whole[-numChirps:] = np.sum(np.abs(data[:, :, 0]), 0)

                    fig = plt.figure()
                    ax = fig.add_subplot(1, 1, 1)
                    mot = ax.plot(np.linspace(-md_plot_len, 0, len(mot_whole)), mot_whole)
                    ax.set_xlabel('Time (sec)')
                    ax.set_ylabel('Amplitude')
                    ax.set_title('Live Motion Graph')
                    ax.grid('both')
                    plt.draw()
                    plt.pause(1e-3)

                else:
                    if not plt.fignum_exists(1):
                        sys.exit('Figure closed, hence stopped.')
                    mot_whole[:-numChirps] = mot_whole[numChirps:]
                    mot_whole[-numChirps:] = np.sum(np.abs(data[:, :, 0]), 0)
                    print('frame: ', cnt)

                    mot[0].set_ydata(mot_whole)
                    ax.set_ylim([0, np.max(mot_whole)+1e5])
                    plt.draw()
                    plt.pause(1e-3)


    except KeyboardInterrupt:
        print('Stopped by keyboard interrupt')
    out.release()





