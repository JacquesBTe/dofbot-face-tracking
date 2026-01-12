# 🤖 DOFBOT Face Tracking Robot

Real-time 3D face tracking system for DOFBOT robot arm using OpenCV and Haar Cascades on NVIDIA Jetson Orin Nano.

## ✨ Features

- **3D Face Tracking**: Tracks faces in X (left/right), Y (up/down), and depth dimensions
- **Smart Search Algorithm**: 
  - LOCAL search: Small square around last seen position
  - EXPANDED search: Larger radius if not found
  - WIDE search: Full room sweep
- **Temporal Smoothing**: Reduces detection flicker using 3-frame history
- **Calibrated Servo Control**: Custom calibration system for precise movements
- **Adaptive Response**: Adjustable deadzone and movement speed

## 🛠️ Hardware

- DOFBOT 6-DOF Robot Arm
- NVIDIA Jetson Orin Nano
- USB Camera
- I2C Bus 7 for servo communication

## ⚠️ Platform Compatibility Note (Jetson Orin Nano)

**FOR SETTING UP PLEASE REFER TO MY REPOSITORY NAMED doftbot-jetson-orin-setup**

The official Yahboom DOFBOT Jetson image and setup guides are primarily built around the **older Jetson Nano + ROS 1 (Noetic/Melodic) workflow**. On the **Jetson Orin Nano**, that vendor-provided image is **not directly compatible**, and ROS 1 compatibility is typically tied to the older Nano-era stack. Only ROS 2 is directly compatible with the new Jetson Orin Nano. 

Yahboom support also confirmed that **DOFBOT does not provide a Jetson Orin-compatible system image** and that adapting the system is a DIY effort outside of their technical support scope. For transparency, here is the response I received from Yahboom:

> Hello,  
>   
> Currently, DOFBOT does not provide a system image compatible with the Jetson Orin development board. If you wish to use this platform, you will need to set up the environment and adapt the functionalities yourself.  
>   
> As this is a DIY development project, related adaptation and debugging work are not covered by our technical support. Thank you for your understanding and support.  
>   
> Best wishes  
> Yahboom Team

Because this DOFBOT stack depends on **ROS 1 Noetic** and the vendor environment was not compatible with Orin Nano, I run the project inside a **Docker container** on the Orin Nano to keep the software environment consistent while still accessing the Orin’s hardware peripherals (camera, I2C, display). This project is unique due to the unrelliance to DOFBOT's provided code it merely learns upon it and I recreated code to implement my stuff. This project is for those who want to be able to use the new Jetson Orin Nano with the DOFBOT robot arm. With my limited knowledge and expertise there were many issues faced in the development of this projects and as such I was limited to implementing this project. I wanted to implement a VLM but encountered too many issues and errors outside of my current expertise. 

## 📋 Requirements
```bash
# Python packages
pip3 install smbus2 opencv-python

# System packages (for Docker)
apt-get install python3-opencv libgl1-mesa-glx libglib2.0-0
```

## 🚀 Quick Start

### Option 1: Run in Docker (Recommended)
```bash
# Start Docker with display access
xhost +local:docker
sudo docker run -it --rm --privileged --network=host \
  -v ~/yahboom_backup:/root/yahboom_backup \
  -v /dev:/dev \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  ros:noetic-ros-base-focal bash

# Inside Docker - run setup
/root/yahboom_backup/Dofbot/face_tracking_project/setup_all.sh

# Run face tracking
python3 /root/yahboom_backup/Dofbot/face_tracking_project/face_track_smart_search.py
```

### Option 2: Run Native on Jetson
```bash
cd ~/yahboom_backup/Dofbot/face_tracking_project
pip3 install smbus2 opencv-python --user
python3 face_track_smart_search.py
```

## 📁 Project Structure
```
face_tracking_project/
├── face_track_smart_search.py   # Main tracking script
├── CalibratedArm.py              # Servo calibration wrapper
├── servo_calibration.json        # Calibration offsets
├── setup_all.sh                  # Dependency installer
└── README.md                     # This file
```

## ⚙️ Configuration

### Tracking Parameters (in face_track_smart_search.py)
```python
deadzone_x = 80          # Horizontal tolerance (pixels)
deadzone_y = 80          # Vertical tolerance (pixels)
move_speed = 2           # Degrees per movement
move_every = 2           # Frames between movements
face_history_size = 3    # Smoothing window
```

### Servo Calibration

The `servo_calibration.json` file contains:
- **offsets**: Angle corrections for misaligned servo horns
- **inversions**: Direction reversals for specific servos

To recalibrate:
1. Press K1 button on robot (resets to straight position)
2. Update offsets in `servo_calibration.json`
3. Restart the tracking script

## 🎮 Controls

- **'q'**: Quit the program
- **Ctrl+C**: Emergency stop

## 📸 Initial Position

The robot starts at:
- Base: 45° (left)
- Elbow (Servo 3): 0° (straight up)
- Wrist (Servo 4): 90° (L-shape)

⚠️ **Important**: Press K1 button before starting for proper initialization

## 🔧 Troubleshooting

### Camera Issues
- Check `/dev/video0` exists
- Try `ls -la /dev/video*`

### Servo Not Responding
- Verify I2C bus: `ls -la /dev/i2c*`
- Check calibration file is in correct location
- Ensure torque is enabled

### X11 Display Errors in Docker
- Run `xhost +local:docker` before starting
- Use system opencv: `apt-get install python3-opencv`

## 🎯 Performance

- **Frame Rate**: ~30 FPS
- **Tracking Latency**: ~100ms
- **Movement Speed**: 2°/update (configurable)
- **Search Time**: 2-5 seconds depending on phase

## 📝 Technical Details

### Face Detection
- Algorithm: Haar Cascade (frontal face)
- Parameters: `scaleFactor=1.2, minNeighbors=3, minSize=(50,50)`

### Servo Control
- Communication: I2C Bus 7
- Update Rate: Every 2 frames
- Movement Time: 250ms per command

## 🤝 Contributing

Feel free to open issues or submit pull requests!

## 📄 License

MIT License

## 👨‍💻 Author

Jacques - Electrical Engineering Student
Specializing in VLSI Design, Embedded Systems, and AI
