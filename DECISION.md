# Where to point this — the recommendation after the prior-art sweep

Written 2026-07-27, after eight adversarial prior-art agents. Evidence in
`research/PRIOR_ART_VERDICTS.md`. Two agents still outstanding (viscoelastic-solver feasibility;
geometric-mechanics attribution) — neither can change the direction below, only sharpen it.

## Scoreboard

| Claim | Verdict |
|---|---|
| RL gait discovery in Stokes flow | **KILLED** — settled sub-field, 2 reviews, ≥6 groups |
| "Exact Stokes solver as RL environment" | **KILLED** — *Nat. Commun.* 16:5441 (2025); *EPJ E* (2025) |
| World model whose latent holds the *fluid's* state | **WEAKENED** — both halves published |
| RL at finite Re | **SURVIVES** only in 0 < Re < 100, with caveats |
| Taylor's 1951 sheet as an ML environment/benchmark | **SURVIVES** |
| RL in a viscoelastic fluid | **SURVIVES** — 2 independent passes + citation-network test |
| SR on the optimum vs a dimensionless group | **WEAKENED**, except vs De/Wi which is **virgin** |

## The recommendation: viscoelastic, and it is one argument rather than three claims

Three independently unoccupied links that compose into a single arc:

1. **The fluid has memory.** RL has never been coupled to *any* viscoelastic constitutive model in
   fluid mechanics — not swimmers, not drag reduction, not elasto-inertial turbulence. Confirmed
   twice, including by a citation-network test: of 340 works citing Lauga (2007), exactly one
   mentions RL (a review, saying it hasn't been done).
2. **⇒ the policy needs the memory field in its state.** No prior work puts a polymer
   conformation/stress field into a policy's observation. This is the specific sentence to defend,
   and it is what makes it a *world-model* problem rather than a control problem — the latent is
   forced by the constitutive equation, not chosen for convenience.
3. **⇒ regress the learned optimum against Deborah number.** SR + De/Wi returns **zero** papers.
   Pak & Lauga (*PRE* 81:036312, 2010) have an optimal De analytically at small amplitude; nothing
   exists at finite amplitude.

## The research design this enables — a two-stage known-answer validation

This is the part that makes it defensible, and it falls out of what we already built:

| Stage | Known answer to hit | Source |
|---|---|---|
| **Newtonian, small amplitude** | U/V = ½(kb)²[1 − 19/16 (kb)²] | Taylor (1951) — **already reproduced, §1–2** |
| **Viscoelastic, small amplitude** | U/U_N = [1 + De²η_s/η] / [1 + De²] | **Lauga, *Phys. Fluids* 19:083104 (2007)** — same waving-sheet geometry |
| **Viscoelastic, finite amplitude** | *nothing exists* | ← the contribution |

Lauga 2007 is the gift here: it is an **exact viscoelastic answer for our exact geometry**, so the
pipeline gets a second unit test *in the target physics*, not just in the Newtonian limit. A
discovery loop that reproduces Taylor's −19/32 **and** Lauga's De-dependence before being pointed
at unknown territory is very hard to argue with.

## Two corrections to the earlier plan

**1. The Taylor sheet is the validation case, not the RL vehicle.** An infinite sheet carries one
wave — there is nothing to sequence, so it cannot demonstrate a sequential decision problem, and a
referee will say so. Use a **multi-link or multi-paddle body** for the RL; keep the sheet as the
analytic unit test. (Credit: this critique came from the finite-Re agent, and it applies equally to
the viscoelastic route.)

**2. The area-law measurement is repurposed as the instrument.** §4 of the README shows Stokes has
reward = enclosed area, exactly, with machine-precision shape-independence. That is a **diagnostic**:
sweep De (or Re) and measure the *departure* from the area law. The departure is a direct,
quantitative measure of how much sequential structure exists — i.e. of whether RL can beat geometry
at all. Publishing that instrument is more useful than publishing another gait.

## What to drop, and what to cite so a referee cannot spring it

**Drop:** "first RL swimmer in a non-Newtonian fluid" (Huynh & Nguyen, *Eng. Res. Express* 8:135205,
2026 — Unity, navigation, but it counts) · "gait matters in viscoelastic fluids" (Elfring & Goyal,
*JNNFM* 234:8, 2016 — the title *is* the question) · "memory makes it a genuine sequential decision
problem" (Lin et al., *PRR* 6:033016, 2024 — made that argument with body elasticity).

**Cite pre-emptively:** Mo, Li & Bian (*Front. Phys.* 11, 2023) which flags this exact programme as
an open question — better to own it than have it produced against you.

## The two risks that matter

**Scoop, and the clock is visible.** Gupta & Dey, arXiv:2607.19820, **22 July 2026 — five days
ago** — already showed analytically that back-and-forth beating exploits fluid memory in a Jeffreys
fluid, calling it *"a generic mechanism for exploiting fluid memory in active oscillators."* The
"surprising stroke" punchline is partly claimed. Two groups hold both halves: **Lailai Zhu** (author
on the exact-solver RL paper *and* the multi-link RL paper, with a stated programme on gaits in
complex fluids) and **Ardekani** (ViscoelasticNet *and* viscoelastic microswimming — *"the two lines
were never joined"*).

**Solver cost is the open technical question.** Neal & Bearon (*Phil. Trans. R. Soc. A* 383:20240268,
2025) built a three-sphere swimmer in a Giesekus fluid with hybrid Newtonian + FEM correction — so
the environment exists in the literature, but "exists" ≠ "millisecond." A viscoelastic solve is
fundamentally harder than the Stokes one: the conformation tensor is an extra advected PDE with its
own stiffness and the well-known high-Weissenberg instability. **This is the go/no-go.** Pending
agent #7. If no viscoelastic solver runs fast enough to train against, the honest fallback is the
Re = O(1) route, where IBAMR/IB-LBM/smoothed-profile are all known to work.

## REVISED after four independent passes on finite Re: this is a genuine two-way choice

Three further agents worked the Re question and it came back much stronger than "fallback." Honest
head-to-head:

| | **Viscoelastic (De)** | **Near-Stokes inertial (Re = O(1))** |
|---|---|---|
| Novelty of the cell | **Nothing at all** — RL has touched no viscoelastic constitutive model in fluid mechanics. Confirmed twice + citation-network test | **Nothing at Re < 10** with a deforming body + real NS. `"scallop theorem"` + `"reinforcement learning"` → **0** |
| The precise open question | Optimal gait at finite amplitude vs De | **How the optimal gait itself deforms as Re sweeps Stokes → inertial.** Nobody has closed this loop |
| Known-answer validation | Taylor 1951 **and** Lauga 2007 (exact, same geometry) | Tuck 1968 (sheet); Felderhof 2015 (slab); Felderhof & Jones 2017 (sphere) |
| Solver cost | **UNKNOWN — the go/no-go.** Conformation tensor = extra advected PDE + high-Weissenberg instability. ⚠️ **And no viscoelastic ML surrogate has ever reported a speedup** — RUDE reports *overhead*; Balasubramanian spent 3,500 GPU-h + 1.5M core-h and reports no inference time. The "surrogate makes it tractable" premise is **unvalidated in this fluid class** | **Known to work.** IBAMR, IB-LBM, smoothed-profile all run at Re ~ 1 |
| Scope of the gap | swimming/locomotion untouched; but a **DFD-2025 abstract** exists for viscoelastic *turbulence* control | ⚠️ **Narrowed: only Re < 100.** Gait optimization at **Re = 550** with CMA-ES + resolved 3D NS already exists (Gazzola 2012 kinematics; van Rees 2015 shape+gait, >10,000 DNS). Say **"Re = O(1)"**, never "finite Re" |
| Cheapest first step | none — needs a real constitutive solver | **O(Re) perturbation on the existing basis** (`u = u₀ + Re·u₁`, linear solve, keeps ms cost) |
| Scoop pressure | **High** — Gupta & Dey 5 days ago; Zhu and Ardekani both hold both halves | **Moderate** — Klotsa's swimmer line *stopped* in 2022 with no ML follow-up; Bailey & Guy don't list nonzero Re even as future work |
| Must carve out | Elfring & Goyal 2016 (the question); Lin et al. 2024 (the framing); Huynh & Nguyen 2026 ("first RL non-Newtonian") | **Felderhof & Jones 2017** (analytic optimization *with inertia* — so "first to optimize a gait with inertia" is false); Chisholm et al. 2016 (owns the Re sweep, froze the stroke) |

**Both routes share the same best framing, which is ours to make:** *both regimes RL has occupied
are rate-independent.* Stokes is geometric by construction (README §4). Jiao et al.'s potential-flow
RL self-describes as a *"driftless dynamical system … geometric phases over the shape space."* **RL
has been applied at both ends of the degenerate spectrum and never in the memory-bearing middle.**

And the area-law diagnostic has a theory citation on the Re side: Kvalheim, Bittner & Revzen
(*Nonlinear Dynamics* 2019, arXiv:1906.04384) — in the *"perturbed Stokes regime … motion is still
governed by a functional relationship between shape velocity and body velocity, but **this function
is no longer linear in shape change rate**."* That is precisely what the diagnostic measures.

Sharpest motivating fact on the Re side: Klotsa's group swept a metachronal paddler over
**Re = 0.05–100** and found swim speed **non-monotonic in Re** (max near Re ≈ 1). When RL finally
reached that *same* geometry in 2025 (Bailey & Guy), it was run at **Re = 0** — and they do not
mention inertia as future work.

Mandatory framing on the Re route: **never write "intermediate Reynolds number"** (≈550 to the
fish/CFD community, 1–1000 to Klotsa's — say **"Re = O(1)"** or **"near-Stokes inertial"**, and give
the band numerically every time); distinguish from Chen & Yang 2025 (Re = 100, tracking not gait
discovery) and Jiao et al. 2021 (inertial but driftless); and stay **out** of small amplitude where
Derr et al. (*JFM* 952:A8, 2022) and Felderhof & Jones already have analytic answers.

## FINAL — after all 14 agents

### The claim to make, and the argument that carries it

**Not** "first RL swimmer in a complex fluid." **Not** "memory makes it a sequential problem" (Fu,
Wolgemuth & Powers said that in 2009). **Not** "an optimum exists in a viscoelastic fluid" (at least
six papers own that). The claim is:

> **Every existing method for optimizing a swimmer's gait relies on Stokes linearity and the Lorentz
> reciprocal theorem to decouple the flow solve from the optimization loop. Fluid memory destroys
> that decoupling. So gait optimization in a viscoelastic fluid has never been done — and a learned
> policy with the polymer conformation field in its state is the natural way to do it.**

The swimmer-optimization community states the dependency itself — Bonnet, Das, Veerapaneni & Zhu
(arXiv:2604.07310, 2026): *"**By exploiting the linearity of the Stokes equations and the Lorentz
reciprocal theorem**, we derive an explicit linear operator … **effectively decoupling the
hydrodynamic boundary value problem from the optimization loop**."*

Supporting evidence, quantifiable and quotable: **in Eric Lauga's complete corpus, the 10 papers with
"optimal" in the title and the 19 papers on viscoelastic/complex fluids do not intersect once.** Same
for Robert Guy and Becca Thomases. The French optimal-control school never left Newtonian. Lauga has
used RL exactly once — Newtonian. And a 2026 review of microswimmers in non-Newtonian fluids
(Kobayashi, Molina & Yamamoto) mentions **no** optimization, adjoint, or RL at all.

Enabling citation that proves it is possible: **Kim, *Appl. Math. Modelling* 115:453 (2023)** derives
a **continuous adjoint for Oldroyd-B** — optimizes nothing, contains no swimmer, but the derivative
exists.

### The validation ladder — four rungs, and this is the strongest part of the design

Every known optimum becomes a **check the agent must recover**, not a result to claim:

| Rung | Target | Source |
|---|---|---|
| Newtonian, small amp. | ½(kb)²[1 − 19/16 (kb)²] | Taylor 1951 — **already reproduced, §1–2** |
| Viscoelastic, small amp. | U/U_N = (1+De²ηₛ/η)/(1+De²) | Lauga, *POF* 19:083104 (2007) |
| Viscoelastic optima | De≈1 efficiency peak · max U=1.3 at De=0.5 · De = mq/√3 · multi-mode requirement | Teran/Fauci/Shelley 2010 · Riley & Lauga 2015 · Elfring & Goyal 2016 |
| **Finite amplitude, strongly elastic** | ***nothing exists*** | ← the contribution |

**Recovering the known optima is a strength; claiming them is fatal.** Open on Thomases & Guy's own
sentence (*JFM* 825:109, 2017): *"High amplitude strokes in strongly elastic flows lead to a
qualitatively different regime."*

### Feasibility: settled, with compromises

**Milliseconds/stroke is impossible with a faithful solver.** Calibration: Rempfer et al.
(arXiv:2509.01327) get 1024² 2D four-roll mill at **~200 ms/step on one CPU core** — but only to
**Wi ≈ 1.1**, 6 h to converge. Realistic target: **O(0.1–10 s)/stroke on one GPU** at 2D, Wi ≲ 5,
coarse resolution + artificial stress diffusion (ε ≈ 1.5×10⁻³, per Thomases & Guy's 512² / dt=10⁻³ /
De 0–5 setup) → **10⁵–10⁶ env steps** with parallel envs. Feasible.

**The wall is timestep COUNT, not the log-conformation transform** (that is < 2× and, remarkably,
never profiled in the literature — a gap in itself). And for immersed boundaries there is a second,
harsher restriction from penalty stiffness κ ∝ h/Δt²; the fix is semi-implicit / **non-stiff IB**,
which is what took Ceniceros & Fisher to Wi > 100 while the explicit IBAMR benchmark caps at Wi = 0.1.

**A free methods contribution sits alongside:** no GPU viscoelastic LBM has *ever* published a
throughput number — verified by exhaustive arXiv sweep, and named as future work by the field's own
2026 review. Even the one GPU-capable implementation (Kellnberger et al., built on FluidX3D) reports
no MLUPS. "First GPU viscoelastic LBM with published throughput" is unoccupied.

### Two corrections to the plan, both load-bearing

1. **The Taylor sheet is the validation case, not the RL vehicle.** An infinite sheet carries one
   wave — nothing to sequence. Use a **multi-link or multi-paddle body** for the RL.
2. **Do not say "geometry is dead in viscoelastic fluids."** Two papers argue the opposite in print:
   Loos et al., *PRX* **14**:021032 (2024) (time-reversal structure survives in viscoelastic media,
   with ML) and Kobayashi, Kitano & Yamamoto, arXiv:2606.10268 (*"a minimal geometric principle …
   in viscoelastic fluids"*). Argue that the *decoupling* breaks, not that geometry vanishes.

### Sequencing

1. **O(Re) perturbation on the existing spectral basis** — `u = u₀ + Re·u₁`, a linear solve, keeps the
   millisecond cost. Measures where the area law first breaks. Days, not weeks; the diagnostic is
   publishable alone and useful under either route.
2. **Get the Asghar *Chin. J. Phys.* 96:664 (2025) PDF** via institutional access. Risk is now low
   (its 45 references contain zero optimization-methodology citations) but it is the one on-title hit
   that could not be verified remotely.
3. **Then build the viscoelastic environment** — 2D, Wi ≲ 5, non-stiff IB, artificial stress
   diffusion. Ives & Morozov (2017) already built an arbitrary-waveform viscoelastic sheet solver and
   never optimized on it; that is both the feasibility proof and the warning.

### ⚠️ CLAIM QUALIFIED — RL *has* touched a viscoelastic fluid, at DFD 2025

Recorded three times from independent passes as "RL has never been coupled to any viscoelastic constitutive
model in fluid mechanics." True of the **published** literature; **false for conference abstracts**:

> APS DFD 2025, abstract U25.10 — *"Control of viscoelastic turbulence via wall blowing & suction optimised
> by reinforcement learning"* — Sharma, **Beneitez**, Wittberg, **Vinuesa**, **Tammisola**, Mirjalili.

Flow control, not locomotion — but the group that already built the **viscoelastic polymeric-stress CNN
estimator** (*JFM* 1009:A36, 2025, naming control as future work), co-authored **HydroGym**, runs the
**Manchester PhD studentship on viscoelastic flow control**, and produced the physics behind **The Well's
`viscoelastic_instability` dataset** — has now run RL on a viscoelastic flow. **A Nov-2025 DFD abstract
means a paper is in preparation now.**

**Corrected claim:** *no **published** paper couples RL to a viscoelastic constitutive model; **swimming/
locomotion** in a viscoelastic fluid remains untouched — but the enabling group is already inside the cell.*
Cite the DFD abstract yourself.

**Strongest coverage-independent evidence the two literatures are still disconnected** (OpenCitations, so
publisher-abstract-coverage-proof): 494 citers of 5 canonical RL-swimmer papers ∩ 447 citers of 4 canonical
viscoelastic-swimmer papers = **4 papers, all reviews or Newtonian. Zero research papers bridge them.**

### 🚨 The clock — tighter than the earlier passes suggested

**The viscoelastic latent model already exists.** Kumar, Constante-Amores & Graham (*JFM* 1007:R1, 2025,
arXiv:2410.02948) built **VEDManD** — viscoelastic POD → autoencoder (50 DoF) → stabilized neural ODE,
**FENE-P at Re = 3000, Wi = 35**. Forward prediction only; "control" appears **exclusively in future
work**. And **Constante-Amores co-authors both that paper and the Newtonian RBC DManD-RL paper** (*PRF*
11:044903, 2026). **One person holds both halves and has not joined them.** Same at Brunton/Kutz/Oishi
and at Vinuesa/Tammisola.

**And someone is recruiting to do it:** Manchester has an **open PhD studentship** (Beneitez, King),
*"Data-driven Approaches to Viscoelastic Flow Control,"* explicitly proposing *"control strategies
through deep reinforcement learning"* for viscoelastic turbulence. The tooling is public and
assembled — **RheoTool + Gym-preCICE/DRLinFluids** is weeks of work.

Also: Gupta & Dey (arXiv:2607.19820) showed the fluid-memory stroke effect analytically five days before
this sweep; Cummings et al. (arXiv:2607.14944) eleven days before. **Lailai Zhu** and **Ardekani** each
hold both halves on the swimmer side.

**So the claim narrows to: *first to close the loop.*** Not "first learned model of a viscoelastic
flow" — Kumar et al. own that.

### ➡️ A SECOND, INDEPENDENT OPENING worth taking seriously

The surrogate-as-RL-environment literature has a **named, unsolved failure mode**. Plotzki & Peitz
(arXiv:2603.28074): *"feasibility as training environments for RL is limited by **distribution shifts**,
as policies induce state distributions not covered by the surrogate training data."* Surrogate-only
training *degrades* performance. Cavallazzi et al. (arXiv:2606.30484) show an estimator with **offline
correlation 0.99 fails in closed loop within a few viscous time units** — *"not one of accuracy but of
distribution shift induced by the controller itself."*

**Nobody has brought the standard world-model answers to the fluid case** — TD-learning through the
latent model, reconstruction-free objectives, MOPO-style uncertainty-penalised rollout truncation,
SimNorm. The fluids community keeps rediscovering the problem and patching it with "swap the real solver
back in every N steps." That is a well-posed, unoccupied, *methodological* contribution — and it is
where genuine world-model expertise actually transfers.

**And it is now on record for a self-propelled swimmer, not just convection.** Maroun, Traoré & Bergmann,
*Phys. Fluids* **36**(7):073621 (2024) — SINDy surrogate + MPC on a self-propelled undulatory swimmer,
abstract verbatim: *"**mismatches between the surrogate model and the high fidelity simulation
significantly impact the quality of the obtained solution** … [this work] **underscores the importance of
addressing model mismatches** for more accurate control strategies in the future."* Peer-reviewed, on a
swimmer, with the authors naming it as future work they did not do. **That is the citation to open with.**

⚠️ **But note what IS occupied:** surrogate-based **gait** optimization for self-propelled swimmers already
exists (Newtonian) — Abouhussein & Peet, *JCP* **482**:112038 (2023), Kriging response surface + Nek5000,
converged in <60 iterations vs 700 for an evolutionary baseline, and it even *proposes a new scaling law*
for efficiency. So the claim is **not** "first surrogate for swimmer gait optimization." It is **fixing the
failure mode those two papers report.**

Cheap companion result: **differentiable-physics gradients vs learned world models have never been
compared on the same environment**, and FluidGym ships both DPC and TD-MPC baselines on a differentiable
PyTorch solver. That head-to-head is days of work.

### One more thing not to claim

**"Learned field model in the control loop" is eight years old** — Morton et al., NeurIPS 2018
(arXiv:1805.07472): deep Koopman autoencoder over the full 128×256 field → 32-D latent → QP-MPC. The
Newtonian side has ~14 such papers, incl. *Nature Communications* (SINDy-RL) and the canonical **440×**
result (Linot, Zeng & Graham, *IJHFF* 101:109139, 2023). ⚠️ And do not cite **"Solver-in-the-Loop"**
(Um/Thuerey, NeurIPS 2020) as control — it is learned correction of solver error, no actuator, no
policy. It is the most common misattribution in this area.
