"""Search the effort-constraint SURFACE, with one candidate set shared across Deborah numbers.

TWO FLAWS IN THE PARETO RUN, BOTH FIXED HERE
--------------------------------------------
1. The RNG stream continued between the De=0.5 and De=3.0 groups, so only 5 of 205 candidates
   were shared. The cross-De comparison was meaningless (it printed nan) and "sinusoid optimal
   at De=3 but beaten at De=0.5" was confounded with different sampling. Here ONE candidate set
   is built once and evaluated at every De, so any difference between Deborah numbers is the
   physics and not the draw.

2. Random sampling put only 12-18 of 205 candidates inside the effort budget -- ~93% of the PDE
   time was spent on strokes that could never be compared fairly. But effort needs no PDE: it is
   quadrature on the stroke, microseconds per candidate. So pre-sample 200k rhythms locally,
   keep the ones that already sit ON the constraint surface, and spend PDE time only on those.

WHAT THIS MEASURES
------------------
Every candidate is matched to the plain sinusoid on excursion, path and period (by construction
via the theta-reparametrisation) AND on effort (by selection, to within 0.4%). There is no slack
on any constraint. So if a rhythm beats the sinusoid here, the win is unambiguous -- it cannot
be a larger stroke, a faster stroke, or more actuation energy, because all of those are pinned.

Note the classic +/-b1 probes are NOT feasible here: their effort is 0.0657-0.0721 against the
sinusoid's 0.06125. The budget-feasible rhythms are a subtler family, which is the point -- the
strokes that win at fixed effort are not the ones that win when effort is free.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-constraint", image=image)

PI = 3.141592653589793
BRINK, D0, AMP = 0.5, 1.0, 0.35
KS = np.array([1.0, 2.0, 3.0])
N_GRID, L_BOX, NSTEPS, NCYC = 192, 4 * PI, 600, 8
DES = [0.3, 0.5, 0.8, 1.5, 3.0]          # spanning the crossover at De_c ~ 0.809
SIN_EFFORT = 0.06125
NCAND = 180
BAND = (0.06095, 0.06125)                # at or just under the sinusoid's own budget


def guard_batch(b):
    """Monotonicity guard, vectorised. Same rule the solver applies."""
    s = np.abs(b * KS).sum(axis=1)
    f = np.where(s > 0.90, 0.90 / np.maximum(s, 1e-300), 1.0)
    return b * f[:, None]


def effort_batch(b, ph, T=1024):
    """<(dd/dt)^2> for a batch of rhythms. Pure quadrature -- no PDE, no Modal."""
    t = np.linspace(0, 2 * PI, T, endpoint=False)
    out = np.empty(len(b))
    for i in range(0, len(b), 4000):
        bb, pp = b[i:i + 4000], ph[i:i + 4000]
        arg = KS[None, :, None] * t[None, None, :] + pp[:, :, None]
        th = t[None, :] + (bb[:, :, None] * np.sin(arg)).sum(1)
        dth = 1.0 + (bb[:, :, None] * KS[None, :, None] * np.cos(arg)).sum(1)
        dd = -AMP * np.sin(th) * dth
        out[i:i + 4000] = (dd ** 2).mean(axis=1)
    return out


@app.function(cpu=2.0, memory=8192, timeout=14400)
def evaluate(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        b = np.array(job["b"]); ph = np.array(job["ph"])

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        r = Solver2(N=job.get("N", N_GRID), L=L_BOX, brink=BRINK, lam=job["lam"],
                    stroke=stroke).run(ncycles=job.get("ncycles", NCYC),
                                       nsteps=job.get("nsteps", NSTEPS))
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   drift=float(abs(r[-1][0] - r[-2][0]) / abs(r[-1][0])))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


@app.local_entrypoint()
def main():
    rng = np.random.default_rng(11)
    M = 200000
    b = guard_batch(rng.uniform(-0.8, 0.8, (M, 3)))
    ph = rng.uniform(-PI, PI, (M, 3))
    e = effort_batch(b, ph)
    sel = np.where((e >= BAND[0]) & (e <= BAND[1]))[0]
    print(f"pre-sampled {M} rhythms locally; {len(sel)} sit on the effort surface "
          f"[{BAND[0]}, {BAND[1]}]")
    take = rng.choice(sel, size=min(NCAND, len(sel)), replace=False)
    cands = [dict(b=[float(x) for x in b[i]], ph=[float(x) for x in ph[i]],
                  effort=float(e[i]), cid=int(n)) for n, i in enumerate(take)]
    cands.append(dict(b=[0., 0., 0.], ph=[0., 0., 0.], effort=SIN_EFFORT, cid=-1))
    print(f"selected {len(cands)} candidates (incl. the sinusoid as cid=-1), "
          f"evaluated at De = {DES}\n")

    jobs = [dict(c, lam=De) for De in DES for c in cands]
    print(f"launching {len(jobs)} runs, one wave\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("constraint_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)}/{len(res)} failed:\n{bad[0]['err']}\n")
    ok = [r for r in res if r.get("ok")]
    print(f"worst per-cycle drift: {100*max(r['drift'] for r in ok):.2f}%   "
          f"max |oint U_stokes| = {max(abs(r['stokes_res']) for r in ok):.1e}\n")

    by = {}
    for r in ok:
        by.setdefault(r["lam"], {})[r["cid"]] = r

    print("BEST RHYTHM AT EACH De, all constraints matched (excursion, path, period, effort)")
    print(f"  {'De':>5} {'sinusoid dx':>13} {'best dx':>13} {'gain':>8} {'cid':>5} "
          f"{'effort':>8}  b")
    best = {}
    for De in DES:
        g = by.get(De, {})
        sin = g.get(-1)
        if not sin:
            print(f"  {De:>5} sinusoid MISSING"); continue
        w = max((r for r in g.values() if r["cid"] >= 0), key=lambda r: abs(r["dx"]))
        best[De] = w
        gain = abs(w["dx"]) / abs(sin["dx"])
        print(f"  {De:>5.1f} {sin['dx']:>13.5e} {w['dx']:>13.5e} {gain:>7.4f}x "
              f"{w['cid']:>5} {w['effort']:>8.5f}  "
              f"[{w['b'][0]:+.3f} {w['b'][1]:+.3f} {w['b'][2]:+.3f}]")

    print("\nDOES THE OPTIMUM MOVE?  each De's winner, evaluated at every De (gain vs sinusoid)")
    hdr = "  " + "winner\\eval".ljust(14) + "".join(f"{De:>10.1f}" for De in DES)
    print(hdr)
    for Dw in DES:
        if Dw not in best:
            continue
        cid = best[Dw]["cid"]
        row = f"  best@De={Dw:<7.1f}"
        for De in DES:
            g = by.get(De, {})
            if cid in g and -1 in g:
                row += f"{abs(g[cid]['dx'])/abs(g[-1]['dx']):>10.4f}"
            else:
                row += f"{'--':>10}"
        print(row)
    print("  (diagonal = its own De. If the diagonal dominates its column, the optimal")
    print("   rhythm is De-specific and no single fixed stroke can be optimal.)")

    print("\nHOW MANY CANDIDATES BEAT THE SINUSOID AT EACH De?")
    for De in DES:
        g = by.get(De, {})
        sin = g.get(-1)
        if not sin:
            continue
        n = sum(1 for r in g.values() if r["cid"] >= 0 and abs(r["dx"]) > abs(sin["dx"]))
        tot = sum(1 for r in g.values() if r["cid"] >= 0)
        print(f"  De={De:<5.1f} {n:>4}/{tot} beat it  ({100*n/tot:.0f}%)"
              + ("   <- sinusoid is NOT optimal here" if n else
                 "   <- sinusoid survives every sampled rhythm"))
