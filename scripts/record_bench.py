"""Record a bench take: ultrasound frames from the capture card and cube poses from the webcam, on one clock.

Usage:
  python scripts/record_bench.py --us-device 1 --cam-device 0 --camera outputs/camera.json \
      --screen outputs/screen.json --marker-mm 35 --out data/bench_2026-10-18 --name sweep

Keys in the preview window: R = start / stop a take (each take gets its own numbered folder), Q = quit.
Devices are OpenCV indices (0, 1, ...) or video file paths for a dry run without hardware.
Each take folder holds frames.h5 (cropped ultrasound frames + timestamps), poses.npz (cube poses + timestamps),
cam.avi (raw webcam video, so tracking can be redone later), meta.json. Format: src/uscov/bench.py.
"""
import argparse
import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import cv2

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.live import ArucoCubeTracker, CubeSpec  # noqa: E402
from uscov.bench import RecordingWriter  # noqa: E402


def device_arg(s):
    return int(s) if s.isdigit() else s


class Grabber(threading.Thread):
    """Reads one capture device as fast as it delivers; calls `on_frame(t, bgr)` for every frame."""

    def __init__(self, device, on_frame, t0, label, pace_files=True):
        super().__init__(daemon=True)
        self.cap = cv2.VideoCapture(device)
        if not self.cap.isOpened():
            raise RuntimeError(f"could not open {label} device {device}")
        self.is_file = isinstance(device, str)
        self.pace = (1.0 / (self.cap.get(cv2.CAP_PROP_FPS) or 30.0)) if (self.is_file and pace_files) else 0.0
        self.on_frame, self.t0, self.label = on_frame, t0, label
        self.stop_flag = False
        self.count = 0
        self.ended = False

    def run(self):
        while not self.stop_flag:
            ok, img = self.cap.read()
            if not ok:
                self.ended = True
                break
            t = time.perf_counter() - self.t0
            self.count += 1
            self.on_frame(t, img)
            if self.pace:
                time.sleep(self.pace)
        self.cap.release()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--us-device", required=True, help="capture card index or video file")
    ap.add_argument("--cam-device", required=True, help="webcam index or video file")
    ap.add_argument("--camera", required=True, help="camera.json from calibrate_camera.py")
    ap.add_argument("--screen", default=None, help="screen.json from pick_crop.py (crop + mm per pixel)")
    ap.add_argument("--marker-mm", type=float, default=35.0)
    ap.add_argument("--edge-mm", type=float, default=None)
    ap.add_argument("--out", required=True, help="session folder, e.g. data/bench_2026-10-18")
    ap.add_argument("--name", default="take")
    ap.add_argument("--notes", default="")
    ap.add_argument("--no-cam-video", action="store_true", help="skip cam.avi (saves disk, loses re-tracking)")
    a = ap.parse_args()

    cam = json.load(open(a.camera))
    K, dist = np.array(cam["K"]), np.array(cam["dist"])
    cube = CubeSpec(edge_mm=a.edge_mm or a.marker_mm + 8, marker_mm=a.marker_mm)
    tracker = ArucoCubeTracker(K, dist, cube)
    screen = json.load(open(a.screen)) if a.screen else {}
    crop = tuple(screen["crop"]) if screen.get("crop") else None

    t0 = time.perf_counter()
    state = dict(rec=None, vw=None, take=0, lock=threading.Lock(), us=None, cam=None, tracked=0, cam_frames=0,
                 rec_frames=0, rec_poses=0, rec_tracked=0)

    def on_us(t, bgr):
        g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        if crop:
            r0, r1, c0, c1 = crop
            g = g[r0:r1, c0:c1]
        state["us"] = g
        with state["lock"]:
            if state["rec"] is not None:
                state["rec"].add_frame(t, g)
                state["rec_frames"] += 1

    def on_cam(t, bgr):
        g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        T, n = tracker.pose(g)
        state["cam_frames"] += 1
        if T is not None:
            state["tracked"] += 1
            rvec, _ = cv2.Rodrigues(T[:3, :3])
            cv2.drawFrameAxes(bgr, K, dist, rvec, T[:3, 3], a.marker_mm)
        state["cam"] = bgr
        with state["lock"]:
            if state["rec"] is not None:
                state["rec"].add_pose(t, T, n)
                state["rec_poses"] += 1
                state["rec_tracked"] += int(T is not None)
                if state["vw"] is not None:
                    state["vw"].write(bgr)
                    state["rec"].add_cam_time(t)

    us = Grabber(device_arg(a.us_device), on_us, t0, "ultrasound")
    cm = Grabber(device_arg(a.cam_device), on_cam, t0, "webcam")
    us.start(); cm.start()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    print("R = start/stop take, Q = quit")

    def start_take():
        if state["us"] is None or state["cam"] is None:
            print("no frames from both devices yet; wait a moment")
            return
        state["take"] += 1
        folder = out / f"{a.name}_{state['take']:02d}"
        rec = RecordingWriter(folder, state["us"].shape)
        vw = None
        if not a.no_cam_video:
            h, w = state["cam"].shape[:2]
            vw = cv2.VideoWriter(str(folder / "cam.avi"), cv2.VideoWriter_fourcc(*"MJPG"), 30, (w, h))
        with state["lock"]:
            state.update(rec=rec, vw=vw, rec_frames=0, rec_poses=0, rec_tracked=0)
        state["t_take"] = time.perf_counter()
        print(f"recording {folder}")

    def stop_take():
        with state["lock"]:
            rec, vw = state["rec"], state["vw"]
            state.update(rec=None, vw=None)
        if vw is not None:
            vw.release()
        meta = dict(started=datetime.now().isoformat(timespec="seconds"), us_device=a.us_device,
                    cam_device=a.cam_device, camera_json=a.camera, screen_json=a.screen, crop=crop,
                    mm_per_px=screen.get("mm_per_px"), marker_mm=a.marker_mm, edge_mm=cube.edge_mm,
                    notes=a.notes, cam_video=not a.no_cam_video)
        folder = rec.close(meta)
        print(f"saved {folder}: {rec.n_frames} frames, {len(rec.pose_t)} poses "
              f"({rec.pose_t and state['rec_tracked'] / max(len(rec.pose_t), 1):.0%} tracked)")

    try:
        while True:
            if us.ended and cm.ended:
                break
            panels = []
            if state["us"] is not None:
                u = cv2.cvtColor(state["us"], cv2.COLOR_GRAY2BGR)
                panels.append(cv2.resize(u, (int(360 * u.shape[1] / u.shape[0]), 360)))
            if state["cam"] is not None:
                c = state["cam"]
                panels.append(cv2.resize(c, (int(360 * c.shape[1] / c.shape[0]), 360)))
            if not panels:
                time.sleep(0.05)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                continue
            vis = np.hstack(panels)
            rec_on = state["rec"] is not None
            tf = state["tracked"] / max(state["cam_frames"], 1)
            line = f"cube seen {tf:.0%}   us {us.count} frames   cam {cm.count} frames"
            cv2.putText(vis, line, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            if rec_on:
                el = time.perf_counter() - state["t_take"]
                cv2.circle(vis, (vis.shape[1] - 30, 25), 10, (0, 0, 255), -1)
                cv2.putText(vis, f"REC take {state['take']:02d}  {el:5.1f} s  {state['rec_frames']} fr "
                                 f"{state['rec_tracked']}/{state['rec_poses']} poses",
                            (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.imshow("record_bench", vis)
            k = cv2.waitKey(30) & 0xFF
            if k == ord("r"):
                stop_take() if rec_on else start_take()
            elif k == ord("q"):
                break
    finally:
        if state["rec"] is not None:
            stop_take()
        us.stop_flag = cm.stop_flag = True
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
