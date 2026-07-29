import modal
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("vesw-dbg", image=image)
@app.function(cpu=2.0, timeout=900)
def one(p: dict):
    import traceback
    try:
        from solver2 import sweep_point
        return {"ok": True, **sweep_point(**p)}
    except Exception:
        return {"ok": False, "tb": traceback.format_exc()}
@app.local_entrypoint()
def main():
    import numpy as np
    r = one.remote(dict(N=96, L=2*np.pi, lam=1.0, amp=0.05, nsteps=400, ncycles=2))
    print(r if r.get("ok") else r["tb"])
