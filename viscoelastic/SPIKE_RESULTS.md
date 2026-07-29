# Two-day spike: 2-D Stokes–Oldroyd-B dumbbell. Physics ✅, cost estimate ❌ by ~500×.

`spike2d.py`. The spike did its job: it confirmed the mechanism in a real PDE **and** found
that my cost estimate was wrong by nearly three orders of magnitude, along with exactly why.

---

## What worked

**The controls are machine-precision zero.** This is the important one — it says the
formulation is right, not just plausible.

| control | Δx per cycle | |
|---|---|---|
| polymer off (`η_p = 0`) | **−4.1e-17** | scallop theorem, in a full PDE solve |
| polymer on, **symmetric** beads | **+4.6e-18** | asymmetry requirement, confirmed in 2-D |
| polymer on, **asymmetric** beads | **−1.56e-05** | **it swims** |

The second row independently reproduces the toy model's prediction that memory alone is
insufficient — you need configuration-dependent coupling too. Two completely different
models, same non-obvious requirement.

**Grid convergence is clean:** N = 96 → 128 changes the answer by **0.0%**. The Gaussian
regularised deltas are applied analytically in Fourier space, so the beads are spectrally
resolved with no grid loops anywhere in the immersed-boundary part.

**It reaches a periodic steady state** and stays there — cycles 4 through 8 agree to four
digits, after a large first-cycle startup transient (which flips sign, as it should).

---

## What broke: the signal is ~1e-7 and *three* convergence parameters must be tight at once

I first measured **2.9 s per stroke** and reported it. That number was contaminated by
three separate under-resolutions, all of which happened to be invisible in the grid check.

### 1. Periodic images converge only as 1/L²

A force-free swimmer's 2-D Stokes far field is a stresslet ~1/r². Summed over a periodic
lattice that converges, but slowly. Holding `dx` fixed and enlarging the box:

| L/2π | N | L/d | Δx per cycle | change |
|---|---|---|---|---|
| 1 | 96 | 6.3 | 5.39e-07 | — |
| 2 | 192 | 12.6 | 3.00e-07 | **+80%** |
| 3 | 288 | 18.8 | 3.68e-07 | +18.6% |
| 4 | 384 | 25.1 | 4.00e-07 | +8.0% |

Errors roughly halve per box doubling, consistent with 1/L². **My original L = 2π box was
~25% wrong and on the wrong side.** Need L/d ≳ 25, i.e. N ≈ 384.

### 2. Time-integration error does not shrink with the signal

RK2 with an explicit `−C/λ` relaxation term. At amp = 0.2:

| nsteps | Δx | change |
|---|---|---|
| 400 | 4.42e-07 | — |
| 800 | 5.44e-07 | **+18.7%** |
| 1600 | 5.70e-07 | +4.6% |

The 400-step runs — which everything above used — carry ~20% error.

### 3. Consequence: the amplitude law never came out clean

Theory demands Δx ~ amp² as amp → 0. Measured exponent:

- L = 2π, nsteps = 400: **1.909**
- L = 6π, nsteps = 400: **1.608** ← bigger box made it *worse*, which is how I knew images weren't the only cause
- L = 2π, Richardson-extrapolated in dt: **1.739** overall, but **1.95 on the two smallest amplitudes**

The data is consistent with `Δx = c₂·amp² + c₄·amp⁴` with a strong negative quartic
(`c₂ ≈ 6.1e-5`, zero crossing near amp ≈ 0.4) — but I could not converge all three of
{dt, L, amp} simultaneously to prove it at reasonable cost.

**Honest cost for a number I would put in a paper:** N = 384, nsteps ≥ 1600, 6 cycles
≈ **25 minutes per stroke.** At ~400 evaluations, one optimisation run is **a week**.
That is not viable.

⚠️ **Every physics number in the earlier run is therefore provisional** — the De sweep, the
amplitude scaling, the asymmetry trend. They were measured at L = 2π / nsteps = 400 and must
be redone. In particular the "peak at De = 4" is almost certainly an artefact: image
contamination grows with De, because polymer stress advects further before relaxing.

---

## Three fixes, in order of leverage

**1. IMEX time integration (biggest, easiest win).** The `−C/λ` relaxation is what forces
the tiny timestep. Treating it implicitly — it is linear and diagonal, so this is nearly
free — should buy ~10× in dt. This is standard and should have been in the first version.

**2. Kill the images: wall-bounded or free-space.** Walls screen hydrodynamic interactions
**exponentially** instead of algebraically, so L/d ~ 5 would suffice instead of 25 — roughly
**25× cheaper**. And it is *better physics*: sperm swim near walls, and confined viscoelastic
swimming is closer to the biology we are motivating with. This turns a numerical problem into
a stronger problem statement.

**3. Stop working at small amplitude.** The signal scales as amp², so amp = 0.3 gives **100×**
the signal of amp = 0.05. The small-amplitude limit was a *validation* exercise, not the
science — Thomases & Guy's own framing is that *"high amplitude strokes in strongly elastic
flows lead to a qualitatively different regime."* Validate once at small amplitude, then work
where the signal is large.

Together: 10× (IMEX) × 25× (walls) ≈ **250×**, taking 25 min/stroke to roughly **6 s/stroke**.
That makes an optimisation run an overnight job rather than a week.

---

## Verdict

**Do not abandon; do not proceed to optimisation yet.** The mechanism is real and the solver
is provably correct — the two machine-precision controls are strong evidence. But the naive
implementation is ~500× too slow for a search loop, and I know precisely why.

**Next step is a targeted solver rewrite** (IMEX + wall-bounded), then re-run the De sweep and
the amplitude law before any optimisation. That is days of work, not weeks, and it is exactly
the kind of thing a spike is supposed to surface before it becomes a month of wasted compute.

**Meta-note worth keeping:** the first cost figure I reported, 2.9 s/stroke, was wrong by
~500× and *looked* fine — the grid-convergence check passed at 0.0%, which gave false
confidence. The tell was the amplitude exponent, a quantity where theory makes a sharp
prediction. **Convergence in the parameter you happen to test is not convergence.**
