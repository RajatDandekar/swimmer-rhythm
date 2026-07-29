"""JFM-style mechanism figures: WHERE the reversal comes from, in space and in the cycle.

The collapse says the reversal sits at De <theta'^2> = K. It does not say why. Two things have
to be shown to make the mechanism concrete rather than asserted:

[1] IN SPACE. The two rhythms are geometrically identical at matched shape, so the difference of
    their stress fields, trace(C-I)|_+b - trace(C-I)|_-b, isolates exactly what the fluid
    remembers differently. Plotted at three Deborah numbers spanning the crossover, the sign
    structure of that difference should INVERT as De passes De_c.

[2] IN THE CYCLE. Net displacement is the integral of U_poly over one stroke. Plotting the
    running integral against phase shows where in the stroke each rhythm gains and loses, and
    the final value is the answer. Below De_c one curve ends higher, above it the other does --
    and the crossing is visible as the two curves swapping which finishes ahead.

Plus the quantitative diagnostic that ties it to the theory: the PHASE LAG of the polymer force
behind the shape. A first-order filter with time constant lambda driven at frequency omega lags
by arctan(lambda*omega). If the polymer is responding to a mean-square frequency <theta'^2>
rather than the nominal one, the lag should track arctan(De <theta'^2>) rather than arctan(De).
"""
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from solver2 import Solver2

PI = np.pi
KS = np.array([1.0, 2.0, 3.0])
D0, AMP = 1.0, 0.35
N, L, BRINK = 256, 4 * PI, 0.5
NSTEPS, NCYC = 600, 6
DES = [0.40, 0.81, 2.00]                       # below / at / above the crossover
OUT = "site/figures"

INK, MUTED, GRID = "#0f1c26", "#5b7280", "#dbe4ea"
CYAN, ORANGE, MAGENTA, GREEN = "#1a9fd4", "#ef8f1c", "#e6009e", "#12a594"
# diverging: cyan (the -b rhythm stores more) -- white -- orange (the +b rhythm stores more)
DIV = LinearSegmentedColormap.from_list("div", [
    "#0d5f80", "#1a9fd4", "#8ed4ee", "#ffffff", "#f8cf95", "#ef8f1c", "#a35c06"])

WX, WY = 1.55, 0.88


def crop(f):
    x = np.linspace(0, L, N, endpoint=False) - L / 2
    return f[np.ix_(np.abs(x) <= WX, np.abs(x) <= WY)]


def grid_xy():
    x = np.linspace(0, L, N, endpoint=False) - L / 2
    return x[np.abs(x) <= WX], x[np.abs(x) <= WY]


def run(b1, lam, thetas):
    """One rhythm at one De. Returns fields at matched shape, plus U_poly over the last cycle."""
    b = np.array([b1, 0.0, 0.0]); ph = np.zeros(3)

    def stroke(t):
        th = t + float(np.sum(b * np.sin(KS * t + ph)))
        dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
        return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

    s = Solver2(N=N, L=L, brink=BRINK, lam=lam, stroke=stroke)
    T = 2 * PI; dt = T / NSTEPS
    tg = np.arange(NSTEPS) * dt
    th_of_t = tg + b1 * np.sin(tg)
    want = {int(np.argmin(np.abs(th_of_t - th))): th for th in thetas}
    caps, up_hist, d_hist, last0 = {}, [], [], 0.0
    for c in range(NCYC):
        if c == NCYC - 1:
            last0 = s.acc_poly
        for n in range(NSTEPS):
            t = n * dt
            if c == NCYC - 1 and n in want:
                d, _ = s.stroke(t)
                caps[want[n]] = dict(f=(s.Cxx + s.Cyy - 2.0).copy(), d=d, xc=s.xc)
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
            if c == NCYC - 1:
                up_hist.append(0.5 * (Up1 + Up2)); d_hist.append(s.stroke(t)[0])
    return caps, np.array(up_hist), np.array(d_hist), s.acc_poly - last0, dt


def phase_lag(up, d, dt):
    """Lag of the polymer response behind the shape, from the fundamental Fourier component.
    Positive = the fluid is responding to what the swimmer did earlier."""
    n = len(up)
    t = np.arange(n) * dt
    w = 1.0
    cu = np.trapezoid(up * np.exp(-1j * w * t), t)
    cd = np.trapezoid((d - d.mean()) * np.exp(-1j * w * t), t)
    return float(np.angle(cu / cd))


def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    thetas = [0.97 * PI]                        # fully closed: where the two differ most
    data = {}
    for De in DES:
        print(f"  De = {De} ...", flush=True)
        cp, upP, dP, dxP, dt = run(+0.5, De, thetas)
        cm, upM, dM_, dxM, _ = run(-0.5, De, thetas)
        data[De] = dict(cp=cp, cm=cm, upP=upP, upM=upM, dP=dP, dM=dM_,
                        dxP=dxP, dxM=dxM, dt=dt,
                        lagP=phase_lag(upP, dP, dt), lagM=phase_lag(upM, dM_, dt))
        print(f"     dx(+b) {dxP:+.4e}   dx(-b) {dxM:+.4e}   ratio {abs(dxP/dxM):.4f}"
              f"   lag(+b) {np.degrees(data[De]['lagP']):+.1f} deg", flush=True)

    np.savez_compressed(
        f"{OUT}/mechanism_cache.npz",
        **{f"{k}_{De}": v for De in DES for k, v in
           (("cp", data[De]["cp"][thetas[0]]["f"]), ("cm", data[De]["cm"][thetas[0]]["f"]),
            ("upP", data[De]["upP"]), ("upM", data[De]["upM"]),
            ("meta", np.array([data[De]["cp"][thetas[0]]["d"],
                               data[De]["cp"][thetas[0]]["xc"], data[De]["dxP"],
                               data[De]["dxM"], data[De]["dt"]])))})
    print("  cached raw fields -> mechanism_cache.npz (re-plot without re-running)",
          flush=True)

    xg, yg = grid_xy()
    XX, YY = np.meshgrid(xg, yg, indexing="ij")

    fig = plt.figure(figsize=(13.4, 7.6))
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1.0], hspace=0.42, wspace=0.22,
                          left=0.065, right=0.975, top=0.885, bottom=0.085)

    # ---- row 1: difference of the stress fields, at matched shape
    diffs = [crop(data[De]["cp"][thetas[0]]["f"]) - crop(data[De]["cm"][thetas[0]]["f"])
             for De in DES]
    vm = max(np.abs(d).max() for d in diffs) * 0.72
    for j, De in enumerate(DES):
        ax = fig.add_subplot(gs[0, j])
        cf = ax.contourf(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 21), cmap=DIV,
                         extend="both")
        ax.contour(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 11), colors=INK,
                   linewidths=0.4, alpha=0.32)
        cap = data[De]["cp"][thetas[0]]
        d, xc = cap["d"], cap["xc"]
        for xb, r, col in ((xc - d / 2, 0.13, MAGENTA), (xc + d / 2, 0.24, ORANGE)):
            ax.add_patch(plt.Circle((xb, 0), r, facecolor=col, edgecolor=INK,
                                    linewidth=1.2, zorder=6))
        ax.plot([xc - d / 2, xc + d / 2], [0, 0], color=INK, lw=1.2, alpha=0.6, zorder=5)
        ax.set_xlim(-WX, WX); ax.set_ylim(-WY, WY)
        ax.set_aspect("equal")
        ax.set_title(("$De = %.2f$   " % De) +
                     ("(below $De_c$)" if De < 0.8 else
                      ("(at $De_c$)" if De < 1.0 else "(above $De_c$)")),
                     fontsize=11.5, color=INK, pad=8)
        ax.tick_params(labelsize=8.5, colors=MUTED, length=3)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        if j == 0:
            ax.set_ylabel("$y$", fontsize=11, color=INK)
        ax.set_xlabel("$x$", fontsize=11, color=INK)
    cax = fig.add_axes([0.30, 0.955, 0.40, 0.016])
    cb = fig.colorbar(cf, cax=cax, orientation="horizontal")
    cb.set_label("stored elastic stress, difference between the two rhythms"
                 r"      $\mathrm{tr}(C-I)_{+b}-\mathrm{tr}(C-I)_{-b}$",
                 fontsize=9.5, color=INK, labelpad=7)
    cb.ax.tick_params(labelsize=8, colors=MUTED)
    cb.outline.set_edgecolor(GRID)

    # ---- row 2: running displacement through the cycle
    for j, De in enumerate(DES):
        ax = fig.add_subplot(gs[1, j])
        D = data[De]; dt = D["dt"]
        ph = np.arange(len(D["upP"])) * dt / (2 * PI)
        cumP = np.cumsum(D["upP"]) * dt
        cumM = np.cumsum(D["upM"]) * dt
        ax.axhline(0, color=GRID, lw=1)
        ax.plot(ph, cumP * 1e3, color=ORANGE, lw=2.2, label="lingers closed")
        ax.plot(ph, cumM * 1e3, color=CYAN, lw=2.2, label="lingers open")
        ax.plot([1], [cumP[-1] * 1e3], "o", color=ORANGE, ms=6)
        ax.plot([1], [cumM[-1] * 1e3], "o", color=CYAN, ms=6)
        win = "closed" if abs(cumP[-1]) > abs(cumM[-1]) else "open"
        ax.text(0.03, 0.06, "wins: lingers %s" % win, transform=ax.transAxes,
                fontsize=10, color=ORANGE if win == "closed" else CYAN, weight="bold")
        ax.set_xlabel("phase through the stroke", fontsize=10, color=INK)
        if j == 0:
            ax.set_ylabel(r"displacement so far  $\times 10^{3}$", fontsize=10, color=INK)
            ax.legend(frameon=False, fontsize=9.5, loc="upper left")
        ax.tick_params(labelsize=8.5, colors=MUTED, length=3)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        ax.set_xlim(0, 1.02)
    fig.savefig(f"{OUT}/mechanism.png", dpi=170, facecolor="white")
    print(f"wrote {OUT}/mechanism.png")

    out = {str(De): dict(dxP=float(data[De]["dxP"]), dxM=float(data[De]["dxM"]),
                         ratio=float(abs(data[De]["dxP"] / data[De]["dxM"])),
                         lagP_deg=float(np.degrees(data[De]["lagP"])),
                         lagM_deg=float(np.degrees(data[De]["lagM"])))
           for De in DES}
    json.dump(out, open(f"{OUT}/mechanism.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
