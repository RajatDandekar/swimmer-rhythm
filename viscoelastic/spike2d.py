"""Two-day feasibility spike: 2-D Stokes-Oldroyd-B, two immersed beads, reciprocal stroke.

Question this answers: does an asymmetric dumbbell with a purely back-and-forth stroke
actually swim in a fluid with memory, in a real PDE solve rather than a 0-D toy -- and how
many seconds does one stroke cost?

PHYSICS
-------
Stokes (inertialess) + Oldroyd-B polymer, 2-D periodic box:

    0 = -grad p + eta_s lap u + div tau_p + f_IB ,   div u = 0
    tau_p = (eta_p / lam) (C - I)
    DC/Dt = L C + C L^T - (C - I)/lam + eps_s lap C ,   L_ij = du_i/dx_j

Dropping inertia is deliberate: the scallop theorem then holds EXACTLY at lam = 0, so any
net displacement is unambiguously attributable to memory. Nothing else can contribute.

SWIMMER
-------
Two beads on the x-axis, separation d(t) = d0 + a cos(t) prescribed (reciprocal by
construction -- one DOF, so it must retrace its path). Beads have DIFFERENT regularisation
widths eps1 != eps2: that is the geometric asymmetry, the PDE analogue of the toy's
requirement that the stress-to-thrust coupling vary with configuration.

Force-free: the two bead forces are internal, F1 = -F, F2 = +F. Writing M_ij for the
mobility (x-velocity at bead i from unit x-force at bead j) and u_p for the polymer-driven
flow, no-slip at both beads gives

    F   = [ ddot - (u_p2 - u_p1) ] / (M11 + M22 - 2 M12)
    U_c = [ F (M22 - M11) + (u_p1 + u_p2) ] / 2

In pure Stokes u_p = 0 and the mobilities depend only on the instantaneous separation, so
U_c = A(d) ddot and the net displacement over a cycle is exactly zero. That is the check.

NUMERICS
--------
Everything is spectral. Gaussian regularised deltas are applied analytically in Fourier
space -- spreading a bead force is a phase factor times exp(-eps^2 k^2 / 2), and
interpolation uses the same kernel -- so there are no grid loops in the immersed-boundary
part at all. Stokes inverts as a projection: uhat = P(k) fhat / (eta_s k^2).
"""
import time
import numpy as np


class Solver:
    def __init__(self, N=128, L=2 * np.pi, eta_s=1.0, eta_p=1.0, lam=1.0,
                 eps_s=2e-3, eps1=0.14, eps2=0.26, d0=1.0, amp=0.30):
        self.N, self.L = N, L
        self.eta_s, self.eta_p, self.lam, self.eps_s = eta_s, eta_p, lam, eps_s
        self.eps1, self.eps2, self.d0, self.amp = eps1, eps2, d0, amp

        k1 = 2 * np.pi * np.fft.fftfreq(N, d=L / N)
        self.KX, self.KY = np.meshgrid(k1, k1, indexing="ij")
        self.K2 = self.KX ** 2 + self.KY ** 2
        self.K2inv = np.where(self.K2 > 0, 1.0 / np.where(self.K2 > 0, self.K2, 1), 0.0)
        # 2/3 dealiasing for the quadratic terms in the conformation equation
        kmax = np.max(np.abs(k1))
        self.mask = (np.abs(self.KX) <= 2 / 3 * kmax) & (np.abs(self.KY) <= 2 / 3 * kmax)

        x = np.arange(N) * L / N
        self.X, self.Y = np.meshgrid(x, x, indexing="ij")
        self.reset()

    def reset(self):
        N = self.N
        self.Cxx = np.ones((N, N)); self.Cxy = np.zeros((N, N)); self.Cyy = np.ones((N, N))
        self.xc = 0.0                      # swimmer centre (x)

    # ---------------------------------------------------------------- spectral pieces
    def stokes(self, fxh, fyh):
        """uhat = P(k) fhat / (eta_s k^2); k=0 mode set to zero (no mean flow)."""
        dot = self.KX * fxh + self.KY * fyh
        uxh = (fxh - self.KX * dot * self.K2inv) * self.K2inv / self.eta_s
        uyh = (fyh - self.KY * dot * self.K2inv) * self.K2inv / self.eta_s
        return uxh, uyh

    def spread_hat(self, Fx, xb, eps):
        """Fourier transform of a Gaussian-regularised point force Fx*xhat at (xb, yc)."""
        ph = np.exp(-1j * (self.KX * xb + self.KY * (self.L / 2)))
        return Fx * ph * np.exp(-0.5 * eps ** 2 * self.K2)

    def interp(self, uh, xb, eps):
        """Value of the field at the bead, using the same Gaussian kernel."""
        ph = np.exp(1j * (self.KX * xb + self.KY * (self.L / 2)))
        return float(np.real(np.sum(uh * ph * np.exp(-0.5 * eps ** 2 * self.K2)))) / self.N ** 2

    def polymer_force_hat(self):
        """div of the polymer stress tau_p = (eta_p/lam)(C - I)."""
        c = self.eta_p / self.lam
        txxh = c * np.fft.fft2(self.Cxx - 1.0)
        txyh = c * np.fft.fft2(self.Cxy)
        tyyh = c * np.fft.fft2(self.Cyy - 1.0)
        return 1j * (self.KX * txxh + self.KY * txyh), 1j * (self.KX * txyh + self.KY * tyyh)

    # ------------------------------------------------------------------- one timestep
    def velocity_field(self, t, dd):
        """Solve the coupled constraint for (F, U_c) and return the resulting flow."""
        d = self.d0 + self.amp * np.cos(t)
        x1, x2 = self.xc - d / 2, self.xc + d / 2

        # polymer-driven flow, and its value at each bead
        pxh, pyh = self.polymer_force_hat()
        upxh, upyh = self.stokes(pxh, pyh)
        up1 = self.interp(upxh, x1, self.eps1)
        up2 = self.interp(upxh, x2, self.eps2)

        # mobilities: unit x-force at bead j, read velocity at bead i
        u1h, _ = self.stokes(self.spread_hat(1.0, x1, self.eps1), np.zeros_like(self.KX))
        u2h, _ = self.stokes(self.spread_hat(1.0, x2, self.eps2), np.zeros_like(self.KX))
        M11 = self.interp(u1h, x1, self.eps1); M21 = self.interp(u1h, x2, self.eps2)
        M12 = self.interp(u2h, x1, self.eps1); M22 = self.interp(u2h, x2, self.eps2)

        F = (dd - (up2 - up1)) / (M11 + M22 - M12 - M21)
        Uc = (F * (M22 - M11) + (up1 + up2)) / 2.0

        fxh = self.spread_hat(-F, x1, self.eps1) + self.spread_hat(F, x2, self.eps2) + pxh
        uxh, uyh = self.stokes(fxh, pyh)
        return uxh, uyh, Uc

    def dCdt(self, uxh, uyh):
        ux = np.real(np.fft.ifft2(uxh)); uy = np.real(np.fft.ifft2(uyh))
        gx = lambda h: np.real(np.fft.ifft2(1j * self.KX * h * self.mask))
        gy = lambda h: np.real(np.fft.ifft2(1j * self.KY * h * self.mask))
        Lxx, Lxy, Lyx, Lyy = gx(uxh), gy(uxh), gx(uyh), gy(uyh)

        Cxxh, Cxyh, Cyyh = (np.fft.fft2(self.Cxx), np.fft.fft2(self.Cxy),
                            np.fft.fft2(self.Cyy))
        adv = lambda h: -(ux * gx(h) + uy * gy(h))
        lap = lambda h: np.real(np.fft.ifft2(-self.K2 * h))

        dxx = adv(Cxxh) + 2 * (Lxx * self.Cxx + Lxy * self.Cxy) \
            - (self.Cxx - 1) / self.lam + self.eps_s * lap(Cxxh)
        dxy = adv(Cxyh) + (Lxx * self.Cxy + Lxy * self.Cyy) \
            + (self.Cxx * Lyx + self.Cxy * Lyy) - self.Cxy / self.lam + self.eps_s * lap(Cxyh)
        dyy = adv(Cyyh) + 2 * (Lyx * self.Cxy + Lyy * self.Cyy) \
            - (self.Cyy - 1) / self.lam + self.eps_s * lap(Cyyh)
        return dxx, dxy, dyy

    def run(self, ncycles=6, nsteps=800, verbose=False):
        """Advance with RK2; return net displacement of the final cycle."""
        T = 2 * np.pi
        dt = T / nsteps
        marks = []
        for c in range(ncycles):
            x_start = self.xc
            for n in range(nsteps):
                t = n * dt
                dd = lambda tt: -self.amp * np.sin(tt)
                ux1, uy1, U1 = self.velocity_field(t, dd(t))
                k1 = self.dCdt(ux1, uy1)
                C0 = (self.Cxx.copy(), self.Cxy.copy(), self.Cyy.copy()); xc0 = self.xc
                self.Cxx = C0[0] + dt * k1[0]; self.Cxy = C0[1] + dt * k1[1]
                self.Cyy = C0[2] + dt * k1[2]; self.xc = xc0 + dt * U1
                ux2, uy2, U2 = self.velocity_field(t + dt, dd(t + dt))
                k2 = self.dCdt(ux2, uy2)
                self.Cxx = C0[0] + 0.5 * dt * (k1[0] + k2[0])
                self.Cxy = C0[1] + 0.5 * dt * (k1[1] + k2[1])
                self.Cyy = C0[2] + 0.5 * dt * (k1[2] + k2[2])
                self.xc = xc0 + 0.5 * dt * (U1 + U2)
            marks.append(self.xc - x_start)
            if verbose:
                print(f"      cycle {c+1}: dx = {marks[-1]:+.3e}   trC = {np.mean(self.Cxx+self.Cyy):.4f}")
        return marks


if __name__ == "__main__":
    print("2-D Stokes-Oldroyd-B, asymmetric dumbbell, reciprocal stroke")
    print("De = lam (stroke frequency = 1). N=96 grid for the spike.\n")

    print("[1] CONTROL: no polymer (eta_p = 0) -> scallop theorem must give zero")
    t0 = time.time()
    s = Solver(N=96, eta_p=0.0, lam=1.0)
    m = s.run(ncycles=3, nsteps=400)
    print(f"    dx per cycle: {m[-1]:+.3e}   (expect ~0)      [{time.time()-t0:.1f}s]")

    print("\n[2] CONTROL: polymer on, but SYMMETRIC beads (eps1 = eps2) -> still zero")
    t0 = time.time()
    s = Solver(N=96, eta_p=1.0, lam=1.0, eps1=0.20, eps2=0.20)
    m = s.run(ncycles=3, nsteps=400)
    print(f"    dx per cycle: {m[-1]:+.3e}   (expect ~0)      [{time.time()-t0:.1f}s]")

    print("\n[3] THE TEST: polymer on, ASYMMETRIC beads -> does it swim?")
    t0 = time.time()
    s = Solver(N=96, eta_p=1.0, lam=1.0, eps1=0.14, eps2=0.26)
    m = s.run(ncycles=5, nsteps=400, verbose=True)
    el = time.time() - t0
    print(f"    dx per cycle (converged): {m[-1]:+.4e}")
    print(f"    cost: {el:.1f}s for 5 cycles = {el/5:.2f}s per stroke")
