import time
import json
import threading
import websockets.sync.client
from pynput import keyboard

SERVER_URL = "ws://10.10.100.91:9000"
KEYS = {"w", "a", "s", "d", "m"}

ws = websockets.sync.client.connect(SERVER_URL)
print(f"Connected to {SERVER_URL}")
print("Use W/A/S/D to send messages. Ctrl+C to quit.")

x = 1.75
y = 5.0
z = 1.7

def move(direction="forward"):

    for _ in range(10):
        if direction == "forward":
            y -= 0.3
        elif direction == "backward":
            y += 0.3
        elif direction == "left":
            x += 0.3
        elif direction == "right":
            x -= 0.3
        msg = {
                "headLocation": {
                    "location": [x, y, z],
                    "timestamp": 1234
                }
            }
        ws.send(json.dumps(msg))



listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()
