"""Figure 5, done properly: three methods, one reversal — JFM style, in matplotlib.

Two panels.
 (a) The reversal transition measured three ways on a shared Deborah axis: SEARCH (full PDE)
     and THEORY (Fourier algebra) as two curves of the closed-over-open advantage, each rising
     through zero; the LEARNING agent as a strategy strip that flips colour at its own crossover.
     A shaded band marks where all three cluster.
 (b) The money shot: rescale the Deborah number by each method's own crossover and the two
     independent transition curves collapse onto a single master curve. The agent's crossover
     sits at unity by construction, marked.

Honest by construction: the three do not agree to three digits (search 0.81, theory 0.61,
learning 0.86); they agree that the optimum flips, cluster near De~0.8, and share one
transition shape. The agent contributes a crossover LOCATION, not a curve, because only the
sign of its learned parameter is robust -- so it is drawn as a location, never as a fake curve.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import theory_analysis as TH

mpl.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 9,
                     "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True, "figure.dpi": 200})
PAPER, WEB = "paper/figs", "site/figures"
CO, CC = "#1a6fb0", "#d06a1c"          # open (cool), closed (warm)
KSEARCH, KTHEORY, KRL = "#111111", "#1a8f7a", "#b3006b"
BAND = "#b3006b"


def zero_cross(x, y):
    for a, b, ya, yb in zip(x, x[1:], y, y[1:]):
        if ya * yb < 0:
            return float(np.exp(np.log(a) + (np.log(b) - np.log(a)) * (0 - ya) / (yb - ya)))
    return None


def load_signals():
    r = [x for x in json.load(open("crossover_results.json")) if x.get("ok")]
    d = {}
    for x in r:
        d.setdefault(x["lam"], {})[x["b1"]] = x["per_cycle"][-1]
    sde = np.array(sorted(d))
    sg = np.array([abs(d[D][0.5]) / abs(d[D][-0.5]) for D in sde]) - 1.0
    tde = np.exp(np.linspace(np.log(0.2), np.log(3), 60))
    tg = np.array([TH.Q_of(-0.5, D) - TH.Q_of(0.5, D) for D in tde])
    c = json.load(open("rl_ctrl_results.json"))
    rde = np.array(sorted(float(k) for k in c))
    rb = np.array([c[str(D)]["best"]["b1"] for D in rde])
    return (sde, sg, zero_cross(sde, sg)), (tde, tg, TH.crossover(0.5)), \
           (rde, rb, zero_cross(rde, rb))


def main():
    (sde, sg, Dcs), (tde, tg, Dct), (rde, rb, Dcr) = load_signals()
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.75), gridspec_kw=dict(wspace=0.34))

    # ---------- (a) three methods on a shared De axis ----------
    a = ax[0]
    a.axhspan(-1.15, -1.4, color="0.96", zorder=0)         # strip background
    a.axvspan(0.6, 0.9, color=BAND, alpha=0.06, zorder=0)
    a.axhline(0, color="0.55", lw=0.8)
    sgn = sg / np.max(np.abs(sg))
    tgn = tg / np.max(np.abs(tg))
    a.plot(sde, sgn, "-", color=KSEARCH, lw=1.7, zorder=4, label="search")
    a.plot(sde, sgn, "o", color=KSEARCH, ms=3, zorder=5)
    a.plot(tde, tgn, "--", color=KTHEORY, lw=1.7, zorder=4, label="theory")
    # RL strategy strip
    ys = -1.27
    for D, b in zip(rde, rb):
        a.plot(D, ys, "s", ms=5, color=(CC if b > 0 else CO), mec="w", mew=0.5, zorder=6)
    a.text(0.205, ys + 0.14, "learning agent's choice", fontsize=6.2, va="bottom",
           ha="left", color="0.45")
    # crossover ticks
    for Dc, c, lab, dy, dx in ((Dct, KTHEORY, "0.61", -0.72, 1.00),
                               (Dcs, KSEARCH, "0.81", -0.44, 0.92),
                               (Dcr, KRL, "0.86", -0.18, 1.07)):
        a.plot([Dc, Dc], [-0.05, 0.05], color=c, lw=1.5, zorder=7)
        a.annotate(r"$De_c\!=\!$" + lab, (Dc, 0), (Dc * dx, dy), fontsize=6.6, color=c,
                   ha="center", va="center",
                   arrowprops=dict(arrowstyle="-", color=c, lw=0.6))
    a.set_xscale("log"); a.set_xlim(0.2, 3); a.set_ylim(-1.42, 1.15)
    a.set_xlabel(r"Deborah number $De$")
    a.set_ylabel(r"linger-closed advantage (norm.)")
    a.set_title("(a) the reversal, three ways", loc="left", fontsize=8.5)
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    a.xaxis.set_major_locator(FixedLocator([0.2, 0.5, 1, 2]))
    a.xaxis.set_major_formatter(FixedFormatter(["0.2", "0.5", "1", "2"]))
    a.xaxis.set_minor_locator(NullLocator())
    a.text(0.735, 1.02, "reversal", fontsize=6.8, color=BAND, ha="center")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=KSEARCH, lw=1.7, label="search"),
               Line2D([], [], color=KTHEORY, lw=1.7, ls="--", label="theory"),
               Line2D([], [], color=CO, marker="s", ls="none", ms=5, mec="w", mew=0.4,
                      label="agent: open"),
               Line2D([], [], color=CC, marker="s", ls="none", ms=5, mec="w", mew=0.4,
                      label="agent: closed")]
    a.legend(handles=handles, frameon=False, fontsize=6.4, loc="upper left",
             handlelength=1.4, borderaxespad=0.5, labelspacing=0.32)

    # ---------- (b) collapse: rescale De by each crossover ----------
    b = ax[1]
    b.axhline(0, color="0.55", lw=0.8); b.axvline(1, color="0.6", lw=0.8, ls=":")
    # amplitude-normalise each to unit value at De/De_c = 2 so shapes overlay
    def rescaled(x, y, Dc):
        xr = x / Dc; yn = y / np.max(np.abs(y))
        ref = np.interp(2.0, xr, yn)
        return xr, yn / (abs(ref) if abs(ref) > 1e-6 else 1)
    xs, ys2 = rescaled(sde, sg, Dcs)
    xt, yt2 = rescaled(tde, tg, Dct)
    b.plot(xs, ys2, "-", color=KSEARCH, lw=1.7, label="search", zorder=4)
    b.plot(xs, ys2, "o", color=KSEARCH, ms=3, zorder=5)
    b.plot(xt, yt2, "--", color=KTHEORY, lw=1.7, label="theory", zorder=4)
    b.plot(1, 0, "s", ms=7, color=KRL, mec="w", mew=0.8, zorder=6, label="learning")
    b.annotate("agent\ncrossover", (1, 0), (1.35, -0.55), fontsize=6.8, color=KRL,
               ha="left", arrowprops=dict(arrowstyle="-", color=KRL, lw=0.6))
    b.set_xscale("log"); b.set_xlim(0.35, 3.2); b.set_ylim(-1.25, 1.35)
    b.set_xlabel(r"$De\,/\,De_c$  (each method's own crossover)")
    b.set_ylabel(r"transition (norm.)")
    b.set_title("(b) the transitions collapse", loc="left", fontsize=8.5)
    b.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 3]))
    b.xaxis.set_major_formatter(FixedFormatter(["0.5", "1", "2", "3"]))
    b.xaxis.set_minor_locator(NullLocator())
    b.legend(frameon=False, fontsize=7, loc="lower right", handlelength=1.6)

    for d in (PAPER, WEB):
        os.makedirs(d, exist_ok=True)
    fig.savefig(f"{PAPER}/fig5_compare.pdf", bbox_inches="tight")
    fig.savefig(f"{WEB}/fig5_compare.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  crossovers: search {Dcs:.3f}, theory {Dct:.3f}, learning {Dcr:.3f}")
    print("  wrote fig5_compare.pdf + png")


if __name__ == "__main__":
    main()
