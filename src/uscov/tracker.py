"""Hybrid pose tracker: marker-cube poses as the anchor, image-based relative motion to bridge dropouts.

Inputs per frame i:
  primary[i]   : absolute tool->world pose from the camera/marker tracker, or None/NaN when the cube
                 was not seen (dropout)
  relative[i]  : estimated motion from frame i-1 to frame i in the tool frame (from an image-based
                 estimator such as DualTrack, or from an IMU), may be None when unavailable

Rule:
  - primary visible          -> use it (optionally smoothed)
  - primary missing          -> integrate relative motion from the last fused pose
  - primary returns after a gap -> jump back to it immediately (the anchor wins); the bridged frames
    are kept but tagged, so the coverage engine can down-weight them if the gap was long

The output is a fused [N,4,4] pose array plus a per-frame source tag and the gap length each frame
sits in, which the coverage accumulator can use as a confidence multiplier.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .noise import smooth_poses

PRIMARY, BRIDGED, UNKNOWN = 0, 1, 2


@dataclass
class FusedPoses:
    T: np.ndarray            # [N,4,4]
    source: np.ndarray       # [N] int: PRIMARY / BRIDGED / UNKNOWN
    gap_len: np.ndarray      # [N] int: length of the dropout this frame sits in (0 for primary)

    def confidence_multiplier(self, max_bridge: int = 40, floor: float = 0.3) -> np.ndarray:
        """1.0 for primary frames; linearly falling to `floor` over `max_bridge` bridged frames; 0 for unknown."""
        w = np.ones(len(self.source), np.float32)
        b = self.source == BRIDGED
        w[b] = np.clip(1.0 - (1.0 - floor) * self.gap_len[b] / max_bridge, floor, 1.0)
        w[self.source == UNKNOWN] = 0.0
        return w


def fuse(primary: list[np.ndarray | None] | np.ndarray, relative: list[np.ndarray | None] | np.ndarray | None,
         smooth_window: int = 9, max_bridge: int | None = None) -> FusedPoses:
    """Fuse an absolute pose stream with dropouts and a relative-motion stream.

    `primary` may be an [N,4,4] array with NaN rows for dropouts, or a list with None entries.
    `relative[i]` is T_{i-1 -> i} in the tool frame (relative[0] ignored). If None for a frame
    inside a dropout, the last known motion is reused (constant-velocity assumption).
    """
    N = len(primary)
    prim = np.full((N, 4, 4), np.nan)
    for i in range(N):
        p = primary[i]
        if p is not None and not np.any(np.isnan(p)):
            prim[i] = p
    visible = ~np.isnan(prim[:, 0, 0])

    # smooth the visible primary poses only over runs of visible frames
    if smooth_window > 1:
        i = 0
        while i < N:
            if visible[i]:
                j = i
                while j < N and visible[j]:
                    j += 1
                prim[i:j] = smooth_poses(prim[i:j], smooth_window)
                i = j
            else:
                i += 1

    T = np.full((N, 4, 4), np.nan)
    source = np.full(N, UNKNOWN, np.int32)
    gap_len = np.zeros(N, np.int32)
    last_rel = np.eye(4)
    last_good = None
    run = 0
    for i in range(N):
        if visible[i]:
            T[i] = prim[i]
            source[i] = PRIMARY
            last_good = T[i]
            run = 0
            if relative is not None and i > 0 and relative[i] is not None:
                last_rel = relative[i]
            continue
        run += 1
        if last_good is None:
            continue  # no anchor yet
        rel = None
        if relative is not None and relative[i] is not None:
            rel = relative[i]
            last_rel = rel
        else:
            rel = last_rel
        if max_bridge is not None and run > max_bridge:
            continue
        T[i] = T[i - 1] @ rel if not np.any(np.isnan(T[i - 1])) else last_good @ rel
        source[i] = BRIDGED
        last_good = T[i]
        gap_len[i] = run
    return FusedPoses(T, source, gap_len)


def simulate_dropouts(N: int, n_gaps: int, gap_len: int, seed: int = 0) -> np.ndarray:
    """Boolean [N] mask, True where the primary tracker is visible, with `n_gaps` dropouts of `gap_len` frames."""
    rng = np.random.default_rng(seed)
    vis = np.ones(N, bool)
    usable = N - 20
    slot = usable / n_gaps
    if slot <= gap_len:
        raise ValueError(f"{n_gaps} gaps of {gap_len} frames do not fit in {N} frames without overlapping")
    for k in range(n_gaps):
        lo = 10 + int(k * slot)
        hi = 10 + int((k + 1) * slot) - gap_len
        s = int(rng.integers(lo, max(lo + 1, hi)))
        vis[s:s + gap_len] = False
    return vis


def relative_from_absolute(T: np.ndarray) -> list[np.ndarray | None]:
    """Tool-frame relative motions T_{i-1->i} from an absolute pose array (relative[0] = None)."""
    out: list[np.ndarray | None] = [None]
    for i in range(1, T.shape[0]):
        out.append(np.linalg.inv(T[i - 1]) @ T[i])
    return out
