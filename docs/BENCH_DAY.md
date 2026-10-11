# Stage 1 bench day runbook

Goal of the session: live frames from the GE cart plus a tracked marker cube, the coverage map filling in on a
phantom, a measured tracking-accuracy number, and a recording of everything for later analysis.

Every step below has a script. Each script prints what "good" looks like for its result.

## Before the day (engineer, at home)

1. Set up the code: clone the repo, `python -m venv .venv`, `.venv\Scripts\pip install -r requirements.txt`,
   then `.venv\Scripts\python -m pytest` (22 tests should pass).
2. Print `docs/print/markers_35mm.pdf` at 100% / actual size. Measure one marker with a ruler (should be 35 mm).
   Regenerate at another size with `python scripts/make_markers.py --marker-mm 40`.
3. Build the cube: rigid block with edge >= 43 mm, one marker per face, flat and matte, ids matching the labels.
   Bracket it to the probe handle so it cannot shift (3D-printed clip preferred). Two faces should face the camera
   in the usual scanning grip.
4. Camera intrinsics: tape page 2 (chessboard) flat to a board, then
   `python scripts/calibrate_camera.py --device 0 --out outputs/camera.json` and grab ~15 varied views.
   Good result: reprojection RMS < 0.5 px. Keep the same camera and resolution on the day; do not change zoom/focus.
5. Jitter test: `python scripts/track_cube.py --camera outputs/camera.json --marker-mm 35`, cube still on a table at
   25-30 cm, press M. Target: smoothed jitter well under 2 mm. Send `outputs/track_log.json` back.
6. Dry-run the recorder with no ultrasound: any video file stands in for the capture card.
   `python scripts/record_bench.py --us-device some_video.mp4 --cam-device 0 --camera outputs/camera.json --out data/dryrun --name test`,
   press R to start and R to stop, Q to quit. The take folder should hold `frames.h5`, `poses.npz`, `cam.avi`, `meta.json`.
7. Buy or borrow a USB capture card matching the cart's video port (HDMI, DVI or VGA plus adapter).

## Kit list

GE cart, capture card + cable, laptop with this repo and `.venv`, webcam on a tripod or clamp, marker cube on probe,
phantom (thyroid or any gel phantom with known inserts), a pin or bead on a thread in a water bath (for calibration),
ruler or a rail for known-distance slides, gel, tape.

## On the day

Pick a session folder once, e.g. `data/bench_2026-10-18`, and use it for every take. Fix depth and zoom on the cart
for the whole session; any change means redoing steps 1 and 3.

1. **Frames and scale.** Plug the capture card into the cart's video out. Confirm the laptop sees it (any webcam
   app) and note the device index. Freeze a frame on the cart, then
   `python scripts/pick_crop.py --device <index> --ruler-mm 10 --out outputs/screen.json`:
   press SPACE to freeze, click the image's top-left and bottom-right corners, then two ticks of the depth ruler
   10 mm apart. It writes the crop and the mm per pixel. Check: the printed image depth should match the cart's
   depth setting.
2. **Camera.** Mount within ~30 cm of where the probe will be, looking down at an angle so two cube faces are seen.
   Start the recorder and check it shows the cube in > 95% of frames during a practice sweep:
   `python scripts/record_bench.py --us-device <index> --cam-device 0 --camera outputs/camera.json --screen outputs/screen.json --marker-mm 35 --out data/bench_DATE --name practice`
3. **Spatial calibration (image to cube).** Put the pin in the water bath. Record a take `--name pinhead` while
   rocking and tilting the probe about the pin on two axes, at least 30 degrees each way, 20-30 s, keeping the pin
   bright in the image. Then
   `python scripts/calibrate_pinhead.py data/bench_DATE/pinhead_01 --screen outputs/screen.json --out outputs/image_to_tool.json`
   and click the pin in 10-15 frames (N/P step frames, S shows the fit so far, Q saves). Good: RMS under 1.5 mm.
   PLUS fCal with an N-wire phantom is the alternative if it is already set up.
4. **Temporal alignment.** Record a take `--name jiggle`: probe on the phantom, tap or jiggle it sharply five or
   six times over ~20 s. Then `python scripts/estimate_lag.py data/bench_DATE/jiggle_01`. Expect about 0.1 s and
   a peak correlation above 0.5.
5. **Accuracy check.** Record a take `--name slide`: slide the probe along the ruler or rail, holding still for a
   second at each mark, e.g. 0, 50, 0, 100, 0, 50, 0, 100 mm. Then
   `python scripts/known_distance.py data/bench_DATE/slide_01 --expected 50,50,100,100,50,50,100,100`.
   This is the measured replacement for the simulated tracker row in the results.
6. **Coverage runs.** On the phantom, one take each: `--name full` (complete sweep), `--name partial` (stop at
   ~60%), `--name blocked` (operator's hand covers the camera for a few seconds mid-sweep).
7. **Save everything.** The recorder already writes each take under the session folder. Copy `outputs/camera.json`,
   `outputs/screen.json`, `outputs/image_to_tool.json` and `outputs/lag.json` into it, and add a `notes.txt`
   (cart model, probe, depth, anything odd). Raw recordings are worth more than any live demo.

## After the day (Claude)

`recording_to_scan` in `src/uscov/bench.py` turns a take plus `image_to_tool.json` and the lag into a Scan the engine
runs unchanged. Then: calibrate the ray-confidence thresholds against the phantom's known inserts, fill the measured
row of the tracking table, and update the project log.

## Pass criteria

| Check | Target |
| --- | --- |
| Capture | full frame rate, stable crop |
| Cube visibility during sweeps | > 95% of frames |
| Pinhead calibration | RMS under 1.5 mm |
| Lag estimate | peak correlation above 0.5 |
| Known-distance error after smoothing | about 2 mm or better |
| Partial sweep | engine names the missing part of the phantom |
| Camera blocked a few seconds | map stays intact (bridging works) |
