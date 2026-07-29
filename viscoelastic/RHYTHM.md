# Rhythm matters, and the optimal rhythm reverses with Deborah number

The question this project was built to answer: does a reciprocal swimmer in a fluid with memory
have a real control problem, or is the obvious stroke trivially optimal? Answer: **real**, but
the first experiment that said so was wrong, and finding out why is most of what follows.

---

## 1. The first answer was an artifact

**Setup.** Stroke `d(t) = d0 + Σ a_k cos(k t + φ_k)`, k = 1..3, every candidate rescaled to the
same actuation effort `⟨(ḋ)²⟩`. CMA-style ES, population 40 × 10 generations, 400 evaluations,
zero failures.

**Result.** Best stroke beat the plain sinusoid by **1.0342×**, clearing the 1.02 bar set in
advance. Resolution-stable: the gain held to 0.17 percentage points across 4× timestep, 1.5×
grid, and 1.5× box. Null controls exact — the winning stroke gives 0.0 with no polymer and
3.5e-18 with symmetric beads, so it was still perfectly reciprocal.

**Why it was still wrong.** Equal effort weights harmonic *k* by *k²*, so amplitude can be
shuffled between harmonics to buy a wider peak-to-peak excursion at constant effort. The winner
ran 0.97% wider. Displacement goes as amp², so:

| | gain |
|---|---|
| total measured | 1.0342× |
| a plain sinusoid stretched to the winner's excursion (**measured, not inferred**) | 1.0231× |
| residual attributable to timing | **1.0109×** |

Renormalising onto four different fairness metrics settles it:

| held equal | gain |
|---|---|
| effort ⟨ḋ²⟩ *(the pre-registered rule)* | 1.0342× |
| excursion | 1.0096× |
| shape-space path ∮\|ḋ\|dt | 1.0096× |
| **peak rate max\|ḋ\|** | **0.9895× — loses** |

The win depended on which metric I chose. That is a reparametrisation win, not a physics claim.
**Verdict: null**, consistent with the earlier small-amplitude run (1.0013×).

---

## 2. Asking the question properly

The flaw was in the parametrisation, so it gets fixed there rather than patched with another
normalisation:

```
d(t) = d0 + A·cos(θ(t)),    θ(t) = t + Σ b_k sin(k t + φ_k)
```

θ is a **monotone reparametrisation of phase**, so `cos θ` sweeps [−1, 1] exactly once per
period for any b, φ. Every candidate therefore has, *by construction and not by rescaling*:

- identical excursion (exactly 2A)
- identical shape-space path (the same segment, once out and once back)
- identical period
- still perfectly reciprocal, so pure Stokes gives exactly zero for every one

and differs **only in rhythm** — where in the stroke the swimmer hurries and where it dawdles.
`θ(t) = t` recovers the reference sinusoid exactly, reproducing dx = −1.90873e-03, which is a
free correctness check on the whole reformulation.

### The controlled pair

`b₁ = +0.5` and `b₁ = −0.5` at φ = 0 are identical on every scalar the stroke has:

| | b₁ = +0.5 | b₁ = −0.5 | agreement |
|---|---|---|---|
| excursion | 0.70000000 | 0.70000000 | exact |
| effort ⟨ḋ²⟩ | 0.07212561 | 0.07212561 | exact |
| path ∮\|ḋ\|dt † | 1.40000000 | 1.40000000 | 2e-16 |
| peak rate | 0.44160067 | 0.44160067 | 6e-17 |
| Stokes limit | 0 | 0 | both reciprocal |
| **dx / cycle** | **−2.18249e-03** | **−1.65946e-03** | **ratio 1.3152** |

† **path is not an independent control.** For a single-shape-DOF swimmer traversing its segment
once out and once back, path ≡ 2 × excursion identically — visible right there in the table as
1.40000 = 2 × 0.70000. It is a consequence of fixing the excursion, not a separate constraint,
and listing it as one implies more control than is being exercised. The genuinely independent
matched quantities are **excursion, effort, peak rate and period**.

Every metric that killed §1 is matched *exactly* here. Nothing is left to trade. The difference
is 31.5%, and it survives refinement:

| | ratio |
|---|---|
| reference (N=192, 600 steps, L=4π) | 1.3152 |
| 4× timestep | 1.3149 |
| finer grid (N=288) | 1.3152 |
| bigger box (L=6π) | 1.3144 |
| everything refined | 1.3143 |
| **spread** | **0.09 percentage points** |

Second pair (φ = −π/2): 0.8021, spread 0.22 points. `∮U_stokes` ≤ 1.2e-16 throughout.

**In a Newtonian fluid this comparison is identically zero** — rate-independence, verified here
to 1e-16. Zero → 1.32× is a qualitative transition, and unlike §1 it cannot be argued away by
choosing a different fairness metric, because there is no slack anywhere to argue about.

**Mechanism.** `θ' = 1 + b cos t` is fast through the *open* extreme and slow through the
*closed* one, so `b₁ > 0` lingers closed. Lingering closed beats lingering open. The second pair
agrees: dawdling through the closing sweep beats hurrying through it. Time spent near the closed
configuration is what generates displacement.

---

## 3. The optimal rhythm reverses at De ≈ 0.81

| De | ratio (closed/open) | winner |
|---|---|---|
| 0.05 | 0.9602 | linger **open** |
| 0.50 | 0.9512 | linger **open** |
| 0.70 | 0.9780 | linger **open** |
| 0.80 | 0.9981 | linger **open** |
| **0.809** | **1.0000** | **crossover** |
| 0.90 | 1.0203 | linger **closed** |
| 1.00 | 1.0434 | linger **closed** |
| 3.00 | 1.3145 | linger **closed** |
| 5.00 | 1.3580 | linger **closed** |
| 20.00 | 1.2800 | linger **closed** |

Not a magnitude change — a **sign change in which rhythm is better**. No fixed stroke is optimal
across the fluid, and the swimmer cannot directly observe De. That is the first thing in this
project that looks like it genuinely needs an adaptive policy rather than a one-shot
optimisation.

The crossover sits at De = 0.8–0.9, where cycle 3 is converged to 0.0%, so it is not a transient.

---

## 4. Two corrections to earlier claims

**(a) "Displacement peaks near De ≈ 3 and saturates" — WRONG. It was a transient.**

That was measured at 3–5 cycles. Cycle 3 is exact for De ≤ 2, but the error grows with De:

| De | cycle 3 | cycle 14 | error of the 3-cycle read |
|---|---|---|---|
| ≤ 2 | — | — | 0.0–0.1% |
| 3 | −2.1825e-03 | −2.2061e-03 | 1.1% |
| 5 | −2.1380e-03 | −2.2966e-03 | 6.9% |
| 10 | −1.7039e-03 | −2.3459e-03 | 27.4% |
| 20 | −1.1016e-03 | −2.4053e-03 | 54.2% |

Because the under-convergence grows with De, it manufactures a fake peak. Converged,
displacement **rises monotonically and is still rising at De = 20**. The relaxation time at
De = 20 is 20 stroke periods; three cycles could never have resolved it. This supersedes
`VALIDATED.md` §Physics and the corresponding memory note.

The error: a convergence check established at De = 3 was reused at De = 20 without re-testing —
the same species of mistake as Richardson-extrapolating along an unverified error model, which
cost this project a week earlier.

**(b) "The rhythm asymmetry must vanish as De → 0" — my reasoning was unfounded.**

Rate-independence forces the *displacement* to vanish, not the *ratio* of two displacements.
Both rhythms are O(De) at small De — measured dx/De = −2.153e-3, −2.138e-3, −2.058e-3 at
De = 0.05, 0.1, 0.2 — so the ratio is a 0/0 limit tending to a finite constant, 0.960. The data
was never in question; the prediction was. The prediction failing is what exposed the crossover.

The De → ∞ half of that prediction *was* sound (as λ → ∞ the upper-convected derivative vanishes
and C becomes path-dependent only, restoring rate-independence) — the transient in (a) was
hiding it. Converged, the ratio does turn back down: peak 1.3580 at De = 5, falling to 1.2800
at De = 20.

---

## 5. Searching the effort-constraint surface — and the De-specific optimum

Rhythm mattering is one thing; whether a rhythm can actually *beat* the sinusoid with nothing
left to trade is another. Effort is not fixed by the θ-construction (at fixed excursion, varying
effort **is** part of the timing), so it has to be matched by selection. Effort needs no PDE —
it is quadrature on the stroke — so 200,000 rhythms were screened locally in seconds and only
those already sitting on the surface `⟨ḋ²⟩ ≤ 0.06125` went to the solver. **One candidate set,
evaluated at every De**, so differences between Deborah numbers are physics and not the draw.

**Result: a rhythm beats the sinusoid by 1.4975× with every constraint matched** — and the
winner uses 0.27% *less* effort than the sinusoid, so it is not winning on actuation energy.
At De = 0.3, 65 of 180 sampled rhythms beat the sinusoid; at De = 3.0 only 3 of 180 do. The
landscape closes up as memory strengthens.

### The optimum is De-specific (each winner evaluated at every De)

| winner \ evaluated at | De=0.3 | De=0.5 | De=0.8 | De=1.5 | De=3.0 |
|---|---|---|---|---|---|
| best@De=0.3 | **1.4975** | 1.4687 | 1.3053 | 1.0600 | **0.9138** |
| best@De=1.5 | 1.2826 | 1.2703 | 1.1948 | **1.0843** | 1.0188 |
| best@De=3.0 | 1.1720 | 1.1723 | 1.1316 | 1.0687 | **1.0310** |

The diagonal dominates every column, so no fixed stroke is optimal across the fluid. The
top-right corner is the sharp claim: **the best low-De stroke scores 0.9138 at De = 3.0 —
worse than the plain sinusoid.** A fixed policy is not merely suboptimal in the wrong fluid,
it is a liability. Since De is not directly observable to the swimmer, that is a control
problem in the strict sense.

### Both claims refined (43 runs, all passing)

| | De=0.3 gain | spread | De=3.0 gain | spread |
|---|---|---|---|---|
| best@De=0.3 | 1.4974 → 1.4976 | **0.41 pp** | 0.9137 → 0.9139 | **0.02 pp** |
| best@De=1.5 | 1.2826 → 1.2827 | 0.21 pp | 1.0187 → 1.0189 | 0.01 pp |
| best@De=3.0 | 1.1719 → 1.1720 | 0.13 pp | 1.0309 → 1.0310 | 0.01 pp |

Across 4× timestep, 1.5× grid, 1.5× box, and full refinement. The sign reversal holds to **0.02
percentage points** — the tightest number in this project. Scallop-theorem control on all three
winners: **exactly 0.000e+00** with the polymer off, so every one is still strictly reciprocal.
`∮U_stokes` ≤ 4.9e-16, drift 0.00%.

Note the winning rhythm sits **exactly on the monotonicity guard** (Σ|b_k·k| = 0.9000, so
dθ/dt dips to 0.10). The constraint is binding, which means 1.4975× is a **lower bound** — the
search is reporting that the box it was given is too small.

---

## 6. Prior art — the framing is not ours, the reversal appears to be

Checked by two adversarial agents briefed to *prove the work already published*, each required
to log every query behind a negative.

**❌ The reparametrisation framing is owned, and was published 17 years ago.**
Fu, Wolgemuth & Powers, *Phys. Fluids* **21**, 033102 (2009):

> *"Any reciprocal motion h(s,t) with period T may be mapped to a strictly time-reversal
> invariant motion by a **reparametrization t₁ = F(t), where F is monotonic, F(0)=0, and
> F(T)=T**."* … *"when λ≠0, the kernel M(t,t′) **spoils reparametrization invariance** … the
> distance covered per period in a non-Newtonian fluid **depends on the rate of motion as well
> as the sequence of shapes**."*

That is §2 of this document, sentence for sentence, including a worked rhythm-only example.
Elfring & Lauga (2015) use it as the textbook derivation of the scallop theorem; Qiu et al.
(*Nat. Commun.* **5**, 5119, 2014) ran the experiment with excursion and period pinned by
hardware in a shear-thinning fluid; "pacing" is a named optimisation variable in Stokes gait
theory (Ramasamy & Hatton, *IEEE T-RO* 2019). **Cite Fu et al. as the source of the method.**

**✅ The reversal of the optimum is not in print.** No paper optimises stroke *timing* for a
single-shape-DOF reciprocal swimmer in a viscoelastic fluid, and none reports the argmax itself
moving with De. arXiv `all:"optimal stroke" AND all:"viscoelastic"` → **0 results**. The
harmful-transfer half (low-De optimum beaten by a plain sinusoid at high De) has no precedent
at all.

**The open question this answers** — Montenegro-Johnson, Smith, Smith, Loghin & Blake,
*Eur. Phys. J. E* **35**, 111 (2012), §4.3, having found the same optimal phase in Stokes and
in shear-thinning:

> *"For viscoelastic properties, this may **not** be the optimum phase difference, due to the
> dependence of the fluid stress on its deformation history."*

Posed in 2012, never executed. **The honest shape of this work: acting on Fu et al.'s 2009
observation to answer Montenegro-Johnson et al.'s 2012 open question.**

**Distinguish, do not confuse:** Riley & Lauga (2015) report a De-dependent sign flip of the
swimming *response at fixed gait* — related, not pre-empting. Singh & Choudhary
(arXiv:2604.27348, 2026) report a reversal driven by **Kelvin–Voigt elasticity in the swimmer's
body, not the fluid** — identical phenomenology, different mechanism, and a referee will raise it.

**Unresolved:** Asghar et al., *Chinese J. Phys.* **96**, 664 (2025) — abstract unobtainable
behind ScienceDirect on two separate attempts. Title-level risk; needs institutional access.

**Correction to an earlier statement in this file's own reasoning:** "in Stokes, timing cannot
matter" is wrong as stated. Timing is irrelevant to *displacement* but decisive for *cost* —
which is exactly why the geometric-mechanics community optimises pacing in Stokes.

---

## 7. Method notes

**Disconnect-proof long runs.** Three optimisation runs died to client disconnects because the ES
driver lived in `@app.local_entrypoint()` — `--detach` keeps the remote app alive but the workers
idle with nobody to tell them what to evaluate next. Fix in `optimize_detached.py`: driver loop
moved into an `@app.function` so it runs server-side, checkpoints to a `modal.Dict` readable from
anywhere, launched with `--detach`. The 10-generation run then completed untouched, and
reproduced the killed run bit-for-bit (same seed, deterministic solver).

**Prefer sampling to evolution when the space is small.** ES generations are sequential:
wall-clock = generations × per-eval, regardless of worker count. The Pareto study samples the
same space in **one parallel wave**.

**The lesson that keeps repeating.** Every wrong answer in this project was caught by a quantity
where theory makes a sharp prediction — the amplitude exponent, the Stokes-limit zero, the
scallop theorem, cycle-to-cycle drift — and never by the convergence checks I chose to run.
Grid convergence passed at 0.0% while the answer was wrong by 500×; the ES reported
`=> TIMING ASYMMETRY WINS` while measuring an amplitude artifact. **Build the exact test first,
and prefer the test you cannot talk your way out of.**

---

## 8. The dimensionless group — validated out-of-sample

De_c ≈ 0.81 is one number for one swimmer. Varying the parameters moves it a lot: rhythm
strength by 8.9%, and amplitude / asymmetry / confinement / polymer fraction by 34–44% each.
On its own that makes the reversal look like a parameter-specific curiosity.

**The correction.** De = λω compares the fluid's memory against the stroke's *nominal*
frequency. But a rhythm-modulated stroke does not move at its nominal frequency — that is the
entire point of it. The fluid responds to the rate at which it is *actually* deformed. So use

    De* = De · ⟨(dθ/dt)²⟩ ,   which for θ = t + b sin t is exactly De · (1 + b²/2)

`1 + b²/2` is the analytic mean-square of `1 + b cos t` (⟨cos²⟩ = ½). **Nothing is fitted; there
is no free parameter.**

| b | De_c | ⟨(dθ/dt)²⟩ | product |
|---|---|---|---|
| 0.25 | 0.883 | 1.0312 | 0.9106 |
| 0.40 | 0.841 | 1.0800 | 0.9083 |
| 0.50 | 0.808 | 1.1250 | 0.9090 |
| 0.65 | 0.746 | 1.2112 | 0.9036 |
| 0.80 | 0.684 | 1.3200 | 0.9029 |
| | | **spread** | **0.34%** |

### Two tests, both passed

**[A] Extrapolation.** Two rhythm strengths outside the fitted range, predicted in advance:

| b | predicted | measured | error |
|---|---|---|---|
| 0.15 | 0.8968 | 0.9005 | **+0.4%** |
| 0.88 | 0.6538 | 0.6515 | **−0.3%** |

**[B] Factorisation.** A b-sweep at other operating points must collapse onto its *own*
constant — same law, different intercept:

| setting | raw De_c range | collapsed spread | K |
|---|---|---|---|
| baseline (A=0.35, ℓ=0.5) | 32% | **0.35%** | 0.9070 |
| A = 0.28 | 26% | **0.90%** | 0.8262 |
| ℓ = 0.8 | 21% | **0.79%** | 1.1563 |

412 runs across the two studies, 0 failures, `∮U_stokes` ≤ 1.9e-16.

### What it does and does not claim

**Does:** the *rhythm* dependence of the reversal point factorises out exactly as the
mean-square rate of shape change. For any stroke that is not uniform in time, the standard
Deborah number is the wrong comparison and this is the corrected one.

**Does not:** explain K. Amplitude, asymmetry, confinement and polymer fraction all move it by
34–44% and are absorbed into the constant. This is not a universal collapse and should not be
presented as one.

This is the more portable result. The reversal is a phenomenon in one system; a corrected
dimensionless group is a tool that applies to any time-modulated stroke in a fluid with memory.

---

## 9. ⚠️ The collapse is family-specific — the universal claim is RETRACTED

§8 presented `De_c · ⟨θ'²⟩ = K` as though ⟨θ'²⟩ were the governing group for any rhythm. It is
not. Two independent lines say so.

### The prediction that made it testable

⟨θ'²⟩ = 1 + ½Σ(k b_k)² is phase-independent and depends only on the second moment, so the law
predicts: **different modulation shapes with the same ⟨θ'²⟩ must reverse at the same De_c.**
Nine cases were run with De_c predicted in advance.

### Result: it fails

| modulation | is ±b the right pairing? | ratio over De = 0.5→1.1 | verdict |
|---|---|---|---|
| 1st harmonic, φ=0 | ✅ mirror images (err 4e-16) | 0.951 → 1.067 | crosses at **0.8085** vs predicted 0.8061 — **0.3%** |
| 3rd harmonic, φ=0 | ✅ mirror images (err 4e-16) | 1.079 → **1.092, flat** | **never crosses. No reversal at all.** |
| 2nd harmonic (×4) | ❌ self-mirror — invalid test | 0.48–0.78 | comparison is meaningless |
| φ = π/4, π/2 | ❌ not mirror-related — invalid | 1.6–4.2 | comparison is meaningless |

**Most of the test was badly designed.** Under t → π−t the shape reflects about d₀ as
`d(π−t; b) = 2d₀ − d(t; −b)` only for ODD modulation harmonics with φ=0. For even harmonics the
rhythm is *self*-mirror, so ±b are not opposite strategies and there is no reason for the ratio
to approach 1. Seven of nine cases were invalid. This should have been checked before running.

But the 3rd-harmonic case *is* a valid pairing, and it shows no reversal anywhere. **One valid
counter-example is enough.**

### The reduced theory said so first

`theory_analysis.py` (Fourier algebra, no PDE) predicted the failure independently:
De_c spread 3.88% under the collapse (vs 0.34% in the PDE's own family), no crossing for 2nd/3rd
harmonic modulation, and phase-invariance broken at 77% spread. Theory and simulation agree the
law is family-specific.

### What stands

- `De_c(b) · (1 + b²/2) = K` **within the family θ = t + b sin t** — out-of-sample to ±0.4%,
  factorising across amplitude and confinement (§8). Real, useful, and narrow.
- **Not** a universal dimensionless group. Do not present it as one.

---

## 10. The mechanism, derived

Why a reversal exists at all is now analytic. At leading order the polymer stress is the strain
rate through a first-order lag, `ŝₙ = i n ĝₙ / (1 + i n De)`, and the swimmer's velocity is that
stress times a shape-dependent coupling. Expanding the coupling about the mean shape:

```
∮ s dt      = 0        a CONSTANT coupling swims nowhere
∮ g s dt    = P(De)    the PAIR term
∮ g² s dt   = Q(De)    the TRIPLE term
```

**The pair term cannot produce a reversal, provably.** Jacobi–Anger gives `ĝₙ = J_{n−1}(b)`, and
`J_k(−b) = (−1)^k J_k(b)`, so the magnitudes |ĝₙ| are identical for ±b. P depends only on
|ĝₙ|² — measured difference **exactly 0.0e+00** at b = 0.3, 0.5, 0.8. At this order the two
rhythms swim identically.

**The triple term flips sign exactly** (`Q(+b) = −Q(−b)` to machine precision) and crosses zero.
It is a three-wave correlation, sensitive to the *phases* of the harmonics rather than their
magnitudes.

**So the reversal is the sign change of a three-wave correlation** — and this is why the 0-D toy
could never produce one: the toy had only the pair term. It also explains why the effect needs
both fluid memory (to make the lag) and a shape-dependent coupling (to make the triple term
exist).
