# AERead methodology — open methodological questions (Q&A)

> Working positions on the 10 open methodological questions for major-lab adoption + methodology-paper acceptance. **Not closed claims** — engagement invited on all ten. Topic-index table for navigation; bodies below; "Open:" line ends each Q.
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

### Q5 — How do the test functions as RL environments providing generalizable training signals?

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
| Continuous-action pricing (v0 C8) | **50-70%** | Continuous-action optimization; demand-prior misinterpretation |
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

**Substrate MVP scope** (4 structurally diverse games):
- ProductProcurementGame (C2) — discrete-action, qualitative evidence — **v0 game 1**
- SimplePricingGame (C8) — continuous-action, demand uncertainty — **v0 game 2**
- VendorSelectionGame (D3) — risk/uncertainty — v0.5+ roadmap (demoted 2026-05-28; structurally similar to C2)
- NegotiationGame — two-agent strategic — v0.5 roadmap
- PricingCompetitionGame — multi-agent / repeated — v0.5+ roadmap

**10 hard constraints** locked into the framework — full details in [`aeread_env_design.md`](aeread_env_design.md).

**Naming**: position as "**OracleDecomposition Environments for LLM Economic Agency**" — not "OpenSpiel for economic games" (too broad).

**Open — sequencing**: the substrate is **NOT v0.5** — it becomes a separate post-v0-paper follow-up paper. v0 first paper ships 2 standalone games (no shared substrate). Building the 4-game MVP + 6-interface architecture is months of engineering; worth doing only after v0 establishes traction.

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

---

## Cross-references

- **Framework + methodological foundation**: [`methodology.md`](methodology.md)
- **Collaboration ask**: [`proposal.md`](proposal.md)
- **Operational v0 scope**: [`v0_sprint.md`](v0_sprint.md)
- **Prior-art primer**: [`prior_art_brief.md`](prior_art_brief.md)
- **Layer 3 candidate pool**: [`layer3_candidates.md`](layer3_candidates.md)
- **Post-v0-paper substrate roadmap**: [`aeread_env_design.md`](aeread_env_design.md)
