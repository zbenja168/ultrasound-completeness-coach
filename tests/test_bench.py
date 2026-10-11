"""Synthetic tests for the bench-day glue: pinhead calibration, lag estimate, stop detection, recording round trip."""
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation as R

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uscov.bench import (RecordingWriter, load_recording, pair_poses_to_frames, recording_to_scan, make_calib,  # noqa: E402
                         pinhead_calibrate, pinhead_pixel, estimate_lag, frame_motion, pose_speed, detect_stops,
                         stop_distances, mm_per_px_from_ruler, save_calib_json, load_calib_json)
from uscov.tracker import PRIMARY  # noqa: E402


def _rigid(rotvec_deg, t):
    T = np.eye(4)
    T[:3, :3] = R.from_rotvec(np.deg2rad(rotvec_deg)).as_matrix()
    T[:3, 3] = t
    return T


def _pinhead_setup(n=15, seed=1, pix_noise=0.0, pose_noise_mm=0.0, pose_noise_deg=0.0):
    rng = np.random.default_rng(seed)
    truth = _rigid([88.0, 3.0, 12.0], [21.0, -6.0, 31.0])
    mm_per_px = (0.2, 0.2)
    pin = np.array([90.0, 40.0, 280.0])
    scale = np.diag([0.2, 0.2, 1, 1])
    poses, pixels = [], []
    for _ in range(n):
        u, v = rng.uniform(60, 580), rng.uniform(60, 420)
        p_img = scale @ np.array([u, v, 0, 1.0])
        p_tool = truth @ p_img
        Rw = R.random(random_state=rng.integers(1 << 31)).as_matrix()
        Tw = np.eye(4)
        Tw[:3, :3] = Rw
        Tw[:3, 3] = pin - Rw @ p_tool[:3]
        poses.append(Tw)
        pixels.append([u, v])
    poses, pixels = np.array(poses), np.array(pixels)
    pixels_n = pixels + rng.normal(0, pix_noise, pixels.shape)
    poses_n = poses.copy()
    for i in range(n):
        d = _rigid(rng.normal(0, pose_noise_deg, 3), rng.normal(0, pose_noise_mm, 3))
        poses_n[i] = poses[i] @ d
    return truth, mm_per_px, pin, poses, pixels, poses_n, pixels_n


def _transform_gap_mm(A, B, mm_per_px=(0.2, 0.2)):
    """Max disagreement of two image->tool transforms over the image area (mm)."""
    s = np.diag([mm_per_px[0], mm_per_px[1], 1, 1])
    pts = np.array([[1, 1, 0, 1], [640, 1, 0, 1], [1, 480, 0, 1], [640, 480, 0, 1], [320, 240, 0, 1]], float)
    return float(np.max(np.linalg.norm(((A - B) @ s @ pts.T)[:3], axis=0)))


def test_pinhead_pixel_inverts_forward_model():
    truth, mm, pin, poses, pixels, _, _ = _pinhead_setup(n=5)
    for Tw, px in zip(poses, pixels):
        assert np.allclose(pinhead_pixel(Tw, truth, mm, pin), px, atol=1e-6)


def test_pinhead_calibration_recovers_transform_clean():
    truth, mm, pin, poses, pixels, _, _ = _pinhead_setup(n=12)
    res = pinhead_calibrate(poses, pixels, mm)
    assert res.rms_mm < 1e-3
    assert _transform_gap_mm(res.image_to_tool, truth) < 1e-2
    assert np.linalg.norm(res.pin_world - pin) < 1e-2


def test_pinhead_calibration_with_realistic_noise():
    truth, mm, pin, _, _, poses_n, pixels_n = _pinhead_setup(n=15, seed=3, pix_noise=1.0, pose_noise_mm=0.4,
                                                              pose_noise_deg=0.3)
    res = pinhead_calibrate(poses_n, pixels_n, mm)
    assert res.rms_mm < 2.5
    assert _transform_gap_mm(res.image_to_tool, truth) < 3.0
    assert np.linalg.norm(res.pin_world - pin) < 2.0


def test_calib_json_round_trip(tmp_path):
    truth = _rigid([10, 20, 30], [1, 2, 3])
    c = make_calib((0.2, 0.25), truth)
    save_calib_json(tmp_path / "c.json", c, note="x")
    c2 = load_calib_json(tmp_path / "c.json")
    assert np.allclose(c2.image_to_tool, truth) and c2.mm_per_pixel == (0.2, 0.25)


def test_lag_estimate_finds_known_shift():
    rng = np.random.default_rng(0)
    t_a = np.arange(0, 20, 1 / 60)
    taps = np.zeros_like(t_a)
    for c in (3, 6, 9.5, 12, 15.2):
        taps += np.exp(-((t_a - c) ** 2) / (2 * 0.08 ** 2))
    true_lag = 0.12
    t_b = np.arange(0.01, 20, 1 / 30)
    s_b = np.interp(t_b - true_lag, t_a, taps) + rng.normal(0, 0.05, len(t_b))
    s_a = taps + rng.normal(0, 0.05, len(t_a))
    s_a[::7] = np.nan     # untracked samples must not break it
    lag, corr = estimate_lag(t_a, s_a, t_b, s_b, max_lag_s=0.5)
    assert abs(lag - true_lag) < 0.012 and corr > 0.5


def test_frame_motion_and_pose_speed_shapes():
    frames = np.zeros((5, 16, 16), np.uint8)
    frames[2] = 100
    m = frame_motion(frames, step=1)
    assert m[0] == 0 and m[2] > 0 and m[3] > 0 and m[1] == 0 and m[4] == 0
    T = np.tile(np.eye(4), (4, 1, 1))
    T[1, :3, 3] = [3, 4, 0]
    T[2] = np.nan
    v = pose_speed(np.array([0, 0.5, 1.0, 1.5]), T)
    assert np.isnan(v[0]) and abs(v[1] - 10) < 1e-9 and np.isnan(v[2]) and np.isnan(v[3])


def test_detect_stops_and_distances():
    rng = np.random.default_rng(2)
    fps = 30
    seg = [(0.0, 1.2), (0.0, 50.0, 1.0), (50.0, 1.2), (50.0, 150.0, 1.5), (150.0, 1.2)]
    xs, ts, t = [], [], 0.0
    for s in seg:
        if len(s) == 2:
            n = int(s[1] * fps)
            xs += [s[0]] * n
        else:
            n = int(s[2] * fps)
            xs += list(np.linspace(s[0], s[1], n, endpoint=False))
        ts += list(t + np.arange(n) / fps)
        t += n / fps
    xs, ts = np.array(xs), np.array(ts)
    T = np.tile(np.eye(4), (len(xs), 1, 1))
    T[:, 0, 3] = xs + rng.normal(0, 0.3, len(xs))
    T[:, 1, 3] = rng.normal(0, 0.3, len(xs))
    T[::11] = np.nan   # occasional dropout
    stops = detect_stops(ts, T, speed_thresh_mm_s=8.0, min_dwell_s=0.6)
    assert len(stops) == 3
    d = stop_distances(stops)
    assert np.allclose(d, [50, 100], atol=1.5)


def test_mm_per_px_from_ruler():
    assert abs(mm_per_px_from_ruler((10, 10), (10, 60), 10.0) - 0.2) < 1e-12


def test_recording_round_trip_and_pairing(tmp_path):
    w = RecordingWriter(tmp_path / "take", (8, 8), compress=False)
    for i in range(10):
        w.add_frame(i * 0.1, np.full((8, 8), i, np.uint8))
    for j in range(20):
        t = j * 0.05
        T = np.eye(4)
        T[0, 3] = j
        w.add_pose(t, None if j in (7, 8) else T, 0 if j in (7, 8) else 2)
    folder = w.close({"note": "test"})
    rec = load_recording(folder)
    assert rec.n_frames == 10 and len(rec.pose_t) == 20 and rec.meta["n_tracked"] == 18
    assert rec.frames[3, 0, 0] == 3
    P = pair_poses_to_frames(rec.frame_t, rec.pose_t, rec.T, lag_s=0.0)
    assert np.allclose(P[:, 0, 3][[0, 1, 2, 3]], [0, 2, 4, 6])
    assert P[4, 0, 3] == 9                 # frame 4 at t=0.4: poses 7 and 8 missing, pose 9 (0.45 s) is within one interval
    assert np.isnan(pair_poses_to_frames(rec.frame_t, rec.pose_t, rec.T, tol_s=0.02)[4, 0, 0])
    P2 = pair_poses_to_frames(rec.frame_t, rec.pose_t, rec.T, lag_s=0.05)
    assert P2[1, 0, 3] == 1                # frame at 0.1 s shows the probe at 0.05 s
    scan, fused = recording_to_scan(rec, make_calib(0.2, np.eye(4)))
    assert scan.n_frames == 10 and np.isfinite(fused.T).all()
    assert (fused.source == PRIMARY).sum() >= 8
