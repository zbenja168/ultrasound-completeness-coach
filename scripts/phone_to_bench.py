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


def mov_creation_local(path):
    """Recording start of a QuickTime/MP4 file as local wall-clock time (naive datetime), or None.

    Prefers the com.apple.quicktime.creationdate string (local time with zone, e.g. 2026-10-30T15:52:49-0500);
    falls back to the mvhd creation time (UTC seconds since 1904) converted to this machine's local zone.
    """
    import re
    import struct
    from datetime import datetime, timedelta, timezone

    def atoms(f, start, end):
        pos = start
        while pos + 8 <= end:
            f.seek(pos)
            hdr = f.read(8)
            if len(hdr) < 8:
                return
            size, typ = struct.unpack(">I4s", hdr)
            hs = 8
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
                hs = 16
            if size == 0:
                size = end - pos
            yield pos, size, typ, hs
            pos += size

    p = Path(path)
    try:
        with open(p, "rb") as f:
            total = p.stat().st_size
            mvhd = None
            for pos, size, typ, hs in atoms(f, 0, total):
                if typ != b"moov":
                    continue
                for pos2, size2, typ2, hs2 in atoms(f, pos + hs, pos + size):
                    if typ2 == b"mvhd":
                        f.seek(pos2 + hs2)
                        v = f.read(1)[0]
                        f.seek(pos2 + hs2 + 4)
                        mvhd = struct.unpack(">Q" if v else ">I", f.read(8 if v else 4))[0]
                    elif typ2 == b"meta":
                        f.seek(pos2 + hs2)
                        blob = f.read(min(size2 - hs2, 1 << 20))
                        m = re.search(rb"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)[+-]\d{4}", blob)
                        if m:
                            return datetime.fromisoformat(m.group(1).decode())
            if mvhd:
                utc = datetime(1904, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=mvhd)
                return utc.astimezone().replace(tzinfo=None)
    except OSError:
        return None
    return None


def predicted_offset(phone_path: str, take: Path, clock_delta: float) -> float | None:
    """Offset expected from the phone file name (YYYYMMDD_HHMMSS) and the take's start time in meta.json.

    offset = phone_start - laptop_start + clock_delta, where clock_delta = laptop clock - phone clock. File-name
    seconds are whole, so this is good to about +-1.5 s; the cross-correlation refines it inside a +-3 s window.
    """
    import re
    from datetime import datetime
    m = re.search(r"(\d{8})_(\d{6})", Path(phone_path).name)
    meta = json.load(open(take / "meta.json")) if (take / "meta.json").exists() else {}
    if "started" not in meta:
        return None
    if m:
        phone_start = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    else:
        phone_start = mov_creation_local(phone_path)   # iPhone .MOV: no time in the name, read the file header
        if phone_start is None:
            return None
    laptop_start = datetime.fromisoformat(meta["started"])
    return (phone_start - laptop_start).total_seconds() + clock_delta


def smooth_signal(t, x, win_s):
    """Moving average over win_s seconds; NaNs are bridged linearly first."""
    x = np.asarray(x, float)
    ok = np.isfinite(x)
    if ok.sum() < 3:
        return np.zeros_like(x)
    xi = np.interp(t, t[ok], x[ok])
    n = max(1, int(round(win_s / max(np.median(np.diff(t)), 1e-3))))
    return np.convolve(xi, np.ones(n) / n, mode="same")


def us_flow_y(frames):
    """Signed vertical image shift between consecutive ultrasound frames (px), by phase correlation: contact
    changes and tilts move the fan image up and down. Zero where the correlation is unreliable."""
    import cv2
    small = [cv2.resize(f, (250, 198)).astype(np.float32) for f in frames]
    win = cv2.createHanningWindow((250, 198), cv2.CV_32F)
    dy = np.zeros(len(frames))
    for i in range(1, len(frames)):
        (sx, sy), resp = cv2.phaseCorrelate(small[i - 1], small[i], win)
        if resp > 0.05 and abs(sy) < 30:
            dy[i] = sy
    return dy


def corr_curve(offs, grid, t, x, ft, us):
    """Normalised cross-correlation of phone signal x(t) shifted by each offset against ultrasound signal us(ft)."""
    b = np.interp(grid, ft, us)
    b = b - b.mean()
    nb = np.linalg.norm(b) or 1.0
    ok = np.isfinite(x)
    out = np.zeros(len(offs))
    if ok.sum() < 3:
        return out
    for k, o in enumerate(offs):
        a = np.interp(grid - o, t[ok], x[ok], left=0.0, right=0.0)
        a = a - a.mean()
        out[k] = float(a @ b) / ((np.linalg.norm(a) or 1.0) * nb)
    return out


def fused_offset(pose_t, T, phone_motion, frame_t, frames, motion, search, predicted, prior_sigma, step=0.02):
    """Clock offset from three weak cues fused with the file-clock prior (2026-10-30 lesson: any single cue
    picks a wrong peak on some takes).
      1. whole-frame phone motion  vs ultrasound frame-to-frame motion   (taps, hand movement)
      2. 3-D cube speed            vs ultrasound frame-to-frame motion   (probe moving vs still)
      3. signed cube velocity along its main axis vs signed vertical image flow (either sign)
    Each curve is clipped at 0, scaled to its own max, summed, and multiplied by a Gaussian prior around the
    file-clock prediction. Returns (offset, peak/next-peak ratio >1 s away, {signal: (peak offset, corr)})."""
    offs = np.arange(search[0], search[1], step)
    grid = np.arange(frame_t[0], frame_t[-1], step)
    us_m = smooth_signal(frame_t, np.minimum(motion, np.percentile(motion, 99)), 0.3)
    us_y = smooth_signal(frame_t, us_flow_y(frames), 0.25)
    pm = smooth_signal(pose_t, np.minimum(phone_motion, np.percentile(phone_motion, 99)), 0.3)
    sp = pose_speed(pose_t, T)
    sp = smooth_signal(pose_t, np.minimum(sp, np.nanpercentile(sp, 99)) if np.isfinite(sp).any() else sp, 0.3)
    pos = T[:, :3, 3]
    ok = np.isfinite(pos[:, 0])
    vel = np.full(len(pose_t), np.nan)
    if ok.sum() > 10:
        P = pos[ok] - pos[ok].mean(axis=0)
        _, V = np.linalg.eigh(P.T @ P)
        proj = pos @ V[:, -1]
        vel[1:] = np.diff(proj) / np.maximum(np.diff(pose_t), 1e-6)
        vel[np.abs(vel) > 300] = np.nan
    c1 = corr_curve(offs, grid, pose_t, pm, frame_t, us_m)
    c2 = corr_curve(offs, grid, pose_t, sp, frame_t, us_m)
    c3 = np.abs(corr_curve(offs, grid, pose_t, smooth_signal(pose_t, vel, 0.25), frame_t, us_y))
    peaks = {"frame": (float(offs[c1.argmax()]), float(c1.max())), "pose": (float(offs[c2.argmax()]), float(c2.max())),
             "flow": (float(offs[c3.argmax()]), float(c3.max()))}
    fused = np.zeros(len(offs))
    for c in (c1, c2, c3):
        c = np.clip(c, 0, None)
        if c.max() > 0:
            fused += c / c.max()
    if predicted is not None and prior_sigma > 0:
        fused *= np.exp(-0.5 * ((offs - predicted) / prior_sigma) ** 2)
    k = int(fused.argmax())
    far = np.abs(offs - offs[k]) > 1.0
    sharp = float(fused[k] / fused[far].max()) if far.any() and fused[far].max() > 0 else float("inf")
    return float(offs[k]), sharp, peaks


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
    ap.add_argument("--marker-mm", type=float, default=None, help="printed marker size (default 35, or the layout file's)")
    ap.add_argument("--layout", default=None, help="cube layout JSON (edge_mm, marker_mm, face_ids, corner_shift); see CubeSpec.from_json")
    ap.add_argument("--search-halfwidth", type=float, default=3.0, help="half-width (s) of the offset search around the file-clock prediction")
    ap.add_argument("--edge-mm", type=float, default=None, help="cube edge; default marker + 8")
    ap.add_argument("--downsample", type=int, default=2, help="shrink the cropped ultrasound image by this factor")
    ap.add_argument("--every", type=int, default=1, help="track every Nth phone frame")
    ap.add_argument("--search", type=float, nargs=2, default=None,
                    help="clock offset search window (s); default: +-3 s around the file-clock prediction")
    ap.add_argument("--clock-delta", type=float, default=1.3,
                    help="laptop clock minus phone clock (s), measured once per session from a clean jiggle take")
    ap.add_argument("--offset", type=float, default=None, help="skip the search and use this offset (s)")
    ap.add_argument("--sync", default="fused", choices=["fused", "frame", "marker", "pose"],
                    help="phone signal for the clock offset: whole-frame motion (default), marker pixel speed, or 3-D cube speed from the poses")
    ap.add_argument("--prior-sigma", type=float, default=1.5, help="fused sync: width (s) of the file-clock prior")
    ap.add_argument("--min-corr", type=float, default=0.15,
                    help="below this correlation the search is distrusted and the file-clock prediction is used")
    a = ap.parse_args()
    a.marker_mm_given = a.marker_mm is not None
    if a.marker_mm is None:
        a.marker_mm = 35.0

    take = Path(a.take)
    cam = json.load(open(a.camera))
    K, dist = np.array(cam["K"]), np.array(cam["dist"])
    if a.layout:
        cube = CubeSpec.from_json(a.layout, marker_mm=a.marker_mm if a.marker_mm_given else None)
    else:
        cube = CubeSpec(edge_mm=a.edge_mm or a.marker_mm + 8, marker_mm=a.marker_mm)
    print(f"cube: marker {cube.marker_mm:g} mm, edge {cube.edge_mm:g} mm, faces {cube.face_ids}, shifts {cube.corner_shift}")
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

    motion = frame_motion(frames)
    predicted = predicted_offset(a.phone, take, a.clock_delta)
    sharp = float("nan")
    peaks = {}
    if a.offset is not None:
        offset, corr, second = a.offset, float("nan"), float("nan")
        print(f"using given offset {offset:+.3f} s")
    elif a.sync == "fused":
        if a.search is not None:
            search = tuple(a.search)
        elif predicted is not None:
            search = (predicted - a.search_halfwidth, predicted + a.search_halfwidth)
        else:
            search = (-40.0, 40.0)
        offset, sharp, peaks = fused_offset(pose_t, T, phone_motion, frame_t, frames, motion, search,
                                            predicted, a.prior_sigma)
        corr, second = sharp, float("nan")
        print(f"clock offset laptop = phone + {offset:+.3f} s  (fused; peak/next-peak {sharp:.2f}; per-signal peaks "
              + ", ".join(f"{k} {v[0]:+.2f} (corr {v[1]:.2f})" for k, v in peaks.items())
              + f"; predicted from file clocks {predicted if predicted is None else round(predicted, 1)}, searched {search[0]:.1f}..{search[1]:.1f})")
        if sharp < 1.3:
            print("  weak peak: treat this offset as approximate (about +-1.5 s)")
    else:
        if a.sync == "frame":
            speed = phone_motion
        elif a.sync == "pose":
            speed = pose_speed(pose_t, T)        # 3-D cube-centre speed (mm/s); clean now that single-face poses do not flip
        else:
            speed = pixel_speed(pose_t, px)
        if np.isfinite(speed).any():
            speed = np.minimum(speed, np.nanpercentile(speed, 99))
        if a.search is not None:
            search = tuple(a.search)
        elif predicted is not None:
            search = (predicted - a.search_halfwidth, predicted + a.search_halfwidth)
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

    w = RecordingWriter(take, frames.shape[1:], compress=True)
    for t, g in zip(frame_t, frames):
        w.add_frame(float(t), g)
    for t, Ti, k in zip(pose_t + offset, T, n_markers):
        w.add_pose(float(t), None if np.isnan(Ti[0, 0]) else Ti, int(k))
    old = json.load(open(take / "meta.json")) if (take / "meta.json").exists() else {}
    old.update(phone_video=str(a.phone), phone_fps_nominal=phone_fps, phone_frames=n_phone,
               phone_tracked_fraction=float(tracked.mean()), clock_offset_s=offset, clock_offset_corr=corr,
               clock_offset_second_peak=second, clock_offset_predicted=predicted, sync_signal=a.sync,
               clock_offset_sharpness=sharp, clock_offset_signal_peaks={k: list(v) for k, v in peaks.items()}, camera_json=str(a.camera), screen_json=str(a.screen),
               crop=[r0, r1, c0, c1], downsample=a.downsample, mm_per_px=mm_px, lag_s=0.0,
               marker_mm=a.marker_mm, edge_mm=cube.edge_mm, pipeline="phone_to_bench.py")
    folder = w.close(old)
    print(f"wrote frames.h5 / poses.npz / meta.json -> {folder}")


if __name__ == "__main__":
    main()
