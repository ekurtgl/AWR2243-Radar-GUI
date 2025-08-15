# Linux/Windows Data Collection and Processing GUI for AWR2243 + DCA1000EVM Setup in Python

## Quick Start Tutorial with Linux [YouTube Link](https://youtu.be/q4e_0xsQMmw)

### Prerequisites:

* For Linux, C-bindings and FTDI drivers must be installed following the steps in [this repo](https://github.com/openradarinitiative/openradar_mmwave_utils).

`main.py` is the main script to run the GUI.

`mmwaveconfig.txt` and `cf.json` needs to be placed where they are needed.

'cwd', 'sudo_password' and 'radar_path' variables in `main.py` need to be adjusted according to your path.

![Screenshot from 2022-02-17 13-22-40](https://user-images.githubusercontent.com/66868163/154562569-dfbd2cab-8984-4aa5-af1a-81557d3bc79a.png)

`main_predict_gallaudet.py`:
![Screenshot from 2022-04-08 16-49-45](https://user-images.githubusercontent.com/66868163/162557287-29c5b592-6e68-40c2-b080-ac11985cfe38.png)

--------------
`main_recording_windows.py`: This file is for recording simultaneous multi-sensor (TI Radar, Leap Motion, Orbbec, Kinect v2, RGB cam, and Intel RealSense Lidar) data.
![image](https://user-images.githubusercontent.com/66868163/162557329-6133ed98-8fb5-4ed1-80c6-785c72e8824a.png)
