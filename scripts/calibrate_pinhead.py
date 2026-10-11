"""Image->cube spatial calibration from a recorded pinhead take (record_bench.py with the probe over a pin in water).

Usage: python scripts/calibrate_pinhead.py data/bench_2026-10-18/pinhead_01 --screen outputs/screen.json \
           --out outputs/image_to_tool.json

In the window: click the pinhead's bright dot to accept the current frame (the nearest cube pose is paired
automatically; frames without a pose are refused). Keys: N / P next / previous frame, F / B jump 10 frames,
U undo the last click, S solve and print the fit so far, Q solve, save and quit.
Collect 10 to 15 clicks with the probe rotated about the pin on two axes (tilt and rock, 30 degrees or more);
poses that only translate leave the fit ambiguous. --points file.json reloads earlier clicks; --no-ui solves
from them without a window.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.bench import (load_recording, pair_poses_to_frames, pinhead_calibrate, pinhead_pixel,  # noqa: E402
                         save_calib_json)


def solve(points, P, mm_per_px):
    idx = [p["frame"] for p in points]
    pix = np.array([[p["col"], p["row"]] for p in points], float)
    res = pinhead_calibrate(P[idx], pix, mm_per_px)
    print(f"pinhead fit from {res.n_poses} poses: RMS {res.rms_mm:.2f} mm, worst {res.per_pose_mm.max():.2f} mm "
          f"(good: RMS under 1.5 mm)")
    for p, e, Tw in zip(points, res.per_pose_mm, P[idx]):
        pred = pinhead_pixel(Tw, res.image_to_tool, mm_per_px, res.pin_world)
        flag = "  <-- check this click" if e > 2 * max(res.rms_mm, 0.5) else ""
        print(f"  frame {p['frame']:5d}: residual {e:.2f} mm, click ({p['col']:.0f},{p['row']:.0f}) "
              f"predicted ({pred[0]:.0f},{pred[1]:.0f}){flag}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--screen", default=None, help="screen.json with mm_per_px; else taken from the take's meta")
    ap.add_argument("--mm-per-px", type=float, default=None)
    ap.add_argument("--lag", type=float, default=None, help="image lag in s; default meta lag_s or 0")
    ap.add_argument("--points", default=None, help="json of earlier clicks to reload")
    ap.add_argument("--no-ui", action="store_true")
    ap.add_argument("--out", default="outputs/image_to_tool.json")
    a = ap.parse_args()

    rec = load_recording(a.recording)
    mm = a.mm_per_px or (json.load(open(a.screen))["mm_per_px"] if a.screen else rec.meta.get("mm_per_px"))
    if not mm:
        sys.exit("mm per pixel unknown: pass --screen or --mm-per-px")
    lag = a.lag if a.lag is not None else float(rec.meta.get("lag_s", 0.0))
    P = pair_poses_to_frames(rec.frame_t, rec.pose_t, rec.T, lag_s=lag)
    has_pose = ~np.isnan(P[:, 0, 0])
    print(f"{rec.n_frames} frames, {has_pose.mean():.0%} with a cube pose, lag {lag*1000:.0f} ms, "
          f"{mm:.4f} mm/px")
    points = json.load(open(a.points)) if a.points else []
    pts_path = Path(a.out).with_suffix(".points.json")

    if not a.no_ui:
        import cv2
        i = int(np.argmax(has_pose))
        win = "pinhead"
        cv2.namedWindow(win)
        state = {"i": i}

        def on_mouse(ev, x, y, flags, _):
            if ev == cv2.EVENT_LBUTTONDOWN:
                k = state["i"]
                if not has_pose[k]:
                    print("no cube pose for this frame; pick another")
                    return
                points.append({"frame": int(k), "col": x + 1.0, "row": y + 1.0})   # 1-based as in data.py
                print(f"click {len(points)}: frame {k} at ({x + 1},{y + 1})")

        cv2.setMouseCallback(win, on_mouse)
        while True:
            k = state["i"]
            vis = cv2.cvtColor(rec.frames[k], cv2.COLOR_GRAY2BGR)
            col = (0, 255, 0) if has_pose[k] else (0, 0, 255)
            cv2.putText(vis, f"frame {k}/{rec.n_frames - 1}  {'pose ok' if has_pose[k] else 'NO CUBE POSE'}  "
                             f"clicks {len(points)}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)
            for p in points:
                if p["frame"] == k:
                    cv2.circle(vis, (int(p["col"] - 1), int(p["row"] - 1)), 6, (0, 255, 255), 2)
            cv2.imshow(win, vis)
            key = cv2.waitKey(30) & 0xFF
            if key == ord("n"):
                state["i"] = min(k + 1, rec.n_frames - 1)
            elif key == ord("p"):
                state["i"] = max(k - 1, 0)
            elif key == ord("f"):
                state["i"] = min(k + 10, rec.n_frames - 1)
            elif key == ord("b"):
                state["i"] = max(k - 10, 0)
            elif key == ord("u") and points:
                print("undo", points.pop())
            elif key == ord("s") and len(points) >= 6:
                solve(points, P, mm)
            elif key == ord("q"):
                break
        cv2.destroyAllWindows()

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(points, open(pts_path, "w"), indent=1)
    print("clicks saved to", pts_path)
    if len(points) < 6:
        sys.exit(f"only {len(points)} clicks; need at least 6 (aim for 10 to 15), nothing solved")
    res = solve(points, P, mm)
    save_calib_json(a.out, res.calib(mm), pin_world=res.pin_world.tolist(), rms_mm=res.rms_mm, n_points=res.n_poses,
                    per_pose_mm=res.per_pose_mm.tolist(), lag_s=lag, recording=str(rec.folder))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
