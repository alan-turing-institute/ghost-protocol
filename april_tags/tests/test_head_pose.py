"""Tests for the camera-independent geometry and detection logic.

These render a synthetic tag into a blank image with a known pose, then check
that the estimator recovers that pose and applies the head offset correctly.
No real camera is needed.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from april_tags.config import CameraIntrinsics, HeadOffset, TagConfig
from april_tags.detector import _TAG_DICT, annotate, annotate_missing, HeadPoseEstimator


@pytest.fixture
def intrinsics() -> CameraIntrinsics:
    """A simple, distortion-free 640x480 pinhole camera."""
    return CameraIntrinsics(fx=600.0, fy=600.0, cx=320.0, cy=240.0)


def _render_tag(
    intrinsics: CameraIntrinsics,
    tag_size: float,
    distance_m: float,
    tag_id: int = 0,
    image_size: tuple[int, int] = (640, 480),
) -> np.ndarray:
    """Render a fronto-parallel, centred tag at the given distance.

    For a tag facing the camera on the optical axis, perspective projection
    reduces to a uniform scale: its side projects to fx * size / distance
    pixels. We paste a marker of that size into the centre of a white frame,
    which keeps the printed code upright and detectable.
    """
    w, h = image_size
    marker = cv2.aruco.generateImageMarker(
        cv2.aruco.getPredefinedDictionary(_TAG_DICT), tag_id, 400
    )

    side = round(intrinsics.fx * tag_size / distance_m)
    marker = cv2.resize(marker, (side, side), interpolation=cv2.INTER_NEAREST)

    canvas = np.full((h, w), 255, dtype=np.uint8)
    cx, cy = int(intrinsics.cx), int(intrinsics.cy)
    top, left = cy - side // 2, cx - side // 2
    canvas[top : top + side, left : left + side] = marker
    return cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)


def test_recovers_distance(intrinsics: CameraIntrinsics) -> None:
    """A tag rendered at a known distance is recovered to within ~2%."""
    tag = TagConfig(tag_id=0, size_m=0.10)
    estimator = HeadPoseEstimator(intrinsics, tag, HeadOffset(0.0, 0.0, 0.0))
    frame = _render_tag(intrinsics, tag.size_m, distance_m=0.6)

    pose = estimator.update(frame, timestamp_ms=0)

    assert pose is not None
    assert pose.tag_xyz[2] == pytest.approx(0.6, rel=0.02)
    # Centred tag → head x/y near zero with a zero offset.
    assert pose.tag_xyz[0] == pytest.approx(0.0, abs=0.02)
    assert pose.tag_xyz[1] == pytest.approx(0.0, abs=0.02)


def test_offset_is_applied(intrinsics: CameraIntrinsics) -> None:
    """The tag->head offset shifts the head relative to the tag centre."""
    tag = TagConfig(tag_id=0, size_m=0.10)
    # Tag faces the camera with no rotation, so tag-frame +y (up) maps to
    # camera-frame -y, and tag-frame -z maps to camera-frame -z.
    offset = HeadOffset(x=0.0, y=-0.07, z=-0.10)
    estimator = HeadPoseEstimator(intrinsics, tag, offset)
    frame = _render_tag(intrinsics, tag.size_m, distance_m=0.6)

    pose = estimator.update(frame, timestamp_ms=0)

    assert pose is not None
    # The tag's printed face points at the camera, so its +z (normal) points
    # back towards the camera. A forehead tag's head centre is 7 cm down and
    # 10 cm into the skull, i.e. 10 cm *further* from the camera than the tag.
    assert pose.head_xyz[1] == pytest.approx(pose.tag_xyz[1] + 0.07, abs=0.02)
    assert pose.head_xyz[2] == pytest.approx(pose.tag_xyz[2] + 0.10, abs=0.02)


def test_wrong_tag_id_returns_none(intrinsics: CameraIntrinsics) -> None:
    """A frame with only tag 0 yields nothing when we look for tag 5."""
    estimator = HeadPoseEstimator(intrinsics, TagConfig(tag_id=5, size_m=0.10))
    frame = _render_tag(intrinsics, 0.10, distance_m=1.5, tag_id=0)

    assert estimator.update(frame, timestamp_ms=0) is None


def test_no_tag_returns_none(intrinsics: CameraIntrinsics) -> None:
    """A blank frame yields no detection."""
    estimator = HeadPoseEstimator(intrinsics, TagConfig(tag_id=0, size_m=0.10))
    blank = np.full((480, 640, 3), 255, dtype=np.uint8)

    assert estimator.update(blank, timestamp_ms=0) is None


def test_preview_overlays_draw_on_frames(intrinsics: CameraIntrinsics) -> None:
    """Overlay helpers modify a copy of the input frame."""
    tag = TagConfig(tag_id=0, size_m=0.10)
    estimator = HeadPoseEstimator(intrinsics, tag, HeadOffset(0.0, 0.0, 0.0))
    frame = _render_tag(intrinsics, tag.size_m, distance_m=0.6)
    pose = estimator.update(frame, timestamp_ms=0)

    assert pose is not None
    annotated = annotate(frame, pose, intrinsics)
    missing = annotate_missing(frame, tag.tag_id)

    assert np.any(annotated != frame)
    assert np.any(missing != frame)


def test_intrinsics_roundtrip(tmp_path, intrinsics: CameraIntrinsics) -> None:
    """Saving and loading intrinsics preserves the values."""
    path = tmp_path / "camera.json"
    intrinsics.dist_coeffs = [0.1, -0.2, 0.001, 0.002, 0.05]
    intrinsics.save(path)
    loaded = CameraIntrinsics.load(path)

    assert loaded == intrinsics
    np.testing.assert_allclose(loaded.camera_matrix, intrinsics.camera_matrix)
