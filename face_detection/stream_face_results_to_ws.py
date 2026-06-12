"""Get images over TCP, process them using YuNet, then stream face detection results over WebSocket."""

from face_detection.detector import run_tcp_stereo_stream
from face_detection.ws_sender import WebSocketClient

CAMERA_0 = "10.10.100.86"
CAMERA_1 = "10.10.100.154"
PORT = 9991
WS_SERVER = "ws://localhost:9000"

sender = WebSocketClient(WS_SERVER)
try:
    run_tcp_stereo_stream(CAMERA_0, PORT, CAMERA_1, PORT, on_stereo=sender)
except KeyboardInterrupt:
    pass
finally:
    sender.close()
