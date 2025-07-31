import pyvjoy
import time

train_controls = pyvjoy.VJoyDevice(1)
THROTTLE_BRAKE = pyvjoy.HID_USAGE_Y

train_controls.set_axis(THROTTLE_BRAKE, 32767)
time.sleep(1)
train_controls.set_axis(THROTTLE_BRAKE, 0)