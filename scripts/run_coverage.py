"""Build the coverage map for one scan from tracked poses, score a partial sweep, list thin regions, animate.

Usage:
  python scripts/run_coverage.py data/extracted/tusrec2025_val --scan 0 --voxel 2 --out outputs/coverage
"""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.data import index_dataset, frame_centres_world  # noqa: E402
from uscov.coverage import CoverageAccumulator, grid_for_scan  # noqa: E402
from uscov.score import roi_from_reference, completeness, thin_regions  # noqa: E402
from uscov.viz import plot_projections, animate_fill  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--scan", default="0")
    ap.add_argument("--voxel", type=float, default=2.0)
    ap.add_argument("--pixel-step", type=int, default=4)
    ap.add_argument("--frame-step", type=int, default=1)
    ap.add_argument("--partial", type=float, default=0.6, help="fraction of the sweep to score as a partial scan")
    ap.add_argument("--out", default="outputs/coverage")
    ap.add_argument("--gif", action="store_true")
    ap.add_argument("--conf", default="ray", choices=["ray", "brightness"], help="confidence model")
    a = ap.parse_args()

    ds = index_dataset(a.dataset_dir)
    scan = ds.load(int(a.scan) if a.scan.isdigit() else a.scan)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    print(f"scan {scan.name}: {scan.n_frames} frames, grid voxel {a.voxel} mm")

    grid = grid_for_scan(scan, voxel_mm=a.voxel)
    print(f"grid shape {grid.shape} = {grid.n_voxels/1e6:.2f} M voxels")

    ref = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step, conf_model=a.conf).run(frame_step=a.frame_step)
    roi = roi_from_reference(ref)
    full = completeness(ref, roi)
    print(f"reference ROI: {full.n_roi} voxels ({full.n_roi * a.voxel**3 / 1000:.1f} cm^3), "
          f"mean conf {full.mean_conf:.2f}")
    div = ref.angular_diversity()[roi]
    print(f"angular diversity in ROI: mean {div.mean():.3f}, 90th pct {np.percentile(div, 90):.3f}")
    plot_projections(ref, out / f"{scan.name}_reference.png", f"{scan.name} reference (tracked)", roi)

    n_part = int(scan.n_frames * a.partial)
    part = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step, conf_model=a.conf).add_frames(
        range(0, n_part, a.frame_step))
    pc = completeness(part, roi)
    print(f"partial sweep (first {a.partial:.0%} of frames): completeness {pc.completeness:.3f}, "
          f"mean conf {pc.mean_conf:.2f}")
    centres = frame_centres_world(scan.frame_to_world(), *scan.shape)
    for k, g in enumerate(thin_regions(part, roi, centres)):
        print(f"  thin region {k+1}: {g.size_voxels} voxels ({g.size_voxels * a.voxel**3 / 1000:.1f} cm^3) "
              f"at {np.round(g.centre_mm, 1)} mm, nearest tracked frame {g.nearest_frame}, mean conf {g.mean_conf:.2f}")
    plot_projections(part, out / f"{scan.name}_partial.png", f"{scan.name} partial {a.partial:.0%}", roi)

    if a.gif:
        acc = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step, conf_model=a.conf)
        animate_fill(acc, out / f"{scan.name}_fill.gif", roi=roi, frame_step=max(1, a.frame_step * 3))
        print("wrote", out / f"{scan.name}_fill.gif")


if __name__ == "__main__":
    main()
