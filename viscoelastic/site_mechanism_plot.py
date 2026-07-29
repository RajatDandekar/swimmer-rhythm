"""Render the JFM mechanism panels from cached results. NO simulation happens here.

Deliberately separated from the compute. The first attempt at this figure put the 20-minute PDE
run and the matplotlib call in the same script, and an unsupported LaTeX macro in a colorbar
label destroyed the whole run. Compute writes mechanism_raw.json; this reads it. A rendering bug
now costs seconds.

    modal run --detach mechanism_modal.py::main    # compute (6 solves, one parallel wave)
    modal run mechanism_modal.py::fetch            # -> mechanism_raw.json
    python site_mechanism_plot.py                  # -> site/figures/mechanism.png
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

OUT = "site/figures"
PI = np.pi
WX, WY = 1.55, 0.88
DES = [0.40, 0.81, 2.00]

INK, MUTED, GRID = "#0f1c26", "#5b7280", "#dbe4ea"
CYAN, ORANGE, MAGENTA = "#1a9fd4", "#ef8f1c", "#e6009e"
DIV = LinearSegmentedColormap.from_list("div", [
    "#0d5f80", "#1a9fd4", "#8ed4ee", "#ffffff", "#f8cf95", "#ef8f1c", "#a35c06"])


def main():
    res = json.load(open("mechanism_raw.json"))
    get = lambda De, sg: next(r for r in res if abs(r["lam"] - De) < 1e-9
                              and np.sign(r["b1"]) == sg)

    fig = plt.figure(figsize=(13.4, 7.8))
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 3, height_ratios=[1.05, 1.0], hspace=0.46, wspace=0.2,
                          left=0.07, right=0.975, top=0.775, bottom=0.088)

    diffs = [np.array(get(De, 1)["cap"]["f"]) - np.array(get(De, -1)["cap"]["f"])
             for De in DES]
    vm = float(np.percentile(np.abs(np.concatenate([d.ravel() for d in diffs])), 97.0))
    nx, ny = diffs[0].shape
    XX, YY = np.meshgrid(np.linspace(-WX, WX, nx), np.linspace(-WY, WY, ny), indexing="ij")

    for j, De in enumerate(DES):
        ax = fig.add_subplot(gs[0, j])
        cf = ax.contourf(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 21), cmap=DIV,
                         extend="both")
        ax.contour(XX, YY, diffs[j], levels=np.linspace(-vm, vm, 11), colors=INK,
                   linewidths=0.4, alpha=0.30)
        cap = get(De, 1)["cap"]
        d, xc = cap["d"], cap["xc"]
        for xb, r, col in ((xc - d / 2, 0.13, MAGENTA), (xc + d / 2, 0.24, ORANGE)):
            ax.add_patch(plt.Circle((xb, 0), r, facecolor=col, edgecolor=INK,
                                    linewidth=1.2, zorder=6))
        ax.plot([xc - d / 2, xc + d / 2], [0, 0], color=INK, lw=1.2, alpha=0.6, zorder=5)
        ax.set_xlim(-WX, WX); ax.set_ylim(-WY, WY); ax.set_aspect("equal")
        tag = "below the crossover" if De < 0.8 else (
            "at the crossover" if De < 1.0 else "above the crossover")
        ax.set_title("De = %.2f   (%s)" % (De, tag), fontsize=11.5, color=INK, pad=8)
        ax.tick_params(labelsize=8.5, colors=MUTED, length=3)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        ax.set_xlabel("x", fontsize=10.5, color=INK)
        if j == 0:
            ax.set_ylabel("y", fontsize=10.5, color=INK)

    cax = fig.add_axes([0.32, 0.885, 0.36, 0.015])
    cb = fig.colorbar(cf, cax=cax, orientation="horizontal")
    cb.set_label("difference in stored elastic stress between the two rhythms",
                 fontsize=9.5, color=INK, labelpad=6)
    cb.ax.tick_params(labelsize=8, colors=MUTED)
    cb.outline.set_edgecolor(GRID)

    for j, De in enumerate(DES):
        ax = fig.add_subplot(gs[1, j])
        p, m = get(De, 1), get(De, -1)
        dt = p["dt"]
        ph = np.arange(len(p["up"])) * dt / (2 * PI)
        cp = np.cumsum(p["up"]) * dt * 1e3
        cm = np.cumsum(m["up"]) * dt * 1e3
        ax.axhline(0, color=GRID, lw=1)
        ax.plot(ph, cp, color=ORANGE, lw=2.3, label="lingers closed")
        ax.plot(ph, cm, color=CYAN, lw=2.3, label="lingers open")
        ax.plot([ph[-1]], [cp[-1]], "o", color=ORANGE, ms=6.5)
        ax.plot([ph[-1]], [cm[-1]], "o", color=CYAN, ms=6.5)
        win = "closed" if abs(cp[-1]) > abs(cm[-1]) else "open"
        ax.text(0.035, 0.08, "wins: lingers %s" % win, transform=ax.transAxes,
                fontsize=10.5, color=ORANGE if win == "closed" else CYAN, weight="bold")
        ax.set_xlabel("phase through one stroke", fontsize=10.5, color=INK)
        if j == 0:
            ax.set_ylabel("distance travelled so far  (x10$^{-3}$)", fontsize=10.5, color=INK)
            ax.legend(frameon=False, fontsize=9.5, loc="upper left")
        ax.tick_params(labelsize=8.5, colors=MUTED, length=3)
        for sp in ax.spines.values():
            sp.set_color(GRID)
        ax.set_xlim(0, 1.02)

    fig.text(0.5, 0.962, "WHERE the asymmetry lives (top) and WHERE the net displacement "
             "is made (bottom)", ha="center", fontsize=13.5, color=INK)
    fig.savefig("%s/mechanism.png" % OUT, dpi=170, facecolor="white")
    print("wrote %s/mechanism.png" % OUT)

    for De in DES:
        p, m = get(De, 1), get(De, -1)
        print("  De=%-5s dx(+b)=%+.4e  dx(-b)=%+.4e  ratio=%.4f"
              % (De, p["dx"], m["dx"], abs(p["dx"] / m["dx"])))


if __name__ == "__main__":
    main()
