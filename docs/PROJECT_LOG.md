# Ultrasound completeness coach — project log

Running record of the project. Mirrors the shared doc "Ultrasound coach project log"; this copy lives in git so the
repository stays self-describing. Newest entries at the top of the work log.

## Stage 0 in one paragraph (completed 2026-10-09)

Stage 0 asked whether software can turn "here is an ultrasound frame and here is where the probe was" into an
honest map of what has and has not been scanned, and how accurately the probe position must be known for that
map to stay honest. Done with no hardware and no people, on public forearm sweeps with lab-grade tracking.
Answer: the map works, and the tracking requirement is modest if the pose stream is smoothed. A marker cube on
the probe watched by a phone camera, with a half-second moving average, lands at ~2 mm error and keeps the map
92% faithful (Dice). Markerless phone tracking does not work (Dice 0.36). Surprise: frame-to-frame jitter
corrupts the map far more than slow drift of the same size, because jitter inflates the map into tissue that was
never imaged. Full numbers in `README.md`.

## Validated vs taken on faith

Validated: pixel-to-world geometry (unit tests + real trajectories), gap finding on partial sweeps, tracking
tolerance by tracker family, the jitter-vs-drift distinction and the smoothing fix.

Taken on faith (Stage 1 work): the brightness-based image-quality rule (no expert graded any frame), anatomy
(no organ labels; "covered" means the engine believes a frame imaged the cube), the target region (defined as
what the sweep covered, not a thyroid outline), tracker noise levels (literature-anchored simulations), and the
organ itself (forearm stands in for thyroid).

## Catalogue

| Item | What | Where |
| --- | --- | --- |
| Code repository | Engine, scripts, tests, README, research report and notes | https://github.com/zbenja168/ultrasound-completeness-coach (private); local `C:\ultrasound_Proj` |
| Proposal doc | Pitch with system sketch, screen mockups, landscape, plan, scope, Stage 0 results | https://claude.ai/code/artifact/1a4b4547-534f-4965-994f-58b910d84daa |
| Project log doc | Shared version of this file | https://claude.ai/code/artifact/96594db2-a83c-4954-a5aa-46c0d7536107 |
| Research report | 5,000-word sourced feasibility report | `reports/Guided 3D ultrasound mapping feasibility.md` |
| Research notes | Five source-note files | `research_notes/Guided 3D ultrasound mapping feasibility/` |
| Engine | `data.py`, `coverage.py`, `score.py`, `noise.py`, `viz.py`, plus Stage 1: `confidence.py`, `roi.py`, `tracker.py`, `live.py` | `src/uscov/` |
| Scripts | inspect, run coverage, noise sweep, confidence compare, hybrid sweep, live demo, make markers, calibrate camera, track cube | `scripts/` |
| DualTrack results | Predicted poses per sweep, coverage comparison CSVs | `outputs/dualtrack_2024/`, `outputs/dualtrack_2025/`, `outputs/dualtrack_cov_2024/`, `outputs/dualtrack_cov_2025/` (local only); code + weights in `third_party/` (local only, CC BY-NC-SA) |
| Bench-day runbook | Before/on/after the lab session, kit list, pass criteria | `docs/BENCH_DAY.md` |
| Printable markers | Six cube markers (35 mm) + calibration chessboard | `docs/print/markers_35mm.pdf` |
| Tests | 13 unit tests | `tests/test_engine.py`, `tests/test_stage1.py`, `tests/test_live.py` |
| Raw data | TUS-REC 2024 val (4.8 GB), 2025 val (1.2 GB), CC BY-NC-SA | `data/raw/` (local only, see README for links) |
| Extracted data | 78 scans as HDF5, 13 GB | `data/extracted/` (local only) |
| Coverage outputs | projections + fill GIFs | `outputs/coverage/`, `outputs/coverage_2024/` (local only) |
| Inspection outputs | sample frames + confidence, trajectories | `outputs/inspect/`, `outputs/inspect_2024/` (local only) |
| Hybrid tracker outputs | CSV: dropout length x strategy | `outputs/hybrid/` (local only) |
| Live demo outputs | replay GIF + final frame | `outputs/live_demo/` (local only) |
| Noise sweep outputs | CSV + box plots: 2025; 2024 raw; 2024 min-hits; 2024 smoothed | `outputs/noise_2025/`, `outputs/noise_2024/`, `outputs/noise_2024_mh/`, `outputs/noise_2024_smooth9/` (local only) |
| Python environment | numpy, scipy, h5py, matplotlib, tqdm, pytest | `.venv/` (rebuild from `requirements.txt`) |

## Work log

| Date | Event |
| --- | --- |
| 2026-10-10 | Ran published DualTrack image-only model on all 72 forearm + 6 rotation sweeps: median drift 6.8 mm (4.0%) forearm, 9.5 mm (2.5%) rotation. Coverage from measured poses: Dice 0.91 forearm, 0.83 rotation alone; hybrid marker + DualTrack 0.93-0.94. Measured row matches Stage 0 simulation. First attempt was stopped by low system memory and rerun after apps were closed |
| 2026-10-10 | Bench-day prep: printable marker + chessboard sheet (`docs/print/markers_35mm.pdf`), camera calibration script (verified on synthetic views to ~1 px), home jitter test for the marker cube, step-by-step runbook `docs/BENCH_DAY.md` |
| 2026-10-09 | Stage 1 software built and tested (13 tests): ray-based shadow confidence (now default), named region templates (thyroid, sweep-thirds), hybrid marker/image tracker, ArUco cube tracker + capture/replay sources, end-to-end replay demo. Hybrid sweep: bridging keeps completeness 0.97 through 5 s camera dropouts vs 0.58 when frames are dropped. Marker rig rules: camera <30 cm, markers >=30-40 mm, two faces visible |
| 2026-10-09 | Decision: hybrid tracking. Marker cube (camera) is the primary pose source; image-based tracking bridges camera dropouts. Not competing with published sensorless methods; the tracking contribution is the tolerance question. Engineering partner invited to repo |
| 2026-10-09 | Hardware settled: the school's GE machine is a cart with a video output port; department has approved plugging a capture card into it. Stage 1 frame access = capture card, no handheld workaround needed |
| 2026-10-09 | Faculty sponsor secured (colorectal surgeon, extensive ultrasound experience, full support). Engineering partner secured. School handheld reported as GE (model to confirm); frame-access route under investigation |
| 2026-10-09 | Project log created (shared doc + this file) |
| 2026-10-09 | GitHub repository created (private), all commits pushed |
| 2026-10-09 | README Stage 0 results table; Stage 0 results section added to proposal doc |
| 2026-10-09 | Smoothed noise sweep on 2024 scans: marker case recovers to Dice 0.92 |
| 2026-10-09 | Pose smoothing filter + test; `--smooth` option in noise sweep |
| 2026-10-09 | Min-hits sweep: no meaningful effect on false coverage |
| 2026-10-09 | Scoring gains `min_hits`; sweep evaluates several values |
| 2026-10-09 | Bug: rotation noise applied about world origin inflated all errors; first results discarded, model fixed, presets retuned |
| 2026-10-09 | TUS-REC 2024 val downloaded/extracted (72 scans); coverage run on straight sweep |
| 2026-10-09 | TUS-REC 2025 val downloaded/extracted (6 scans); coverage run on rotation sweep; partial-sweep gap cue verified |
| 2026-10-09 | Proposal doc: system sketch + two monitor mockups |
| 2026-10-09 | Coverage engine, scoring, noise models, viz, tests committed (5 tests) |
| 2026-10-09 | Stage 0 skeleton; git init; Python env |
| 2026-10-08 | Scope decided: completeness coach for education/QA; finding detection, steering guidance, diagnostic claims excluded |
| 2026-10-08 | Deep research (5 researchers + report writer); report delivered |
| 2026-10-08 | Idea raised after M2 ultrasound lab |

## Open items for Stage 1

- [x] Ray-based shadow confidence model built 2026-10-09 (thresholds to calibrate on the phantom)
- [x] Named region templates built 2026-10-09 (thyroid + sweep-thirds); registration to a real neck is Stage 2
- [ ] Measure a real marker-cube rig: pose error, jitter spectrum, smoother window
- [ ] Pick clinical region size (4–5 mm) that absorbs ~2 mm pose error
- [ ] Bench day: PLUS fCal spatial + temporal calibration; capture-card crop and mm/px from the on-screen scale; camera intrinsics (chessboard)
- [ ] Build the marker cube per the rig rules (camera <30 cm, markers >=30-40 mm, two faces visible)
- [x] Frame access settled 2026-10-09: GE cart with video port, permission granted; use a USB capture card via PLUS
- [ ] Five need-validation conversations (see proposal)
- [x] Faculty sponsor (colorectal surgeon) and engineering partner secured 2026-10-09; next: brief both, agree IRB timeline
- [ ] Apply for ImFusion academic SDK
- [x] Hybrid tracker built and tested 2026-10-09: bridging holds through 5 s dropouts
- [x] DualTrack run on all sweeps 2026-10-10; measured results in README
