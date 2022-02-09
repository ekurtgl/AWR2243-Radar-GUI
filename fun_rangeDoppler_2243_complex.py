import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import colors
from helpers import fig2img


# params
save_rd_map = True
rangelim = 3

idletime = 100e-6
adcStartTime = 5e-6
rampEndTime = 50e-6
sampleFreq = 6.25e6
c = 299792458
slope = 80e12
fstart = 77e9
Bw = 4e9
fstop = fstart + Bw
fc = (fstart + fstop) / 2
lamda = c / fc
Rmax = sampleFreq * c / (2 * slope)
Tc = idletime + adcStartTime + rampEndTime
# Tf = SweepTime
# dT = SweepTime / NPpF
# prf = 1 / dT
velmax = lamda / (Tc * 4)
DFmax = velmax / (c / fc / 2)
# rResol = c / (2 * Bw)
# vResol = lamda / (2 * Tf)
# RNGD2_GRID = np.linspace(0, Rmax, numADCSamples)
# DOPP_GRID = np.linspace(DFmax, -DFmax, numLoopsPerFrame)
# V_GRID = (c / fc / 2) * DOPP_GRID


def rangeDoppler(fname):
    f = open(fname)
    data = np.fromfile(f, dtype=np.int16)
    f.close()

    # Parameters
    SweepTime = 40e-3
    NTS = 256
    numTX = 1
    NoC = 255
    NPpF = numTX * NoC
    numRX = 4
    numChirps = int(np.ceil(len(data) / 2 / NTS / numRX))
    NoF = numChirps // NPpF
    dT = SweepTime / NPpF
    velmax = lamda / (Tc * 4)
    prf = 1 / dT
    isReal = 0
    duration = numChirps * dT

    # zero pad
    zerostopad = int(NTS * numChirps * numRX * 2 - len(data))
    data = np.concatenate([data, np.zeros((zerostopad,))])

    # Organize data per RX
    data = data.reshape(numRX * 2, -1, order='F')
    data = data[0:4, :] + data[4:8, :] * 1j
    data = data.T
    data = data.reshape(NTS, numChirps, numRX, order='F')

    for i in tqdm(range(NoF)):
        # rd_frame = data[:, i*NoC: (i+1)*NoC, 0].T - np.mean(data[:, i*NoC: (i+1)*NoC, 0], 1)
        rd_frame = data[:, i*NoC: (i+1)*NoC, 0].T
        rd_frame = np.fft.fftshift(np.fft.fft2(rd_frame.T, axes=(0, 1)), 1)
        rd_frame = rd_frame[rd_frame.shape[0] // 2:]  # second half after fft
        rd_frame = rd_frame[: int(rd_frame.shape[0] // Rmax * rangelim)]  # desired max range
        maxval = np.max(np.abs(rd_frame))

        if i == 0:
            fig = plt.figure(frameon=False)
            vmin = 190
            vmax = None
            norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
            im = plt.imshow((20 * np.log10((np.abs(rd_frame) / maxval))).astype(np.uint8), cmap='jet',
                            norm=norm, aspect="auto", extent=[-velmax, velmax, rangelim, 0])
            plt.xlabel('Velocity (m/s)')
            plt.ylabel('Range (m)')
            plt.title('Range-Doppler map')
            # plt.ylim([rangelim, 0])
            plt.colorbar()
            plt.draw()
            # plt.pause(1e-3)
            if save_rd_map:
                import cv2

                norm_pool = np.zeros((256, 254))
                fps = int(1 / SweepTime)
                size = im.get_array().shape[:2]
                # size = [512, 512]
                # out = cv2.VideoWriter(fname.replace('bin', 'avi'),
                #                       cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                #                       fps, (size[1], size[0]), isColor=1)
                # final = im.get_array()
                # final[final < vmin] = vmin
                # final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
                #                                         None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                # out.write(final)
                savename = fname[:-4] + '_frame_' + str(i) + '.png'
                fig.savefig(savename, dpi=200)
                # cv2.imwrite(savename, cv2.resize(final, (256, 256)))

        else:
            im.set_data((20 * np.log10((np.abs(rd_frame) / maxval))).astype(np.uint8))
            plt.draw()
            # plt.pause(1e-3)
            if save_rd_map:
                # final = im.get_array()
                # final[final < vmin] = vmin
                # final = cv2.applyColorMap(cv2.normalize(final, None, vmin,
                #                                         None, cv2.NORM_MINMAX), cv2.COLORMAP_JET)
                # out.write(final)
                savename = fname[:-4] + '_frame_' + str(i) + '.png'
                fig.savefig(savename, dpi=200)
                # cv2.imwrite(savename, cv2.resize(final, (256, 256)))
    return NoF






