"""Coverage-map faithfulness with real DualTrack poses (replaces the simulated 'sensorless' row of Stage 0).

Reads outputs/dualtrack_*/<scan>.npz produced by run_dualtrack.py, builds the coverage map from the predicted poses,
and compares it with the map from the true poses. Also reports DualTrack used as the hybrid bridge for simulated
camera dropouts (marker poses + DualTrack relative motion), the real version of the hybrid sweep.

Usage: python scripts/dualtrack_coverage.py data/extracted/tusrec2024_val outputs/dualtrack_2024 --out outputs/dualtrack_cov_2024
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
from uscov.tracker import fuse, simulate_dropouts, relative_from_absolute  # noqa: E402


def protocol(name):
    parts = name.split("__")[-1].split("_")
    return "_".join(parts[1:3]) if len(parts) >= 3 else parts[-1]   # e.g. Par_L, Per_S, rotation


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("pred_dir")
    ap.add_argument("--voxel", type=float, default=2.0)
    ap.add_argument("--pixel-step", type=int, default=4)
    ap.add_argument("--frame-step", type=int, default=1)
    ap.add_argument("--max-scans", type=int, default=0)
    ap.add_argument("--hybrid-gap", type=int, default=100)
    ap.add_argument("--out", default="outputs/dualtrack_cov")
    a = ap.parse_args()
    ds = index_dataset(a.dataset_dir)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    files = sorted(Path(a.pred_dir).glob("*.npz"))
    if a.max_scans:
        files = files[:a.max_scans]
    rows = []
    for f in files:
        name = f.stem
        scan = ds.load(name)
        d = np.load(f)
        pred = d["pred_tforms"]
        h, w = scan.shape
        N = scan.n_frames
        centre = np.array([(w + 1) / 2, (h + 1) / 2, 0.0, 1.0])
        T_gt = scan.frame_to_world()
        T_dt = scan.frame_to_world(pred)
        # hybrid: marker-style primary with dropouts, bridged by DualTrack relative motion
        marker = corrupt_poses(scan.tforms, PRESETS["aruco_phone"], seed=0)
        gap = min(a.hybrid_gap, max(5, (N - 20) // 3 - 1))
        vis = simulate_dropouts(N, 3, gap, seed=0)
        primary = [marker[i] if vis[i] else None for i in range(N)]
        fused = fuse(primary, relative_from_absolute(pred), smooth_window=9)
        T_hy = scan.frame_to_world(fused.T)
        grid = grid_for_scan(scan, voxel_mm=a.voxel, extra_T=[T_dt, T_hy])
        ref = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step).run(frame_step=a.frame_step)
        roi = roi_from_reference(ref)
        for label, T in (("dualtrack_only", T_dt), ("hybrid_marker+dualtrack", T_hy)):
            te = trajectory_error(T_gt, T, centre)
            cand = CoverageAccumulator(scan, grid, T_frame_to_world=T, pixel_step=a.pixel_step).run(frame_step=a.frame_step)
            cc = completeness(cand, roi); tr = truthfulness(cand, ref)
            rows.append(dict(scan=name, protocol=protocol(name), source=label, n_frames=N, path_mm=te.path_length_mm,
                             final_drift_mm=te.final_drift_mm, drift_rate=te.final_drift_rate, mean_err_mm=te.mean_err_mm,
                             completeness=cc.completeness, false_coverage=tr.false_coverage, false_gap=tr.false_gap,
                             dice=tr.dice, hybrid_gap=gap))
            print(f"{name:22s} {label:24s} drift {te.final_drift_mm:6.1f} mm ({te.final_drift_rate*100:4.1f}%) "
                  f"mean {te.mean_err_mm:5.1f} | comp {cc.completeness:.3f} false-cov {tr.false_coverage:.3f} "
                  f"false-gap {tr.false_gap:.3f} dice {tr.dice:.3f}", flush=True)
    with open(out / "dualtrack_coverage.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); wr.writeheader(); wr.writerows(rows)
    print("wrote", out / "dualtrack_coverage.csv")


if __name__ == "__main__":
    main()
