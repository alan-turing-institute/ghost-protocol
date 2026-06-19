# april_tags

Estimate the **3D position of a person's head** from a **single camera**, using
an AprilTag worn by that person.

Unlike the stereo face-detection approach (`../face_detection`), one tag is
enough: because the tag's physical size is known, `solvePnP` recovers its full
6-DoF pose (position **and** orientation) from a single view. We then apply a
fixed offset from the tag to the head centre.

Output is the head position in metres in the **camera frame**: `+x` right,
`+y` down, `+z` forward (into the scene), matching OpenCV's convention.

## Install

```bash
cd april_tags
uv sync
```

## Quick start

```bash
# 1. Generate the tag to print (AprilTag family 36h11, id 0)
uv run april-tags generate-tag --id 0 --out tag.png

# 2. Calibrate your camera (capture views, then solve)
uv run april-tags capture   --pattern 9x6
uv run april-tags calibrate --pattern 9x6 --square 0.025 --out camera.json

# 3a. Head pose from your webcam
uv run april-tags webcam --camera camera.json --tag-size 0.10

# 3b. ...or from a phone TCP JPEG stream (same protocol as face_detection)
uv run april-tags tcp --camera camera.json --host 192.168.0.42 --port 5000 --tag-size 0.10
```

`webcam` opens a live preview with an overlay: the detected tag axes, the
estimated head position, and a projected head-centre marker. Press `q` to quit
the preview. Each detection also prints a line like:

```
t1234ms  head=(+0.031, -0.118, +1.642) m  dist=1.648 m
```

Use `--quiet` for overlay-only output, or `--no-preview` for text-only output:

```bash
uv run april-tags webcam --camera camera.json --tag-size 0.10 --quiet
uv run april-tags webcam --camera camera.json --tag-size 0.10 --no-preview
```

---

## What you need to do

### Which tag to print

- **Family: `36h11`.** It is the recommended general-purpose AprilTag family
  (large Hamming distance → very low false-positive rate) and the default here.
- **Specific tag: id `0`.** Generate it with the command above. If you have
  several people, give each a different id (`--id 1`, `--id 2`, …) and run one
  estimator per id.
- **Print it big and rigid.** A ~10 cm black square reads reliably out to a few
  metres; bigger is better at distance. Print at **100% scale** ("actual size",
  not "fit to page"), then **mount it on stiff card or foamboard** so it stays
  perfectly flat — any curl warps the pose.
- **Measure it.** With a ruler, measure the side of the solid black square on
  the *printout* and pass that (in metres) as `--tag-size`. solvePnP scales the
  whole distance estimate by this number, so a 5% error here is a 5% error in
  reported distance.

### Where to attach the tag

Default geometry assumes the tag is **mounted flat on a cap brim or headband,
centred on the forehead, facing forward** (the same direction the person looks).
This keeps the tag close to the head, so the tag→head offset is small and pose
errors stay small.

The offset from the tag centre to the head centre is configured in the **tag's
own frame** (`+x` right, `+y` up, `+z` out of the tag towards the camera). The
defaults are:

| offset | default | meaning |
| ------ | ------- | ------- |
| `--offset-x` | `0.0` m | tag centred left-right on the head |
| `--offset-y` | `-0.07` m | head centre ~7 cm below the forehead |
| `--offset-z` | `-0.10` m | head centre ~10 cm behind the forehead surface |

If you instead mount the tag on the **chest** (easier to keep flat and rigid),
re-measure: the head centre is then roughly 35 cm *up* and a little *behind*,
so something like `--offset-y -0.35 --offset-z -0.05` (sign depends on how you
clip the board — verify against the live read-out). Whatever you choose,
**sanity-check by standing a known distance from the camera** and confirming the
printed `dist` matches.

### Calibration, step by step

You must calibrate the **same camera at the same resolution** you'll run
detection on — the focal length and principal point are what turn tag pixels
into metres.

1. Print an OpenCV chessboard (e.g. 9×6 *inner* corners = 10×7 squares).
   Tape it to something flat. Measure one square's side in metres.
2. `uv run april-tags capture --pattern 9x6` — a preview opens. When the board
   is detected the overlay turns green; press **SPACE** to save that view.
   Capture **15–25 views** with the board at varied angles, distances, and
   positions across the frame (corners included). Press **q** when done.
3. `uv run april-tags calibrate --pattern 9x6 --square 0.025 --out camera.json`
   — solves and reports an RMS reprojection error. **Aim for < 0.5 px**; if it's
   high, recapture with more varied, sharper, well-lit views.

`camera.json` is reusable until you change the camera or its resolution.

---

## Using it as a library

```python
from april_tags import CameraIntrinsics, HeadOffset, TagConfig, run_tcp_stream

intrinsics = CameraIntrinsics.load("camera.json")
run_tcp_stream(
    intrinsics,
    host="192.168.0.42",
    port=5000,
    tag=TagConfig(tag_id=0, size_m=0.10),
    offset=HeadOffset(y=-0.07, z=-0.10),
    on_head=lambda p: print(p.head_xyz, p.distance_m),
)
```

`HeadPoseEstimator.update(frame, timestamp_ms)` returns a `HeadPose` (or `None`)
if you want to drive the detection loop yourself.

## How it works

1. `cv2.aruco` detects the 36h11 tag and refines its 4 corners to sub-pixel.
2. `cv2.solvePnP(..., SOLVEPNP_IPPE_SQUARE)` recovers the tag pose `(rvec, tvec)`
   in the camera frame from those corners, the known tag size, and the
   intrinsics.
3. The configured tag→head offset is rotated into the camera frame and added to
   the tag centre to give the head position.

## Limitations

- The tag must be **visible and roughly facing the camera**; pose degrades at
  very shallow viewing angles.
- Accuracy is bounded by calibration quality, tag-size measurement, and how
  rigidly the tag is mounted.
- This estimates head position in the **camera** frame. Placing it in a shared
  world frame (for the two-camera Ghost Protocol setup) needs a known
  camera-to-world transform — out of scope here.
