# Solver validated. Optimisation is now a 9–34 minute job, not a week.

## The fix: Brinkman screening

The blocker was the periodic box. A force-free swimmer's 2-D Stokes far field is a stresslet
~cos(2θ)/r²; summed over a lattice of images the angular factor makes contributions partly
cancel, so the sum converges **slowly and non-monotonically** (measured: −28%, then +19%).
That is also why Richardson extrapolation in 1/L² made things *worse* — I extrapolated along
an error model that was wrong.

Replacing Stokes with **Brinkman** — `(k² + 1/ℓ²)` instead of `k²`, so flow decays as
`exp(−r/ℓ)` — kills the images exponentially. One line of code.

| screening ℓ | amplitude exponent (theory: **2.000**) | box spread |
|---|---|---|
| **0.5** | **1.9944** | **5.3%** (box2→box3 only **0.27%**) |
| 1.0 | 2.0026 | 22.6% |
| 2.0 | 2.0124 | 51.9% |
| none (pure Stokes) | **0.9895** | 33–146%, non-monotonic |

Box spread grows monotonically with ℓ, exactly as the image picture predicts. **Signal is also
200× larger** (−2.9e-5 vs +1.3e-7), so everything is cheaper to resolve.

**This is physics, not a numerical hack.** Brinkman describes a confined film or porous medium,
and ℓ = 0.5 against a swimmer of length 1 means confinement comparable to the body — closer to
the biology than an infinite bath, with directly relevant literature already in the sweep
(Iqbal, Penington, Thomas & Koens, *"A Taylor swimming sheet under a finite Brinkman layer"*,
arXiv:2507.16125).

## Six exact tests, all passing — including re-run under the new operator

Screening changes the Green's function, so the controls were **re-verified**, not assumed:

| test | result |
|---|---|
| scallop theorem (no polymer), Brinkman | **exactly 0.0** |
| symmetric beads + polymer, Brinkman | 9.6e-19 |
| scallop theorem, pure Stokes | −4.1e-17 |
| translation invariance | identical to 7 digits |
| bead-swap antisymmetry | sum = 3e-18 |
| `∮U_stokes` diagnostic | 1.6e-17 |

Plus: cycle-converged (0.0% drift over cycles 3–6), grid-converged (N 96→128: 0.0%).

## Physics

**Deborah sweep** (amp = 0.10, ℓ = 0.5): displacement rises monotonically and **peaks near
De ≈ 3, then saturates** (De=3: −1.527e-4; De=5: −1.524e-4).

> ### ❌ RETRACTED — the peak and the plateau were both transients. See `RHYTHM.md` §4a.
>
> This sweep ran at 5 cycles. Cycle 3 is exact for De ≤ 2, but the under-convergence *grows
> with De* — 1.1% at De=3, 6.9% at De=5, 27.4% at De=10, 54.2% at De=20 — which manufactures
> a fake peak followed by a fake decay. At 14 cycles the displacement **rises monotonically and
> is still rising at De = 20**. At De = 20 the relaxation time is 20 stroke periods; three to
> five cycles could never have resolved it.
>
> The mistake was reusing a convergence check established at De = 3 at values 7× larger without
> re-testing it. The reasoning below about η_p/λ versus `C − I` was constructed to explain a
> plateau that does not exist — a fitted story for an artifact.

⚠️ **This supersedes the 0-D toy, which predicted De = 1 with decay at large De.** The toy's
Maxwell element sends stress → 0 as λ → ∞; in the PDE the prefactor η_p/λ falls but `C − I`
grows because nothing relaxes it, and the two effects cancel into a plateau. The toy was a
good de-risking tool — it correctly predicted the mechanism and the two necessary
ingredients — but **its quantitative De prediction did not survive contact with the PDE.**

**Asymmetry sweep:** exactly zero when symmetric (1.4e-18), then roughly linear and
**saturating** — fitted exponent 0.830 over Δε ∈ [0.04, 0.16].

## Cost

Measured at N=192 (L=4π), nsteps=800, 5 cycles: **43 s per stroke**, 214 s per evaluation.

| configuration | per eval | 960 evals (CMA-ES, pop 24 × 40 gen) | wall-clock @100 parallel |
|---|---|---|---|
| as measured | 214 s | 57 CPU-h | **34 min** |
| 3 cycles (converged by 3) | 129 s | 34 CPU-h | **21 min** |
| + N=128 | 57 s | 15 CPU-h | **9 min** |

Against the spike's honest estimate of ~25 min *per stroke* and a week per optimisation run.

## Status

**Answered — see `RHYTHM.md`.** Asymmetric *amplitude* content does not beat the sinusoid: the
optimiser's 1.0342× decomposed into 2.31% excursion + 1.09% timing and lost under equal peak
rate. Asymmetric *rhythm* does, decisively: at identical excursion, effort, path, peak rate and
period, reversing the rhythm changes displacement by **31.5%** (converged to 0.09 percentage
points), and the optimal rhythm **reverses at De ≈ 0.81**.
