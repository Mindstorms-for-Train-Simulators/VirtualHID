import pyvjoy
import time

train_controls = pyvjoy.VJoyDevice(1)
THROTTLE = pyvjoy.HID_USAGE_Z

train_controls.set_axis(THROTTLE, 32767)
time.sleep(1)
train_controls.set_axis(THROTTLE, 0)