# Ultrasound completeness coach — Stage 0

Stage 0 is an offline, no-hardware study of the *coverage engine*: given a
tracked freehand ultrasound sweep (frames + probe poses), build a voxel map of
how well each part of the target region was imaged, score completeness, point
at thin regions, and measure how badly the map degrades when the poses carry
realistic tracking error (phone / marker / sensorless levels).

It uses the public TUS-REC forearm datasets as a stand-in for the eventual
clinical target (thyroid / FAST windows). The forearm proves the mechanics,
not the organ.

## Data

TUS-REC validation sets (UCL/KCL), CC BY-NC-SA 4.0, research use only,
cite arXiv:2506.21765. Put the zips under `data/raw/` (gitignored):

- `data/raw/tusrec2025_val/Freehand_US_data_val_2025.zip` (1.2 GB, 3 subjects,
  2 rotation/tilt scans each)
- `data/raw/tusrec2024_val/Freehand_US_data_val.zip` (4.8 GB, 3 subjects,
  24 scans each: straight / C / S, parallel / perpendicular, both directions)

Each scan: `frames` [N,480,640] uint8 at 20 fps, `tforms` [N,4,4] tracker-tool
to camera, plus `calib_matrix.csv` (pixel->mm scale and image->tool rigid
transform, pinhead calibration).

## Layout

- `src/uscov/data.py`      load scans, build per-frame image->world transforms
- `src/uscov/coverage.py`  per-pixel confidence + voxel coverage accumulation
- `src/uscov/score.py`     completeness score and "thin region" finder
- `src/uscov/noise.py`     pose corruption models (drift, jitter, bias)
- `src/uscov/viz.py`       plots and fill-in animation
- `scripts/`               runnable entry points
- `tests/`                 unit tests for transforms and coverage

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Stage 0 results (2026-10-09)

Engine validated on real tracked sweeps (TUS-REC 2024 validation: 8 straight/C/S forearm scans, ~450 frames,
~150 mm path each; TUS-REC 2025 validation: 6 rotation/tilt scans, ~1,500 frames). Voxel 2 mm, pixel step 4.

**Partial-sweep scoring works.** Scoring the first 60% of a straight sweep gives completeness 0.72 and a single
zero-confidence thin region located just past where the partial sweep stopped, tied to the nearest frame.

**Tracking tolerance** (medians over 8 scans x 2 seeds, reference = optically tracked poses):

| pose source (simulated)        | mean err | claimed completeness | false coverage | false gap | Dice |
| ------------------------------ | -------: | -------------------: | -------------: | --------: | ---: |
| optical tracker, raw           |   0.5 mm |                0.997 |          0.047 |     0.003 | 0.975 |
| marker + phone, raw            |   5.5 mm |                0.999 |          0.456 |     0.001 | 0.704 |
| marker + phone, 9-frame smooth |   2.0 mm |                0.980 |          0.141 |     0.020 | 0.918 |
| sensorless DL (~5% drift)      |   3.7 mm |                0.914 |          0.084 |     0.086 | 0.916 |
| markerless phone VIO           |  41.2 mm |                0.578 |          0.742 |     0.422 | 0.360 |

Findings:
1. **Jitter is worse than drift.** Independent per-frame error inflates the map (every frame lands slightly off,
   so a shell of never-imaged voxels gets "covered"). Smooth drift of similar size keeps the map internally
   consistent (Dice ~0.92). The metric to watch for a coverage map is *false coverage*, not trajectory error.
2. **Requiring multiple hits per voxel does not help** (min_hits 1/3/5 change false coverage by <2 points),
   because jittered frames hit the shell many times. **Temporal pose smoothing does help**: a 9-frame
   moving average cuts marker-tracker error 5.5 -> 2.0 mm, false coverage 0.46 -> 0.14, while blurring real
   probe motion by only 0.1 mm.
3. **Markerless phone tracking is unusable** for a coverage map at reported drift levels (Dice 0.36).
4. **Decision:** the Stage 1 rig is a marker cube + phone/webcam with pose smoothing; expect ~2 mm pose error
   and ~15% false coverage at a 2 mm grid. A coarser clinical grid (4-5 mm regions) will tolerate this better.
5. Rotation/tilt protocols accumulate ~2x the sensorless drift of straight sweeps (per-frame bias over 3x the frames).

Caveats: noise models are literature-anchored simulations, not measured trackers; the reference region is the
swept slab of a single sweep, which is the worst case for shell inflation; forearm stands in for thyroid.

Reproduce: `scripts/run_coverage.py`, `scripts/noise_sweep.py --min-hits 1,3,5`, `--smooth 9`. CSVs under `outputs/`.

## Stage 1 software (2026-10-09)

Built ahead of the bench session so the lab day is hardware-only. All on the public sweeps; 13 tests pass.

| Module | What it adds | Validation |
| --- | --- | --- |
| `src/uscov/confidence.py` | Ray-based shadow model: confidence follows each scan line from the probe face; a dark region with signal beyond it (cyst) keeps credit, a dark region with nothing beyond (bone shadow, dropout, no contact) loses it. Fan geometry (virtual apex, angles, radii) is recovered from the mask automatically; linear probes fall back to parallel rays | Synthetic shadow vs cyst test; visual check on real frames (`scripts/confidence_compare.py`); now the default `conf_model="ray"` |
| `src/uscov/roi.py` | Named region templates (ellipsoids/boxes) so a gap gets a name. `thyroid_template()` = 2 lobes x (upper, lower pole) + isthmus; `sweep_thirds_template()` = start/middle/end x superficial/deep for phantoms; per-part completeness report | Unit tests; live demo cue reads "next: end third, deep (45%)" when a sweep is stopped at 80% |
| `src/uscov/tracker.py` | Hybrid pose fusion: marker pose is the anchor; during camera dropouts the last pose is propagated with image-based relative motion (or constant velocity); frames tagged PRIMARY/BRIDGED with gap length and a confidence multiplier | Unit test + `scripts/hybrid_sweep.py` on 4 real sweeps (table below) |
| `src/uscov/live.py` | Frame sources (capture card via OpenCV, replay of recorded sweeps), ArUco cube tracker (6-face board, sub-pixel corners, solvePnP), marker bitmap generator | Synthetic virtual-camera tests: single face and two faces |
| `scripts/live_demo.py` | End-to-end replay "as if live": dropouts -> hybrid fusion -> ray confidence -> named parts -> cue; writes a GIF | `outputs/live_demo/` |

**Hybrid tracker vs dropouts** (4 straight/C sweeps, 3 dropouts each, marker-style primary poses, medians):

| gap (frames @20 fps) | strategy | completeness | false gap | Dice |
| --- | --- | ---: | ---: | ---: |
| 10 (0.5 s) | drop frames | 0.986 | 1.4% | 0.880 |
| 40 (2 s)   | drop frames | 0.902 | 9.8% | 0.829 |
| 40 (2 s)   | bridge with image motion | 0.984 | 1.6% | 0.889 |
| 100 (5 s)  | drop frames | 0.576 | 42.4% | 0.678 |
| 100 (5 s)  | bridge with image motion | 0.968 | 3.2% | 0.889 |
| 100 (5 s)  | bridge with constant velocity | 0.585 | 41.5% | 0.685 |

Bridging with image-based motion keeps the map intact through 5-second camera dropouts (bridged-frame error ~2.6 mm);
constant-velocity extrapolation is useless beyond a second. Simply dropping untracked frames loses the map.

**Marker rig design rules from the synthetic camera tests:** a single 24 mm marker at 40 cm has ~7 mm depth ambiguity;
at 25 cm it is ~2 mm; a 40 mm marker at 40 cm ~3.5 mm. Two visible faces resolve the ambiguity (sub-mm with exact corners).
So: camera within ~30 cm, markers >= 30-40 mm, cube oriented so two faces are visible, sub-pixel corner refinement on.

Still open for the bench: spatial calibration (image <-> cube) and temporal alignment come from PLUS fCal on the day;
the ray model's thresholds are to be calibrated against the phantom; the thyroid template needs a registration step (Stage 2).
