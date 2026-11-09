import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
INK, GREY, PRINT, SKIN, ACC = "#1b2a3a", "#8a94a0", "#f4e9d2", "#d9e4ee", "#c0392b"
CUBE, HT, CLIP0, CLIP1, SW = 60, 24, 108, 128, 12
def parts(s, lean):
    L = np.radians(lean)
    P0 = np.array([HT/2 + 6, CLIP1 - 2]); d = np.array([np.sin(L), np.cos(L)]); P1 = P0 + s*d
    n = np.array([d[1], -d[0]]) * SW/2
    body = np.array([(-12,0),(12,0),(14,28),(HT/2,58),(HT/2,150),(-HT/2,150),(-HT/2,58),(-14,28)])
    clip = np.array([(-HT/2-3,CLIP0),(HT/2+9,CLIP0),(HT/2+9,CLIP1),(-HT/2-3,CLIP1)])
    stalk = np.array([P0+n, P0-n, P1-n, P1+n])
    cube = np.array([(P1[0]-30,P1[1]),(P1[0]+30,P1[1]),(P1[0]+30,P1[1]+60),(P1[0]-30,P1[1]+60)])
    return body, clip, stalk, cube
def rot(pts, th):
    t = np.radians(th); R = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])  # tilt forward (+x) by th
    return pts @ R.T
fig, axes = plt.subplots(1, 4, figsize=(13, 4.4))
opts = [(60,25,"as drawn now"),(60,45,"your arrow (roughly)"),(60,60,"flatter still"),(80,45,"your arrow + longer stalk")]
for ax,(s,lean,name) in zip(axes, opts):
    ax.set_aspect("equal"); ax.set_xlim(-60, 230); ax.set_ylim(-15, 250); ax.set_xticks([]); ax.set_yticks([])
    ax.add_patch(Rectangle((-60,-15), 290, 15, fc=SKIN, ec="none"))
    body, clip, stalk, cube = parts(s, lean)
    for th, alpha in ((0, 0.25), (45, 1.0)):
        for poly, fc in ((body,"#c9ced6"),(clip,PRINT),(stalk,PRINT),(cube,"white")):
            ax.add_patch(Polygon(rot(poly, th), closed=True, fc=fc, ec=INK, lw=0.8, alpha=alpha))
    c45 = rot(cube, 45)[:,1].min(); c60 = rot(cube, 60)[:,1].min()
    lowest = rot(cube,45)[rot(cube,45)[:,1].argmin()]
    ax.annotate("", xy=(lowest[0], 0), xytext=(lowest[0], lowest[1]), arrowprops=dict(arrowstyle="<->", color=ACC, lw=1))
    ax.text(lowest[0]+4, lowest[1]/2, f"{c45:.0f} mm", color=ACC, fontsize=9, va="center", fontweight="bold")
    hand = rot(np.array([(-HT/2-4,55),(HT/2+4,55),(HT/2+4,105),(-HT/2-4,105)]), 45)
    ax.add_patch(Polygon(hand, closed=True, fc="none", ec=GREY, lw=0.7, ls=(0,(2,2))))
    ax.set_title(f"stalk {s} mm, {lean}° off vertical\n{name}", fontsize=9.5, color=INK)
    verdict = "ok" if c60 > 15 else ("tight" if c60 > 0 else "HITS the skin")
    ax.text(0.5, -0.03, f"probe tilted 45° (solid) vs upright (faint)\ncube above skin: {c45:.0f} mm at 45°, {c60:.0f} mm at 60° ({verdict})\ncube centre {rot(cube,0)[:,1].mean():.0f} mm above the probe face",
            transform=ax.transAxes, ha="center", va="top", fontsize=7.5, color=INK)
fig.suptitle("How far forward can the stalk lean? Cube clearance when the probe is tilted 45° towards the cube (flat surface)", fontsize=11, color=INK)
fig.tight_layout(rect=(0,0.1,1,0.93))
fig.savefig(r"C:\ultrasound_Proj\docs\figures\print_sketch\stalk_lean_options.png", dpi=170)
print("ok")
