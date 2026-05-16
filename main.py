# terminal code for ease: python -m auto_py_to_exe

import socket
import json
import pyvjoy
from pynput.keyboard import Controller, KeyCode, Key

HOST = "0.0.0.0"
PORT = 1337

# vJoy axis mappings (0–32767)
train_controls = pyvjoy.VJoyDevice(1)
REVERSER = pyvjoy.HID_USAGE_X
THROTTLE_BRAKE = pyvjoy.HID_USAGE_Y
THROTTLE = pyvjoy.HID_USAGE_Z
DYNAMIC_BRAKE = pyvjoy.HID_USAGE_RX
TRAIN_BRAKE = pyvjoy.HID_USAGE_RY
LOCO_BRAKE = pyvjoy.HID_USAGE_RZ

KEYS = {"alt": Key.alt, "altleft": Key.alt_l, "altright": Key.alt_r, "backspace": Key.backspace, "capslock": Key.caps_lock, "cmd": Key.cmd, "cmdleft": Key.cmd_l,
        "cmdright": Key.cmd_r, "ctrl": Key.ctrl, "ctrlleft": Key.ctrl_l, "ctrlright": Key.ctrl_r, "delete": Key.delete, "down": Key.down, "end": Key.end, 
        "enter": Key.enter, "escape": Key.esc, "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4, "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8, "f9": Key.f9, 
        "f10": Key.f10, "f11": Key.f11, "f12": Key.f12, "home": Key.home, "insert": Key.insert, "left": Key.left, "pagedown": Key.page_down, "pageup": Key.page_up, 
        "right": Key.right, "shift": Key.shift, "shiftleft": Key.shift_l, "shiftright": Key.shift_r, "space": Key.space, "tab": Key.tab, "up": Key.up, "n0": KeyCode.from_vk(96),
        "n1": KeyCode.from_vk(97), "n2": KeyCode.from_vk(98), "n3": KeyCode.from_vk(99), "n4": KeyCode.from_vk(100), "n5": KeyCode.from_vk(101), "n6": KeyCode.from_vk(102),
        "n7": KeyCode.from_vk(103), "n8": KeyCode.from_vk(104), "n9": KeyCode.from_vk(105), "decimal": KeyCode.from_vk(110), "multiply": KeyCode.from_vk(106),
        "add": KeyCode.from_vk(107), "subtract": KeyCode.from_vk(109), "divide": KeyCode.from_vk(111), "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7",
        "8": "8", "9": "9", "0": "0", "-": "-", "=": "=", "`": "`", "a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f", "g": "g", "h": "h", "i": "i", "j": "j", "k": "k",
        "l": "l", "m": "m", "n": "n", "o": "o", "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "u": "u", "v": "v", "w": "w", "x": "x", "y": "y", "z": "z", "[": "[", "]": "]",
        ";": ";", "'": "'", ",": ",", ".": ".", "/": "/", "\\": "\\"}

keyboard = Controller()

def assignLevers(name):
    return {
        "Reverser": REVERSER,
        "ThrottleAndBrake": THROTTLE_BRAKE,
        "Throttle": THROTTLE,
        "DynamicBrake": DYNAMIC_BRAKE,
        "TrainBrake": TRAIN_BRAKE,
        "LocoBrake": LOCO_BRAKE
    }.get(name, None)

def apply_axis(axis, value):
    if axis is None:
        return
    scaled = int(((value + 100) / 200) * 32767)
    scaled = max(0, min(32767, scaled))
    train_controls.set_axis(axis, scaled)

def start_server():
    print(f"[INFO] Starting server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)

        while True:
            print("[WAIT] Awaiting EV3 connection...")
            conn, addr = server.accept()
            print(f"[CONNECTED] From {addr}")

            try:
                handle_client(conn)
            except Exception as e:
                print(f"[ERROR] Server error: {e}")
            finally:
                print("[INFO] Connection closed.")

def handle_client(conn):
    with conn:
        buffer = b""
        pressed_keys = set()
        left = middle = right = None

        while True:
            chunk = conn.recv(1024)
            if not chunk:
                print("[DISCONNECT] EV3 disconnected.")
                break

            buffer += chunk
            lines = buffer.split(b'\n')
            buffer = lines.pop()  # Save incomplete line

            for line in lines:
                if not line.strip():
                    continue

                try:
                    msg = json.loads(line.decode())
                    print(f"[RECV] {msg}")

                    if msg.get("type") == "CONFIG":
                        left = assignLevers(msg.get("left"))
                        middle = assignLevers(msg.get("middle"))
                        right = assignLevers(msg.get("right"))
                        color = assignLevers(msg.get("color"))
                        print(f"[CONFIG] Left: {msg.get('left')} => {left}")
                        print(f"[CONFIG] Middle: {msg.get('middle')} => {middle}")
                        print(f"[CONFIG] Right: {msg.get('right')} => {right}")
                        print(f"[CONFIG] Color: {msg.get('color')} => {color}")

                    elif msg.get("type") == "DATA":
                        apply_axis(left, msg.get("left", 0))
                        apply_axis(middle, msg.get("middle", 0))
                        apply_axis(right, msg.get("right", 0))
                        color_value = msg.get("color", 0)
                        if isinstance(color_value, str):
                            color_value = { "Color.BLACK": -100, "Color.RED": -60, "Color.YELLOW": -20, "Color.GREEN": 20, "Color.BLUE": 60, "Color.WHITE": 100, "Color.BLACKinv": 100, "Color.REDinv": 60, "Color.YELLOWinv": 20, "Color.GREENinv": -20, "Color.BLUEinv": -60, "Color.WHITEinv": -100}.get(color_value, 0)
                        apply_axis(color, color_value)

                        current_keys = set(msg.get("buttons", []))

                        for key in current_keys - pressed_keys:
                            print(f"[KEYDOWN] {key}")

                            for action in key.split("+"):
                                keyboard.press(KEYS[action])

                        for key in pressed_keys - current_keys:
                            print(f"[KEYUP] {key}")

                            for action in reversed(key.split("+")):
                                keyboard.release(KEYS[action])

                        pressed_keys = current_keys

                    elif msg.get("type") == "END":
                        print("[INFO] Received END message.")
                        return

                    else:
                        print(f"[WARN] Unknown message type: {msg.get('type')}")

                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON decode error: {e}")
                except Exception as e:
                    print(f"[ERROR] Message handling error: {e}")

# Main entry point
if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[EXIT] Server stopped by user.")
