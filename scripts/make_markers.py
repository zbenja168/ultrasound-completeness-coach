"""Printable sheet: six ArUco markers for the cube faces plus a chessboard for camera calibration.

Prints at exact physical size. Print at 100% / "actual size" (no fit-to-page), then measure one marker
with a ruler; if it is not the stated size, pass the measured value to the tracker instead.

Usage: python scripts/make_markers.py --marker-mm 35 --out outputs/print/markers_35mm.pdf
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.live import render_marker_image, CubeSpec  # noqa: E402

MM = 1 / 25.4  # inches per mm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--marker-mm", type=float, default=35.0)
    ap.add_argument("--square-mm", type=float, default=25.0, help="chessboard square size")
    ap.add_argument("--board", default="9x6", help="inner corners of the chessboard, cols x rows")
    ap.add_argument("--paper", default="letter", choices=["letter", "a4"])
    ap.add_argument("--out", default="outputs/print/markers.pdf")
    a = ap.parse_args()
    W, H = (215.9, 279.4) if a.paper == "letter" else (210.0, 297.0)
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    cube = CubeSpec(edge_mm=a.marker_mm + 8, marker_mm=a.marker_mm)
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(out) as pdf:
        # page 1: markers
        fig = plt.figure(figsize=(W * MM, H * MM))
        fig.text(0.5, 1 - 12 / H, f"Cube markers  {cube.dictionary}  marker {a.marker_mm:g} mm  "
                 f"(cube edge >= {cube.edge_mm:g} mm)", ha="center", fontsize=9)
        fig.text(0.5, 1 - 17 / H, "Print at 100% / actual size. Measure one black square edge to check.",
                 ha="center", fontsize=7)
        m = a.marker_mm
        cols, rows = 2, 3
        gx = (W - cols * m) / (cols + 1)
        gy = (H - 30 - rows * m) / (rows + 1)
        for k, (face, mid) in enumerate(cube.face_ids.items()):
            c, r = k % cols, k // cols
            x0 = gx + c * (m + gx)
            y0 = H - 30 - gy - r * (m + gy) - m
            ax = fig.add_axes([x0 / W, y0 / H, m / W, m / H])
            ax.imshow(render_marker_image(mid, 400, cube.dictionary), cmap="gray", interpolation="nearest")
            ax.axis("off")
            fig.text((x0 + m / 2) / W, (y0 - 4) / H, f"id {mid}  face {face}", ha="center", fontsize=7)
        pdf.savefig(fig); plt.close(fig)
        # page 2: chessboard
        cx, cy = (int(v) for v in a.board.split("x"))
        sq = a.square_mm
        bw, bh = (cx + 1) * sq, (cy + 1) * sq
        board = np.indices((cy + 1, cx + 1)).sum(axis=0) % 2
        fig = plt.figure(figsize=(W * MM, H * MM))
        ax = fig.add_axes([((W - bw) / 2) / W, ((H - bh) / 2) / H, bw / W, bh / H])
        ax.imshow(board, cmap="gray", interpolation="nearest"); ax.axis("off")
        fig.text(0.5, 1 - 12 / H, f"Camera calibration chessboard  {cx}x{cy} inner corners  square {sq:g} mm",
                 ha="center", fontsize=9)
        fig.text(0.5, 1 - 17 / H, "Tape flat to a rigid board. Print at 100%.", ha="center", fontsize=7)
        pdf.savefig(fig); plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    main()
