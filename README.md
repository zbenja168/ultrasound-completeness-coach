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
