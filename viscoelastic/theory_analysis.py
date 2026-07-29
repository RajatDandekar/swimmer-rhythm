"""Reduced-order theory for the reversal. No PDE -- this is a few lines of Fourier algebra.

THE STRUCTURE, DERIVED
----------------------
At leading order in amplitude the Oldroyd-B conformation obeys  dc/dt + c/lambda = 2E, so the
polymer stress is the strain rate passed through a FIRST-ORDER LAG:

    s_n = (i n g_n) / (1 + i n De)          g(t) = cos(theta(t)) is the shape signal

A force-free two-bead swimmer's velocity is the stress times a coupling that depends on the
instantaneous shape (through the separation-dependent mobility). Expanding that coupling about
the mean shape,

    U ~ s(t) * (c0 + c1 A g + c2 A^2 g^2 + ...)

and integrating over a cycle:

    oint s dt        = 0        zero-mean forcing; a CONSTANT coupling swims nowhere
    oint g s dt      = P(De)    the PAIR term
    oint g^2 s dt    = Q(De)    the TRIPLE term

WHY THE PAIR TERM CANNOT EXPLAIN THE REVERSAL. Jacobi-Anger gives
cos(t + b sin t) = sum_k J_k(b) cos((k+1)t), so g_n = J_{n-1}(b). Since J_k(-b) = (-1)^k J_k(b),
the MAGNITUDES |g_n| are identical for +b and -b. P depends only on |g_n|^2 -- indeed
P = sum_n |g_n|^2 n^2 De/(1+n^2 De^2), manifestly positive and identical for both rhythms. So at
this order the two rhythms swim IDENTICALLY. That is why the 0-D toy could never produce a
reversal: it only had this term.

The triple term is a three-wave correlation and is sensitive to the PHASES, which do flip. So

    dx(+b) = c1 A P + c2 A^2 Q(+b)
    dx(-b) = c1 A P + c2 A^2 Q(-b)      and the reversal is where Q(+b) = Q(-b).

THE PREDICTION TO CHECK. If this is the right structure, the crossover De_c comes out of the
Fourier algebra alone -- no fluid solver, no fitted constants -- and it should scale the same
way the PDE says it does: De_c proportional to 1 / <theta'^2>.

Note <theta'^2> is exactly the spectral second moment of the analytic signal exp(i theta):
sum_n n^2 |J_{n-1}(b)|^2 = <|d/dt e^{i theta}|^2> = <theta'^2> = 1 + b^2/2, using sum J_k^2 = 1.
So "the fluid responds to the mean-square frequency it actually sees" is a statement about where
the spectral weight of the stroke sits.
"""
import numpy as np

NT = 4096


def signals(b, De, m=1, phi=0.0):
    """Shape g = cos(theta), and the lagged stress s, for theta = t + b sin(m t + phi)."""
    t = np.arange(NT) * 2 * np.pi / NT
    th = t + b * np.sin(m * t + phi)
    g = np.cos(th)
    n = np.fft.fftfreq(NT, d=1.0 / NT)
    gh = np.fft.fft(g)
    sh = (1j * n * gh) / (1.0 + 1j * n * De)          # strain rate through the lag
    s = np.real(np.fft.ifft(sh))
    return g, s


def P_of(b, De, m=1, phi=0.0):
    g, s = signals(b, De, m, phi)
    return float(np.mean(g * s))


def Q_of(b, De, m=1, phi=0.0):
    g, s = signals(b, De, m, phi)
    return float(np.mean(g * g * s))


def crossover(b, m=1, phi=0.0, lo=0.02, hi=8.0):
    """De where Q(+b) = Q(-b): bisect on the antisymmetric part."""
    f = lambda D: Q_of(b, D, m, phi) - Q_of(-b, D, m, phi)
    a, c = lo, hi
    fa, fc = f(a), f(c)
    if fa * fc > 0:
        return None
    for _ in range(80):
        mid = np.sqrt(a * c)
        fm = f(mid)
        if fa * fm <= 0:
            c, fc = mid, fm
        else:
            a, fa = mid, fm
    return float(np.sqrt(a * c))


def second_moment(b, m=1):
    return 1.0 + 0.5 * (m * b) ** 2


if __name__ == "__main__":
    print(__doc__.split("THE STRUCTURE")[0].strip())
    print("=" * 78)

    print("\n[1] THE PAIR TERM IS BLIND TO THE SIGN OF b  (so it cannot reverse anything)")
    print("  %6s %14s %14s %12s" % ("b", "P(+b)", "P(-b)", "difference"))
    for b in (0.3, 0.5, 0.8):
        p, m_ = P_of(b, 1.0), P_of(-b, 1.0)
        print("  %6.2f %14.6e %14.6e %12.1e" % (b, p, m_, abs(p - m_)))

    print("\n[2] THE TRIPLE TERM DOES FLIP, AND CROSSES ZERO")
    print("  %6s %14s %14s %14s" % ("De", "Q(+0.5)", "Q(-0.5)", "difference"))
    for De in (0.3, 0.6, 0.9, 1.2, 2.0):
        qp, qm = Q_of(0.5, De), Q_of(-0.5, De)
        print("  %6.2f %14.6e %14.6e %14.3e" % (De, qp, qm, qp - qm))

    print("\n[3] THE CROSSOVER FROM THEORY ALONE — no solver, no fitted constants")
    print("  %6s %10s %12s %14s" % ("b", "De_c", "<theta'^2>", "De_c x <th'^2>"))
    rows = []
    for b in (0.15, 0.25, 0.40, 0.50, 0.65, 0.80, 0.88):
        dc = crossover(b)
        if dc is None:
            print("  %6.2f %10s" % (b, "none")); continue
        m2 = second_moment(b)
        rows.append((b, dc, dc * m2))
        print("  %6.2f %10.4f %12.4f %14.4f" % (b, dc, m2, dc * m2))
    if rows:
        v = np.array([r[2] for r in rows])
        print("  -> theory constant %.4f, spread %.2f%%" % (v.mean(), 100 * v.std() / v.mean()))

    print("\n[4] SHAPE INDEPENDENCE — modulate a different harmonic, same second moment")
    print("  %28s %8s %10s %12s %14s" % ("modulation", "b", "De_c", "<theta'^2>", "product"))
    tests = [("1st harmonic  b=0.50", 0.50, 1), ("2nd harmonic  b=0.25", 0.25, 2),
             ("3rd harmonic  b=1/6 ", 1 / 6, 3)]
    prods = []
    for name, b, m in tests:
        dc = crossover(b, m=m)
        if dc is None:
            print("  %28s %8.3f %10s" % (name, b, "none")); continue
        m2 = second_moment(b, m)
        prods.append(dc * m2)
        print("  %28s %8.3f %10.4f %12.4f %14.4f" % (name, b, dc, m2, dc * m2))
    if len(prods) > 1:
        v = np.array(prods)
        print("  -> spread across DIFFERENT modulation shapes: %.2f%%   %s"
              % (100 * v.std() / v.mean(),
                 "SECOND MOMENT GOVERNS" if v.std() / v.mean() < 0.03 else "shape matters too"))

    print("\n[5] PHASE INVARIANCE — <theta'^2> does not depend on phi, so De_c must not either")
    print("  %10s %10s" % ("phi/pi", "De_c"))
    ps = []
    for k in (0.0, 0.25, 0.5, 0.75):
        dc = crossover(0.5, phi=k * np.pi)
        ps.append(dc)
        print("  %10.2f %10.4f" % (k, dc if dc else float("nan")))
    ps = np.array([p for p in ps if p])
    print("  -> spread %.2f%%" % (100 * ps.std() / ps.mean()))
