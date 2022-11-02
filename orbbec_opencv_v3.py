import cv2
import numpy as np
import time
from openni import openni2
from openni import _openni2 as c_api
# python 2

fps = 30
width = 640
height = 480
mirroring = True
compression = False
duration = 3  # in sec
fname = 'orbbec'

# Initialize the depth device
openni2.initialize()
dev = openni2.Device.open_any()
if dev.has_sensor(openni2.SENSOR_COLOR):
    print("Color Stream found")

# Start the depth stream
depth_stream = dev.create_depth_stream()
depth_stream.set_mirroring_enabled(mirroring)
dev.set_image_registration_mode(True)
dev.set_depth_color_sync_enabled(True)
depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM,
                                               resolutionX=width, resolutionY=height, fps=fps))
depth_stream.start()

# Start the color stream
is_color_available = dev.has_sensor(c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888)
print('is_color_available:', is_color_available)
color_stream = dev.create_color_stream()
color_stream.set_mirroring_enabled(mirroring)
color_stream.start()
color_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888,
                                               resolutionX=width, resolutionY=height, fps=fps))

# Function to return some pixel information when the OpenCV window is clicked
refPt = []
selecting = False

# Initial OpenCV Window Functions
cv2.namedWindow("Depth Image")
# cv2.setMouseCallback("Depth Image", point_and_shoot)

rec = openni2.Recorder((fname + ".oni").encode('utf-8'))
rec.attach(depth_stream, compression)
rec.attach(color_stream, compression)
rec.start()

start = time.time()

# Loop
# while True:
while time.time() - start < duration:
    print('Orbbec time: ' + str(round(time.time() - start, 1)))
    # Grab a new depth frame
    # frame = depth_stream.read_frame()
    frame = color_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    # Put the depth frame into a numpy array and reshape it
    img = np.frombuffer(frame_data, dtype=np.uint16)
    img.shape = (1, 480, 640)
    img = np.concatenate((img, img, img), axis=0)
    img = np.swapaxes(img, 0, 2)
    img = np.swapaxes(img, 0, 1)

    # if len(refPt) > 1:
    #     img = img.copy()
    #     cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)

    # Display the reshaped depth frame using OpenCV
    cv2.imshow("Depth Image", img)
    key = cv2.waitKey(1) & 0xFF

    # If the 'c' key is pressed, break the while loop
    if key == ord("c"):
        break

# Close all windows and unload the depth device
openni2.unload()
# rec.stop()
depth_stream.stop()
color_stream.stop()
cv2.destroyAllWindows()
