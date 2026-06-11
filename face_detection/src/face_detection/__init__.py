"""
face_detection: real-time face and eye landmark detection.
"""

from __future__ import annotations

from importlib.metadata import version

from face_detection.detector import (
    FaceResult,
    StereoResult,
    run_tcp_stereo_stream,
)

__all__ = (
    "FaceResult",
    "StereoResult",
    "__version__",
    "run_tcp_stereo_stream",
)
__version__ = version(__name__)
