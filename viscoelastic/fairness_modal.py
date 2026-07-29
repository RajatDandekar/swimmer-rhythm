"""Did the winner beat the sinusoid, or did it just find a bigger stroke?

THE PROBLEM
-----------
The pre-registered fair-fight rule was equal actuation effort <(dd/dt)^2>. Under that rule the
winner beats the sinusoid by 1.0342x. But the verification run exposed something: at equal
effort the winner's peak-to-peak excursion is 0.7068 vs the sinusoid's 0.7000 -- 0.97% larger.
Displacement scales as amp^1.9944 (measured), so amplitude ALONE predicts 1.0195x. That would
leave only ~1.45% for timing, below the 2% bar, and would make the result a reparametrisation
win ("multi-harmonic strokes buy more amplitude per unit effort") rather than a physics claim
("asymmetric timing exploits fluid memory").

Both readings fit the equal-effort number. One experiment separates them.

THE TEST
--------
Rescale the winner (all a_k by a common factor s -- shape and phasing untouched) so that it
matches the sinusoid on each of four different fairness metrics in turn:

    effort      <(dd/dt)^2>       s^2   the original rule
    excursion   max d - min d     s     kills the amplitude explanation outright
    peak rate   max|dd/dt|        s     equal maximum actuation demand
    path        oint |dd/dt| dt   s     equal total travel in shape space

The metric choice is a judgement call and each is defensible, which is exactly why the winner
should be made to face all four. Winning under one metric is an artifact of my taste. Winning
under all four is a property of the swimmer.

Plus a direct control: a PURE SINUSOID stretched to the winner's excursion. That measures the
amplitude-only gain empirically instead of inferring it from a fitted exponent.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-fairness", image=image)

PI = 3.141592653589793
BRINK, LAM = 0.5, 3.0
N_GRID, L_BOX, NSTEPS, NCYCLES = 192, 4 * PI, 600, 3
K = np.array([1.0, 2.0, 3.0])

# post-rescale harmonics, straight from the verification run
BASE_A = np.array([0.35000000, 0.0, 0.0]);            BASE_PH = np.array([0.0, 0.0, 0.0])
WIN_A = np.array([0.34230000, -0.03260000, 0.01100000])
WIN_PH = np.array([0.0, -0.1443502946922665, 0.038500269240537156])


def metrics(a, ph, n=200001):
    """All four fairness metrics for one stroke. Trapezoid on a dense grid; the integrand is
    smooth and periodic so this is spectrally accurate and the cost is irrelevant."""
    t = np.linspace(0, 2 * PI, n)
    d = (a[:, None] * np.cos(K[:, None] * t[None, :] + ph[:, None])).sum(0)
    dd = -(a[:, None] * K[:, None] * np.sin(K[:, None] * t[None, :] + ph[:, None])).sum(0)
    return dict(effort=float(np.trapezoid(dd ** 2, t) / (2 * PI)),
                excursion=float(d.max() - d.min()),
                peak_rate=float(np.abs(dd).max()),
                path=float(np.trapezoid(np.abs(dd), t)))


# how each metric scales when every a_k is multiplied by s
POWER = dict(effort=2.0, excursion=1.0, peak_rate=1.0, path=1.0)


@app.function(cpu=2.0, memory=8192, timeout=7200)
def evaluate(job: dict) -> dict:
    import traceback
    out = {k: v for k, v in job.items() if k not in ("a", "ph")}
    try:
        from solver2 import Solver2
        a = np.array(job["a"]); ph = np.array(job["ph"])

        def stroke(t):
            return (1.0 + float(np.sum(a * np.cos(K * t + ph))),
                    float(-np.sum(a * K * np.sin(K * t + ph))))

        r = Solver2(N=N_GRID, L=L_BOX, brink=BRINK, lam=LAM,
                    stroke=stroke).run(ncycles=NCYCLES, nsteps=NSTEPS)
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   a=[float(x) for x in a])
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


@app.local_entrypoint()
def main():
    mb, mw = metrics(BASE_A, BASE_PH), metrics(WIN_A, WIN_PH)
    print("metric values at the equal-effort normalisation")
    print(f"    {'metric':<11} {'sinusoid':>12} {'winner':>12} {'ratio w/s':>11}")
    for k in POWER:
        print(f"    {k:<11} {mb[k]:>12.6f} {mw[k]:>12.6f} {mw[k]/mb[k]:>11.5f}")

    jobs = [dict(tag="sinusoid (reference)", a=list(BASE_A), ph=list(BASE_PH))]
    for k, p in POWER.items():
        s = (mb[k] / mw[k]) ** (1.0 / p)          # rescale winner to match sinusoid on metric k
        jobs.append(dict(tag=f"winner @ equal {k}", metric=k, s=float(s),
                         a=list(WIN_A * s), ph=list(WIN_PH)))
    # empirical amplitude-only control: pure sinusoid stretched to the winner's excursion
    s_amp = mw["excursion"] / mb["excursion"]
    jobs.append(dict(tag="sinusoid @ winner's excursion", metric="control", s=float(s_amp),
                     a=list(BASE_A * s_amp), ph=list(BASE_PH)))

    print(f"\nlaunching {len(jobs)} runs\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("fairness_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} failed:\n{bad[0]['err']}\n")
    ok = {r["tag"]: r for r in res if r.get("ok")}

    ref = ok.get("sinusoid (reference)")
    if not ref:
        print("reference run failed -- nothing to compare against"); return
    print(f"{'stroke':<32} {'scale s':>9} {'dx/cycle':>14} {'gain':>9}")
    print(f"{'sinusoid (reference)':<32} {1.0:>9.5f} {ref['dx']:>14.5e} {1.0:>9.4f}x")
    gains = {}
    for j in jobs[1:]:
        r = ok.get(j["tag"])
        if not r:
            print(f"{j['tag']:<32} FAILED"); continue
        g = abs(r["dx"]) / abs(ref["dx"]); gains[j["metric"]] = g
        print(f"{j['tag']:<32} {j['s']:>9.5f} {r['dx']:>14.5e} {g:>9.4f}x")

    amp_only = gains.get("control")
    print(f"\nDECOMPOSITION at the original equal-effort normalisation")
    print(f"    total measured gain                      {gains.get('effort', float('nan')):.4f}x")
    if amp_only:
        print(f"    from larger excursion alone (measured)   {amp_only:.4f}x")
        print(f"    residual attributable to TIMING          "
              f"{gains.get('effort', float('nan'))/amp_only:.4f}x")

    core = {k: v for k, v in gains.items() if k != "control"}
    if core:
        print(f"\nVERDICT -- winner must beat 1.0 under every metric, not just the one I picked")
        for k, v in core.items():
            print(f"    equal {k:<10} {v:.4f}x   " + ("wins" if v > 1.0 else "LOSES"))
        lo = min(core.values())
        print(f"\n    worst case {lo:.4f}x")
        if lo > 1.02:
            print("    => TIMING WINS under every fairness metric. Robust.")
        elif lo > 1.0:
            print("    => winner survives everywhere but the margin is metric-dependent;")
            print("       the honest claim is the WORST case, not the best.")
        else:
            print("    => the win does NOT survive renormalisation. It was amplitude, not timing.")
