"""Known-distance accuracy from a slide take: the measured replacement for the simulated tracker row.

Record a take (record_bench.py) in which the probe, with the cube on it, is slid along a ruler or rail and held
still for about a second at each mark (for example 0, 50, 0, 100, 0, 50, 0, 100 mm). Then:
    python scripts/known_distance.py data/bench_2026-10-18/slide_01 --expected 50,50,100,100,50,50,100,100
--expected lists the distance of each move in order; one value applies to every move; omit it to just print the
measured distances. Writes a CSV next to --out.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.bench import load_recording, detect_stops, stop_distances, known_distance_rows  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording")
    ap.add_argument("--expected", default=None, help="comma list of expected move lengths in mm")
    ap.add_argument("--speed-thresh", type=float, default=4.0, help="mm/s below which the probe counts as still")
    ap.add_argument("--min-dwell", type=float, default=0.6, help="s a stop must last")
    ap.add_argument("--out", default="outputs/known_distance.csv")
    a = ap.parse_args()
    rec = load_recording(a.recording, into_memory=False)
    stops = detect_stops(rec.pose_t, rec.T, a.speed_thresh, a.min_dwell)
    print(f"{len(stops)} stops found (cube tracked {rec.tracked_fraction:.0%} of the time)")
    for i, s in enumerate(stops):
        print(f"  stop {i}: {s.t_start:6.2f}-{s.t_end:6.2f} s at ({s.centre[0]:7.1f}, {s.centre[1]:7.1f}, "
              f"{s.centre[2]:7.1f}) mm")
    if len(stops) < 2:
        sys.exit("need at least two stops; lower --speed-thresh or hold still longer")
    expected = [float(v) for v in a.expected.split(",")] if a.expected else None
    rows = known_distance_rows(stop_distances(stops), expected)
    for r in rows:
        line = f"  move {r['move']}: {r['measured_mm']:7.2f} mm"
        if r["expected_mm"] is not None:
            line += f"  expected {r['expected_mm']:6.1f}  error {r['error_mm']:+6.2f} mm"
        print(line)
    if expected:
        err = np.array([r["error_mm"] for r in rows])
        print(f"mean abs error {np.abs(err).mean():.2f} mm, worst {np.abs(err).max():.2f} mm, "
              f"bias {err.mean():+.2f} mm (target: about 2 mm or better)")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
