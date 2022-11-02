from datetime import datetime
import time
import argparse
import sys
import configparser
import os
from openni import openni2
from openni import _openni2 as c_api

width = 640
height = 480
fps = 30
mirroring = True
compression = False
length = 3  # in sec
debug = True
dst = 'Recordings'


def write_files(dev, dst):

    if debug:
        import cv2
        import numpy as np
    depth_stream = dev.create_depth_stream()
    color_stream = dev.create_color_stream()
    depth_stream.set_mirroring_enabled(mirroring)
    color_stream.set_mirroring_enabled(mirroring)
    depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM,
                                                   resolutionX=width,
                                                   resolutionY=height,
                                                   fps=fps))
    color_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888,
                                                   resolutionX=width,
                                                   resolutionY=height,
                                                   fps=fps))
    dev.set_image_registration_mode(True)
    dev.set_depth_color_sync_enabled(True)
    depth_stream.start()
    color_stream.start()

    current_date = datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
    if not os.path.exists(dst):
        os.mkdir(dst)
        print("Directory ", dst, " Created ")
    rec = openni2.Recorder((dst + '/' + current_date + ".oni").encode('utf-8'))
    rec.attach(depth_stream, compression)
    rec.attach(color_stream, compression)
    rec.start()
    print("Recording started.. press ctrl+C to stop or wait " + str(length) + " seconds..")
    start = time.time()
    depth_scale_factor = 0.05
    depth_scale_beta_factor = 0
    try:
        while True:
            if (time.time()-start)>length:
                break
            if debug:
                frame_color = color_stream.read_frame()
                frame_depth = depth_stream.read_frame()

                frame_color_data = frame_color.get_buffer_as_uint8()
                frame_depth_data = frame_depth.get_buffer_as_uint16()

                color_array = np.ndarray((frame_color.height, frame_color.width, 3),dtype=np.uint8,buffer=frame_color_data)
                color_array = cv2.cvtColor(color_array, cv2.COLOR_BGR2RGB)
                depth_array = np.ndarray((frame_depth.height, frame_depth.width),dtype=np.uint16,buffer=frame_depth_data)
                depth_uint8 = depth_array*depth_scale_factor+depth_scale_beta_factor
                depth_uint8[depth_uint8>255] = 255
                depth_uint8[depth_uint8<0] = 0
                depth_uint8 = depth_uint8.astype('uint8')

                cv2.imshow('depth', depth_uint8)
                cv2.imshow('color', color_array)
                cv2.waitKey(1)
    except KeyboardInterrupt:
        pass
    if debug:
        cv2.destroyAllWindows()
    rec.stop()
    depth_stream.stop()
    color_stream.stop()

def readSettings():
    global width,height,fps,mirroring,compression,length,debug,dst
    config = configparser.ConfigParser()
    config.read('settings.ini')
    print(config)
    width = int(config['camera']['width'])
    height = int(config['camera']['height'])
    fps = int(config['camera']['fps'])
    mirroring = config.getboolean('camera','mirroring')
    compression = config.getboolean('camera','compression')
    length = int(config['camera']['length'])
    debug = config.getboolean('camera','debug')
    dst = config['system']['out_folder']


def main():

    print("pyOniRecorder by Rocco Pietrini v1 \n ")
    readSettings()
    try:
        if sys.platform == "win32":
            libpath = ""
        else:
            libpath = "lib/Linux"
        print("library path is: ", os.path.join(os.path.dirname(__file__),libpath))
        openni2.initialize(os.path.join(os.path.dirname(__file__),libpath))
        print("OpenNI2 initialized \n")
    except Exception as ex:
        print("ERROR OpenNI2 not initialized",ex," check library path..\n")
        return
    try:
        dev = openni2.Device.open_any()
    except Exception as ex:
        print("ERROR Unable to open the device: ",ex," device disconnected? \n")
        return
    write_files(dev, dst)
    try:
        openni2.unload()
        print("Device unloaded \n")
    except Exception as ex:
        print("Device not unloaded: ",ex, "\n")


if __name__ == '__main__':
    main()