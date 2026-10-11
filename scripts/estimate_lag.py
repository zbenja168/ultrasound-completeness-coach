"""Temporal alignment from a jiggle take: how much later the capture-card image arrives than the cube pose.

Record a take (record_bench.py) in which the probe is tapped or jiggled sharply five or six times over ~20 s
while touching the phantom, then:
    python scripts/estimate_lag.py data/bench_2026-10-18/jiggle_01 [--max-lag 1.0] [--plot outputs/lag.png]
Writes outputs/lag.json and stores lag_s in the take's meta.json; record_bench takes made afterwards can be paired
with --lag, and calibrate_pinhead / the engine read it from meta or lag.json.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.bench import load_recording, estimate_lag, frame_motion, pose_speed  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--max-lag", type=float, default=1.0)
    ap.add_argument("--out", default="outputs/lag.json")
    ap.add_argument("--plot", default=None)
    ap.add_argument("--no-meta", action="store_true", help="do not write lag_s into the take's meta.json")
    a = ap.parse_args()
    rec = load_recording(a.recording)
    sp = pose_speed(rec.pose_t, rec.T)
    fm = frame_motion(rec.frames)
    lag, corr = estimate_lag(rec.pose_t, sp, rec.frame_t, fm, max_lag_s=a.max_lag)
    verdict = "good" if corr > 0.5 else ("weak, jiggle harder / longer" if corr > 0.3 else "no match, not usable")
    print(f"image lags cube pose by {lag*1000:.0f} ms (peak correlation {corr:.2f}: {verdict}); "
          f"frames {rec.fps:.1f} fps, cube tracked {rec.tracked_fraction:.0%}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"lag_s": lag, "peak_corr": corr, "recording": str(rec.folder)}, open(a.out, "w"), indent=2)
    if not a.no_meta:
        rec.meta["lag_s"] = lag
        rec.meta["lag_peak_corr"] = corr
        json.dump(rec.meta, open(rec.folder / "meta.json", "w"), indent=2, default=str)
    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
        ok = np.isfinite(sp)
        ax[0].plot(rec.pose_t[ok], sp[ok], lw=0.8); ax[0].set_ylabel("probe speed (mm/s)")
        ax[1].plot(rec.frame_t - lag, fm, lw=0.8, color="C1"); ax[1].set_ylabel("image motion (shifted)")
        ax[1].set_xlabel("time (s)"); fig.suptitle(f"lag {lag*1000:.0f} ms, corr {corr:.2f}")
        fig.tight_layout(); fig.savefig(a.plot, dpi=120)
        print("wrote", a.plot)


if __name__ == "__main__":
    main()
