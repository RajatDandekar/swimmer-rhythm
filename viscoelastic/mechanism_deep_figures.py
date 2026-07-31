"""What sets De_c: the phase-lag mechanism, from the PDE time series. Diagnose first, then plot.

Reads mechanism_deep.json. Prints the phase lag phi(De), the drift ratio, and the elastic/viscous
split so the physical story can be checked before it is drawn. Then produces two publication
figures: (fig6) the lag mechanism, and (fig7) the contour sequence through the cycle at De_c.
"""
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

mpl.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 9,
                     "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True, "figure.dpi": 200})
PAPER, WEB = "paper/figs", "site/figures"
PI = np.pi
CO, CC, MAG, GRN = "#1a6fb0", "#d06a1c", "#b3006b", "#2a8"
DIV = LinearSegmentedColormap.from_list("div", [
    "#08306b", "#4292c6", "#c6dbef", "#ffffff", "#fdd0a2", "#e6550d", "#7f2704"])
WX, WY = 1.55, 0.88


def fundamental_lag(up, d, dt):
    """Phase of the polymer velocity relative to the shape, at the fundamental. Positive = lag."""
    n = len(up); t = np.arange(n) * dt
    cu = np.trapezoid(np.array(up) * np.exp(-1j * t), t)
    cd = np.trapezoid((np.array(d) - np.mean(d)) * np.exp(-1j * t), t)
    return float(np.angle(cu * np.conj(cd)))


def analyse():
    D = json.load(open("mechanism_deep.json"))
    sweep = [r for r in D["sweep"] if r.get("ok")]
    des = sorted(set(r["lam"] for r in sweep))
    get = lambda De, b1: next(r for r in sweep if abs(r["lam"] - De) < 1e-9
                              and np.sign(r["b1"]) == np.sign(b1))
    print(f"{'De':>6} {'dx(+b)':>11} {'dx(-b)':>11} {'ratio':>7} "
          f"{'lag+ (deg)':>10} {'lag- (deg)':>10}")
    rows = []
    for De in des:
        p, m = get(De, +1), get(De, -1)
        lp = np.degrees(fundamental_lag(p["up"], p["d"], p["dt"]))
        lm = np.degrees(fundamental_lag(m["up"], m["d"], m["dt"]))
        ratio = abs(p["dx"]) / abs(m["dx"])
        rows.append(dict(De=De, dxp=p["dx"], dxm=m["dx"], ratio=ratio, lagp=lp, lagm=lm))
        print(f"{De:>6.2f} {p['dx']:>11.4e} {m['dx']:>11.4e} {ratio:>7.4f} {lp:>10.1f} {lm:>10.1f}")
    # crossover from the ratio
    for a, b in zip(rows, rows[1:]):
        if (a["ratio"] - 1) * (b["ratio"] - 1) < 0:
            la, lb = np.log(a["De"]), np.log(b["De"])
            dec = float(np.exp(la + (lb - la) * (1 - a["ratio"]) / (b["ratio"] - a["ratio"])))
            # lag at the crossover (mean of the two rhythms, interpolated)
            f = (np.log(dec) - la) / (lb - la)
            lagc = 0.5 * ((a["lagp"] + (b["lagp"] - a["lagp"]) * f) +
                          (a["lagm"] + (b["lagm"] - a["lagm"]) * f))
            print(f"\n  drift crossover De_c = {dec:.3f}")
            print(f"  polymer phase lag there = {lagc:.1f} deg   "
                  f"(n*De with lag=45deg would give n={np.tan(np.radians(45))/dec:.2f})")
            return rows, dec, lagc
    return rows, None, None


def fig_lag(rows, dec, lagc):
    des = np.array([r["De"] for r in rows])
    ratio = np.array([r["ratio"] for r in rows])
    lagp = np.array([r["lagp"] for r in rows])
    fig, ax = plt.subplots(1, 3, figsize=(6.5, 2.25), gridspec_kw=dict(wspace=0.5))
    # (a) phase lag vs De
    ax[0].plot(des, lagp, "o-", color=MAG, ms=3, lw=1.3)
    if dec:
        ax[0].axvline(dec, color="0.5", ls=":", lw=0.9)
        ax[0].axhline(lagc, color="0.5", ls=":", lw=0.9)
        ax[0].plot(dec, lagc, "o", color="k", ms=4)
        ax[0].text(dec * 1.05, lagc - 12, rf"$De_c={dec:.2f}$", fontsize=7)
    ax[0].set_xscale("log"); ax[0].set_xlabel("$De$"); ax[0].set_ylabel(r"polymer lag (deg)")
    ax[0].set_title("(a) stress lags the shape", loc="left", fontsize=8)
    # (b) the reversal (ratio)
    ax[1].axhline(1, color="0.6", lw=0.8, ls="--")
    if dec:
        ax[1].axvline(dec, color=MAG, lw=0.9, ls=":")
    ax[1].plot(des, ratio, "-", color="0.3", lw=1.0)
    ax[1].scatter(des, ratio, c=[CC if q > 1 else CO for q in ratio], s=18, zorder=3,
                  edgecolors="w", linewidths=0.5)
    ax[1].set_xscale("log"); ax[1].set_xlabel("$De$")
    ax[1].set_ylabel(r"$|\Delta x_{\rm c}|/|\Delta x_{\rm o}|$")
    ax[1].set_title("(b) the reversal", loc="left", fontsize=8)
    # (c) Lissajous: polymer velocity vs shape at De_c, both rhythms
    D = json.load(open("mechanism_deep.json"))
    sweep = [r for r in D["sweep"] if r.get("ok")]
    Dtarget = min((r["lam"] for r in sweep), key=lambda x: abs(x - (dec or 0.81)))
    for b1, c in ((+0.5, CC), (-0.5, CO)):
        r = next(x for x in sweep if abs(x["lam"] - Dtarget) < 1e-9
                 and np.sign(x["b1"]) == np.sign(b1))
        d = np.array(r["d"]) - np.mean(r["d"]); up = np.array(r["up"])
        ax[2].plot(d / d.max(), up / np.abs(up).max(), color=c, lw=1.2)
    ax[2].set_xlabel(r"shape $d-\bar d$ (norm.)"); ax[2].set_ylabel(r"$U_p$ (norm.)")
    ax[2].set_title(rf"(c) hysteresis at $De\!\approx\!{Dtarget:.2f}$", loc="left", fontsize=8)
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    for a in (ax[0], ax[1]):
        a.set_xlim(0.27, 2.3)
        a.xaxis.set_major_locator(FixedLocator([0.3, 0.5, 1.0, 2.0]))
        a.xaxis.set_major_formatter(FixedFormatter(["0.3", "0.5", "1", "2"]))
        a.xaxis.set_minor_locator(NullLocator())
    for d in (PAPER, WEB):
        os.makedirs(d, exist_ok=True)
    fig.savefig(f"{PAPER}/fig6_lag.pdf", bbox_inches="tight")
    fig.savefig(f"{WEB}/fig6_lag.png", bbox_inches="tight", dpi=200)
    plt.close(fig); print("  fig6_lag: pdf+png")


def fig_contour_movie():
    D = json.load(open("mechanism_deep.json"))
    movie = [r for r in D["movie"] if r.get("ok")]
    ths = D["movie_th"]
    De = min(D["movie_de"], key=lambda x: abs(x - 0.81))
    getp = next(r for r in movie if abs(r["lam"] - De) < 1e-9 and r["b1"] > 0)
    getm = next(r for r in movie if abs(r["lam"] - De) < 1e-9 and r["b1"] < 0)
    keys = sorted(getp["caps"], key=float)
    diffs = [np.array(getp["caps"][k]["f"]) - np.array(getm["caps"][k]["f"]) for k in keys]
    vm = float(np.percentile(np.abs(np.concatenate([d.ravel() for d in diffs])), 97))
    nx, ny = diffs[0].shape
    XX, YY = np.meshgrid(np.linspace(-WX, WX, nx), np.linspace(-WY, WY, ny), indexing="ij")
    n = len(keys)
    fig, axes = plt.subplots(1, n, figsize=(6.5, 1.55))
    for j, (k, ax) in enumerate(zip(keys, axes)):
        cf = ax.contourf(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 15), cmap=DIV,
                         extend="both")
        cap = getp["caps"][k]; dd, xc = cap["d"], cap["xc"]
        for xb, rr, col in ((xc - dd / 2, 0.12, MAG), (xc + dd / 2, 0.2, CC)):
            ax.add_patch(plt.Circle((xb, 0), rr, facecolor=col, ec="k", lw=0.5, zorder=5))
        ax.set_aspect("equal"); ax.set_xlim(-WX, WX); ax.set_ylim(-WY, WY)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(rf"$\theta={float(k):.2f}\pi$", fontsize=7)
    fig.suptitle(rf"Stress-difference between the two rhythms through one cycle, "
                 rf"$De={De:.2f}\approx De_c$", fontsize=8.5, y=1.06)
    fig.subplots_adjust(wspace=0.08)
    for d in (PAPER, WEB):
        os.makedirs(d, exist_ok=True)
    fig.savefig(f"{PAPER}/fig7_movie.pdf", bbox_inches="tight")
    fig.savefig(f"{WEB}/fig7_movie.png", bbox_inches="tight", dpi=200)
    plt.close(fig); print("  fig7_movie: pdf+png")


if __name__ == "__main__":
    rows, dec, lagc = analyse()
    if "--figs" in sys.argv:
        fig_lag(rows, dec, lagc)
        fig_contour_movie()
