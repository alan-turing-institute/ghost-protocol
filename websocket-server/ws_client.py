import time
import json
import threading
import websockets.sync.client
from pynput import keyboard

SERVER_URL = "ws://10.10.100.91:9000"
KEYS = {"w", "a", "s", "d"}

ws = websockets.sync.client.connect(SERVER_URL)
print(f"Connected to {SERVER_URL}")

# starting position
x = 1.75
y = 5.0
z = 1.7

<<<<<<< HEAD
def move(direction="w"):

    for _ in range(10):
        if direction == "w":
            y -= 0.3
        elif direction == "s":
            y += 0.3
        elif direction == "a":
            x += 0.3
        elif direction == "d":
            x -= 0.3
=======
## starting position
#x = 1.75
#y = 5.0
#z = 1.7

def move(direction="w", x=1.75, y=5.0, z=1.7):

    for _ in range(5):
        if direction == "w":
            y -= 0.1
        elif direction == "s":
            y += 0.1
        elif direction == "a":
            x += 0.1
        elif direction == "d":
            x -= 0.1
>>>>>>> 254970d (update ws_client)
        msg = {
                "headLocation": {
                    "location": [x, y, z],
                    "timestamp": 1234
                }
            }
        ws.send(json.dumps(msg))
        time.sleep(0.1)
