"""Hybrid tracker evaluation on real sweeps with simulated camera dropouts.

Primary = marker-style poses (jitter, smoothed) with dropouts of a given length; bridge = sensorless-style
relative motion. Compares fused poses against truth and the resulting coverage map against the reference.

Usage: python scripts/hybrid_sweep.py data/extracted/tusrec2024_val --max-scans 4 --gap-lens 10,40,100 --out outputs/hybrid
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.data import index_dataset  # noqa: E402
from uscov.coverage import CoverageAccumulator, grid_for_scan  # noqa: E402
from uscov.score import roi_from_reference, completeness, truthfulness  # noqa: E402
from uscov.noise import PRESETS, corrupt_poses, trajectory_error  # noqa: E402
from uscov.tracker import fuse, simulate_dropouts, relative_from_absolute, BRIDGED  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--max-scans", type=int, default=4)
    ap.add_argument("--gap-lens", default="10,40,100")
    ap.add_argument("--n-gaps", type=int, default=3)
    ap.add_argument("--voxel", type=float, default=2.0)
    ap.add_argument("--pixel-step", type=int, default=4)
    ap.add_argument("--out", default="outputs/hybrid")
    a = ap.parse_args()
    ds = index_dataset(a.dataset_dir)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows = []
    for si in range(min(a.max_scans, len(ds))):
        scan = ds.load(si)
        h, w = scan.shape
        N = scan.n_frames
        T_gt = scan.frame_to_world()
        centre = np.array([(w + 1) / 2, (h + 1) / 2, 0.0, 1.0])
        marker = corrupt_poses(scan.tforms, PRESETS["aruco_phone"], seed=si)
        sensorless = corrupt_poses(scan.tforms, PRESETS["sensorless"], seed=si + 100)
        rel = relative_from_absolute(sensorless)
        grid = grid_for_scan(scan, voxel_mm=a.voxel, extra_T=[scan.frame_to_world(marker)])
        ref = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step).run()
        roi = roi_from_reference(ref)
        print(f"[{scan.name}] {N} frames")
        for gl in [int(x) for x in a.gap_lens.split(",")]:
            vis = simulate_dropouts(N, a.n_gaps, gl, seed=si)
            primary = [marker[i] if vis[i] else None for i in range(N)]
            variants = {
                "drop_frames": None,                      # just skip frames without a primary pose
                "bridge_sensorless": fuse(primary, rel, smooth_window=9),
                "bridge_const_vel": fuse(primary, None, smooth_window=9),
            }
            for name, fused in variants.items():
                if fused is None:
                    keep = np.where(vis)[0]
                    Tn = scan.frame_to_world(fuse(primary, None, smooth_window=9).T)
                    cand = CoverageAccumulator(scan, grid, T_frame_to_world=Tn, pixel_step=a.pixel_step).add_frames(keep)
                    te = trajectory_error(T_gt[keep], Tn[keep], centre)
                else:
                    Tn = scan.frame_to_world(fused.T)
                    cand = CoverageAccumulator(scan, grid, T_frame_to_world=Tn, pixel_step=a.pixel_step).run()
                    te = trajectory_error(T_gt, Tn, centre)
                    b = fused.source == BRIDGED
                    err_b = np.linalg.norm((T_gt[b] @ centre)[:, :3] - (Tn[b] @ centre)[:, :3], axis=1) if b.any() else np.zeros(1)
                cc = completeness(cand, roi); tr = truthfulness(cand, ref)
                row = dict(scan=scan.name, gap_len=gl, variant=name, mean_err_mm=te.mean_err_mm,
                           bridged_err_mm=float(err_b.mean()) if fused is not None else float("nan"),
                           completeness=cc.completeness, false_coverage=tr.false_coverage,
                           false_gap=tr.false_gap, dice=tr.dice)
                rows.append(row)
                print(f"   gap {gl:3d}  {name:18s} mean err {te.mean_err_mm:5.2f} mm  "
                      f"bridged err {row['bridged_err_mm']:5.2f} mm  completeness {cc.completeness:.3f}  "
                      f"false-cov {tr.false_coverage:.3f}  false-gap {tr.false_gap:.3f}  dice {tr.dice:.3f}", flush=True)
    with open(out / "hybrid_sweep.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    print("wrote", out / "hybrid_sweep.csv")


if __name__ == "__main__":
    main()
