"""Voxel coverage accumulation with per-pixel imaging confidence.

A voxel is not "covered" because a probe passed over it; it is covered to the
degree that some frame produced usable signal there. Stage 0 uses a simple
proxy confidence per pixel:

  conf = fan_mask * signal_conf(local brightness) * depth_weight(row)

- fan_mask      : pixels inside the curvilinear fan (ever non-zero in the scan)
- signal_conf   : soft threshold on local block-mean intensity; dark blocks are
                  shadow / dropout / poor contact and earn low confidence
- depth_weight  : gentle linear roll-off with depth (attenuation proxy)

Per voxel we keep the max confidence, the hit count, and the summed image-plane
normal so that angular diversity (1 - resultant length) can be reported.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import uniform_filter

from .data import Scan, pixel_grid, frame_normals_world, frame_corners_world


@dataclass
class GridSpec:
    origin: np.ndarray      # [3] mm, min corner
    voxel_mm: float
    shape: tuple[int, int, int]

    @classmethod
    def from_points(cls, pts: np.ndarray, voxel_mm: float, pad_mm: float = 5.0) -> "GridSpec":
        lo = pts.min(axis=0) - pad_mm
        hi = pts.max(axis=0) + pad_mm
        shape = tuple(int(v) for v in (np.ceil((hi - lo) / voxel_mm).astype(int) + 1))
        return cls(origin=lo.astype(np.float64), voxel_mm=float(voxel_mm), shape=shape)  # type: ignore[arg-type]

    def to_index(self, pts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """pts [M,3] -> (flat voxel index [M_inside], inside mask [M])."""
        ijk = np.floor((pts - self.origin) / self.voxel_mm).astype(np.int64)
        inside = np.all((ijk >= 0) & (ijk < np.array(self.shape)), axis=1)
        flat = np.ravel_multi_index(tuple(ijk[inside].T), self.shape)
        return flat, inside

    def centres(self, flat_idx: np.ndarray) -> np.ndarray:
        ijk = np.stack(np.unravel_index(flat_idx, self.shape), axis=1)
        return self.origin + (ijk + 0.5) * self.voxel_mm

    @property
    def n_voxels(self) -> int:
        return int(np.prod(self.shape))


@dataclass
class ConfidenceParams:
    block: int = 15                # block size (pixels) for local mean intensity
    dark_level: float = 12.0       # intensity at which signal_conf ~ 0.5
    softness: float = 6.0          # width of the soft threshold
    depth_min_weight: float = 0.6  # weight at the bottom of the image
    near_field_rows: int = 0       # rows at the top to down-weight (0 = off)


def fan_mask_from_scan(frames: np.ndarray, thresh: int = 2) -> np.ndarray:
    """Pixels that are ever brighter than `thresh` across the scan: the imaging fan."""
    mx = frames.max(axis=0)
    return mx > thresh


def pixel_confidence(frame: np.ndarray, fan: np.ndarray, p: ConfidenceParams) -> np.ndarray:
    """[H,W] float32 confidence in [0,1]."""
    f = frame.astype(np.float32)
    local = uniform_filter(f, size=p.block, mode="nearest")
    signal = 1.0 / (1.0 + np.exp(-(local - p.dark_level) / p.softness))
    h = frame.shape[0]
    depth_w = np.linspace(1.0, p.depth_min_weight, h, dtype=np.float32)[:, None]
    conf = signal * depth_w
    if p.near_field_rows > 0:
        conf[: p.near_field_rows] *= 0.5
    conf[~fan] = 0.0
    return conf.astype(np.float32)


@dataclass
class CoverageMap:
    grid: GridSpec
    conf_max: np.ndarray            # flat [V]
    hits: np.ndarray                # flat [V] int32
    normal_sum: np.ndarray          # flat [V,3]
    frames_added: list[int] = field(default_factory=list)

    @classmethod
    def empty(cls, grid: GridSpec) -> "CoverageMap":
        V = grid.n_voxels
        return cls(grid, np.zeros(V, np.float32), np.zeros(V, np.int32), np.zeros((V, 3), np.float32))

    def angular_diversity(self) -> np.ndarray:
        """1 - mean resultant length of plane normals; 0 = always same angle, ->1 = many angles."""
        with np.errstate(invalid="ignore", divide="ignore"):
            R = np.linalg.norm(self.normal_sum, axis=1) / np.maximum(self.hits, 1)
        div = 1.0 - R
        div[self.hits == 0] = 0.0
        return div.astype(np.float32)

    def volume(self, name: str = "conf_max") -> np.ndarray:
        arr = {"conf_max": self.conf_max, "hits": self.hits, "diversity": self.angular_diversity()}[name]
        return arr.reshape(self.grid.shape)

    def copy(self) -> "CoverageMap":
        return CoverageMap(self.grid, self.conf_max.copy(), self.hits.copy(), self.normal_sum.copy(),
                           list(self.frames_added))


class CoverageAccumulator:
    """Incrementally places frames into a voxel grid. Mirrors live use: call add_frame as frames arrive."""

    def __init__(self, scan: Scan, grid: GridSpec, T_frame_to_world: np.ndarray | None = None,
                 pixel_step: int = 4, conf_params: ConfidenceParams | None = None,
                 fan: np.ndarray | None = None, conf_model: str = "ray"):
        """conf_model: 'ray' (scan-line shadow model, default) or 'brightness' (Stage 0 rule)."""
        self.scan = scan
        self.grid = grid
        self.T = scan.frame_to_world() if T_frame_to_world is None else T_frame_to_world
        self.params = conf_params or ConfidenceParams()
        h, w = scan.shape
        self.P, self.rr, self.cc = pixel_grid(h, w, pixel_step)
        self.fan = fan_mask_from_scan(scan.frames) if fan is None else fan
        self.normals = frame_normals_world(self.T)
        self.map = CoverageMap.empty(grid)
        self.conf_model = conf_model
        self._ray = None
        if conf_model == "ray":
            from .confidence import RayConfidence
            self._ray = RayConfidence(self.fan)
        elif conf_model != "brightness":
            raise ValueError(f"unknown conf_model {conf_model!r}")

    def confidence_image(self, i: int) -> np.ndarray:
        if self._ray is not None:
            return self._ray.full(self.scan.frames[i])
        return pixel_confidence(self.scan.frames[i], self.fan, self.params)

    def _confidence_at_samples(self, i: int) -> np.ndarray:
        if self._ray is not None:
            return self._ray.at_pixels(self.scan.frames[i], self.rr, self.cc)
        return pixel_confidence(self.scan.frames[i], self.fan, self.params)[self.rr, self.cc]

    def add_frame(self, i: int) -> None:
        conf = self._confidence_at_samples(i)
        keep = conf > 0.0
        m = self.map
        if not np.any(keep):
            m.frames_added.append(i)
            return
        X = (self.T[i] @ self.P[:, keep])[:3].T  # [M,3]
        flat, inside = self.grid.to_index(X)
        c = conf[keep][inside]
        np.maximum.at(m.conf_max, flat, c)
        np.add.at(m.hits, flat, 1)
        # sum of normals: same vector for every hit this frame -> bincount per voxel is cheaper than add.at
        cnt = np.bincount(flat, minlength=m.hits.shape[0]).astype(np.float32)
        m.normal_sum += cnt[:, None] * self.normals[i][None, :]
        m.frames_added.append(i)

    def add_frames(self, indices) -> CoverageMap:
        for i in indices:
            self.add_frame(int(i))
        return self.map

    def run(self, frame_step: int = 1) -> CoverageMap:
        return self.add_frames(range(0, self.scan.n_frames, frame_step))


def grid_for_scan(scan: Scan, voxel_mm: float = 2.0, T_frame_to_world: np.ndarray | None = None,
                  pad_mm: float = 10.0, extra_T: list[np.ndarray] | None = None) -> GridSpec:
    """Grid that bounds the swept image planes (plus any alternative pose sets, so noisy runs fit too)."""
    h, w = scan.shape
    Ts = [scan.frame_to_world() if T_frame_to_world is None else T_frame_to_world]
    if extra_T:
        Ts.extend(extra_T)
    pts = np.concatenate([frame_corners_world(T, h, w).reshape(-1, 3) for T in Ts], axis=0)
    return GridSpec.from_points(pts, voxel_mm, pad_mm)
