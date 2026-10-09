"""Loading TUS-REC style scans and building per-frame image->world transforms.

Conventions (from the TUS-REC baseline README):
  tforms[i]        : tracker tool -> camera (world), 4x4, per frame
  image_to_tool    : image (mm) -> tracker tool, 4x4, from calib_matrix.csv
  scale            : pixel -> mm, 4x4 diagonal
  world point of pixel p (homogeneous [x_col, y_row, 0, 1], 1-based)
                   = tforms[i] @ image_to_tool @ scale @ p
"""
from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import h5py
import numpy as np


@dataclass
class Calib:
    scale: np.ndarray          # 4x4 pixel -> mm
    image_to_tool: np.ndarray  # 4x4 image(mm) -> tool

    @property
    def pixel_to_tool(self) -> np.ndarray:
        return self.image_to_tool @ self.scale

    @property
    def mm_per_pixel(self) -> tuple[float, float]:
        return float(self.scale[0, 0]), float(self.scale[1, 1])


@dataclass
class Scan:
    name: str
    frames: np.ndarray   # [N,H,W] uint8
    tforms: np.ndarray   # [N,4,4] tool -> world
    calib: Calib

    @property
    def n_frames(self) -> int:
        return int(self.frames.shape[0])

    @property
    def shape(self) -> tuple[int, int]:
        return int(self.frames.shape[1]), int(self.frames.shape[2])

    def frame_to_world(self, tforms: np.ndarray | None = None) -> np.ndarray:
        """[N,4,4] pixel(1-based homogeneous) -> world(mm) for every frame.

        `tforms` lets callers substitute corrupted poses for the tracked ones.
        """
        T = self.tforms if tforms is None else tforms
        return T @ self.calib.pixel_to_tool  # broadcasts over N


# --------------------------------------------------------------------------- calib

_NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")


def load_calib(path: str | Path) -> Calib:
    """Parse TUS-REC calib_matrix.csv.

    The file holds two labelled blocks: a pixel->mm scaling and a 4x4 rigid
    image->tool transform. The parser collects every number following each
    label so it tolerates minor layout differences between releases.
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    blocks: dict[str, list[float]] = {}
    current: str | None = None
    for line in text.splitlines():
        low = line.lower()
        if "scaling" in low:
            current = "scale"
            blocks.setdefault(current, [])
            tail = line.split(",", 1)[-1] if "," in line else ""
            if tail and not re.search(r"[a-zA-Z]", tail):
                blocks[current].extend(float(x) for x in _NUM.findall(tail))
            continue
        if "calibration" in low or "spatial" in low:
            current = "rigid"
            blocks.setdefault(current, [])
            continue
        if current is None:
            continue
        blocks[current].extend(float(x) for x in _NUM.findall(line))

    if "scale" not in blocks or "rigid" not in blocks:
        raise ValueError(f"Could not find scaling and calibration blocks in {path}: {list(blocks)}")

    s = blocks["scale"]
    if len(s) >= 16:
        scale = np.array(s[:16], dtype=np.float64).reshape(4, 4)
    elif len(s) >= 2:
        scale = np.diag([s[0], s[1], 1.0, 1.0])
    elif len(s) == 1:
        scale = np.diag([s[0], s[0], 1.0, 1.0])
    else:
        raise ValueError(f"Unexpected scaling block: {s}")

    r = blocks["rigid"]
    if len(r) < 16:
        raise ValueError(f"Rigid calibration block has {len(r)} numbers, expected 16")
    rigid = np.array(r[:16], dtype=np.float64).reshape(4, 4)
    return Calib(scale=scale, image_to_tool=rigid)


# --------------------------------------------------------------------------- dataset

@dataclass
class DatasetIndex:
    root: Path
    calib: Calib
    scans: list[tuple[str, Path, Path]]  # (name, frames_h5, tforms_h5)

    def __len__(self) -> int:
        return len(self.scans)

    def names(self) -> list[str]:
        return [s[0] for s in self.scans]

    def load(self, name_or_idx: str | int, frame_step: int = 1) -> Scan:
        if isinstance(name_or_idx, int):
            name, fpath, tpath = self.scans[name_or_idx]
        else:
            matches = [s for s in self.scans if s[0] == name_or_idx]
            if not matches:
                raise KeyError(name_or_idx)
            name, fpath, tpath = matches[0]
        with h5py.File(fpath, "r") as f:
            frames = f["frames"][::frame_step]
        with h5py.File(tpath, "r") as f:
            tforms = f["tforms"][::frame_step].astype(np.float64)
        return Scan(name=name, frames=np.asarray(frames), tforms=tforms, calib=self.calib)

    def iter_scans(self, frame_step: int = 1) -> Iterator[Scan]:
        for i in range(len(self.scans)):
            yield self.load(i, frame_step=frame_step)


def ensure_extracted(zip_path: str | Path, out_dir: str | Path) -> Path:
    """Extract a TUS-REC zip once; return the extraction root."""
    zip_path, out_dir = Path(zip_path), Path(out_dir)
    marker = out_dir / ".extracted"
    if not marker.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(out_dir)
        marker.write_text("ok")
    return out_dir


def index_dataset(root: str | Path) -> DatasetIndex:
    """Discover scans under an extracted TUS-REC folder.

    Supports both layouts seen in the releases:
      frames/<sub>/<scan>.h5 + transfs/<sub>/<scan>.h5      (validation sets)
      frames_transfs/<sub>/<scan>.h5 with both keys inside   (2025 train)
    """
    root = Path(root)
    calib_files = list(root.rglob("calib_matrix.csv"))
    if not calib_files:
        raise FileNotFoundError(f"No calib_matrix.csv under {root}")
    calib = load_calib(calib_files[0])
    base = calib_files[0].parent

    scans: list[tuple[str, Path, Path]] = []
    if (base / "frames").is_dir() and (base / "transfs").is_dir():
        for fpath in sorted((base / "frames").rglob("*.h5")):
            rel = fpath.relative_to(base / "frames")
            tpath = base / "transfs" / rel
            if tpath.exists():
                scans.append((rel.with_suffix("").as_posix().replace("/", "__"), fpath, tpath))
    elif (base / "frames_transfs").is_dir():
        for fpath in sorted((base / "frames_transfs").rglob("*.h5")):
            rel = fpath.relative_to(base / "frames_transfs")
            scans.append((rel.with_suffix("").as_posix().replace("/", "__"), fpath, fpath))
    else:
        raise FileNotFoundError(f"Unrecognised layout under {base}")
    if not scans:
        raise FileNotFoundError(f"No scans found under {base}")
    return DatasetIndex(root=base, calib=calib, scans=scans)


# --------------------------------------------------------------------------- geometry helpers

def pixel_grid(h: int, w: int, step: int = 1) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Homogeneous pixel coords [4,M] (x=col, y=row, 0, 1; 1-based) plus (rows, cols) index arrays."""
    rows = np.arange(0, h, step)
    cols = np.arange(0, w, step)
    rr, cc = np.meshgrid(rows, cols, indexing="ij")
    rr, cc = rr.ravel(), cc.ravel()
    P = np.stack([cc + 1.0, rr + 1.0, np.zeros(rr.shape, dtype=np.float64), np.ones(rr.shape, dtype=np.float64)])
    return P, rr, cc


def frame_corners_world(T_frame_to_world: np.ndarray, h: int, w: int) -> np.ndarray:
    """World coords [N,4,3] of the four image corners for every frame."""
    P = np.array([[1, 1, 0, 1], [w, 1, 0, 1], [w, h, 0, 1], [1, h, 0, 1]], dtype=np.float64).T  # 4x4
    X = T_frame_to_world @ P  # [N,4,4]
    return np.transpose(X[:, :3, :], (0, 2, 1))


def frame_centres_world(T_frame_to_world: np.ndarray, h: int, w: int) -> np.ndarray:
    p = np.array([(w + 1) / 2.0, (h + 1) / 2.0, 0.0, 1.0])
    return (T_frame_to_world @ p)[:, :3]


def frame_normals_world(T_frame_to_world: np.ndarray) -> np.ndarray:
    """Unit normal of each image plane in world coords (image z axis, i.e. elevational direction)."""
    n = T_frame_to_world[:, :3, 2]
    return n / np.linalg.norm(n, axis=1, keepdims=True)
