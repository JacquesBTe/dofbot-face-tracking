#!/usr/bin/env python3
import pygame
import sys
import time
import cv2
import threading
sys.path.append('/root/yahboom_backup/Dofbot/0.py_install')
from Arm_Lib import Arm_Device

print("🎮 Gamepad Control for DOFBOT with Camera")
print("=" * 50)
print("Controls:")
print("  Left Stick - Servo 1 (base) & Servo 2 (shoulder)")
print("  Right Stick Up/Down - Servo 6 (gripper)")
print("  Right Stick Left/Right - Servo 5 (wrist rotate)")
print("  L1/L2 - Servo 3 (elbow)")
print("  R1/R2 - Servo 4 (wrist)")
print("  SELECT/BACK - Reset all servos to 90°")
print("  START - Quit")
print("=" * 50)

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("⚠️  Warning: Camera not available")
    camera_available = False
else:
    print("📷 Camera opened successfully")
    camera_available = True

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("❌ No gamepad detected!")
    sys.exit(1)

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"✅ Connected: {joystick.get_name()}")
print(f"   Axes: {joystick.get_numaxes()}")
print(f"   Buttons: {joystick.get_numbuttons()}")

# Initialize arm
Arm = Arm_Device()
time.sleep(0.5)
Arm.Arm_serial_set_torque(1)

# Starting positions
angles = [90, 90, 90, 90, 90, 90]
s_step = 2
s_time = 100

# Move to start position
Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 90, 1000)
time.sleep(1)

print("\n✅ Ready! Use gamepad to control")
if camera_available:
    print("📹 Camera window opened - press 'q' in window to close camera\n")

clock = pygame.time.Clock()
running = True

try:
    while running:
        pygame.event.pump()
        
        # Display camera feed
        if camera_available:
            ret, frame = cap.read()
            if ret:
                # Add angle overlay on camera feed
                y_pos = 30
                for i, angle in enumerate(angles):
                    text = f"Servo {i+1}: {angle}°"
                    cv2.putText(frame, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.6, (0, 255, 0), 2)
                    y_pos += 30
                
                cv2.imshow('DOFBOT Camera', frame)
                
                # Check for 'q' key to close window
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    camera_available = False
                    cv2.destroyAllWindows()
        
        # Get axes (0-5 typically)
        num_axes = joystick.get_numaxes()
        axis0 = joystick.get_axis(0) if num_axes > 0 else 0  # Left X
        axis1 = joystick.get_axis(1) if num_axes > 1 else 0  # Left Y
        axis2 = joystick.get_axis(2) if num_axes > 2 else 0  # Right X or triggers
        axis3 = joystick.get_axis(3) if num_axes > 3 else 0  # Right Y
        
        # Servo 1 (base) - Left stick X
        if abs(axis0) > 0.15:
            if axis0 > 0:
                angles[0] = max(0, angles[0] - s_step)
            else:
                angles[0] = min(180, angles[0] + s_step)
            Arm.Arm_serial_servo_write(1, angles[0], s_time)
        
        # Servo 2 (shoulder) - Left stick Y
        if abs(axis1) > 0.15:
            if axis1 > 0:
                angles[1] = max(0, angles[1] - s_step)
            else:
                angles[1] = min(180, angles[1] + s_step)
            Arm.Arm_serial_servo_write(2, 180-angles[1], s_time)
        
        # Servo 6 (gripper) - Right stick Y
        if abs(axis3) > 0.15:
            if axis3 > 0:
                angles[5] = min(180, angles[5] + s_step)
            else:
                angles[5] = max(0, angles[5] - s_step)
            Arm.Arm_serial_servo_write(6, angles[5], s_time)
        
        # Servo 5 (wrist rotate) - Right stick X
        if abs(axis2) > 0.15:
            if axis2 > 0:
                angles[4] = min(180, angles[4] + s_step)
            else:
                angles[4] = max(0, angles[4] - s_step)
            Arm.Arm_serial_servo_write(5, angles[4], s_time)
        
        # Buttons for Servo 3 and 4
        num_buttons = joystick.get_numbuttons()
        
        # L1/L2 for Servo 3
        if num_buttons > 4 and joystick.get_button(4):
            angles[2] = max(0, angles[2] - s_step)
            Arm.Arm_serial_servo_write(3, angles[2], s_time)
        if num_buttons > 6 and joystick.get_button(6):
            angles[2] = min(180, angles[2] + s_step)
            Arm.Arm_serial_servo_write(3, angles[2], s_time)
        
        # R1/R2 for Servo 4
        if num_buttons > 5 and joystick.get_button(5):
            angles[3] = max(0, angles[3] - s_step)
            Arm.Arm_serial_servo_write(4, angles[3], s_time)
        if num_buttons > 7 and joystick.get_button(7):
            angles[3] = min(180, angles[3] + s_step)
            Arm.Arm_serial_servo_write(4, angles[3], s_time)
        
        # SELECT/BACK button - Reset
        if num_buttons > 8 and joystick.get_button(8):
            print("Resetting to 90°...")
            angles = [90, 90, 90, 90, 90, 90]
            Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 90, 1000)
            time.sleep(1)
        
        # START button - Quit
        if num_buttons > 9 and joystick.get_button(9):
            print("\nQuitting...")
            running = False
        
        clock.tick(20)  # 20 Hz update rate
        
except KeyboardInterrupt:
    print("\n\nStopped by user")

# Cleanup
if camera_available:
    cap.release()
    cv2.destroyAllWindows()
pygame.quit()
Arm.Arm_serial_servo_write6(90, 90, 90, 90, 90, 90, 500)
print("👋 Arm reset to home position")
