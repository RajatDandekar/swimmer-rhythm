"""Parallel convergence study on Modal.

The three error sources found in the spike -- timestep, periodic-image (box size) and
finite-amplitude nonlinearity -- are ENTANGLED, and each is amplitude-dependent. Resolving
them means a 3-D grid where each point costs seconds to ~10 minutes. Serially that is a
couple of hours of babysitting; in parallel it is one wall-clock coffee break.

Grid: amp x nsteps x box, with N scaled to hold the grid spacing dx fixed so that box size
is varied at constant resolution (otherwise the two effects are confounded).

    python -m modal run sweep_modal.py
"""
import json
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6")
         .add_local_python_source("solver2"))

app = modal.App("viscoelastic-convergence", image=image)


@app.function(cpu=2.0, memory=8192, timeout=7200)
def run_point(p: dict) -> dict:
    """One grid point. Never raises: a single bad point must not cancel the whole map.
    Echoes its own parameters back and casts numpy scalars so the result is JSON-safe."""
    import time, traceback
    out = dict(p)                       # echo params (sweep_point pops some of them)
    try:
        from solver2 import sweep_point
        t0 = time.time()
        r = sweep_point(**dict(p))
        out.update(dx=float(r["dx"]),
                   stokes_residual=float(r["stokes_residual"]),
                   history=[float(x) for x in r["history"]],
                   wall_s=time.time() - t0, ok=True)
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-800:])
    return out


# grid spacing dx = L/N is held FIXED at 2*pi/96 across all three boxes
BOXES = [(1, 96), (2, 192), (3, 288)]
AMPS = [0.05, 0.075, 0.10, 0.15]
NSTEPS = [400, 800, 1600]


@app.local_entrypoint()
def main():
    import numpy as np
    jobs = []
    for mult, N in BOXES:
        for amp in AMPS:
            for ns in NSTEPS:
                jobs.append(dict(N=N, L=mult * 2 * np.pi, lam=1.0, amp=amp,
                                 nsteps=ns, ncycles=6))
    print(f"launching {len(jobs)} runs in parallel "
          f"(largest: N=288, nsteps=1600 -- ~10 min)\n")

    results = list(run_point.map(jobs))
    with open("sweep_results.json", "w") as f:
        json.dump(results, f, indent=1)

    bad = [r for r in results if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)}/{len(results)} runs FAILED. first traceback:\n{bad[0]['err']}\n")
    results = [r for r in results if r.get("ok")]
    tot = sum(r["wall_s"] for r in results)
    print(f"done. {len(results)} runs ok, {tot/60:.0f} CPU-minutes total\n")

    # --- Richardson-extrapolate in dt (RK2 -> error ~ dt^2) at each (box, amp)
    def get(mult, amp, ns):
        L = mult * 2 * np.pi
        for r in results:
            if abs(r["L"] - L) < 1e-9 and abs(r["amp"] - amp) < 1e-12 and r["nsteps"] == ns:
                return r["dx"]
        return None

    print("dt-EXTRAPOLATED dx (from nsteps 800 & 1600), and the amplitude exponent")
    print(f"{'box L/2pi':>10} " + "".join(f"{a:>13}" for a in AMPS) + f"{'exponent':>11}")
    ext = {}
    for mult, _N in BOXES:
        row, vals = [], []
        for amp in AMPS:
            v8, v16 = get(mult, amp, 800), get(mult, amp, 1600)
            e = (4 * v16 - v8) / 3.0
            ext[(mult, amp)] = e
            vals.append(e); row.append(f"{e:13.5e}")
        p = np.polyfit(np.log(AMPS), np.log(np.abs(vals)), 1)[0]
        print(f"{mult:>10} " + "".join(row) + f"{p:11.4f}")

    print("\nthen Richardson in the box too (image error ~ 1/L^2), using L/2pi = 2 & 3:")
    fin = []
    for amp in AMPS:
        e2, e3 = ext[(2, amp)], ext[(3, amp)]
        # error ~ C/L^2 : eliminate C between the two boxes
        v = (9 * e3 - 4 * e2) / 5.0
        fin.append(v)
        print(f"    amp={amp:5.3f}  dx = {v:12.5e}   dx/amp^2 = {v/amp**2:11.5e}")
    p = np.polyfit(np.log(AMPS), np.log(np.abs(fin)), 1)[0]
    sp = max(v / a ** 2 for v, a in zip(fin, AMPS)) / min(v / a ** 2 for v, a in zip(fin, AMPS)) - 1
    print(f"\n    FULLY EXTRAPOLATED exponent = {p:.4f}   (theory: 2.0000)")
    print(f"    dx/amp^2 spread = {sp*100:.1f}%   (raw spike gave 6.7% at one box/dt)")
    print(f"\n    max |oint U_stokes| across all runs = "
          f"{max(abs(r['stokes_residual']) for r in results):.1e}  (must be round-off)")
