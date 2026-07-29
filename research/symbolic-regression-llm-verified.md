# PROMPT
You are verifying bibliographic facts for a PhD-level literature review on LLM-based scientific equation discovery. Today is July 2026.

FIRST: load web tools with ToolSearch query "select:WebSearch,WebFetch" (max_results 2).

Then VERIFY each of the following papers by WebFetching its arXiv /abs/ page (or DOI landing page). For EACH, report: exact title, full author list IN ORDER, year/date, venue (conference/journal or "preprint"), working URL, and a 2-3 sentence summary of the method + the headline quantitative result. If a specific rediscovered equation/law is named, quote it verbatim. Mar

# RESULT
All seven verified. Findings below.

## Verification results

**1. arXiv 2602.10576 — CONFIRMED (title exact)**
- **Title:** "LLM-Based Scientific Equation Discovery via Physics-Informed Token-Regularized Policy Optimization"
- **Authors (in order):** Boxiao Wang, Kai Li, Tianyi Liu, Chen Li, Junzhe Wang, Yifan Zhang, Jian Cheng
- **Date:** 11 Feb 2026 (v1) · **Venue:** preprint (no comment/journal-ref) · cs.LG, cs.AI
- **URL:** https://arxiv.org/abs/2602.10576
- **Method/result:** Proposes **PiT-PO** (Physics-informed Token-regularized Policy Optimization), which turns the LLM from a static generator into an RL-adapted one, using a dual-constraint mechanism enforcing "hierarchical physical validity" plus token-level penalties suppressing redundant structure. Claims SOTA on "standard benchmarks," discovery of "novel turbulence models for challenging fluid dynamics problems," and that small open models beat "closed-source giants."
- ⚠️ **No headline number and no named benchmark or turbulence equation appears in the abstract** — any specific figure you cite must come from the PDF body. UNVERIFIED at abstract level.

**2. arXiv 2605.29184 — CONFIRMED (title exact)**
- **Title:** "Influence-Guided Symbolic Regression: Scientific Discovery via LLM-Driven Equation Search with Granular Feedback"
- **Authors (in order):** Evgeny S. Saveliev, Samuel Holt, Nabeel Seedat, David L. Bentley, Jim Weatherall, Mihaela van der Schaar
- **Date:** 27 May 2026 · **Venue: ICML 2026** (stated in arXiv comment field) · cs.LG, cs.AI
- **URL:** https://arxiv.org/abs/2605.29184
- **Method/result:** **IGSR** frames discovery as generate-then-select: an LLM proposes candidate basis functions ψⱼ(x) for a linear model, scored by granular influence scores Δⱼ measuring "each term's marginal contribution to generalization accuracy," with influence-guided pruning embedded in MCTS. Benchmarks: LLM-SRBench, pharmacological PKPD models, an epidemiological simulation, and real genomic data.
- **Headline result (verbatim):** IGSR "identified a novel relationship between DNA methylation and RNA Polymerase II pausing; a hypothesis that was subsequently supported via wet-lab experimentation." No numeric headline in the abstract.

**3. arXiv 2605.08694 — ID AND TITLE CONFIRMED, BUT TOPICALLY WRONG PAPER ⚠️**
- **Title:** "A Learning Method for Symbolic Systems Using Large Language Models"
- **Authors (in order):** Jian Fang, Yixun Yao, Yingfei Xiong
- **Date:** 9 May 2026 · **Venue:** preprint
- **URL:** https://arxiv.org/abs/2605.08694
- **Method/result:** This is **LLM2Ltac — automated theorem proving, not equation discovery.** It mines reusable symbolic *tactics* from formal proof corpora and feeds them to symbolic solvers. Evaluated on the Rocq 8.20.0 proof assistant: 11,725 standard-library theorems mined, tested on 6,199 theorems across four verification projects; mined tactics improved CoqHammer by **23.87%**, and combined with Claude Code gave a **9.90%** overall increase in theorems proven.
- **Flag for the review:** "symbolic systems" here means formal proof/tactic synthesis. It does **not** belong in a symbolic-regression / scientific-equation-discovery citation list — this looks like a title-similarity mis-pull.

**4. arXiv 2410.17448 — CONFIRMED (title exact)**
- **Title:** "In Context Learning and Reasoning for Symbolic Regression with Large Language Models"
- **Authors (in order):** Samiha Sharlin, Tyler R. Josephson (both UMBC)
- **Date:** 22 Oct 2024 (v1); **v3 last revised 16 Apr 2026** · **Venue: preprint** — no journal-ref or DOI beyond the arXiv DOI; I found no peer-reviewed publication record
- **URL:** https://arxiv.org/abs/2410.17448
- **Method/result:** Prompts GPT-4 and GPT-4o to propose expressions, optimized/evaluated by external Python tools with results fed back; chain-of-thought plus a scratchpad and natural-language scientific context.
- **Named rediscovered laws (verbatim):** evaluated "in rediscovery of **Langmuir and dual-site Langmuir's model for adsorption**, along with **Nikuradse's dataset on flow in rough pipes**, which does not have a known target model equation." Both models succeeded, better with scratchpad + context; explicitly "does not outperform established SR programs where target equations are more complex."

**5. arXiv 2505.07956 — ID CORRECT, TITLE INCOMPLETE AS GIVEN ⚠️**
- **Actual full title:** "Symbolic Regression with Multimodal Large Language Models **and Kolmogorov Arnold Networks**" (the supplied title truncates the second half)
- **Authors (in order):** Thomas R. Harvey, Fabian Ruehle, Kit Fraser-Taliente, James Halverson
- **Date:** 12 May 2025 · **Venue:** preprint · cs.LG, cs.NE, cs.SC
- **URL:** https://arxiv.org/abs/2505.07956
- **Method/result:** A vision-capable LLM is shown a *plot* of a univariate function and proposes an ansatz; free parameters are fit numerically, and the ansätze form the population of a FunSearch-style genetic algorithm. No fixed operator set is required. Using KANs they argue "`univariate is all you need'" and extend to multivariate functions by learning the univariate function on each edge of a trained KAN, then simplifying with an LM.
- No quantitative headline or benchmark named in the abstract — UNVERIFIED at abstract level.

**6. arXiv 2503.09592 — CONFIRMED (title exact)**
- **Title:** "Parsing the Language of Expression: Enhancing Symbolic Regression with Domain-Aware Symbolic Priors"
- **Authors (in order):** Sikai Huang, Yixin Berry Wen, Tara Adusumilli, Kusum Choudhary, Haizhao Yang
- **Date:** 12 Mar 2025 · **Venue:** preprint · cs.LG, cs.SC
- **URL:** https://arxiv.org/abs/2503.09592
- **Method/result:** Derives symbol probability distributions from domain-specific expressions (physics, biology, chemistry, engineering) and uses them to steer tree-structured RNNs; adds a hierarchical unary/binary operator tree and pre-compiled per-domain expression blocks in the operator dictionary. Result stated only qualitatively: symbol priors give "faster convergence and higher accuracy." No numbers in the abstract — UNVERIFIED at abstract level.

**7. PNAS SR-LLM — CONFIRMED, venue is solid, but the year is 2025 not 2026**
- **Title:** "SR-LLM: An incremental symbolic regression framework driven by LLM-based retrieval-augmented generation"
- **Authors (in order):** Zelin Guo, Siqi Wang, Yonglin Tian, Jing Yang, Hui Yu, Xiaoxiang Na, Levente Kovács, Li Li, Petros A. Ioannou, Fei-Yue Wang
- **Venue:** *Proceedings of the National Academy of Sciences (PNAS)* — **Vol. 122, Issue 52, article e2516995122**
- **Date:** published online **22 Dec 2025**; **issue date 30 Dec 2025** (both dates appear on the record — cite as 2025)
- **DOI:** 10.1073/pnas.2516995122 · **PMID:** 41428869 · **PMCID:** PMC12772181 · Code: github.com/ThuOneLab/SR-LLM
- **Method/result:** RAG over an external knowledge base of prior expressions and past exploration results; the LLM composes retrieved priors into small "symbolic groups," and deep RL combines those groups into complex but interpretable expressions ("standing on the shoulders of giants"). Pipeline = sampling (DRL policy net) → calibration (two-stage parameter optimization) → evaluation (fit error, similarity to expert models, complexity) → LLM-based knowledge update.
- **Headline number (verbatim):** "SR-LLM achieves a **76.1% recovery rate** on this benchmark, significantly outperforming other symbolic regression methods" — the Feynman benchmark (100 classical physics formulas), vs. eight baselines.
- **Named rediscovered laws:** the abstract says it "successfully rediscovers famous traditional car-following models and discovers new models from empirical trajectory data." The body identifies these as "the representative **Helly, GHR, and IDM** models." Note the abstract itself does not name them; the specific model names come from the results section. Full closed-form equations are not quoted as a single verbatim rediscovery statement in the accessible text — pull them from the PMC full text if you need the exact forms.

## Corrections to make before citing

1. **Paper 3 (2605.08694) does not belong in this review** — correct ID and title, but it is a Coq/Rocq theorem-proving tactic-mining paper, not equation discovery.
2. **Paper 5's title must be extended** to "...and Kolmogorov Arnold Networks."
3. **Paper 7 must be dated 2025**, vol 122(52), e2516995122 — not 2026.
4. **Papers 1, 4, 5, 6 are preprints**, not peer-reviewed venues; only **Paper 2 (ICML 2026)** and **Paper 7 (PNAS)** carry venue claims. Paper 4 is still preprint-only despite a v3 revision in April 2026.
5. Quantitative headline claims for papers 1, 2, 5, 6 are **not present in their abstracts** — do not attribute numbers to them without reading the PDFs.

## Sources

- https://arxiv.org/abs/2602.10576
- https://arxiv.org/abs/2605.29184
- https://arxiv.org/abs/2605.08694
- https://arxiv.org/abs/2410.17448
- https://arxiv.org/abs/2505.07956
- https://arxiv.org/abs/2503.09592
- http://export.arxiv.org/api/query?id_list=2602.10576,2605.29184,2605.08694
- http://export.arxiv.org/api/query?id_list=2410.17448,2505.07956,2503.09592
- https://doi.org/10.1073/pnas.2516995122
- https://www.pnas.org/doi/full/10.1073/pnas.2516995122
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12772181/
- https://pubmed.ncbi.nlm.nih.gov/41428869/
- https://github.com/ThuOneLab/SR-LLM