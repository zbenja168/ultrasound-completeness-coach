"""Ray-based imaging confidence for scan-converted curvilinear (or linear) B-mode frames.

Why: the Stage 0 brightness rule cannot tell a bone shadow from a cyst. Both are dark. The
difference is what lies *beyond* them along the scan line: a cyst has tissue signal behind it
(sound passed through), a shadow has nothing (sound was blocked). So confidence is computed
along rays from the probe face, not per pixel in isolation.

Model, per ray, with s(r) the smoothed intensity at depth r:
    sig_now(r)   = soft threshold of s(r)                      (is there signal here?)
    sig_ahead(r) = soft threshold of max_{r' > r} s(r')        (is there signal deeper?)
    shadow(r)    = (1 - sig_now) * (1 - sig_ahead)            (dark here AND nothing beyond)
    conf(r)      = (1 - shadow(r)) * depth_weight(r)
A dark region with signal beneath it keeps its confidence (anechoic structure, imaged fine).
A dark region with no signal beneath it loses it (shadow, dropout, or no contact).

Geometry is recovered from the fan mask: the lateral edges of a curvilinear fan are straight
lines meeting at a virtual apex above the image; rays are cast from that apex. A linear probe
(rectangular mask) is handled as parallel vertical rays.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import map_coordinates, uniform_filter1d, uniform_filter


@dataclass
class FanGeometry:
    apex: tuple[float, float]      # (row, col), may lie above the image
    theta_min: float               # radians, measured from straight down (0) ; negative = left
    theta_max: float
    r_min: float                   # px, top arc
    r_max: float                   # px, bottom arc
    linear: bool = False           # rectangular (linear probe) fallback

    @classmethod
    def from_mask(cls, mask: np.ndarray) -> "FanGeometry":
        h, w = mask.shape
        rows = np.where(mask.any(axis=1))[0]  # rows with any fan pixel (gaps inside the fan are skipped)
        r0, r1 = int(rows.min()), int(rows.max())
        left = np.array([np.where(mask[r])[0].min() for r in rows], dtype=float)
        right = np.array([np.where(mask[r])[0].max() for r in rows], dtype=float)
        rr = rows.astype(float)
        # use rows where the fan does not touch the image border and is still widening (lateral edges)
        widest = int(np.argmax(right - left))
        ok = (left > 0) & (right < w - 1) & (np.arange(len(rr)) < widest)
        ok[: max(3, int(0.08 * len(rr)))] = False  # skip the top arc itself
        if ok.sum() < 10:
            return cls(apex=(float(r0), w / 2.0), theta_min=0.0, theta_max=0.0, r_min=0.0,
                       r_max=float(r1 - r0), linear=True)
        pl = np.polyfit(rr[ok], left[ok], 1)   # col = a*row + b
        pr = np.polyfit(rr[ok], right[ok], 1)
        if abs(pl[0] - pr[0]) < 1e-3:         # parallel edges -> linear probe
            return cls(apex=(float(r0), (left[ok].mean() + right[ok].mean()) / 2), theta_min=0.0, theta_max=0.0,
                       r_min=0.0, r_max=float(r1 - r0), linear=True)
        apex_row = (pr[1] - pl[1]) / (pl[0] - pr[0])
        apex_col = pl[0] * apex_row + pl[1]
        ys, xs = np.nonzero(mask)
        d = np.hypot(ys - apex_row, xs - apex_col)
        th = np.arctan2(xs - apex_col, ys - apex_row)  # 0 = straight down
        return cls(apex=(float(apex_row), float(apex_col)), theta_min=float(th.min()),
                   theta_max=float(th.max()), r_min=float(d.min()), r_max=float(d.max()))


@dataclass
class RayConfidenceParams:
    n_rays: int = 256
    r_step_px: float = 2.0         # radial sample spacing
    smooth_px: int = 9             # along-ray smoothing (~2 mm at 0.23 mm/px)
    lateral_rays: int = 3          # across-ray smoothing
    dark_level: float = 12.0
    softness: float = 6.0
    depth_min_weight: float = 0.6  # weight at r_max
    ahead_level: float = 28.0      # 'signal beyond' must clear this (noise floor in shadows is ~10-20)
    ahead_smooth_px: int = 21      # heavier along-ray smoothing before the beyond-test (~5 mm)


class RayConfidence:
    """Precomputes polar sampling for one fan geometry; call per frame."""

    def __init__(self, mask: np.ndarray, params: RayConfidenceParams | None = None):
        self.p = params or RayConfidenceParams()
        self.mask = mask
        self.geom = g = FanGeometry.from_mask(mask)
        p = self.p
        h, w = mask.shape
        self.n_r = int(np.ceil((g.r_max - g.r_min) / p.r_step_px)) + 1
        rs = g.r_min + np.arange(self.n_r) * p.r_step_px
        if g.linear:
            ths = np.linspace(0, 1, p.n_rays)  # fraction across the rectangle
            ys, xs = np.nonzero(mask)
            x0, x1 = xs.min(), xs.max()
            cols = x0 + ths * (x1 - x0)
            R, C = np.meshgrid(rs, cols, indexing="ij")
            self.rows_f = g.apex[0] + R
            self.cols_f = C
        else:
            ths = np.linspace(g.theta_min, g.theta_max, p.n_rays)
            R, T = np.meshgrid(rs, ths, indexing="ij")           # [n_r, n_rays]
            self.rows_f = g.apex[0] + R * np.cos(T)
            self.cols_f = g.apex[1] + R * np.sin(T)
        self.ths = ths
        self.rs = rs
        self._valid = (self.rows_f >= 0) & (self.rows_f <= h - 1) & (self.cols_f >= 0) & (self.cols_f <= w - 1)
        self.depth_w = np.exp(np.log(p.depth_min_weight) * (rs - g.r_min) / max(g.r_max - g.r_min, 1.0))[:, None]

    # ------------------------------------------------------------------ core
    def polar_confidence(self, frame: np.ndarray) -> np.ndarray:
        """[n_r, n_rays] confidence in polar coordinates."""
        p = self.p
        f = frame.astype(np.float32)
        s = map_coordinates(f, [self.rows_f, self.cols_f], order=1, mode="constant", cval=0.0)
        s[~self._valid] = 0.0
        step = max(1, int(p.r_step_px))
        raw = s
        s = uniform_filter1d(raw, size=max(1, p.smooth_px // step), axis=0, mode="nearest")
        if p.lateral_rays > 1:
            s = uniform_filter1d(s, size=p.lateral_rays, axis=1, mode="nearest")
        sig_now = 1.0 / (1.0 + np.exp(-(s - p.dark_level) / p.softness))
        # signal beyond: heavier smoothing, then reverse running max along the ray, then a stricter threshold,
        # so the noise floor inside a shadow does not pass as 'tissue beyond'
        s2 = uniform_filter1d(raw, size=max(1, p.ahead_smooth_px // step), axis=0, mode="nearest")
        if p.lateral_rays > 1:
            s2 = uniform_filter1d(s2, size=p.lateral_rays, axis=1, mode="nearest")
        ahead = np.maximum.accumulate(s2[::-1], axis=0)[::-1]
        ahead = np.vstack([ahead[1:], np.zeros((1, s.shape[1]), np.float32)])  # exclude current depth
        sig_ahead = 1.0 / (1.0 + np.exp(-(ahead - p.ahead_level) / p.softness))
        shadow = (1.0 - sig_now) * (1.0 - sig_ahead)
        conf = (1.0 - shadow) * self.depth_w
        conf[~self._valid] = 0.0
        return conf.astype(np.float32)

    def _polar_index(self, rows: np.ndarray, cols: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        g = self.geom
        if g.linear:
            ys, xs = np.nonzero(self.mask)
            x0, x1 = xs.min(), xs.max()
            ri = np.round((rows - g.apex[0]) / self.p.r_step_px).astype(int)
            ti = np.round((cols - x0) / max(x1 - x0, 1) * (self.p.n_rays - 1)).astype(int)
        else:
            d = np.hypot(rows - g.apex[0], cols - g.apex[1])
            th = np.arctan2(cols - g.apex[1], rows - g.apex[0])
            ri = np.round((d - g.r_min) / self.p.r_step_px).astype(int)
            ti = np.round((th - g.theta_min) / (g.theta_max - g.theta_min) * (self.p.n_rays - 1)).astype(int)
        inside = (ri >= 0) & (ri < self.n_r) & (ti >= 0) & (ti < self.p.n_rays)
        return ri, ti, inside

    def at_pixels(self, frame: np.ndarray, rows: np.ndarray, cols: np.ndarray) -> np.ndarray:
        """Confidence at the given pixel positions (used by the coverage accumulator)."""
        conf_p = self.polar_confidence(frame)
        ri, ti, inside = self._polar_index(rows.astype(float), cols.astype(float))
        out = np.zeros(rows.shape, np.float32)
        out[inside] = conf_p[ri[inside], ti[inside]]
        out[~self.mask[rows, cols]] = 0.0
        return out

    def full(self, frame: np.ndarray) -> np.ndarray:
        """[H,W] confidence image for visualisation."""
        h, w = frame.shape
        rr, cc = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
        return self.at_pixels(frame, rr.ravel(), cc.ravel()).reshape(h, w)
