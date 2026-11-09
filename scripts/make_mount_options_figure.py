import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Ellipse, FancyBboxPatch
INK, GREY, PRINT, SKIN, ACC, FLESH = "#1b2a3a", "#8a94a0", "#f4e9d2", "#d9e4ee", "#c0392b", "#f1d2b6"
HT, HW, CLIP0, CLIP1, SW = 24, 40, 108, 128, 12
def R(th):
    t = np.radians(th); return np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
def rot(pts, th): return np.asarray(pts) @ R(th).T
def body(w):  return np.array([(-12,0),(12,0),(14,28),(w/2,58),(w/2,150),(-w/2,150),(-w/2,58),(-14,28)])
def clip(w):  return np.array([(-w/2-3,CLIP0),(w/2+3,CLIP0),(w/2+3,CLIP1),(-w/2-3,CLIP1)])
def stalk(P0, P1):
    d = (P1-P0)/np.linalg.norm(P1-P0); n = np.array([d[1],-d[0]])*SW/2
    return np.array([P0+n, P0-n, P1-n, P1+n])
def cube(c):  return np.array([(c[0]-30,c[1]-30),(c[0]+30,c[1]-30),(c[0]+30,c[1]+30),(c[0]-30,c[1]+30)])
def ell(c, w, h, n=40):
    a = np.linspace(0, 2*np.pi, n); return np.c_[c[0] + w/2*np.cos(a), c[1] + h/2*np.sin(a)]
def bar(p, q, wd, n=10):  # rounded bar from p to q
    p, q = np.asarray(p, float), np.asarray(q, float); d = (q-p)/np.linalg.norm(q-p); nn = np.array([d[1],-d[0]])*wd/2
    a = np.linspace(0, np.pi, n)
    cap_q = [q + nn*np.cos(t) + d*(wd/2)*np.sin(t) for t in a]
    cap_p = [p - nn*np.cos(t) - d*(wd/2)*np.sin(t) for t in a]
    return np.array(cap_q + cap_p)
def lowest(poly, th): return rot(poly, th)[:,1].min()
def hits_at(poly):
    for th in np.arange(0, 90, 0.5):
        if lowest(poly, th) <= 0: return th
    return 90

def draw_pose(ax, w, polys, th, alpha, side=True):
    """probe + mount + hand at tilt th; the hand is drawn behind the handle (palm) and in front (fingers)."""
    if side:
        palm = ell((-20, 82), 46, 66)
        thumb = bar((-26, 92), (-8, 122), 13)
        fingers = [bar((-6, y), (23, y - 2), 11) for y in (64, 77, 90, 103)]
        for poly in (palm, thumb):
            ax.add_patch(Polygon(rot(poly, th), closed=True, fc=FLESH, ec=INK, lw=0.7, alpha=alpha))
    for poly, fc in polys:
        ax.add_patch(Polygon(rot(poly, th), closed=True, fc=fc, ec=INK, lw=0.8, alpha=alpha))
    if side:
        for f in fingers:
            ax.add_patch(Polygon(rot(f, th), closed=True, fc=FLESH, ec=INK, lw=0.7, alpha=alpha))
    else:
        # front view: fingertips curl round the left side of the handle, thumb tip on the right
        for y in (64, 77, 90, 103):
            ax.add_patch(Polygon(rot(ell((-w/2 + 6, y), 16, 11), th), closed=True, fc=FLESH, ec=INK, lw=0.7, alpha=alpha))
        ax.add_patch(Polygon(rot(ell((w/2 - 5, 100), 14, 20), th), closed=True, fc=FLESH, ec=INK, lw=0.7, alpha=alpha))

def forearm_side(ax):
    # static forearm coming in from the operator's side (left), elbow higher than the hand; cable lies on it
    axis_dir = np.array([-np.cos(np.radians(22)), np.sin(np.radians(22))])
    p = np.array([-42, 86]); q = p + axis_dir*200
    ax.add_patch(Polygon(bar(p, q, 62), closed=True, fc=FLESH, ec=INK, lw=0.7, alpha=0.55))
    ax.text(-150, 92, "forearm\n(operator side)", fontsize=7, color=INK, ha="center", va="center")
    t = np.linspace(0, 1, 60)
    ax.plot([0, 0], [150, 192], color="#555", lw=4, solid_capstyle="round", alpha=0.6)
    ax.plot(-230*t, 192 + 50*t - 110*t**2, color="#555", lw=2.5, solid_capstyle="round", alpha=0.6)
    ax.text(-95, 212, "cable over the back\nof the hand and arm", fontsize=7, color=INK, ha="center")

designs = [
  ("A  as drawn now (side view, operator at left)\nstalk up-forward 25°", HT, True, 45, "forward tilt (fanning) 45°"),
  ("B  your drawing (side view)\nstalk down-forward, cube at hand height", HT, True, 28, "forward tilt 28°: already touching"),
  ("C  side mount (front view, operator behind the probe)\nstalk out to the side, 20° up", HW, False, 30, "rock 30° towards the cube"),
]
fig, axes = plt.subplots(1, 3, figsize=(15, 5.4))
for ax, (name, w, side, tilt, cap) in zip(axes, designs):
    ax.set_aspect("equal"); ax.set_ylim(-15, 262); ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(-245, 235)
    ax.add_patch(Rectangle((-250,-15), 500, 15, fc=SKIN, ec="none"))
    if name.startswith("A"):
        P0 = np.array([HT/2+6, CLIP1-2]); d = np.array([np.sin(np.radians(25)), np.cos(np.radians(25))]); P1 = P0 + 60*d; cc = P1 + [0,30]
    elif name.startswith("B"):
        P0 = np.array([HT/2+6, CLIP0+4]); P1 = np.array([90, 112]); cc = np.array([120, 112])
    else:
        P0 = np.array([HW/2+3, CLIP1-4]); d = np.array([np.cos(np.radians(20)), np.sin(np.radians(20))]); P1 = P0 + 60*d; cc = np.array([P1[0]+30, P1[1]])
    polys = [(body(w),"#c9ced6"),(clip(w),PRINT),(stalk(P0,P1),PRINT),(cube(cc),"white")]
    if side:
        forearm_side(ax)
    else:
        ax.add_patch(Ellipse((0, 92), 62, 48, fc=FLESH, ec=INK, lw=0.7, ls=(0,(2,2)), alpha=0.45))
        ax.text(-70, 150, "hand and forearm are\nBEHIND the probe here\n(operator side, away\nfrom you); cable too", fontsize=7, color=INK, ha="center", va="center")
    draw_pose(ax, w, polys, 0, 0.25, side)
    draw_pose(ax, w, polys, tilt, 1.0, side)
    cb = cube(cc); pt = rot(cb, tilt)[rot(cb, tilt)[:,1].argmin()]; cl = max(lowest(cb, tilt), 0)
    ax.annotate("", xy=(pt[0], 0), xytext=(pt[0], pt[1]), arrowprops=dict(arrowstyle="<->", color=ACC, lw=1))
    ax.text(pt[0]+4, max(pt[1]/2, 8), f"{cl:.0f} mm", color=ACC, fontsize=9, va="center", fontweight="bold")
    ax.set_title(name, fontsize=9, color=INK)
    lever = np.hypot(cc[0], cc[1])
    if side:
        txt = (f"solid = {cap}\ncube above skin: {max(lowest(cb,30),0):.0f} mm at 30°, {max(lowest(cb,45),0):.0f} mm at 45°; touches at {hits_at(cb):.0f}°\n"
               f"cube centre {lever:.0f} mm from the probe face")
    else:
        z0 = cb[:,1].min()
        txt = (f"solid = {cap}\nfanning 45° (the usual sweep): cube stays {z0*np.cos(np.radians(45)):.0f} mm up, 60°: {z0*0.5:.0f} mm\n"
               f"rock 30° towards the cube: {cl:.0f} mm; cube centre {lever:.0f} mm from the probe face")
    ax.text(0.5, -0.03, txt, transform=ax.transAxes, ha="center", va="top", fontsize=7.5, color=INK)
fig.suptitle("Normal hold: fingers low on the probe, little-finger side of the hand on the patient, cable over the arm, forearm from the operator's side.  "
             "Faint = upright, solid = tilted, red = cube height above the skin.", fontsize=9.5, color=INK)
fig.tight_layout(rect=(0,0.11,1,0.93))
fig.savefig(r"C:\ultrasound_Proj\docs\figures\print_sketch\mount_options.png", dpi=170); print("ok")
