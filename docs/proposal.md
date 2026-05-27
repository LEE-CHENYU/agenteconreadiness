# AgentEcon Readiness (AERead): a unified benchmark for LLM rational economic decision-making

**Proposal v0.3 — for Yuecheng Fang and Zihao Li**
Owner: Cheney Li | Date: 2026-05-26 | Read time: ~12 minutes (skim the §9.5 ownership tables on first read)

---

## Executive summary

**The direction**: measure LLM economic-decision performance on **real-world use cases** — procurement, vendor selection, persona-fit, bargaining, agentic tool selection — by **economic value** (dollar surplus, oracle-gap utility, revealed-preference rank correlation). The leaderboard is a deployment verdict: "is your agent ready for the economy?"

**The supporting framework**: provide **complete cross-layer diagnostic decomposition** through 3 layers (axioms × parameters × outcomes) and a 5-axis failure taxonomy. The decomposition is what turns a single-number leaderboard into actionable signal — telling you *why* a model fails and what to fine-tune. Without it, AERead is just another use-case benchmark; with it, it's a tool.

**The adoption strategy**: optimize the entire toolchain for **plug-and-play usability** by researchers who are NOT sophisticated engineers. Zero-code contribution via YAML; one-line evaluation via `pip install`; web form / Colab / PR submission paths; 5-minute clone-to-first-output SLO; integrate AS lm-evaluation-harness task family so frontier labs already have us installed.

Three Q1-2026 benchmark papers (Stanford TERMS-Bench, Harvard EconEvals, MIT Revealed Rationality) each address one layer; none integrate all three with cross-layer decomposition; none ship with the plug-and-play UX needed to compete with the field's adoption gatekeepers.

This proposal asks: enter a 4-week trial collaboration on a bounded Phase-0 item; we revisit authorship + commitment at the 2026-06-30 checkpoint based on what actually gets contributed.

---

## 1. The opening question

A 2025 Anthropic publication reports that **5.9% of Claude API conversations are economic decisions**. JPMorgan announced LLM-agent shareholder voting; Visa announced AI shopping agents. The deployments are happening; the rationality validation is not.

Three Q1-2026 papers from elite teams stake claims in three corners of this problem:
- **Stanford TERMS-Bench** (Zhang/Athey/Roth-advising, May 2026) — [arxiv 2605.13909](https://arxiv.org/abs/2605.13909): bilateral negotiation outcome layer
- **Harvard EconEvals** (Fish/Gonczarowski, Feb 2026) — [arxiv 2503.18825](https://arxiv.org/abs/2503.18825): procurement/scheduling/pricing parameter+outcome layer
- **MIT Revealed Rationality** (Andrews, Feb 2026) — [PDF in repo](papers/pdfs/andrews_2026_revealed_rationality.pdf): label-free representation-theorem penalties at the axiom layer

> **Citation links.** All paper references in this proposal map to public URLs or repo-hosted PDFs via [`papers/links.md`](papers/links.md). Inline links below are first-occurrence only.

None integrate the three layers. The integrated benchmark is the open opportunity — and the timing window is narrow (6-9 months before any of these teams ships a v2 extending into the other layers).

## 2. The 3-layer hierarchy (canonical revealed-preference pipeline)

| Layer | Cat | Question | Method | Closest prior art |
|---|---|---|---|---|
| 1 — existence | A (axioms) | Are preferences internally consistent? | Bayesian model selection on choice triplets; CCEI + money-pump + Houtman-Maks family | Davis-Stober (transitivity); Andrews 2026 (penalty math) |
| 2 — identification | B (parametric utility fits) | What are the implied parameters of a chosen utility framework? v0: KT prospect theory (λ, α) + exp-vs-hyperbolic discount (δ, k) + Fehr-Schmidt social (α, β). Framework extends to ambiguity-aversion, regret theory, rank-dependent utility as v1.5+ instantiations. | Mazeika 2025 (utility engineering); Ross-Kim-Lo 2024 (LLM Economicus) |
| 3 — predictive validity | C (outcome) | A **collection of real-world economic decision use cases**, each individually `OracleDecomposable`. v0: C1 persona-fit (IRL on 13F) + C2 price-aware product selection. v2: D2 bargaining (wrap TERMS-Bench), D3 agentic vendor selection. | TERMS-Bench (D2); EconEvals (D3 precedent); novel for C1 + C2 |

The three layers map to the canonical revealed-preference pipeline: **existence** (does a rationalizing utility exist?) → **identification** (which utility, within a functional class, is consistent with observed choices?) → **predictive validity** (does the identified utility predict held-out choices?). Layer 3 uses **predict-then-validate**: fit on a training portion of revealed preferences, predict held-out, score by predictive accuracy.

**The novel contribution is the Layer 3 collection-of-use-cases framing**, not any single use case. Each Cat C / Cat D use case is `OracleDecomposable` (hidden state + simulator + oracle + scalar utility), so the same Eq. 4 decomposition applies across all of them. This is what makes the methodology paper §3 contribution rigorous: we don't just apply TERMS-Bench's Eq. 4 to one new task; we apply it to a *family*, demonstrating portability beyond their single bargaining domain.

- **C1 Persona-fit (IRL on 13F)**: hidden state = principal utility coefficients; oracle = closed-form Kelly-Markowitz. Novel — no prior LLM benchmark grounds in dollar-equivalent decisions of named human principals at scale.
- **C2 Price-aware product selection**: hidden state = vendor true cost/quality; oracle = cheapest dominating choice. Novel + massive untested deployment surface.
- **D2 Bargaining (v2)**: native TERMS-Bench instantiation; wrap their runtime when code releases.
- **D3 Agentic vendor selection (v2)**: extends C2 to full marketplace with agentic tool-use; EconEvals provides protocol precedent.

> **The v0 list is intentionally short.** The full open candidate pool — EconEvals procurement/pricing/scheduling wraps, Calvano-style algorithmic-collusion detection, Gale-Shapley matching, multi-issue negotiation, Vending-Bench long-horizon coherence, Zhu-Griffiths weather/event forecasting, ~25 candidates total across 7 structural clusters — is enumerated in [`layer3_candidates.md`](layer3_candidates.md) on a value × testability matrix, with per-case pros/cons + Tier S/A/B/C/D priority. Adding cases later strengthens the §3 generalization claim (more domains → broader OracleDecomposable demonstration); the candidate doc is the input to that prioritization conversation.

## 3. Novel methodology contribution: 5-axis failure taxonomy + `OracleDecomposable` generalization

This is the methodologically defensible contribution that distinguishes AERead from STEER, EconEvals, Rationality Check!, TERMS-Bench, and every other Q1-2026 LLM-economics benchmark.

**The diagnostic question every benchmark fails to answer**: when a model scores low on a Cat C/D outcome task, *which mechanism failed?* Existing benchmarks decompose along at most one axis: TERMS-Bench by information condition (Δ_inf + Δ_unc + Δ_ctrl) within bargaining; Andrews 2026 by representation theorem; Mazeika 2025 by emergent utility; STEER/EconEvals/Rationality Check! report one number. **None integrate multiple axes.**

**What the diagnostic literature itself says about this gap.** Four 2023–2026 diagnostic papers each *explicitly* discuss whether their single-axis approach is sufficient — and each admits it is not. [Chadwick et al. 2025](papers/pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) (§Future Work): "(approximate) probabilistic coherence and transitivity of preferences are necessary conditions for rationality, they are arguably **not sufficient**…it has yet to be determined how useful our system is in real-world scenarios"; and they pose precisely AERead's stack-design question: *"does a two-step refinement (first ordinal, then cardinal) outperform a single probability-based approach?"* [Betz & Richardson 2023](https://doi.org/10.1371/journal.pone.0281372) (§Future Research) calls for "improved diagnostic tools" with "high-resolution representations of an agent's probabilistic belief system" relating inferential structure of training data to current behavior. [Zhu & Griffiths 2024](https://arxiv.org/abs/2401.16646) flags the truthful-reporting assumption underlying any single-axis probability probe. Andrews 2026 §7 separates calibration from coherence as complementary properties.

Reading these papers in sequence is reading a request for AERead. The 5-axis taxonomy + cross-decomposition matrix is the integration they each pointed to; the 3-layer pipeline (existence → identification → predictive validity) is the empirical answer to Chadwick's ordinal-then-cardinal question; the collection-of-use-cases Layer 3 design is the cross-domain generalization their single-domain studies could not deliver.

**Our proposal: a 5-axis failure taxonomy**, each axis prior-art-anchored:

| # | Axis | Causal hypothesis | Prior-art anchor |
|---|---|---|---|
| 1 | **Information** | Agent lacks knowledge of hidden state | TERMS-Bench (Zhang et al. 2026) — generalized via `OracleDecomposable` |
| 2 | **Consistency** | Agent's preference / belief structure violates axioms | Andrews 2026 (representation theorem penalties) |
| 3 | **Calibration** | Agent's economic parameters are misfit | [Mazeika 2025](https://arxiv.org/abs/2502.08640) (utility engineering); [Guo 2017](https://arxiv.org/abs/1706.04599) (ECE diagnostic); Gneiting-Raftery 2007 (proper scoring rules — [PDF](papers/pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf)) |
| 4 | **Computational floor** | Agent can't execute the math the choice requires | Novel for v0; partial precedent in code-eval lit |
| 5 | **Meta-cognitive calibration** | Agent's confidence is uncalibrated (stated ≠ realized accuracy) | Yamin et al. 2026 ([arxiv 2602.06286](https://arxiv.org/abs/2602.06286)) (belief coherence) |

Each axis has a distinct intervention mechanism and decomposes the per-(model, task) gap independently. Cross-decomposition (information × consistency, etc.) produces the full attribution matrix.

**Generalizing TERMS-Bench Eq. 4 (the load-bearing claim for Axis 1)**: Zhang et al. 2026 introduced the oracle-gap intervention decomposition U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl, but presented it as bargaining-specific. We abstract the construction into an **`OracleDecomposable` interface** — any task with (hidden state, controllable simulator, oracle policy, belief substitution, state reveal, scalar utility) admits the same decomposition. The **generalization is the multi-use-case application**:

- **Cat C v1 — C1 persona-fit**: hidden state = principal's IRL-fit utility coefficients (α_kelly, δ_turnover); oracle = closed-form Kelly-Markowitz. Eq. 4 applied to a non-bargaining domain.
- **Cat C v1 — C2 price-aware product selection**: hidden state = vendor true cost; oracle = cheapest dominating choice. Eq. 4 applied to a procurement-style domain.
- **Cat D v2 — D2 bargaining**: native TERMS-Bench instantiation; wrap their runtime when code releases (their `github.com/zou-group/terms-bench` repo is 404 as of 2026-05-26; expect release within 1-3 months). Eq. 4 in its native form.
- **Cat D v2 — D3 agentic vendor selection**: extends C2 to full marketplace simulator with realistic agentic tool-use; EconEvals provides protocol precedent.

Demonstrating the same Eq. 4 mechanics across **4 use cases (persona-fit, product selection, bargaining, agentic vendor selection)** is what makes this a generalization — not just an application to one new task.

The methodology paper's §3 contribution is precisely:

> *"Existing benchmarks decompose failures along at most one axis. We propose a 5-axis failure taxonomy — information (extending Zhang et al. 2026 via `OracleDecomposable`), consistency (extending Andrews 2026), calibration (extending Mazeika 2025), computational floor (novel), and meta-cognitive (extending Yamin et al. 2026). Cross-decomposition along multiple axes produces high-resolution attribution. We demonstrate residual unexplained variance < 15% **across a collection of Layer 3 use cases** (C1 persona-fit + C2 price-aware product selection; with v2 extension to bargaining + agentic vendor selection) — methodologically complete attribution at a precision no prior benchmark achieves, *and* demonstrating the OracleDecomposable Eq. 4 generalization across non-bargaining domains."*

This respects all prior art (we're extending, not claiming to invent) while staking the integrative claim.

**Diagnostic surface**: every per-(model, task) result has a drill-down page rendering a **5-axis radar chart** with one spoke per axis + headline ("model X's primary failure mode is Axis 3 calibration via B1 risk-preference miscalibration during persona inference") + cross-decomposition matrix for advanced users.

## 4. Five methodological commitments (each citation-anchored)

1. **Descriptive measurement, not normative ranking.** Higher composite scores ≠ better-aligned. Each dimension reports a fingerprint; downstream users decide which dimensions matter. *Anchored: Andrews 2026 §7 — "coherence is not sufficient for good behavior."*

2. **Measurement-model pluralism.** Each axiom-style sub-test fits 4-6 competing measurement models on the same data; reports Bayesian posterior. *Anchored: Echenique 2021 on CCEI; Davis-Stober mixture-of-orderings finding.*

3. **Judge-free by construction.** No LLM evaluates another LLM's output. Three concurrent Q1-2026 benchmarks (TERMS-Bench, EconEvals, Revealed Rationality) independently rejected LLM-as-judge; AERead is the integrated artifact exploiting this property across all three layers. *Anchored: TERMS-Bench environment-as-verifier; EconEvals "directly grounded in theoretical model"; QEDBench documented LLM-judge alignment gap.*

4. **Context-conditional axiomatization** is a measurable dimension, not an assumption. Personas, system prompts, and domain framing already degrade axiom compliance. *Anchored: Wen 2025 — biotechnology-expert and economist personas substantially reduce GARP compliance vs baseline.*

5. **Cross-layer attribution + oracle-gap decomposition.** The diagnostic depth that turns scores into actionable signals. The five commitments above combine into the defensible position vs. STEER/EconEvals/Rationality-Check (none of which formalize these), TERMS-Bench (which has commitment 5 at one layer only), and Andrews (who has commitment 5 at one axiom only).

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

- Three Q1-2026 papers establish the field is forming
- TERMS-Bench code is not yet released (their repo is 404); first-mover on the integrated benchmark is open for the next 3-6 months
- LLM frontier labs are deploying agents in economic tasks faster than evaluation infrastructure can characterize them
- Open Philanthropy is funding AI evaluation infrastructure in 2026
- The traction analysis exemplar (Utility Engineering, 15-month adoption arc) suggests a 6-9 month window from preprint to model-card adoption for benchmarks that ship with the right architecture

Without consolidated infrastructure landing in this window, the field fragments permanently around three competing benchmarks.

## 7. Engineering plan — AI-accelerated MVP

### v0 runtime (2-3 weeks of focused build)

With Claude Code drafting from the runtime spec, the v0 runtime build cycle is **2-3 weeks of focused execution**, mostly Cheney-time + API spend:

- **Adapter framework** (lm-evaluation-harness integration) for Cat A + Cat B + Cat C v1
- **Scorer + generator library** (~9 scorers, ~11 generators) — researchers configure via pure YAML
- **Cache layer never invalidates** — reproducibility hard guarantee
- **5-axis diagnostic decomposition** module (`aeread/diagnostic/`) covering all axes:
  - Axis 1 (information): `OracleDecomposable` interface — TERMS-Bench Eq. 4 generalized
  - Axis 2 (consistency): counterfactual axiom interventions
  - Axis 3 (calibration): parameter-fit attribution
  - Axis 4 (computational floor): quantity substitution
  - Axis 5 (meta-cognitive): confidence elicitation + calibration metrics
- **Live leaderboard** at agenteconreadiness.org accepting external PRs, with diagnostic drill-down pages (5-axis radar + cross-decomposition matrix)
- **Three submission paths** (web form / Colab / PR) — plug-and-play onboarding

Total bootstrap cost: under $10K in API spend + author time.

### Methodology-paper timeline (where the human-collaboration weeks actually live)

The methodology paper, not the runtime, is the timeline's critical path. The intellectual contribution (5-axis taxonomy formalization, OracleDecomposable identification conditions, predict-then-validate validation across 4-5 use cases) is where collaborator hours matter most:

| Phase | Calendar | Activity |
|---|---|---|
| Phase 0 — trial collaboration | Weeks 1-4 | Each contributor takes 1-2 Phase-0 DoL items from §9; Cheney drafts §1+§2 in parallel; output drives the §9.6 checkpoint discussion |
| Phase 1 — paper draft | Weeks 5-8 | Methodology paper §3 (5-axis + OracleDecomposable) drafted (continuing from Zihao's Phase-0 work); §1+§2 polished from Cheney's Phase-0 drafts; §10 + §6 first drafts; arxiv preprint target |
| Phase 2 — preprint + reviews | Weeks 9-12 | External methodology reviews (Andrews, Gonczarowski); leaderboard launch with 8+ models; frontier-lab pre-commit conversations |
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

Methodology + IRL infrastructure + Category C implementation. Has working 13F-extraction pipeline (~309 named investor network mapped); has Phase-0 baseline transitivity test results on Claude / GPT / DeepSeek.

**Phase-0 commitment** (independent of any collaborator decision):
- Ship A4 stability dimension end-to-end by 2026-06-09
- Draft methodology paper §1 + §2 by 2026-06-23 for collaborator review

### 9.2 Yuecheng Fang — proposed Phase-0 DoL (benchmark implementation track)

Yuecheng's prior benchmark-building experience is the natural fit for the implementation side — the runtime infrastructure, scorer library, leaderboard ops that turn the methodology into a tool researchers can actually use. Phase-0 options (pick 1-2 for ~10-20 hours total):

- **(A) Standard scorer library scoping memo + first scorer implemented.** Review the runtime spec §5 scorer / generator menu (request access from Cheney per §15 below); propose which 3-5 scorers ship in v0 and which defer to v1.5; **then implement one of the v0 scorers end-to-end** (e.g., Bradley-Terry transitivity scorer with measurement-model-pluralism plumbing). The scoring layer is the load-bearing primitive for Layer 1 + Layer 2 outputs — picking the right v0 set determines what dimensions can actually be measured at launch. ~8-12 hours.

- **(B) lm-evaluation-harness integration prototype.** Sketch the entry-point structure that makes AERead install as an `lm_eval/tasks/aeread_*` task family — a single end-to-end smoke test on a toy task (e.g., a 5-option transitivity probe on Haiku) showing the integration works. Include cache layer for response replay (per §14.7). This is the §5 plug-and-play adoption gate. ~10-15 hours.

- **(C) Leaderboard schema + composite-score design + thin frontend prototype.** Propose how per-task scores aggregate into the AERead composite (per the runtime spec §10 leaderboard rendering): what's the right user-facing single number, what's reported alongside in the diagnostic page, how does the 5-axis radar map to a sortable column? **Ship a static-HTML leaderboard prototype** with 1-2 mock results showing the design works. ~8-12 hours.

These are the implementation primitives that turn the methodology paper into a benchmark. Whichever you pick informs the §7 engineering plan directly and seeds the Phase 1+ workstreams in §9.5. The scope is intentionally larger than "review and propose" — Phase-0 should signal whether you can ship a contributor-extensible workstream end-to-end, since the §9.5 ownership map asks you to primary-own multiple such workstreams in Phase 1.

Time commitment for Phase-0: **~10-20 hours over 2-4 weeks** depending on scope picked.

### 9.3 Zihao Li — proposed Phase-0 DoL (econ + formal-math foundation track)

Zihao's economics + formal-mathematics background is the natural fit for the **load-bearing methodology work**: the Layer 1 axiom protocols, the Layer 2 identification framework, and the OracleDecomposable formalization that generalizes TERMS-Bench Eq. 4. This is the §3 methodology-paper core — without it, the benchmark has no rigorous claim.

Phase-0 options (pick 1-2 for ~8-30 hours total, depending on which):

- **(A) OracleDecomposable formalization.** Formalize the OracleDecomposable interface mathematically — what are the precise conditions (hidden state, controllable simulator, oracle policy, belief substitution, state reveal, scalar utility) that admit the Δ_inf + Δ_unc + Δ_ctrl decomposition? Identify which of the v0 use cases (C1 persona-fit, C2 price-aware product selection) satisfy each condition, where the abstraction breaks down, and what the v2 extensions (D2 bargaining, D3 agentic vendor selection) need. Anchor on Zhang et al. 2026 TERMS-Bench §4 (their Eq. 4 derivation); the methodology paper §3 takes this verbatim. **~10-15 hours.** This is the highest-leverage single item in the trial.

- **(B) Layer 1 axiom protocol specs.** Draft the formal specifications for the Layer 1 axiom-test family: CCEI, GARP, WARP, transitivity, monotonicity, Houtman-Maks. For each: test definition + what passing means + the Bayesian-model-selection posterior structure under measurement-model pluralism (4-6 competing measurement models fit on the same data; reported posterior over them). Pair with [Andrews 2026](papers/pdfs/andrews_2026_revealed_rationality.pdf) representation-theorem penalties as the Axis 2 (consistency) mathematical anchor. **~10-15 hours.**

- **(C) Layer 2 identification framework.** Formalize the within-class identification claim: given a functional class (KT '79 prospect theory, CRRA, CARA, cumulative prospect theory TK '92, Kelly-Markowitz), what does identification mean operationally? When does the framework recover unique parameters vs admit non-uniqueness (Andrews 2026's critique that representation theorems guarantee existence, not identification)? Draft the §3 methodology-paper subsection that handles this. **~10-15 hours.**

- **(D) Layer 3 candidate curation — mechanism-design lens.** Read [`layer3_candidates.md`](layer3_candidates.md) (open pool of ~25 cases on a value × testability matrix); from your mechanism-design background, do either or both:
  1. **Propose 2-3 additional candidates** not yet in the pool (examples we suspect are missing: spectrum auctions, prediction markets, generalized second-price / AdWords mechanism, market-maker bid-ask spread, revenue-equivalence stress tests). For each: source paper(s), OracleDecomposable mapping sketch, matrix-position justification.
  2. **Formalize the oracle policy for 1-2 existing high-value cases** that currently sit in medium testability (A2 EconEvals pricing or B1 Calvano collusion are the highest-leverage targets) — move them into the high-testability column by deriving the closed-form oracle their mechanism-design lit supports.
  
  Either path closes the same matrix gap: "high economic value × high testability" is the quadrant where AERead's commercial leaderboard story sits, and it's currently sparse because the oracle-derivation work hasn't been done. **~8-12 hours** for either path; ~15-20h if you do both. This is the highest-leverage Phase-0 item for the candidate-pool curation workstream in §9.5.

You're effectively the §3 co-lead of the methodology paper if this trial converts. One item alone is sufficient signal for the trial; picking more is welcome but not expected.

Time commitment for Phase-0: **~8-30 hours over 2-4 weeks** depending on scope picked (option D alone is ~8-12h; pairing (A)+(B) or (A)+(C) is ~25-30h on the upper end).

### 9.4 Open slot: infrastructure-ops collaborator

Yuecheng covers the benchmark *implementation* side (§9.2) — scorer library, lm-eval-harness integration, leaderboard schema, contributor-facing infrastructure. The runtime *operations* side — reproducibility-cache hardening, leaderboard CI/CD, HuggingFace / model-card integration, eval-harness ops at scale — is a distinct workstream and remains an open slot. If we find someone whose ops contribution is substantive enough to be a coauthor (not a paid contractor), we want them on the team.

Candidate identification continues via lm-evaluation-harness contributor graph + HuggingFace Datasets maintainers + existing network search. Same Phase-0 / 4-week-checkpoint discipline applies; if a candidate emerges, they get a Phase-0 DoL item (likely: ship one specific eval-harness adapter or leaderboard-infrastructure piece). Authorship decided at the checkpoint.

Framing: potential coauthor specializing on the ops side, not a paid contractor.

### 9.5 Proposed post-exploration ownership map

A first-pass DoL for the full v0 scope, mapping workstreams to proposed primary owner + supporting collaborators. This is a *proposal* for the checkpoint discussion, not a commitment — Phase-0 contribution patterns drive the actual ownership decisions.

**Methodology paper workstreams**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| §1 Introduction | Cheney | Zihao (framing review) |
| §2 Related work | Cheney | Zihao (econ-lit anchors), Yuecheng (LLM-bench anchors) |
| §3 Methods — 5-axis taxonomy + OracleDecomposable formalization | Zihao | Cheney (writing pass) |
| §3 Methods — measurement-model pluralism formalization | Zihao | Yuecheng (scorer-library implementation notes) |
| §6 Methods — statistical reproducibility (cross-validation + held-out test design) | Yuecheng | Zihao (formal justification) |
| §7 Category C implementation (C1 persona-fit, C2 product selection) | Cheney | Zihao (utility-class identification) |
| §8 Experiments — cross-model eval runs + result tables | Yuecheng | Cheney (analysis), Zihao (interpretation) |
| §10 Discussion — mechanism design + agent-market thesis | Zihao | Cheney |

**Methodology workstreams (Layer × Axis)**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| Layer 1 axiom protocol specs (CCEI / GARP / WARP / transitivity / monotonicity / Houtman-Maks) | Zihao | Yuecheng (scorer impl) |
| Layer 2 within-class identification framework | Zihao | Yuecheng (fit-procedure impl) |
| Layer 3 OracleDecomposable formalization | Zihao | Cheney (C1 instantiation) |
| Layer 3 candidate-pool curation (mechanism-design lens) | Zihao | Cheney (deployment-relevance scoring) |
| Layer 3 predict-then-validate train/test split design | Cheney | Yuecheng (cache extension) |
| Axis 1 Information — OracleDecomposable Δ_inf / Δ_unc / Δ_ctrl mechanics | Zihao | Cheney |
| Axis 2 Consistency — counterfactual axiom interventions | Zihao | Yuecheng |
| Axis 3 Calibration — Mazeika utility-fit + Brier/CRPS scoring | Yuecheng | Zihao (proper-scoring-rule theory) |
| Axis 4 Computational floor — quantity-substitution probes | Yuecheng | Cheney |
| Axis 5 Meta-cognitive — Brier on held-out + Dutch-book / probabilistic-identity probes | Yuecheng | Zihao (Gneiting-Raftery foundations) |

**Engineering workstreams**:

| Workstream | Proposed primary | Supporting |
|---|---|---|
| lm-evaluation-harness integration + entry-point structure | Yuecheng | — |
| Standard scorer library (Bradley-Terry, WST/MST/SST, KT-MLE, isotonic, etc.) | Yuecheng | Zihao (mathematical correctness review) |
| Generator library + YAML schema | Yuecheng | — |
| Cache layer (responses / stimuli / scores / splits / fits / predictions / diagnostics) | Yuecheng | Cheney (Cat C-specific extensions) |
| CLI (`aeread evaluate / diagnose / check / init`) | Yuecheng | — |
| Composite-score aggregator | Yuecheng | Zihao (rubric design) |
| **Category A test design (A1 / A2 / A3 / A5)** — A4 covered by Cheney's Phase-0 | Cheney | Zihao (axiom-spec review), Yuecheng (scorer wiring) |
| **Category B test design (B1 risk / B2 inter-temporal / B3 social)** — protocol picking + prompt engineering | Cheney | Zihao (utility-class anchors), Yuecheng (scorer wiring) |
| C1 13F-IRL pipeline (persona-fit, existing infrastructure) | Cheney | — |
| C2 price-aware product selection task design | Cheney | Zihao (oracle policy formalization) |
| Three submission paths (web form / Colab / PR) | Yuecheng | — |
| **Documentation** (README, new-task-guide, Colab template, contributor onboarding) | Yuecheng | Cheney (intro framing) |
| **Benchmark validation runs** (execute AERead on 8+ models pre-launch, generate v1 leaderboard) | Yuecheng | Cheney (API spend + analysis) |
| Leaderboard frontend + reliability-diagram visualization | Open (ops slot) — Cheney inherits if no candidate | Yuecheng (design review) |
| Diagnostic drill-down page (5-axis radar + cross-decomposition matrix) | Open (ops slot) — Cheney inherits if no candidate | Cheney (UX review) |
| HuggingFace integration + model-card adoption pipeline | Open (ops slot) — defers to v1.5 if no candidate | — |
| Reproducibility hardening (signed ScoreRecords, external-submission flow) | Open (ops slot) — Cheney inherits if no candidate | Yuecheng (schema design) |

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
- Yuecheng: 1-2 Phase-0 tasks from §9.2 (target: 2026-06-23)
- Zihao: 1-2 Phase-0 tasks from §9.3 (target: 2026-06-23)

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
- Phase-0 items are bounded (8-30 hours over 2-4 weeks per §9.2 / §9.3, depending on which item picked) so the trial cost is low relative to a 6-month paper commitment
- If the trial generates strong contributions, authorship is a natural follow-up conversation; if not, both sides save the expected-but-unrealized commitment

## 12. Risk acknowledgments + off-ramps

This proposal is not risk-free. Honest list:

| Risk | Likelihood | Mitigation / off-ramp |
|---|---|---|
| **Paper rejection from NeurIPS/COLM** | Medium | Defensible methodology contribution + 5-pillar framing makes top-venue acceptance plausible. If rejected, resubmit to TMLR / Springer Nature Communications. Worst case: arxiv-only + adoption via leaderboard. |
| **Frontier-lab partner falls through** | Medium-High | The launch gate. Without a model-card commitment, AERead lands in EconEvals's 1-cite-at-14-months territory. Backup: maximize PI-endorsement signal (Athey + Roth + Andrews + Gonczarowski + Leyton-Brown) to compensate. |
| **TERMS-Bench releases code with different methodology** | Low-Medium | We generalize their Eq. 4 via `OracleDecomposable` interface, which is independent of their specific implementation. We cite extensively + frame as extension. |
| **OracleDecomposable generalization contested by reviewers** | Medium | Frame conservatively: "we apply their Eq. 4 to non-bargaining domains via abstraction X; we do not claim to invent the decomposition; we name TERMS-Bench in the title." If still contested, drop the "generalization" claim and present as "AERead applies their Eq. 4 to C1 persona-fit." |
| **5-axis taxonomy contested by reviewers** ("too many axes") | Medium | Per-axis prior-art anchors (Zhang/Andrews/Mazeika/Yamin/novel) make the taxonomy defensible. If still contested, fallback ordering: drop Axis 5 (metacog), then Axis 4 (computational floor) — gracefully degrades from 5-axis to 4-axis to 3-axis. Each fallback still beats every existing competitor. |
| **Time commitment mismatch with your day jobs** | Medium | Phase-0 is intentionally bounded (8-30 hours over 2-4 weeks per §9.2 / §9.3 — picking a lower-end item like §9.3 (D) at ~8-12h is fine signal). If even that becomes unworkable, we part ways at the checkpoint with no acrimony. Time-commitment budgets for Phase 1+ are negotiated only at the 4-week checkpoint based on actual Phase-0 fit. |
| **Authorship order disputes** | Low | Deferred to 4-week checkpoint; informed by actual Phase-0 contributions, not pre-committed. Both sides have an off-ramp at the checkpoint if expectations diverge. |
| **Open ops-collaborator slot stays unfilled** | Medium | §9.5 lists 4 ops-side workstreams (leaderboard frontend, diagnostic page, HuggingFace integration, reproducibility hardening). If no ops collaborator emerges from the trial, Cheney inherits leaderboard + diagnostic page (the launch-critical ones; extends his timeline by ~1-2 weeks); HuggingFace integration defers to v1.5. The 2-3 week runtime build (§7) is doable solo at this scope; ops slot stays open as upside, not blocker. |
| **Open Philanthropy grant rejection** | Medium-Low | Bootstrap-fund v0 at lower-resolution (smaller model coverage, slower API spend). Still ships, just slower. |

## 13. Concrete next steps

1. **Read this proposal + the [methodology summary](methodology.md) + [reading list](reading_list.txt)**. Time: ~45 min for the proposal (skim §9.5 tables on first pass; the ownership map is checkpoint input, not Phase-0 commitment), optional 1-2 hours for the rest.
2. **First sync 2026-06-02 at 4pm Pacific** (30 min) — async agenda + responses 24h prior.
3. **Pick one or two Phase-0 items each** from §9.2 (Yuecheng) and §9.3 (Zihao); flag your picks at the first sync.
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

- **[Methodology summary](methodology.md)** — 3-layer pipeline + 5-axis taxonomy condensed
- **[Layer 3 candidate pool](layer3_candidates.md)** — open list of ~25 real-world economic decision use cases on a value × testability matrix; per-case pros/cons + Tier S/A/B/C/D priority for v0.5 / v1 / v1.5 / v2 expansion
- **[Citation links](papers/links.md)** — one-stop lookup mapping every cited paper to a public URL or repo-hosted PDF
- **[Reading list](reading_list.txt)** — T1 / T2 / T3 papers with [AXIS-N] anchor flags
- **[Bibliography](papers/references_master.yaml)** — 160-entry machine-readable references
- **[Curated paper index](papers/_INDEX.md)** — annotated reading guide

### Available on request (source-repo artifacts)

The master plan + runtime spec live in the internal source repo (`rationale`) — they're the implementation-side documents this proposal summarizes. Request access from Cheney if your Phase-0 item needs drill-down:

- **Master plan** (~3,000 lines) — full §1.5.* methodology development, §2.5 dimension scoping, §6 implementation phases, §7 per-dimension notes, §14 diagnostic decomposition architecture, §17 commercial framing. Useful for Yuecheng's Phase-0 (A) scorer scoping and Zihao's Phase-0 (B)/(C) protocol specs.
- **Runtime spec** (~1,200 lines) — §2 architecture, §5 scorer menu, §10 leaderboard rendering, §14.7 cache layer extension. Useful for Yuecheng's Phase-0 (B) integration prototype.
- **Diagnostic-page mock** (~500 lines) — UX wireframes for the 5-axis radar drill-down page. Useful for Yuecheng's Phase-0 (C) leaderboard schema design.

These will be folded into the sister repo (made public alongside the methodology paper preprint) once they stabilize.

---

**End of proposal v0.3.**
