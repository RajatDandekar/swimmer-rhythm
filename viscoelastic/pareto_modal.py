"""The achievable set, not my choice of objective.

Twice now a scalar objective has produced a misleading answer: equal-effort let the optimiser
buy excursion (2.31 of its 3.42 points), and raw-displacement-at-fixed-excursion lets a rhythm
win by simply spending more effort. Every scalar I pick embeds a judgement about what is
scarce for the swimmer, and I keep picking wrong.

So stop picking. Sample the rhythm space, record (effort, displacement) for every candidate,
and report the PARETO FRONT. That is metric-free: it is the set of achievable trade-offs, and
any particular objective is just a direction of approach to it. The reader can impose their own
scarcity and read off their own optimum.

Excursion, path and period are still fixed by construction (the theta-reparametrisation), so
the only trade left is displacement against actuation effort -- exactly the trade that should
be on the table.

THE HEADLINE NUMBER, loophole-free
----------------------------------
Along the front, read off the best displacement available at effort <= the plain sinusoid's own
effort (0.061250). At that point the winning rhythm is matched to the sinusoid on excursion,
path, period AND effort simultaneously, with no slack anywhere. Whatever it beats the sinusoid
by is then unambiguous.

RUN AT TWO DEBORAH NUMBERS, either side of the crossover at De_c ~ 0.809, because the
interesting claim is not that some rhythm wins -- it is that the winner is a DIFFERENT rhythm
on each side, which is what makes this a control problem rather than a one-off optimisation.

Note this needs no evolution strategy: sampling is embarrassingly parallel, so the whole study
is ONE .map() with no sequential generation barrier. The ES cost 10 sequential generations of
wall-clock to search a space this size; this is one wave.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-pareto", image=image)

PI = 3.141592653589793
BRINK, D0, AMP = 0.5, 1.0, 0.35
KS = np.array([1.0, 2.0, 3.0])
N_GRID, L_BOX, NSTEPS = 192, 4 * PI, 600
NCYC = 8                      # De=3 converges by cycle 7; De=0.5 by cycle 3
DES = [0.5, 3.0]              # either side of De_c ~ 0.809
NRAND = 200
SIN_EFFORT = 0.061250         # the plain sinusoid's own effort, at this excursion


def guard(b):
    """Keep theta monotone so every candidate traverses the same segment once out, once back."""
    b = np.asarray(b, dtype=float)
    s = float(np.sum(np.abs(b * KS)))
    return b * (0.90 / s) if s > 0.90 else b


@app.function(cpu=2.0, memory=8192, timeout=14400)
def evaluate(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        b = guard(np.array(job["b"])); ph = np.array(job["ph"])

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        t = np.linspace(0, 2 * PI, 100001)
        th = t + (b[:, None] * np.sin(KS[:, None] * t + ph[:, None])).sum(0)
        dth = 1.0 + (b[:, None] * KS[:, None] * np.cos(KS[:, None] * t + ph[:, None])).sum(0)
        d = D0 + AMP * np.cos(th); dd = -AMP * np.sin(th) * dth

        r = Solver2(N=N_GRID, L=L_BOX, brink=BRINK, lam=job["lam"],
                    stroke=stroke).run(ncycles=NCYC, nsteps=NSTEPS)
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   b=[float(x) for x in b],
                   effort=float(np.trapezoid(dd ** 2, t) / (2 * PI)),
                   excursion=float(d.max() - d.min()),
                   peak_rate=float(np.abs(dd).max()),
                   drift=float(abs(r[-1][0] - r[-2][0]) / abs(r[-1][0])))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


@app.local_entrypoint()
def main():
    rng = np.random.default_rng(7)
    jobs = []
    for De in DES:
        jobs.append(dict(lam=De, kind="sinusoid", b=[0., 0., 0.], ph=[0., 0., 0.]))
        for b1 in (+0.5, -0.5):                       # the two probe pairs, for continuity
            for phi in (0.0, -PI / 2):
                jobs.append(dict(lam=De, kind="probe", b=[b1, 0., 0.], ph=[phi, 0., 0.]))
        for _ in range(NRAND):
            jobs.append(dict(lam=De, kind="random",
                             b=list(rng.uniform(-0.8, 0.8, 3)),
                             ph=list(rng.uniform(-PI, PI, 3))))
    print(f"launching {len(jobs)} runs ({NCYC} cycles each), one parallel wave\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("pareto_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)}/{len(res)} failed:\n{bad[0]['err']}\n")
    ok = [r for r in res if r.get("ok")]

    exc = max(abs(r["excursion"] - 2 * AMP) for r in ok)
    dmax = max(r["drift"] for r in ok)
    print(f"excursion fixed across all {len(ok)} candidates to {exc:.1e}  (loophole closed)")
    print(f"worst per-cycle drift at cycle {NCYC}: {100*dmax:.2f}% "
          + ("(converged)" if dmax < 0.01 else "(SOME NOT CONVERGED)"))
    print(f"max |oint U_stokes| = {max(abs(r['stokes_res']) for r in ok):.1e}\n")

    for De in DES:
        grp = [r for r in ok if r["lam"] == De]
        sin = next(r for r in grp if r["kind"] == "sinusoid")
        s = abs(sin["dx"])
        print(f"{'='*78}\nDe = {De}   sinusoid: dx = {sin['dx']:.5e}, "
              f"effort = {sin['effort']:.5f}")

        # Pareto front: maximise |dx|, minimise effort
        pts = sorted(grp, key=lambda r: r["effort"])
        front, best = [], -1.0
        for r in pts:
            if abs(r["dx"]) > best:
                best = abs(r["dx"]); front.append(r)
        print(f"  front has {len(front)} points out of {len(grp)} sampled")
        print(f"    {'effort':>9} {'dx':>13} {'vs sinusoid':>12}  b (guarded)")
        for r in front:
            print(f"    {r['effort']:>9.5f} {r['dx']:>13.5e} {abs(r['dx'])/s:>11.4f}x  "
                  f"[{r['b'][0]:+.3f} {r['b'][1]:+.3f} {r['b'][2]:+.3f}]")

        # the loophole-free headline: best displacement at or below the sinusoid's own effort
        feas = [r for r in grp if r["effort"] <= SIN_EFFORT * 1.0001]
        if feas:
            w = max(feas, key=lambda r: abs(r["dx"]))
            print(f"\n  AT THE SINUSOID'S OWN EFFORT BUDGET ({SIN_EFFORT:.5f}) -- "
                  f"{len(feas)} feasible candidates")
            print(f"    best: dx = {w['dx']:.5e}  = {abs(w['dx'])/s:.4f}x the sinusoid")
            print(f"    b = [{w['b'][0]:+.3f} {w['b'][1]:+.3f} {w['b'][2]:+.3f}]  "
                  f"phi = [{w['ph'][0]:+.3f} {w['ph'][1]:+.3f} {w['ph'][2]:+.3f}]  "
                  f"effort = {w['effort']:.5f}")
            if abs(w["dx"]) / s > 1.02:
                print("    => a rhythm beats the sinusoid with NO slack on any constraint.")
            else:
                print("    => sinusoid is essentially optimal at its own effort budget.")
        print()

    # does the optimum MOVE between the two Deborah numbers? that is the control claim.
    if len(DES) == 2:
        ws = []
        for De in DES:
            grp = [r for r in ok if r["lam"] == De]
            feas = [r for r in grp if r["effort"] <= SIN_EFFORT * 1.0001]
            ws.append(max(feas, key=lambda r: abs(r["dx"])) if feas else None)
        if all(ws):
            print("=" * 78)
            print("DOES THE OPTIMAL RHYTHM MOVE WITH De?  (cross-evaluate each winner at both)")
            for i, De in enumerate(DES):
                other = ws[1 - i]
                same = [r for r in ok if r["lam"] == De
                        and r["b"] == other["b"] and r["ph"] == other["ph"]]
                grp = [r for r in ok if r["lam"] == De]
                s = abs(next(r for r in grp if r["kind"] == "sinusoid")["dx"])
                own = abs(ws[i]["dx"]) / s
                cross = abs(same[0]["dx"]) / s if same else float("nan")
                print(f"  at De={De}: its own best rhythm gives {own:.4f}x; "
                      f"the OTHER De's best rhythm gives {cross:.4f}x")
            print("  (a large gap means the optimal stroke is De-specific -> real control problem)")
