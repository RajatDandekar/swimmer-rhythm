"""Turn the captured real-simulation frames (swim_frames.npz) into the movie.

Side by side: the same swimmer in two fluids. Left, weak memory (De=0.5) where the optimal
rhythm lingers OPEN; right, strong memory (De=2.0) where it lingers CLOSED. Each panel shows
the actual polymer-stretch field the solver produced, the two-bead body opening and closing on
its real schedule, a stroke-phase trace that makes the lingering visible, and an honest
net-distance meter racing the winning rhythm against the other one.

Frames -> PNG -> H.264 via ffmpeg.  Also drops a poster still.
"""
import json
import os
import subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, FancyBboxPatch

PI = np.pi
PAPER, INK, INK2, MUTED, FAINT, LINE = "#fbf9f3", "#16130d", "#3a352b", "#6d665a", "#a49c8c", "#e4dece"
TEAL, ORANGE, GOOD, HOT = "#1a6fb0", "#c05f18", "#1c7a55", "#b3006b"
CMAP = LinearSegmentedColormap.from_list("stretch", [
    "#ffffff", "#eaf5fb", "#c2e2f2", "#8ecde8", "#4fb2da",
    "#1a9fd4", "#1370a0", "#0f3550"])
FR = "/private/tmp/claude-501/-Users-raj-Downloads-Vizuara/0ddf2ea6-71c5-4ee7-94da-c1eb7d68fb0d/scratchpad/swim_frames"
OUT = "site/figures"
FPS = 30

plt.rcParams.update({"font.family": "serif", "font.serif": ["Georgia", "DejaVu Serif"],
                     "mathtext.fontset": "cm"})


def load():
    z = np.load("swim_frames.npz")
    cx = json.load(open("crossover_results.json"))
    dxg = {(r["lam"], r["b1"]): abs(r["dx"]) for r in cx if r.get("ok")}
    panels = [
        dict(key="open", accent=TEAL, De=0.5, gait="lingers OPEN", other="lingering closed",
             title="Weak fluid memory", win=dxg[(0.5, -0.5)], lose=dxg[(0.5, 0.5)], dwell="open"),
        dict(key="closed", accent=ORANGE, De=2.0, gait="lingers CLOSED", other="lingering open",
             title="Strong fluid memory", win=dxg[(2.0, 0.5)], lose=dxg[(2.0, -0.5)], dwell="closed"),
    ]
    for p in panels:
        p["fields"] = z[f"{p['key']}_fields"].astype(np.float32)
        p["ux"] = z[f"{p['key']}_ux"].astype(np.float32)
        p["uy"] = z[f"{p['key']}_uy"].astype(np.float32)
        p["d"] = z[f"{p['key']}_d"]; p["xc"] = z[f"{p['key']}_xc"]
        p["phase"] = z[f"{p['key']}_phase"]
        p["spdmax"] = float(np.percentile(np.sqrt(p["ux"] ** 2 + p["uy"] ** 2), 99.0))
    ext = z["extent"]
    # shared brightness normalisation across both panels (comparable fields)
    allc = np.concatenate([p["fields"].ravel() for p in panels])
    lo, hi = np.percentile(allc, 46.0), np.percentile(allc, 99.5)
    return panels, ext, float(lo), float(hi)


def draw_sphere(ax, cx, cy, r, tint, zorder=8):
    """A lit 3-D sphere (Lambert + specular) so the swimmer reads as a real body, not a disc."""
    n = 120
    u = np.linspace(-1, 1, n); U, V = np.meshgrid(u, u)
    R2 = U ** 2 + V ** 2; Z = np.sqrt(np.clip(1 - R2, 0, 1))
    L = np.array([-0.5, 0.62, 0.60]); L /= np.linalg.norm(L)     # light: top-left, toward viewer
    diff = np.clip(U * L[0] + V * L[1] + Z * L[2], 0, 1)
    shade = 0.26 + 0.80 * diff
    spec = np.clip(diff, 0, 1) ** 22                              # tight highlight
    tint = np.array(tint)
    rgb = np.clip(tint[None, None, :] * shade[..., None] + spec[..., None] * 0.85, 0, 1)
    alpha = np.clip((1.0 - np.sqrt(R2)) / 0.035, 0, 1)            # anti-aliased rim
    # soft depth halo behind
    ax.add_patch(Circle((cx, cy), r * 1.16, facecolor="#0b1a22", alpha=0.16, zorder=zorder - 1,
                        edgecolor="none"))
    ax.imshow(np.dstack([rgb, alpha]), extent=[cx - r, cx + r, cy - r, cy + r], origin="lower",
              zorder=zorder, interpolation="bilinear")
    ax.add_patch(Circle((cx, cy), r, facecolor="none", edgecolor="#16262f", lw=1.1, alpha=0.75,
                        zorder=zorder + 1))


def phase_curve(dwell):
    """One cycle of the actual gait's opening d(t), for the little phase trace."""
    b1 = -0.5 if dwell == "open" else 0.5
    ph = np.linspace(0, 1, 240)
    th = 2 * PI * ph + b1 * np.sin(2 * PI * ph)
    return ph, 1.0 + 0.35 * np.cos(th)


def draw_panel(fig, p, ext, lo, hi, fi, x0):
    """Render one panel at horizontal origin x0 (figure fraction). fi = frame index."""
    ac = p["accent"]; cx = x0 + 0.205
    nf = len(p["phase"]); frac = fi / (nf - 1)               # 0..1 through the shown cycles
    # --- header (three clean stacked lines, no overlap)
    fig.text(cx, 0.862, p["title"], ha="center", fontsize=17.5, color=INK,
             family="serif", weight="bold")
    fig.text(cx, 0.833, f"Deborah number   De = {p['De']}", ha="center", fontsize=11.5,
             color=MUTED, family="monospace")
    fig.text(cx, 0.806, f"the winning rhythm  {p['gait']}", ha="center", fontsize=13,
             color=ac, family="serif", weight="bold", style="italic")

    # --- the field + body
    axf = fig.add_axes([x0 + 0.028, 0.43, 0.355, 0.355])
    fld, ux, uy = p["fields"][fi], p["ux"][fi], p["uy"][fi]      # each (nx, ny)
    nx, ny = fld.shape
    X = np.linspace(ext[0], ext[1], nx); Y = np.linspace(ext[2], ext[3], ny)
    zf = np.clip((fld.T - lo) / (hi - lo), 0, 1)
    # (1) filled elastic-stress field, softened so the line-work reads on top
    axf.imshow(zf ** 0.72, origin="lower", extent=ext, cmap=CMAP, vmin=0, vmax=1,
               interpolation="bilinear", aspect="auto", alpha=0.92)
    # (2) dense stress contour lines -- the deforming "topography" of stored stress
    axf.contour(X, Y, zf, levels=np.linspace(0.08, 0.98, 15), colors="#f4fbff",
                linewidths=0.5, alpha=0.32, zorder=2)
    axf.contour(X, Y, zf, levels=np.linspace(0.08, 0.98, 15), colors="#0d3a55",
                linewidths=0.5, alpha=0.16, zorder=2)
    # (3) streamlines of the actual flow the swimmer drives -- deform through the stroke
    spd = np.sqrt(ux ** 2 + uy ** 2).T
    lw = 0.25 + 2.1 * np.clip(spd / (p["spdmax"] + 1e-9), 0, 1) ** 0.7
    axf.streamplot(X, Y, ux.T, uy.T, density=1.35, color="#12222b", linewidth=lw,
                   arrowsize=0.7, arrowstyle="-|>", zorder=3)
    # (4) the swimmer as two shaded, life-like beads on a rod
    d, xc = float(p["d"][fi]), float(p["xc"][fi])
    axf.plot([xc - d / 2, xc + d / 2], [0, 0], color="#243038", lw=3.0, alpha=.75, zorder=6,
             solid_capstyle="round")
    draw_sphere(axf, xc - d / 2, 0, 0.15, (0.96, 0.90, 0.76), zorder=8)
    draw_sphere(axf, xc + d / 2, 0, 0.27, (0.97, 0.93, 0.82), zorder=8)
    axf.set_xlim(ext[0], ext[1]); axf.set_ylim(ext[2], ext[3])
    axf.set_xticks([]); axf.set_yticks([])
    for s in axf.spines.values():
        s.set_color(LINE)
    axf.text(.025, .93, "flow streamlines over the stored elastic stress",
             transform=axf.transAxes, fontsize=8.3, color="#1b2c35", family="monospace", va="top",
             bbox=dict(boxstyle="round,pad=0.3", fc=PAPER, ec="none", alpha=0.7))

    # --- stroke-phase trace (shows WHERE it lingers)
    fig.text(x0 + 0.030, 0.400, "the stroke, in time  ·  " + ("dwells while OPEN"
             if p["dwell"] == "open" else "dwells while CLOSED"), fontsize=9.5,
             color=ac, family="monospace", va="center")
    axp = fig.add_axes([x0 + 0.028, 0.255, 0.355, 0.115])
    ph, dc = phase_curve(p["dwell"])
    now = p["phase"][fi] % 1.0
    band = (dc.max() - .18, dc.max() + .03) if p["dwell"] == "open" else (dc.min() - .03, dc.min() + .18)
    axp.axhspan(band[0], band[1], color=ac, alpha=.12)
    axp.plot(ph, dc, color=ac, lw=2.0)
    td = np.linspace(0, 1, 26, endpoint=False)             # equal-time dots bunch where it dawdles
    thd = 2 * PI * td + (-0.5 if p["dwell"] == "open" else 0.5) * np.sin(2 * PI * td)
    axp.plot(td, 1 + 0.35 * np.cos(thd), "o", color=ac, ms=2.6, alpha=.55)
    dn = 1 + 0.35 * np.cos(2 * PI * now + (-0.5 if p["dwell"] == "open" else 0.5) * np.sin(2 * PI * now))
    axp.plot(now, dn, "o", color=INK, ms=8, zorder=6, mec=PAPER, mew=1.5)
    axp.set_xlim(0, 1); axp.set_ylim(0.5, 1.5)
    axp.set_yticks([]); axp.set_xticks([]); axp.tick_params(length=0)
    for s in ("top", "right", "left"):
        axp.spines[s].set_visible(False)
    axp.spines["bottom"].set_color(LINE)
    axp.text(0.5, -0.16, "body wide  ·  ← one full stroke →  ·  body closed", transform=axp.transAxes,
             ha="center", fontsize=8, color=FAINT, family="monospace", va="top")

    # --- net-distance meter: the winning rhythm vs the other one, at their true net rates
    fig.text(x0 + 0.030, 0.185, "net distance swum", fontsize=9.5, color=INK, family="monospace")
    margin = 100 * (p["win"] / p["lose"] - 1)
    fig.text(x0 + 0.383, 0.185, f"winner +{margin:.0f}%", ha="right", fontsize=9.5,
             color=ac, family="monospace", weight="bold")
    axm = fig.add_axes([x0 + 0.028, 0.055, 0.355, 0.11]); axm.axis("off")
    for lane, (val, col, lab, al) in enumerate([
            (frac, ac, p["gait"].lower(), 1.0),
            (frac * (p["lose"] / p["win"]), "#c7bda8", p["other"], 1.0)]):
        y = 0.74 - lane * 0.52
        axm.add_patch(FancyBboxPatch((0, y - .085), 1.0, .17, boxstyle="round,pad=0,rounding_size=.06",
                      transform=axm.transAxes, facecolor="#efe9db", edgecolor="none"))
        axm.add_patch(FancyBboxPatch((0, y - .085), max(val, 1e-3), .17,
                      boxstyle="round,pad=0,rounding_size=.06", transform=axm.transAxes,
                      facecolor=col, edgecolor="none", alpha=al))
        axm.text(0.012, y, lab, transform=axm.transAxes, va="center", fontsize=9,
                 color="#fff" if lane == 0 else INK2,
                 family="monospace", weight="bold" if lane == 0 else "normal")


def render():
    panels, ext, lo, hi = load()
    nf = min(len(p["phase"]) for p in panels)
    os.makedirs(FR, exist_ok=True)
    for f in os.listdir(FR):
        os.remove(os.path.join(FR, f))
    print(f"rendering {nf} frames ...")
    for fi in range(nf):
        fig = plt.figure(figsize=(14.4, 8.1), dpi=100)
        fig.patch.set_facecolor(PAPER)
        fig.text(0.5, 0.955, "One swimmer.  Two fluids.  The best rhythm reverses.",
                 ha="center", fontsize=25, color=INK, family="serif", weight="bold")
        fig.text(0.5, 0.905, "A real spectral simulation — identical body, effort, path and period; "
                 "only the timing of the stroke differs between the two fluids.",
                 ha="center", fontsize=12.5, color=MUTED, family="serif")
        draw_panel(fig, panels[0], ext, lo, hi, fi, 0.0)
        draw_panel(fig, panels[1], ext, lo, hi, fi, 0.5)
        # centre divider + verdict
        fig.add_artist(plt.Line2D([0.5, 0.5], [0.08, 0.80], color=LINE, lw=1.2))
        fig.text(0.5, 0.5, "⟶\nreverses", ha="center", va="center", fontsize=11, color=HOT,
                 family="monospace", linespacing=1.4,
                 bbox=dict(boxstyle="round,pad=0.4", fc=PAPER, ec=HOT, lw=1))
        fig.text(0.5, 0.028, "Vizuara Research   ·   spectral Stokes–Oldroyd-B solver, "
                 "the same engine behind every number in the paper",
                 ha="center", fontsize=9.5, color=FAINT, family="monospace")
        fig.savefig(f"{FR}/f{fi:04d}.png", facecolor=PAPER)
        plt.close(fig)
    # poster = a frame where both bodies are mid-stroke
    import shutil
    shutil.copy(f"{FR}/f{nf//4:04d}.png", f"{OUT}/swimmer-gaits-poster.png")
    mp4 = f"{OUT}/swimmer-gaits.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{FR}/f%04d.png",
                    "-vf", "scale=1440:810,format=yuv420p", "-c:v", "libx264", "-crf", "18",
                    "-preset", "slow", "-movflags", "+faststart", mp4], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {mp4}  and  {OUT}/swimmer-gaits-poster.png  ({nf} frames @ {FPS}fps)")


if __name__ == "__main__":
    render()
