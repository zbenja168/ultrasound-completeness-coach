"""End-to-end Stage 1 software demo on a recorded sweep replayed as if live.

Pipeline per frame: replay frame -> simulated marker pose (jitter, smoothed) with camera dropouts ->
hybrid fusion with image-based relative motion -> ray-confidence coverage -> named-region completeness
-> cue. Writes a GIF with the coverage projection, the named-part bars and the cue text.

Usage: python scripts/live_demo.py data/extracted/tusrec2024_val --scan 052__LH_Per_L_DtP --out outputs/live_demo
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.data import index_dataset, frame_centres_world  # noqa: E402
from uscov.coverage import CoverageAccumulator, grid_for_scan  # noqa: E402
from uscov.score import roi_from_reference, completeness, thin_regions  # noqa: E402
from uscov.noise import PRESETS, corrupt_poses  # noqa: E402
from uscov.tracker import fuse, simulate_dropouts, relative_from_absolute, BRIDGED  # noqa: E402
from uscov.roi import sweep_thirds_template, extent_of_roi, report_by_part, worst_parts  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir")
    ap.add_argument("--scan", default="052__LH_Per_L_DtP")
    ap.add_argument("--voxel", type=float, default=2.0)
    ap.add_argument("--pixel-step", type=int, default=4)
    ap.add_argument("--gap-len", type=int, default=40)
    ap.add_argument("--n-gaps", type=int, default=3)
    ap.add_argument("--stop-at", type=float, default=0.8, help="fraction of the sweep the 'operator' completes")
    ap.add_argument("--out", default="outputs/live_demo")
    a = ap.parse_args()

    ds = index_dataset(a.dataset_dir)
    scan = ds.load(a.scan)
    N = scan.n_frames
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    # reference map from true poses (what a complete, well-tracked scan images) -> ROI and its named parts
    grid = grid_for_scan(scan, voxel_mm=a.voxel, pad_mm=12.0)
    ref = CoverageAccumulator(scan, grid, pixel_step=a.pixel_step).run()
    roi = roi_from_reference(ref)
    lo, hi = extent_of_roi(roi, grid)
    centres = frame_centres_world(scan.frame_to_world(), *scan.shape)
    sweep_axis = int(np.argmax(np.abs(centres[-1] - centres[0])))
    depth_dir = np.abs(scan.frame_to_world()[:, :3, 1].mean(axis=0))  # image y axis in world = depth
    depth_axis = int(np.argmax(depth_dir)) if int(np.argmax(depth_dir)) != sweep_axis else int(np.argsort(depth_dir)[-2])
    direction = float(np.sign(centres[-1][sweep_axis] - centres[0][sweep_axis]))
    template = sweep_thirds_template(lo, hi, sweep_axis, depth_axis, sweep_direction=direction)
    labels = template.label_grid(grid) * roi  # named parts restricted to the imaged region
    names = template.part_names()

    # 'live' pose stream: marker tracker with dropouts, bridged by image-based motion
    marker = corrupt_poses(scan.tforms, PRESETS["aruco_phone"], seed=0)
    vis = simulate_dropouts(N, a.n_gaps, a.gap_len, seed=0)
    primary = [marker[i] if vis[i] else None for i in range(N)]
    rel = relative_from_absolute(corrupt_poses(scan.tforms, PRESETS["sensorless"], seed=1))
    fused = fuse(primary, rel, smooth_window=9)
    T_live = scan.frame_to_world(fused.T)
    w = fused.confidence_multiplier()

    acc = CoverageAccumulator(scan, grid, T_frame_to_world=T_live, pixel_step=a.pixel_step)
    n_stop = int(N * a.stop_at)
    snaps = []
    for i in range(n_stop):
        acc.add_frame(i)
        if i % 8 == 0 or i == n_stop - 1:
            comp = completeness(acc.map, roi).completeness
            rep = report_by_part(acc.map, labels, names)
            worst = worst_parts(rep, 1)[0]
            cue = f"next: {worst.name} ({worst.completeness:.0%})" if worst.completeness < 0.9 else "coverage complete"
            src = "marker" if fused.source[i] != BRIDGED else f"bridged ({fused.gap_len[i]} frames)"
            snaps.append((i, acc.map.volume("conf_max").max(axis=2).T.copy(), comp,
                          [r.completeness for r in rep], cue, src))

    final_rep = report_by_part(acc.map, labels, names)
    print(f"scan {scan.name}: stopped at {a.stop_at:.0%}, completeness {completeness(acc.map, roi).completeness:.3f}")
    for r in final_rep:
        print(f"   {r.name:28s} {r.completeness:6.1%}  ({r.n_voxels * a.voxel**3 / 1000:.0f} cm3)")
    gaps = thin_regions(acc.map, roi, centres)
    if gaps:
        g = gaps[0]
        print(f"   largest thin region {g.size_voxels * a.voxel**3 / 1000:.0f} cm3 near frame {g.nearest_frame}")
    print(f"   frames bridged: {(fused.source == BRIDGED).sum()} of {N}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [1.4, 1]})
    im = ax1.imshow(snaps[0][1], origin="lower", cmap="viridis", vmin=0, vmax=1, aspect="equal")
    ax1.contour(roi.reshape(grid.shape).max(axis=2).T, levels=[0.5], colors="w", linewidths=0.6)
    ax1.set_title(""); ax1.set_xticks([]); ax1.set_yticks([])
    bars = ax2.barh(range(len(names)), snaps[0][3], color="tab:green")
    ax2.set_yticks(range(len(names))); ax2.set_yticklabels(names, fontsize=8); ax2.set_xlim(0, 1)
    ax2.invert_yaxis(); ax2.set_xlabel("completeness")
    cue_txt = ax2.set_title("")

    def update(k):
        i, img, comp, parts, cue, src = snaps[k]
        im.set_data(img)
        ax1.set_title(f"frame {i}/{N}  completeness {comp:.2f}  pose: {src}", fontsize=10)
        for b, v in zip(bars, parts):
            b.set_width(v); b.set_color("tab:green" if v >= 0.9 else ("tab:orange" if v >= 0.5 else "tab:red"))
        cue_txt.set_text(cue)
        return [im, *bars, cue_txt]

    anim = FuncAnimation(fig, update, frames=len(snaps), blit=False)
    anim.save(out / f"{scan.name}_live_demo.gif", writer=PillowWriter(fps=8))
    fig.savefig(out / f"{scan.name}_live_demo_final.png", dpi=110)
    print("wrote", out / f"{scan.name}_live_demo.gif")


if __name__ == "__main__":
    main()
