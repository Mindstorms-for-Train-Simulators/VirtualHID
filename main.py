import socket
import json
import pyvjoy
import keyboard

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
                        apply_axis(color, msg.get("color", 0))

                        current_keys = set(msg.get("buttons", []))

                        for key in current_keys - pressed_keys:
                            print(f"[KEYDOWN] {key}")
                            keyboard.press(key)

                        for key in pressed_keys - current_keys:
                            print(f"[KEYUP] {key}")
                            keyboard.release(key)

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
