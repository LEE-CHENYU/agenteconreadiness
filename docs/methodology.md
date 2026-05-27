# AERead methodology — 3-layer pipeline + 5-axis failure taxonomy

This is a condensed methodology overview. The full master plan lives in the implementation repo; this document describes the conceptual architecture that should travel with the proposal.

> **Citation links.** Every paper named below has a clickable link in [`papers/links.md`](papers/links.md) — public URL where one exists, or PDF in [`papers/pdfs/`](papers/pdfs/) where it does not. Inline links below are first-occurrence only.

## The thesis in one paragraph

LLM agents are being deployed for economic decisions — procurement, pricing, negotiation, investment, vendor selection. Whether they satisfy the rationality assumptions those use cases presuppose has not been validated at scale. AERead is the integrated benchmark: a 3-layer revealed-preference pipeline (existence → identification → predictive validity) cross-cut by a 5-axis failure taxonomy (information, consistency, calibration, computational floor, meta-cognitive). The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed.

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

Multi-class robustness check: fit all 5 candidate functional classes (prospect theory KT '79, CRRA, CARA, cumulative prospect theory TK '92, Kelly-Markowitz) on the training set; report a posterior over classes as a secondary score. This is the response to [Andrews 2026](papers/pdfs/andrews_2026_revealed_rationality.pdf)'s non-identification critique: within-class identification is honest about which functional class assumption is doing the work.

## OracleDecomposable: the load-bearing abstraction

A Layer 3 use case is `OracleDecomposable` if it admits:

- A **hidden state** (the principal's preferences, the vendor's true cost, etc.)
- A **controllable simulator** (we can substitute beliefs or reveal state)
- An **oracle policy** (the Bayes-optimal action given perfect knowledge of the hidden state)
- A **scalar utility function** over (action, hidden state)

Any such use case admits the [TERMS-Bench](https://arxiv.org/abs/2605.13909) Eq. 4 decomposition: U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl (information gap + uncertainty gap + control gap).

Zhang et al. 2026 introduced this decomposition for bilateral bargaining. We abstract the construction and demonstrate it on a *collection* of use cases. The v0 collection:

- **C1 Persona-fit**: hidden state = principal's IRL-fit utility coefficients (α_kelly, δ_turnover); oracle = closed-form Kelly-Markowitz
- **C2 Price-aware product selection**: hidden state = vendor true cost/quality; oracle = cheapest dominating choice
- **D2 Bargaining (v2)**: native TERMS-Bench instantiation
- **D3 Agentic vendor selection (v2)**: extends C2 to full marketplace with agentic tool-use

The full open candidate pool — ~25 cases including EconEvals procurement/pricing/scheduling wraps, Calvano collusion detection, Gale-Shapley two-sided matching, Vending-Bench long-horizon coherence, weather/event forecasting — is enumerated in [`layer3_candidates.md`](layer3_candidates.md) on a value × testability matrix with per-case pros/cons. The generalization claim is the multi-domain application — not just one new task wrapped in the same Eq. 4. v0 ships with 4; v0.5+ expansion ranks against the candidate pool.

## The 5-axis failure taxonomy

When a model scores low on a Layer 3 task, *which mechanism failed?* The 5-axis taxonomy decomposes the gap:

| # | Axis | Causal hypothesis | Prior-art anchor |
|---|---|---|---|
| 1 | **Information** | Agent lacks knowledge of hidden state | TERMS-Bench (Zhang et al. 2026) — generalized via OracleDecomposable |
| 2 | **Consistency** | Agent's preference / belief structure violates axioms | Andrews 2026 (representation theorem penalties) |
| 3 | **Calibration** | Agent's economic parameters are misfit (Layer 2 identification fails) | [Mazeika 2025](https://arxiv.org/abs/2502.08640) (utility engineering); [Guo et al. 2017](https://arxiv.org/abs/1706.04599) (ECE diagnostic); [Gneiting & Raftery 2007](papers/pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf) (proper scoring rules) |
| 4 | **Computational floor** | Agent can't execute the math the choice requires | Novel for v0; partial precedent in code-eval literature |
| 5 | **Meta-cognitive** | Agent's confidence is uncalibrated (stated ≠ realized accuracy) | [Yamin et al. 2026](https://arxiv.org/abs/2602.06286) (belief coherence); [Chadwick 2025](papers/pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) (Dutch books); [Zhu & Griffiths 2024](https://arxiv.org/abs/2401.16646) (incoherent probability judgments) |

**Axis 5 footnote — calibration vs. coherence as complementary, not redundant.** Following Andrews 2026's framing, we treat *calibration* ([Guo et al. 2017](https://arxiv.org/abs/1706.04599); [Gneiting & Raftery 2007](papers/pdfs/gneiting_raftery_2007_strictly_proper_scoring_rules.pdf)'s proper scoring rules) and *coherence* (de Finetti / Dutch-book diagnostics) as **complementary** properties. Calibration asks whether predicted probabilities match empirical frequencies — it requires ground-truth outcomes and operates event-by-event. Coherence asks whether stated probabilities are internally consistent — it requires no ground truth and operates across multiple related assessments. A model can be well-calibrated on many events yet incoherent across them, or coherent yet poorly calibrated. AERead's Axis 5 reports both signals separately: calibration error against the held-out validation set (Layer 3 outcomes), and coherence violations under Dutch-book / proper-scoring-rule probes (no ground truth needed).

**Methodological gotcha — strict propriety for the leaderboard score.** Gneiting & Raftery 2007 establishes that a leaderboard score (which models are incentivized to maximize) must use a **strictly proper** scoring rule, otherwise it can be gamed by deliberate miscalibration. Expected Calibration Error (Guo et al. 2017) is the field-standard *diagnostic* metric but is **not strictly proper** — it can be lowered by shifting probability mass away from extreme bins without improving the underlying forecast. AERead therefore uses **Brier score (discrete events) and Continuous Ranked Probability Score / CRPS (continuous emissions)** for the leaderboard headline, both of which are strictly proper per Gneiting & Raftery's §3-§4. ECE + reliability diagrams remain on the diagnostic page for interpretability, but they do not enter the ranking.

Each axis has a distinct intervention mechanism:
- **Axis 1**: substitute beliefs / reveal state and rerun
- **Axis 2**: present counterfactual choice triplets and check axiom violations
- **Axis 3**: hold out test decisions, refit, compare predictive accuracy
- **Axis 4**: substitute the computational quantity with a closed-form answer
- **Axis 5**: elicit confidence + compare to realized accuracy for calibration (Brier score on held-out events; ECE + reliability diagrams for diagnostic visualization); run Dutch-book + money-pump constructions (Chadwick 2025) and probabilistic-identity probes (Zhu & Griffiths 2024) for coherence (no ground truth needed)

Cross-decomposition (Axis 1 × Axis 2, etc.) produces an attribution matrix with main-effect cells + pairwise interaction cells + residual. **Whether main effects explain a high fraction of the per-(model, task) gap (target: > 80% across v0 Layer 3 use cases) is an empirical hypothesis to be validated, not an assumption.** Interactions between axes are expected (e.g., calibration depends on whether the agent has the relevant information; computational-floor failures can masquerade as inconsistent preference) — the factorial design measures these rather than assuming them away.

### Relation to the diagnostic-and-correction literature

A growing body of work documents LLM rationality violations: [Betz & Richardson 2023](https://doi.org/10.1371/journal.pone.0281372) (probabilistic coherence as an epistemic-agent property; with a training-step correction), [Chen et al. 2023](https://arxiv.org/abs/2305.12763) (emergence of economic rationality), [Hagendorff et al. 2023](https://arxiv.org/abs/2212.05206) (thinking-fast-and-slow patterns), Zhu & Griffiths 2024 (incoherent probability judgments), Chadwick et al. 2025 (Dutch-book / money-pump diagnostics + post-processing correction), [Wen 2025](https://arxiv.org/abs/2501.18190) (persona-degrades-GARP), and [Qiu et al. 2026](https://arxiv.org/abs/2503.17523) (Bayesian-teaching training corrections). AERead's contribution relative to this literature is the **integrative** stance: rather than documenting one violation type at a time, the 5-axis taxonomy organizes all of them into a single attribution framework anchored on Andrews 2026's representation-theorem "if and only if" guarantees — if the per-axis penalty terms can be driven to zero, the representation theorems imply that there must exist a prior + utility + computational policy + calibration map that fully explain the model's behavior. The diagnostic page is what makes that attribution legible.

#### What these papers say about the diagnostic-framework challenge

These papers each *explicitly* discuss whether their diagnostic / correction approach works and what challenges remain. The challenges they admit cluster into a tight set — and the cluster maps onto the design constraints AERead is built to satisfy:

| Challenge admitted in the literature | Source | AERead's design response |
|---|---|---|
| **Single-domain validation** — each paper tests one axis in one domain | Betz (synthetic corpora), Zhu-Griffiths (weather + politics), Chadwick (synthetic preferences), Mazeika (preference elicitation only) | The collection-of-use-cases framing (Layer 3: C1 persona-fit + C2 price-aware product selection + v2 D2 bargaining + D3 agentic vendor selection) demonstrates portability of the same Eq. 4 decomposition across non-bargaining domains |
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

This page is the Tier 2 audit deliverable surface: when a financial firm asks "what's wrong with our deployed Claude agent?" the answer is one of these.

## Five methodological commitments

Each citation-anchored:

1. **Descriptive measurement, not normative ranking.** Higher composite scores ≠ better-aligned. *Andrews 2026 §7.*
2. **Measurement-model pluralism.** 4-6 competing models per axiom; report Bayesian posterior. *Echenique 2021 / Davis-Stober.*
3. **Judge-free by construction.** No LLM evaluates another LLM. All three anchor papers (TERMS-Bench May 2026; Revealed Rationality Feb 2026; EconEvals March 2025) independently adopted this. *TERMS-Bench / EconEvals / QEDBench.*
4. **Context-conditional axiomatization.** Personas degrade axiom compliance; this is a measurable dimension, not an assumption to control. *Wen 2025.*
5. **Cross-layer attribution + oracle-gap decomposition.** What turns scores into actionable signals.

## Adoption commitment: plug-and-play usability

Plug-and-play is an **adoption** commitment, not a methodology commitment — separate from the five above. Adoption traction analysis (25 benchmarks studied) found that no benchmark > 200 cites lacks (a) a live submission leaderboard with auto-scoring, (b) a frontier-lab model-card commitment, and (c) ≤ 5-minute clone-to-first-output. Therefore AERead is designed for:

- Zero-code task contribution via YAML
- One-line evaluation: `pip install aeread && aeread evaluate --model claude-opus-4-7 --task all`
- Three submission paths (web form / Colab / PR) for differing technical comfort levels
- Integration AS lm-evaluation-harness task family — so labs already running `lm_eval` have us installed automatically
- Cache layer never invalidates — reviewer reproducibility is a hard guarantee

## What this is not

- It is not a normative test of "rationality." Higher AERead scores ≠ better-aligned models.
- It is not a substitute for safety / hallucination / RAG benchmarks. It is the rationality dimension that those benchmarks do not measure.
- It is not a single-number leaderboard. It is a fingerprint along multiple axes, and the diagnostic page is the load-bearing artifact.
- It does not claim to invent the decomposition methods. Each pillar is an extension of an existing piece of literature; the integration is the novel contribution.
