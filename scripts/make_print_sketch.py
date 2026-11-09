"""Dimensioned print sketch for the marker-cube mount (clip + stalk + cube), for the meeting with Emily Simpson."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages

INK, GREY, LIGHT, ACC, BLUE, PRINT, SKIN = "#1b2a3a", "#8a94a0", "#e6ebf0", "#c0392b", "#2c6fb0", "#f4e9d2", "#d9e4ee"
OUT = r"C:\ultrasound_Proj\docs\figures\print_sketch"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.edgecolor": GREY})

# ---------- geometry (mm) ----------
CUBE = 60.0; RECESS = 52.0; STICKER = 51.0; MARKER = 35.0; RIM = (CUBE - RECESS) / 2
CLIP_Y0, CLIP_Y1 = 108.0, 128.0           # clip band on the handle, above the hand
STALK_L, STALK_W, LEAN = 50.0, 12.0, 30.0  # stalk length, width, backward lean (deg)
HAND_Y0, HAND_Y1 = 55.0, 105.0
HANDLE_T, HANDLE_W = 24.0, 40.0            # handle thickness (side view) and width (front view) [measure]
d = np.array([np.sin(np.radians(LEAN)), np.cos(np.radians(LEAN))])
n = np.array([d[1], -d[0]]) * STALK_W / 2
S0 = np.array([HANDLE_T / 2 + 3 + 3, CLIP_Y1])       # stalk root on the back of the clip boss
S1 = S0 + d * STALK_L                                # stalk top = cube bottom-face centre
CUBE_C = S1 + np.array([0, CUBE / 2])


def dim_h(ax, x0, x1, y, text, dy=2.0, fs=6.5, color=INK):
    ax.annotate("", xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color=color, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + dy, text, ha="center", va="bottom" if dy >= 0 else "top", fontsize=fs, color=color)


def dim_v(ax, y0, y1, x, text, dx=2.0, fs=6.5, color=INK, rot=90):
    ax.annotate("", xy=(x, y0), xytext=(x, y1), arrowprops=dict(arrowstyle="<->", color=color, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(x + dx, (y0 + y1) / 2, text, ha="left" if dx >= 0 else "right", va="center", fontsize=fs, color=color, rotation=rot)


def ext(ax, p, q):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=GREY, lw=0.5)


def note(ax, xy, xytext, text, fs=6.5, color=INK):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=color, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6, shrinkA=0, shrinkB=2))


def marker(ax, cx, cy, size, seed=3):
    rng = np.random.default_rng(seed)
    bit = size / 6
    for i in range(6):
        for j in range(6):
            black = (i in (0, 5) or j in (0, 5)) or rng.random() < 0.5
            if black:
                ax.add_patch(Rectangle((cx - size / 2 + j * bit, cy - size / 2 + i * bit), bit, bit, fc=INK, ec="none"))


def title(ax, letter, text):
    ax.text(0.0, 1.01, f"{letter}  {text}", transform=ax.transAxes, fontsize=8.5, fontweight="bold", color=INK, va="bottom")


def setup(ax, xlim, ylim):
    ax.set_aspect("equal"); ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.5)


# ---------- A: side view, probe in scanning position ----------
def side_view(ax):
    setup(ax, (-70, 185), (-20, 290))
    title(ax, "A", "Side view, probe on the phantom (mm, 1:1 within the panel)")
    ax.add_patch(Rectangle((-70, -20), 235, 20, fc=SKIN, ec="none"))
    ax.text(-66, -10, "phantom / patient", fontsize=6.5, color=GREY, va="center")
    body = [(-12, 0), (12, 0), (14, 28), (HANDLE_T / 2, 58), (HANDLE_T / 2, 150), (-HANDLE_T / 2, 150), (-HANDLE_T / 2, 58), (-14, 28)]
    ax.add_patch(Polygon(body, closed=True, fc="#c9ced6", ec=INK, lw=0.9))
    ax.text(0, 30, "probe", ha="center", fontsize=6.5, color=INK)
    t = np.linspace(0, 1, 50)
    ax.plot(-6 * t ** 2, 150 + 120 * t, color="#555", lw=3, solid_capstyle="round")
    ax.text(-10, 262, "cable", fontsize=6.5, color=INK, ha="right")
    ax.add_patch(Rectangle((-HANDLE_T / 2 - 4, HAND_Y0), HANDLE_T + 8, HAND_Y1 - HAND_Y0, fc="none", ec=GREY, lw=0.7, ls=(0, (2, 2))))
    ax.text(-HANDLE_T / 2 - 7, (HAND_Y0 + HAND_Y1) / 2, "scanning hand\n(grip zone)\nnothing printed here", ha="right", va="center", fontsize=6.5, color=GREY)
    ax.add_patch(Rectangle((-HANDLE_T / 2 - 3, CLIP_Y0), HANDLE_T + 6, CLIP_Y1 - CLIP_Y0, fc=PRINT, ec=INK, lw=0.9))
    ax.add_patch(Rectangle((HANDLE_T / 2 + 3, CLIP_Y0), 6, CLIP_Y1 - CLIP_Y0, fc=PRINT, ec=INK, lw=0.9))
    ax.add_patch(Polygon([S0 + n, S0 - n, S1 - n, S1 + n], closed=True, fc=PRINT, ec=INK, lw=0.9))
    ax.add_patch(Rectangle((S1[0] - 10, S1[1] - 3), 20, 3, fc=PRINT, ec=INK, lw=0.9))
    ax.add_patch(Rectangle((CUBE_C[0] - CUBE / 2, S1[1]), CUBE, CUBE, fc="white", ec=INK, lw=1.0))
    ax.add_patch(Rectangle((CUBE_C[0] - RECESS / 2, S1[1] + RIM), RECESS, RECESS, fc=LIGHT, ec=GREY, lw=0.5))
    marker(ax, CUBE_C[0], CUBE_C[1], MARKER, seed=5)
    ax.text(CUBE_C[0] - CUBE / 2 + 1.5, S1[1] + CUBE - 1.5, "3", fontsize=5, ha="left", va="top", color=INK)
    c = CUBE_C
    u = np.array([np.cos(np.radians(45)), np.sin(np.radians(45))])
    p1 = c + u * 44; p2 = c + u * 56; p3 = c + u * 78
    ax.plot(*zip(c, p1), color=BLUE, lw=0.8, ls="--")
    ax.plot(*zip(p2, p3), color=BLUE, lw=0.8, ls="--")
    for q in (p1, p2):
        ax.plot([q[0] - 3, q[0] + 3], [q[1] + 3, q[1] - 3], color=BLUE, lw=0.8)
    cam = p3
    ax.add_patch(FancyBboxPatch((cam[0] - 6, cam[1] - 11), 12, 22, boxstyle="round,pad=0.6", fc="white", ec=BLUE, lw=0.9))
    ax.add_patch(Circle((cam[0], cam[1] + 5), 2.2, fc=BLUE, ec="none"))
    ax.text(cam[0] + 10, cam[1], "phone camera on tripod\n~30 cm from the cube,\nlooking down 45°: sees the\ntop face + one side face", fontsize=6.5, color=BLUE, va="center", ha="left")
    dim_h(ax, CUBE_C[0] - CUBE / 2, CUBE_C[0] + CUBE / 2, S1[1] + CUBE + 8, f"{CUBE:.0f}")
    ext(ax, (CUBE_C[0] - CUBE / 2, S1[1] + CUBE), (CUBE_C[0] - CUBE / 2, S1[1] + CUBE + 9))
    ext(ax, (CUBE_C[0] + CUBE / 2, S1[1] + CUBE), (CUBE_C[0] + CUBE / 2, S1[1] + CUBE + 9))
    m = (S0 + S1) / 2 + n * 1.9
    ax.annotate("", xy=S0 + n * 1.9, xytext=S1 + n * 1.9, arrowprops=dict(arrowstyle="<->", color=INK, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(m[0] + 3, m[1] + 4, f"stalk {STALK_L:.0f}\n(50-80 ok, shorter is better:\nless height = less error\nat the probe tip)", ha="left", va="center", fontsize=6.5)
    ax.plot([S0[0], S0[0]], [S0[1], S0[1] + 20], color=GREY, lw=0.5, ls=":")
    ax.text(S0[0] + 12, CLIP_Y0 + 2, f"stalk leans back {LEAN:.0f}°\nso the cube clears the cable", fontsize=6.5, va="bottom")
    dim_v(ax, CLIP_Y0, CLIP_Y1, -HANDLE_T / 2 - 10, f"clip {CLIP_Y1 - CLIP_Y0:.0f}", dx=-3, rot=0)
    xr = 118
    dim_v(ax, 0, CUBE_C[1], xr, f"cube centre to probe face\n≈{CUBE_C[1]:.0f} here. Exact value is read\nfrom the CAD and typed into\nthe software, any value is fine", dx=3, rot=0)
    ext(ax, (CUBE_C[0] + CUBE / 2, CUBE_C[1]), (xr + 1, CUBE_C[1]))
    ext(ax, (12, 0), (xr + 1, 0))
    ax.plot([CUBE_C[0] - 4, CUBE_C[0] + 4], [CUBE_C[1], CUBE_C[1]], color=ACC, lw=0.6)
    ax.plot([CUBE_C[0], CUBE_C[0]], [CUBE_C[1] - 4, CUBE_C[1] + 4], color=ACC, lw=0.6)
    note(ax, (HANDLE_T / 2 + 3, (CLIP_Y0 + CLIP_Y1) / 2), (-66, 180),
         "clip: wraps the handle just\nabove the hand, 3 mm wall,\nfoam tape inside, snap-fit\nor one M3 screw (see E)")
    note(ax, (S1[0] - 10, S1[1] - 1.5), (-66, 215), "stalk, boss and cube printed\nas ONE piece per probe")
    ax.text(-66, 284, "Probes: GE C1-5 (curved) and L4-12t-RS (linear).\nOne print per probe, two copies each.", fontsize=6.5, color=INK, va="top")


# ---------- B: front view ----------
def front_view(ax):
    setup(ax, (-80, 80), (-20, 255))
    title(ax, "B", "Front view (button side); stalk hidden behind")
    ax.add_patch(Rectangle((-80, -20), 160, 20, fc=SKIN, ec="none"))
    body = [(-34, 0), (34, 0), (30, 25), (HANDLE_W / 2, 58), (HANDLE_W / 2, 150), (-HANDLE_W / 2, 150), (-HANDLE_W / 2, 58), (-30, 25)]
    ax.add_patch(Rectangle((-CUBE / 2, S1[1]), CUBE, CUBE, fc="white", ec=INK, lw=1.0))
    ax.add_patch(Rectangle((-RECESS / 2, S1[1] + RIM), RECESS, RECESS, fc=LIGHT, ec=GREY, lw=0.5))
    marker(ax, 0, CUBE_C[1], MARKER, seed=7)
    ax.text(-CUBE / 2 + 1.5, S1[1] + CUBE - 1.5, "2", fontsize=5, ha="left", va="top")
    ax.add_patch(Rectangle((-10, S1[1] - 3), 20, 3, fc=PRINT, ec=INK, lw=0.9))
    ax.plot([-STALK_W / 2, -STALK_W / 2, STALK_W / 2, STALK_W / 2], [150, S1[1] - 3, S1[1] - 3, 150], color=INK, lw=0.6, ls=(0, (3, 2)))
    ax.add_patch(Polygon(body, closed=True, fc="#c9ced6", ec=INK, lw=0.9))
    ax.plot([0, 0], [150, 240], color="#555", lw=3, solid_capstyle="round")
    for yb in (76, 85):
        ax.add_patch(Circle((0, yb), 2.6, fc="white", ec=INK, lw=0.7))
    note(ax, (3, 80.5), (26, 66), "buttons (L4-12t-RS):\nmust stay uncovered,\nclip sits above them")
    ax.add_patch(Rectangle((-HANDLE_W / 2 - 3, CLIP_Y0), 3, CLIP_Y1 - CLIP_Y0, fc=PRINT, ec=INK, lw=0.9))
    ax.add_patch(Rectangle((HANDLE_W / 2, CLIP_Y0), 3, CLIP_Y1 - CLIP_Y0, fc=PRINT, ec=INK, lw=0.9))
    ax.plot([-HANDLE_W / 2, HANDLE_W / 2], [CLIP_Y0, CLIP_Y0], color=INK, lw=0.6, ls=(0, (3, 2)))
    ax.plot([-HANDLE_W / 2, HANDLE_W / 2], [CLIP_Y1, CLIP_Y1], color=INK, lw=0.6, ls=(0, (3, 2)))
    ax.add_patch(Rectangle((-STALK_W / 2, CLIP_Y0 + 4), STALK_W, CLIP_Y1 - CLIP_Y0 - 8, fc="none", ec=INK, lw=0.6, ls=(0, (3, 2))))
    ax.annotate("", xy=(-HANDLE_W / 2, CLIP_Y0 - 8), xytext=(HANDLE_W / 2, CLIP_Y0 - 8), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.7, shrinkA=0, shrinkB=0))
    ax.text(HANDLE_W / 2 + 4, CLIP_Y0 - 8, "handle width\n[measure today]", fontsize=6.5, va="center", ha="left")
    ext(ax, (-HANDLE_W / 2, CLIP_Y0), (-HANDLE_W / 2, CLIP_Y0 - 9)); ext(ax, (HANDLE_W / 2, CLIP_Y0), (HANDLE_W / 2, CLIP_Y0 - 9))
    dim_h(ax, -CUBE / 2, CUBE / 2, S1[1] + CUBE + 6, f"{CUBE:.0f}")
    dim_v(ax, 0, CLIP_Y0, -HANDLE_W / 2 - 14, f"{CLIP_Y0:.0f} from\nprobe face\n[adjust to\nthe hand]", dx=-3, rot=0)
    ext(ax, (-HANDLE_W / 2 - 3, CLIP_Y0), (-HANDLE_W / 2 - 15, CLIP_Y0)); ext(ax, (-34, 0), (-HANDLE_W / 2 - 15, 0))
    ax.text(0, S1[1] + CUBE + 16, "cube centred on the probe's width axis", ha="center", fontsize=6.5)


# ---------- C: cube net ----------
def cube_net(ax):
    setup(ax, (-105, 115), (-128, 96))
    title(ax, "C", "Cube unfolded: five marker faces + bottom (stalk)")
    pos = {1: (0, 0), 4: (0, CUBE), 2: (0, -CUBE), 3: (CUBE, 0), 5: (-CUBE, 0)}
    label = {1: "1  top", 2: "2  front", 3: "3  right", 4: "4  back", 5: "5  left"}
    for k, (cx, cy) in pos.items():
        ax.add_patch(Rectangle((cx - CUBE / 2, cy - CUBE / 2), CUBE, CUBE, fc="white", ec=INK, lw=1.0))
        ax.add_patch(Rectangle((cx - RECESS / 2, cy - RECESS / 2), RECESS, RECESS, fc=LIGHT, ec=GREY, lw=0.6))
        ax.add_patch(Rectangle((cx - STICKER / 2, cy - STICKER / 2), STICKER, STICKER, fc="none", ec=GREY, lw=0.5, ls=(0, (2, 2))))
        marker(ax, cx, cy, MARKER, seed=k)
        ax.text(cx - CUBE / 2 + 1.0, cy + CUBE / 2 - 0.8, str(k), fontsize=6, fontweight="bold", ha="left", va="top")
        if k != 1:
            ax.annotate("", xy=(cx, cy + CUBE / 2 - 0.6), xytext=(cx, cy + CUBE / 2 - 3.6), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8, mutation_scale=5))
        ax.text(cx + CUBE / 2 - 1, cy - CUBE / 2 + 0.6, label[k], fontsize=5, ha="right", va="bottom", color=GREY)
    bx, by = -CUBE, -CUBE
    ax.add_patch(Rectangle((bx - CUBE / 2, by - CUBE / 2), CUBE, CUBE, fc="none", ec=INK, lw=0.8, ls=(0, (3, 2))))
    ax.add_patch(Circle((bx, by), STALK_W / 2 + 4, fc=PRINT, ec=INK, lw=0.8))
    ax.add_patch(Circle((bx, by), STALK_W / 2, fc="none", ec=INK, lw=0.6))
    ax.text(bx, by - 13, "bottom face: stalk\nboss, no marker", fontsize=6, ha="center", va="top")
    cx, cy = pos[3]
    dim_h(ax, cx - CUBE / 2, cx + CUBE / 2, cy + CUBE / 2 + 4, f"{CUBE:.0f} cube", dy=1.5)
    dim_h(ax, cx - RECESS / 2, cx + RECESS / 2, cy - CUBE / 2 - 5, f"{RECESS:.0f} recess, 0.5 deep", dy=-1.5)
    dim_h(ax, cx - MARKER / 2, cx + MARKER / 2, cy - CUBE / 2 - 16, f"{MARKER:.0f} marker + 8 white border\n= {STICKER:.0f} sticker (dashed)", dy=-1.5)
    ext(ax, (cx - RECESS / 2, cy - RECESS / 2), (cx - RECESS / 2, cy - CUBE / 2 - 6)); ext(ax, (cx + RECESS / 2, cy - RECESS / 2), (cx + RECESS / 2, cy - CUBE / 2 - 6))
    ext(ax, (cx - MARKER / 2, cy - MARKER / 2), (cx - MARKER / 2, cy - CUBE / 2 - 17)); ext(ax, (cx + MARKER / 2, cy - MARKER / 2), (cx + MARKER / 2, cy - CUBE / 2 - 17))
    cx, cy = pos[5]
    note(ax, (cx, cy + CUBE / 2 - 2), (-103, 52), "up-arrow on the rim\nof every side face", fs=6)
    cx, cy = pos[4]
    note(ax, (cx - CUBE / 2 + 2, cy + CUBE / 2 - 2), (-103, 84), f"face number, 3 mm,\nembossed 0.4 mm\non the {RIM:.0f} mm rim", fs=6)
    ax.text(-103, -127, "Stickers (markers) are printed on paper by us and glued into the recesses after printing.\nAll five recesses identical; which marker goes on which face is recorded by the face number.", fontsize=6, va="bottom", color=INK)


# ---------- D: face section ----------
def face_section(ax):
    setup(ax, (-46, 46), (-21, 11))
    title(ax, "D", "Section through one face (vertical scale x5)")
    k = 5.0
    wall = 2.0
    ax.add_patch(Rectangle((-CUBE / 2, -wall * k), CUBE, wall * k, fc=PRINT, ec=INK, lw=0.9))
    ax.add_patch(Rectangle((-RECESS / 2, -0.5 * k), RECESS, 0.5 * k, fc="white", ec=INK, lw=0.7))
    ax.add_patch(Rectangle((-STICKER / 2, -0.5 * k), STICKER, 0.2 * k, fc="#fafafa", ec=GREY, lw=0.6, hatch="////"))
    ax.add_patch(Rectangle((-MARKER / 2, -0.5 * k), MARKER, 0.2 * k, fc=INK, ec="none"))
    ax.add_patch(Rectangle((-CUBE / 2 + 0.8, 0), 2.4, 0.4 * k, fc=PRINT, ec=INK, lw=0.7))
    ax.text(0, -wall * k - 1.0, "hollow inside, 2 mm walls (about 50 g in PLA)", ha="center", va="top", fontsize=6.5)
    dim_v(ax, -0.5 * k, 0, RECESS / 2 + 2, "0.5 recess", dx=1.5, rot=0)
    dim_v(ax, -0.5 * k, -0.3 * k, -RECESS / 2 - 2, "sticker ~0.2", dx=-1.5, rot=0)
    note(ax, (-CUBE / 2 + 2, 0.4 * k), (-32, 8), "embossed number / arrow\n0.4 high on the rim", fs=6)
    note(ax, (0, -0.4 * k), (4, 7), "35 mm marker (black part of the sticker)\nmust lie FLAT: no supports, layer steps\nor warping on the five marker faces", fs=6)
    ax.text(0, -20.5, "The recess stops the sticker edge peeling and self-centres it. Faces must be flat and matte white\n(markers are found by black/white contrast; gloss and dark filament break detection).", ha="center", fontsize=6, va="bottom")


# ---------- E: clip cross-section ----------
def handle(ax, cx):
    ax.add_patch(FancyBboxPatch((cx - HANDLE_W / 2 - 1, -HANDLE_T / 2 - 1), HANDLE_W + 2, HANDLE_T + 2, boxstyle="round,pad=0,rounding_size=9", fc="#c9ced6", ec="#999", lw=1.2, ls=":"))
    ax.add_patch(FancyBboxPatch((cx - HANDLE_W / 2, -HANDLE_T / 2), HANDLE_W, HANDLE_T, boxstyle="round,pad=0,rounding_size=8", fc="#c9ced6", ec=INK, lw=0.8))
    ax.text(cx, 0, "handle\n[measure W x T\non both probes]", ha="center", va="center", fontsize=5.5)


def clip_section(ax):
    setup(ax, (-70, 128), (-40, 40))
    title(ax, "E", "Clip cross-section at the handle: two ways to make it (pick one)")
    for cx, mode in ((-30, "snap"), (55, "screw")):
        ax.add_patch(FancyBboxPatch((cx - HANDLE_W / 2 - 4, -HANDLE_T / 2 - 4), HANDLE_W + 8, HANDLE_T + 8, boxstyle="round,pad=0,rounding_size=12", fc=PRINT, ec=INK, lw=0.9))
        handle(ax, cx)
        if mode == "snap":
            ax.add_patch(Rectangle((cx - 12, -HANDLE_T / 2 - 5), 24, 6, fc="white", ec="none"))
            ax.plot([cx - 12, cx - 12], [-HANDLE_T / 2 - 4, -HANDLE_T / 2 - 1], color=INK, lw=0.9)
            ax.plot([cx + 12, cx + 12], [-HANDLE_T / 2 - 4, -HANDLE_T / 2 - 1], color=INK, lw=0.9)
            ax.text(cx, -HANDLE_T / 2 - 9, "opening at the front (button side), ~24 mm:\nflex the walls open to snap it on", ha="center", va="top", fontsize=6)
            ax.text(-67, HANDLE_T / 2 + 15, "E1  snap-fit C-clip (simplest, no hardware)\nPLA may crack when flexed: PETG helps", ha="left", va="bottom", fontsize=6.5, fontweight="bold")
        else:
            ax.plot([cx - HANDLE_W / 2 - 4, cx - HANDLE_W / 2 - 1], [0, 0], color=INK, lw=0.9)
            ax.plot([cx + HANDLE_W / 2 + 1, cx + HANDLE_W / 2 + 4], [0, 0], color=INK, lw=0.9)
            ax.add_patch(Rectangle((cx - HANDLE_W / 2 - 12, -5), 8, 10, fc=PRINT, ec=INK, lw=0.9))
            ax.plot([cx - HANDLE_W / 2 - 8, cx - HANDLE_W / 2 - 8], [-9, 9], color=INK, lw=1.2)
            ax.plot([cx - HANDLE_W / 2 - 10.5, cx - HANDLE_W / 2 - 5.5], [9, 9], color=INK, lw=1.2)
            ax.add_patch(Circle((cx + HANDLE_W / 2 + 4, 0), 2.5, fc="white", ec=INK, lw=0.8))
            ax.text(34, HANDLE_T / 2 + 15, "E2  two-piece clamp, one M3 screw + nut\n(firmer, reusable; resized per probe)", ha="left", va="bottom", fontsize=6.5, fontweight="bold")
            ax.text(cx - HANDLE_W / 2 - 14, -11, "M3 screw\n+ nut trap", ha="right", va="top", fontsize=6)
            ax.text(cx + HANDLE_W / 2 + 8, -4, "hinge pin\nor tongue", ha="left", va="top", fontsize=6)
        ax.add_patch(Rectangle((cx - STALK_W / 2, HANDLE_T / 2 + 4), STALK_W, 6, fc=PRINT, ec=INK, lw=0.9))
        ax.text(cx + STALK_W / 2 + 2, HANDLE_T / 2 + 7, "stalk (back side)", fontsize=6, va="center")
    ax.text(-67, -38, "Both: 3 mm wall, 20 mm tall, 1 mm foam tape inside (dotted) so the probe is not scratched; cable and buttons\nuntouched; must not rotate or slide once on (any slip moves every measurement). Split line = the two halves.", fontsize=6, va="bottom")


# ---------- F: spec table + checklist ----------
def spec_text(ax):
    ax.axis("off")
    title(ax, "F", "What to print (summary) and what to measure today")
    rows = [
        ("Cube", f"{CUBE:.0f} mm edge (55-60 ok), hollow, 2 mm walls, matte WHITE"),
        ("Marker faces", f"5 faces (all but bottom): recess {RECESS:.0f} x {RECESS:.0f} x 0.5 mm, flat, no supports on them"),
        ("Labels", "face numbers 1-5 (3 mm) + up-arrow on side faces, embossed 0.4 mm on the rim"),
        ("Stalk", f"{STALK_L:.0f} mm (50-80), {STALK_W:.0f} mm round or 12 x 8 oval, leans back ~{LEAN:.0f}°, stiff"),
        ("Clip", "wraps the handle above the hand, 20 mm tall, 3 mm wall, snap (E1) or M3 clamp (E2), foam inside"),
        ("Keep free", "the scanning grip, both buttons (L4-12t-RS), the cable exit"),
        ("Pieces", "clip + stalk + cube as ONE part per probe (C1-5, L4-12t-RS); 2 copies each = 4 prints"),
        ("Material", "PLA fine (PETG if snap-fit); white, matte; no glossy or dark filament"),
        ("Camera", "phone ~30 cm away, 45° down: top face + one side face visible in the normal grip"),
        ("Tolerances", "nothing tight: ±0.5 mm is fine everywhere except the clip's grip on the handle"),
    ]
    y = 0.93
    for k, v in rows:
        ax.text(0.0, y, k, fontsize=6.8, fontweight="bold", va="top", transform=ax.transAxes)
        ax.text(0.19, y, v, fontsize=6.8, va="top", transform=ax.transAxes)
        y -= 0.062
    y -= 0.03
    ax.text(0.0, y, "Measure today (bring calipers and a phone):", fontsize=7, fontweight="bold", va="top", transform=ax.transAxes)
    y -= 0.062
    for s in ["handle width and thickness of BOTH probes at 100-130 mm from the probe face (clip zone)",
              "position of the two buttons on the L4-12t-RS, and the cable-exit diameter",
              "a photo of each probe with a ruler, side and front, so the handle can be modelled",
              "Emily's printer, nozzle, filament colours, and the largest part her bed takes (≈ 60 x 90 x 150 mm needed)"]:
        ax.text(0.02, y, "•  " + s, fontsize=6.8, va="top", transform=ax.transAxes)
        y -= 0.062


# ---------- G: what the camera sees ----------
def camera_view(ax):
    setup(ax, (-60, 60), (-58, 52))
    title(ax, "G", "What the phone sees (cube in the camera's eye, 45° down)")
    a = 30
    top = [(-a, 15), (0, 15 + a * 0.5), (a, 15), (0, 15 - a * 0.5)]
    right = [(0, 15 - a * 0.5), (a, 15), (a, 15 - a), (0, 15 - a * 1.5)]
    left = [(-a, 15), (0, 15 - a * 0.5), (0, 15 - a * 1.5), (-a, 15 - a)]
    for poly, fc in ((left, "#eef1f4"), (right, "white"), (top, "white")):
        ax.add_patch(Polygon(poly, closed=True, fc=fc, ec=INK, lw=0.9))

    def skew(poly, s):
        cx = sum(p[0] for p in poly) / 4; cy = sum(p[1] for p in poly) / 4
        return [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in poly]

    for poly in (top, right):
        ax.add_patch(Polygon(skew(poly, RECESS / CUBE), closed=True, fc=LIGHT, ec=GREY, lw=0.5))
        ax.add_patch(Polygon(skew(poly, MARKER / CUBE), closed=True, fc=INK, ec="none"))
        inner = skew(poly, MARKER / CUBE * 4 / 6)
        ax.add_patch(Polygon(inner, closed=True, fc="white", ec="none"))
        cx = sum(p[0] for p in inner) / 4; cy = sum(p[1] for p in inner) / 4
        for dx, dy in ((-4, 2), (3, -3), (5, 3), (-2, -5)):
            ax.add_patch(Polygon([(cx + dx + x, cy + dy + y) for x, y in ((-2, 0), (0, 1), (2, 0), (0, -1))], fc=INK, ec="none"))
    ax.text(0, 15 + a * 0.5 - 2.5, "1", fontsize=6, ha="center", va="top", fontweight="bold")
    ax.text(a - 3, 15 - 2, "3", fontsize=6, ha="right", va="top", fontweight="bold")
    ax.text(-a + 3, 15 - 2, "2", fontsize=6, ha="left", va="top", fontweight="bold", color=GREY)
    ax.plot([0, 0], [15 - a * 1.5, -30], color=INK, lw=4, solid_capstyle="round", alpha=0.25)
    ax.text(3, -24, "stalk", fontsize=6, color=GREY)
    ax.text(0, -36, "Two faces at right angles in every frame is what gives the tracker a stable 3-D pose.\n"
                    "This is why the cube sits above the hand on a stalk: fingers must never cover a face.\n"
                    "A third face (2) caught at a glancing angle helps too.", ha="center", fontsize=6.5, va="top")


def header(fig, sub):
    fig.text(0.04, 0.965, "Marker cube mount for the ultrasound probe: print sketch", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.04, 0.94, sub, fontsize=8, color=GREY)


def page1():
    fig = plt.figure(figsize=(11, 8.5))
    header(fig, "Ben Zheng, MS2 · for Emily Simpson · 2026-11-09 · all dimensions in mm · page 1 of 2: assembly and cube")
    side_view(fig.add_axes([0.04, 0.05, 0.50, 0.86]))
    front_view(fig.add_axes([0.56, 0.53, 0.42, 0.38]))
    cube_net(fig.add_axes([0.56, 0.04, 0.42, 0.44]))
    return fig


def page2():
    fig = plt.figure(figsize=(11, 8.5))
    header(fig, "page 2 of 2: face detail, clip options, summary and today's measurements")
    face_section(fig.add_axes([0.04, 0.60, 0.44, 0.31]))
    clip_section(fig.add_axes([0.52, 0.52, 0.46, 0.39]))
    spec_text(fig.add_axes([0.04, 0.04, 0.44, 0.50]))
    camera_view(fig.add_axes([0.52, 0.04, 0.46, 0.42]))
    return fig


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    f1, f2 = page1(), page2()
    f1.savefig(os.path.join(OUT, "print_sketch_p1.png"), dpi=200)
    f2.savefig(os.path.join(OUT, "print_sketch_p2.png"), dpi=200)
    with PdfPages(r"C:\ultrasound_Proj\docs\MARKER_CUBE_PRINT_SKETCH.pdf") as pdf:
        pdf.savefig(f1); pdf.savefig(f2)
    print("done")
