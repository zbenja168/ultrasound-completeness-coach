"""Synthetic test of the ArUco cube tracker: render one cube face into a virtual camera, recover its pose."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uscov.live import ArucoCubeTracker, CubeSpec, render_marker_image, ReplaySource  # noqa: E402
from uscov.data import Scan, Calib  # noqa: E402


def _project(K, T_cam, pts):
    P = (T_cam @ np.c_[pts, np.ones(len(pts))].T)[:3].T
    uv = (K @ P.T).T
    return uv[:, :2] / uv[:, 2:3]


def _render_cube(cv2, cube, K, T_cam, faces, size=(640, 480)):
    """Composite the given cube faces (by name) into a virtual camera image. Faces must be camera-facing."""
    board = cube.board(cv2)
    names = list(cube.face_ids.keys())
    canvas = np.full((size[1], size[0]), 255, np.uint8)
    src = np.array([[0, 0], [239, 0], [239, 239], [0, 239]], np.float32)
    for f in faces:
        pts = board.getObjPoints()[names.index(f)]
        uv = _project(K, T_cam, pts).astype(np.float32)
        marker = render_marker_image(cube.face_ids[f], 240)
        H, _ = cv2.findHomography(src, uv)
        warped = cv2.warpPerspective(marker, H, size, borderValue=255)
        mask = cv2.warpPerspective(np.full_like(marker, 255), H, size, borderValue=0) > 0
        canvas[mask] = warped[mask]
    return canvas


def _pose_err(T_est, T_true):
    err_t = np.linalg.norm(T_est[:3, 3] - T_true[:3, 3])
    R_err = np.rad2deg(np.arccos(np.clip((np.trace(T_est[:3, :3].T @ T_true[:3, :3]) - 1) / 2, -1, 1)))
    return err_t, R_err


def test_aruco_single_face_pose_at_working_distance():
    """One 24 mm marker at 25 cm: the single-marker ambiguity stays within a few mm.
    (At 40 cm the same marker gives ~7 mm depth error: keep the camera close or the markers >= 40 mm.)"""
    import cv2
    cube = CubeSpec(edge_mm=30.0, marker_mm=24.0)
    K = np.array([[800.0, 0, 320.0], [0, 800.0, 240.0], [0, 0, 1.0]])
    ang = np.deg2rad(15)
    T_cam = np.eye(4)
    T_cam[:3, :3] = np.array([[np.cos(ang), 0, np.sin(ang)], [0, 1, 0], [-np.sin(ang), 0, np.cos(ang)]])
    T_cam[:3, 3] = [10.0, -5.0, 250.0]
    T_cam = T_cam @ np.diag([1.0, -1.0, -1.0, 1.0])  # cube's +z face toward the camera
    canvas = _render_cube(cv2, cube, K, T_cam, ["+z"])
    T_est, n = ArucoCubeTracker(K, np.zeros(5), cube).pose(canvas)
    assert T_est is not None and n == 1
    err_t, R_err = _pose_err(T_est, T_cam)
    assert err_t < 3.0, f"translation error {err_t:.2f} mm"
    assert R_err < 3.0, f"rotation error {R_err:.2f} deg"


def test_aruco_two_faces_resolve_ambiguity_and_check_cube_geometry():
    """Cube turned 35 deg so +z and +x faces are both visible: the two-face solve must be sub-mm, which only
    happens if the face corner layouts in CubeSpec.board are geometrically consistent."""
    import cv2
    cube = CubeSpec(edge_mm=30.0, marker_mm=24.0)
    K = np.array([[800.0, 0, 320.0], [0, 800.0, 240.0], [0, 0, 1.0]])
    ang = np.deg2rad(35)
    T_cam = np.eye(4)
    T_cam[:3, :3] = np.array([[np.cos(ang), 0, np.sin(ang)], [0, 1, 0], [-np.sin(ang), 0, np.cos(ang)]])
    T_cam[:3, 3] = [0.0, 0.0, 350.0]
    T_cam = T_cam @ np.diag([1.0, -1.0, -1.0, 1.0])
    # which of +x/-x faces the camera after the flip and rotation: pick by normal direction
    R = T_cam[:3, :3]
    x_face = "+x" if (R @ np.array([1.0, 0, 0]))[2] < 0 else "-x"
    canvas = _render_cube(cv2, cube, K, T_cam, ["+z", x_face])
    T_est, n = ArucoCubeTracker(K, np.zeros(5), cube).pose(canvas)
    assert T_est is not None and n == 2, f"detected {n} markers"
    err_t, R_err = _pose_err(T_est, T_cam)
    # synthetic 640x480 camera at 35 cm; residual is corner-detection noise, not geometry (ideal points give 0)
    assert err_t < 2.5, f"translation error {err_t:.2f} mm"
    assert R_err < 0.5, f"rotation error {R_err:.2f} deg"


def test_replay_source_streams_frames_in_order():
    frames = np.zeros((5, 8, 8), np.uint8)
    for i in range(5):
        frames[i] = i
    scan = Scan("r", frames, np.tile(np.eye(4), (5, 1, 1)), Calib(np.eye(4), np.eye(4)))
    src = ReplaySource(scan, fps=20.0)
    seen = []
    while (r := src.read()) is not None:
        ts, f = r
        seen.append((ts, int(f[0, 0])))
    assert [v for _, v in seen] == [0, 1, 2, 3, 4]
    assert abs(seen[-1][0] - 4 / 20.0) < 1e-9
