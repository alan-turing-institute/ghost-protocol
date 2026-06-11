"""Phone-side face detection: laptop connects out to the phone as a client.

Use `run_tcp_coordinate_stream` on the laptop when the phone is running the YuNet model and doing the face detection.
The phone runs `phone_sender.py` and streams the FaceResults.
"""

from __future__ import annotations

import json
import socket
from collections.abc import Callable

from face_detection.detector import FaceResult


def run_tcp_coordinate_stream(
    host: str,
    port: int = 5006,
    on_face: Callable[[FaceResult], None] | None = None,
) -> None:
    """Connect to phone_sender.py running on the phone and call on_face for each detected face.

    The phone acts as the TCP server; this function connects as a client.
    """
    if on_face is None:
        on_face = print  # type: ignore[assignment]

    print(f"Connecting to phone at {host}:{port}...")
    sock = socket.create_connection((host, port))
    print("Connected.")

    try:
        buf = ""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk.decode()
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                if payload.get("face") is None:
                    continue
                f = payload["face"]
                on_face(
                    FaceResult(
                        left_eye=tuple(f["left_eye"]),  # type: ignore[arg-type]
                        right_eye=tuple(f["right_eye"]),  # type: ignore[arg-type]
                        bbox=tuple(f["bbox"]),  # type: ignore[arg-type]
                        frame_width=payload["frame_width"],
                        frame_height=payload["frame_height"],
                        frame_index=payload["frame_index"],
                        timestamp_ms=payload["timestamp_ms"],
                    )
                )
    finally:
        sock.close()
