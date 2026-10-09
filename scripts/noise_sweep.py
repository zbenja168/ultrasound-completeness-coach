"""How much does tracking error corrupt the coverage map?

For each scan and each noise preset: corrupt the tracked poses, rebuild the map, compare it with the
reference map built from tracked poses. Reports trajectory error, completeness error, false-coverage
and false-gap rates, Dice. Writes a CSV and a summary plot.

Usage:
  python scripts/noise_sweep.py data/extracted/tusrec2025_val --max-scans 6 --seeds 2 --out outputs/noise
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--max-scans", type=int, default=4)
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--presets", default="optical,aruco_phone,sensorless,arkit_free")
    ap.add_argument("--voxel", type=float, default=2.0)
    ap.add_argument("--pixel-step", type=int, default=4)
    ap.add_argument("--frame-step", type=int, default=2)
    ap.add_argument("--out", default="outputs/noise")
    ap.add_argument("--min-hits", default="1,3", help="comma list of min_hits values to evaluate")
    a = ap.parse_args()
    min_hits_list = [int(x) for x in a.min_hits.split(",")]

    ds = index_dataset(a.dataset_dir)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    presets = a.presets.split(",")
    rows = []
    for si in range(min(a.max_scans, len(ds))):
        scan = ds.load(si)
        h, w = scan.shape
        T_gt = scan.frame_to_world()
        centre_px = np.array([(w + 1) / 2, (h + 1) / 2, 0.0, 1.0])
        noisy = {(p, s): scan.frame_to_world(corrupt_poses(scan.tforms, PRESETS[p], seed=s))
                 for p in presets for s in range(a.seeds)}
        grid = grid_for_scan(scan, voxel_mm=a.voxel, extra_T=list(noisy.values()))
        ref = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step).run(frame_step=a.frame_step)
        roi = roi_from_reference(ref)
        ref_c = completeness(ref, roi)
        print(f"[{scan.name}] {scan.n_frames} frames, grid {grid.shape}, ROI {ref_c.n_roi} voxels")
        for (p, s), Tn in noisy.items():
            te = trajectory_error(T_gt, Tn, centre_px)
            cand = CoverageAccumulator(scan, grid, T_frame_to_world=Tn, pixel_step=a.pixel_step).run(
                frame_step=a.frame_step)
            for mh in min_hits_list:
                roi_mh = roi_from_reference(ref, min_hits=mh)
                cc = completeness(cand, roi_mh, min_hits=mh)
                tr = truthfulness(cand, ref, min_hits=mh)
                row = dict(scan=scan.name, preset=p, seed=s, min_hits=mh, n_frames=scan.n_frames,
                           path_mm=te.path_length_mm, final_drift_mm=te.final_drift_mm,
                           drift_rate=te.final_drift_rate, mean_err_mm=te.mean_err_mm,
                           completeness_claimed=cc.completeness, false_coverage=tr.false_coverage,
                           false_gap=tr.false_gap, dice=tr.dice)
                rows.append(row)
                print(f"   {p:12s} seed {s} min_hits {mh}: drift {te.final_drift_mm:6.1f} mm "
                      f"({te.final_drift_rate*100:4.1f}%), mean err {te.mean_err_mm:5.1f} mm | "
                      f"claimed completeness {cc.completeness:.3f} false-cov {tr.false_coverage:.3f} "
                      f"false-gap {tr.false_gap:.3f} dice {tr.dice:.3f}", flush=True)

    csv_path = out / "noise_sweep.csv"
    with open(csv_path, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader(); wr.writerows(rows)
    print("wrote", csv_path)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(min_hits_list), 3, figsize=(13, 4 * len(min_hits_list)), squeeze=False)
    for r_i, mh in enumerate(min_hits_list):
        for ax, key, title in zip(axes[r_i], ["mean_err_mm", "false_coverage", "dice"],
                                  ["mean tracking error (mm)", "false coverage rate", "Dice vs reference map"]):
            data = [[r[key] for r in rows if r["preset"] == p and r["min_hits"] == mh] for p in presets]
            ax.boxplot(data, tick_labels=presets); ax.set_title(f"{title}  (min_hits={mh})")
            ax.tick_params(axis="x", rotation=20)
    fig.tight_layout(); fig.savefig(out / "noise_sweep.png", dpi=120)
    print("wrote", out / "noise_sweep.png")


if __name__ == "__main__":
    main()
