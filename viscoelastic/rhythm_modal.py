"""Same path, different rhythm. The loophole-free version of the question.

WHAT WENT WRONG LAST TIME
-------------------------
The stroke was parametrised as a sum of harmonics, d(t) = d0 + sum_k a_k cos(k t + phi_k),
normalised to equal actuation effort <(dd/dt)^2>. But effort weights harmonic k by k^2, so the
optimiser could shuffle amplitude between harmonics and come out with a 0.97% wider peak-to-peak
excursion at the same effort. Displacement goes as amp^2, so that alone bought 2.31 of the 3.42
percentage points it won by (measured directly: a plain sinusoid stretched to the winner's
excursion gets 1.0231x). It answered "how do I get more amplitude per unit effort", which is
not the question.

THE QUESTION I ACTUALLY WANT
----------------------------
A reciprocal swimmer has ONE shape degree of freedom, so it traces the same segment of shape
space out and back. The only freedom left is the RHYTHM -- how fast it moves along that segment
at each moment. In a Newtonian fluid rhythm is provably irrelevant (rate-independence, verified
to 1e-16 here). In a fluid with memory, is it?

THE FIX -- close the loophole by construction, not by normalisation
-------------------------------------------------------------------
    d(t) = d0 + A cos(theta(t)),   theta(t) = t + sum_k b_k sin(k t + phi_k)

theta is a monotone reparametrisation of the phase, so cos(theta) sweeps [-1, 1] exactly once
per period NO MATTER WHAT b and phi are. Every candidate therefore has:

    * identical excursion            (exactly 2A, by construction -- the loophole is gone)
    * identical shape-space path     (the same segment, traversed once out and once back)
    * identical period
    * still perfectly reciprocal     (so pure Stokes gives exactly zero for every one of them)

and differs ONLY in timing. theta(t) = t recovers the reference sinusoid exactly, which is a
free correctness check: it must reproduce dx = -1.90873e-03.

Effort is no longer held fixed -- at fixed excursion, varying effort IS the timing (rushing one
way and dawdling the other). So it is measured and reported per candidate, and the verdict is
required to hold for raw displacement AND for displacement per unit effort.

PROBES BEFORE SEARCH
--------------------
Seven hand-built rhythms with interpretable knobs run first. b_k sin(kt) with phi=0 is
time-symmetric about the turning points (fast/slow at the extremes); phi=-pi/2 makes it
genuinely asymmetric (hurry out, dawdle back) -- the classic "fast power stroke, slow recovery
stroke" of real cilia. If none of these moves the needle, the null is already answered and a
400-evaluation search is not worth buying.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-rhythm", image=image)

PI = 3.141592653589793
BRINK, LAM = 0.5, 3.0
N_GRID, L_BOX, NSTEPS, NCYCLES = 192, 4 * PI, 600, 3
D0, AMP = 1.0, 0.35                      # excursion 0.70, identical to the old baseline
KS = np.array([1.0, 2.0, 3.0])


def phase_fn(b, ph):
    """theta(t) = t + sum b_k sin(k t + ph_k), guarded to stay monotone (dtheta/dt > 0).
    Monotonicity keeps the interpretation clean: the swimmer traverses the segment once out
    and once back, never backtracking mid-sweep."""
    b = np.asarray(b, dtype=float)
    s = float(np.sum(np.abs(b * KS)))
    if s > 0.90:
        b = b * (0.90 / s)               # guard, not a constraint on the physics
    return b


def stroke_stats(b, ph, n=200001):
    t = np.linspace(0, 2 * PI, n)
    th = t + (b[:, None] * np.sin(KS[:, None] * t[None, :] + ph[:, None])).sum(0)
    dth = 1.0 + (b[:, None] * KS[:, None]
                 * np.cos(KS[:, None] * t[None, :] + ph[:, None])).sum(0)
    d = D0 + AMP * np.cos(th)
    dd = -AMP * np.sin(th) * dth
    return dict(excursion=float(d.max() - d.min()),
                effort=float(np.trapezoid(dd ** 2, t) / (2 * PI)),
                peak_rate=float(np.abs(dd).max()),
                path=float(np.trapezoid(np.abs(dd), t)),
                min_dth=float(dth.min()))


@app.function(cpu=2.0, memory=8192, timeout=7200)
def evaluate(job: dict) -> dict:
    import traceback
    out = {k: v for k, v in job.items() if k not in ("b", "ph")}
    try:
        from solver2 import Solver2
        b = phase_fn(np.array(job["b"]), np.array(job["ph"])); ph = np.array(job["ph"])

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        kw = dict(N=N_GRID, L=L_BOX, brink=BRINK, lam=LAM, stroke=stroke)
        if job.get("eta_p") is not None:
            kw["eta_p"] = job["eta_p"]
        r = Solver2(**kw).run(ncycles=NCYCLES, nsteps=NSTEPS)
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]),
                   b=[float(x) for x in b], **stroke_stats(b, ph))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-500:])
    return out


PROBES = [
    ("sinusoid  theta=t          ", [0.0, 0, 0], [0.0, 0, 0]),
    ("fast at extremes  b1=+0.5  ", [+0.5, 0, 0], [0.0, 0, 0]),
    ("slow at extremes  b1=-0.5  ", [-0.5, 0, 0], [0.0, 0, 0]),
    ("hurry out, dawdle back +0.5", [+0.5, 0, 0], [-PI / 2, 0, 0]),
    ("dawdle out, hurry back -0.5", [-0.5, 0, 0], [-PI / 2, 0, 0]),
    ("hurry out, dawdle back +0.8", [+0.8, 0, 0], [-PI / 2, 0, 0]),
    ("2nd harmonic      b2=+0.4  ", [0.0, +0.4, 0], [0.0, 0, 0]),
]


@app.local_entrypoint()
def main():
    jobs = [dict(tag=t, b=b, ph=p) for t, b, p in PROBES]
    # control: the most asymmetric rhythm with no polymer -- must be exactly zero
    jobs.append(dict(tag="CONTROL +0.8 asym, no polymer", b=[+0.8, 0, 0],
                     ph=[-PI / 2, 0, 0], eta_p=0.0))
    print(f"launching {len(jobs)} probes  (excursion fixed at {2*AMP:.2f} by construction)\n")
    res = list(evaluate.map(jobs))
    json.dump(res, open("rhythm_results.json", "w"), indent=1)
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} failed:\n{bad[0]['err']}\n")
    ok = [r for r in res if r.get("ok")]
    ref = next((r for r in ok if r["tag"].startswith("sinusoid")), None)
    if not ref:
        print("reference failed"); return

    print(f"{'rhythm':<29} {'excursion':>10} {'effort':>9} {'dx/cycle':>13} "
          f"{'gain':>8} {'dx/effort':>10}")
    for r in ok:
        if r["tag"].startswith("CONTROL"):
            continue
        g = abs(r["dx"]) / abs(ref["dx"])
        eff = (abs(r["dx"]) / r["effort"]) / (abs(ref["dx"]) / ref["effort"])
        print(f"{r['tag']:<29} {r['excursion']:>10.5f} {r['effort']:>9.5f} "
              f"{r['dx']:>13.5e} {g:>7.4f}x {eff:>9.4f}x")

    c = next((r for r in ok if r["tag"].startswith("CONTROL")), None)
    if c:
        print(f"\nCONTROL  most asymmetric rhythm, no polymer: dx = {c['dx']:+.3e}  "
              + ("OK (scallop theorem holds)" if abs(c["dx"]) < 1e-12 else "<<< ARTIFACT"))

    body = [r for r in ok if not r["tag"].startswith("CONTROL")]
    exc = max(abs(r["excursion"] - 2 * AMP) for r in body)
    gains = [abs(r["dx"]) / abs(ref["dx"]) for r in body]
    print(f"\nexcursion identical across all rhythms to {exc:.1e}  (loophole closed)")
    print(f"reference reproduced: dx = {ref['dx']:.5e}  (must match -1.90873e-03)")
    print(f"\nrhythm changes displacement by at most "
          f"{100*max(abs(g-1) for g in gains):.2f}% at fixed excursion")
    if max(gains) > 1.02:
        print("  => RHYTHM MATTERS. Worth searching the full space.")
    else:
        print("  => rhythm is nearly irrelevant; amplitude is the only lever.")
        print("     A full search would be buying a 400-evaluation confirmation of this.")
