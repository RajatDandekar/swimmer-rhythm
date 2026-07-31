"""Reinforcement-learning figures: reward curve + learned gaits, JFM style. Plus the RL loop
schematic is built separately as SVG. Everything read from the training output JSONs.

Makes it unambiguous that the rhythm was found by RL: an agent, a reward, a learning curve that
climbs from the plain stroke, and the family of gaits the policy settled on across fluids.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({"font.family": "serif", "mathtext.fontset": "cm", "font.size": 9,
                     "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True, "figure.dpi": 200})
PAPER, WEB = "paper/figs", "site/figures"
PI = np.pi
CO, CC, MAG = "#1a6fb0", "#d06a1c", "#b3006b"
KS = np.array([1.0, 2.0, 3.0])
A = 0.35


def gait_dt(b1, t):
    th = t + b1 * np.sin(t)
    return 1.0 + A * np.cos(th)


def main():
    free = json.load(open("rl_results.json"))
    ctrl = json.load(open("rl_ctrl_results.json"))
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.7), gridspec_kw=dict(wspace=0.32))

    # ---------- (a) the reward curve ----------
    a = ax[0]
    a.axhline(1.0, color="0.55", lw=0.9, ls="--")
    cols = {"0.5": CO, "0.81": MAG, "2.0": CC}
    order = ["0.5", "0.81", "2.0"]
    for k in order:
        h = free[k]["history"]
        g = np.concatenate([[1.0], [hh["gain"] for hh in h]])   # start untrained at the plain stroke
        it = np.arange(len(g))
        a.plot(it, g, "-", color=cols[k], lw=1.6, label=rf"$De={k}$")
        a.plot(it[-1], g[-1], "o", color=cols[k], ms=4)
    a.text(21, 1.025, "plain stroke (untrained)", fontsize=7, color="0.5", va="bottom", ha="center")
    a.annotate("", (4, 1.7), (1, 1.05), arrowprops=dict(arrowstyle="->", color="0.5", lw=0.8))
    a.text(5.5, 1.42, "learns in a\nfew updates", fontsize=7, color="0.4", ha="left")
    a.set_xlabel("training iteration")
    a.set_ylabel(r"reward $/$ plain stroke")
    a.set_title("(a) learning from reward alone", loc="left", fontsize=8.5)
    a.legend(frameon=False, fontsize=7.5, loc="lower right", handlelength=1.5)
    a.set_ylim(0.96, 2.02)

    # ---------- (b) the learned gaits ----------
    b = ax[1]
    t = np.linspace(0, 2 * PI, 400)
    b.plot(t / (2 * PI), gait_dt(0.0, t), color="0.6", lw=1.1, ls="--", label="plain (sinusoid)")
    # learned gaits at low and high De (controlled agents)
    g_lo = ctrl["0.3"]["best"]["b1"]     # open
    g_hi = ctrl["2.0"]["best"]["b1"]     # closed
    b.plot(t / (2 * PI), gait_dt(g_lo, t), color=CO, lw=1.9,
           label=r"learned, $De=0.3$ (open)")
    b.plot(t / (2 * PI), gait_dt(g_hi, t), color=CC, lw=1.9,
           label=r"learned, $De=2.0$ (closed)")
    # time markers: where the swimmer dawdles (equal-time dots bunch up)
    for b1, c in ((g_lo, CO), (g_hi, CC)):
        ts = np.linspace(0, 2 * PI, 22, endpoint=False)
        b.plot(ts / (2 * PI), gait_dt(b1, ts), "o", color=c, ms=2.6, zorder=5)
    b.set_xlabel(r"time through the stroke  $t/T$")
    b.set_ylabel(r"body opening  $d(t)$")
    b.set_title("(b) the gaits the agent discovered", loc="left", fontsize=8.5)
    b.legend(frameon=False, fontsize=6.8, loc="upper center", handlelength=1.6)
    b.set_ylim(0.55, 1.62)


    for d in (PAPER, WEB):
        os.makedirs(d, exist_ok=True)
    fig.savefig(f"{PAPER}/fig_rl_learn.pdf", bbox_inches="tight")
    fig.savefig(f"{WEB}/fig_rl_learn.png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("  fig_rl_learn: reward curve + learned gaits")


if __name__ == "__main__":
    main()
