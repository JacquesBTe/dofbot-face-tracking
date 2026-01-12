#!/bin/bash
echo "🚀 Setting up DOFBOT environment..."
echo "=================================="

# Install dependencies
echo "📦 Installing dependencies..."
apt-get update -qq

if ! command -v pip3 &> /dev/null; then
    echo "  Installing pip3..."
    apt-get install -y python3-pip > /dev/null 2>&1
fi

echo "  Installing xcb/Qt libraries..."
apt-get install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-shape0 libxcb-xfixes0 libgl1-mesa-glx libglib2.0-0 > /dev/null 2>&1

echo "  Installing Python packages..."
pip3 install -q smbus2 opencv-python

echo "✅ Dependencies installed!"

# Setup calibration
echo ""
echo "🔧 Setting up calibration..."
cat > /root/servo_calibration.json << 'CALEOF'
{
  "offsets": {
    "1": -1,
    "2": 91,
    "3": -89,
    "4": 1,
    "5": 0,
    "6": 87
  },
  "inversions": {
    "1": false,
    "2": false,
    "3": false,
    "4": false,
    "5": false,
    "6": false
  }
}
CALEOF

cat > /root/CalibratedArm.py << 'PYEOF'
#!/usr/bin/env python3
import sys
import json
sys.path.append('/root/yahboom_backup/Dofbot/0.py_install')
from Arm_Lib import Arm_Device

class CalibratedArm:
    def __init__(self, cal_file='/root/servo_calibration.json'):
        self.arm = Arm_Device()
        try:
            with open(cal_file, 'r') as f:
                cal = json.load(f)
            self.offsets = {int(k): v for k, v in cal['offsets'].items()}
            self.inversions = {int(k): v for k, v in cal['inversions'].items()}
        except:
            self.offsets = {i: 0 for i in range(1, 7)}
            self.inversions = {i: False for i in range(1, 7)}
    
    def _apply_calibration(self, servo_id, angle):
        if self.inversions.get(servo_id, False):
            angle = 180 - angle
        actual_angle = angle + self.offsets.get(servo_id, 0)
        return max(0, min(180, actual_angle))
    
    def write(self, servo_id, angle, time_ms=1000):
        actual_angle = self._apply_calibration(servo_id, angle)
        return self.arm.Arm_serial_servo_write(servo_id, actual_angle, time_ms)
    
    def write6(self, a1, a2, a3, a4, a5, a6, time_ms=1000):
        angles = [a1, a2, a3, a4, a5, a6]
        actual_angles = [self._apply_calibration(i, angle) for i, angle in enumerate(angles, start=1)]
        return self.arm.Arm_serial_servo_write6(*actual_angles, time_ms)
    
    def read(self, servo_id):
        actual = self.arm.Arm_serial_servo_read(servo_id)
        if actual is None:
            return None
        angle = actual - self.offsets.get(servo_id, 0)
        if self.inversions.get(servo_id, False):
            angle = 180 - angle
        return angle
    
    def set_torque(self, enable):
        return self.arm.Arm_serial_set_torque(enable)
PYEOF

# Copy calibration files to /root/yahboom_backup for persistence
cp /root/servo_calibration.json /root/yahboom_backup/
cp /root/CalibratedArm.py /root/yahboom_backup/

echo "✅ Calibration files created and saved!"
echo ""
echo "=================================="
echo "✅ Setup complete!"
echo "=================================="
