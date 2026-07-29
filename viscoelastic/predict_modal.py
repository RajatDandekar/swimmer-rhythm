"""Out-of-sample test of the collapse. Predictions stated BEFORE the runs.

WHAT THE SCALING STUDY FOUND
----------------------------
The critical Deborah number where the optimal rhythm reverses moves by 8.9% as rhythm strength
b varies over 0.25-0.80. But

    De_c x <(dtheta/dt)^2>  =  De_c x (1 + b^2/2)  =  0.9069 +/- 0.34%

<(dtheta/dt)^2> = 1 + b^2/2 is not a fitted form -- it is the exact analytic mean-square of the
phase speed for theta = t + b sin t, since <cos^2> = 1/2. Nothing was tuned. The reading is that
the fluid does not care about the stroke's nominal frequency; it responds to the mean-square
rate at which it is actually being deformed.

A collapse fitted and then admired on its own training data is worth very little. Two tests:

[A] EXTRAPOLATION. Two rhythm strengths OUTSIDE the range that produced the collapse, with the
    crossover predicted in advance:

        b = 0.15  ->  De_c predicted 0.8969
        b = 0.88  ->  De_c predicted 0.6538

    If measurement lands on those, the group has predictive content. If it does not, it was a
    smooth interpolation over five points and nothing more.

[B] FACTORISATION. The other parameters (amplitude, asymmetry, confinement, polymer fraction)
    move De_c by 34-44% and the group says nothing about them. The claim is narrower and
    sharper: the b-dependence FACTORISES OUT as <(dtheta/dt)^2>, leaving a residue that depends
    on everything else. So at a different amplitude and at a different confinement, sweeping b
    should again collapse -- onto a DIFFERENT constant. Same collapse, different intercept.

    If instead the constant drifts with b at the new settings, the group is not separable and
    the whole thing is a local coincidence around one operating point.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-predict", image=image)
STATE = modal.Dict.from_name("viscoelastic-predict-state", create_if_missing=True)

PI = 3.141592653589793
KS = np.array([1.0, 2.0, 3.0])
D0 = 1.0
N_GRID, L_BOX, NSTEPS, NCYC = 192, 4 * PI, 600, 6
K_COLLAPSE = 0.9069                      # measured on the b-sweep, used here as a PREDICTOR

BASE = dict(amp=0.35, eps1=0.14, eps2=0.26, brink=0.5, eta_p=1.0)
CASES = (
    [dict(BASE, b1=b, _fam="EXTRAPOLATION (baseline)", _b=b) for b in (0.15, 0.88)]
    + [dict(BASE, amp=0.28, b1=b, _fam="FACTORISATION at A=0.28", _b=b)
       for b in (0.30, 0.60, 0.80)]
    + [dict(BASE, brink=0.8, b1=b, _fam="FACTORISATION at l=0.8", _b=b)
       for b in (0.30, 0.60, 0.80)]
)
DES = [0.42, 0.50, 0.58, 0.66, 0.74, 0.82, 0.92, 1.02, 1.15, 1.30]


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
def evaluate(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        b = np.array([job["b1"] * job["sign"], 0.0, 0.0]); ph = np.zeros(3)
        A = job["amp"]

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + A * np.cos(th), -A * np.sin(th) * dth)

        r = Solver2(N=N_GRID, L=L_BOX, brink=job["brink"], lam=job["lam"],
                    eps1=job["eps1"], eps2=job["eps2"], eta_p=job["eta_p"],
                    stroke=stroke).run(ncycles=NCYC, nsteps=NSTEPS)
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   drift=float(abs(r[-1][0] - r[-2][0]) / max(abs(r[-1][0]), 1e-300)))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-400:])
    return out


@app.function(cpu=1.0, memory=2048, timeout=14400)
def driver() -> dict:
    jobs = []
    for i, c in enumerate(CASES):
        for De in DES:
            for sg in (+1, -1):
                jobs.append({k: v for k, v in c.items() if not k.startswith("_")}
                            | dict(lam=De, sign=sg, cid=i))
    STATE["status"] = dict(state="running", n=len(jobs))
    raw = list(evaluate.map(jobs, return_exceptions=True))
    res = [r for r in raw if isinstance(r, dict)]
    STATE["results"] = res
    STATE["meta"] = [{k: v for k, v in c.items() if k.startswith("_")} | {"i": i}
                     for i, c in enumerate(CASES)]
    STATE["status"] = dict(state="done", n=len(jobs), ok=len(res), dead=len(raw) - len(res))
    return dict(ok=len(res))


@app.local_entrypoint()
def main():
    print("PREDICTIONS, fixed before the runs (K = %.4f):" % K_COLLAPSE)
    for b in (0.15, 0.88):
        print("   b = %.2f  ->  De_c predicted %.4f" % (b, K_COLLAPSE / (1 + b ** 2 / 2)))
    call = driver.spawn()
    print(f"\nspawned, call id = {call.object_id}")
    print("read:  modal run predict_modal.py::status")


@app.local_entrypoint()
def status():
    try:
        st = STATE["status"]
    except KeyError:
        print("no state yet"); return
    print(f"status: {st}")
    if st.get("state") != "done":
        return
    res = [r for r in STATE["results"] if r.get("ok")]
    meta = STATE["meta"]
    json.dump(dict(results=res, meta=meta), open("predict_results.json", "w"), indent=1)

    def crossing(cid):
        g = {}
        for r in res:
            if r["cid"] == cid:
                g.setdefault(r["lam"], {})[r["sign"]] = r["dx"]
        des = sorted(d for d in g if 1 in g[d] and -1 in g[d])
        q = [abs(g[d][1]) / abs(g[d][-1]) for d in des]
        for a, b_, qa, qb in zip(des, des[1:], q, q[1:]):
            if (qa - 1) * (qb - 1) < 0:
                la, lb = np.log(a), np.log(b_)
                return float(np.exp(la + (lb - la) * (1 - qa) / (qb - qa)))
        return None

    print("\n[A] EXTRAPOLATION — predicted in advance, outside the fitted range")
    print("  %6s %12s %12s %10s" % ("b", "predicted", "measured", "error"))
    for m in meta:
        if not m["_fam"].startswith("EXTRAP"):
            continue
        b_ = m["_b"]; pred = K_COLLAPSE / (1 + b_ ** 2 / 2); got = crossing(m["i"])
        if got is None:
            print("  %6.2f %12.4f %12s" % (b_, pred, "no crossing")); continue
        print("  %6.2f %12.4f %12.4f %9.1f%%" % (b_, pred, got, 100 * (got - pred) / pred))

    print("\n[B] FACTORISATION — b-sweep at other settings must collapse onto its own constant")
    for fam in ("FACTORISATION at A=0.28", "FACTORISATION at l=0.8"):
        sub = [m for m in meta if m["_fam"] == fam]
        vals = []
        print(f"\n  {fam}")
        print("  %6s %10s %10s %14s" % ("b", "De_c", "1+b^2/2", "product"))
        for m in sub:
            b_ = m["_b"]; dc = crossing(m["i"])
            if dc is None:
                print("  %6.2f %10s" % (b_, "none")); continue
            p = dc * (1 + b_ ** 2 / 2); vals.append(p)
            print("  %6.2f %10.4f %10.4f %14.4f" % (b_, dc, 1 + b_ ** 2 / 2, p))
        if len(vals) >= 2:
            v = np.array(vals)
            print("  -> constant %.4f, spread %.2f%%   %s" % (
                v.mean(), 100 * v.std() / v.mean(),
                "COLLAPSES" if v.std() / v.mean() < 0.02 else "DOES NOT COLLAPSE"))
    print(f"\n  max |oint U_stokes| {max(abs(r['stokes_res']) for r in res):.1e}")
