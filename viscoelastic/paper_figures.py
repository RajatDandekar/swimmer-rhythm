"""Publication-quality figures for the JFM-Rapids paper (and the professional web figures).

All data is read from the result JSONs written by the Modal runs -- nothing typed by hand.
Outputs high-res PDF (for LaTeX) and PNG (for the website) into paper/figs/ and site/figures/.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib as mpl

mpl.rcParams.update({
    "font.family": "serif", "mathtext.fontset": "cm", "font.size": 9,
    "axes.linewidth": 0.8, "axes.labelsize": 9, "axes.titlesize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True, "figure.dpi": 200,
})

PAPER = "paper/figs"
WEB = "site/figures"
PI = np.pi
INK = "#111111"
CO, CC = "#1a6fb0", "#d06a1c"     # open (cool), closed (warm) -- print-safe
MAG = "#b3006b"
DIV = LinearSegmentedColormap.from_list("div", [
    "#08306b", "#4292c6", "#c6dbef", "#ffffff", "#fdd0a2", "#e6550d", "#7f2704"])


def save(fig, name):
    for d in (PAPER, WEB):
        os.makedirs(d, exist_ok=True)
    fig.savefig(f"{PAPER}/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"{WEB}/{name}.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print(f"  {name}: pdf+png")


# ------------------------------------------------------------------ Fig 1: reversal
def fig_reversal():
    r = [x for x in json.load(open("crossover_results.json")) if x.get("ok")]
    d = {}
    for x in r:
        d.setdefault(x["lam"], {})[x["b1"]] = x["per_cycle"][-1]
    des = np.array(sorted(d))
    ratio = np.array([abs(d[De][0.5]) / abs(d[De][-0.5]) for De in des])

    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.55), gridspec_kw=dict(wspace=0.32))
    # (a) the two rhythms on the reparametrisation axis
    t = np.linspace(0, 2 * PI, 400)
    for b1, c, lab in ((+0.5, CC, r"$b_1>0$: linger closed"),
                       (-0.5, CO, r"$b_1<0$: linger open")):
        thp = t + b1 * np.sin(t)
        ax[0].plot(t / (2 * PI), 1 + 0.35 * np.cos(thp), color=c, lw=1.6, label=lab)
    ax[0].plot(t / (2 * PI), 1 + 0.35 * np.cos(t), color="0.6", lw=1.0, ls="--",
               label="sinusoid")
    ax[0].set_xlabel(r"$t/T$"); ax[0].set_ylabel(r"gap $d(t)$")
    ax[0].legend(frameon=False, loc="upper right", fontsize=6.8, handlelength=1.4)
    ax[0].set_title("(a) two rhythms, same path and period", loc="left", fontsize=8.5)
    ax[0].set_ylim(0.55, 1.5)

    # (b) reversal
    ax[1].axhline(1, color="0.5", lw=0.8, ls="--")
    ax[1].axvline(0.809, color=MAG, lw=0.9, ls=":")
    ax[1].plot(des, ratio, "-", color="0.3", lw=1.2, zorder=1)
    ax[1].scatter(des, ratio, c=[CC if q > 1 else CO for q in ratio], s=22,
                  edgecolors="w", linewidths=0.6, zorder=2)
    ax[1].set_xscale("log"); ax[1].set_xlabel(r"Deborah number $De$")
    ax[1].set_ylabel(r"$|\Delta x_{\rm closed}| / |\Delta x_{\rm open}|$")
    ax[1].text(0.83, 1.31, r"$De_c\!\approx\!0.81$", color=MAG, fontsize=7.5)
    ax[1].text(0.22, 1.34, "closed wins", color=CC, fontsize=7.5)
    ax[1].text(0.22, 0.905, "open wins", color=CO, fontsize=7.5)
    ax[1].set_title("(b) the optimal rhythm reverses", loc="left", fontsize=8.5)
    save(fig, "fig1_reversal")


# ------------------------------------------------------------ Fig 2: De-specific optimum
def fig_transfer():
    rows = [("best at $De{=}0.3$", [1.4975, 1.4687, 1.3053, 1.0600, 0.9138]),
            ("best at $De{=}1.5$", [1.2826, 1.2703, 1.1948, 1.0843, 1.0188]),
            ("best at $De{=}3.0$", [1.1720, 1.1723, 1.1316, 1.0687, 1.0310])]
    cols = ["0.3", "0.5", "0.8", "1.5", "3.0"]
    M = np.array([r[1] for r in rows])
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    im = ax.imshow(M, cmap=DIV, vmin=1 - 0.5, vmax=1 + 0.5, aspect="auto")
    for i in range(3):
        for j in range(5):
            ax.text(j, i, f"{M[i, j]:.3f}", ha="center", va="center", fontsize=7.5,
                    color="k", fontweight="bold" if (i, j) in [(0, 0), (1, 3), (2, 4)] else "normal")
    for (i, j) in [(0, 0), (1, 3), (2, 4)]:
        ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec="k", lw=1.4))
    ax.add_patch(plt.Rectangle((4 - 0.5, 0 - 0.5), 1, 1, fill=False, ec=MAG, lw=1.8))
    ax.set_xticks(range(5)); ax.set_xticklabels(cols)
    ax.set_yticks(range(3)); ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlabel(r"evaluated at $De$")
    ax.set_title(r"speed $/$ sinusoid; boxed $=$ its own fluid", loc="left", fontsize=8)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("relative speed", fontsize=8)
    ax.text(4, 0, "", )
    save(fig, "fig2_transfer")


# ------------------------------------------------------- Fig 3: mechanism contours
def fig_mechanism():
    res = json.load(open("mechanism_raw.json"))
    DES = [0.40, 0.81, 2.00]
    WX, WY = 1.55, 0.88
    get = lambda De, sg: next(r for r in res if abs(r["lam"] - De) < 1e-9
                              and np.sign(r["b1"]) == sg)
    diffs = [np.array(get(De, 1)["cap"]["f"]) - np.array(get(De, -1)["cap"]["f"]) for De in DES]
    vm = float(np.percentile(np.abs(np.concatenate([d.ravel() for d in diffs])), 97))
    nx, ny = diffs[0].shape
    XX, YY = np.meshgrid(np.linspace(-WX, WX, nx), np.linspace(-WY, WY, ny), indexing="ij")

    fig = plt.figure(figsize=(6.5, 4.0))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0], hspace=0.5, wspace=0.18,
                          left=0.09, right=0.9, top=0.9, bottom=0.11)
    for j, De in enumerate(DES):
        ax = fig.add_subplot(gs[0, j])
        cf = ax.contourf(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 19), cmap=DIV,
                         extend="both")
        ax.contour(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 9), colors="k",
                   linewidths=0.25, alpha=0.35)
        cap = get(De, 1)["cap"]; dd, xc = cap["d"], cap["xc"]
        for xb, rr, col in ((xc - dd / 2, 0.13, MAG), (xc + dd / 2, 0.22, CC)):
            ax.add_patch(plt.Circle((xb, 0), rr, facecolor=col, ec="k", lw=0.7, zorder=5))
        ax.set_aspect("equal"); ax.set_xlim(-WX, WX); ax.set_ylim(-WY, WY)
        tag = "below" if De < 0.8 else ("at" if De < 1 else "above")
        ax.set_title(rf"$De={De:.2f}$ ({tag} $De_c$)", fontsize=8)
        ax.set_xlabel("$x$"); ax.set_xticks([-1, 0, 1])
        if j == 0:
            ax.set_ylabel("$y$")
        ax.set_yticks([-0.5, 0, 0.5])
    cax = fig.add_axes([0.915, 0.55, 0.014, 0.33])
    cb = fig.colorbar(cf, cax=cax); cb.set_label(r"$\Delta\,\mathrm{tr}(\mathsf{C}-\mathsf{I})$",
                                                 fontsize=8)
    cb.ax.tick_params(labelsize=7)

    for j, De in enumerate(DES):
        ax = fig.add_subplot(gs[1, j])
        p, m = get(De, 1), get(De, -1); dt = p["dt"]
        ph = np.arange(len(p["up"])) * dt / (2 * PI)
        cp = np.cumsum(p["up"]) * dt * 1e3; cm = np.cumsum(m["up"]) * dt * 1e3
        ax.axhline(0, color="0.7", lw=0.7)
        ax.plot(ph, cp, color=CC, lw=1.5); ax.plot(ph, cm, color=CO, lw=1.5)
        ax.plot(1, cp[-1], "o", color=CC, ms=4); ax.plot(1, cm[-1], "o", color=CO, ms=4)
        ax.set_xlabel(r"$t/T$"); ax.set_xlim(0, 1.02)
        if j == 0:
            ax.set_ylabel(r"$\int U_p\,dt\ (\times10^{3})$")
    fig.text(0.09, 0.955, r"(a) stored-stress difference between the two rhythms (matched shape)",
             fontsize=8)
    fig.text(0.09, 0.47, r"(b) cycle-resolved displacement; markers swap which finishes ahead",
             fontsize=8)
    save(fig, "fig3_mechanism")


# ------------------------------------------------------------- Fig 4: theory + collapse
def fig_theory():
    import importlib
    TH = importlib.import_module("theory_analysis")
    des = np.exp(np.linspace(np.log(0.12), np.log(6), 80))
    b = 0.5
    P = [TH.P_of(b, D) for D in des]; Pm = [TH.P_of(-b, D) for D in des]
    Q = [TH.Q_of(b, D) for D in des]; Qm = [TH.Q_of(-b, D) for D in des]
    dc = TH.crossover(b)

    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.35), gridspec_kw=dict(wspace=0.5))
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
    Lclosed, Lopen = "linger closed ($+b$)", "linger open ($-b$)"

    # (a) pair term -- the two curves coincide
    ax[0].plot(des, P, color=CC, lw=2.4, label=Lclosed)
    ax[0].plot(des, Pm, color=CO, lw=1.1, ls="--", label=Lopen)
    ax[0].set_xscale("log"); ax[0].set_xlabel("$De$")
    ax[0].set_ylabel(r"pair term  $\oint g\,s\,dt$", labelpad=2)
    ax[0].set_title("(a) identical for both rhythms", loc="left", fontsize=8)
    ax[0].legend(frameon=False, fontsize=6.6, loc="lower center", handlelength=1.6)

    # (b) triple term -- antisymmetric, crosses zero
    ax[1].axhline(0, color="0.6", lw=0.7)
    ax[1].plot(des, Q, color=CC, lw=1.7, label=Lclosed)
    ax[1].plot(des, Qm, color=CO, lw=1.7, label=Lopen)
    if dc:
        ax[1].axvline(dc, color=MAG, lw=1.0, ls=":")
        ax[1].annotate("crosses 0\nhere", (dc, 0), (dc * 1.25, 0.011), fontsize=6.4,
                       color=MAG, ha="left", va="center",
                       arrowprops=dict(arrowstyle="-", color=MAG, lw=0.6))
    ax[1].set_xscale("log"); ax[1].set_xlabel("$De$")
    ax[1].set_ylabel(r"triple term  $\oint g^{2} s\,dt$", labelpad=2)
    ax[1].set_title("(b) flips sign between rhythms", loc="left", fontsize=8)
    ax[1].legend(frameon=False, fontsize=6.6, loc="lower left", handlelength=1.6)

    # (c) collapse -- descriptive legend labels
    COLL = {"baseline swimmer": (CC, [(0.15, 0.9005), (0.25, 0.883), (0.40, 0.841),
                                      (0.50, 0.808), (0.65, 0.746), (0.80, 0.684),
                                      (0.88, 0.6515)]),
            "smaller stroke": (CO, [(0.30, 0.7994), (0.60, 0.7001), (0.80, 0.6191)]),
            "looser confinement": ("#1a8f7a", [(0.30, 1.0956), (0.60, 0.9803),
                                               (0.80, 0.8842)])}
    for name, (c, pts) in COLL.items():
        bb = np.array([p[0] for p in pts]); dd = np.array([p[1] for p in pts])
        ax[2].plot(bb, dd * (1 + bb ** 2 / 2), "o-", color=c, ms=3.2, lw=1.3, label=name)
    ax[2].set_xlabel(r"rhythm strength $b$")
    ax[2].set_ylabel(r"$De_c\,\langle\dot\theta^{2}\rangle$  (collapsed)", labelpad=2)
    ax[2].set_title(r"(c) one group collapses it", loc="left", fontsize=8)
    ax[2].legend(frameon=False, fontsize=6.4, loc="center right")
    ax[2].set_ylim(0.55, 1.28)
    save(fig, "fig4_theory")




# ------------------------------------------------------------------ Fig 5: RL
def fig_rl():
    ctrl = json.load(open("rl_ctrl_results.json"))
    free = json.load(open("rl_results.json"))
    des = np.array(sorted(float(k) for k in ctrl))
    gains = np.array([ctrl[str(D)]["history"][-1]["gain"] if ctrl[str(D)]["history"] else 1.0
                      for D in des])
    closed = np.array([ctrl[str(D)]["best"]["b1"] > 0 for D in des])
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.5), gridspec_kw=dict(wspace=0.34))
    # flip location
    xf = None
    for i in range(len(des) - 1):
        if closed[i] != closed[i + 1]:
            xf = np.sqrt(des[i] * des[i + 1])
    ax[0].plot(des, gains, "-", color="0.4", lw=1.0, zorder=1)
    ax[0].scatter(des, gains, c=[CC if cl else CO for cl in closed], s=26,
                  edgecolors="w", linewidths=0.6, zorder=2)
    if xf:
        ax[0].axvline(xf, color=MAG, lw=0.9, ls=":")
        ax[0].text(xf * 1.03, gains.max(), r"flips $\approx%.2f$" % xf, color=MAG, fontsize=7)
    ax[0].set_xscale("log"); ax[0].set_xlabel(r"$De$")
    ax[0].set_ylabel("speed / sinusoid")
    ax[0].set_title("(a) strategy learned from reward", loc="left", fontsize=8.5)
    ax[0].scatter([], [], c=CO, label="linger open"); ax[0].scatter([], [], c=CC,
                                                                    label="linger closed")
    ax[0].legend(frameon=False, fontsize=6.8, loc="lower right")

    ax[1].axhline(1, color="0.6", lw=0.8, ls="--")
    cols = {"0.5": CO, "0.81": MAG, "2.0": CC}
    for k in sorted(free, key=float):
        h = free[k]["history"]
        if not h:
            continue
        g = [hh["gain"] for hh in h]
        ax[1].plot(range(len(g)), g, color=cols.get(k, "0.5"), lw=1.4,
                   label=rf"$De={k}$")
    ax[1].set_xlabel("training update"); ax[1].set_ylabel("reward / sinusoid")
    ax[1].set_title("(b) a free agent learning", loc="left", fontsize=8.5)
    ax[1].legend(frameon=False, fontsize=7)
    save(fig, "fig5_rl")


if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["reversal", "transfer", "mechanism", "theory", "rl"]
    fns = dict(reversal=fig_reversal, transfer=fig_transfer, mechanism=fig_mechanism,
               theory=fig_theory, rl=fig_rl)
    for w in which:
        fns[w]()
