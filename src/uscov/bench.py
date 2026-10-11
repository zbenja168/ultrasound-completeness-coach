"""Bench-day glue: the pieces that connect real hardware recordings to the coverage engine.

  Recording format      RecordingWriter / load_recording: frames + timestamps (HDF5), cube poses + timestamps (npz),
                        optional raw webcam video, meta.json. One folder per take under data/bench_YYYY-MM-DD/.
  Pose <-> frame pairing pair_poses_to_frames: nearest cube pose for each ultrasound frame, after removing the lag.
  Spatial calibration   pinhead_calibrate: the fixed image->cube transform from a pinhead imaged at many probe poses.
  Temporal alignment    estimate_lag: cross-correlate probe speed (cube) with image motion (frames) from a jiggle test.
  Screen scale          mm_per_px_from_ruler: millimetres per pixel from two clicked ruler ticks.
  Known-distance check  detect_stops / stop_distances: slide-along-a-ruler accuracy from a recording.

Conventions follow data.py: a pixel is homogeneous [col, row, 0, 1] (1-based), and
    world point = T_tool_world @ image_to_tool @ scale @ pixel.
The 'tool' here is the marker cube (cube frame -> camera frame is what ArucoCubeTracker returns, so the webcam
is the world frame).
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as R

from .data import Calib, Scan


# ----------------------------------------------------------------------------- calibration containers

def make_scale(mm_per_px: float | tuple[float, float]) -> np.ndarray:
    mx, my = (mm_per_px, mm_per_px) if np.isscalar(mm_per_px) else mm_per_px
    return np.diag([float(mx), float(my), 1.0, 1.0])


def make_calib(mm_per_px: float | tuple[float, float], image_to_tool: np.ndarray) -> Calib:
    return Calib(scale=make_scale(mm_per_px), image_to_tool=np.asarray(image_to_tool, np.float64))


def save_calib_json(path: str | Path, calib: Calib, **extra) -> None:
    d = {"mm_per_px": list(calib.mm_per_pixel), "image_to_tool": calib.image_to_tool.tolist()}
    d.update(extra)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    json.dump(d, open(path, "w"), indent=2)


def load_calib_json(path: str | Path) -> Calib:
    d = json.load(open(path))
    return make_calib(tuple(d["mm_per_px"]), np.array(d["image_to_tool"]))


def mm_per_px_from_ruler(p0, p1, mm: float) -> float:
    """Two clicked points on the on-screen depth ruler (pixels) that are `mm` apart."""
    d = float(np.hypot(p1[0] - p0[0], p1[1] - p0[1]))
    if d <= 0:
        raise ValueError("ruler points coincide")
    return mm / d


# ----------------------------------------------------------------------------- recording format

class RecordingWriter:
    """Writes one take: frames.h5 (frames [N,H,W] uint8 + t), poses.npz (t, T, n_markers), meta.json.

    Frames are appended to a resizable, chunked HDF5 dataset so long takes never sit in memory.
    Timestamps are seconds from a shared origin chosen by the caller (both streams must use the same one).
    """

    def __init__(self, folder: str | Path, frame_shape: tuple[int, int], compress: bool = True):
        import h5py
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        h, w = frame_shape
        self.h5 = h5py.File(self.folder / "frames.h5", "w")
        kw = dict(compression="gzip", compression_opts=1) if compress else {}
        self.d_frames = self.h5.create_dataset("frames", shape=(0, h, w), maxshape=(None, h, w), dtype="uint8",
                                               chunks=(8, h, w), **kw)
        self.d_t = self.h5.create_dataset("t", shape=(0,), maxshape=(None,), dtype="float64")
        self.n_frames = 0
        self.pose_t: list[float] = []
        self.pose_T: list[np.ndarray] = []
        self.pose_n: list[int] = []
        self.cam_t: list[float] = []
        self.closed = False

    def add_frame(self, t: float, gray: np.ndarray) -> None:
        i = self.n_frames
        self.d_frames.resize(i + 1, axis=0)
        self.d_t.resize(i + 1, axis=0)
        self.d_frames[i] = gray
        self.d_t[i] = t
        self.n_frames += 1

    def add_pose(self, t: float, T: np.ndarray | None, n_markers: int = 0) -> None:
        self.pose_t.append(float(t))
        self.pose_T.append(np.full((4, 4), np.nan) if T is None else np.asarray(T, np.float64))
        self.pose_n.append(int(n_markers))

    def add_cam_time(self, t: float) -> None:
        """Timestamp of a raw webcam frame written to cam.avi by the caller (same index order)."""
        self.cam_t.append(float(t))

    def close(self, meta: dict | None = None) -> Path:
        if self.closed:
            return self.folder
        self.h5.close()
        np.savez_compressed(self.folder / "poses.npz", t=np.array(self.pose_t), T=np.array(self.pose_T).reshape(-1, 4, 4),
                            n_markers=np.array(self.pose_n), cam_t=np.array(self.cam_t))
        m = dict(meta or {})
        m.update(n_frames=self.n_frames, n_poses=len(self.pose_t),
                 n_tracked=int(sum(1 for T in self.pose_T if not np.isnan(T[0, 0]))))
        json.dump(m, open(self.folder / "meta.json", "w"), indent=2, default=str)
        self.closed = True
        return self.folder


@dataclass
class BenchRecording:
    folder: Path
    frames: np.ndarray        # [N,H,W] uint8 (in memory) or an h5py dataset
    frame_t: np.ndarray       # [N] s
    pose_t: np.ndarray        # [M] s
    T: np.ndarray             # [M,4,4] cube->camera, NaN rows when not tracked
    n_markers: np.ndarray     # [M]
    meta: dict = field(default_factory=dict)

    @property
    def n_frames(self) -> int:
        return int(self.frame_t.shape[0])

    @property
    def tracked_fraction(self) -> float:
        return float(np.mean(~np.isnan(self.T[:, 0, 0]))) if len(self.T) else 0.0

    @property
    def fps(self) -> float:
        return float(1.0 / np.median(np.diff(self.frame_t))) if self.n_frames > 1 else float("nan")


def load_recording(folder: str | Path, into_memory: bool = True) -> BenchRecording:
    import h5py
    folder = Path(folder)
    h5 = h5py.File(folder / "frames.h5", "r")
    frames = h5["frames"][...] if into_memory else h5["frames"]
    frame_t = h5["t"][...]
    if into_memory:
        h5.close()
    p = np.load(folder / "poses.npz")
    meta = json.load(open(folder / "meta.json")) if (folder / "meta.json").exists() else {}
    return BenchRecording(folder, frames, frame_t, p["t"], p["T"], p["n_markers"], meta)


def pair_poses_to_frames(frame_t: np.ndarray, pose_t: np.ndarray, T: np.ndarray, lag_s: float = 0.0,
                         tol_s: float | None = None) -> np.ndarray:
    """Nearest tracked cube pose for every frame, [N,4,4] with NaN rows where none is close enough.

    `lag_s` = image timestamp minus pose timestamp for the same physical instant (positive: the capture card
    delivers later than the webcam), from estimate_lag. `tol_s` defaults to one pose interval.
    """
    T = np.asarray(T)
    ok = ~np.isnan(T[:, 0, 0])
    out = np.full((len(frame_t), 4, 4), np.nan)
    if ok.sum() == 0:
        return out
    pt, PT = np.asarray(pose_t)[ok], T[ok]
    if tol_s is None:
        tol_s = float(np.median(np.diff(np.asarray(pose_t)))) if len(pose_t) > 1 else 0.05
    want = np.asarray(frame_t) - lag_s
    j = np.searchsorted(pt, want)
    j0 = np.clip(j - 1, 0, len(pt) - 1)
    j1 = np.clip(j, 0, len(pt) - 1)
    pick = np.where(np.abs(pt[j1] - want) < np.abs(pt[j0] - want), j1, j0)
    near = np.abs(pt[pick] - want) <= tol_s
    out[near] = PT[pick[near]]
    return out


def recording_to_scan(rec: BenchRecording, calib: Calib, lag_s: float = 0.0, smooth_window: int = 9,
                      name: str | None = None):
    """Scan the engine can run, plus the FusedPoses that says which frames were tracked / bridged / unknown."""
    from .tracker import fuse
    primary = pair_poses_to_frames(rec.frame_t, rec.pose_t, rec.T, lag_s)
    fused = fuse(primary, None, smooth_window=smooth_window)
    frames = rec.frames if isinstance(rec.frames, np.ndarray) else rec.frames[...]
    return Scan(name or rec.folder.name, frames, fused.T, calib), fused


# ----------------------------------------------------------------------------- pinhead spatial calibration

def pinhead_residuals(x: np.ndarray, T_tool_world: np.ndarray, pix_mm: np.ndarray) -> np.ndarray:
    Rm = R.from_rotvec(x[:3]).as_matrix()
    t, pin = x[3:6], x[6:9]
    p_img = np.c_[pix_mm, np.zeros(len(pix_mm))]                    # [N,3] image mm, z = 0
    p_tool = p_img @ Rm.T + t
    p_world = np.einsum("nij,nj->ni", T_tool_world[:, :3, :3], p_tool) + T_tool_world[:, :3, 3]
    return (p_world - pin).ravel()


@dataclass
class PinheadResult:
    image_to_tool: np.ndarray   # 4x4
    pin_world: np.ndarray       # 3
    rms_mm: float
    per_pose_mm: np.ndarray     # [N]
    n_poses: int

    def calib(self, mm_per_px) -> Calib:
        return make_calib(mm_per_px, self.image_to_tool)


def pinhead_calibrate(T_tool_world: np.ndarray, pixels: np.ndarray, mm_per_px: float | tuple[float, float],
                      n_starts: int = 12, seed: int = 0) -> PinheadResult:
    """Solve the fixed image->tool transform from one pinhead seen at many probe poses.

    T_tool_world [N,4,4]: cube pose at each click. pixels [N,2]: (col,row) of the pinhead, 1-based as in data.py.
    Nine unknowns (6 for the transform, 3 for the pin position in the world) from 3N equations; use at least 10
    poses, and rotate the probe about the pin through 30 degrees or more on two axes, or the fit is ambiguous.
    Several random rotation starts guard against the mirror-image local minimum.
    """
    T_tool_world = np.asarray(T_tool_world, np.float64)
    pixels = np.asarray(pixels, np.float64)
    N = len(pixels)
    if N < 6:
        raise ValueError("need at least 6 pinhead observations (aim for 10 to 15)")
    s = make_scale(mm_per_px)
    pix_mm = pixels * np.array([s[0, 0], s[1, 1]])
    rng = np.random.default_rng(seed)
    centre_world = T_tool_world[:, :3, 3].mean(axis=0)
    best = None
    for k in range(n_starts):
        rv = np.zeros(3) if k == 0 else R.random(random_state=rng.integers(1 << 31)).as_rotvec()
        x0 = np.r_[rv, np.zeros(3), centre_world]
        sol = least_squares(pinhead_residuals, x0, args=(T_tool_world, pix_mm), method="lm", max_nfev=4000)
        if best is None or sol.cost < best.cost:
            best = sol
    res = pinhead_residuals(best.x, T_tool_world, pix_mm).reshape(-1, 3)
    per = np.linalg.norm(res, axis=1)
    T = np.eye(4)
    T[:3, :3] = R.from_rotvec(best.x[:3]).as_matrix()
    T[:3, 3] = best.x[3:6]
    return PinheadResult(T, best.x[6:9].copy(), float(np.sqrt((per ** 2).mean())), per, N)


def pinhead_pixel(T_tool_world: np.ndarray, image_to_tool: np.ndarray, mm_per_px, pin_world: np.ndarray) -> np.ndarray:
    """Where the pin would appear (col,row) in a frame taken at this pose, if it lies in the image plane.

    Inverse of the forward model, used for synthetic tests and for checking a calibration on new frames.
    """
    P = np.linalg.inv(np.asarray(T_tool_world) @ np.asarray(image_to_tool) @ make_scale(mm_per_px))
    p = P @ np.r_[pin_world, 1.0]
    return p[:2]


# ----------------------------------------------------------------------------- temporal alignment

def frame_motion(frames: np.ndarray, step: int = 4) -> np.ndarray:
    """Mean absolute difference between consecutive frames (subsampled pixels); [N], first entry 0."""
    f = np.asarray(frames)[:, ::step, ::step].astype(np.float32)
    m = np.zeros(len(f), np.float32)
    if len(f) > 1:
        m[1:] = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    return m


def pose_speed(pose_t: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Translation speed in mm/s per pose sample; NaN where either neighbour is untracked. [M], first entry NaN."""
    T = np.asarray(T)
    tr = T[:, :3, 3]
    v = np.full(len(T), np.nan)
    if len(T) > 1:
        dt = np.diff(np.asarray(pose_t))
        v[1:] = np.linalg.norm(np.diff(tr, axis=0), axis=1) / np.maximum(dt, 1e-6)
    return v


def _resample(t: np.ndarray, s: np.ndarray, grid: np.ndarray) -> np.ndarray:
    ok = np.isfinite(s)
    if ok.sum() < 3:
        return np.zeros_like(grid)
    y = np.interp(grid, t[ok], s[ok], left=np.nan, right=np.nan)
    y = np.where(np.isfinite(y), y, np.nanmean(y))
    y = y - y.mean()
    n = np.linalg.norm(y)
    return y / n if n > 0 else y


def estimate_lag(t_a: np.ndarray, s_a: np.ndarray, t_b: np.ndarray, s_b: np.ndarray, max_lag_s: float = 1.0,
                 dt: float = 0.005) -> tuple[float, float]:
    """Lag of signal b behind signal a (seconds) by normalised cross-correlation, and the peak correlation.

    Positive result: b happens later than a. For the jiggle test call it as
        estimate_lag(pose_t, pose_speed(...), frame_t, frame_motion(...))
    and pass the result as `lag_s` to pair_poses_to_frames. Peak correlation below ~0.3 means the signals did
    not line up; jiggle harder or longer.
    """
    t0 = max(np.nanmin(t_a), np.nanmin(t_b))
    t1 = min(np.nanmax(t_a), np.nanmax(t_b))
    if t1 - t0 < 4 * max_lag_s:
        raise ValueError("recordings overlap too little for the requested lag range")
    grid = np.arange(t0, t1, dt)
    a = _resample(np.asarray(t_a), np.asarray(s_a, float), grid)
    b = _resample(np.asarray(t_b), np.asarray(s_b, float), grid)
    k = int(round(max_lag_s / dt))
    lags = np.arange(-k, k + 1)
    best, best_c = 0.0, -np.inf
    for L in lags:
        if L >= 0:
            c = float(np.dot(a[: len(a) - L], b[L:]))
        else:
            c = float(np.dot(a[-L:], b[: len(b) + L]))
        if c > best_c:
            best, best_c = L * dt, c
    return float(best), float(best_c)


# ----------------------------------------------------------------------------- known-distance check

@dataclass
class Stop:
    t_start: float
    t_end: float
    centre: np.ndarray    # 3, mm


def detect_stops(pose_t: np.ndarray, T: np.ndarray, speed_thresh_mm_s: float = 4.0, min_dwell_s: float = 0.6,
                 smooth_window: int = 9) -> list[Stop]:
    """Dwell periods of the probe (speed below threshold for at least min_dwell_s), each with its mean position."""
    from .noise import smooth_poses
    T = np.asarray(T)
    ok = ~np.isnan(T[:, 0, 0])
    t = np.asarray(pose_t)[ok]
    Ts = smooth_poses(T[ok], smooth_window) if ok.sum() >= 3 else T[ok]
    v = pose_speed(t, Ts)
    still = np.r_[False, v[1:] < speed_thresh_mm_s]
    stops: list[Stop] = []
    i = 0
    while i < len(still):
        if still[i]:
            j = i
            while j + 1 < len(still) and still[j + 1]:
                j += 1
            if t[j] - t[i] >= min_dwell_s:
                stops.append(Stop(float(t[i]), float(t[j]), Ts[i:j + 1, :3, 3].mean(axis=0)))
            i = j + 1
        else:
            i += 1
    return stops


def stop_distances(stops: list[Stop]) -> np.ndarray:
    c = np.array([s.centre for s in stops])
    return np.linalg.norm(np.diff(c, axis=0), axis=1) if len(c) > 1 else np.zeros(0)


def known_distance_rows(distances: np.ndarray, expected: list[float] | None) -> list[dict]:
    rows = []
    for i, d in enumerate(distances):
        e = None
        if expected:
            e = expected[i] if len(expected) == len(distances) else expected[i % len(expected)]
        rows.append(dict(move=i + 1, measured_mm=float(d), expected_mm=e,
                         error_mm=None if e is None else float(d - e)))
    return rows


def now_s(t0: float) -> float:
    return time.perf_counter() - t0
