"""Camera intrinsics from chessboard images (webcam or a folder of photos). Saves K and distortion to JSON.

Live:   python scripts/calibrate_camera.py --device 0 --out outputs/camera.json
        (hold the printed chessboard at varied angles and distances; press SPACE to grab, Q to finish; ~15 views)
Folder: python scripts/calibrate_camera.py --images path/to/jpgs --out outputs/camera.json
"""
import argparse
import json
from pathlib import Path

import numpy as np
import cv2


def find_corners(gray, pattern):
    ok, corners = cv2.findChessboardCorners(gray, pattern, cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)
    if not ok:
        return None
    return cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-3))


def calibrate(grays, pattern, square_mm):
    objp = np.zeros((pattern[0] * pattern[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:pattern[0], 0:pattern[1]].T.reshape(-1, 2) * square_mm
    obj, img = [], []
    for g in grays:
        c = find_corners(g, pattern)
        if c is not None:
            obj.append(objp); img.append(c)
    if len(obj) < 5:
        raise RuntimeError(f"only {len(obj)} usable chessboard views; need at least 5 (aim for 15)")
    rms, K, dist, _, _ = cv2.calibrateCamera(obj, img, grays[0].shape[::-1], None, None)
    return rms, K, dist, len(obj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", type=int, default=None)
    ap.add_argument("--images", default=None)
    ap.add_argument("--board", default="9x6")
    ap.add_argument("--square-mm", type=float, default=25.0)
    ap.add_argument("--out", default="outputs/camera.json")
    a = ap.parse_args()
    pattern = tuple(int(v) for v in a.board.split("x"))
    grays = []
    if a.images:
        for p in sorted(Path(a.images).glob("*")):
            im = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
            if im is not None:
                grays.append(im)
    else:
        cap = cv2.VideoCapture(0 if a.device is None else a.device)
        print("SPACE = grab view, Q = finish")
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            c = find_corners(g, pattern)
            vis = frame.copy()
            if c is not None:
                cv2.drawChessboardCorners(vis, pattern, c, True)
            cv2.putText(vis, f"views: {len(grays)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("calibrate", vis)
            k = cv2.waitKey(1) & 0xFF
            if k == ord(" ") and c is not None:
                grays.append(g)
            elif k == ord("q"):
                break
        cap.release(); cv2.destroyAllWindows()
    rms, K, dist, n = calibrate(grays, pattern, a.square_mm)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"K": K.tolist(), "dist": dist.ravel().tolist(), "rms_px": rms, "views": n,
               "image_size": list(grays[0].shape[::-1])}, open(a.out, "w"), indent=2)
    print(f"calibrated from {n} views, reprojection RMS {rms:.3f} px (good: < 0.5) -> {a.out}")


if __name__ == "__main__":
    main()
