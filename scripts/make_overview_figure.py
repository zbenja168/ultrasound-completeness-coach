"""One-page overview sketch of the completeness coach for emails and slides.

Usage: python scripts/make_overview_figure.py --out docs/figures/overview_sketch.png
"""
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Ellipse, Circle, FancyArrowPatch, Polygon

INK = "#1f2a37"
MUTED = "#5b6773"
GREEN = "#2e9e5b"
AMBER = "#e0a32a"
GREY = "#c9cfd6"
BLUE = "#2f6fb3"
PANEL = "#f6f7f9"


def box(ax, x, y, w, h, fc="white", ec=INK, lw=1.2, r=0.08, z=2):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(p)
    return p


def text(ax, x, y, s, size=9, color=INK, ha="left", va="center", weight="normal", z=5):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, zorder=z)


def arrow(ax, x0, y0, x1, y1, color=MUTED, lw=1.2, style="-|>", ls="-", z=4):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=10, color=color, lw=lw,
                                 linestyle=ls, zorder=z))


def panel(ax, x, title, w=3.45):
    box(ax, x, 0.75, w, 4.55, fc=PANEL, ec="#dde1e6", lw=1, r=0.12, z=1)
    text(ax, x + 0.15, 5.08, title, size=11, weight="bold")
    return x


def marker_cube(ax, cx, cy, s=0.22):
    # a cube with two visible faces, each carrying a square marker
    ax.add_patch(Rectangle((cx, cy), s, s, fc="white", ec=INK, lw=1, zorder=6))
    ax.add_patch(Polygon([(cx, cy + s), (cx + 0.08, cy + s + 0.08), (cx + s + 0.08, cy + s + 0.08), (cx + s, cy + s)],
                         fc="#e9ecef", ec=INK, lw=1, zorder=6))
    ax.add_patch(Polygon([(cx + s, cy), (cx + s + 0.08, cy + 0.08), (cx + s + 0.08, cy + s + 0.08), (cx + s, cy + s)],
                         fc="#d5d9de", ec=INK, lw=1, zorder=6))
    m = s * 0.6
    ax.add_patch(Rectangle((cx + (s - m) / 2, cy + (s - m) / 2), m, m, fc=INK, zorder=7))
    for i in range(3):
        for j in range(3):
            if (i + j) % 2 == 0:
                ax.add_patch(Rectangle((cx + (s - m) / 2 + i * m / 3, cy + (s - m) / 2 + j * m / 3), m / 3, m / 3,
                                       fc="white", zorder=8))


def draw_setup(ax, x0):
    panel(ax, x0, "1. Setup in the room")
    # cart (left column): screen, body, wheels, video-out port
    box(ax, x0 + 0.2, 3.9, 1.1, 0.7, fc="#e9ecef")
    text(ax, x0 + 0.75, 4.25, "US cart", size=8, ha="center")
    box(ax, x0 + 0.25, 2.5, 1.0, 1.4, fc="white")
    ax.add_patch(Circle((x0 + 0.42, 2.4), 0.06, fc=INK, zorder=3))
    ax.add_patch(Circle((x0 + 1.08, 2.4), 0.06, fc=INK, zorder=3))
    text(ax, x0 + 0.75, 2.6, "video out", size=6.5, color=MUTED, ha="center")
    # capture card and laptop under the cart
    arrow(ax, x0 + 0.75, 2.33, x0 + 0.75, 2.08)
    box(ax, x0 + 0.45, 1.75, 0.6, 0.32, fc="white", r=0.04)
    text(ax, x0 + 0.75, 1.91, "capture\ncard", size=6, ha="center")
    arrow(ax, x0 + 0.75, 1.73, x0 + 0.75, 1.52)
    box(ax, x0 + 0.35, 1.0, 0.8, 0.5, fc="white", r=0.04)
    box(ax, x0 + 0.25, 0.93, 1.0, 0.08, fc="#e9ecef", r=0.02)
    text(ax, x0 + 0.75, 1.25, "laptop", size=7, ha="center")
    # phantom (neck) and probe (right column)
    ax.add_patch(Ellipse((x0 + 2.5, 1.55), 1.6, 0.55, fc="#f3e3d3", ec="#c9a98a", lw=1, zorder=2))
    text(ax, x0 + 2.5, 1.1, "gel phantom (no patients)", size=7, color=MUTED, ha="center")
    box(ax, x0 + 2.35, 1.8, 0.3, 0.75, fc="#dfe3e8", r=0.05)
    text(ax, x0 + 2.25, 2.15, "probe", size=7.5, color=MUTED, ha="right")
    marker_cube(ax, x0 + 2.6, 2.4)
    text(ax, x0 + 2.95, 2.75, "marker cube\non the probe", size=7, color=MUTED)
    # camera on a tripod, looking down at the cube
    box(ax, x0 + 1.5, 4.3, 0.45, 0.3, fc="white", r=0.04)
    ax.add_patch(Circle((x0 + 1.95, 4.45), 0.09, fc="white", ec=INK, lw=1, zorder=3))
    ax.plot([x0 + 1.72, x0 + 1.72], [4.3, 3.95], color=INK, lw=1, zorder=3)
    text(ax, x0 + 1.35, 4.8, "webcam on tripod", size=7.5, color=MUTED)
    arrow(ax, x0 + 2.0, 4.35, x0 + 2.65, 2.72, color=BLUE, lw=1, style="-", ls="--")
    arrow(ax, x0 + 2.0, 4.35, x0 + 2.95, 2.72, color=BLUE, lw=1, style="-", ls="--")
    text(ax, x0 + 1.35, 3.45, "camera sees\nthe cube:\nprobe position", size=7, color=BLUE)


def thyroid(ax, cx, cy, s, fills):
    # fills: dict part -> colour. Right lobe is on the viewer's left (as on an image).
    lw = 1.1
    for side, px in (("R", -1), ("L", 1)):
        ex = cx + px * 0.55 * s
        ax.add_patch(Ellipse((ex, cy), 0.55 * s, 1.5 * s, fc="none", ec=INK, lw=lw, zorder=6))
        for half, y0 in (("upper", cy), ("lower", cy - 0.75 * s)):
            r = Rectangle((ex - 0.3 * s, y0), 0.6 * s, 0.75 * s, fc=fills[f"{side} {half}"], ec="none", zorder=5)
            ax.add_patch(r)
            r.set_clip_path(Ellipse((ex, cy), 0.55 * s, 1.5 * s, transform=ax.transData))
        ax.plot([ex - 0.28 * s, ex + 0.28 * s], [cy, cy], color=INK, lw=0.8, ls=":", zorder=7)
    ax.add_patch(Rectangle((cx - 0.3 * s, cy - 0.12 * s), 0.6 * s, 0.24 * s, fc=fills["isthmus"], ec=INK, lw=lw,
                           zorder=5))
    ax.add_patch(Circle((cx, cy - 0.35 * s), 0.22 * s, fc="none", ec=MUTED, lw=0.8, ls="--", zorder=4))


def draw_scan(ax, x0):
    panel(ax, x0, "2. While the student scans")
    fills = {"R upper": GREEN, "R lower": GREEN, "isthmus": GREEN, "L upper": AMBER, "L lower": GREY}
    cx, cy, s = x0 + 1.05, 3.55, 1.0
    thyroid(ax, cx, cy, s, fills)
    text(ax, cx, 4.65, "coverage map of the target (thyroid)", size=7.5, color=MUTED, ha="center")
    # probe footprint sweeping down the lobe that is already covered
    px = cx - 0.55 * s
    ax.add_patch(Rectangle((px - 0.18, 4.32), 0.36, 0.1, fc=BLUE, ec="none", zorder=7))
    arrow(ax, px, 4.3, px, 3.0, color=BLUE, lw=1.1, ls="--", z=8)
    text(ax, px + 0.22, 4.2, "sweep", size=6.8, color=BLUE)
    # legend to the right of the gland
    for i, (c, lab) in enumerate(((GREEN, "seen clearly"), (AMBER, "seen partly or\nthrough shadow"),
                                  (GREY, "not seen yet"))):
        yy = 4.2 - i * 0.42
        ax.add_patch(Rectangle((x0 + 2.2, yy - 0.09), 0.18, 0.18, fc=c, ec=INK, lw=0.6, zorder=6))
        text(ax, x0 + 2.45, yy, lab, size=6.8)
    text(ax, x0 + 0.2, 2.2, "Each image frame is placed in 3D using the\n"
                             "probe position from the camera. Image-based\n"
                             "tracking bridges moments when the camera\n"
                             "cannot see the cube.", size=7.5)
    text(ax, x0 + 0.2, 1.3, "The map only says where the probe has looked,\n"
                             "and how trustworthy each look was.", size=7.5, color=MUTED)


def draw_output(ax, x0):
    panel(ax, x0, "3. What student and instructor see")
    box(ax, x0 + 0.2, 2.95, 3.05, 1.85, fc="white")
    text(ax, x0 + 0.35, 4.6, "Completeness: 71%", size=10, weight="bold")
    text(ax, x0 + 0.35, 4.33, "Missing: left lobe, lower pole", size=8, color="#b3261e")
    rows = (("Right lobe, upper pole", 0.96, GREEN), ("Right lobe, lower pole", 0.91, GREEN),
            ("Isthmus", 0.88, GREEN), ("Left lobe, upper pole", 0.62, AMBER), ("Left lobe, lower pole", 0.18, GREY))
    for i, (lab, v, c) in enumerate(rows):
        y = 4.02 - i * 0.22
        text(ax, x0 + 0.35, y, lab, size=7)
        ax.add_patch(Rectangle((x0 + 1.95, y - 0.06), 0.95, 0.12, fc="#eceff2", ec="none", zorder=5))
        ax.add_patch(Rectangle((x0 + 1.95, y - 0.06), 0.95 * v, 0.12, fc=c, ec="none", zorder=6))
        text(ax, x0 + 2.95, y, f"{int(v*100)}%", size=6.5, color=MUTED)
    text(ax, x0 + 0.2, 2.7, "Standard views captured automatically:", size=7.5)
    for i, (lab, ok) in enumerate((("Transverse\nisthmus", True), ("Long. right\nlobe", True),
                                   ("Long. left\nlobe", False))):
        bx = x0 + 0.25 + i * 1.02
        ax.add_patch(Polygon([(bx + 0.15, 2.5), (bx + 0.75, 2.5), (bx + 0.9, 1.95), (bx, 1.95)],
                             fc="#2b2f36" if ok else "#eceff2", ec=INK, lw=0.8, zorder=5))
        if ok:
            ax.add_patch(Ellipse((bx + 0.45, 2.2), 0.3, 0.14, fc="#9aa3ad", ec="none", zorder=6))
        text(ax, bx + 0.45, 1.72, lab, size=6.3, ha="center", color=INK if ok else MUTED)
        text(ax, bx + 0.45, 1.44, "captured" if ok else "pending", size=6.3, ha="center",
             color=GREEN if ok else MUTED)
    text(ax, x0 + 0.2, 1.05, "Full sweep is archived so an instructor can\nreview it later.", size=7.5, color=MUTED)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/figures/overview_sketch.png")
    a = ap.parse_args()
    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=200)
    ax.set_xlim(0, 11); ax.set_ylim(0, 6.2); ax.axis("off")
    text(ax, 0.3, 5.85, "Ultrasound completeness coach", size=15, weight="bold")
    text(ax, 0.3, 5.5, "An education / QA tool that shows a novice which parts of the target organ they have not "
                       "imaged yet.", size=9.5, color=MUTED)
    draw_setup(ax, 0.3)
    draw_scan(ax, 3.9)
    draw_output(ax, 7.5)
    arrow(ax, 3.72, 3.0, 3.92, 3.0, color=INK, lw=1.5)
    arrow(ax, 7.32, 3.0, 7.52, 3.0, color=INK, lw=1.5)
    text(ax, 0.3, 0.4, "What it is not: no diagnosis, no detection of findings, no \"move the probe this way\" "
                       "instructions. Phantom testing first; any volunteer study goes through the IRB.",
         size=8, color=INK, weight="bold")
    text(ax, 0.3, 0.15, "Nothing on the machine is changed; the laptop only records its screen output. Tested so far "
                        "on a public tracked-ultrasound dataset, where the map matches the true coverage in over 90% "
                        "of the volume.", size=7.5, color=MUTED)
    fig.savefig(a.out, bbox_inches="tight", facecolor="white")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
