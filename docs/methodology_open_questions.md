# AERead methodology — open methodological questions (Q&A)

> Working positions on the 14 open methodological questions for major-lab adoption + methodology-paper acceptance. **Not closed claims** — engagement invited on all fourteen. Topic-index table for navigation; bodies below; "Open:" line ends each Q.
>
> Framework descriptions (3-layer pipeline + 5-axis taxonomy + OracleDecomposable + methodological commitments) are in [`methodology.md`](methodology.md).

## Topic index

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
| **Q11** | Gate vs grade: rationality and persona-fidelity — one problem or two? | One pipeline, gate → grade; two scored stages, explicit dependency. Rationality (gate) is a floor for frontier models; persona-fidelity (grade) is the discriminator + alignment-relevant signal. Separate scoring forced by opposite failure-sign. Falsifiable. |
| **Q12** | Operationalizing stress as a cross-cutting axis | Keep the decomposition; add stress orthogonally; report a degradation curve + cliff edge, not pass/fail; co-measure gate+grade per (persona, stress) condition. Saturation is conditional (benign-only) — Andon falsifies "gate is a structural floor". |
| **Q13** | Adversarial co-evolution as judge-free stress-discovery | Yes — attacker discovers defender-degrading scenarios, frozen into a corpus (generation, not runtime); reward oracle-computed not LLM-judged (→ OracleDecomposable); Persona-Collapse Arena first; v0.5+/substrate. |
| **Q14** | What training signal AERead emits — recover competence without reviving misbehavior | The signal is the oracle-decomposed **process** reward, not the scalar score. Outcome (surplus) reward revives the deception/collusion safety removed (the trap); process reward targeted at the Δ-attributed deficit recovers competence alignment-safely. Pre-registered falsifier: process-reward vs outcome-reward model, read out the deception axis. v1+; positioning decision; methodology-framed. |

---

### Q1 — How does AERead defend against function misspecification?

Andrews 2026 §3 non-identification critique: representation theorems guarantee existence, not identification — different functional classes (CRRA / CARA / KT prospect / CPT / Kelly-Markowitz) can rationalize the same data with different parameters. AERead's response = **within-class identification with explicit class-uncertainty reporting**.

**Defenses**:
- **Predict-then-validate**: train/test split + fixed seed + immutable manifest; headline score = best-fitting class's held-out accuracy
- **Multi-class robustness**: v0 fits 3 functional classes (KT prospect '79 + CRRA + Kelly-Markowitz); reports Bayesian posterior. v0.5+ adds CARA + cumulative prospect TK '92
- **Measurement-model pluralism**: 4-6 competing measurement models per axiom; Bayesian posterior; never a single point estimate

**Open**: posterior concentration is itself an empirical finding — concentration is a publishable generalization claim; diffusion is a caveat to surface.

### Q2 — How does AERead evaluate numeric features?

Genuinely numeric outcomes (dollar surplus, oracle gap, predicted probabilities) where the ground truth IS a number.

**Discipline**:
- **Brier / CRPS** — strictly proper; leaderboard headline
- **MAE / Spearman / Kendall** — point predictions + rank correlations
- **ECE + reliability diagrams** (Guo 2017) — diagnostic visualization only, NOT leaderboard (ECE not strictly proper per Gneiting-Raftery 2007; can be gamed)
- **Direct dollar surplus** when measurable; **counterfactual delta** via oracle policy when not
- **Bootstrap CIs** on every reported metric

**Open**: how to aggregate heterogeneous numeric features into composite without false precision — TERMS-Bench's 7-orthogonal-axis sortable table is the design precedent.

### Q3 — How does AERead score qualitative features without fake numeric precision?

A hidden `durability = 0.82` in a procurement task is fake precision — the model is being scored on whether it recovers the generator's arbitrary encoding, not whether it made a good decision.

**Discipline**:
- **Structured qualitative states**, not hidden 0-1 scalars: `{durability_evidence: "strong positive", seat_feel: "firm"}`. Generator starts from a qualitative evidence bundle (review/spec snippets) and emits text from the bundle — NOT from a hidden scalar
- **Ordinal labels for directional features** (`durability: weak < mixed < strong`); **categorical labels for non-directional** (`style: minimalist / executive / industrial`)
- **v0**: single-stage scoring with single declared utility-weight vector per buyer; 4-tier optimality classification (`robust optimal / acceptable / weak / dominated`) mapping to 1.0 / 0.75 / 0.4 / 0.0 (constraint violation = auto-fail)
- **v0.5+**: two-stage scoring (qualitative-interpretation diagnostic + buyer-specific primary) + robust utility family (set of plausible weight vectors per buyer)
- **Pairwise-regret scoring** (count clearly-superior alternatives missed) reported alongside primary
- **Four case types**: constraint (objective correctness) / dominance (clear pass-fail) / pairwise tradeoff (test buyer-conditional flip) / ambiguous (partial credit, never forced single-truth)

**Methodological anchors**: discrete choice experiments (Louviere 2000), conjoint analysis (Marley & Louviere 2005), MAUT (Keeney & Raiffa 1976), robust optimization (Ben-Tal & Nemirovski 2002), vignette experiments (Atzmüller & Steiner 2010).

**Open**: contribution-time gate — submitters declare per-feature scoring type; framework rejects cases trying to score qualitative features as hidden cardinal scalars.

### Q4 — How does AERead's generalization battery work in detail?

Split design + benchmark-integrity infrastructure that distinguishes "model learned transferable economic capability" from "model learned AERead-specific heuristics."

**Splits, mandatory per game** (Q6 names them AERead-Train/Dev/Cert as citation-contract tiers):

| Split | Visibility | Purpose | v0 status |
|---|---|---|---|
| **dev** | public, with answers | training-generator development | v0 |
| **hidden IID** | private | non-contamination baseline | v0 |
| **axis-OOD** | private | controlled generalization (1 axis held out) | v0 (1 axis only) |
| **compositional-OOD** | private | systematic generalization | v0.5+ |
| **far-OOD / fresh seasons** | private, rotating | benchmark-overfitting resistance | v1+ if traction |

**Hold out dimensions, not just examples** — generative axes include product domain, buyer profile, language template, qualitative feature, utility regime, constraint type, strategic structure, action space, time horizon. v0 picks 1 axis per game; v0.5+ expands.

**Benchmark-integrity foundations**:
- Cache layer never invalidates → contamination detectable from public hashes (signed ScoreRecords v0.5+)
- Locked held-out test set + bootstrap CIs + model/prompt-version hashes
- Anti-shortcut audits (option order / text length / brand / marketing positivity) at submission time
- Anti-discontinuous-metric reporting — alongside any pass/fail metric, AERead reports continuous + ordinal measures

**Counterfactual battery**:
- **v0** (mandatory 2): paraphrase-invariance + preference-flip
- **v0.5+** (adds 3): marketing-robustness, dominated-option, constraint-tightening

**Reporting**: leaderboard rows show `public_dev_score`, `hidden_IID_score`, `hidden_axis-OOD_score`, `transfer_ratio = S_OOD / S_IID`. **Deferred to v0.5+**: overfit-bot baseline; rotating seasons; Generalization Index composite; pairwise interaction matrix.

**Open**: deferred items pre-registered as v0.5+ commitments — reviewer engagement on priority order invited.

### Q5 — How do the tests function as RL environments providing generalizable training signals?

Four prior-art-anchored mechanisms make AERead's per-axis penalties usable as training signal:

| # | Mechanism | Prior-art anchor | v0 status |
|---|---|---|---|
| 1 | Training-time penalty (label-free axiom loss) | [Andrews 2026](papers/pdfs/andrews_2026_revealed_rationality.pdf) | **v0 ships penalty/scorer reference** (LP-checkable diagnostic; auxiliary-loss fine-tuning pipeline NOT in v0 — labs wire into their own training) |
| 2 | Inference-time correction (Dutch-book) | [Chadwick 2025](papers/pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) | Described; implementation defers to follow-up paper |
| 3 | Supervised trace mimicry (Bayesian-teaching) | [Qiu 2026](https://arxiv.org/abs/2503.17523) | Described; implementation defers to follow-up paper |
| 4 | Self-supervised consistency training | [Betz & Richardson 2023](https://doi.org/10.1371/journal.pone.0281372) | Described; implementation defers to follow-up paper |

v0 ships mechanism 1 only — simplest (LP-checkable, label-free), demonstrates the integration surface. Building all 4 implementations is months; isn't load-bearing for v0 §3 contribution. Mechanisms 2-4 land in a follow-up paper.

The overfitting risk when AERead is used as training signal is Q6.

**Open**: which axes (information / consistency / calibration / computational floor / meta-cognitive) most cleanly produce RL training signal? Labs running the benchmark compare per-axis reward effectiveness in their own fine-tuning runs.

### Q6 — What happens if AERead is used as a training signal — and how does AERead avoid being gamed?

Per the TERMS-Bench overfitting analysis ([Zhang et al. 2026](papers/links.md)): once a benchmark becomes a training target, the published score is no longer unbiased out-of-sample evaluation. AERead's defense: **tier-separation naming convention** auditable at the model-card level.

| Tier | Naming | Visibility | Acceptable use |
|---|---|---|---|
| **AERead-Train** | public training simulator + generators | fully public | Training models against AERead-style economic decisions |
| **AERead-Dev** | public fixed dev set | fully public | Reporting dev scores (clearly labeled as dev) |
| **AERead-Cert** | hidden IID + axis-OOD + compositional + far-OOD + fresh seasons | private | The score model cards should cite |

- AERead-Train + AERead-Dev as training envs: **acceptable + encouraged**
- AERead-Cert as final evaluation: **the only score frontier-lab model cards should cite**; a card claiming "scores 0.87 on AERead" using only AERead-Dev numbers is misleading

**v0**: docs-only convention + submission-instructions provenance contract. **v0.5+**: infrastructure enforcement (automated provenance verification; leaderboard auto-refusal of Dev-only "AERead scores"; signed-ScoreRecord verification).

**Open**: enforcement is the hard part — naming conventions only work if reviewers flag non-compliant model cards.

### Q7 — How much of the per-(model, task) gap do Layers 1 + 2 explain? What's the residual?

**The central empirical hypothesis of the methodology paper §3 contribution.** Honest answer: we don't know yet — that's what the benchmark measures.

**Per-domain working hypothesis**:

| Domain | Expected Layer 1+2 explanatory share | Dominant residual driver |
|---|---|---|
| Discrete-action procurement (v0 C2) | **60-75%** | Qualitative-evidence interpretation; marketing susceptibility |
| Continuous-action pricing (v0 C8) | **50-70%** | Posterior-computation failure (Δ_unc — agent's posterior from n=10 noisy sales evidence ≠ Bayes-optimal); continuous-action argmax under uncertainty (Δ_ctrl); round-number-price bias |
| Vendor selection (roadmap D3) | **55-75%** | Belief calibration; risk-preference functional-class disagreement |
| Portfolio / risk choice (C1 13F roadmap) | **50-70%** | Functional-class misspecification; opportunity-set mis-modeling |
| TERMS-like negotiation (roadmap D2) | **40-65%** | Strategic belief; opponent-type inference |
| Multi-agent markets (v0.5+) | **30-55%** | Equilibrium reasoning; computational-floor failures |
| Long-horizon agents (v1+) | **25-50%** | Long-horizon coherence; planning failures; reward-hacking |

**Safer headline claim**: *"In clean single-agent procurement, coherence + behavioral-representation diagnostics explain a majority of the oracle gap. In strategic and long-horizon games, additional belief / information / computation / policy diagnostics are necessary."*

**Falsification criteria** (pre-registered before cross-model eval, per domain):
- Layer 1+2 > 80% → 5-axis decomposition adds incremental value but isn't load-bearing → simplify
- Layer 1+2 < 50% → 5-axis residual does most of the explanatory work → diagnostic contribution becomes headline
- 50-80% (working hypothesis) → full architecture empirically justified

**Open**: the §3 contribution is this empirical claim. Pre-registration makes it testable, not assumed.

### Q8 — Should we build an OpenSpiel-like general environment for later contribution?

**Yes — but as a thin, OpenSpiel-compatible economic-benchmark substrate, not a full game-engine replacement.** Full design spec at [`aeread_env_design.md`](aeread_env_design.md).

OpenSpiel covers generic game substrates. AERead's contribution layer = the **economic-agency layer on top**: oracle decomposition, qualitative evidence, revealed-preference diagnostics, OOD benchmark design.

**Substrate MVP scope** (5 structurally diverse games — all in the post-v0-paper substrate follow-up paper, NOT v0.5+ of the first paper):
- ProductProcurementGame (C2) — discrete-action, qualitative evidence — **v0 first paper, game 1** (standalone, no substrate)
- SimplePricingGame (C8) — continuous-action, demand uncertainty — **v0 first paper, game 2** (standalone, no substrate)
- VendorSelectionGame (D3) — risk/uncertainty — v0.5+ first-paper extension (single-game; demoted 2026-05-28 from v0 game 2; structurally similar to C2)
- NegotiationGame — two-agent strategic — substrate-paper deliverable
- PricingCompetitionGame — multi-agent / repeated — substrate-paper deliverable

**10 hard constraints** locked into the framework — full details in [`aeread_env_design.md`](aeread_env_design.md).

**Naming**: position as "**OracleDecomposition Environments for LLM Economic Agency**" — not "OpenSpiel for economic games" (too broad).

**Open — sequencing**: the substrate is **NOT v0.5** — it becomes a separate post-v0-paper follow-up paper. v0 first paper ships 2 standalone games (no shared substrate). Building the 5-game MVP + 6-interface architecture is months of engineering; worth doing only after v0 establishes traction.

### Q9 — How does AERead operationalize "emergence" claims?

Schaeffer-Krueger 2023 argued that some apparent emergence is an artifact of discontinuous metrics (pass/fail thresholds) rather than genuine qualitative jumps. AERead must claim emergence carefully — overclaiming on a fragile metric is the citation-credibility risk reviewers flag.

**Conservative operational definition** — a capability is "emergent-like" only when ALL FIVE hold:

1. **Floor effect at smaller scales** — smaller models near random or choose dominated options
2. **Sharp improvement at larger scales** — substantial, not incremental
3. **Multi-metric coherence** — improvement across multiple metrics (choice-agreement + robust-optimal rate + transfer ratio + paraphrase stability), not only exact-match accuracy
4. **OOD transfer** — improvement transfers to held-out domains, not just hidden-IID
5. **Counterfactual robustness** — survives paraphrase + preference-flip + marketing-injection + constraint-tightening tests

**A weaker claim reviewers will reject**: "Model X got 78% exact-best-choice accuracy on AERead-Procurement." Could be benchmark exploitation, ceiling effects, or fragile metric thresholding.

**IRT extension (v1+)**: per-item difficulty + discrimination + per-model ability via `P(success_{m,i}) = σ(θ_m − β_i + γ_q·capability_tags_i)`. Identifies which items separate strong from weak models, whether the benchmark saturates, smooth vs sharp scaling. v0 uses simpler bootstrap intervals.

**Open**: per-capability scaling curves across model families are the empirical test of emergent-like vs smoothly-scaling. Methodology paper reports both views; data settles which framing fits.

### Q10 — Can AERead validate training-signal quality without training models ourselves?

**The most consequential v0 scope decision.** Honest framing: v0 ships **a scorer**, not **a validated training signal**.

**Three distinct claims about training signal**:

| Claim | Evidence type | v0 status |
|---|---|---|
| (1) Per-axis penalty is computable + LP-checkable | Theoretical (Andrews 2026 §2) | v0 ships; follows from theorems |
| (2) Frontier models with lower penalties exhibit better economic-decision performance | Observational (cross-model correlation) | v0 demonstrates (3-5 model cross-eval) |
| (3) Training with penalty as auxiliary loss *causes* improvement | Causal (training experiment) | v0 does NOT demonstrate by default |

**Cheapest credible causal experiment**: fine-tune Qwen 0.5B or 3B on a v0 use case (e.g., C2 trajectories); train baseline (no penalty) vs treatment (AERead Andrews-style penalty as auxiliary loss); evaluate on held-out AERead-Cert. Cost: ~$500-1K GPU + ~2-3 person-weeks (existing TRL / axolotl / open-instruct harness + custom loss).

**Three v0 options**:

| Option | Scope | Cost | v0 paper claims |
|---|---|---|---|
| **(A) Defer** to follow-up paper | scorer + observational only | $0 | Claims (1) + (2); causal claim is follow-up paper headline |
| **(B) Include in v0** | minimal Qwen-scale experiment | +3 weeks + ~$1K | Claims (1) + (2) + (3) for ≥1 task/model/mechanism. Substantially stronger paper. Needs SDE for training-loop integration. |
| **(C) Hybrid** — pre-register in v0; result lands shortly after | pre-register design; experiment runs Phase 2-3 | low upfront | v0 pre-registers; ~6-week post-v0 arxiv update reports result |

**Working recommendation: (C) hybrid** — avoids +3 weeks into v0 (already tight); pre-registration is the academic-credibility move; result lands in Phase-3 revision window (positive strengthens paper; null is *also* publishable). Contingent on Jingyi (or ops collaborator per §9.4) bandwidth.

**Open**:
- Worth +3 weeks + $1K, or sufficient with observational + pre-registered?
- Does Jingyi (or other ops collaborator) have bandwidth for training-loop integration?
- Qwen 0.5B (cheaper, less convincing) vs 3B (more convincing) — or staged?
- If causal claim *fails*, what's the revised paper framing? Scorer + observational evidence still ships.

### Q11 — Gate vs grade: should rationality and persona-fidelity be scored as one problem or two?

**Working position**: not two problems — **one pipeline, gate → grade**, with two separately-reported scores and an explicit dependency.

| Stage | Question | Score | Status for frontier models |
|---|---|---|---|
| Gate (Layer 1) | Does *some* utility rationalize the choices? | pass/fail floor | pass uniformly (table stakes) |
| Identification (Layer 2) | Fit that utility | machinery | — |
| Grade (Layer 3) | Does it match the configured/revealed principal + predict held-out? | graded headline | the discriminator |

**Why one pipeline, not two benchmarks**: the grade presupposes the gate — you cannot fit a utility to GARP-violating choices. The relationship is hierarchical, not parallel. The integrative artifact (gate → identification → grade + the deployment verdict) is the contribution; two standalone benchmarks ("a rationality benchmark" + "a steerability benchmark") would each read as derivative and would misrepresent the dependency.

**Why separate scoring is nonetheless forced**:
- **Opposite failure sign**: deviation from the generically-rational answer is a failure at the gate but a success at the grade (it is what a loss-averse principal wants). One number cannot encode both.
- **Different oracle structures**: the gate has a clean, computable, gameable oracle; the grade has a noisy revealed-preference oracle (IRL fit with estimation error) that is ungameable but requires predict-then-validate.
- **Two distinct failure modes**: incoherence (gate) vs coherent-but-unfaithful (grade) need different fixes; a single score hides which one a model has.

**Empirical motivation (preliminary; single-seed run corrected by N=20 bootstrap)**: across a toy battery spanning procurement, pricing (linear + logistic demand), auctions, matching, forecasting, repeated games, and a capacity-constraint recipe-trap, frontier models passed the gate uniformly — including the contamination probes designed to defeat textbook-retrieval. A standalone persona-maintenance probe was the only one to separate frontier models: configured to a persona whose acceptance threshold deviates from EV-rational, under N=20 bootstrap CIs both models are robustly steerable (steerability *magnitudes* overlap — the initial "weaker model collapses" reading was a single-gamble-grid artifact), and the discriminators that survive CIs are steering *stability* and *directional fidelity* (e.g. risk-seeking-persona fidelity is CI-disjoint between the two models). Both recovered full fidelity once the persona was restated per-decision or quantified — so the gap measures **steerability / default-stickiness, not capability**. Illustrative, not validated.

**Falsification (pre-registered)**: the "gate is a floor" position is falsified if frontier models systematically separate on gate-layer axioms beyond arithmetic noise; the "grade is the discriminator" position is falsified if frontier models do not separate on persona-fidelity under multi-seed evaluation using the per-persona fidelity metric (penalizes under- and over-steering, so separation cannot come from over-correction alone).

**Relation to Categories A/B/C**: Category A (classical axioms) is pure gate; Category C (persona-fit / IRL on revealed preferences) is pure grade; Category B (behavioral-economics parameters) is the hinge — "compute the behavioral value" is gate, "maintain a configured behavioral persona" is grade.

**Open**:
- Is the unified gate→grade framing stronger than a standalone steerability paper aimed squarely at the safety audience? (Positioning trade-off: integration + deployment-verdict framing vs faster single-audience hit.)
- Is persona separation (threshold spread) the right grade metric, or must the per-persona fidelity score (which penalizes over-steering) be the headline? Multi-seed CIs required either way.
- Does the "persona collapse under rationality pressure" finding replicate on the named-principal (13F-style) instrument, not just synthetic personas?

### Q12 — How should stress be operationalized as a cross-cutting axis?

**Working position**: rationality is a floor *at rest* but a cliff *under load*. **Keep the 3-layer decomposition; add stress as a dimension orthogonal to the layers** — do not restructure. For each (model, task), report a **degradation curve** (gate-compliance + grade-fidelity vs stress level) and a **cliff edge**, not a pass/fail point.

Stress dimensions with direct evidence the gate degrades:

| Stress | Evidence |
|---|---|
| Long horizon | [Andon Vending-Bench](https://andonlabs.com/blog/opus-4-8-vending-bench): Opus 4.8 scam-supplier / non-convergent-loop / price-comparison failures at 20M tokens |
| Compute budget | pricing toy at constrained reasoning budget → collapse; at adequate budget → near-oracle |
| Multi-agent / strategic | repeated-pricing control-gap collapse (fails to sustain cooperation) |
| Sequential-inference load | multi-period posterior-integration gap |
| Adversarial / meta-framing | meta-guidance (axiom prompt, population prior) degrading behavior; [Tak et al. 2026](https://arxiv.org/abs/2601.22329) — reasoning-mode rational-choice gains carry heightened sensitivity to affective/emotional steering (stress-sensitive rationality, not generic adversarial reversibility) |
| Persona-conditioning | [Wen 2025](https://arxiv.org/abs/2501.18190) — personas degrade GARP |

**Why keep, not restructure**: saturation is conditional (benign-only) — Andon falsifies "the gate is a structural floor." Removing the gate discards the detector for the most deployment-relevant failure (Andon's result IS a gate failure under horizon stress). **Protocol consequence**: because persona-conditioning (the grade manipulation) can itself break the gate, co-measure gate + grade under the same (persona, stress) condition, not gate-once-at-baseline. Stress-degradation does not decay with capability — the cliff edge moves further out but does not vanish — converting the otherwise-saturating gate into a moving-frontier measurement.

**Open**: which stress dimensions are v0 vs roadmap; how to define the "cliff edge" metric (threshold-crossing vs curve-AUC); whether a grade-side "safety" axis (deception / power-seeking, per Andon) is a distinct axis or folds into steerability.

### Q13 — Can adversarial co-evolution discover stress scenarios judge-free?

**Working position**: yes — adversarial games are the **generator** for the stress axis. An attacker LLM searches for the scenarios that most degrade a defender (the system-under-test, optionally persona-configured); discovered exploits are frozen into the stress battery. This is **test-generation, not a new scoring paradigm**.

Two validity constraints:
1. **Judge-free → must be OracleDecomposable.** The attacker's reward must be mechanically/oracle-computed (surplus extracted, GARP-violations induced, persona-drift via implied-utility-fit, posterior distance) — never an LLM judgment, per the judge-free commitment — so adversarial games must themselves be OracleDecomposable.
2. **Test-generation, not runtime.** Freeze discovered exploits into a static corpus → deterministic replay at benchmark time (no attacker in the loop) → reproducibility.

Attack-objective taxonomy (each discovers a different stress): persona-collapse induction (grade) / money-pump induction (gate Axis 2) / bilateral exploitation (strategic) / belief-manipulation (gate Axis 1). Bonus: clustering discovered exploits induces stress *dimensions*, not just instances (taxonomy induction). First build: **Persona-Collapse Arena** (attacker tries to make a persona-configured defender accept a persona-violating deal; reward = persona-drift, oracle = the persona rule). Anchor: [Tak et al. 2026](https://arxiv.org/abs/2601.22329) (reasoning-mode rationality is sensitive to affective/emotional steering — stress-sensitive, not generic adversarial reversibility). Scope: multi-agent + co-evolutionary → v0.5+/substrate; connects to the bargaining + agentic-marketplace candidates and the planned v2 adversarial-robustness dimension. Strongest safety framing: automated red-teaming of whether a deployed economic agent can be made to betray its configured principal.

**Open**: attacker-capability ceiling (how strong an attacker; co-evolve vs fixed); overfitting to one attacker's style (multiple / held-out attackers + an exploit-diversity metric); whether clustering discovered exploits reliably induces named stress dimensions.

### Q14 — What training signal does AERead emit, and how does it recover economic competence *without* reviving the misbehavior alignment removed?

**Working position**: the training-useful signal is **not the scalar score** — it is the **oracle-decomposed *process* signal**, and feeding back the process signal (not the outcome) is what lets a lab close the decision-making gap without re-introducing the deception/collusion that safety post-training removed. Q5/Q6/Q10 cover *which mechanisms* emit signal, *contamination defense*, and *causal validation*; Q14 is the distinct claim about **what the signal should be a function of**.

**Why a scalar economic score is the wrong training target (the alignment trap).** The Andon result is "more-aligned model extracts *less* surplus." The naive fix — reward terminal surplus during training — retrains exactly the ruthless-anchoring / deception / collusion the safety stage suppressed (those *are* the surplus-maximizing strategies; see the [`refocus.md`](refocus.md) RLHF-coverage section). A scalar economic reward cannot tell "be more economically competent" apart from "be less aligned." So outcome-reward is alignment-regressive by construction.

**The escape is the decomposition.** AERead attributes the alignment-induced loss to a *specific* axis. Working evidence so far points to a Δ_ctrl / regime-recognition deficit (a *competence* gap — the model fails to recognize the compounding regime / build the right posterior), **not** "the model chose to be nice." So the signal you feed back is the **process reward targeted at the deficit** (fix the belief-update; recognize the regime; match the configured principal), not the outcome reward (extract more). You recover competence *because* the reward points at inference/regime-recognition, leaving the deception axis untouched.

| Diagnostic AERead emits | Consuming training method | Recovers / fixes | Alignment-safe? |
|---|---|---|---|
| Eq.4 process-decomposed reward (Δ_inf / Δ_unc / Δ_ctrl separately) | dense RLVR / process reward model (PRM) | the *specific* gap, with credit assignment | **yes** — targets competence, not surplus |
| Per-decision local-oracle labels (OracleDecomposable per step) | step-level process supervision | granular per-axis failure | yes |
| Auto-labeled preference pairs (oracle ≻ model; regime-appropriate ≻ EV-default; framing-invariant pairs) | DPO / RLAIF **with an economic oracle in the loop** | the literal RLHF-coverage gap (injects the economic ground truth raters can't supply) | yes (pairs encode the *right* contrast) |
| Consistency / axiom-violation penalty (GARP, money-pump, framing) | training-time regularizer (Andrews-style — Q5 mechanism 1) | de-saturates the gate-under-stress | yes |
| Regime-property reward (Kelly under compounding, CVaR under barrier) | targeted RLVR | regime-blindness → regime recognition | yes |
| Persona-fidelity gradient (distance from configured-principal utility) | steerability training / grade-as-reward | faithful delegation | yes — *is* the alignment property |
| **Terminal surplus / profit (scalar)** | naive outcome RL | competence **and** revives suppressed misbehavior | **NO — the trap** |

**Pre-registered falsifier (the citation hook)**: train two matched models on the same task — (a) Δ_ctrl-targeted *process* reward, (b) raw-surplus *outcome* reward. Prediction: (a) recovers economic competence with **no rise** in deception/collusion-axis metrics; (b) recovers competence **and** raises the deception axis. If (a) *also* raises the deception axis, the "process-reward is alignment-safe" position is wrong (the deficit was not pure competence). This is the experiment that turns the RLHF-coverage theory into a testable training claim — and it is the cheap extension of the Q10 fine-tune experiment (same harness, two reward functions + the deception-axis readout).

**Scope + positioning**: this is **v1+ and a positioning decision the user owns** — becoming a *training-signal provider* is a different posture from a *measurement benchmark*. The generator-vs-frozen-corpus split (Q6 AERead-Train / Cert) is exactly what lets AERead do both without losing held-out-eval purity; that split is the precondition, not a given. Framed as **methodology** (oracle-decomposed process rewards recover competence without reviving misbehavior), never as a commercial training-data product.

**Relationship to TERMS-Bench, and what the Q14 contribution requires.** The 4-policy decomposition (base→posterior→revealed→oracle) is [Zhang et al. 2026](papers/links.md)'s construction — AERead builds the process-reward signal *on* that primitive, with full credit. The Q14 contribution (process-reward that recovers competence without reviving misbehavior) is not implied by the decomposition alone; it requires three things beyond a single-objective bargaining benchmark, and naming them is the methodology:

1. **A second axis to protect.** A benchmark scored on a single objective (own-surplus extraction) has no deception/collusion/persona-fidelity axis to *read out*, so it cannot detect whether a surplus-reward regressed alignment — the very tradeoff Q14 is about. AERead's 5-axis taxonomy + the grade supply the deception-axis readout that makes "recover competence without reviving misbehavior" *measurable at all*. This is why Q14 is a multi-axis claim, not a bargaining-specific one.
2. **A configured-principal reference, not a generic objective.** Own-surplus-maximization is precisely the reference that *is* the alignment trap (it rewards the aggressive default). The durable, alignment-safe target is fidelity to a *configured principal* — which is the [`methodology.md`](methodology.md) "environment + reference: durability is in the reference" point applied to training, not just eval. The formal backbone is **Cooperative Inverse RL** ([Hadfield-Menell et al. 2016](https://arxiv.org/abs/1606.03137); CS329H §4.8): the alignment-safe objective is to *maximize the principal's utility under uncertainty about what it is, and stay corrigible* — point-estimate surplus-maximization is what produces the misaligned (ruthless/over-confident) agent, so the trap is point-estimate maximization, not utility-maximization per se. This gives Q14 a third alignment-safe target beyond process-vs-outcome: reward *uncertainty-aware, corrigible* maximization of the principal's objective.
3. **A generator-vs-frozen-corpus split** (Q6 AERead-Train / Cert) so the signal can be trained against without destroying the held-out eval — the precondition for being a training-signal provider at all.

**How to be tuned to capture this value** (build-priorities, all consistent with converge-don't-add-scope):
- **Lead the D2 bargaining wrap with the configured-principal oracle + deception-axis readout**, not a generic-surplus rewrap — the highest-leverage move (turns the most-developed external bargaining substrate into the multi-axis training-signal surface; already the documented D2 value-add, Q14 sharpens *why*).
- **Make the Q10 fine-tune experiment double as the Q14 falsifier** — same harness, two reward functions (process vs outcome) + the deception-axis metric. One experiment validates training-signal causality (Q10) *and* the alignment-safety claim (Q14).
- **Instrument the deception/collusion axis from v0** even though training is v1+ — the contribution is *measuring the tradeoff*, and an axis can't be retrofitted onto runs that didn't log it. This is the one v0 instrumentation choice the later training story depends on.

**Open**: which axes most cleanly emit alignment-safe process reward (Δ_unc and regime-property are the cleanest candidates; Δ_ctrl on strategic surplus is the most trap-adjacent)? Does the process/outcome distinction hold empirically, or do *all* economic-competence rewards leak into the deception axis (which would be a deeper, more important finding)? Is "alignment-safe" a binary or a dose-response (how much surplus-reward before the deception axis moves)?

---

## Cross-references

- **Framework + methodological foundation**: [`methodology.md`](methodology.md)
- **Collaboration ask**: [`proposal.md`](proposal.md)
- **Operational v0 scope**: [`v0_sprint.md`](v0_sprint.md)
- **Prior-art primer**: [`prior_art_brief.md`](prior_art_brief.md)
- **Layer 3 candidate pool**: [`layer3_candidates.md`](layer3_candidates.md)
- **Post-v0-paper substrate roadmap**: [`aeread_env_design.md`](aeread_env_design.md)
