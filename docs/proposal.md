# AgentEcon Readiness (AERead): a unified benchmark for LLM rational economic decision-making

**Proposal v0.2 — for Yuecheng Fang and Zihao Li**
Owner: Cheney Li | Date: 2026-05-26 | Read time: 8 minutes

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
- **Stanford TERMS-Bench** (Zhang/Athey/Roth-advising, May 2026): bilateral negotiation outcome layer
- **Harvard EconEvals** (Fish/Gonczarowski, Feb 2026): procurement/scheduling/pricing parameter+outcome layer
- **MIT Revealed Rationality** (Andrews, Feb 2026): label-free representation-theorem penalties at the axiom layer

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

**What the diagnostic literature itself says about this gap.** Four 2023–2026 diagnostic papers each *explicitly* discuss whether their single-axis approach is sufficient — and each admits it is not. Chadwick et al. 2025 (§Future Work): "(approximate) probabilistic coherence and transitivity of preferences are necessary conditions for rationality, they are arguably **not sufficient**…it has yet to be determined how useful our system is in real-world scenarios"; and they pose precisely AERead's stack-design question: *"does a two-step refinement (first ordinal, then cardinal) outperform a single probability-based approach?"* Betz & Richardson 2023 (§Future Research) calls for "improved diagnostic tools" with "high-resolution representations of an agent's probabilistic belief system" relating inferential structure of training data to current behavior. Zhu & Griffiths 2024 flags the truthful-reporting assumption underlying any single-axis probability probe. Andrews 2026 §7 separates calibration from coherence as complementary properties.

Reading these papers in sequence is reading a request for AERead. The 5-axis taxonomy + cross-decomposition matrix is the integration they each pointed to; the 3-layer pipeline (existence → identification → predictive validity) is the empirical answer to Chadwick's ordinal-then-cardinal question; the collection-of-use-cases Layer 3 design is the cross-domain generalization their single-domain studies could not deliver.

**Our proposal: a 5-axis failure taxonomy**, each axis prior-art-anchored:

| # | Axis | Causal hypothesis | Prior-art anchor |
|---|---|---|---|
| 1 | **Information** | Agent lacks knowledge of hidden state | TERMS-Bench (Zhang et al. 2026) — generalized via `OracleDecomposable` |
| 2 | **Consistency** | Agent's preference / belief structure violates axioms | Andrews 2026 (representation theorem penalties) |
| 3 | **Calibration** | Agent's economic parameters are misfit | Mazeika 2025 (utility engineering) |
| 4 | **Computational floor** | Agent can't execute the math the choice requires | Novel for v0; partial precedent in code-eval lit |
| 5 | **Meta-cognitive calibration** | Agent's confidence is uncalibrated (stated ≠ realized accuracy) | Yamin et al. 2026 (belief coherence) |

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

## 7. Engineering plan — what we ship

### v0 runtime (14 weeks, $40-55K contract engineering)

- **Engine A** (lm-evaluation-harness integration) for Cat A + Cat B + Cat C v1
- **Standard scorer + generator library** (~9 scorers, ~11 generators) — researchers configure via pure YAML
- **Three submission paths** (web form / Colab / PR) — researcher-first, plug-and-play priorities
- **Cache layer never invalidates** — reproducibility hard guarantee
- **5-axis diagnostic decomposition** module (`aeread/diagnostic/`) covering all axes:
  - Axis 1 (information): `OracleDecomposable` interface — TERMS-Bench Eq. 4 generalized
  - Axis 2 (consistency): counterfactual axiom interventions
  - Axis 3 (calibration): parameter-fit attribution
  - Axis 4 (computational floor): quantity substitution
  - Axis 5 (meta-cognitive): confidence elicitation + calibration metrics
- **Live leaderboard** at agenteconreadiness.org accepting external PRs by week 20, with diagnostic drill-down pages (5-axis radar + cross-decomposition matrix)

### Active OSS engineer recruit

In progress (as of 2026-05-26): external-network search (lm-evaluation-harness contributor graph, HuggingFace Datasets maintainers) running. Decision point: 2026-06-15.

### Full v0 (24-week timeline)

| Week | Deliverable |
|---|---|
| 3-4 | A4 stability dimension + adapter / scorer infrastructure |
| 4-6 | A2 monotonicity + A5 prompt invariance |
| 7-8 | A1 transitivity with multi-measurement-model Bayesian posterior |
| 9-12 | Category B (B1 risk, B2 inter-temporal, B3 social preferences) |
| 11-15 | Category C — persona-fit IRL on 5 named investors |
| 13-16 | Diagnostic decomposition implementation + `OracleDecomposable` for C1 |
| 16-18 | Methodology paper draft → arxiv → submission to NeurIPS or COLM 2026 |
| 18-20 | Leaderboard at agenteconreadiness.org with 8+ models tested |
| 21-24 | Tier 2 audit pilot with 1-2 design-partner financial firms |

## 8. Commercial framing (separate from research collaboration)

If the benchmark establishes the brand (Tier 1, marketing engine), three downstream tiers become defensible:

- **Tier 2**: enterprise audit / certification — "your agent fails axiom X in scenario Y; here's the dollar-impact estimate" — $50K-500K per audit. **Anchored on Andrews 2026** representation-theorem rigor for credibility.
- **Tier 3**: online monitoring SaaS — Datadog/Sentry pattern. LangSmith / Patronus / Galileo cover safety / hallucination / RAG but not rationality.
- **Tier 4**: training-signal API — rationality penalties as auxiliary RLHF / DPO loss. **Andrews 2026 provides the academic foundation** (de Finetti / Afriat / Echenique-Saito penalties are LP-checkable in polynomial time, label-free). Cite this in any commercial pitch.

Combined realistic 5-year ARR ceiling: $50-350M.

**This proposal does NOT ask you to commit to the commercial layers.** The v0 methodology paper is a research collaboration; commercial structure is decided separately and revisited at month 6 post-launch.

## 9. Initial team composition

### 9.1 Cheney Li (lead, full-time)

Methodology + IRL infrastructure + Category C implementation. Has working 13F-extraction pipeline (~309 named investor network mapped); has Phase-0 baseline transitivity test results on Claude / GPT / DeepSeek.

**Owns**: §1 (introduction), §2 (related work), §7 (Category C implementation), §8 (experiments), §10 (discussion) of methodology paper. Repo maintenance + leaderboard ops + Open Philanthropy grant application.

### 9.2 Yuecheng Fang — methodology + statistical framework

**Why this team needs you**:
- Berkeley applied-math / statistics background fills the measurement-model-pluralism formalization (Bayesian model selection over 4-6 competing transitivity / monotonicity / dominance models — the statistical-rigor anchor)
- The `OracleDecomposable` generalization (Section 3 above) needs a statistical co-author to formalize the identification conditions across non-bargaining domains
- Sky Computing Lab access is the highest-leverage path for the frontier-lab model-card pre-commitment (the §5 hard launch gate)

**Contribution surface**:
- Methodology paper §3 (methods): measurement-model fitting framework + `OracleDecomposable` identification conditions
- Methodology paper §6 (statistical reproducibility): cross-validation across measurement-model sets; held-out test design
- Co-coordination with Sky Computing Lab / RadixArc on inference-backend determinism guarantees
- Optional: extending the measurement-model framework to a follow-on methods paper on "measurement-model pluralism in LLM evaluation"

**Estimated time commitment**: 8-10 hours/week through paper submission (months 1-6), then 2-4 hours/week for revisions

### 9.3 Zihao Li — game theory + mechanism design

**Why this team needs you**:
- Game-theory background is the natural co-author for the v2 D-dimension expansion (the agent-economy / agent-market thesis you proposed during initial conversation)
- The methodology paper's §10 (discussion) connects AERead to mechanism design — "once humans are replaced by agents, game theory's idealized rational actor assumptions can hold; mechanism design becomes implementable" — that thesis is yours to develop
- US-based, no military-funding restriction, so you can be a US-named co-author on any frontier-lab partnership outcome
- Columbia game-theory standing provides senior credibility for any v2 paper on agentic mechanism design

**Contribution surface**:
- Methodology paper §10 (discussion + future work): mechanism-design extension; agent-market thesis
- v2 paper (separate publication, ~12-18 months out): "Context-conditional rationality + agentic mechanism design" — likely lead authorship
- Methodology paper §3 (methods): game-theoretic foundations for Cat C/D outcome dimensions (TERMS-Bench-style Bayesian games + extensions)
- Connection to Columbia game-theory community for senior-reviewer feedback

**Estimated time commitment**: 4-6 hours/week through paper submission (months 1-6), heavier for v2 paper (months 12-18)

### 9.4 Proposed authorship order (negotiable)

**Methodology paper (v0)**:
- First + corresponding: Cheney Li
- Equal-second authors: Yuecheng Fang, Zihao Li (alphabetical order on title page)
- Acknowledgments: senior advisors, Erica Zhang (via her Athey/Blanchet/Zou connections), Isaiah Andrews (MIT, for §3 review)

**v2 paper (~12-18 months out)**:
- First + corresponding: TBD by topic — likely Zihao Li if mechanism-design-focused, Yuecheng Fang if statistical-methodology-focused
- Cheney + remaining are co-authors

If you'd prefer a different ordering or want to negotiate equal-first on the v0 paper, raise this at the first sync — fully open.

### 9.5 Open recruit: OSS engineer (contract engagement)

Per §7 above. Target: identified by 2026-06-15. Not a methodology coauthor — focused on shipping the runtime per the launch gates. Likely listed in acknowledgments, not author list (depending on contribution scope).

## 10. What's in it for each of you (honest framing)

### For Yuecheng:

- **Co-authorship on a v0 methodology paper targeting NeurIPS / COLM 2026** in a topic the field will be citing for years
- **Possible v2 lead authorship** on the statistical-methodology follow-up
- **Senior-network access**: working closely with the Stanford TERMS-Bench team (via Erica Zhang) + MIT Isaiah Andrews + Harvard Yannai Gonczarowski
- **Sky Computing Lab institutional visibility** via senior advisor introduction
- **No equity commitment**, no commercial-tier obligation
- **Time budget**: 8-10 hr/week × 6 months ~ 200-250 hours total. If that becomes unworkable, you can downshift to "consulting contributor" — credited but not coauthor

### For Zihao:

- **Co-authorship on a v0 methodology paper targeting NeurIPS / COLM 2026**
- **v2 lead authorship** on the mechanism-design / agent-market follow-up (this is the bigger long-term contribution from your skill set)
- **Methodological collaboration with game-theory-adjacent researchers** at Stanford (Athey/Blanchet) and Harvard (Gonczarowski) for review feedback
- **Career visibility**: a benchmark on which frontier labs report their models is the kind of artifact that opens senior-faculty-attention in your application cycle
- **No equity commitment**, no commercial-tier obligation
- **Time budget**: 4-6 hr/week × 6 months ~ 100-150 hours total for v0; heavier for v2

### For Cheney:

- Honest: methodology cohesion + senior-advisor introductions + paper-quality reviewers are the value-adds I can't generate alone. The trade is real: I'm asking for your time + intellectual contribution, you're getting paper authorship + network access + first dibs on the v2 paper.

## 11. Timeline + sync cadence proposal

**First sync**: **Monday 2026-06-02 at 4pm Pacific** (30 min, async-first: written agenda + responses 24h before, live discussion only for things that need it).

**Recurring**: weekly 30-min sync, same slot, through paper submission (months 1-6). Reduce to bi-weekly post-submission unless something is on fire.

**Async channel**: GitHub repo issues + Slack workspace. Slack invite at first sync.

**First-month milestones** (concrete deliverables before first sync):
- Cheney: ship A4 stability dimension end-to-end (target: 2026-06-09)
- Yuecheng: review the measurement-model-pluralism framework + send feedback (target: 2026-06-02)
- Zihao: review §1 (introduction) + §10 (discussion); flag any framings to challenge (target: 2026-06-02)

If you're not available for the proposed slot, propose alternates. The cadence matters more than the specific slot.

## 12. Explicit ask + decision deadline

**Ask**: co-author the v0 methodology paper. Specifically:
- Yuecheng: at the time commitment described in §9.2 + §10
- Zihao: at the time commitment described in §9.3 + §10

**Decision deadline**: **2026-06-15** (3 weeks from now). This gives you time to:
- Review this proposal and the methodology / reading-list artifacts in this repo
- Attend the 2026-06-02 first sync (which is exploratory; not binding)
- Have a follow-up sync 2026-06-09 (week 2)
- Make a final decision before our 2026-06-16 sync

**Off-ramps** (no obligation):
- If you say no, we stay collegial, no hard feelings; I cite your relevant work in the methodology paper as I'd planned to anyway
- If you say yes-but-different-scope (e.g., "I want to be on v2 only" or "I want to be acknowledged but not coauthor"), let's adjust
- If you say yes-but-different-authorship (equal-first, different name order), let's discuss — this is negotiable

## 13. Risk acknowledgments + off-ramps

This proposal is not risk-free. Honest list:

| Risk | Likelihood | Mitigation / off-ramp |
|---|---|---|
| **Paper rejection from NeurIPS/COLM** | Medium | Defensible methodology contribution + 5-pillar framing makes top-venue acceptance plausible. If rejected, resubmit to TMLR / Springer Nature Communications. Worst case: arxiv-only + adoption via leaderboard. |
| **Frontier-lab partner falls through** | Medium-High | The launch gate. Without a model-card commitment, AERead lands in EconEvals's 1-cite-at-14-months territory. Backup: maximize PI-endorsement signal (Athey + Roth + Andrews + Gonczarowski + Leyton-Brown) to compensate. |
| **TERMS-Bench releases code with different methodology** | Low-Medium | We generalize their Eq. 4 via `OracleDecomposable` interface, which is independent of their specific implementation. We cite extensively + frame as extension. |
| **OracleDecomposable generalization contested by reviewers** | Medium | Frame conservatively: "we apply their Eq. 4 to non-bargaining domains via abstraction X; we do not claim to invent the decomposition; we name TERMS-Bench in the title." If still contested, drop the "generalization" claim and present as "AERead applies their Eq. 4 to C1 persona-fit." |
| **5-axis taxonomy contested by reviewers** ("too many axes") | Medium | Per-axis prior-art anchors (Zhang/Andrews/Mazeika/Yamin/novel) make the taxonomy defensible. If still contested, fallback ordering: drop Axis 5 (metacog), then Axis 4 (computational floor) — gracefully degrades from 5-axis to 4-axis to 3-axis. Each fallback still beats every existing competitor. |
| **Time commitment mismatch with your day jobs** | Medium-High | Explicit hour budgets in §9.2 + §9.3. If 8-10 / 4-6 hr/week become unworkable, downshift to "consulting contributor"; no acrimony. |
| **Authorship order disputes** | Low | Explicit proposal in §9.4 + negotiable. Lock at first sync 2026-06-02 to avoid mid-paper drama. |
| **OSS engineer recruit falls through** | Medium | Cheney ships solo at ~16-20 wk timeline (vs 12-16 with engineer). Total v0 delivery slips by 4-8 weeks; this is the largest concrete risk to the launch-gate calendar. |
| **Open Philanthropy grant rejection** | Medium-Low | Bootstrap-fund v0 at lower-resolution (smaller model coverage, slower API spend). Still ships, just slower. |

## 14. Concrete next steps

1. **You read this proposal + the [methodology summary](methodology.md) + [reading list](reading_list.txt)**. Time: ~30 min for proposal, optional 1-2 hours for the rest.
2. **First sync 2026-06-02 at 4pm Pacific** (30 min) — async agenda + responses 24h prior.
3. **Yuecheng: review the measurement-model-pluralism framework + send feedback** by 2026-06-02.
4. **Zihao: review the §1 + §10 framing of the methodology paper draft outline + flag any framings to challenge** by 2026-06-02.
5. **Cheney: ship A4 stability dimension end-to-end** by 2026-06-09.
6. **All three: outreach to Isaiah Andrews (MIT) and Yannai Gonczarowski (Harvard)** during June — Cheney drafts the DMs; both review before send.
7. **Second sync 2026-06-09 (week 2)** — refine v0.3 of this proposal based on feedback.
8. **Decision by 2026-06-15** — formal commit (or off-ramp) on co-authorship.
9. **Third sync 2026-06-16** — assuming yes-yes outcome, lock authorship order + paper outline + role split through paper submission.

## 15. What this proposal is NOT asking for

- It is NOT asking either of you to commit to founding a company. We can write the paper as a research collaboration and revisit commercial structure independently.
- It is NOT asking for capital or introductions to investors. v0 is bootstrap-funded through Open Phil grant application + Cheney's personal time.
- It is NOT asking for equity / IP commitments. The OSS layer is MIT-licensed forever; commercial layers are deferred and independently funded.
- It is NOT asking for endorsement letters or "we vouch for AERead" public statements. Those come later, and only after v0 results justify them.

What it IS asking: do you both want to co-author the v0 methodology paper at the time commitment in §9. Decision by **2026-06-15**.

## 16. Linked artifacts (in this repo)

- **[Methodology summary](methodology.md)** — 3-layer pipeline + 5-axis taxonomy condensed
- **[Reading list](reading_list.txt)** — T1 / T2 / T3 papers with [AXIS-N] anchor flags
- **[Bibliography](papers/references_master.yaml)** — 160-entry machine-readable references
- **[Curated paper index](papers/_INDEX.md)** — annotated reading guide

---

**End of proposal v0.2.**
