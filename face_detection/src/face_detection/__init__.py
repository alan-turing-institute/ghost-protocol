"""
face_detection: real-time face and eye landmark detection.
"""

from __future__ import annotations

from importlib.metadata import version

from face_detection.detector import FaceResult, StereoResult, run_stereo_stream, run_stream, run_tcp_stereo_stream

__all__ = ("__version__", "FaceResult", "StereoResult", "run_stereo_stream", "run_stream", "run_tcp_stereo_stream")
__version__ = version(__name__)
