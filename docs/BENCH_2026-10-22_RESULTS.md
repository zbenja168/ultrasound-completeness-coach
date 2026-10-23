# Bench session 2026-10-22: what the data showed

First hardware session: GE Venue Go, curved abdominal probe (C1-5 preset, depth 16 cm, gain 0), abdominal
phantom, Elgato Cam Link 4K on the cart's HDMI output, laptop recording the screen with
`scripts/record_us_only.py`, and the marker cube filmed by a phone on a tripod (no webcam available). Eighteen
ultrasound takes and 23 phone clips were uploaded the same night; the processing on 2026-10-23 is below.

## Headline

The capture chain works end to end. Tracking of the marker cube did not: the top face was recognised in a
median 23 % of frames per take (range 1-63 %), so the coverage maps and scores from this session are not
usable as evidence, and the slide accuracy test could not be evaluated. The causes are all rig choices that the
next session fixes (see Lessons in `docs/BENCH_DAY.md`).

## What worked

| Step | Result |
| --- | --- |
| Screen capture | 1920x1080 at 30 fps via Media Foundation, per-frame timestamps, 18 takes, no dropped frames noticed |
| Screen geometry | depth ruler 47 px per cm (0.2128 mm/px), fan rows 130-918, crop rows 130-920 cols 560-1560 (`data/bench_2026-10-22/screen.json`) |
| Phone calibration | 66 chessboard views; the printed board was clipped to 8x6 inner corners; constrained fit, RMS 1.16 px after dropping 15 outlier views (`phone_camera.json`) |
| Clock alignment | the three taps show as whole-frame motion in the phone video and image motion on the screen; clean take jiggle_take2: offset -3.72 s, correlation 0.53 vs 0.14 for the next peak, matching the file-clock prediction (-3.7 s) |
| Pipeline | `scripts/phone_to_bench.py` turns a take plus its phone clip into the standard bench recording (frames.h5, poses.npz, meta.json) |

## What did not

| Measure | Value | Why |
| --- | --- | --- |
| Top-face tracking per take | median 23 %, best 63 % (jiggle_01), worst 1 % (slide3) | printed markers have no white margin, so where the black border meets the black cube body the square never closes; the scanning hand covered one marker edge in most sweep frames |
| Side faces | never recognised | phone looked almost straight down (cube tilt from camera axis median 9 degrees); side faces too foreshortened |
| Position noise, probe held still | lateral std 2.6 / 5 mm, depth std 36 mm (jiggle_take2, one face, 67 poses) | phone about 75 cm away, markers about 100 px wide; a single square constrains depth poorly |
| Pose flips | fixed in software | one square has two mirror tilt solutions; `ArucoCubeTracker.pose_continuous` keeps the one closest to the previous frame |
| Slide accuracy | not measurable | no two stops with the cube tracked, in any of the four slide takes; no reference distances were written down |
| Partial and blocked scores | 0.02 and 0.10 against the full sweep | 47 and 257 usable frames against a 190-frame reference; not meaningful |

Per-take table: `docs/figures/bench_2026-10-22/takes.md`. Figures: `full_take2_reference_map.png` (first map
from real frames, estimated image-to-cube transform, 190 usable frames), `jiggle_take2_sync.png`,
`marker_occlusion_closeups.jpg`, `phone_view_samples.jpg`.

## Not in the upload

No notes.txt, no photos of the cube on the probe with a scale object, no cube-to-probe-face distance, no slide
reference distances. The coverage maps therefore use a guessed 60 mm face distance and a lateral axis
estimated from the sweep's rotation.

## Next session, in order

1. Reprint markers with a white margin of one bit or more and mount them on a white cube on a short stalk above
   the probe, clear of the grip.
2. Phone at 25-30 cm, 45 degrees, two faces visible, 1080p, focus and exposure locked.
3. Pinhead calibration (`scripts/calibrate_pinhead.py`) so the image-to-cube transform is measured.
4. Slide along a measured reference with 1 s holds; write the distances in notes.txt before leaving.
5. Keep the three taps at the start of every take; they worked.
