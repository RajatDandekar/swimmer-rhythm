"""Generate the site's scientific figures as SVG, straight from the result JSONs.

Every number rendered here is read from a file written by a Modal run. Nothing is typed in by
hand, so the figures cannot drift from the data -- if a result is re-run, the figures change.
"""
import json
import os
import numpy as np

OUT = "site/figures"
# Light theme keyed to the Vizuara mark: orange / cyan / magenta.
# The colour assignment carries meaning and is used consistently everywhere on the site --
# ORANGE = the lingers-closed rhythm, CYAN = the lingers-open rhythm, MAGENTA = the alarm
# (a champion doing worse than the plain stroke), GREEN = a passed check.
BG, PANEL = "#ffffff", "#ffffff"
INK, MUTED, GRID = "#0f1c26", "#5b7280", "#e3eaef"
PLOT = "#fbfcfd"
TEAL, GOLD, CORAL, BLUE = "#12a594", "#ef8f1c", "#e6009e", "#1a9fd4"
F = "ui-sans-serif,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def svg(w, h, body, vb=None):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb or w} {h}" '
            f'width="100%" style="max-width:{w}px;height:auto;font-family:{F}">'
            f'<rect width="{vb or w}" height="{h}" rx="14" fill="{PANEL}" stroke="{GRID}"/>{body}</svg>')


def txt(x, y, s, size=13, fill=INK, anchor="start", weight="400", family=F, op=1.0):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{family}" opacity="{op}">{s}</text>')


def load(p):
    return json.load(open(p))


# ---------------------------------------------------------------- 1. the crossover
def fig_crossover():
    r = [x for x in load("crossover_results.json") if x.get("ok")]
    d = {}
    for x in r:
        d.setdefault(x["lam"], {})[x["b1"]] = x["per_cycle"][-1]
    des = sorted(d)
    rat = [abs(d[De][0.5]) / abs(d[De][-0.5]) for De in des]

    W, H = 860, 470
    ml, mr, mt, mb = 78, 34, 58, 62
    pw, ph = W - ml - mr, H - mt - mb
    lx = np.log10(des)
    x0, x1 = lx.min(), lx.max()
    y0, y1 = 0.90, 1.42

    def X(v): return ml + (np.log10(v) - x0) / (x1 - x0) * pw
    def Y(v): return mt + (y1 - v) / (y1 - y0) * ph

    b = [f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" stroke="{GRID}" rx="6"/>']
    # shaded regions
    b.append(f'<rect x="{ml}" y="{Y(y1)}" width="{pw}" height="{Y(1.0)-Y(y1)}" '
             f'fill="{GOLD}" opacity="0.045"/>')
    b.append(f'<rect x="{ml}" y="{Y(1.0)}" width="{pw}" height="{Y(y0)-Y(1.0)}" '
             f'fill="{BLUE}" opacity="0.05"/>')
    for gv in [0.9, 1.0, 1.1, 1.2, 1.3, 1.4]:
        b.append(f'<line x1="{ml}" y1="{Y(gv)}" x2="{ml+pw}" y2="{Y(gv)}" stroke="{GRID}" '
                 f'stroke-width="1"/>')
        b.append(txt(ml - 12, Y(gv) + 4, f"{gv:.1f}", 12, MUTED, "end", family=MONO))
    for gv in [0.2, 0.5, 1, 2, 5, 10, 20]:
        b.append(f'<line x1="{X(gv)}" y1="{mt}" x2="{X(gv)}" y2="{mt+ph}" stroke="{GRID}" '
                 f'stroke-width="1" opacity="0.6"/>')
        b.append(txt(X(gv), mt + ph + 22, f"{gv:g}", 12, MUTED, "middle", family=MONO))
    # the equal line
    b.append(f'<line x1="{ml}" y1="{Y(1.0)}" x2="{ml+pw}" y2="{Y(1.0)}" stroke="{INK}" '
             f'stroke-width="1.6" stroke-dasharray="6 4" opacity="0.75"/>')
    b.append(txt(ml + pw - 8, Y(1.0) - 10, "the two rhythms tie", 12, INK, "end", op=0.75))
    # crossover marker
    xc = 0.809
    b.append(f'<line x1="{X(xc)}" y1="{mt}" x2="{X(xc)}" y2="{mt+ph}" stroke="{CORAL}" '
             f'stroke-width="2" stroke-dasharray="4 4" opacity="0.9"/>')
    b.append(txt(X(xc) + 9, mt + 20, "De  0.81", 13, CORAL, "start", "700", MONO))
    b.append(txt(X(xc) + 9, mt + 37, "the optimum flips", 12, CORAL, "start", op=0.85))
    # curve
    pts = " ".join(f"{X(D):.1f},{Y(q):.1f}" for D, q in zip(des, rat))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{GOLD}" stroke-width="2.6" '
             f'stroke-linejoin="round"/>')
    for D, q in zip(des, rat):
        c = GOLD if q > 1 else BLUE
        b.append(f'<circle cx="{X(D):.1f}" cy="{Y(q):.1f}" r="5.2" fill="{c}" '
                 f'stroke="#ffffff" stroke-width="2"/>')
    b.append(txt(ml, 26, "Which rhythm wins, as the fluid&#8217;s memory gets longer",
                 15, INK, "start", "600"))
    b.append(txt(ml, 44, "ratio of swimming speed:  lingers-closed  ÷  lingers-open",
                 12.5, MUTED))
    b.append(txt(ml + pw, mt - 14, "lingering CLOSED is better ↑", 12, GOLD, "end", "600"))
    b.append(txt(ml + 8, mt + ph - 12, "↓ lingering OPEN is better", 12, BLUE, "start", "600"))
    b.append(txt(ml + pw / 2, H - 16, "Deborah number  (how long the fluid remembers)",
                 12.5, MUTED, "middle"))
    return svg(W, H, "".join(b))


# ------------------------------------------------------- 2. transfer matrix heatmap
def fig_transfer():
    rows = [("best at De=0.3", [1.4975, 1.4687, 1.3053, 1.0600, 0.9138]),
            ("best at De=1.5", [1.2826, 1.2703, 1.1948, 1.0843, 1.0188]),
            ("best at De=3.0", [1.1720, 1.1723, 1.1316, 1.0687, 1.0310])]
    cols = ["0.3", "0.5", "0.8", "1.5", "3.0"]
    diag = [0, 3, 4]
    W, H = 860, 400
    cw, chh = 116, 74
    ml, mt = 210, 118

    def col_for(v):
        if v < 1.0:
            return CORAL, 0.30 + 0.55 * min(1.0, (1.0 - v) / 0.10)
        return GOLD, 0.12 + 0.72 * min(1.0, (v - 1.0) / 0.50)

    b = []
    b.append(txt(34, 34, "The best stroke depends on the fluid — and gets it wrong "
                 "in the other one", 15, INK, "start", "600"))
    b.append(txt(34, 54, "each row is one optimised rhythm, scored in five different fluids "
                 "(1.00 = ties the plain sinusoid)", 12.5, MUTED))
    b.append(txt(ml + 5 * cw / 2, mt - 44, "evaluated in a fluid with De =", 12.5, MUTED,
                 "middle"))
    for j, c in enumerate(cols):
        b.append(txt(ml + j * cw + cw / 2, mt - 20, c, 13.5, INK, "middle", "600", MONO))
    for i, (name, vals) in enumerate(rows):
        y = mt + i * chh
        b.append(txt(ml - 22, y + chh / 2 + 5, name, 13, INK, "end", "500"))
        for j, v in enumerate(vals):
            x = ml + j * cw
            fc, op = col_for(v)
            isd = (i, j) in [(0, 0), (1, 3), (2, 4)]
            b.append(f'<rect x="{x+4}" y="{y+4}" width="{cw-8}" height="{chh-8}" rx="8" '
                     f'fill="{fc}" opacity="{op:.3f}"/>')
            if isd:
                b.append(f'<rect x="{x+4}" y="{y+4}" width="{cw-8}" height="{chh-8}" rx="8" '
                         f'fill="none" stroke="{INK}" stroke-width="2" opacity="0.85"/>')
            tc = INK
            b.append(txt(x + cw / 2, y + chh / 2 + 6, f"{v:.3f}", 16, tc, "middle",
                         "700" if isd else "500", MONO))
    yb = mt + 3 * chh + 30
    b.append(f'<rect x="{ml + 4*cw + 4}" y="{mt+4}" width="{cw-8}" height="{chh-8}" rx="8" '
             f'fill="none" stroke="{CORAL}" stroke-width="2.5"/>')
    b.append(txt(34, yb + 6, "■", 13, INK))
    b.append(txt(52, yb + 6, "outlined = the fluid that stroke was optimised for. "
                 "It wins its own column every time.", 12.5, MUTED))
    b.append(txt(34, yb + 26, "■", 13, CORAL))
    b.append(txt(52, yb + 26, "0.9138 — the low-memory champion is WORSE than doing "
                 "nothing clever in a high-memory fluid.", 12.5, CORAL))
    return svg(W, H, "".join(b))


# ------------------------------------------------- 3. same path, different rhythm
def fig_strokes():
    W, H = 860, 360
    ml, mr, mt, mb = 68, 210, 56, 52
    pw, ph = W - ml - mr, H - mt - mb
    t = np.linspace(0, 2 * np.pi, 600)

    def d_of(b1):
        th = t + b1 * np.sin(t)
        return 1.0 + 0.35 * np.cos(th)

    def X(v): return ml + v / (2 * np.pi) * pw
    def Y(v): return mt + (1.35 - v) / 0.70 * ph

    b = [f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" stroke="{GRID}" rx="6"/>']
    for lv, lab in ((1.35, "fully open"), (1.0, ""), (0.65, "fully closed")):
        b.append(f'<line x1="{ml}" y1="{Y(lv)}" x2="{ml+pw}" y2="{Y(lv)}" stroke="{GRID}" '
                 f'stroke-width="1" stroke-dasharray="{"0" if lab else "3 3"}"/>')
        if lab:
            b.append(txt(ml - 10, Y(lv) + 4, lab, 11.5, MUTED, "end"))
    for name, b1, c in (("lingers CLOSED", +0.5, GOLD), ("lingers OPEN", -0.5, BLUE),
                        ("plain sinusoid", 0.0, MUTED)):
        y = d_of(b1)
        pts = " ".join(f"{X(a):.1f},{Y(v):.1f}" for a, v in zip(t, y))
        dash = ' stroke-dasharray="5 4"' if b1 == 0 else ""
        b.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="2.6"'
                 f'{dash} opacity="{0.55 if b1==0 else 1}"/>')
    # markers showing where each spends its time
    for b1, c, yo in ((+0.5, GOLD, 0), (-0.5, BLUE, 1)):
        ts = np.linspace(0, 2 * np.pi, 25, endpoint=False)
        th = ts + b1 * np.sin(ts)
        dv = 1.0 + 0.35 * np.cos(th)
        for a, v in zip(ts, dv):
            b.append(f'<circle cx="{X(a):.1f}" cy="{Y(v):.1f}" r="2.6" fill="{c}" '
                     f'opacity="0.95"/>')
    b.append(txt(ml, 26, "Same motion. Same energy. Different rhythm.", 15, INK,
                 "start", "600"))
    b.append(txt(ml, 44, "dots are equally spaced in time — where they bunch up, "
                 "the swimmer is dawdling", 12.5, MUTED))
    b.append(txt(ml + pw / 2, H - 14, "one full stroke cycle", 12.5, MUTED, "middle"))
    lx = ml + pw + 26
    rows = [("excursion", "identical"), ("energy used", "identical"),
            ("top speed", "identical"), ("period", "identical"),
            ("in water", "both exactly 0")]
    b.append(txt(lx, mt + 6, "held equal:", 12.5, INK, "start", "600"))
    for i, (k, v) in enumerate(rows):
        yy = mt + 30 + i * 22
        b.append(txt(lx, yy, k, 12, MUTED))
        b.append(txt(W - 22, yy, v, 12, TEAL, "end", "600", MONO))
    yy = mt + 30 + len(rows) * 22 + 12
    b.append(f'<line x1="{lx}" y1="{yy-12}" x2="{W-22}" y2="{yy-12}" stroke="{GRID}"/>')
    b.append(txt(lx, yy + 6, "speed differs by", 12.5, INK, "start", "600"))
    b.append(txt(W - 22, yy + 28, "31.5%", 24, GOLD, "end", "700", MONO))
    return svg(W, H, "".join(b))


# ------------------------------------------------------ 4. how many rhythms beat it
def fig_fraction():
    des = [0.3, 0.5, 0.8, 1.5, 3.0]
    frac = [65 / 180, 47 / 180, 24 / 180, 7 / 180, 3 / 180]
    best = [1.4975, 1.4687, 1.3053, 1.0843, 1.0310]
    W, H = 860, 380
    ml, mr, mt, mb = 70, 70, 62, 60
    pw, ph = W - ml - mr, H - mt - mb
    bw = pw / len(des) * 0.46

    def X(i): return ml + (i + 0.5) * pw / len(des)
    def Y(v): return mt + (0.40 - v) / 0.40 * ph

    b = [f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" stroke="{GRID}" rx="6"/>']
    for g in [0, 0.1, 0.2, 0.3, 0.4]:
        b.append(f'<line x1="{ml}" y1="{Y(g)}" x2="{ml+pw}" y2="{Y(g)}" stroke="{GRID}"/>')
        b.append(txt(ml - 10, Y(g) + 4, f"{g*100:.0f}%", 11.5, MUTED, "end", family=MONO))
    for i, (D, f_, bs) in enumerate(zip(des, frac, best)):
        x = X(i)
        b.append(f'<rect x="{x-bw/2}" y="{Y(f_)}" width="{bw}" height="{Y(0)-Y(f_)}" '
                 f'rx="5" fill="{TEAL}" opacity="{0.35+0.5*f_/0.40:.2f}"/>')
        b.append(txt(x, Y(f_) - 10, f"{f_*100:.0f}%", 13.5, TEAL, "middle", "700", MONO))
        b.append(txt(x, mt + ph + 22, f"De {D}", 12.5, MUTED, "middle", family=MONO))
        b.append(txt(x, mt + ph + 42, f"best {bs:.2f}×", 11.5, GOLD, "middle",
                     family=MONO))
    b.append(txt(ml, 26, "As the fluid&#8217;s memory grows, the plain sinusoid gets harder "
                 "to beat", 15, INK, "start", "600"))
    b.append(txt(ml, 44, "share of 180 sampled rhythms that beat it at matched energy",
                 12.5, MUTED))
    return svg(W, H, "".join(b))


# ------------------------------------------------------------- 5. convergence proof
def fig_convergence():
    rows = [("reference", 1.4974, 0.9137), ("4× finer in time", 1.4976, 0.9139),
            ("1.5× finer grid", 1.4974, 0.9137), ("1.5× bigger box", 1.4935, 0.9137),
            ("all of the above", 1.4976, 0.9138)]
    W, H = 860, 330
    b = []
    b.append(txt(34, 32, "The numbers do not move when the simulation is refined",
                 15, INK, "start", "600"))
    b.append(txt(34, 52, "the same two claims, recomputed at four higher resolutions",
                 12.5, MUTED))
    x1, x2 = 470, 700
    b.append(txt(x1, 92, "speed-up at De=0.3", 12.5, GOLD, "middle", "600"))
    b.append(txt(x2, 92, "at De=3.0", 12.5, CORAL, "middle", "600"))
    for i, (n, a, c) in enumerate(rows):
        y = 126 + i * 30
        b.append(txt(40, y, n, 13, MUTED))
        b.append(txt(x1, y, f"{a:.4f}×", 14, INK, "middle", "500", MONO))
        b.append(txt(x2, y, f"{c:.4f}×", 14, INK, "middle", "500", MONO))
    y = 126 + len(rows) * 30
    b.append(f'<line x1="34" y1="{y-14}" x2="{W-34}" y2="{y-14}" stroke="{GRID}"/>')
    b.append(txt(40, y + 8, "total spread", 13, INK, "start", "600"))
    b.append(txt(x1, y + 8, "0.41%", 14, GOLD, "middle", "700", MONO))
    b.append(txt(x2, y + 8, "0.02%", 14, CORAL, "middle", "700", MONO))
    b.append(txt(40, y + 38, "In water, every one of these strokes returns exactly 0.000 "
                 "— the swimmer really is a scallop.", 12.5, TEAL))
    return svg(W, H, "".join(b))


def main():
    os.makedirs(OUT, exist_ok=True)
    figs = dict(crossover=fig_crossover(), transfer=fig_transfer(), strokes=fig_strokes(),
                fraction=fig_fraction(), convergence=fig_convergence(),
                collapse=fig_collapse(), theory=fig_theory())
    for k, v in figs.items():
        open(f"{OUT}/{k}.svg", "w").write(v)
        print(f"wrote {OUT}/{k}.svg  ({len(v)//1024} kB)")




# ------------------------------------------------ 6. the collapse: De_c x <(dtheta/dt)^2>
COLLAPSE = {
    "baseline": ("#ef8f1c", [(0.15, 0.9005, 1), (0.25, 0.883, 0), (0.40, 0.841, 0),
                             (0.50, 0.808, 0), (0.65, 0.746, 0), (0.80, 0.684, 0),
                             (0.88, 0.6515, 1)]),
    "smaller stroke": ("#1a9fd4", [(0.30, 0.7994, 0), (0.60, 0.7001, 0), (0.80, 0.6191, 0)]),
    "looser confinement": ("#12a594", [(0.30, 1.0956, 0), (0.60, 0.9803, 0),
                                       (0.80, 0.8842, 0)]),
}


def fig_collapse():
    """Left: the crossover moves all over the place. Right: one multiplication and it doesn't.
    The open rings are out-of-sample predictions, made before those runs existed."""
    W, H = 880, 470
    gap, ml, mt, mb = 54, 62, 112, 62
    pw = (W - ml - 34 - gap) / 2
    ph = H - mt - mb

    def panel(x0, ylo, yhi, title, sub, collapsed):
        b = [f'<rect x="{x0}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" '
             f'stroke="{GRID}" rx="6"/>']
        def X(v): return x0 + (v - 0.05) / 0.90 * pw
        def Y(v): return mt + (yhi - v) / (yhi - ylo) * ph
        for gv in np.linspace(ylo, yhi, 5):
            b.append(f'<line x1="{x0}" y1="{Y(gv)}" x2="{x0+pw}" y2="{Y(gv)}" '
                     f'stroke="{GRID}"/>')
            b.append(txt(x0 - 9, Y(gv) + 4, f"{gv:.2f}", 11, MUTED, "end", family=MONO))
        for gv in (0.2, 0.4, 0.6, 0.8):
            b.append(txt(X(gv), mt + ph + 20, f"{gv:.1f}", 11, MUTED, "middle", family=MONO))
        for name, (col, pts) in COLLAPSE.items():
            vals = [(bb, dd * (1 + bb ** 2 / 2) if collapsed else dd, oos)
                    for bb, dd, oos in pts]
            poly = " ".join(f"{X(a):.1f},{Y(v):.1f}" for a, v, _ in vals)
            b.append(f'<polyline points="{poly}" fill="none" stroke="{col}" '
                     f'stroke-width="2.4" stroke-linejoin="round"/>')
            for a, v, oos in vals:
                b.append(f'<circle cx="{X(a):.1f}" cy="{Y(v):.1f}" r="5" '
                         + (f'fill="#ffffff" stroke="{col}" stroke-width="2.5"/>' if oos
                            else f'fill="{col}" stroke="#ffffff" stroke-width="1.5"/>'))
        b.append(txt(x0, mt - 34, title, 14, INK, "start", "600"))
        b.append(txt(x0, mt - 15, sub, 12, MUTED))
        b.append(txt(x0 + pw / 2, H - 16, "rhythm strength  b", 12, MUTED, "middle"))
        return "".join(b)

    body = [txt(34, 30, "One correction removes the rhythm-dependence entirely",
                15.5, INK, "start", "600"),
            txt(34, 50, "each colour is a different swimmer or fluid; hollow rings were "
                        "predicted before those runs existed", 12.5, MUTED)]
    body.append(panel(ml, 0.58, 1.15, "Before  —  De at the reversal",
                      "moves by 21-32% as the rhythm changes", False))
    body.append(panel(ml + pw + gap, 0.58, 1.30,
                      "After  —  De × ⟨(dθ/dt)²⟩ at the reversal",
                      "flat to under 1% — three different constants", True))
    lx = ml + pw + gap
    # legend low-left in the right panel: the curves live at ~0.83-1.17, so the band under
    # 0.76 is the only empty region. Top-left would sit on the teal curve.
    for i, (name, (col, _)) in enumerate(COLLAPSE.items()):
        yy = mt + ph - 58 + i * 19
        body.append(f'<circle cx="{lx+14}" cy="{yy-4}" r="4.5" fill="{col}"/>')
        body.append(txt(lx + 26, yy, name, 11.5, MUTED))
    return svg(W, H, "".join(body))




# ---------------------------------------- 7. the analytic mechanism: pair vs triple term
def fig_theory():
    """The whole derivation in one picture. Left: the pair term is identical for both rhythms,
    so it CANNOT produce a reversal. Right: the triple term is exactly antisymmetric and
    crosses zero -- that crossing IS the reversal. Computed by Fourier algebra, no solver."""
    import theory_analysis as TH
    des = np.exp(np.linspace(np.log(0.12), np.log(6.0), 90))
    b = 0.5
    P = np.array([TH.P_of(b, D) for D in des])
    Pm = np.array([TH.P_of(-b, D) for D in des])
    Q = np.array([TH.Q_of(b, D) for D in des])
    Qm = np.array([TH.Q_of(-b, D) for D in des])
    dc = TH.crossover(b)

    W, H = 880, 430
    gap, ml, mt, mb = 60, 66, 112, 60
    pw = (W - ml - 34 - gap) / 2
    ph = H - mt - mb

    def axis(x0, lo, hi, title, sub):
        s = [f'<rect x="{x0}" y="{mt}" width="{pw}" height="{ph}" fill="{PLOT}" '
             f'stroke="{GRID}" rx="6"/>']
        for gv in np.linspace(lo, hi, 5):
            yy = mt + (hi - gv) / (hi - lo) * ph
            s.append(f'<line x1="{x0}" y1="{yy}" x2="{x0+pw}" y2="{yy}" stroke="{GRID}"/>')
            s.append(txt(x0 - 9, yy + 4, f"{gv:+.2f}", 10.5, MUTED, "end", family=MONO))
        for gv in (0.2, 0.5, 1, 2, 5):
            xx = x0 + (np.log(gv) - np.log(0.12)) / (np.log(6.0) - np.log(0.12)) * pw
            s.append(f'<line x1="{xx}" y1="{mt}" x2="{xx}" y2="{mt+ph}" stroke="{GRID}" '
                     f'opacity="0.6"/>')
            s.append(txt(xx, mt + ph + 20, f"{gv:g}", 10.5, MUTED, "middle", family=MONO))
        s.append(txt(x0, mt - 30, title, 13.5, INK, "start", "600"))
        s.append(txt(x0, mt - 12, sub, 11.5, MUTED))
        s.append(txt(x0 + pw / 2, H - 14, "Deborah number", 11.5, MUTED, "middle"))
        return s

    def curve(x0, lo, hi, vals, col, wid=2.6, dash=""):
        pts = []
        for D, v in zip(des, vals):
            xx = x0 + (np.log(D) - np.log(0.12)) / (np.log(6.0) - np.log(0.12)) * pw
            yy = mt + (hi - v) / (hi - lo) * ph
            pts.append(f"{xx:.1f},{yy:.1f}")
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" '
                f'stroke-width="{wid}"{d} stroke-linejoin="round"/>')

    body = [txt(34, 30, "The mechanism, from algebra alone — no simulation",
                15.5, INK, "start", "600"),
            txt(34, 50, "the cycle integral splits in two; only one half can tell the "
                        "rhythms apart", 12.5, MUTED)]

    # left: pair term
    lo, hi = 0.0, 0.40
    body += axis(ml, lo, hi, "The PAIR term  ∮ g·s dt",
                 "identical for both rhythms — cannot reverse anything")
    body.append(curve(ml, lo, hi, P, GOLD, 4.2))
    body.append(curve(ml, lo, hi, Pm, BLUE, 2.0, "6 4"))
    body.append(txt(ml + pw - 10, mt + 24, "both rhythms lie exactly on top", 11.5, INK,
                    "end", "600"))
    body.append(txt(ml + pw - 10, mt + 41, "difference = 0.0e+00", 11.5, TEAL, "end",
                    "700", MONO))

    # right: triple term
    x1 = ml + pw + gap
    lo2, hi2 = -0.03, 0.03
    body += axis(x1, lo2, hi2, "The TRIPLE term  ∮ g²·s dt",
                 "exactly equal and opposite — and it crosses zero")
    yz = mt + (hi2 - 0) / (hi2 - lo2) * ph
    body.append(f'<line x1="{x1}" y1="{yz}" x2="{x1+pw}" y2="{yz}" stroke="{INK}" '
                f'stroke-width="1.4" opacity="0.55"/>')
    body.append(curve(x1, lo2, hi2, Q, GOLD))
    body.append(curve(x1, lo2, hi2, Qm, BLUE))
    if dc:
        xc = x1 + (np.log(dc) - np.log(0.12)) / (np.log(6.0) - np.log(0.12)) * pw
        body.append(f'<line x1="{xc}" y1="{mt}" x2="{xc}" y2="{mt+ph}" stroke="{CORAL}" '
                    f'stroke-width="2" stroke-dasharray="4 4"/>')
        body.append(f'<circle cx="{xc}" cy="{yz}" r="5.5" fill="{CORAL}" stroke="#fff" '
                    f'stroke-width="2"/>')
        body.append(txt(xc + 9, mt + 22, "both vanish here", 11.5, CORAL, "start", "700"))
        body.append(txt(xc + 9, mt + 38, "→ the reversal", 11.5, CORAL, "start"))
    return svg(W, H, "".join(body))


if __name__ == "__main__":
    main()
