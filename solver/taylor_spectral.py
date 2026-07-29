"""
Taylor (1951) swimming sheet, solved from scratch with a spectral boundary-collocation
method for 2D Stokes flow.  Pure numpy.  No CFD package.

Physics
-------
Fluid occupies y > y_s(x,t), semi-infinite, Stokes flow (mu grad^2 u = grad p, div u = 0).
Stream function psi:  u = psi_y,  v = -psi_x,  biharmonic:  grad^4 psi = 0.

Lab frame: fluid at rest at infinity  =>  the n=0 (mean) mode of psi vanishes.
Decaying biharmonic basis for mode n >= 1:
    psi = e^{-n y} [ (A + C y) cos(n x) + (B + D y) sin(n x) ]
    u   = e^{-n y} [ (C - n A - n C y) cos(n x) + (D - n B - n D y) sin(n x) ]
    v   = e^{-n y} [ -n (A + C y) * (-sin(n x)) ... ] see code

Sheet: material points carry a prescribed traveling wave in the sheet's own frame,
plus an unknown rigid translation U e_x (the swimming speed).  Collocate no-slip at
M points, least-squares solve for {A,B,C,D}_{n=1..N} and U.

Units: k = 1, sigma = 1, mu = 1  =>  wave speed V = sigma/k = 1, wavelength = 2*pi.
Taylor's prediction:  U / V = -1/2 (k b)^2  (minus = opposite to wave propagation).
"""
import numpy as np


def basis(xs, ys, N):
    """Columns of (u, v) for each decaying biharmonic mode. Returns (nrows=M, 4N) each."""
    U_cols, V_cols = [], []
    for n in range(1, N + 1):
        E = np.exp(-n * ys)
        cn, sn = np.cos(n * xs), np.sin(n * xs)
        # A_n : psi = A e^{-ny} cos(nx)
        U_cols.append(-n * E * cn);            V_cols.append(n * E * sn)
        # B_n : psi = B e^{-ny} sin(nx)
        U_cols.append(-n * E * sn);            V_cols.append(-n * E * cn)
        # C_n : psi = C y e^{-ny} cos(nx)
        U_cols.append((1 - n * ys) * E * cn);  V_cols.append(n * ys * E * sn)
        # D_n : psi = D y e^{-ny} sin(nx)
        U_cols.append((1 - n * ys) * E * sn);  V_cols.append(-n * ys * E * cn)
    return np.array(U_cols).T, np.array(V_cols).T


def sheet(eps, t, M, kind="transverse"):
    """Material points and their velocity in the sheet's own (non-translating) frame."""
    a = np.linspace(0.0, 2 * np.pi, M, endpoint=False)  # material label
    if kind == "transverse":
        # purely transverse wave, extensible sheet:  x = a,  y = eps sin(a - t)
        xs = a
        ys = eps * np.sin(a - t)
        ux = np.zeros_like(a)
        uy = -eps * np.cos(a - t)
    elif kind == "inextensible":
        # Shape is the traveling sinusoid y = eps sin(x - t); material points are
        # advected along it so that arc length is conserved.  Solve
        #   s(x,t) = int_0^x sqrt(1 + eps^2 cos^2(x'-t)) dx'  =  Lam/(2pi) * a
        # for x, where Lam = arc length per wavelength.  Then u_x = dx/dt at fixed a.
        xs = _invert_arclength(a, eps, t)
        ys = eps * np.sin(xs - t)
        # 5-point central difference in t (O(h^4)) on both x(a,t) and y(a,t)
        h = 2e-3
        X, Y = {}, {}
        for j in (-2, -1, 1, 2):
            X[j] = _invert_arclength(a, eps, t + j * h)
            Y[j] = eps * np.sin(X[j] - (t + j * h))
        ux = (-X[2] + 8 * X[1] - 8 * X[-1] + X[-2]) / (12 * h)
        uy = (-Y[2] + 8 * Y[1] - 8 * Y[-1] + Y[-2]) / (12 * h)
    else:
        raise ValueError(kind)
    return xs, ys, ux, uy


def _invert_arclength(a, eps, t, nq=2000):
    """Given material labels a in [0,2pi), return x such that scaled arclength = a.

    Arclength is accumulated with composite Simpson (O(h^4)) and inverted by cubic
    interpolation, so the O(h^2) trapezoid error no longer limits the O((kb)^4)
    coefficient we are trying to read off.
    """
    from scipy.integrate import cumulative_simpson
    from scipy.interpolate import CubicSpline
    xg = np.linspace(0.0, 2 * np.pi, 2 * nq + 1)
    integ = np.sqrt(1.0 + (eps * np.cos(xg - t)) ** 2)
    s = np.concatenate([[0.0], cumulative_simpson(integ, x=xg)])
    Lam = s[-1]
    return CubicSpline(s, xg)(a * Lam / (2 * np.pi))


def swim_speed(eps, N=20, t=0.0, kind="transverse", oversample=6, report=False):
    """Instantaneous mean drift of the sheet's material points, in the frame where the
    fluid is at rest at infinity.

    NOTE on the frame artifact: the arclength inversion anchors material label a=0 to
    x=0, which injects a SPATIALLY UNIFORM, zero-time-mean longitudinal velocity m(t)
    into the prescribed kinematics.  The solver's U then reads U_true - m(t).  Adding
    back mean(ux) recovers the true drift and makes the answer t-independent.
    """
    M = oversample * N
    xs, ys, ux, uy = sheet(eps, t, M, kind)
    Gu, Gv = basis(xs, ys, N)
    # unknowns: [coeffs (4N), U];  u-eq: u_flow - U = ux ;  v-eq: v_flow = uy
    G = np.zeros((2 * M, 4 * N + 1))
    G[:M, :4 * N] = Gu
    G[M:, :4 * N] = Gv
    G[:M, -1] = -1.0
    rhs = np.concatenate([ux, uy])
    scale = np.linalg.norm(G, axis=0)
    scale[scale == 0] = 1.0
    q, *_ = np.linalg.lstsq(G / scale, rhs, rcond=None)
    q = q / scale
    resid = np.linalg.norm(G @ q - rhs) / max(np.linalg.norm(rhs), 1e-300)
    if report:
        print(f"    N={N} M={M} rel_resid={resid:.3e}")
    return q[-1] + ux.mean(), resid


def swim_speed_avg(eps, N=20, kind="transverse", nt=8, oversample=6):
    """Period-average, as a belt-and-braces check that the drift is truly steady."""
    ts = np.linspace(0.0, 2 * np.pi, nt, endpoint=False)
    vals = [swim_speed(eps, N=N, t=t, kind=kind, oversample=oversample) for t in ts]
    U = np.array([v[0] for v in vals])
    return U.mean(), U.std(), max(v[1] for v in vals)


if __name__ == "__main__":
    np.set_printoptions(precision=10)
    print("Taylor swimming sheet: spectral boundary collocation, pure numpy")
    print("units k=sigma=mu=1 -> wave speed V=1; Taylor: U/V = -1/2 (kb)^2\n")

    print("[1] convergence in N at kb=0.2 (transverse, extensible)")
    for N in (4, 8, 12, 16, 20, 24, 32):
        U, r = swim_speed(0.2, N=N, kind="transverse")
        print(f"    N={N:3d}  U={U:+.12f}  U/(-0.5 eps^2)={U/(-0.5*0.04):.10f}  resid={r:.2e}")

    print("\n[2] time-independence check (kb=0.3, N=24)")
    for t in np.linspace(0, 2 * np.pi, 5, endpoint=False):
        U, r = swim_speed(0.3, N=24, t=t, kind="transverse")
        print(f"    t={t:.4f}  U={U:+.12f}")

    print("\n[3] amplitude sweep -> recover 1/2 and the O((kb)^4) coefficient")
    from fractions import Fraction
    for kind in ("transverse", "inextensible"):
        print(f"\n    --- {kind} ---")
        print(f"    {'kb':>7} {'U(drift)':>18} {'-U/(kb)^2':>13} {'t-spread':>10} {'resid':>9}")
        rows = []
        for eps in (0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5):
            N = 24 if eps <= 0.3 else 34
            U, sd, r = swim_speed_avg(eps, N=N, kind=kind)
            rows.append((eps, U))
            print(f"    {eps:7.3f} {U:+18.12f} {-U/eps**2:13.9f} {sd:10.1e} {r:9.1e}")
        # fit  -U/V = 1/2 eps^2 (1 + c eps^2 + d eps^4 + f eps^6) on the small-eps rows
        sub = [r for r in rows if r[0] <= 0.2]
        e = np.array([r[0] for r in sub])
        y = np.array([-r[1] for r in sub]) / (0.5 * e ** 2) - 1.0
        A = np.vstack([e ** 2, e ** 4, e ** 6]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        c = coef[0]
        print(f"    fit (kb<=0.2):  -U/V = 0.5 (kb)^2 [1 + c (kb)^2 + ...]")
        print(f"         c = {c:+.9f}    nearest simple fraction: "
              f"{Fraction(c).limit_denominator(64)}  (= {float(Fraction(c).limit_denominator(64)):+.9f})")
        print(f"         reference: -19/32 = {-19/32:.9f} | -19/16 = {-19/16:.9f} | "
              f"-31/32 = {-31/32:.9f}")
