"""Does screening the far field cure the box-size disease? Test, don't assert.

DIAGNOSIS SO FAR
----------------
The solver passes every exact test: scallop theorem 1e-17, symmetric-bead 1e-18,
translation invariance to 7 digits, bead-swap antisymmetry 3e-18, oint U_stokes 4.8e-17.
It is correct. But the answer will not converge in box size, and it wanders
NON-monotonically (box1 -> box2 -> box3 gives -28%, +19%).

That is expected for a 2-D periodic Stokes swimmer: the far field of a force-free swimmer
is a stresslet ~cos(2theta)/r^2. Summed over a square lattice of images the angular factor
makes contributions partly cancel, so the lattice sum converges slowly AND with sign
structure. Which is exactly why Richardson in 1/L^2 made things worse rather than better.

THE TEST
--------
Replace Stokes with Brinkman: (k^2 + 1/l^2) in the denominator instead of k^2, so the flow
decays as exp(-r/l) rather than algebraically. Images are then killed exponentially and the
box dependence must vanish once l << L.

Two reasons this is the right screening to try first:
  * it is a ONE-LINE change to the solver, and
  * it is physically legitimate, not a numerical hack -- Brinkman describes a confined film
    or a porous medium, and there is a directly relevant literature (Iqbal, Penington,
    Thomas & Koens, "A Taylor swimming sheet under a finite Brinkman layer",
    arXiv:2507.16125, 2025), which the prior-art sweep already turned up.

If box dependence collapses for finite l and returns as l grows, the diagnosis is confirmed
and we have a usable formulation. Wall-bounded flow screens the same way, so this also
de-risks the planned move to a channel.
"""
import json
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6")
         .add_local_python_source("solver2"))

app = modal.App("viscoelastic-brinkman", image=image)


@app.function(cpu=2.0, memory=8192, timeout=7200)
def run_point(p: dict) -> dict:
    import time, traceback
    out = dict(p)
    try:
        from solver2 import sweep_point
        t0 = time.time()
        r = sweep_point(**dict(p))
        out.update(dx=float(r["dx"]), stokes_residual=float(r["stokes_residual"]),
                   wall_s=time.time() - t0, ok=True)
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-600:])
    return out


BOXES = [(1, 96), (2, 192), (3, 288)]      # dx held fixed at 2*pi/96
BRINK = [0.5, 1.0, 2.0, None]              # screening length; None = pure Stokes
AMPS = [0.05, 0.10, 0.15]


@app.local_entrypoint()
def main():
    import numpy as np
    jobs = [dict(N=N, L=m * 2 * np.pi, lam=1.0, amp=a, brink=b, nsteps=800, ncycles=5)
            for m, N in BOXES for a in AMPS for b in BRINK]
    print(f"launching {len(jobs)} runs\n")
    res = [r for r in run_point.map(jobs) if r.get("ok")]
    json.dump(res, open("brinkman_results.json", "w"), indent=1)

    def get(m, a, b):
        for r in res:
            if (abs(r["L"] - m * 2 * np.pi) < 1e-9 and abs(r["amp"] - a) < 1e-12
                    and ((b is None and r["brink"] is None)
                         or (b is not None and r["brink"] is not None
                             and abs(r["brink"] - b) < 1e-12))):
                return r["dx"]

    print("BOX DEPENDENCE vs SCREENING LENGTH  (spread across the three boxes)")
    print(f"{'screening l':>12} {'amp':>6} " + "".join(f"{'L/2pi='+str(m):>13}" for m, _ in BOXES)
          + f"{'spread':>9}")
    for b in BRINK:
        for a in AMPS:
            v = [get(m, a, b) for m, _ in BOXES]
            if any(x is None for x in v):
                continue
            sp = (max(v) - min(v)) / abs(np.mean(v))
            lab = f"{b}" if b is not None else "none(Stokes)"
            print(f"{lab:>12} {a:6.3f} " + "".join(f"{x:13.4e}" for x in v) + f"{sp:8.1%}")
        print()

    print("AMPLITUDE EXPONENT at the largest box (theory: 2.000)")
    for b in BRINK:
        v = [get(3, a, b) for a in AMPS]
        if any(x is None for x in v):
            continue
        p = np.polyfit(np.log(AMPS), np.log(np.abs(v)), 1)[0]
        lab = f"l={b}" if b is not None else "pure Stokes"
        print(f"    {lab:>14}   exponent = {p:.4f}")
