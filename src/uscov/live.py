"""Live pipeline pieces: frame sources, a marker-cube pose source, and a session that feeds the engine.

Sources are deliberately tiny interfaces so the engine never knows whether frames come from a capture
card, a recorded sweep, or a test pattern.

  FrameSource.read()  -> (timestamp_s, gray uint8 [H,W]) or None at end of stream
  PoseSource.read()   -> (timestamp_s, 4x4 tool->world) or (timestamp_s, None) when not tracked

Concrete sources:
  CaptureCardSource   : OpenCV VideoCapture on a USB capture card (the cart's video output); crops the image region
  ReplaySource        : replays a TUS-REC scan with its tracked poses, as if live (for testing without hardware)
  ArucoCubeTracker    : OpenCV ArUco board (markers on cube faces) seen by a webcam -> probe pose

Spatial calibration (image <-> tool) and temporal alignment are supplied as constants here; PLUS fCal
produces them in the lab. For the replay source the dataset's calibration is used.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from .data import Scan, Calib


# ----------------------------------------------------------------------------- frame sources

class ReplaySource:
    """Replay a loaded Scan at its native frame rate (or faster)."""

    def __init__(self, scan: Scan, fps: float = 20.0, speed: float = 1.0, realtime: bool = False):
        self.scan, self.fps, self.speed, self.realtime = scan, fps, speed, realtime
        self.i = 0
        self._t0 = time.time()

    def read(self):
        if self.i >= self.scan.n_frames:
            return None
        ts = self.i / self.fps
        if self.realtime:
            target = self._t0 + ts / self.speed
            now = time.time()
            if target > now:
                time.sleep(target - now)
        frame = self.scan.frames[self.i]
        self.i += 1
        return ts, frame

    def pose(self, i: int) -> np.ndarray:
        return self.scan.tforms[i]


class CaptureCardSource:
    """USB capture card / webcam via OpenCV. `crop` = (row0, row1, col0, col1) of the ultrasound image region."""

    def __init__(self, device: int = 0, crop: tuple[int, int, int, int] | None = None, width: int | None = None,
                 height: int | None = None):
        import cv2
        self.cv2 = cv2
        self.cap = cv2.VideoCapture(device)
        if width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        if height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if not self.cap.isOpened():
            raise RuntimeError(f"could not open capture device {device}")
        self.crop = crop
        self._t0 = time.time()

    def read(self):
        ok, img = self.cap.read()
        if not ok:
            return None
        ts = time.time() - self._t0
        g = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)
        if self.crop:
            r0, r1, c0, c1 = self.crop
            g = g[r0:r1, c0:c1]
        return ts, g

    def release(self):
        self.cap.release()


# ----------------------------------------------------------------------------- marker cube tracker

@dataclass
class CubeSpec:
    """Marker layout on a cube: marker ids per face and the cube edge length (mm). Markers centred on faces."""
    edge_mm: float = 30.0
    marker_mm: float = 24.0
    face_ids: dict[str, int] = field(default_factory=lambda: {"+x": 0, "-x": 1, "+y": 2, "-y": 3, "+z": 4, "-z": 5})
    dictionary: str = "DICT_4X4_50"

    def board(self, cv2):
        """cv2.aruco.Board with each marker's 4 corners in the cube frame (origin at cube centre)."""
        h = self.edge_mm / 2.0
        m = self.marker_mm / 2.0
        # corners in marker order (top-left, top-right, bottom-right, bottom-left) as seen from outside
        faces = {
            "+z": [[-m, m, h], [m, m, h], [m, -m, h], [-m, -m, h]],
            "-z": [[m, m, -h], [-m, m, -h], [-m, -m, -h], [m, -m, -h]],
            "+x": [[h, m, m], [h, m, -m], [h, -m, -m], [h, -m, m]],
            "-x": [[-h, m, -m], [-h, m, m], [-h, -m, m], [-h, -m, -m]],
            "+y": [[-m, h, -m], [m, h, -m], [m, h, m], [-m, h, m]],
            "-y": [[-m, -h, m], [m, -h, m], [m, -h, -m], [-m, -h, -m]],
        }
        ids, objpts = [], []
        for face, mid in self.face_ids.items():
            ids.append(mid)
            objpts.append(np.array(faces[face], dtype=np.float32))
        dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, self.dictionary))
        return cv2.aruco.Board(np.array(objpts, dtype=np.float32), dictionary, np.array(ids, dtype=np.int32))


class ArucoCubeTracker:
    """Estimates the cube pose (cube->camera) from a camera image. Needs camera intrinsics (K, dist)."""

    def __init__(self, K: np.ndarray, dist: np.ndarray, cube: CubeSpec | None = None):
        import cv2
        self.cv2 = cv2
        self.K, self.dist = np.asarray(K, np.float64), np.asarray(dist, np.float64)
        self.cube = cube or CubeSpec()
        self.board = self.cube.board(cv2)
        params = cv2.aruco.DetectorParameters()
        params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX  # sub-pixel corners: pose error scales with this
        self.detector = cv2.aruco.ArucoDetector(self.board.getDictionary(), params)

    def detect(self, gray: np.ndarray):
        corners, ids, _ = self.detector.detectMarkers(gray)
        return corners, ids

    def pose(self, gray: np.ndarray) -> tuple[np.ndarray | None, int]:
        """Returns (4x4 cube->camera or None, number of markers used)."""
        corners, ids = self.detect(gray)
        if ids is None or len(ids) == 0:
            return None, 0
        obj, img = self.board.matchImagePoints(corners, ids)
        if obj is None or len(obj) < 4:
            return None, 0
        ok, rvec, tvec = self.cv2.solvePnP(obj, img, self.K, self.dist, flags=self.cv2.SOLVEPNP_ITERATIVE)
        if not ok:
            return None, 0
        R, _ = self.cv2.Rodrigues(rvec)
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = tvec.ravel()
        return T, int(len(ids))


def render_marker_image(marker_id: int, size_px: int = 200, dictionary: str = "DICT_4X4_50") -> np.ndarray:
    """Marker bitmap for printing / for synthetic tests."""
    import cv2
    d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dictionary))
    return cv2.aruco.generateImageMarker(d, marker_id, size_px)


# ----------------------------------------------------------------------------- live session

@dataclass
class LiveSession:
    """Feeds frames + poses into a CoverageAccumulator as they arrive; keeps the last completeness and cue."""
    acc: object            # CoverageAccumulator built on a Scan-like container with preallocated frames
    roi: np.ndarray | None = None
    frames_seen: int = 0
    last_completeness: float = float("nan")

    def step(self, i: int) -> None:
        from .score import completeness
        self.acc.add_frame(i)
        self.frames_seen += 1
        if self.roi is not None and self.frames_seen % 10 == 0:
            self.last_completeness = completeness(self.acc.map, self.roi).completeness
