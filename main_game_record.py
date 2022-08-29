import os
import subprocess
import json
import time
from RDC_extract_2243 import RDC_extract_2243
from RDC_to_microDoppler_2243 import RDC_microDoppler
from fun_microDoppler_2243_complex import microDoppler

record_dur = 3
filebase_path = '/home/emre/PycharmProjects/RadarGUI/data/'
fname = 'raw_game'

# Rename filename and duration
now = time.time()
cwd = '/home/emre/Desktop/77ghz/CLI/Release'
json_file = cwd + '/cf.json'
a_file = open(json_file, "r")
json_object = json.load(a_file)
a_file.close()
json_object['DCA1000Config']['captureConfig']['captureStopMode'] = 'duration'
json_object['DCA1000Config']['captureConfig']['durationToCapture_ms'] = record_dur * 1000
json_object['DCA1000Config']['captureConfig']['filePrefix'] = fname
json_object['DCA1000Config']['captureConfig']['fileBasePath'] = filebase_path
a_file = open(json_file, "w")
json.dump(json_object, a_file)
a_file.close()
print('File name and duration preparation: ', time.time() - now)


sudo_password = '190396'
radar_path = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/' \
             'open_radar_initiative-new_receive_test/setup_radar/build'
radar_cmd = './setup_radar'
export_cmd = 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd'
os.environ["LD_LIBRARY_PATH"] = cwd  # + ':' + os.getcwd() # error code 127 when not executed


fpga_cmd = './DCA1000EVM_CLI_Control fpga cf.json'.split()
record_cmd = './DCA1000EVM_CLI_Control record cf.json'.split()
start_cmd = './DCA1000EVM_CLI_Control start_record cf.json'.split()
stop_cmd = './DCA1000EVM_CLI_Control stop_record cf.json'.split()

cmd = subprocess.Popen(start_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
cmd.wait()
time.sleep(record_dur + 0.1)

now = time.time()
print('start error return code: ', cmd.returncode)

pid = subprocess.check_output(['pgrep gnome-terminal'], shell=True)

cmd = subprocess.Popen(['kill', str(pid.decode())[:-1]], cwd=cwd, shell=False,
                       stdin=subprocess.PIPE, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
cmd.wait()
print('exit error return code: ', cmd.returncode)

cmd = subprocess.Popen(stop_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print('Stop time: ', time.time() - now)

# Spectrogram generation
now = time.time()
RDC, params = RDC_extract_2243(filebase_path + fname + '_Raw_0.bin')
print('rdc extract time: ', time.time() - now)
now = time.time()
RDC_microDoppler(RDC, filebase_path + fname + '_Raw_0.png', params)
print('mD gen time: ', time.time() - now)

# Prediction





