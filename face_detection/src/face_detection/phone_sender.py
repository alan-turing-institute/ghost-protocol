"""Run on the phone: detect faces locally and stream coordinates to a laptop via TCP.

The phone acts as a TCP server; the laptop connects to it.

Usage:
    python3 phone_sender.py --port 5006 --source "droidcamsrc mode=2 ! video/x-raw,width=640,height=480 ! videoconvert ! appsink drop=true sync=false"

The laptop then calls run_tcp_coordinate_stream(host=<phone-ip>, port=5006) from _detector_phone.py.
"""

from __future__ import annotations

import argparse
import json
import socket
import time
import urllib.request
from pathlib import Path

import cv2
import numpy as np

_MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
_IOU_THRESHOLD = 0.3


def _download_model() -> str:
    model_path = Path.home() / ".cache" / "yunet" / "face_detection_yunet_2023mar.onnx"
    if not model_path.exists():
        model_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading YuNet model to {model_path}...")
        urllib.request.urlretrieve(_MODEL_URL, model_path)
    return str(model_path)


def _iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    ax1, ay1 = box_a[0], box_a[1]
    ax2, ay2 = ax1 + box_a[2], ay1 + box_a[3]
    bx1, by1 = box_b[0], box_b[1]
    bx2, by2 = bx1 + box_b[2], by1 + box_b[3]
    inter_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    inter_h = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = inter_w * inter_h
    union = box_a[2] * box_a[3] + box_b[2] * box_b[3] - inter
    return float(inter / union) if union > 0 else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5006)
    parser.add_argument(
        "--source", default="0", help="Camera index or GStreamer pipeline"
    )
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    args = parser.parse_args()

    source = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(
        source, cv2.CAP_GSTREAMER if isinstance(source, str) else cv2.CAP_ANY
    )
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open source: {args.source}")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or args.width
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or args.height

    detector = cv2.FaceDetectorYN.create(
        _download_model(),
        "",
        (w, h),
        score_threshold=0.6,
        nms_threshold=0.3,
        top_k=10,
    )
    tracked_box: np.ndarray | None = None

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", args.port))
    server.listen(1)
    print(f"Listening on port {args.port}, waiting for laptop to connect...")
    sock, addr = server.accept()
    print(f"Laptop connected from {addr}. Streaming coordinates.")

    frame_index = 0
    t0 = time.monotonic()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            fh2, fw = frame.shape[:2]
            detector.setInputSize((fw, fh2))
            _, faces = detector.detect(frame)
            timestamp_ms = int((time.monotonic() - t0) * 1000)

            face_row = None
            if faces is not None and len(faces) > 0:
                if tracked_box is None:
                    best = max(faces, key=lambda f: f[2] * f[3])
                else:
                    best = max(faces, key=lambda f: _iou(f[:4], tracked_box))
                    if _iou(best[:4], tracked_box) < _IOU_THRESHOLD:
                        best = None

                if best is not None:
                    tracked_box = best[:4].copy()
                    face_row = best
                else:
                    tracked_box = None
            else:
                tracked_box = None

            payload: dict = {
                "frame_index": frame_index,
                "timestamp_ms": timestamp_ms,
                "frame_width": fw,
                "frame_height": fh2,
                "face": None,
            }
            if face_row is not None:
                payload["face"] = {
                    "bbox": [
                        float(face_row[0]),
                        float(face_row[1]),
                        float(face_row[2]),
                        float(face_row[3]),
                    ],
                    "right_eye": [float(face_row[4]), float(face_row[5])],
                    "left_eye": [float(face_row[6]), float(face_row[7])],
                }

            sock.sendall((json.dumps(payload) + "\n").encode())
            frame_index += 1
    finally:
        cap.release()
        sock.close()
        server.close()


if __name__ == "__main__":
    main()
