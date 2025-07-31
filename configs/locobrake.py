import pyvjoy
import time

train_controls = pyvjoy.VJoyDevice(1)
LOCO_BRAKE = pyvjoy.HID_USAGE_RZ

train_controls.set_axis(LOCO_BRAKE, 32767)
time.sleep(1)
train_controls.set_axis(LOCO_BRAKE, 0)