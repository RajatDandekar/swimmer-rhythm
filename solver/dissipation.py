"""Second, independent validation: the rate of working / energy dissipation.

Taylor eq (14):  W = b^2 sigma^2 k mu   (mean rate of work per unit area of sheet,
leading order in b).  With mu = sigma = k = 1 this is simply W = (kb)^2.

We rebuild the full stress field analytically from the same spectral coefficients used
for the swimming speed, so this exercises a different part of the solution (pressure and
velocity gradients) than the drift did.

Per mode n, with f = A + C y, g = B + D y, E = e^{-n y}:
    psi  = E (f cos nx + g sin nx)
    u    = E [ (C - n f) cos nx + (D - n g) sin nx ]
    v    = E [ n f sin nx - n g cos nx ]
    u_x  = n E [ (n f - C) sin nx + (D - n g) cos nx ]
    u_y  = E [ (n^2 f - 2 n C) cos nx + (n^2 g - 2 n D) sin nx ]
    v_x  = n^2 E [ f cos nx + g sin nx ]
    v_y  = -u_x
    p    = 2 mu n E [ D cos nx - C sin nx ]      (A,B modes are harmonic -> no pressure)
"""
import numpy as np
from taylor_spectral import sheet, basis


def solve_coeffs(eps, N, t, kind, oversample=6):
    M = oversample * N
    xs, ys, ux, uy = sheet(eps, t, M, kind)
    Gu, Gv = basis(xs, ys, N)
    G = np.zeros((2 * M, 4 * N + 1))
    G[:M, :4 * N] = Gu
    G[M:, :4 * N] = Gv
    G[:M, -1] = -1.0
    rhs = np.concatenate([ux, uy])
    sc = np.linalg.norm(G, axis=0); sc[sc == 0] = 1.0
    q, *_ = np.linalg.lstsq(G / sc, rhs, rcond=None)
    q = q / sc
    return q[:4 * N].reshape(N, 4), q[-1], (xs, ys, ux, uy)


def fields(coeffs, xs, ys, mu=1.0):
    """Assemble u, v, p and velocity gradients at the given points."""
    u = np.zeros_like(xs); v = np.zeros_like(xs); p = np.zeros_like(xs)
    ux_ = np.zeros_like(xs); uy_ = np.zeros_like(xs); vx_ = np.zeros_like(xs)
    for i, (A, B, C, D) in enumerate(coeffs):
        n = i + 1
        E = np.exp(-n * ys); cn = np.cos(n * xs); sn = np.sin(n * xs)
        f = A + C * ys; g = B + D * ys
        u  += E * ((C - n * f) * cn + (D - n * g) * sn)
        v  += E * (n * f * sn - n * g * cn)
        p  += 2 * mu * n * E * (D * cn - C * sn)
        ux_ += n * E * ((n * f - C) * sn + (D - n * g) * cn)
        uy_ += E * ((n * n * f - 2 * n * C) * cn + (n * n * g - 2 * n * D) * sn)
        vx_ += n * n * E * (f * cn + g * sn)
    return u, v, p, ux_, uy_, vx_


def rate_of_working(eps, N=24, t=0.0, kind="transverse", mu=1.0, oversample=8):
    coeffs, U, (xs, ys, uxm, uym) = solve_coeffs(eps, N, t, kind, oversample)
    u, v, p, ux_, uy_, vx_ = fields(coeffs, xs, ys, mu)
    # material velocity of the sheet in the lab frame (= imposed no-slip data)
    Um = uxm + U
    Vm = uym
    # stress
    sxx = -p + 2 * mu * ux_
    syy = -p - 2 * mu * ux_          # v_y = -u_x
    sxy = mu * (uy_ + vx_)
    # upward normal * ds  =  (-dy/dx, 1) dx   (the sqrt(1+y'^2) cancels)
    if kind == "transverse":
        dydx = eps * np.cos(xs - t)
    else:
        dydx = eps * np.cos(xs - t)  # shape is the same sinusoid in both cases
    nx_ds, ny_ds = -dydx, np.ones_like(dydx)
    tx = sxx * nx_ds + sxy * ny_ds
    ty = sxy * nx_ds + syy * ny_ds
    # mean rate of work done by the sheet on the fluid, per unit area of the mean plane
    W = np.mean(Um * tx + Vm * ty)
    return W, U


if __name__ == "__main__":
    print("Rate of working per unit area.  Taylor eq (14): W = mu sigma^2 b^2 k")
    print("units mu=sigma=k=1  ->  W_Taylor = (kb)^2\n")
    for kind in ("transverse", "inextensible"):
        print(f"--- {kind} ---")
        print(f"{'kb':>7} {'W_numeric':>14} {'W/(kb)^2':>12} {'t-spread':>10}")
        for eps in (0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5):
            N = 24 if eps <= 0.3 else 34
            vals = [rate_of_working(eps, N=N, t=tt, kind=kind)[0]
                    for tt in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
            W = float(np.mean(vals))
            print(f"{eps:7.3f} {W:14.9f} {W/eps**2:12.8f} {np.std(vals):10.1e}")
        print()
