"""Side-by-side: raw frames, old brightness confidence, new ray-shadow confidence, and the ray model's internals.

Usage: python scripts/confidence_compare.py data/extracted/tusrec2024_val 052__LH_Per_L_DtP 0,150,300,467
"""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from uscov.data import index_dataset  # noqa: E402
from uscov.coverage import fan_mask_from_scan, pixel_confidence, ConfidenceParams  # noqa: E402
from uscov.confidence import RayConfidence  # noqa: E402


def main():
    root, name, idx = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
    out = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("outputs/confidence_compare.png")
    ds = index_dataset(root)
    s = ds.load(name)
    m = fan_mask_from_scan(s.frames)
    rc = RayConfidence(m)
    print("geometry:", rc.geom)
    fig, ax = plt.subplots(3, len(idx), figsize=(3.5 * len(idx), 9))
    for k, i in enumerate(idx):
        ax[0, k].imshow(s.frames[i], cmap="gray"); ax[0, k].set_title(f"frame {i}"); ax[0, k].axis("off")
        ax[1, k].imshow(pixel_confidence(s.frames[i], m, ConfidenceParams()), cmap="magma", vmin=0, vmax=1)
        ax[1, k].set_title("old: brightness"); ax[1, k].axis("off")
        ax[2, k].imshow(rc.full(s.frames[i]), cmap="magma", vmin=0, vmax=1)
        ax[2, k].set_title("new: ray shadow model"); ax[2, k].axis("off")
    fig.tight_layout(); fig.savefig(out, dpi=100)
    print("saved", out)


if __name__ == "__main__":
    main()
