import threading
import websockets.sync.client
from pynput import keyboard

SERVER_URL = "ws://localhost:9000"
KEYS = {"w", "a", "s", "d"}

ws = websockets.sync.client.connect(SERVER_URL)
print(f"Connected to {SERVER_URL}")
print("Use W/A/S/D to send messages. Ctrl+C to quit.")


messages = {
    "w": {"x": 0, "y":0, "z": 10, "speed": 10},
    "a": {"x": 0, "y":0, "z": -10, "speed": 10},
    "s": {"x": -10, "y":0, "z": 0, "speed": 10},
    "d": {"x": 10, "y":0, "z": 0, "speed": 10}
}

def on_press(key):
    try:
        char = key.char
        if char in KEYS:
            ws.send(f"{messages[char]}")
            print(f"[>] {messages[char]}")
    except AttributeError:
        pass



listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()
