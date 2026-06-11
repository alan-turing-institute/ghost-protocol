import sys
import tty
import termios
import json
import websockets.sync.client

SERVER_URL = "ws://10.10.100.91:9000"
KEYS = {"w", "a", "s", "d"}

ws = websockets.sync.client.connect(SERVER_URL)
print(f"Connected to {SERVER_URL}")

# starting position
x = 8.66 # 1.75
y = 1.65 # 5.0
z = 9.57 # 1.7

def step(direction):
    global x, y, z

    if direction == "w":
        z -= 0.3
    elif direction == "s":
        z += 0.3
    elif direction == "a":
        x += 0.3
    elif direction == "d":
        x -= 0.3
    elif direction == "q":
        y -= 0.3
    elif direction == "e":
        y += 0.3
    else:
        return  # ignore unknown keys

    msg = {
        "headLocation": {
            "location": [x, y, z],
            "timestamp": 1234
        }
    }
    ws.send(json.dumps(msg))
    print(f"[{direction}] -> x={x:.1f} y={y:.1f} z={z:.1f}", end="\r\n")


def read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


print("WASD/QE to move, ESC or Ctrl-C to quit")
while True:
    key = read_key().lower()
    if key in ("\x1b", "\x03"):  # ESC or Ctrl-C
        break
    step(key)
