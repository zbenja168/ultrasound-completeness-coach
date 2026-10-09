"""Unit tests on a synthetic sweep with known geometry (no dataset needed)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uscov.data import Calib, Scan, pixel_grid, frame_centres_world  # noqa: E402
from uscov.coverage import GridSpec, CoverageAccumulator, ConfidenceParams, grid_for_scan  # noqa: E402
from uscov.score import roi_from_reference, completeness, truthfulness, thin_regions  # noqa: E402
from uscov.noise import PRESETS, corrupt_poses, trajectory_error, NoiseSpec  # noqa: E402


def synthetic_scan(n=60, h=64, w=80, mm_per_px=0.5, step_mm=1.0, dark_band=None) -> Scan:
    """Bright frames translated along +z (elevational) by step_mm each frame. Optional dark band (shadow)."""
    frames = np.full((n, h, w), 120, dtype=np.uint8)
    if dark_band is not None:
        r0, r1 = dark_band
        frames[:, r0:r1, :] = 0
    tforms = np.tile(np.eye(4), (n, 1, 1))
    tforms[:, 2, 3] = np.arange(n) * step_mm
    calib = Calib(scale=np.diag([mm_per_px, mm_per_px, 1.0, 1.0]), image_to_tool=np.eye(4))
    return Scan("synthetic", frames, tforms, calib)


def test_pixel_grid_world_mapping():
    scan = synthetic_scan()
    T = scan.frame_to_world()
    P, rr, cc = pixel_grid(*scan.shape, step=1)
    X = (T[10] @ P)[:3].T
    # pixel (col=1,row=1) -> (0.5,0.5,10) mm; pixel (col=80,row=64) -> (40,32,10)
    assert np.allclose(X[0], [0.5, 0.5, 10.0])
    assert np.allclose(X[-1], [40.0, 32.0, 10.0])


def test_full_sweep_fills_box_and_shadow_is_not_covered():
    scan = synthetic_scan(dark_band=(30, 44))
    grid = grid_for_scan(scan, voxel_mm=2.0, pad_mm=2.0)
    acc = CoverageAccumulator(scan, grid, pixel_step=2)
    cov = acc.run()
    vol = cov.volume("conf_max")
    # a voxel in the bright region, mid-sweep, should be well covered
    bright = grid.to_index(np.array([[20.0, 5.0, 30.0]]))[0][0]
    shadow = grid.to_index(np.array([[20.0, 18.5, 30.0]]))[0][0]  # rows 30-44 -> y 15-22 mm
    assert cov.conf_max[bright] > 0.8
    assert cov.conf_max[shadow] < 0.2
    assert vol.max() <= 1.0


def test_partial_sweep_has_lower_completeness_and_a_thin_region_near_the_end():
    scan = synthetic_scan(n=80)
    grid = grid_for_scan(scan, voxel_mm=2.0, pad_mm=2.0)
    ref = CoverageAccumulator(scan, grid, pixel_step=2).run()
    roi = roi_from_reference(ref)
    part = CoverageAccumulator(scan, grid, pixel_step=2).add_frames(range(0, 50))
    full_c = completeness(ref, roi).completeness
    part_c = completeness(part, roi).completeness
    assert full_c > 0.99
    assert 0.5 < part_c < 0.75
    centres = frame_centres_world(scan.frame_to_world(), *scan.shape)
    gaps = thin_regions(part, roi, centres)
    assert gaps, "expected an unscanned region"
    assert gaps[0].centre_mm[2] > 50.0  # the missing slab is at the far end of the sweep
    assert gaps[0].nearest_frame >= 49


def test_noise_presets_order_and_truthfulness():
    scan = synthetic_scan(n=120, step_mm=1.0)
    T_gt = scan.frame_to_world()
    p = np.array([40.0, 32.0, 0.0, 1.0])
    errs = {}
    for name in ["optical", "aruco_phone", "sensorless", "arkit_free"]:
        Tn = scan.frame_to_world(corrupt_poses(scan.tforms, PRESETS[name], seed=1))
        errs[name] = trajectory_error(T_gt, Tn, p)
    assert errs["optical"].mean_err_mm < 1.0
    assert errs["optical"].mean_err_mm < errs["aruco_phone"].mean_err_mm < errs["arkit_free"].mean_err_mm
    # sensorless bias drift should be in the few-percent range on a straight 120 mm path
    assert 0.01 < errs["sensorless"].final_drift_rate < 0.2

    Tn = scan.frame_to_world(corrupt_poses(scan.tforms, PRESETS["arkit_free"], seed=1))
    grid = grid_for_scan(scan, voxel_mm=2.0, pad_mm=2.0, extra_T=[Tn])
    ref = CoverageAccumulator(scan, grid, pixel_step=2).run()
    cand = CoverageAccumulator(scan, grid, T_frame_to_world=Tn, pixel_step=2).run()
    t = truthfulness(cand, ref)
    assert 0.0 < t.dice < 1.0
    assert t.false_coverage > 0.0


def test_smoothing_reduces_jitter_but_not_drift():
    from uscov.noise import smooth_poses
    scan = synthetic_scan(n=200, step_mm=0.5)
    T_gt = scan.frame_to_world()
    p = np.array([40.0, 32.0, 0.0, 1.0])
    jit = corrupt_poses(scan.tforms, NoiseSpec("jit", jitter_mm=2.5, jitter_deg=1.0), seed=3)
    e_raw = trajectory_error(T_gt, scan.frame_to_world(jit), p)
    e_sm = trajectory_error(T_gt, scan.frame_to_world(smooth_poses(jit, 9)), p)
    assert e_sm.mean_err_mm < 0.5 * e_raw.mean_err_mm
    # smoothing clean poses barely moves them
    e_clean = trajectory_error(T_gt, scan.frame_to_world(smooth_poses(scan.tforms, 9)), p)
    assert e_clean.mean_err_mm < 0.05
    # smooth bias drift is not reduced by averaging
    drift = corrupt_poses(scan.tforms, NoiseSpec("bias", bias_frac_of_step=0.05), seed=3)
    e_d = trajectory_error(T_gt, scan.frame_to_world(drift), p)
    e_ds = trajectory_error(T_gt, scan.frame_to_world(smooth_poses(drift, 9)), p)
    assert abs(e_ds.final_drift_mm - e_d.final_drift_mm) < 0.1 * e_d.final_drift_mm


def test_perfect_noise_is_identity():
    scan = synthetic_scan(n=20)
    Tn = corrupt_poses(scan.tforms, NoiseSpec("none"), seed=0)
    assert np.allclose(Tn, scan.tforms, atol=1e-9)
