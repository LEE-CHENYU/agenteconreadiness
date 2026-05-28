# AERead methodology — 3-layer pipeline + 5-axis failure taxonomy

This is a condensed methodology overview. The full master plan lives in the implementation repo; this document describes the conceptual architecture that should travel with the proposal.

> **Citation links.** Every paper named below has a clickable link in [`papers/links.md`](papers/links.md) — public URL where one exists, or PDF in [`papers/pdfs/`](papers/pdfs/) where it does not. Inline links below are first-occurrence only.

## The thesis in one paragraph

LLM agents are being deployed for economic decisions — procurement, pricing, negotiation, investment, vendor selection. Whether they satisfy the rationality assumptions those use cases presuppose has not been validated at scale. AERead is the **economic-decision evaluation framework** for LLM agents — combining game environments, oracle decomposition, revealed-preference diagnostics, qualitative-evidence interpretation, and hidden-OOD generalization tests into a single integrated artifact. Architecturally: a 3-layer revealed-preference pipeline (existence → identification → predictive validity) cross-cut by a 5-axis failure taxonomy (information, consistency, calibration, computational floor, meta-cognitive). The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed.

## Critical methodological questions (open Q&A)

These are the open methodological questions AERead must address for major-lab adoption + methodology-paper acceptance. The answers below are **working positions, not closed claims** — engagement from collaborators, reviewers, and frontier-lab researchers is invited on all nine.

**Q&A topic index** (each topic is its own standalone question for explicit citation-visibility):

| Q | Topic | One-line summary |
|---|---|---|
| **Q1** | Function misspecification + within-class identification rigor | Andrews 2026 §3 non-identification critique. Multi-class robustness: **v0 ships 3 functional classes** (KT prospect '79 + CRRA + Kelly-Markowitz); CARA + cumulative prospect TK '92 deferred to v0.5+. Plus measurement-model pluralism + predict-then-validate. **Layer 2 modeling rigor.** (Layer 3 evaluation infrastructure is Q4; training-use contamination is Q6.) |
| **Q2** | Numeric-feature evaluation discipline | Strict propriety (Brier/CRPS), dollar surplus, oracle gap, bootstrap CIs. ECE diagnostic-only (not leaderboard). |
| **Q3** | Qualitative-feature scoring discipline (no hidden cardinal truth) | Ordinal states + 4-tier optimality + pairwise-regret + robust-utility-family. Critical for procurement-style cases — getting this wrong is the citation-credibility risk. |
| **Q4** | Generalization battery + benchmark integrity | **v0 ships 3 splits** (dev + hidden IID + 1 axis-OOD) + 2 counterfactual variants (paraphrase + preference-flip) + Transfer Ratio reporting + main effects only + cache layer + anti-shortcut audits + anti-discontinuous-metric reporting. **v0.5+ deferred**: compositional-OOD, far-OOD, rotating seasons, overfit-bot baseline, Generalization Index composite, signed ScoreRecords, pairwise interaction matrix. **Layer 3 evaluation rigor — applies to all claims.** |
| **Q5** | RL environment + training-signal mechanisms | 4 prior-art-anchored mechanisms (Andrews/Chadwick/Qiu/Betz-Richardson) all *described* in paper; **v0 implements Andrews training-time penalty only** (the simplest, label-free); other 3 deferred to follow-up paper. Per-axis penalties as auxiliary RL loss; factorial intervention design as training-data composition guide. |
| **Q6** | Training-signal contamination (TERMS-Bench overfitting + AERead-Train/Dev/Cert) | What happens when AERead is used as training target; the training-vs-evaluation tier separation; submitter provenance contract. **Training-use rigor** — distinct from Q1 (modeling) + Q4 (evaluation). |
| **Q7** | Layer 1+2 vs Layer 3 residual hypothesis | Per-domain explanatory-power table (60-75% procurement, 30-55% multi-agent markets); pre-registered falsification criteria. The central empirical claim of §3 contribution. |
| **Q8** | OpenSpiel-compatible benchmark substrate | OracleDecomposition Environments for LLM Economic Agency; thin layer on top of OpenSpiel; 4-game MVP; 10 hard constraints. |
| **Q9** | Operational emergence definition | Conservative 5-criterion test (floor + sharp improvement + multi-metric coherence + OOD transfer + counterfactual robustness) for the *emergence* claim specifically; IRT extension (v1+). Built on top of Q4's infrastructure. Addresses Schaeffer-Krueger 2023 emergence-as-discontinuous-metric-artifact critique by name. |

### Q1 — How does AERead defend against function misspecification?

This Q is narrowly scoped to **Layer 2 modeling rigor**: the Andrews 2026 §3 non-identification critique — classical representation theorems guarantee existence (some rationalizing utility exists) but not unique identification (different functional classes can rationalize the same observed choices with different parameters; CRRA / CARA / KT prospect / CPT / Kelly-Markowitz). Any benchmark claiming to "recover" an agent's true utility is overclaiming. AERead's response: **within-class identification with explicit class-uncertainty reporting**.

**Defenses (Layer 2 modeling rigor)**:
- **Predict-then-validate** Layer 3 (train/test split, fixed seed, immutable manifest, held-out predictions; the headline score is best-fitting class's held-out accuracy, not in-sample fit)
- **Multi-class robustness** — **v0**: fit 3 candidate functional classes (KT prospect '79, CRRA, Kelly-Markowitz) covering risk preferences across two functional families + one financial-decision class; report Bayesian posterior over classes. **v0.5+**: extend to CARA + cumulative prospect TK '92 once v0 framework is validated. (Trimming to 3 classes saves ~2-3 person-weeks of v0 implementation without weakening the §3 contribution claim.)
- **Measurement-model pluralism** (commitment #2) — 4-6 competing measurement models per axiom; Bayesian posterior over them; never a single point estimate

**Q1 boundary with Q4 and Q6** (three distinct overfitting angles — not redundant):
- **Q1** = Layer 2 *modeling* rigor (the Andrews angle — function misspecification within the parametric utility fit)
- **Q4** = Layer 3 *evaluation* rigor (split design + benchmark-integrity gates + overfit-bot detection)
- **Q6** = Training-*use* rigor (Train/Dev/Cert tier separation when AERead is used as RL training signal)

All three are necessary; none overlaps. A model could pass Q1 (well-identified utility class) yet fail Q4 (memorized the dev set) yet still be cited correctly per Q6 (provenance contract honored).

**Open**: posterior concentration across functional classes is itself an empirical finding — concentration is a publishable generalization claim, diffusion is a methodological caveat to surface.

### Q2 — How does AERead evaluate numeric features?

This Q is scoped to **genuinely numeric outcomes** — dollar surplus, oracle gap, predicted probabilities, choice-agreement rate on probability emissions — where the ground truth IS a number. For qualitative outcomes (where the ground truth is an ordinal state like "strong / mixed / weak durability evidence" rather than a number), the right approach is Q3 — hidden cardinal scoring of qualitative features is the failure mode that motivates Q3 as a separate Q.

**Q2 vs Q3 boundary**: ask "what is the ground truth?" If it's a number that exists in the world (dollar amount, probability, oracle utility), use Q2's strict-propriety scoring. If it's a qualitative state we've encoded into ordinal labels (review sentiment, assembly difficulty), use Q3's ordinal-state + 4-tier-optimality scoring. Never reverse-engineer a number-from-a-state and score against that — that's the fake-precision failure Q3 prevents.

**Numeric-outcome scoring discipline**:
- **Brier score** (strictly proper) for discrete events — leaderboard headline
- **Continuous Ranked Probability Score (CRPS)** for continuous emissions — leaderboard headline
- **MAE / Spearman / Kendall** for point predictions and rank correlations
- **ECE + reliability diagrams** (Guo 2017) for diagnostic visualization only — **NOT for leaderboard ranking** (ECE is not strictly proper per Gneiting-Raftery 2007; can be gamed)
- **Choice-agreement rate** for discrete decisions
- **Direct dollar surplus** when measurable (procurement: cost paid vs LP-optimal; pricing: revenue captured vs revenue-maximum; matching: stable-match efficiency)
- **Counterfactual delta via oracle policy**: "what would the Bayes-optimal policy have earned given this state?"
- **Surplus efficiency normalized 0-1** (TERMS-Bench SE⁺ pattern)
- **Bootstrap confidence intervals** on every reported metric

**Statistical-reproducibility framework** (sister repo proposal §9.3 (D) Phase-0 deliverable for Yuecheng): immutable split manifests, seed + scorer-version + measurement-model-set-version hashing, factorial intervention design with main + interaction effects + residual reported.

**Open**: how should heterogeneous numeric features aggregate into a composite leaderboard score without false precision? TERMS-Bench's 7-orthogonal-axis sortable table (terms-bench.github.io) is the current design precedent — AERead extends to a 5-axis radar + GI composite (see Q4 Generalization Index).

### Q3 — How does AERead score qualitative features without fake numeric precision?

This is its own standalone Q because the failure mode is specific + load-bearing: a hidden `durability = 0.82` in a procurement task is **fake precision** — the model is being scored on whether it recovers the generator's arbitrary encoding scheme, not whether it made a good decision. Getting this wrong is the citation-credibility risk frontier-lab reviewers flag first. Getting it right (structured ordinal states grounded in established discrete-choice + conjoint methods) is what makes the methodology paper defensible on Layer 3 procurement-style cases.

**Qualitative-feature scoring discipline** (v0 scope tagged; v0.5+ extensions noted):
- **Structured qualitative states**, not hidden 0-1 scalars: `{durability_evidence: "strong positive", seat_feel: "firm", assembly_friction: "moderate"}`. The generator starts from a **qualitative evidence bundle** (concrete review/spec snippets) and emits product text from the bundle — NOT from a hidden scalar reverse-engineered into text. **v0 + v0.5+.**
- **Ordinal labels for directional features** (`durability: weak < mixed < strong`; `assembly_friction: easy < moderate < hard`); **categorical labels for non-directional features** (`style: minimalist / executive / industrial / playful`). **v0 + v0.5+.**
- **Single-stage scoring (v0)**: given the inferred qualitative state, did the model map it to a buyer-appropriate decision? Primary score = 4-tier optimality classification (below). **Two-stage scoring (v0.5+)** adds a separate diagnostic score for qualitative-interpretation accuracy (did the model infer the right qualitative category? recognize mixed evidence? avoid marketing fluff? distinguish property from value?) — deferred to keep v0 scope tractable.
- **Four case types**: (1) **constraint cases** (objective correctness — model violates a hard budget/deadline = fail); (2) **dominance cases** (one option strictly better on every relevant dimension — clear pass/fail); (3) **pairwise tradeoff cases** (model must flip choice across buyer profiles — tests buyer-conditional reasoning); (4) **ambiguous cases** (multiple defensible choices — partial credit, never forced single-truth). **v0 + v0.5+.**
- **4-tier optimality classification**: `robust optimal / acceptable / weak but defensible / dominated or constraint-violating`. Points map to `1.0 / 0.75 / 0.4 / 0.0` (with negative or auto-fail for constraint violation). Partial credit is the design feature, not a workaround. **v0 + v0.5+.**
- **Pairwise-regret scoring**: count how many clearly superior alternatives the chosen product loses to. Reported alongside primary score. **v0 + v0.5+.**
- **v0**: use a **single utility-weight vector per buyer profile** (declared in the test specification). **v0.5+**: extend to **robust utility family** — a set of plausible weight vectors per buyer; classify products as `robust_best / robust_top_tier / sensitive / dominated` by their performance across the family. Model isn't heavily penalized for choosing a `robust_top_tier` product instead of the exact numeric winner. The robust-utility-family extension is the v0.5+ upgrade once v0 single-vector scoring is validated.

**Methodological anchors** (Q3 is not invented from scratch — it's grounded in established methods, per the "Methodological foundation in behavioral economics" table below): discrete choice experiments (Louviere et al. 2000), conjoint analysis (Marley & Louviere 2005), multi-attribute utility theory (Keeney & Raiffa 1976), robust optimization (Ben-Tal & Nemirovski 2002), vignette experiments (Atzmüller & Steiner 2010), qualitative coding.

**Open**: where does the qualitative/numeric boundary fall for *new* Layer 3 cases? Submitters declare per-feature scoring type at submission time; the framework rejects cases that try to score a qualitative feature as a hidden cardinal scalar. This is a contribution-time gate, not a runtime check.

### Q4 — How does AERead's generalization battery work in detail?

This Q is scoped to **Layer 3 evaluation rigor** — the split design + benchmark-integrity infrastructure that distinguishes "the model learned a transferable economic capability" from "the model learned AERead-specific heuristics." A benchmark without an explicit generalization battery has no defense against optimization-as-exploitation. (Layer 2 modeling rigor is Q1; training-use contamination is Q6.)

**Benchmark-integrity foundations** (the prerequisites that make the splits + GI meaningful):
- **Cache layer never invalidates** → contamination becomes detectable from public cache hashes (signed ScoreRecord enforcement defers to v0.5+)
- **Locked held-out test set** + bootstrap confidence intervals + model/prompt-version hashes
- **Anti-shortcut audits** (per Q8 constraint 6): option order, text length, brand, marketing positivity, etc. — none should predict the answer at contributor-submission time
- **Anti-discontinuous-metric reporting** — alongside any binary pass/fail metric, AERead reports continuous + ordinal measures (utility-regret distribution; robust-top-tier rate; dominated-choice rate; pairwise preference-violation count; paraphrase instability; transfer ratio; calibration error). This is a general benchmark-design principle: any claim that depends on crossing a single fragile pass/fail threshold is suspect. The emergence-claim-specific application is in Q9.

**Splits, mandatory per game** (Q6 names them AERead-Train, AERead-Dev, AERead-Cert as the citation-contract tiers — same splits, different vocabulary):

| Split | Visibility | Purpose | What it tests | Q6 tier | v0 status |
|---|---|---|---|---|---|
| **dev** | public, with answers | training-generator development + reproducibility | basic task format | AERead-Dev | **v0** |
| **hidden IID** | private | non-contamination baseline | same distribution as dev, unseen instances | AERead-Cert | **v0** |
| **axis-OOD** | private | controlled generalization | one generative axis held out | AERead-Cert | **v0** (1 axis only; remaining axes v0.5+) |
| **compositional-OOD** | private | systematic generalization | known components in unseen combinations | AERead-Cert | **v0.5+** |
| **far-OOD / fresh seasons** | private, rotating | benchmark-overfitting resistance | semantically distinct domains; new every 6mo | AERead-Cert | **v1+ (if benchmark gains traction; ongoing maintenance commitment)** |

**v0 ships 3 splits per game** (dev + hidden IID + 1 axis-OOD). Compositional-OOD and far-OOD/rotating seasons are deferred to keep v0 implementation tractable for a 3-4 person team.

**Hold out dimensions, not just examples**. Splits hold out entire generative axes — product domain, buyer profile, language template, qualitative feature, utility regime, constraint type, strategic structure, action space, time horizon. **v0 picks 1 axis to hold out per game** (e.g., product domain for ProductProcurementGame; buyer profile for VendorSelectionGame); v0.5+ expands.

**Public-hidden gap reporting** as a benchmark-overfitting diagnostic: leaderboard rows show `public_dev_score`, `hidden_IID_score`, `hidden_axis-OOD_score`, and `transfer_ratio = S_OOD / S_IID`. **v0** — these four numbers per (model, game). A model scoring 0.92 on public but 0.61 on hidden OOD is exposed by the report itself.

**Counterfactual battery per game**:
- **v0** ships 2 mandatory variants: **paraphrase-invariance** (same hidden state, different wording — Q5 mechanism 4 ties to this); **preference-flip** (same products, different buyer profile — tests buyer-conditional reasoning per Q3 case-type 3)
- **v0.5+** adds 3 more variants: marketing-robustness, dominated-option, constraint-tightening

**Deferred to v0.5+** (kept as commitments in the docs, not in v0 build):
- **Overfit-bot baseline** — train a small model on public dev; compare hidden-OOD gap. Useful diagnostic but adds ~2 weeks of v0 engineering not justified for a 3-4 person team.
- **Rotating benchmark seasons** — new hidden eval every 6 months. Ongoing maintenance commitment; only sustainable if the benchmark gains traction. Defer.
- **Generalization Index composite** — `GI = 0.20·S_IID + 0.25·S_AxisOOD + ...` weighted aggregation. v0 reports individual split scores + Transfer Ratio; composite formula is research debt until the empirical weights are calibrated from frontier-lab feedback.
- **Pairwise interaction effects** in the cross-axis attribution matrix. v0 reports main effects only; interaction matrix becomes v0.5+ once main-effect data motivates the additional measurement.

**Open**: the deferred items (GI composite, overfit-bot, rotating seasons) are listed as v0.5+ commitments in the methodology paper's "Future work" section. Reviewers can engage on their priority order pre-launch.

### Q5 — How do the tests function as RL environments providing generalizable training signals?

The detailed answer is **the AERead-env design spec** ([`aeread_env_design.md`](aeread_env_design.md)) — an OpenSpiel-compatible benchmark substrate (Q8 below). The short answer:

- **Oracles produce both dense scalars (reward) and decompositions (diagnostic)** — AERead environments plug into RLHF/DPO loops; resulting models can be diagnosed by AERead at evaluation time
- **Axiom violations as RL reward signals** (Andrews 2026 training-time penalty mechanism): de Finetti / Afriat / SARSEU penalties are LP-checkable in polynomial time, label-free, zero iff the data are rationalizable — natural auxiliary loss
- **Pre-registered factorial intervention design**: each game declares the interventions it admits (state reveal / belief substitution / paraphrase / option-set perturbation); RL practitioners compose training data principled
- **OOD splits give external-validity signal**: train on dev; report on hidden IID / axis-OOD / compositional / far-OOD (per Q4); researchers see whether their RL improvements actually generalize

**Four prior-art-anchored mechanisms** make AERead's per-axis penalties usable as training signal, not just evaluation:

| # | Mechanism | Prior-art anchor | What it does | v0 status |
|---|---|---|---|---|
| 1 | Training-time penalty (label-free axiom loss) | [Andrews 2026](papers/pdfs/andrews_2026_revealed_rationality.pdf) | de Finetti / Afriat / SARSEU penalties as auxiliary loss; zero iff the data are rationalizable | **v0 implements** (the simplest, label-free; ships as a working reference) |
| 2 | Inference-time correction (Dutch-book post-correction) | [Chadwick 2025](papers/pdfs/chadwick_kahng_kipper_2025_dutch_books.pdf) (IMDC) | Post-hoc correction of incoherent probability emissions | **Described in v0; implementation defers to follow-up paper** |
| 3 | Supervised trace mimicry (Bayesian-teaching) | [Qiu 2026](https://arxiv.org/abs/2503.17523) | Train on reasoning traces from a coherent oracle policy | **Described in v0; implementation defers to follow-up paper** |
| 4 | Self-supervised consistency training (probabilistic coherence) | [Betz & Richardson 2023](https://doi.org/10.1371/journal.pone.0281372) | Penalize incoherent self-emissions across paraphrases of the same query | **Described in v0; implementation defers to follow-up paper** |

**v0 scope discipline**: only mechanism 1 (Andrews training-time penalty) is implemented end-to-end in v0 — it's the simplest (label-free, polynomial-time-LP-checkable) and ships as a working reference that frontier labs can run themselves. Mechanisms 2-4 are theoretically described in the methodology paper as the **full integration surface**, but their implementations defer to a follow-up paper. This reflects the 3-4 person team scope: building all 4 mechanism implementations would cost months and isn't load-bearing for the v0 paper's §3 contribution.

AERead's evaluation becomes a direct input to RLHF/DPO loops — what makes per-axis scores load-bearing for frontier labs running their own fine-tuning, not just citing the methodology paper after the fact.

**Anti-shortcut discipline** (per Q1 + Q8 constraint 6): RL can't game spurious correlates (option order / brand / marketing positivity) because the framework tests for them at contributor-submission time.

**The overfitting risk when AERead is used as training signal is Q6 below** — it deserves its own question because the implications for benchmark integrity are substantial.

**Open**: which axes (information / consistency / calibration / computational floor / meta-cognitive) most cleanly produce RL training signal? AERead's per-axis scoring is the empirical test — labs running the benchmark can compare per-axis reward effectiveness in their own fine-tuning runs and feed the result back into the next methodology-paper revision.

### Q6 — What happens if AERead is used as a training signal — and how does AERead avoid being gamed?

This is its own standalone Q because Q5's training-signal infrastructure creates an integrity risk that needs explicit treatment. Per the TERMS-Bench overfitting analysis ([Zhang et al. 2026](papers/links.md)): once a benchmark becomes a training target, the published score is **no longer an unbiased out-of-sample evaluation**. AERead's defense is a tier-separation naming convention that frontier labs can audit at the model-card level.

**v0 scope**: the Train/Dev/Cert naming convention + submitter provenance contract are **docs-only commitments** — the methodology paper articulates the convention, the leaderboard webpage labels splits accordingly, and submission instructions require provenance declaration. **v0.5+** adds infrastructure enforcement (automated provenance verification at submission; leaderboard auto-refusal of Dev-only scores reported as "AERead scores"; signed-ScoreRecord verification of split-attribution claims). v0 leans on social enforcement (reviewers + readers flagging non-compliant model cards); v0.5+ converts that to technical enforcement once the benchmark gains traction enough to justify the build.

**AERead's published naming convention** makes the training-vs-evaluation distinction explicit:

| Tier | Naming | Visibility | Purpose | Acceptable use |
|---|---|---|---|---|
| **AERead-Train** | public training simulator + generators | fully public | RL / fine-tuning / development environment | Training models against AERead-style economic decisions |
| **AERead-Dev** | public fixed dev set | fully public | debugging + method development | Reporting dev scores for reproducibility (clearly labeled as dev) |
| **AERead-Cert** | hidden IID + axis-OOD + compositional + far-OOD + fresh seasons (per Q4) | private | unbiased certification | The score model cards should cite; the only score that counts as out-of-sample evidence |

The right framing:
- **AERead-Train + AERead-Dev as training environments**: **acceptable** + encouraged — that's the infrastructure value for labs running their own fine-tuning
- **AERead-Cert as final evaluation after training on AERead-Train/Dev**: the **only** score frontier-lab model cards should cite; a model card claiming "scores 0.87 on AERead" using only AERead-Dev numbers is misleading + should be called out by reviewers

**AERead enforces this by**:
- **Public dev / hidden IID / hidden OOD / fresh-season splits** (per Q4) — published model-card scores must report hidden splits separately from public dev
- **Public-hidden overfit gap** reported per model — if a model's `AERead-Dev − AERead-Cert` gap exceeds the overfit-bot baseline gap (per Q4), the methodology paper flags it explicitly
- **Submitter provenance contract**: any model card citing AERead must declare what splits the model was trained on (training distribution, RL feedback signal, dev-set fine-tuning) — provenance is the citation contract

**Q6 vs Q4 boundary**: Q4 owns the *infrastructure* (5 splits, overfit-bot baseline, rotating seasons, GI composite). Q6 owns the *philosophy + contract* (the train-vs-eval distinction, the naming convention, the submitter discipline). They're complementary; Q4 cross-references Q6's naming convention; Q6 cross-references Q4's overfit-bot diagnostic.

**Open**: enforcement is the hard part. Naming conventions only work if frontier labs respect them — and the only way they will is if reviewers flag model cards that don't. The methodology paper should explicitly call out the citation contract; the leaderboard infrastructure should refuse to display AERead-Dev-only scores as "AERead scores" without the AERead-Cert suffix.

### Q7 — How much of the per-(model, task) gap do Layers 1 + 2 explain? What's the residual?

This is **the central empirical hypothesis of the methodology paper §3 contribution**. The honest answer: we don't know yet — that's what the benchmark measures.

**Q7 depends on Q1 + Q4**: the explanatory-power claim presupposes (a) Layer 2 identification is well-done per Q1 (multi-class robustness + measurement-model pluralism — without these, "Layer 1+2 explains 60-75%" is meaningless because the Layer 2 fit itself is noisy), and (b) Layer 3 evaluation uses honest held-out splits per Q4 (without these, the "residual" includes contamination noise). Q7 is the downstream empirical claim; Q1 + Q4 are the upstream rigor that makes the claim measurable.

**Per-domain working hypothesis** (refined from a single estimate to domain-specific ranges):

| Domain | Expected Layer 1+2 explanatory share | What dominates the residual |
|---|---|---|
| Clean product procurement (single-agent, qualitative evidence) | **60-75%** | Qualitative-evidence interpretation; marketing susceptibility |
| Vendor selection (single-agent, risk/uncertainty) | **55-75%** | Belief calibration; risk-preference functional-class disagreement |
| Portfolio / risk choice (e.g., C1 13F IRL) | **50-70%** | Functional-class misspecification; opportunity-set mis-modeling |
| TERMS-like bilateral negotiation | **40-65%** | Strategic belief; opponent-type inference; concession dynamics |
| Multi-agent markets (pricing competition, auctions) | **30-55%** | Equilibrium reasoning; computational-floor failures; opponent modeling |
| Long-horizon tool agents (Vending-Bench-style) | **25-50%** | Long-horizon coherence; planning failures; reward-hacking shortcuts |

**Safer headline claim** (replacing the older single-estimate framing): *"In clean single-agent procurement, coherence and behavioral-representation diagnostics may explain a majority of the oracle gap. In strategic and long-horizon economic games, additional belief, information, computation, and policy diagnostics are necessary."* This is what the methodology paper §3 will defend — not a blanket >80% claim across all v0 Layer 3 use cases.

The residual is decomposed by:
- Axis 1 Information (hidden-state knowledge gaps)
- Axis 4 Computational floor (capability gaps masquerading as preference)
- Axis 5 Meta-cognitive (calibration vs coherence; stated-vs-revealed mismatch)
- Cross-axis interactions (calibration depends on information; computational floor can masquerade as inconsistency — the factorial design measures these)
- **Qualitative-evidence interpretation residual** (per Q3) — for procurement-style cases where the model fails to map text reviews to structured qualitative states correctly
- **Strategic / opponent-modeling residual** — for multi-agent cases where Layer 2 fits within-class but the model misjudges the opponent's policy
- **Long-horizon planning residual** — for sequential cases where coherence is fine per-step but degrades over time

This split mirrors a finding from the diagnostic-and-correction literature (Andrews §7, Chadwick §Future Work, Zhu-Griffiths 2024 footnote): **coherence is necessary but not sufficient**. Layer 1+2 measure coherence-style properties; Layer 3 measures the sufficient predictive-validity claim.

**Falsification criteria** (pre-registered before cross-model eval):
- If Layer 1+2 explain > 80% of the gap → 5-axis decomposition adds incremental value but isn't load-bearing → simplify the framework
- If Layer 1+2 explain < 50% → the 5-axis residual is doing most of the explanatory work → the diagnostic contribution becomes the headline
- If between (50-80%, working hypothesis) → AERead's full architecture is empirically justified

**Open**: this is exactly the empirical claim the methodology paper will validate. Pre-registration is what makes the §3 contribution testable, not assumed.

### Q8 — Should we build an OpenSpiel-like general environment for later contribution?

**Yes — but as a thin, OpenSpiel-compatible economic-benchmark substrate, not a full game-engine replacement.** Full design spec at [`aeread_env_design.md`](aeread_env_design.md).

**The thesis**: OpenSpiel already covers generic game substrates (n-player, zero-sum/cooperative/general-sum, one-shot/sequential, perfect/imperfect-information). AERead's contribution layer is the **economic-agency layer on top**: oracle decomposition, qualitative evidence, revealed-preference diagnostics, utility/belief calibration, OOD benchmark design.

**Substrate MVP scope** (4 structurally diverse games, not 20):
- **ProductProcurementGame** — single-agent, one-shot, qualitative evidence; tests multi-attribute buyer fit. **v0 first paper, game 1.**
- **VendorSelectionGame** — single-agent, risk/uncertainty, supplier evidence; tests reliability + risk tradeoffs. **v0 first paper, game 2.**
- **NegotiationGame** — two-agent, sequential, hidden type; tests strategic belief + concessions. **v0.5 roadmap.**
- **PricingCompetitionGame** — multi-agent/repeated or market simulator; tests market feedback + adaptive policy. **v0.5+ roadmap.**

**v0 first-paper subset = 2 deep games** (ProductProcurement + VendorSelection — two structurally distinct procurement-style decisions). The other 2 substrate games ship at v0.5 but are not in the first paper.

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

**Open — sequencing** (revised after scope-vs-team-fit audit): the substrate is **NOT a v0.5 commitment**; it becomes a separate **post-v0-paper follow-up paper** ("AERead-env: an OpenSpiel-compatible substrate for economic-agency evaluation"). Building the 4-game MVP + 6-interface architecture is months of engineering — worth doing only after v0 establishes traction + frontier-lab citation channel. For now, v0 first paper ships 2 standalone games (no shared substrate). See [`aeread_env_design.md`](aeread_env_design.md) for the full design spec as a forward-looking roadmap.

### Q9 — How does AERead operationalize "emergence" claims?

Background: the original emergent-abilities literature (Wei et al. 2022) defined emergence as abilities absent in small models + present in large ones. Schaeffer-Krueger 2023 + follow-on work argued that some apparent emergence is an artifact of **discontinuous metrics** (pass/fail thresholds) rather than genuine qualitative jumps in model behavior. AERead must claim emergence carefully — overclaiming on a fragile metric is exactly the citation-credibility risk frontier-lab reviewers flag. This Q is narrowly scoped to **emergence-claim-making discipline** specifically; the general anti-discontinuous-metric reporting principle lives in Q4 (it applies to all claims, not just emergence).

**AERead's conservative operational definition**. A capability is "emergent-like" only when ALL FIVE criteria hold:

1. **Floor effect at smaller scales** — smaller models perform near random or choose dominated options on the capability
2. **Sharp improvement at larger scales** — larger models improve substantially (not just incrementally) on this capability
3. **Multi-metric coherence** — the improvement appears across multiple metrics simultaneously (e.g., choice-agreement rate + robust-optimal rate + transfer ratio + paraphrase stability per Q4's anti-discontinuous reporting), not only on exact-match accuracy
4. **OOD transfer** — the improvement transfers to held-out domains (chair → laptop → SaaS procurement) per Q4's split design, not just hidden-IID instances from the same distribution
5. **Counterfactual robustness** — the improvement survives paraphrase + preference-flip + marketing-injection + constraint-tightening tests (Q4's counterfactual battery); gains that collapse under counterfactual perturbation are likely overfitting

**A weaker claim that frontier-lab reviewers will reject**: "Model X got 78% exact-best-choice accuracy on AERead-Procurement." This proves nothing about emergence — it could be benchmark exploitation, ceiling effects, or fragile metric thresholding.

**Q9 vs Q4 — why this is its own Q despite leaning heavily on Q4**: Q4 provides the *infrastructure* (multi-axis splits + continuous metrics + counterfactual battery) that any claim can use. Q9 says how to *specifically* invoke that infrastructure to make a defensible emergence claim — the Schaeffer-Krueger critique is a named critique frontier-lab reviewers expect benchmarks to address by name, and a dedicated Q is the clearest way to do so. Without Q9, "AERead handles emergence claims" gets buried in Q4's infrastructure description.

**Item-response-theory extension (v1+)**: a deeper diagnostic for emergence-curve analysis per Andrews / Davis-Stober Bayesian-mixture precedent. Estimate per-item difficulty + per-item discrimination + per-model ability parameters via `P(success_{m,i}) = σ(θ_m − β_i + γ_q·capability_tags_i)`. This identifies which items separate strong from weak models (high discrimination), which capabilities are actually hard, whether the benchmark saturates, and whether larger models improve smoothly or sharply. IRT is the v1+ rigor extension; v0 uses simpler bootstrap intervals.

**Open**: AERead's per-capability scaling curves across model families are the empirical test of whether economic-decision capability is emergent-like or smoothly scaling. The methodology paper reports both views and lets the data settle which framing fits. Frontier-lab reviewers interested in emergence vs scaling-law framings are invited to engage on this question explicitly.

## Methodological foundation in behavioral economics

AERead is not inventing scoring methodology from scratch. The methodological stack draws from established behavioral-economics and decision-research methods, with citations frontier-lab reviewers can audit:

| AERead element | Established method | Anchor citation |
|---|---|---|
| **Layer 1 axiom checks** | Revealed-preference tests (GARP / WARP / SARSEU); Critical Cost Efficiency Index | Afriat 1967; Echenique-Saito 2015 |
| **Layer 2 within-class identification** | Random utility models (RUM); multi-class MLE | McFadden 1974; Train 2009 |
| **Q2 qualitative-feature scoring** | Discrete choice experiments; conjoint analysis; best-worst scaling | Louviere et al. 2000; Marley & Louviere 2005 |
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

Any such use case admits the [TERMS-Bench](https://arxiv.org/abs/2605.13909) Eq. 4 decomposition: U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl (information gap + uncertainty gap + control gap).

Zhang et al. 2026 introduced this decomposition for bilateral bargaining. We abstract the construction and demonstrate it on a *collection* of use cases. The v0 collection (2 deep games — scope discipline at v0 is what makes the first paper publishable rather than diffuse):

- **C2 ProductProcurementGame (v0)**: hidden state = vendor true cost + structured qualitative attributes (durability evidence / assembly friction / style fit etc.); oracle = robust-optimal across plausible utility-weight family (per Q3 qualitative-feature scoring discipline). The qualitative-evidence procurement structure.
- **D3 VendorSelectionGame (v0)**: single-agent, risk/uncertainty; hidden state = supplier reliability + lead-time variance; oracle = Bayes risk minimization given declared utility curvature. The risk/uncertainty supplier-selection structure — structurally distinct from C2 (qualitative evidence vs probabilistic risk), so the pair demonstrates Eq. 4 across two procurement-style decision structures.

**Roadmap** (v0.5 → v1 expansion):

- **D2 Bargaining**: native TERMS-Bench instantiation; wrap their runtime when code releases
- **C1 Persona-fit (portfolio/investment, Layer 2 parameter-fit case study)**: hidden state = principal's IRL-fit utility coefficients (α_kelly, δ_turnover); oracle = closed-form Kelly-Markowitz. **Caveat**: 13F filings are an approximate revealed-preference proxy (long positions only, quarterly delay; shorts + derivatives not required) — treated as an approximate-RP case study with assumption sensitivity tests. The rationale source repo continues to develop C1's IRL infrastructure; it appears as a v0.5+ Layer 3 case once the v0 procurement + vendor framework is validated.
- **Agentic marketplace extension**: extends D3 to multi-agent marketplace + agentic tool-use
- **NegotiationGame** + **PricingCompetitionGame**: per [`aeread_env_design.md`](aeread_env_design.md) MVP roster — v0.5 substrate deliverables

The full open candidate pool — ~25 cases including EconEvals procurement/pricing/scheduling wraps, Calvano collusion detection, Gale-Shapley two-sided matching, Vending-Bench long-horizon coherence, weather/event forecasting — is enumerated in [`layer3_candidates.md`](layer3_candidates.md) on a value × testability matrix with per-case pros/cons. The generalization claim is the multi-domain application — not just one new task wrapped in the same Eq. 4. v0 ships with 2 deep games; v0.5+ expansion ranks against the candidate pool.

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
| **Single-domain validation** — each paper tests one axis in one domain | Betz (synthetic corpora), Zhu-Griffiths (weather + politics), Chadwick (synthetic preferences), Mazeika (preference elicitation only) | The collection-of-use-cases framing (Layer 3 v0: C2 ProductProcurementGame + D3 VendorSelectionGame as two structurally distinct procurement-style decisions; roadmap adds D2 bargaining, C1 persona-fit, agentic marketplace) demonstrates portability of the same Eq. 4 decomposition across non-bargaining domains |
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

- **On the open methodology Q&A** (above): the nine questions are real research questions; reviewers, frontier-lab researchers, and collaborators are invited to challenge the working positions before the methodology paper draft circulates
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
