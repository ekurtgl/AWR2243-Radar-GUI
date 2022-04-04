import numpy as np


def RDC_extract_2243(fname):
    f = open(fname)
    data = np.fromfile(f, dtype=np.int16)
    f.close()

    # Radar config params
    params = dict()
    params['f_start'] = 77e9
    params['f_end'] = 81e9
    params['fc'] = (params['f_start'] + params['f_end']) / 2
    params['SweepTime'] = 40e-3
    params['NTS'] = 256
    params['numTX'] = 3
    params['numRX'] = 4
    params['NoC'] = 88
    params['slope'] = 80e12
    params['sampleFreq'] = 5.688e6
    params['idletime'] = 100e-6
    params['adcStartTime'] = 5e-6
    params['rampEndTime'] = 50e-6
    params['isBPM'] = True
    params['isTDM'] = True
    params['max_range_plot'] = 3  # params['sampleFreq'] * 299792458 / (2 * params['slope'])  # max range to be plotted
    params['save_ra_map_az'] = True
    params['save_ra_map_el'] = True
    params['save_rd_map'] = True
    params['save_spectrogram'] = True

    # Calculated params
    params['c'] = 299792458
    params['Bw'] = params['f_end'] - params['f_start']
    params['NPpF'] = int(params['numTX'] * params['NoC'])
    params['numChirps'] = int(np.ceil(len(data) / 2 / params['NTS'] / params['numRX']))
    params['dT'] = params['SweepTime'] / params['NPpF']
    params['prf'] = 1 / params['dT']
    params['duration'] = params['numChirps'] * params['dT']
    params['Rmax'] = params['sampleFreq'] * params['c'] / (2 * params['slope'])
    params['rResol'] = params['c'] / (2 * params['Bw'])
    params['RANGE_FFT_SIZE'] = params['NTS']
    params['RNGD2_GRID'] = np.linspace(0, params['Rmax'], params['RANGE_FFT_SIZE'])
    params['fps'] = int(1 / params['SweepTime'])
    params['n_frames'] = int(np.floor(params['duration']) * params['fps'])
    params['Tc'] = params['idletime'] + params['rampEndTime']
    params['lambda'] = params['c'] / params['fc']
    params['velmax'] = params['lambda'] / (params['Tc'] * 4)  # Unambiguous max velocity
    params['DFmax'] = params['velmax'] / (params['c'] / params['fc'] / 2)
    params['vResol'] = params['lambda'] / (2 * params['SweepTime'])

    # zero pad
    zerostopad = int(params['NTS'] * params['numChirps'] * params['numRX'] * 2 - len(data))
    data = np.concatenate([data, np.zeros((zerostopad,))])

    # Organize data per RX
    data = data.reshape(params['numRX'] * 2, -1, order='F')
    data = data[0:4, :] + data[4:8, :] * 1j
    data = data.T
    data = data.reshape(params['NTS'], params['numChirps'], params['numRX'], order='F')

    # if BPM and TDM enabled
    if params['isTDM'] and params['isBPM']:
        prf = 1 / params['dT'] / params['numTX']
        rem = -(data.shape[1] % 3)
        if rem:
            data = data[:, :rem, :]
        chirp1 = 1/2 * (data[:, 0::3, :] + data[:, 1::3, :])
        chirp2 = 1/2 * (data[:, 0::3, :] - data[:, 1::3, :])
        chirp3 = data[:, 2::3, :]
        data = np.concatenate([chirp1, chirp2, chirp3], -1)

    if params['isTDM'] and not params['isBPM']:
        prf = 1 / params['dT'] / params['numTX']
        rem = -(data.shape[1] % 3)
        if rem:
            data = data[:, :rem, :]
        chirp1 = data[:, 0::3, :]
        chirp2 = data[:, 1::3, :]
        chirp3 = data[:, 2::3, :]
        data = np.concatenate([chirp1, chirp2, chirp3], -1)

    return data, params
