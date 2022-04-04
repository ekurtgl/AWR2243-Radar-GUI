import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import colors


def RDC_to_DOA_2243(RDC, fname, params, elev_or_azimuth='az', K=1, M=10, MTI=False):
    # If BPM and TDM
    ratio = params['NTS'] / params['Rmax']
    rangelimMatrix = int(ratio * params['max_range_plot'])

    if elev_or_azimuth == 'az':
        RDC = RDC[:rangelimMatrix, :, :8]
    elif elev_or_azimuth == 'el':
        RDC = np.stack([np.sum(RDC[:, :, 2:6], -1), np.sum(RDC[:, :, 8:], -1)], 2)
        params['numRX'] = 2
        params['numTX2'] = 1
    # RDC = RDC[:, :, :8]
    print('RDC:', RDC.shape)

    # MTI here ...
    if MTI:
        from scipy.signal import lfilter
        h = np.array([1, -2, 1])
        RDC = lfilter(h, 1, RDC, axis=1)

    RDC = np.fft.fft(RDC, axis=0)

    # Range Angle (azimuth) Map

    ang_ax = np.arange(-90, 91)
    d = 0.5

    if params['isTDM'] and elev_or_azimuth == 'az':
        params['numTX2'] = 2  # if BPM and TDM keep this 2, not 3
    elif params['isTDM'] and elev_or_azimuth == 'el':
        params['numTX2'] = 1
        params['numRX'] = 2
    else:
        params['numTX2'] = 1

    # Steering matrix
    a1 = np.zeros((RDC.shape[-1], len(ang_ax)), dtype='complex')
    for k in range(len(ang_ax)):
        a1[:, k] = np.exp(-1j * 2 * np.pi * (d * np.arange(0, params['numTX2'] * params['numRX']) *
                                             np.sin(ang_ax[k] * np.pi / 180)))
    # plt.figure(frameon=True)
    # plt.imshow(np.abs(np.matmul(a1.conj().T, a1)).astype(np.uint8), cmap='jet')
    # plt.draw()
    # plt.show()

    for i in tqdm(range(params['n_frames']), position=0):
        range_az_music = np.zeros((RDC.shape[0], len(ang_ax)), dtype='complex')
        for r in range(RDC.shape[0]):

            Rxx = np.zeros((params['numTX2'] * params['numRX'], params['numTX2'] * params['numRX']), dtype='complex')

            for mp in range(M):
                p_idx = i * int(params['NPpF'] / params['numTX']) + mp
                if i == params['n_frames'] - 1:
                    p_idx = (i - 1) * int(params['NPpF'] / params['numTX']) + mp
                A = np.expand_dims(RDC[r, p_idx, :], -1)
                Rxx += 1/M * np.matmul(A, A.conj().T)

            D, Q = np.linalg.eig(Rxx)  # Q: eigenvectors(columns), D: eigenvalues
            idx = np.argsort(D)[::-1]
            Q = Q[:, idx]
            Qs = Q[:, :K]
            Qn = Q[:, K:]

            music_spectrum2 = np.zeros((len(ang_ax),), dtype='complex')
            for k in range(len(ang_ax)):
                music_spectrum2[k] = np.matmul(np.expand_dims(a1[:, k], -1).conj().T, np.expand_dims(a1[:, k], -1)) / \
                                     np.matmul(np.matmul(np.expand_dims(a1[:, k], -1).conj().T,
                                                         np.matmul(Qn, Qn.conj().T)), np.expand_dims(a1[:, k], -1))
                # music_spectrum2[k] = (a1[:, k].conj().T * a1[:, k]) / (a1[:, k].conj().T * (Qn * Qn.conj().T) *
                #                                                        a1[:, k])

            range_az_music[r, :] = music_spectrum2

        maxval = np.max(np.abs(range_az_music))
        # minval = np.min(np.abs(range_az_music))
        # assert maxval != 0

        if i == 0:
            # print(maxval)
            # print(minval)
            fig = plt.figure(1, frameon=False)
            vmin = 190
            vmax = None
            norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
            im = plt.imshow((20 * np.log10((np.abs(range_az_music) / maxval))).astype(np.uint8), cmap='jet',
                            norm=norm, aspect="auto", extent=[ang_ax[0], ang_ax[-1],
                                                              params['max_range_plot'], 0])
            if elev_or_azimuth == 'az':
                plt.xlabel('Azimuth (degree)')
                plt.title('Range-Azimuth map')
            elif elev_or_azimuth == 'el':
                plt.xlabel('Elevation (degree)')
                plt.title('Range-Elevation map')

            plt.ylabel('Range (m)')
            plt.xlim([-60, 60])
            # plt.colorbar()
            # plt.draw()
            # plt.show()
            # plt.pause(1e-3)
            plt.close(1)
            if params['save_ra_map_az'] or params['save_ra_map_el']:
                import cv2

                # norm_pool = np.zeros((256, 254))
                size = im.get_array().shape[:2]
                # size = [512, 512]
                out = cv2.VideoWriter(fname.replace('.bin', '_' + elev_or_azimuth + '.avi'),
                                      cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                      params['fps'], (size[1], size[0]), isColor=1)
                final = im.get_array()
                final[final < vmin] = vmin
                final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
                                                        None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                # final = cv2.applyColorMap(cv2.normalize(final, None, None,
                #                                         None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                out.write(final)
                # savename = fname[:-4] + '_frame_' + str(i) + '.png'
                # fig.savefig(savename, dpi=200)
                # cv2.imwrite(savename, cv2.resize(final, (256, 256)))

        else:
            im.set_data((20 * np.log10((np.abs(range_az_music) / maxval))).astype(np.uint8))
            # plt.draw()
            # plt.show()
            # plt.pause(1e-3)
            if params['save_ra_map_az'] or params['save_ra_map_el']:
                final = im.get_array()
                final[final < vmin] = vmin
                final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
                                                        None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                # final = cv2.applyColorMap(cv2.normalize(final, None, None,
                #                                         None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                out.write(final)
                # savename = fname[:-4] + '_frame_' + str(i) + '.png'
                # fig.savefig(savename, dpi=200)
                # cv2.imwrite(savename, cv2.resize(final, (256, 256)))
        # playing w.o. saving frames added but commented out
        # final = im.get_array()
        # final[final < vmin] = vmin
        # final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
        #                                         None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
        # final = final[:, :, ::-1]  # bgr to rgb
        # # print(final.shape)
        # final = Image.fromarray(final).resize(size=(700, 700))
        # bio = io.BytesIO()
        # final.save(bio, format="PNG")
        # del final

