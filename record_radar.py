import os
from radar import RadarManager
from datetime import datetime

class_name = 'some_class_name'
record_duration = 3
sudo_password = '190396'
datapath = '/home/emre/PycharmProjects/ASL_game/data/'  # data directory
release = '/home/emre/Desktop/77ghz/CLI/Release'  # radar release directory
setup = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/open_radar_initiative-new_receive_test/setup_radar/build'  # setup folder

# create data folder if doesn't exist
if not os.path.exists(datapath):
    os.mkdir(datapath)

radar_mng = RadarManager(setup, release, sudo_password, datapath)  # radar manager object
radar_mng.radar_init()  # initialize radar

now = datetime.now()
date_time = now.strftime("%Y_%m_%d_%H_%M_%S_")  # today's date and time
filename = os.path.join(datapath, str(datetime) + 'class_' + class_name)  # full filename to be saved

cmd_start = radar_mng.record_radar(filename, duration=record_duration)  # start recording
cmd_start.wait()  # wait for recording to end

radar_mng.execute('stop_record')
radar_mng.execute('kill')

if cmd_start.returncode != 0:  # if radar fails to record
    radar_mng.reset()
    raise Exception('Recording failed.')

radar_mng.generate_spectrogram(filename, cmd_start)









