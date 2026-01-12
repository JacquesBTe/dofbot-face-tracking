#!/usr/bin/env python3
import os
os.environ['QT_X11_NO_MITSHM'] = '1'

import sys
import cv2
import time

if os.path.exists('/root/yahboom_backup'):
    base_path = '/root/yahboom_backup/Dofbot'
else:
    base_path = os.path.expanduser('~/yahboom_backup/Dofbot')

sys.path.append(os.path.join(base_path, '5.AI_Visual'))
sys.path.append(base_path)

from CalibratedArm import CalibratedArm

print("👤 Face Tracking with Smart Search")
print("=" * 50)

# Initialize camera FIRST
print("📷 Initializing camera first...")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(2)

# Initialize arm
print("🔧 Initializing arm...")
arm = CalibratedArm()
arm.set_torque(1)
time.sleep(1)

print("📐 Moving to initial position...")
arm.write(1, 45, 1500)
time.sleep(2.5)
arm.write(3, 0, 1500)
time.sleep(2.5)
arm.write(4, 90, 1500)
time.sleep(2.5)

print("✅ Initial position complete!")

base_angle = 45
shoulder_angle = 30
elbow_angle = 0

faceDetect = cv2.CascadeClassifier(os.path.join(base_path, '5.AI_Visual/haarcascade_frontalface_default.xml'))

print("✅ Starting tracking... Press 'q' to quit\n")

center_x = 320
center_y = 240
deadzone_x = 80     # Smaller deadzone (was 100)
deadzone_y = 80     # Smaller deadzone (was 100)
move_speed = 2      # Faster speed (was 1)
move_counter = 0
move_every = 2      # Move more often (was 3)

# Face smoothing - reduced for faster response
face_history = []
face_history_size = 3          # Less smoothing (was 5)
face_confidence_threshold = 2   # Lower threshold (was 3)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(50, 50))
        
        move_counter += 1
        
        # Update face history
        if len(faces) > 0:
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            face_history.append(largest_face)
        else:
            face_history.append(None)
        
        if len(face_history) > face_history_size:
            face_history.pop(0)
        
        recent_faces = [f for f in face_history if f is not None]
        face_detected = len(recent_faces) >= face_confidence_threshold
        
        if face_detected and len(recent_faces) > 0:
            avg_x = sum([f[0] + f[2]//2 for f in recent_faces]) // len(recent_faces)
            avg_y = sum([f[1] + f[3]//2 for f in recent_faces]) // len(recent_faces)
            
            (x, y, w, h) = recent_faces[-1]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            cv2.circle(frame, (avg_x, avg_y), 8, (0, 0, 255), -1)
            
            error_x = avg_x - center_x
            error_y = avg_y - center_y
            
            cv2.putText(frame, f'TRACKING | Base:{base_angle}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if move_counter >= move_every:
                move_counter = 0
                
                if abs(error_x) > deadzone_x:
                    if error_x > 0:
                        base_angle = max(20, base_angle - move_speed)
                    else:
                        base_angle = min(160, base_angle + move_speed)
                    arm.write(1, base_angle, 250)  # Faster movement time
                
                if abs(error_y) > deadzone_y:
                    if error_y > 0:
                        shoulder_angle = min(60, shoulder_angle + move_speed)
                    else:
                        shoulder_angle = max(5, shoulder_angle - move_speed)
                    arm.write(2, shoulder_angle, 250)  # Faster movement time
        else:
            cv2.putText(frame, 'No face detected', (10, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.line(frame, (center_x, 0), (center_x, 480), (255, 0, 0), 1)
        cv2.line(frame, (0, center_y), (640, center_y), (255, 0, 0), 1)
        
        cv2.imshow('Smart Face Tracking', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        time.sleep(0.03)

except KeyboardInterrupt:
    print("\n👋 Stopping...")

cap.release()
cv2.destroyAllWindows()
print("✅ Done!")
