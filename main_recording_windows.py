import json
import os
import shutil
import subprocess
import time
import sys
import signal
import glob
import PySimpleGUI as sg

from fun_microDoppler_2243_complex import microDoppler
from helpers import convert_to_bytes
from datetime import datetime
from pynput.keyboard import Key, Controller

# custom parameters/paths depending on the local computer
data_path = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\data\\'
# data_path = 'D:\\Gallaudet_data\\'
kinect_path = 'C:\\Users\\emrek\\Desktop\\Technical\\ffmpeg\\bin\\ffmpeg.exe -f dshow -rtbufsize 2048M -i video="Kinect V2 Video Sensor"'
kinect_path_xef = '"C:\\Program Files\\Microsoft SDKs\\Kinect\\v2.0_1409\\Tools\\KinectStudio\\KSUtil.exe"'
sudo_password = '190396'
cwd = data_path
radar_path = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/' \
             'open_radar_initiative-new_receive_test/setup_radar/build'
leap_main_path = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\'
leap_main_path2 = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\main_leap_exe\\dist\\main_leap\\main_leap.exe'
orbbec_main_path = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\orbbec_main_exe\\dist\\orbbec_opencv_v4\\orbbec_opencv_v4.exe'
orbbec_main_path2 = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\'
webcam_main_path = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\webcam_record_exe\\dist\\webcam_record\\\webcam_record.exe'
kinectron_main_path = 'C:\\Kinect-server-0.3.7\\kinectron-server.exe'
kinectron_save_path = 'C:\\Users\\emrek\\kinectron-recordings\\'
lidar_path = 'C:\\Users\\emrek\\PycharmProjects\\RadarGui\\lidar_record_exe\\dist\\lidar_record_v2\\lidar_record_v2.exe'

radar_fps = 25

keyboard = Controller()
radar_cmd = './setup_radar'
setup_leap = 'sudo leapd'.split()

export_cmd = 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd'
os.environ["LD_LIBRARY_PATH"] = cwd  # + ':' + os.getcwd() # error code 127 when not executed

dca = './DCA1000EVM_CLI_Control'

fpga_cmd = './DCA1000EVM_CLI_Control fpga cf.json'.split()
record_cmd = './DCA1000EVM_CLI_Control record cf.json'.split()
start_cmd = './DCA1000EVM_CLI_Control start_record cf.json'.split()
stop_cmd = './DCA1000EVM_CLI_Control stop_record cf.json'.split()

class_fname = 'presentations\\motions_140_sign_5_set_v2.txt'
class_fname = 'presentations\\motions_sequential_v2.txt'
# class_fname = 'presentations\\motions_sentences.txt'
with open(class_fname) as f:
    # lines = f.readlines()  # ignore \n
    lines = f.read().splitlines()

sg.theme("DarkTeal2")

layout = [[sg.Text('Data Recording GUI', size=(50, 2), font=('courier', 20))],
          [sg.Text('Sensors List:', size=(15, 2), font=('courier', 12)),
           sg.Checkbox('77 Front', default=False, key="77_front_check", size=(8, 10), font=('courier', 12)),
           sg.Checkbox('Orbbec', default=False, key="orbbec_check", size=(6, 10), font=('courier', 12)),
           sg.Checkbox('Leap Motion', default=False, key="leap_motion_check", size=(11, 10), font=('courier', 12)),
           sg.Checkbox('Kinect', default=False, key="kinect_check", size=(6, 10), font=('courier', 12)),
           sg.Checkbox('Webcam', default=False, key="webcam_check", size=(6, 10), font=('courier', 12)),
           sg.Checkbox('Kinectron', default=False, key="kinectron_check", size=(9, 10), font=('courier', 12)),
           sg.Checkbox('Lidar', default=False, key="lidar_check", size=(5, 10), font=('courier', 12))],
          [sg.Text('Subject:', size=(8, 2), font=('courier', 12)),
           sg.InputText(size=(10, 5), key='subject', font=('courier', 12)),
           sg.VSep(),
           sg.Text('Class:', size=(7, 2), font=('courier', 12)),
           sg.Combo(values=lines, default_value='TEST', key='class_list', size=(30, 10), font=('courier', 12)),
           sg.VSep(),
           sg.Text('Experiment:', size=(11, 2), font=('courier', 12)),
           sg.Combo(values=['0', '1', '2', '3', '4'], default_value='0', key='exp_list', size=(5, 12),
                    font=('courier', 12)),
           sg.VSep(),
           sg.Text('Duration (sec):', size=(15, 2), font=('courier', 12)),
           sg.InputText(size=(10, 5), key='duration', font=('courier', 12))],
          [sg.Image('data/md.png', key='-IMAGE-', size=(500, 300)),
           sg.VSep(),
           sg.Text('  TIME:', size=(150, 15), key='time', font=('courier', 20))],
          # [sg.Button('Setup Radar', button_color=('white', 'black'), size=(18, 2), font=('courier', 12)),
          #  sg.Text('', key='setup_text', font=('courier', 12)),
          #  sg.Button('Setup Leap Motion', button_color=('white', 'black'), size=(18, 2), font=('courier', 12))]],
          [sg.Button('1. Start Recording', button_color=('white', 'green'), size=(18, 2), font=('courier', 12)),
           sg.Text('                               ', key='start_text', font=('courier', 12))],
          # sg.VSep(),
          # sg.Button('2. Stop Recording', button_color=('white', 'red'), size=(18, 2), font=('courier', 12)),
          # sg.Text('                             ', key='stop_text', font=('courier', 12))],
          [sg.Button('3. Micro-Doppler Signature', button_color=('white', 'blue'), size=(18, 2), font=('courier', 12)),
           sg.Text('                               ', key='md_text', font=('courier', 12)),
           sg.VSep(),
           sg.Exit(button_color=('white', 'black'), size=(18, 2), font=('courier', 12))]]

window = sg.Window('Radar GUI', size=(1300, 800)).Layout(layout)

while True:  # Event Loop
    event, values = window.Read()
    if event in (None, 'Exit'):
        break

    if event == 'Setup Radar':
        window['md_text'].update('                               ')
        window['stop_text'].update('                             ')
        window['start_text'].update('                               ')

        # std = subprocess.run(radar_cmd, cwd=radar_path, shell=True, stdin=subprocess.PIPE,  # check=True,
        #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # print('setup_radar: ', std.stderr)

        pwd = subprocess.Popen(['echo', sudo_password], cwd=radar_path, stdout=subprocess.PIPE)
        pwd.wait()
        print('sudopass: ', pwd.stdout.read())

        cmd = subprocess.Popen(['sudo', '-S'] + [radar_cmd], cwd=radar_path, stdin=pwd.stdout,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        print('setup_radar error return code: ', cmd.stderr.read())

        cmd = subprocess.Popen(fpga_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        cmd.wait()
        print('fpga error return code: ', cmd.returncode)
        print('fpga error2: ', cmd.stderr.read())
        print('fpga stdout: ', cmd.stdout.read())

        cmd = subprocess.Popen(record_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        cmd.wait()
        # cmd.stdin.write("record cf.json")
        # cmd.wait()

        print('record error return code: ', cmd.returncode)
        print('record error2: ', cmd.stderr.read())
        print('record stdout: ', cmd.stdout.read())

        if cmd.returncode == 0:
            window['setup_text'].update('Radar is ready to go!')
        else:
            window['setup_text'].update('Radar is set already!')

    elif event == 'Setup Leap Motion':
        pwd = subprocess.Popen(['echo', sudo_password], cwd=radar_path, stdout=subprocess.PIPE)
        pwd.wait()

        cmd_leap = subprocess.Popen(['sudo', '-S'] + setup_leap, cwd=cwd, stdin=pwd.stdout,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    elif event == '1. Start Recording':
        window['-IMAGE-'].update('data/md.png', size=(500, 300))
        window['md_text'].update('                               ')
        # window['stop_text'].update('                             ')
        window['start_text'].update('Go!                            ')
        window['time'].update('TIME')
        # window['setup_text'].update('                               ')
        # _, values = window.read()

        print('duration: ', values['duration'])
        data_class = values['class_list'].split()[0]
        now = datetime.now()
        date_time = now.strftime("%Y_%m_%d_%H_%M_%S_")
        fname = date_time + 'subj' + values['subject'] + '_Exp' + values['exp_list'] + '_class' + data_class
        # filename = os.path.join(r'C:\Users', data_path) + fname
        filename = data_path + fname

        # first open mmwave studio, then kinectron, then gui
        if values['kinect_check']:
            # kinect_cmd = kinect_path + ' -t ' + values['duration'] + ' "' + filename + '.mp4"'
            # os.popen(kinect_cmd)
            kinect_cmd2 = kinect_path_xef + ' /record ' + filename + '.xef ' + values['duration'] +\
                          ' -stream color depth ir body'
            #' "/stream color depth ir body"'
            #1> camlog2.txt 2>&1
            print(kinect_cmd2)
            cmd4kinect = subprocess.Popen(kinect_cmd2, cwd=cwd, shell=True, stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # cmd4kinect.wait()
            # print(cmd4kinect.stderr.read())
            print('kinect recording ...')
            # if not values['kinectron_check']:
            #     time.sleep(2.5)

        if values['lidar_check']:
            lidar_cmd = lidar_path + ' --filename ' + filename + ' --duration ' + values['duration']
            print(lidar_cmd)
            cmd4webcam = subprocess.Popen(lidar_cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print('lidar recording ...')

        if values['kinectron_check']:
            # highlight start button in start recording
            keyboard.press(Key.alt_l)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            keyboard.release(Key.alt_l)
            time.sleep(0.1)
            keyboard.press(Key.space)
            keyboard.release(Key.space)

        if values['orbbec_check']:
            orbbec_cmd = orbbec_main_path + ' --filename ' + filename + ' --duration ' + values['duration']
            print(orbbec_cmd)
            # cmd4orbbec = subprocess.Popen('start ' + orbbec_cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE,
            #                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # os.system(orbbec_cmd)  # works
            os.popen(orbbec_cmd)
            # os.execv(orbbec_main_path, [filename, values['duration']])
            # os.spawnl(os.P_NOWAIT, orbbec_cmd)
            # , executable=orbbec_main_path, close_fds=False
            # cmd4orbbec = subprocess.Popen(orbbec_cmd.split(), cwd=cwd, shell=False, stdin=subprocess.PIPE,
            #                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
            # cmd4orbbec = subprocess.Popen(orbbec_cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE,
            #                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
            # orbbec_cmd2 = 'python2 ' + orbbec_main_path2 + 'orbbec_opencv_v4.py --filename ' + filename + \
            #               ' --duration ' + values['duration']
            # cmd4orbbec = subprocess.Popen(orbbec_cmd2, cwd=cwd, shell=True, stdin=subprocess.PIPE,
            #                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # cmd4orbbec.wait()
            print('orbbec recording ...')
            # cmd4orbbec.wait()
            # output = cmd4orbbec.stderr.read()
            # print(output)
            # time.sleep(1)

        if values['webcam_check']:
            webcam_cmd = webcam_main_path + ' --filename ' + filename + ' --duration ' + values['duration']
            print(webcam_cmd)
            # cmd4webcam = subprocess.Popen('start ' + webcam_cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE,
            #                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cmd4webcam = subprocess.Popen(webcam_cmd, cwd=cwd, shell=True, stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print('webcam recording ...')

        if values['77_front_check']:
            '''json_file = cwd + '/cf.json'
            a_file = open(json_file, "r")
            json_object = json.load(a_file)
            # print(json_object)
            a_file.close()
            # print(json_object['DCA1000Config']['captureConfig']['framesToCapture'])
            # json_object['DCA1000Config']['captureConfig']['framesToCapture'] = radar_fps * int(values['duration'])
            # json_object['DCA1000Config']['captureConfig']['captureStopMode'] = 'frames'
            json_object['DCA1000Config']['captureConfig']['captureStopMode'] = 'duration'
            json_object['DCA1000Config']['captureConfig']['durationToCapture_ms'] = int(values['duration']) * 1000
            json_object['DCA1000Config']['captureConfig']['filePrefix'] = fname
            a_file = open(json_file, "w")
            json.dump(json_object, a_file)
            a_file.close()
            cmd = subprocess.Popen(start_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE,  # text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cmd.wait()
            # cmd.stdin.write("start_record cf.json")
            # cmd.wait()

            print('start error return code: ', cmd.returncode)
            print('start error2: ', cmd.stderr.read())
            print('start stdout: ', cmd.stdout.read())'''

            # go to mmwave studio and type the filename (highlight it beforehand)
            num_nonradar_sensors = values['kinectron_check']  # values['kinect_check'] --> uncomment if you use subprocess for kinect or orbbec
            print('num_nonradar_sensors:', num_nonradar_sensors)
            keyboard.press(Key.alt_l)
            for i in range(num_nonradar_sensors + 1):
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                time.sleep(0.1)
            keyboard.release(Key.alt_l)
            time.sleep(0.1)
            keyboard.type(filename + '.bin')

            # go to DCA ARM button
            keyboard.press(Key.shift_l)
            for i in range(4):
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                time.sleep(0.1)
            keyboard.release(Key.shift_l)
            time.sleep(0.1)

            # press DCA ARM and Trigger Frame buttons
            for i in range(2):
                keyboard.press(Key.enter)
                time.sleep(0.1)
                keyboard.release(Key.enter)
                time.sleep(0.1)

            # go back to filename section
            for i in range(2):
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                time.sleep(0.1)

            print('front radar recording ...')

        if values['leap_motion_check']:
            # leap_cmd = 'python2 ' + leap_main_path + 'main_leap.py --filename ' + filename + '.data' + \
            #            ' --duration ' + values['duration']
            leap_cmd2 = leap_main_path2 + ' --filename ' + filename + '.data' + ' --duration ' + values['duration']
            cmd4leap = subprocess.Popen('start ' + leap_cmd2, cwd=cwd, shell=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
            print('leap recording ...')

        left_time = int(values['duration'])

        for i in range(left_time):
            window['time'].update('  TIME: ' + str(left_time))
            window.refresh()
            time.sleep(1)
            left_time -= 1

        # stop recording of kinectron
        if values['kinectron_check']:
            if values['leap_motion_check']:
                keyboard.press(Key.alt_l)
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                keyboard.release(Key.alt_l)
                time.sleep(0.1)
            if values['77_front_check']:
                keyboard.press(Key.alt_l)
                keyboard.press(Key.tab)
                keyboard.release(Key.tab)
                keyboard.release(Key.alt_l)
                time.sleep(0.3)

            # 1 for stopping, 5 for filename approval
            keyboard.press(Key.space)
            keyboard.release(Key.space)
            time.sleep(1)
            for i in range(5):
                keyboard.press(Key.space)
                keyboard.release(Key.space)
                time.sleep(0.5)

            # find kinectron files
            kinectron_files = []
            extensions = ['*.webm', '*.json']
            for e in extensions:
                temp_files = glob.glob(kinectron_save_path + e)
                print(temp_files)
                if isinstance(temp_files, list):
                    for t in temp_files:
                        kinectron_files.append(t)
                else:  # if single file
                    kinectron_files.append(temp_files)

            # move files to the saving location
            for f in kinectron_files:
                print(f)
                idx = [pos for pos, char in enumerate(f) if char == '\\']
                dst = filename + '_' + f[idx[-1] + 1:]
                print(dst)
                shutil.move(f, dst)
                # os.remove(f)
                # os.replace(f, dst)

        # go back to gui
        if values['77_front_check'] or values['kinectron_check']:
            if values['leap_motion_check']:
                time.sleep(3)
            else:
                time.sleep(0.5)
            keyboard.press(Key.alt_l)
            keyboard.press(Key.tab)
            if values['77_front_check'] and values['kinectron_check']:
                keyboard.release(Key.tab)
                time.sleep(0.1)
                keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            keyboard.release(Key.alt_l)

        # if values['leap_motion_check']:
        #     cmd4leap.wait()
        #     print(cmd4leap.stdout.read().decode())
        # if values['kinect_check']:
        #     time.sleep(1)
        #     subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=cmd4kinect.pid))
        # window['time'].update('  Finished!')
        saved_files = 'Recorded files: \n'
        file_sizes = ''
        search_path = filename + '*'
        idx = [pos for pos, char in enumerate(filename) if char == '\\']
        print(search_path)
        cnt = 1
        for file in glob.glob(filename + '*'):

            if round(os.path.getsize(file)/1e6, 1) > 1:
                saved_files += str(cnt) + '. ' + file[idx[-1]+1:] + '  -->  ' + str(round(os.path.getsize(file)/1e6, 1)) + \
                               ' mb' + '\n'
            else:
                saved_files += str(cnt) + '. ' + file[idx[-1] + 1:] + '  -->  ' + str(
                    round(os.path.getsize(file) / 1e3, 1)) + \
                               ' kb' + '\n'
            cnt += 1
        window['time'].update(saved_files, font=10)
        window.refresh()

    elif event == '2. Stop Recording':
        window['stop_text'].update('Stopping...                        ')
        window['md_text'].update('                               ')
        window['stop_text'].update('Done!                        ')
        window['start_text'].update('                               ')
        # window['setup_text'].update('                               ')

        # cmd = subprocess.Popen(['sudo', '-S', 'kill', '`ps -e | grep -i gnome-terminal`'], cwd=cwd, shell=False,
        #                        stdin=pwd.stdout, text=True,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        # cmd.wait()
        # time.sleep(2)
        try:
            pid = subprocess.check_output(['pgrep gnome-terminal'], shell=True)  # , check=True)
            print('pid stdoutstr: ' + str(pid.decode())[:-1] + '-')

            cmd = subprocess.Popen(['kill', str(pid.decode())[:-1]], cwd=cwd, shell=False,
                                   stdin=subprocess.PIPE, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
            cmd.wait()
            print('exit error return code: ', cmd.returncode)
            print('exit error2: ', cmd.stderr.read())
            print('exit stdout: ', cmd.stdout.read())

        except:
            print('No open command windows!')

        cmd = subprocess.Popen(stop_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        cmd.wait()
        # cmd.stdin.write("stop_record cf.json")
        # cmd.wait()
        print('stop error return code: ', cmd.returncode)
        print('stop error2: ', cmd.stderr.read())
        print('stop stdout: ', cmd.stdout.read())

    elif event == '3. Micro-Doppler Signature':
        window['md_text'].update('Generating Micro-Doppler Signature...')
        window.refresh()
        microDoppler(data_path + '/' + fname + '_Raw_0.bin')
        window['-IMAGE-'].update(data=convert_to_bytes(data_path + '/' + fname + '_Raw_0_py.png', resize=(500, 300)))
        window['md_text'].update('Done!                          ')
        window.refresh()

window.Close()
