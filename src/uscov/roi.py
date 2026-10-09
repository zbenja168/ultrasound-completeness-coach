"""Named target regions so a gap can be reported as 'lower pole, left lobe' rather than as coordinates.

A `RegionTemplate` is a set of named primitives (ellipsoids and boxes) in a template frame.
`fit_to_extent` places it in world coordinates by scaling/translating the template's bounding box
onto a target bounding box (e.g. the extent of a scout sweep, or a phantom's known footprint).
Stage 2 will replace the extent fit with a real registration; the naming machinery stays.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .coverage import GridSpec, CoverageMap


@dataclass
class Primitive:
    name: str
    kind: str                 # 'ellipsoid' | 'box'
    centre: np.ndarray        # [3] template units
    half: np.ndarray          # [3] semi-axes / half-sizes

    def contains(self, pts: np.ndarray) -> np.ndarray:
        d = (pts - self.centre) / self.half
        if self.kind == "ellipsoid":
            return (d ** 2).sum(axis=1) <= 1.0
        return np.all(np.abs(d) <= 1.0, axis=1)


@dataclass
class RegionTemplate:
    name: str
    parts: list[Primitive] = field(default_factory=list)

    def bounds(self) -> tuple[np.ndarray, np.ndarray]:
        lo = np.min([p.centre - p.half for p in self.parts], axis=0)
        hi = np.max([p.centre + p.half for p in self.parts], axis=0)
        return lo, hi

    def transformed(self, scale: np.ndarray, offset: np.ndarray, name: str | None = None) -> "RegionTemplate":
        return RegionTemplate(name or self.name, [
            Primitive(p.name, p.kind, p.centre * scale + offset, p.half * scale) for p in self.parts])

    def fit_to_extent(self, lo: np.ndarray, hi: np.ndarray, axes: tuple[int, int, int] = (0, 1, 2)) -> "RegionTemplate":
        """Scale/translate so the template's bounding box fills [lo, hi] in world mm.

        `axes` maps template axes (x = left-right, y = superior-inferior, z = anterior-posterior) onto
        world axes, since a scout sweep's orientation is arbitrary.
        """
        tlo, thi = self.bounds()
        perm = np.array(axes)
        parts = []
        for p in self.parts:
            c = p.centre[perm]; hsz = p.half[perm]
            tl, th = tlo[perm], thi[perm]
            scale = (hi - lo) / np.maximum(th - tl, 1e-6)
            parts.append(Primitive(p.name, p.kind, (c - tl) * scale + lo, hsz * scale))
        return RegionTemplate(self.name, parts)

    def label_grid(self, grid: GridSpec) -> np.ndarray:
        """Flat int label per voxel: 0 = outside, i = index+1 of the first part containing the voxel centre."""
        centres = grid.centres(np.arange(grid.n_voxels))
        lab = np.zeros(grid.n_voxels, np.int32)
        for i, p in enumerate(self.parts):
            m = (lab == 0) & p.contains(centres)
            lab[m] = i + 1
        return lab

    def part_names(self) -> list[str]:
        return [p.name for p in self.parts]


def thyroid_template() -> RegionTemplate:
    """Adult thyroid, approximate dimensions in mm (template frame: x left-right, y sup-inf, z ant-post).

    Lobes ~ 45 mm tall, 18 mm wide, 15 mm deep; isthmus ~ 20 mm wide, 12 mm tall, 4 mm deep.
    Each lobe is split into upper and lower halves so gaps can name the pole.
    """
    lobe_w, lobe_h, lobe_d = 18.0, 45.0, 15.0
    x_off = 20.0  # lobe centre offset from midline
    parts = []
    for side, sx in (("right", -1.0), ("left", 1.0)):
        cx = sx * x_off
        parts.append(Primitive(f"{side} lobe, upper pole", "ellipsoid",
                               np.array([cx, lobe_h / 4, 0.0]), np.array([lobe_w / 2, lobe_h / 4 + 2, lobe_d / 2])))
        parts.append(Primitive(f"{side} lobe, lower pole", "ellipsoid",
                               np.array([cx, -lobe_h / 4, 0.0]), np.array([lobe_w / 2, lobe_h / 4 + 2, lobe_d / 2])))
    parts.append(Primitive("isthmus", "box", np.array([0.0, -2.0, 5.0]), np.array([x_off, 6.0, 2.0])))
    return RegionTemplate("thyroid", parts)


def sweep_thirds_template(lo: np.ndarray, hi: np.ndarray, sweep_axis: int, depth_axis: int,
                          sweep_direction: float = 1.0) -> RegionTemplate:
    """Generic named region for a non-anatomical target (phantom, forearm): the extent split into
    start/middle/end thirds along the sweep and superficial/deep halves along depth. Names let the
    cue read 'end third, deep' until an anatomical template is available.

    `sweep_direction` < 0 means the sweep ran toward decreasing coordinate, so 'start' is the high end."""
    parts = []
    size = hi - lo
    thirds = ("start third", "middle third", "end third")
    if sweep_direction < 0:
        thirds = thirds[::-1]
    for k, third in enumerate(thirds):
        for j, depth in enumerate(("superficial", "deep")):
            c = (lo + hi) / 2.0
            h = size / 2.0
            c = c.copy(); h = h.copy()
            c[sweep_axis] = lo[sweep_axis] + size[sweep_axis] * (k + 0.5) / 3.0
            h[sweep_axis] = size[sweep_axis] / 6.0
            c[depth_axis] = lo[depth_axis] + size[depth_axis] * (j + 0.5) / 2.0
            h[depth_axis] = size[depth_axis] / 4.0
            parts.append(Primitive(f"{third}, {depth}", "box", c, h))
    return RegionTemplate("sweep thirds", parts)


def extent_of_roi(roi_flat: np.ndarray, grid: GridSpec) -> tuple[np.ndarray, np.ndarray]:
    """Bounding box (mm) of the voxels in a flat boolean ROI."""
    idx = np.where(roi_flat)[0]
    c = grid.centres(idx)
    return c.min(axis=0) - grid.voxel_mm / 2, c.max(axis=0) + grid.voxel_mm / 2


@dataclass
class PartReport:
    name: str
    n_voxels: int
    completeness: float
    mean_conf: float


def report_by_part(cov: CoverageMap, labels: np.ndarray, names: list[str], thresh: float = 0.5,
                   min_hits: int = 1) -> list[PartReport]:
    from .score import covered_mask
    covered = covered_mask(cov, thresh, min_hits)
    out = []
    for i, nm in enumerate(names):
        m = labels == i + 1
        n = int(m.sum())
        out.append(PartReport(nm, n, float(covered[m].mean()) if n else 0.0,
                              float(cov.conf_max[m].mean()) if n else 0.0))
    return out


def worst_parts(reports: list[PartReport], k: int = 3) -> list[PartReport]:
    return sorted(reports, key=lambda r: r.completeness)[:k]
