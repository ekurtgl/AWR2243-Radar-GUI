import os
import subprocess

import PySimpleGUI as sg

from fun_microDoppler_2243_complex import microDoppler
from fun_rangeDoppler_2243_complex import rangeDoppler
from helpers import convert_to_bytes

fname = 'data/raw_data_Raw_0.bin'
sudo_password = '190396'
cwd = '/home/emre/Desktop/77ghz/CLI/Release'
radar_path = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/' \
             'open_radar_initiative-new_receive_test/setup_radar/build'
radar_cmd = './setup_radar'
export_cmd = 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd'
# env = dict(os.environ)
# env = os.environ.copy()
# env['LD_LIBRARY_PATH'] = cwd + ':' + os.getcwd()
os.environ["LD_LIBRARY_PATH"] = cwd  # + ':' + os.getcwd() # error code 127 when not executed
# print(env)

# os.system("LD_LIBRARY_PATH={}".format(os.getcwd()))

# env = dict(os.environ)
# env = os.environ.copy()
# env['LD_LIBRARY_PATH'] = '"{}":{}'.format(
#     os.getcwd(), env.get('LD_LIBRARY_PATH', ''))
# print(env)

CREATE_NO_WINDOW = 0x08000000
# startupinfo = None
# if os.name == 'nt':
# startupinfo = subprocess.STARTUPINFO()
# startupinfo.wShowWindow = SW_HIDE
# startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


dca = './DCA1000EVM_CLI_Control'

fpga_cmd = './DCA1000EVM_CLI_Control fpga cf.json'.split()
# fpga_cmd = ["./DCA1000EVM_CLI_Control", "fpga cf.json"]
record_cmd = './DCA1000EVM_CLI_Control record cf.json'.split()
start_cmd = './DCA1000EVM_CLI_Control start_record cf.json'.split()
stop_cmd = './DCA1000EVM_CLI_Control stop_record cf.json'.split()

layout = [[sg.Image('data/md.png', key='-IMAGE-', size=(700, 700)),
           sg.VSep(),
           sg.Image('data/rd.png', key='-VIDEO-', size=(700, 700)),
           sg.VSep(),
           [sg.Button('Setup Radar', button_color=('white', 'black'), size=(18, 2), font=('courier', 20)),
            sg.Text('', key='setup_text', font=('courier', 20))]],
          [sg.Button('1. Start Recording', button_color=('white', 'green'), size=(18, 2), font=('courier', 20)),
           sg.Text('                               ', key='start_text', font=('courier', 20)),
           sg.VSep(),
           sg.Button('2. Stop Recording', button_color=('white', 'red'), size=(18, 2), font=('courier', 20)),
           sg.Text('                             ', key='stop_text', font=('courier', 20)),
           sg.VSep(),
           sg.Exit(button_color=('white', 'black'), size=(18, 2), font=('courier', 20))],
          [sg.Button('3. Micro-Doppler Signature', button_color=('white', 'blue'), size=(18, 2), font=('courier', 20)),
           sg.Text('                               ', key='md_text', font=('courier', 20)),
           sg.VSep(),
           sg.Button('4. Range-Doppler Map', button_color=('white', 'blue'), size=(18, 2), font=('courier', 20)),
           sg.Text('                     ', key='rd_text', font=('courier', 20))]]


window = sg.Window('Radar GUI').Layout(layout)

while True:  # Event Loop
    event, values = window.Read()
    if event in (None, 'Exit'):
        break

    if event == 'Setup Radar':
        window['md_text'].update('                               ')
        window['rd_text'].update('')
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

    elif event == '1. Start Recording':
        window['-IMAGE-'].update('data/md.png')
        window['-VIDEO-'].update('data/rd.png')
        window['md_text'].update('                               ')
        window['rd_text'].update('')
        window['stop_text'].update('                             ')
        window['start_text'].update('Go!                            ')
        window['setup_text'].update('                               ')

        cmd = subprocess.Popen(start_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        # cmd.stdin.write("start_record cf.json")
        # cmd.wait()

        print('start error return code: ', cmd.returncode)
        print('start error2: ', cmd.stderr.read())
        print('start stdout: ', cmd.stdout.read())

    elif event == '2. Stop Recording':
        window['md_text'].update('                               ')
        window['rd_text'].update('')
        window['stop_text'].update('Done!                        ')
        window['start_text'].update('                               ')
        window['setup_text'].update('                               ')

        pwd = subprocess.Popen(['echo', sudo_password], cwd=radar_path, stdout=subprocess.PIPE)
        pwd.wait()
        print('sudopass: ', pwd.stdout.read())

        # cmd = subprocess.Popen(['sudo', '-S', 'kill', '`ps -e | grep -i gnome-terminal`'], cwd=cwd, shell=False,
        #                        stdin=pwd.stdout, text=True,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        # cmd.wait()

        pid = subprocess.check_output(['pgrep gnome-terminal'], shell=True)  # , check=True)
        print('pid stdoutstr: ' + str(pid.decode())[:-1] + '-')

        cmd = subprocess.Popen(['kill', str(pid.decode())[:-1]], cwd=cwd, shell=False,
                               stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        cmd.wait()
        print('exit error return code: ', cmd.returncode)
        print('exit error2: ', cmd.stderr.read())
        print('exit stdout: ', cmd.stdout.read())

        cmd = subprocess.Popen(stop_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE,  text=True,
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
        microDoppler(fname)
        window['-IMAGE-'].update(data=convert_to_bytes(fname[:-4] + '_py.png', resize=(700, 700)))
        window['md_text'].update('Done!                          ')
        window.refresh()

    elif event == '4. Range-Doppler Map':
        window['rd_text'].update('Generating Range-Doppler Map...')
        window.refresh()
        num_frames = rangeDoppler(fname)
        for i in range(num_frames):
            window.refresh()
            savename = fname[:-4] + '_frame_' + str(i) + '.png'
            window['-VIDEO-'].update(data=convert_to_bytes(savename, resize=(700, 700)))
            window['rd_text'].update('Playing! Time: ' + str(round(i/25, 1)))
            window.refresh()

window.Close()












