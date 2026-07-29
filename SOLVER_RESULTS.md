# Taylor (1951) swimming sheet — reproduced from scratch, no CFD package

Solver: `taylor_spectral.py` (+ `richardson.py`, `dissipation.py`). Pure numpy/scipy.
Method: spectral boundary collocation. Expand the Stokes stream function in the decaying
biharmonic basis for a periodic strip,

    psi = sum_{n>=1} e^{-n y} [ (A_n + C_n y) cos(n x) + (B_n + D_n y) sin(n x) ]

impose no-slip at M points on the *actual wavy* material surface, and solve least-squares
for {A,B,C,D}_n together with the unknown rigid drift U. The mean (n=0) mode is set to
zero, i.e. the lab frame with fluid at rest at infinity; requiring a decaying solution is
what makes the sheet force-free, so U is determined without a separate force condition.

Units: k = sigma = mu = 1, so wave speed V = 1, wavelength 2*pi, and kb = the amplitude.

## Convergence

| N (modes) | U at kb=0.2 | rel. residual |
|---|---|---|
| 4 | -0.019235445606 | 1.9e-03 |
| 8 | -0.019235693436 | 5.7e-06 |
| 12 | -0.019235693438 | 1.8e-08 |
| 16 | -0.019235693438 | 6.4e-11 |
| 24 | -0.019235693438 | 3.3e-15 |

Exponential convergence; machine precision by N=24. Drift is time-independent to 1e-17
(as it must be — the traveling wave is steady in the wave frame). Cost: **3.6 ms/solve**
at N=24. The whole amplitude sweep that yields both coefficients: **0.34 s**.

## Result 1 — the swimming speed

Sign is negative: the sheet moves **opposite** to the wave, as Taylor states.

Fitting `-U/V = 1/2 (kb)^2 [1 + c (kb)^2 + ...]` and Richardson-extrapolating in (kb)^2:

| sheet | c extrapolated | exact | rel. err |
|---|---|---|---|
| inextensible (Taylor's case) | -1.187484 | **-19/16** = -1.187500 | 1.3e-5 |
| purely transverse, extensible | -0.999984 | **-1** | 1.6e-5 |

So the inextensible sheet gives

    U/V = 1/2 (kb)^2 - 19/32 (kb)^4 + ...

recovering both of Taylor's coefficients. Leading order at kb=0.01: `-U/(kb)^2 = 0.4999406`
→ 1/2.

**Discriminating finding:** the leading 1/2 is the *same* for both sheets, but the
fourth-order coefficient is not (-19/16 vs -1). Inextensibility is invisible at O((kb)^2)
because the longitudinal correction it forces is O((kb)^2) with zero time-mean; it first
bites at O((kb)^4). A numerical study that only checks the 1/2 cannot tell the two
kinematics apart — the 19/32 is the term that certifies you have Taylor's actual sheet.

## Result 2 — the rate of working (independent check)

Taylor eq (14): `W = mu sigma^2 b^2 k`. Same solver, but now exercising the pressure and
velocity-gradient fields rather than the drift:

| kb | W numeric | W/(kb)^2 |
|---|---|---|
| 0.01 | 0.000099973 | 0.999725 |
| 0.02 | 0.000399560 | 0.998901 |
| 0.05 | 0.002482871 | 0.993149 |
| 0.10 | 0.009728731 | 0.972873 |

→ 1 as kb → 0. Confirmed.

## Gotcha worth recording

The arclength inversion that builds the inextensible kinematics anchors material label
a=0 to x=0. That injects a spatially uniform, zero-time-mean longitudinal velocity m(t)
into the prescribed motion, so the solver returns `U_true - m(t)` and the leading
coefficient reads 1/4 instead of 1/2 — exactly a factor 2 off, which looks like a physics
error and is not. Adding back `mean(ux)` (or period-averaging) fixes it and makes the
drift t-independent. Any reimplementation will hit this.
