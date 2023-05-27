import numpy as np
# import os
# print(os.getcwd())
from radar_utils.helpers import stft


def RDC_microDoppler(RDC, fname, params):

    # Range FFT
    # RDC = np.fft.fft(RDC, axis=0)

    rBin = np.arange(18, 25)  # 20 30
    nfft = 2 ** 12
    window = 256
    noverlap = 200
    shift = window - noverlap

    y2 = np.sum(RDC[rBin, :], 0)
    sx = stft(y2[:, -1], window, nfft, shift)
    sx2 = np.abs((np.fft.fftshift(sx, 0)))

    # Plot
    if params['save_spectrogram']:
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
                        extent=[0, params['duration'], -params['prf'] / 2, params['prf'] / 2])
        plt.xlabel('Time (sec)')
        plt.ylabel('Frequency (Hz)')
        # plt.ylim([-prf/6, prf/6])
        plt.title('Radar Micro-Doppler Spectrogram')
        fig.savefig(savename, transparent=False, dpi=200)
        # ax.set_axis_off()
        # fig.add_axes(ax)
        # ax.imshow(your_image, aspect='auto')
        # plt.axis('off')
        # fig.savefig(savename.replace('.', '_im.'), bbox_inches=extent)
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off',
                        labelright='off', labelbottom='off')
        # ax.set_title('')
        im.get_figure().gca().set_title("")
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

        plt.savefig(savename.replace('.', '_im.'), bbox_inches='tight', transparent=True, pad_inches=0)

        # plt.imsave(savename.replace('.', '_im.'), ax.get_images())

        # frame = plt.gcf()
