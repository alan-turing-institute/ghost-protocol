import time
import json
import threading
import websockets.sync.client

SERVER_URL = "ws://10.10.100.91:9000"
KEYS = {"w", "a", "s", "d"}

ws = websockets.sync.client.connect(SERVER_URL)
print(f"Connected to {SERVER_URL}")

# starting position
x = 0
y = 0
z = 0

def move(direction="w"):
    global x, y, z

    for _ in range(10):
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
        msg = {
                "headLocation": {
                    "location": [x, y, z],
                    "timestamp": 1234
                }
            }
        ws.send(json.dumps(msg))
        time.sleep(0.1)
