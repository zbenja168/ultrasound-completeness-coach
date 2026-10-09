"""Pose corruption models that mimic real tracking error families.

All models operate on the *relative* motion between consecutive frames and
re-integrate, so error accumulates the way it does in real trackers.

  jitter  : independent per-frame noise, no accumulation   (optical/marker trackers)
  drift   : random-walk position/orientation offset         (IMU/VIO style)
  bias    : constant small per-frame error in a fixed
            direction -> linear growth with path length     (sensorless DL style)

Presets are rough, literature-anchored levels (see research notes):
  optical      ~0.25 mm RMS
  aruco_phone  ~2-3 mm, ~1 deg (marker cube + phone/RGB-D camera)
  sensorless   ~5% final drift rate of path length (TUS-REC 2025 best)
  arkit_free   ~0.02 m/s relative drift (markerless phone VIO) = 1 mm/frame at 20 fps
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation as R


@dataclass
class NoiseSpec:
    name: str
    jitter_mm: float = 0.0
    jitter_deg: float = 0.0
    drift_mm_per_frame: float = 0.0
    drift_deg_per_frame: float = 0.0
    bias_frac_of_step: float = 0.0     # bias magnitude as a fraction of the mean inter-frame step
    bias_deg_per_frame: float = 0.0


PRESETS: dict[str, NoiseSpec] = {
    "perfect": NoiseSpec("perfect"),
    "optical": NoiseSpec("optical", jitter_mm=0.25, jitter_deg=0.1),
    "aruco_phone": NoiseSpec("aruco_phone", jitter_mm=2.5, jitter_deg=1.0, drift_mm_per_frame=0.02),
    "sensorless": NoiseSpec("sensorless", jitter_mm=0.1, bias_frac_of_step=0.05, bias_deg_per_frame=0.003,
                            drift_mm_per_frame=0.03),
    "arkit_free": NoiseSpec("arkit_free", jitter_mm=1.0, jitter_deg=0.3, drift_mm_per_frame=1.0,
                            drift_deg_per_frame=0.05),
}


def _se3(t: np.ndarray, rotvec_deg: np.ndarray) -> np.ndarray:
    T = np.eye(4)
    T[:3, :3] = R.from_rotvec(np.deg2rad(rotvec_deg)).as_matrix()
    T[:3, 3] = t
    return T


def _perturb_about_tool(T: np.ndarray, t_world: np.ndarray, rotvec_deg: np.ndarray) -> np.ndarray:
    """Rotate about the tool's own origin (not the world origin) and translate in world coordinates."""
    out = T @ _se3(np.zeros(3), rotvec_deg)
    out[:3, 3] += t_world
    return out


def corrupt_poses(tforms: np.ndarray, spec: NoiseSpec, seed: int = 0) -> np.ndarray:
    """Return corrupted [N,4,4] tool->world poses. Frame 0 is kept as the anchor."""
    rng = np.random.default_rng(seed)
    N = tforms.shape[0]
    out = np.empty_like(tforms)
    out[0] = tforms[0]
    if N == 1:
        return out

    # relative GT motions expressed in the previous tool frame
    rel = np.linalg.inv(tforms[:-1]) @ tforms[1:]
    mean_step = float(np.linalg.norm(rel[:, :3, 3], axis=1).mean())

    # constant per-frame bias (sensorless-style linear drift)
    bias_dir = rng.normal(size=3); bias_dir /= np.linalg.norm(bias_dir)
    bias_axis = rng.normal(size=3); bias_axis /= np.linalg.norm(bias_axis)
    eps = _se3(bias_dir * spec.bias_frac_of_step * mean_step, bias_axis * spec.bias_deg_per_frame)
    for i in range(1, N):
        out[i] = out[i - 1] @ rel[i - 1] @ eps

    # random-walk offset (IMU/VIO-style drift): translation in world, rotation about the tool origin
    if spec.drift_mm_per_frame > 0 or spec.drift_deg_per_frame > 0:
        wt = np.cumsum(rng.normal(scale=spec.drift_mm_per_frame, size=(N, 3)), axis=0)
        wr = np.cumsum(rng.normal(scale=spec.drift_deg_per_frame, size=(N, 3)), axis=0)
        for i in range(1, N):
            out[i] = _perturb_about_tool(out[i], wt[i], wr[i])

    # independent per-frame jitter (marker/optical-style)
    if spec.jitter_mm > 0 or spec.jitter_deg > 0:
        jt = rng.normal(scale=spec.jitter_mm, size=(N, 3))
        jr = rng.normal(scale=spec.jitter_deg, size=(N, 3))
        for i in range(1, N):
            out[i] = _perturb_about_tool(out[i], jt[i], jr[i])
    return out


@dataclass
class TrajectoryError:
    final_drift_mm: float
    mean_err_mm: float
    max_err_mm: float
    path_length_mm: float

    @property
    def final_drift_rate(self) -> float:
        return self.final_drift_mm / self.path_length_mm if self.path_length_mm else 0.0


def trajectory_error(T_gt: np.ndarray, T_noisy: np.ndarray, probe_point: np.ndarray) -> TrajectoryError:
    """Compare where a fixed homogeneous point lands under GT vs noisy frame->world transforms."""
    p_gt = (T_gt @ probe_point)[:, :3]
    p_no = (T_noisy @ probe_point)[:, :3]
    err = np.linalg.norm(p_gt - p_no, axis=1)
    path = float(np.linalg.norm(np.diff(p_gt, axis=0), axis=1).sum())
    return TrajectoryError(float(err[-1]), float(err.mean()), float(err.max()), path)
