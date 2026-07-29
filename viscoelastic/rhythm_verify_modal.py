"""Refine the rhythm-reversal pairs before believing 31.5%.

The last headline number (1.0342x) was resolution-stable and still collapsed, because the
flaw was in the experiment design rather than the discretisation. This one has the design
flaw closed by construction -- b -> -b holds excursion, effort, path, peak rate and period
*exactly* fixed -- so discretisation is the remaining way to be wrong. Hence this run.

WHAT IS MEASURED
----------------
[A] The within-pair RATIO, refined. Both members of a pair are evaluated at the same
    resolution and the ratio taken, so common-mode error cancels; the question is whether the
    ratio holds still under 4x timestep, finer grid, bigger box, and more cycles. The pair is
    the ideal object for this: the two strokes are mirror images, so they discretise almost
    identically and anything that survives the ratio is physics.

[B] Deborah sweep of the same ratio. The whole effect is fluid memory, so it must vanish as
    De -> 0 (no memory: rate-independence, and rhythm cannot matter) and it must vanish as
    De -> infinity (frozen polymer: no relaxation during the stroke, so nothing can be timed
    against). A peak in between is the signature of the mechanism actually being memory
    rather than a numerical asymmetry. If the ratio does NOT decay at small De, the effect is
    not memory and the interpretation is wrong.

[B] is the real test. [A] only checks that the number is converged; [B] checks that the number
means what I claim it means.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-rhythm-verify", image=image)

PI = 3.141592653589793
BRINK = 0.5
D0, AMP = 1.0, 0.35
KS = np.array([1.0, 2.0, 3.0])

PAIRS = [("linger-closed / linger-open   (phi=0)", 0.0),
         ("dawdle-closing / hurry-closing (phi=-pi/2)", -PI / 2)]


@app.function(cpu=2.0, memory=8192, timeout=10800)
def evaluate(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        b = np.array([job["b1"], 0.0, 0.0]); ph = np.array([job["phi"], 0.0, 0.0])

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        r = Solver2(N=job["N"], L=job["L"], brink=BRINK, lam=job["lam"],
                    stroke=stroke).run(ncycles=job["ncycles"], nsteps=job["nsteps"])
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


LADDER = [("reference  ", 192, 4 * PI, 600, 3),
          ("4x timestep", 192, 4 * PI, 2400, 3),
          ("finer grid ", 288, 4 * PI, 600, 3),
          ("bigger box ", 288, 6 * PI, 600, 3),
          ("refined all", 288, 4 * PI, 1200, 5)]
DES = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0]


@app.local_entrypoint()
def main():
    jobs = []
    for name, phi in PAIRS:
        for tag, N, L, ns, nc in LADDER:
            for b1 in (+0.5, -0.5):
                jobs.append(dict(kind="ladder", pair=name, tag=tag, b1=b1, phi=phi,
                                 N=N, L=L, nsteps=ns, ncycles=nc, lam=3.0))
    for De in DES:
        for b1 in (+0.5, -0.5):
            jobs.append(dict(kind="de", pair=PAIRS[0][0], tag=f"De={De}", b1=b1,
                             phi=0.0, N=192, L=4 * PI, nsteps=600, ncycles=3, lam=De))
    print(f"launching {len(jobs)} runs\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("rhythm_verify_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} failed:\n{bad[0]['err']}\n")
    ok = [r for r in res if r.get("ok")]

    def get(**q):
        for r in ok:
            if all(abs(r[k] - v) < 1e-12 if isinstance(v, float) else r[k] == v
                   for k, v in q.items()):
                return r
        return None

    print("[A] RESOLUTION LADDER -- the within-pair ratio must hold still")
    for name, phi in PAIRS:
        print(f"\n  {name}")
        print(f"    {'config':<12} {'b=+0.5':>13} {'b=-0.5':>13} {'ratio':>9}")
        rr = []
        for tag, N, L, ns, nc in LADDER:
            p = get(kind="ladder", pair=name, tag=tag, b1=+0.5, nsteps=ns, N=N, L=L, ncycles=nc)
            m = get(kind="ladder", pair=name, tag=tag, b1=-0.5, nsteps=ns, N=N, L=L, ncycles=nc)
            if not (p and m):
                print(f"    {tag:<12} MISSING"); continue
            q = abs(p["dx"]) / abs(m["dx"]); rr.append(q)
            print(f"    {tag:<12} {p['dx']:>13.5e} {m['dx']:>13.5e} {q:>8.4f}x")
        if rr:
            print(f"    -> ratio spread over the ladder: "
                  f"{100*(max(rr)-min(rr)):.2f} percentage points "
                  + ("(CONVERGED)" if max(rr) - min(rr) < 0.02 else "(NOT CONVERGED)"))

    print("\n[B] DEBORAH SWEEP of the ratio -- must vanish at BOTH ends if this is memory")
    print(f"    {'De':>7} {'b=+0.5':>13} {'b=-0.5':>13} {'ratio':>9}   asymmetry")
    rows = []
    for De in DES:
        p = get(kind="de", b1=+0.5, lam=De); m = get(kind="de", b1=-0.5, lam=De)
        if not (p and m):
            print(f"    {De:>7} MISSING"); continue
        q = abs(p["dx"]) / abs(m["dx"]); rows.append((De, q))
        bar = "#" * int(round(120 * abs(q - 1.0)))
        print(f"    {De:>7.2f} {p['dx']:>13.5e} {m['dx']:>13.5e} {q:>8.4f}x   {bar}")
    if rows:
        pk = max(rows, key=lambda r: abs(r[1] - 1.0))
        lo, hi = rows[0], rows[-1]
        print(f"\n    De -> 0  ({lo[0]}):  ratio {lo[1]:.4f}   "
              + ("-> 1, rhythm stops mattering. CORRECT." if abs(lo[1] - 1) < 0.05
                 else "<<< does NOT vanish -- not a memory effect"))
        print(f"    De -> inf ({hi[0]}): ratio {hi[1]:.4f}")
        print(f"    peak asymmetry at De = {pk[0]}  (ratio {pk[1]:.4f})")

    print(f"\n    max |oint U_stokes| = {max(abs(r['stokes_res']) for r in ok):.1e}")
