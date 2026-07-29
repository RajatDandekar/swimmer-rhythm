"""Now that the formulation is validated: re-run the controls, then the actual physics.

Brinkman screening (l = 0.5, i.e. half the swimmer length) fixed the box-convergence
disease and recovered the exact amplitude exponent 1.9944 vs the theoretical 2.000. Before
trusting any physics from it, the exact tests must be re-passed under the NEW operator --
screening changes the Green's function, so the scallop theorem is not automatically safe.

Then the two physics questions the toy model could not answer:
  * where in Deborah number is the sweet spot?  (0-D toy said De = 1 exactly)
  * how does displacement scale with the geometric asymmetry?
"""
import json
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-physics", image=image)

BRINK = 0.5
BOX = dict(N=192, L=2 * 3.141592653589793 * 2)     # L = 4pi, dx = 2pi/96


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


@app.local_entrypoint()
def main():
    import numpy as np
    base = dict(**BOX, brink=BRINK, nsteps=800, ncycles=5)

    controls = [
        dict(**base, lam=1.0, amp=0.10, eta_p=0.0, _tag="no polymer -> scallop theorem"),
        dict(**base, lam=1.0, amp=0.10, eps1=0.20, eps2=0.20, _tag="symmetric beads"),
        dict(**base, lam=1.0, amp=0.10, _tag="asymmetric + polymer (should swim)"),
    ]
    des = [0.2, 0.35, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
    asyms = [(0.20, 0.20), (0.18, 0.22), (0.16, 0.24), (0.14, 0.26), (0.12, 0.28)]

    jobs = [{k: v for k, v in c.items() if k != "_tag"} for c in controls]
    jobs += [dict(**base, lam=D, amp=0.10) for D in des]
    jobs += [dict(**base, lam=1.0, amp=0.10, eps1=a, eps2=b) for a, b in asyms]
    print(f"launching {len(jobs)} runs (Brinkman l={BRINK}, L=4pi, N=192)\n")

    res = list(run_point.map(jobs))
    json.dump(res, open("physics_results.json", "w"), indent=1)
    ok = [r for r in res if r.get("ok")]
    if len(ok) < len(res):
        print(f"!! {len(res)-len(ok)} failed\n")

    print("[1] CONTROLS -- must still hold under the screened operator")
    for c, r in zip(controls, ok[:3]):
        print(f"    {c['_tag']:<38} dx = {r['dx']:+.4e}")

    print("\n[2] DEBORAH SWEEP  (0-D toy predicted the peak at De = 1)")
    dd = ok[3:3 + len(des)]
    print(f"    {'De':>6} {'dx/cycle':>14}")
    peak = max(dd, key=lambda r: abs(r["dx"]))
    for D, r in zip(des, dd):
        bar = "#" * int(56 * abs(r["dx"]) / max(abs(x["dx"]) for x in dd))
        print(f"    {D:6.2f} {r['dx']:14.4e}  {bar}")
    print(f"    -> peak at De = {peak['lam']}")

    print("\n[3] ASYMMETRY SWEEP  (symmetric must be exactly zero)")
    aa = ok[3 + len(des):]
    print(f"    {'eps1':>6} {'eps2':>6} {'delta':>7} {'dx/cycle':>14}")
    for (e1, e2), r in zip(asyms, aa):
        print(f"    {e1:6.2f} {e2:6.2f} {e2-e1:7.2f} {r['dx']:14.4e}")
    nz = [(e2 - e1, r["dx"]) for (e1, e2), r in zip(asyms, aa) if e2 - e1 > 1e-9]
    p = np.polyfit(np.log([d for d, _ in nz]), np.log([abs(v) for _, v in nz]), 1)[0]
    print(f"    scaling with asymmetry: exponent {p:.3f}")
    print(f"\n    max |oint U_stokes| = {max(abs(r['stokes_residual']) for r in ok):.1e}")
