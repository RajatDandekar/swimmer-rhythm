"""The RL figure: an agent DISCOVERS the reversal from reward alone.

Two panels, reading the real training output:
  [A] controlled agents (rl_ctrl_results.json): the learned rhythm parameter b1 vs De, crossing
      zero at the crossover -- the reversal, discovered not derived.
  [B] free-agent learning curves (rl_results.json): reward / sinusoid climbing from 1.0 as the
      agent learns, proving it genuinely learns rather than being handed the answer.
Plus a callout for the two-act lesson (naive reward games effort; only a fair energy budget
recovers the reversal).
"""
import json
import numpy as np

OUT = "site/figures"
INK, MUTED, GRID, PLOT = "#0f1c26", "#5b7280", "#e3eaef", "#fbfcfd"
GOLD, BLUE, CORAL, GREEN = "#ef8f1c", "#1a9fd4", "#e6009e", "#12a594"
F = "ui-sans-serif,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def txt(x, y, s, size=13, fill=INK, anchor="start", weight="400", family=F, op=1.0):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{family}" opacity="{op}">{s}</text>')


def main():
    ctrl = json.load(open("rl_ctrl_results.json"))
    free = json.load(open("rl_results.json"))
    W, H = 900, 470
    gap, ml, mt, mb = 66, 66, 116, 66
    pw = (W - ml - 34 - gap) / 2
    ph = H - mt - mb
    b = [f'<rect width="{W}" height="{H}" rx="14" fill="#ffffff" stroke="{GRID}"/>']
    b.append(txt(34, 32, "An agent discovers the reversal from reward alone", 15.5, INK,
                "start", "600"))
    b.append(txt(34, 52, "a 65-parameter numpy policy, trained by REINFORCE — no equations, "
                "no supplied answer, only “swim far for your energy”", 12.5, MUTED))

    # ---------- [A] controlled: gain, coloured by the learned strategy ----------
    # Only the SIGN of b1 carries meaning here -- matched effort normalises its magnitude away,
    # so we plot the robust quantities: how much the agent beats the sinusoid (always >=1) with
    # the marker COLOUR = the strategy it chose. The colour flips at the crossover.
    des = sorted(float(k) for k in ctrl)
    gains = [ctrl[str(D)]["history"][-1]["gain"] if ctrl[str(D)]["history"] else 1.0 for D in des]
    strat = [ctrl[str(D)]["best"]["b1"] > 0 for D in des]     # True = closed
    x0 = ml
    lde = np.log10(des); lo, hi = lde.min(), lde.max()
    gmn, gmx = 1.0, max(gains) * 1.06

    def X(v): return x0 + (np.log10(v) - lo) / (hi - lo) * pw
    def Yc(v): return mt + (gmx - v) / (gmx - gmn) * ph
    b.append(f'<rect x="{x0}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" '
             f'stroke="{GRID}" rx="6"/>')
    for gv in np.linspace(1.0, gmx, 4):
        yy = Yc(gv)
        b.append(f'<line x1="{x0}" y1="{yy}" x2="{x0+pw}" y2="{yy}" stroke="{GRID}"/>')
        b.append(txt(x0 - 8, yy + 4, f"{gv:.2f}", 10.5, MUTED, "end", family=MONO))
    # crossover: where the learned strategy flips
    xflip = None
    for i in range(len(des) - 1):
        if strat[i] != strat[i + 1]:
            xflip = np.sqrt(des[i] * des[i + 1])
    if xflip:
        b.append(f'<line x1="{X(xflip)}" y1="{mt}" x2="{X(xflip)}" y2="{mt+ph}" '
                 f'stroke="{CORAL}" stroke-width="1.8" stroke-dasharray="4 4" opacity="0.85"/>')
        b.append(txt(X(xflip) + 7, mt + 16, "the agent flips here", 11, CORAL, "start", "700"))
        b.append(txt(X(xflip) + 7, mt + 31, "De ≈ 0.81", 11, CORAL, "start", "700", MONO))
    pts = " ".join(f"{X(D):.1f},{Yc(g):.1f}" for D, g in zip(des, gains))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{GREEN}" stroke-width="2.2" '
             f'opacity="0.55"/>')
    TICKS = [0.3, 0.5, 0.8, 1.0, 2.0]
    for D, g, cl in zip(des, gains, strat):
        c = GOLD if cl else BLUE
        b.append(f'<circle cx="{X(D):.1f}" cy="{Yc(g):.1f}" r="5.0" fill="{c}" '
                 f'stroke="#fff" stroke-width="1.6"/>')
    for D in TICKS:
        b.append(txt(X(D), mt + ph + 20, f"{D:g}", 10, MUTED, "middle", family=MONO))
    b.append(txt(x0, mt - 34, "[A]  what the agent learned, at each fluid", 13.5, INK,
                "start", "600"))
    b.append(txt(x0, mt - 15, "how much it beats the sinusoid — colour is the strategy it chose",
                11.5, MUTED))
    b.append(f'<circle cx="{x0+12}" cy="{mt+ph-30}" r="5" fill="{BLUE}"/>')
    b.append(txt(x0 + 22, mt + ph - 26, "lingers OPEN", 11, BLUE, "start", "700"))
    b.append(f'<circle cx="{x0+12}" cy="{mt+ph-12}" r="5" fill="{GOLD}"/>')
    b.append(txt(x0 + 22, mt + ph - 8, "lingers CLOSED", 11, GOLD, "start", "700"))
    b.append(txt(x0 + pw / 2, H - 16, "Deborah number", 11.5, MUTED, "middle"))

    # ---------- [B] free-agent learning curves ----------
    x1 = ml + pw + gap
    allg = [h["gain"] for k in free for h in free[k]["history"]]
    g1, g2 = min(0.98, min(allg)), max(1.05, max(allg))
    b.append(f'<rect x="{x1}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" '
             f'stroke="{GRID}" rx="6"/>')
    for gv in np.linspace(1.0, g2, 4):
        yy = mt + (g2 - gv) / (g2 - g1) * ph
        b.append(f'<line x1="{x1}" y1="{yy}" x2="{x1+pw}" y2="{yy}" stroke="{GRID}"/>')
        b.append(txt(x1 - 8, yy + 4, f"{gv:.2f}", 10.5, MUTED, "end", family=MONO))
    yo = mt + (g2 - 1.0) / (g2 - g1) * ph
    b.append(f'<line x1="{x1}" y1="{yo}" x2="{x1+pw}" y2="{yo}" stroke="{INK}" '
             f'stroke-dasharray="5 4" opacity="0.5"/>')
    b.append(txt(x1 + pw - 6, yo - 6, "the plain sinusoid", 10.5, INK, "end", op=0.55))
    ng = max((len(free[k]["history"]) for k in free), default=1)
    cols = {"0.5": BLUE, "0.81": CORAL, "2.0": GOLD}
    for k in sorted(free, key=float):
        h = free[k]["history"]
        if not h:
            continue
        c = cols.get(k, GREEN)
        line = " ".join(f"{x1 + hh['gen']/(ng-1)*pw:.1f},"
                        f"{mt + (g2-hh['gain'])/(g2-g1)*ph:.1f}" for hh in h)
        b.append(f'<polyline points="{line}" fill="none" stroke="{c}" stroke-width="2.2"/>')
        last = h[-1]
        b.append(txt(x1 + pw - 6, mt + (g2 - last["gain"]) / (g2 - g1) * ph - 5,
                     f"De {k}", 11, c, "end", "700", MONO))
    b.append(txt(x1, mt - 34, "[B]  a free agent learning to swim", 13.5, INK, "start", "600"))
    b.append(txt(x1, mt - 15, "reward ÷ sinusoid, climbing as it learns", 11.5, MUTED))
    b.append(txt(x1 + pw / 2, H - 16, "training update", 11.5, MUTED, "middle"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
            f'style="max-width:{W}px;height:auto;font-family:{F}">' + "".join(b) + "</svg>")


if __name__ == "__main__":
    svg = main()
    open(f"{OUT}/rl.svg", "w").write(svg)
    print(f"wrote {OUT}/rl.svg ({len(svg)//1024} kB)")
