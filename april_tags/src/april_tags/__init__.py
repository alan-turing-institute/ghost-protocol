"""Estimate a person's head position in 3D from a single worn AprilTag."""

from __future__ import annotations

from april_tags.config import CameraIntrinsics, HeadOffset, TagConfig
from april_tags.detector import (
    HeadPose,
    HeadPoseEstimator,
    annotate,
    run_stream,
    run_tcp_stream,
)

__all__ = [
    "CameraIntrinsics",
    "HeadOffset",
    "HeadPose",
    "HeadPoseEstimator",
    "TagConfig",
    "annotate",
    "run_stream",
    "run_tcp_stream",
]
