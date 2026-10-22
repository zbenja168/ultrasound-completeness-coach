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
7. Buy or borrow a USB capture card for the machine's video port (the Venue Go lists an HDMI output; confirm from the reference PDF).

## The machine: GE Venue Go

Confirmed 2026-10-19 by the ultrasound lead (software version to follow). What matters for us:

- Portable point-of-care system, 15.6-inch touchscreen, on a stand. Reseller spec listings give it an HDMI
  output port plus USB 3.0 and Ethernet; confirm the port and its location from the reference PDF he attached
  before buying the capture card (HDMI capture card is the likely answer).
- The small-parts probe for a thyroid is the L4-12t-RS linear array: 38 mm field of view (the simulator's probe
  width), 3.4-12.6 MHz, buttons on the handle. The cube bracket must leave the buttons and the cable exit free.
- The screen layout (image region, depth ruler) is read on the day by `pick_crop.py`; nothing is hard-coded to it.

## Kit list

GE Venue Go, HDMI capture card + cable, laptop with this repo and `.venv`, webcam on a tripod or clamp, marker cube on probe,
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

## No webcam? Phone-camera fallback (used 2026-10-22)

If no USB webcam can be attached to the laptop (school network blocked the phone-webcam installer), the probe camera
is the phone itself, recording ordinary video, and the laptop records only the ultrasound. Everything else moves
to after the session.

1. **Phone on the tripod**, lens 25-30 cm from the scanning spot, looking down at ~45 degrees so two cube faces
   show. 1080p, highest frame rate offered, focus and exposure locked if the camera app allows. Plug it into
   power. Nobody touches the tripod between takes.
2. **Calibration clip first**: film the printed checkerboard for ~30 s while moving and tilting it around the
   view. Later: extract frames and run `calibrate_camera.py --images <folder>`.
3. **Each take**: start the phone video, start
   `python scripts/record_us_only.py --us-device <camlink index> --out data/bench_DATE --name <take>`,
   then tap the probe sharply on the phantom three times. The taps sync the two recordings. Q stops the laptop
   side; stop the phone after. Same take names as above: practice, pinhead, jiggle, slide, full, partial, blocked.
4. **Screen crop** can be picked afterwards: `pick_crop.py --device data/bench_DATE/full_01/us.avi ...`.
5. **Copy the phone videos** into the take folders (`phone.mp4`) before leaving, or at least the same day.

After the day: track the cube in `phone.mp4` with the calibrated intrinsics, cross-correlate the tap jolts to
find the offset to `us_times.csv`, then continue with `recording_to_scan` as for a webcam take.

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
