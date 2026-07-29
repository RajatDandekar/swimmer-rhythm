# Taylor's swimming sheet, from scratch — and where a world model actually helps

**Status (2026-07-27):** the numerics are **done and triple-validated**. The world-model
question is answered below, and the answer is *not* the one the framing implies.

---

## 1. The headline: you do not need CFD software, and you do not need a world model

`solver/taylor_spectral.py` — **200 lines of numpy, zero CFD dependencies, 3.6 ms/solve** —
reproduces Taylor (1951) exactly:

```
U/V = ½(kb)² [ 1 − 19/16 (kb)² + … ]   =   ½(kb)² − 19/32 (kb)⁴ + …
```

| quantity | numerics | exact | rel. err |
|---|---|---|---|
| leading coefficient | 0.4999406 | **½** | 1.2e-4 |
| O((kb)⁴) coeff, inextensible sheet | −1.187491 | **−19/16** | 7.7e-6 |
| O((kb)⁴) coeff, transverse/extensible sheet | −0.999991 | **−1** | 9.2e-6 |
| rate of working W/(kb)² as kb→0 | 0.999725 | **1** (Taylor eq. 14) | 2.8e-4 |

**Method.** Spectral boundary collocation. Expand the Stokes stream function in the decaying
biharmonic basis for a periodic half-strip,

```
ψ = Σ_{n≥1} e^{−ny} [ (Aₙ + Cₙ y) cos nx + (Bₙ + Dₙ y) sin nx ]
```

impose no-slip at M points on the *actual wavy material surface* (not a linearised flat one),
and least-squares solve for {A,B,C,D}ₙ together with the unknown rigid drift U. Setting the
n=0 mode to zero puts us in the lab frame with fluid at rest at infinity; **requiring a
decaying solution is what makes the sheet force-free**, so U falls out without a separate
force balance. Convergence is exponential — machine precision by N=24 modes (residual 3e-15).

## 2. Three independent validations

**(a) Asymptotic — Taylor's own two coefficients.** Above.

**(b) Finite amplitude — against Sauzade, Elfring & Lauga (2011).** They solved the same
problem by a completely different route: a singly-periodic boundary-integral method plus a
1000-order perturbation series (500 nonzero terms, 300-digit GMP arithmetic) Euler-transformed
to kill the pole at δ₀ ≈ −0.9149. My spectral solver agrees with their resummed series to
**~1e-6 across 0.05 ≤ kb ≤ 0.5** — the limit of the reference precision I have, not of the
solver:

| kb | spectral (mine) | Lauga 500-term Euler | rel diff |
|---|---|---|---|
| 0.05 | 0.001246299 | 0.0012463 | 7.7e-07 |
| 0.10 | 0.004941259 | 0.0049413 | 8.3e-06 |
| 0.20 | 0.019089311 | 0.0190893 | 5.9e-07 |
| 0.30 | 0.040616496 | 0.0406165 | 1.0e-07 |
| 0.40 | 0.067039536 | 0.0670395 | 5.4e-07 |
| 0.50 | 0.095784264 | 0.0957843 | 3.7e-07 |

Two unrelated discretisations agreeing to 6–7 digits at finite amplitude is about as strong
as numerical validation gets.

**(c) A different physical channel — the dissipation.** `solver/dissipation.py` rebuilds the
full pressure and velocity-gradient fields from the same coefficients and recovers Taylor's
rate of working `W = μσ²b²k`. This exercises parts of the solution the drift never touches,
so it is a genuine independent check rather than a restatement.

### The discriminating finding worth keeping

The leading ½ is **identical** for the inextensible and the purely-transverse extensible
sheet. Inextensibility is invisible at O((kb)²) — the longitudinal correction it forces is
itself O((kb)²) with zero time-mean — and first bites at O((kb)⁴), where the coefficient
splits −19/16 vs −1. **A numerical study that only checks the ½ cannot tell the two
kinematics apart.** The 19/32 is the term that certifies you have Taylor's actual sheet.
Any "we rediscovered Taylor's law" claim that stops at ½ has proven almost nothing.

### The gotcha that will bite any reimplementation

The arclength inversion that builds the inextensible kinematics anchors material label a=0
to x=0. That injects a spatially uniform, zero-time-mean longitudinal velocity m(t) into the
prescribed motion, so the solver returns `U_true − m(t)` and the leading coefficient reads
**¼ instead of ½** — exactly a factor 2 off, which looks like a physics error and is not.
Adding back `mean(uₓ)` (or period-averaging) fixes it and makes the drift t-independent to
1e-17. Cost me real time; documented at `taylor_spectral.py:88-96`.

---

## 3. The honest verdict on the world-model framing

Two separate goals got fused in the original question. They pull in opposite directions.

**Goal A — "I don't want to use specialized CFD software."** ✅ **Solved, and a world model
would be strictly worse.** The exact solver is 200 lines, has no dependencies beyond numpy/
scipy, runs in milliseconds, and is accurate to machine precision. A learned surrogate would
cost weeks of work to build, need this solver to generate its training data, and be *less*
accurate. There is no version of this where the learned model wins on the Newtonian
swimming-sheet problem.

**Goal B — "derive the Taylor formula with a world model."** ⚠️ **Weak as a standalone
target, because the problem is already solved to 500 orders.** Sauzade/Elfring/Lauga
published the exact series coefficients as arXiv ancillary data in 2011. Rediscovering
½(kb)² from simulation data is a *sanity check on your pipeline*, not a scientific result —
and the 2026 equation-discovery field is crowded (SR-LLM, PNAS 122:e2516995122, reports 76.1%
recovery on the 100-formula Feynman benchmark; IGSR at ICML 2026; NewtonBench; KeplerAgent;
SR-Scientist). A paper whose headline is "we recovered a known 1951 result" competes badly
against those.

**The move that makes both goals pay off:** keep this solver as the **ground-truth
generator**, use Taylor's ½ and −19/32 as the *unit test* that proves the discovery pipeline
works on a case with a known answer, and then point the pipeline where the analytics genuinely
run out. The asymptotics die and no closed form exists for:

- **finite Reynolds number** — the series is in kb *and* Re; direction reversal is reported
  but the coefficient structure is not known in closed form
- **viscoelastic fluid** — Lauga's own results show the sign of the correction depends on
  Deborah number in a way no simple formula captures at finite amplitude
- **confinement** — sheet near a wall, or two sheets at finite separation (this is where the
  Elfring–Lauga synchronisation work lives: phase-locking force is O(amplitude⁴) for
  prescribed asymmetric waveforms in a Newtonian fluid, but drops to O(amplitude²) once
  elasticity supplies the symmetry-breaking)
- **elastic sheet with prescribed internal forcing** — the shape becomes an unknown, so
  there is no amplitude to expand in

That is a defensible contribution: *the discovery loop is validated against a case with a
known exact answer, then produces new closed forms where none exist.* The Taylor formula
becomes your credibility, not your result.

---

## 4. Where reinforcement learning fits — and where it provably doesn't

`solver/gait.py` settles this numerically rather than by argument. The solver already *is* an
RL environment interface: observation = sheet shape, action = shape rate, reward = drift. So
put a two-parameter shape family `y = a₁(t) sin x + a₂(t) cos x` on it — a gait is a closed
loop in the (a₁, a₂) plane, and the circle `a₁ = b cos t, a₂ = −b sin t` *is* Taylor's
traveling wave — and measure what the reward actually depends on.

**Result 1 — reward per cycle is exactly the enclosed area.**

| b | net displacement/cycle | signed area | ratio | 1 − b² |
|---|---|---|---|---|
| 0.30 | −2.597177e-01 | −2.827429e-01 | 0.918565 | 0.910000 |
| 0.10 | −3.110539e-02 | −3.141587e-02 | 0.990117 | 0.990000 |
| 0.02 | −1.256135e-03 | −1.256635e-03 | 0.999602 | 0.999600 |
| 0.01 | −3.141279e-04 | −3.141587e-04 | 0.999902 | 0.999900 |

Ratio → 1, and the correction tracks **(1 − b²)** — the same O(b²) coefficient (−1) measured
independently from the amplitude sweep in §1. Three-way consistent.

**Result 1b — displacement depends ONLY on area, not on loop shape.** This is the airtight
form of the claim, and the one that actually kills the sequential structure. `equalarea.py`
runs five wildly different loops of *identical* enclosed area:

| loop (b = 0.02) | net displacement | displ/area |
|---|---|---|
| circle | −1.256135e-03 | 0.999602 |
| ellipse 2:1 | −1.256009e-03 | 0.999502 |
| ellipse 4:1 | −1.255570e-03 | 0.999153 |
| square (sharp corners) | +1.256140e-03 | 0.999604 |
| triangle (sharp corners) | +1.255943e-03 | 0.999449 |

All agree to ~4 digits and converge to 1. **Aspect ratio is irrelevant. Sharp corners are
irrelevant. Only the enclosed area matters.** (Sign differences are loop orientation only.)

**Result 2 — the scallop theorem, to machine precision.** Every zero-area loop returns zero
net displacement, *including* one with deliberately non-sinusoidal timing and a figure-eight:

```
RECIPROCAL line (a2 = 0)                   1.932e-19
RECIPROCAL line, non-sinusoidal timing    -6.786e-20
RECIPROCAL diagonal line                  -7.843e-18
figure eight (zero net area)               3.701e-18
```

No amount of clever timing buys a single micron. **Result 3 — rate-independence to 1e-16:**
warping the traversal schedule leaves displacement per cycle unchanged (Stokes has no clock).

### The consequence

In pure Stokes the MDP is **degenerate**. There is no hidden state to track, no memory to
exploit, and no credit to assign across time — reward per cycle is a pure functional of *one
scalar*, the enclosed area. Optimal gait selection collapses to *"maximize enclosed area
subject to a dissipation budget"*: a two-dimensional variational problem solvable directly.
A policy has nothing to decide about *how* to move through shape space, only about which
region to encircle. RL would be a very expensive way to rediscover a geometric identity.

### ⚠️ Attribution: the area law is ESTABLISHED THEORY, not a finding here

Verified 2026-07-27. All three measurements above are **standard results**, stated verbatim in:

> L. Koens & E. Lauga, "Geometric phase methods with Stokes theorem for a general viscous
> swimmer," *J. Fluid Mech.* **916**, A17 (2021), doi:10.1017/jfm.2021.181, arXiv:2104.05144.

- *area law:* "This representation can be transformed into an area integral for simple swimmers
  using Stokes theorem" — their Eq. (9) is exactly our form,
  `Δx = ∮(M₁ dl₁/dt + M₂ dl₂/dt)dt = −∬(∂M₁/∂l₂ − ∂M₂/∂l₁)dl₁dl₂`
- *and our exact configuration:* "For swimmers that travel in one dimension and only have two
  degrees of freedom, geometrical techniques can be simplified through the use of the Stokes
  theorem, which allows the net displacement from any stroke to be visualized on a plane."
- *scallop:* "Swimming strokes that do not break time-reversal symmetry contain zero area within
  them and so clearly produce no displacement."
- *rate independence:* "This result is independent of the speed at which l varies, as expected
  for swimmers in Stokes flow."

Origin is **Shapere & Wilczek** — *PRL* **58**, 2051 (1987) and *JFM* **198**, 557–585 (1989),
doi:10.1017/S002211208900025X. Modern robotics restatement with the explicit `∇×A`: Hatton &
Choset, *IJRR* **30**(8), 988 (2011); Rieser et al., *PNAS* **121**(24), e2320517121 (2024) —
*"the net displacement can be approximated by taking the integral of the curvature of A over the
region of the shape space enclosed by a gait."*

**So §4 is an independent high-precision numerical confirmation for a continuum (waving-sheet)
swimmer — not a discovery.** Frame it that way.

### Two things the measurements *do* contribute

**1. The figure-eight zero is evidence of Abelian-ness, not a triviality.** Exact cancellation of
signed area requires an **Abelian** connection; in non-Abelian settings a figure-eight generically
*does* produce net motion. Avron & Raz (*NJP* **10**, 063016, 2008): *"Stokes theorem only works
for commutative coordinates."* So the measured 1e-18 confirms that our (a₁,a₂) sheet with pure
x-translation is the Abelian case — worth stating explicitly.

**Corollary — the O(b²) residual is misattributed if called a Stokes-theorem failure.** Because the
system is Abelian, the (1 − b²) correction is the **amplitude dependence of the connection A
itself**, i.e. the small-amplitude expansion of A, not non-commutativity.

**2. The "RL is degenerate in Stokes" thesis is genuinely NOT in print** — ~50 searches across
arXiv/APS/AIP/Nature/IOP/Springer found no paper arguing that Stokes gait optimization is not a
sequential decision problem. The RL branch and the geometric-mechanics branch barely cite each
other. The component facts are all published; **the synthesis is absent.** That is the contribution.

### Scope it honestly — two published claims bound it

- **Koens & Lauga (2021) themselves prove the objective degenerates upward:** *"for swimmers with
  more than two modes of deformation, there exists an infinite set of strokes that generate each
  net displacement. Hence, in the absence of additional restrictions, general microscopic swimmers
  do not have a single stroke that maximises their displacement."* So "maximize the area" needs an
  extra constraint to be well-posed. **The argument is airtight in the Abelian two-parameter case
  and weakens as dimension grows.**
- **Hu & Dear (arXiv:2301.13072)** — the only paper putting geometric mechanics and RL-for-Stokes-
  gaits in one frame — supplies the counter-argument: *"Analytically optimizing gaits is thus
  equivalent to solving a multi-objective constrained optimization problem over a continuous space,
  a task that becomes exponentially more difficult with increasing system complexity."*

Must be distinguished explicitly: **Mecanna, Loisy & Eloy**, *EPJ E* **48**, 58 (2025),
arXiv:2505.05525 — the only published critique of RL here, but it targets *navigation* and
*affirms* sequential structure (*"a model-free partially observable Markov decision process…
usually well-suited for reinforcement learning"*). Their thesis is "RL done badly"; ours is "RL is
the wrong frame." Say so, or be called a duplicate.

**Concede:** gait switching / navigation (Zou 2022), navigation in flows (Mecanna 2025),
elastohydrodynamic swimmers where shape is not directly actuated (Lin 2024), finite-size
hydrodynamic coupling (Zhu 2022). The claim is strongest exactly where this solver lives:
**kinematically actuated, low-DOF, quiescent fluid, prescribed shape.**

### So RL earns its keep exactly where those three properties break

| regime | area law | scallop | rate-free | what becomes the state | RL case |
|---|---|---|---|---|---|
| Stokes (here) | holds | holds | holds | nothing — shape is all | ❌ degenerate |
| **finite Re** | breaks | **breaks** | **breaks** | vorticity history | ✅ real MDP |
| **viscoelastic** | breaks | **breaks** | **breaks** | polymer conformation field | ✅✅ strongest |
| two sheets / wall | holds\* | holds\* | holds\* | neighbour's phase | ✅ as a *game* |
| navigation in ambient flow | — | — | — | local flow estimate | ⚠️ well-trodden |

\* still Stokes, so still reversible — the state is the *other* swimmer, which makes it
multi-agent rather than memory-driven.

**The viscoelastic case is where RL and the world model become the same project.** The polymer
conformation tensor is a high-dimensional, partially-observed field that persists across
strokes — the swimmer must exploit stress it laid down in earlier cycles. That is precisely a
latent-dynamics-model problem: learn the conformation field's evolution from solver rollouts,
plan in imagination, and the Deborah-number dependence of the learned optimal gait is then a
symbolic-regression target where **no closed form exists**. Taylor's ½ and −19/32 remain the
unit test that proves the loop is sound.

### ~~Distinctive asset~~ — RETRACTED 2026-07-27, falsified by prior art

I previously claimed here that *"most RL-for-microswimmer work uses either resistive-force-theory
toys or full CFD, so a 3.6 ms exact Stokes solve is a distinctive asset."* **That is wrong.**
Two papers already use a genuine boundary-integral Stokes solver as the RL environment:

- Xiong, Liu, Wang, Ong & Zhu, "Chemotactic navigation in robotic swimmers via reset-free
  hierarchical reinforcement learning," ***Nature Communications* 16, 5441 (2025)**,
  doi:10.1038/s41467-025-60646-z. Verbatim: *"We build the numerical hydrodynamic environment
  of microswimmers using a 3D boundary integral method to solve the Stokes equation.
  Specifically, we adopt a regularized Stokeslet method."* PPO, 9-hinge chain / 20-link ring.
- Bailey & Guy, "Optimizing metachronal paddling with reinforcement learning at low Reynolds
  number," arXiv:2507.18849, *EPJ E* (2025), doi:10.1140/epje/s10189-025-00511-5. Regularized
  Stokeslets + tabular Q-learning.

So "exact solver as RL environment" is **not** available as a novelty claim. What remains on
the solver axis is only *spectral / high-order / lubrication-resolved* fidelity beyond
regularized Stokeslets — an incremental-fidelity claim, and only interesting if the extra
fidelity **changes the learned gait**. See `research/PRIOR_ART_VERDICTS.md`.

### The argument above is *supported* by that literature, though

§4's geometric result predicts that RL-for-Stokes-gaits should be a crowded field that mostly
**rediscovers known optima** — because there is nothing else there to find. That is exactly
what the papers report: Tsang et al. (2020) *"recover a previously known propulsion strategy"*;
Qin et al. (2023) *"identifying the classical swimming gaits of Purcell's swimmer."* And
Kanazawa, Ishimoto & Kawaguchi (arXiv:2603.08444, 2026) now **prove** analytically which
strokes are optimal, validated against 3D Stokes simulation — no RL required.

The area-law/scallop measurements are therefore best used as a **critique and a diagnostic**
("here is why that subfield saturated, and here is the test that tells you whether a regime has
anything for RL to learn"), not as a launchpad for another Stokes RL paper.

## 5. On `next-state/open-dreamer` — do not build on it

I read the codebase. Three blocking problems, in order of severity:

1. **The licence forbids it.** `LICENSE` reads *"All rights reserved… No license or permission
   is granted, whether express or implied, to use, copy, modify…"*; GitHub reports
   `NOASSERTION`. You cannot legally fork, vendor, or derive from it.
2. **There is no agent in it.** Only the world-model half of Dreamer 4 — tokenizer plus
   action-conditioned flow-matching dynamics. Verified by exhaustive grep: no policy, actor,
   critic, value, GAE, PPO, planner, reward head, or imagination rollout. It is a controllable
   video predictor, not a model-based controller. Its own README roadmap admits this.
3. **It is not ready.** ~1.57B params, CUDA-12 JAX only, zero tests, 8 commits. The CoinRun
   (non-Minecraft) path is *provably broken at HEAD* — `ShardWriter` is called with a kwarg it
   doesn't accept, and writes msgpack where the reader does `pickle.loads`. Two hard asserts
   pin the Minecraft VPT action space (27 binary / 121 camera classes), which the repo's own
   `coinrun.yaml` cannot satisfy. RGB is hardcoded in the encoder while the decoder reads
   channel count from config, so `C≠3` has never run.

There is also a real inductive-bias defect for field data: RoPE is applied over the
**raster-flattened** spatial token index, so vertical neighbours in a 2-D grid sit `W/patch`
positions apart in phase. (A `2d-rope` branch exists on the remote, so the authors know.)

**Worth reading and reimplementing, ~400 lines:** the shortcut-forcing self-distillation loss,
the τ-ladder sampler, and the x-prediction + v-space loss weighting. Steal the algorithms,
write your own code.

---

## 6. Layout

```
solver/
  taylor_spectral.py   the solver + convergence/amplitude sweeps (run this first)
  gait.py              is RL useful here? area law + scallop theorem + rate-independence
  equalarea.py         the decisive test: equal-area loops of different shape agree
  dissipation.py       independent validation via the rate of working
  richardson.py        Richardson extrapolation in (kb)² for the coefficients
SOLVER_RESULTS.md      raw captured output from the validation runs
```

Run with any numpy/scipy environment:

```bash
python3 solver/taylor_spectral.py    # ~0.4 s for the full sweep
python3 solver/dissipation.py
python3 solver/gait.py               # the RL-relevance experiment
python3 solver/equalarea.py          # shape-independence (run from solver/)
```

## 7. Key references (all verified against publisher records, not recalled)

- G. I. Taylor, "Analysis of the swimming of microscopic organisms," *Proc. R. Soc. A* **209**,
  447–461 (1951). The original; U/V = ½(kb)²[1 − 19/16 (kb)²], and W = μσ²b²k at eq. (14).
- M. Sauzade, G. J. Elfring & E. Lauga, "Taylor's swimming sheet: Analysis and improvement of
  the perturbation series," *Physica D* **240**(20), 1567–1573 (2011).
  doi:10.1016/j.physd.2011.06.023, arXiv:1302.4029. **The benchmark.** Boundary-integral +
  500-term series; coefficients in the arXiv ancillary file. Their c₁ = −19/32 exactly
  confirms Taylor. Raw series diverges past kb ≈ 0.9565 (pole at δ₀ ≈ −0.914912); Taylor's own
  4th-order form is good to kb ≈ 0.4. Note: **no element count, no mesh-convergence study, no
  tabulated BI values** — so it is a great *analytical* target and a poor *BEM* benchmark.
- R. Drummond, *J. Fluid Mech.* **25**, 787–793 (1966). Extends Taylor to 8th order.
- G. J. Elfring & E. Lauga, "Hydrodynamic phase locking of swimming microorganisms,"
  *Phys. Rev. Lett.* **103**, 088101 (2009), arXiv:0907.0962 — the rigid/prescribed baseline.
- G. J. Elfring, O. S. Pak & E. Lauga, "Two-dimensional flagellar synchronization in
  viscoelastic fluids," *J. Fluid Mech.* **646**, 505–515 (2010), arXiv:0912.2377. (Three
  authors — do not cite as "Elfring & Lauga".)
- G. J. Elfring & E. Lauga, "Synchronization of flexible sheets," *J. Fluid Mech.* **674**,
  163–173 (2011), arXiv:1108.5791. Elasticity supplies the symmetry-breaking; phase-locking
  force becomes O(amplitude²) instead of O(amplitude⁴).
