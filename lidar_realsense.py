# First import the library
import cv2
import pyrealsense2 as rs
import numpy as np

# Create a context object. This object owns the handles to all connected realsense devices
pipeline = rs.pipeline()
pipeline.start()

cnt = 1

while True:
    # Create a pipeline object. This object configures the streaming camera and owns it's handle
    frames = pipeline.wait_for_frames()
    print(dir(frames))  # see all the data fields
    depth = frames.get_depth_frame()
    # Print a simple text-based representation of the image, by breaking it into 10x20 pixel regions and
    # approximating the coverage of pixels within one meter
    # coverage = np.zeros(64)
    # for y in range(480):
    #     for x in range(640):
    #         dist = depth.get_distance(x, y)
    #         if 0 < dist and dist < 1:
    #             coverage[int(x/10)] += 1
    #
    #     if y % 20 == 19:
    #         line = ""
    #         for c in coverage:
    #             line += " .:nhBXWW" + str(c/25)
    #         coverage = [0]*64
    #         # print(line)

    depth_data = depth.as_frame().get_data()
    np_image = np.asanyarray(depth_data)
    # print('Frame:', cnt)
    print('Frame:', frames.frame_number)
    cv2.imshow("Lidar Image", np_image)

    # If the 'c' key is pressed, break the while loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("c"):
        break
    cnt += 1

pipeline.stop()
cv2.destroyAllWindows()

