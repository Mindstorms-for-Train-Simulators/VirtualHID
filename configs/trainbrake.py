import pyvjoy
import time

train_controls = pyvjoy.VJoyDevice(1)
TRAIN_BRAKE = pyvjoy.HID_USAGE_RY

train_controls.set_axis(TRAIN_BRAKE, 32767)
time.sleep(1)
train_controls.set_axis(TRAIN_BRAKE, 0)