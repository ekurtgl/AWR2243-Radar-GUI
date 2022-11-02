import argparse
import time
import cv2

parser = argparse.ArgumentParser()

# Add an argument
parser.add_argument('--filename', type=str, required=True)
parser.add_argument('--duration', type=int, required=True)
parser.add_argument('--cam_id', type=int, required=True)

# Parse the argument
args = parser.parse_args()

# Capture video from webcam
vid_capture = cv2.VideoCapture(args.cam_id)
vid_cod = cv2.VideoWriter_fourcc(*'XVID')
output = cv2.VideoWriter(args.filename + ".mp4", vid_cod, 30.0, (640, 480))

start = time.time()

while time.time() - start < args.duration:
    # Capture each frame of webcam video
    ret, frame = vid_capture.read()
    # cv2.imshow("My cam video", frame)
    output.write(frame)
    # Close and break the loop after pressing "x" key
    # if cv2.waitKey(1) & 0XFF == ord('x'):
    #     break
# close the already opened camera
vid_capture.release()
# close the already opened file
output.release()
# close the window and de-allocate any associated memory usage
# cv2.destroyAllWindows()
print('Webcam recording is done!')
