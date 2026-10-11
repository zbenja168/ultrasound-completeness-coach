"""Screen setup: pick the ultrasound image region and the depth-ruler scale on a frozen capture-card frame.

    python scripts/pick_crop.py --device 1 --ruler-mm 10 --out outputs/screen.json
    python scripts/pick_crop.py --image outputs/screen_frame.png --ruler-mm 10

Live: SPACE freezes the current frame (freeze the cart first for a still picture), Q aborts.
Then click, in order: (1) top-left and (2) bottom-right corners of the ultrasound image, (3) and (4) two ticks of
the on-screen depth ruler that are --ruler-mm apart (the big ticks are usually 10 mm or 1 cm; check the cart).
U undoes a click, ENTER or S saves, Q aborts. Writes screen.json (crop rows/cols + mm per pixel) that
record_bench.py and the engine use, plus screen_frame.png and screen_preview.png next to it.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.bench import mm_per_px_from_ruler  # noqa: E402

LABELS = ["image top-left", "image bottom-right", "ruler tick A", "ruler tick B"]


def grab(device):
    cap = cv2.VideoCapture(int(device) if str(device).isdigit() else device)
    if not cap.isOpened():
        sys.exit(f"could not open device {device}")
    print("SPACE = freeze this frame, Q = abort")
    frame = None
    while True:
        ok, img = cap.read()
        if not ok:
            break
        cv2.imshow("live (SPACE to freeze)", img)
        k = cv2.waitKey(30) & 0xFF
        if k == ord(" "):
            frame = img
            break
        if k == ord("q"):
            break
    cap.release(); cv2.destroyAllWindows()
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=None)
    ap.add_argument("--image", default=None)
    ap.add_argument("--ruler-mm", type=float, default=10.0, help="distance between the two clicked ruler ticks")
    ap.add_argument("--out", default="outputs/screen.json")
    a = ap.parse_args()
    if a.image:
        frame = cv2.imread(a.image)
    elif a.device is not None:
        frame = grab(a.device)
    else:
        sys.exit("pass --device or --image")
    if frame is None:
        sys.exit("no frame")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out.with_name("screen_frame.png")), frame)

    clicks = []
    win = "pick_crop"
    cv2.namedWindow(win)

    def on_mouse(ev, x, y, flags, _):
        if ev == cv2.EVENT_LBUTTONDOWN and len(clicks) < 4:
            clicks.append((x, y))
            print(f"{LABELS[len(clicks) - 1]}: ({x}, {y})")

    cv2.setMouseCallback(win, on_mouse)
    saved = False
    while True:
        vis = frame.copy()
        if len(clicks) >= 2:
            cv2.rectangle(vis, clicks[0], clicks[1], (0, 255, 0), 2)
        if len(clicks) == 4:
            cv2.line(vis, clicks[2], clicks[3], (0, 255, 255), 2)
        for c in clicks:
            cv2.circle(vis, c, 5, (0, 0, 255), -1)
        msg = f"click {LABELS[len(clicks)]}" if len(clicks) < 4 else "ENTER/S = save, U = undo, Q = abort"
        cv2.putText(vis, msg, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow(win, vis)
        k = cv2.waitKey(30) & 0xFF
        if k == ord("u") and clicks:
            clicks.pop()
        elif k in (13, ord("s")) and len(clicks) == 4:
            saved = True
            break
        elif k == ord("q"):
            break
    cv2.destroyAllWindows()
    if not saved:
        sys.exit("aborted, nothing written")
    (x0, y0), (x1, y1) = clicks[0], clicks[1]
    r0, r1, c0, c1 = min(y0, y1), max(y0, y1), min(x0, x1), max(x0, x1)
    mm = mm_per_px_from_ruler(clicks[2], clicks[3], a.ruler_mm)
    depth_mm = (r1 - r0) * mm
    d = {"crop": [r0, r1, c0, c1], "mm_per_px": mm, "ruler_px": float(np.hypot(clicks[3][0] - clicks[2][0],
                                                                                 clicks[3][1] - clicks[2][1])),
         "ruler_mm": a.ruler_mm, "image_size": [frame.shape[1], frame.shape[0]], "crop_size": [c1 - c0, r1 - r0],
         "image_depth_mm": depth_mm, "source": a.image or f"device {a.device}"}
    json.dump(d, open(out, "w"), indent=2)
    cv2.imwrite(str(out.with_name("screen_preview.png")), vis)
    print(f"crop rows {r0}:{r1} cols {c0}:{c1} ({c1 - c0}x{r1 - r0} px), {mm:.4f} mm/px, "
          f"image depth {depth_mm:.0f} mm -> {out}")


if __name__ == "__main__":
    main()
