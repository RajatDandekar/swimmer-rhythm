"""Disconnect-proof optimisation. The pattern to use for anything long (RL especially).

WHY THE OBVIOUS FIX ISN'T ENOUGH
--------------------------------
`modal run --detach` says "Don't stop the app if the local process dies or disconnects."
True -- but it keeps the remote APP alive, not the *driver*. An evolution strategy lives in
`@app.local_entrypoint()`, i.e. on the laptop: it proposes a generation, waits for 40 remote
evaluations, selects elites, proposes the next. Kill the laptop process and the workers just
idle with nobody to tell them what to evaluate. Three runs died that way here.

THE ACTUAL FIX -- three pieces, all needed
------------------------------------------
1. Move the ES loop itself into an `@app.function`, so the driver runs server-side and calls
   `evaluate.map()` remotely from inside. Nothing on the laptop is load-bearing.
2. Checkpoint to a `modal.Dict` rather than a local file -- a server-side loop cannot write
   to local disk, and a Dict is readable from anywhere, any time, including after the
   launching process is long gone.
3. Launch with `--detach` so the app outlives the client that started it.

    ./.venv/bin/modal run --detach optimize_detached.py       # fire and forget
    ./.venv/bin/modal run optimize_detached.py::status        # read progress any time
"""
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6")
         .add_local_python_source("solver2"))
app = modal.App("viscoelastic-optimise-detached", image=image)

# survives the run; readable from any client, any time
STATE = modal.Dict.from_name("viscoelastic-opt-state", create_if_missing=True)

PI = 3.141592653589793
N_GRID, L_BOX, BRINK, LAM = 192, 4 * PI, 0.5, 3.0
NSTEPS, NCYCLES = 600, 3
REF_AMP = 0.35
EFFORT = 0.5 * REF_AMP ** 2
POP, GEN = 40, 10


@app.function(cpu=2.0, memory=8192, timeout=7200)
def evaluate(p_list: list) -> dict:
    import traceback
    import numpy as np
    try:
        from solver2 import Solver2
        p = np.array(p_list, dtype=float)
        a = np.array([p[0], p[1], p[3]]); ph = np.array([0.0, p[2], p[4]])
        k = np.array([1.0, 2.0, 3.0])
        e = 0.5 * float(np.sum((k * a) ** 2))
        if e < 1e-14:
            a = np.array([np.sqrt(2 * EFFORT), 0.0, 0.0]); e = EFFORT
        a = a * np.sqrt(EFFORT / e)

        def stroke(t):
            return (1.0 + float(np.sum(a * np.cos(k * t + ph))),
                    float(-np.sum(a * k * np.sin(k * t + ph))))

        s = Solver2(N=N_GRID, L=L_BOX, brink=BRINK, lam=LAM, stroke=stroke)
        r = s.run(ncycles=NCYCLES, nsteps=NSTEPS)
        return dict(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                    amps=[float(x) for x in a], phases=[float(x) for x in ph])
    except Exception:
        return dict(ok=False, err=traceback.format_exc()[-400:])


@app.function(cpu=1.0, memory=2048, timeout=7200)
def optimise(tag: str = "bigamp") -> dict:
    """The ES driver, running SERVER-SIDE. Nothing local is required once this starts."""
    import numpy as np
    base = evaluate.remote([1.0, 0.0, 0.0, 0.0, 0.0])
    if not base.get("ok"):
        STATE[tag] = dict(status="baseline-failed", err=base.get("err"))
        return STATE[tag]
    target = abs(base["dx"])

    rng = np.random.default_rng(0)
    lo = np.array([-2, -2, -PI, -2, -PI]); hi = np.array([2, 2, PI, 2, PI])
    mean = np.array([1.0, 0.0, 0.0, 0.0, 0.0]); sigma = 0.5
    best_val, best_p = target, mean.copy()
    hist = []
    STATE[tag] = dict(status="running", baseline=base, history=[], best=None,
                      config=dict(ref_amp=REF_AMP, effort=EFFORT, lam=LAM,
                                  pop=POP, gen=GEN, N=N_GRID))

    for g in range(GEN):
        cand = [mean.copy()] + [np.clip(mean + sigma * rng.normal(size=5), lo, hi)
                                for _ in range(POP - 1)]
        res = list(evaluate.map([list(c) for c in cand]))
        vals = np.array([abs(r["dx"]) if r.get("ok") else -1.0 for r in res])
        order = np.argsort(vals)[::-1]
        mean = np.array([cand[i] for i in order[:max(2, POP // 4)]]).mean(axis=0)
        if vals[order[0]] > best_val:
            best_val, best_p = float(vals[order[0]]), cand[order[0]].copy()
        sigma = max(0.06, sigma * 0.82)
        hist.append(dict(gen=g, gen_best=float(vals[order[0]]), running_best=best_val,
                         gain=best_val / target, sigma=float(sigma),
                         nfail=int((vals < 0).sum())))
        STATE[tag] = dict(status="running", baseline=base, history=hist,
                          best=dict(dx=best_val, gain=best_val / target,
                                    p=[float(x) for x in best_p]),
                          config=STATE[tag]["config"])          # checkpoint every generation

    fin = evaluate.remote(list(best_p))
    out = dict(status="done", baseline=base, history=hist,
               best=dict(dx=best_val, gain=best_val / target,
                         p=[float(x) for x in best_p]),
               final=fin, config=STATE[tag]["config"])
    STATE[tag] = out
    return out


@app.local_entrypoint()
def main(tag: str = "bigamp"):
    """Fire and forget. Returns immediately; the loop continues server-side."""
    call = optimise.spawn(tag)
    print(f"spawned server-side optimisation, call id = {call.object_id}")
    print(f"read progress any time (even from a different machine):")
    print(f"  ./.venv/bin/modal run optimize_detached.py::status")


@app.local_entrypoint()
def status(tag: str = "bigamp"):
    try:
        s = STATE[tag]
    except KeyError:
        print("no state yet -- has it started?"); return
    print(f"status: {s['status']}   config: {s.get('config')}")
    b = s.get("baseline") or {}
    if b.get("dx") is not None:
        print(f"baseline sinusoid dx = {b['dx']:+.5e}  (stokes res {b['stokes_res']:.1e})")
    for r in s.get("history", []):
        print(f"  gen {r['gen']:2d}: gen-best {r['gen_best']:.4e}  running {r['running_best']:.4e}"
              f"  gain {r['gain']:.4f}x  sigma {r['sigma']:.3f}"
              + (f"  ({r['nfail']} failed)" if r["nfail"] else ""))
    bb = s.get("best")
    if bb:
        print(f"\nbest: dx = {bb['dx']:.5e}   gain = {bb['gain']:.4f}x")
    if s["status"] == "done":
        a = s["final"]["amps"]
        print(f"  harmonics: {a[0]:.4f}, {a[1]:.4f}, {a[2]:.4f}   "
              f"a2/a1 = {a[1]/a[0]:+.3f}  a3/a1 = {a[2]/a[0]:+.3f}")
        print("\n  => TIMING ASYMMETRY WINS" if bb["gain"] > 1.02
              else "\n  => sinusoid essentially optimal")
