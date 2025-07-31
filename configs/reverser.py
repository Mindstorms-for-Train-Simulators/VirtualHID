import pyvjoy
import time

train_controls = pyvjoy.VJoyDevice(1)
REVERSER = pyvjoy.HID_USAGE_X

train_controls.set_axis(REVERSER, 32767)
time.sleep(1)
train_controls.set_axis(REVERSER, 0)