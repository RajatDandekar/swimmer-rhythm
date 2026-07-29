# Prior-art verdicts — RL / world models for swimming

Adversarial prior-art sweep run 2026-07-27. Each claim was handed to an agent instructed to
**kill** it. Verdicts: KILLED (someone did it) / WEAKENED (near-misses, narrowed daylight) /
SURVIVES (credible negative). All citations verified against arXiv `/abs/` or publisher
records by the agent, not recalled — items that could not be verified are marked.

---

## Claim 3 — "Model-based RL / world model on a fluid-immersed swimmer, latent encodes the *fluid's* state"

### Verdict: **WEAKENED — survives only in a narrow form**

The claim is a three-way conjunction: (1) Dreamer-style learned latent dynamics + (2) a
fluid-immersed swimmer + (3) latent encodes the *fluid's* internal state. **Every pair is
already published. The full triple is not. The viscoelastic variant has zero prior art.**

### Dead — do not claim these

**"First world model / Dreamer for a fluid-immersed swimmer"** — owned by:
> Medany, Piglia, Achenbach, Mukkavilli & Ahmed, "Model-based reinforcement learning for
> ultrasound-driven autonomous microrobots," *Nature Machine Intelligence* **7**(7),
> 1076–1090 (2025). doi:10.1038/s42256-025-01054-2, PMC12283351.

Uses **DreamerV3 by name**, with imagination: *"The agent generates future trajectories within
the latent space and uses these imagined trajectories to train the policy and value networks."*
Real-time microrobot manipulation in vasculature under static **and flow** conditions.
*Mitigating details:* the latent compresses **image observations only** — no explicit flow/
vorticity state; fluid is Newtonian; the microrobot is **externally actuated** (acoustic
radiation force on a microbubble cluster), not a self-propelled deforming swimmer.
**This will be a reviewer's first objection.**

**"First learned latent of a fluid field used to train an RL policy"** — owned by:
> Liu, Beckers & Eldredge, "Model-based reinforcement learning for control of strongly-disturbed
> unsteady aerodynamic flows," arXiv:2408.14685; *AIAA Journal* (2025), doi:10.2514/1.J064790.

Verbatim: *"a physics-augmented autoencoder, which compresses high-dimensional CFD flow field
snapshots into a three-dimensional latent space, and a latent dynamics model … trained to
accurately predict the long-time dynamics of trajectories in the latent space in response to
action sequences."* TD3 trained **entirely inside the latent environment**, then transferred to
full CFD. Latent contains **vorticity field**, boundary layer, wake. *Mitigating:* pitching
airfoil / wind turbine — forced, rigid, **not self-propelled**; never uses "world model".

**"MBRL for fluid flow control"** generally — a mature field. Also verified: Mao/Zhong/Yin
*Phys. Fluids* 36:083619 (2024, NODE + dimensionality reduction; publisher page 403, metadata
verified elsewhere); Ye & Elsheikh *Phys. Fluids* 37:093363 (2025, PETS + MBPO, 2–9× sample
efficiency); Weiner & Geise arXiv:2402.16543 (ensemble models, −85% training time); Zolman et
al. SINDy-RL, arXiv:2403.09110 / *Nat. Commun.* **16**:10714 (2025) — note its "Swimmer" is
**MuJoCo Swimmer, not a fluid**; Plotzki & Peitz arXiv:2603.28074 (2026, LRAN latent for
Rayleigh–Bénard); Werner & Peitz arXiv:2302.07160 (ConvLSTM for Kuramoto–Sivashinsky).

### The viscoelastic check — completely clean

Searched repeatedly and specifically. **No RL or MBRL control of a viscoelastic fluid's
conformation or stress field exists — not model-based, not model-free, not for swimmers, not
for any geometry.** What exists is modelling *without* control: CNN prediction of polymeric
stress in viscoelastic channel turbulence; ROM of a viscoelastic jet (arXiv:2604.26240);
ViscoelasticNet (arXiv:2209.06972, PINN stress discovery). Lauga's review *"Microswimming in
viscoelastic fluids," J. Non-Newt. Fluid Mech.* **297**:104655 (2021) is pure physics.

Near-miss to name carefully: *"Emergence of odd elasticity in a microswimmer using deep
reinforcement learning," Phys. Rev. Research* **6**:033016 (2024), arXiv:2311.01973 — **DQN,
model-free**, and the elasticity is a property of the **swimmer's body, not the fluid**.

### A gift for the motivation section

> Rodwell & Tallapragada, "Physics-informed reinforcement learning for motion control of a
> fish-like swimming robot," *Sci. Rep.* **13**:10754 (2023), doi:10.1038/s41598-023-36399-4.

States the exact problem verbatim: **"the vortex field is not an observed variable or state in
the training"**, and the system is **"seemingly non Markov from the perspective of the agent."**
A published, citable statement of the gap.

### Surviving framings, ranked

1. **STRONG (uncontested) — the viscoelastic variant.** A learned latent world model whose
   state encodes the **polymer conformation / elastic stress field**, used for
   planning-in-imagination to control a swimmer. Zero prior art in any bucket. The physics
   rationale is forced rather than convenient: elastic stress carries genuine memory
   (relaxation time λ), so "the latent must encode fluid internal state" follows from the
   constitutive equation. **Put the novelty claim here.**
2. **MODERATE — vorticity-history latent for a self-propelled, deforming swimmer.** The triple
   is unpublished and Rodwell & Tallapragada supplies the motivation, but Liu/Beckers/Eldredge
   has the method and Medany has the setting, so expect "incremental combination" pushback.
   Defend on physics (wake-memory non-Markovianity in *self*-propulsion, absent from a forced
   airfoil and invisible in a pixel latent), not on algorithmic novelty.

### Live competitive risks

- **Eldredge group (UCLA/Caltech)** already has the exact machinery; airfoil → self-propelled
  swimmer is their natural next paper.
- **Peitz's group** is systematically sweeping learned-latent surrogates for RL in fluids and
  moving fast (2026 preprint).

### Needs manual verification

*Ocean Engineering* (2026), PII S0029801826009959, believed "Deep reinforcement learning control
of fish locomotion via physics-guided surrogates" — a two-stage **PD-FS** framework embedding NN
surrogates as the RL environment, then refining in high-fidelity CFD. **ScienceDirect returned
403.** This is the one item that could reclassify from "fast surrogate environment" to genuine
model-based RL and narrow framing 2. Re-verification dispatched.

---

## Claim 1 — "RL for microswimmer gait discovery in Stokes flow is unexplored"

### Verdict: **KILLED** — and it takes the "exact solver" differentiator with it

Not merely explored: a small **established sub-field** with a canonical lineage, **two 2025
review articles**, and ≥6 independent groups publishing 2018–2026 (Pak/Tsang at Santa Clara +
HKU; Zhu at NUS; Zöttl/Kahl at Vienna; Komura/Ishimoto in Japan; Nejat Pishkenari at Sharif;
Guy at UC Davis). Every search angle returned direct hits.

### The canonical citations (must appear in your first paragraph if you touch this)

1. **Tsang, Tong, Nallan & Pak**, "Self-learning how to swim at low Reynolds number,"
   *Phys. Rev. Fluids* **5**, 074101 (2020), arXiv:1808.07639. The origin paper. Tabular
   Q-learning, N-sphere Najafi–Golestanian. Verbatim: *"a swimmer develops its own propulsion
   strategy based on its interactions with the surrounding medium via reinforcement learning"*
   and it *"can recover a previously known propulsion strategy without prior knowledge."*
2. **Zou, Liu, Young, Pak & Tsang**, "Gait switching and targeted navigation of microswimmers
   via deep reinforcement learning," *Commun. Phys.* **5**, 158 (2022),
   doi:10.1038/s42005-022-00935-x. Actor-critic + PPO. Oseen tensor.
3. **Qin, Zou, Zhu & Pak**, "Reinforcement learning of a multi-link swimmer at low Reynolds
   numbers," *Phys. Fluids* **35**(3), 032003 (2023), doi:10.1063/5.0140662. RL rediscovers
   **Purcell's** stroke. Resistive force theory.
4. **Xiong, Liu, Wang, Ong & Zhu**, *Nature Communications* **16**, 5441 (2025),
   doi:10.1038/s41467-025-60646-z. ⚠️ **EXACT SOLVER** — 3D boundary integral / regularized
   Stokeslets + hierarchical PPO.
5. **Bailey & Guy**, arXiv:2507.18849, *EPJ E* (2025), doi:10.1140/epje/s10189-025-00511-5.
   ⚠️ **EXACT SOLVER** — method of regularized Stokeslets + tabular Q-learning.
6. **Hartl, Hübl, Kahl & Zöttl**, "Microswimmers learning chemotaxis with genetic algorithms,"
   *PNAS* **118**(19), e2019683118 (2021). NEAT neuroevolution branch.

**Reviews that already codify it as settled:** Cai, Wang, Zhang, Qu & Huang, "Reinforcement
learning for active matter," *Biophysics Rev.* **6**, 031302 (2025), arXiv:2503.23308; Yang et
al., "Machine learning for micro- and nanorobots," *Nat. Mach. Intell.* **6** (2024),
doi:10.1038/s42256-024-00859-x.

### Every plausible novelty hook is already taken

Recover Najafi–Golestanian from scratch (Tsang 2020) · recover Purcell's loop (Qin 2023, Lai
2025, Hu & Dear 2023) · beat the classical optimum with more DOF (Tsang 2020, Qin 2023,
Jebellat 2024) · velocity- vs efficiency-optimal reward shaping (Lai 2025, Bailey & Guy 2025) ·
gait switching / run-and-tumble (Zou 2022) · multi-swimmer gait coordination (Liu 2023,
*Sci. Rep.* 13:9397) · elastic/compliant swimmers (Lin 2023, Tokoro 2025) · exotic geometries
incl. ring/amoeboid (Mozafarinia 2025, Xiong 2025) · gait adaptation to a different medium
(Tsang 2020) · confinement/constrictions (Xiong 2025) · **LLM instead of RL** (Xu & Zhu,
arXiv:2402.00044 — GPT-4 few-shot, *"substantially outperformed traditional reinforcement
learning in training speed"*).

### Also pre-empts "we found which strokes are optimal"

**Kanazawa, Ishimoto & Kawaguchi**, "Hydrodynamic origins of symmetric swimming strategies,"
arXiv:2603.08444 (Mar 2026) — **no RL**, but *proves* symmetric/anti-symmetric strokes optimal
among all strokes: *"we prove are optimal among all strokes. We validate this using numerical
simulations of Stokes flow."*

Non-RL baselines an RL paper must beat: **Tam & Hosoi**, *PRL* **98**, 068105 (2007) (canonical
Purcell optimum, plus the *Comment* at *PRL* **100**, 029801 showing better strokes exist at
large aspect ratio); arXiv:0906.4502 (boundary-integral + direct constrained minimization —
exact-solver stroke optimization since 2009, sans RL); shape optimization with exact solvers at
arXiv:2405.00656 (*SIAM J. Sci. Comput.*) and arXiv:2409.11776.

### What honestly remains (all narrow, none a headline)

- Spectral / high-order / lubrication-resolved solver as the RL environment (regularized
  Stokeslets is current SOTA). Incremental-fidelity — only interesting if it **changes the
  learned gait** vs Oseen/RFT.
- **Joint shape-and-stroke co-optimization** by RL with an exact solver. The non-RL shape-opt
  literature and the RL stroke literature exist separately; no paper does both via RL.
- **Closed-loop RL gait discovery on a real physical Stokes-regime swimmer.** All gait-discovery
  work above is in silico (Xiong et al. say so explicitly, flagging it as the known frontier —
  so others are likely already on it). Cichos's *Sci. Robotics* **6**, eabd9285 (2021) is
  experimental but *navigation*, not stroke discovery.
- Theory: proving what RL converges to / connecting RL solutions to the geometric-mechanics
  optima. **Hu & Dear (arXiv:2301.13072, deep RL *guided by geometric mechanics*) and Kanazawa
  2026 are encroaching from both sides.**

### Consequence for this project

Do **not** frame anything as "RL for microswimmer gait discovery," "RL rediscovers Purcell /
Najafi–Golestanian," or "first exact-Stokes RL environment." The §4 area-law result is still
valuable — but as a **critique and diagnostic** of why that subfield saturated, not as a
launchpad.

*Unverified, flagged for honesty:* solver details for Abdi & Pishkenari (2023) and Jebellat et
al. (2024) (ScienceDirect 403, OpenAlex abstracts null); Muiños-Landin *Sci. Robotics* (2021)
and Behrens *Adv. Intell. Syst.* (2022) verified via search metadata only (paywalls); Tsang
2020's mobility approximation not confirmed from the abstract page.

---

## Claim 5 — "Taylor's 1951 swimming sheet has never been used as an ML/RL environment, benchmark, or validation case"

### Verdict: **SURVIVES** — a credible negative, with a bigger finding attached

Base citation verified: Taylor, *Proc. R. Soc. A* **209**, 447–461 (1951),
doi:10.1098/rspa.1951.0218, ~1,059 citations (Royal Society page 403s fetchers; verified via
Semantic Scholar API).

### The searches, with index sanity checks

**arXiv API (metadata):** `all:"swimming sheet" AND all:"neural network"` → **0 results**.
`all:"swimming sheet"` → **12 total, all purely analytical/asymptotic**. `all:"Taylor sheet"`
→ 1 result, unrelated (Savart–Taylor sheet in hydraulic jumps).

**OpenAlex full text** — index sanity-checked first: `"swimming sheet"` alone → **197 works**,
so coverage is genuine, not a dead query.

| Query | Hits | Outcome |
|---|---|---|
| `"swimming sheet"` + `"neural network"` | 1 | historical background only |
| `"swimming sheet"` + `"reinforcement learning"` | 2 | historical background only |
| `"swimming sheet"` + `"symbolic regression"` | **0** | — |
| `"swimming sheet"` + `"physics-informed"` | **0** | — |
| `"swimming sheet"` + `"deep learning"` | **0** | — |

Both real co-occurrences were read and are one-line historical mentions, not benchmarks:
Mo, Li & Bian, *Front. Phys.* **11** (2023), doi:10.3389/fphy.2023.1279883; and "Roadmap for
Animate Matter," *J. Phys.: Condens. Matter* (2025), doi:10.1088/1361-648X/adebd3.

**What the ML/RL microswimmer corpus actually uses:** Purcell three-link, Najafi–Golestanian
three-sphere, slender undulating filaments, biflagellate models. **Never the Taylor sheet.**
Closest adjacent: El Khiyati, Chesneaux, Giraldi & Bec, arXiv:2302.05081 → *EPJE* (slender
deformable body) — verified it **does not cite Taylor 1951 and uses no Taylor-formula validation**.

**Reverse check — Taylor sheet as a validation case in ML-for-CFD:** the most on-target learned-
Stokes-operator paper, arXiv:2606.25075 ("Solver Exactness, Learned Flexibility: Equivariant
Boundary-Correction Operators for Stokes Flow"), explicitly motivates on microswimmer locomotion
but validates on sphere drag (6πμa), Oberbeck ellipsoid drag, manufactured Stokeslets, and BEM
ground truth — **no swimming sheet, no squirmer**.

**PDE/ML benchmark suites — full task lists fetched, not recalled:** PDEBench, PDEArena,
The Well (all 16 datasets), CFDBench → **no swimming sheet, no Stokes swimmer, no cilia/flagella**.
(Note: The Well *does* include `viscoelastic_instability` — relevant ML-ready viscoelastic data.)

### The bigger finding: fluid mechanics is absent from the *entire* equation-discovery ecosystem

Equation lists fetched and full-text searched for fluid / Stokes / viscous / viscosity /
swimming / sheet / Reynolds:

| Benchmark | Contents | Fluid mechanics? |
|---|---|---|
| **AI-Feynman / Feynman SRD** (Udrescu & Tegmark, *Sci. Adv.* 6:eaay2631) | 100 Feynman eqs + 20 bonus (Goldstein, Jackson, Weinberg, Schwartz) | **zero hits — none at all** |
| **SRBench** (NeurIPS 2021 D&B) | 116 Feynman + 14 ODE-Strogatz + 122 PMLB black-box | none |
| **LLM-SRBench** (arXiv:2504.10415, ICML 2025 Oral) | 239 problems; matsci/chem/phys_osc/bio | none |
| **NewtonBench** (arXiv:2510.07172, ICLR 2026) | all 12 laws fetched | **zero** |
| **ERBench** (arXiv:2606.09276, 2026) | 10,000 formulas | **zero** |
| **SciCode** (NeurIPS 2024 D&B) | 80 problems / 16 subfields | **no fluid-dynamics subdomain exists** |

**This is a larger gap than the one I asked about.** The opening is not "use the Taylor sheet as
an ML benchmark" — it is that *fluid mechanics has no representation in symbolic-regression
benchmarking at all*, and Taylor's sheet is close to an ideal seed case because it supplies a
**closed-form answer with a non-trivial second coefficient** (the −19/32) rather than a
numerically-optimized gait.

### Two things to get right

**The motivation, not the novelty, is the weak point.** Purcell's three-link and the
Najafi–Golestanian three-sphere *are* already used as known-answer RL test problems. A reviewer
will ask "why the Taylor sheet instead?" The answer must be the closed form: those give a
numerically-optimized gait; Taylor gives ½(kb)²[1 − 19/16 (kb)²] — an analytic target with a
second coefficient that discriminates the physics (see §2 of the README).

**Naming discipline.** Always write "**Taylor's 1951 swimming sheet**", never "the Taylor case."
*Taylor–Green vortex* and *Rayleigh–Taylor instability* are both established ML benchmarks and
invite a false-positive rebuttal.

### Useful physics papers surfaced en route

- Iqbal, Penington, Thomas & Koens, "A Taylor swimming sheet under a finite Brinkman layer,"
  arXiv:2507.16125 (2025) — asymptotic, no ML.
- "Taylor's swimming sheet near a soft boundary," arXiv:2410.02278 → *Soft Matter* (2025).
- "The Optimal Swimming Sheet," arXiv:1406.1070 — **optimization of the sheet, not ML.** Directly
  relevant to §4; check before claiming anything about optimal sheet gaits.

*Caveats:* OpenAlex indexes 197 works containing "swimming sheet" against ~1,059 citations of
Taylor 1951, and the arXiv API searches metadata only — a validation figure buried in a paywalled
ML paper cannot be excluded with certainty. One co-occurrence went unread: "Numerical Modeling of
Sperm Swimming," *Fluids* **6**(2):73 (2021), doi:10.3390/fluids6020073 (MDPI 403) — a
numerical-methods review, not an ML pipeline.

---

## Claim 4 — "RL for undulatory swimming at finite Reynolds number is unexplored"

### Verdict: **SURVIVES in the near-Stokes band — and the gap is ~3 orders of magnitude wide**

The literature exists but sits *entirely* at high Re. Every Reynolds number below was verified
against source PDFs / abstract pages, with the defining formula recorded:

| Paper | Re for the **RL** task | Solver | Algorithm |
|---|---|---|---|
| Gazzola, Hejazialhosseini & Koumoutsakos, *SIAM J. Sci. Comput.* **36**(3):B622 (2014) | **Re_fish = 550** (both RL tasks) | 2D remeshed vortex + Brinkman penalization, wavelet-adaptive | tabular 1-step Q-learning |
| Gazzola, Tchieu, Alexeev, de Brauer & Koumoutsakos, *JFM* **789** (2016), arXiv:1509.04605 | **none — inviscid** (self-propelling vortex dipoles, Biot–Savart) | — | Q-learning + CMA-ES |
| Novati, Verma, Alexeev, Rossinelli, van Rees & Koumoutsakos, *Bioinspir. Biomim.* **12**:036001 (2017), arXiv:1610.04248 | **Re = 2250** (dragged rigid) / **5000** (self-propelled + RL follower) | 2D NS velocity–vorticity, remeshed vortex | tabular Q-learning, γ=0.8 |
| Verma, Novati & Koumoutsakos, *PNAS* **115**(23):5849 (2018), arXiv:1802.02674 | **2D Re ≈ 5000** | 2D wavelet vortex; 3D FD pressure-projection (CUBISM/AccFFT) | async recurrent DQN + LSTM |
| Zhu, Tian, Young, Liao & Lai, *Sci. Rep.* **11**:1691 (2021) | **Re = 1000** (all three RL tasks) | IB-LBM | DRQN |
| Jiao, Ling, Heydari, Heess, Merel & Kanso, *Phys. Rev. Fluids* **6**:050505 (2021), arXiv:2009.14280 | **none — potential (inviscid) flow** | — | PPO |

**Lowest Re anywhere in the Navier-Stokes-resolved RL-swimming literature: Re = 550**
(Gazzola 2014, chosen *"because of biological relevance to larval anguilliform swimmers"*).
The full set is **{550, 1000, 2250, 5000, 7143}**. **Nothing below Re ≈ 100.** Sub-100 RL
swimming exists only at the opposite extreme — the Stokes limit, Re = 0 (Tsang et al.,
*Phys. Rev. Fluids* **5**:074101, 2020; see Claim 1).

### The consequence — the gap is the transition region

```
Re = 0            Re ~ 0.1 – 10          Re >= 550
Stokes            THE GAP                fish / larval
saturated         nothing at all         saturated
(Claim 1)                                (this claim)
```

RL-for-swimming is worked out at both ends and **absent across the middle** — which is
precisely the band where the physics of interest lives:

- **Re = 0:** scallop theorem holds, area law exact, MDP degenerate (measured in §4 of README:
  1e-18 zeros, shape-independence to 4 digits).
- **Re ~ 0.1–10:** the scallop theorem *first breaks*, reciprocal strokes begin to produce net
  motion, rate-independence dies. This is where sequential structure **emerges**.
- **Re ≥ 550:** fully inertial, thoroughly studied.

So the natural question — *at what Reynolds number does an RL policy first beat the geometric
optimum, and by how much?* — has no answer in the literature, because nobody has looked in the
band where the answer is non-trivial. The §4 area-law measurement is the right instrument:
**departure from the area law is a direct measure of how much there is to learn.**

This also makes the O(Re) perturbation extension the cheapest high-value build: expand
`u = u₀ + Re·u₁ + …` on the existing spectral basis, where `u₁` solves a *linear* Stokes-like
problem forced by the inertial term evaluated on `u₀`. Keeps the millisecond cost, and lands
exactly in the empty band.

### Corrections to earlier assumptions

- **Novati, Mahadevan & Koumoutsakos, *Phys. Rev. Fluids* **4**:093902 (2019)** is **not
  swimming and not Navier–Stokes** — a 2D gliding/perching ellipse with a quasi-steady ODE force
  closure, only *"consistent with Reynolds numbers Re ~ O(10³)"*. RL = RACER vs PPO.
- **Brunton, Noack & Koumoutsakos, *Annu. Rev. Fluid Mech.* **52**:477 (2020) does NOT survey Re
  ranges for RL swimming** — all 12 "Reynolds" mentions are RANS / Reynolds-stress / high-Re
  turbulence. Do not cite it for that.
- ⚠️ **Trap:** in Gazzola et al. *JFM* 789 (2016), the `Re[·]` appearing in the equations is the
  **real-part operator, not a Reynolds number**.
- ⚠️ **Do not cite** arXiv:2209.10935 ("Learning swimming via deep RL", Zhang, Zhou & Cao) — a
  physical water-tunnel experiment (NACA0012 + VAE + PPO, Re_c = 13500), but the arXiv comment
  states *"We found some errors in the experimental data"* and **v2 was withdrawn**.

*Still open:* Yu, Liu, Wang, Liu, Lu & Huang, *Phys. Rev. E* **105**:045105 (2022) and Zhu & Pang,
*Proc. IMechE C* **237**:2450 (2023) — Re not stated on landing pages, full-text hunts running.
Neither is likely to be sub-100, but not assumed.

---

### Claim 4, second independent pass — SURVIVES, conditional on three framing moves

Confirms the bimodal gap, adds the verified floor and a crucial structural insight.

**The verified Re floor for RL of a deforming body in full Navier–Stokes is 100, not 550:**
> Chen & Yang, "Deep reinforcement learning for tracking a moving target in jellyfish-like
> swimming," *JFM* (2025), arXiv:2409.08815. **Re = 100** (verified in arXiv HTML). DQN, IBAMR
> immersed boundary + AMR.

So the category "RL + deforming body + finite Re + flow memory" is **not** new. What is empty is
**0 < Re < 100**, the scallop-theorem/rate-dependence framing, and **gait discovery** (Chen & Yang
do target tracking with a prescribed torsional-spring muscle model).

**🔑 The best structural insight from the whole sweep: both regimes RL has occupied are
rate-independent.** Stokes is geometric by construction (see §4 of README). And Jiao, Ling,
Heydari, Heess, Merel & Kanso, *Phys. Rev. Fluids* **6**:050505 (2021), arXiv:2009.14280 —
RL for a three-link fish in **potential flow**, where inertia not viscosity propels — describes
itself verbatim as *"a class of problems in geometric mechanics, known as **driftless dynamical
systems**, which allow us to analyze the swimming behavior in terms of **geometric phases over the
shape space**."* That is the *same* degenerate structure as Stokes, at the opposite pole.
**RL has been applied at both ends of the degenerate spectrum and never in the memory-bearing
middle.** Clean and quotable, and it independently corroborates §4's argument.

**The single most damning fact for the field, i.e. the best motivation for us:** Klotsa's group
mapped the *same* metachronal paddler across **Re = 0.05–100** (Nguyen & Klotsa, arXiv:2108.00095;
swim speed **non-monotonic in Re**, max near Re ≈ 1, flat min at Re = 20–30). When RL was finally
applied to that geometry in 2025 (Bailey & Guy), the authors ran it at **Re = 0**. The obvious
experiment — put the learner in the band where the speed is non-monotonic — has not been done.

**⚠️ Three mandatory framing moves**

1. **Never write "intermediate Reynolds number."** It already means Re ≈ 550 in the fish/CFD
   community (van Rees, Gazzola & Koumoutsakos, *JFM* **722**:R3, 2013) and Re ~ 1–1000 in the
   Klotsa community. Write **"Re = O(1)", "near-Stokes inertial", or "mesoscale."**
2. Explicitly distinguish from Chen & Yang 2025 (Re = 100, tracking not gait discovery) and Jiao
   et al. 2021 (inertial but driftless).
3. **Stay out of the small-amplitude regime.** Derr, Dombrowski, Rycroft & Klotsa, *JFM* **952**:A8
   (2022), doi:10.1017/jfm.2022.873 already give a *general* small-amplitude asymptotic theory at
   intermediate Re with an explicit swim-speed decomposition (slip velocity + Reynolds stresses).
   Verbatim: *"In Stokes flow, Purcell's scallop theorem forbids objects with time-reversible
   (reciprocal) swimming strokes from moving. In the presence of inertia, this restriction is eased
   and reciprocally deforming bodies can swim."* An RL result in the small-amplitude few-DOF corner
   reads as "RL rediscovers known asymptotics." Go large-amplitude / many-DOF / multi-objective.

**🚨 Vehicle warning — this bites our plan.** *"An infinite sheet has an impoverished action space
(one wave, nothing to sequence). A reviewer can fairly ask why that model demonstrates a
sequential decision problem. A multi-paddle or multi-link body at Re ~ 1 is the defensible
vehicle."* The Taylor sheet is the right **validation** case, not the right **RL** case.

*Low barrier ⇒ scoop risk:* IBAMR, IB-LBM and smoothed-profile all run at Re ~ 1; Klotsa owns the
physics, Guy owns the RL. This is "nobody has done it yet," not "hard to do."
*Unresolved:* Sankaewtong, Molina, Turner & Yamamoto, *PRE* **107**:065102 (2023), arXiv:2212.11482
(+ *POF* 36:041902, *PRResearch* 6:033305, 2024) — RL + DNS smoothed-profile, Re not stated,
APS/AIP blocked. But a non-deforming squirmer doing navigation — no stroke, no gait.
*Taylor sheet at finite Re (no ML anywhere):* Reynolds (1965); **Tuck, *JFM* 31:305 (1968)**;
Felderhof, arXiv:1507.01186.

---

---

## Claim 2 — "RL for a swimmer in a viscoelastic fluid is unexplored" (THE LOAD-BEARING CLAIM)

### Verdict: **SURVIVES — the method↔fluid cell is genuinely empty — but three sub-claims are WEAKENED and there is a live scoop risk**

### The negative is clean and quantified

**RL has never been coupled to *any* viscoelastic constitutive model in fluid mechanics** — not
swimmers, not polymer drag reduction, not elasto-inertial turbulence.

| Query | Result |
|---|---|
| arXiv `abs:"reinforcement learning" AND abs:"viscoelastic"` | **2 total**, both irrelevant (metamaterial design 2408.06300; stiff contact sim 2101.06846) |
| arXiv `abs:"viscoelastic" AND abs:"swimmer"` | **40**, all analytical/numerical/experimental — **zero** learning |
| arXiv `abs:"reinforcement learning" AND microswimmer` | **24**, all Newtonian/turbulent/Brownian — **zero** viscoelastic |
| arXiv `"reinforcement learning" "Oldroyd-B"` | **0** |
| arXiv `"reinforcement learning" "polymer solution"` | **0** |

Corroborated by two dedicated reviews: Mo, Li & Bian, *Front. Phys.* **11** (2023) states
verbatim *"The non-Newtonian feature of the biological fluids, the elasticity of the
microswimmers, and the tortuous elastic boundaries are often not taken into account."* And Cai
et al., *Biophysics Rev.* **6**:031302 (2025) — full text contains **zero** occurrences of
viscoelastic / non-Newtonian / polymer / complex fluid / Oldroyd / shear-thinning.

### ⚠️ WEAKENING 1 — the idea is already in print as an anticipated next step

Same review (Mo, Li & Bian 2023), verbatim:
> *"we anticipate that an intelligent microswimmer needs to mitigate or even exploit the effects
> of viscoelasticity by **modifying its propulsion gait** so that its navigation ability can be
> enhanced."*

It even names the geometry: *"It is known that a Taylor sheet swims slower in viscoelastic fluids
than in Newtonian fluids."* Nobody executed it — but expect **"obvious extension"** from a
referee. **Cite this review yourself** rather than let a referee produce it.

### ⚠️ WEAKENING 2 — the *question* has an analytical owner

> Elfring & Goyal, "**The effect of gait on swimming in viscoelastic fluids**,"
> *J. Non-Newtonian Fluid Mech.* **234**, 8–14 (2016), doi:10.1016/j.jnnfm.2016.04.005,
> arXiv:1511.06386.

The title *is* the question. Reciprocal-theorem analysis of small-amplitude deformations of a
**two-dimensional sheet**, deriving when it swims faster or slower than Newtonian; key result
*"speed increase can only be realized by multiple deformation modes."* **Do not claim
"discovering that gait matters in a viscoelastic fluid."** Mitigation: it is perturbative and
small-amplitude; non-perturbative gait *discovery* is open.

Also exactly our system: Lauga, "Propulsion in a viscoelastic fluid," *Phys. Fluids* **19**,
083104 (2007) — *"a waving sheet of small amplitude free to move in a polymeric fluid with a
single relaxation time"*; U/U_N = [1+De²η_s/η]/[1+De²]. And Thomases & Guy, *JFM* (2017),
doi:10.1017/jfm.2017.383 — Stokes–Oldroyd-B, finite-amplitude, but actuation held fixed.

### ⚠️ WEAKENING 3 — the "memory ⇒ sequential decision problem" framing is taken

> Lin, Yasuda, Ishimoto & Komura, "Emergence of odd elasticity in a microswimmer using deep
> reinforcement learning," *Phys. Rev. Research* **6**, 033016 (2024), arXiv:2311.01973.

Fluid is **Newtonian** (verified from full text: Stokes mobility + Oseen tensor; elasticity is in
**springs between spheres**). But it already (i) has cross-stroke memory, (ii) argues RL is needed
because the sequential problem is hard, and (iii) discovers a history-dependent **"waiting"**
strategy. A referee will use it against the framing.

### 🚨 LIVE SCOOP RISK — a paper five days old partially scoops the headline physics

> Gupta & Dey, "**Fluid Memory Enhances Active Beating via Back-and-Forth Motion**,"
> arXiv:2607.19820, submitted **22 July 2026**.

Jeffreys fluid, **no ML, no optimization** — analytical. Verbatim: *"back-and-forth beating
transiently aligns the driving and polymeric forces, leading to a rapid increase in the beating
frequency once the fluid memory becomes comparable to the stroke duration"*, identifying
back-and-forth beating as *"a generic mechanism for exploiting fluid memory in active
oscillators."*

**That is the headline physics finding — a non-obvious stroke that exploits fluid memory —
obtained analytically, five days ago.** It does not kill the RL claim, and it is arguably a gift
as motivation (someone else established the regime matters). But it means the window is closing
and the "surprising result" has partly been claimed.

### Competitive threat, named

**Lailai Zhu's group is the dangerous one.** Zhu is a co-author on *both* the exact-solver RL
paper (Xiong et al., *Nat. Commun.* 16:5441, 2025 — see Claim 1) *and* the multi-link RL paper
(Qin et al. 2023), and the group's stated programme is understanding *"the effectiveness of
different swimming gaits in various types of complex fluids."* That is exact-solver RL + complex
fluids + the stated intent. **On Shun Pak's** group publishes both halves separately.

### Feasibility — good news

> Neal & Bearon, "A computational approach to simulating a three-sphere swimmer in a viscoelastic
> fluid modelled via the Giesekus constitutive law," *Phil. Trans. R. Soc. A* **383**(2304),
> 20240268 (11 Sep 2025).

The canonical RL testbed swimmer in a Giesekus fluid, hybrid Newtonian-solution + FEM correction,
reporting *"enhancements in swimming speed and efficiency of up to 7 and 16%, respectively."*
**The environment a viscoelastic-RL paper needs already exists in the literature.**

### Surviving daylight, ranked — defend on these, not on "first RL swimmer"

1. **First learned policy of any kind in a viscoelastic swimmer.** Uncontested and unusually
   clean (RL has touched no viscoelastic constitutive model in fluid mechanics at all).
2. **Polymer conformation tensor in the policy's observation.** No prior work puts the polymer
   stress/conformation field into a policy's state. **Strongest and most specific — lead here.**
3. **Finite amplitude, fully nonlinear.** Lauga 2007 and Elfring & Goyal 2016 are perturbative.
4. **Transients / stroke-to-stroke scheduling at De ~ O(1)** rather than periodic steady state —
   the regime Gupta & Dey just showed matters. Be first to *optimize* there.

**Drop:** "gait matters in viscoelastic fluids" (Elfring & Goyal own it) and "memory makes it a
genuine sequential decision problem" (Lin et al. own it).

*Also verified negative:* Qiu et al., *Nat. Commun.* **5**:5119 (2014) micro-scallop breaks the
scallop theorem via **rate-dependent viscosity, not memory** — no learning. Only two RL-in-
viscoelastic papers exist anywhere and both are far away: inkjet waveform control (Kim, Cho &
Jung, *Langmuir* **41**:10831, 2025) and a dielectric-elastomer **solid** actuator (IEEE RA-L 2019).

### Claim 2, second independent pass — CONFIRMS, with one hit that narrows the wording

A second agent re-ran Claim 2 with a different method and reached the same conclusion. Two
additions matter.

**A citation-network test — the strongest form of the negative.** Any RL paper working in a
viscoelastic fluid would almost certainly cite Lauga 2007 or Teran–Fauci–Shelley 2010. Of the
**340 works citing Lauga, *Phys. Fluids* 19:083104 (2007)**, the Mo/Li/Bian review is the *only*
one whose title/abstract mentions "reinforcement learning." Of Tsang et al. (2020)'s **68
citations**, only 3 mention viscoelastic/non-Newtonian and **none uses RL**. This is far stronger
than keyword search, which can only ever show absence of a phrase.

**⚠️ One genuine (a)-class hit exists — "first ever" is no longer available.**
> Huynh & Nguyen, "Learning control of micro-robots in vascular systems," *Engineering Research
> Express* **8**(13), 135205 (2026), doi:10.1088/2631-8695/ae7ecd.

Verbatim: *"complex haemodynamics, **non-Newtonian blood flow**, and highly dynamic obstacles"*;
*"A Unity-based simulation platform that replicates **pulsatile non-Newtonian blood flow**."*
It literally satisfies RL + swimmer + non-Newtonian fluid. **But** it is *navigation*, not gait
design; the non-Newtonian property is a background-flow **viscosity model inside a game engine
(Unity)**, not a polymer-stress field coupled to the swimmer's deformation; the agent judged
"turbulence-aware RL at capillary scale" physically questionable; low-visibility venue.

**Consequence — word the claim as:** *first learned policy for a swimmer in a fluid with a
**viscoelastic constitutive model**, with the **polymer conformation/stress field in the
observation***. Not "first RL swimmer in a non-Newtonian fluid." Cite Huynh & Nguyen to show you
know it.

**Closest high-quality adjacent work:** Amoudruz, Litvinov & Koumoutsakos, arXiv:2404.02171 — RL
navigation of magnetic microswimmers in blood capillaries with deformable RBCs, so the *bulk*
rheology is non-Newtonian. But verified from full text: *"Both plasma and cytosol are **viscous
Newtonian fluids**"* (DPD). A complex *suspension*, not a viscoelastic continuum.

**New trap ruled out:** Singh & Choudhary, arXiv:2604.27348 (Apr 2026), "Propulsion and far-field
hydrodynamics of linked-sphere microswimmers with **viscoelastic deformability**" — the
viscoelasticity is a **Kelvin–Voigt body** in a Newtonian fluid, and there is **no learning at
all**. Title is a false positive.

**Second named competitor: Ardekani's group.** They publish *both* ViscoelasticNet (PINN for
Oldroyd-B / Giesekus / linear PTT stress, *JNNFM* 2024, doi:10.1016/j.jnnfm.2024.105265,
arXiv:2209.06972) *and* microswimming in viscoelastic fluids — *"yet the two lines were never
joined."* Along with Lailai Zhu's group, that is two teams holding both halves.

**Fuller version of the open-problem quote** (Mo, Li & Bian 2023) — cite this verbatim:
> *"we anticipate that an intelligent microswimmer needs to mitigate or even exploit the effects
> of viscoelasticity by modifying its propulsion gait so that its navigation ability can be
> enhanced. **However, to understand how the biological microswimmers adapt themselves to
> different complex fluidic structures and to discover smart gait-switching strategies for
> synthetic microswimmers are still open questions.**"*

**Also useful:** Mecanna, Loisy & Eloy, "A critical assessment of reinforcement learning methods
for microswimmer navigation in complex flows," *EPJ E* **48**:58 (2025), arXiv:2505.05525 — a
critical-assessment paper worth reading before choosing an algorithm. Its "complex flows" are
Taylor–Green / ABC / 2D turbulence, i.e. Newtonian. And Xu & Zhu's LLM-as-policy work is now
published: *Phys. Rev. Applied* **23**, 044058 (2025).

**Angles explicitly returning zero:** `all:"Oldroyd" AND all:"reinforcement learning"` → 0;
`abs:"reinforcement learning" AND abs:"non-Newtonian"` → 0; OpenAlex `"reinforcement learning"
AND "shear-thinning"` → 0; FENE-P/Giesekus + RL swimmer → nothing; APS DFD abstracts → nothing;
theses → nothing; sperm/cilia RL in mucus → nothing (RL sperm papers Newtonian, viscoelastic
mucus papers use no learning); macroscopic robotic fish in non-Newtonian → nothing; evolutionary/
Bayesian gait optimization in viscoelastic → nothing.

*Method caveat carried forward:* arXiv API searches metadata only; OpenAlex abstract coverage is
null for many Elsevier/RSC records — which is exactly why the citation-network test matters.

---

## Claim 6 — "Symbolic regression on an optimizer's/RL loop's output to get a scaling law vs a dimensionless group"

### Verdict: **WEAKENED** — survives literally, squeezed from both sides

**Both halves are independently well-precedented, so only the composition is new.**

**Side 1 — SR on optimizer output is an established move.** Segel et al., "Symbolic explanations
for hyperparameter optimization," AutoML 2023, PMLR v224: *"We propose to apply symbolic regression
to meta-data collected with Bayesian optimization (BO) during HPO."* Also Diveev et al.,
*Mathematics* **12**(22):3595 (2024) — SR over a family of optimal trajectories → feedback law
(exactly our nesting order, wrong output type); Wu, Zhang & Zhang, *AIAA J.* (2024),
doi:10.2514/1.J064416 (SR on an adjoint field-inversion optimum).

**⚠️ Most dangerous single paper:** Botteghi & Fasel, "Parametric PDE control with deep
reinforcement learning and differentiable L0-sparse polynomial policies," arXiv:2403.15267 (2024).
The policy dictionary explicitly contains the swept PDE parameter, and they print learned laws like
`a₄ = tanh(−7.524m₄ + 0.226m₃² − 2.128m₃m₇ − 2.659m₈μ − 0.691m₁μ² − 0.317μ³)`. I.e. **a closed-form
optimal control law as an explicit function of a swept physical parameter, from an RL loop.**
*Why it doesn't kill:* μ is a dimensional PDE coefficient, not a named dimensionless group; the
method is L0 dictionary regression *inside* the policy, not post-hoc free-form SR; and the output is
a parameter-conditioned feedback law, not a scaling law of an optimum (no exponent).

**Side 2 — "scaling law for the optimum vs a dimensionless number" is a mature program, done by hand.**
- Hassanzadeh, Chini & Doering, "Wall to wall optimal transport," *JFM* **751** (2014),
  arXiv:1309.5542: *"Nu_MAX ~ Pe and **Γ_opt ~ Pe^(−1/2)**"* — a scaling law for the optimal
  **design**, solved variationally at many Péclet numbers. Our exact construct, minus SR, in 2014.
  Continued by Tobasco & Doering; Souza, Tobasco & Doering.
- **Pak & Lauga, "Pumping by flapping in a viscoelastic fluid," *PRE* 81:036312 (2010),
  arXiv:1002.4634** — an **optimal Deborah number** with De³ and 1/De asymptotics **already exists
  analytically.** Directly on our target.
- ⚠️ **Zhu, Kang, Tong, Ma, Tian & Fan, *JFM* **1006** (2025), doi:10.1017/jfm.2025.45** —
  DRL + IB-LBM zebrafish: *"Furthermore, we **derive scaling laws** governing the swimming
  performance of trained fish."* **Scaling laws for the output of an RL loop, in JFM, 2025.**
  Closest in spirit; must be addressed head-on. (Hand-derived, not SR; full text not obtained.)
- Murari et al., *Nucl. Fusion* **56**:026005 (2016) — SR → scaling laws in dimensionless
  quantities, a decade old, on the ITPA multi-machine database.

**Class (c) policy distillation is always at ONE parameter value** (SINDy-RL at fixed Re = 1000;
Castellanos et al. *POF* 34:047118 at Re = 100; Landajuela et al. ICML 2021). And Girard,
"Dimensionless policies based on the Buckingham π theorem," *Mathematics* **12**(5):709 (2024),
arXiv:2307.15852, builds numerically tabulated **dimensionless** optimal policies and **does not
apply SR** — the gap sits precisely there.

**Class (d) GEP/SpaRTA turbulence closure has the nesting INVERTED:** in CFD-driven GEP, *SR is the
optimizer and CFD is the fitness evaluator* — [SR search] ⊃ [PDE solve]. Ours is [SR fit] ∘ [set of
optimizations]. And Re enters as training cases for a single Re-*invariant* closure — the opposite
design intent.

### The exact surviving gap

1. **SR + Deborah / Weissenberg is virgin territory** — repeated searches returned **zero** SR
   papers in elasticity numbers, only analytical/asymptotic work. **Strongest part of the claim.**
2. **SR on an argmin family**, not a forward response surface (all class-(b) work) or a closure
   (all class-(d) work).
3. **Optimal *design* vs the parameter**, not just optimal performance — Doering et al. did
   Γ_opt ~ Pe^{−1/2} analytically; nobody has done the automated-discovery version.

Three defences any writeup must carry: vs **Botteghi & Fasel** (dimensionless framing + law-of-the-
optimum, not parameter-conditioned feedback); vs **Zhu et al. JFM 2025** (automated discovery of the
functional form vs hand-fitting); vs **Hassanzadeh/Doering 2014 + Murari 2016** (concept and tool
each predate us by a decade — only the composition is new).

---

### Claim 4, THIRD independent pass — the Re question is now fully resolved

Most rigorous of the eight. Resolves the two items earlier passes left open and hardens the negative.

**The open Sankaewtong question — ANSWERED, and it does not compete.**
> Sankaewtong, Molina, Turner & Yamamoto, "Learning to swim efficiently in a nonuniform flow
> field," *Phys. Rev. E* **107**, 065102 (2023), arXiv:2212.11482.

Verbatim: *"we combine deep reinforcement learning with direct numerical simulations to resolve the
hydrodynamics"*; and from Methods: *"corresponds to a Reynolds number of Re ≈ 1 … the swimmer is set
to be a puller … corresponding to a particle Reynolds number of Re ≈ 6 × 10⁻², comparable to that of
E. coli in water."* Smoothed-Profile method with the advective term retained; deep Q-learning.
**This is the lowest Re of any RL-swimming paper with a real Navier–Stokes solver.** But: a
**fixed-slip squirmer** (B₁ constant, no deformation), the action is an **external steering torque**,
and the task is orientation control in a zig-zag shear flow. Decisive: *fluid inertia is present in
the solver but is not the resource the policy exploits — the same policy would work at Re = 0.*

**New data point:** Chen & Yang, arXiv:2511.04156 (2025), SAC + IBAMR — has a **Re = 10** point, but
only as a single fixed-policy sensitivity probe (trained at Re = 100): *"The swimmer at Re=10 has a
larger deflection angle and moves at a significantly lower speed than those at Re=100."* Companion:
*JFM* **1017** A18 (2025), doi:10.1017/jfm.2025.10470.

**⚠️ Scope correction: Re = 100 IS occupied**, so "first RL swimming at Re ≤ 100" is false. Clean
claims are: *learning a **gait*** at Re < 100; a **Re sweep across the viscous–inertial crossover**;
or **Re < 10 with a real NS solver and a deforming body** — that last one is entirely unclaimed.

**Hard negatives — direct arXiv abstract-field census**

| Query | Result |
|---|---|
| `"reinforcement learning"` + `"finite Reynolds"` | **0** |
| `"reinforcement learning"` + `squirmer` | **0** |
| `"reinforcement learning"` + `inertia` + `swim` | **0** |
| `"reinforcement learning"` + `"intermediate Reynolds"` | **exactly 1** — Ren, Rabault & Tang, arXiv:2006.10683, a *cylinder wake at Re = 1000*, not a swimmer |
| `"reinforcement learning"` + `"microswimmer"` | 22 (2017–2026) — **none** a deforming swimmer whose propulsion depends on fluid inertia |
| `"inertial swimmer"` OR `"inertial squirmer"` OR `"mesoscale swimmer"` | 11 — **zero** using ML *or* optimization |

Survey corroboration: Mecanna, Loisy & Eloy, arXiv:2505.05525 contains **zero** occurrences of
"Reynolds" or "inertia" (*"an inertialess point-like particle"*); Cai et al., *Biophysics Rev.*
**6**:031302 (2025) has no Reynolds-regime discussion and **does not even flag this as an open gap.**

**The split, sharpened — and neither side mentions the other.** Nguyen & Klotsa (arXiv:2108.00095)
swept **Re = 0.05–100** on a metachronal paddler with NS + immersed boundary, no learning. Bailey &
Guy (*EPJ E* 48:48, 2025) applied RL to the **same paddler, same paddle-spacing sweep, same
question** — at **Re = 0**, with regularized Stokeslets. And they **do not flag nonzero Re even as
future work.**

**🎁 Non-RL optimization at finite Re is thin, analytic, and gives us validation targets**
- **Felderhof, "Swimming of a deformable slab in a viscous incompressible fluid with inertia,"
  *Phys. Rev. E* **92**, 063014 (2015), arXiv:1507.01186.** Verbatim: *"The swimming of a deformable
  planar slab in a viscous incompressible fluid is studied on the basis of the Navier-Stokes
  equations. A continuum of plane wave displacements … allows optimization of the swimming
  efficiency with respect to polarization."* **A sheet-like body at finite Re with an analytic
  optimum — i.e. a known-answer validation target for a finite-Re sheet solver**, optimized over
  only *one scalar* (polarization angle).
- Felderhof & Jones, *Physica A* **202**(1–2):94–118 (1994) — NS perturbation in stroke amplitude to
  second order, defines a finite-Re swimming efficiency.
- Yang & Hatton, RSS 2025 (arXiv:2504.19072) and ICRA 2025 (arXiv:2409.15220) — geometric gait
  optimization, but **Morison's equation, not Navier–Stokes**, and "intermediate Re" in the robotics
  (fish-scale) sense.

**Conclusion:** *"the intermediate-Re gait has been optimized only analytically, only at small
amplitude, and only over one or two parameters. No black-box, gradient-free, or learned search has
ever been run there."*

**Useful distinction:** Tokoro, Takayama, Deguchi, Zöttl & Matsunaga, arXiv:2511.00816 (*PRF* 2026,
doi:10.1103/sbcw-q33d) uses PPO and finds timescale-dependent optima — but verbatim *"the
hydrodynamic model based on the Stokes equations"*; its rate dependence comes from **discrete
actuation intervals, not flow memory.** Do not confuse with genuine inertial rate-dependence.

*403-blocked, unverified:* *PRResearch* 6:033305; *POF* 36:041902; bioRxiv 10.1101/2025.07.14.664791.
arXiv API intermittently 429'd — read the census as thorough, not provably exhaustive.

---

### Claim 4, FOURTH pass — two carve-outs that must be stated, and the exact untouched question

**⚠️ CARVE-OUT 1: analytic stroke optimization *with fluid inertia* already exists.**
> Felderhof & Jones, "Swimming of a sphere in a viscous incompressible fluid with inertia,"
> *Fluid Dynamics Research* **49**(4), 045510 (2017), arXiv:1512.04667.

Genuine stroke optimization spanning Stokes → inertia-dominated. Verbatim: *"Optimization of the
mean swimming velocity for given rate of dissipation requires the solution of a **generalized
eigenvalue problem** involving the two matrices. It is found for surface modulations of low
multipole order that the optimal swimming efficiency depends in intricate fashion on a
dimensionless scale number involving the radius of the sphere, the period of the cycle, and the
kinematic viscosity."* **So "first to optimize a gait with fluid inertia" is FALSE.**
*Its limits:* small-amplitude perturbative, a squirming **sphere** (not jointed/multi-body), no
CFD, no learning, and inertia enters via a "scale number" rather than a resolved Re sweep.
Companion sweep paper (no optimization): arXiv:1803.02104, *Eur. J. Mech. B/Fluids* (2019).

**⚠️ CARVE-OUT 2: the Stokes→inertial sweep has an owner, who explicitly froze the stroke.**
> Chisholm, Legendre, Lauga & Khair, "A squirmer across Reynolds numbers," *JFM* **796**, 233–256
> (2016), doi:10.1017/jfm.2016.239. **Re = 0.01 to 1000, DNS of Navier–Stokes.**

Verbatim: *"A squirmer with a **fixed swimming stroke** and fixed swimming direction is
considered."* They compute power and efficiency, compare pushers vs pullers — and never optimize
the slip profile, never ask how an optimal gait reshapes with Re.

### 🎯 The exact untouched question

**Nobody has swept Re from Stokes into the inertial regime and asked how the *optimal gait itself*
deforms.** Chisholm et al. (Re 0.01–1000) froze the stroke. Nguyen & Klotsa (Re 0.05–100) fixed the
phase lag at π/2 and grid-swept two parameters. Bailey & Guy learned the gait — at Re = 0.
**Nobody has closed the loop.**

Defensible framing: *first **learned / large-amplitude / non-perturbative** gait optimization on a
**multi-body** swimmer with **resolved Navier–Stokes** across an **explicit Re sweep**.*

### 🎁 A theory citation that directly supports the area-law diagnostic

> Kvalheim, Bittner & Revzen, "Gait modeling and optimization for the perturbed Stokes regime,"
> *Nonlinear Dynamics* (2019), arXiv:1906.04384, doi:10.1007/s11071-019-05121-3.

Verbatim: *"In the 'perturbed Stokes regime' where inertial forces are still dominated by
viscosity, but are not negligible (low Reynolds number), we show that motion is still governed by a
functional relationship between shape velocity and body velocity, but **this function is no longer
linear in shape change rate**."* That is the theoretical statement of exactly the transition the
area-law diagnostic measures — the geometric/linear structure breaking as inertia enters. Cite it.
(Reduced-order singular perturbation parameterized by inertia-to-damping ratio, not resolved NS;
hardware-in-the-loop optimization, no ML, no Re sweep of an optimal gait.)

### Klotsa's group produced no ML follow-up — confirmed

The intermediate-Re swimmer line runs 2015 → 2022 and stops; 2024–25 output is active Brownian
particle mixtures and septin/membrane biophysics. **No title in the record mentions learning,
optimization, neural networks, or AI.** Lineage verified: *PRL* **115**:248102 (2015);
*PRFluids* **4**:021101 (2019); *PRFluids* **5**:063103 (2020); *Soft Matter* **15**:8946 (2019)
perspective; arXiv:2108.00095 (2021); *PRFluids* **7**:074401 (2022); *JFM* **952**:A8 (2022).

Second group in the regime, also no optimization: Hubert, Trosman, Collard, Sukhov, Harting,
Vandewalle & Smith, *PRL* **126**:224501 (2021); Ziegler et al., arXiv:2311.03269 (uses the *word*
"optimized" — the mechanism is mechanical resonance, no optimization performed).

**Bailey & Guy is the single most dangerous adjacent paper** — same organism motivation as
Nguyen & Klotsa — but Stokes-only, and **nonzero Re is not listed even as future work** (their
stated future work: bending paddles, deep Q-learning, actor-critic for continuous actions).

### More hard negatives

| Query | Total |
|---|---|
| `all:"scallop theorem" AND all:"reinforcement learning"` | **0** |
| `abs:"intermediate Reynolds" AND abs:swimmer AND abs:optimal` | **0** |
| `abs:"reinforcement learning" AND abs:"Reynolds number" AND abs:swimmer` | 5 — **zero** at intermediate Re |
| `abs:"intermediate Reynolds numbers" AND abs:swimmer` | 7 — **none** uses learning or optimization |

**Terminology, restated because it will cost a paper:** Klotsa/Lauga mean Re ~ 0.01–100 (scallop
theorem breaking); van Rees, Gazzola & Koumoutsakos (*JFM* **722**:R3, 2013 — CMA-ES **shape**
optimization, "intermediate Reynolds numbers" literally in the title) and the geometric-mechanics
roboticists mean Re ~ 10²–10⁵. **Define the band numerically every single time.**

---

## Claim 7 — "Learned conformation/stress-field model inside a control loop"

### Verdict: **SURVIVES** — zero papers. Plus the feasibility answer.

**Nobody puts a learned model of the polymer conformation/stress *field* inside a control or
policy-optimization loop.** Four independent arXiv full-text sweeps came back empty:
`"viscoelastic"+"reinforcement learning"` → 2 irrelevant; `"elastic turbulence"+"machine learning"`
→ **0**; `"viscoelastic"+"flow control"` → 3, none implements a controller; `"conformation tensor"`
→ 79 hits, only 5 involve ML, **none does control**.

**The two best-positioned groups each explicitly stopped short:**
- Balasubramanian, Vinuesa & Tammisola, *JFM* **1009** (2025), doi:10.1017/jfm.2025.240,
  arXiv:2404.14121 — learns the polymeric-stress field, then names control as *future work*:
  *"This method could be used in flow control or when only wall information is available from
  experiments (for example, in opaque fluids)."*
- ⚠️ **Oishi, Kaptanoglu, Kutz & Brunton, "Nonlinear parametric models of viscoelastic fluid flows,"
  *R. Soc. Open Sci.* **11**(10):240995 (2024), arXiv:2308.04405** — SINDy ROM on POD coefficients of
  the symmetric square root of the conformation tensor; Oldroyd-B four-roll mill, **Wi 2–7,
  parametric in Wi, extrapolates to high Wi. No control.** Same group later co-authored HydroGym —
  **and still shipped no viscoelastic environment.** Frame our contribution as *closing the loop*,
  not as *learning the field*.

Also: van Buel & Stark, *Sci. Rep.* **10**:15704 (2020), arXiv:1912.06950 — **open-loop** control of
elastic turbulence (Oldroyd-B Taylor–Couette, OpenFOAM, shear-rate modulation), no feedback, no
learned model. Their own framing is the best white-space quote available: *"the search for active
control strategies appropriate for viscoelastic fluids has so far been limited."* So the delta is
**closed-loop + learned model**, not "first control of a viscoelastic flow."

### 🚨 FEASIBILITY — the go/no-go, answered

> **"Milliseconds/stroke is NOT achievable with a faithful solver."**
> **O(0.1–10 s)/stroke on one GPU is realistic** at 2D, moderate Wi (1–10 — the Oishi Wi 2–7 and
> Thomases–Guy swimmer regime), coarse resolution, with stress diffusion as regularizer.
> That puts **10⁵–10⁶ env steps** in reach with parallel envs. **Verdict: FEASIBLE-WITH-COMPROMISES.**

RL budget anchor (Newtonian 2D): Rabault, Kuchta, Jensen, Reglade & Cerardi, *JFM* **865**:281
(2019), arXiv:1808.07664 — cylinder Re=100, ~8×10⁴ interaction samples, ~4000 solver timesteps per
episode, ≈24 h on a **single desktop core**. Expensive end: Capocci, Linkmann & Morozov,
arXiv:2606.09468 — 3D elastic turbulence at Wi=150 took **1.6×10⁶ core hours**; but their finding
cuts in our favour — tolerating local Tr **c** < 3 violations preserved all mid-plane statistics,
*"potentially lowering computational barriers for studying elastic turbulence."* Binding constraint
is the **high-Weissenberg number problem** (see Yu, Lian & Chu, arXiv:2607.15334, Jul 2026: *"Loss
of positive definiteness is a symptom, not the cause, of high-Weissenberg-number breakdown."*)

**Three concrete solver paths, in order:**
1. **GPU lattice Boltzmann + conformation tensor + immersed moving boundary.** Best-matched published
   method: **Kuron, Stewart, de Graaf & Holm, *EPJ E* 43:20 (2020), arXiv:2009.12279** — *"a lattice
   Boltzmann solver for Oldroyd-B fluids that can handle arbitrarily-shaped fixed and **moving**
   boundary conditions."* Plus Yu, Chen, Wang, Yuan & Shu, arXiv:2508.16997 — two-relaxation-time
   regularized LB for hydrodynamics **and** conformation tensor, validated to **Wi = 10⁴**. LBM is
   the most GPU-friendly family and HydroGym already ships an LBM backend. *No published GPU
   implementation of the viscoelastic variant exists — that part is ours to write.*
2. **Differentiable 2D JAX/PyTorch solver with conformation transport.** Precedent: Brenner group,
   arXiv:2510.24673, already backpropagates through a full differentiable non-Newtonian solver.
   Gives batched envs via `vmap` **and** analytic policy gradients — potentially skipping RL
   sample-inefficiency entirely. ⚠️ Verify whether their solver is truly viscoelastic or merely
   generalized-Newtonian ("local material response" reads generalized-Newtonian) — **that gap may
   itself be the contribution.** Cf. the PICT differentiable PyTorch solver from FluidGym.
3. **Learned surrogate as the environment** — i.e. the claim itself. Oishi et al. already did the
   surrogate half (rolls out stably, extrapolates in Wi). Nobody closed the loop.

⚠️ **Unresolved flag — resolve before submission.** The search index repeatedly surfaced a
"**PhySF-UNO** (Physics-guided Spectral-Fourier U-Net Operator)" described as reconstructing
viscoelastic stress fields by predicting the conformation tensor from velocity fields. **Direct
searches for the exact string return nothing and no primary source exists.** Almost certainly a
search-summarizer confabulation — but if real it is a direct bucket-(b) hit.

---

## Claim 8 (supporting-citation task) — the area law: CONFIRMED as established theory

**See README §4 for the full attribution.** Headline: all three measurements are standard results.
**Single best citation: Koens & Lauga, *JFM* 916, A17 (2021)** — contains the area law via Stokes,
zero-area ⇒ zero displacement, *and* rate independence, all verbatim, for **exactly our
configuration** (1-D displacement, 2 shape DOF). Origin: Shapere & Wilczek, *PRL* **58**:2051
(1987) + *JFM* **198**:557 (1989). Explicit `∇×A` in robotics language: Hatton & Choset, *IJRR*
**30**(8):988 (2011); Rieser et al., *PNAS* **121**(24):e2320517121 (2024).

### 🎯 The one genuinely novel piece: the RL-degeneracy thesis is NOT in print

~50 searches. **No paper argues that RL is unnecessary/degenerate for Stokes gait optimization
because the problem reduces to geometric area-maximization with no sequential structure.** Not
found: any framing as a bandit/single-step problem; any statement that rate-independence removes
credit assignment; any co-occurrence of "geometric phase" and "reinforcement learning" in that
argumentative sense. **Structural reason: the RL-application branch and the geometric-mechanics
branch barely cite each other.** The component facts are all published; the synthesis is absent.

**The RL papers concede the premise in their own words — quote them against themselves:**
- Bulusu & Zöttl, *EPJ E* **48**:50 (2025) — the cleanest admission: *"**For simple model systems,
  typically classical optimization techniques can be applied**"*; RL is defended because it works
  *"without the need of solving mathematically challenging optimization procedures."* **A
  convenience argument, not a necessity argument.**
- Lai, Heydari, Pak & Man, arXiv:2506.00084 — *"the strategies developed by RL are **at least 80% as
  effective as the optimal solutions**."*
- Zhu, Fang & Zhu, *JFM* **944**:A3 (2022) — optimal control beats RL head-to-head, in print:
  *"we shall not regard our RL-trained strategies as globally-optimal"*; *"RL is easily trapped to
  local optima."*

**Defusing "but RL is model-free" — model-free *geometric* methods are far more sample-efficient:**
Bittner, Hatton & Revzen, *Nonlinear Dynamics* **94**(3):1933 (2018) — learns the connection from
noisy experimental data, converged in **"a dozen trials"** in an 88-parameter gait space. Deng, Cowan
& Bittner, arXiv:2310.02141 — *"approximately 10 cycles per link… a factor of ten improvement in
optimization speed over the state of the art."* Htet & Ishimoto, arXiv:2606.22440 (Jun 2026) —
geometric phase from real sperm/nematode data using *"only gauge-theoretic structure."*

### 🎁 A direct independent hit on our shape family

> Alouges, DeSimone, Giraldi, Or & Wiezel, "Energy-optimal strokes for multi-link microswimmers:
> Purcell's loops and Taylor's waves reconciled," *New J. Phys.* **21**, 043050 (2019),
> arXiv:1801.04687.

Verbatim: *"**Remarkably, the optimal stroke is an ellipse lying within a two-dimensional plane** in
the (N−1)-dimensional space of joint angles, where N can be arbitrarily large. For large N, the
optimal stroke is a **traveling wave of bending**."* **Our circular loop in (a₁,a₂) is exactly that
object** — independent confirmation that the two-mode family is the right one.

### ⚠️ CAUTION — do not over-claim from the b→0 limit

> Montenegro-Johnson & Lauga, "Optimal swimming of a sheet," *Phys. Rev. E* **89**(6), 060701(R)
> (2014), arXiv:1406.1070 (note: arXiv title differs — cite the PRE title).

Verbatim: *"the optimal waveform is a front-back symmetric regularized cusp that is **25% more
efficient than the optimal sine-wave**. This optimal two-dimensional shape is smooth, qualitatively
different from the kinked form of Lighthill's optimal three-dimensional flagellum, **not predicted
by small-amplitude theory**."* **At finite amplitude the optimum leaves our two-mode family.**

**Established optimal-gait methods** (four families, all verified): optimal control / sub-Riemannian
geodesics (Alouges–DeSimone–Lefebvre *J. Nonlinear Sci.* 18:277, 2008; Tam & Hosoi *PRL* 98:068105,
2007 — plus the published Raz & Avron *Comment*, *PRL* 100:029801, 2008; Bettiol, Bonnard & Rouot
*SIAM J. Control Optim.* 56:1794, 2018) · **isoperimetric/geometric — the family our result belongs
to** (Avron & Raz: *"the variational problem can be rephrased geometrically as the 'isoperimetric
problem': Find the shortest path that encloses the most flux"*; Ramasamy & Hatton *IEEE T-RO*
35:1014, 2019, the "soap bubble" form; Choi et al. arXiv:2502.17672, the "weighted isoareal
problem") · adjoint shape optimization (Michelin & Lauga *POF* 22:111901, 2010; Osterman & Vilfan
*PNAS* 108:15727, 2011; Guo, Zhu, Liu, Bonnet & Veerapaneni *JFM* 927, 2021) · and the
normalization argument (Lauga & Powers, *Rep. Prog. Phys.* **72**:096601, 2009 §9.3 — *"optimizing
swimming speeds is not, in general, a well-posed mathematical problem… a form of normalization is
required"*).

*Caveats:* "Dido problem" is **not** the established term here (zero hits) — use *isoperimetric*.
**Lauga's *The Fluid Dynamics of Cell Motility* (CUP 2020) has NO geometric/optimal-gait chapter**
(Ch. 3 is "The Waving Sheet Model") — go to Avron–Raz and Hatton instead. No first-hand verbatim
quote from Shapere & Wilczek's own text was obtainable (no PDF text extraction available), so
attribute the *gauge-field/holonomy* framing to them and the explicit *curl-over-area* statement to
Koens & Lauga / Hatton & Choset / Rieser et al., all of whom credit S&W as the origin.

---

## Claim 7b — GPU viscoelastic LBM throughput: a cleanly unoccupied claim

### ⚠️ CITATION CORRECTION to my Claim-7 entry above

I cited the moving-boundary Oldroyd-B LBM as "Kuron, Stewart, de Graaf & Holm, *EPJ E* **43**:20
(2020)". **Wrong volume/year.** Correct: ***Eur. Phys. J. E* 44, 1 (2021)**,
doi:10.1140/epje/s10189-020-00005-6, arXiv:2009.12279, open access PMC7870644. Also **it is not a
Dzanic paper** — a conflation to avoid; Dzanic's corpus is separate (hybrid LB + finite difference +
logarithmic Cholesky).

**And its capability is far more limited than I implied:** Kuron et al. reports **no wall-clock, no
MLUPS, no GPU run**, on tiny grids (channel width L = 28Δx; cavity L = 194), at **Wi ∈ [0,1] only.**
Per Kellnberger et al.'s comparison table, Kuron's **max Wi = 1**.

### 🎯 The finding: no GPU viscoelastic LBM has EVER published a throughput number

Verified three ways: (1) exhaustive arXiv sweep, `abs:"lattice Boltzmann" AND abs:viscoelastic`,
60 results / 30 distinct papers back to 1999 — **zero** abstracts mention GPU, CUDA, MLUPS or GLUPS;
(2) the field's own 2026 review names it as future work; (3) targeted searches surfaced only
Newtonian GPU-LBM.

> Dzanic, Huang, From & Sauret, "Lattice Boltzmann methods for simulating non-Newtonian fluids: A
> comprehensive review," *J. Non-Newtonian Fluid Mech.* **349**, 105591 (2026), arXiv:2601.08206.

Verbatim: *"the intrinsically local and highly parallel structure of the LBM makes it particularly
well suited to modern high-performance computing architectures, especially GPU-accelerated
platforms… **Future work should aim to systematically benchmark and quantify these potential
advantages… massively parallel computations on GPUs.**"*

**The single strongest "the gap is real" datapoint:** Kellnberger, Jüngst & Gekle, *Int. J. Numer.
Methods Fluids* **97**(2) (2025), doi:10.1002/fld.5335 — a viscoelastic LBM **built directly on
FluidX3D**, verbatim *"implemented in OpenCL and thus capable of running on GPUs from different
vendors"* — and it reports **no MLUPS, no GPU model, no wall-clock.** (PTT model, not Oldroyd-B;
"viscosity shuffling" trick; targets bioinks at Rη > 10 000.)

**Newtonian GPU-LBM throughput it would inherit** (FluidX3D, D3Q19 SRT, 256³, FP32): A100 SXM4 80GB
**10 228 MLUPS** (77% of roofline) · H100 SXM5 **17 602** · RTX 4090 **5 624** (85%) · B200 SXM6
**42 152**. Palabos ≈7–8 GLUPS SP on one A100 40GB (75–85% of roofline). XLB (JAX, *Comput. Phys.
Commun.* **300**:109187, 2024) 11 448 MLUPS on 8×A100 → 220 332 on 512 GPUs. Peer-reviewed anchor:
Lehmann et al., *Phys. Rev. E* **106**, 015308 (2022), arXiv:2112.08926.

**What high-Wi viscoelastic DNS currently costs** — Lellep, Linkmann & Morozov, *PNAS* **121**(9),
e2318851121 (2024), arXiv:2312.08091: *"A typical production run was carried out on **16 384 cores
for approximately 260 hours**"* (≈4.3M core-hours). Plus Capocci et al., arXiv:2606.09468: 1.6×10⁶
core-hours at Wi = 150.

**Stability reality check** (Kellnberger Table 3, "Covered ranges of Wi and Rη for existing 3D LB
methods"): Kuron **Wi 1** / Rη 9 · Malaspinas 2010 **Wi 10** / Rη 9 · Gupta **Wi 100** / Rη 0.7 ·
Su 2013 **Wi 10** / Rη 1. Their verdict: *"existing LB methods appear to be appropriate only for
relatively dilute solutions."* Log-conformation or Cholesky is **required** at high Wi (HWNP);
artificial diffusivity *"remains a topic of ongoing debate, as it can undesirably smear sharp stress
gradients, generate unphysical numerical artefacts, and laminarise viscoelastic instabilities."*
⚠️ And arXiv:2508.16997's headline **Wi = 10 000 is only 1D-effective steady Poiseuille** (Ny = 32);
its genuinely 2D four-roll mill tops out near **Wi = 30**. Don't quote the 10⁴ as a solver capability.

**So "first GPU viscoelastic LBM with published throughput" is genuinely unoccupied ground** — a
methods contribution that is independent of, and complementary to, the RL claim.

---

## Claim 2c — squirmer/sheet optimization in viscoelastic fluids: the narrowest carve-outs yet

### The good news, verified by full-text keyword extraction

Nobody formally optimizes squirmer slip modes (B₂/B₁) or swirl amplitude in a viscoelastic fluid.
**Binagia, Phoa, Housiadas & Shaqfeh, *JFM* 900, A4 (2020)** and **Housiadas, Binagia & Shaqfeh,
*JFM* 911, A16 (2021)** each contain **zero occurrences of "optim*" or "maximiz*".**

**Binagia et al. (2020) lay out the trade-off and stop** — verbatim: *"a squirmer with significant
azimuthal swirl not only swims faster in a viscoelastic fluid but is also more energy efficient…
It should be noted, however, that all else considered equal, increasing [swirl] leads to a
**monotonic increase in power expended**… power increases and efficiency decrease with respect to
increasing swirl."* Speed↑ and power↑ both monotone; **the trade-off is never resolved.** That gap
is a defensible position.

⚠️ **Pre-empt this:** Housiadas et al. (2021) *do* report an interior extremum over the slip
parameter ξ = B₂/B₁ — *"The maximum window of validity is observed for ξ = 1/3"* — but it maximizes
the **radius of convergence of the perturbation series**, not speed or efficiency.

### ⚠️⚠️ THE MOST DANGEROUS PRIOR ART — Elfring & Goyal 2016 contains a closed-form optimum

Beyond what was reported under Claim 2 above. Verbatim from the body, after their eq. (43) for a
two-mode gait (mode numbers m, q) in **Oldroyd-B**:

> *"which is **maximum when De = 1/√3·mq** and decays quadratically as De → ∞. If q² > m² then the
> swimmer moves in the direction of k as the thrust due to the compressional waves is dominant, if
> q² < m² the opposite is true, while if m = q there is only a single mode and the swimming speed is
> zero."*

**That is an analytic gait–elasticity matching optimum for a waving sheet in an Oldroyd-B fluid:**
for a given gait there is an optimal De, and for a given De an optimal mode product mq. Plus the
design principle *"a speed increase can only be realized by multiple deformation modes."*

**The only wedge, and it is narrow:** "optim"/"maximiz" are **0 hits** — there is no optimization
*procedure*; the maximum falls out of a closed-form **small-amplitude** expression.

### ⚠️ Two more that must be cited and distinguished

- **Ali & Sajid, "Inertial swimming in an Oldroyd-B fluid," *EPJ E* **48**(4–5), 19 (2025)**,
  doi:10.1140/epje/s10189-025-00485-4. **A waving sheet, Oldroyd-B, AND inertia — it spans both of
  our candidate routes.** Verbatim: *"At a particular Deborah number, the oscillation frequency of
  the sheet could be adjusted to achieve the maximum speed. Similarly, at a particular frequency of
  oscillation, the Deborah numbers could be adjusted to achieve the maximum speed."* Small-amplitude
  asymptotics, no search/learning — but that sentence will be quoted at us.
- **Das, Zhu, Bonnet & Veerapaneni, "Squirmers with arbitrary shape and slip: modeling, simulation,
  and optimization," arXiv:2602.19336 (2026).** **Exactly our machinery, in a Newtonian fluid:**
  *"for a given arbitrary swimmer shape…, we investigate which slip profile minimizes the total
  power loss. A partial minimization… followed by a global optimization procedure."* Expect: *"why is
  porting this to Oldroyd-B novel rather than incremental?"*
- **Zhu, Fang & Zhu, *JFM* (2022), doi:10.1017/jfm.2022.476** — *"We use optimal control to seek the
  globally optimal solutions… and reinforcement learning (RL) for general situations."* Newtonian —
  **and it is Lailai Zhu's group**, who also own the viscoelastic-squirmer line. A referee will ask
  why they haven't already done this.

### ✅ RECOMMENDED REFRAMING (from the agent, and I agree)

Claim novelty in **optimization over the full slip-mode/stroke space at finite Wi with a nonlinear
constitutive model** — i.e. *beyond* the small-amplitude / low-De asymptotics where Elfring–Goyal and
Ali–Sajid live — and, if RL is the method, in the **learned, non-asymptotic discovery** of the
optimum rather than in the existence of an optimum per se.

*Corrections:* "Swimming with a cage" by Binagia/Shaqfeh **does not exist**. There is **no standalone
Binagia FENE-P paper** (FENE-P appears inside the 2020 and 2021 papers). **Neither Binagia 2020 nor
Housiadas 2021 contains any Taylor-sheet section** — 0 hits for "Taylor" in both full texts, contrary
to a search-summarizer claim. Singh & Choudhary arXiv:2604.27348's viscoelasticity is **Kelvin–Voigt
in the body**, Newtonian fluid — not viscoelastic-fluid prior art.

---

## FINAL PASS — the framing correction that matters most

### ⚠️ "Fluid memory ⇒ sequential decision problem" was published in 2009. Do not claim the insight.

> Fu, Wolgemuth & Powers, "Swimming speeds of filaments in nonlinearly viscoelastic fluids,"
> *Phys. Fluids* **21**, 033102 (2009), doi:10.1063/1.3086320, arXiv:1004.0850, PMC2698278.

Body text, verbatim: **"The speed of the swimmer during each stroke depends on its motion during
previous strokes."** Abstract: *"the leading order violation of the scallop theorem occurs for
reciprocal motions in which the backward and forward strokes occur at different rates."*

And Elfring & Goyal (2016) states verbatim: **"A viscoelastic fluid retains a memory of its flow
history."** Plus Elfring & Lauga (Springer 2015, arXiv:1410.4322): *"the mathematical details which
lead to the scallop theorem, namely linearity and an independence of time, are no longer present."*
Also Lauga, "Life at high Deborah number," *EPL* **86**:64001 (2009); Lauga, "Life around the scallop
theorem," *Soft Matter* **7**:3060 (2011): *"the rate at which the reciprocal sequence of shapes is
being displayed would matter."* Esparza-López & Lauga, *PRF* **8**:063301 (2023) is the cleanest
rate-invariance ⇔ scallop-theorem statement.

**Claim only that nobody ACTED on it.**

### ⚠️ Two more sharp near-misses

- **Montenegro-Johnson & Lauga, "Optimal swimming of a sheet," *PRE* 89(6):060701(R) (2014)** —
  *"the **large-amplitude waveform of the two-dimensional swimming sheet that yields optimum
  hydrodynamic efficiency**… a front-back symmetric regularized cusp that is 25% more efficient than
  the optimal sine-wave."* **Identical object, identical question, free-form large-amplitude
  optimization — only the fluid differs (Newtonian).** The single sharpest near-miss.
- **Ives & Morozov, *Phys. Fluids* 29:121612 (2017), arXiv:1801.08922** — *"a numerical spectral method
  capable of finding the swimming speed of a waving sheet with an **arbitrary amplitude and
  waveform**."* **Viscoelastic, arbitrary waveform, ZERO optimization. The solver existed; nobody
  optimized on it.** Both a gift (feasibility proof) and a warning (someone could).

Also: **Li & Ardekani, *JFM* 784:R4 (2015)** — waving sheet in Giesekus: *"the swimming speed of an
infinitely long waving sheet in an inelastic shear-thinning fluid **has a maximum**."*

### 🎯 The decisive structural fact — quote this

In **Eric Lauga's complete corpus**, the set of titles matching `optimal|optimis|optimiz|efficien`
and the set matching `viscoelastic|non-Newt|shear-thinning|Deborah|polymer|mucus|Oldroyd` have an
**EMPTY INTERSECTION.** Same pattern for Montenegro-Johnson: his optimization papers are Newtonian;
his non-Newtonian papers don't optimize. **The two literatures have never been joined by the people
best placed to join them.**

Corroborating: **Lauga has used RL exactly once, and it was Newtonian** — Vona & Lauga, "Stabilising
viscous extensional flows using Reinforcement Learning," *PRE* **104**:055108 (2021), arXiv:2110.14677.
Zero learning+viscoelastic papers in his record.

### ⚠️ A result that cuts AGAINST our framing — engage it

> Loos, Monter, Ginot & Bechinger, "Universal Symmetry of Optimal Control at the Microscale,"
> *Phys. Rev. X* **14**, 021032 (2024), arXiv:2311.00470.

Verbatim: *"consideration of **memory effects** in the surrounding fluid… our experiments were
performed in viscous and **viscoelastic** media… **Using a machine learning algorithm**, we
demonstrate that the algorithmic exploitation of time-reversal symmetry can significantly enhance the
performance of numerical optimization algorithms."* A dragged trapped colloid — no gait, no shape
space — **but its result argues that time-reversal structure SURVIVES in viscoelastic media.** Do not
assert "memory destroys the geometric structure" without addressing this.

Relatedly: **Kobayashi, Kitano & Yamamoto, arXiv:2606.10268** argues *for* *"a minimal geometric
principle for rotation-induced propulsion in viscoelastic fluids."* **Avoid a blanket "geometry is
dead in viscoelastic fluids" statement** — it is contradicted in print.

### ⚠️ "Non-Markovian RL swimming" is already claimed (differently)

**El Khiyati, Chesneaux, Giraldi & Bec, arXiv:2302.05081** — *"the **non-Markovianity of the decision
process**"* — but from partial observation of an **external Newtonian flow**, not fluid memory.
Differentiate explicitly. And the nearest RL competitor, **Tokoro, Takayama, Deguchi, Zöttl &
Matsunaga, arXiv:2511.00816** (*PRF* 2026), finds *"the optimum solutions depend on the action
interval… based on its internal state"* — but Rotne–Prager, Newtonian. **Our differentiator: their
timescale is a *controller* timescale; ours is the *fluid relaxation* timescale.**

### 🚨 ONE UNRESOLVED RISK — get this PDF before writing anything

> Asghar, Rehman, Shatanawi & Khan, "**Efficiency optimization of micro-swimmers in viscoelastic
> bio-fluids within complex cervical environments**," *Chinese Journal of Physics* **96**, 664–677
> (2025), doi:10.1016/j.cjph.2025.06.003.

Metadata Crossref-verified; **abstract unobtainable** (ScienceDirect 403; Crossref abstract empty;
Semantic Scholar and OpenAlex both null; ouci 502 ×4; X-MOL CAPTCHA; Scilit 403). **Its title alone is
the one item in this entire sweep that could, on its face, contradict "no prior efficiency
optimization in a viscoelastic fluid."** Contextual evidence from the group's companion output
suggests analytical lubrication theory optimizing one or two scalars — **but that is inference, not
verification. Obtain via institutional access.**

### ✅ THE FRAME TO USE (adopted)

> *"That fluid memory breaks rate-invariance and hence the scallop theorem is established [Lauga 2009;
> Fu, Wolgemuth & Powers 2009; Elfring & Lauga 2015]. **What has not been done is to act on it** — to
> treat polymer stress as part of the agent's state and learn the gait by sequential decision-making,
> rather than prescribing a waveform and evaluating it post hoc. Ives & Morozov (2017) built an
> arbitrary-waveform viscoelastic solver and never optimized; Montenegro-Johnson & Lauga (2014)
> optimized the identical sheet in a Newtonian fluid; Neal & Bearon (2025) name the optimal
> viscoelastic stroke as future work; Mo, Li & Bian (2023) name gait modulation under viscoelasticity
> as an open question."*

**And the key tactical move: present every known optimum as a VALIDATION CHECK the agent recovers.**
De ≈ 1 efficiency peak (Teran, Fauci & Shelley, *PRL* 104:038101, 2010) · the finite-De enhancement
window with max U = 1.3 at De = 0.5 (Riley & Lauga, *J. Theor. Biol.* 382:345, 2015, arXiv:1507.00021)
· the shear-thinning speed maximum (Li & Ardekani 2015) · the multi-mode requirement and De = mq/√3
optimum (Elfring & Goyal 2016) · Lauga 2007's U/U_N = (1+De²ηₛ/η)/(1+De²).
**Recovering them is a strength; claiming them is fatal.**

Scope to **finite/high amplitude and strongly elastic regimes**, opening with Thomases & Guy's own
sentence (*JFM* 825:109, 2017): *"**High amplitude strokes in strongly elastic flows lead to a
qualitatively different regime** in which highly concentrated elastic stresses accumulate near
swimmer bodies and where dramatic slow-downs are seen."*

### Feasibility, final numbers

**Cost decomposes into three independent factors, and only one is a real wall:**
1. **Log-conformation overhead: small and unmeasured.** Per-cell 3×3 symmetric eigendecomposition is
   O(1); every source treats it as a modest constant; the papers designed to eliminate it publish no
   timings. Budget < 2×. **This is a genuine literature gap — no profiling percentage exists anywhere.**
2. **Resolution: the 3D killer.** 1.6×10⁶ core-h (Capocci) vs 1.5×10⁶ core-h for one Wi = 8 channel
   (Balasubramanian). Nobody resolves the real problem — real polymer diffusivity is **3–6 orders of
   magnitude below** what stability requires (Gupta & Vincenzi, *JFM* 870:405, 2019); experimental
   Pe = 10⁵–10¹⁰ vs simulated 10³ (Yerasi et al., *JFM* 1000:A37, 2024).
3. **Timestep COUNT: the 2D / moving-boundary killer.** Cell counts in 2D are trivial (512², 72k,
   12.8k cells) but step counts are **10⁷–10⁸**, because dt ~ 10⁻⁵–10⁻⁶ λ and you must integrate
   hundreds-to-a-thousand relaxation times. **And immersed boundaries add a second, harsher
   restriction from penalty stiffness (κ ∝ h/Δt²).** The community's answer is semi-implicit /
   non-stiff IB — exactly what unlocked Wi > 100 (Ceniceros & Fisher, *JNNFM* 171:31, 2012) versus the
   **Wi = 0.1 ceiling** of the explicit IBAMR cylinder benchmark (Gruninger et al., *JCP* 506:112888,
   2024 — which, strikingly for a benchmarking paper, reports **no wall-clock anywhere**).

**The calibration datapoint** — Rempfer, Zhu, Stam, Nesenberend, Panja & de Graaf, arXiv:2509.01327:
2D four-roll mill, **1024², single Intel i7-11700K core, ≈200 ms/step (~5 MLUPS)**; but **Wi only up
to 1.1**, and *"approximately 6 hours on a modern desktop machine"* to converge Wi = 1.1. They concede
a 10²–10³× gap vs Newtonian LB, and name moving boundaries as future work.
**Practical recipe:** De/Wi ≲ 5, artificial stress diffusion (ε ≈ 1.5×10⁻³ à la Thomases & Guy 2017,
who used 512² at dt = 10⁻³ over De 0–5), 10⁶–10⁷ steps at ~10⁻¹ s/step. **Only three papers in the
entire viscoelastic literature report an absolute cost.**

---

## THE STRUCTURAL ARGUMENT — why these two literatures have never been joined

This is the deepest and most defensible novelty statement in the entire sweep. **Every adjoint /
gradient / shape-optimization method for swimmers rests on two properties that an Oldroyd-B or
Giesekus constitutive law destroys.** The swimmer-optimization community says so itself:

> Bonnet, Das, Veerapaneni & Zhu, "Slip optimization on arbitrary 3D microswimmers: a
> reduced-dimension and boundary-integral framework," arXiv:2604.07310 (2026).

Verbatim: *"**By exploiting the linearity of the Stokes equations and the Lorentz reciprocal
theorem**, we derive an explicit linear operator that maps the tangential surface slip velocity to
the resulting rigid-body … velocities, **effectively decoupling the hydrodynamic boundary value
problem from the optimization loop**."*

**That decoupling is the whole trick — and it does not survive fluid memory.** Hence: adjoint
swimmer optimization exists only in Newtonian Stokes flow. Verified instances, all Newtonian:
Guo, Zhu, Liu, Bonnet & Veerapaneni, *JFM* **927**:A22 (2021), arXiv:2103.15642 (*"efficiency
sensitivities are derived using an adjoint-based method"*) · Liu, Zhu, Guo, Bonnet & Veerapaneni,
*SIAM J. Sci. Comput.*, doi:10.1137/24M1659649, arXiv:2405.00656 · Das, Zhu, Bonnet & Veerapaneni,
arXiv:2602.19336 · Dvoriashyna & Lauga, *Soft Matter* **21**:3503 (2025), arXiv:2504.02424
(*"adjoint-based variational calculus"*) · Montenegro-Johnson & Lauga, *PRE* **89**:060701(R) (2014) ·
Wilkening & Hosoi, *JFM* (2008) · Palazzolo, Giraldi, Binois & Berti, *PRF* **10**:034101 (2025) ·
El Alaoui-Faris, Pomet, Régnier & Giraldi, *PRE* **101**:042604 (2020) · Ishimoto, *J. Theor. Biol.*
**399**:166 (2016) (GA).

### 🎯 The corpus audit, quantified — quote this

**Eric Lauga's complete publication list: 10 papers with "optimal/optimum/optimisation" in the title,
19 papers on viscoelastic / complex / shear-thinning / polymeric fluids — the two sets DO NOT
INTERSECT ONCE.** The world's most prolific author in *both* subfields has never combined them.
**Same audit, same result, for Robert Guy and Becca Thomases.** And the French optimal-control school
(Alouges, DeSimone, Giraldi, Pomet, Zoppello, Heltai, Lefebvre, Merlet) has **never** extended
controllability/optimal-stroke theory to a non-Newtonian fluid.
*(Audit hole: On Shun Pak's publication page returned HTTP 401.)*

### 🎁 The enabling citation — a continuous adjoint for Oldroyd-B IS derivable

> Kim, "Adjoint-based sensitivity analysis of viscoelastic fluids at a low Deborah number,"
> *Applied Mathematical Modelling* **115**, 453–469 (2023), doi:10.1016/j.apm.2022.10.044.

*"A set of **continuous adjoint** governing equations is formulated…"* viscoelasticity *"modeled by
the **Oldroyd-B** constitutive equation"* at *"the Deborah number 0.5"*; *"illustrates how adjoint
sensitivity analysis can be utilized for flow control of viscoelastic fluids."* **It optimizes
nothing and contains no swimmer** — but it proves the derivative exists. Adjacent machinery also
exists for viscoelastic topology optimization (Jensen, Szabó & Okkels, *APL* **100**:234102, 2012),
non-isothermal viscoelastic optimal control (Kunisch & Marduel, *JNNFM* **88**:261, 2000), and
non-Newtonian blood-flow adjoints (Bletsos, Kühl & Rung, *IJNMF*, 2023, doi:10.1002/fld.5227;
Abraham, Behr & Heinkenschloss, 2005).

### The closest true hit — and it is brute force

> Kroo, Binagia, Eckman, Prakash & Shaqfeh, "A freely suspended robotic swimmer propelled by
> viscoelastic normal stresses," *JFM* **944**, A20 (2022), doi:10.1017/jfm.2022.485, arXiv:2111.10515.

*"**Optimized cylindrical and conic tail geometries are shown to double the propulsive signal**,
relative to the optimal spherical tail."* Single-mode **Giesekus** (α_m = 0.035). But: *"we conducted
numerical simulations for a range of tail shapes and geometries"* — a **grid search over 1–3
geometric variables**, no gradients, no adjoint, no infinite-dimensional design space, and it
optimizes **body shape, not gait**. This is the state of the art to improve on.

### ✅ The Asghar CJPh 2025 risk is now largely DEFUSED

The **complete 45-item reference list** was retrieved. It contains **zero optimization-methodology
citations** — no adjoint, no gradient descent, no Nelder–Mead, no GA, no Bayesian optimization, no
ML/RL. The group's invariant method across 20+ years: lubrication/Stokes reduction → `bvp4c` →
**modified Newton–Raphson used as a root-finder for the force-free/torque-free constraint, not as a
maximizer** → power dissipation plotted against swept rheological parameters. Across their entire
swimmer corpus, the CJPh 2025 paper is the **only** title containing "optimization"/"optimal."
Elsevier deposits no CJPh abstracts anywhere (confirmed against a sibling paper), so this cannot be
closed remotely. **Still worth the institutional-access PDF, but the risk is now low.**

### The exhaustive empty list — no hit for ANY of these

`"adjoint" + swimmer + viscoelastic` · `"optimal control" + swimming microorganism + viscoelastic` ·
`"optimal swimming" + "FENE-P"` · `Giesekus + swimmer + stroke optimization` · `"optimal swimming" +
"second-order fluid"` · `"gradient-based optimization" + non-Newtonian swimmer` · `"shape
optimization" + microswimmer + non-Newtonian` · `"waveform optimization" + flagellum + viscoelastic` ·
**PTT / Johnson–Segalman / Ellis / Williamson / Jeffrey / UCM-Maxwell / power-law + swimmer +
optimization → not one hit** · `differentiable simulation + non-Newtonian + swimmer optimization`
(Nava et al., ICML 2022, arXiv:2204.12584, list non-Newtonian flow as **future work**) · and the exact
phrases **"optimal swimming in a viscoelastic fluid"** / **"optimal stroke in a viscoelastic fluid"** —
**no such title exists.**

Independent corroboration from a 2026 review of exactly this field: **Kobayashi, Molina & Yamamoto,
"Microswimmers in Non-Newtonian Fluids," *Seibutsu Butsuri* 66(1), 30–34 (2026)**,
doi:10.2142/biophys.66.30 — full text searched: **no mention of optimization, optimal stroke, adjoint,
gradient-based design, or reinforcement learning.**

*Method limitations carried forward:* arXiv/Semantic Scholar/OpenAlex APIs returned HTTP 429 during
this pass (OpenAlex `Retry-After: ~8h`), so no exhaustive API-level enumeration was possible —
individual `/abs/` fetches, PMC, PubMed, Crossref and ~35 web searches were substituted. Read the
census as thorough, not provably exhaustive.


---

## Claim 2, THIRD pass — the infrastructure angle: no RL benchmark for non-Newtonian flow exists

A systematic survey of every RL-for-fluids benchmark suite. **Eleven libraries, ~90+ environments,
zero non-Newtonian.** This is the gap stated at the level of *tooling*, independent of the paper
census and the citation-network test.

| Suite | Envs | Non-Newtonian? |
|---|---|---|
| **FluidGym** (arXiv:2601.15015, **ICML 2026**) | 13 (×3 difficulties) | **NO — stated explicitly** |
| **HydroGym** (arXiv:2512.17534; 21 authors incl. Brunton, Vinuesa) | **61+**, Re up to 400,000 | **NO** — no mention in paper or repo |
| ControlGym (arXiv:2311.18736, PMLR v242) | 10 PDEs + 36 linear | **NO** — and *no Navier–Stokes at all* |
| PDE Control Gym (arXiv:2405.11401, PMLR v242) | 3 | NO |
| RBC-Gym (HammerLabML) | 2D/3D RBC, Oceananigans.jl | NO |
| KTH-FlowAI RBC 2D + 3D | shenfun, 10 / 64 actuators | NO — *"standard Newtonian convection control"* |
| SmartFlow / SmartSOD2D / Relexi | coupling frameworks | NO — incompressible Newtonian |
| KTH MARL channel benchmark | turbulent open channel | NO |
| SofaGym (*Soft Robotics* 10:410) | 14 soft-robot FEM | **NO — zero fluid envs at all** |
| Beacon, Gym-preCICE, DRLinFluids, drlFoam, DRLFluent | — | NO (per FluidGym's related-work table) |

Verbatim from FluidGym: *"No environment involves non-Newtonian, viscoelastic, or polymeric fluid
constitutive models (Oldroyd-B, FENE-P, Giesekus, Carreau, power-law, shear-thinning). All
environments model Newtonian incompressible flows."*

**Agent's conclusion:** *"I found no RL environment, gym, or benchmark of any kind for non-Newtonian /
viscoelastic / polymeric flow."* Targeted searches pairing RL with each constitutive model returned
only (a) viscoelastic CFD with no RL, or (b) RL flow control with no viscoelasticity.

### 🎁 FEASIBILITY LEAD — a differentiable PyTorch solver to extend

> **PICT** — *"a differentiable, GPU-accelerated multi-block PISO solver"*, finite-volume,
> incompressible NS + thermal transport, **implemented entirely in PyTorch with custom CUDA
> kernels**, **fully differentiable across all 13 FluidGym environments**.
> Franz, Thuerey et al., *Journal of Computational Physics* **544** (2026).
> Repo: github.com/safe-autonomous-systems/fluidgym (MIT, on PyPI).

This is the most promising base for a viscoelastic RL environment: adding a conformation-tensor
transport equation to a differentiable PyTorch FV solver is a far smaller job than writing one, and
differentiability opens DPC/TD-MPC in addition to model-free RL. **MIT licensed** (unlike
open-dreamer). Partially answers the solver-feasibility question pending from agent #7.

**Two learned-surrogate-in-the-RL-loop precedents worth copying (both RBC):** Chen &
Constante-Amores, arXiv:2510.26705 — **DManD** (POD + autoencoder + neural ODE), policy trained in
the ROM and deployed in DNS, 16–23% Nu reduction. Plotzki & Peitz, arXiv:2603.28074 — **LRAN**, with
a *policy-aware* variant countering distribution shift, >40% training-time cut.

### Traps and corrections from this pass

- **SofaGym's "viscoelasticity" is a SOLID Kelvin–Voigt material law — categorically not a
  non-Newtonian fluid constitutive model.** Do not let it be counted as prior art.
- **ControlGym has no Navier–Stokes whatsoever** (10 PDEs: CDR, Wave, Schrödinger, Burgers,
  Kuramoto–Sivashinsky, Fisher, Allen–Cahn, KdV, Cahn–Hilliard, Ginzburg–Landau).
- **"PDEgym"** (camlab-ethz) is a **static HuggingFace dataset collection** for operator learning —
  no Gymnasium API, no actuators, no reward. **Not an RL benchmark**; don't cite it as one.
- ⚠️ **The four-roll mill is a classic *viscoelastic* benchmark geometry**, so arXiv:2504.20336
  (Dai, Xu, Zhang & Yang, *JFM* **1012**:A8, 2025, RL-assisted four-roll mill control) *looks* like a
  hit — it is **Newtonian** (droplet centring at Re ~ O(1); no Oldroyd-B/Weissenberg anywhere).
- Nearest "extra physics" RBC-RL: arXiv:2606.06191, double-diffusive salt-finger convection — still
  a Newtonian fluid with two scalars.
- *Do not cite:* "Convection gym" (does not exist); "Comparing and Contrasting Deep RL for
  Rayleigh-Bénard" (no such title). RBC-Gym has **no paper, no license file, and is uncited** — even
  by its own lab's 2026 Koopman paper. The KTH MARL channel benchmark ships **only a compiled solver
  binary**, materially limiting reproducibility. PNAS Zhou & Zhu author list is snippet-level only.

---

## RESOLVED — the 403-blocked *Ocean Engineering* paper: ADJACENT, not competing

> Sun, Zhan, Wang, Jiang, Qu, Li & **Cao** (corresponding), "**Deep reinforcement learning control of
> fish locomotion via physics-guided surrogates**," *Ocean Engineering* **355**, 125161 (2026),
> doi:10.1016/j.oceaneng.2026.125161. Online 23 Mar 2026; issue 15 May 2026. Tsinghua SIGS + Georgia
> Tech + HKU. Closed access, **no preprint or repository copy anywhere**.

**Classification: bucket (b) — a fast drop-in *environment* for model-free RL, NOT model-based RL.**
~90–95% confidence, from three independent lines:

1. **Every phrase is environment-substitution language:** *"DRL agents **interact with** surrogate
   environments"*; *"control policies are first trained in a surrogate-based **environment** and
   subsequently refined within a high-fidelity CFD solver"*; *"**reducing the need for** high-fidelity
   simulations **during DRL training**."* No planning, imagination, model rollouts, value expansion,
   MPC, or Dyna interleaving anywhere.
2. **The complete 70-reference bibliography (pulled from Crossref) contains ZERO model-based-RL or
   world-model literature** — no Dyna, PETS, MBPO, PlaNet, Dreamer, or "world model." Every RL
   citation is model-free DRL for flow control.
3. **The decisive structural tell:** pretrain in the cheap surrogate, then fine-tune the *same* policy
   in expensive CFD. That is sim-to-sim transfer / curriculum. Genuine model-based RL either uses the
   model at decision time or interleaves imagined rollouts while improving the model. And its closest
   cited precedent (ref 42 = Rodwell & Tallapragada 2023) does exactly this with an analytic Chaplygin-
   sleigh surrogate.

**Low-dimensional signals, not flow fields** (inference, but strongly supported): they hand-engineer
*"wake vortex shedding delays"* — a correction you only need if the surrogate output is a force/state
**time series with memory**; a field emulator would carry the wake automatically. *"**Multiple**
neural-network surrogate models"* = regime-partitioned regression. And the surrogate-methods
references are Co-Kriging, Sudret's UQ overview, and — tellingly — **Marquardt, "Ridge regression in
practice" (1975)**. *Caveat:* they do cite FNO once out of 70.

**No learned latent.** Zero autoencoder/VAE/latent-dynamics citations. The group *does* have ROM
capability — Jiang et al., *PRF* (2024) balanced-POD VIV control; Jiang, Pfister, Huang & Cao,
*PRE* **111**:045101 (2025) Koopman ROM of flag flapping — but it is **linear/modal ROM on other
systems**, not a latent state for the fish RL.

**Newtonian.** Exactly one complex-fluid citation in 70: Hewitt, *"Swimming in viscoplastic fluids"*
(*Rheol. Acta* 2024) — **yield-stress, not viscoelastic**. Zero polymer / Oldroyd-B / FENE-P citations.

### ⚠️ ADD TO THE "DO NOT CLAIM" LIST

This paper **is** prior art for the umbrella idea *"use a learned surrogate of the flow so you don't
have to run CFD inside the RL loop, for a deforming swimmer"* — and it is **not even the first**, since
it explicitly extends Rodwell & Tallapragada (2023). **So do not frame novelty as "first to replace
expensive CFD with a learned model for swimmer control" or "first learned-model-based control of a
deforming swimmer."**

**Use it as the foil instead** — one or two sentences cleanly position the work and hand you a
legitimate baseline: *"surrogate-as-environment with CFD fine-tuning (Sun et al., 2026)"* versus *"a
world model queried for imagined rollouts."* Novelty must be carried by the **conjunction**:
field-level latent state **+** planning-in-imagination (not environment substitution) **+**
viscoelastic physics. All three are untouched here.

*Unverified:* RL algorithm and Reynolds number (methods section unreachable — ScienceDirect 403 +
CAPTCHA from both WebFetch and direct curl; every aggregator, proxy, and preprint route exhausted).
Residual risk: if PD-FS does predict compressed flow fields, the gap narrows — but it would remain
model-free RL in a fast Newtonian environment, contesting neither planning-in-imagination nor
viscoelasticity. Cheapest certainty: institutional PDF, or email Shunxiang Cao.

---

## CLOSING BATCH — loose ends resolved, and one scientific warning

### 🚨 THE MOST IMPORTANT SCIENTIFIC CAVEAT IN THE WHOLE SWEEP — Felderhof predicts a NULL for the finite-Re route

> Felderhof, "Swimming at small Reynolds number of a collinear assembly of spheres in an
> incompressible viscous fluid **with inertia**," arXiv:1610.06029; *Eur. J. Mech. B/Fluids* (2017).
> *(⚠ volume/pages disputed across sources — vol. 63 p. 47 vs vol. 64 pp. 47–54. Verify.)*

Verbatim from the body: *"The optimal stroke for swimming in the x direction for given power is given
by the eigenvector of the generalized eigenvalue problem."* And then the killer:

> *"It turns out that for the three-sphere swimmer **the maximum eigenvalue and the corresponding
> eigenvector hardly depend on the scale number**."*

**Translation: the Stokes-optimal three-sphere stroke stays near-optimal across the entire inertial
range.** So "inertia reshapes the optimal gait" may simply be **false** for small-amplitude, few-DOF
swimmers. Any finite-Re claim must be made where that perturbative conclusion demonstrably fails:
**large amplitude**, or **reciprocal strokes where the Stokes optimum is identically zero and the
whole objective is inertia-generated.** This is a real risk of a null result, not a framing problem.

Related: the scale number maps onto Reynolds explicitly — *"We call s the scale number. It is related
to the Roshko number Ro = L²fρ/η … by Ro = 4s²/π"* — with efficiency maxima at s ≈ 0.865–0.962
(Ro ≈ 1) and results out to s = 10⁴. **So Felderhof & Jones already optimized analytically across
Re ~ 0.01–100.** "First to optimize a gait with fluid inertia" is dead (already recorded); this adds
that they also *covered our band*.

### 🎁 The cleanest citable statement of the finite-Re gap — from the people who left it

> Yang & Hatton, "Geometric Design and Gait Co-Optimization for Soft Continuum Robots Swimming at Low
> and High Reynolds Numbers," arXiv:2409.15220, **ICRA 2025**.

Verbatim: *"extending this approach to scenarios at **intermediate Reynolds numbers** … would
complicate the optimization due to **time-variant dynamics**."* Their "low Re" is a linear viscous-drag
model and "high Re" is Lighthill added inertia — **the Navier–Stokes equations are never solved.**

### The closest existing "optimal gait at Re 0.1–10" — and it is a sweep

> Granzier-Nakajima, **Guy** & Zhang-Molina, "A Numerical Study of Metachronal Propulsion at Low to
> Intermediate Reynolds Numbers," *Fluids* **5**(2), 86 (2020), doi:10.3390/fluids5020086.

Verbatim: *"…immersed boundary method, which allows us to simulate metachronal propulsion at Reynolds
numbers (RE) ranging from close to 0 to about 100. Our main finding is that the highest average flux is
generated when nearest-neighbor paddles maintain an approximate 20%-25% phase-difference…"* Plus
**"At RE 0.1 the maximum efficiency occurs at two paddles"** and **"a tight paddle spacing is preferred
when RE is less than 10."** A grid scan over phase lag, spacing and paddle count — **no optimizer.**
Note it is **Guy's group**, i.e. the same group as Bailey & Guy's Re = 0 RL paper.

**Overall verdict on non-RL optimization in the band:** *"no optimization method of any kind —
evolutionary, Bayesian, adjoint, gradient/AD, surrogate, or topology-based — has been applied to a
**free-swimming** gait computed from the unsteady Navier–Stokes equations in Re ≈ 0.1–10."* Nearest by
Re: Xu, Wei, Li & Dong (*AIAA J.* 2019, arXiv:1809.04100) adjoint at **Re = 100** — but a **tethered**
plate in a uniform stream, thrust objective, not a free swimmer. And Alhashim, Hausknecht & Brenner,
*PNAS* (2025), arXiv:2403.06257 — differentiable IBM in JAX-CFD + Ipopt, flapping swimmer
thrust/power efficiency, **Re = 1000**. ⚠️ Its title says *"complex fluids"* — **check whether that
means non-Newtonian or merely FSI before citing.**

### Open item CLOSED: Yu et al. is Re = 7142, not sub-100

> Yu, Liu, Wang, Liu, Lu & Huang, *Phys. Rev. E* **105**, 045105 (2022).

Verbatim from the Figure 2 caption: *"…at Reynolds number (Re) = L²/T_pν = **7142**."* Recovered via
**Wayback Machine captures of the APS abstract page, which publishes figure captions free** (direct
fetch 403s; the 2022 and 2024 captures are byte-identical; the 2026 redesign hides them). 2D IB-LBM,
collective swimming of undulatory foils, no Re sweep. **Confirms the Re gap stands.**
⚠️ **Misattribution trap:** search engines attach *"value-based LSTM-DRQN coupled with IB-LBM"* to this
paper — that phrasing belongs to **Zhu, Tian, Young, Liao & Lai, *Sci. Rep.* 11:1691 (2021)**. Yu et
al.'s algorithm is never named in free text (a review calls it Q-learning; unverified).

### 🎁 A quote that supports the §4 thesis, from an unexpected source

> Cao's own group: "Model predictive control of fluid–structure interaction via Koopman-based
> reduced-order model," *JFM* (2026), doi:10.1017/jfm.2025.11035.

Verbatim: *"**The framework matches the control performance of reinforcement learning while markedly
reducing computational cost.**"* A flow-control group demonstrating that a principled reduced-order
method equals RL at lower cost — directly supporting the argument that RL is often not the right tool
for these problems. Pair with Bulusu & Zöttl's *"For simple model systems, typically classical
optimization techniques can be applied."*

### Benchmark-suite gap — FOURTH independent confirmation, now with grep evidence

**15 libraries verified by code search, not inference. Zero non-Newtonian environments.** Hard
evidence: `transportModel Newtonian; nu [0 2 -1 0 0 0 0] 0.001;` in Gym-preCICE's `jet_cylinder` and
DRLinFluids' `cylinder2D` transportProperties; 7-term searches (viscoelastic / Oldroyd / FENE /
Giesekus / Carreau / non-Newtonian / polymer) returning **0 hits each** across HydroGym (all 6
backends), FluidGym, Beacon, Relexi, SmartSOD2D, SmartFlow, PDEControlGym, smarties, Korali,
DRLFluent, CubismUP/CUP2D/CUP3D. Also: *"I found no RL flow-control paper (let alone benchmark) on
polymer solutions or elastic turbulence."*

**Corrections worth keeping:** "Flow Control Gym", "flowgym", "gym-flow" **do not exist** as CFD RL
packages, and the Gymnasium third-party-environments page lists **no fluid/CFD/PDE environments at
all**. ⚠️ `flow-gym-suite` ("Flow Gym", arXiv:2512.20642) is flow-field **estimation** (PIV-style),
**not control** — do not cite as a control benchmark. ⚠️ **BSK-RL** is built on the *spacecraft*
Basilisk, nothing to do with Popinet's CFD Basilisk. `github.com/cselab/korali` now **404s** (use
`korali-mirror/korali`). PDEControlGym has **no LICENSE file** (undefined reuse terms) and a real
registration bug (two `id=` kwargs in one `register()` call; its Neuron-Growth env is implemented but
unregistered); its README calls the hyperbolic env "Burger's Equation" but the paper's instance is a
**linear transport PDE with recirculation**. Gym-preCICE is **SoftwareX** 23:101446 (not Software
Impacts); authors are **Shams & Elsheikh only** — an agent caught and discarded a hallucinated author
list from a PDF extraction here, which is a useful reminder about PDF-text provenance.

### PD-FS surrogate reconstructed from the authors' open record (the closed *Ocean Engineering* paper)

Five independent lines say the surrogate predicts **force/performance scalars, not flow fields**: the
ML citation set is FNO + multi-fidelity co-kriging + a UQ-surrogate overview + **Marquardt, "Ridge
regression in practice" (1975)** — *"nobody cites ridge regression while building a flow-field neural
operator"*; **no CNN/LSTM/GRU/autoencoder/graph-network citation anywhere** in 70 refs; **no
self-citation to the group's own GNO-ViT or masked-FNO field surrogates**; "multiple surrogate models …
distinct hydrodynamic responses" = per-regime regressors; and *"physics-guided" is anchored on
Lighthill's **reactive force** — you can only compensate a force with a force*, so the architecture is
almost certainly analytic-EBT baseline + NN learning the CFD-minus-EBT residual. **RL is PPO or TRPO**
(TRPO is the only core RL-algorithm paper cited; the group's confirmed house style is PPO, ~200
episodes, from *Phys. Fluids* 35:107140, 2023). CFD is **ANSYS Fluent with dynamic mesh, Python-scripted**
— not the group's FEniCS/ALE research code. Division of labour: **Cao** = FSI/CFD + RL template
(PhD Virginia Tech under K. Wang → postdoc Caltech with Colonius), **Qu** = robot + CPG hardware,
**Zhan** = DRL machinery (from *legged-robot* RL, arXiv:2605.08804), **Xiaofan Li** = physics-informed
correction. ⚠️ **Correction:** the widely-quoted *"surrogate under an hour vs 16 days of CFD"* figure
belongs to **Zhang et al., *IEEE T-RO* 38(6):3861 (2022)**, **not** to this paper. Re remains
unavailable publicly; the paper's key body-model reference (Chao, Mahbub & Cheng, *JFM* 2022) spans
St 0.1–1.0, **Re 50–2000**.

---

## 🚨 THE MOST DANGEROUS NEAR-MISS IN THE SWEEP — the viscoelastic latent model ALREADY EXISTS

> Kumar, **Constante-Amores** & **Graham**, "Elastoinertial turbulence: data-driven reduced-order model
> based on manifold dynamics," ***JFM* 1007, R1 (2025)**, doi:10.1017/jfm.2025.130, arXiv:2410.02948.

**VEDManD:** viscoelastic POD (1.6×10⁶ → ~4,000 DoF) → hybrid autoencoder (→ **50** DoF) → stabilized
neural ODE. **FENE-P, β = 0.97, b = 6400, Re = 3000, Wi = 35.**

**Verified: forward prediction only — no RL, no MPC, no actuator, no policy.** "Control" appears
**exclusively in future work**: these models *"could facilitate the design of control strategies …
beyond the MDR limit."*

**This is literally the missing half.** The exact latent-world-model machinery, already built for a
viscoelastic (FENE-P) flow — and **Constante-Amores co-authors BOTH** this paper *and* the Newtonian
RBC DManD-RL paper (arXiv:2510.26705 → *PRF* 11:044903, 2026, which trains TD3 inside a learned DManD
ROM and deploys to DNS for 16–23% Nu reduction). **One person holds both halves and has not joined
them.** Same pattern at Brunton/Kutz/Oishi (Oldroyd-B SINDy ROM + SINDy-RL) and Vinuesa/Tammisola
(viscoelastic CNN estimator + HydroGym + DRL drag reduction).

### 🚨 And someone is actively recruiting to do exactly this

**Manchester has an OPEN PhD studentship** (Beneitez, King): *"Data-driven Approaches to Viscoelastic
Flow Control,"* explicitly proposing *"control strategies through deep reinforcement learning"* for
viscoelastic turbulence. **The shortest path is also already assembled and public: RheoTool**
(Oldroyd-B, Giesekus, FENE-CR/P, PTT, PomPom, log-conformation) **+ Gym-preCICE or DRLinFluids**, both
OpenFOAM-coupled. Anyone could wire this up in weeks.

**Revised claim wording:** not "first learned model of a viscoelastic flow" (Kumar et al. own that),
but ***first to close the loop* — no learned model or RL controller has ever been closed around a
constitutive-model-resolved viscoelastic flow field.**

### The Newtonian side is far more crowded than earlier passes recorded

**~14 papers where a learned model IS the RL environment.** Canonical: Linot, Zeng & Graham, *IJHFF*
**101**:109139 (2023) — DManD 25-D neural ODE, plane Couette Re = 400, **440× speedup**, laminarizes
84% vs 58% for opposition control. Progenitor: Zeng, Linot & Graham, *Proc. R. Soc. A* **478**:20220297
(2022). Plus **SINDy-RL** (*Nat. Commun.* **16**:10714, 2025 — 14.47× sample efficiency, surrogate 10⁴×
faster than CFD); Liu, Beckers & Eldredge (*AIAA J.* **63**:4105, 2025 — the tightest literal match:
autoencoder over CFD *field snapshots* + action-conditioned latent dynamics as the RL env); Mao, Zhong
& Yin (*POF* 36:083619, 2024 — AENODE, 10% of the data); Ye & Elsheikh (*POF* 37:093363, 2025 — PETS +
MBPO, 2–9× sample efficiency); Zhang et al. (*EAAI* 162:112468, 2025 — transformer + MS-ESRGAN
full-field surrogate, CFD swapped back in every 5 interactions).

**And the 2018 archetype:** Morton, Jameson, Kochenderfer & Witherden, **NeurIPS 2018**, arXiv:1805.07472
— deep Koopman ResNet-conv autoencoder over the **full 4-channel 128×256 field** → 32-D linear latent →
16-step QP-MPC, cylinder Re = 50 with rotation. **"Learned field model in the loop" is eight years old.**

**Highest-Re instance:** Zhao et al., **PINO-PC**, arXiv:2510.03360 — a PINO *observer of the interior
velocity field* + FNO policy, turbulent channel Re_b 3,000–15,000, **39.0% drag reduction (up to
43.5%)**. Preprint only, no confirmed venue.

**The only hardware instance:** Uchytil, Korda & Zemánek, arXiv:2507.12479 — a real electrolyte steered
to prescribed velocity/vorticity fields with **PIV field feedback** and Lorentz-force actuation, Koopman
MPC real-time on a laptop. **Kills any "won't work on a real fluid" objection.**

⚠️ **"World model" is essentially unclaimed vocabulary in fluids** — Dreamer/DreamerV3/RSSM have **zero**
fluid or PDE applications. But **the door just started closing: FluidGym v2 (May 2026) added TD-MPC as a
baseline** — a latent world-model algorithm has now formally touched flow control, as an off-the-shelf
benchmark entry with no analysis.

### ⚠️ Rule-outs — the misattributions most likely to embarrass

- **"Solver-in-the-Loop"** (Um, Brand, Fei, Holl, Thuerey, NeurIPS 2020, arXiv:2007.00016) is **learned
  correction of solver numerical error, NOT control.** No actuator, no policy. *The single most common
  misattribution in this space.*
- **Kochkov et al., *PNAS* 118(21), 2021** — solver acceleration (40–80×), no actuator, no controller.
- **Novati, Lascombes de Laroussilhe & Koumoutsakos, *Nat. Mach. Intell.* 3:87 (2021)** is **not flow
  control** — MARL discovers an **LES subgrid closure**. Cite it as neither model-free AFC nor
  model-in-the-loop control.
- **The Krstić neural-operator school is not competing prior art** — all ~21 group papers learn the
  **gain/controller/observer kernel, never the plant**, and **none touches Navier–Stokes or any fluid.**
- **Dai, Xu, Zhang & Yang, *JFM* 1012:A8 (2025)** — the four-roll mill *is* the canonical Oldroyd-B
  benchmark, but the paper states the domain is **"filled with a Newtonian fluid."** Tantalizing, not a hit.

### 🚨 THREE FAILURE MODES TO PRE-EMPT — and one is an opening

1. **Distribution shift is named but UNSOLVED.** Plotzki & Peitz (arXiv:2603.28074) verbatim: surrogates'
   *"feasibility as training environments for RL is limited by **distribution shifts**, as policies induce
   state distributions not covered by the surrogate training data."* Surrogate-only training *degrades*
   performance; DNS pretraining recovers SOTA at only ~40% savings. Werner & Peitz found the same in
   2023; Zhang et al. must force CFD back every 5 interactions; Mao et al. built AENODE specifically to
   stop the error cascade. **➡️ THE OPENING: nobody has brought the standard world-model answers —
   TD-learning through the latent model, reconstruction-free objectives, MOPO-style
   uncertainty-penalised rollout truncation, SimNorm — to the fluid case.** That is a real,
   well-posed, unoccupied contribution independent of the viscoelastic angle.
2. **Offline accuracy ≠ closed-loop stability.** Cavallazzi, Pérez-Cuadrado & Pinelli, arXiv:2606.30484
   (Jun 2026): a wall-sensor neural estimator with offline correlation **0.99** and near-unity coherence
   **fails in closed loop, decorrelating within a few viscous time units** — *"not one of accuracy but of
   distribution shift induced by the controller itself."* Fixed only by spectral consistency + retraining
   on closed-loop data. **The sharpest statement of the risk to this whole framing.**
3. **Learned surrogates have never reached engineering-relevant turbulence.** Wang, Suárez, Bode &
   Vinuesa, arXiv:2604.09434 (Apr 2026) verbatim: *"Surrogate-assisted DRL has shown promise in flow
   control, yet existing studies have been limited to low-Reynolds-number laminar configurations"* and
   *"no study has demonstrated surrogate-trained policy transfer to a turbulent wall-bounded flow of
   engineering relevance."* They solve it with a **proxy DNS**, explicitly declining a learned emulator —
   leaving that route open.

### 🎁 A cheap, publishable, untested comparison

*"Differentiable-physics gradients vs learned world models have **never been compared on the same
environment**"* — and **FluidGym makes that head-to-head trivially runnable** (fully differentiable PICT
solver in PyTorch, with DPC *and* TD-MPC already shipped as baselines). Low-risk companion result.

### The community dataset with viscoelasticity — and it has no control task

**`viscoelastic_instability_v2` in The Well** (Ohana et al., NeurIPS 2024 D&B, arXiv:2412.00568): 2D
channel, **FENE-P, Re = 1000, Wi = 50, β = 0.9, L_max = 70**, 512×512, **260 trajectories across four
coexisting attractors** (laminar, steady arrowhead, chaotic arrowhead, EIT); fields p, u, v, c_xx, c_yy,
c_xy, c_zz. Physics from Beneitez, Page & Kerswell, *JFM* **981**:A30 (2024). ⚠️ Wall blowing/suction
only *generated* initial conditions — **open-loop forward sim, no actuator in the loop**. ⚠️ **Use v2 —
v1 is deprecated for processing errors.** ⚠️ Do not conflate The Well's `active_matter` with a
polymeric model.

---

## FINAL CONFIRMATION — the *Ocean Engineering* abstract, verbatim

Recovered via **NASA ADS bibcode `2026OcEng.35525161S`** (a JS SPA — fetched through `r.jina.ai`), and
independently cross-checked **character-for-character over the first 919 chars** against the Google
Scholar citation page (raw HTML, no proxy). Elsevier deposited **no abstract to Crossref at all** — the
raw `vnd.crossref.unixsd+xml` contains zero abstract blocks, which is the root cause of the nulls
everywhere else. No OA copy, no preprint.

> "…this study proposes a Physical–Data–Driven Flow Simulation framework for efficient control of
> undulatory locomotion. The framework adopts a two-stage training strategy in which **control policies
> are first trained in a surrogate-based environment and subsequently refined within a high-fidelity CFD
> solver**. To capture the distinct hydrodynamic responses associated with constant-frequency and
> frequency-switching propulsion, **multiple neural-network surrogate models are constructed and embedded
> in training**. Physics-guided compensation is further introduced to improve policy transferability…
> Overall, the proposed framework achieves efficient control of locomotion with an **order-of-magnitude
> reduction in computational cost** compared with direct CFD-based learning."

Keywords, verbatim: *"Undulatory propulsion; Deep reinforcement learning; Surrogate modeling; Vortex
dynamics."*

**✅ Bucket (b) CONFIRMED VERBATIM.** "Surrogate-based **environment**" + "subsequently **refined** within
a high-fidelity CFD solver" + "**multiple** neural-network surrogate models" — exactly as inferred from
the bibliography. No planning, no imagination, no latent world model. Speedup is **one order of
magnitude**, against Linot/Zeng/Graham's **440×** on the Newtonian side. Task is point-to-point
navigation by modulating oscillation frequency. **Adjacent, cite as the foil, not a competitor.**

⚠️ **Methodological caution worth carrying forward:** the WebSearch tool's summaries *looked* like
verbatim Highlights but were **paraphrases** — it produced "In the first stage, a dynamic model…" where
the real page text reads "**In Stage I,** a dynamic model…". Never quote a search summary as verbatim;
only quote text retrieved from a page or API you actually fetched.

---

## Appendix — paywall-routing techniques that worked (reusable)

Publishers block automated fetches (ScienceDirect, APS, AIP, Springer, IEEE, Royal Society, MDPI,
Annual Reviews all returned 403/CAPTCHA). These routes got real text anyway:

- **NASA ADS / SciX by bibcode** (e.g. `2026OcEng.35525161S`) carries full abstracts + keywords for
  closed papers. Both are JS SPAs returning HTTP 202 to curl — fetch through `https://r.jina.ai/`.
- **Google Scholar citation pages** give the abstract truncated at ~919 chars, as **raw HTML with no
  proxy** — ideal as an *independent* cross-check against an ADS pull (we diffed them character-for-
  character to confirm one abstract was genuine and not a renderer artifact).
- **APS publishes all figure captions free on the abstract page**, and the **Wayback Machine** has
  captures. Direct fetch 403s; archived copies do not. This is how Re = 7142 was recovered from Yu et
  al., *PRE* 105:045105 — and two independent captures (2022, 2024) were byte-identical. ⚠️ The 2026
  APS redesign hides captions; use older captures.
- **IEEE Xplore REST endpoints are open with no subscription** —
  `https://ieeexplore.ieee.org/rest/document/<articleNumber>/{abstract,keywords,figures,toc,references}`
  with a `Referer` header. `/figures` returns **every figure caption**; `/toc` returns section headings.
  This recovered all 11 captions + index terms from a paywalled IROS paper.
- **Crossref `application/vnd.crossref.unixsd+xml`** returns the publisher's raw deposit — use it to
  prove an abstract was *never deposited* (as opposed to merely missing downstream). Also the reliable
  route to a **complete reference list**, which is often enough to classify a paper's method by what it
  cites and does not cite.
- **Elsevier `api.elsevier.com/content/abstract/doi/…`** answers **without an API key** (stub only, but
  yields the Scopus EID). `api.elsevier.com/content/article/pii/…` gives coredata + cover date.
- Europe PMC / PMC full text for anything with a PMCID; OpenAlex for affiliations + resolved references.

⚠️ **Never quote a search-engine summary as verbatim.** In this sweep a WebSearch summary rendered
"In the first stage, a dynamic model…" where the page actually read "**In Stage I,** a dynamic model…",
and a PDF text extraction produced an entirely **fabricated author list** for Gym-preCICE (caught and
discarded by cross-checking an institutional repository). Quote only from a page or API actually fetched,
and cross-check author lists against Crossref or PubMed.
- **ISOPE hosts its own proceedings server, and it is NOT Cloudflare-walled** (unlike OnePetro). It
  serves **page 1** of each paper — which contains the full abstract, keywords, affiliations and the
  opening of the introduction. TOC: `publications.isope.org/proceedings/ISOPE/ISOPE%202024/data/toc.html`;
  PDFs under `…/data/pdfs/<id>.pdf`. Verify page count with Ghostscript — pages 2+ genuinely are not
  published, so absence of method detail there is a real negative, not a fetch failure.
- **Chinese patent full texts are public** and typically disclose joint counts, control equations and
  tuned parameters that the papers omit — a good last resort when a group's method detail is paywalled.

**Corroboration this route produced:** the ISOPE-2024 predecessor to the PD-FS line is confirmed
verbatim as **PSO over an "improved CPG network"** evaluated on a CFD platform, **no RL anywhere**, with a
real robot. And a sibling paper (*Ocean Engineering* 2024, doi:10.1016/j.oceaneng.2024.119349) reportedly
trains *"a neural-network model on a CFD dataset with motion parameters as inputs and hydrodynamic
performance metrics as outputs"* (relayed, not verbatim-verified) — **independent support for the
inference that the PD-FS surrogate maps motion parameters → performance scalars, not flow fields.**

---

## ⚠️ EPISTEMIC CONFLICT — two agents disagree on whether the *Ocean Engineering* abstract was retrieved

**Read the "verbatim abstract" section above with this caveat attached.**

**Agent A** reported the full abstract, sourced from **NASA ADS bibcode `2026OcEng.35525161S`** (via
`r.jina.ai`), and claimed an independent cross-check: **character-for-character identity over the first
919 chars against the Google Scholar citation page in raw HTML with no proxy**, with Google truncating at
*"…under realistic …"* and ADS supplying the tail.

**Agent B**, working the same target independently across ~45 routes, concluded the abstract is **NOT
publicly retrievable** and explicitly flagged the PD-FS text as a possible **fabrication trap** — i.e.
WebSearch's own model-written summary rather than retrieved text. Its strongest evidence: an
**exact-phrase probe for `"Physical-Data-Driven Flow Simulation"` restricted to `sciencedirect.com`
returned 8 unrelated papers, not S0029801826009959.**

**Plausible reconciliation, and why I lean toward Agent A:** Agent A noted, unprompted, that the dashes
are **U+2013 en dashes "confirmed at byte level"** — *Physical–Data–Driven*. Agent B's phrase probe used
**ASCII hyphens**, which would not match. That explains B's null result, and a byte-level orthographic
detail is not the kind of thing a summarizer invents. Two independent retrieval paths agreeing
character-for-character over 919 chars is also very hard to produce by hallucination.

**But treat the abstract as HIGH-CONFIDENCE, NOT CONFIRMED.** Do not quote it in print without one of:
(a) an institutional ScienceDirect login in a real browser; (b) a paid Elsevier Content API key
(`view=META_ABS` then returns `dc:description`); or (c) a reprint request to the corresponding author,
**caoshunxiang@sz.tsinghua.edu.cn** (Shunxiang Cao, Institute for Ocean Engineering, Tsinghua SIGS).

**The classification does NOT depend on the disputed text.** Bucket (b) — surrogate-as-environment, not
model-based RL — rests independently on the **Crossref-retrieved 70-item reference list**, which contains
**zero** model-based-RL or world-model citations (no Dyna, PETS, MBPO, PlaNet, Dreamer) and whose
surrogate-methods block is co-kriging + ridge regression + UQ overview. That evidence is solid.

**One refinement from Agent B:** **PPO is NOT in the reference list; TRPO is** (Schulman 2015, ref 44).
So the algorithm is **trust-region on-policy**, and the earlier "PPO or TRPO" should be narrowed toward
TRPO — while noting the group's confirmed house style elsewhere is PPO, and 3 of 70 refs are unresolved.

**Lesson for the rest of this file:** where a claim rests on a single agent's retrieval, it is marked. The
verdicts that matter most here — Stokes RL **KILLED**, viscoelastic RL-control **EMPTY**, the
Stokes-linearity/reciprocal-theorem structural argument, the benchmark-suite gap — each rest on **three or
more independent passes, with grep- or citation-level evidence**, not on any single fetch.

### ✅ CONFLICT RESOLVED — "PD-FS" is independently corroborated

A third agent found that **Shunxiang Cao's own Google Scholar profile lists a preprint form of the
paper: *"PD-FS: Surrogate-Enhanced Physical Data-Driven Framework for Rapid Deep Reinforcement Learning
Control."*** That is an **independent, author-controlled source for the framework name** — which was the
one element Agent B could not corroborate at the phrase-index level.

Combined with (a) the ADS + Google-Scholar character-for-character agreement, (b) the en-dash detail that
explains B's failed ASCII-hyphen phrase probe, and (c) the author's own listing, **the abstract is now
CORROBORATED.** Upgrade from "high-confidence, not confirmed" to **confirmed-by-triangulation**; still
worth an institutional PDF before quoting in print, but the fabrication concern is closed.

⚠️ **One more attribution trap on this paper.** Searching its title also surfaces **"Comparative CFD
Simulations of a Soft Robotic Fish for Undulatory Swimming Behaviors," *Biomimetics* 10(12):805 (2025),
PMC12730769** — by a **completely different group** (Koca, Ay, Bal, Korkmaz, Akpolat; Firat University,
Turkey), which uses **no CPG** and merely *cites* the Tsinghua IROS paper. Its highly quotable settings
(ANSYS Fluent 21, 2D, SST k-ω, Δt = T/100, 14,039 nodes, L = 1 m, **Re 99,621–498,105**, f = 0.5–2 Hz,
St 0.1–2.0, CNN-GRU on ~80,000 samples) **must not be attributed to the Tsinghua work.** Search-engine
summaries blend the two.

**Useful confirmed detail from a free source:** the ISOPE/IJOPE sibling's **COT is energy per unit
distance in J/m, not mass-normalised** — *"The COT of multi-jointed robotic fish that have been developed
is generally 100–1,000 J/m while the COT range of robots based on advanced materials is 0–100 J/m"*
(free abstract PDF at `isope.org/wp-content/uploads/2025/09/abst-35-3-p317-jc944-Wang.pdf`).

---

## Claim 6, refined — the METHOD has a name, and it's in five other communities

Earlier I recorded Claim 6 as WEAKENED. A deeper pass shows the **three-part conjunction survives** — but
"run an optimizer many times over a parameter, then symbolically regress the family of optima" is
**established prior art in evolutionary design, control tuning, optimal-control synthesis, structural
design codes, and RANS closure.** Four names must be pre-empted by name.

**1. "Automated innovization" is an entire named subfield for exactly this** (Deb & Bandaru, 2006–2017).
Deb & Srinivasan (GECCO 2006 / Springer 2008): *"first finds a set of near-Pareto-optimal solutions and
then analyses them to unveil salient knowledge about properties which make a solution optimal."*
Bandaru & Deb (2011): *"enables the designer to handcraft solutions for other optimization tasks …
**thus eliminating the need to actually optimize**."* Two entries are uncomfortably close to our framing:
**"A Dimensionally-Aware Genetic Programming Architecture for Automated Innovization"** (EMO 2013,
doi:10.1007/978-3-642-37140-0_39) — *"a method for introducing **dimensionality information** in the
search process"* — and **"Higher and lower-level knowledge discovery from Pareto-optimal sets"**
(*J. Global Optim.* **57**, doi:10.1007/s10898-012-0026-x) — *"**higher-level innovization** … the
discovery of common features among solutions from **different Pareto-optimal fronts**."* **The default
output form in innovization is a power law.**

**2. FISR — the fluid-mechanics instance, and a referee will cite it.** Field Inversion + Symbolic
Regression: an adjoint/PDE-constrained inner optimization produces an optimal corrective field per case,
then SR is fit to that family. ~6 papers, Wu/Zhang et al. 2023–2026: arXiv:2304.11347 (*PRF* 2023);
arXiv:2402.16355 (*AIAA J.* 2024, doi:10.2514/1.J064416); arXiv:2510.24192; arXiv:2510.22469; and
arXiv:2604.14569, which explicitly *collapses* the two stages — *"Unlike conventional two-stage
approaches, the correction model is optimized end-to-end … using an EQL architecture."*
**Distinction to state:** their inner loop is *data assimilation*, not design optimization; the sweep is
over flow *cases*, not a dimensionless group; and the SR target is a **local closure field vs local
features**, not an optimum-vs-Re law.

**3. Regress-the-optimum with PySR already published, 2026.** Bekdaş, Khalbous, Nigdeli & Işıkdağ,
*Processes* **14**(7):1163 (2026), doi:10.3390/pr14071163: *"1300 optimal strengthening scenarios was
generated using the Jaya optimization algorithm … subsequently processed through **symbolic regression
using the PySR platform** to identify explicit mathematical relationships … **These equations eliminate
iterative design processes**."* Dimensional design variables, not a dimensionless group.

**4. And the motivation sentence was written in 2012.** Das, Pan, Das & Gupta, *ISA Transactions*
**51**(2):237–261 (2012), arXiv:1202.5683 — GA tunes controllers, GP regresses the optimal gains:
*"These rules … inherit the power of the GA-based tuning methodology, but can be easily calculated
**without the requirement for running the computationally intensive GA every time**."* Also the Diveev
school (ECC 2020, doi:10.23919/ECC51009.2020.9143798): *"solve the optimal control problem for various
initial states, and … use the found optimal trajectories to determine the structure of the synthesizing
function."*

### ⚠️ The closest published near-miss in swimming — and why it isn't us

> Lin, Liang, Bhalla, Sheikh Al-Shabab, Skote, Zheng & Zhang, "How wavelength affects hydrodynamic
> performance of two accelerating mirror-symmetric undulating hydrofoils," *Phys. Fluids* (2023),
> doi:10.1063/5.0155661, arXiv:2212.11004.

Verbatim: *"we numerically investigate how **Reynolds number Re=1000–2000, Strouhal number St=0.2–0.7**,
and wavelength λ=0.5–2 affect the mean net thrust and net propulsive efficiency… **In total, 550 cases**
are simulated… **We apply a symbolic regression algorithm** to formulate this relationship… The highest
efficiency is obtained at St=0.5 and λ=1.2."* **SR fits the raw 550-case response surface; the optimum is
read off a grid and never itself regressed.** That is the whole distinction — state it explicitly.

### And "closed-form law for an optimal Strouhal number" is an already-populated result category

Eloy, *J. Fluids Struct.* **30**:205 (2012): *"Using Lighthill's elongated-body theory … the **optimal
Strouhal number increases from 0.15 to 0.8** for animals spanning from the largest cetaceans to the
smallest tadpoles."* Analytic, no SR. Plus Taylor's *PNAS* **115**(32) commentary (2018), literally titled
*"Simple scaling law predicts peak efficiency in oscillatory propulsion."*

### Strong negatives (load-bearing)

**arXiv metadata: `"symbolic regression" AND "shape optimization"` → 0 results.** Same for `AND "topology
optimization"` → 0 and `AND "optimal design"` → 0. OpenAlex title+abstract: `"symbolic regression" AND
"Strouhal number"` → 2 works, both the same hydrofoil paper. **Zero hits for SR/equation-discovery
combined with Deborah, Weissenberg, Womersley, reduced frequency, optimal gait scaling, or microswimmer
optimum.** *(Caveats: OpenAlex daily budget exhausted mid-session; arXiv API rate-limited, fell back to
title/abstract-only web search, so full-text-only mentions could be missed.)*

### 🚨 One PDF to obtain before writing related work

> Cao, Cao, Zhao, He & Feng, "**A Physics-Augmented Neuro-Symbolic Framework for Interpretable
> Aerodynamic Optimization and Knowledge Extraction**," *Aerospace Science and Technology* **176** (2026),
> doi:10.1016/j.ast.2026.112658.

Title/authors/venue/DOI Crossref-verified; **abstract unobtainable** (Elsevier captcha through every
route). *"Optimization **and** knowledge extraction"* makes this the one paper that could be a direct hit.

### What remains ours

The conjunction: **(1)** the swept variable is a *governing dimensionless group* — not a design variable,
plant parameter, initial state, or flow case; **(2)** the SR target is *the optimum itself* as a function
of that group; **(3)** the deliverable is framed and validated as a **new physical scaling law** (an
exponent with meaning), not a design shortcut or a closure term. **Pre-empt automated innovization, FISR,
Hi-π, and Eloy/Floryan by name in the first paragraph.**

### ✅ PD-FS method now GROUNDED IN THE AUTHORS' OWN CODE — inferences replaced, one corrected

Found not by topic search but by a **GitHub *user* search on author names**: **`github.com/FishMove-Tools`**
(bio: *"created by Zhan Ruixin, Georgia Institute of Technology and Sun Weiyuan, TsingHua University"*).
Repo `DataDriven-Tools_PyFluent` README: `- [2026-03] PDFS is accepted by Ocean Engineering`, and TODO
`- [ ] Release the PD-FS framework.` → **the framework itself is unreleased; what is public is the CFD
fine-tuning stage, the Fluent case, and the phase-2 PPO weights.**

| Question | Answer, from their files |
|---|---|
| CFD solver | **ANSYS Fluent 2023 R1 (v231), 2-D double precision**, driven from Python via **PyFluent**. Not OpenFOAM, not LBM, not an in-house IB code |
| Mesh | **Overset (Chimera)** — 48,624 cells, 98,004 faces, 326 2-D overset faces, plus a `DEFINE_GRID_MOTION` UDF |
| Equations | Residual columns `continuity · x-velocity · y-velocity · k · omega` ⇒ **2-D incompressible URANS with k-ω (SST)**. Δt = 0.005 s |
| Fluid | Material named `air` but **edited**: ρ = 1, μ = 1e-4 ⇒ **ν = 1e-4** — a scaled fluid, neither air nor water |
| **Reynolds number** | **Not stated anywhere.** *Derived* from their own `positionx.txt` (mean \|U\| = 0.242, L ≈ 0.95–1, ν = 1e-4): **Re ≈ 2,400 cruise, ~5,300 peak.** Clearly a derivation, not a quote |
| Body | **Continuously deforming, NOT rigid multi-link** — prescribed travelling wave with a quadratic amplitude envelope and a `(1 − 1/(1+10t))` startup ramp; tail p-p ≈ 20% L |
| Self-propelled? | **YES, free-swimming, 1 DOF (surge)** — `DEFINE_EXECUTE_AT_END` integrates Newton's 2nd law from `Compute_Force_And_Moment`; **mass = 0.082122**; `*omega = 0` |
| **The surrogate** | ✅ **CONFIRMS the earlier inference.** Three separate `.pth` nets — `fish_dynamics_increase`, `fish_dynamics_decrease`, `fish_dynamics_single` (恒定 = *constant*). A **regime-switched surrogate predicting body dynamics (x, v, a) on a 5-D state. NO flow-field prediction on a grid.** Maps exactly onto the abstract's "constant-frequency and frequency-switching propulsion" |
| Latent / POD / DMD | **None in the fish work** (those live in Cao's separate VIV/flag papers) |
| ⚠️ **RL algorithm — CORRECTION** | **PPO (stable-baselines3) + VecNormalize**, discrete 3-action (Δfrequency ∈ {−1,0,+1}) over 5 rungs ω ∈ {3.14…5.655} rad/s, obs 5-D `[x, v, a, w_index, steps]`, reward `−10·\|x+5.0\|` with proximity bonuses. **This overrides the earlier citation-based inference of TRPO** — TRPO is cited, PPO is used |

**Two-stage structure, verbatim from the companion repo README:** *"Stage 1 — ROM Pre-training … enabling
>10³ simulation steps per second. Stage 2 — CFD Fine-tuning: The pretrained policy is transferred to a
high-fidelity CFD environment (ANSYS Fluent) via the PyFluent interface … **This stage accounts for only
10–15% of total training time.**"*

**A second, unreleased companion paper exists:** *"DyCFish-Gym: An Intelligent Control Platform Bridging
Reduced-Order Dynamics and Computational Fluid Dynamics for Thunniform Propulsion"* (Sun, Zhan, Jiang, Li,
Huang, Cao; *Int. J. Mechanical Sciences*). Crucial distinction: in **DyCFish** stage 1 is an **analytical
2-link rigid-body ROM**; in **PD-FS** stage 1 is the **learned** surrogate. DyCFish reports *"exploiting
reverse Kármán vortices to minimize cost of transport"*, 40%/30%/20% gains over PID and MPC, and
**sim-to-real on a physical dual-joint robotic fish.**

**Independent corroboration of one abstract sentence from raw indexed text** (a Brave SERP snippet, *not*
an AI summary): *"To capture the distinct hydrodynamic responses associated with constant-frequency and
frequency-switching propulsion, multiple neural-network surrogate models are constructed and embedded in
training."* Attribution in-SERP to PII S0029801826009959, dated March 23 2026. ⚠️ The
**"Physical–Data–Driven Flow Simulation" expansion remains search-index-reported**, not verbatim-confirmed.

⚠️ **Contamination to discard.** AI summaries attributed *"max speed +3.6%", "COT −13.9% at 0.4 m/s",
"1.12 BL/s", "min COT 12.1 J/(kg·m)"* to the ISOPE predecessor. **None is groundable** — and the unit
mismatch proves it: that paper's own convention is **J/m**, not J/(kg·m). The numbers most likely belong
to Lu et al., *IEEE T-ASE*, doi:10.1109/tase.2023.3269775. Likewise, arXiv:2603.28200 (Shibayama &
Kawashima, fish-school guidance) is **not** a preprint of this paper.

**Net effect on the verdict: unchanged, now on firmer ground.** Bucket (b) — surrogate-as-environment for
model-free PPO, low-dimensional body-dynamics surrogate, Newtonian, 2-D URANS at Re ~ 2,400. **Adjacent;
cite as the foil.** The distinction to state is now sharp and code-verified: *their* surrogate predicts
`(x, v, a)`; a world model for our purposes would have to encode the **polymer conformation field**.

### 📌 Methodological lesson, earned the hard way — citation-based method inference is unreliable

**Three independent agents** analysed the same 70-item reference list and all three concluded the RL
algorithm was **TRPO**, reasoning that Schulman 2015 (TRPO) is the *only* core RL-algorithm paper cited
and PPO appears nowhere. The reasoning was sound and the conclusion was **wrong**: the authors' own
released code uses **PPO via stable-baselines3**.

**A reference list tells you what a group read, not what they ran.** Where a method claim matters, rank
evidence: released code > full text > figure captions / supplementary video descriptions > reference-list
inference. And when several agents converge on the same inference from the same artifact, that is
**correlated error, not corroboration** — they share the artifact, so agreement adds no independent
information. (Contrast the abstract case, where two *different* retrieval paths agreeing
character-for-character was genuine corroboration.)

Practical corollary for this sweep: the verdicts resting on **grep-level or citation-network evidence**
(Stokes RL KILLED; viscoelastic RL-control EMPTY; the benchmark-suite gap; the Lauga-corpus disjunction)
are solid, because each was reached by **independent methods on independent artifacts**. The verdicts that
rested on inference from a single artifact are marked as such throughout.

---

**SWEEP CLOSED 2026-07-27.** ~20 adversarial agents; saturation reached (later agents re-derived earlier
agents' findings without adding new ones). Two items remain genuinely unresolved and both need
institutional access: **Asghar et al., *Chin. J. Phys.* 96:664–677 (2025)** and **Cao et al., *Aerospace
Sci. Tech.* 176 (2026)**. Neither can overturn the central verdicts; both should be read before a related-
work section is written.

---

## ⚠️ REOPENED — a DFD 2025 abstract QUALIFIES the "RL has never touched a viscoelastic fluid" claim

I recorded three times, from three independent passes, that **RL has never been coupled to any viscoelastic
constitutive model in fluid mechanics.** That is true of the *published* literature. It is **not true of
conference abstracts.**

> **APS DFD 2025 (78th), abstract U25.10 — "Control of viscoelastic turbulence via wall blowing & suction
> optimised by reinforcement learning"** — Udit Sharma, **Miguel Beneitez**, Lisa Wittberg,
> **Ricardo Vinuesa**, **Outi Tammisola**, Seyedshahabaddin Mirjalili.
> `schedule.aps.org/dfd/2025/events/U25/10`

**Why this matters more than its length suggests.** It is flow control, not locomotion — but it means the
**Vinuesa / Tammisola / Beneitez group has already run RL on a viscoelastic flow.** And those names recur
across this entire sweep: Vinuesa/Tammisola built the **viscoelastic polymeric-stress CNN estimator**
(*JFM* 1009:A36, 2025) that names control as future work; Vinuesa co-authored **HydroGym**; **Beneitez** is
behind both the **Manchester PhD studentship on "Data-driven Approaches to Viscoelastic Flow Control"** and
the physics behind **The Well's `viscoelastic_instability` dataset** (*JFM* 981:A30, 2024).

**A DFD abstract in Nov 2025 means a paper is in preparation now.** Revise the claim to:

> *No **published** paper couples RL to a viscoelastic constitutive model. A DFD 2025 abstract exists for
> viscoelastic **turbulence flow control** (Sharma, Beneitez, Wittberg, Vinuesa, Tammisola, Mirjalili).
> **Swimming/locomotion in a viscoelastic fluid remains untouched** — but the enabling group is already
> inside the cell.*

Cite the DFD abstract yourself. Being scooped on "first RL in a viscoelastic fluid" while claiming it is
the avoidable failure mode here.

### 🎯 The strongest coverage-independent check in the whole sweep — a citation-intersection test

Rather than keyword search (which can only show absence of a phrase), this tests whether the two
literatures are *connected at all*:

- Works citing any of **5 canonical RL-swimmer papers**: **494 unique citers**
- Works citing any of **4 canonical viscoelastic-swimmer papers**: **447 unique citers**
- **Intersection: 4 papers — and all 4 are reviews or Newtonian.** (Wu, Chen, Mukasa, Pak & Gao,
  *Chem. Soc. Rev.* **49**:8088, 2020; El Khiyati et al., *EPJE* 2023, Newtonian; Mo, Li & Bian,
  *Front. Phys.* 2023, the gap statement; Yasuda, Hosaka & Komura, *J. Phys. Soc. Jpn.* **92**:121008, 2023.)

**Zero research papers bridge the two literatures.** Via OpenCitations, so it is independent of any
publisher's abstract coverage.

### Other independent surfaces swept clean

- **APS meeting abstract databases, DFD12–DFD24 + MAR15–MAR26** — 26 meetings × 18 term combinations via
  the legacy `SearchAbstract` POST endpoint. `reinforcement learning viscoelastic` = **0 across every
  meeting**; same for non-Newtonian, mucus, rheology, Weissenberg, Deborah, sperm, cilia, complex-fluid
  swim. **Sanity-checked:** DFD24 alone returns 68 hits for "viscoelastic" and 17 for "reinforcement
  learning" *separately* — so the index and query semantics work; the null is real. (DFD25 is absent from
  the legacy DB, which is why the U25.10 abstract above required a separate web route; DFD26 is not public.)
- **Journal-scoped Crossref sweeps by ISSN** across JNNFM, *J. Rheology*, *Rheologica Acta*, *Soft Matter*,
  *POF*, *PRF*, *JFM*, *Commun. Phys.*, *Sci. Adv.*, *Nat. Commun.*, *PNAS*, *PRL*, *PRE*, *PRR*, *EPJ E*,
  *Bioinspir. Biomim.*, *Nature*, *Science*, *PRX*, *Langmuir*, *JCP* → **zero** titles pairing learning
  with a viscoelastic/non-Newtonian swimmer. **JNNFM has no paper at all whose title contains "learning"
  or "neural" alongside any swimming/locomotion term.**
- **Full enumeration** of all **330** OpenAlex works matching `"reinforcement learning" AND (swimmer OR
  microswimmer OR swimming)`: only 5 contained any rheology-adjacent keyword, **none** a viscoelastic-fluid
  swimmer.
- **The field's own 2025 survey**, *"Reinforcement Learning for Active Matter"* — full HTML pulled (88k
  chars): **zero** occurrences of viscoelastic, non-Newtonian, shear-thinning, Oldroyd, rheology, Deborah,
  Weissenberg, mucus, or polymer-solution.

### One surface genuinely unsearchable — stated for honesty

**Society of Rheology annual meeting abstracts** are sold only as proceedings volumes (proceedings.com) and
are not web-indexed. No SOR abstract could be checked. Given that a DFD abstract turned out to matter, an
SOR abstract could too. Also unusable: Europe PMC's `FULL_TEXT:` field returned 0 even for control queries;
OATD returned empty 29-byte responses; Semantic Scholar hard-rate-limited (429s).

**Whitespace, stated plainly:** the two literatures contain the *same people* — On Shun Pak, Lailai Zhu,
Alan Tsang, Gwynn Elfring — and cite each other's reviews, yet not one research paper puts an RL policy
inside a viscoelastic constitutive model with a swimmer. Mo, Li & Bian (2023) is the citable, referee-proof
statement of the gap: *"**The non-Newtonian feature of the biological fluids**, the elasticity of the
microswimmers, and the tortuous elastic boundaries **are often not taken into account.**"*

---

## Claim 4 — last open Re items closed, and a correction to the canonical paper

### ⚠️ In Verma/Novati/Koumoutsakos (*PNAS* 2018), the 3D case is NOT reinforcement learning

Recovered the published **SI Appendix** (canonical PNAS URL 403s; PMC copy is a JS shim — got the real 8.3 MB
PDF via `web.archive.org/web/2id_/…`). Two things matter:

**1. Deep RL is used only for the 2D swimmers.** Fig. 5A caption, verbatim: *"a follower (solid blue line)
that adjusts its undulations via a **proportional-integrator (PI) feedback controller** to maintain a
specified position in the wake"*, and the SI has a dedicated *"Proportional-Integral feedback controller"*
section for *"the 3D follower's body-kinematics."* **So the field's flagship RL-swimming result is 2D-only;
its 3D half is classical control.** Worth stating — it further thins the "RL + resolved 3D NS + deforming
swimmer" record.

**2. Re ≈ 5000, and the definition is unconventional.** Main text: *"[Reynolds number **Re = L²/(Tν) ≈
5000**]"*; SI p. 3: *"The Reynolds number of the self-propelled swimmers is computed as Re = L²/(νT_p)."*
Note the arXiv preprint used the conventional `Re = UL/ν ≈ 5000` instead — consistent, since U ~ L/T_p, but
**cite the published form.** SI p. 6 also notes *"albeit at **Re = 500** and not Re = 5000 as studied
herein"* — that 500 belongs to **van Rees, Gazzola & Koumoutsakos, *JFM* 775:178–188**, not to this paper.
**No separate 3D Re is stated anywhere** — and since 3D uses L = 0.2 vs 2D L = 0.1 while ν is never given
numerically, neither "3D also 5000" nor "3D = 20000" is written down. **Do not cite a 3D number.**

**The algorithm is named, in the SI:** *"**Algorithm 1: Asynchronous recurrent DQN algorithm**"* — 3 layers ×
24 LSTM cells → linear; γ = 0.9; under-relaxation α = 10⁻⁴; ε annealed 1 → 0.1; BPTT + Adam; **1200 forward
simulations ≈ 46,000 transitions**; 6 observed states, 5 discrete actions (amplitudes 0, ±0.25, ±0.5).
Grep-verified **absent**: smarties, ReF-ER, V-RACER, DDPG — those are Novati's *later* work.
Solvers: 2D wavelet-adaptive vortex method (effective 4096², 1024² for training runs, FMM Poisson);
3D pressure-projection FD in **CUBISM**, 2048 × 1024 × 256, CFL < 0.1, ≈2500 steps per tail-beat.

### Zhu & Pang (*Proc. IMechE C* 237, 2023) — Re genuinely unverifiable; do not fill the gap

**IB-LBM confirmed** from the abstract: *"a hybrid method of the DRL method and the **immersed
boundary–lattice Boltzmann method (IB–LBM)**"*; the journal's own free editorial calls it the *"multi-block
geometry-adaptive"* variant. **Re is not stated in any accessible source**, and exhaustion is documented:
Unpaywall `oa_status: closed`, no repository copy, no arXiv preprint, **no Wayback snapshot of any SAGE URL**,
SAGE 403 on all six path variants, and **citation contexts for all 8 citing works pulled — none quotes a Re.**
RL algorithm likely **DRQN** (its 64 refs include Hausknecht & Stone DRQN and Mnih DQN, and contain **no**
DDPG/PPO/TD3/SAC) — circumstantial, not verified.

⚠️ **Two contamination traps on this paper.** Search summaries produce a spurious **"Re = 1000"** by blending
it with the same authors' *Sci. Rep.* **11**:1691 (2021), and a spurious **"SAC"** by blending it with a 2024
*Phys. Fluids* paper (doi:10.1063/5.0184690). Both are wrong. Sibling Re values, verbatim and **not
transferable**: *Sci. Rep.* 2021 — *"Re = ρUL/μ = 1000 … for a juvenile fish less than 5cm"*; *Front. Phys.*
**10**:870273 (2022) — *"Re = ρUL/μ = 400"* (and it contains **zero** occurrences of "three-link");
*Fluids* **7**(1):41 (2022) — *"Re = ρL²/Tμ = 2500 … equivalent to Re_u = 1000."*
Bibliographic corrections: vol 237 **issue 11** (not 10), pp. 2450–2460; affiliations are **Guangdong Ocean
University / its Shenzhen Institute**, not Shenzhen Institute of Information Technology.

**Net effect on the Re-coverage table: unchanged and slightly strengthened.** The RL-swimming Re set remains
{0} ∪ {≈1, 10 (probe), 100, 200–300, 550, 1000, 1100, 5000, 7142}, **0 < Re < 100 stays empty**, and the
5000 datapoint is now known to be **2D-only**.

---

## Surrogates & differentiable solvers for viscoelastic flow — an open question resolved, and a new risk

### ✅ RESOLVED — Brenner's differentiable solver does NOT close the viscoelastic gap

I flagged earlier (Claim 7, path 2) that Sunol, Roggeveen, Alhashim, Bae & Brenner (arXiv:**2510.24673**)
needed checking: *"verify whether their solver is truly viscoelastic or merely generalized-Newtonian."*
**Answer: generalized-Newtonian.**

Their solver is real and impressive — *"a differentiable JAX-based framework that follows established
components from JAX-CFD and immersed-boundary (IB) methods… All operations are expressed as pure JAX
transformations, enabling exact reverse-mode differentiation through the full computation"* — with implicit
and IMEX variants for viscosity stiffness, and a frame-invariant TBNN closure trained end-to-end through it.
**But the differentiable *flow* demonstrations are Carreau–Yasuda shear-thinning.** The genuinely viscoelastic
models (Oldroyd-B, Giesekus, linear PTT, with upper-convected and Gordon–Schowalter derivatives) appear
**only in the 0-D bulk-rheometry fitting section**, not in the 2-D differentiable flow solver.

Likewise Alhashim, Hausknecht & Brenner (arXiv:2403.06257, *PNAS* 2025) is **Newtonian** — its "complex
fluids" means complex geometry and suspended particles, not viscoelasticity.

**Framework audit, READMEs fetched directly:** **JAX-CFD**, **PhiFlow**, **JAX-Fluids**, **XLB** — *none*
mentions non-Newtonian, viscoelastic, polymeric, or conformation tensor. **Nobody has published a
differentiable solver that transports a conformation tensor through a flow simulation.** That gap is real,
and it is a well-posed methods contribution on its own.

### 🚨 NEW RISK — no viscoelastic ML surrogate has EVER reported a speedup, and the two closest report *overhead*

This undercuts the premise that a learned surrogate makes viscoelastic RL tractable. **It is unvalidated in
this fluid class**, and the nearest attempts go the wrong way:

- **Lennon, McKinley & Swan, RUDE, *PNAS* 120(27):e2304669120 (2023)** — verbatim: *"requiring only a small
  constant multiplicative factor of **additional computation in excess of** simulations with typical analytic
  rheological equations of state while providing substantially higher accuracy."* **An admitted overhead.**
- **Balasubramanian, Vinuesa & Tammisola, *JFM* (2025)** — FENE-P, Wi = 8, grid 1728×576×864, FCN with
  985,105 parameters. Cost: *"approximately **3,500 GPU-hours** for training a single network model"* plus
  *"approximately **1.5 million core-hours**"* for the dataset — and **no inference time and no speedup
  reported at all.**
- **Every other viscoelastic surrogate reports accuracy only, no timing:** Mangal, Saadat & Jamali,
  *J. Rheol.* **69**(2):55 (2025) (PI-DeepONet / PI-FNO / DeepONet / FNO on TEVP + **tensorial 2-D
  Giesekus**) · Saberi, Barati Farimani & Jamali, **RheOFormer**, arXiv:2510.01365 (qualitative only:
  *"accelerating predictive complex fluid simulations"*) · Cummings et al., arXiv:2607.14944 (TBNN+UDE
  **inside rheoTool/OpenFOAM V9**, trained 0.1 ≤ Wi ≤ 40, tested Wi = 1, 2.5, 40 — **zero** speed numbers;
  its only "orders of magnitude" refers to *training loss*) · ViscoelasticNet · Matos, Fernandes & Alves,
  *JNNFM* 350:105637 (2026) (PINN outputting the **matrix logarithm** of the conformation tensor).

⚠️ **The "1000× / three-orders / six-orders faster" FNO claims are NOT viscoelastic** — they trace to plasma
surrogates, geological carbon storage, melt-pool prediction, and rotordynamics. The one hard number in the
polymer space (Uglov et al., arXiv:2107.14574, **~17× vs Autodesk Moldflow**) is injection-molding with
generalized-Newtonian Cross-WLF fill physics — **not a conformation-tensor surrogate. Do not cite it as one.**

**Both a risk and an opening:** "first reported speedup for a viscoelastic-flow surrogate" is unoccupied —
but it means the number has to be *measured*, not assumed, and the honest prior from RUDE is that a learned
constitutive closure can cost *more* than the analytic one.

**Best-documented Wi coverage of any viscoelastic ROM** (useful as a target): Oishi, Kaptanoglu, Kutz &
Brunton, *R. Soc. Open Sci.* **11**:240995 (2024) — Oldroyd-B four-roll mill; fixed Wi = 2, 3.5, 4;
parametric train {4, 4.35, 4.5} → test 4.2 (**1.75% error**) and 5.0 (**~10%**); high-Wi train {6, 6.75} →
test 6.5, 7.0; aperiodic 5.5 (<10%). Still *"a considerably reduced computational cost"* with **no factor**.

**The scientific benchmark to be judged against:** King & Lind, *JNNFM* **293**:104556 (2021),
arXiv:2009.12245 — incompressible SPH with **log-conformation + elasto-viscous stress splitting**, accurate
**up to Wi = 85**. Offline CPU code.

### Graphics real-time viscoelastic — mostly not faithful, and the faithful ones aren't real-time

Relevant because "real-time viscoelastic particle methods" looks like a shortcut. It mostly isn't.

| Method | Conformation tensor? | Wi reported? | Speed |
|---|---|---|---|
| **Ram et al., SCA 2015** (MPM) | ✅ **Yes** — *"upper convected derivative terms… combined with an Oldroyd-B model"* | ✅ **Only paper that does** — Wi = 1e-4 … 1e30; *"the Weissenberg number directly controls the amount of the plasticity"* | **0.28–23.6 min/frame**, 0.3–1.3M particles (table recovered from the author's open UCLA thesis, eScholarship `qt87d1h4dn`) |
| **Barreiro et al., ACM TOG 36(6):221 (2017)** | ⚠️ Correct derivation, then *"**Instead**, we formulate viscoelasticity as a **constraint** on the conformation tensor"* — a compliant XPBD velocity constraint, not a momentum-coupled UCM stress | ❌ 0 occurrences | ✅ **The real-time one** — *"up to 15k particles… simulated at 30 ms/frame"*; 150k at 1.13 s/frame. Ships in **RealFlow** |
| **Zhang et al., CGF 43(8), SCA 2024** | ✅ Yes, full upper-convected + Oldroyd-B `s(C) = C − I` | ❌ 0 occurrences | ≈**93 s per animation-second** at 318k particles (×1.97 vs IMM, from larger stable Δt) |
| Clavet et al., SCA 2005 | ❌ **Springs** between neighbouring particles | ❌ | 1k particles ≈10 fps; 20k ≈2 s/frame |
| Brito et al., SBGames 2017; Takahashi et al., *Vis. Comput.* 32:57 (2016) | ❌ PBD **velocity correction** | ❌ | 7.76× CUDA-vs-OpenMP (same physics); max 15 fps at 100k |
| Yu et al., **XPBI**, arXiv:2405.11694 (2024) | ❌ Elasto/visco**plasticity** (Von Mises, Drucker-Prager…) | ❌ | 20k at 30 fps; 1M at 24–139 s/frame |

**Takeaways:** real-time viscoelastic *with real physics* tops out around **15–20k particles**; the graphics
"speedups" are GPU-port or larger-timestep wins, **not surrogate wins** — do not conflate them. And
Su, Xue, Han, Jiang & Aanjaneya (ACM TOG, SIGGRAPH 2021, doi:10.1145/3450626.3459820) is physically
grounded — *"generalizes prior models, such as Oldroyd-B, the Upper-convected Maxwell (UCM) model, and
classical Newtonian viscosity under one umbrella"* — but its timings/Wi could not be verified (Box-gated).

**And a fifth independent confirmation of the headline gap:** searched five ways (RL + viscoelastic flow
control; RL + polymer drag reduction with Oldroyd-B/FENE-P; RL + elastic turbulence; ML/DL microswimmer in
viscoelastic fluid; DRL + viscoelastic DNS with Wi) — *"**RL control of a viscoelastic flow with a reported
Weissenberg number appears unpublished as of July 2026.**"* Consistent with the DFD-2025 caveat above: an
abstract exists, a paper does not.

---

## Claim 4, FINAL carve-out — gait optimization at Re = 550 with resolved 3D NS already exists

All three van Rees / Gazzola / Koumoutsakos papers verified **from published-version body text** (recovered
via Wayback snapshots of the ETH CSE-Lab papercite archive). **All at Re = 550**, same definition
`Re = (L²/T)/ν`, same justification — larval zebrafish 5 days post-fertilization — and explicitly cross-cited.

| | **2012 C-start** | **2013 anguilliform** | **2015 morphokinematics** |
|---|---|---|---|
| Citation | *JFM* **698**, **pp. 5–18** (⚠️ *not* 5–44 — corrected from the 2013 paper's own reference list; the PDF is 14 pp.) | *JFM* **722**, R3 | *JFM* **775**, 178–188 |
| Re | 550 (2D **and** 3D) | 550 | 550 |
| Optimizer | **CMA-ES**, multi-host rank-µ weighted recombination | same | same |
| **Optimizes** | **GAIT / kinematics** (shape fixed) | **shape only** (kinematics fixed) | **shape AND gait jointly**, 15 params |
| Solver | remeshed vortex + Brinkman penalization + projection + level set, FFT Poisson | remeshed vortex + penalization + projection | same |
| Scale | pop. 100 (2D) → 40 (3D); δx = L/256 → L/512 | h = L/256 → L/512 | *"over **10 000** individual direct numerical simulations of 3D self-propelled bodies"* |

**So "optimizing a gait against resolved 3D Navier–Stokes at finite Re" is NOT open at Re ≈ 550.** Gazzola
et al. (2012) optimize mid-line curvature with the shape fixed — *"an optimization of the fish motion, for a
specified zebrafish-like geometry"* — and van Rees et al. (2015) do shape **and** gait together. **Narrow the
claim to Re < 100, and preferably state it as Re = O(1) / near-Stokes inertial with the band given
numerically.** The empty region remains 0 < Re < 100; it is *not* "finite Re" in general.

### ⚠️ A verification trap worth remembering — and a live instance of the failure mode recorded above

*"The Cambridge Core '…pdf' URLs that Unpaywall reports as bronze OA actually **302-redirect to the abstract
landing page**. A naive fetch returns the abstract plus reference list, from which a summarizer will happily
'confirm' CMA-ES — but that string is only there because it is the **title of the Hansen, Müller &
Koumoutsakos 2003 reference**."*

This is exactly the correlated-error mode logged in the *"citation-based method inference is unreliable"*
appendix: the artifact contains the method name, so the inference looks confirmed, and any number of agents
reading the same artifact will agree. **Unpaywall's `bronze` status does not guarantee a fetchable full
text — check that what came back is body text, not a landing page.** The Wayback route to an author-archive
PDF is what settled it.

---

## Surrogate-based gait optimization for self-propelled swimmers — already exists (Newtonian), and one paper states our motivation in print

### ⚠️ NARROWS the claim: "surrogate + swimmer + gait optimization" is occupied

Two published instances, both **self-propelled** and both optimizing **gait**:

**1. Abouhussein & Peet, *J. Comput. Phys.* 482:112038 (2023)**, doi:10.1016/j.jcp.2023.112038 — verbatim:
*"A new computational framework for high-fidelity optimization of kinematic gaits during **self-propelled
undulatory swimming**… a **surrogate-based optimization (SBO)** procedure… a **Kriging response surface**
method… Lastly, the SBO algorithm converged to an optimized gate with significantly less function
evaluations than typically observed for evolutionary algorithms."* **Nek5000 spectral element**, 2D
incompressible NS, ALE on moving body-fitted grids, 8887 elements, N = 5 and 9. Self-propelled but 1-DOF
(surge only). Converged in <60 iterations vs a COLINY-EA baseline that reached only 11.6% efficiency in 700.
**Re is an OUTPUT, not an input** — the swimmer accelerates from rest, so `Re_max = U_max·L/ν` is tabulated:
**≈3.0×10³ to 3.1×10⁴, optimum at ≈3×10⁴.** ⚠️ Two traps: the paper's *"Reynolds number ranging from
1.47×10⁵ to 2.46×10⁵"* is a **cited biological survey** (Akanyeti et al.), not the simulations; and a search
snippet attaches *"all at Reynolds number 5000"* to this title — **that figure is not in the paper.**
📌 **Also relevant to Claim 6:** it *"propose[s] a new scaling law"* for efficiency vs tail amplitude and
effective flapping length — i.e. a scaling law extracted from an optimization sweep, hand-derived.

**2. Maroun, Traoré & Bergmann, "Data-driven optimal control of undulatory swimming," *Phys. Fluids*
36(7):073621 (2024)**, doi:10.1063/5.0215502 — **SINDy** surrogate (PySINDy, polynomials to degree 4 —
explicitly *not* a neural network) + **model predictive control** for velocity tracking, plus open-loop
direct collocation (CasADi/IPOPT) for cost-of-transport minimization, *"resulting in a solution akin to a
**burst-and-coast** strategy."* 2D volume-penalization immersed boundary (Navier–Stokes–Brinkman), Chorin–
Temam. Self-propelled, x-constrained. **Re ∈ [100, 2000]**, verbatim: *"the flow Reynolds number, Re = u_G^s
l / ν is between 100 and 2000"* (their own note: *"The critical Reynolds number for undulatory swimmers is
Re_critical ≈ 3000"*). **There is no "Re = 1000" in this paper.**

### 🎯 …AND Maroun et al. states the distribution-shift problem IN PRINT, for a swimmer

This is the best available motivation for the second opening in `DECISION.md`. Verbatim from the abstract:

> *"Despite achieving energy performance comparable to continuous swimming cases, **mismatches between the
> surrogate model and the high fidelity simulation significantly impact the quality of the obtained
> solution.** This work sheds light on the potential of surrogate models in optimizing self-propelled
> swimming behavior and **underscores the importance of addressing model mismatches** for more accurate
> control strategies in the future."*

Until now the distribution-shift evidence was all Rayleigh–Bénard / channel flow (Plotzki & Peitz;
Cavallazzi et al.; Werner & Peitz). **This puts it on a self-propelled swimmer, in a peer-reviewed journal,
with the authors explicitly naming it as future work they did not do.** Cite it as the opening.

### Remaining two, for completeness

**Xu, Wei, Li & Dong, *AIAA J.* 57(9):3716–3727 (2019)**, doi:10.2514/1.J057203 — **Re = 100 confirmed
verbatim** (*"in a uniform stream at Reynolds number 100"*, `Re = U∞c/ν`); continuous adjoint with
non-cylindrical calculus; sharp-interface immersed boundary, 240×200×200; **tethered**, thrust objective;
kinematics only. Optimum (45.0°, 35.9°, 122.6°) raised C̄_T from 0.286 → 2.390 (~8×). ⚠️ One sentence in
§IV.C swaps the roll/pitch amplitude labels — a preprint typo.

**Xu & Wei, *JFM* 799:56–99 (2016)**, doi:10.1017/jfm.2016.351 — ✅ **NOW RESOLVED: Re = 100 AND Re = 300.**
Recovered from Google Scholar's index of the author-deposited PDF (the paper's own words, as search
snippets rather than a full PDF read — labelled accordingly). Verbatim: *"The Reynolds number defined by the
**incoming flow velocity and plate length** is Re = 100"*, and *"The optimization has been applied to
different Reynolds numbers: **Re = 300 and Re = 100**, and different levels of flexibility: n = 0 for a rigid
plate, n = 1 having only the first eigenmode."* Exact-phrase probes for Re = 150/200/400/500 all failed to
return the paper, so {100, 300} appears complete. **The suspicion that a single Re would be wrong was
correct.** ⚠️ Still unresolved: whether the Re = 300 sweep covers the **3-D hovering** case — for hovering
there is no incoming flow, so a different velocity scale must apply there. Tethered ("plunges normally to an
incoming flow", "against an incoming flow", "in hovering motion"; `"self-propelled"` returns zero hits);
optimizes kinematics **and deformation eigenmodes**, not shape. Solver: staggered Cartesian finite
difference with stretching + sharp-interface immersed boundary (Mittal et al. 2008 is in its reference
list); continuous adjoint with non-cylindrical calculus, conjugate-gradient.
⚠️ **Affiliation correction:** on this 2016 paper **both authors are at New Mexico State University**.
Kansas State is Mingjun Wei's *later* affiliation — correct for the 2019 AIAA companion, wrong for 2016.

**Consolidated:** all five optimize gait/kinematics; **none optimizes shape alone**; self-propelled = only
Abouhussein & Peet and Maroun et al. (both 1-DOF); tethered = the other three. ⚠️ *Methodological caution
repeated by this agent:* OpenAlex inverted-index reconstruction **garbles abstracts with repeated words** —
it mangled the JFM abstract on first attempt. Always prefer a publisher-typeset or publisher-deposited source.

**One more reusable access route, from that verification:** **Google Scholar indexes the full text of
author-deposited PDFs and returns verbatim snippets** — `scholar.google.com/scholar?cluster=<id>` plus
exact-phrase probes recovered two Reynolds numbers from a hard-paywalled JFM paper that Cambridge, Unpaywall
(`oa_status: closed`) and Semantic Scholar all reported as having no accessible full text. Exact-phrase
probes also work as **negative** evidence: `"Re = 200"`, `"Re = 400"` etc. failing to return the paper is
weak-but-real evidence those values are absent. Rate-limits aggressively; budget queries.
