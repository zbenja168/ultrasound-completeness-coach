# Bench session 2026-10-30: what the data showed

Second hardware session, same cart and preset as the first (GE Venue Go, C1-5 curvilinear probe, depth 16 cm,
gain 0, abdominal phantom, Cam Link on HDMI, `record_us_only.py` on the laptop). Changes from 2026-10-22: markers
printed with the white margin and glued to a white paper cube strapped to the back of the probe; the phone (a
teammate's iPhone this time) on the tripod closer to the probe. Two operators: take 1 of each manoeuvre by Ben,
take 2 by a teammate. Twelve laptop takes and 13 phone clips uploaded the same day; processed 2026-10-31.

## Headline

Tracking works. The cube pose was recovered in 87-97 % of frames in the slide and full-sweep takes (median 23 % on
2026-10-22), two faces were seen in 30-60 % of frames, and the probe held still at a mark moves by 0.2-0.5 mm
per axis in the track (35 mm on 2026-10-22). The first coverage maps from real frames look like sweeps, and the
first operator-to-operator comparison exists. The known-distance test against the chessboard squares used as the ruler gives a mean absolute error of 2.3 mm over four moves of 38-95 mm. The weak link is now the clock alignment between phone and laptop
(about +-0.3 s on the good takes, +-1.5 s on three takes), and the cube-to-probe-face distance is still an assumption.

## What worked

| Step | Result |
| --- | --- |
| Screen capture | 1920x1080 at 30 fps, 12 takes; depth ruler at the same rows as 2026-10-22, so `screen.json` was reused |
| Cube tracking | per take (frames with a pose): slide_03 97 %, full2_01 96 %, slide2_02 88 %, full_01 87 %, blocked2_01 66 %, partial_02 59 %, partial_01 58 %, jiggle2_01 56 %, blocked_01 48 %, jiggle_01 25 % (`takes.md`) |
| Cube at rest | position std 0.2-0.5 mm per axis inside five 0.6-1.0 s holds (slide_03); phone 26-32 cm from the cube |
| Known distance | slide_03 moves between holds 55.6, 56.9, 39.9, 100.8 mm against 3, 3, 2, 5 chessboard squares (57, 57, 38, 95 mm): mean absolute error 2.3 mm, worst 5.8 mm; slide2_02 excursions 40, 90, 35, 90 mm (2 and 5 squares, no holds) |
| Coverage maps | fan-shaped swept volumes from real frames for both operators (`full_01_reference.png`, `full2_01_vs_reference.png`) |
| Operator comparison | with the same image-to-cube transform: the teammate's full sweep covers 65 % of Ben's reference volume, Ben's covers 73 % of hers (Dice 0.69 both ways); partial sweeps score 0.36-0.44, blocked sweeps 0.37-0.47 against either reference |
| Pipeline | `phone_to_bench.py` handles iPhone .MOV (start time from the file header), fits nothing by hand; `cube_layout.json` and `phone_camera.json` describe this rig |

## What had to be fixed in processing

| Problem | What happened | Fix |
| --- | --- | --- |
| Phone calibration | the two chessboard clips disagree by 2x in focal length (one was filmed zoomed); the takes match the wide clip | focal length fitted from 557 two-face cube frames instead (f = 975 px at 1080x1920, median reprojection 1.45 px); chessboard clips kept only as a cross-check |
| Cube layout | the markers were not glued as the sheet's face map says: id 2 on top, id 4 on an adjacent side; reprojection with the printed layout was 100 px off | layout searched over faces and rotations on the same frames; `CubeSpec` now takes a layout file (`cube_layout.json`: edge/marker ratio 1.625, so 56.9 mm edge if the marker is 35 mm) |
| Single-face pose flips | when the side face dropped out the pose jumped 57 mm (cube centre mirrored through the top face) in 115 frames of full2_01 | `pose_continuous` solves the lone marker in its own plane and composes with the fixed marker-to-cube transform; residual jumps gone (95th percentile speed 90 mm/s, was 1,700) |
| Clock sync | no single cue is reliable: whole-frame phone motion, cube speed and image flow each pick a wrong peak on some takes | fused estimate (three cues plus a file-clock prior); clear peak on 7 takes, approximate (+-1.5 s) on partial_02, blocked_01, blocked2_01 |
| Slide holds | the teammate's slide has no holds at the marks, so stops cannot be detected; Ben's holds were 0.6-1.0 s | hold a full second next time; turning points still give the excursion lengths |
| Blocked takes | the hand over the lens hides the cube for about 12 s; gaps over 10 frames are not bridged | expected; the image-only bridge (DualTrack) is the planned remedy and was not applied here |

## Numbers to carry into the application

- Cube tracked in 87-97 % of frames during sweeps and slides (median 23 % one week earlier).
- Still-probe position noise 0.2-0.5 mm per axis after the rig changes (35 mm depth noise before).
- Known-distance error 2.3 mm mean absolute (worst 5.8 mm) over moves of 38-95 mm.
- Two operators' full sweeps overlap with Dice 0.69; partial sweeps score about 0.4 against a full sweep.

## Confirmed by the team (2026-10-31)

- Marker 35 mm. The faces were cut outside the dashed line (rig photos, `cube_photo.jpg`), so the cube edge is
  about 57 mm, which is what the fit found (edge/marker 1.625). No reprocessing needed.
- The slide marks were chessboard squares (19 mm). Ben's holds give moves of 3, 3, 2 and 5 squares:

| Move | Expected (mm) | Measured (mm) | Error (mm) |
| --- | --- | --- | --- |
| 3 squares | 57 | 55.6 | -1.4 |
| 3 squares back | 57 | 56.9 | -0.1 |
| 2 squares | 38 | 39.9 | +1.9 |
| 5 squares | 95 | 100.8 | +5.8 |

  Mean absolute error 2.3 mm, bias +1.5 mm (`known_distance_slide_03.csv`). A print-scale error would move marker and squares
  together and cancel here, so this is the tracker's own error. The teammate's turning points (40, 90, 35, 90 mm)
  fit 2 and 5 squares as well.

## Still open

1. Cube centre to probe face (mm). The maps use 120 mm; the photos show the cube loose, not mounted.
2. sweep_01 and freestyle_01 have no phone clip; no notes.txt was written.

Figures: `docs/figures/bench_2026-10-30/` (tracked_fraction.png, slide_traces.png, marker_detections.jpg, cube_photo.jpg, the
four coverage projections, takes.md, known_distance_slide_03.csv, both summary JSONs). Raw outputs: `outputs/bench_2026-10-30/`.
