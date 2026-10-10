"""Live marker-cube tracking test with a webcam: shows the pose and measures jitter while the cube is held still.

This is the at-home test for the engineer: it turns the simulated 'marker + phone' tracker in the Stage 0
results into a measured one. Hold the cube still on a table for ~10 s, press M to measure, Q to quit.

Usage: python scripts/track_cube.py --camera outputs/camera.json --marker-mm 35 --device 0
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.live import ArucoCubeTracker, CubeSpec  # noqa: E402
from uscov.noise import smooth_poses  # noqa: E402


def jitter_stats(poses):
    P = np.array(poses)
    t = P[:, :3, 3]
    raw = float(np.sqrt(((t - t.mean(axis=0)) ** 2).sum(axis=1).mean()))
    s = smooth_poses(P, 9)[:, :3, 3] if len(P) >= 9 else t
    sm = float(np.sqrt(((s - s.mean(axis=0)) ** 2).sum(axis=1).mean()))
    return raw, sm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", required=True)
    ap.add_argument("--marker-mm", type=float, default=35.0)
    ap.add_argument("--edge-mm", type=float, default=None, help="cube edge; default marker + 8")
    ap.add_argument("--device", type=int, default=0)
    ap.add_argument("--log", default="outputs/track_log.json")
    a = ap.parse_args()
    cam = json.load(open(a.camera))
    K, dist = np.array(cam["K"]), np.array(cam["dist"])
    cube = CubeSpec(edge_mm=a.edge_mm or a.marker_mm + 8, marker_mm=a.marker_mm)
    tr = ArucoCubeTracker(K, dist, cube)
    cap = cv2.VideoCapture(a.device)
    window, measuring, results = [], False, []
    seen = total = 0
    print("M = measure jitter for 10 s (hold the cube still), Q = quit")
    t_meas = 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        total += 1
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        T, n = tr.pose(g)
        vis = frame.copy()
        if T is not None:
            seen += 1
            rvec, _ = cv2.Rodrigues(T[:3, :3])
            cv2.drawFrameAxes(vis, K, dist, rvec, T[:3, 3], a.marker_mm)
            cv2.putText(vis, f"{n} faces  xyz {T[0,3]:.0f} {T[1,3]:.0f} {T[2,3]:.0f} mm", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if measuring:
                window.append(T)
        else:
            cv2.putText(vis, "cube not seen", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if measuring and time.time() - t_meas > 10:
            measuring = False
            if len(window) >= 20:
                raw, sm = jitter_stats(window)
                dist_mm = float(np.linalg.norm(np.array(window)[:, :3, 3].mean(axis=0)))
                results.append({"distance_mm": dist_mm, "frames": len(window), "jitter_raw_mm": raw,
                                "jitter_smoothed_mm": sm})
                print(f"distance {dist_mm:.0f} mm: jitter RMS raw {raw:.2f} mm, smoothed(9) {sm:.2f} mm "
                      f"over {len(window)} frames")
            else:
                print("too few tracked frames; is the cube visible?")
        cv2.putText(vis, f"visible {seen}/{total}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.imshow("cube", vis)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("m") and not measuring:
            measuring, window, t_meas = True, [], time.time()
            print("measuring... hold still")
        elif k == ord("q"):
            break
    cap.release(); cv2.destroyAllWindows()
    Path(a.log).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"visible_fraction": seen / max(total, 1), "measurements": results}, open(a.log, "w"), indent=2)
    print("wrote", a.log)


if __name__ == "__main__":
    main()
