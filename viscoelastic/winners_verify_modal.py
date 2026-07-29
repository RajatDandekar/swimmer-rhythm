"""Refine the constraint-surface winners. Server-side driver -- nothing local is load-bearing.

THIS RUN HAS NOW DIED TWICE, FOR TWO DIFFERENT REASONS
------------------------------------------------------
1. A container was killed (preemption hit this account 5x today) and one dead container
   cancels an entire Modal .map(). The try/except inside evaluate() cannot catch its own
   container being killed -- that is not a Python exception. Fixed with Modal-level
   retries= plus return_exceptions=True on the map.
2. The local Claude process restarted and took the run with it, because the .map() and the
   json.dump both live in @app.local_entrypoint() -- i.e. on this laptop. --detach keeps the
   remote app alive but there is nobody left to collect or write the results.

(2) is the same failure that killed three optimisation runs earlier. The fix was built then
(optimize_detached.py: driver inside an @app.function, checkpoint to a modal.Dict, launch with
--detach) and it ran 400 evaluations untouched -- but it was never applied to the sweeps. It is
applied here. Every long run in this project should use this shape.

    modal run --detach winners_verify_modal.py::main     # fire and forget
    modal run winners_verify_modal.py::status            # read results any time, from anywhere

WHAT IS UNDER TEST
------------------
[A] THE HEADLINE. best-at-De=0.3 beats the sinusoid by 1.4975x with excursion, path, period and
    effort ALL matched (the winner even uses 0.27% less effort). It is also the most
    numerically demanding stroke run so far: it sits exactly on the monotonicity guard
    (sum |b_k k| = 0.9000), so dtheta/dt dips to 0.10 and the swimmer crawls at a tenth of
    nominal phase speed through part of the stroke. Sharp features in time are what a fixed
    timestep resolves worst.

[B] THE SIGN REVERSAL, which matters more. The De=0.3 winner scores 0.9138x at De=3.0 -- WORSE
    than the plain sinusoid. That is the strong form of the control claim: the optimal low-De
    stroke is a liability at high De, not merely suboptimal. A ratio whose meaning lives in
    which side of 1.0 it lands on is the most fragile thing to assert from unrefined numbers.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-winners", image=image)
STATE = modal.Dict.from_name("viscoelastic-winners-state", create_if_missing=True)

PI = 3.141592653589793
BRINK, D0, AMP = 0.5, 1.0, 0.35
KS = np.array([1.0, 2.0, 3.0])

STROKES = {
    "sinusoid":     ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
    "best@De=0.3":  ([-0.526, -0.0854, 0.0678], [-1.733, 2.6653, 1.1516]),
    "best@De=1.5":  ([0.2232, -0.0138, -0.0616], [1.3895, 3.0182, -2.6772]),
    "best@De=3.0":  ([0.1346, 0.0106, 0.0196], [1.1525, 0.3273, -0.3072]),
}
LADDER = [("reference  ", 192, 4 * PI, 600, 8),
          ("4x timestep", 192, 4 * PI, 2400, 8),
          ("finer grid ", 288, 4 * PI, 600, 8),
          ("bigger box ", 288, 6 * PI, 600, 8),
          ("refined all", 288, 4 * PI, 1200, 10)]
DES = [0.3, 3.0]


@app.function(cpu=2.0, memory=8192, timeout=21600,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
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

        kw = dict(N=job["N"], L=job["L"], brink=BRINK, lam=job["lam"], stroke=stroke)
        if job.get("eta_p") is not None:
            kw["eta_p"] = job["eta_p"]
        r = Solver2(**kw).run(ncycles=job["ncycles"], nsteps=job["nsteps"])
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   drift=float(abs(r[-1][0] - r[-2][0]) / max(abs(r[-1][0]), 1e-300)))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


@app.function(cpu=1.0, memory=2048, timeout=21600)
def driver() -> dict:
    """Runs SERVER-SIDE. Survives the laptop restarting, disconnecting, or being closed."""
    jobs = []
    for De in DES:
        for tag, N, L, ns, nc in LADDER:
            for name, (b, ph) in STROKES.items():
                jobs.append(dict(name=name, tag=tag, b=b, ph=ph, lam=De,
                                 N=N, L=L, nsteps=ns, ncycles=nc))
    for name, (b, ph) in STROKES.items():          # scallop-theorem control on each winner
        if name != "sinusoid":
            jobs.append(dict(name=name, tag="no-polymer", b=b, ph=ph, lam=3.0,
                             N=192, L=4 * PI, nsteps=600, ncycles=4, eta_p=0.0))
    STATE["status"] = dict(state="running", n=len(jobs))
    raw = list(evaluate.map(jobs, return_exceptions=True))
    res = [r for r in raw if isinstance(r, dict)]
    dead = [str(r)[:200] for r in raw if not isinstance(r, dict)]
    STATE["results"] = res
    STATE["status"] = dict(state="done", n=len(jobs), ok=len(res), dead=dead)
    return dict(ok=len(res), dead=len(dead))


@app.local_entrypoint()
def main():
    call = driver.spawn()
    print(f"spawned server-side verification, call id = {call.object_id}")
    print("read results any time:  modal run winners_verify_modal.py::status")


@app.local_entrypoint()
def status():
    try:
        st = STATE["status"]
    except KeyError:
        print("no state yet -- has it started?"); return
    print(f"status: {st}")
    if st.get("state") != "done":
        print("still running; re-run this when it reports done"); return
    res = STATE["results"]
    json.dump(res, open("winners_verify_results.json", "w"), indent=1)
    ok = [r for r in res if r.get("ok")]
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} raised inside the solver:\n{bad[0]['err']}\n")

    def get(name, tag, De):
        for r in ok:
            if r["name"] == name and r["tag"] == tag and r["lam"] == De:
                return r
        return None

    for De in DES:
        print(f"{'='*74}\nDe = {De}   gain vs the plain sinusoid, refined")
        others = [n for n in STROKES if n != "sinusoid"]
        print(f"  {'config':<12}" + "".join(f"{n:>15}" for n in others))
        cols = {n: [] for n in others}
        for tag, *_ in LADDER:
            s = get("sinusoid", tag, De)
            if not s:
                print(f"  {tag:<12} sinusoid MISSING"); continue
            row = f"  {tag:<12}"
            for n in others:
                r = get(n, tag, De)
                if r:
                    g = abs(r["dx"]) / abs(s["dx"]); cols[n].append(g)
                    row += f"{g:>14.4f}x"
                else:
                    row += f"{'--':>15}"
            print(row)
        row = f"  {'spread (pp)':<12}"
        for n in others:
            row += (f"{100*(max(cols[n])-min(cols[n])):>14.2f} " if cols[n] else f"{'--':>15}")
        print(row)
        for n in others:
            if cols[n] and (min(cols[n]) - 1.0) * (max(cols[n]) - 1.0) < 0:
                print(f"  !! {n} straddles 1.0 across the ladder -- SIGN NOT ESTABLISHED")

    print(f"\n{'='*74}\nSCALLOP-THEOREM CONTROL (polymer off -- every winner must be exactly 0)")
    for name in STROKES:
        if name == "sinusoid":
            continue
        r = get(name, "no-polymer", 3.0)
        if r:
            print(f"  {name:<14} dx = {r['dx']:+.3e}   "
                  + ("OK" if abs(r["dx"]) < 1e-12 else "<<< NOT ZERO -- ARTIFACT"))
    if ok:
        print(f"\n  worst drift {100*max(r['drift'] for r in ok):.2f}%   "
              f"max |oint U_stokes| {max(abs(r['stokes_res']) for r in ok):.1e}")
    if st.get("dead"):
        print(f"\n  {len(st['dead'])} containers died even after retries: {st['dead'][0]}")
