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
