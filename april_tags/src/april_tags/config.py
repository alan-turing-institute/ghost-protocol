"""Camera intrinsics and tag/head geometry, with JSON (de)serialisation.

All distances are in metres and all coordinates follow OpenCV's camera
convention: +x right, +y down, +z forward (away from the camera, into the
scene).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class CameraIntrinsics:
    """Pinhole camera model produced by :mod:`april_tags.calibrate`."""

    fx: float  # focal length in pixels (x)
    fy: float  # focal length in pixels (y)
    cx: float  # principal point x (pixels)
    cy: float  # principal point y (pixels)
    dist_coeffs: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0, 0.0])
    image_width: int | None = None
    image_height: int | None = None

    @property
    def camera_matrix(self) -> np.ndarray:
        """Return the 3x3 intrinsic matrix K."""
        return np.array(
            [
                [self.fx, 0.0, self.cx],
                [0.0, self.fy, self.cy],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )

    @property
    def dist(self) -> np.ndarray:
        """Return distortion coefficients as a row vector for cv2.solvePnP."""
        return np.array(self.dist_coeffs, dtype=np.float64).reshape(1, -1)

    def save(self, path: str | Path) -> None:
        """Write intrinsics to a JSON file."""
        Path(path).write_text(json.dumps(self.__dict__, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> CameraIntrinsics:
        """Read intrinsics from a JSON file written by :meth:`save`."""
        data = json.loads(Path(path).read_text())
        return cls(**data)


@dataclass
class TagConfig:
    """Physical AprilTag the person is wearing.

    `size_m` is the side length of the tag's solid black square, measured on
    the *printed* tag with a ruler — not the nominal size you asked the printer
    for. solvePnP scales the whole position estimate by this number, so a 5%
    error here is a 5% error in reported distance.
    """

    tag_id: int = 0
    size_m: float = 0.10  # 10 cm black square — measure your printout to confirm


@dataclass
class HeadOffset:
    """Vector from the tag centre to the head centre, in the *tag's* own frame.

    Tag frame (looking at the printed tag head-on): +x points right, +y points
    up, +z points out of the tag towards the camera. So for a tag worn flat on
    the forehead and facing the camera, the head centre is slightly *below* the
    tag (-y) and *behind* it, into the skull (-z).

    Defaults assume the tag is mounted on a cap/headband over the forehead.
    Re-measure for your own rig and placement.
    """

    x: float = 0.0
    y: float = -0.07  # head centre ~7 cm below the forehead tag
    z: float = -0.10  # head centre ~10 cm behind the forehead surface

    def as_vector(self) -> np.ndarray:
        """Return the offset as a 3x1 column vector in the tag frame."""
        return np.array([[self.x], [self.y], [self.z]], dtype=np.float64)
