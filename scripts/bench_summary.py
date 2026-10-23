"""Table of what each bench take delivered: tracking rate, clock offset and its confidence, frames, duration.

    python scripts/bench_summary.py data/bench_2026-10-22/us [--md docs/figures/bench_2026-10-22/takes.md]
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_us_dir")
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    rows = []
    for d in sorted(Path(a.session_us_dir).iterdir()):
        m = d / "meta.json"
        if not m.exists():
            continue
        j = json.load(open(m))
        rows.append(dict(take=d.name, started=j.get("started", "")[11:19], frames=j.get("frames"),
                         dur=j.get("duration_s"), phone=Path(j.get("phone_video", "")).name,
                         tracked=j.get("phone_tracked_fraction"), offset=j.get("clock_offset_s"),
                         corr=j.get("clock_offset_corr"), second=j.get("clock_offset_second_peak"),
                         pred=j.get("clock_offset_predicted")))
    hdr = "| take | laptop start | US frames | s | phone clip | top face tracked | clock offset s | corr (next) | predicted |"
    sep = "|---|---|---|---|---|---|---|---|---|"
    lines = [hdr, sep]
    for r in rows:
        f = lambda v, fmt: ("" if v is None else fmt.format(v))
        lines.append(f"| {r['take']} | {r['started']} | {r['frames']} | {f(r['dur'], '{:.1f}')} | {r['phone'] or 'none'} | "
                     f"{f(r['tracked'], '{:.0%}')} | {f(r['offset'], '{:+.2f}')} | {f(r['corr'], '{:.2f}')} ({f(r['second'], '{:.2f}')}) | "
                     f"{f(r['pred'], '{:+.1f}')} |")
    text = "\n".join(lines)
    print(text)
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
