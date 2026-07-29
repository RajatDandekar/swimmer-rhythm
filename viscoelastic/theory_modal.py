"""Does the collapse follow the SPECTRAL SECOND MOMENT? A shape-independence test.

THE HYPOTHESIS
--------------
The empirical collapse is De_c x (1 + b^2/2) = K for theta = t + b sin t. The factor 1 + b^2/2
is exactly <theta'^2>, and the exponent is the tell: for a phase-modulated signal
z(t) = exp(i theta(t)),

    zdot = i theta' exp(i theta)   =>   <|zdot|^2> / <|z|^2> = <theta'^2>   EXACTLY

i.e. <theta'^2> is the SPECTRAL SECOND MOMENT of the shape signal -- its mean-square
instantaneous frequency. The polymer is a first-order filter with time constant lambda. What it
responds to is not the stroke's nominal frequency but the mean-square frequency content of what
is actually driving it. If that reading is right, then for ANY modulation

    theta = t + sum_k b_k sin(k t + phi_k)   =>   <theta'^2> = 1 + (1/2) sum_k (k b_k)^2

(cross terms vanish for distinct k), and the reversal criterion De_c x <theta'^2> = K should
hold regardless of the SHAPE of the modulation -- only its second moment should matter.

THE TEST -- shape independence at fixed second moment
-----------------------------------------------------
Four rhythms that look nothing like each other, all with <theta'^2> = 1.125 exactly:

    b = [0.50, 0,    0    ]   modulate the 1st harmonic      (measured already: De_c = 0.808)
    b = [0,    0.25, 0    ]   modulate the 2nd harmonic
    b = [0,    0,    1/6  ]   modulate the 3rd harmonic
    b = [0.30, 0.20, 0    ]   modulate two at once

If the second moment is what matters, ALL FOUR must reverse at De_c = K/1.125 = 0.8061. If
instead the collapse was a curve-fit special to the sin-t family, the four will scatter.

This is a much stronger test than the earlier extrapolation: that varied a coefficient inside
one functional form, this varies the functional form itself while holding the predicted
invariant fixed.

Also tested:
  * SCALING across second moments using the 2nd-harmonic family alone.
  * PHASE INVARIANCE: <theta'^2> does not depend on phi, so De_c must not either.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-theory", image=image)
STATE = modal.Dict.from_name("viscoelastic-theory-state", create_if_missing=True)

PI = 3.141592653589793
KS = np.array([1.0, 2.0, 3.0])
D0, AMP = 1.0, 0.35
N_GRID, L_BOX, NSTEPS, NCYC = 192, 4 * PI, 600, 6
BRINK, EPS1, EPS2, ETA_P = 0.5, 0.14, 0.26, 1.0
K_LAW = 0.9069                      # from the 1st-harmonic family; used here as a PREDICTOR


def second_moment(b):
    """<theta'^2> = 1 + (1/2) sum (k b_k)^2  -- exact, phase-independent."""
    return 1.0 + 0.5 * float(np.sum((KS * np.asarray(b, dtype=float)) ** 2))


CASES = [
    # --- shape independence: four different modulations, all <theta'^2> = 1.125
    dict(b=[0.50, 0.0, 0.0], ph=[0, 0, 0], fam="SHAPE  1st harmonic"),
    dict(b=[0.0, 0.25, 0.0], ph=[0, 0, 0], fam="SHAPE  2nd harmonic"),
    dict(b=[0.0, 0.0, 1 / 6], ph=[0, 0, 0], fam="SHAPE  3rd harmonic"),
    dict(b=[0.30, 0.20, 0.0], ph=[0, 0, 0], fam="SHAPE  1st + 2nd mixed"),
    # --- scaling across second moments, 2nd-harmonic family only
    dict(b=[0.0, 0.15, 0.0], ph=[0, 0, 0], fam="SCALE  2nd harmonic"),
    dict(b=[0.0, 0.35, 0.0], ph=[0, 0, 0], fam="SCALE  2nd harmonic"),
    dict(b=[0.0, 0.44, 0.0], ph=[0, 0, 0], fam="SCALE  2nd harmonic"),
    # --- phase invariance: same b, shifted phase -> same second moment
    dict(b=[0.50, 0.0, 0.0], ph=[PI / 4, 0, 0], fam="PHASE  phi = pi/4"),
    dict(b=[0.50, 0.0, 0.0], ph=[PI / 2, 0, 0], fam="PHASE  phi = pi/2"),
]
DES = [0.50, 0.56, 0.62, 0.68, 0.74, 0.80, 0.86, 0.93, 1.00, 1.10]


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
def evaluate(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        b = np.array(job["b"]) * job["sign"]; ph = np.array(job["ph"])

        def stroke(t):
            th = t + float(np.sum(b * np.sin(KS * t + ph)))
            dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        r = Solver2(N=N_GRID, L=L_BOX, brink=BRINK, lam=job["lam"], eps1=EPS1, eps2=EPS2,
                    eta_p=ETA_P, stroke=stroke).run(ncycles=NCYC, nsteps=NSTEPS)
        out.update(ok=True, dx=float(r[-1][0]), stokes_res=float(r[-1][1]))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-400:])
    return out


@app.function(cpu=1.0, memory=2048, timeout=14400)
def driver() -> dict:
    jobs = []
    for i, c in enumerate(CASES):
        for De in DES:
            for sg in (+1, -1):
                jobs.append(dict(b=c["b"], ph=c["ph"], lam=De, sign=sg, cid=i))
    STATE["status"] = dict(state="running", n=len(jobs))
    raw = list(evaluate.map(jobs, return_exceptions=True))
    res = [r for r in raw if isinstance(r, dict)]
    STATE["results"] = res
    STATE["meta"] = [dict(i=i, fam=c["fam"], b=c["b"], ph=c["ph"],
                          m2=second_moment(c["b"])) for i, c in enumerate(CASES)]
    STATE["status"] = dict(state="done", n=len(jobs), ok=len(res), dead=len(raw) - len(res))
    return dict(ok=len(res))


@app.local_entrypoint()
def main():
    print("PREDICTIONS from De_c = K / <theta'^2>,  K = %.4f  (fixed before the runs)\n"
          % K_LAW)
    print("%-24s %-22s %10s %12s" % ("family", "b", "<theta'^2>", "De_c pred"))
    for c in CASES:
        m2 = second_moment(c["b"])
        print("%-24s %-22s %10.4f %12.4f"
              % (c["fam"], "[%.2f %.2f %.3f]" % tuple(c["b"]), m2, K_LAW / m2))
    call = driver.spawn()
    print(f"\nspawned, call id = {call.object_id}")
    print("read:  modal run theory_modal.py::status")


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
    json.dump(dict(results=res, meta=meta), open("theory_results.json", "w"), indent=1)

    def crossing(cid):
        g = {}
        for r in res:
            if r["cid"] == cid:
                g.setdefault(r["lam"], {})[r["sign"]] = r["dx"]
        des = sorted(d for d in g if 1 in g[d] and -1 in g[d])
        q = [abs(g[d][1]) / abs(g[d][-1]) for d in des]
        for a, b_, qa, qb in zip(des, des[1:], q, q[1:]):
            if (qa - 1) * (qb - 1) < 0:
                la, lb = np.log(a), np.log(b_)
                return float(np.exp(la + (lb - la) * (1 - qa) / (qb - qa)))
        return None

    rows = []
    for m in meta:
        dc = crossing(m["i"])
        rows.append(dict(m, dec=dc, pred=K_LAW / m["m2"],
                         prod=dc * m["m2"] if dc else None))

    print("\n%-24s %10s %11s %11s %8s %11s"
          % ("family", "<theta'^2>", "predicted", "measured", "error", "De_c x m2"))
    for r in rows:
        if r["dec"] is None:
            print("%-24s %10.4f %11.4f %11s" % (r["fam"], r["m2"], r["pred"], "no crossing"))
            continue
        print("%-24s %10.4f %11.4f %11.4f %7.1f%% %11.4f"
              % (r["fam"], r["m2"], r["pred"], r["dec"],
                 100 * (r["dec"] - r["pred"]) / r["pred"], r["prod"]))

    shape = [r for r in rows if r["fam"].startswith("SHAPE") and r["dec"]]
    if len(shape) >= 2:
        d = np.array([r["dec"] for r in shape])
        print("\nSHAPE INDEPENDENCE — four different modulations, same second moment 1.125")
        print("   De_c values: " + "  ".join("%.4f" % x for x in d))
        print("   spread %.2f%%   %s" % (100 * d.std() / d.mean(),
              "SECOND MOMENT IS WHAT MATTERS" if d.std() / d.mean() < 0.02
              else "SHAPE MATTERS TOO — hypothesis fails"))

    ph = [r for r in rows if r["fam"].startswith("PHASE") and r["dec"]]
    b0 = [r for r in rows if r["fam"] == "SHAPE  1st harmonic" and r["dec"]]
    if ph and b0:
        d = np.array([b0[0]["dec"]] + [r["dec"] for r in ph])
        print("\nPHASE INVARIANCE — same b, shifted phase (second moment unchanged)")
        print("   De_c values: " + "  ".join("%.4f" % x for x in d))
        print("   spread %.2f%%   %s" % (100 * d.std() / d.mean(),
              "INVARIANT as predicted" if d.std() / d.mean() < 0.02 else "NOT invariant"))

    allr = [r for r in rows if r["dec"]]
    if allr:
        p = np.array([r["prod"] for r in allr])
        print("\nALL %d CASES:  De_c x <theta'^2> = %.4f +/- %.2f%%"
              % (len(p), p.mean(), 100 * p.std() / p.mean()))
    print("   max |oint U_stokes| %.1e" % max(abs(r["stokes_res"]) for r in res))
