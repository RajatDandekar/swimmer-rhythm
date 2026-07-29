# PROMPT
You are doing rigorous literature verification for a PhD researcher. Load web tools first: ToolSearch with query "select:WebSearch,WebFetch" max_results 5.

VERIFY TWO PAPERS by fetching the arXiv /abs/ page AND the publisher landing page. NEVER cite from memory. If you cannot confirm a detail, say UNVERIFIED for that detail.

PAPER A: Gwynn J. Elfring & Eric Lauga, "Synchronization of flexible sheets" — believed J. Fluid Mech. around 2011. Find exact title, full author list, year, journal volume, page range or article number, DOI, and a working arXiv URL (try searching arxiv.org for Elfring L

# RESULT
All verification complete. Here is the report.

---

# Literature Verification Report

## PAPER A — VERIFIED

**Exact citation (all fields VERIFIED):**
- **Title:** *Synchronization of flexible sheets* — VERIFIED (identical string on arXiv /abs/, Cambridge Core landing page, Crossref registry, and Lauga's own publication list)
- **Authors:** Gwynn J. Elfring and Eric Lauga — VERIFIED (exactly two authors; Crossref renders them as "GWYNN J. ELFRING, ERIC LAUGA"). Affiliation on the Cambridge landing page: Department of Mechanical and Aerospace Engineering, University of California San Diego, 9500 Gilman Drive, La Jolla, CA 92093-0411, USA — VERIFIED
- **Journal / volume / pages:** *Journal of Fluid Mechanics* **674**, 163–173 — VERIFIED. No issue number; a true page range, not an article number — VERIFIED
- **Year:** 2011 — VERIFIED. Published online 22 March 2011; print issue 10 May 2011 (Crossref `published-online` 2011-03-22, `published-print` 2011-05-10) — VERIFIED
- **DOI:** `10.1017/S0022112011000814` — VERIFIED (resolves via doi.org → Cambridge Core)
- **arXiv:** `arXiv:1108.5791` [physics.flu-dyn; cond-mat.soft], submitted Tue 30 Aug 2011 01:34:31 UTC — VERIFIED
- **Working URLs (all fetched successfully this session):** https://arxiv.org/abs/1108.5791 · https://ar5iv.labs.arxiv.org/html/1108.5791 · https://www.cambridge.org/core/product/identifier/S0022112011000814/type/journal_article

**Preferred citation string:**
> G. J. Elfring & E. Lauga, "Synchronization of flexible sheets," *J. Fluid Mech.* **674**, 163–173 (2011). doi:10.1017/S0022112011000814; arXiv:1108.5791.

**Caveat (INFERENCE):** the arXiv posting (30 Aug 2011) *postdates* journal publication (Mar/May 2011), so arXiv:1108.5791v1 is a postprint. My full-text quotes below come from that arXiv version via ar5iv; the JFM typeset PDF is paywalled and was not accessible. Section and equation numbers I cite are the arXiv ones and may differ from JFM's.

---

## CRITICAL QUESTION — Does flexibility change the conclusion vs. the rigid 2009 case?

**INFERENCE (my reading): YES, unambiguously, and this is the paper's central claim.** With compliance, two *identical* sheets driven by *purely sinusoidal (symmetric) internal forcing* — which provably do **not** synchronize when the waveform is prescribed in a Newtonian fluid — **do** synchronize. The waveform is no longer prescribed: hydrodynamic coupling through the thin fluid layer deforms the two sheets *unequally*, and that emergent shape difference supplies the front-back symmetry-breaking that the rigid theory had to put in by hand. Symmetry-breaking is therefore *still necessary* — the mechanism is unchanged — but it is now **generated self-consistently by elasticity** rather than **required as an input assumption**. A second, sharper change: the rigid asymmetric case can lock in-phase *or* opposite-phase (and may *maximize* dissipation), whereas the flexible case has a *unique* stable fixed point at φ = 0, always the minimum-dissipation state.

### VERBATIM QUOTES — abstract
Source: https://arxiv.org/abs/1108.5791 (string byte-identical in the ar5iv full text)

> "When swimming in close proximity, some microorganisms such as spermatozoa synchronize their flagella. Previous work on swimming sheets showed that such synchronization requires a geometrical asymmetry in the flagellar waveforms. Here we inquire about a physical mechanism responsible for such symmetry-breaking in nature. Using a two-dimensional model, we demonstrate that flexible sheets with symmetric internal forcing, deform when interacting with each other via a thin fluid layer in such a way as to systematically break the overall waveform symmetry, thereby always evolving to an in-phase conformation where energy dissipation is minimized. This dynamics is shown to be mathematically equivalent to that obtained for prescribed waveforms in viscoelastic fluids, emphasizing the crucial role of elasticity in symmetry-breaking and synchronization."

The Cambridge Core landing page's abstract rendering is consistent with this (it reproduced the fragments "deformation when interacting with each other via a thin fluid layer" and "energy dissipation is minimized"), but I obtained only a partial quotation there — **full JFM-side abstract byte-match: UNVERIFIED**.

### VERBATIM QUOTES — Introduction (§I)
Source: https://ar5iv.labs.arxiv.org/html/1108.5791 — each quote below was re-checked by string search against the raw fetched HTML, not taken from a summarizer

> "In recent theoretical analysis it was demonstrated that two infinite sheets passing waves of a prescribed shape, will not synchronize in a Newtonian fluid if the shape of the waveforms η₁ and η₂ satisfy [η₂(x) = −η₁(−x+θ)] (where θ is a fixed phase shift and x is the direction along the sheets) because of the kinematic reversibility of the Stokes equations"

> "For a sinusoidal sheet, a geometric perturbation must therefore be added (for example in the form of a higher order mode) to break the necessary front/back symmetry, and give rise to a time-evolution of phase toward the synchronized state"

> "We use this model to show that elastic deformation due to fluid body interactions, with purely sinusoidal forcing, always leads to in-phase synchronization."

> "Flexibility has long been considered as an avenue for symmetry breaking in Stokes flow."

> "We show that flexible sheets with symmetric sinusoidal forcing will deform when interacting with each other via a thin fluid layer in such a way as to break geometrical symmetry, and to evolve to an in-phase conformation where energy dissipation is minimized. Further, this evolution of phase is shown to be functionally equivalent to that found for prescribed waveforms in viscoelastic fluids, illuminating the role of elasticity in symmetry-breaking and synchronization."

### VERBATIM QUOTES — what sets the stable phase (§III.1 "Linear regime: Statics")
Same source and same verification method.

> "The phase locking force is proportional to the sine of the phase, meaning that the only stable fixed point is expected to occur at [φ = 0], and hence all initial conformations will evolve to the stable in-phase conformation. We thus see that the elasticity of the swimmers, and thus fluid-structure interactions, can introduce the geometrical symmetry-breaking necessary to develop a nonzero phase locking force. The force is found to be quadratic in amplitude, reminiscent of viscoelastic symmetry-breaking; by comparison, the phase-locking force arises at fourth order in amplitude for prescribed asymmetric waveforms in a Newtonian fluid. The reason for the difference is that with elastic deformation, the sheets are ultimately not the same shape, despite having identical mechanical properties"

> "We see that the energy dissipation is a global minimum when [φ = 0] and global maximum when [φ = π]. It follows then that the cells will always evolve to a state of minimum energy dissipation."

> "It is important to note that waveforms with a prescribed broken symmetry may evolve to either the in-phase or opposite-phase conformation; in contrast, the natural symmetry-breaking due to elasticity of the bodies, or in the fluid, leads to a conformation of minimum energy dissipation."

### VERBATIM QUOTES — dynamics (§III.2) and nonlinear check (§III.3)

> "All initial conformations, [φ₀], decay in time to the stable in-phase conformation, [φ = 0]. Notably, the time-evolution of the phase for a sinusoidally forced elastic sheet we obtain here is mathematically similar to that for a fixed sinusoidal waveform in a viscoelastic fluid and for rigid bodies with flexible trajectories, emphasizing therefore the cr[ucial role]…"

> "as the forcing amplitude increases, the nonlinear equations yield an increasingly slower evolution to a synchronized conformation than that predicted by the linear regime; however, the general behavior remains qualitatively unchanged."

### VERBATIM QUOTES — Conclusion (§IV)

> "In this paper we inquired about a physical mechanism responsible for symmetry-breaking and synchronization in the flagella of biological cells such as spermatozoa. In a Newtonian fluid, two swimming sheets passing waveforms of a prescribed sinusoidal shape will not synchronize due to an excess of symmetry; however, here we have demonstrated that identical flexible sheets with symmetric sinusoidal forcing will deform, when interacting with each other via a thin fluid layer, in such a way as to systematically break the overall geometrical symmetry. This system will always evolve to an in-phase conformation where energy dissipation is minimized, in contrast to a prescribed asymmetry, which may maximize energy dissipation. In addition, this time-evolution of the relative phase is shown to be equivalent to that obtained for prescribed waveforms in viscoelastic fluids, emphasizing the crucial role of elasticity in symmetry-breaking and synchronization – be it that of the fluid, or the swimmers themselves."

### Governing results (LaTeX extracted verbatim from the ar5iv source; equation numbers are the arXiv version's)
- Eq. (13), "the main result of our paper" — phase-locking force: `f_x = -6∫₀^{2π}(η₂-η₁)(η₂+η₁)dx = 2πα sin φ`, with `α = 144A²/(576B + B³)`
- Eq. (14) — dissipation: `Ė = 12∫₀^{2π}(η₂-η₁)² dx = [24πA²/(576+B²)](1 - cos φ)`
- Eq. (16) — phase evolution: `dφ/dt = -α sin φ`
- Eq. (17) — closed form: `φ(t) = 2 tan⁻¹[tan(φ₀/2) e^{-αt}]`
- Here `A` and `B` are the dimensionless forcing amplitude and bending stiffness (`A* = Aε²k²/μω`, `B* = Bε³k³/μω`; stars dropped in the equations). **INFERENCE:** α > 0 for all physical A, B, so φ = 0 is the unique attractor and it coincides exactly with the global minimum of Ė ∝ (1 − cos φ). That is what sets the stable phase.

---

## PAPER B — BOTH candidate papers exist and are DISTINCT papers

Your prompt conflated two real works. Both VERIFIED:

### B1 — the *Physics of Fluids ~2011* one you had in mind
- **Citation:** G. J. Elfring & E. Lauga, "Passive hydrodynamic synchronization of two-dimensional swimming cells," *Phys. Fluids* **23**(1), 011902 (2011) — VERIFIED
- **DOI:** `10.1063/1.3532954` — VERIFIED (Crossref: vol 23, issue 1, article-number 011902, published-print 2011-01-01, published-online 2011-01-11)
- **arXiv:** `arXiv:1009.2102`, submitted Fri 10 Sep 2010 — VERIFIED; https://arxiv.org/abs/1009.2102 (journal-ref line reads "Phys. Fluids (2011) 23, 011902")
- **Publisher landing page:** https://pubs.aip.org/aip/pof/article-abstract/23/1/011902/985469/... returned **HTTP 403** to my fetch — direct publisher-page confirmation **UNVERIFIED**; metadata instead confirmed via the Crossref DOI registry and Lauga's own list
- **Role (INFERENCE):** this is the long-form *rigid / prescribed-waveform, Newtonian* companion to the 2009 PRL — i.e. the paper Paper A is arguing *against*, not a flexibility paper.
- **VERBATIM (abstract, https://arxiv.org/abs/1009.2102):** "…we derive the synchronizing dynamics analytically for arbitrarily shaped waveforms in Newtonian fluids, and show that phase locking will always occur for sufficiently asymmetric shapes." … "For two closely-swimming cells, synchronization always occurs at the in-phase or opposite-phase conformation, depending solely on the geometry of the cells. In contrast, the work done by the swimmers is always minimized at the in-phase conformation. As the swimmers get further apart, additional fixed points arise at intermediate values of the relative phase."

### B2 — the viscoelastic one (note: 2010, JFM, and THREE authors)
- **Citation:** G. J. Elfring, O. S. Pak & E. Lauga, "Two-dimensional flagellar synchronization in viscoelastic fluids," *J. Fluid Mech.* **646**, 505–515 (2010) — VERIFIED
- **DOI:** `10.1017/S0022112009994010` — VERIFIED (Crossref + Cambridge Core landing page fetched successfully at https://www.cambridge.org/core/product/identifier/S0022112009994010/type/journal_article; published online 8 March 2010, print 10 March 2010)
- **arXiv:** `arXiv:0912.2377`, submitted Fri 11 Dec 2009 — VERIFIED; https://arxiv.org/abs/0912.2377
- **Correction to your premise:** it is **2010, not ~2011**, it is **JFM, not Phys. Fluids**, and the author list includes **On Shun Pak** as second author — do not cite it as "Elfring & Lauga".
- **VERBATIM (abstract, https://arxiv.org/abs/0912.2377):** "In a Newtonian fluid, it was shown theoretically that such synchronization arises passively due to hydrodynamic forces between the two swimmers if their waveforms exhibit a front-back geometrical asymmetry." … "Using a two-dimensional infinite sheet model we show that the presence of polymeric stresses removes the geometrical asymmetry constraint, and therefore even symmetric swimmers synchronize. Such synchronization occurs on asymptotically faster time scales than in a Newtonian fluid, and the swimmers are seen to be driven into a stable in-phase conformation minimizing the energy dissipated in the surrounding fluid."
- **INFERENCE:** this is the paper Paper A calls "mathematically equivalent" — elasticity *in the fluid* vs. elasticity *in the swimmer* produce the same phase dynamics. If your argument is "compliance relaxes the asymmetry requirement," B2 is the cleaner, more explicit statement of it ("removes the geometrical asymmetry constraint, and therefore even symmetric swimmers synchronize"), and B2 + Paper A together are the strong citation pair.

---

## The 2009 rigid baseline you cited — VERIFIED, with one title nuance
- **Citation:** G. J. Elfring & E. Lauga, "Hydrodynamic Phase Locking of Swimming Microorganisms," *Phys. Rev. Lett.* **103**(8), 088101 (2009) — VERIFIED via Crossref (`10.1103/PhysRevLett.103.088101`, published 17 Aug 2009, article-number 088101, issue 8)
- **APS landing page** (https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.103.088101) returned **HTTP 403** to my fetch — direct publisher-page confirmation **UNVERIFIED** (blocked, not contradicted)
- **arXiv:** `arXiv:0907.0962`, submitted 6 July 2009 — VERIFIED. **Title nuance:** the arXiv title hyphenates — "Hydrodynamic phase-locking of swimming microorganisms" — while the published PRL title does not. Use the PRL capitalization/spelling when citing the journal version.
- **VERBATIM (abstract, https://arxiv.org/abs/0907.0962)** — this confirms your framing of the rigid result: "Using a simplified model (two infinite, parallel, two-dimensional waving sheets), we show that phase-locking arises from hydrodynamics forces alone, and has its origin in the front-back asymmetry of the geometry of their flagellar waveform. The time-evolution of the phase difference between co-swimming cells depends only on the nature of this geometrical asymmetry, and microorganisms can phase-lock into conformations which minimize or maximize energy dissipation."

---

## Two incidental findings worth knowing
- A third-party comment exists: Guanghua Zhu, "Note on 'Hydrodynamic Phase Locking of Swimming Microorganisms'," `arXiv:0908.4321` (29 Aug 2009, cond-mat.soft). Abstract verbatim: "We make remarks on Elfring and Lauga's [*Phys. Rev. Lett.* **103**, 088101 (2009)] paper. The energy dissipation or viscous dissipation plays an important role in the phase-locked state." **No journal reference or non-arXiv DOI found — appears arXiv-only. Peer-review status: UNVERIFIED.** Low significance, but you may want to be aware of it before leaning hard on the 2009 PRL.
- Adjacent papers that surfaced but which I did **not** verify in depth (listed only so you don't mistake them for Paper A): "Hydrodynamic interactions of sheets vs filaments: Synchronization, attraction, and alignment," *Phys. Fluids* **27**, 121901 (2015); "An actuated elastic sheet interacting with passive and active structures in a viscoelastic fluid," *Phys. Fluids* **25**, 013103 (2013); "Competing effects of inertia, sheet elasticity, fluid compressibility, and viscoelasticity on the synchronization of two actuated sheets," *Phys. Fluids* **33**, 043109 (2021); "Bistability in the synchronization of actuated microfilaments," *J. Fluid Mech.* Author lists and exact metadata for these: **UNVERIFIED**.

## Summary of what could not be verified
- JFM typeset full text of Paper A (paywalled) — full-text quotes are from arXiv:1108.5791v1
- Full byte-level match of the Cambridge-side abstract for Paper A (only partial quotation obtained)
- Direct publisher landing pages for the AIP Phys. Fluids paper (403) and the APS PRL paper (403) — both confirmed instead through the Crossref DOI registry plus Lauga's institutional publication list

**Sources:**
- [arXiv:1108.5791 abstract page](https://arxiv.org/abs/1108.5791)
- [ar5iv full text of 1108.5791](https://ar5iv.labs.arxiv.org/html/1108.5791)
- [Cambridge Core landing page, JFM 674, 163–173](https://www.cambridge.org/core/product/identifier/S0022112011000814/type/journal_article)
- [Eric Lauga publication list, DAMTP Cambridge](https://www.damtp.cam.ac.uk/user/lauga/publications.html)
- [arXiv:1009.2102 abstract page](https://arxiv.org/abs/1009.2102)
- [arXiv:0912.2377 abstract page](https://arxiv.org/abs/0912.2377)
- [Cambridge Core landing page, JFM 646, 505–515](https://www.cambridge.org/core/product/identifier/S0022112009994010/type/journal_article)
- [arXiv:0907.0962 abstract page](https://arxiv.org/abs/0907.0962)
- [arXiv:0908.4321 abstract page](https://arxiv.org/abs/0908.4321)
- Crossref DOI registry records for 10.1017/S0022112011000814, 10.1063/1.3532954, 10.1017/S0022112009994010, 10.1103/PhysRevLett.103.088101 (via api.crossref.org)