"""Face detection and landmark streaming using YuNet (OpenCV)."""

from __future__ import annotations

import threading
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from queue import Empty, Queue

import cv2
import numpy as np

_MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
_IOU_THRESHOLD = 0.3  # minimum overlap to consider a detection the same face


@dataclass
class FaceResult:
    """Detected face with eye coordinates in pixel space."""

    left_eye: tuple[float, float]       # (x, y) pixels
    right_eye: tuple[float, float]      # (x, y) pixels
    bbox: tuple[float, float, float, float]  # (x, y, w, h) pixels
    frame_width: int
    frame_height: int
    frame_index: int
    timestamp_ms: int


@dataclass
class StereoResult:
    """Paired face detections from two cameras at the same frame index."""

    frame_index: int
    camera_0: FaceResult | None
    camera_1: FaceResult | None


def _iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    """Compute IoU between two boxes in [x, y, w, h] format."""
    ax1, ay1 = box_a[0], box_a[1]
    ax2, ay2 = ax1 + box_a[2], ay1 + box_a[3]
    bx1, by1 = box_b[0], box_b[1]
    bx2, by2 = bx1 + box_b[2], by1 + box_b[3]

    inter_w = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    inter_h = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = inter_w * inter_h

    union = box_a[2] * box_a[3] + box_b[2] * box_b[3] - inter
    return float(inter / union) if union > 0 else 0.0


def _face_result(face: np.ndarray, w: int, h: int, frame_index: int, timestamp_ms: int) -> FaceResult:
    # YuNet row: [x, y, w, h, re_x, re_y, le_x, le_y, nose_x, nose_y, rm_x, rm_y, lm_x, lm_y, score]
    return FaceResult(
        left_eye=(float(face[6]), float(face[7])),
        right_eye=(float(face[4]), float(face[5])),
        bbox=(float(face[0]), float(face[1]), float(face[2]), float(face[3])),
        frame_width=w,
        frame_height=h,
        frame_index=frame_index,
        timestamp_ms=timestamp_ms,
    )


def _annotate(frame: np.ndarray, face: FaceResult) -> np.ndarray:
    out = frame.copy()
    x, y, w, h = (int(v) for v in face.bbox)
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    for point in (face.left_eye, face.right_eye):
        cv2.circle(out, (int(point[0]), int(point[1])), 4, (0, 0, 255), -1)
    cv2.putText(out, f"f{face.frame_index} t{face.timestamp_ms}ms",
                (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return out


class FaceTracker:
    """Wraps YuNet with IoU-based single-person tracking across frames."""

    def __init__(self, width: int, height: int) -> None:
        self._detector = cv2.FaceDetectorYN.create(
            _download_model(),
            "",
            (width, height),
            score_threshold=0.6,
            nms_threshold=0.3,
            top_k=10,
        )
        self._tracked_box: np.ndarray | None = None  # [x, y, w, h] of current target

    def update(self, frame: np.ndarray, frame_index: int, timestamp_ms: int) -> FaceResult | None:
        h, w = frame.shape[:2]
        self._detector.setInputSize((w, h))
        _, faces = self._detector.detect(frame)

        if faces is None or len(faces) == 0:
            self._tracked_box = None
            return None

        if self._tracked_box is None:
            # no target yet — pick the largest face
            best = max(faces, key=lambda f: f[2] * f[3])
            self._tracked_box = best[:4].copy()
            return _face_result(best, w, h, frame_index, timestamp_ms)

        # find the face with highest IoU against the last known box
        best_face = max(faces, key=lambda f: _iou(f[:4], self._tracked_box))
        best_iou = _iou(best_face[:4], self._tracked_box)

        if best_iou < _IOU_THRESHOLD:
            self._tracked_box = None
            return None

        self._tracked_box = best_face[:4].copy()
        return _face_result(best_face, w, h, frame_index, timestamp_ms)


def _download_model() -> str:
    model_path = Path.home() / ".cache" / "yunet" / "face_detection_yunet_2023mar.onnx"
    if not model_path.exists():
        model_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Downloading YuNet model to {model_path}...")  # noqa: T201
        urllib.request.urlretrieve(_MODEL_URL, model_path)  # noqa: S310
    return str(model_path)


def _camera_worker(
    source: int | str,
    result_queue: Queue,  # type: ignore[type-arg]
    stop_event: threading.Event,
) -> None:
    """Read frames from a source and push (frame_index, FaceResult | None) to the queue."""
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        result_queue.put(None)
        return

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    tracker = FaceTracker(w, h)
    frame_index = 0

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        timestamp_ms = int(frame_index * 1000 / fps)
        face = tracker.update(frame, frame_index, timestamp_ms)
        result_queue.put((frame_index, face))
        frame_index += 1

    cap.release()
    result_queue.put(None)


def run_stream(
    source: int | str = 0,
    on_face: Callable[[FaceResult], None] | None = None,
    output_path: str | None = None,
) -> None:
    """Open a camera or video file and call on_face for each detected face.

    If output_path is given, writes an annotated video with bounding boxes and eye points.
    """
    if on_face is None:
        on_face = print  # type: ignore[assignment]

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        msg = f"Cannot open source {source}"
        raise RuntimeError(msg)

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    tracker = FaceTracker(w, h)
    frame_index = 0

    writer = None
    if output_path is not None:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            timestamp_ms = int(frame_index * 1000 / fps)
            face = tracker.update(frame, frame_index, timestamp_ms)
            frame_index += 1
            if face is not None:
                on_face(face)
                if writer is not None:
                    writer.write(_annotate(frame, face))
            elif writer is not None:
                writer.write(frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()


def run_stereo_stream(
    source_0: int | str,
    source_1: int | str,
    on_stereo: Callable[[StereoResult], None] | None = None,
) -> None:
    """Run face detection on two sources in parallel and emit paired StereoResults."""
    if on_stereo is None:
        def on_stereo(r: StereoResult) -> None:
            if r.camera_0 is not None or r.camera_1 is not None:
                print(r)  # noqa: T201

    queue_0: Queue = Queue()  # type: ignore[type-arg]
    queue_1: Queue = Queue()  # type: ignore[type-arg]
    stop_event = threading.Event()

    t0 = threading.Thread(target=_camera_worker, args=(source_0, queue_0, stop_event), daemon=True)
    t1 = threading.Thread(target=_camera_worker, args=(source_1, queue_1, stop_event), daemon=True)
    t0.start()
    t1.start()

    try:
        while True:
            try:
                item_0 = queue_0.get(timeout=5.0)
                item_1 = queue_1.get(timeout=5.0)
            except Empty:
                break

            if item_0 is None or item_1 is None:
                break

            frame_index_0, face_0 = item_0
            frame_index_1, face_1 = item_1

            on_stereo(StereoResult(
                frame_index=frame_index_0,
                camera_0=face_0,
                camera_1=face_1,
            ))

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        stop_event.set()
        t0.join()
        t1.join()
        cv2.destroyAllWindows()
