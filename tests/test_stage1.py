"""Tests for the Stage 1 modules: ray confidence, named regions, hybrid tracker."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uscov.confidence import RayConfidence, FanGeometry  # noqa: E402
from uscov.roi import thyroid_template, report_by_part, worst_parts  # noqa: E402
from uscov.coverage import GridSpec, CoverageMap  # noqa: E402


def _fan_mask(h=240, w=320, apex=(-40.0, 160.0), r0=70.0, r1=270.0, half_angle=0.8):
    rr, cc = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    d = np.hypot(rr - apex[0], cc - apex[1])
    th = np.arctan2(cc - apex[1], rr - apex[0])
    return (d >= r0) & (d <= r1) & (np.abs(th) <= half_angle)


def test_fan_geometry_recovers_apex():
    m = _fan_mask()
    g = FanGeometry.from_mask(m)
    assert not g.linear
    assert abs(g.apex[0] - (-40.0)) < 6 and abs(g.apex[1] - 160.0) < 3
    assert abs(g.r_min - 70) < 3 and abs(g.r_max - 270) < 3


def test_shadow_scores_low_but_cyst_scores_high():
    m = _fan_mask()
    rng = np.random.default_rng(0)
    frame = np.where(m, 80 + rng.normal(0, 8, m.shape), 0).clip(0, 255).astype(np.uint8)
    g = FanGeometry.from_mask(m)
    rr, cc = np.meshgrid(np.arange(m.shape[0]), np.arange(m.shape[1]), indexing="ij")
    d = np.hypot(rr - g.apex[0], cc - g.apex[1])
    th = np.arctan2(cc - g.apex[1], rr - g.apex[0])
    # bone-like shadow: a wedge of rays dark from depth 150 px to the bottom (only noise floor)
    shadow = m & (th > 0.3) & (th < 0.5) & (d > 150)
    frame[shadow] = rng.normal(8, 4, shadow.sum()).clip(0, 30).astype(np.uint8)
    # cyst-like anechoic blob with normal tissue beyond it
    cyst = m & (th > -0.5) & (th < -0.3) & (d > 120) & (d < 160)
    frame[cyst] = 0
    rc = RayConfidence(m)
    conf = rc.full(frame)
    sh = conf[m & (th > 0.35) & (th < 0.45) & (d > 200) & (d < 260)]
    cy = conf[m & (th > -0.45) & (th < -0.35) & (d > 130) & (d < 150)]
    tissue = conf[m & (np.abs(th) < 0.1) & (d > 130) & (d < 150)]
    assert sh.mean() < 0.25, f"shadow conf {sh.mean():.2f}"
    assert cy.mean() > 0.7, f"cyst conf {cy.mean():.2f}"
    assert tissue.mean() > 0.8
    assert conf[~m].max() == 0.0


def test_hybrid_tracker_bridges_gaps_and_tags_frames():
    from uscov.tracker import fuse, simulate_dropouts, relative_from_absolute, PRIMARY, BRIDGED, UNKNOWN
    from uscov.noise import corrupt_poses, NoiseSpec
    N = 300
    T_gt = np.tile(np.eye(4), (N, 1, 1))
    T_gt[:, 2, 3] = np.arange(N) * 0.5          # straight sweep, 0.5 mm per frame
    T_gt[:, 0, 3] = 3.0 * np.sin(np.arange(N) / 40.0)
    vis = simulate_dropouts(N, n_gaps=3, gap_len=20, seed=1)
    primary = [T_gt[i] if vis[i] else None for i in range(N)]
    # image-based relative motion with a little drift
    rel = relative_from_absolute(corrupt_poses(T_gt, NoiseSpec("s", bias_frac_of_step=0.05), seed=2))
    fused = fuse(primary, rel, smooth_window=1)
    assert not np.any(np.isnan(fused.T))
    assert (fused.source == PRIMARY).sum() == vis.sum()
    assert (fused.source == BRIDGED).sum() == (~vis).sum()
    assert fused.gap_len.max() == 20
    err = np.linalg.norm(fused.T[:, :3, 3] - T_gt[:, :3, 3], axis=1)
    assert err[vis].max() < 1e-9                    # anchored frames are exact
    assert err[~vis].max() < 2.0                    # bridged frames drift only slightly over 20 frames
    w = fused.confidence_multiplier(max_bridge=40, floor=0.3)
    assert w[vis].min() == 1.0 and 0.3 <= w[~vis].min() < 1.0

    # no relative stream: constant-velocity bridging still fills the gap
    fused2 = fuse(primary, None, smooth_window=1)
    assert not np.any(np.isnan(fused2.T))
    # gap longer than max_bridge leaves frames unknown
    fused3 = fuse(primary, rel, smooth_window=1, max_bridge=5)
    assert (fused3.source == UNKNOWN).sum() == 3 * 15


def test_thyroid_template_parts_and_report():
    t = thyroid_template()
    assert len(t.parts) == 5
    g = GridSpec(origin=np.array([-40.0, -40.0, -20.0]), voxel_mm=2.0, shape=(40, 40, 20))
    lab = t.label_grid(g)
    assert set(np.unique(lab)) == {0, 1, 2, 3, 4, 5}
    cov = CoverageMap.empty(g)
    # pretend only the right lobe was imaged
    right = (lab == 1) | (lab == 2)
    cov.conf_max[right] = 0.9
    cov.hits[right] = 5
    rep = report_by_part(cov, lab, t.part_names())
    by = {r.name: r for r in rep}
    assert by["right lobe, upper pole"].completeness > 0.99
    assert by["left lobe, lower pole"].completeness == 0.0
    assert worst_parts(rep, 1)[0].name.startswith("left lobe") or worst_parts(rep, 1)[0].name == "isthmus"

    f = t.fit_to_extent(np.array([0.0, 0.0, 0.0]), np.array([58.0, 49.0, 15.0]))
    lo, hi = f.bounds()
    assert np.allclose(lo, 0.0, atol=1e-6) and np.allclose(hi, [58.0, 49.0, 15.0], atol=1e-6)
