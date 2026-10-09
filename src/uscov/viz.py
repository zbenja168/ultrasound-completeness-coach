"""Plots: trajectories, coverage projections, and a fill-in animation."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .coverage import CoverageMap, CoverageAccumulator
from .data import frame_corners_world, frame_centres_world


def _equal_3d(ax) -> None:
    lims = np.array([ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()])
    ctr = lims.mean(axis=1)
    r = (lims[:, 1] - lims[:, 0]).max() / 2
    ax.set_xlim3d(ctr[0] - r, ctr[0] + r)
    ax.set_ylim3d(ctr[1] - r, ctr[1] + r)
    ax.set_zlim3d(ctr[2] - r, ctr[2] + r)


def plot_trajectories(T_sets: dict[str, np.ndarray], h: int, w: int, out: Path, every: int = 25) -> None:
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    for name, T in T_sets.items():
        c = frame_centres_world(T, h, w)
        line, = ax.plot(c[:, 0], c[:, 1], c[:, 2], label=name, lw=1.5)
        corners = frame_corners_world(T, h, w)
        for i in range(0, T.shape[0], every):
            q = np.vstack([corners[i], corners[i][:1]])
            ax.plot(q[:, 0], q[:, 1], q[:, 2], lw=0.4, alpha=0.5, color=line.get_color())
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)"); ax.set_zlabel("z (mm)")
    ax.legend()
    _equal_3d(ax)
    fig.tight_layout(); fig.savefig(out, dpi=130); plt.close(fig)


def plot_projections(cov: CoverageMap, out: Path, title: str = "", roi: np.ndarray | None = None) -> None:
    """Max-intensity projections of conf_max, log hits and angular diversity along each axis."""
    vols = {"confidence (max)": cov.volume("conf_max"),
            "log(1+hits)": np.log1p(cov.volume("hits")),
            "angular diversity": cov.volume("diversity")}
    fig, axes = plt.subplots(3, 3, figsize=(12, 11))
    for r, (name, v) in enumerate(vols.items()):
        for axis in range(3):
            img = v.max(axis=axis)
            im = axes[r, axis].imshow(img.T, origin="lower", cmap="viridis", aspect="equal")
            if roi is not None and r == 0:
                m = roi.reshape(cov.grid.shape).max(axis=axis)
                axes[r, axis].contour(m.T, levels=[0.5], colors="w", linewidths=0.6)
            axes[r, axis].set_title(f"{name}  (proj axis {axis})", fontsize=9)
            plt.colorbar(im, ax=axes[r, axis], fraction=0.046)
    fig.suptitle(title); fig.tight_layout(); fig.savefig(out, dpi=120); plt.close(fig)


def plot_sample_frames(frames: np.ndarray, conf_imgs: list[np.ndarray], idx: list[int], out: Path) -> None:
    fig, axes = plt.subplots(2, len(idx), figsize=(3.2 * len(idx), 6))
    for k, i in enumerate(idx):
        axes[0, k].imshow(frames[i], cmap="gray"); axes[0, k].set_title(f"frame {i}"); axes[0, k].axis("off")
        axes[1, k].imshow(conf_imgs[k], cmap="magma", vmin=0, vmax=1)
        axes[1, k].set_title("confidence"); axes[1, k].axis("off")
    fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)


def animate_fill(acc: CoverageAccumulator, out: Path, roi: np.ndarray | None = None,
                 frame_step: int = 5, snap_every: int = 25, proj_axis: int = 2, fps: int = 8) -> None:
    """Replay the sweep and save a GIF of the coverage projection filling in, with completeness in the title."""
    from matplotlib.animation import FuncAnimation, PillowWriter
    from .score import completeness

    n = acc.scan.n_frames
    snaps: list[tuple[int, np.ndarray, float]] = []
    k = 0
    for i in range(0, n, frame_step):
        acc.add_frame(i)
        if k % max(1, snap_every // frame_step) == 0 or i + frame_step >= n:
            comp = completeness(acc.map, roi).completeness if roi is not None else float("nan")
            snaps.append((i, acc.map.volume("conf_max").max(axis=proj_axis).T.copy(), comp))
        k += 1

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(snaps[0][1], origin="lower", cmap="viridis", vmin=0, vmax=1, aspect="equal")
    if roi is not None:
        ax.contour(roi.reshape(acc.grid.shape).max(axis=proj_axis).T, levels=[0.5], colors="w", linewidths=0.6)
    ttl = ax.set_title("")

    def update(j):
        i, img, comp = snaps[j]
        im.set_data(img)
        ttl.set_text(f"frame {i}/{n}   completeness {comp:.2f}")
        return im, ttl

    anim = FuncAnimation(fig, update, frames=len(snaps), blit=False)
    anim.save(out, writer=PillowWriter(fps=fps))
    plt.close(fig)
