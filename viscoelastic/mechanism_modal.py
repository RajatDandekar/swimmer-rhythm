"""The JFM mechanism panels, computed on Modal so a laptop restart cannot kill them.

Run locally this is 6 sequential PDE solves, ~20 minutes, and it has now been destroyed twice --
once by a bad LaTeX label in the plotting step and once by the local process restarting. Both
are the same lesson this project keeps re-learning: never put long compute in the same failure
domain as anything else. Here the six solves run in ONE parallel wave, the driver lives
server-side, and the workers return only the small cropped window rather than whole fields, so
the result is a few kB and lands in a modal.Dict that outlives everything.

WHAT IT SHOWS
-------------
[1] IN SPACE. At matched shape the two rhythms are geometrically identical, so the DIFFERENCE of
    their stress fields isolates exactly what the fluid remembers differently. Shown at three
    Deborah numbers spanning the crossover.
[2] IN THE CYCLE. Net displacement is the integral of U_poly over one stroke, so the running
    integral shows where each rhythm gains and loses, and which finishes ahead. Below De_c one
    curve wins, above it the other does.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-mechanism", image=image)
STATE = modal.Dict.from_name("viscoelastic-mechanism-state", create_if_missing=True)

PI = 3.141592653589793
KS = [1.0, 2.0, 3.0]
D0, AMP = 1.0, 0.35
N, L, BRINK = 256, 4 * PI, 0.5
NSTEPS, NCYC = 600, 6
DES = [0.40, 0.81, 2.00]
THETA = 0.97 * PI                       # fully closed: where the two rhythms differ most
WX, WY = 1.55, 0.88


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
def one(job: dict) -> dict:
    import traceback
    out = dict(job)
    try:
        import numpy as np
        from solver2 import Solver2
        ks = np.array(KS)
        b = np.array([job["b1"], 0.0, 0.0]); ph = np.zeros(3)

        def stroke(t):
            th = t + float(np.sum(b * np.sin(ks * t + ph)))
            dth = 1.0 + float(np.sum(b * ks * np.cos(ks * t + ph)))
            return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)

        s = Solver2(N=N, L=L, brink=BRINK, lam=job["lam"], stroke=stroke)
        dt = 2 * PI / NSTEPS
        tg = np.arange(NSTEPS) * dt
        nwant = int(np.argmin(np.abs(tg + job["b1"] * np.sin(tg) - THETA)))
        x = np.linspace(0, L, N, endpoint=False) - L / 2
        mx, my = np.abs(x) <= WX, np.abs(x) <= WY
        cap, up, last0 = None, [], 0.0
        for c in range(NCYC):
            if c == NCYC - 1:
                last0 = s.acc_poly
            for n in range(NSTEPS):
                t = n * dt
                if c == NCYC - 1 and n == nwant:
                    d, _ = s.stroke(t)
                    cap = dict(f=(s.Cxx + s.Cyy - 2.0)[np.ix_(mx, my)].tolist(),
                               d=float(d), xc=float(s.xc))
                C0 = (s.Cxx.copy(), s.Cxy.copy(), s.Cyy.copy()); xc0 = s.xc
                u1x, u1y, Us1, Up1 = s.velocity_field(t)
                k1 = s.dCdt(u1x, u1y)
                s.Cxx = C0[0] + dt * k1[0]; s.Cxy = C0[1] + dt * k1[1]
                s.Cyy = C0[2] + dt * k1[2]; s.xc = xc0 + dt * (Us1 + Up1)
                u2x, u2y, Us2, Up2 = s.velocity_field(t + dt)
                k2 = s.dCdt(u2x, u2y)
                s.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0])
                s.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
                s.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
                s.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
                s.acc_poly += 0.5 * dt * (Up1 + Up2)
                s.acc_stokes += 0.5 * dt * (Us1 + Us2)
                if c == NCYC - 1:
                    up.append(0.5 * (Up1 + Up2))
        out.update(ok=True, cap=cap, up=[float(v) for v in up],
                   dx=float(s.acc_poly - last0), dt=float(dt),
                   stokes_res=float(s.acc_stokes))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-400:])
    return out


@app.function(cpu=1.0, memory=4096, timeout=14400)
def driver() -> dict:
    jobs = [dict(lam=De, b1=b) for De in DES for b in (+0.5, -0.5)]
    STATE["status"] = dict(state="running", n=len(jobs))
    raw = list(one.map(jobs, return_exceptions=True))
    res = [r for r in raw if isinstance(r, dict)]
    STATE["results"] = res
    STATE["status"] = dict(state="done", n=len(jobs), ok=len(res), dead=len(raw) - len(res))
    return dict(ok=len(res))


@app.local_entrypoint()
def main():
    call = driver.spawn()
    print(f"spawned mechanism run, call id = {call.object_id}")
    print("fetch:  modal run mechanism_modal.py::fetch")


@app.local_entrypoint()
def fetch():
    """Pull the results down and write the JSON the plotting script reads."""
    try:
        st = STATE["status"]
    except KeyError:
        print("no state yet"); return
    print(f"status: {st}")
    if st.get("state") != "done":
        print("still running"); return
    res = [r for r in STATE["results"] if r.get("ok")]
    json.dump(res, open("mechanism_raw.json", "w"))
    print(f"wrote mechanism_raw.json  ({len(res)} runs)")
    for De in DES:
        p = next(r for r in res if r["lam"] == De and r["b1"] > 0)
        m = next(r for r in res if r["lam"] == De and r["b1"] < 0)
        print(f"  De={De:<5} dx(+b)={p['dx']:+.4e}  dx(-b)={m['dx']:+.4e}  "
              f"ratio={abs(p['dx'] / m['dx']):.4f}")
