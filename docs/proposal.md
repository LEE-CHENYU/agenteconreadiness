# AgentEcon Readiness (AERead): a unified benchmark for LLM rational economic decision-making

**Proposal v0.3 — for Yuecheng Fang and Zihao Li**
Owner: Cheney Li | Date: 2026-05-26 | Read time: 7 minutes

---

## Executive summary

**The direction**: measure LLM economic-decision performance on **real-world use cases** — procurement, vendor selection, persona-fit, bargaining, agentic tool selection — by **economic value** (dollar surplus, oracle-gap utility, revealed-preference rank correlation). The leaderboard is a deployment verdict: "is your agent ready for the economy?"

**The supporting framework**: provide **complete cross-layer diagnostic decomposition** through 3 layers (axioms × parameters × outcomes) and a 5-axis failure taxonomy. The decomposition is what turns a single-number leaderboard into actionable signal — telling you *why* a model fails and what to fine-tune. Without it, AERead is just another use-case benchmark; with it, it's a tool.

**The adoption strategy**: optimize the entire toolchain for **plug-and-play usability** by researchers who are NOT sophisticated engineers. Zero-code contribution via YAML; one-line evaluation via `pip install`; web form / Colab / PR submission paths; 5-minute clone-to-first-output SLO; integrate AS lm-evaluation-harness task family so frontier labs already have us installed.

Three Q1-2026 benchmark papers (Stanford TERMS-Bench, Harvard EconEvals, MIT Revealed Rationality) each address one layer; none integrate all three with cross-layer decomposition; none ship with the plug-and-play UX needed to compete with the field's adoption gatekeepers.

This proposal asks: do you want to co-author the v0 methodology paper, with a decision by 2026-06-15.

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

5. **Cross-layer attribution + oracle-gap decomposition.** The diagnostic depth that turns scores into actionable signals. The four methodology pillars combine into the defensible position vs. STEER/EconEvals/Rationality-Check (none of which formalize these), TERMS-Bench (which has pillar 5 at one layer), and Andrews (who has pillar 5 at one axiom).

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
| Phase 0 — trial collaboration | Weeks 1-4 | Each contributor takes one Phase-0 DoL item from §9; output drives the §9 collaboration-fit discussion |
| Phase 1 — paper draft | Weeks 5-8 | Methodology paper §3 (5-axis + OracleDecomposable) drafted; §1, §2, §10 first drafts; arxiv preprint target |
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

### 9.2 Yuecheng Fang — proposed Phase-0 DoL

If you want to evaluate fit, pick one of these as your Phase-0 contribution:

- **(A) Measurement-model framework review.** Read the §1.5.6 measurement-model-pluralism framework (link in master plan); flag the 3 highest-leverage statistical-rigor improvements. ~3-4 hours.
- **(B) OracleDecomposable identification conditions.** Write a 1-2 page sketch of the identification conditions for OracleDecomposable across the two v0 Cat C use cases (C1 persona-fit, C2 price-aware product selection). ~5-8 hours.
- **(C) Sky Computing Lab feasibility.** Explore with your senior advisor whether the cc'd-email introduction pattern is viable for AERead launch; report back on what would unlock it. ~1-2 conversations.

Why these: the §1.5.6 + OracleDecomposable workstreams are the natural Berkeley applied-math / statistics fit; (C) is the highest-leverage non-paper contribution if the advisor channel opens.

Time commitment for Phase-0: **~4-8 hours over 2-4 weeks.** No deeper commitment until the 4-week checkpoint.

### 9.3 Zihao Li — proposed Phase-0 DoL

If you want to evaluate fit, pick one of these:

- **(A) §10 discussion framing review.** Read the methodology paper §10 (discussion + future work) outline; flag mechanism-design framings that should be sharpened or are missing. ~3-4 hours.
- **(B) v2 D-dimension priority memo.** Draft a 1-page memo on which v2 D-dimension expansion is highest-leverage from a game-theory perspective: D1 context-conditional axiomatization vs D2 bargaining vs D3 agentic vendor selection. ~5-8 hours.
- **(C) Columbia game-theory advisor channel.** Discuss with your advisor whether AERead is the right artifact to anchor a future agent-mechanism-design paper. ~1 conversation.

Why these: §10 + v2 framing are the natural Columbia mechanism-design fit; (C) tests whether senior-advisor support exists before we commit to that channel.

Time commitment for Phase-0: **~4-8 hours over 2-4 weeks.** No deeper commitment until the 4-week checkpoint.

### 9.4 Open slot: engineering-side collaborator

The 2-3 week AI-accelerated runtime (§7) reduces the need for a long-term contract engineer, but the **engineering side of the methodology paper** (reproducibility infrastructure, leaderboard polish, evaluation-harness integration) is still a real workstream. If we find someone whose technical contribution is substantive enough to be a coauthor — not a paid contractor — we want them on the team.

Candidate identification continues via lm-evaluation-harness contributor graph + HuggingFace Datasets maintainers + the existing network search. Same Phase-0 / 4-week-checkpoint discipline applies: if a candidate emerges, they get a Phase-0 DoL item (likely: ship a specific evaluator-harness adapter or leaderboard-infrastructure piece) and authorship is decided at the checkpoint based on what they actually contribute.

Framing: potential coauthor specializing on the infrastructure side, not a paid contractor.

### 9.5 What gets decided at the 4-week checkpoint (2026-06-30)

After 4 weeks of trial collaboration, with each contributor's Phase-0 output in hand, we discuss:

- **Whether the collaboration is generating contributions all parties find valuable**
- **Authorship** (informed by actual Phase-0 work, not pre-committed)
- **Time-commitment budgets** for Phase 1 (paper draft, weeks 5-8)
- **Role specialization** within the methodology paper

If 4 weeks doesn't generate sufficient signal (Phase-0 didn't land, scheduling was rough, etc.), we extend the trial by 2 more weeks rather than locking in authorship under uncertainty.

## 10. Timeline + sync cadence

**First sync**: **Monday 2026-06-02 at 4pm Pacific** (30 min, async-first: written agenda + responses 24h before, live discussion only for things that need it).

**Recurring**: weekly 30-min syncs through the 4-week checkpoint.

**4-week checkpoint**: **2026-06-30** — decision: continue collaboration with authorship discussion / extend Phase-0 trial / part ways.

**Async channel**: GitHub repo issues + Slack workspace. Slack invite at first sync.

**Phase-0 deliverables before the checkpoint**:
- Cheney: A4 stability dimension end-to-end (2026-06-09) + methodology paper §1+§2 draft (2026-06-23)
- Yuecheng: one Phase-0 task from §9.2 (target: 2026-06-23)
- Zihao: one Phase-0 task from §9.3 (target: 2026-06-23)

If the proposed sync slot doesn't work, propose alternates. Cadence matters more than the specific slot.

## 11. Explicit ask + 4-week checkpoint

**Ask**: enter a 4-week trial collaboration. Pick one Phase-0 item from §9.2 / §9.3 and deliver it before 2026-06-23.

**Decision at the checkpoint (2026-06-30)**:
- **Continue** → discuss authorship + Phase 1 commitment
- **Extend trial** → 2 more weeks of Phase-0 if signal is inconclusive
- **Part ways** → no acrimony; Cheney cites your work in the paper as planned anyway

**Why this framing instead of "commit to coauthor by 2026-06-15"**:
- Neither of us has signal yet on whether this collaboration generates good work for you
- Locking in authorship before any actual contributions is premature
- The Phase-0 items are bounded (4-8 hours) so the trial cost is low for you
- If the trial generates strong contributions, authorship is a natural follow-up conversation; if not, both sides save 6 months of expected-but-unrealized commitment

## 12. Risk acknowledgments + off-ramps

This proposal is not risk-free. Honest list:

| Risk | Likelihood | Mitigation / off-ramp |
|---|---|---|
| **Paper rejection from NeurIPS/COLM** | Medium | Defensible methodology contribution + 5-pillar framing makes top-venue acceptance plausible. If rejected, resubmit to TMLR / Springer Nature Communications. Worst case: arxiv-only + adoption via leaderboard. |
| **Frontier-lab partner falls through** | Medium-High | The launch gate. Without a model-card commitment, AERead lands in EconEvals's 1-cite-at-14-months territory. Backup: maximize PI-endorsement signal (Athey + Roth + Andrews + Gonczarowski + Leyton-Brown) to compensate. |
| **TERMS-Bench releases code with different methodology** | Low-Medium | We generalize their Eq. 4 via `OracleDecomposable` interface, which is independent of their specific implementation. We cite extensively + frame as extension. |
| **OracleDecomposable generalization contested by reviewers** | Medium | Frame conservatively: "we apply their Eq. 4 to non-bargaining domains via abstraction X; we do not claim to invent the decomposition; we name TERMS-Bench in the title." If still contested, drop the "generalization" claim and present as "AERead applies their Eq. 4 to C1 persona-fit." |
| **5-axis taxonomy contested by reviewers** ("too many axes") | Medium | Per-axis prior-art anchors (Zhang/Andrews/Mazeika/Yamin/novel) make the taxonomy defensible. If still contested, fallback ordering: drop Axis 5 (metacog), then Axis 4 (computational floor) — gracefully degrades from 5-axis to 4-axis to 3-axis. Each fallback still beats every existing competitor. |
| **Time commitment mismatch with your day jobs** | Medium | Phase-0 is intentionally bounded (4-8 hours over 2-4 weeks). If even that becomes unworkable, we part ways at the checkpoint with no acrimony. Time-commitment budgets for Phase 1+ are negotiated only at the 4-week checkpoint based on actual Phase-0 fit. |
| **Authorship order disputes** | Low | Deferred to 4-week checkpoint; informed by actual Phase-0 contributions, not pre-committed. Both sides have an off-ramp at the checkpoint if expectations diverge. |
| **Engineering collaborator slot stays open** | Medium | The 2-3 week runtime build (§7) is doable solo at this scope; an engineering coauthor is upside, not blocker. |
| **Open Philanthropy grant rejection** | Medium-Low | Bootstrap-fund v0 at lower-resolution (smaller model coverage, slower API spend). Still ships, just slower. |

## 13. Concrete next steps

1. **Read this proposal + the [methodology summary](methodology.md) + [reading list](reading_list.txt)**. Time: ~30 min for proposal, optional 1-2 hours for the rest.
2. **First sync 2026-06-02 at 4pm Pacific** (30 min) — async agenda + responses 24h prior.
3. **Pick one Phase-0 item each** from §9.2 (Yuecheng) and §9.3 (Zihao); flag your pick at the first sync.
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

## 15. Linked artifacts (in this repo)

- **[Methodology summary](methodology.md)** — 3-layer pipeline + 5-axis taxonomy condensed
- **[Reading list](reading_list.txt)** — T1 / T2 / T3 papers with [AXIS-N] anchor flags
- **[Bibliography](papers/references_master.yaml)** — 160-entry machine-readable references
- **[Curated paper index](papers/_INDEX.md)** — annotated reading guide

---

**End of proposal v0.2.**
