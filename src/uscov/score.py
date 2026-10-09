"""Completeness scoring, map-truthfulness metrics, and thin-region finding."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import label, center_of_mass

from .coverage import CoverageMap


@dataclass
class CompletenessResult:
    completeness: float          # fraction of ROI voxels with conf >= thresh
    mean_conf: float             # mean conf over ROI
    n_roi: int
    n_covered: int


def roi_from_reference(ref: CoverageMap, thresh: float = 0.5, min_hits: int = 1) -> np.ndarray:
    """Define the target region as what a full, well-tracked sweep actually imaged (flat bool [V])."""
    return (ref.conf_max >= thresh) & (ref.hits >= min_hits)


def completeness(cov: CoverageMap, roi: np.ndarray, thresh: float = 0.5) -> CompletenessResult:
    inroi = cov.conf_max[roi]
    covered = inroi >= thresh
    n = int(roi.sum())
    return CompletenessResult(
        completeness=float(covered.mean()) if n else 0.0,
        mean_conf=float(inroi.mean()) if n else 0.0,
        n_roi=n,
        n_covered=int(covered.sum()),
    )


@dataclass
class TruthfulnessResult:
    """How a candidate map (e.g. built from noisy poses) disagrees with the reference map."""
    false_coverage: float   # fraction of candidate-covered voxels the reference says were NOT imaged
    false_gap: float        # fraction of reference-covered voxels the candidate says were NOT imaged
    dice: float
    n_ref: int
    n_cand: int


def truthfulness(cand: CoverageMap, ref: CoverageMap, thresh: float = 0.5) -> TruthfulnessResult:
    a = cand.conf_max >= thresh
    b = ref.conf_max >= thresh
    inter = int((a & b).sum())
    na, nb = int(a.sum()), int(b.sum())
    return TruthfulnessResult(
        false_coverage=float((a & ~b).sum() / na) if na else 0.0,
        false_gap=float((b & ~a).sum() / nb) if nb else 0.0,
        dice=float(2 * inter / (na + nb)) if (na + nb) else 1.0,
        n_ref=nb,
        n_cand=na,
    )


@dataclass
class ThinRegion:
    size_voxels: int
    centre_mm: np.ndarray
    nearest_frame: int
    mean_conf: float


def thin_regions(cov: CoverageMap, roi: np.ndarray, frame_centres_mm: np.ndarray,
                 thresh: float = 0.5, min_size: int = 5, top_k: int = 5) -> list[ThinRegion]:
    """Connected components inside the ROI whose confidence is below threshold, largest first.

    `frame_centres_mm` [N,3] lets each region be tied to the frame that passed closest,
    which is the most natural 'go back near here' cue for a user.
    """
    gaps = (roi & (cov.conf_max < thresh)).reshape(cov.grid.shape)
    lab, n = label(gaps)
    if n == 0:
        return []
    sizes = np.bincount(lab.ravel())[1:]
    order = np.argsort(sizes)[::-1]
    out: list[ThinRegion] = []
    conf_vol = cov.conf_max.reshape(cov.grid.shape)
    for k in order[:top_k]:
        if sizes[k] < min_size:
            break
        com = np.array(center_of_mass(gaps, lab, k + 1))
        centre = cov.grid.origin + (com + 0.5) * cov.grid.voxel_mm
        d = np.linalg.norm(frame_centres_mm - centre, axis=1)
        out.append(ThinRegion(int(sizes[k]), centre, int(np.argmin(d)), float(conf_vol[lab == k + 1].mean())))
    return out
