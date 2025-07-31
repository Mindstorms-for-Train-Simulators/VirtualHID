import pyvjoy
import time

train_controls = pyvjoy.VJoyDevice(1)
DYNAMIC_BRAKE = pyvjoy.HID_USAGE_RX

train_controls.set_axis(DYNAMIC_BRAKE, 32767)
time.sleep(1)
train_controls.set_axis(DYNAMIC_BRAKE, 0)