"""Step 0 (hours-scale de-risking): does fluid memory let a RECIPROCAL swimmer move?

This is the cheapest possible test of the mechanism, before committing to a 2D
Stokes-Oldroyd-B solver.  It is not a swimmer simulation -- it is the minimal ODE that
contains the physics we are betting on.

THE MODEL
---------
One shape degree of freedom xi(t), periodic.  With one DOF every periodic stroke is
reciprocal by construction (you must return the way you came), which is exactly why the
scallop is the cleanest probe.

  Stokes (no memory):     xdot = A(xi) xidot
  With memory:            xdot = A(xi) xidot  +  C(xi) s
  Polymer stress:         De ds/dtau = -s + dxi/dtau        (Maxwell relaxation)

with tau = omega t, so De = lambda*omega is the Deborah number: relaxation time over
stroke time.  A(xi) is the instantaneous Stokes coupling; C(xi) couples the *stored*
polymer stress to thrust.

WHY THE STOKES TERM IS EXACTLY ZERO
-----------------------------------
  oint A(xi) xidot dt = oint A(xi) dxi = 0
for any closed path in a 1-D shape space, because A depends on the instantaneous shape
only.  That is the scallop theorem in one line, and it is the 1-D case of the "net
displacement = enclosed area" law measured in ../solver/gait.py (a 1-D loop encloses no
area).  So EVERY micron of motion below is attributable to memory.  Nothing else can
contribute.

WHY C(xi) MUST DEPEND ON SHAPE
------------------------------
Integrating the stress equation over one period with s periodic gives oint s dtau = 0.
So a constant C contributes C * oint s dtau = 0.  Memory alone is not enough: the
coupling must vary with configuration.  Physically that is the geometric asymmetry an
asymmetric dumbbell provides.  Both ingredients are necessary; the script checks this.

SOLUTION METHOD
---------------
The stress equation is LINEAR in s even when C is nonlinear (C only enters the
displacement integral).  So s is obtained exactly by Fourier transform, with no time
stepping and no transient to discard:

  xi = sum_n xihat_n e^{i n tau}   =>   shat_n = i n xihat_n / (1 + i n De)

and the net displacement per cycle is  Dx = oint C(xi) s dtau, evaluated by quadrature.
"""
import numpy as np


# ----------------------------------------------------------------------------- core

def stress_from_shape(xi, De):
    """Periodic steady-state Maxwell stress driven by dxi/dtau, computed spectrally.

    De ds/dtau = -s + dxi/dtau   ->   shat_n = i n xihat_n / (1 + i n De)
    """
    N = len(xi)
    n = np.fft.fftfreq(N, d=1.0 / N)          # integer wavenumbers
    xihat = np.fft.fft(xi)
    shat = (1j * n * xihat) / (1.0 + 1j * n * De)
    return np.real(np.fft.ifft(shat))


def displacement(xi, De, C):
    """Net displacement per cycle, Dx = (1/N) sum C(xi) s  (the Stokes term is exactly 0)."""
    s = stress_from_shape(xi, De)
    return float(np.mean(C(xi) * s)) * 2 * np.pi     # oint ... dtau over [0, 2pi)


def waveform(coeffs, N=4096):
    """Periodic shape xi(tau) from harmonic coefficients [(a1,p1), (a2,p2), ...]."""
    tau = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    xi = np.zeros_like(tau)
    for k, (a, p) in enumerate(coeffs, start=1):
        xi += a * np.cos(k * tau + p)
    return tau, xi


def dissipation(xi):
    """Cost proxy: mean square shape rate, <(dxi/dtau)^2>. Fixes the 'effort' budget."""
    N = len(xi)
    n = np.fft.fftfreq(N, d=1.0 / N)
    d = np.real(np.fft.ifft(1j * n * np.fft.fft(xi)))
    return float(np.mean(d ** 2))


# ------------------------------------------------------------------- analytic check

def displacement_linear_analytic(coeffs, De):
    """Exact result for LINEAR coupling C(xi)=xi.

    Dx = 2 pi De sum_n n^2 |xihat_n|^2 / (1 + n^2 De^2)

    For a single harmonic of amplitude a this is  pi a^2 De / (1 + De^2),
    which peaks at De = 1 -- independent of amplitude.
    """
    tot = 0.0
    for k, (a, _p) in enumerate(coeffs, start=1):
        tot += np.pi * a ** 2 * k ** 2 * De / (1.0 + k ** 2 * De ** 2)
    return tot


if __name__ == "__main__":
    lin = lambda xi: xi                       # C(xi) = xi     (linear coupling)
    const = lambda xi: np.ones_like(xi)       # C(xi) = 1      (no shape dependence)

    print("Reciprocal swimmer with fluid memory -- 0-D mechanism check")
    print("one shape DOF => every stroke is reciprocal => Stokes gives exactly zero\n")

    print("[1] the two necessary ingredients (sinusoid, a=1)")
    _, xi = waveform([(1.0, 0.0)])
    print(f"    {'case':<44} {'Dx/cycle':>14}")
    print(f"    {'De=0   (no memory), C(xi)=xi':<44} {displacement(xi, 0.0, lin):>14.3e}  <- scallop theorem")
    print(f"    {'De=1   (memory),    C(xi)=1  (const)':<44} {displacement(xi, 1.0, const):>14.3e}  <- no shape dependence")
    print(f"    {'De=1   (memory),    C(xi)=xi':<44} {displacement(xi, 1.0, lin):>14.3e}  <- BOTH: it swims")

    print("\n[2] numerics vs exact analytic result, C(xi)=xi")
    print(f"    {'De':>6} {'numeric':>14} {'analytic':>14} {'rel err':>10}")
    for De in (0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 20.0):
        num = displacement(xi, De, lin)
        ana = displacement_linear_analytic([(1.0, 0.0)], De)
        err = abs(num - ana) / max(abs(ana), 1e-300)
        print(f"    {De:6.2f} {num:14.9f} {ana:14.9f} {err:10.1e}")

    print("\n[3] Deborah sweep -- where is the sweet spot?")
    print(f"    {'De':>7} {'Dx/cycle':>14}   {'':<22}")
    best = (0, -1)
    for De in (0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 10.0, 30.0):
        d = displacement(xi, De, lin)
        bar = "#" * int(60 * d / (np.pi / 2))
        if d > best[1]:
            best = (De, d)
        print(f"    {De:7.2f} {d:14.6f}   {bar}")
    print(f"    peak at De = {best[0]} "
          f"(analytic optimum for a single harmonic is exactly De = 1)")

    print("\n[4] limits behave as they must")
    for De, label in ((1e-6, "De->0   fluid forgets instantly (Stokes)"),
                      (1e6, "De->inf fluid never relaxes (elastic solid)")):
        print(f"    {label:<45} Dx = {displacement(xi, De, lin):.3e}")
