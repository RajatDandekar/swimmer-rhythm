"""Does RL have anything to learn in pure Stokes flow?  Settle it numerically.

The solver in taylor_spectral.py prescribes sheet kinematics and returns the instantaneous
rigid drift U.  That is exactly an RL environment interface: action = shape rate, observation
= shape, reward = drift.  So we can ask the decisive question directly.

Shape space.  Take the two-mode family
    y_s(a, t) = a1(t) sin(a) + a2(t) cos(a)
on material points x = a (purely transverse, extensible sheet).  A gait is a closed loop in
the (a1, a2) plane.  Note that the circle a1 = b cos t, a2 = -b sin t gives
    y_s = b sin(a - t)
i.e. exactly Taylor's traveling wave.

Stokes flow is instantaneous and kinematically reversible, so the net displacement over one
cycle is a *geometric* quantity: a line integral of a connection 1-form over the loop, with
no dependence on how fast the loop is traversed.  Three consequences, all testable here:

  (1) AREA LAW      net displacement per cycle ~ -(signed area enclosed in shape space)
  (2) SCALLOP       a loop that encloses zero area (a back-and-forth line, a figure eight)
                    produces exactly zero net displacement, however cleverly it is timed
  (3) RATE-FREE     traversing the same loop faster changes nothing per cycle

If (1)-(3) hold, then optimal gait selection in Stokes is "maximize enclosed area subject to
a dissipation budget" -- a calculus-of-variations problem in two dimensions, not a sequential
decision problem.  There is no hidden state for a policy to track and no credit to assign
across time.  RL would be a very expensive way to rediscover a geometric identity.

RL earns its keep only once the fluid has MEMORY (finite Re, viscoelasticity, a neighbour),
because that is what breaks the rate-independence and turns shape into a genuine state.
"""
import numpy as np
from taylor_spectral import basis


def drift(a1, a2, a1dot, a2dot, N=20, oversample=6):
    """Instantaneous rigid drift U for the two-mode transverse shape, given shape + shape rate."""
    M = oversample * N
    a = np.linspace(0.0, 2 * np.pi, M, endpoint=False)
    xs = a
    ys = a1 * np.sin(a) + a2 * np.cos(a)
    ux = np.zeros_like(a)
    uy = a1dot * np.sin(a) + a2dot * np.cos(a)

    Gu, Gv = basis(xs, ys, N)
    G = np.zeros((2 * M, 4 * N + 1))
    G[:M, :4 * N] = Gu
    G[M:, :4 * N] = Gv
    G[:M, -1] = -1.0
    rhs = np.concatenate([ux, uy])
    scale = np.linalg.norm(G, axis=0)
    scale[scale == 0] = 1.0
    q, *_ = np.linalg.lstsq(G / scale, rhs, rcond=None)
    return (q / scale)[-1] + ux.mean()


def net_displacement(loop, nt=240, N=20):
    """Integrate the drift once around a closed loop in shape space.

    loop(s) -> (a1, a2) for s in [0, 1), assumed closed and traversed once.
    Shape rates come from a spectrally-accurate derivative of the sampled loop, so the
    result is insensitive to nt.
    """
    s = np.linspace(0.0, 1.0, nt, endpoint=False)
    A = np.array([loop(si) for si in s])            # (nt, 2)
    # d/ds by FFT (the loop is periodic in s by construction)
    k = np.fft.fftfreq(nt, d=1.0 / nt)
    dA = np.real(np.fft.ifft(1j * 2 * np.pi * k[:, None] * np.fft.fft(A, axis=0), axis=0))
    U = np.array([drift(A[i, 0], A[i, 1], dA[i, 0], dA[i, 1], N=N) for i in range(nt)])
    return U.mean()                                  # = (1/T) * integral over one period


def signed_area(loop, nt=2000):
    """Signed area enclosed by the loop in the (a1, a2) plane (shoelace / Green's theorem)."""
    s = np.linspace(0.0, 1.0, nt, endpoint=False)
    A = np.array([loop(si) for si in s])
    x, y = A[:, 0], A[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


if __name__ == "__main__":
    b = 0.15
    tau = 2 * np.pi

    print(__doc__.split("if (1)")[0].strip()[:0] or "", end="")
    print("Two-mode transverse sheet, shape y = a1 sin(x) + a2 cos(x).  b = %.2f\n" % b)

    gaits = {
        "circle (= Taylor traveling wave)":
            lambda s: (b * np.cos(tau * s), -b * np.sin(tau * s)),
        "circle, reversed orientation":
            lambda s: (b * np.cos(tau * s), +b * np.sin(tau * s)),
        "ellipse, a2 half-amplitude":
            lambda s: (b * np.cos(tau * s), -0.5 * b * np.sin(tau * s)),
        "RECIPROCAL line (a2 = 0)":
            lambda s: (b * np.cos(tau * s), 0.0),
        "RECIPROCAL line, non-sinusoidal timing":
            lambda s: (b * np.cos(tau * s + 0.7 * np.sin(tau * s)), 0.0),
        "RECIPROCAL diagonal line":
            lambda s: (b * np.cos(tau * s), 0.6 * b * np.cos(tau * s)),
        "figure eight (zero net area)":
            lambda s: (b * np.sin(tau * s), b * np.sin(2 * tau * s)),
    }

    print("[1] area law and the scallop theorem")
    print("    claim:  net displacement per cycle  =  signed area enclosed in shape space")
    print(f"    {'gait':<38} {'net displ / cycle':>18} {'signed area':>14} {'ratio':>8}")
    for name, g in gaits.items():
        d = net_displacement(g)
        ar = signed_area(g)
        ratio = (d / ar) if abs(ar) > 1e-12 else float("nan")
        print(f"    {name:<38} {d:>18.3e} {ar:>14.3e} {ratio:>8.4f}")

    print("\n[1b] the area law is the LEADING-ORDER statement: ratio -> 1 as b -> 0")
    print(f"    {'b':>7} {'net displ':>15} {'signed area':>14} {'ratio':>9} {'1-b^2':>9}")
    for bb in (0.30, 0.20, 0.10, 0.05, 0.02, 0.01):
        g = (lambda B: (lambda s: (B * np.cos(tau * s), -B * np.sin(tau * s))))(bb)
        d, ar = net_displacement(g), signed_area(g)
        print(f"    {bb:7.2f} {d:15.6e} {ar:14.6e} {d/ar:9.6f} {1-bb**2:9.6f}")

    print("\n[2] rate-independence: same loop, traversed at different speeds")
    print("    (net displacement PER CYCLE must not change -- Stokes has no clock)")
    circle = gaits["circle (= Taylor traveling wave)"]
    base = net_displacement(circle)
    for rate in (1, 2, 5):
        # reparametrise s -> s (same loop), but sample a non-uniform schedule to fake
        # a different traversal law: s' = s + 0.3 sin(2 pi s) still covers the loop once
        warp = (lambda r: (lambda s: circle((s + 0.3 * np.sin(tau * s) / r) % 1.0)))(rate)
        d = net_displacement(warp)
        print(f"    traversal warp 1/{rate}:  net displ/cycle = {d:.6e}   "
              f"rel. change vs uniform = {abs(d - base) / abs(base):.1e}")

    print("\n[3] what an RL agent would be optimising, if you ran one")
    print("    reward-per-cycle is a pure function of the enclosed area, so the whole")
    print("    sequential-decision structure collapses to a 2-D geometry problem.")
