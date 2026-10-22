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
| Overview sketch | One-page figure for emails and slides (setup, map, output, scope statement) | `docs/figures/overview_sketch.png`; script `scripts/make_overview_figure.py` |
| Bench tooling | Recorder, crop/scale picker, pinhead calibration, lag estimator, known-distance check; recording format and pairing code; 9 tests | `src/uscov/bench.py`; `scripts/record_bench.py`, `pick_crop.py`, `calibrate_pinhead.py`, `estimate_lag.py`, `known_distance.py`; `tests/test_bench.py` |
| MS2 seed grant application draft | Full draft of the AWSOM MS2 Student Research Seed Grant application (sections A-K): two-phase validity study of the coach score against blinded expert rating of novice thyroid sweeps, timeline, $1,180 budget, compliance and incidental-findings plan, expert rating form, notes to finish; revised 2026-10-19 after teammate review | Claude Docs https://claude.ai/code/artifact/5536756a-5811-42e1-8e84-209f080cefd0 |
| Coverage coach simulator | Browser demo: scan a simulated neck with the cursor and watch the thyroid coverage map fill (top-down or rotatable 3D block view with cut-away); compare tracker types | public page https://zbenja168.github.io/coverage-coach-simulator/ (repo `zbenja168/coverage-coach-simulator`); private copy https://claude.ai/artifact/SmwGZaRm5BG5KuQrK1kMNU; source `sim/coverage_simulator.html` |
| Printable markers | Six cube markers (35 mm) + calibration chessboard | `docs/print/markers_35mm.pdf` |
| Tests | 22 unit tests | `tests/test_engine.py`, `tests/test_stage1.py`, `tests/test_live.py`, `tests/test_bench.py` |
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
| 2026-10-12 | Simulator published as a public GitHub Page: https://zbenja168.github.io/coverage-coach-simulator/ (separate public repo `zbenja168/coverage-coach-simulator`, local copy in the gitignored `sim_public/`; the main repo stays private). To update: copy `sim/coverage_simulator.html` to `sim_public/index.html`, commit and push there |
| 2026-10-22 | Bench session recorded on the abdominal phantom with the curved probe (depth 16 cm, gain 0, GE Venue Go): takes practice, jiggle, slide, full, partial, blocked, each with three sync taps; pinhead calibration skipped (probe-and-cube photos with a scale object instead); slide used an improvised reference object (distances in notes.txt); probe camera = phone on a tripod with a chessboard calibration clip. Laptop ran Microsoft Store Python 3.13 (DirectShow cannot open cameras by index there; scipy import broken). Data to be transferred to the home machine; next: sync, phone-video tracking, slide accuracy, first coverage map |
| 2026-10-22 | Bench day. Cam Link 4K on the Venue Go HDMI output works (screen visible in the Camera app). No webcam on site and the school network blocked the phone-webcam installer, so the probe camera is the phone recording video separately; added scripts/record_us_only.py (ultrasound-only recorder with per-frame timestamps, three-tap sync) and a phone-fallback section in docs/BENCH_DAY.md. Offline merge of phone video + ultrasound recording is a follow-up task |
| 2026-10-19 | Seed grant application revised after a teammate's review (run through Codex): target volume now defined by a faculty reference sweep per volunteer and shadow/contact handling explained; assigned omission reframed as the experimental condition with blinded raters as the reference standard and a rule for disagreements and cannot-tell; Phase 1 coverage verified independently (overhead camera over a printed grid, embedded beads) with a go/no-go checkpoint before Phase 2; primary analysis reported as association with cluster-bootstrap and mixed-model uncertainty, pilot framing, thresholds labelled exploratory; preliminary figures stated as simulation with the noise model, 60%/0.72 and dropout caveats and the TUS-REC reference; System Usability Scale moved to after scanning with the display shown; unsupported claims softened; honesty notes folded into the text. Narrative now about 2,300 words, over the 3-page limit, with a cut order in the notes |
| 2026-10-19 | Seed grant application drafted in Claude Docs (sections A-K in the form's order; placeholders for mentor details, IRB body, Research Day date and the 2026-10-22 bench measurements). Deadline 2026-12-02 |
| 2026-10-19 | Funding opportunity identified: AWSOM MS2 Student Research Seed Grant (up to $1,600; due 2026-12-02; project period 2026-12-16 to 2027-06-30; mentor attestation in-form; 3-page narrative; AWSOM Research Day dissemination). Assessment: fits a scoped Stage 2 validity study (coach score vs blinded expert rating of novice thyroid sweeps on volunteers, phantom phase first), not the randomised benefit study |
| 2026-10-19 | Machine confirmed by the ultrasound lead: GE Venue Go (software version to follow; reference PDF received by email). Reseller listings give it an HDMI output, so the capture card should be HDMI; thyroid probe is the L4-12t-RS linear array with a 38 mm field of view. Runbook updated with a machine section |
| 2026-10-13 | Simulator: added a 3D view of the coverage map (same voxel map drawn as a shaded block model; drag to rotate, Above/Side/Below presets, cut-away slider to expose deeper layers, believed slice shown as a sheet). Pushed to the public page and the private artifact |
| 2026-10-11 | Bench-day tooling built and tested on synthetic data (9 new tests, 22 total): recorder for capture-card frames + cube poses on one clock (`scripts/record_bench.py`, HDF5 + npz + raw webcam video per take), screen crop and scale picker (`pick_crop.py`), pinhead image-to-cube calibration solver (`calibrate_pinhead.py`, recovers the transform within 3 mm under realistic click and pose noise), jiggle-test lag estimator (`estimate_lag.py`), known-distance accuracy check (`known_distance.py`). `uscov.bench.recording_to_scan` turns a take into a Scan for the engine. Runbook rewritten so every step names its script and pass value |
| 2026-10-11 | One-page overview sketch for outreach emails (`docs/figures/overview_sketch.png`, regenerate with `scripts/make_overview_figure.py`): room setup, coverage map, student/instructor view, and the not-diagnostic statement. Drafted the access-request email to the ultrasound lead and the pre-bench-day task list for the engineer |
| 2026-10-10 | Simulator: probe tilt added (slider, A / D keys, Shift + scroll; up to 35 degrees). The beam fans under the skin from the probe face, the coverage map paints the tilted slice, and tracker noise and drift include tilt |
| 2026-10-10 | Interactive teaching simulator (`sim/coverage_simulator.html`, published privately at https://claude.ai/artifact/SmwGZaRm5BG5KuQrK1kMNU): cursor acts as the probe on a simulated neck with a synthetic B-mode image (trachea and bone shadow, vessels), thyroid coverage map with 5 named parts, depth setting, and switchable trackers (perfect, raw cube, smoothed cube, cube + image model, image only) with a block-camera control and live map-correct / false-coverage readouts. Anatomy and noise are approximate |
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
