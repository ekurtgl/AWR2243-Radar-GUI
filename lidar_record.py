import time
import pyrealsense2 as rs


duration = 3
filename = 'lidar'
# Create a context object. This object owns the handles to all connected realsense devices
pipeline = rs.pipeline()
config = rs.config()
print(dir(config))
config.enable_stream(rs.stream.depth, rs.format.z16, 30)
config.enable_stream(rs.stream.color, rs.format.bgr8, 30)
config.enable_record_to_file(filename + '.bag')
pipeline.start(config)
cnt = 1
start = time.time()

while time.time() - start < duration:
    # Create a pipeline object. This object configures the streaming camera and owns its handle
    frames = pipeline.wait_for_frames()
pipeline.stop()

