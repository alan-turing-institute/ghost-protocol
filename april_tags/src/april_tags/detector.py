"""AprilTag-based head position estimation from a single camera.

A single AprilTag of known physical size gives a full 6-DoF pose from one
camera (no stereo needed), because the tag's size fixes the scale. We detect
the tag, recover its pose with solvePnP, then apply a fixed tag->head offset to
report where the person's head is in the camera's coordinate frame.

Coordinate frame of the result (OpenCV camera convention):
  +x right, +y down, +z forward (away from the camera). Units: metres.

Use `run_stream()` for a local webcam or video file, or `run_tcp_stream()` to
consume the same size-prefixed JPEG TCP feed as
`face_detection.detector` (the phone streams frames; this host does the work).
"""

from __future__ import annotations

import socket
import struct
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from queue import Empty, Queue

import cv2
import numpy as np

from april_tags.config import CameraIntrinsics, HeadOffset, TagConfig

_STREAM_DONE = object()  # sentinel pushed to queues when a worker exits

# AprilTag family. 36h11 is the recommended general-purpose family: large
# Hamming distance, low false-positive rate, and the default for most toolkits.
_TAG_DICT = cv2.aruco.DICT_APRILTAG_36h11


@dataclass
class HeadPose:
    """Estimated head position derived from a detected tag.

    Positions are in metres in the camera frame (+x right, +y down, +z forward).
    """

    head_xyz: tuple[float, float, float]  # head centre in camera frame
    tag_xyz: tuple[float, float, float]  # tag centre in camera frame
    distance_m: float  # straight-line distance from camera to the head
    tag_id: int
    frame_width: int
    frame_height: int
    timestamp_ms: int
    rvec: np.ndarray  # tag orientation (Rodrigues) in the camera frame
    tvec: np.ndarray  # tag translation in the camera frame


def _object_points(size_m: float) -> np.ndarray:
    """Return the tag's 4 corner coordinates in its own frame.

    Order matches cv2.aruco corner order (top-left, top-right, bottom-right,
    bottom-left) and the layout cv2.SOLVEPNP_IPPE_SQUARE expects. The tag lies
    in the z=0 plane with +x right and +y up.
    """
    h = size_m / 2.0
    return np.array(
        [
            [-h, h, 0.0],
            [h, h, 0.0],
            [h, -h, 0.0],
            [-h, -h, 0.0],
        ],
        dtype=np.float64,
    )


class HeadPoseEstimator:
    """Detect the target AprilTag and report the wearer's head position."""

    def __init__(
        self,
        intrinsics: CameraIntrinsics,
        tag: TagConfig | None = None,
        offset: HeadOffset | None = None,
    ) -> None:
        """Configure the estimator with camera, tag, and tag->head geometry."""
        self._intrinsics = intrinsics
        self._tag = tag or TagConfig()
        self._offset = offset or HeadOffset()
        self._object_points = _object_points(self._tag.size_m)

        dictionary = cv2.aruco.getPredefinedDictionary(_TAG_DICT)
        params = cv2.aruco.DetectorParameters()
        # Sub-pixel corner refinement noticeably steadies the pose at distance.
        params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self._detector = cv2.aruco.ArucoDetector(dictionary, params)

    def update(self, frame: np.ndarray, timestamp_ms: int) -> HeadPose | None:
        """Return the head pose for the target tag, or None if it isn't visible."""
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self._detector.detectMarkers(gray)

        if ids is None:
            return None

        match = self._select_target(corners, ids)
        if match is None:
            return None

        image_points = match.reshape(4, 2).astype(np.float64)
        solved = self._solve_pose(image_points)
        if solved is None:
            return None
        rvec, tvec, rotation = solved

        # Map the tag-frame offset into the camera frame and add it to the tag
        # centre to get the head position.
        head = (tvec + rotation @ self._offset.as_vector()).flatten()
        tag = tvec.flatten()
        head_xyz = (float(head[0]), float(head[1]), float(head[2]))
        tag_xyz = (float(tag[0]), float(tag[1]), float(tag[2]))

        return HeadPose(
            head_xyz=head_xyz,
            tag_xyz=tag_xyz,
            distance_m=float(np.linalg.norm(head)),
            tag_id=self._tag.tag_id,
            frame_width=w,
            frame_height=h,
            timestamp_ms=timestamp_ms,
            rvec=rvec,
            tvec=tvec,
        )

    def _solve_pose(
        self, image_points: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
        """Recover (rvec, tvec, R) for the tag, resolving the planar ambiguity.

        SOLVEPNP_IPPE_SQUARE yields two solutions for a planar square. Only one
        has the tag's printed face pointing back towards the camera (the only
        way we could be seeing it), so we keep the solution whose tag normal has
        the most negative z in the camera frame. This avoids frame-to-frame
        orientation flips that would otherwise throw the head offset the wrong
        way for near-head-on tags.
        """
        _, rvecs, tvecs, _ = cv2.solvePnPGeneric(
            self._object_points,
            image_points,
            self._intrinsics.camera_matrix,
            self._intrinsics.dist,
            flags=cv2.SOLVEPNP_IPPE_SQUARE,
        )
        if not rvecs:
            return None

        best: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None
        best_normal_z = np.inf
        for rvec, tvec in zip(rvecs, tvecs, strict=False):
            rotation, _ = cv2.Rodrigues(rvec)
            normal_z = rotation[2, 2]  # camera-frame z of the tag's +z (normal)
            if normal_z < best_normal_z:
                best_normal_z = normal_z
                best = (rvec, tvec, rotation)
        return best

    def _select_target(
        self, corners: Sequence[np.ndarray], ids: np.ndarray
    ) -> np.ndarray | None:
        """Return the corners of the configured tag id, if present."""
        for tag_corners, tag_id in zip(corners, ids.flatten(), strict=False):
            if int(tag_id) == self._tag.tag_id:
                return tag_corners
        return None


def annotate(
    frame: np.ndarray, pose: HeadPose, intrinsics: CameraIntrinsics
) -> np.ndarray:
    """Draw the tag axes and a head-position read-out onto a copy of frame."""
    out = frame.copy()
    cv2.drawFrameAxes(
        out,
        intrinsics.camera_matrix,
        intrinsics.dist,
        pose.rvec,
        pose.tvec,
        length=0.05,
    )
    x, y, z = pose.head_xyz
    _draw_head_point(out, pose, intrinsics)
    lines = [
        f"tag #{pose.tag_id}",
        f"head x={x:+.2f} y={y:+.2f} z={z:+.2f} m",
        f"dist {pose.distance_m:.2f} m",
    ]
    _draw_status(out, lines, color=(0, 255, 0))
    return out


def annotate_missing(frame: np.ndarray, tag_id: int) -> np.ndarray:
    """Draw a preview overlay for frames where the target tag is not visible."""
    out = frame.copy()
    _draw_status(out, [f"tag #{tag_id} not detected"], color=(0, 180, 255))
    return out


def _draw_status(
    frame: np.ndarray, lines: Sequence[str], color: tuple[int, int, int]
) -> None:
    """Draw legible status text on top of a translucent backing panel."""
    width = 20 + max(
        cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0]
        for line in lines
    )
    height = 22 + len(lines) * 28
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), thickness=-1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, dst=frame)
    for i, line in enumerate(lines):
        cv2.putText(
            frame,
            line,
            (10, 30 + i * 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )


def _draw_head_point(
    frame: np.ndarray, pose: HeadPose, intrinsics: CameraIntrinsics
) -> None:
    """Project the estimated head centre into the image and mark it."""
    x, y, z = pose.head_xyz
    if z <= 0:
        return
    px = round(intrinsics.fx * x / z + intrinsics.cx)
    py = round(intrinsics.fy * y / z + intrinsics.cy)
    if 0 <= px < pose.frame_width and 0 <= py < pose.frame_height:
        cv2.drawMarker(
            frame,
            (px, py),
            (255, 0, 255),
            markerType=cv2.MARKER_CROSS,
            markerSize=24,
            thickness=2,
        )
        cv2.circle(frame, (px, py), 8, (255, 0, 255), 2)


def _default_on_head(pose: HeadPose) -> None:
    """Print a one-line summary of a head pose."""
    x, y, z = pose.head_xyz
    print(
        f"t{pose.timestamp_ms}ms  head=({x:+.3f}, {y:+.3f}, {z:+.3f}) m  "
        f"dist={pose.distance_m:.3f} m"
    )


def run_stream(
    intrinsics: CameraIntrinsics,
    source: int | str = 0,
    tag: TagConfig | None = None,
    offset: HeadOffset | None = None,
    on_head: Callable[[HeadPose], None] | None = None,
    show: bool = True,
) -> None:
    """Open a webcam (int index) or video file (path) and estimate head pose.

    Press 'q' in the preview window to quit.
    """
    on_head = on_head or _default_on_head
    active_tag = tag or TagConfig()
    estimator = HeadPoseEstimator(intrinsics, tag, offset)

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        msg = f"Cannot open source {source}"
        raise RuntimeError(msg)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            timestamp_ms = int(frame_count * 1000 / fps)
            pose = estimator.update(frame, timestamp_ms)
            frame_count += 1
            if pose is not None:
                on_head(pose)
            if show:
                display = (
                    annotate(frame, pose, intrinsics)
                    if pose
                    else annotate_missing(frame, active_tag.tag_id)
                )
                cv2.imshow("april_tags head pose", display)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Read exactly n bytes from sock, raising EOFError if the connection closes."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError("TCP connection closed")
        buf.extend(chunk)
    return bytes(buf)


def _tcp_worker(
    host: str,
    port: int,
    estimator: HeadPoseEstimator,
    result_queue: Queue,  # type: ignore[type-arg]
    stop_event: threading.Event,
) -> None:
    """Connect to a TCP stream of size-prefixed JPEGs and estimate head pose."""
    try:
        print(f"Creating connection to {host}:{port}")
        sock = socket.create_connection((host, port))
    except OSError as e:
        print(f"Error caught, exiting. Error details: {e}")
        result_queue.put(_STREAM_DONE)
        return

    try:
        while not stop_event.is_set():
            size_bytes = _recv_exact(sock, 4)
            size = struct.unpack(">I", size_bytes)[0]
            jpeg = _recv_exact(sock, size)

            frame = cv2.imdecode(np.frombuffer(jpeg, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                sock.sendall(b"Done!\n")
                continue

            timestamp_ms = int(time.time() * 1000)
            pose = estimator.update(frame, timestamp_ms)
            result_queue.put(pose)
            sock.sendall(b"Done!\n")  # ACK — phone may now send the next frame
    except EOFError:
        pass
    finally:
        sock.close()
        result_queue.put(_STREAM_DONE)


def run_tcp_stream(
    intrinsics: CameraIntrinsics,
    host: str,
    port: int,
    tag: TagConfig | None = None,
    offset: HeadOffset | None = None,
    on_head: Callable[[HeadPose], None] | None = None,
) -> None:
    """Connect to a single TCP JPEG stream and call on_head for each head pose.

    Mirrors `face_detection.detector.run_tcp_stream`: the phone streams JPEG
    frames (4-byte big-endian length prefix, then the JPEG) and this host runs
    detection, ACKing each frame with ``b"Done!\\n"``.
    """
    on_head = on_head or _default_on_head
    estimator = HeadPoseEstimator(intrinsics, tag, offset)

    queue: Queue = Queue()  # type: ignore[type-arg]
    stop_event = threading.Event()
    worker = threading.Thread(
        target=_tcp_worker,
        args=(host, port, estimator, queue, stop_event),
        daemon=True,
    )
    worker.start()

    print(f"Connecting to {host}:{port}...")
    try:
        while True:
            item = queue.get(timeout=10.0)
            if item is _STREAM_DONE:
                print("Connection closed.")
                break
            if item is not None:
                on_head(item)
    except Empty:
        print("Timed out waiting for frames.")
    finally:
        stop_event.set()
        worker.join()
