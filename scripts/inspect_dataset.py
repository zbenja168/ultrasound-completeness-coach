"""Extract (if needed) and inspect a TUS-REC zip: list scans, shapes, calibration, sample frames, trajectory.

Usage:
  python scripts/inspect_dataset.py data/raw/tusrec2025_val/Freehand_US_data_val_2025.zip data/extracted/tusrec2025_val
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.data import ensure_extracted, index_dataset, frame_centres_world  # noqa: E402
from uscov.coverage import fan_mask_from_scan, pixel_confidence, ConfidenceParams  # noqa: E402
from uscov.viz import plot_trajectories, plot_sample_frames  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip_or_dir")
    ap.add_argument("out_dir")
    ap.add_argument("--plots", default="outputs/inspect")
    ap.add_argument("--max-scans", type=int, default=3)
    a = ap.parse_args()

    src = Path(a.zip_or_dir)
    root = ensure_extracted(src, a.out_dir) if src.suffix == ".zip" else src
    ds = index_dataset(root)
    print(f"dataset root: {ds.root}")
    print(f"scans: {len(ds)}")
    for n in ds.names():
        print("  ", n)
    print("calib scale (mm/px):", ds.calib.mm_per_pixel)
    print("calib image->tool:\n", np.array2string(ds.calib.image_to_tool, precision=4, suppress_small=True))

    plots = Path(a.plots); plots.mkdir(parents=True, exist_ok=True)
    for i in range(min(a.max_scans, len(ds))):
        scan = ds.load(i)
        T = scan.frame_to_world()
        c = frame_centres_world(T, *scan.shape)
        path = np.linalg.norm(np.diff(c, axis=0), axis=1)
        print(f"\n[{scan.name}] frames {scan.frames.shape} dtype {scan.frames.dtype} "
              f"tforms {scan.tforms.shape}  path {path.sum():.1f} mm  mean step {path.mean():.3f} mm "
              f"max step {path.max():.2f} mm  intensity mean {scan.frames.mean():.1f}")
        fan = fan_mask_from_scan(scan.frames)
        print(f"   fan mask covers {fan.mean()*100:.1f}% of the image")
        idx = [0, scan.n_frames // 3, 2 * scan.n_frames // 3, scan.n_frames - 1]
        conf = [pixel_confidence(scan.frames[j], fan, ConfidenceParams()) for j in idx]
        plot_sample_frames(scan.frames, conf, idx, plots / f"{scan.name}_frames.png")
        plot_trajectories({"tracked": T}, *scan.shape, plots / f"{scan.name}_trajectory.png")
    print(f"\nplots in {plots}")


if __name__ == "__main__":
    main()
