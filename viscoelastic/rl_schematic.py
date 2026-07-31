"""The reinforcement-learning loop, as a clean labelled schematic (SVG).

Agent (policy) -> action (a stroke rhythm) -> environment (the viscoelastic fluid solver) ->
reward (net displacement at fixed energy) -> policy-gradient update -> back to the agent.
Built to sit on the site in the same warm-paper design language.
"""
INK, INK2, MUTED, FAINT = "#16130d", "#3a352b", "#6d665a", "#a49c8c"
LINE, PANEL, SINK = "#e7e2d5", "#ffffff", "#f6f4ec"
CO, CC, MAG, GOOD = "#1a6fb0", "#d06a1c", "#b3006b", "#1c7a55"
UI = "ui-sans-serif,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',Menlo,Consolas,monospace"
SER = "Fraunces,Georgia,serif"


def box(x, y, w, h, title, sub, accent, tcol=None):
    tcol = tcol or accent
    return f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{PANEL}" stroke="{LINE}"/>
  <rect x="{x}" y="{y}" width="5" height="{h}" rx="2.5" fill="{accent}"/>
  <text x="{x+w/2}" y="{y+27}" font-size="15.5" fill="{INK}" text-anchor="middle"
        font-family="{SER}" font-weight="600">{title}</text>
  <text x="{x+w/2}" y="{y+48}" font-size="12" fill="{MUTED}" text-anchor="middle"
        font-family="{UI}">{sub}</text>'''


def arrow(x1, y1, x2, y2, label, sub, col, curve=0):
    mid = f"M {x1} {y1} C {x1+curve} {(y1+y2)/2}, {x2-curve} {(y1+y2)/2}, {x2} {y2}" \
        if curve else f"M {x1} {y1} L {x2} {y2}"
    lx, ly = (x1 + x2) / 2, (y1 + y2) / 2
    txt = f'''
  <text x="{lx}" y="{ly-11}" font-size="12" fill="{col}" text-anchor="middle"
        font-family="{UI}" font-weight="600">{label}</text>
  <text x="{lx}" y="{ly+11}" font-size="10" fill="{MUTED}" text-anchor="middle"
        font-family="{MONO}">{sub}</text>''' if label else ""
    return f'<path d="{mid}" fill="none" stroke="{col}" stroke-width="2" ' \
           f'marker-end="url(#ah-{col.strip("#")})"/>{txt}'


def main():
    W, H = 900, 430
    cols = [CO, CC, MAG]
    defs = "".join(
        f'<marker id="ah-{c.strip("#")}" markerWidth="9" markerHeight="9" refX="7" refY="3.2" '
        f'orient="auto"><path d="M0,0 L7,3.2 L0,6.4 Z" fill="{c}"/></marker>' for c in cols)

    b = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" '
         f'style="max-width:{W}px;height:auto"><defs>{defs}</defs>',
         f'<rect width="{W}" height="{H}" rx="14" fill="{PANEL}" stroke="{LINE}"/>']
    b.append(f'<text x="34" y="40" font-size="19" fill="{INK}" font-family="{SER}" '
             f'font-weight="600">How the agent learns to swim</text>')
    b.append(f'<text x="34" y="63" font-size="13" fill="{MUTED}" font-family="{UI}">a '
             f'policy trained by REINFORCE — no equations, no target stroke, only a scalar '
             f'reward</text>')

    # three boxes across the middle
    y0, bh = 150, 96
    b.append(box(60, y0, 210, bh, "Agent", "policy network π(a | s)", CO))
    b.append(box(345, y0, 210, bh, "Environment", "viscoelastic fluid solver", CC))
    b.append(box(630, y0, 210, bh, "Reward", "how far it swam", GOOD))

    # forward arrows
    b.append(arrow(272, y0 + bh / 2, 343, y0 + bh / 2, "action",
                   "rhythm ρ(t)", CO))
    b.append(arrow(557, y0 + bh / 2, 628, y0 + bh / 2, "outcome",
                   "Δx / stroke", CC))

    # feedback loop: reward -> update -> agent (down, across, up)
    yb = y0 + bh + 70
    b.append(f'<path d="M735 {y0+bh} L735 {yb} L165 {yb} L165 {y0+bh}" fill="none" '
             f'stroke="{MAG}" stroke-width="2" marker-end="url(#ah-{MAG.strip("#")})"/>')
    b.append(f'<rect x="360" y="{yb-22}" width="180" height="44" rx="10" fill="{SINK}" '
             f'stroke="{LINE}"/>')
    b.append(f'<text x="450" y="{yb-3}" font-size="13" fill="{MAG}" text-anchor="middle" '
             f'font-family="{UI}" font-weight="600">policy-gradient update</text>')
    b.append(f'<text x="450" y="{yb+14}" font-size="10.5" fill="{MUTED}" text-anchor="middle" '
             f'font-family="{MONO}">nudge π toward higher reward</text>')

    # the reward definition, boxed at the bottom
    ry = yb + 46
    b.append(f'<rect x="60" y="{ry}" width="780" height="42" rx="10" fill="{PANEL}" '
             f'stroke="{GOOD}" stroke-opacity="0.5"/>')
    b.append(f'<text x="80" y="{ry+26}" font-size="12.5" fill="{MUTED}" font-family="{UI}">'
             f'reward &#160;=&#160;</text>')
    b.append(f'<text x="150" y="{ry+26}" font-size="14" fill="{INK}" font-family="{MONO}" '
             f'font-weight="700">net displacement per stroke</text>')
    b.append(f'<text x="440" y="{ry+26}" font-size="12.5" fill="{MUTED}" font-family="{UI}">'
             f'&#160;&#160;at a fixed energy budget &#160;(so it cannot cheat by pushing '
             f'harder)</text>')

    b.append("</svg>")
    open("site/figures/rl_loop.svg", "w").write("".join(b))
    print("wrote site/figures/rl_loop.svg")


if __name__ == "__main__":
    import os
    os.makedirs("site/figures", exist_ok=True)
    main()
