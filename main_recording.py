import json
import os
import subprocess
import time
import PySimpleGUI as sg

from fun_microDoppler_2243_complex import microDoppler
from helpers import convert_to_bytes
from datetime import datetime

fname = 'data/raw_data_Raw_0.bin'
sudo_password = '190396'
cwd = '/home/emre/Desktop/77ghz/CLI/Release'
radar_path = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/' \
             'open_radar_initiative-new_receive_test/setup_radar/build'
leap_main_path = '/home/emre/PycharmProjects/LeapMotion/'
radar_fps = 25

radar_cmd = './setup_radar'
setup_leap = 'sudo leapd'.split()

export_cmd = 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd'
os.environ["LD_LIBRARY_PATH"] = cwd  # + ':' + os.getcwd() # error code 127 when not executed

dca = './DCA1000EVM_CLI_Control'

fpga_cmd = './DCA1000EVM_CLI_Control fpga cf.json'.split()
record_cmd = './DCA1000EVM_CLI_Control record cf.json'.split()
start_cmd = './DCA1000EVM_CLI_Control start_record cf.json'.split()
stop_cmd = './DCA1000EVM_CLI_Control stop_record cf.json'.split()

class_fname = 'classes.txt'
with open(class_fname) as f:
    # lines = f.readlines()  # ignore \n
    lines = f.read().splitlines()

sg.theme("DarkTeal2")

layout = [[sg.Text('Data Recording GUI', size=(50, 2), font=('courier', 20))],
          [sg.Text('Sensors List:', size=(15, 2), font=('courier', 20)),
           sg.Checkbox('77 Front', default=False, key="77_front_check", size=(15, 10), font=('courier', 20)),
           sg.Checkbox('77 Corner', default=False, key="77_corner_check", size=(15, 10), font=('courier', 20)),
           sg.Checkbox('77 Side', default=False, key="77_side_check", size=(15, 10), font=('courier', 20)),
           sg.Checkbox('Leap Motion', default=False, key="leap_motion_check", size=(15, 10), font=('courier', 20)),
           sg.Checkbox('Kinect', default=False, key="kinect_check", size=(15, 10), font=('courier', 20))],
          [sg.Text('Subject:', size=(8, 2), font=('courier', 20)),
           sg.InputText(size=(10, 5), key='subject', font=('courier', 20)),
           sg.VSep(),
           sg.Text('Class:', size=(7, 2), font=('courier', 20)),
           sg.Combo(values=lines, default_value='TEST', key='class_list', size=(10, 10), font=('courier', 20)),
           sg.VSep(),
           sg.Text('Experiment:', size=(11, 2), font=('courier', 20)),
           sg.Combo(values=['Exp1', 'Exp2', 'Exp3', 'Exp4'], default_value='TEST', key='exp_list', size=(5, 10),
                    font=('courier', 20)),
           sg.VSep(),
           sg.Text('Duration (sec):', size=(15, 2), font=('courier', 20)),
           sg.InputText(size=(10, 5), key='duration', font=('courier', 20))],
          [sg.Image('data/md.png', key='-IMAGE-', size=(700, 500)),
           sg.VSep(),
           [sg.Button('Setup Radar', button_color=('white', 'black'), size=(18, 2), font=('courier', 20)),
            sg.Text('', key='setup_text', font=('courier', 20)),
            sg.Button('Setup Leap Motion', button_color=('white', 'black'), size=(18, 2), font=('courier', 20))]],
          [sg.Button('1. Start Recording', button_color=('white', 'green'), size=(18, 2), font=('courier', 20)),
           sg.Text('                               ', key='start_text', font=('courier', 20)),
           sg.VSep(),
           sg.Button('2. Stop Recording', button_color=('white', 'red'), size=(18, 2), font=('courier', 20)),
           sg.Text('                             ', key='stop_text', font=('courier', 20))],
          [sg.Button('3. Micro-Doppler Signature', button_color=('white', 'blue'), size=(18, 2), font=('courier', 20)),
           sg.Text('                               ', key='md_text', font=('courier', 20)),
           sg.VSep(),
           sg.Exit(button_color=('white', 'black'), size=(18, 2), font=('courier', 20))]]

window = sg.Window('Radar GUI').Layout(layout)

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
        window['-IMAGE-'].update('data/md.png', size=(700, 500))
        window['md_text'].update('                               ')
        window['stop_text'].update('                             ')
        window['start_text'].update('Go!                            ')
        # window['setup_text'].update('                               ')
        # _, values = window.read()

        print('duration: ', values['duration'])
        data_class = values['class_list'].split()[0]
        now = datetime.now()
        main_path = '/home/emre/PycharmProjects/RadarGUI/data/'
        date_time = now.strftime("%Y_%m_%d_%H_%M_%S_")
        fname = date_time + 'subj' + values['subject'] + '_' + values['exp_list'] + '_class' + data_class
        filename = main_path + fname

        if values['leap_motion_check']:
            leap_cmd = 'python2 ' + leap_main_path + 'main.py --filename ' + filename + '.data' + \
                       ' --duration ' + values['duration']

            cmd = subprocess.Popen(leap_cmd.split(), cwd=cwd, shell=False, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)

            # print('leap')
        json_file = cwd + '/cf.json'
        a_file = open(json_file, "r")
        json_object = json.load(a_file)
        # print(json_object)
        a_file.close()
        # print(json_object['DCA1000Config']['captureConfig']['framesToCapture'])
        # json_object['DCA1000Config']['captureConfig']['framesToCapture'] = radar_fps * int(values['duration'])
        json_object['DCA1000Config']['captureConfig']['captureStopMode'] = 'duration'
        json_object['DCA1000Config']['captureConfig']['durationToCapture_ms'] = int(values['duration']) * 1000
        json_object['DCA1000Config']['captureConfig']['filePrefix'] = fname
        a_file = open(json_file, "w")
        json.dump(json_object, a_file)
        a_file.close()
        # time.sleep(1)
        # print(json_object)

        if values['77_front_check']:
            cmd = subprocess.Popen(start_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE,  # text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cmd.wait()
            # cmd.stdin.write("start_record cf.json")
            # cmd.wait()

            print('start error return code: ', cmd.returncode)
            print('start error2: ', cmd.stderr.read())
            print('start stdout: ', cmd.stdout.read())

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
        microDoppler('data/' + fname + '_Raw_0.bin')
        window['-IMAGE-'].update(data=convert_to_bytes('data/' + fname + '_Raw_0_py.png', resize=(700, 500)))
        window['md_text'].update('Done!                          ')
        window.refresh()

window.Close()
