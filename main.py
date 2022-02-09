import PySimpleGUI as sg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from fun_microDoppler_2243_complex import microDoppler
from fun_rangeDoppler_2243_complex import rangeDoppler
from helpers import convert_to_bytes


fname = 'data/raw_adc.bin'

layout = [[sg.Image('data/md.png', key='-IMAGE-', size=(700, 700)),
           sg.VSep(),
           sg.Image('data/rd.png', key='-VIDEO-', size=(700, 700))],
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
# window['-IMAGE-'].expand(True, True)

while True:  # Event Loop
    event, values = window.Read()
    if event in (None, 'Exit'):
        break
    if event == '3. Micro-Doppler Signature':
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












