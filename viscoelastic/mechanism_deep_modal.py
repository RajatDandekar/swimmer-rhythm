"""What sets the critical Deborah number? The phase-lag mechanism, measured from the PDE.

The reduced theory says the reversal is where a triple-wave correlation changes sign, and it
predicts a crossover -- but at De~0.61 against the PDE's 0.81. So the mechanism is right and the
NUMBER is not yet explained. This run measures, directly from the full solver, the physical
quantity that should set De_c: the phase lag of the polymer force behind the shape, and the
decomposition of the net drift into an elastic (in-phase) and a viscous (quadrature) part.

HYPOTHESIS. Net drift = <(mobility gradient) . F_poly>. The mobility gradient is in phase with
the shape; F_poly lags it by an angle phi(De) that grows from 0 (viscous limit) toward pi/2
(elastic limit). The drift is a projection ~ cos(phi - phi*), so it changes sign when the lag
crosses a critical angle. If the two mirror rhythms project this lag differently, De_c is where
their projections cross -- a definite, measurable phase condition, not a fitted number.

OUTPUTS (to a modal.Dict, disconnect-proof):
 [sweep] fine De grid, both rhythms: time series d(t), U_poly(t) over the last cycle, and the
         drift. -> phase lag phi(De), elastic/viscous split, and the crossover as a phase.
 [movie] 3 De spanning De_c, both rhythms: cropped stress field at 6 phases through the cycle.
         -> contour sequence and its +/-b difference; where the asymmetry lives and reverses.
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-mech-deep", image=image)
STATE = modal.Dict.from_name("viscoelastic-mech-deep-state", create_if_missing=True)

PI = 3.141592653589793
KS = [1.0, 2.0, 3.0]
D0, AMP = 1.0, 0.35
N, L, BRINK = 192, 4 * PI, 0.5
MOVIE_N = 288          # higher resolution for the publication contour figure
NSTEPS, NCYC = 600, 6
WX, WY = 1.55, 0.88
SWEEP_DE = [0.3, 0.4, 0.5, 0.6, 0.7, 0.81, 0.9, 1.0, 1.2, 1.5, 2.0]
MOVIE_DE = [0.5, 0.81, 1.5]
MOVIE_TH = [0.15, 0.35, 0.55, 0.75, 0.90, 1.30]     # phases (theta/pi) through the cycle


def stroke_of(b1):
    b = np.array([b1, 0.0, 0.0]); ph = np.zeros(3); ks = np.array(KS)

    def stroke(t):
        th = t + float(np.sum(b * np.sin(ks * t + ph)))
        dth = 1.0 + float(np.sum(b * ks * np.cos(ks * t + ph)))
        return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)
    return stroke


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0, initial_delay=5.0))
def run_series(job: dict) -> dict:
    """Last-cycle time series of shape and polymer velocity (small payload)."""
    import numpy as np, traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        s = Solver2(N=N, L=L, brink=BRINK, lam=job["lam"], stroke=stroke_of(job["b1"]))
        dt = 2 * PI / NSTEPS
        d_hist, up_hist, ddot_hist, last0 = [], [], [], 0.0
        for c in range(NCYC):
            if c == NCYC - 1:
                last0 = s.acc_poly
            for n in range(NSTEPS):
                t = n * dt
                _, _, Us, Up = s.velocity_field(t)
                C0 = (s.Cxx.copy(), s.Cxy.copy(), s.Cyy.copy()); xc0 = s.xc
                ux1, uy1, Us1, Up1 = s.velocity_field(t); k1 = s.dCdt(ux1, uy1)
                s.Cxx = C0[0] + dt * k1[0]; s.Cxy = C0[1] + dt * k1[1]; s.Cyy = C0[2] + dt * k1[2]
                s.xc = xc0 + dt * (Us1 + Up1)
                ux2, uy2, Us2, Up2 = s.velocity_field(t + dt); k2 = s.dCdt(ux2, uy2)
                s.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0]); s.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
                s.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
                s.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
                s.acc_poly += 0.5 * dt * (Up1 + Up2); s.acc_stokes += 0.5 * dt * (Us1 + Us2)
                if c == NCYC - 1:
                    dd, dv = s.stroke(t)
                    d_hist.append(dd); ddot_hist.append(dv); up_hist.append(0.5 * (Up1 + Up2))
        out.update(ok=True, dx=float(s.acc_poly - last0), dt=float(dt),
                   d=[float(x) for x in d_hist], ddot=[float(x) for x in ddot_hist],
                   up=[float(x) for x in up_hist])
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-300:])
    return out


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0, initial_delay=5.0))
def run_movie(job: dict) -> dict:
    """Cropped stress field at several phases through the last cycle."""
    import numpy as np, traceback
    out = dict(job)
    try:
        from solver2 import Solver2
        Nm = MOVIE_N
        s = Solver2(N=Nm, L=L, brink=BRINK, lam=job["lam"], stroke=stroke_of(job["b1"]))
        dt = 2 * PI / NSTEPS
        tg = np.arange(NSTEPS) * dt
        th_of_t = tg + job["b1"] * np.sin(tg)
        want = {int(np.argmin(np.abs(th_of_t - th * PI))): th for th in MOVIE_TH}
        x = np.linspace(0, L, Nm, endpoint=False) - L / 2
        mx, my = np.abs(x) <= WX, np.abs(x) <= WY
        caps = {}
        for c in range(NCYC):
            for n in range(NSTEPS):
                t = n * dt
                if c == NCYC - 1 and n in want:
                    d, _ = s.stroke(t)
                    caps[f"{want[n]:.2f}"] = dict(
                        f=(s.Cxx + s.Cyy - 2.0)[np.ix_(mx, my)].tolist(),
                        d=float(d), xc=float(s.xc))
                C0 = (s.Cxx.copy(), s.Cxy.copy(), s.Cyy.copy()); xc0 = s.xc
                ux1, uy1, Us1, Up1 = s.velocity_field(t); k1 = s.dCdt(ux1, uy1)
                s.Cxx = C0[0] + dt * k1[0]; s.Cxy = C0[1] + dt * k1[1]; s.Cyy = C0[2] + dt * k1[2]
                s.xc = xc0 + dt * (Us1 + Up1)
                ux2, uy2, Us2, Up2 = s.velocity_field(t + dt); k2 = s.dCdt(ux2, uy2)
                s.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0]); s.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
                s.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
                s.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
                s.acc_poly += 0.5 * dt * (Up1 + Up2); s.acc_stokes += 0.5 * dt * (Us1 + Us2)
        out.update(ok=True, caps=caps)
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-300:])
    return out


@app.function(cpu=1.0, memory=4096, timeout=21600)
def driver() -> dict:
    sweep_jobs = [dict(lam=De, b1=b) for De in SWEEP_DE for b in (+0.5, -0.5)]
    STATE["status"] = dict(state="sweep", n=len(sweep_jobs))
    sweep = [r for r in run_series.map(sweep_jobs, return_exceptions=True) if isinstance(r, dict)]
    STATE["sweep"] = sweep
    movie_jobs = [dict(lam=De, b1=b) for De in MOVIE_DE for b in (+0.5, -0.5)]
    STATE["status"] = dict(state="movie", n=len(movie_jobs))
    movie = [r for r in run_movie.map(movie_jobs, return_exceptions=True) if isinstance(r, dict)]
    STATE["movie"] = movie
    STATE["status"] = dict(state="done", sweep=len(sweep), movie=len(movie))
    return dict(sweep=len(sweep), movie=len(movie))


@app.local_entrypoint()
def main():
    call = driver.spawn()
    print(f"spawned deep-mechanism run, id = {call.object_id}")
    print("fetch:  modal run mechanism_deep_modal.py::fetch")


@app.function(cpu=1.0, memory=4096, timeout=21600)
def driver_movie() -> dict:
    jobs = [dict(lam=De, b1=b) for De in MOVIE_DE for b in (+0.5, -0.5)]
    STATE["status"] = dict(state="movie", n=len(jobs))
    movie = [r for r in run_movie.map(jobs, return_exceptions=True) if isinstance(r, dict)]
    STATE["movie"] = movie
    STATE["status"] = dict(state="done", sweep=len(STATE.get("sweep", [])), movie=len(movie))
    return dict(movie=len(movie))


@app.local_entrypoint()
def movie_only():
    call = driver_movie.spawn()
    print(f"spawned hi-res movie, id = {call.object_id}")


@app.local_entrypoint()
def fetch():
    try:
        st = STATE["status"]
    except KeyError:
        print("no state yet"); return
    print("status:", st)
    if st.get("state") != "done":
        print("still running"); return
    json.dump(dict(sweep=STATE["sweep"], movie=STATE["movie"],
                   sweep_de=SWEEP_DE, movie_de=MOVIE_DE, movie_th=MOVIE_TH),
              open("mechanism_deep.json", "w"))
    print(f"wrote mechanism_deep.json ({st['sweep']} sweep + {st['movie']} movie)")
