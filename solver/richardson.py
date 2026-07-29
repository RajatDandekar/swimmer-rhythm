"""Richardson-extrapolate the O((kb)^4) coefficient to pin it to an exact fraction,
and dump the sweep to JSON for plotting."""
import json
from fractions import Fraction
import numpy as np
from taylor_spectral import swim_speed_avg

def coeff_series(eps_list, kind, N=28):
    """c(eps) = [(-U/V)/(0.5 eps^2) - 1]/eps^2  ->  c + d eps^2 + ...  as eps->0."""
    out = []
    for eps in eps_list:
        U, sd, r = swim_speed_avg(eps, N=N, kind=kind, nt=8)
        c = ((-U) / (0.5 * eps ** 2) - 1.0) / eps ** 2
        out.append((eps, U, c, r))
    return out

def richardson(eps, c):
    """Successively eliminate the leading eps^2 error term."""
    e = np.asarray(eps, float); v = np.asarray(c, float)
    table = [v]
    while len(v) > 1:
        e2 = e ** 2
        v = (v[1:] * e2[:-1] - v[:-1] * e2[1:]) / (e2[:-1] - e2[1:])
        e = e[1:]
        table.append(v)
    return table

results = {}
for kind, exact_label, exact_val in (
        ("transverse",   "-1",     -1.0),
        ("inextensible", "-19/16", -19 / 16)):
    print(f"\n=== {kind} ===")
    eps_list = [0.16, 0.12, 0.09, 0.0675, 0.050625]   # geometric, ratio 4/3
    rows = coeff_series(eps_list, kind)
    for eps, U, c, r in rows:
        print(f"  kb={eps:.6f}  U={U:+.14f}  c_raw={c:+.9f}  resid={r:.1e}")
    tab = richardson([r[0] for r in rows], [r[2] for r in rows])
    print("  Richardson tableau (each row eliminates one more (kb)^2 order):")
    for i, row in enumerate(tab):
        print(f"    order {i}: " + "  ".join(f"{x:+.9f}" for x in row))
    best = tab[-1][0]
    print(f"  --> extrapolated c = {best:+.10f}")
    print(f"      exact {exact_label:>7} = {exact_val:+.10f}   "
          f"rel.err = {abs(best - exact_val) / abs(exact_val):.2e}")
    print(f"      nearest fraction (den<=64): {Fraction(best).limit_denominator(64)}")
    results[kind] = {"c_extrapolated": best, "c_exact": exact_val,
                     "exact_label": exact_label,
                     "raw": [{"kb": r[0], "U": r[1], "c": r[2]} for r in rows]}

# --- sweep for plotting -------------------------------------------------------
print("\n=== plotting sweep ===")
sweep = {}
kbs = np.concatenate([np.linspace(0.02, 0.3, 15), np.linspace(0.35, 0.8, 10)])
for kind in ("transverse", "inextensible"):
    xs, us = [], []
    for eps in kbs:
        N = 24 if eps <= 0.3 else (34 if eps <= 0.55 else 44)
        U, sd, r = swim_speed_avg(float(eps), N=N, kind=kind, nt=6)
        xs.append(float(eps)); us.append(float(-U))
        if r > 1e-6:
            print(f"  warn {kind} kb={eps:.3f} resid={r:.1e}")
    sweep[kind] = {"kb": xs, "U_over_V": us}
    print(f"  {kind}: {len(xs)} points, kb in [{xs[0]:.3f},{xs[-1]:.3f}]")

json.dump({"coefficients": results, "sweep": sweep},
          open("taylor_results.json", "w"), indent=1)
print("\nwrote taylor_results.json")
