"""Render the polymer stress field around the swimmer -- the picture of WHY it moves.

This is the one figure that shows the mechanism rather than asserting it. Two rhythms that are
identical in excursion, effort, peak rate and period, differing only in when the swimmer
hurries, produce visibly different elastic stress fields. That asymmetry in the field IS the
31.5% difference in swimming speed.

Renders trace(C - I), the polymer stretch, which is zero in a relaxed fluid and grows wherever
the flow has been stretching polymer faster than it can relax.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from solver2 import Solver2

PI = np.pi
KS = np.array([1.0, 2.0, 3.0])
D0, AMP = 1.0, 0.35
# N=448 for the picture, not 192. The integrated results are grid-converged (N 192->288 moves
# them <0.1%), but the regularised beads span only ~3 cells at N=192 and that under-resolution
# shows up as visible ringing in a pointwise field plot. Harmless to the science, ugly and
# misleading in a figure.
N, L, BRINK, LAM = 448, 4 * PI, 0.5, 3.0
NSTEPS, NCYC = 600, 6

OUT = "site/figures"

# the deep-teal -> gold palette the site uses
# light sequential: relaxed fluid is white, taut fluid is deep ink
CMAP = LinearSegmentedColormap.from_list("stretch", [
    "#ffffff", "#eaf5fb", "#c2e2f2", "#8ecde8", "#4fb2da",
    "#1a9fd4", "#1370a0", "#0f3550"])


def make_stroke(b1, phi):
    b = np.array([b1, 0.0, 0.0]); ph = np.array([phi, 0.0, 0.0])

    def stroke(t):
        th = t + float(np.sum(b * np.sin(KS * t + ph)))
        dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
        return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)
    return stroke


def run_and_capture(b1, phi, thetas):
    """Run to a periodic state, then capture the stretch field at matched SHAPE.

    Capture is keyed on theta, not on t. The two rhythms reach any given opening at different
    moments -- that is the whole point of them -- so comparing them at equal time compares
    different configurations and shows nothing. At equal theta both swimmers are in the
    *identical* geometric configuration moving the *same* direction, so any difference in the
    surrounding stress is purely what the fluid remembers about how they got there.

    Returns the displacement of the LAST cycle alone. acc_poly is a running total, so reporting
    it directly mixes in the start-up transient -- that is how this figure first came out at
    ratio 1.356 instead of the converged 1.3145.
    """
    s = Solver2(N=N, L=L, brink=BRINK, lam=LAM, stroke=make_stroke(b1, phi))
    T = 2 * PI; dt = T / NSTEPS
    caps = {}
    last_cycle_start = 0.0
    # theta(t) = t + b1 sin(t+phi) is monotone; find the step nearest each target theta
    tg = np.arange(NSTEPS) * dt
    th_of_t = tg + b1 * np.sin(tg + phi)
    want = {int(np.argmin(np.abs(th_of_t - th))): th for th in thetas}
    for c in range(NCYC):
        if c == NCYC - 1:
            last_cycle_start = s.acc_poly
        for n in range(NSTEPS):
            t = n * dt
            if c == NCYC - 1 and n in want:
                d, _ = s.stroke(t)
                caps[want[n]] = dict(field=(s.Cxx + s.Cyy - 2.0).copy(),
                                     d=d, xc=s.xc, phase=n / NSTEPS, theta=want[n])
            # RK2, mirroring Solver2.run
            C0 = (s.Cxx.copy(), s.Cxy.copy(), s.Cyy.copy()); xc0 = s.xc
            u1x, u1y, Us1, Up1 = s.velocity_field(t)
            k1 = s.dCdt(u1x, u1y)
            s.Cxx = C0[0] + dt * k1[0]; s.Cxy = C0[1] + dt * k1[1]
            s.Cyy = C0[2] + dt * k1[2]; s.xc = xc0 + dt * (Us1 + Up1)
            u2x, u2y, Us2, Up2 = s.velocity_field(t + dt)
            k2 = s.dCdt(u2x, u2y)
            s.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0])
            s.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
            s.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
            s.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
            s.acc_poly += 0.5 * dt * (Up1 + Up2)
            s.acc_stokes += 0.5 * dt * (Us1 + Us2)
    return caps, s.acc_poly - last_cycle_start


WX, WY = 1.7, 0.95        # wide crop: the swimmer is horizontal, so the box should be too


def crop(f):
    """Window around the swimmer, wider than tall."""
    x = np.linspace(0, L, N, endpoint=False) - L / 2
    return f[np.ix_(np.abs(x) <= WX, np.abs(x) <= WY)]


def panel(ax, cap, lo, hi, title):
    sub = crop(cap["field"])
    # subtract the background stretch so relaxed fluid reads as truly dark, then a mild gamma
    # to lift structure. Without the subtraction the whole frame washes out, because the fluid
    # carries a roughly uniform baseline stretch everywhere.
    z = np.clip((sub.T - lo) / (hi - lo), 0, 1) ** 0.62
    ax.imshow(z, origin="lower", extent=[-WX, WX, -WY, WY], cmap=CMAP,
              vmin=0, vmax=1, interpolation="bilinear")
    d, xc = cap["d"], cap["xc"]
    for xb, r, col in ((xc - d / 2, 0.14, "#e6009e"), (xc + d / 2, 0.26, "#ef8f1c")):
        ax.add_patch(plt.Circle((xb, 0), r, facecolor=col, edgecolor="#0f1c26",
                                linewidth=1.6, zorder=5, alpha=0.95))
    ax.plot([xc - d / 2, xc + d / 2], [0, 0], color="#0f1c26", lw=1.4, alpha=0.5, zorder=4)
    ax.set_title(title, color="#33475a", fontsize=10, pad=6)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color("#c9d6de")


LABELS = [(0.30 * PI, "opening out"), (0.62 * PI, "half closed"),
          (0.97 * PI, "fully closed"), (1.45 * PI, "opening again")]


def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    thetas = [t for t, _ in LABELS]
    print("running linger-closed (b1=+0.5) ...")
    capA, dxA = run_and_capture(+0.5, 0.0, thetas)
    print("running linger-open   (b1=-0.5) ...")
    capB, dxB = run_and_capture(-0.5, 0.0, thetas)

    allc = np.concatenate([crop(c["field"]).ravel()
                           for c in list(capA.values()) + list(capB.values())])
    lo = float(np.percentile(allc, 55.0))       # background stretch -> black
    hi = float(np.percentile(allc, 99.7))       # shared by both rows, so rows are comparable
    print(f"stretch in crop: p55 {lo:.3e}  p99.7 {hi:.3e}  max {allc.max():.3e}")

    fig, axes = plt.subplots(2, 4, figsize=(13.6, 5.4))
    fig.patch.set_facecolor("#ffffff")
    for j, (th, lab) in enumerate(LABELS):
        panel(axes[0, j], capA[th], lo, hi, "")
        panel(axes[1, j], capB[th], lo, hi, "")
        axes[0, j].set_title(lab, color="#33475a", fontsize=10.5, pad=7)
        for i, cap in ((0, capA[th]), (1, capB[th])):
            axes[i, j].text(0.5, 0.055, f"opening {cap['d']:.3f}", transform=axes[i, j].transAxes,
                            ha="center", color="#94a8b4", fontsize=8.5, family="monospace")
    axes[0, 0].set_ylabel("lingers CLOSED\nfaster swimmer", color="#c47408",
                          fontsize=10.5, labelpad=10)
    axes[1, 0].set_ylabel("lingers OPEN\nslower swimmer", color="#0d5f80",
                          fontsize=10.5, labelpad=10)
    fig.suptitle("Elastic stress stored in the fluid   ·   both swimmers shown in the "
                 "SAME configurations, reached by different rhythms",
                 color="#0f1c26", fontsize=12.5, y=0.972)
    fig.text(0.5, 0.028, f"net displacement per cycle:    lingers-closed {dxA:.4e}"
                         f"        lingers-open {dxB:.4e}        ratio {abs(dxA/dxB):.4f}",
             ha="center", color="#5b7280", fontsize=10.5, family="monospace")
    plt.tight_layout(rect=[0.015, 0.055, 1, 0.945])
    fig.savefig(f"{OUT}/stress_field.png", dpi=170, facecolor="#ffffff")
    print(f"wrote {OUT}/stress_field.png   dxA={dxA:.4e} dxB={dxB:.4e} "
          f"ratio={abs(dxA/dxB):.4f}")
    json.dump(dict(dx_closed=float(dxA), dx_open=float(dxB),
                   ratio=float(abs(dxA / dxB)), N=N), open(f"{OUT}/stress_field.json", "w"),
              indent=1)


if __name__ == "__main__":
    main()
