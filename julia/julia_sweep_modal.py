"""Run the Julia parameter sweeps on Modal — massively parallel, one container per point.

Every sweep point is an independent run of the from-scratch Julia solver (ViscoelasticSwimmer.jl),
so we fan all of them out with .map(). Produces the three JSON files the local plot / symbolic-
regression scripts read:
    julia_dense.json     the reversal sweep (18 De x 2 rhythms)
    julia_collapse.json  De_c(b1) for the De_c*<θ̇²> = K collapse
    julia_amp.json       |Δx| vs amplitude for the exponent

    modal run julia_sweep_modal.py
"""
import json
import math
import statistics
from pathlib import Path

import modal

HERE = Path(__file__).parent

image = (
    modal.Image.from_registry("julia:1.11", add_python="3.11")
    .run_commands(
        "julia -e 'using Pkg; Pkg.add(\"FFTW\"); using FFTW; println(\"FFTW precompiled\")'"
    )
    .add_local_file(str(HERE / "ViscoelasticSwimmer.jl"), "/root/ViscoelasticSwimmer.jl", copy=True)
    .add_local_file(str(HERE / "sweep_one.jl"), "/root/sweep_one.jl", copy=True)
)
app = modal.App("julia-swimmer-sweep", image=image)


@app.function(cpu=1.0, memory=4096, timeout=1800)
def sweep_point(job: dict) -> dict:
    import subprocess
    out = dict(job)
    try:
        args = [str(job[k]) for k in ("De", "b1", "amp", "N", "nsteps", "ncyc")]
        p = subprocess.run(["julia", "/root/sweep_one.jl", *args],
                           capture_output=True, text=True, timeout=1500)
        line = p.stdout.strip().split("\n")[-1]
        dx, res = line.split()
        out.update(dx=float(dx), stokes_res=float(res), ok=True)
    except Exception as e:
        out.update(ok=False, err=f"{e} | stderr={p.stderr[-400:] if 'p' in dir() else ''}")
    return out


def build_jobs():
    jobs = []
    DES = [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95,
           1.00, 1.10, 1.25, 1.45, 1.70, 2.00, 2.35, 2.70, 3.00]
    for De in DES:
        for b1 in (-0.5, 0.5):
            jobs.append(dict(kind="dense", De=De, b1=b1, amp=0.35, N=192, nsteps=600, ncyc=6))
    for base in (0.30, 0.40, 0.50, 0.60):
        for De in (0.70, 0.80, 0.90, 1.00):
            for sgn in (-1.0, 1.0):
                jobs.append(dict(kind="collapse", De=De, b1=sgn * base, base=base,
                                 amp=0.35, N=192, nsteps=400, ncyc=6))
    for amp in (0.06, 0.08, 0.11, 0.14, 0.18, 0.23, 0.30):
        jobs.append(dict(kind="amp", De=1.0, b1=0.0, amp=amp, N=192, nsteps=500, ncyc=6))
    return jobs


@app.local_entrypoint()
def main():
    jobs = build_jobs()
    print(f"dispatching {len(jobs)} Julia sweep points to Modal ...")
    res = list(sweep_point.map(jobs))
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print(f"!! {len(bad)} failed. first error:\n{bad[0].get('err')}")
    ok = [r for r in res if r.get("ok")]
    print(f"{len(ok)}/{len(jobs)} succeeded")

    # ---- dense -> julia_dense.json ----
    dense = [r for r in ok if r["kind"] == "dense"]
    json.dump({"params": {"N": 192, "L": 4 * math.pi, "brink": 0.5, "amp": 0.35,
                          "nsteps": 600, "ncyc": 6},
               "results": [{"lam": r["De"], "b1": r["b1"], "dx": r["dx"]} for r in dense]},
              open(HERE / "julia_dense.json", "w"), indent=1)

    # sanity vs NumPy at De=0.5
    def dget(De, b1):
        return next(r["dx"] for r in dense if abs(r["De"] - De) < 1e-9 and abs(r["b1"] - b1) < 1e-9)
    print(f"  check De=0.5 open: Julia/Modal {dget(0.5,-0.5):.6e}  (NumPy -9.4494e-04)")

    # ---- collapse -> julia_collapse.json ----
    col = [r for r in ok if r["kind"] == "collapse"]
    rows = []
    for base in (0.30, 0.40, 0.50, 0.60):
        des = sorted({r["De"] for r in col if abs(r["base"] - base) < 1e-9})
        def dx(De, sgn):
            return abs(next(r["dx"] for r in col if abs(r["base"] - base) < 1e-9
                            and abs(r["De"] - De) < 1e-9 and (r["b1"] > 0) == (sgn > 0)))
        ratio = [dx(De, 1) / dx(De, -1) for De in des]
        Dec = None
        for i in range(1, len(des)):
            if (ratio[i-1] - 1) * (ratio[i] - 1) <= 0:
                Dec = des[i-1] + (1 - ratio[i-1]) * (des[i] - des[i-1]) / (ratio[i] - ratio[i-1])
                break
        th2 = 1 + base ** 2 / 2
        rows.append(dict(b1=base, thetadot2=th2, De_c=Dec, K=(Dec * th2 if Dec else None),
                         De=des, ratio=ratio))
    Ks = [r["K"] for r in rows if r["K"]]
    json.dump({"rows": rows, "K_mean": statistics.mean(Ks),
               "K_std": (statistics.pstdev(Ks) if len(Ks) > 1 else 0.0), "N": 192},
              open(HERE / "julia_collapse.json", "w"), indent=1)
    print(f"  collapse K = {statistics.mean(Ks):.4f} "
          f"(spread {100*(max(Ks)-min(Ks))/statistics.mean(Ks):.1f}%)")

    # ---- amp -> julia_amp.json ----
    amp = sorted([r for r in ok if r["kind"] == "amp"], key=lambda r: r["amp"])
    amps = [r["amp"] for r in amp]; dxs = [abs(r["dx"]) for r in amp]
    X = [math.log(a) for a in amps]; Y = [math.log(d) for d in dxs]
    n = len(X); mx = sum(X)/n; my = sum(Y)/n
    p = sum((x-mx)*(y-my) for x, y in zip(X, Y)) / sum((x-mx)**2 for x in X)
    c = my - p * mx
    json.dump({"amps": amps, "dx": dxs, "exponent": p, "logintercept": c, "De": 1.0, "N": 192},
              open(HERE / "julia_amp.json", "w"), indent=1)
    print(f"  amplitude exponent p = {p:.4f}")
    print("wrote julia_dense.json, julia_collapse.json, julia_amp.json")
