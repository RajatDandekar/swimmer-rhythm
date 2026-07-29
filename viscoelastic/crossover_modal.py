"""Two jobs: kill the large-De transient worry, and pin down the rhythm crossover.

WHY
---
The De sweep was run at ncycles=3, on the strength of a "converged by cycle 3 (0.0% drift)"
check that was actually measured at De=3. At De=20 the relaxation time is 20 stroke periods,
so three cycles cannot possibly have reached the periodic orbit -- those points are transients
being read as steady state. Extrapolating a convergence check past the parameter where it was
established is the same class of error as extrapolating Richardson along a wrong error model,
which already cost this project a week.

So: run 14 cycles and report the per-cycle displacement. The last-cycle value is only
meaningful if consecutive cycles have stopped changing, and that has to be demonstrated at
each De rather than assumed from one.

The second job is the interesting one. The ratio crosses 1 somewhere between De=0.5 (0.9512,
linger-open wins) and De=1.0 (1.0434, linger-closed wins) -- the optimal rhythm REVERSES. A
fine scan locates it. That crossing is the strongest evidence so far that this environment has
a real control problem in it: at the crossover the two opposite rhythms are exactly equally
good, and on either side the ranking flips, so no fixed stroke is optimal across De.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-crossover", image=image)

PI = 3.141592653589793
BRINK, D0, AMP = 0.5, 1.0, 0.35
KS = np.array([1.0, 2.0, 3.0])
NCYC = 14

DES = [0.2, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0]


@app.function(cpu=2.0, memory=8192, timeout=14400)
def evaluate(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        b = np.array([job["b1"], 0.0, 0.0]); ph = np.zeros(3)

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        r = Solver2(N=192, L=4 * PI, brink=BRINK, lam=job["lam"],
                    stroke=stroke).run(ncycles=NCYC, nsteps=600)
        out.update(ok=True, per_cycle=[float(x[0]) for x in r],
                   dx=float(r[-1][0]), stokes_res=float(r[-1][1]))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


@app.local_entrypoint()
def main():
    jobs = [dict(lam=De, b1=b) for De in DES for b in (+0.5, -0.5)]
    print(f"launching {len(jobs)} runs at {NCYC} cycles each\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("crossover_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} failed:\n{bad[0]['err']}\n")
    ok = {(r["lam"], r["b1"]): r for r in res if r.get("ok")}

    print("[1] CYCLE CONVERGENCE -- is the last cycle steady state, or still a transient?")
    print(f"    {'De':>6} {'cyc3':>12} {'cyc7':>12} {'cyc14':>12} "
          f"{'drift 13->14':>13} {'3-cyc error':>12}")
    conv = {}
    for De in DES:
        r = ok.get((De, 0.5))
        if not r:
            print(f"    {De:>6} MISSING"); continue
        pc = r["per_cycle"]
        drift = abs(pc[-1] - pc[-2]) / abs(pc[-1])
        err3 = abs(pc[2] - pc[-1]) / abs(pc[-1])
        conv[De] = drift < 0.01
        print(f"    {De:>6.2f} {pc[2]:>12.4e} {pc[6]:>12.4e} {pc[-1]:>12.4e} "
              f"{100*drift:>12.2f}% {100*err3:>11.1f}%"
              + ("" if drift < 0.01 else "   <<< NOT CONVERGED"))

    print("\n[2] RHYTHM RATIO at cycle 14 vs the cycle-3 value used earlier")
    print(f"    {'De':>6} {'linger-closed':>14} {'linger-open':>14} "
          f"{'ratio@14':>10} {'ratio@3':>10} {'winner':>16}")
    rows = []
    for De in DES:
        p, m = ok.get((De, 0.5)), ok.get((De, -0.5))
        if not (p and m):
            print(f"    {De:>6} MISSING"); continue
        q14 = abs(p["per_cycle"][-1]) / abs(m["per_cycle"][-1])
        q3 = abs(p["per_cycle"][2]) / abs(m["per_cycle"][2])
        rows.append((De, q14))
        print(f"    {De:>6.2f} {p['per_cycle'][-1]:>14.5e} {m['per_cycle'][-1]:>14.5e} "
              f"{q14:>10.4f} {q3:>10.4f} {'CLOSED' if q14 > 1 else 'OPEN':>16}")

    cross = [(a, b) for (a, qa), (b, qb) in zip(rows, rows[1:]) if (qa - 1) * (qb - 1) < 0]
    print()
    if cross:
        for a, b in cross:
            qa = dict(rows)[a]; qb = dict(rows)[b]
            De_c = a + (b - a) * (1 - qa) / (qb - qa)      # linear interpolation in De
            print(f"    CROSSOVER between De={a} and De={b}  ->  De_c ~ {De_c:.3f}")
        print("    => the optimal rhythm REVERSES with Deborah number. No single stroke is")
        print("       optimal across the fluid; the best policy depends on a property the")
        print("       swimmer does not directly observe.")
    else:
        print("    no crossover at 14 cycles -- the cycle-3 sign change was a transient.")

    unconv = [De for De, c in conv.items() if not c]
    if unconv:
        print(f"\n    NOT converged even at {NCYC} cycles: De = {unconv}")
        print("    -> treat those ratios as transients; they need a longer run to trust.")
    print(f"\n    max |oint U_stokes| = "
          f"{max(abs(r['stokes_res']) for r in res if r.get('ok')):.1e}")
