"""Generate a printable AprilTag image (family 36h11).

The saved PNG is the raw marker plus a white quiet-zone border (the detector
needs that border). Print it at 100% scale / "actual size" — do NOT let your
printer "fit to page", or the physical size will not match what you configure.
After printing, measure the side of the solid black square with a ruler and put
that value (in metres) into TagConfig.size_m.
"""

from __future__ import annotations

import cv2

from april_tags.detector import _TAG_DICT


def generate_tag(
    tag_id: int = 0,
    pixels: int = 1200,
    border_squares: int = 1,
    path: str = "tag.png",
) -> str:
    """Write an AprilTag PNG with a white quiet zone and return its path.

    `border_squares` is the white margin width in units of the tag's internal
    bit-squares (1 is the recommended minimum quiet zone).
    """
    dictionary = cv2.aruco.getPredefinedDictionary(_TAG_DICT)
    marker = cv2.aruco.generateImageMarker(dictionary, tag_id, pixels)

    # A 36h11 tag is 10 squares wide (8 data + 2 border); size one quiet-zone
    # square to match so the printed border is a clean multiple.
    square = pixels // 10
    pad = square * border_squares
    bordered = cv2.copyMakeBorder(
        marker, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255
    )
    cv2.imwrite(path, bordered)
    return path
