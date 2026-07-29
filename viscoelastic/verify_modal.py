"""Is the 3.4% gain physics, or is it discretisation?

The optimiser reports the winner beating the sinusoid by 1.034x. That number is small enough
that it has to be defended before it is believed -- a 3% effect can easily be 3% of numerical
error that happens to favour one stroke shape. Three independent attacks:

[A] RESOLUTION LADDER. Evaluate baseline and winner at the SAME resolution, take the ratio,
    and refine. Common-mode discretisation error cancels in the ratio; what matters is whether
    the ratio is *stable* as N, nsteps, ncycles and box size are refined. A gain that is real
    sits still. A gain that is numerics wanders.

[B] NULL CONTROLS ON THE WINNER. The winning stroke, run with no polymer, must give exactly
    zero (it is reciprocal -- one shape DOF -- so the scallop theorem applies to it just as
    much as to the sinusoid). Same stroke with symmetric beads must also give zero. If the
    winner "swims" in either control it is exploiting an artifact, not memory.

[C] IS IT WINNING BY REACHING FURTHER? The fair-fight rule is equal actuation effort
    <(dd/dt)^2>, fixed in advance. But a multi-harmonic stroke at equal mean-square velocity
    can still have a larger peak-to-peak excursion. That does not break the rule, but the
    reader deserves the number, so it is reported alongside.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-verify", image=image)

PI = 3.141592653589793
BRINK, LAM = 0.5, 3.0
REF_AMP = 0.35
EFFORT = 0.5 * REF_AMP ** 2

BASE_P = [1.0, 0.0, 0.0, 0.0, 0.0]                       # the plain sinusoid
BEST_P = [1.5036716778944965, -0.14335996665148124, -0.1443502946922665,
          0.048375167998124594, 0.038500269240537156]    # gen-6 winner, gain 1.0342


def harmonics(p):
    """p -> (amplitudes, phases) after the equal-effort rescale. Pure function, no solver."""
    p = np.asarray(p, dtype=float)
    a = np.array([p[0], p[1], p[3]]); ph = np.array([0.0, p[2], p[4]])
    k = np.array([1.0, 2.0, 3.0])
    e = 0.5 * float(np.sum((k * a) ** 2))
    if e < 1e-14:
        a = np.array([np.sqrt(2 * EFFORT), 0.0, 0.0]); e = EFFORT
    return a * np.sqrt(EFFORT / e), ph, k


@app.function(cpu=2.0, memory=8192, timeout=10800)
def evaluate(job: dict) -> dict:
    import time, traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        a, ph, k = harmonics(job["p"])

        def stroke(t):
            return (1.0 + float(np.sum(a * np.cos(k * t + ph))),
                    float(-np.sum(a * k * np.sin(k * t + ph))))

        kw = dict(N=job["N"], L=job["L"], brink=BRINK, lam=LAM, stroke=stroke)
        for opt in ("eta_p", "eps1", "eps2"):
            if opt in job:
                kw[opt] = job[opt]
        t0 = time.time()
        r = Solver2(**kw).run(ncycles=job["ncycles"], nsteps=job["nsteps"])
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   per_cycle=[float(x[0]) for x in r], wall_s=time.time() - t0)
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


@app.local_entrypoint()
def main():
    # [A] ladder: (N, L, nsteps, ncycles). dx = L/N is held at 2pi/96 for the first four.
    LADDER = [
        ("reference   ", 192, 4 * PI, 600, 3),
        ("2x timestep ", 192, 4 * PI, 1200, 3),
        ("4x timestep ", 192, 4 * PI, 2400, 3),
        ("finer grid  ", 288, 4 * PI, 600, 3),
        ("more cycles ", 192, 4 * PI, 600, 6),
        ("bigger box  ", 288, 6 * PI, 600, 3),
        ("refined all ", 288, 4 * PI, 1200, 5),
    ]
    jobs = []
    for tag, N, L, ns, nc in LADDER:
        for name, p in (("baseline", BASE_P), ("winner", BEST_P)):
            jobs.append(dict(tag=tag, which=name, p=p, N=N, L=L, nsteps=ns, ncycles=nc))
    # [B] null controls, winner stroke only
    ctl = dict(tag="control", p=BEST_P, N=192, L=4 * PI, nsteps=600, ncycles=3)
    jobs.append(dict(ctl, which="winner/no-polymer", eta_p=0.0))
    jobs.append(dict(ctl, which="winner/symmetric-beads", eps1=0.20, eps2=0.20))

    print(f"launching {len(jobs)} runs\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("verify_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} failed. first:\n{bad[0]['err']}\n")

    def find(tag, which):
        for r in res:
            if r.get("ok") and r["tag"] == tag and r["which"] == which:
                return r
        return None

    print("[A] RESOLUTION LADDER -- the ratio is the quantity that must hold still")
    print(f"    {'config':<13} {'N':>4} {'L/pi':>5} {'steps':>6} {'cyc':>4} "
          f"{'baseline dx':>13} {'winner dx':>13} {'gain':>8}")
    gains = []
    for tag, N, L, ns, nc in LADDER:
        b, w = find(tag, "baseline"), find(tag, "winner")
        if not (b and w):
            print(f"    {tag:<13} MISSING"); continue
        g = abs(w["dx"]) / abs(b["dx"]); gains.append(g)
        print(f"    {tag:<13} {N:>4} {L/PI:>5.0f} {ns:>6} {nc:>4} "
              f"{b['dx']:>13.5e} {w['dx']:>13.5e} {g:>8.4f}x")
    if gains:
        print(f"\n    gain across the ladder: min {min(gains):.4f}  max {max(gains):.4f}  "
              f"spread {100*(max(gains)-min(gains)):.2f} percentage points")
        print("    -> REAL" if min(gains) > 1.02 else "    -> NOT ESTABLISHED at the 2% bar")

    print("\n[B] NULL CONTROLS on the winning stroke (both must be round-off)")
    for which in ("winner/no-polymer", "winner/symmetric-beads"):
        r = find("control", which)
        if r:
            print(f"    {which:<26} dx = {r['dx']:+.3e}   "
                  + ("OK" if abs(r["dx"]) < 1e-12 else "<<< NOT ZERO -- ARTIFACT"))

    print("\n[C] HOW THE WINNER DIFFERS  (equal effort <(dd/dt)^2> = "
          f"{EFFORT:.5f} by construction)")
    t = np.linspace(0, 2 * PI, 4001)
    for name, p in (("baseline", BASE_P), ("winner", BEST_P)):
        a, ph, k = harmonics(p)
        d = 1.0 + (a[:, None] * np.cos(k[:, None] * t[None, :] + ph[:, None])).sum(0)
        dd = -(a[:, None] * k[:, None]
               * np.sin(k[:, None] * t[None, :] + ph[:, None])).sum(0)
        print(f"    {name:<9} a = [{a[0]:+.4f} {a[1]:+.4f} {a[2]:+.4f}]  "
              f"peak-to-peak d = {d.max()-d.min():.4f}  "
              f"max|d/dt| = {np.abs(dd).max():.4f}  "
              f"effort = {np.mean(dd**2):.5f}")

    smax = max(abs(r["stokes_res"]) for r in res if r.get("ok"))
    print(f"\n    max |oint U_stokes| over all runs = {smax:.1e}  (must be round-off)")
