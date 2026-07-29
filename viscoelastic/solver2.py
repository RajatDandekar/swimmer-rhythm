"""Solver v2. One change from spike2d.py, and it is the whole ballgame.

THE DIAGNOSIS I GOT WRONG FIRST TIME
------------------------------------
v1 needed ~1600 timesteps per cycle for 1% accuracy, and I blamed stiffness in the -C/lam
relaxation. Wrong. Checking the actual limits at lam=1, dx=0.065, |u|~0.3:

    relaxation   dt < lam              = 1.0
    diffusion    dt < dx^2/(4 eps_s)   = 0.53
    advection    dt < dx/|u|           = 0.21
    used                                 0.0157

Nothing was stiff. The error was **catastrophic cancellation**: the instantaneous swimmer
velocity is O(1e-2), and the net displacement per cycle is O(1e-7). Five orders of
cancellation, so a 1e-9 per-step quadrature error is a 1% error in the answer.

THE FIX
-------
Split the velocity analytically. With F = (ddot - Du_p)/SumM,

    U_c = F (M22 - M11)/2 + ubar_p
        = [ddot/SumM](M22-M11)/2          <- U_stokes = A(d) ddot
        + [-Du_p/SumM](M22-M11)/2 + ubar_p <- U_poly

In a periodic box the mobilities are translation-invariant, so M11 and M22 are constants
and M12 depends only on the separation d. Hence A depends on d alone and

    oint U_stokes dt = oint A(d) dd = 0     EXACTLY, analytically.

So the net displacement per cycle is oint U_poly dt -- and U_poly is *already* the small
quantity. The cancellation is gone: we integrate 1e-7 to get 1e-7 instead of integrating
1e-2 to get 1e-7.

The swimmer is still advanced with the full U_stokes + U_poly (that is the true motion, and
the within-cycle excursion does influence the polymer field). Only the *reported* net
displacement uses the split. oint U_stokes dt is carried as a free diagnostic: it must come
out at round-off, and if it does not, something is wrong.
"""
import numpy as np


class Solver2:
    def __init__(self, N=128, L=2 * np.pi, eta_s=1.0, eta_p=1.0, lam=1.0,
                 eps_s=2e-3, eps1=0.14, eps2=0.26, d0=1.0, amp=0.30, stroke=None,
                 brink=None):
        self.N, self.L = N, L
        self.eta_s, self.eta_p, self.lam, self.eps_s = eta_s, eta_p, lam, eps_s
        self.eps1, self.eps2, self.d0, self.amp = eps1, eps2, d0, amp
        self.brink = brink   # screening length; None = pure Stokes
        # stroke(t) -> (d, ddot); default is the plain reciprocal sinusoid
        self.stroke = stroke or (lambda t: (d0 + amp * np.cos(t), -amp * np.sin(t)))

        k1 = 2 * np.pi * np.fft.fftfreq(N, d=L / N)
        self.KX, self.KY = np.meshgrid(k1, k1, indexing="ij")
        self.K2 = self.KX ** 2 + self.KY ** 2
        self.K2inv = np.where(self.K2 > 0, 1.0 / np.where(self.K2 > 0, self.K2, 1), 0.0)
        kmax = np.max(np.abs(k1))
        self.mask = (np.abs(self.KX) <= 2 / 3 * kmax) & (np.abs(self.KY) <= 2 / 3 * kmax)
        self.zero = np.zeros_like(self.KX)
        self.reset()

    def reset(self):
        N = self.N
        self.Cxx = np.ones((N, N)); self.Cxy = np.zeros((N, N)); self.Cyy = np.ones((N, N))
        self.xc = 0.0
        self.acc_poly = 0.0        # integral of U_poly   -> the answer
        self.acc_stokes = 0.0      # integral of U_stokes -> must be round-off

    # ------------------------------------------------------------------ spectral ops
    def stokes(self, fxh, fyh):
        dot = self.KX * fxh + self.KY * fyh
        px = fxh - self.KX * dot * self.K2inv
        py = fyh - self.KY * dot * self.K2inv
        if self.brink is None:
            return px * self.K2inv / self.eta_s, py * self.K2inv / self.eta_s
        # Brinkman: (k^2 + 1/l^2) instead of k^2 -> real-space decay ~ exp(-r/l)
        inv = 1.0 / (self.K2 + 1.0 / self.brink ** 2)
        return px * inv / self.eta_s, py * inv / self.eta_s

    def spread_hat(self, Fx, xb, eps):
        return Fx * np.exp(-1j * (self.KX * xb + self.KY * (self.L / 2))) \
                  * np.exp(-0.5 * eps ** 2 * self.K2)

    def interp(self, uh, xb, eps):
        ph = np.exp(1j * (self.KX * xb + self.KY * (self.L / 2)))
        return float(np.real(np.sum(uh * ph * np.exp(-0.5 * eps ** 2 * self.K2)))) / self.N ** 2

    def polymer_force_hat(self):
        c = self.eta_p / self.lam
        txxh = c * np.fft.fft2(self.Cxx - 1.0)
        txyh = c * np.fft.fft2(self.Cxy)
        tyyh = c * np.fft.fft2(self.Cyy - 1.0)
        return 1j * (self.KX * txxh + self.KY * txyh), 1j * (self.KX * txyh + self.KY * tyyh)

    # -------------------------------------------------------------------------- step
    def velocity_field(self, t):
        d, dd = self.stroke(t)
        x1, x2 = self.xc - d / 2, self.xc + d / 2

        pxh, pyh = self.polymer_force_hat()
        upxh, _ = self.stokes(pxh, pyh)
        up1, up2 = self.interp(upxh, x1, self.eps1), self.interp(upxh, x2, self.eps2)

        u1h, _ = self.stokes(self.spread_hat(1.0, x1, self.eps1), self.zero)
        u2h, _ = self.stokes(self.spread_hat(1.0, x2, self.eps2), self.zero)
        M11 = self.interp(u1h, x1, self.eps1); M21 = self.interp(u1h, x2, self.eps2)
        M12 = self.interp(u2h, x1, self.eps1); M22 = self.interp(u2h, x2, self.eps2)
        SumM, dM = M11 + M22 - M12 - M21, M22 - M11

        # --- the analytic split: Stokes part integrates to zero over a closed stroke
        U_stokes = (dd / SumM) * dM / 2.0
        U_poly = (-(up2 - up1) / SumM) * dM / 2.0 + (up1 + up2) / 2.0

        F = (dd - (up2 - up1)) / SumM
        fxh = self.spread_hat(-F, x1, self.eps1) + self.spread_hat(F, x2, self.eps2) + pxh
        uxh, uyh = self.stokes(fxh, pyh)
        return uxh, uyh, U_stokes, U_poly

    def dCdt(self, uxh, uyh):
        ux, uy = np.real(np.fft.ifft2(uxh)), np.real(np.fft.ifft2(uyh))
        gx = lambda h: np.real(np.fft.ifft2(1j * self.KX * h * self.mask))
        gy = lambda h: np.real(np.fft.ifft2(1j * self.KY * h * self.mask))
        Lxx, Lxy, Lyx, Lyy = gx(uxh), gy(uxh), gx(uyh), gy(uyh)
        Cxxh, Cxyh, Cyyh = np.fft.fft2(self.Cxx), np.fft.fft2(self.Cxy), np.fft.fft2(self.Cyy)
        adv = lambda h: -(ux * gx(h) + uy * gy(h))
        lap = lambda h: np.real(np.fft.ifft2(-self.K2 * h))
        return (adv(Cxxh) + 2 * (Lxx * self.Cxx + Lxy * self.Cxy)
                - (self.Cxx - 1) / self.lam + self.eps_s * lap(Cxxh),
                adv(Cxyh) + (Lxx * self.Cxy + Lxy * self.Cyy)
                + (self.Cxx * Lyx + self.Cxy * Lyy) - self.Cxy / self.lam + self.eps_s * lap(Cxyh),
                adv(Cyyh) + 2 * (Lyx * self.Cxy + Lyy * self.Cyy)
                - (self.Cyy - 1) / self.lam + self.eps_s * lap(Cyyh))

    def run(self, ncycles=6, nsteps=400):
        T = 2 * np.pi; dt = T / nsteps
        out = []
        for _ in range(ncycles):
            p0, s0 = self.acc_poly, self.acc_stokes
            for n in range(nsteps):
                t = n * dt
                C0 = (self.Cxx.copy(), self.Cxy.copy(), self.Cyy.copy()); xc0 = self.xc
                ux1, uy1, Us1, Up1 = self.velocity_field(t)
                k1 = self.dCdt(ux1, uy1)
                self.Cxx = C0[0] + dt * k1[0]; self.Cxy = C0[1] + dt * k1[1]
                self.Cyy = C0[2] + dt * k1[2]; self.xc = xc0 + dt * (Us1 + Up1)
                ux2, uy2, Us2, Up2 = self.velocity_field(t + dt)
                k2 = self.dCdt(ux2, uy2)
                self.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0])
                self.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
                self.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
                self.xc = xc0 + 0.5 * dt * (Us1 + Us2 + Up1 + Up2)
                self.acc_poly += 0.5 * dt * (Up1 + Up2)
                self.acc_stokes += 0.5 * dt * (Us1 + Us2)
            out.append((self.acc_poly - p0, self.acc_stokes - s0))
        return out


def sweep_point(**kw):
    """One (parameters) -> displacement evaluation. This is the unit of parallel work."""
    nc = kw.pop("ncycles", 5); ns = kw.pop("nsteps", 400)
    s = Solver2(**kw); r = s.run(ncycles=nc, nsteps=ns)
    return dict(dx=r[-1][0], stokes_residual=r[-1][1], history=[a for a, _ in r], **kw)


if __name__ == "__main__":
    import time
    print("v2: analytic Stokes/polymer split -- cancellation removed\n")
    print(f"{'amp':>6} {'dx (v2)':>14} {'oint U_stokes':>15} {'dx/amp^2':>13}")
    amps = [0.05, 0.075, 0.10, 0.15]; vals = []
    t0 = time.time()
    for a in amps:
        r = sweep_point(N=96, lam=1.0, amp=a, ncycles=5, nsteps=400)
        vals.append(r["dx"])
        print(f"{a:6.3f} {r['dx']:14.6e} {r['stokes_residual']:15.2e} {r['dx']/a**2:13.6e}")
    p = np.polyfit(np.log(amps), np.log(np.abs(vals)), 1)[0]
    sp = max(v/a**2 for v, a in zip(vals, amps)) / min(v/a**2 for v, a in zip(vals, amps)) - 1
    print(f"\nexponent = {p:.4f}  (v1 gave 1.909; theory says 2.000)")
    print(f"dx/amp^2 spread = {sp*100:.1f}%   (v1 gave 6.7%)     [{time.time()-t0:.0f}s]")
