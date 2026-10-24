"""Printable sheet: six ArUco markers for the cube faces plus a chessboard for camera calibration.

Prints at exact physical size. Print at 100% / "actual size" (no fit-to-page), then measure one marker
with a ruler; if it is not the stated size, pass the measured value to the tracker instead.

Each marker is surrounded by a white quiet zone (default: one marker bit, at least 8 mm) and a thin grey cut
line outside it. Cut on the grey line and keep the white: the 2026-10-22 session showed that a marker cut flush
and glued to a dark cube is not detected wherever its black border meets the dark body. The cube should be
white (3D-printed or painted) with an edge of at least the face size printed on the sheet.

The chessboard is sized to fit the paper: a 9x6 board at 25 mm is 250 mm wide and overflows letter paper,
which clipped the 2026-10-22 print to 8x6 usable corners. The sheet states the size actually printed.

Usage: python scripts/make_markers.py --marker-mm 35 --out docs/print/markers_35mm.pdf [--png]
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
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marker-mm", type=float, default=35.0)
    ap.add_argument("--margin-mm", type=float, default=None,
                    help="white quiet zone around each marker; default max(8 mm, one marker bit)")
    ap.add_argument("--square-mm", type=float, default=25.0, help="chessboard square size (shrunk to fit the paper)")
    ap.add_argument("--board", default="9x6", help="inner corners of the chessboard, cols x rows")
    ap.add_argument("--paper", default="letter", choices=["letter", "a4"])
    ap.add_argument("--out", default="outputs/print/markers.pdf")
    ap.add_argument("--png", action="store_true", help="also write a PNG preview of each page next to the PDF")
    a = ap.parse_args()
    W, H = (215.9, 279.4) if a.paper == "letter" else (210.0, 297.0)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    m = a.marker_mm
    bit = m / 6.0                                   # DICT_4X4: 4 data bits + 2 border bits across
    margin = a.margin_mm if a.margin_mm is not None else max(8.0, round(bit * 1.2, 1))
    face = m + 2 * margin
    cube = CubeSpec(edge_mm=face, marker_mm=m)
    from matplotlib.backends.backend_pdf import PdfPages
    pages = []
    with PdfPages(out) as pdf:
        # page 1: markers with quiet zone and cut lines
        fig = plt.figure(figsize=(W * MM, H * MM))
        fig.text(0.5, 1 - 10 / H, f"Cube markers  {cube.dictionary}  marker {m:g} mm  white margin {margin:g} mm  "
                 f"face {face:g} mm  (cube edge >= {face:g} mm)", ha="center", fontsize=9)
        fig.text(0.5, 1 - 15 / H, "Print at 100% / actual size. Measure one black square edge to check. "
                 "Cut on the grey line and KEEP THE WHITE MARGIN; glue to a white cube.", ha="center", fontsize=7)
        cols, rows = 2, 3
        gx = (W - cols * face) / (cols + 1)
        gy = (H - 28 - rows * face) / (rows + 1)
        for k, (face_name, mid) in enumerate(cube.face_ids.items()):
            c, r = k % cols, k // cols
            x0 = gx + c * (face + gx)
            y0 = H - 28 - gy - r * (face + gy) - face
            # cut line = face outline
            axf = fig.add_axes([x0 / W, y0 / H, face / W, face / H])
            axf.set_xlim(0, 1); axf.set_ylim(0, 1); axf.axis("off")
            axf.add_patch(plt.Rectangle((0.004, 0.004), 0.992, 0.992, fill=False, lw=0.6, ec="0.6", ls="--", clip_on=False))
            # marker centred inside the white face
            ax = fig.add_axes([(x0 + margin) / W, (y0 + margin) / H, m / W, m / H])
            ax.imshow(render_marker_image(mid, 600, cube.dictionary), cmap="gray", vmin=0, vmax=255,
                      interpolation="nearest")
            ax.axis("off")
            fig.text((x0 + face / 2) / W, (y0 - 3.5) / H, f"id {mid}  face {face_name}", ha="center", fontsize=7)
        pdf.savefig(fig)
        pages.append(fig)
        # page 2: chessboard, shrunk to fit the paper with 12 mm margins
        cx, cy = (int(v) for v in a.board.split("x"))
        sq = min(a.square_mm, (W - 24) / (cx + 1), (H - 40) / (cy + 1))
        sq = float(np.floor(sq * 2) / 2)             # round down to 0.5 mm so the stated size is exact
        bw, bh = (cx + 1) * sq, (cy + 1) * sq
        board = np.indices((cy + 1, cx + 1)).sum(axis=0) % 2
        fig = plt.figure(figsize=(W * MM, H * MM))
        ax = fig.add_axes([((W - bw) / 2) / W, ((H - bh) / 2) / H, bw / W, bh / H])
        ax.imshow(board, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
        ax.axis("off")
        fig.text(0.5, 1 - 10 / H, f"Camera calibration chessboard  {cx}x{cy} inner corners  square {sq:g} mm"
                 + ("" if sq == a.square_mm else f"  (reduced from {a.square_mm:g} mm to fit the paper)"),
                 ha="center", fontsize=9)
        fig.text(0.5, 1 - 15 / H, f"Tape flat to a rigid board. Print at 100%. Calibrate with --board {cx}x{cy} "
                 f"--square-mm {sq:g}. Film it tilted at many angles, not flat on the table.", ha="center", fontsize=7)
        pdf.savefig(fig)
        pages.append(fig)
    if a.png:
        for i, fig in enumerate(pages, 1):
            fig.savefig(out.with_name(f"{out.stem}_page{i}.png"), dpi=100)
    for fig in pages:
        plt.close(fig)
    print(f"wrote {out}: marker {m:g} mm, margin {margin:g} mm, face {face:g} mm; chessboard {cx}x{cy} at {sq:g} mm")


if __name__ == "__main__":
    main()
