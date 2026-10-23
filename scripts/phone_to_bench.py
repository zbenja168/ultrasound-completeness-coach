"""Turn a phone-camera take into a bench recording the engine can read.

Bench days without a webcam (2026-10-22) recorded the ultrasound screen on the laptop (record_us_only.py:
us.avi + us_times.csv) and filmed the marker cube with a phone on a tripod. This script joins the two:

  python scripts/phone_to_bench.py data/bench_2026-10-22/us/full_take2_01 \
      --phone data/bench_2026-10-22/phone/20261022_154633.mp4 \
      --camera data/bench_2026-10-22/phone_camera.json --screen data/bench_2026-10-22/screen.json

1. Tracks the cube in every phone frame (ArucoCubeTracker) -> poses on the phone clock.
2. Crops the ultrasound screen to the image region (screen.json from pick_crop.py), optionally downsampled.
3. Finds the clock offset between phone and laptop from the three probe taps at the start of the take: the
   cube speed (phone) is cross-correlated with the image motion (ultrasound) over a wide search window.
4. Writes frames.h5, poses.npz (pose times moved onto the laptop clock) and meta.json into the take folder,
   so load_recording / estimate_lag.py / known_distance.py / recording_to_scan work unchanged.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.bench import RecordingWriter, frame_motion, pose_speed  # noqa: E402
from uscov.live import ArucoCubeTracker, CubeSpec  # noqa: E402


def track_phone(path: str, tracker: ArucoCubeTracker, every: int = 1):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    t, T, n, px, mot = [], [], [], [], []
    i = 0
    prev = None
    small_prev = None
    while True:
        ok, f = cap.read()
        if not ok:
            break
        if i % every == 0:
            ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            ts = ms / 1000.0 if ms > 0 or i == 0 else i / fps
            g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            pose, k = tracker.pose_continuous(g, prev)
            c = tracker.marker_centre()
            # whole-frame motion: the tripod is fixed, so this is hand + probe movement (taps included) and it
            # does not need the cube to be visible
            small = cv2.resize(g, (g.shape[1] // 8, g.shape[0] // 8), interpolation=cv2.INTER_AREA).astype(np.float32)
            mot.append(0.0 if small_prev is None else float(np.abs(small - small_prev).mean()))
            small_prev = small
            t.append(ts)
            T.append(np.full((4, 4), np.nan) if pose is None else pose)
            n.append(k)
            px.append(np.full(2, np.nan) if c is None else c)
            if pose is not None:
                prev = pose
        i += 1
    cap.release()
    return (np.array(t), np.array(T).reshape(-1, 4, 4), np.array(n), np.array(px).reshape(-1, 2), np.array(mot),
            fps, i)


def pixel_speed(t: np.ndarray, px: np.ndarray) -> np.ndarray:
    """Marker-centre speed in px/s; immune to pose flips, so it is the signal used for the clock offset."""
    v = np.full(len(t), np.nan)
    if len(t) > 1:
        v[1:] = np.linalg.norm(np.diff(px, axis=0), axis=1) / np.maximum(np.diff(t), 1e-6)
    return v


def read_us_times(take: Path) -> np.ndarray:
    with open(take / "us_times.csv", newline="") as f:
        return np.array([float(r["t_s"]) for r in csv.DictReader(f)])


def predicted_offset(phone_path: str, take: Path, clock_delta: float) -> float | None:
    """Offset expected from the phone file name (YYYYMMDD_HHMMSS) and the take's start time in meta.json.

    offset = phone_start - laptop_start + clock_delta, where clock_delta = laptop clock - phone clock. File-name
    seconds are whole, so this is good to about +-1.5 s; the cross-correlation refines it inside a +-3 s window.
    """
    import re
    from datetime import datetime
    m = re.search(r"(\d{8})_(\d{6})", Path(phone_path).name)
    meta = json.load(open(take / "meta.json")) if (take / "meta.json").exists() else {}
    if not m or "started" not in meta:
        return None
    phone_start = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    laptop_start = datetime.fromisoformat(meta["started"])
    return (phone_start - laptop_start).total_seconds() + clock_delta


def clock_offset(pose_t, speed, frame_t, motion, search=(-40.0, 40.0), step=0.01):
    """offset such that laptop_t = phone_t + offset, by normalised cross-correlation of the two motion signals."""
    ok = np.isfinite(speed)
    pt, ps = pose_t[ok], speed[ok]
    ps = ps - np.nanmedian(ps)
    grid = np.arange(frame_t[0], frame_t[-1], step)
    b = np.interp(grid, frame_t, motion)
    b = b - b.mean()
    nb = np.linalg.norm(b) or 1.0
    offsets = np.arange(search[0], search[1], step)
    best, best_c, curve = 0.0, -np.inf, []
    for off in offsets:
        a = np.interp(grid - off, pt, ps, left=0.0, right=0.0)
        a = a - a.mean()
        na = np.linalg.norm(a) or 1.0
        c = float(np.dot(a, b) / (na * nb))
        curve.append(c)
        if c > best_c:
            best, best_c = float(off), c
    curve = np.array(curve)
    # second-best peak at least 1 s away, as a sanity figure
    far = np.abs(offsets - best) > 1.0
    second = float(curve[far].max()) if far.any() else float("nan")
    return best, best_c, second


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("take", help="take folder with us.avi, us_times.csv, meta.json")
    ap.add_argument("--phone", required=True, help="phone video of the cube for this take")
    ap.add_argument("--camera", required=True, help="camera.json for the phone (calibrate_camera.py)")
    ap.add_argument("--screen", required=True, help="screen.json (crop + mm per pixel) from pick_crop.py")
    ap.add_argument("--marker-mm", type=float, default=35.0)
    ap.add_argument("--edge-mm", type=float, default=None, help="cube edge; default marker + 8")
    ap.add_argument("--downsample", type=int, default=2, help="shrink the cropped ultrasound image by this factor")
    ap.add_argument("--every", type=int, default=1, help="track every Nth phone frame")
    ap.add_argument("--search", type=float, nargs=2, default=None,
                    help="clock offset search window (s); default: +-3 s around the file-clock prediction")
    ap.add_argument("--clock-delta", type=float, default=1.3,
                    help="laptop clock minus phone clock (s), measured once per session from a clean jiggle take")
    ap.add_argument("--offset", type=float, default=None, help="skip the search and use this offset (s)")
    ap.add_argument("--sync", default="frame", choices=["frame", "marker"],
                    help="phone signal for the clock offset: whole-frame motion (default) or marker pixel speed")
    ap.add_argument("--min-corr", type=float, default=0.15,
                    help="below this correlation the search is distrusted and the file-clock prediction is used")
    a = ap.parse_args()

    take = Path(a.take)
    cam = json.load(open(a.camera))
    K, dist = np.array(cam["K"]), np.array(cam["dist"])
    cube = CubeSpec(edge_mm=a.edge_mm or a.marker_mm + 8, marker_mm=a.marker_mm)
    tracker = ArucoCubeTracker(K, dist, cube)
    screen = json.load(open(a.screen))
    r0, r1, c0, c1 = screen["crop"]
    mm_px = float(screen["mm_per_px"]) * a.downsample

    print(f"tracking cube in {a.phone} ...")
    pose_t, T, n_markers, px, phone_motion, phone_fps, n_phone = track_phone(a.phone, tracker, a.every)
    tracked = ~np.isnan(T[:, 0, 0])
    print(f"  {tracked.sum()}/{len(T)} frames tracked ({100 * tracked.mean():.0f}%), phone {phone_fps:.2f} fps nominal")

    print(f"reading ultrasound {take / 'us.avi'} ...")
    frame_t = read_us_times(take)
    cap = cv2.VideoCapture(str(take / "us.avi"))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)[r0:r1, c0:c1]
        if a.downsample > 1:
            g = cv2.resize(g, (g.shape[1] // a.downsample, g.shape[0] // a.downsample), interpolation=cv2.INTER_AREA)
        frames.append(g)
    cap.release()
    frames = np.array(frames)
    n = min(len(frames), len(frame_t))
    if len(frames) != len(frame_t):
        print(f"  warning: {len(frames)} video frames vs {len(frame_t)} timestamps; using the first {n}")
    frames, frame_t = frames[:n], frame_t[:n]
    print(f"  {n} frames {frames.shape[2]}x{frames.shape[1]} px, {mm_px:.4f} mm/px after downsample")

    speed = phone_motion if a.sync == "frame" else pixel_speed(pose_t, px)
    if np.isfinite(speed).any():
        speed = np.minimum(speed, np.nanpercentile(speed, 99))
    motion = frame_motion(frames)
    predicted = predicted_offset(a.phone, take, a.clock_delta)
    if a.offset is None:
        if a.search is not None:
            search = tuple(a.search)
        elif predicted is not None:
            search = (predicted - 3.0, predicted + 3.0)
        else:
            search = (-40.0, 40.0)
        offset, corr, second = clock_offset(pose_t, speed, frame_t, motion, search)
        print(f"clock offset laptop = phone + {offset:+.3f} s  (corr {corr:.2f}, next best peak {second:.2f}; "
              f"predicted from file clocks {predicted if predicted is None else round(predicted, 1)}, searched {search[0]:.1f}..{search[1]:.1f})")
        at_edge = min(abs(offset - search[0]), abs(offset - search[1])) < 0.15
        if (corr < a.min_corr or at_edge) and predicted is not None:
            why = "correlation too weak" if corr < a.min_corr else "best offset sits on the search-window edge (no real peak)"
            print(f"  {why}; using the file-clock prediction {predicted:+.1f} s (about +-1.5 s)")
            offset, corr = predicted, float("nan")
    else:
        offset, corr, second = a.offset, float("nan"), float("nan")
        print(f"using given offset {offset:+.3f} s")

    w = RecordingWriter(take, frames.shape[1:], compress=True)
    for t, g in zip(frame_t, frames):
        w.add_frame(float(t), g)
    for t, Ti, k in zip(pose_t + offset, T, n_markers):
        w.add_pose(float(t), None if np.isnan(Ti[0, 0]) else Ti, int(k))
    old = json.load(open(take / "meta.json")) if (take / "meta.json").exists() else {}
    old.update(phone_video=str(a.phone), phone_fps_nominal=phone_fps, phone_frames=n_phone,
               phone_tracked_fraction=float(tracked.mean()), clock_offset_s=offset, clock_offset_corr=corr,
               clock_offset_second_peak=second, clock_offset_predicted=predicted, sync_signal=a.sync, camera_json=str(a.camera), screen_json=str(a.screen),
               crop=[r0, r1, c0, c1], downsample=a.downsample, mm_per_px=mm_px, lag_s=0.0,
               marker_mm=a.marker_mm, edge_mm=cube.edge_mm, pipeline="phone_to_bench.py")
    folder = w.close(old)
    print(f"wrote frames.h5 / poses.npz / meta.json -> {folder}")


if __name__ == "__main__":
    main()
