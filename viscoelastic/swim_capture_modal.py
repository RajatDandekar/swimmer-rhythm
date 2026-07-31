"""Capture the REAL swimmer simulation for the two Deborah-number regimes.

Not a cartoon: this steps the actual spectral Stokes/Oldroyd-B solver (solver2.Solver2, the
same engine behind every number in the paper) and records, frame by frame, the polymer-stretch
field the swimmer leaves in the fluid together with the exact body configuration (opening d,
centre x) and the running net displacement. Two runs:

    weak memory  (De = 0.5): the winning rhythm lingers OPEN
    strong memory(De = 2.0): the winning rhythm lingers CLOSED

Both are the optimum-at-that-fluid found by search / theory / RL. Rendered side by side they
show the strategy reversing. Fields are cropped to a tight window and returned as float16 so
the whole capture fits in a few MB; swim_render.py turns them into the movie.
"""
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-swim-capture", image=image)

PI = 3.141592653589793
BRINK, D0, AMP = 0.5, 1.0, 0.35          # exactly the paper/field settings
KS = np.array([1.0, 2.0, 3.0])
N, L = 384, 4 * PI                        # crisp field; regularised beads span ~8 cells
NSTEPS = 300                              # per cycle
WARMUP, SHOW = 4, 3                       # cycles: settle to the periodic orbit, then film
CAP_EVERY = 5                             # -> 60 frames / cycle
WX, WY = 2.15, 1.2                        # crop window (physical units), wider than tall


def make_stroke(b1):
    b = np.array([b1, 0.0, 0.0]); ph = np.zeros(3)

    def stroke(t):
        th = t + float(np.sum(b * np.sin(KS * t + ph)))
        dth = 1.0 + float(np.sum(b * KS * np.cos(KS * t + ph)))
        return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * dth)
    return stroke


@app.function(cpu=4.0, memory=16384, timeout=7200)
def capture(job: dict) -> dict:
    import traceback
    from solver2 import Solver2
    out = dict(job)
    try:
        s = Solver2(N=N, L=L, brink=BRINK, lam=job["lam"], stroke=make_stroke(job["b1"]))
        T = 2 * PI; dt = T / NSTEPS
        x = np.linspace(0, L, N, endpoint=False) - L / 2
        mx, my = np.abs(x) <= WX, np.abs(x) <= WY
        ix = np.ix_(mx, my)
        fields, uxs, uys, ds, xcs, phases, accs = [], [], [], [], [], [], []
        show_start_acc = None
        for c in range(WARMUP + SHOW):
            filming = c >= WARMUP
            if filming and show_start_acc is None:
                show_start_acc = s.acc_poly
            for n in range(NSTEPS):
                t = n * dt
                # RK2 (mirrors Solver2.run exactly)
                C0 = (s.Cxx.copy(), s.Cxy.copy(), s.Cyy.copy()); xc0 = s.xc
                u1x, u1y, Us1, Up1 = s.velocity_field(t)
                if filming and (n % CAP_EVERY == 0):
                    d, _ = s.stroke(t)
                    fields.append((s.Cxx + s.Cyy - 2.0)[ix].astype(np.float16))
                    uxs.append(np.real(np.fft.ifft2(u1x))[ix].astype(np.float16))
                    uys.append(np.real(np.fft.ifft2(u1y))[ix].astype(np.float16))
                    ds.append(float(d)); xcs.append(float(s.xc))
                    phases.append((c - WARMUP + n / NSTEPS)); accs.append(float(s.acc_poly))
                k1 = s.dCdt(u1x, u1y)
                s.Cxx = C0[0] + dt * k1[0]; s.Cxy = C0[1] + dt * k1[1]
                s.Cyy = C0[2] + dt * k1[2]; s.xc = xc0 + dt * (Us1 + Up1)
                u2x, u2y, Us2, Up2 = s.velocity_field(t + dt); k2 = s.dCdt(u2x, u2y)
                s.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0])
                s.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
                s.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
                s.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
                s.acc_poly += 0.5 * dt * (Up1 + Up2)
        out.update(ok=True, fields=np.stack(fields), ux=np.stack(uxs), uy=np.stack(uys),
                   d=np.array(ds), xc=np.array(xcs),
                   phase=np.array(phases), acc=np.array(accs),
                   dx_per_cycle=float((s.acc_poly - show_start_acc) / SHOW),
                   extent=[-WX, WX, -WY, WY], N=N, L=L, nframes=len(fields))
    except Exception:
        out.update(ok=False, err=traceback.format_exc()[-800:])
    return out


@app.local_entrypoint()
def main():
    jobs = [dict(name="open", label="lingers OPEN", lam=0.5, b1=-0.5),
            dict(name="closed", label="lingers CLOSED", lam=2.0, b1=+0.5)]
    print(f"capturing {len(jobs)} hero simulations at N={N} ...")
    res = list(capture.map(jobs))
    bad = [r for r in res if not r.get("ok")]
    if bad:
        print("FAILED:\n", bad[0]["err"]); return
    save = {}
    for r in res:
        p = r["name"]
        save[f"{p}_fields"] = r["fields"]; save[f"{p}_ux"] = r["ux"]; save[f"{p}_uy"] = r["uy"]
        save[f"{p}_d"] = r["d"]; save[f"{p}_xc"] = r["xc"]; save[f"{p}_phase"] = r["phase"]
        save[f"{p}_acc"] = r["acc"]
        print(f"  {p:6s}  De={r['lam']}  frames={r['nframes']}  "
              f"field={r['fields'].shape}  |u|max={float(np.abs(r['ux']).max()):.3f}  "
              f"dx/cyc={r['dx_per_cycle']:.4e}")
    save["extent"] = np.array(res[0]["extent"]); save["meta"] = np.array([N, L, NSTEPS])
    np.savez_compressed("swim_frames.npz", **save)
    print("wrote swim_frames.npz")


if __name__ == "__main__":
    main()
