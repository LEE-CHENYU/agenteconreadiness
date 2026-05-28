# AERead methodology — 3-layer pipeline + 5-axis failure taxonomy

This is a condensed methodology overview. The full master plan lives in the implementation repo; this document describes the conceptual architecture that should travel with the proposal.

> **Citation links.** Every paper named below has a clickable link in [`papers/links.md`](papers/links.md) — public URL where one exists, or PDF in [`papers/pdfs/`](papers/pdfs/) where it does not. Inline links below are first-occurrence only.

## The thesis in one paragraph

LLM agents are being deployed for economic decisions — procurement, pricing, negotiation, investment, vendor selection. Whether they satisfy the rationality assumptions those use cases presuppose has not been validated at scale. AERead is the integrated benchmark: a 3-layer revealed-preference pipeline (existence → identification → predictive validity) cross-cut by a 5-axis failure taxonomy (information, consistency, calibration, computational floor, meta-cognitive). The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed.

## Critical methodological questions (open Q&A)

These are the open methodological questions AERead must address for major-lab adoption + methodology-paper acceptance. The answers below are **working positions, not closed claims** — engagement from collaborators, reviewers, and frontier-lab researchers is invited on all six.

### Q1 — How does AERead prevent overfitting + function misspecification?

Two distinct risks: (a) overfitting to the v0 task set / chosen functional classes; (b) misspecifying the rationalizing utility (Andrews 2026 §3 non-identification critique — representation theorems guarantee existence, not unique identification).

**Defenses in place**:
- **Predict-then-validate** Layer 3 (train/test split, fixed seed, immutable manifest, held-out predictions; the headline score is best-fitting class's held-out accuracy, not in-sample fit)
- **Multi-class robustness** — fit all 5 candidate functional classes (KT prospect '79, CRRA, CARA, cumulative prospect TK '92, Kelly-Markowitz); report Bayesian posterior over classes
- **Measurement-model pluralism** (commitment #2) — 4-6 competing measurement models per axiom; Bayesian posterior over them; never a single point estimate
- **Cache layer never invalidates** + signed ScoreRecords → contamination becomes detectable from public cache hashes
- **Locked held-out test set** + bootstrap confidence intervals + model/prompt-version hashes
- **Anti-shortcut audits** (per Q5 below): option order, text length, brand, marketing positivity — none should predict the answer at contributor-submission time
- **OOD splits** mandatory per game: dev → hidden IID → axis-OOD → compositional → far-OOD → fresh
- **Hold out dimensions, not just examples**. Splits hold out entire generative axes — product domain (chairs in dev → laptops + SaaS in OOD), buyer profile (budget-sensitive in dev → committee-compromise in OOD), language template (clean spec sheets in dev → noisy review snippets in OOD), qualitative feature (durability in dev → vendor-lock-in in OOD), utility regime (price-dominant in dev → constraint-dominant in OOD). A model learning "AERead-specific heuristics" rather than transferable economic reasoning fails the cross-axis tests.
- **Overfit-bot baseline** — train a small model or rule-based agent directly on the public dev generator; report its hidden-IID + hidden-OOD scores; any frontier LLM with the same public-vs-hidden gap pattern as the overfit bot is exhibiting benchmark exploitation, not general capability
- **Rotating benchmark seasons** — v0.5+ ships a new hidden eval set every 6 months (new domains, new templates, new utility regimes); per-season scores + cross-season stability both reported; static-leaderboard ageing is a known failure mode of every benchmark we want to avoid
- **Public-hidden gap reporting** as a first-class benchmark-overfitting diagnostic: leaderboard rows show `public_dev_score`, `hidden_IID_score`, `hidden_OOD_score`, and `transfer_ratio = S_OOD / S_IID`. A model scoring 0.92 on public but 0.61 on hidden OOD is exposed by the report itself — no manual audit needed
- **Generalization Index** as composite leaderboard score (a *possible* aggregation, weights subject to community calibration): `GI = 0.20·S_IID + 0.25·S_AxisOOD + 0.25·S_CompositionalOOD + 0.20·S_FarOOD + 0.10·S_Counterfactual − Penalties`. Penalties include hard-constraint violations, dominated choices, paraphrase instability, marketing susceptibility, and the public-hidden overfit gap

**Open**: (a) posterior concentration across functional classes is itself an empirical finding — concentration is a publishable generalization claim, diffusion is a methodological caveat to surface; (b) the Generalization Index weights are an empirical question — the methodology paper will calibrate them against frontier-lab feedback rather than asserting them.

### Q2 — How does AERead evaluate quantitative features?

Two distinct sub-problems hide inside this question: (a) **scoring discipline for genuinely numeric outcomes** (dollar surplus, oracle gaps, predicted probabilities) and (b) **scoring discipline for qualitative product/state features** that are often presented as numeric but shouldn't be (a hidden `durability = 0.82` in a procurement task is fake precision — the model is being scored on whether it recovers the generator's arbitrary encoding scheme, not whether it made a good decision).

#### (a) Numeric outcomes — strict-propriety + bootstrap

For genuinely numeric outcomes (Layer 3 predictive validity, dollar surplus, oracle gap):
- **Brier score** (strictly proper) for discrete events — leaderboard headline
- **Continuous Ranked Probability Score (CRPS)** for continuous emissions — leaderboard headline
- **MAE / Spearman / Kendall** for point predictions and rank correlations
- **ECE + reliability diagrams** (Guo 2017) for diagnostic visualization only — **NOT for leaderboard ranking** (ECE is not strictly proper per Gneiting-Raftery 2007; can be gamed)
- **Choice-agreement rate** for discrete decisions
- **Direct dollar surplus** when measurable (procurement: cost paid vs LP-optimal; pricing: revenue captured vs revenue-maximum; matching: stable-match efficiency)
- **Counterfactual delta via oracle policy**: "what would the Bayes-optimal policy have earned given this state?"
- **Surplus efficiency normalized 0-1** (TERMS-Bench SE⁺ pattern)
- **Bootstrap confidence intervals** on every reported metric

#### (b) Qualitative features — structured states + ordinal labels, never hidden cardinal truth

For procurement-style cases where product attributes (durability, comfort, style fit, assembly difficulty) are qualitative, AERead **does not** evaluate by hidden cardinal truth (`durability = 0.82`). Instead:

**Qualitative-feature scoring discipline**:
- **Structured qualitative states**, not hidden 0-1 scalars: `{durability_evidence: "strong positive", seat_feel: "firm", assembly_friction: "moderate"}`. The generator starts from a **qualitative evidence bundle** (concrete review/spec snippets) and emits product text from the bundle — NOT from a hidden scalar reverse-engineered into text.
- **Ordinal labels for directional features** (`durability: weak < mixed < strong`; `assembly_friction: easy < moderate < hard`); **categorical labels for non-directional features** (`style: minimalist / executive / industrial / playful`). Non-directional feature value depends on buyer fit, not feature value alone.
- **Two-stage scoring**:
  - **Stage 1 (qualitative interpretation)** — diagnostic score: did the model infer the right qualitative category? did it recognize mixed evidence? did it avoid turning marketing fluff into evidence? did it distinguish property from value?
  - **Stage 2 (buyer-specific procurement choice)** — primary score: given the inferred qualitative state, did the model map it to a decision appropriate for a particular buyer profile? The same product may be optimal for buyer A and dominated for buyer B.
- **Four case types**: (1) **constraint cases** (objective correctness — model violates a hard budget/deadline = fail); (2) **dominance cases** (one option strictly better on every relevant dimension — clear pass/fail); (3) **pairwise tradeoff cases** (model must flip choice across buyer profiles — tests buyer-conditional reasoning); (4) **ambiguous cases** (multiple defensible choices — partial credit, never forced single-truth).
- **4-tier optimality classification**: `robust optimal / acceptable / weak but defensible / dominated or constraint-violating`. Points map to `1.0 / 0.75 / 0.4 / 0.0` (with negative or auto-fail for constraint violation). Partial credit is the design feature, not a workaround.
- **Pairwise-regret scoring**: count how many clearly superior alternatives the chosen product loses to. Reported alongside primary score.
- **Robust utility, not one arbitrary utility function**: define a **family of plausible utility weight vectors** per buyer profile; classify products as `robust_best / robust_top_tier / sensitive / dominated` by their performance across the family. Model isn't heavily penalized for choosing a `robust_top_tier` product instead of the exact numeric winner — only for choosing dominated or constraint-violating options.

#### Statistical-reproducibility framework

(Sister repo proposal §9.3 (D) Phase-0 deliverable for Yuecheng): immutable split manifests, seed + scorer-version + measurement-model-set-version hashing, factorial intervention design with main + interaction effects + residual reported.

**Open**: (a) how should heterogeneous quantitative features aggregate into a composite leaderboard score without false precision? TERMS-Bench's 7-orthogonal-axis sortable table (terms-bench.github.io) is the current design precedent — AERead extends to a 5-axis radar + GI composite (see Q1 Generalization Index). (b) Where does the qualitative/numeric boundary fall for *new* Layer 3 cases? Submitters declare per-feature scoring type at submission time; the framework rejects cases that try to score a qualitative feature as a hidden cardinal scalar.

### Q3 — How do the tests function as RL environments providing generalizable training signals?

The detailed answer is **the AERead-env design spec** ([`aeread_env_design.md`](aeread_env_design.md)) — an OpenSpiel-compatible benchmark substrate. The short answer:

- **Oracles produce both dense scalars (reward) and decompositions (diagnostic)** — AERead environments plug into RLHF/DPO loops; resulting models can be diagnosed by AERead at evaluation time
- **Axiom violations as RL reward signals** (Andrews 2026 training-time penalty mechanism): de Finetti / Afriat / SARSEU penalties are LP-checkable in polynomial time, label-free, zero iff the data are rationalizable — natural auxiliary loss
- **Pre-registered factorial intervention design**: each game declares the interventions it admits (state reveal / belief substitution / paraphrase / option-set perturbation); RL practitioners compose training data principled
- **Anti-shortcut audits prevent reward-hacking**: RL can't game spurious correlates (option order / brand / marketing positivity) because the framework tests for them at contributor-submission time
- **OOD splits give external-validity signal**: train on dev; report on hidden IID / axis-OOD / compositional / far-OOD; researchers see whether their RL improvements actually generalize

**Training-signal infrastructure**: AERead's per-axis penalties are designed to plug directly into model training, not just into evaluation. Four prior-art mechanisms anchor the integration surface — Andrews 2026 (training-time penalty; label-free axiom loss), Chadwick 2025 (inference-time IMDC; Dutch-book post-correction), Qiu 2026 (supervised trace; Bayesian-teaching mimicry), Betz & Richardson 2023 (self-supervised consistency training; probabilistic coherence). AERead's evaluation becomes a direct input to RLHF/DPO loops — this is what makes per-axis scores load-bearing for frontier labs running their own fine-tuning, not just citing the methodology paper after the fact.

**Training-environment vs final-evaluation discipline**. A critical honesty principle (per the TERMS-Bench overfitting analysis in [Zhang et al. 2026](papers/links.md)): once a benchmark becomes a training target, the published score is **no longer an unbiased out-of-sample evaluation**. The right distinction:

- **AERead as a training environment** (lab uses public dev set to fine-tune): **acceptable** + encouraged — that's the Tier 4 infrastructure value
- **AERead as final evaluation after training on it** (claim "model X scores 0.87 on AERead" using only the public dev distribution): **contaminated** — should not be cited as out-of-sample evidence

AERead enforces this by:
- **Public dev / hidden IID / hidden OOD / fresh-season splits** (see Q1) — published model-card scores must report hidden splits separately from public dev
- **Public-hidden overfit gap** reported per model — if a model's `public_dev_score − hidden_IID_score` exceeds the overfit-bot baseline gap, the methodology paper flags it explicitly
- **Submitter discipline**: any model card citing AERead must declare what splits the model was trained on (training distribution, RL feedback signal, dev-set fine-tuning) — provenance is the citation contract

**Open**: which axes (information / consistency / calibration / computational floor / meta-cognitive) most cleanly produce RL training signal? AERead's per-axis scoring is the empirical test — labs running the benchmark can compare per-axis reward effectiveness in their own fine-tuning runs and feed the result back into the next methodology-paper revision.

### Q4 — How much of the per-(model, task) gap do Layers 1 + 2 explain? What's the residual?

This is **the central empirical hypothesis of the methodology paper §3 contribution**. The honest answer: we don't know yet — that's what the benchmark measures.

**Working hypothesis**: For frontier models on simple use cases, Layer 1 (existence — axiom compliance) + Layer 2 (identification — within-class utility fit) explain **~50-70% of the Layer 3 predictive-validity gap**. The remaining **~30-50% residual** is what the 5-axis taxonomy decomposes into:
- Axis 1 Information (hidden-state knowledge gaps)
- Axis 4 Computational floor (capability gaps masquerading as preference)
- Axis 5 Meta-cognitive (calibration vs coherence; stated-vs-revealed mismatch)
- Cross-axis interactions (calibration depends on information; computational floor can masquerade as inconsistency — the factorial design measures these)

This split mirrors a finding from the diagnostic-and-correction literature (Andrews §7, Chadwick §Future Work, Zhu-Griffiths 2024 footnote): **coherence is necessary but not sufficient**. Layer 1+2 measure coherence-style properties; Layer 3 measures the sufficient predictive-validity claim.

**Falsification criteria** (pre-registered before cross-model eval):
- If Layer 1+2 explain > 80% of the gap → 5-axis decomposition adds incremental value but isn't load-bearing → simplify the framework
- If Layer 1+2 explain < 50% → the 5-axis residual is doing most of the explanatory work → the diagnostic contribution becomes the headline
- If between (50-80%, working hypothesis) → AERead's full architecture is empirically justified

**Open**: this is exactly the empirical claim the methodology paper will validate. Pre-registration is what makes the §3 contribution testable, not assumed.

### Q5 — Should we build an OpenSpiel-like general environment for later contribution?

**Yes — but as a thin, OpenSpiel-compatible economic-benchmark substrate, not a full game-engine replacement.** Full design spec at [`aeread_env_design.md`](aeread_env_design.md).

**The thesis**: OpenSpiel already covers generic game substrates (n-player, zero-sum/cooperative/general-sum, one-shot/sequential, perfect/imperfect-information). AERead's contribution layer is the **economic-agency layer on top**: oracle decomposition, qualitative evidence, revealed-preference diagnostics, utility/belief calibration, OOD benchmark design.

**MVP scope** (4 structurally diverse games, not 20):
- **ProductProcurementGame** — single-agent, one-shot, qualitative evidence; tests multi-attribute buyer fit
- **NegotiationGame** — two-agent, sequential, hidden type; tests strategic belief + concessions
- **VendorSelectionGame** — single-agent, risk/uncertainty, supplier evidence; tests reliability + risk tradeoffs
- **PricingCompetitionGame** — multi-agent/repeated or market simulator; tests market feedback + adaptive policy

**10 hard constraints** locked into the framework (full details in [`aeread_env_design.md`](aeread_env_design.md)):
1. Symbolic ground state exposed separately from text observations
2. Legal-actions + invalid-action penalty taxonomy
3. At least one oracle or reference policy per game (no oracle, no benchmark)
4. At least one diagnostic intervention per game (baseline + paraphrase + constraint-explicit + state-revealed)
5. Declared OOD axes per game (domain / buyer_type / language_template / utility_regime / risk_model / opponent_policy)
6. Anti-shortcut audits before inclusion (option order / product_id / text length / price / brand / marketing positivity)
7. Seedable + reproducible (no uncontrolled randomness)
8. Public + private split separation (train generator / dev / hidden certification / hidden OOD)
9. Decomposable metrics (every game returns outcome_score + constraint_violations + oracle_gap + per-axis diagnostic_breakdown — never a single opaque number)
10. Declare what the game is NOT testing (prevents overclaiming)

**Naming**: not "OpenSpiel for economic games" (too broad). Position as "**OracleDecomposition Environments for LLM Economic Agency**" — a lightweight OpenSpiel-compatible benchmark layer with oracle decomposition, qualitative evidence, revealed-preference diagnostics, and OOD generalization tests.

**Open**: when does this ship relative to v0? Likely **v0.5** — after methodology paper draft + first 2 v0 use cases land. The 4-game MVP becomes a v1 contribution that reinforces the "AERead is a benchmark substrate, not a single benchmark" framing.

### Q6 — How does AERead operationalize "emergence" claims?

Background: the original emergent-abilities literature (Wei et al. 2022) defined emergence as abilities absent in small models + present in large ones. Schaeffer-Krueger 2023 + follow-on work argued that some apparent emergence is an artifact of **discontinuous metrics** (pass/fail thresholds) rather than genuine qualitative jumps in model behavior. AERead must claim emergence carefully — overclaiming on a fragile metric is exactly the citation-credibility risk frontier-lab reviewers flag.

**AERead's conservative operational definition**. A capability is "emergent-like" only when ALL FIVE criteria hold:

1. **Floor effect at smaller scales** — smaller models perform near random or choose dominated options on the capability
2. **Sharp improvement at larger scales** — larger models improve substantially (not just incrementally) on this capability
3. **Multi-metric coherence** — the improvement appears across multiple metrics simultaneously (e.g., choice-agreement rate + robust-optimal rate + transfer ratio + paraphrase stability), not only on exact-match accuracy
4. **OOD transfer** — the improvement transfers to held-out domains (chair → laptop → SaaS procurement), not just hidden-IID instances from the same distribution
5. **Counterfactual robustness** — the improvement survives paraphrase + preference-flip + marketing-injection + constraint-tightening tests; gains that collapse under counterfactual perturbation are likely overfitting

**A weaker claim that frontier-lab reviewers will reject**: "Model X got 78% exact-best-choice accuracy on AERead-Procurement." This proves nothing about emergence — it could be benchmark exploitation, ceiling effects, or fragile metric thresholding.

**Anti-discontinuity discipline**: AERead reports **continuous and ordinal measures** alongside any binary pass/fail metric:
- Utility-regret distribution (not just exact-match)
- Robust-top-tier rate (not just exact-optimal)
- Dominated-choice rate (counterpart to optimal-choice rate)
- Pairwise preference-violation count (continuous)
- Paraphrase instability (continuous variance)
- Transfer ratio (continuous OOD vs IID)
- Calibration error (continuous)

When a larger model improves, the methodology paper asks: is this a real jump across multiple continuous metrics, or only an artifact of crossing a pass/fail threshold on one fragile metric?

**Item-response-theory extension (v1+)**: a deeper diagnostic per Andrews / Davis-Stober Bayesian-mixture precedent. Estimate per-item difficulty + per-item discrimination + per-model ability parameters via `P(success_{m,i}) = σ(θ_m − β_i + γ_q·capability_tags_i)`. This identifies which items separate strong from weak models (high discrimination), which capabilities are actually hard, whether the benchmark saturates, and whether larger models improve smoothly or sharply. IRT is the v1+ rigor extension; v0 uses simpler bootstrap intervals.

**Open**: AERead's per-capability scaling curves across model families are the empirical test of whether economic-decision capability is emergent-like or smoothly scaling. The methodology paper reports both views and lets the data settle which framing fits. Frontier-lab reviewers interested in emergence vs scaling-law framings are invited to engage on this question explicitly.

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

- **C1 Persona-fit**: hidden state = principal's IRL-fit utility coefficients (α_kelly, δ_turnover); oracle = closed-form Kelly-Markowitz. **Caveat**: 13F filings are an approximate revealed-preference proxy (long positions only, quarterly delay; shorts + derivatives not required) — v0 treats C1 as an approximate-RP case study with assumption sensitivity tests, not clean ground truth.
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

- **On the open methodology Q&A** (above): the six questions are real research questions; reviewers, frontier-lab researchers, and collaborators are invited to challenge the working positions before the methodology paper draft circulates
- **On the 5-axis taxonomy**: if a sixth axis is needed (or a current axis collapses into another), the pre-registered factorial design will reveal it — pre-registration commits us to publishing the finding regardless of direction
- **On the OracleDecomposable abstraction**: counterexamples — economic decisions that don't fit the (hidden state + controllable simulator + oracle policy + scalar utility) interface — strengthen the methodology paper by exposing scope limits. Submit them.
- **On Layer 3 use cases**: the open candidate pool ([`layer3_candidates.md`](layer3_candidates.md)) invites external researchers to propose new cases via the value × testability matrix; high-value + high-testability gaps (especially the empty top-right cell) are explicitly open contribution surface
- **On the OpenSpiel-compatible substrate** ([`aeread_env_design.md`](aeread_env_design.md)): external contributors can add games via the 10-hard-constraint submission API once the substrate ships (v0.5)
- **On the falsifiability of §3** ([proposal §3](proposal.md#3-novel-methodology-contribution-5-axis-failure-taxonomy--oracledecomposable-generalization)): the headline "main effects explain > 80% of variance" claim is pre-registered with falsification criteria — reviewers can challenge the threshold or the design before cross-model evaluation begins

**Channel for engagement**: contact details in [`proposal.md` §15](proposal.md). Before methodology-paper preprint circulation, we will invite reviewer engagement from major-lab safety + economics-of-AI researchers — pre-registration is the artifact that makes the §3 claim citable rather than asserted.

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
