"""The hero figure: three independent methods, one reversal. Shown at the top of the site.

Three horizontal tracks share a Deborah-number axis. Each shows that method's signature of the
reversal and where it places the crossover. A shaded band marks the De~0.8 region where all
three cluster. Honest: the methods do not agree on the number to three digits -- search 0.81,
learning ~0.86, the leading-order theory ~0.61 -- they agree that the optimal strategy flips,
and cluster around De~0.7-0.9. That honesty is the point.
"""
import json
import numpy as np

OUT = "site/figures"
INK, MUTED, GRID, PLOT = "#0f1c26", "#5b7280", "#e3eaef", "#fbfcfd"
GOLD, BLUE, MAG, GREEN = "#ef8f1c", "#1a9fd4", "#e6009e", "#12a594"
F = "ui-sans-serif,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def txt(x, y, s, size=13, fill=INK, anchor="start", weight="400", family=F, op=1.0):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{family}" opacity="{op}">{s}</text>')


def main():
    # numerics: ratio(De) crossing 1
    r = [x for x in json.load(open("crossover_results.json")) if x.get("ok")]
    dd = {}
    for x in r:
        dd.setdefault(x["lam"], {})[x["b1"]] = x["per_cycle"][-1]
    num_de = np.array(sorted(dd))
    num_ratio = np.array([abs(dd[D][0.5]) / abs(dd[D][-0.5]) for D in num_de])
    # RL: learned strategy per De
    ctrl = json.load(open("rl_ctrl_results.json"))
    rl_de = np.array(sorted(float(k) for k in ctrl))
    rl_closed = np.array([ctrl[str(D)]["best"]["b1"] > 0 for D in rl_de])

    W, H = 1000, 500
    ml, mr = 92, 40
    pw = W - ml - mr
    DEMIN, DEMAX = 0.2, 3.0
    lx0, lx1 = np.log10(DEMIN), np.log10(DEMAX)

    def X(v): return ml + (np.log10(v) - lx0) / (lx1 - lx0) * pw

    b = [f'<rect width="{W}" height="{H}" rx="16" fill="#ffffff" stroke="{GRID}"/>']
    b.append(txt(ml, 46, "Three independent methods, one reversal", 26, INK, "start", "700",
                 "Fraunces,Georgia,serif"))
    b.append(txt(ml, 72, "search, theory and a learning agent all find the optimal swimming "
                 "rhythm flipping at a critical fluid memory", 14, MUTED))

    # the clustering band De in [0.6, 0.9]
    b.append(f'<rect x="{X(0.6):.1f}" y="98" width="{X(0.9)-X(0.6):.1f}" height="336" '
             f'fill="{MAG}" opacity="0.06"/>')
    b.append(f'<line x1="{X(0.6):.1f}" y1="98" x2="{X(0.6):.1f}" y2="434" stroke="{MAG}" '
             f'stroke-width="1" stroke-dasharray="3 4" opacity="0.5"/>')
    b.append(f'<line x1="{X(0.9):.1f}" y1="98" x2="{X(0.9):.1f}" y2="434" stroke="{MAG}" '
             f'stroke-width="1" stroke-dasharray="3 4" opacity="0.5"/>')
    b.append(txt(X(0.735), 116, "the reversal", 12.5, MAG, "middle", "700"))

    tops = [140, 250, 360]      # track baselines
    th = 78

    # ---- track 1: numerics (ratio curve)
    t0 = tops[0]
    y0, y1 = 0.9, 1.4
    def Yn(v): return t0 + th - (v - y0) / (y1 - y0) * th
    b.append(f'<line x1="{ml}" y1="{Yn(1.0):.1f}" x2="{ml+pw}" y2="{Yn(1.0):.1f}" '
             f'stroke="{GRID}"/>')
    pts = " ".join(f"{X(D):.1f},{Yn(min(y1,max(y0,q))):.1f}" for D, q in zip(num_de, num_ratio))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{GOLD}" stroke-width="2.4"/>')
    for D, q in zip(num_de, num_ratio):
        if DEMIN <= D <= DEMAX:
            b.append(f'<circle cx="{X(D):.1f}" cy="{Yn(min(y1,max(y0,q))):.1f}" r="3.5" '
                     f'fill="{GOLD if q>1 else BLUE}"/>')
    b.append(f'<circle cx="{X(0.809):.1f}" cy="{Yn(1.0):.1f}" r="5.5" fill="none" '
             f'stroke="{MAG}" stroke-width="2"/>')
    b.append(txt(ml - 12, t0 + 30, "1  SEARCH", 12.5, INK, "end", "700", MONO))
    b.append(txt(ml - 12, t0 + 46, "solve the PDE", 10.5, MUTED, "end"))
    b.append(txt(X(0.809) + 9, Yn(1.0) - 8, "De_c = 0.81", 11.5, MAG, "start", "700", MONO))

    # ---- track 2: theory (triple-term curve)
    import importlib
    TH = importlib.import_module("theory_analysis")
    des = np.exp(np.linspace(np.log(DEMIN), np.log(DEMAX), 60))
    Q = np.array([TH.Q_of(0.5, D) - TH.Q_of(-0.5, D) for D in des])
    dc_th = TH.crossover(0.5)
    t0 = tops[1]
    qmax = np.abs(Q).max()
    def Yt(v): return t0 + th / 2 - v / qmax * (th / 2)
    b.append(f'<line x1="{ml}" y1="{Yt(0):.1f}" x2="{ml+pw}" y2="{Yt(0):.1f}" stroke="{GRID}"/>')
    pts = " ".join(f"{X(D):.1f},{Yt(q):.1f}" for D, q in zip(des, Q))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{GREEN}" stroke-width="2.4"/>')
    if dc_th:
        b.append(f'<circle cx="{X(dc_th):.1f}" cy="{Yt(0):.1f}" r="5.5" fill="none" '
                 f'stroke="{MAG}" stroke-width="2"/>')
        b.append(txt(X(dc_th) + 9, Yt(0) - 8, f"De_c = {dc_th:.2f}", 11.5, MAG, "start",
                     "700", MONO))
    b.append(txt(ml - 12, t0 + 30, "2  THEORY", 12.5, INK, "end", "700", MONO))
    b.append(txt(ml - 12, t0 + 46, "Fourier algebra", 10.5, MUTED, "end"))

    # ---- track 3: RL (learned strategy band)
    t0 = tops[2]
    yb = t0 + th / 2
    for i in range(len(rl_de)):
        D = rl_de[i]
        if not (DEMIN <= D <= DEMAX):
            continue
        c = GOLD if rl_closed[i] else BLUE
        x = X(D)
        b.append(f'<circle cx="{x:.1f}" cy="{yb:.1f}" r="6" fill="{c}" stroke="#fff" '
                 f'stroke-width="1.5"/>')
    # flip location
    xf = None
    for i in range(len(rl_de) - 1):
        if rl_closed[i] != rl_closed[i + 1]:
            xf = np.sqrt(rl_de[i] * rl_de[i + 1])
    if xf:
        b.append(f'<circle cx="{X(xf):.1f}" cy="{yb:.1f}" r="9" fill="none" stroke="{MAG}" '
                 f'stroke-width="2"/>')
        b.append(txt(X(xf) + 12, yb - 9, f"flips ~ {xf:.2f}", 11.5, MAG, "start", "700", MONO))
    b.append(txt(ml - 12, t0 + 30, "3  LEARNING", 12.5, INK, "end", "700", MONO))
    b.append(txt(ml - 12, t0 + 46, "reward only", 10.5, MUTED, "end"))
    b.append(f'<circle cx="{ml+6}" cy="{yb+34}" r="5" fill="{BLUE}"/>')
    b.append(txt(ml + 16, yb + 38, "linger open", 10.5, BLUE, "start", "600"))
    b.append(f'<circle cx="{ml+120}" cy="{yb+34}" r="5" fill="{GOLD}"/>')
    b.append(txt(ml + 130, yb + 38, "linger closed", 10.5, GOLD, "start", "600"))

    # x axis
    for D in (0.2, 0.5, 1.0, 2.0, 3.0):
        b.append(f'<line x1="{X(D):.1f}" y1="434" x2="{X(D):.1f}" y2="440" stroke="{MUTED}"/>')
        b.append(txt(X(D), 456, f"{D:g}", 12, MUTED, "middle", family=MONO))
    b.append(txt(ml + pw / 2, 482, "Deborah number  —  how long the fluid remembers", 13,
                 MUTED, "middle"))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
            f'style="max-width:{W}px;height:auto;font-family:{F}">' + "".join(b) + "</svg>")


if __name__ == "__main__":
    svg = main()
    open(f"{OUT}/hero_compare.svg", "w").write(svg)
    print(f"wrote {OUT}/hero_compare.svg ({len(svg)//1024} kB)")
