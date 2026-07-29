"""THE EXPERIMENT: can a searched stroke beat the plain sinusoid?

Everything before this was de-risking. This is the scientific question, and the one the 0-D
toy could not answer honestly -- the toy only produced a non-trivial optimum after I
*inserted* a nonlinear coupling C(xi) = xi + c2 xi^2 by hand. The PDE has real hydrodynamic
nonlinearity, so this is the real test.

SETUP
-----
Stroke:  d(t) = d0 + sum_k a_k cos(k t + phi_k),  k = 1..3   (5 free params; phi_1 = 0 fixes
the time origin). Every such stroke is RECIPROCAL -- one shape DOF means it must retrace its
path -- so pure Stokes gives exactly zero for all of them and any motion is memory.

Fair fight: every candidate is rescaled to the SAME actuation effort <(dd/dt)^2>, so a
stroke cannot win by simply moving more.

DESIGN NOTES (learned the hard way)
-----------------------------------
* Evolution-strategy generations are inherently SEQUENTIAL -- only the population inside a
  generation parallelises. Wall-clock = n_generations x per-eval, NOT total/n_workers. So use
  a WIDE population and FEW generations: 40 x 10 costs the same 400 evals as 16 x 25 but
  runs in ~40% of the wall time.
* Results are checkpointed to JSON after EVERY generation. The previous attempt was killed
  before its single end-of-run write and lost all 400 evaluations.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6")
         .add_local_python_source("solver2"))
app = modal.App("viscoelastic-optimise", image=image)

PI = 3.141592653589793
N_GRID, L_BOX, BRINK, LAM = 192, 4 * PI, 0.5, 3.0     # De=3: the measured PDE peak
NSTEPS, NCYCLES = 600, 3                              # converged by cycle 3 (0.0% drift)
REF_AMP = 0.35                                        # finite amplitude: where the
EFFORT = 0.5 * REF_AMP ** 2                           # amp^4 term competes with amp^2
POP, GEN = 40, 10                                     # wide + shallow => low wall-clock


@app.function(cpu=2.0, memory=8192, timeout=7200)
def evaluate(p_list: list) -> dict:
    """One candidate stroke -> net displacement per cycle. Self-contained: no module-level
    helpers referenced, so nothing depends on how the image was assembled."""
    import traceback
    import numpy as np
    try:
        from solver2 import Solver2
        p = np.array(p_list, dtype=float)
        a = np.array([p[0], p[1], p[3]]); ph = np.array([0.0, p[2], p[4]])
        k = np.array([1.0, 2.0, 3.0])
        e = 0.5 * float(np.sum((k * a) ** 2))          # <(dd/dt)^2> for this stroke
        if e < 1e-14:
            a = np.array([np.sqrt(2 * EFFORT), 0.0, 0.0]); e = EFFORT
        a = a * np.sqrt(EFFORT / e)                    # rescale onto the effort budget

        def stroke(t):
            return (1.0 + float(np.sum(a * np.cos(k * t + ph))),
                    float(-np.sum(a * k * np.sin(k * t + ph))))

        s = Solver2(N=N_GRID, L=L_BOX, brink=BRINK, lam=LAM, stroke=stroke)
        r = s.run(ncycles=NCYCLES, nsteps=NSTEPS)
        return dict(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                    amps=[float(x) for x in a], phases=[float(x) for x in ph],
                    p=[float(x) for x in p])
    except Exception:
        return dict(ok=False, err=traceback.format_exc()[-500:], p=list(p_list))


@app.local_entrypoint()
def main():
    ckpt = "optimise_results_bigamp.json"
    state = dict(config=dict(N=N_GRID, L=L_BOX, brink=BRINK, lam=LAM, nsteps=NSTEPS,
                             ncycles=NCYCLES, effort=EFFORT, pop=POP, gen=GEN),
                 baseline=None, history=[], best=None)

    base = evaluate.remote([1.0, 0.0, 0.0, 0.0, 0.0])
    if not base.get("ok"):
        print("BASELINE FAILED:\n" + base.get("err", "")); return
    target = abs(base["dx"])
    state["baseline"] = base
    print(f"BASELINE pure sinusoid: dx = {base['dx']:+.5e}  "
          f"(stokes residual {base['stokes_res']:.1e})")
    print(f"effort budget <(dd/dt)^2> = {EFFORT:.5f}; De = {LAM}\n")

    rng = np.random.default_rng(0)
    lo = np.array([-2, -2, -PI, -2, -PI]); hi = np.array([2, 2, PI, 2, PI])
    mean = np.array([1.0, 0.0, 0.0, 0.0, 0.0]); sigma = 0.5
    best_val, best_p = target, mean.copy()

    for g in range(GEN):
        cand = [mean.copy()] + [np.clip(mean + sigma * rng.normal(size=5), lo, hi)
                                for _ in range(POP - 1)]
        res = list(evaluate.map([list(c) for c in cand]))
        vals = np.array([abs(r["dx"]) if r.get("ok") else -1.0 for r in res])
        nfail = int((vals < 0).sum())
        order = np.argsort(vals)[::-1]
        elite = np.array([cand[i] for i in order[:max(2, POP // 4)]])
        mean = elite.mean(axis=0)
        if vals[order[0]] > best_val:
            best_val, best_p = float(vals[order[0]]), cand[order[0]].copy()
        sigma = max(0.06, sigma * 0.82)

        state["history"].append(dict(gen=g, gen_best=float(vals[order[0]]),
                                    running_best=best_val, gain=best_val / target,
                                    sigma=float(sigma), nfail=nfail))
        state["best"] = dict(dx=best_val, gain=best_val / target,
                             p=[float(x) for x in best_p])
        json.dump(state, open(ckpt, "w"), indent=1)     # checkpoint EVERY generation
        print(f"  gen {g:2d}: gen-best {vals[order[0]]:.4e}  running {best_val:.4e}  "
              f"gain {best_val/target:.4f}x  sigma {sigma:.3f}"
              + (f"  ({nfail} failed)" if nfail else ""))

    fin = evaluate.remote(list(best_p))
    a, ph = fin["amps"], fin["phases"]
    print(f"\nBEST  dx = {best_val:.5e}   gain over sinusoid = {best_val/target:.4f}x")
    print(f"  harmonic amplitudes: {a[0]:.4f}, {a[1]:.4f}, {a[2]:.4f}")
    print(f"  a2/a1 = {a[1]/a[0]:+.3f}   a3/a1 = {a[2]/a[0]:+.3f}")
    print(f"  relative phases: {ph[1] % (2*PI):.3f}, {ph[2] % (2*PI):.3f} rad")
    state["final"] = fin
    json.dump(state, open(ckpt, "w"), indent=1)

    if best_val / target > 1.02:
        print("\n  => TIMING ASYMMETRY BEATS THE SINUSOID in the real PDE.")
        print("     There is a genuine search problem; the optimisation framing holds.")
    else:
        print("\n  => Sinusoid essentially optimal. The toy's hand-inserted nonlinearity")
        print("     was not physical -- rethink before any RL/world-model work.")
