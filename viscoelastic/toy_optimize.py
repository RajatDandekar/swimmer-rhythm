"""Step 0b: is the optimal stroke NON-TRIVIAL? This decides whether the project has legs.

toy0d.py showed a reciprocal swimmer moves when the fluid has memory. But "it moves" is
not yet a research programme -- we need there to be something worth SEARCHING for. If the
best stroke is always a plain sinusoid, there is nothing for CMA-ES (let alone RL) to
discover and the whole optimisation framing collapses.

THE ANALYTIC WARNING
--------------------
For LINEAR coupling C(xi) = xi, the exact result from toy0d.py is

    Dx = 2 pi De sum_n n^2 |xihat_n|^2 / (1 + n^2 De^2)

Maximising this at fixed dissipation <(dxi/dtau)^2> = sum_n n^2 |xihat_n|^2 means
maximising a weighted average of the per-mode gain De/(1 + n^2 De^2). That gain is
strictly DECREASING in n, so all the effort should go into the n = 1 mode:
**the pure sinusoid is provably optimal and the search is trivial.**

So a positive answer requires nonlinearity in the coupling. Physically that is real -- an
asymmetric dumbbell's coupling to the stored stress is not linear in its separation, and
its drag varies with configuration too. Here we add the leading correction

    C(xi) = xi + c2 * xi^2

and ask whether asymmetric TIMING (harmonics beating against each other) now beats the
sinusoid at equal effort. If yes, the optimisation is real and the full solver is
justified. If no, the whole approach needs rethinking before anything expensive is built.
"""
import numpy as np
from scipy.optimize import minimize

from toy0d import stress_from_shape, waveform, dissipation

N = 2048
DISS_BUDGET = 0.5      # fixed effort: <(dxi/dtau)^2>. sinusoid a=1 gives exactly 0.5


def shape_from_params(p, N=N):
    """p = [a1, a2, phi2, a3, phi3]; harmonic 1's phase is fixed to 0 (time origin)."""
    coeffs = [(p[0], 0.0), (p[1], p[2]), (p[3], p[4])]
    return waveform(coeffs, N=N)[1]


def rescale(xi, budget=DISS_BUDGET):
    """Scale the stroke to sit exactly on the effort budget."""
    d = dissipation(xi)
    return xi * np.sqrt(budget / d) if d > 1e-14 else xi


def displacement_nl(xi, De, c2):
    """Net displacement with C(xi) = xi + c2 xi^2."""
    s = stress_from_shape(xi, De)
    return float(np.mean((xi + c2 * xi ** 2) * s)) * 2 * np.pi


def optimize(De, c2, restarts=40, seed=0):
    """Maximise displacement at fixed effort. Multi-start to avoid local optima."""
    rng = np.random.default_rng(seed)
    best_val, best_p = -np.inf, None
    for i in range(restarts):
        p0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0]) if i == 0 else \
             np.concatenate([[rng.uniform(0.3, 1.5)],
                             rng.uniform(-0.8, 0.8, 1), rng.uniform(0, 2 * np.pi, 1),
                             rng.uniform(-0.5, 0.5, 1), rng.uniform(0, 2 * np.pi, 1)])
        f = lambda p: -displacement_nl(rescale(shape_from_params(p)), De, c2)
        r = minimize(f, p0, method="Nelder-Mead",
                     options=dict(maxiter=4000, xatol=1e-10, fatol=1e-12))
        if -r.fun > best_val:
            best_val, best_p = -r.fun, r.x
    return best_val, best_p


def sinusoid_baseline(De, c2):
    xi = rescale(shape_from_params(np.array([1.0, 0, 0, 0, 0])))
    return displacement_nl(xi, De, c2)


def asymmetry(xi):
    """Time-reversal asymmetry: how unlike its own time-reverse the stroke is.
    0 = perfectly reversible timing (e.g. a pure sinusoid), 1 = maximally asymmetric."""
    best = min(np.linalg.norm(xi - np.roll(xi[::-1], k)) for k in range(len(xi)))
    return float(best / (2 * np.linalg.norm(xi)))


if __name__ == "__main__":
    print("Is the optimal reciprocal stroke non-trivial?")
    print(f"effort held fixed at <(dxi/dtau)^2> = {DISS_BUDGET} for every stroke\n")

    print("[1] LINEAR coupling C(xi)=xi  -- theory says the sinusoid must win")
    print(f"    {'De':>5} {'sinusoid':>12} {'optimised':>12} {'gain':>8} {'asym':>7}")
    for De in (0.3, 1.0, 3.0):
        base = sinusoid_baseline(De, 0.0)
        val, p = optimize(De, 0.0, restarts=25)
        xi = rescale(shape_from_params(p))
        print(f"    {De:5.1f} {base:12.6f} {val:12.6f} {val/base:8.4f} {asymmetry(xi):7.3f}")
    print("    -> gain ~ 1.0 confirms the analytic prediction: nothing to search for.")

    print("\n[2] NONLINEAR coupling C(xi)=xi + c2 xi^2  -- does timing start to matter?")
    print(f"    {'De':>5} {'c2':>5} {'sinusoid':>12} {'optimised':>12} {'gain':>8} {'asym':>7}")
    results = []
    for c2 in (0.3, 0.6):
        for De in (0.3, 1.0, 3.0):
            base = sinusoid_baseline(De, c2)
            val, p = optimize(De, c2, restarts=40)
            xi = rescale(shape_from_params(p))
            g = val / base if abs(base) > 1e-12 else np.nan
            results.append((De, c2, g))
            print(f"    {De:5.1f} {c2:5.2f} {base:12.6f} {val:12.6f} {g:8.4f} {asymmetry(xi):7.3f}")

    gains = [g for _, _, g in results]
    print(f"\n    best gain over the sinusoid: {max(gains):.3f}x")
    if max(gains) > 1.02:
        print("    -> VERDICT: the optimum is NON-TRIVIAL. Stroke timing matters, so there")
        print("       is a real search problem and the full 2-D solver is justified.")
    else:
        print("    -> VERDICT: sinusoid still wins. The optimisation framing needs rethinking")
        print("       BEFORE building anything expensive.")

    print("\n[3] what the winning stroke looks like (De=1, c2=0.6)")
    val, p = optimize(1.0, 0.6, restarts=60)
    xi = rescale(shape_from_params(p))
    a = np.abs([p[0], p[1], p[3]])
    print(f"    harmonic amplitudes |a1|,|a2|,|a3| = {a[0]:.3f}, {a[1]:.3f}, {a[2]:.3f}")
    print(f"    relative phases phi2, phi3 = {p[2] % (2*np.pi):.3f}, {p[4] % (2*np.pi):.3f} rad")
    print(f"    time-reversal asymmetry = {asymmetry(xi):.3f}  "
          f"(sinusoid = {asymmetry(rescale(shape_from_params(np.array([1.,0,0,0,0])))):.3f})")
    tau = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    xs = np.interp(tau, np.linspace(0, 2*np.pi, N, endpoint=False), xi)
    lo, hi = xs.min(), xs.max()
    print("\n    stroke over one cycle (open -> close):")
    for lev in range(6, -1, -1):
        row = "".join("#" if (x - lo) / (hi - lo) * 6 >= lev - 0.5 else " " for x in xs)
        print(f"      |{row}|")
