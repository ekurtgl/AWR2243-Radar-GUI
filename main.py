import os
import subprocess

import PySimpleGUI as sg

from fun_microDoppler_2243_complex import microDoppler
from fun_rangeDoppler_2243_complex import rangeDoppler
from helpers import convert_to_bytes

fname = 'data/raw_adc.bin'
sudo_password = '190396'
cwd = '/home/emre/Desktop/77ghz/CLI/Release'
radar_path = '/home/emre/Desktop/77ghz/open_radar/open_radar_initiative-new_receive_test/' \
             'open_radar_initiative-new_receive_test/setup_radar/build'
radar_cmd = './setup_radar'
export_cmd = 'LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd'
# env = dict(os.environ)
env = os.environ.copy()
env['LD_LIBRARY_PATH'] = cwd + ':' + os.getcwd()
os.environ["LD_LIBRARY_PATH"] = cwd  # + ':' + os.getcwd()
print(env)

# os.system("LD_LIBRARY_PATH={}".format(os.getcwd()))

# env = dict(os.environ)
# env = os.environ.copy()
# env['LD_LIBRARY_PATH'] = '"{}":{}'.format(
#     os.getcwd(), env.get('LD_LIBRARY_PATH', ''))
# print(env)

fpga_cmd = './DCA1000EVM_CLI_Control fpga_record cf.json'.split()
record_cmd = './DCA1000EVM_CLI_Control record_record cf.json'.split()
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

        cmd = subprocess.Popen(['echo', sudo_password], cwd=radar_path, stdout=subprocess.PIPE)
        cmd.wait()
        print('sudopass: ', cmd.stdout.read())
        cmd = subprocess.Popen(['sudo', '-S'] + [radar_cmd], cwd=radar_path, stdin=cmd.stdout,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        print('setup_radar: ', cmd.stderr.read())
        # print('setup_radar21: ', cmd.stdout.read())

        # print(export_cmd)
        # cmd = subprocess.Popen(['export', export_cmd], cwd=cwd, stdin=cmd.stdout, shell=True, env=env,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # cmd.wait()
        # print('export: ', cmd.stdout.read())

        cmd = subprocess.run(fpga_cmd, cwd=cwd, stdin=subprocess.PIPE, shell=True, env=env,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print('fpga: ', cmd)
        # cmd.wait()
        print('fpga: ', cmd.stderr.read())

        cmd = subprocess.Popen(record_cmd, cwd=cwd, stdin=cmd.stdout, shell=True,  env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        print('record: ', cmd.stdout.read())

        window['setup_text'].update('Radar is ready to go!')

    elif event == '1. Start Recording':
        window['md_text'].update('                               ')
        window['rd_text'].update('')
        window['stop_text'].update('                             ')
        window['start_text'].update('Go!                            ')
        # os.system('cd /home/emre/Desktop/77ghz/CLI/Release')
        # os.system('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$pwd')
        # os.system('./DCA1000EVM_CLI_Control start_record cf.json')
        # std1 = subprocess.Popen(export_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True, stdout=subprocess.PIPE)
        # subprocess.run(lib_cfg_cmd, cwd=cwd, shell=True)
        # std2 = subprocess.Popen(fpga_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True, stdout=subprocess.PIPE)
        # std3 = subprocess.Popen(record_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True, stdout=subprocess.PIPE)
        # std = subprocess.run(export_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True,
        #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # # std.wait()
        # # output = std.stdout.read().decode()
        # # print(output)
        # print('export: ', std.stdout)
        #
        # std = subprocess.run(fpga_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True,
        #                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        # # std.wait()
        # # output = std.stdout.read().decode()
        # # print(output)
        # print('fpga: ', std.stdout)
        #
        # std = subprocess.Popen(record_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # std.wait()
        # output = std.stdout.read().decode()
        # print(output)
        # print(std.stdout)
        #
        # std = subprocess.Popen(start_cmd, stdin=subprocess.PIPE, cwd=cwd, shell=True,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # std.wait()
        # output = std.stdout.read().decode()
        # print(output)
        cmd = subprocess.Popen(start_cmd, cwd=cwd, stdin=subprocess.PIPE, shell=True, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        print('start: ', cmd.stdout.read())

    elif event == '2. Stop Recording':
        window['md_text'].update('                               ')
        window['rd_text'].update('')
        window['stop_text'].update('Done!                        ')
        window['start_text'].update('                               ')
        # subprocess.run(stop_cmd, cwd=cwd)
        cmd = subprocess.Popen(stop_cmd, cwd=cwd, stdin=subprocess.PIPE, shell=True, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        print('stop: ', cmd.stderr.read())

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












