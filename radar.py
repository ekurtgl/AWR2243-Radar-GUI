import time
import subprocess
import tensorflow as tf
import os
from tensorflow import keras
from keras.models import load_model
from keras.layers import *
from livelossplot import PlotLossesKerasTF
from PIL import Image, ImageOps
from matplotlib import colors
import matplotlib.pyplot as plt
import numpy as np
import warnings
import glob
import json
from radar_utils.RDC_extract_2243 import RDC_extract_2243
from radar_utils.helpers import stft
from radar_utils.prediction import prediction, predict_140
from radar_utils.ioserver import IOServer
from radar_utils.RDC_to_microDoppler_2243 import RDC_microDoppler


class RadarConfig:
    def __init__(self, config_location, stop_mode='duration', duration=None, prefix=None, directory=None):
        self.config_location = config_location
        if any([var is None for var in [stop_mode, duration, prefix, directory]]):
            print('All params not supplied: reading radar config from file')
            self.read_config()
            self.savename = self.directory + self.prefix + '_Raw_0.png'
            return
        self.stop_mode = stop_mode
        self.duration = int(duration)
        self.prefix = prefix
        self.directory = directory
        self.savename = directory + prefix + '_Raw_0.png'
        self.save_config()

    def set_duration(self, duration):
        self.duration = int(duration)
        self.save_config()

    def set_prefix(self, prefix):
        self.prefix = prefix
        self.save_config()

    def set_directory(self, directory):
        self.directory = directory
        self.save_config()

    def read_config(self):
        with open(self.config_location, 'r') as fp:
            config = json.load(fp)['DCA1000Config']['captureConfig']
            self.stop_mode = config['captureStopMode']
            self.duration = int(config['durationToCapture_ms']) / 1000  # read record duration in seconds
            self.prefix = config['filePrefix']
            self.directory = config['fileBasePath']

    def save_config(self):
        prior_config = json.load(open(self.config_location, 'r'))
        prior_config['DCA1000Config']['captureConfig']['captureStopMode'] = self.stop_mode
        prior_config['DCA1000Config']['captureConfig']['durationToCapture_ms'] = int(self.duration * 1000)
        prior_config['DCA1000Config']['captureConfig']['filePrefix'] = self.prefix
        prior_config['DCA1000Config']['captureConfig']['fileBasePath'] = self.directory
        with open(self.config_location, 'w') as fp:
            json.dump(prior_config, fp)


class RadarManager:
    def __init__(self, radar_path, cwd, sudo_password, storage_directory):
        # Defaults to existing radar config in file
        self.config = RadarConfig(config_location=cwd + '/cf.json')
        self.config.set_directory(storage_directory)
        self.cwd = cwd
        self.sudo_password = sudo_password
        self.storage_dir = storage_directory
        self.radar_path = radar_path

        os.environ["LD_LIBRARY_PATH"] = self.cwd

    def radar_init(self):
        # reset and kill existing recording process, if any
        # pid = subprocess.check_output(['pgrep gnome-terminal'], shell=True)
        self.reset()

        # radar init command with sudo privileges
        pwd = subprocess.Popen(['echo', self.sudo_password], cwd=self.radar_path, stdout=subprocess.PIPE)
        pwd.wait()
        cmd = subprocess.Popen(['sudo', '-S', './setup_radar'], cwd=self.radar_path, stdin=pwd.stdout,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # setup radar
        cmd.wait()
        print('setup_radar error return code: ', cmd.stderr.read())
        print('setup_radar error return code: ', cmd.returncode)

        cmd = self.execute('fpga')  # set fpga
        cmd.wait()
        print('fpga error return code: ', cmd.returncode)

        cmd = self.execute('record')  # set record-ready
        cmd.wait()
        print('record error return code: ', cmd.returncode)

        if cmd.returncode == 0:
            print('Radar is ready to go!')
        else:
            raise Exception('Radar setup error!')

    def reset(self):
        print('Resetting radar...')
        os.system("gnome-terminal 'ls'")  # opens a new terminal
        cmd = self.execute('kill')
        cmd.wait()
        print('kill error return code: ', cmd.returncode)
        cmd = self.execute('stop_record')
        cmd.wait()
        print('Reset successful!')

    def execute(self, command):
        cmd_string = \
            ['kill', str(subprocess.check_output(['pgrep gnome-terminal'], shell=True).decode())[:-1]]\
            if command == 'kill' else f'./DCA1000EVM_CLI_Control {command} cf.json'.split()
        # print(cmd_string)
        cmd = subprocess.Popen(cmd_string, cwd=self.cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return cmd

    def record_radar(self, filename, duration=None):
        # Modify config to specific duration
        if duration is not None and duration != self.config.duration:
            self.config.set_duration(duration)

        # Modify filename in config
        if self.config.prefix != filename:
            self.config.set_prefix(filename)

        # Just follows outline from main_game_record.py
        cmd_start = self.execute('start_record')
        # print(cmd.pid)
        time.sleep(0.5)
        # cmd2 = self.execute('xdotool windowminimize $(xdotool getactivewindow)')
        # cmd2 = self.execute('xdotool windowminimize `xdotool search --pid ' + str(cmd.pid) + '`')
        # cmd2 = self.execute('xdotool search "Google Chrome" windowminimize')
        # cmd2 = self.execute('xdotool search --pid ' + str(cmd.pid.__str__()) + ' windowminimize')
        cmd2 = subprocess.Popen('xdotool windowminimize $(xdotool getactivewindow)', cwd=self.cwd, shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # minimize recording window
        # cmd2.wait()
        # print('minimizeerror return code: ', cmd2.stderr.read())
        # cmd_start.wait()
        # print('start_record error return code: ', cmd_start.returncode)
        # time.sleep(duration + 0.1)
        # cmd = self.execute('kill')
        # stop_cmd = self.execute('stop_record')
        # cmd.wait()
        # print('kill error return code: ', cmd.returncode)
        # cmd.wait()
        # print('stop_record error return code: ', cmd.returncode)
        return cmd_start

    def generate_sx2(self, filename):
        RDC, params = RDC_extract_2243(self.storage_dir + filename + '_Raw_0.bin')
        # DC removal
        RDC -= np.expand_dims(np.mean(RDC, 1), 1)  # , (1, RDC.shape[1], 1)
        rBin = np.arange(10, 30)  # 20 30
        nfft = 2 ** 12
        window = 256
        noverlap = 200
        shift = window - noverlap
        y2 = np.sum(RDC[rBin, :], 0)
        sx = stft(y2[:, -1], window, nfft, shift)
        sx2 = np.abs((np.fft.fftshift(sx, 0)))
        return sx2, params

    def plot_spectrogram(self, sx2, params, filename):
        maxval = np.max(sx2)
        norm = colors.Normalize(vmin=-45, vmax=None, clip=True)
        fig = plt.figure(frameon=True)
        im = plt.imshow(20 * np.log10((abs(sx2) / maxval)), cmap='jet', norm=norm, aspect="auto",
                        extent=[0, params['duration'], -params['prf'] / 2, params['prf'] / 2])
        # ax = plt.Axes(fig, [0., 0., 1., 1.])
        plt.xlabel('Time (sec)')
        plt.ylabel('Frequency (Hz)')
        plt.title('Radar Micro-Doppler Spectrogram')
        self.config.savename = self.config.directory + self.config.prefix + '_Raw_0.png'
        # fig.savefig(self.config.savename, transparent=False, dpi=200)  # with axes
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off',
                        labelright='off', labelbottom='off')
        im.get_figure().gca().set_title("")
        plt.savefig(self.config.savename.replace('.', '_im.'), bbox_inches='tight', transparent=True, pad_inches=0)

    def generate_spectrogram(self, filename, cmd_start):
        cmd_start.wait()
        sx2, params = self.generate_sx2(filename)
        self.plot_spectrogram(sx2, params, filename)

    def record_and_plot(self, filename, duration=3):
        cmd_start = self.record_radar(filename, duration=duration)
        # self.generate_spectrogram(filename, cmd_start)  # must wait for start_cmd to end
        return cmd_start

    def predict_sample(self, model_path, size):
        pred = prediction(model_path, size, self.config.savename.replace('.', '_im.'))
        # pred = predict_140(self.config.savename.replace('.', '_im.'))
        # maybe = round(pred[0][0] * 100, 2)
        # you = round(pred[0][1] * 100, 2)
        for i, p in enumerate(pred[0]):
            confidence = round(p * 100, 2)
            print('Class #' + str(i+1) + ' confidence: ' + str(confidence) + '%')
        return pred[0]








