from datetime import datetime
import glob
import os
import subprocess
import time

import PySimpleGUI as sg

from fun_microDoppler_2243_complex import microDoppler
# from fun_rangeDoppler_2243_complex import rangeDoppler
from helpers import convert_to_bytes
from prediction import *

fname = 'data/raw_data_Raw_0.bin'
model_path = 'keras_model.h5'
train_path = 'train_folder'
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
im_size = (64, 64)
new_model_name = 'keras_custom.h5'
is_split = False  # whether train/test split enabled
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

spect_size = (500, 300)

bcols = ['blue', 'orange', 'green']
BAR_WIDTH = 100
BAR_SPACING = 300
EDGE_OFFSET = 100
GRAPH_SIZE = (1000, 300)
DATA_SIZE = (GRAPH_SIZE[0], 120)
graph = sg.Graph(GRAPH_SIZE, (0, 0), DATA_SIZE, background_color='white')
graph.erase()
myfont = "Ariel 18"
font_size = 15
sg.theme("DarkTeal2")

layout = [[sg.Text('Radar User Interface', size=(50, 2), font=('courier', font_size))],
          [sg.Button('Setup Radar', button_color=('white', 'black'), size=(18, 2), font=('courier', font_size)),
           sg.Text('', key='setup_text', font=('courier', 20)),
           sg.Exit(button_color=('white', 'black'), size=(18, 2), font=('courier', font_size))],
          [sg.Image('data/md.png', key='-IMAGE-', size=spect_size),
           sg.VSep(),
           graph],
          [sg.Button('1. Start Recording', button_color=('white', 'green'), size=(18, 2), font=('courier', font_size)),
           sg.Text('                               ', key='start_text', font=('courier', font_size)),
           sg.VSep(),
           sg.InputText(size=(10, 5), key='class_name', font=('courier', font_size), default_text='CLASS_NAME'),
           sg.Text('Type the new class name here.\n(MAYBE and YOU are the default two classes.)',
                   key='default_classes', font=('courier', 20))],
          [sg.Button('2. Stop Recording', button_color=('white', 'red'), size=(18, 2), font=('courier', font_size)),
           sg.Text('                               ', key='stop_text', font=('courier', font_size)),
           sg.VSep(),
           sg.Button('Start Train \n Data Recording', key='train_start_record', button_color=('white', 'green'),
                     size=(18, 2), font=('courier', font_size)),
           sg.Text('', key='train_start_record_text', font=('courier', font_size))],
          [sg.Button('3. Micro-Doppler Signature', button_color=('white', 'blue'), size=(18, 2),
                     font=('courier', font_size)),
           sg.Text('                               ', key='md_text', font=('courier', font_size)),
           sg.VSep(),
           sg.Button('Stop Train \n Data Recording', key='train_stop_record', button_color=('white', 'red'),
                     size=(18, 2), font=('courier', font_size)),
           sg.Text('', key='train_stop_record_text', font=('courier', font_size))],
          [sg.Button('4. Predict', button_color=('black', 'yellow'), size=(18, 2), font=('courier', font_size)),
           sg.Text('                               ', key='pred_text', font=('courier', font_size)),
           sg.VSep(),
           sg.Button('Train the model', key='train', button_color=('white', 'blue'),
                     size=(18, 2), font=('courier', font_size)),
           sg.Text('Learning\n Rate:', size=(8, 2), font=('courier', font_size)),
           sg.Combo(values=[0.001, 0.01, 0.1], default_value=0.001, key='learn_rate', size=(5, 12),
                    font=('courier', font_size)),
           sg.VSep(),
           sg.Text('Num. of\nEpochs:', size=(7, 2), font=('courier', font_size)),
           sg.Combo(values=[10, 20, 50], default_value=20, key='epochs', size=(5, 12),
                    font=('courier', font_size)),
           sg.VSep(),
           sg.Text('Num. of\nLayers:', size=(7, 2), font=('courier', font_size)),
           sg.Combo(values=[1, 3, 5, 10], default_value=3, key='layers', size=(5, 12),
                    font=('courier', font_size))],
          [sg.Button('', key='somekey', button_color=('black', 'gray'), size=(18, 2), font=('courier', font_size)),
           sg.Text('                               ', key='some_text', font=('courier', font_size)),
           sg.VSep(),
           sg.Button('Predict on\nNew Model', key='pred_new', button_color=('black', 'yellow'),
                     size=(18, 2), font=('courier', font_size)),
           sg.Text('', key='pred_new_text', font=('courier', font_size))]]

window = sg.Window('Radar GUI').Layout(layout)

while True:  # Event Loop
    event, values = window.Read()
    if event in (None, 'Exit'):
        break

    if event == 'Setup Radar':
        window['md_text'].update('                               ')
        # window['rd_text'].update('')
        window['stop_text'].update('                               ')
        window['start_text'].update('                               ')
        window['-IMAGE-'].update('data/blank.png', size=spect_size)

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
        window['-IMAGE-'].update('data/md.png', size=spect_size)
        # window['-VIDEO-'].update('data/rd.png')
        window['md_text'].update('                               ')
        # window['rd_text'].update('')
        window['stop_text'].update('                               ')
        window['start_text'].update('Go!                            ')
        # window['setup_text'].update('                               ')
        window.refresh()

        cmd = subprocess.Popen(start_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        # cmd.stdin.write("start_record cf.json")
        # cmd.wait()

        print('start error return code: ', cmd.returncode)
        print('start error2: ', cmd.stderr.read())
        print('start stdout: ', cmd.stdout.read())

    elif event == '2. Stop Recording':
        window['stop_text'].update('Stopping...                    ')
        window['md_text'].update('                               ')
        # window['rd_text'].update('')
        window['start_text'].update('                               ')
        # window['setup_text'].update('                               ')
        window.refresh()

        # cmd = subprocess.Popen(['sudo', '-S', 'kill', '`ps -e | grep -i gnome-terminal`'], cwd=cwd, shell=False,
        #                        stdin=pwd.stdout, text=True,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        # cmd.wait()
        time.sleep(2)
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

        window['stop_text'].update('Done!                          ')
        window.refresh()

    elif event == '3. Micro-Doppler Signature':
        window['md_text'].update('Generating Micro-Doppler Signature...')
        window['stop_text'].update('                               ')
        window.refresh()
        microDoppler(fname)
        window['-IMAGE-'].update(data=convert_to_bytes(fname[:-4] + '_py_whiteborder.png', resize=spect_size))
        window['md_text'].update('Done!                          ')
        window.refresh()

    elif event == '4. Predict':
        window['pred_text'].update('Predicting...                  ')
        window['md_text'].update('                               ')
        window.refresh()
        im_size_default = (224, 224)
        pred = prediction(model_path, im_size_default)
        maybe = pred[0][0] * 100
        you = pred[0][1] * 100

        # add offset for visualization purposes
        offset = 3
        if maybe > you:
            you += offset
            you_offset = offset
            maybe_offset = 0
        else:
            maybe += offset
            you_offset = 0
            maybe_offset = offset

        graph.erase()
        graph.draw_rectangle(top_left=(0 * BAR_SPACING + EDGE_OFFSET, maybe),
                             bottom_right=(0 * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=bcols[0])
        graph.draw_text(text='MAYBE --> ' + str(round(maybe - maybe_offset, 2))+'%',
                        location=(0 * BAR_SPACING + EDGE_OFFSET + 120, maybe + 10), color=bcols[0], font=myfont)
        graph.draw_rectangle(top_left=(1 * BAR_SPACING + EDGE_OFFSET, you),
                             bottom_right=(1 * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=bcols[1])
        graph.draw_text(text='YOU --> ' + str(round(you - you_offset, 2)) + '%',
                        location=(1 * BAR_SPACING + EDGE_OFFSET + 120, you + 10), color=bcols[1], font=myfont)

        window['pred_text'].update('Predicted!                     ')
        window.refresh()

    elif event == 'train_start_record':
        window['-IMAGE-'].update('data/md.png', size=spect_size)
        # window['-VIDEO-'].update('data/rd.png')
        window['md_text'].update('                               ')
        # window['rd_text'].update('')
        window['stop_text'].update('                               ')
        window['train_start_record_text'].update('Go!')
        # window['setup_text'].update('                               ')
        window.refresh()

        cmd = subprocess.Popen(start_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd.wait()
        # cmd.stdin.write("start_record cf.json")
        # cmd.wait()

        print('train record start error return code: ', cmd.returncode)
        print('train record start error2: ', cmd.stderr.read())
        print('train record start stdout: ', cmd.stdout.read())

    elif event == 'train_stop_record':
        window['train_stop_record_text'].update('Stopping...')
        window['md_text'].update('                               ')
        # window['rd_text'].update('')
        window['train_start_record_text'].update('')
        # window['setup_text'].update('                               ')
        window.refresh()
        time.sleep(2)
        # cmd = subprocess.Popen(['sudo', '-S', 'kill', '`ps -e | grep -i gnome-terminal`'], cwd=cwd, shell=False,
        #                        stdin=pwd.stdout, text=True,
        #                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        # cmd.wait()
        # time.sleep(2)
        pid = subprocess.check_output(['pgrep gnome-terminal'], shell=True)  # , check=True)
        print('pid stdoutstr: ' + str(pid.decode())[:-1] + '-')

        cmd = subprocess.Popen(['kill', str(pid.decode())[:-1]], cwd=cwd, shell=False,
                               stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        cmd.wait()
        print('exit error return code: ', cmd.returncode)
        print('exit error2: ', cmd.stderr.read())
        print('exit stdout: ', cmd.stdout.read())

        cmd = subprocess.Popen(stop_cmd, cwd=cwd, shell=False, stdin=subprocess.PIPE, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # , check=True)
        cmd.wait()
        # cmd.stdin.write("stop_record cf.json")
        # cmd.wait()
        print('stop error return code: ', cmd.returncode)
        print('stop error2: ', cmd.stderr.read())
        print('stop stdout: ', cmd.stdout.read())

        window['train_stop_record_text'].update('Generating Micro-Doppler Signature...')
        window.refresh()
        microDoppler(fname)
        window['-IMAGE-'].update(data=convert_to_bytes(fname[:-4] + '_py_whiteborder.png', resize=spect_size))

        # rename to move it to the data folder
        now = datetime.now()
        date_time = now.strftime("_%Y_%m_%d_%H_%M_%S_")
        src = fname[:-4] + '_py_im.png'
        dst = src.replace('data', train_path).replace('raw', values['class_name'] + date_time)
        os.rename(src, dst)

        files = glob.glob(train_path + '/' + values['class_name'] + '*.png')

        window['train_stop_record_text'].update('Done! Num. of files: ' + str(len(files)))

    elif event == 'train':
        data = preprocess(train_path, values['class_name'], im_size, is_split)
        model, history = CNN_train(data, is_split, values['layers'], values['learn_rate'], 1, values['epochs'],
                                   new_model_name)

    elif event == 'pred_new':
        window['pred_new_text'].update('Predicting...')
        window.refresh()
        pred = prediction_new(new_model_name, im_size)
        maybe = pred[0][0] * 100
        you = pred[0][1] * 100
        custom_class = pred[0][2] * 100

        # add offset for visualization purposes
        offset = 3
        if maybe > you:
            you += offset
            you_offset = offset
            maybe_offset = 0
        else:
            maybe += offset
            you_offset = 0
            maybe_offset = offset
        graph.erase()
        graph.draw_rectangle(top_left=(0 * BAR_SPACING + EDGE_OFFSET, maybe),
                             bottom_right=(0 * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=bcols[0])
        graph.draw_text(text='MAYBE --> ' + str(round(maybe - maybe_offset, 2)) + '%',
                        location=(0 * BAR_SPACING + EDGE_OFFSET + 120, maybe + 10), color=bcols[0], font=myfont)
        graph.draw_rectangle(top_left=(1 * BAR_SPACING + EDGE_OFFSET, you),
                             bottom_right=(1 * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=bcols[1])
        graph.draw_text(text='YOU --> ' + str(round(you - you_offset, 2)) + '%',
                        location=(1 * BAR_SPACING + EDGE_OFFSET + 120, you + 10), color=bcols[1], font=myfont)
        graph.draw_rectangle(top_left=(2 * BAR_SPACING + EDGE_OFFSET, custom_class),
                             bottom_right=(2 * BAR_SPACING + EDGE_OFFSET + BAR_WIDTH, 0), fill_color=bcols[2])
        graph.draw_text(text=values['class_name'].upper() + ' --> ' + str(round(custom_class, 2)) + '%',
                        location=(2 * BAR_SPACING + EDGE_OFFSET + 120, custom_class + 10), color=bcols[2], font=myfont)
        window.refresh()

        window['pred_text'].update('Predicted!')

window.Close()












