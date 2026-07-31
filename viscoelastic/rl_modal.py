"""Reinforcement learning: the swimmer DISCOVERS the rhythm from reward alone.

THE POINT
---------
Everything so far found the optimal rhythm by optimisation or by algebra -- methods that already
"know" they are looking for a stroke. This asks a different question, the one an organism faces:
given only the goal "go as far as you can per stroke" and a scalar reward, can an agent that
starts knowing nothing LEARN the right rhythm? And -- the headline -- does an identical agent,
trained at different Deborah numbers, learn OPPOSITE strategies?

WHY THIS IS GENUINELY RL, AND ONLY IN A FLUID WITH MEMORY
--------------------------------------------------------
In Newtonian fluid the scallop theorem makes this MDP degenerate: displacement depends only on
the SEQUENCE of shapes, never on their timing, so there is no hidden state and nothing to learn
(every policy scores exactly zero). In a viscoelastic fluid the polymer stress field is real
hidden state carrying the swimmer's history -- what the agent does now changes the reward later.
That is genuine temporal credit assignment. RL earns its keep precisely where memory exists.

THE FORMULATION -- deliberately the SAME axis we validated
----------------------------------------------------------
The agent controls only its RHYTHM, on the exact reparametrisation axis the rest of the project
uses: nominal time t in [0, 2pi), the policy emits a positive warp rate rho(t) = dtheta/dt,
normalised so integral(rho) = 2pi. So the shape path (cos theta over [-1,1]) and the period are
fixed BY CONSTRUCTION -- no amplitude or frequency loophole -- and rho == 1 is exactly the plain
sinusoid a naive agent starts from. Reward = net displacement per cycle (fixed period => more
per cycle = fewer cycles = least time from A to B, the user's objective).

The policy is a tiny from-scratch numpy MLP (no torch -- matches the repo). It is trained by
REINFORCE (policy gradient): no gradient through the fluid solver, no supplied answer, just
(reward - baseline) x grad-log-prob. The learned "linger metric" C = <rho(t) cos t> is >0 when
the agent chooses to rush through the open phase (linger closed) and <0 when it lingers open.
C reversing sign across De IS the reversal, learned.

    modal run --detach rl_modal.py::main           # train agents below & above the crossover
    modal run rl_modal.py::status                   # learning curves + learned rhythms, any time
    python rl_modal.py                              # LOCAL: env sanity vs known ground truth
"""
import json
import numpy as np
import modal

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("numpy==2.4.6").add_local_python_source("solver2"))
app = modal.App("viscoelastic-rl", image=image)
STATE = modal.Dict.from_name("viscoelastic-rl-state", create_if_missing=True)

PI = 3.141592653589793
D0, AMP = 1.0, 0.35
BRINK, EPS1, EPS2, ETA_P = 0.5, 0.14, 0.26, 1.0
NBIN = 24                 # policy resolution over the cycle
HID = 16                  # MLP hidden units
N_GRID, NSTEPS, NCYC = 128, 400, 3
POP, GENS = 40, 45        # rollouts per update, updates
DES = [0.5, 0.81, 2.0]    # below / at / above the crossover


# ------------------------------------------------------------------ the environment
def rho_to_stroke(rho_bins):
    """A per-bin warp rate rho(t) -> a smooth stroke(t) on the fixed reparametrisation axis.
    rho is smoothed (periodic) and normalised so theta sweeps exactly 2pi per period -- path and
    period are therefore fixed and only the TIMING varies. rho==const gives the plain sinusoid."""
    T = len(rho_bins)
    tc = (np.arange(T) + 0.5) * 2 * PI / T
    M = 2048
    tg = np.linspace(0, 2 * PI, M, endpoint=False)
    # periodic linear interp of the bin values, kept strictly positive
    ext_t = np.concatenate([tc - 2 * PI, tc, tc + 2 * PI])
    ext_r = np.tile(np.maximum(rho_bins, 1e-3), 3)
    rf = np.interp(tg, ext_t, ext_r)
    rf *= (M / rf.sum())                       # <rho> = 1  =>  integral over [0,2pi) = 2pi
    dt = 2 * PI / M
    theta = np.concatenate([[0.0], np.cumsum(rf) * dt])[:M]   # theta(t), theta(0)=0
    tg_ext = np.concatenate([tg, [2 * PI]])
    th_ext = np.concatenate([theta, [2 * PI]])
    rf_ext = np.concatenate([rf, [rf[0]]])

    def stroke(t):
        tm = t % (2 * PI)
        th = np.interp(tm, tg_ext, th_ext)
        rr = np.interp(tm, tg_ext, rf_ext)
        return (D0 + AMP * np.cos(th), -AMP * np.sin(th) * rr)
    return stroke


ETARGET = 0.0721   # the effort of the +/-0.5 rhythms -- the shell the reversal lives on


def rescale_to_effort(rho_bins, E0=ETARGET):
    """Scale the modulation (not the mean) so <(dd/dt)^2> = E0. Mean stays 1 => period fixed.
    Pure quadrature, no PDE. Returns the rescaled pacing; the naive sinusoid is the s=0 floor."""
    r = np.asarray(rho_bins, float)
    m = r - r.mean()
    if np.max(np.abs(m)) < 1e-9:
        return np.ones_like(r)

    ts = np.linspace(0, 2 * PI, 1200, endpoint=False)
    tcb = (np.arange(len(m)) + 0.5) * 2 * PI / len(m)
    ext_t = np.concatenate([tcb - 2 * PI, tcb, tcb + 2 * PI])

    def eff(s):
        rr = np.maximum(1.0 + s * m, 1e-3)
        rf = np.interp(ts, ext_t, np.tile(rr, 3)); rf *= len(ts) / rf.sum()
        theta = np.concatenate([[0.0], np.cumsum(rf) * (2 * PI / len(ts))])[:len(ts)]
        dd = -AMP * np.sin(theta) * rf
        return float(np.mean(dd ** 2))

    lo, hi = 0.0, 6.0
    if eff(hi) < E0:                       # modulation too weak to reach budget: use max
        return np.maximum(1.0 + hi * m, 1e-3)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if eff(mid) < E0:
            lo = mid
        else:
            hi = mid
    return np.maximum(1.0 + 0.5 * (lo + hi) * m, 1e-3)


def reward(rho_bins, lam, N=N_GRID, nsteps=NSTEPS, ncyc=NCYC):
    """Net |displacement| per cycle -- the scalar the agent maximises. Never raises."""
    import traceback
    try:
        from solver2 import Solver2
        rho_bins = rescale_to_effort(rho_bins)      # matched energy budget -- see ETARGET
        s = Solver2(N=N, L=4 * PI, brink=BRINK, lam=lam, eps1=EPS1, eps2=EPS2,
                    eta_p=ETA_P, stroke=rho_to_stroke(rho_bins))
        r = s.run(ncycles=ncyc, nsteps=nsteps)
        return dict(ok=True, R=abs(float(r[-1][0])), dx=float(r[-1][0]),
                    stokes_res=float(r[-1][1]))
    except Exception:
        return dict(ok=False, err=traceback.format_exc()[-300:])


# --------------------------------------------------------------- the policy (numpy MLP)
def policy_init(seed=0):
    rng = np.random.default_rng(seed)
    return dict(W1=rng.normal(0, 0.5, (2, HID)), b1=np.zeros(HID),
                W2=rng.normal(0, 0.3, (HID, 1)), b2=np.zeros(1))


def policy_mean(P):
    """Mean action a(t) at each bin centre; rho = softplus(a) + 0.05 keeps it positive.
    Returns (means, cache-for-backprop)."""
    tc = (np.arange(NBIN) + 0.5) * 2 * PI / NBIN
    X = np.stack([np.cos(tc), np.sin(tc)], 1)          # (NBIN, 2)
    H = np.tanh(X @ P["W1"] + P["b1"])                 # (NBIN, HID)
    mu = (H @ P["W2"] + P["b2"])[:, 0]                 # (NBIN,)
    return mu, (X, H)


def policy_grad(P, cache, dmu):
    """Backprop d(objective)/d(params) given d(objective)/d(mu) per bin."""
    X, H = cache
    gW2 = H.T @ dmu[:, None]
    gb2 = np.array([dmu.sum()])
    dH = (dmu[:, None] @ P["W2"].T) * (1 - H ** 2)
    gW1 = X.T @ dH
    gb1 = dH.sum(0)
    return dict(W1=gW1, b1=gb1, W2=gW2, b2=gb2)


def act_to_rho(a):
    return np.log1p(np.exp(np.clip(a, -20, 20))) + 0.05     # softplus + floor


def linger_metric(rho_bins):
    """C = <rho(t) cos t>.  >0: rushes the OPEN phase -> lingers CLOSED.  <0: lingers open."""
    tc = (np.arange(len(rho_bins)) + 0.5) * 2 * PI / len(rho_bins)
    return float(np.mean(rho_bins * np.cos(tc)))


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
def rollout(job: dict) -> dict:
    """One episode: sample actions from the current policy, evaluate reward. Self-contained."""
    import numpy as np
    P = {k: np.array(v) for k, v in job["policy"].items()}
    sigma, seed, lam = job["sigma"], job["seed"], job["lam"]
    mu, _ = policy_mean(P)
    rng = np.random.default_rng(seed)
    a = mu + sigma * rng.normal(size=NBIN)             # sampled action
    r = reward(act_to_rho(a), lam)
    if not r.get("ok"):
        return dict(ok=False, err=r.get("err"), seed=seed)
    return dict(ok=True, R=r["R"], dx=r["dx"], a=[float(x) for x in a],
                stokes_res=r["stokes_res"], seed=seed)


@app.function(cpu=1.0, memory=2048, timeout=43200)
def train(lam: float) -> dict:
    """REINFORCE, running SERVER-SIDE so a disconnect cannot kill it. Checkpoints every update."""
    import numpy as np
    tag = f"De={lam}"
    P = policy_init(seed=0)
    # Adam
    m = {k: np.zeros_like(v) for k, v in P.items()}
    v = {k: np.zeros_like(v) for k, v in P.items()}
    b1, b2, eps, lr = 0.9, 0.999, 1e-8, 0.03
    sigma = 0.45
    hist, best = [], dict(R=-1.0)
    STATE[tag] = dict(status="running", lam=lam, history=[], best=None,
                      config=dict(nbin=NBIN, hid=HID, pop=POP, gens=GENS, N=N_GRID))

    # baseline sinusoid (rho == 1) for reference
    base = reward(np.ones(NBIN), lam)
    base_R = base["R"] if base.get("ok") else float("nan")

    for g in range(GENS):
        mu, cache = policy_mean(P)
        jobs = [dict(policy={k: P[k].tolist() for k in P}, sigma=sigma,
                     seed=1000 * g + i, lam=lam) for i in range(POP)]
        res = [r for r in rollout.map(jobs, return_exceptions=True) if isinstance(r, dict)]
        good = [r for r in res if r.get("ok")]
        if len(good) < POP // 2:
            continue
        R = np.array([r["R"] for r in good])
        A = np.array([r["a"] for r in good])               # (n, NBIN)
        adv = (R - R.mean()) / (R.std() + 1e-9)            # baseline + normalise
        # REINFORCE: grad_mu = E[ adv * (a - mu)/sigma^2 ]
        dmu = ((adv[:, None] * (A - mu[None, :])) / sigma ** 2).mean(0)
        grads = policy_grad(P, cache, dmu)                 # maximise -> ascend
        for k in P:
            m[k] = b1 * m[k] + (1 - b1) * grads[k]
            v[k] = b2 * v[k] + (1 - b2) * grads[k] ** 2
            mhat = m[k] / (1 - b1 ** (g + 1))
            vhat = v[k] / (1 - b2 ** (g + 1))
            P[k] = P[k] + lr * mhat / (np.sqrt(vhat) + eps)   # + : gradient ASCENT
        sigma = max(0.08, sigma * 0.955)

        mu_now, _ = policy_mean(P)
        rho_now = rescale_to_effort(act_to_rho(mu_now))
        det = reward(rho_now, lam)                         # greedy (noise-free) policy value
        detR = det["R"] if det.get("ok") else float("nan")
        C = linger_metric(rho_now)
        if detR > best["R"]:
            best = dict(R=detR, rho=[float(x) for x in rho_now], C=C, gen=g)
        hist.append(dict(gen=g, batch_mean=float(R.mean()), greedy_R=float(detR),
                         gain=float(detR / base_R), linger_C=C, sigma=float(sigma)))
        STATE[tag] = dict(status="running", lam=lam, base_R=float(base_R),
                          history=hist, best=best, config=STATE[tag]["config"])

    STATE[tag] = dict(status="done", lam=lam, base_R=float(base_R), history=hist,
                      best=best, config=STATE[tag]["config"])
    return dict(lam=lam, best_R=best["R"], best_C=best["C"])


@app.local_entrypoint()
def main():
    calls = [(De, train.spawn(De)) for De in DES]
    print("spawned RL training, server-side (disconnect-proof):")
    for De, c in calls:
        print(f"  De={De:<5} call {c.object_id}")
    print("\nread progress any time:  modal run rl_modal.py::status")


@app.local_entrypoint()
def status():
    out = {}
    print(f"{'De':>6} {'status':>9} {'base':>10} {'greedy':>10} {'gain':>8} "
          f"{'linger C':>10} {'strategy':>16}")
    for De in DES:
        try:
            s = STATE[f"De={De}"]
        except KeyError:
            print(f"{De:>6}   (no state yet)"); continue
        h = s.get("history", [])
        b = s.get("best") or {}
        C = b.get("C", float("nan"))
        strat = "LINGER CLOSED" if C > 0.02 else ("LINGER OPEN" if C < -0.02 else "~symmetric")
        last = h[-1] if h else {}
        print(f"{De:>6} {s['status']:>9} {s.get('base_R',float('nan')):>10.3e} "
              f"{b.get('R',float('nan')):>10.3e} {last.get('gain',float('nan')):>8.3f} "
              f"{C:>10.4f} {strat:>16}")
        out[str(De)] = dict(lam=De, base_R=s.get("base_R"), history=h, best=b,
                            status=s["status"])
    json.dump(out, open("rl_results.json", "w"), indent=1)
    if all(out.get(str(D), {}).get("status") == "done" for D in DES):
        Cs = [(D, out[str(D)]["best"]["C"]) for D in DES if str(D) in out]
        print("\nlearned linger-metric vs De:")
        for D, C in Cs:
            print(f"  De={D}: C={C:+.4f}  -> {'closed' if C>0 else 'open'}")
        signs = [np.sign(C) for _, C in Cs]
        if signs[0] < 0 < signs[-1]:
            print("\n  => THE AGENT LEARNED OPPOSITE STRATEGIES ACROSS De. Reversal, from reward alone.")


# ----------------------------------------------------- LOCAL: validate env vs ground truth
if __name__ == "__main__":
    # The env MUST reproduce the known crossover before any RL result is trusted.
    # rho = 1 + b cos t  rushes the open phase -> lingers CLOSED (C>0); rho = 1 - b cos t opens.
    print("ENV SANITY — must match crossover_results.json:")
    print("  De=0.5 -> OPEN wins    De=2.0 -> CLOSED wins\n")
    tc = (np.arange(NBIN) + 0.5) * 2 * PI / NBIN
    closed = 1 + 0.5 * np.cos(tc)      # linger closed
    openr = 1 - 0.5 * np.cos(tc)       # linger open
    print(f"  {'De':>5} {'closed |dx|':>13} {'open |dx|':>13} {'winner':>10} "
          f"{'C_closed':>9}")
    for De in (0.5, 2.0):
        rc = reward(closed, De, N=96, nsteps=400, ncyc=4)
        ro = reward(openr, De, N=96, nsteps=400, ncyc=4)
        win = "CLOSED" if rc["R"] > ro["R"] else "OPEN"
        print(f"  {De:>5} {rc['R']:>13.4e} {ro['R']:>13.4e} {win:>10} "
              f"{linger_metric(closed):>9.4f}")
    # uniform rho must reproduce the plain sinusoid baseline
    su = reward(np.ones(NBIN), 2.0, N=96, nsteps=400, ncyc=4)
    print(f"\n  uniform rho (should be the sinusoid): |dx|={su['R']:.4e}  "
          f"stokes_res={su['stokes_res']:.1e}")


# ============================ CONTROLLED agent: learns on the exact reversal axis ============
# The free agent above explores all pacing shapes and picks its own modulation depth, so its
# crossover need not sit at our headline De_c=0.81. This controlled agent is restricted to the
# ONE-parameter reversal axis rho(t) = 1 + b1 cos t (rescaled to the matched-effort shell), so
# the only thing it can learn is the SIGN and size of b1 -- exactly the axis on which De_c=0.81
# is defined. b1>0 lingers closed, b1<0 lingers open. The learned b1 must flip sign at De_c.

DES_CTRL = [0.3, 0.5, 0.65, 0.81, 1.0, 1.3, 2.0]


def reward_b1(b1, lam):
    tc = (np.arange(NBIN) + 0.5) * 2 * PI / NBIN
    return reward(1.0 + b1 * np.cos(tc), lam)      # rescale_to_effort inside puts it on E0


@app.function(cpu=2.0, memory=8192, timeout=14400,
              retries=modal.Retries(max_retries=3, backoff_coefficient=1.0,
                                    initial_delay=5.0))
def rollout_b1(job: dict) -> dict:
    import numpy as np
    mu, sig, seed, lam = job["mu"], job["sigma"], job["seed"], job["lam"]
    rng = np.random.default_rng(seed)
    b1 = float(np.clip(mu + sig * rng.normal(), -0.9, 0.9))
    r = reward_b1(b1, lam)
    if not r.get("ok"):
        return dict(ok=False, seed=seed)
    return dict(ok=True, R=r["R"], b1=b1, seed=seed)


@app.function(cpu=1.0, memory=2048, timeout=43200)
def train_b1(lam: float) -> dict:
    """REINFORCE on the single parameter b1. Gaussian policy N(mu, sigma); learn mu."""
    import numpy as np
    tag = f"ctrl De={lam}"
    mu, sigma, m, v = 0.0, 0.4, 0.0, 0.0
    hist, best = [], dict(R=-1.0)
    base = reward_b1(0.0, lam); baseR = base["R"] if base.get("ok") else float("nan")
    for g in range(28):
        jobs = [dict(mu=mu, sigma=sigma, seed=100 * g + i, lam=lam) for i in range(24)]
        res = [r for r in rollout_b1.map(jobs, return_exceptions=True)
               if isinstance(r, dict) and r.get("ok")]
        if len(res) < 6:
            continue
        R = np.array([r["R"] for r in res]); B = np.array([r["b1"] for r in res])
        adv = (R - R.mean()) / (R.std() + 1e-9)
        gmu = float((adv * (B - mu) / sigma ** 2).mean())
        m = 0.9 * m + 0.1 * gmu; v = 0.999 * v + 0.001 * gmu ** 2
        mu = float(np.clip(mu + 0.06 * (m / (1 - 0.9 ** (g + 1))) /
                           (np.sqrt(v / (1 - 0.999 ** (g + 1))) + 1e-8), -0.9, 0.9))
        sigma = max(0.05, sigma * 0.93)
        det = reward_b1(mu, lam); detR = det["R"] if det.get("ok") else float("nan")
        if detR > best["R"]:
            best = dict(R=detR, b1=mu, gen=g)
        hist.append(dict(gen=g, b1=mu, R=float(detR), gain=float(detR / baseR)))
        STATE[tag] = dict(status="running", lam=lam, baseR=float(baseR), history=hist,
                          best=best)
    STATE[tag] = dict(status="done", lam=lam, baseR=float(baseR), history=hist, best=best)
    return dict(lam=lam, b1=best["b1"])


@app.local_entrypoint()
def controlled():
    calls = [(De, train_b1.spawn(De)) for De in DES_CTRL]
    print("spawned CONTROLLED agents (learn b1 on the reversal axis):")
    for De, c in calls:
        print(f"  De={De:<5} {c.object_id}")
    print("read:  modal run rl_modal.py::ctrl_status")


@app.local_entrypoint()
def ctrl_status():
    out = {}
    print(f"{'De':>6} {'status':>9} {'learned b1':>11} {'gain':>7} {'strategy':>15}")
    for De in DES_CTRL:
        try:
            s = STATE[f"ctrl De={De}"]
        except KeyError:
            print(f"{De:>6}   (none)"); continue
        b = s.get("best", {}); b1 = b.get("b1", float("nan"))
        strat = "LINGER CLOSED" if b1 > 0.03 else ("LINGER OPEN" if b1 < -0.03 else "~sinusoid")
        last = s.get("history", [{}])[-1]
        print(f"{De:>6} {s['status']:>9} {b1:>+11.4f} {last.get('gain', float('nan')):>7.3f} "
              f"{strat:>15}")
        out[str(De)] = dict(lam=De, best=b, history=s.get("history", []), status=s["status"])
    json.dump(out, open("rl_ctrl_results.json", "w"), indent=1)
    done = [o for o in out.values() if o["status"] == "done"]
    if len(done) == len(DES_CTRL):
        bs = [(o["lam"], o["best"]["b1"]) for o in sorted(out.values(), key=lambda z: z["lam"])]
        neg = [De for De, b in bs if b < 0]; pos = [De for De, b in bs if b > 0]
        if neg and pos and max(neg) < min(pos):
            print(f"\n  => LEARNED b1 FLIPS SIGN between De={max(neg)} and De={min(pos)}.")
            print("     The agent learned OPPOSITE strategies across the crossover. Reversal, "
                  "from reward.")
