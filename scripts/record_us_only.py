"""Record the ultrasound screen only (no webcam), for sessions where the probe camera is a phone
filming the marker cube separately.

  python scripts/record_us_only.py --us-device 1 --out data/bench_2026-10-22 --name full

Writes <out>/<name>_NN/us.avi (full capture-card frames, MJPG), us_times.csv (frame index, seconds
since start, wall clock) and meta.json. Press Q in the preview window to stop a take.

Sync with the phone video: at the start of every take, tap the probe sharply on the phantom three
times while both are recording. The taps show as jolts in the ultrasound image and as cube motion
in the phone video, and scripts/estimate_lag.py-style cross-correlation lines them up afterwards.
pick_crop.py accepts us.avi as its --device, so the screen crop can be chosen after the session.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime

import cv2


def next_take_dir(out: str, name: str) -> str:
    os.makedirs(out, exist_ok=True)
    n = 1
    while os.path.exists(os.path.join(out, f"{name}_{n:02d}")):
        n += 1
    d = os.path.join(out, f"{name}_{n:02d}")
    os.makedirs(d)
    return d


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--us-device", required=True, help="capture card index (e.g. 1) or a video file for a dry run")
    ap.add_argument("--out", required=True, help="session folder, e.g. data/bench_2026-10-22")
    ap.add_argument("--name", default="take")
    ap.add_argument("--notes", default="")
    ap.add_argument("--max-seconds", type=float, default=0, help="stop automatically after this many seconds (0 = until Q)")
    ap.add_argument("--no-preview", action="store_true")
    a = ap.parse_args()

    src = int(a.us_device) if str(a.us_device).isdigit() else a.us_device
    cap = cv2.VideoCapture(src, cv2.CAP_DSHOW) if isinstance(src, int) and os.name == "nt" else cv2.VideoCapture(src)
    if not cap.isOpened():
        raise SystemExit(f"could not open ultrasound source {a.us_device!r}")
    if isinstance(src, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    ok, frame = cap.read()
    if not ok:
        raise SystemExit("source opened but gave no frame; check the HDMI cable and that the cart is not frozen on a menu")
    h, w = frame.shape[:2]
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    take = next_take_dir(a.out, a.name)
    writer = cv2.VideoWriter(os.path.join(take, "us.avi"), cv2.VideoWriter_fourcc(*"MJPG"), src_fps, (w, h))
    times_f = open(os.path.join(take, "us_times.csv"), "w", newline="")
    times = csv.writer(times_f)
    times.writerow(["frame", "t_s", "wall_clock"])

    print(f"recording {w}x{h} @ {src_fps:.0f} fps -> {take}")
    print("TAP the probe sharply on the phantom 3 times now (sync with the phone video). Q stops the take.")
    t0 = time.perf_counter()
    n = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("source ended")
                break
            t = time.perf_counter() - t0
            writer.write(frame)
            times.writerow([n, f"{t:.4f}", datetime.now().isoformat(timespec="milliseconds")])
            n += 1
            if not a.no_preview:
                small = cv2.resize(frame, (w // 2, h // 2))
                cv2.putText(small, f"{a.name}  {t:6.1f}s  {n} frames  Q=stop", (10, 24),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("ultrasound (recording)", small)
                if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                    break
            if a.max_seconds and t >= a.max_seconds:
                break
    finally:
        dur = time.perf_counter() - t0
        writer.release()
        times_f.close()
        cap.release()
        cv2.destroyAllWindows()
        meta = {
            "take": os.path.basename(take), "name": a.name, "notes": a.notes,
            "us_device": a.us_device, "width": w, "height": h, "nominal_fps": src_fps,
            "frames": n, "duration_s": round(dur, 3), "measured_fps": round(n / dur, 2) if dur > 0 else None,
            "started": datetime.fromtimestamp(time.time() - dur).isoformat(timespec="seconds"),
            "probe_camera": "phone video recorded separately; sync by the three taps at the start",
        }
        json.dump(meta, open(os.path.join(take, "meta.json"), "w"), indent=2)
        print(f"saved {n} frames, {dur:.1f} s, {meta['measured_fps']} fps -> {take}")


if __name__ == "__main__":
    main()
