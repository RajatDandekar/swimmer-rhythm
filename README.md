# A swimmer that cannot move in water — and the rhythm that reverses

**A 2012 open question in microswimmer hydrodynamics, run for the first time.**

Purcell's scallop theorem says a swimmer with a single shape degree of freedom cannot move at
low Reynolds number: it retraces its shapes in reverse and its net displacement is *exactly*
zero. Fluid memory (viscoelasticity) breaks that argument, and such a swimmer can move — known
since 2009.

The open question was whether the **rhythm** matters: not the path, not the amplitude, just
*when* the swimmer hurries and when it dawdles. Montenegro-Johnson, Smith, Smith, Loghin & Blake
wrote in 2012 that in a viscoelastic fluid this "may not be the optimum phase difference, due to
the dependence of the fluid stress on its deformation history," and that someone should check.

Nobody did. This repository is the answer.

**→ [Read the write-up, with figures and an interactive simulation](https://swimmer-rhythm.vercel.app)**

---

## The result

**1. Rhythm alone changes swimming speed by 31.5%.** Two strokes with *identical* excursion,
actuation effort, peak rate and period — differing only in where the swimmer lingers — differ by
a third in speed. Converged to 0.09 percentage points across four independent refinements. In a
Newtonian fluid the same comparison is identically zero (verified to 1e-16).

**2. The optimal rhythm reverses.** Below a critical Deborah number the swimmer should dawdle
while *open*; above it, while *closed*. Not a shift — a sign change in which strategy wins.
Crossover at De ≈ 0.81, converged to 0.02 percentage points.

**3. The wrong-fluid champion is worse than useless.** A rhythm optimised for a short-memory
fluid scores **0.9138×** in a long-memory fluid — beaten by the plain, unoptimised stroke. Being
highly optimised for the wrong fluid is an active handicap, not merely suboptimal.

Because the Deborah number is not locally observable to the swimmer, this is a genuine adaptive
control problem rather than a one-shot optimisation.

## Verified three independent ways

| | |
|---|---|
| **Numerically** | 2-D spectral Stokes/Brinkman + Oldroyd-B with immersed asymmetric beads. ~1,000 PDE solves across refinement ladders, parameter sweeps, and out-of-sample tests. |
| **Analytically** | Fourier algebra, no solver. The cycle integral splits into a *pair* term and a *triple* term. Since `Jₖ(−b) = (−1)ᵏ Jₖ(b)`, flipping the rhythm leaves every `\|ĝₙ\|` unchanged — so the pair term is **provably identical** for both rhythms and cannot reverse anything. The triple term flips sign exactly. **The reversal is a three-wave correlation changing sign.** |
| **By reinforcement learning** | A 65-parameter numpy policy (REINFORCE, no torch) given only a scalar reward and no equations learns the rhythm; trained separately at each fluid it learns **opposite strategies**, flipping at the same crossover. Two acts: a *naive* "go far" reward makes the agent game effort and linger closed everywhere (the amplitude trap); only an *energy-budgeted* reward recovers the reversal. |

All three routes agree on the mechanism — and all agree on its limits.

The RL result closes the loop the project opened with: in a Newtonian fluid this MDP is
**degenerate** (the scallop theorem leaves no hidden state, so every policy scores zero and there
is nothing to learn). Fluid memory is precisely what makes it a real learning problem — memory
turns an unlearnable problem learnable.

The algebra also explains a loose end: an early 0-D toy model stubbornly refused to produce a
reversal. It only ever had the pair term.

**What sets the critical point.** The reduced theory locates the crossover only approximately
(De ≈ 0.61 vs the full 0.81) because it discards the near-field stress structure. Resolving the
field directly (`mechanism_deep_modal.py`) shows the mechanism: the stored-stress *difference*
between the two rhythms oscillates in sign through the cycle — the linger-closed rhythm builds
excess stress during the opening phase, linger-open during the closing phase. The finite
relaxation time decides how much of each survives to propel; at De_c the two integrate to
equality. A definite physical balance that lives in the full field — which is why the scalar
theory can only approximate it.

## What is *not* claimed

The reparametrisation framing is **not ours**. Fu, Wolgemuth & Powers (*Phys. Fluids* **21**,
033102, 2009) state the monotone phase reparametrisation verbatim, observe that memory spoils
reparametrisation invariance, and give a worked example. We use their method and cite it. That
rhythm *can* matter has been in print for 17 years.

We also **retracted a stronger claim** during this work. A scaling law `De_c · ⟨θ′²⟩ = K` holds
well within the family `θ = t + b sin t` — out-of-sample to ±0.4%, factorising across amplitude
and confinement — and we initially presented it as a general dimensionless group. It is not.
Third-harmonic modulation is a valid comparison and shows no reversal at all. The reduced-order
theory predicted that failure before the simulations confirmed it. See
[`viscoelastic/RHYTHM.md`](viscoelastic/RHYTHM.md) §9.

Two further retractions are documented there: an optimiser "win" of 1.0342× that turned out to
be 2.31% wider excursion rather than better timing, and a "displacement peaks at De ≈ 3" result
that was a convergence artifact — three cycles is exact at De = 2 and 54% wrong at De = 20.

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r viscoelastic/requirements.txt
cd viscoelastic

python3 theory_analysis.py        # the analytic mechanism — pure numpy, ~1 second, no solver
python3 rhythm_modal.py           # same path, different rhythm — the 31.5%
python3 crossover_modal.py        # locate the reversal, with cycle convergence
python3 constraint_modal.py       # matched-energy search across five fluids
python3 winners_verify_modal.py   # refine every headline number
python3 rl_modal.py               # LOCAL: validate the RL env against the crossover data
modal run --detach rl_modal.py::controlled   # the agent learns the reversal from reward
```

The solver (`viscoelastic/solver2.py`, ~160 lines) needs **only numpy**. No commercial CFD
package is used anywhere. The `*_modal.py` scripts fan sweeps across cloud CPUs via
[Modal](https://modal.com) purely for wall-clock; each runs locally if you replace `.map()`
with a loop.

## Independent reproduction in Julia

The whole solver is re-implemented from scratch in **Julia** (only FFTW) in [`julia/`](julia/), as
a cross-language, cross-FFT-library check. It reproduces the reversal — **De_c ≈ 0.809** vs the
NumPy value 0.81 — and matches the NumPy net displacements to **8 significant figures** (max
relative difference `1.3e-8` over all 18 Deborah/rhythm points), with the scallop theorem holding
to `∮U_stokes ≈ 1.7e-16`. See [`julia/README.md`](julia/README.md) and `julia/julia_reversal.png`.

```bash
cd julia
julia --startup-file=no --project=. -e 'using Pkg; Pkg.instantiate()'
julia --startup-file=no --project=. -t auto reversal.jl      # -> De_c and the NumPy comparison
```

## Exact tests the solver passes

| test | result |
|---|---|
| Scallop theorem (no polymer) | **exactly 0.0** |
| Symmetric beads + polymer | 9.6e-19 |
| Translation invariance | identical to 7 digits |
| Bead-swap antisymmetry | 3e-18 |
| Force balance `∮U_stokes` | ≤ 1e-16 across ~1,000 runs |

**A numerical note worth knowing:** pure 2-D periodic Stokes is unusable for a free swimmer. The
stresslet far field decays as `cos(2θ)/r²`, so the periodic image sum converges slowly *and*
non-monotonically — the amplitude exponent comes out 0.99 against a theoretical 2.00, and
Richardson extrapolation in `1/L²` makes it worse. Brinkman screening (`k² + 1/ℓ²`) fixes it in
one line, recovering exponent **1.9944**, and is physically legitimate: it describes a confined
film or porous medium.

## Layout

```
viscoelastic/
  solver2.py               the solver — Stokes/Brinkman + Oldroyd-B, numpy only
  theory_analysis.py       the analytic mechanism, no PDE
  rhythm_modal.py          rhythm at fixed excursion
  crossover_modal.py       locating the reversal + cycle convergence
  constraint_modal.py      matched-energy search across five fluids
  winners_verify_modal.py  refinement of every headline number
  scaling_modal.py         the scaling law across swimmer/fluid parameters
  theory_modal.py          shape-independence test — this is what broke the general claim
  mechanism_modal.py       fields and cycle-resolved displacement for the JFM figure
  rl_modal.py              reinforcement learning — the agent that discovers the reversal
  RHYTHM.md                full write-up, including all three retractions
  VALIDATED.md             solver validation and the Brinkman fix
  site/                    the published write-up
solver/                    Newtonian precursor — recovers Taylor (1951) ½ and −19/32
NEWTONIAN.md               that precursor's write-up
research/                  prior-art sweeps
```

## Status and caveats

A **computational result, not a peer-reviewed publication**. Stated plainly:

- One 2025 paper (Asghar et al., *Chinese J. Phys.* **96**, 664) remains paywalled and unread —
  a title-level risk we could not close.
- Singh & Choudhary (arXiv:2604.27348, 2026) report a similar-looking reversal driven by
  **Kelvin–Voigt elasticity in the swimmer's body, not the fluid**. Different mechanism, same
  phenomenology; worth distinguishing.
- Novelty rests on two adversarial literature searches briefed to *prove the result already
  published*, with every query logged. `all:"optimal stroke" AND all:"viscoelastic"` returns
  zero results on arXiv.

Corrections are welcome and will be published. The fastest way to find out whether this is wrong
is for someone to try to break it.

## Standing on

Purcell (1977) · Fu, Wolgemuth & Powers (2009) · Montenegro-Johnson, Smith, Smith, Loghin &
Blake (2012) · Elfring & Lauga (2015) · Iqbal, Penington, Thomas & Koens (2025)

---

Built at [Vizuara](https://vizuara.ai).
