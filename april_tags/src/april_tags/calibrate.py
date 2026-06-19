"""Estimate camera intrinsics from chessboard images.

You must calibrate the *same* camera (and resolution) you will run detection on,
because the focal length and principal point are what convert tag pixels into
metres. Print a chessboard, hold it at many angles/distances filling the frame,
and capture ~15-25 views.

Workflow:
  1. Print an OpenCV chessboard (e.g. 9x6 inner corners). Measure one square.
  2. Capture frames: `capture_chessboards(...)` (webcam) or supply your own.
  3. `calibrate_from_images(...)` -> CameraIntrinsics, then `.save("camera.json")`.

"Inner corners" = (squares_per_row - 1, squares_per_col - 1).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from april_tags.config import CameraIntrinsics

# Sub-pixel corner refinement criteria.
_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


def capture_chessboards(
    pattern_size: tuple[int, int] = (9, 6),
    source: int | str = 0,
    out_dir: str = "calib_images",
) -> int:
    """Show a live preview; press SPACE to save a frame, 'q' to finish.

    Frames where the chessboard is detected are highlighted. Returns the number
    of images saved to `out_dir`.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        msg = f"Cannot open source {source}"
        raise RuntimeError(msg)

    saved = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(gray, pattern_size)
            preview = frame.copy()
            if found:
                cv2.drawChessboardCorners(preview, pattern_size, corners, found)
            cv2.putText(
                preview,
                f"saved {saved}  [SPACE]=save if green  [q]=done",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0) if found else (0, 0, 255),
                2,
            )
            cv2.imshow("calibration capture", preview)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" ") and found:
                cv2.imwrite(str(out / f"calib_{saved:03d}.png"), frame)
                saved += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()
    print(f"Saved {saved} images to {out}")
    return saved


def calibrate_from_images(
    image_dir: str = "calib_images",
    pattern_size: tuple[int, int] = (9, 6),
    square_size_m: float = 0.025,
) -> CameraIntrinsics:
    """Run cv2.calibrateCamera over chessboard images and return intrinsics.

    `square_size_m` is the measured side of one chessboard square in metres.
    """
    paths = sorted(Path(image_dir).glob("*.png")) + sorted(
        Path(image_dir).glob("*.jpg")
    )
    if not paths:
        msg = f"No images found in {image_dir}"
        raise RuntimeError(msg)

    # 3D coordinates of the chessboard corners in the board's own frame.
    objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0 : pattern_size[0], 0 : pattern_size[1]].T.reshape(-1, 2)
    objp *= square_size_m

    obj_points: list[np.ndarray] = []
    img_points: list[np.ndarray] = []
    image_size: tuple[int, int] | None = None

    for path in paths:
        gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        found, corners = cv2.findChessboardCorners(gray, pattern_size)
        if not found:
            print(f"  chessboard not found in {path.name}, skipping")
            continue
        corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), _CRITERIA)
        obj_points.append(objp)
        img_points.append(corners)
        image_size = (gray.shape[1], gray.shape[0])

    if image_size is None:
        msg = "No usable chessboard views; calibration failed."
        raise RuntimeError(msg)

    rms, camera_matrix, dist, _, _ = cv2.calibrateCamera(
        obj_points, img_points, image_size, None, None
    )
    print(f"Calibrated on {len(obj_points)} views, RMS reprojection error {rms:.3f} px")

    return CameraIntrinsics(
        fx=float(camera_matrix[0, 0]),
        fy=float(camera_matrix[1, 1]),
        cx=float(camera_matrix[0, 2]),
        cy=float(camera_matrix[1, 2]),
        dist_coeffs=[float(c) for c in dist.flatten()],
        image_width=image_size[0],
        image_height=image_size[1],
    )
