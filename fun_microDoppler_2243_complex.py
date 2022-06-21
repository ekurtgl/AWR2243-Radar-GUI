import numpy as np
from helpers import stft


def microDoppler(fname):
    f = open(fname)
    data = np.fromfile(f, dtype=np.int16)
    f.close()

    # Parameters
    save_spectrograms = True
    SweepTime = 40e-3
    NTS = 256
    numTX = 1
    NoC = 255
    isBPM = False
    isTDM = False
    NPpF = numTX * NoC
    numRX = 4
    numChirps = int(np.ceil(len(data) / 2 / NTS / numRX))
    NoF = round(numChirps / NPpF)
    dT = SweepTime / NPpF
    prf = 1 / dT
    isReal = 0
    duration = numChirps * dT

    # zero pad
    zerostopad = int(NTS * numChirps * numRX * 2 - len(data))
    print('1', data.shape)
    data = np.concatenate([data, np.zeros((zerostopad,))])
    print('2', data.shape)

    # Organize data per RX
    data = data.reshape(numRX * 2, -1, order='F')
    data = data[0:4, :] + data[4:8, :] * 1j
    data = data.T
    data = data.reshape(NTS, numChirps, numRX, order='F')
    print('3', data.shape)

    # if BPM and TDM enabled
    if isTDM and isBPM:
        prf = 1 / dT / numTX
        rem = -(data.shape[1] % 3)
        if rem:
            data = data[:, :rem, :]
        chirp1 = 1/2 * (data[:, 0::3, :] + data[:, 1::3, :])
        chirp2 = 1/2 * (data[:, 0::3, :] - data[:, 1::3, :])
        chirp3 = data[:, 2::3, :]
        data = np.concatenate([chirp1, chirp2, chirp3], -1)

    print(data.shape)

    # Range FFT
    rp = np.fft.fft(data)

    # micro-Doppler Spectrogram
    rBin = np.arange(18, 25)  # 20 30
    nfft = 2 ** 12
    window = 256
    noverlap = 200
    shift = window - noverlap

    y2 = np.sum(rp[rBin, :], 0)
    sx = stft(y2[:, -1], window, nfft, shift)
    sx2 = np.abs((np.fft.fftshift(sx, 0)))

    # Plot
    if save_spectrograms:
        from matplotlib import colors
        import matplotlib.pyplot as plt

        fig = plt.figure(frameon=True)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        savename = fname[:-4] + '_py.png'

        maxval = np.max(sx2)
        norm = colors.Normalize(vmin=-45, vmax=None, clip=True)

        # imwrite (no axes)
        # ax.imshow(20 * np.log10((abs(sx2) / maxval)), cmap='jet', norm=norm, aspect="auto",
        #           extent=[0, duration, -prf/2, prf/2])
        # ax.set_xlabel('Time (sec)')
        # ax.set_ylabel('Frequency (Hz)')
        # ax.set_title('Complex mmwave ASL python')
        # ax.set_ylim([-prf/6, prf/6])
        # # ax.set_axis_off()
        # fig.add_axes(ax)
        # fig.savefig(savename, dpi=200)

        # gcf (with axes)
        im = plt.imshow(20 * np.log10((abs(sx2) / maxval)), cmap='jet', norm=norm, aspect="auto",
                   extent=[0, duration, -6400 / 2, 6400 / 2])
        plt.xlabel('Time (sec)')
        plt.ylabel('Frequency (Hz)')
        # plt.ylim([-prf/6, prf/6])
        # plt.title('Radar Micro-Doppler Spectrogram')
        plt.title('Complex my_param CLI-openradar asl python process_complex')
        fig.savefig(savename, transparent=True, dpi=200)
        # ax.set_axis_off()
        # fig.add_axes(ax)
        # ax.imshow(your_image, aspect='auto')
        # plt.axis('off')
        # fig.savefig(savename.replace('.', '_im.'), bbox_inches=extent)
        plt.title('Radar Micro-Doppler Spectrogram')
        fig.savefig(savename.replace('.', '_whiteborder.'), transparent=False, dpi=200)

        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off',
                        labelright='off', labelbottom='off')
        # ax.set_title('')
        im.get_figure().gca().set_title("")
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

        plt.savefig(savename.replace('.', '_im.'), bbox_inches='tight', transparent=True, pad_inches=0)



        # plt.imsave(savename.replace('.', '_im.'), ax.get_images())

        # frame = plt.gcf()

