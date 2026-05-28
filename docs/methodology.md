# AERead methodology — 3-layer pipeline + 5-axis failure taxonomy

This is a condensed methodology overview. The full master plan lives in the implementation repo; this document describes the conceptual architecture that should travel with the proposal.

> **Citation links.** Every paper named below has a clickable link in [`papers/links.md`](papers/links.md) — public URL where one exists, or PDF in [`papers/pdfs/`](papers/pdfs/) where it does not. Inline links below are first-occurrence only.
>
> **Operational scope**: this doc describes the **full methodology framework** with inline v0/v0.5+ scope tags showing what v0 first paper implements vs what defers to v0.5+. For a **consolidated operational view** (v0 deliverables, ownership map, phase timeline, status tracker — all in one place), see [`v0_sprint.md`](v0_sprint.md).

## The thesis in one paragraph

LLM agents are being deployed for economic decisions — procurement, pricing, negotiation, investment, vendor selection. Whether they satisfy the rationality assumptions those use cases presuppose has not been validated at scale. AERead is the **economic-decision evaluation framework** for LLM agents — combining game environments, oracle decomposition, revealed-preference diagnostics, qualitative-evidence interpretation, and hidden-OOD generalization tests into a single integrated artifact. Architecturally: a 3-layer revealed-preference pipeline (existence → identification → predictive validity) cross-cut by a 5-axis failure taxonomy (information, consistency, calibration, computational floor, meta-cognitive). The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed.

## Critical methodological questions (open Q&A)

10 open methodological questions for major-lab adoption + methodology-paper acceptance. Working positions, not closed claims — engagement invited on all ten. **Full bodies + tables + "Open:" engagement lines for each Q live in [`methodology_open_questions.md`](methodology_open_questions.md).** This topic index is the navigation pointer:

| Q | Topic | Working position |
|---|---|---|
| **Q1** | Function misspecification + within-class identification | Multi-class robustness over 3 v0 functional classes (KT '79 + CRRA + Kelly-Markowitz) + measurement-model pluralism + predict-then-validate |
| **Q2** | Numeric-feature evaluation | Strict-propriety scoring (Brier/CRPS, dollar surplus, oracle gap); ECE diagnostic-only |
| **Q3** | Qualitative-feature scoring (no hidden cardinal truth) | Ordinal states + 4-tier optimality + single utility-weight vector per buyer (v0); robust-utility-family is v0.5+ |
| **Q4** | Generalization battery + benchmark integrity | v0: 3 splits + 2 counterfactual variants + Transfer Ratio + main effects only |
| **Q5** | RL environment + training-signal mechanisms | 4 prior-art-anchored mechanisms described; v0 ships Andrews-style penalty/scorer reference only |
| **Q6** | Training-signal contamination + AERead-Train/Dev/Cert | Tier-separation naming; v0 docs-only convention; v0.5+ adds infra enforcement |
| **Q7** | Layer 1+2 vs Layer 3 residual hypothesis | Per-domain explanatory-power table (60-75% procurement → 25-50% long-horizon); pre-registered falsification |
| **Q8** | OpenSpiel-compatible benchmark substrate | Post-v0-paper follow-up paper, NOT v0.5+; v0 ships 2 standalone games |
| **Q9** | Operational emergence definition | Conservative 5-criterion test for emergence claims (addresses Schaeffer-Krueger 2023 critique) |
| **Q10** | Training-signal validation (scorer vs validated signal) | v0 ships a scorer + observational evidence; causal claim requires training experiment. Three options pending checkpoint. |


## Methodological foundation in behavioral economics

AERead is not inventing scoring methodology from scratch. The methodological stack draws from established behavioral-economics and decision-research methods, with citations frontier-lab reviewers can audit:

| AERead element | Established method | Anchor citation |
|---|---|---|
| **Layer 1 axiom checks** | Revealed-preference tests (GARP / WARP / SARSEU); Critical Cost Efficiency Index | Afriat 1967; Echenique-Saito 2015 |
| **Layer 2 within-class identification** | Random utility models (RUM); multi-class MLE | McFadden 1974; Train 2009 |
| **Q3 qualitative-feature scoring** | Discrete choice experiments; conjoint analysis; best-worst scaling | Louviere et al. 2000; Marley & Louviere 2005 |
| **Buyer-fit decomposition** | Multi-attribute utility theory (MAUT) | Keeney & Raiffa 1976 |
| **4-tier optimality (robust optimal / acceptable / weak / dominated)** | Robust optimization + partial-order scoring | Ben-Tal & Nemirovski 2002 |
| **Risk preferences across functional classes** | Prospect theory (KT '79); cumulative prospect theory (TK '92) | Kahneman & Tversky 1979; Tversky & Kahneman 1992 |
| **Preference-flip / paraphrase / dominated-option counterfactuals** | Vignette experiments; qualitative coding | Atzmüller & Steiner 2010 |
| **Calibration vs coherence separation** | Strictly proper scoring rules | Gneiting & Raftery 2007 |
| **Information-state diagnostics (Axis 1)** | Belief elicitation; Bayesian updating tests | Harrison & Rutström 2008 |
| **Counterfactual interventions** | Causal inference (do-calculus framing) | Pearl 2009 |

The integrative move is combining these established methods into a single LLM-evaluation framework — not the methods themselves. This grounding is what gives the methodology paper its reviewer-defensibility: every load-bearing scoring decision has a 30-50-year-old citation behind it.

**Open**: the methodological-foundation table is an audit invitation. Reviewers spotting a load-bearing methodological choice without a cited anchor are exactly the engagement we want — those are the gaps the methodology paper needs to address before preprint circulation.

## The 3-layer pipeline

The three layers are the canonical revealed-preference pipeline applied to LLM behavior:

| Layer | Question | Method | What's measured |
|---|---|---|---|
| 1 — existence | Does any rationalizing utility exist? | Axiomatic compliance: CCEI / GARP / WARP / transitivity / monotonicity / dominance | Pass/fail (per axiom) + degree of violation |
| 2 — identification | Within a chosen functional class, what utility parameters are consistent with observed choices? | MLE fit of KT prospect (λ, α) / CRRA / CARA / exp-vs-hyperbolic discount (δ, k) / Fehr-Schmidt (α, β) on training portion | Per-class point estimates + log-likelihood / AIC / BIC + Bayesian posterior over classes |
| 3 — predictive validity | Does the identified utility predict held-out choices? | Predict-then-validate: train/test split → identify on training → predict held-out → score predictive accuracy | Choice-agreement rate (discrete) + MAE (continuous) on held-out + oracle gap |

The methodology paper's load-bearing argument is that **integration** of all three layers is what enables actionable diagnostics. A single-number score at any one layer (the current state of the art) cannot tell you whether a model failed because its preferences are inconsistent, because its calibrated utility is wrong, or because it can't execute the choice the calibrated utility prescribes.

## Layer 3 design discipline: predict-then-validate

Every Layer 3 use case follows the same protocol:

1. **Train/test split** — partition observed decisions into N−K training + K held-out (fixed seed, immutable manifest).
2. **Layer 2 identification** — fit parameters within the assumed functional class using training only.
3. **Predict held-out** — deterministic prediction from fitted parameters + observable context.
4. **Predictive accuracy** — choice-agreement rate (for discrete choices) or MAE (for continuous emissions) on held-out decisions.

Multi-class robustness check: fit **3 candidate functional classes in v0** (KT prospect '79, CRRA, Kelly-Markowitz) on the training set; report a posterior over classes as a secondary score. CARA + cumulative prospect theory TK '92 are added in v0.5+. This is the response to [Andrews 2026](papers/pdfs/andrews_2026_revealed_rationality.pdf)'s non-identification critique: within-class identification is honest about which functional class assumption is doing the work, and the 3-class v0 already demonstrates the principle without requiring the full 5-class suite.

## OracleDecomposable: the load-bearing abstraction

A Layer 3 use case is `OracleDecomposable` if it admits:

- A **hidden state** (the principal's preferences, the vendor's true cost, etc.)
- A **controllable simulator** (we can substitute beliefs or reveal state)
- An **oracle policy** (the Bayes-optimal action given perfect knowledge of the hidden state)
- A **scalar utility function** over (action, hidden state)

Any such use case is **a candidate** for the [TERMS-Bench](https://arxiv.org/abs/2605.13909) Eq. 4 decomposition: U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl (information gap + uncertainty gap + control gap). The "any such use case admits the decomposition" claim is **conditional** — TERMS-Bench's decomposition is simulator-relative and intervention-order-specific; the full conditions under which an OracleDecomposable task admits a well-defined Eq. 4 attribution (non-commutativity of interventions; Shapley/Sobol-style attribution when interventions don't commute; failure conditions when the abstraction breaks) are exactly what Zihao's Phase-0 (A) formalization scope ([proposal §9.2](proposal.md#92-zihao-li--proposed-phase-0-dol-econ--formal-math-foundation-track)) is meant to prove. Until that Phase-0 work lands, the OracleDecomposable interface is a **candidate abstraction with conditions to be formalized**, not a closed claim.

Zhang et al. 2026 introduced this decomposition for bilateral bargaining. We abstract the construction and demonstrate it on a *collection* of use cases. The v0 collection (2 deep games — scope discipline at v0 is what makes the first paper publishable rather than diffuse):

- **C2 ProductProcurementGame (v0)**: single-agent, one-shot, **discrete-action**; hidden state = vendor true cost + structured qualitative attributes (durability evidence / assembly friction / style fit etc.); **v0 oracle = optimal under single declared utility-weight vector per buyer profile** (per Q3 v0 scope — single-vector scoring); v0.5+ upgrade is the robust-utility-family extension (oracle = robust-optimal across plausible weight vectors). Deterministic preference-matching payoff. The qualitative-evidence procurement structure.
- **C8 SimplePricingGame (v0)**: single-agent, one-shot, **continuous-action** (price p ∈ [0, P_max]); hidden state = true demand-curve parameters (intercept α*, elasticity β*, noise σ*). **Designed for TERMS-Bench Eq. 4 decomposition** via three conditions: (a) **base** = model sees declared prior + product description + **n=10 noisy historical (price, quantity) sales observations** → infers posterior + picks price; (b) **belief-substituted** = model is given the Bayes-optimal posterior directly → picks price (isolates posterior-computation gap from price-choice gap); (c) **state-revealed** = true (α*, β*, σ*) revealed → picks oracle price. Eq. 4 splits the gap as Δ_inf (state-revealed − base) + Δ_unc (belief-substituted − base) + Δ_ctrl (state-revealed − belief-substituted). Oracle = Bayes-optimal expected revenue under the posterior (closed-form for linear demand). **Structurally distinct from C2** on action space (continuous vs discrete) + outcome (stochastic revenue vs deterministic preference match) + oracle math (Bayesian-posterior argmax vs utility-vector dot product) + uncertainty representation (parametric demand curve + noisy evidence vs qualitative text). The pair (C2 + C8) demonstrates Eq. 4 across action-space variation — genuine structural distinction beyond uncertainty-type variation.

**Roadmap** (v0.5 → v1 expansion):

- **D3 VendorSelectionGame** (single-agent risk/uncertainty supplier selection): hidden state = supplier reliability + lead-time variance; oracle = Bayes risk minimization given declared utility curvature. **Demoted from v0 to v0.5+** (2026-05-28) because structurally similar to C2 (single-agent + one-shot + discrete-choice + solo + decision-theoretic); v0 pair needed cross-structure variation, so C8 SimplePricingGame replaced D3.
- **D2 Bargaining**: native TERMS-Bench instantiation; wrap their runtime when code releases. Multi-agent strategic; broadens generalization claim significantly.
- **C1 Persona-fit (portfolio/investment, Layer 2 parameter-fit case study)**: hidden state = principal's IRL-fit utility coefficients (α_kelly, δ_turnover); oracle = closed-form Kelly-Markowitz. **Caveat**: 13F filings are an approximate revealed-preference proxy (long positions only, quarterly delay; shorts + derivatives not required) — treated as an approximate-RP case study with assumption sensitivity tests. The rationale source repo continues to develop C1's IRL infrastructure; it appears as a v0.5+ Layer 3 case once the v0 procurement + pricing framework is validated.
- **Agentic marketplace extension**: extends D3 to multi-agent marketplace + agentic tool-use
- **EconEvals A2 pricing wrap**: v0.5+ wrap of EconEvals's full multi-period pricing dimension (100 periods × 3 difficulty levels × collusion litmus); C8 v0 SimplePricingGame is the AERead-native single-period simplification that maps to A2 territory
- **NegotiationGame** + **PricingCompetitionGame**: per [`aeread_env_design.md`](aeread_env_design.md) MVP roster — **post-v0-paper substrate follow-up paper** deliverables (NOT v0.5+; substrate itself is the follow-up paper, not a v0.5 extension)

The full open candidate pool — ~25 cases including EconEvals procurement/pricing/scheduling wraps, Calvano collusion detection, Gale-Shapley two-sided matching, Vending-Bench long-horizon coherence, weather/event forecasting — is enumerated in [`layer3_candidates.md`](layer3_candidates.md) on a value × testability matrix with per-case pros/cons. The generalization claim is the multi-domain application — not just one new task wrapped in the same Eq. 4. v0 ships with 2 deep games (discrete-action C2 + continuous-action C8); v0.5+ expansion ranks against the candidate pool.

## The 5-axis failure taxonomy

When a model scores low on a Layer 3 task, *which mechanism failed?* The 5-axis taxonomy decomposes the gap.

**v0 instrumentation tiers** (5-axis taxonomy stays intact as the paper's §3 claim; instrumentation depth varies):

| Axis | v0 instrumentation | v0.5+ extension |
|---|---|---|
| **Axis 1 — Information** | Full Δ_inf measurement per OracleDecomposable (TERMS-Bench Eq. 4) | Belief-substitution beyond state-reveal |
| **Axis 2 — Consistency** | 2 axiom tests (transitivity + dominance) per game | Full 6-axiom family (CCEI/GARP/WARP/transitivity/monotonicity/Houtman-Maks) |
| **Axis 3 — Calibration** | Brier score + within-class utility-fit error per Q1 multi-class | ECE diagnostic + reliability diagrams + full proper-scoring-rule suite |
| **Axis 4 — Computational floor** | 1 quantity-substitution probe per game (sketched only) | Full computation-substitution suite (LP-substitution / DP-substitution / Bayes-update-substitution) |
| **Axis 5 — Meta-cognitive** | Confidence elicitation + Brier calibration on held-out (sketched only) | Full Dutch-book / probabilistic-identity / money-pump probe suite |

**Why this split**: the 5-axis taxonomy paper claim is the integrative framework; v0 demonstrates it by **fully instrumenting axes 1-3** + **sketching axes 4-5 with 1 sub-test each**. Reviewers see the full taxonomy in the paper; the implementation is partial-but-honest. v0.5+ extensions are pre-committed in the methodology paper's "Future work" section + the v0.5+ extension column above.

| # | Axis | Causal hypothesis | Prior-art anchor |
|---|---|---|---|
| 1 | **Information** | Agent lacks knowledge of hidden state | TERMS-Bench (Zhang et al. 2026) — generalized via OracleDecomposable |
| 2 | **Consistency** | Agent's preference / belief structure violates axioms | Andrews 2026 (representation theorem penalties) |
| 3 | **Calibration** | Agent's economic parameters are misfit (Layer 2 identification fails) | [Mazeika 2025](https://arxiv.org/abs/2502.08640) (utility engineering); [Guo et al. 2017](https://arxiv.org/abs/1706.04599) (ECE diagnostic); [Gneiting & Raftery 2007](papers/pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf) (proper scoring rules) |
| 4 | **Computational floor** | Agent can't execute the math the choice requires | Specific quantity-substitution operationalization; EconEvals 2025 competency-as-prerequisite is the closest precedent (we extend it from pre-check to per-axis decomposition) |
| 5 | **Meta-cognitive** | Agent's confidence is uncalibrated (stated ≠ realized accuracy) | [Yamin et al. 2026](https://arxiv.org/abs/2602.06286) (belief coherence); [Chadwick 2025](papers/pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) (Dutch books); [Zhu & Griffiths 2024](https://arxiv.org/abs/2401.16646) (incoherent probability judgments) |

**Axis 5 footnote — calibration vs. coherence as complementary, not redundant.** Following Andrews 2026's framing, we treat *calibration* ([Guo et al. 2017](https://arxiv.org/abs/1706.04599); [Gneiting & Raftery 2007](papers/pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf)'s proper scoring rules) and *coherence* (de Finetti / Dutch-book diagnostics) as **complementary** properties. Calibration asks whether predicted probabilities match empirical frequencies — it requires ground-truth outcomes and operates event-by-event. Coherence asks whether stated probabilities are internally consistent — it requires no ground truth and operates across multiple related assessments. A model can be well-calibrated on many events yet incoherent across them, or coherent yet poorly calibrated. AERead's Axis 5 reports both signals separately: calibration error against the held-out validation set (Layer 3 outcomes), and coherence violations under Dutch-book / proper-scoring-rule probes (no ground truth needed).

**Methodological gotcha — strict propriety for the leaderboard score.** Gneiting & Raftery 2007 establishes that a leaderboard score (which models are incentivized to maximize) must use a **strictly proper** scoring rule, otherwise it can be gamed by deliberate miscalibration. Expected Calibration Error (Guo et al. 2017) is the field-standard *diagnostic* metric but is **not strictly proper** — it can be lowered by shifting probability mass away from extreme bins without improving the underlying forecast. AERead therefore uses **Brier score (discrete events) and Continuous Ranked Probability Score / CRPS (continuous emissions)** for the leaderboard headline, both of which are strictly proper per Gneiting & Raftery's §3-§4. ECE + reliability diagrams remain on the diagnostic page for interpretability, but they do not enter the ranking.

Each axis has a distinct intervention mechanism:
- **Axis 1**: substitute beliefs / reveal state and rerun
- **Axis 2**: present counterfactual choice triplets and check axiom violations
- **Axis 3**: hold out test decisions, refit, compare predictive accuracy
- **Axis 4**: substitute the computational quantity with a closed-form answer
- **Axis 5**: elicit confidence + compare to realized accuracy for calibration (Brier score on held-out events; ECE + reliability diagrams for diagnostic visualization); run Dutch-book + money-pump constructions (Chadwick 2025) and probabilistic-identity probes (Zhu & Griffiths 2024) for coherence (no ground truth needed)

Cross-decomposition (Axis 1 × Axis 2, etc.) produces an attribution matrix with main-effect cells + pairwise interaction cells + residual. **Whether main effects explain a high fraction of the per-(model, task) gap is a per-domain empirical hypothesis** (per Q7 working ranges: 60-75% discrete-action procurement (v0 C2), 50-70% continuous-action pricing (v0 C8), declining to 30-55% multi-agent markets and 25-50% long-horizon agents — see [`methodology_open_questions.md` § Q7](methodology_open_questions.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual) for the full table). This is pre-registered with falsification criteria per domain, not assumed as a uniform threshold. Interactions between axes are expected (e.g., calibration depends on whether the agent has the relevant information; computational-floor failures can masquerade as inconsistent preference) — the factorial design measures these rather than assuming them away.

### Relation to the diagnostic-and-correction literature

A growing body of work documents LLM rationality violations: [Betz & Richardson 2023](https://doi.org/10.1371/journal.pone.0281372) (probabilistic coherence as an epistemic-agent property; with a training-step correction), [Chen et al. 2023](https://arxiv.org/abs/2305.12763) (emergence of economic rationality), [Hagendorff et al. 2023](https://arxiv.org/abs/2212.05206) (thinking-fast-and-slow patterns), Zhu & Griffiths 2024 (incoherent probability judgments), Chadwick et al. 2025 (Dutch-book / money-pump diagnostics + post-processing correction), [Wen 2025](https://arxiv.org/abs/2501.18190) (persona-degrades-GARP), and [Qiu et al. 2026](https://arxiv.org/abs/2503.17523) (Bayesian-teaching training corrections). AERead's contribution relative to this literature is the **integrative** stance: rather than documenting one violation type at a time, the 5-axis taxonomy organizes all of them into a single attribution framework anchored on Andrews 2026's representation-theorem "if and only if" guarantees — if the per-axis penalty terms can be driven to zero, the representation theorems imply that there must exist a prior + utility + computational policy + calibration map that fully explain the model's behavior. The diagnostic page is what makes that attribution legible.

#### What these papers say about the diagnostic-framework challenge

These papers each *explicitly* discuss whether their diagnostic / correction approach works and what challenges remain. The challenges they admit cluster into a tight set — and the cluster maps onto the design constraints AERead is built to satisfy:

| Challenge admitted in the literature | Source | AERead's design response |
|---|---|---|
| **Single-domain validation** — each paper tests one axis in one domain | Betz (synthetic corpora), Zhu-Griffiths (weather + politics), Chadwick (synthetic preferences), Mazeika (preference elicitation only) | The collection-of-use-cases framing (Layer 3 v0: C2 ProductProcurementGame + C8 SimplePricingGame demonstrating Eq. 4 across **action-space variation** — discrete vs continuous; roadmap adds D2 bargaining, D3 VendorSelectionGame, C1 persona-fit, agentic marketplace) demonstrates portability of the same Eq. 4 decomposition across non-bargaining domains |
| **Coherence ≠ accuracy** — necessary but not sufficient | Chadwick explicit ("a model's probability estimates may be coherent but still fail to be calibrated or accurate"); Betz Q4 caveat; Andrews 2026 §7 | Axis 5 reports calibration (Brier on held-out outcomes) AND coherence (Dutch-book / probabilistic-identity probes) **separately**; never substitutes one for the other |
| **Scaling unverified** — small models / narrow domains | Betz (T5 only; BART / GPT-3 not tested); Zhu-Griffiths (4 SOTA but only on probability judgments, not deployed decisions) | AERead targets frontier LLMs on deployment-relevant tasks (13F decisions, procurement, negotiation) — the scaling gap *is* our headline contribution |
| **Stack-design question: which combination order?** | Chadwick explicit: "does a two-step refinement (first ordinal, then cardinal) outperform a single probability-based approach?" | The 3-layer pipeline IS our answer: existence → identification → predictive validity. The cross-layer attribution matrix measures whether the layers compose. |
| **Choice of measurement model matters** | Chadwick (Kemeny may not be the right benchmark); Betz (multiple normative frameworks beyond Bayesian) | Measurement-model pluralism (4-6 competing models per axiom; Bayesian posterior reported over them) is a methodological commitment, not an assumption |
| **Real-world deployment gap** | Chadwick: "it has yet to be determined how useful our system is in real-world scenarios"; all four implicit | Predict-then-validate Layer 3 design (see "Layer 3 design discipline" section above) — the headline score IS held-out predictive accuracy on deployed-style decisions |
| **Cross-axis integration is missing** | All four papers test ≤ 1 axis | The 5-axis taxonomy + cross-decomposition matrix is the integrative claim — none of the prior diagnostic papers attempt this |
| **Existential-statement falsification problem** | Betz (Rationality Hypothesis can be confirmed by example, never falsified by absence) | AERead reports per-(model, task) fingerprints, not a "this model is rational" verdict — sidesteps the falsification problem |
| **Truthful-reporting assumption** | Zhu-Griffiths footnote: "LLMs were assumed to demonstrate truthful reporting of latent event probabilities" | Stated-vs-revealed cross-checks (compare elicited probability vs deployed choice) are part of Axis 5; we don't take stated confidence at face value |

Betz & Richardson 2023's §Future Research explicitly calls for "improved diagnostic tools" with "high-resolution representations of an agent's probabilistic belief system" and the ability to relate the inferential structure of training data to current model behavior. **AERead's 5-axis cross-decomposition + drill-down diagnostic page is exactly the artifact they called for.**

Chadwick et al. 2025's §Future Work explicitly asks: "does a two-step refinement (first ordinal, then cardinal) outperform a single probability-based approach?" **AERead's 3-layer pipeline (existence → identification → predictive validity) is the empirical answer.**

The methodology paper's §3 framing therefore writes itself: four 2023–2026 diagnostic papers each measured one axis of LLM rationality in one domain; each explicitly admitted that integration with other axes, scaling beyond their setup, the coherence-vs-accuracy gap, and real-world deployment validity remained open. AERead is built directly on the diagnostic surface Betz & Richardson called for and the stack-design question Chadwick et al. posed.

## The diagnostic surface

Every per-(model, task) leaderboard row links to a drill-down page rendering:

1. **5-axis radar chart** — one spoke per axis, with the model's per-axis gap visualized
2. **Headline diagnostic** — "model X's primary failure mode is Axis 3 calibration via B1 risk-preference miscalibration during persona inference"
3. **Cross-decomposition matrix** — full attribution at the per-cell level for advanced users
4. **Cat A waterfall** — per-axiom delta sorted by magnitude
5. **Cat B card** — predicted-vs-actual parameter table + consistency boolean
6. **Oracle-gap card** (if applicable) — Δ_inf / Δ_unc / Δ_ctrl split with TERMS-Bench citation
7. **Counterfactual scenario card** — "if Axis 4 computational floor were fixed, predictive accuracy → 0.71"
8. **Raw trajectory viewer** — link to JSONL with per-decision rationale + axiom-probe results

This page is the **load-bearing diagnostic artifact** of the methodology paper: when a reviewer asks "show me how the 5-axis decomposition tells me something I couldn't get from a single-number leaderboard," the answer is one of these. The same page is also what enables downstream applications (deployed-agent diagnostics, training-signal feedback, audit deliverables) — but those are derivative of the methodology-paper artifact, not the other way around.

## Five methodological commitments

Each citation-anchored:

1. **Descriptive measurement, not normative ranking.** Higher composite scores ≠ better-aligned. *Andrews 2026 §7.*
2. **Measurement-model pluralism.** 4-6 competing models per axiom; report Bayesian posterior. *Echenique 2021 / Davis-Stober.*
3. **Judge-free by construction.** No LLM evaluates another LLM. All three anchor papers (TERMS-Bench May 2026; Revealed Rationality Feb 2026; EconEvals March 2025) independently adopted this. *TERMS-Bench / EconEvals / QEDBench.*
4. **Context-conditional axiomatization.** Personas degrade axiom compliance; this is a measurable dimension, not an assumption to control. *Wen 2025.*
5. **Cross-layer attribution + oracle-gap decomposition.** What turns scores into actionable signals.

## How to engage (pre-commercial final goal)

These docs are working artifacts. AERead's pre-commercial deliverable is the methodology paper + reproducible v0 runtime — and the citation channel we're optimizing for is **methodological engagement from frontier-lab researchers**, not adoption traction alone. Every design choice (Q&A invitations, pre-registered factorial hypothesis, falsification criteria, OracleDecomposable counterexample channel, OpenSpiel-compatible substrate) is structured to invite engagement *before* the methodology paper circulates.

Engagement is invited at every layer:

- **On the open methodology Q&A** (full bodies in [`methodology_open_questions.md`](methodology_open_questions.md); topic-index above): the ten questions are real research questions; reviewers, frontier-lab researchers, and collaborators are invited to challenge the working positions before the methodology paper draft circulates. Q10 (training-signal validation) is the most consequential v0 scope decision pending the 4-week checkpoint.
- **On the 5-axis taxonomy**: if a sixth axis is needed (or a current axis collapses into another), the pre-registered factorial design will reveal it — pre-registration commits us to publishing the finding regardless of direction
- **On the OracleDecomposable abstraction**: counterexamples — economic decisions that don't fit the (hidden state + controllable simulator + oracle policy + scalar utility) interface — strengthen the methodology paper by exposing scope limits. Submit them.
- **On Layer 3 use cases**: the open candidate pool ([`layer3_candidates.md`](layer3_candidates.md)) invites external researchers to propose new cases via the value × testability matrix; high-value + high-testability gaps (especially the empty top-right cell) are explicitly open contribution surface
- **On the OpenSpiel-compatible substrate** ([`aeread_env_design.md`](aeread_env_design.md)): external contributors can add games via the 10-hard-constraint submission API once the substrate ships (post-v0-paper follow-up paper, NOT v0.5)
- **On the falsifiability of §3** ([proposal §3](proposal.md#3-novel-methodology-contribution-5-axis-failure-taxonomy--oracledecomposable-generalization)): the headline per-domain explanatory-share hypothesis (60-75% discrete-action procurement → 25-50% long-horizon agents; see [`methodology_open_questions.md` § Q7](methodology_open_questions.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual) for the full table) is pre-registered with falsification criteria — reviewers can challenge the per-domain thresholds or the design before cross-model evaluation begins

**Channel for engagement**: contact details in [`proposal.md` §15](proposal.md). Before methodology-paper preprint circulation, we will invite reviewer engagement from major-lab safety + economics-of-AI researchers — pre-registration is the artifact that makes the §3 claim citable rather than asserted.

## Adoption commitment: plug-and-play usability

Plug-and-play is an **adoption** commitment, not a methodology commitment — separate from the five above. Adoption traction analysis (25 benchmarks studied) found that no benchmark > 200 cites lacks (a) a live submission leaderboard with auto-scoring, (b) a frontier-lab model-card commitment, and (c) ≤ 5-minute clone-to-first-output. Therefore AERead is designed for:

- Zero-code task contribution via YAML
- One-line evaluation: `pip install aeread && aeread evaluate --model claude-opus-4-7 --task all`
- **v0**: one submission path (web form); Colab + PR paths defer to v0.5+
- Integration AS lm-evaluation-harness task family — so labs already running `lm_eval` have us installed automatically
- Cache layer never invalidates — good-hygiene reproducibility (cache hashes externally auditable; signed-ScoreRecord cryptographic provenance defers to v0.5+)

## What this is not

- It is not a normative test of "rationality." Higher AERead scores ≠ better-aligned models.
- It is not a substitute for safety / hallucination / RAG benchmarks. It is the rationality dimension that those benchmarks do not measure.
- It is not a single-number leaderboard. It is a fingerprint along multiple axes, and the diagnostic page is the load-bearing artifact.
- It does not claim to invent the decomposition methods. Each pillar is an extension of an existing piece of literature; the integration is the novel contribution.
