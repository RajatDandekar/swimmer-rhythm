# The rhythm reversal, reproduced in Julia

A from-scratch **Julia** re-implementation of the spectral Stokes/Brinkman–Oldroyd-B solver behind
the paper *"The optimal stroke rhythm of a reciprocal microswimmer reverses with fluid memory"*
(Dandekar, Dandekar & Panat, Vizuara Research 2026). It exists to reproduce the central result in a
second language and a second FFT library, as an independent check on the NumPy original.

**The result it reproduces.** A two-bead reciprocal swimmer in a viscoelastic fluid has an optimal
stroke *rhythm* — where in the cycle it hurries and where it dawdles — and that optimum **reverses**
at a critical Deborah number **De_c ≈ 0.81**: below it the swimmer should linger *open*, above it it
should linger *closed*. Holding the shape path, excursion and period fixed, only the rhythm varies.

Everything is `Float64` and depends only on **FFTW** for the transforms; the time stepping,
spectral Stokes/Brinkman solve, immersed regularised beads, and upper-convected Maxwell update are
all written out explicitly. `ViscoelasticSwimmer.jl` is a faithful, line-by-line port of
`../viscoelastic/solver2.py`.

## Files

| file | what it does |
|---|---|
| `ViscoelasticSwimmer.jl` | the solver: `Swimmer`, `run_cycles!`, `warp_stroke` |
| `smoke.jl` | correctness checks — the scallop theorem to round-off, and Julia-vs-NumPy displacements |
| `reversal.jl` | sweeps the Deborah number for both rhythms and locates the crossover `De_c` |
| `plot_reversal.jl` | draws `julia_reversal.png` from the sweep output |

## Run it

```bash
cd julia
julia --startup-file=no --project=. -e 'using Pkg; Pkg.instantiate()'   # one-time
julia --startup-file=no --project=. smoke.jl                            # ~4 min: validation
julia --startup-file=no --project=. -t auto reversal.jl                 # the De sweep -> De_c
julia --startup-file=no --project=. plot_reversal.jl                    # -> julia_reversal.png
```

(`-t auto` runs the Deborah-number sweep across threads. Use `--startup-file=no` to skip any local
Julia startup configuration.)

## What we get (this is the reproduction)

Sweeping the Deborah number for the two mirror rhythms (`reversal.jl`, N=192, nsteps=600):

```
  De     open (b1=-0.5)  closed (b1=+0.5)  ratio|c|/|o|  winner   maxΔ vs NumPy
  0.50  -9.4494e-04    -8.9881e-04     0.9512   OPEN     1.2e-10
  0.60  -1.0816e-03    -1.0402e-03     0.9617   OPEN     4.1e-10
  0.70  -1.1993e-03    -1.1729e-03     0.9780   OPEN     9.7e-10
  0.80  -1.2983e-03    -1.2958e-03     0.9981   OPEN     1.8e-09
  0.90  -1.3802e-03    -1.4082e-03     1.0203   CLOSED   2.9e-09
  1.00  -1.4467e-03    -1.5095e-03     1.0434   CLOSED   4.1e-09
  1.20  -1.5424e-03    -1.6799e-03     1.0891   CLOSED   6.8e-09
  1.50  -1.6214e-03    -1.8657e-03     1.1507   CLOSED   1.0e-08
  2.00  -1.6679e-03    -2.0497e-03     1.2289   CLOSED   1.3e-08

  ⇒ crossover  De_c ≈ 0.809   (independent NumPy search gave 0.81)
  agreement with NumPy: max relative difference over all points = 1.3e-08
  scallop residual across all runs: max |∮U_stokes| = 1.7e-16
```

- **The reversal is reproduced.** The linger-open rhythm wins for `De ≤ 0.8`; the linger-closed
  rhythm wins for `De ≥ 0.9`. The speed ratio crosses unity at **De_c ≈ 0.809**, matching the
  independent NumPy search value of 0.81.
- **Agreement with NumPy to 8 significant figures.** Across all 18 (De, rhythm) points the Julia
  net displacement differs from `../viscoelastic/crossover_results.json` by at most `1.3e-8`
  relative — a genuine cross-language, cross-FFT-library check, not a shared code path.
- **The scallop theorem, to round-off.** The analytic Stokes/polymer split makes
  `∮ U_stokes dt ≈ 1.7e-16` over a closed stroke, exactly as in the original.

`plot_reversal.jl` draws this as `julia_reversal.png`.

## What "reproduced" means here

Same physics, independent code: the FFT algebra, the analytic Stokes/polymer velocity split, the
RK2 update and the 2/3 dealiasing are all re-derived in Julia, with FFT conventions matched to
NumPy (`fft` ≡ `fft2`, `ifft` ≡ `ifft2`). No part of the Python is called.

Project: <https://github.com/RajatDandekar/swimmer-rhythm> · site: <https://swimmer-rhythm.vercel.app>
