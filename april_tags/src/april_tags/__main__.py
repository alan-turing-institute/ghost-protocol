"""Command-line entry point for april_tags.

Examples:
    # 1. Print a tag (defaults to id 0, family 36h11)
    uv run april-tags generate-tag --id 0 --out tag.png

    # 2. Capture chessboard views, then solve for intrinsics
    uv run april-tags capture --pattern 9x6
    uv run april-tags calibrate --pattern 9x6 --square 0.025 --out camera.json

    # 3a. Estimate head pose from the webcam
    uv run april-tags webcam --camera camera.json --tag-size 0.10

    # 3b. ...or from a phone TCP JPEG stream (see face_detection.detector)
    uv run april-tags tcp --camera camera.json --host 192.168.0.42 --port 5000 --tag-size 0.10
"""

from __future__ import annotations

import argparse

from april_tags.config import CameraIntrinsics, HeadOffset, TagConfig


def _parse_pattern(value: str) -> tuple[int, int]:
    """Parse a 'WxH' inner-corner spec like '9x6'."""
    w, h = value.lower().split("x")
    return int(w), int(h)


def _add_geometry_args(parser: argparse.ArgumentParser) -> None:
    """Add the tag and offset options shared by the streaming subcommands."""
    parser.add_argument(
        "--camera", required=True, help="intrinsics JSON from calibrate"
    )
    parser.add_argument("--tag-id", type=int, default=0)
    parser.add_argument(
        "--tag-size", type=float, default=0.10, help="black square side, metres"
    )
    parser.add_argument("--offset-x", type=float, default=0.0)
    parser.add_argument("--offset-y", type=float, default=-0.07)
    parser.add_argument("--offset-z", type=float, default=-0.10)


def _geometry(
    args: argparse.Namespace,
) -> tuple[CameraIntrinsics, TagConfig, HeadOffset]:
    """Build estimator inputs from parsed args."""
    intrinsics = CameraIntrinsics.load(args.camera)
    tag = TagConfig(tag_id=args.tag_id, size_m=args.tag_size)
    offset = HeadOffset(x=args.offset_x, y=args.offset_y, z=args.offset_z)
    return intrinsics, tag, offset


def main() -> None:
    """Dispatch the chosen subcommand."""
    parser = argparse.ArgumentParser(prog="april-tags", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_tag = sub.add_parser("generate-tag", help="write a printable AprilTag PNG")
    p_tag.add_argument("--id", type=int, default=0)
    p_tag.add_argument("--pixels", type=int, default=1200)
    p_tag.add_argument("--out", default="tag.png")

    p_cap = sub.add_parser("capture", help="capture chessboard images for calibration")
    p_cap.add_argument("--pattern", type=_parse_pattern, default=(9, 6))
    p_cap.add_argument("--source", default="0")
    p_cap.add_argument("--out-dir", default="calib_images")

    p_cal = sub.add_parser("calibrate", help="solve camera intrinsics from images")
    p_cal.add_argument("--pattern", type=_parse_pattern, default=(9, 6))
    p_cal.add_argument(
        "--square", type=float, default=0.025, help="square side, metres"
    )
    p_cal.add_argument("--image-dir", default="calib_images")
    p_cal.add_argument("--out", default="camera.json")

    p_web = sub.add_parser("webcam", help="estimate head pose from a webcam/video")
    p_web.add_argument("--source", default="0", help="webcam index or video path")
    p_web.add_argument(
        "--no-preview",
        action="store_true",
        help="disable the live OpenCV preview window",
    )
    p_web.add_argument(
        "--quiet",
        action="store_true",
        help="do not print pose lines to stdout",
    )
    _add_geometry_args(p_web)

    p_tcp = sub.add_parser("tcp", help="estimate head pose from a TCP JPEG stream")
    p_tcp.add_argument("--host", required=True)
    p_tcp.add_argument("--port", type=int, required=True)
    _add_geometry_args(p_tcp)

    args = parser.parse_args()

    # Import the heavy module lazily so `generate-tag`/`calibrate` start fast.
    from april_tags import calibrate, detector, generate_tag

    if args.command == "generate-tag":
        path = generate_tag.generate_tag(
            tag_id=args.id, pixels=args.pixels, path=args.out
        )
        print(f"Wrote {path} (AprilTag 36h11, id {args.id}). Print at 100% scale.")
    elif args.command == "capture":
        source: int | str = int(args.source) if args.source.isdigit() else args.source
        calibrate.capture_chessboards(args.pattern, source, args.out_dir)
    elif args.command == "calibrate":
        intrinsics = calibrate.calibrate_from_images(
            args.image_dir, args.pattern, args.square
        )
        intrinsics.save(args.out)
        print(f"Wrote intrinsics to {args.out}")
    elif args.command == "webcam":
        intrinsics, tag, offset = _geometry(args)
        source = int(args.source) if args.source.isdigit() else args.source
        on_head = (lambda pose: None) if args.quiet else None
        detector.run_stream(
            intrinsics,
            source,
            tag,
            offset,
            on_head=on_head,
            show=not args.no_preview,
        )
    elif args.command == "tcp":
        intrinsics, tag, offset = _geometry(args)
        detector.run_tcp_stream(intrinsics, args.host, args.port, tag, offset)


if __name__ == "__main__":
    main()
