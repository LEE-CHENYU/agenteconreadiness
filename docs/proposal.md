# AgentEcon Readiness (AERead): a unified benchmark for LLM rational economic decision-making

**Proposal v0.3 — for Yuecheng Fang and Zihao Li**
Owner: Cheney Li | Date: 2026-05-26 | Read time: ~12 minutes (skim the §9.5 ownership tables on first read)

---

## Executive summary

**The direction**: measure LLM economic-decision performance on **real-world use cases** — procurement, vendor selection, persona-fit, bargaining, agentic tool selection — by **economic value** (dollar surplus, oracle-gap utility, revealed-preference rank correlation). The leaderboard is a deployment verdict: "is your agent ready for the economy?"

**The supporting framework**: provide **complete cross-layer diagnostic decomposition** through 3 layers (axioms × parameters × outcomes) and a 5-axis failure taxonomy. The decomposition is what turns a single-number leaderboard into actionable signal — telling you *why* a model fails and what to fine-tune. Without it, AERead is just another use-case benchmark; with it, it's a tool.

**The training-signal goal**: AERead's per-axis penalties are designed to plug into RLHF/DPO loops as auxiliary losses — the diagnostic surface frontier labs can use as **training signal**, not just as evaluation. Four prior-art-anchored mechanisms (Andrews 2026 training-time penalty / Chadwick 2025 inference-time correction / Qiu 2026 supervised trace mimicry / Betz-Richardson 2023 self-supervised consistency — see methodology Q5) describe the integration surface. **v0 ships**: the Andrews-style penalty/scorer reference (LP-checkable diagnostic) + observational evidence (frontier-model penalty correlated with capability across 3-5 models). **What v0 does NOT yet ship**: the *causal* claim that training a model with AERead's penalty as auxiliary loss *causes* downstream improvement. The causal claim requires a small-model training experiment (~$500-1K GPU + ~3 person-weeks; e.g., Qwen 0.5B / 3B fine-tune with vs without penalty) — pending checkpoint decision (see methodology Q10) on whether to include in v0 or defer to follow-up paper.

**The adoption strategy**: optimize the entire toolchain for **plug-and-play usability** by researchers who are NOT sophisticated engineers. Zero-code contribution via YAML; one-line evaluation via `pip install`; web form / Colab / PR submission paths; 5-minute clone-to-first-output SLO; integrate AS lm-evaluation-harness task family so frontier labs already have us installed.

Three recent benchmark papers (Harvard EconEvals March 2025, MIT Revealed Rationality Feb 2026, Stanford TERMS-Bench May 2026) each address one layer; none we know of integrate all three with cross-layer decomposition; none ship with the plug-and-play UX needed to compete with the field's adoption gatekeepers; none demonstrate the training-signal application even at the observational level.

This proposal asks: enter a 4-week trial collaboration on a bounded Phase-0 item; we revisit authorship + commitment at the 2026-06-30 checkpoint based on what actually gets contributed.

---

## 1. The opening question

A 2025 Anthropic publication reports that **5.9% of Claude API conversations are economic decisions**. JPMorgan announced LLM-agent shareholder voting; Visa announced AI shopping agents. The deployments are happening; the rationality validation is not.

Three recent benchmark papers from elite teams (spanning March 2025 to May 2026) stake claims in three corners of this problem:
- **Harvard EconEvals** (Fish/Gonczarowski, March 2025) — [arxiv 2503.18825](https://arxiv.org/abs/2503.18825): procurement/scheduling/pricing parameter+outcome layer
- **MIT Revealed Rationality** (Andrews, February 2026) — [PDF in repo](papers/pdfs/andrews_2026_revealed_rationality.pdf): label-free representation-theorem penalties at the axiom layer
- **Stanford TERMS-Bench** (Zhang/Athey/Roth-advising, May 2026) — [arxiv 2605.13909](https://arxiv.org/abs/2605.13909): bilateral negotiation outcome layer

> **Citation links.** All paper references in this proposal map to public URLs or repo-hosted PDFs via [`papers/links.md`](papers/links.md). Inline links below are first-occurrence only.

None integrate the three layers. The integrated benchmark is the open opportunity — and the timing window is narrow (6-9 months before any of these teams ships a v2 extending into the other layers).

## 2. The 3-layer hierarchy (canonical revealed-preference pipeline)

| Layer | Cat | Question | Method | Closest prior art |
|---|---|---|---|---|
| 1 — existence | A (axioms) | Are preferences internally consistent? | Bayesian model selection on choice triplets; CCEI + money-pump + Houtman-Maks family | Davis-Stober (transitivity); Andrews 2026 (penalty math) |
| 2 — identification | B (parametric utility fits) | What are the implied parameters of a chosen utility framework? v0: KT prospect theory (λ, α) + exp-vs-hyperbolic discount (δ, k) + Fehr-Schmidt social (α, β). Framework extends to ambiguity-aversion, regret theory, rank-dependent utility as v1.5+ instantiations. | Mazeika 2025 (utility engineering); Ross-Kim-Lo 2024 (LLM Economicus) |
| 3 — predictive validity | C (outcome) | A **collection of real-world economic decision use cases**, each individually `OracleDecomposable`. v0: C2 ProductProcurementGame (qualitative-evidence procurement) + D3 VendorSelectionGame (risk/uncertainty + supplier reliability). Roadmap: D2 bargaining (wrap TERMS-Bench), C1 persona-fit (IRL on 13F as Layer 2 parameter-fit case study), agentic marketplace extension, pricing competition. | TERMS-Bench (D2); EconEvals (D3 procurement precedent); novel for C2 + D3 |

The three layers map to the canonical revealed-preference pipeline: **existence** (does a rationalizing utility exist?) → **identification** (which utility, within a functional class, is consistent with observed choices?) → **predictive validity** (does the identified utility predict held-out choices?). Layer 3 uses **predict-then-validate**: fit on a training portion of revealed preferences, predict held-out, score by predictive accuracy.

**The novel contribution is the Layer 3 collection-of-use-cases framing**, not any single use case. Each Cat C / Cat D use case is `OracleDecomposable` (hidden state + simulator + oracle + scalar utility), so the same Eq. 4 decomposition applies across all of them. This is what makes the methodology paper §3 contribution rigorous: we don't just apply TERMS-Bench's Eq. 4 to one new task; we apply it to a *family*, demonstrating portability beyond their single bargaining domain.

- **C2 ProductProcurementGame (v0)**: hidden state = vendor true cost/quality + qualitative product attributes (durability / comfort / style fit / assembly friction); **v0 oracle = optimal under single declared utility-weight vector per buyer profile** (per methodology Q3 v0 scope — single-vector scoring with 4-tier optimality classification; robust-utility-family upgrade is v0.5+). Novel + massive untested deployment surface; primary demonstration site for the qualitative-evidence-interpretation layer of the §3 contribution.
- **D3 VendorSelectionGame (v0)**: single-agent, risk/uncertainty; hidden state = supplier reliability history + lead-time variance; oracle = Bayes risk minimization given declared utility curvature. Tests Axis 3 (calibration on risk) + Axis 4 (reliability-cost tradeoff). Structurally different from C2 (risk/uncertainty vs qualitative evidence) — the pair demonstrates Eq. 4 portability across two distinct procurement-style decision structures.
- **C1 Persona-fit / 13F IRL (roadmap, Layer 2 parameter-fit case study)**: hidden state = principal utility coefficients; oracle = closed-form Kelly-Markowitz. Novel — no prior LLM benchmark grounds in dollar-equivalent decisions of named human principals at scale. **Caveat**: 13F filings are an **approximate** revealed-preference proxy (long positions only, quarterly delay; shorts + derivatives not required). The rationale source repo continues to develop C1 as Layer 2 (within-class identification) infrastructure; it becomes a v0.5+ Layer 3 case study once the qualitative-evidence procurement + risk vendor scoring framework is validated. Not in the v0 first paper.
- **D2 Bargaining (roadmap, TERMS-Bench wrap)**: native TERMS-Bench instantiation; wrap their runtime when code releases.
- **Agentic marketplace extension (roadmap)**: extends D3 VendorSelection to multi-agent marketplace + agentic tool-use; EconEvals provides protocol precedent.

> **The v0 list is intentionally short.** The full open candidate pool — EconEvals procurement/pricing/scheduling wraps, Calvano-style algorithmic-collusion detection, Gale-Shapley matching, multi-issue negotiation, Vending-Bench long-horizon coherence, Zhu-Griffiths weather/event forecasting, ~25 candidates total across 7 structural clusters — is enumerated in [`layer3_candidates.md`](layer3_candidates.md) on a value × testability matrix, with per-case pros/cons + Tier S/A/B/C/D priority. Adding cases later strengthens the §3 generalization claim (more domains → broader OracleDecomposable demonstration); the candidate doc is the input to that prioritization conversation.

## 3. Novel methodology contribution: 5-axis failure taxonomy + `OracleDecomposable` generalization

This is the methodologically defensible contribution that distinguishes AERead from STEER, EconEvals, Rationality Check!, TERMS-Bench, and every other 2025-2026 LLM-economics benchmark.

**The diagnostic question prior benchmarks address only partially**: when a model scores low on a Cat C/D outcome task, *which mechanism failed?* Prior benchmarks have substantive decomposition machinery — TERMS-Bench has the Δ_inf + Δ_unc + Δ_ctrl oracle-gap decomposition within bargaining; Andrews 2026 has representation-theorem penalties (de Finetti / Afriat / SARSEU) for the axiom layer; Mazeika 2025 has the emergent-utility framework; **STEER has a 64-element taxonomy + dependency graph**; **EconEvals has the litmus / reliability / competency triplet** (competency as a pre-check is the closest precedent for AERead's Axis 4). What none of them combine is **AERead's exact 3-layer predict-then-validate pipeline (existence → identification → predictive validity) cross-cut by oracle-gap interventions across Layer 3 economic tasks** — the integrative claim is the combination, not the absence of axes in prior work.

**What the diagnostic literature itself says about this gap.** Four 2023–2026 diagnostic papers each *explicitly* discuss whether their single-axis approach is sufficient — and each admits it is not. [Chadwick et al. 2025](papers/pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) (§Future Work): "(approximate) probabilistic coherence and transitivity of preferences are necessary conditions for rationality, they are arguably **not sufficient**…it has yet to be determined how useful our system is in real-world scenarios"; and they pose precisely AERead's stack-design question: *"does a two-step refinement (first ordinal, then cardinal) outperform a single probability-based approach?"* [Betz & Richardson 2023](https://doi.org/10.1371/journal.pone.0281372) (§Future Research) calls for "improved diagnostic tools" with "high-resolution representations of an agent's probabilistic belief system" relating inferential structure of training data to current behavior. [Zhu & Griffiths 2024](https://arxiv.org/abs/2401.16646) flags the truthful-reporting assumption underlying any single-axis probability probe. Andrews 2026 §7 separates calibration from coherence as complementary properties.

Reading these papers in sequence is reading a request for AERead. The 5-axis taxonomy + cross-decomposition matrix is the integration they each pointed to; the 3-layer pipeline (existence → identification → predictive validity) is the empirical answer to Chadwick's ordinal-then-cardinal question; the collection-of-use-cases Layer 3 design is the cross-domain generalization their single-domain studies could not deliver.

**Our proposal: a 5-axis failure taxonomy**, each axis prior-art-anchored:

| # | Axis | Causal hypothesis | Prior-art anchor |
|---|---|---|---|
| 1 | **Information** | Agent lacks knowledge of hidden state | TERMS-Bench (Zhang et al. 2026) — generalized via `OracleDecomposable` |
| 2 | **Consistency** | Agent's preference / belief structure violates axioms | Andrews 2026 (representation theorem penalties) |
| 3 | **Calibration** | Agent's economic parameters are misfit | [Mazeika 2025](https://arxiv.org/abs/2502.08640) (utility engineering); [Guo 2017](https://arxiv.org/abs/1706.04599) (ECE diagnostic); Gneiting-Raftery 2007 (proper scoring rules — [PDF](papers/pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf)) |
| 4 | **Computational floor** | Agent can't execute the math the choice requires | Specific quantity-substitution operationalization; EconEvals 2025 competency-as-prerequisite is the closest precedent (we extend it from pre-check to per-axis decomposition) |
| 5 | **Meta-cognitive calibration** | Agent's confidence is uncalibrated (stated ≠ realized accuracy); separately, agent's probability judgments are internally incoherent | Yamin et al. 2026 ([arxiv 2602.06286](https://arxiv.org/abs/2602.06286)) (belief coherence); Zhu & Griffiths 2024 (incoherent probability judgments); Chadwick 2025 (Dutch books / money pumps) |

Each axis has a distinct intervention mechanism and **approximately** decomposes the per-(model, task) gap; interaction effects between axes are explicitly measured (pairwise factorial design) rather than assumed away. Cross-decomposition (information × consistency, etc.) produces an attribution matrix with main-effect + interaction-effect cells + residual.

**Generalizing TERMS-Bench Eq. 4 (the load-bearing claim for Axis 1)**: Zhang et al. 2026 introduced the oracle-gap intervention decomposition U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl, but presented it as bargaining-specific. We abstract the construction into an **`OracleDecomposable` interface** — any task with (hidden state, controllable simulator, oracle policy, belief substitution, state reveal, scalar utility) admits the same decomposition. The **generalization is the multi-use-case application**:

- **v0 — C2 ProductProcurementGame**: hidden state = vendor true cost + structured qualitative attributes (per methodology Q3); **v0 oracle = optimal under single declared utility-weight vector per buyer profile** (robust-utility-family is v0.5+ upgrade per Q3). Eq. 4 applied to a qualitative-evidence procurement domain.
- **v0 — D3 VendorSelectionGame**: hidden state = supplier reliability + lead-time variance; oracle = Bayes risk minimization given declared utility curvature. Eq. 4 applied to a risk/uncertainty domain — structurally distinct from C2 (qualitative evidence vs declared probabilistic risk).
- **Roadmap — D2 bargaining**: native TERMS-Bench instantiation; wrap their runtime when code releases (their `github.com/zou-group/terms-bench` repo is 404 as of 2026-05-26; expect release within 1-3 months). Eq. 4 in its native form.
- **Roadmap — C1 persona-fit (Layer 2 parameter-fit case study)**: hidden state = principal's IRL-fit utility coefficients (α_kelly, δ_turnover); oracle = closed-form Kelly-Markowitz. Eq. 4 applied to portfolio/investment domain. Rationale source repo continues to develop the IRL infrastructure; first appears as a v0.5+ Layer 3 case once the v0 procurement + vendor framework is validated.
- **Roadmap — agentic marketplace extension**: extends D3 to multi-agent marketplace + agentic tool-use; EconEvals provides protocol precedent.

Demonstrating the same Eq. 4 mechanics across two structurally distinct procurement-style decisions (qualitative-evidence procurement vs risk/uncertainty vendor selection) is what makes the v0 claim a generalization, not just an application. **v0 implements two deep games (C2 + D3); roadmap wraps add D2 (bargaining via TERMS-Bench) + C1 (persona-fit) + agentic marketplace** — the broader 5-use-case demonstration is staged across v0 → v0.5 → v1, not v0 alone. Scope discipline at v0 is what makes the first paper publishable rather than diffuse.

The methodology paper's §3 contribution is precisely:

> *"Prior benchmarks decompose failures along narrower axes than the integrated taxonomy AERead proposes. We propose a 5-axis failure taxonomy — information (extending Zhang et al. 2026 via `OracleDecomposable`), consistency (extending Andrews 2026), calibration (extending Mazeika 2025), computational floor (extending EconEvals 2025 competency-as-prerequisite from pre-check to per-axis decomposition), and meta-cognitive (extending Yamin et al. 2026). We estimate the per-(model, task) gap using a pre-registered factorial intervention design: each axis admits a distinct intervention; we report main effects, pairwise interactions, and residual unexplained gap. The per-axis main effects explain a **domain-dependent** fraction of variance (working hypothesis: 60-75% for clean single-agent procurement; 55-75% for vendor selection under risk; declining to 30-55% for multi-agent markets and 25-50% for long-horizon agents — see [`methodology.md` § Q7](methodology.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual) for the full per-domain table). This is an **empirical hypothesis to be validated per domain**, not an assumed uniform threshold. We demonstrate the OracleDecomposable Eq. 4 generalization across two structurally distinct procurement-style decisions — C2 ProductProcurementGame (qualitative-evidence procurement) + D3 VendorSelectionGame (risk/uncertainty supplier selection) — in v0, with planned roadmap extension to D2 bargaining (TERMS-Bench wrap), C1 persona-fit (portfolio/investment), and agentic marketplace."*

This respects all prior art (we're extending, not claiming to invent) while staking the integrative claim.

**Why the falsifiability matters for citation**. The per-domain explanatory-power hypothesis is **pre-registered with falsification criteria** before cross-model evaluation begins (per-domain bands in [`methodology.md` § Q7](methodology.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual)): for any given domain, if Layer 1+2 explain > 80% of the gap → 5-axis decomposition simplifies; if < 50% → the 5-axis residual becomes the headline; if 50-80% → the architecture is empirically justified for that domain. This is what makes the §3 contribution **citable as methodology** rather than asserted as framework — an empirical claim with a stated falsification path per domain, regardless of which band the data land in. **The pre-commercial citation channel we're optimizing for is methodological engagement from frontier-lab researchers** (safety, economics-of-AI, evaluation methodology); pre-registration is the artifact that invites that engagement.

**Diagnostic surface**: every per-(model, task) result has a drill-down page rendering a **5-axis radar chart** with one spoke per axis + headline ("model X's primary failure mode is Axis 3 calibration via B1 risk-preference miscalibration during persona inference") + cross-decomposition matrix for advanced users.

> **Open methodological questions** — ten strategic questions critical to frontier-lab methodological engagement are addressed in a dedicated Q&A section: [`methodology.md` § Critical methodological questions](methodology.md#critical-methodological-questions-open-qa). The ten Qs (each tagged with v0 scope vs v0.5+ deferrals): (Q1) function misspecification + within-class identification rigor — v0 uses 3 functional classes; (Q2) numeric-feature evaluation discipline; (Q3) qualitative-feature scoring discipline — v0 single-stage 4-tier optimality with single utility-weight vector (robust utility family + two-stage scoring v0.5+); (Q4) generalization battery — v0 ships 3 splits + 2 counterfactual variants + Transfer Ratio (compositional-OOD, far-OOD, rotating seasons, overfit-bot, Generalization Index composite all v0.5+); (Q5) RL environment + training-signal mechanisms — v0 ships Andrews-style penalty/scorer reference (LP-checkable diagnostic; auxiliary-loss fine-tuning pipeline NOT in v0); Chadwick / Qiu / Betz described but deferred to follow-up paper; (Q6) TERMS-Bench-as-training-signal overfitting + AERead-Train/Dev/Cert — docs-only convention in v0; (Q7) Layer 1+2 vs Layer 3 residual hypothesis (per-domain estimates); (Q8) OpenSpiel-compatible environment substrate ([`aeread_env_design.md`](aeread_env_design.md)) — **not v0.5; separate post-v0-paper follow-up paper**; (Q9) operational emergence definition (5-criterion conservative claim); **(Q10) training-signal validation (scorer vs validated training signal) — the most consequential v0 scope decision: whether to include a small-model (Qwen 0.5B / 3B) training experiment in v0 to causally validate the per-axis penalty as training signal, or defer to follow-up paper. Pending 4-week checkpoint resolution.** Each Q&A entry ends with an "Open:" invitation. Engagement on all ten invited at the 2026-06-02 first sync and again before methodology-paper preprint circulation.

## 4. Five methodological commitments (each citation-anchored)

1. **Descriptive measurement, not normative ranking.** Higher composite scores ≠ better-aligned. Each dimension reports a fingerprint; downstream users decide which dimensions matter. *Anchored: Andrews 2026 §7 — "coherence is not sufficient for good behavior."*

2. **Measurement-model pluralism.** Each axiom-style sub-test fits 4-6 competing measurement models on the same data; reports Bayesian posterior. *Anchored: Echenique 2021 on CCEI; Davis-Stober mixture-of-orderings finding.*

3. **Judge-free by construction.** No LLM evaluates another LLM's output. Three concurrent 2025-2026 benchmarks (TERMS-Bench, EconEvals, Revealed Rationality) independently rejected LLM-as-judge; AERead is the integrated artifact exploiting this property across all three layers. *Anchored: TERMS-Bench environment-as-verifier; EconEvals "directly grounded in theoretical model"; QEDBench documented LLM-judge alignment gap.*

4. **Context-conditional axiomatization** is a measurable dimension, not an assumption. Personas, system prompts, and domain framing already degrade axiom compliance. *Anchored: Wen 2025 — biotechnology-expert and economist personas substantially reduce GARP compliance vs baseline.*

5. **Cross-layer attribution + oracle-gap decomposition.** The diagnostic depth that turns scores into actionable signals. The five commitments above describe AERead's integrative methodology stance — STEER (64-element taxonomy + dependency graph), EconEvals (litmus / reliability / competency triplet), Rationality Check!, TERMS-Bench (oracle-gap at one layer), and Andrews 2026 (representation-theorem penalties at one axiom) each formalize a subset of these commitments; AERead's contribution is the **integration of all five** rather than the introduction of any single commitment.

## 5. Adoption-key findings (the launch strategy)

A traction analysis of 25 benchmarks (in the master plan) identified the cross-paper patterns that determine adoption:

| Pattern | Evidence | AERead strategy |
|---|---|---|
| **Live submission leaderboard with auto-scoring is the highest-leverage adoption mechanism.** | Every benchmark >200 cites has it (MT-Bench/Arena 5,639 cites + 39K stars; SWE-bench 2,299 cites + 5K stars; GPQA 2,586 cites). Every paper without one (EconEvals 1 cite, Rationality Check! 0 cites) sits at 0-1 cites despite Harvard/Tsinghua authorship. | **Live leaderboard as Day-1 infrastructure**, not Phase-2. Hard launch gate. |
| **Industry-lab model-card adoption is a bigger amplifier than top-conference accept.** | GPQA reached 2,586 cites *without a formal venue*, purely via Anthropic/OpenAI/DeepMind model-card citations. STEER at ICML 2024 reached 26 cites in 27 months. | **Pre-commit a frontier-lab partner before launch.** Hard launch gate. |
| **Stanford/MIT/Harvard PI brand is necessary but not sufficient.** | EconEvals (Gonczarowski + Harvard) at 1 cite at 14 months. STEER (Leyton-Brown ICML) at 26 cites. Brand opens the door; *distribution drags the paper through*. | Senior endorsement (Athey/Roth via Erica) is one of multiple amplifiers, not the only one. |

**Exemplar trajectory**: Utility Engineering (Mazeika/Hendrycks/CAIS) reached 50 citations + NeurIPS 2025 + viral X thread in 15 months in this same niche. Their launch playbook is the closest reference.

**Anti-exemplar**: Rationality Check! (Tsinghua + James Evans, Sept 2025) sits at **0 citations / 1 GitHub star after 8 months** despite claiming "first omnibus rationality benchmark." Their fate is the precise outcome we avoid via (a) Day-1 leaderboard, (b) frontier-lab partner, (c) memorable name modeled on GDPval (AERead, not RationalityBench).

## 6. Why now (the timing window)

- Three recent benchmark papers (March 2025 – May 2026) establish the field is forming
- TERMS-Bench code is not yet released (their repo is 404); first-mover on the integrated benchmark is open for the next 3-6 months
- LLM frontier labs are deploying agents in economic tasks faster than evaluation infrastructure can characterize them
- Open Philanthropy is funding AI evaluation infrastructure in 2026
- The traction analysis exemplar (Utility Engineering, 15-month adoption arc) suggests a 6-9 month window from preprint to model-card adoption for benchmarks that ship with the right architecture

Without consolidated infrastructure landing in this window, the field fragments permanently around three competing benchmarks.

## 7. Engineering plan — AI-accelerated MVP

### v0 runtime: ~2-3 weeks internal MVP; ~8-12 weeks public research-grade artifact

Two distinct milestones, both Cheney-time + API spend:

- **Internal MVP (~2-3 weeks of focused build)**: Claude Code drafts from the runtime spec; scorer + adapter + cache scaffolding works end-to-end on a toy task; one model evaluated end-to-end; enough to validate the architecture but not yet reproducible by external researchers.
- **Public research-grade artifact (~8-12 weeks total — v0 scope per post-audit trim)**: **good-hygiene reproducibility** — cache layer + locked held-out test set + bootstrap confidence intervals + model/prompt-version hashes + cache manifest (NOT cryptographically signed in v0; signed ScoreRecords + hard anti-contamination guarantees defer to v0.5+). Plus contributor docs, web-form submission backend, cross-model validation runs (3-5 frontier models; 8+ models defer to v0.5+), reliability-diagram visualization. This is the artifact the methodology paper points at. Reproducibility is "honest hygiene, externally auditable via cache hashes" — not "cryptographic provenance guarantee" — in v0.

The 2-3 week timeline alone is not credible for a research-grade reproducible benchmark; the 8-12 week timeline matches the Phase 0 → Phase 2 trajectory in the methodology-paper plan (§7 below) where Phase 0 ships the scaffold and Phase 1-2 harden the reproducibility surface. v0 content (**trimmed to fit 3-4 person team × 16-week timeline** per post-audit scope discipline):

- **Adapter framework** (lm-evaluation-harness integration) for Cat A + Cat B + Cat C v1
- **Scorer + generator library — v0 subset**: ~3 scorers (Brier + transitivity + 1 multi-class utility-fit) + ~4 generators (enough for C2 + D3). Full library (~9 scorers, ~11 generators) defers to v0.5+.
- **Cache layer** — reproducibility guarantee; signed-ScoreRecord enforcement defers to v0.5+
- **5-axis diagnostic decomposition** (paper claim intact; v0 implementation tiered):
  - Axis 1 (information): full Δ_inf via `OracleDecomposable` Eq. 4 — **v0**
  - Axis 2 (consistency): 2 axiom tests (transitivity + dominance) — **v0**
  - Axis 3 (calibration): Brier/CRPS + within-class utility-fit error — **v0**
  - Axis 4 (computational floor): 1 quantity-substitution probe — **v0 sketched only**; full suite v0.5+
  - Axis 5 (meta-cognitive): confidence elicitation + Brier calibration — **v0 sketched only**; Dutch-book / probabilistic-identity probes v0.5+
- **Live leaderboard** at agenteconreadiness.org with diagnostic drill-down page (5-axis radar; v0 shows axes 1+2+3 fully + axes 4+5 as sketched cells; main effects only — cross-decomposition matrix defers to v0.5+). Closest design precedent: [TERMS-Bench leaderboard](https://terms-bench.github.io) — 7 orthogonal diagnostic axes on a sortable table.
- **One submission path** (web form) — Colab + PR paths defer to v0.5+
- **Validation runs** — 3-5 frontier models pre-launch (NOT 8+; that's v0.5+ scope)

**Deferred to v0.5+** (per methodology.md Q3/Q4/Q5/Q6 + post-audit scope): full 5-functional-class multi-class fits (v0 ships 3); robust utility family (v0 single weight vector); multi-stage qualitative scoring (v0 single stage); 5-counterfactual battery (v0 ships 2); compositional + far-OOD splits + rotating seasons (v0 ships dev + hidden IID + 1 axis-OOD); overfit-bot baseline; Generalization Index composite; pairwise interaction matrix; 3 of 4 RL training-signal mechanisms (v0 ships Andrews-style penalty/scorer reference only — Chadwick/Qiu/Betz implementations defer to follow-up paper); signed-ScoreRecord enforcement; cross-decomposition diagnostic matrix; Colab + PR submission paths; AERead-env substrate (now flagged as post-v0-paper follow-up paper, NOT v0.5).

Total bootstrap cost: under $10K in API spend + author time (3-5 model validation runs, not 8+).

### Methodology-paper timeline (where the human-collaboration weeks actually live)

The methodology paper, not the runtime, is the timeline's critical path. The intellectual contribution (5-axis taxonomy formalization, OracleDecomposable identification conditions, predict-then-validate validation across 2 v0 use cases — C2 + D3) is where collaborator hours matter most:

| Phase | Calendar | Activity |
|---|---|---|
| Phase 0 — trial collaboration | Weeks 1-4 | Each contributor takes 1-2 Phase-0 DoL items from §9; Cheney drafts §1+§2 in parallel; output drives the §9.6 checkpoint discussion |
| Phase 1 — paper draft | Weeks 5-8 | Methodology paper §3 (5-axis + OracleDecomposable) drafted (continuing from Zihao's Phase-0 work); §1+§2 polished from Cheney's Phase-0 drafts; §6 polished from Yuecheng's Phase-0 (D) draft if picked, else first draft; §10 (Zihao) first draft; arxiv preprint target |
| Phase 2 — preprint + reviews | Weeks 9-12 | External methodology reviews (Andrews, Gonczarowski); leaderboard launch with 3-5 frontier models (8+ defers to v0.5+); frontier-lab pre-commit conversations |
| Phase 3 — submission + pilot | Weeks 13-16 | NeurIPS / COLM submission; Tier 2 audit pilot conversations with 1-2 design-partner financial firms |

## 8. Commercial framing (separate from research collaboration)

If the benchmark establishes the brand (Tier 1, marketing engine), three downstream tiers become defensible:

- **Tier 2**: enterprise audit / certification — "your agent fails axiom X in scenario Y; here's the dollar-impact estimate" — $50K-500K per audit. **Anchored on Andrews 2026** representation-theorem rigor for credibility.
- **Tier 3**: online monitoring SaaS — Datadog/Sentry pattern. LangSmith / Patronus / Galileo cover safety / hallucination / RAG but not rationality.
- **Tier 4**: training-signal API — rationality penalties as auxiliary RLHF / DPO loss. **Andrews 2026 provides the academic foundation** (de Finetti / Afriat / Echenique-Saito penalties are LP-checkable in polynomial time, label-free). Cite this in any commercial pitch.

Combined realistic 5-year ARR ceiling: $50-350M.

**This proposal does NOT ask you to commit to the commercial layers.** The v0 methodology paper is a research collaboration; commercial structure is decided separately and revisited at month 6 post-launch.

## 9. Initial division of labor — trial collaboration

The principle: **contribution patterns drive authorship, not vice versa.** A negotiated authorship order before any work happens is premature — none of us has signal on collaboration fit yet. So §9 proposes an initial **division of labor (DoL)** for a 4-week trial; authorship + time-commitment budgets are revisited at the 4-week checkpoint (§11) based on actual contribution patterns.

### 9.1 Cheney Li (lead)

Methodology integration + ergonomic design (UX, contributor experience, leaderboard layout) + v0 Category C implementation (C2 ProductProcurementGame + D3 VendorSelectionGame task design) + external outreach + grant management. Note that the §3 methodology core is Zihao's track (§9.2) and the stats-specific methodology is Yuecheng's (§9.3); Cheney owns the integration layer that holds them together + the v0 game implementations + the product/UX surface. Has working 13F-extraction pipeline (~309 named investor network mapped — informs C1 persona-fit roadmap Layer 2 infrastructure in the rationale source repo; not in v0 first paper); has Phase-0 baseline transitivity test results on Claude / GPT / DeepSeek.

**Phase-0 commitment** (independent of any collaborator decision):
- Ship A4 stability dimension end-to-end by 2026-06-09
- Draft methodology paper §1 + §2 by 2026-06-23 for collaborator review

### 9.2 Zihao Li — proposed Phase-0 DoL (econ + formal-math foundation track)

Zihao's economics + formal-mathematics background is the natural fit for the **load-bearing methodology work**: the Layer 1 axiom protocols, the Layer 2 identification framework, and the OracleDecomposable formalization that generalizes TERMS-Bench Eq. 4. This is the §3 methodology-paper core — without it, the benchmark has no rigorous claim.

Phase-0 options (pick 1-2 for ~8-30 hours total, depending on which):

- **(A) OracleDecomposable formalization.** Formalize the OracleDecomposable interface mathematically — what are the precise conditions that admit the Δ_inf + Δ_unc + Δ_ctrl decomposition? Anchor on Zhang et al. 2026 TERMS-Bench §4 (their Eq. 4 derivation); the methodology paper §3 takes this verbatim. **Scope (10 formalization items)**: (1) task distribution — what is random (hidden state / context / prompt / model sampling / counterpart behavior)?; (2) action space — discrete / continuous / sequential / tool-mediated?; (3) utility functional — scalar over terminal outcomes, trajectories, or both?; (4) oracle policy — Bayes-optimal relative to which prior + simulator specification?; (5) information intervention — what does "reveal state" mean without changing task semantics?; (6) uncertainty intervention — how are beliefs elicited or substituted without confounding the policy?; (7) control intervention — what residual remains after state + belief interventions?; (8) stochastic policy handling — score over one sample, repeated samples, or an estimated policy distribution?; (9) non-commutativity — do interventions commute, or do we need a Shapley/Sobol-style attribution?; (10) failure conditions — which candidate tasks fail the abstraction and why? Identify which of **v0 use cases (C2 ProductProcurementGame + D3 VendorSelectionGame)** satisfy each condition + where the abstraction breaks, and what **roadmap wraps (D2 bargaining + C1 persona-fit + agentic marketplace)** need. **~10-15 hours.** This is the highest-leverage single item in the trial.

- **(B) Layer 1 axiom protocol specs.** Draft the formal specifications for the Layer 1 axiom-test family: CCEI, GARP, WARP, transitivity, monotonicity, Houtman-Maks. For each: test definition + what passing means + the Bayesian-model-selection posterior structure under measurement-model pluralism (4-6 competing measurement models fit on the same data; reported posterior over them). Pair with [Andrews 2026](papers/pdfs/andrews_2026_revealed_rationality.pdf) representation-theorem penalties as the Axis 2 (consistency) mathematical anchor. **~10-15 hours.**

- **(C) Layer 2 identification framework.** Formalize the within-class identification claim: given a functional class (KT '79 prospect theory, CRRA, CARA, cumulative prospect theory TK '92, Kelly-Markowitz), what does identification mean operationally? When does the framework recover unique parameters vs admit non-uniqueness (Andrews 2026's critique that representation theorems guarantee existence, not identification)? Draft the §3 methodology-paper subsection that handles this. **~10-15 hours.**

- **(D) Layer 3 candidate curation — mechanism-design lens.** Read [`layer3_candidates.md`](layer3_candidates.md) (open pool of ~25 cases on a value × testability matrix); from your mechanism-design background, do either or both:
  1. **Propose 2-3 additional candidates** not yet in the pool (examples we suspect are missing: spectrum auctions, prediction markets, generalized second-price / AdWords mechanism, market-maker bid-ask spread, revenue-equivalence stress tests). For each: source paper(s), OracleDecomposable mapping sketch, matrix-position justification.
  2. **Formalize the oracle policy for 1-2 existing high-value cases** that currently sit in medium testability (A2 EconEvals pricing or B1 Calvano collusion are the highest-leverage targets) — move them into the high-testability column by deriving the closed-form oracle their mechanism-design lit supports.
  
  Either path closes the same matrix gap: "high economic value × high testability" is the quadrant where the OracleDecomposable Eq. 4 generalization gets the strongest empirical demonstration (the methodology paper §3 claim), and it's currently sparse because the oracle-derivation work hasn't been done. **~8-12 hours** for either path; ~15-20h if you do both. This is the highest-leverage Phase-0 item for the candidate-pool curation workstream in §9.5.

You're effectively the §3 co-lead of the methodology paper if this trial converts. One item alone is sufficient signal for the trial; picking more is welcome but not expected.

Time commitment for Phase-0: **~8-30 hours over 2-4 weeks** depending on scope picked (option D alone is ~8-12h; pairing (A)+(B) or (A)+(C) is ~25-30h on the upper end).

### 9.3 Yuecheng Fang — proposed Phase-0 DoL (benchmark implementation + stats-methodology track)

Yuecheng's prior benchmark-building experience is the natural fit for two adjacent surfaces: (1) **statistics-specific methodology leadership** — predict-then-validate experimental design, cross-validation, held-out test design, statistical reproducibility framework — and (2) **benchmark implementation (math/stats-heavy side)** — standard scorer library (the Bradley-Terry / WST/MST/SST / KT-MLE / isotonic implementations), Layer 3 cache extensions (splits / fits / predictions for predict-then-validate), validation runs + statistical analysis. The complementary researcher-facing surface (generator library, CLI design, submission paths, leaderboard frontend) is Cheney's — see §9.5 split note. Phase-0 options (pick 1-2 for ~10-20 hours total):

- **(A) Standard scorer library scoping memo + first scorer implemented.** Review the runtime spec §5 scorer / generator menu (request access from Cheney per §15 below); propose which 3-5 scorers ship in v0 and which defer to v1.5; **then implement one of the v0 scorers end-to-end** (e.g., Bradley-Terry transitivity scorer with measurement-model-pluralism plumbing). The scoring layer is the load-bearing primitive for Layer 1 + Layer 2 outputs — picking the right v0 set determines what dimensions can actually be measured at launch. ~8-12 hours.

- **(B) lm-evaluation-harness integration prototype.** Sketch the entry-point structure that makes AERead install as an `lm_eval/tasks/aeread_*` task family — a single end-to-end smoke test on a toy task (e.g., a 5-option transitivity probe on Haiku) showing the integration works. Include cache layer for response replay (per §14.7). This is the §5 plug-and-play adoption gate. ~10-15 hours. **Note**: this item may shift to Jingyi Lu (see §9.4 open ops slot) if she joins as an ops collaborator — in that case Yuecheng's Phase-0 menu narrows to (A) + (C) + (D).

- **(C) Composite-score schema implementation + thin frontend prototype.** Cheney owns the leaderboard design spec (what's the right user-facing single number, how does the 5-axis radar map to a sortable column, what's on the drill-down page); your task is to **ship a static-HTML leaderboard prototype** with 1-2 mock results that validates Cheney's design spec works in practice + propose any implementation tradeoffs the spec didn't anticipate. Closest design precedent: [TERMS-Bench leaderboard](https://terms-bench.github.io) — study their 7-column orthogonal-axis layout (SE⁺, AGR⁺, CSE⁺, FAGR⁻, BEtype, CritViol%, Ū); AERead extends this pattern with the 5-axis radar + drill-down. ~8-12 hours.

- **(D) Predict-then-validate experimental design memo.** Stake out the statistics-specific methodology that becomes §6 of the methodology paper: train/test split protocol (stratified by what?), seed + immutable-manifest discipline, cross-validation scheme for the multi-class robustness check (per-persona K-fold? leave-one-out?), the held-out-set reporting convention (point estimate + bootstrap CI? full posterior?), reproducibility requirements (cache manifest hash + scorer-version + measurement-model-set version). Pair with Zihao's §9.2 (C) Layer 2 identification work for the formal justification. **~10-15 hours.** This is the highest-leverage Phase-0 signal for the stats-methodology-lead workstream in §9.5.

These are the implementation primitives + stats-methodology design that turn the methodology paper into a benchmark. Cheney owns the ergonomic-design layer (UX, contributor onboarding, leaderboard layout, plug-and-play flow); your role is to (a) own the stats methodology and (b) make Cheney's ergonomic-design decisions executable. Whichever you pick informs the §7 engineering plan directly and seeds the Phase 1+ workstreams in §9.5. The scope is intentionally larger than "review and propose" — Phase-0 should signal whether you can ship a contributor-extensible workstream end-to-end, since the §9.5 ownership map asks you to primary-own multiple such workstreams in Phase 1.

Time commitment for Phase-0: **~10-25 hours over 2-4 weeks** depending on scope picked (any single item is ~8-15h; pairing two — e.g., (D) + (B) — is ~20-25h on the upper end).

### 9.4 Open slot: infrastructure-ops collaborator

Benchmark implementation is split between Cheney (researcher-facing surface — generator library, CLI design, submission paths, leaderboard frontend) and Yuecheng (math/stats-heavy infrastructure — scorer library, Layer 3 cache extensions, validation runs); see §9.5 for the per-row split. The runtime *operations* side — reproducibility-cache hardening, leaderboard CI/CD, HuggingFace / model-card integration, eval-harness ops at scale — is a distinct workstream and remains an open slot. If we find someone whose ops contribution is substantive enough to be a coauthor (not a paid contractor), we want them on the team.

**Candidate under consideration** (not yet committed): **Jingyi Lu** — SDE at Jump Trading. Strong engineering background; possibly limited time. Proposed Phase-0 item if she joins: **lm-evaluation-harness adapter prototype** (~10-15 hours; ships AERead as an `lm_eval/tasks/aeread_*` task family with a single end-to-end smoke test). If Jingyi takes this, it shifts off Yuecheng's Phase-0 (B) menu and Yuecheng's §9.3 focuses on (A) scorer + (C) leaderboard prototype + (D) predict-then-validate. Sustained scope through Phase 1-3 if trial converts: maintain + extend the adapter (~2-5 hours/week); optionally promote signed-ScoreRecords / cache-verification from v0.5+ to v0 if bandwidth allows. Total allocation ~5-8% of v0 person-weeks. Adapter is an adoption hard-launch-gate (per §5 traction analysis), so contribution is comfortably co-author-level if she ships it.

Other candidate identification continues via lm-evaluation-harness contributor graph + HuggingFace Datasets maintainers + existing network search. Same Phase-0 / 4-week-checkpoint discipline applies; if a candidate emerges, they get a Phase-0 DoL item (likely: ship one specific eval-harness adapter or leaderboard-infrastructure piece). Authorship decided at the checkpoint.

Framing: potential coauthor specializing on the ops side, not a paid contractor.

### 9.5 Proposed post-exploration ownership map

A first-pass DoL for the v0 scope, mapping workstreams to proposed primary owner + supporting collaborators. This is a *proposal* for the checkpoint discussion, not a commitment — Phase-0 contribution patterns drive the actual ownership decisions.

**Scope discipline (post-audit)**: this ownership map reflects the **trimmed v0 scope** (~12-14 workstreams for the 3-4 person team over 16 weeks). Deferred items (5-axis full instrumentation of axes 4-5; robust utility family; multi-stage qualitative scoring; rotating benchmark seasons; Generalization Index composite; overfit-bot baseline; pairwise interaction effects; 3 of 4 RL training-signal mechanisms; AERead-env substrate; 2 of 5 functional classes; 3 of 5 counterfactual variants; compositional + far-OOD splits) are flagged as **v0.5+** in methodology.md and are NOT in this v0 ownership map. A separate "v0.5+ extension ownership map" can be drafted post-launch once v0 ships.

**Note on engineering ownership**: Cheney ships the v0 runtime scaffold during Phase-0 (per §7); the engineering primary roles below reflect the **ongoing post-conversion split**. Benchmark implementation is shared between Cheney and Yuecheng — Cheney leads the researcher-facing surface (generator library, CLI, submission path, documentation, leaderboard/diagnostic frontend); Yuecheng leads the math/stats-heavy infrastructure (scorer library, cache, validation runs, statistical reproducibility framework). The split tracks expertise rather than abstraction layer.

**Methodology paper workstreams**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| §1 Introduction | Cheney | Zihao (framing review) |
| §2 Related work | Cheney | Zihao (econ-lit anchors), Yuecheng (LLM-bench anchors) |
| §3 Methods — 5-axis taxonomy + OracleDecomposable formalization | Zihao | Cheney (writing pass) |
| §3 Methods — measurement-model pluralism formalization | Zihao | Yuecheng (scorer-library implementation notes) |
| §6 Methods — statistical reproducibility (cross-validation + held-out test design) | Yuecheng | Zihao (formal justification) |
| §7 Category C implementation (C2 ProductProcurementGame + D3 VendorSelectionGame v0; C1 persona-fit Layer 2 infrastructure in source repo) | Cheney | Zihao (utility-class identification) |
| §8 Experiments — cross-model eval runs + result tables | Yuecheng | Cheney (analysis), Zihao (interpretation) |
| §10 Discussion — mechanism design + agent-market thesis | Zihao | Cheney |

**Methodology workstreams (v0 only — 5 workstreams)**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| Layer 1 axiom protocol specs — **v0 subset: transitivity + dominance** (full 6-axiom family deferred to v0.5+) | Zihao | Yuecheng (scorer impl) |
| Layer 2 within-class identification framework — **v0 subset: 3 functional classes (KT prospect '79 + CRRA + Kelly-Markowitz)** | Zihao | Yuecheng (fit-procedure impl) |
| Layer 3 OracleDecomposable formalization | Zihao | Cheney (C2 + D3 instantiation) |
| Layer 3 predict-then-validate train/test split design + Q4 generalization-battery v0 scope (dev + hidden IID + 1 axis-OOD per game) | Yuecheng | Zihao (formal justification) |
| **5-axis taxonomy**: full instrumentation of Axis 1 (Δ_inf via OracleDecomposable) + Axis 2 (transitivity + dominance counterfactuals) + Axis 3 (Brier/CRPS scoring on within-class fit). **v0 sketched only**: Axis 4 (1 quantity-substitution probe), Axis 5 (1 confidence-elicitation probe). Full instrumentation of axes 4-5 defers to v0.5+. | Yuecheng (axes 3+4+5) + Zihao (axes 1+2) | Cheney |

**v0.5+ workstreams (NOT in v0 ownership)**: full 6-axiom family; CARA + cumulative prospect functional classes; axes 4-5 full instrumentation; rotating benchmark seasons; overfit-bot baseline; Generalization Index composite; pairwise interaction effects in cross-axis matrix; 3 of 4 RL training-signal mechanism implementations; compositional-OOD + far-OOD splits; multi-stage qualitative scoring; robust utility family.

**Engineering workstreams (v0 only — 7 workstreams)**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| lm-evaluation-harness integration + entry-point structure | Cheney (v0 scaffold) + **Jingyi Lu if she joins per §9.4** (adapter prototype + sustained maintenance); else Yuecheng | Yuecheng (scorer integration regardless of who owns the adapter) |
| **v0 scorer library (subset)** — Brier + 1 transitivity scorer + 1 multi-class utility-fit scorer (NOT the full Bradley-Terry / WST/MST/SST / KT-MLE / isotonic library — that's v0.5+) | Yuecheng | Zihao (correctness review), Cheney (v0 scaffold for simpler scorers) |
| Generator library + YAML schema (v0 scope: enough for C2 + D3 generation) | Cheney | Yuecheng (refinement) |
| Cache layer (responses / stimuli / scores / splits / fits / predictions) — **v0 subset** without signed-ScoreRecord enforcement (signed-ScoreRecord defers to v0.5+) | Cheney + Yuecheng | — |
| CLI (`aeread evaluate / diagnose / init`) — v0 subset; `aeread check` deferred to v0.5+ | Cheney | Yuecheng (extension) |
| **C2 ProductProcurementGame** end-to-end (qualitative-evidence procurement; Q3 single-stage 4-tier optimality scoring with single utility-weight vector per buyer; 2 counterfactual variants — paraphrase + preference-flip) | Cheney | Zihao (oracle formalization), Yuecheng (Q3 scoring impl) |
| **D3 VendorSelectionGame** end-to-end (risk/uncertainty; Bayes risk minimization; 2 counterfactual variants) | Cheney | Zihao (Bayes-risk oracle), Yuecheng (risk-calibration scorer) |
| Leaderboard frontend + diagnostic drill-down page (5-axis radar — v0 shows axes 1+2+3 fully, axes 4+5 as sketched) | Cheney | Yuecheng (review) |
| **Benchmark validation runs (v0 scope: 3-5 frontier models, not 8+)** | Cheney (run orchestration) + Yuecheng (result-table generation) | — |
| Documentation (README, contributor onboarding for v0 scope) | Cheney | Yuecheng (technical content) |
| **Web-form submission path only** (Colab + PR paths defer to v0.5+) | Cheney | — |

**Engineering deferred to v0.5+ (NOT in v0 ownership)**: full Bradley-Terry / WST/MST/SST / KT-MLE / isotonic scorer library; signed ScoreRecords; Colab + PR submission paths; composite-score aggregator (Generalization Index formula); HuggingFace + model-card adoption pipeline; reproducibility-hardening external-submission flow; cross-decomposition matrix on diagnostic page (v0 shows main effects only).

**Open ops slot**: still relevant if a candidate emerges (leaderboard / HuggingFace ops would be their workstream). If no candidate by Phase-0 checkpoint, the deferred items above stay deferred; Cheney does NOT inherit them in v0.

**External outreach + coordination**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| Isaiah Andrews (MIT) — §3 methodology review | Cheney drafts; Zihao reviews before send | — |
| Yannai Gonczarowski (Harvard) — parameter-layer comparison | Cheney drafts; Zihao reviews before send | — |
| Erica Zhang (Stanford) — TERMS-Bench coordination | Cheney (existing relationship) | — |
| Frontier-lab partner pre-commit | Cheney | — |
| Open Phil grant application + ongoing reporting | Cheney | — |

This map is the input to the 4-week checkpoint discussion — adjust based on what Phase-0 actually reveals about fit.

### 9.6 What gets decided at the 4-week checkpoint (2026-06-30)

After 4 weeks of trial collaboration, with each contributor's Phase-0 output in hand, we discuss:

- **Whether the collaboration is generating contributions all parties find valuable**
- **Authorship** (informed by actual Phase-0 work, not pre-committed)
- **Time-commitment budgets** for Phase 1 (paper draft, weeks 5-8)
- **Ownership map adjustments** to §9.5 based on Phase-0 fit signal

If 4 weeks doesn't generate sufficient signal (Phase-0 didn't land, scheduling was rough, etc.), we extend the trial by 2 more weeks rather than locking in authorship under uncertainty.

## 10. Timeline + sync cadence

**First sync**: **Monday 2026-06-02 at 4pm Pacific** (30 min, async-first: written agenda + responses 24h before, live discussion only for things that need it).

**Recurring**: weekly 30-min syncs through the 4-week checkpoint.

**4-week checkpoint**: **2026-06-30** — decision: continue collaboration with authorship discussion / extend Phase-0 trial / part ways.

**Async channel**: GitHub repo issues + Slack workspace. Slack invite at first sync.

**Phase-0 deliverables before the checkpoint**:
- Cheney: A4 stability dimension end-to-end (2026-06-09) + methodology paper §1+§2 draft (2026-06-23)
- Zihao: 1-2 Phase-0 tasks from §9.2 (target: 2026-06-23)
- Yuecheng: 1-2 Phase-0 tasks from §9.3 (target: 2026-06-23)

If the proposed sync slot doesn't work, propose alternates. Cadence matters more than the specific slot.

## 11. Explicit ask + 4-week checkpoint

**Ask**: enter a 4-week trial collaboration. Pick 1-2 Phase-0 items from §9.2 / §9.3 and deliver them before 2026-06-23.

**Decision at the checkpoint (2026-06-30)**:
- **Continue** → discuss authorship + Phase 1 commitment
- **Extend trial** → 2 more weeks of Phase-0 if signal is inconclusive
- **Part ways** → no acrimony; Cheney cites your work in the paper as planned anyway

**Why the trial-first framing**:
- Neither of us has signal yet on whether this collaboration generates good work for you
- Locking in authorship before any actual contributions is premature
- Phase-0 items are bounded (8-30 hours over 2-4 weeks per §9.2 / §9.3, depending on which item picked; lighter-end items are ~8-12h) so the trial cost is low relative to a 6-month paper commitment
- If the trial generates strong contributions, authorship is a natural follow-up conversation; if not, both sides save the expected-but-unrealized commitment

## 12. Risk acknowledgments + off-ramps

This proposal is not risk-free. Honest list:

| Risk | Likelihood | Mitigation / off-ramp |
|---|---|---|
| **Paper rejection from NeurIPS/COLM** | Medium | Defensible methodology contribution + 5-pillar framing makes top-venue acceptance plausible. If rejected, resubmit to TMLR / Springer Nature Communications. Worst case: arxiv-only + adoption via leaderboard. |
| **Frontier-lab partner falls through** | Medium-High | The launch gate. Without a model-card commitment, AERead lands in EconEvals's 1-cite-at-14-months territory. Backup: maximize PI-endorsement signal (Athey + Roth + Andrews + Gonczarowski + Leyton-Brown) to compensate. |
| **TERMS-Bench releases code with different methodology** | Low-Medium | We generalize their Eq. 4 via `OracleDecomposable` interface, which is independent of their specific implementation. We cite extensively + frame as extension. |
| **OracleDecomposable generalization contested by reviewers** | Medium | Frame conservatively: "we apply their Eq. 4 to non-bargaining domains via abstraction X; we do not claim to invent the decomposition; we name TERMS-Bench in the title." If still contested, drop the "generalization" claim and present as "AERead applies their Eq. 4 to C1 persona-fit." |
| **5-axis taxonomy contested by reviewers** ("too many axes") | Medium | Per-axis prior-art anchors (Zhang/Andrews/Mazeika/Yamin/EconEvals competency precedent) make the taxonomy defensible. If still contested, fallback ordering: drop Axis 5 (metacog), then Axis 4 (computational floor) — gracefully degrades from 5-axis to 4-axis to 3-axis while preserving the load-bearing integrative claim. |
| **Time commitment mismatch with your day jobs** | Medium | Phase-0 is intentionally bounded (8-30 hours over 2-4 weeks per §9.2 / §9.3 — picking a lower-end item like §9.2 (D) at ~8-12h is fine signal). If even that becomes unworkable, we part ways at the checkpoint with no acrimony. Time-commitment budgets for Phase 1+ are negotiated only at the 4-week checkpoint based on actual Phase-0 fit. |
| **Authorship order disputes** | Low | Deferred to 4-week checkpoint; informed by actual Phase-0 contributions, not pre-committed. Both sides have an off-ramp at the checkpoint if expectations diverge. |
| **Open ops-collaborator slot stays unfilled** | Medium | §9.5 lists 4 ops-side workstreams (leaderboard frontend, diagnostic page, HuggingFace integration, reproducibility hardening). If no ops collaborator emerges from the trial, Cheney inherits leaderboard + diagnostic page (the launch-critical ones; extends his timeline by ~1-2 weeks); HuggingFace integration defers to v1.5. The 2-3 week runtime build (§7) is doable solo at this scope; ops slot stays open as upside, not blocker. |
| **Open Philanthropy grant rejection** | Medium-Low | Bootstrap-fund v0 at lower-resolution (smaller model coverage, slower API spend). Still ships, just slower. |

## 13. Concrete next steps

1. **Read this proposal + the [methodology summary](methodology.md) + [reading list](reading_list.txt)**. Time: ~45 min for the proposal (skim §9.5 tables on first pass; the ownership map is checkpoint input, not Phase-0 commitment), optional 1-2 hours for the rest.
2. **First sync 2026-06-02 at 4pm Pacific** (30 min) — async agenda + responses 24h prior.
3. **Pick one or two Phase-0 items each** from §9.2 (Zihao) and §9.3 (Yuecheng); flag your picks at the first sync.
4. **Cheney**: ship A4 stability dimension end-to-end by 2026-06-09; draft methodology paper §1+§2 by 2026-06-23.
5. **Weekly 30-min sync** through the checkpoint.
6. **Phase-0 delivery target**: 2026-06-23.
7. **4-week checkpoint**: 2026-06-30 — decision on continuation + authorship discussion.

## 14. What this proposal is NOT asking for

- It is NOT asking either of you to commit to founding a company. We can write the paper as a research collaboration and revisit commercial structure independently.
- It is NOT asking for capital or introductions to investors. v0 is bootstrap-funded through Open Phil grant application + Cheney's personal time.
- It is NOT asking for equity / IP commitments. The OSS layer is MIT-licensed forever; commercial layers are deferred and independently funded.
- It is NOT asking for endorsement letters or "we vouch for AERead" public statements. Those come later, and only after v0 results justify them.
- It is NOT asking for pre-committed authorship before any Phase-0 contributions exist. That gets decided at the checkpoint based on what actually happens.

What it IS asking: enter a 4-week trial collaboration with one bounded Phase-0 item. Decision on continuation at **2026-06-30**.

## 15. Linked artifacts

### In this repo

- **[v0 sprint plan](v0_sprint.md)** — consolidated operational view: what v0 actually ships, ownership map for the ~13 workstreams, phase timeline, v0.5+ deferral roadmap. **Read this for the operational picture in one place** rather than hunting through inline v0/v0.5+ tags in framework docs.
- **[Methodology summary](methodology.md)** — 3-layer pipeline + 5-axis taxonomy + 9-Q&A with inline v0/v0.5+ scope tags
- **[Prior art brief](prior_art_brief.md)** — ~3-page primer on the anchor benchmarks AERead integrates (TERMS-Bench / Andrews 2026 / EconEvals)
- **[Layer 3 candidate pool](layer3_candidates.md)** — open list of ~25 real-world economic decision use cases on a value × testability matrix
- **[Post-v0-paper substrate roadmap](aeread_env_design.md)** — forward-looking design spec for an OpenSpiel-compatible substrate (separate follow-up paper, NOT v0.5)
- **[Citation links](papers/links.md)** — one-stop lookup mapping every cited paper to a public URL or repo-hosted PDF
- **[Reading list](reading_list.txt)** — T1 / T2 / T3 papers with [AXIS-N] anchor flags
- **[Bibliography](papers/references_master.yaml)** — 160-entry machine-readable references
- **[Curated paper index](papers/_INDEX.md)** — deep-dive synopses (~5-6 paragraphs each) for 12 supporting-literature papers

### Available on request (source-repo artifacts)

The master plan + runtime spec live in the internal source repo (`rationale`) — they're the implementation-side documents this proposal summarizes. Request access from Cheney if your Phase-0 item needs drill-down:

- **Master plan** (~3,000 lines) — full §1.5.* methodology development (including §1.5.2.1 predict-then-validate design), §2.5 dimension scoping, §6 implementation phases, §7 per-dimension notes, §14 diagnostic decomposition architecture, §17 commercial framing. Useful for Zihao's Phase-0 (B)/(C) protocol specs, Yuecheng's Phase-0 (A) scorer scoping + (D) predict-then-validate design.
- **Runtime spec** (~1,200 lines) — §2 architecture, §5 scorer menu, §10 leaderboard rendering, §14.7 cache layer extension (relevant for predict-then-validate split files). Useful for Yuecheng's Phase-0 (B) integration prototype + (D) reproducibility framework.
- **Diagnostic-page mock** (~500 lines) — UX wireframes for the 5-axis radar drill-down page that Cheney will design against. Useful for Yuecheng's Phase-0 (C) composite-score schema implementation + thin frontend prototype.

These will be folded into the sister repo (made public alongside the methodology paper preprint) once they stabilize.

---

**End of proposal v0.3.**
