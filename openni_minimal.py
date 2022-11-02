from openni import openni2
# python 2
openni2.initialize()     # can also accept the path of the OpenNI redistribution

dev = openni2.Device.open_any()
print(dev.get_device_info())

depth_stream = dev.create_depth_stream()
depth_stream.start()
frame = depth_stream.read_frame()
print(dir(frame))
frame_data = frame.get_buffer_as_uint16()
print(dir(frame_data))
depth_stream.stop()

openni2.unload()

