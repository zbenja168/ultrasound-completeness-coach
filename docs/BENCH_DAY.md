# Stage 1 bench day runbook

Goal of the session: live frames from the GE cart plus a tracked marker cube, the coverage map filling in on a
phantom, a measured tracking-accuracy number, and a recording of everything for later analysis.

## Before the day (engineer, at home)

1. Print `docs/print/markers_35mm.pdf` at 100% / actual size. Measure one marker with a ruler (should be 35 mm).
   Regenerate at another size with `python scripts/make_markers.py --marker-mm 40`.
2. Build the cube: rigid block with edge >= 43 mm, one marker per face, flat and matte, ids matching the labels.
   Bracket it to the probe handle so it cannot shift (3D-printed clip preferred). Two faces should face the camera
   in the usual scanning grip.
3. Camera intrinsics: tape page 2 (chessboard) flat to a board, then
   `python scripts/calibrate_camera.py --device 0 --out outputs/camera.json` and grab ~15 varied views.
   Good result: reprojection RMS < 0.5 px. Keep the same camera and resolution on the day; do not change zoom/focus.
4. Jitter test: `python scripts/track_cube.py --camera outputs/camera.json --marker-mm 35`, cube still on a table at
   25-30 cm, press M. Target: smoothed jitter well under 2 mm. Send `outputs/track_log.json` back.
5. Buy or borrow a USB capture card matching the cart's video port (HDMI, DVI or VGA plus adapter).

## Kit list

GE cart, capture card + cable, laptop with this repo and `.venv`, webcam on a tripod or clamp, marker cube on probe,
phantom (thyroid or any gel phantom with known inserts), ruler or a rail for known-distance slides, gel, tape.

## On the day

1. **Frames.** Plug the capture card into the cart's video out. Confirm the laptop sees it (any webcam app).
   Note the device index. Freeze a frame and record the crop rectangle of the ultrasound image (rows/cols) and the
   depth setting. Fix depth and zoom for the session.
2. **Scale.** On a frozen frame, measure the on-screen depth ruler in pixels to get mm per pixel, or image a
   phantom insert of known size.
3. **Camera.** Mount within ~30 cm of where the probe will be, looking down at an angle so two cube faces are seen.
   Check `track_cube.py` shows the cube in > 95% of frames during a practice sweep.
4. **Spatial calibration (image to cube).** Use PLUS fCal with an N-wire or stylus phantom if available; otherwise
   the pinhead method: image a pinhead from 10-15 probe poses and solve for the fixed transform. This gives the
   `image_to_tool` matrix the engine needs (same role as `calib_matrix.csv` in the public data).
5. **Temporal alignment.** Tap or jiggle the probe sharply a few times while recording both streams; the motion
   spike in the pose stream and in the image stream gives the lag (expect ~0.1 s).
6. **Accuracy check.** Slide the probe along a ruler or rail by known distances (50 and 100 mm), three times each.
   Compare with the tracker. This is the measured replacement for the simulated tracker row in the results.
7. **Coverage runs.** On the phantom: one complete sweep, one deliberately stopped at ~60%, one with the operator's
   hand blocking the camera for a few seconds. Record frames + poses for each.
8. **Save everything** into `data/bench_YYYY-MM-DD/` (frames, poses with timestamps, camera.json, crop, mm/px,
   calibration result, notes). Raw recordings are worth more than any live demo.

## After the day (Claude)

Load the recordings into the engine, calibrate the ray-confidence thresholds against the phantom's known inserts,
fill the measured row of the tracking table, and update the project log.

## Pass criteria

| Check | Target |
| --- | --- |
| Capture | full frame rate, stable crop |
| Cube visibility during sweeps | > 95% of frames |
| Known-distance error after smoothing | about 2 mm or better |
| Partial sweep | engine names the missing part of the phantom |
| Camera blocked a few seconds | map stays intact (bridging works) |
