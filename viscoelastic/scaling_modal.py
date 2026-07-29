"""Hunt for the dimensionless group that predicts WHERE the rhythm reversal happens.

THE OBSERVATION TO EXPLAIN
--------------------------
The optimal rhythm reverses at De_c ~ 0.81 for one particular swimmer. A critical value for one
parameter set is a curiosity. A critical value that collapses onto a single number across
swimmer geometry, stroke size, rhythm strength and confinement is a LAW -- and it is the kind
of thing that gets a name.

THE HYPOTHESIS
--------------
De = lambda * omega compares the fluid's memory against the stroke's NOMINAL frequency. But a
rhythm-modulated stroke does not move at its nominal frequency -- that is the entire point of
it. With theta(t) = t + b sin(t), the swimmer's shape-change rate peaks at roughly (1 + b) and
troughs at (1 - b). The fluid does not care about our bookkeeping frequency; it cares about how
fast it is actually being deformed.

So the natural guess is that the relevant group is not De but

    De* = De x (effective shape-change rate)

and that the reversal sits at a fixed De*, not a fixed De. If true, De_c should DROP as the
rhythm gets stronger, in a way that a single rescaling collapses.

Competing hypotheses this also distinguishes:
  * De_c is universal (~0.81 regardless) -> the crossover is set by the constitutive model alone
  * De_c tracks the swimmer's geometric asymmetry -> it is a property of the body, not the stroke
  * De_c tracks confinement (Brinkman length) -> it is set by the hydrodynamic screening

MEASUREMENT
-----------
For each parameter set, bracket the crossing of ratio(De) = 1 and locate it by interpolation in
log De. Everything is held converged: De <= 1.5 here, where cycle 3 is exact (verified in the
14-cycle study), so 6 cycles is comfortable.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-scaling", image=image)
STATE = modal.Dict.from_name("viscoelastic-scaling-state", create_if_missing=True)

PI = 3.141592653589793
KS = np.array([1.0, 2.0, 3.0])
D0 = 1.0
N_GRID, L_BOX, NSTEPS, NCYC = 192, 4 * PI, 600, 6

# baseline swimmer, then one-at-a-time variations
BASE = dict(amp=0.35, b1=0.5, eps1=0.14, eps2=0.26, brink=0.5, eta_p=1.0)
VARIATIONS = (
    [dict(BASE, b1=v, _fam="rhythm strength b", _val=v) for v in (0.25, 0.4, 0.5, 0.65, 0.8)]
    + [dict(BASE, amp=v, _fam="stroke amplitude A", _val=v) for v in (0.20, 0.28, 0.45)]
    + [dict(BASE, eps1=a, eps2=b, _fam="bead asymmetry", _val=round(b - a, 3))
       for a, b in ((0.17, 0.23), (0.11, 0.29))]
    + [dict(BASE, brink=v, _fam="confinement l", _val=v) for v in (0.35, 0.8)]
    + [dict(BASE, eta_p=v, _fam="polymer fraction", _val=v) for v in (0.5, 2.0)]
)
DES = [0.3, 0.45, 0.6, 0.7, 0.8, 0.9, 1.05, 1.3, 1.6]


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
def evaluate(job: dict) -> dict:
    import traceback
    out = {k: v for k, v in job.items()}
    try:
        from solver2 import Solver2
        b = np.array([job["b1"] * job["sign"], 0.0, 0.0]); ph = np.zeros(3)
        A = job["amp"]

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + A * np.cos(th), -A * np.sin(th) * dth)

        s = Solver2(N=N_GRID, L=L_BOX, brink=job["brink"], lam=job["lam"],
                    eps1=job["eps1"], eps2=job["eps2"], eta_p=job["eta_p"], stroke=stroke)
        r = s.run(ncycles=NCYC, nsteps=NSTEPS)
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   drift=float(abs(r[-1][0] - r[-2][0]) / max(abs(r[-1][0]), 1e-300)))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-400:])
    return out


@app.function(cpu=1.0, memory=2048, timeout=14400)
def driver() -> dict:
    jobs = []
    for i, v in enumerate(VARIATIONS):
        for De in DES:
            for sg in (+1, -1):
                jobs.append({k: x for k, x in v.items() if not k.startswith("_")}
                            | dict(lam=De, sign=sg, vid=i))
    STATE["status"] = dict(state="running", n=len(jobs))
    raw = list(evaluate.map(jobs, return_exceptions=True))
    res = [r for r in raw if isinstance(r, dict)]
    STATE["results"] = res
    STATE["meta"] = [{k: v for k, v in x.items() if k.startswith("_")} | {"i": i}
                     for i, x in enumerate(VARIATIONS)]
    STATE["status"] = dict(state="done", n=len(jobs), ok=len(res),
                           dead=len(raw) - len(res))
    return dict(ok=len(res))


@app.local_entrypoint()
def main():
    call = driver.spawn()
    print(f"spawned scaling study, call id = {call.object_id}")
    print("read:  modal run scaling_modal.py::status")


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
    json.dump(dict(results=res, meta=meta), open("scaling_results.json", "w"), indent=1)
    print(f"worst drift {100*max(r['drift'] for r in res):.2f}%   "
          f"max |oint U_stokes| {max(abs(r['stokes_res']) for r in res):.1e}\n")

    def crossing(vid):
        g = {}
        for r in res:
            if r["vid"] == vid:
                g.setdefault(r["lam"], {})[r["sign"]] = r["dx"]
        des = sorted(d for d in g if 1 in g[d] and -1 in g[d])
        q = [abs(g[d][1]) / abs(g[d][-1]) for d in des]
        for a, b, qa, qb in zip(des, des[1:], q, q[1:]):
            if (qa - 1) * (qb - 1) < 0:
                la, lb = np.log(a), np.log(b)
                return float(np.exp(la + (lb - la) * (1 - qa) / (qb - qa))), des, q
        return None, des, q

    print(f"{'family':<22} {'value':>8} {'De_c':>9}   ratio(De) across the sweep")
    rows = []
    for m in meta:
        dc, des, q = crossing(m["i"])
        fam, val = m.get("_fam", "?"), m.get("_val", 0)
        spark = " ".join(f"{x:.2f}" for x in q)
        rows.append(dict(fam=fam, val=val, dec=dc))
        print(f"{fam:<22} {val:>8} {('%.3f' % dc) if dc else '    --':>9}   {spark}")

    print("\nDOES De_c MOVE?  (if it is constant, the crossover is a property of the fluid model)")
    for fam in dict.fromkeys(r["fam"] for r in rows):
        sub = [r for r in rows if r["fam"] == fam and r["dec"]]
        if len(sub) < 2:
            continue
        lo, hi = min(r["dec"] for r in sub), max(r["dec"] for r in sub)
        print(f"  {fam:<22} De_c ranges {lo:.3f} to {hi:.3f}   "
              f"({100*(hi-lo)/((hi+lo)/2):.0f}% variation)")

    rb = [r for r in rows if r["fam"] == "rhythm strength b" and r["dec"]]
    if len(rb) >= 3:
        b = np.array([r["val"] for r in rb]); dc = np.array([r["dec"] for r in rb])
        print("\nTEST OF THE HYPOTHESIS  De* = De_c x (peak shape-change rate) = const?")
        print(f"  {'b':>6} {'De_c':>8} {'De_c(1+b)':>11} {'De_c/(1-b)':>12} "
              f"{'De_c(1+b^2/2)':>14}")
        for bb, d in zip(b, dc):
            print(f"  {bb:>6.2f} {d:>8.3f} {d*(1+bb):>11.3f} {d/(1-bb):>12.3f} "
                  f"{d*(1+bb**2/2):>14.3f}")
        for name, f in (("De_c", dc), ("De_c(1+b)", dc * (1 + b)),
                        ("De_c/(1-b)", dc / (1 - b)), ("De_c(1+b^2/2)", dc * (1 + b ** 2 / 2))):
            print(f"  spread of {name:<15} {100*np.std(f)/np.mean(f):.1f}%  "
                  f"(mean {np.mean(f):.3f})")
