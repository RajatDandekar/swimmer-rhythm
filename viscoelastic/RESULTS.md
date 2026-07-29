# Step 0 — hours-scale de-risking. Both gates PASSED.

Before committing to a 2-D Stokes–Oldroyd-B solver, two questions had to be answered:
**(1) does the mechanism exist at all?** and **(2) is there anything non-trivial to optimise?**
A "no" to either would have killed the project. Both came back yes, and the second one
told us something useful about where to aim.

Run: `python toy0d.py` and `python toy_optimize.py` (numpy + scipy only, seconds).

---

## The model

One shape degree of freedom `ξ(t)`. **With one DOF every periodic stroke is reciprocal by
construction** — you must return the way you came — which is exactly why Purcell's scallop
is the cleanest possible probe.

```
Stokes (no memory):   ẋ = A(ξ) ξ̇
with memory:          ẋ = A(ξ) ξ̇ + C(ξ) s
polymer stress:       De · ds/dτ = −s + dξ/dτ        (Maxwell relaxation)
```

`De = λω` — relaxation time over stroke time. The Stokes term contributes
`∮A(ξ)ξ̇ dt = ∮A(ξ)dξ = 0` for **any** closed 1-D path, because `A` depends on
instantaneous shape only. That is the scallop theorem in one line, and it is the 1-D case
of the area law measured in `../solver/gait.py` (a 1-D loop encloses no area).
**So every micron of motion below is attributable to memory. Nothing else can contribute.**

The stress equation is linear in `s` even when `C` is nonlinear, so `s` is obtained
*exactly* by Fourier transform — no time stepping, no transient to discard.

---

## Gate 1 — the mechanism is real, and needs exactly two ingredients

| case | Δx per cycle | |
|---|---|---|
| De = 0 (no memory), C(ξ) = ξ | **0.000e+00** | scallop theorem, exactly |
| De = 1 (memory), C(ξ) = 1 (constant) | **0.000e+00** | memory alone is not enough |
| De = 1 (memory), C(ξ) = ξ | **1.571** | both → **it swims** |

The middle row is a real prediction, not a nuisance: integrating the stress equation over
one period gives `∮s dτ = 0`, so a constant coupling contributes exactly nothing.
**Memory *and* configuration-dependent coupling are both necessary** — which is precisely
the geometric asymmetry an asymmetric dumbbell supplies.

**Validation.** Numerics match the closed form
`Δx = 2π·De·Σₙ n²|ξ̂ₙ|²/(1+n²De²)` to **1e-16** across De ∈ [0, 20], and both limits
vanish as they must (De→0: fluid forgets instantly; De→∞: fluid never relaxes).

**Δx peaks at De = 1, exactly** — matching Teran, Fauci & Shelley (*PRL* 104:038101,
2010), who report velocity and efficiency *"peaking for Deborah numbers near one."*
An independent consistency check against the literature.

---

## Gate 2 — the optimum is non-trivial, and the analytic control case proves the search works

**Linear coupling C(ξ) = ξ → the sinusoid is provably optimal.** Maximising
`Σₙ n²|ξ̂ₙ|²·De/(1+n²De²)` at fixed effort means maximising a weighted average of a gain
that strictly decreases in `n`, so all effort goes to `n = 1`. The optimiser, given 25
restarts and free rein over 3 harmonics, returns **gain = 1.0000, asymmetry = 0.000** at
every De. *The search correctly finds nothing — which is how we know it isn't broken.*

**Nonlinear coupling C(ξ) = ξ + c₂ξ² → timing starts to matter.** At fixed effort:

| De | sinusoid | optimised | gain | asymmetry |
|---|---|---|---|---|
| 0.05 | 0.1567 | 0.2326 | **1.484×** | 0.019 |
| 0.10 | 0.3110 | 0.4538 | 1.459× | 0.036 |
| 0.30 | 0.8647 | 1.1302 | 1.307× | 0.073 |
| 0.70 | 1.4759 | 1.6920 | 1.146× | 0.067 |
| **1.00** | 1.5708 | **1.7391** | 1.107× | 0.054 |
| 2.00 | 1.2566 | 1.3481 | 1.073× | 0.030 |
| 10.0 | 0.3110 | 0.3298 | 1.060× | 0.006 |

**There is a real search problem.** The winning stroke is dominantly first-harmonic with a
~18% second harmonic at a non-zero relative phase — an asymmetric, fast-one-way profile,
not a sinusoid.

---

## 🎯 The finding that matters for the build

**The relative payoff from optimising is largest at LOW De (1.48× at De = 0.05), while
absolute speed peaks at De ≈ 1.** Both regimes of interest sit at **De ≤ ~2.**

That is unexpectedly good news, because it puts the whole project **below the
high-Weissenberg regime** — the numerical instability I had flagged as the main technical
risk. Recall from the prior-art sweep:

- Kuron et al. (*EPJ E* 44:1, 2021), LB Oldroyd-B with **moving boundaries**: max **Wi = 1**
- Rempfer et al. (arXiv:2509.01327), fast FFT Stokes–Oldroyd-B: reached **Wi ≈ 1.1**
- Thomases & Guy, 2-D IB Stokes–Oldroyd-B swimmer: **De 0–5**

All three were previously logged as *limitations*. At De ≤ 2 they are **sufficient**.
Log-conformation, Cholesky factorisation and heavy artificial stress diffusion may not be
needed at all — they are high-Wi machinery, and we do not need high Wi.

---

## Honest caveats

- `C(ξ) = ξ + c₂ξ²` is a **stand-in**. The real coupling comes from the actual
  hydrodynamics. The toy establishes the *structure* — linear ⇒ trivial, nonlinear ⇒
  non-trivial — not the magnitude. **The 1.48× is not a prediction for the real system.**
- The toy has no spatial fields, so it cannot say anything about how much of the
  conformation field a policy would need to observe. That question needs the 2-D solver.
- Gains rise as c₂ rises (1.12× at c₂=0.3 → 1.31× at c₂=0.6, at De=0.3), so the real
  magnitude hinges on how nonlinear the true coupling is — currently unknown.

## Verdict

Both gates passed, and the target regime is **De ≈ 0.1–2** — comfortably inside what
published solvers already reach. **Proceed to the two-day feasibility spike:** simplest
working 2-D Stokes–Oldroyd-B with two immersed spheres, measure wall-clock per stroke,
confirm it moves.
