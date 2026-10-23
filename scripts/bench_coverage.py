"""Coverage maps and completeness scores from bench-day recordings (phone camera + capture card).

  python scripts/bench_coverage.py data/bench_2026-10-22/us/full_take2_01 \
      --takes data/bench_2026-10-22/us/partial_take2_01 data/bench_2026-10-22/us/blocked_take2_01 \
      --face-mm 60 --out outputs/bench_2026-10-22

The first take is the reference sweep: its coverage defines the target region (roi_from_reference). Every other
take is scored against it (completeness, truthfulness), like the simulation pipeline in run_coverage.py.

Image -> cube transform without a pinhead calibration (the 2026-10-22 session skipped it):
  * lateral image axis = the cube axis the probe rocked about during the reference sweep (a fan sweep rotates the
    probe about its long axis, which is the lateral axis of the image), or --lateral x|y to force it;
  * depth axis = cube -z (the marker face with id 4 pointed up on that day);
  * the probe face centre sits --face-mm below the cube centre, under the fan apex column of the screen.
Treat the resulting maps as approximate: left/right mirror and the face distance are not identifiable from the
data, and a pinhead calibration replaces all of this (calibrate_pinhead.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.bench import load_recording, recording_to_scan, make_calib, save_calib_json  # noqa: E402
from uscov.coverage import CoverageAccumulator, grid_for_scan  # noqa: E402
from uscov.data import Scan  # noqa: E402
from uscov.score import roi_from_reference, completeness, truthfulness  # noqa: E402
from uscov.tracker import PRIMARY, BRIDGED, UNKNOWN  # noqa: E402
from uscov.viz import plot_projections  # noqa: E402
from scipy.spatial.transform import Rotation as R  # noqa: E402


def dominant_rotation_axis(T: np.ndarray, min_deg: float = 0.5) -> tuple[np.ndarray, float]:
    """Unit axis (cube frame) the cube rotated about most, from consecutive tracked poses, and that axis's share
    of the total rotation (1.0 = pure rotation about one axis)."""
    ok = ~np.isnan(T[:, 0, 0])
    idx = np.where(ok)[0]
    rv = []
    for a, b in zip(idx[:-1], idx[1:]):
        if b - a > 3:
            continue
        Rrel = T[a, :3, :3].T @ T[b, :3, :3]
        v = R.from_matrix(Rrel).as_rotvec()
        if np.degrees(np.linalg.norm(v)) >= min_deg:
            rv.append(v)
    rv = np.array(rv)
    if len(rv) < 5:
        return np.array([1.0, 0, 0]), 0.0
    w, V = np.linalg.eigh(rv.T @ rv)
    return V[:, -1], float(w[-1] / w.sum())


def image_to_tool_from_axes(lateral: np.ndarray, face_mm: float, apex_mm: float, depth0_mm: float) -> np.ndarray:
    """4x4 image(mm) -> cube: image x along `lateral`, image y (depth) along cube -z, origin so that the fan apex
    (column apex_mm, row depth0_mm) lands face_mm below the cube centre."""
    ez = np.array([0.0, 0.0, 1.0])
    lat = lateral - lateral.dot(ez) * ez
    lat /= np.linalg.norm(lat)
    down = -ez
    normal = np.cross(lat, down)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2] = lat, down, normal
    M[:3, 3] = -apex_mm * lat - depth0_mm * down - face_mm * ez
    return M


def scan_from_recording(rec, calib, smooth: int, max_bridge: int):
    """Like recording_to_scan, but gaps longer than max_bridge frames stay unknown instead of being
    extrapolated: with the 2026-10-22 tracking rates (23-54 %), unlimited constant-velocity bridging invents
    most of the sweep."""
    from uscov.bench import pair_poses_to_frames
    from uscov.tracker import fuse
    primary = pair_poses_to_frames(rec.frame_t, rec.pose_t, rec.T, float(rec.meta.get("lag_s", 0.0)))
    fused = fuse(primary, None, smooth_window=smooth, max_bridge=max_bridge)
    frames = rec.frames if isinstance(rec.frames, np.ndarray) else rec.frames[...]
    scan = Scan(rec.folder.name, frames, fused.T, calib)
    ok = ~np.isnan(fused.T[:, 0, 0])
    stats = dict(frames=int(len(fused.T)), primary=int((fused.source == PRIMARY).sum()),
                 bridged=int((fused.source == BRIDGED).sum()), unknown=int((fused.source == UNKNOWN).sum()))
    return Scan(scan.name, scan.frames[ok], fused.T[ok], calib), stats


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reference", help="take folder of the reference (full) sweep")
    ap.add_argument("--takes", nargs="*", default=[], help="take folders to score against the reference")
    ap.add_argument("--face-mm", type=float, default=60.0, help="cube centre to probe face, mm (hand-measured)")
    ap.add_argument("--lateral", default="auto", choices=["auto", "x", "y"], help="cube axis = image lateral axis")
    ap.add_argument("--apex-col", type=float, default=None, help="fan apex column in the cropped full-res frame (px)")
    ap.add_argument("--voxel", type=float, default=3.0)
    ap.add_argument("--pixel-step", type=int, default=4)
    ap.add_argument("--frame-step", type=int, default=1)
    ap.add_argument("--smooth", type=int, default=9)
    ap.add_argument("--max-bridge", type=int, default=10, help="longest dropout (frames) to bridge; longer gaps are dropped")
    ap.add_argument("--out", default="outputs/bench_coverage")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ref_rec = load_recording(a.reference)
    meta = ref_rec.meta
    mm_px = float(meta["mm_per_px"])
    ds = int(meta.get("downsample", 1))
    screen_path = meta.get("screen_json")
    screen = json.load(open(screen_path)) if screen_path and Path(screen_path).exists() else {}
    r0, r1, c0, c1 = meta["crop"]
    apex_col = a.apex_col if a.apex_col is not None else (c1 - c0) / 2.0
    apex_mm = apex_col / ds * mm_px
    depth0_mm = float(screen.get("depth_zero_row_in_crop", 0)) / ds * mm_px

    if a.lateral == "auto":
        axis, share = dominant_rotation_axis(ref_rec.T)
        k = int(np.argmax(np.abs(axis[:2])))
        lateral = np.zeros(3)
        lateral[k] = 1.0
        print(f"dominant rotation axis in cube frame {np.round(axis, 2)} ({share:.0%} of rotation) "
              f"-> lateral = cube {'xy'[k]}")
    else:
        lateral = np.array([1.0, 0, 0]) if a.lateral == "x" else np.array([0, 1.0, 0])
    i2t = image_to_tool_from_axes(lateral, a.face_mm, apex_mm, depth0_mm)
    calib = make_calib(mm_px, i2t)
    save_calib_json(out / "calib_estimated.json", calib, face_mm=a.face_mm, lateral=lateral.tolist(),
                    apex_mm=apex_mm, depth0_mm=depth0_mm, note="estimated, not pinhead-calibrated")

    ref_scan, st = scan_from_recording(ref_rec, calib, a.smooth, a.max_bridge)
    print(f"reference {ref_scan.name}: {st['frames']} frames, tracked {st['primary']}, bridged {st['bridged']}, "
          f"unknown {st['unknown']} -> {ref_scan.n_frames} usable")
    cand = []
    for t in a.takes:
        rec = load_recording(t)
        sc, s2 = scan_from_recording(rec, calib, a.smooth, a.max_bridge)
        print(f"take {sc.name}: {s2['frames']} frames, tracked {s2['primary']}, bridged {s2['bridged']}, "
              f"unknown {s2['unknown']} -> {sc.n_frames} usable")
        cand.append((sc, s2))

    grid = grid_for_scan(ref_scan, voxel_mm=a.voxel, extra_T=[sc.frame_to_world() for sc, _ in cand])
    print(f"grid {grid.shape} = {grid.n_voxels / 1e6:.2f} M voxels at {a.voxel} mm")
    ref_cov = CoverageAccumulator(ref_scan, grid, pixel_step=a.pixel_step).run(frame_step=a.frame_step)
    roi = roi_from_reference(ref_cov)
    full = completeness(ref_cov, roi)
    print(f"reference ROI {full.n_roi} voxels = {full.n_roi * a.voxel ** 3 / 1000:.0f} cm^3, "
          f"mean conf {full.mean_conf:.2f}")
    plot_projections(ref_cov, out / f"{ref_scan.name}_reference.png", f"{ref_scan.name} reference", roi)

    rows = [dict(take=ref_scan.name, role="reference", completeness=1.0, mean_conf=full.mean_conf, **st)]
    for sc, s2 in cand:
        cov = CoverageAccumulator(sc, grid, pixel_step=a.pixel_step).run(frame_step=a.frame_step)
        c = completeness(cov, roi)
        tr = truthfulness(cov, ref_cov)
        print(f"{sc.name:22s} completeness {c.completeness:.3f}  mean conf {c.mean_conf:.2f}  "
              f"false coverage {tr.false_coverage:.2f} false gap {tr.false_gap:.2f} dice {tr.dice:.2f}")
        plot_projections(cov, out / f"{sc.name}_vs_reference.png", f"{sc.name} vs reference", roi)
        rows.append(dict(take=sc.name, role="candidate", completeness=c.completeness, mean_conf=c.mean_conf,
                         false_coverage=tr.false_coverage, false_gap=tr.false_gap, dice=tr.dice, **s2))
    json.dump(dict(reference=ref_scan.name, voxel_mm=a.voxel, face_mm=a.face_mm, lateral=lateral.tolist(),
                   roi_voxels=full.n_roi, rows=rows), open(out / "summary.json", "w"), indent=2)
    print("wrote", out / "summary.json")


if __name__ == "__main__":
    main()
