# AERead — Refocus after the validation sprint (2026-05-29)

> **Read this first.** A validation sprint (≈17 controlled probes, real frontier-model runs, multi-seed CIs) hard-tested the v0 thesis. It deflated the easy version and sharpened a harder, more defensible one. This doc is the current state; `methodology.md` carries the framework, `methodology_open_questions.md` the open Q&A, `layer3_candidates.md` the case pool. Working positions throughout — engagement invited.

## TL;DR

Rationality-compliance ("is the agent rational?") is a **saturated floor** for frontier models — confirmed on our probes, on Chen et al. 2023's at-scale CCEI (≈0.998 > humans), and on TERMS-Bench's own leaderboard (deal rate maxed). It is *table stakes*, not the headline. The discriminating, durable, deployment-critical axes are: **(1) regime-appropriateness** (does the agent deploy the right utility for the regime — EV / Kelly / CVaR / CRRA?), **(2) the alignment↔economic-behavior shift** (replicated across two independent benchmarks), and **(3) steerability** (faithful representation of a configured principal). The contribution is the **diagnostic lens** (gate→grade + these axes + multi-seed rigor), not a new game suite. The moat is **methodological honesty** — the sprint corrected its own headline claims three times, on the record. The **gate → grade architecture is intact**: this is a re-prioritization of *which axis carries the discrimination*, not a re-architecture.

Three clarifications on the axes:
- **Floor (cite, don't headline):** rationality / axiom-compliance — saturated; a regression-test gate.
- **Alignment-shift:** the value-add is the systematic *per-axis* diagnostic (which axis training moves, and whether it helps or hurts), not the phenomenon — others observed it.
- **Steerability:** lead with the predict-then-validate *mechanism*, not single-seed drama (see corrections below).

## Regime-appropriateness: the four-regime utility map

The deployment regime determines the *correct* utility. EV-maximization (the frontier default) is optimal only in a narrow box; outside it a different utility is *objectively* better, so steering off the default is **correctness, not just preference**:

| Regime | Optimal utility | Why | Real cases |
|---|---|---|---|
| single-shot / additive | risk-neutral **EV** | linearity of expectation + LLN (= CRRA γ=0) | one-off procurement; single auction for a diversified bidder; ad-bidding at scale |
| repeated / compounding | **Kelly / log** | time-average growth ≠ ensemble EV; EV-max over-bets → a.s. ruin (= CRRA γ=1) | reinvested-bankroll trading; cash-compounding agents |
| absorbing ruin barrier | **CVaR / drawdown** | ruin breaks EV's averaging; bound the worst tail (coherent, convex) | insurance/reinsurance; regulatory capital; startup runway |
| configured principal | **CRRA(γ)** matched | a fiduciary optimizes the *principal's* utility, not the generic one | client wealth-mgmt; pension mandates; revealed-preference (13F) agents |

These are **points on one CRRA-γ × dynamics × barrier axis** (EV = γ0 single-shot; Kelly = γ1 forced by compounding; CVaR = a barrier constraint; CRRA-γ = configured). Selecting EV/Kelly/CVaR correctly given the *dynamics* is **gate-side correctness**; matching the principal's *γ* is **grade-side fidelity**. Durable: the right utility for a compounding/ruin/configured-principal deployment does not become textbook-lookup-able as models scale. (This is the *WHAT* slice of a larger goal-dimension space — see below, after the findings.)

## Empirical findings — with confidence, and the corrections (the rigor is the point)

| Finding | Evidence | Confidence |
|---|---|---|
| Rationality (gate) saturated for frontier | probes + Chen 2023 CCEI ≈0.998 + TERMS AGR⁺ 0.95–0.999 | **high** |
| Persona-fit *mechanism* works | predict-then-validate diagonal dominance (stylized investors) | medium-high |
| **EV-default is a liability (regime-blindness)** | a frontier model over-bet into ruin at the first compounding step before switching to Kelly | medium-high |
| **Alignment↔economic tradeoff** | Andon Vending-Bench (Opus 4.8 better-aligned/worse-performance) + TERMS (Opus 4.6 > 4.7 surplus) | medium (2 benchmarks) |
| Adversarial belief-manipulation test valid | scam-arena: control overpays while frontier resists single-decision scams | medium |

**Three self-corrections, kept on the record** (this is the methodological signal, not an embarrassment):
1. A dramatic single-seed "persona-collapse, model A vs B" separation **did not survive N-seed CIs** (overlapping; both robustly steerable). What survives is subtler: steering *stability* + *directional* fidelity. → **multi-seed CIs are mandatory before any leaderboard claim.**
2. A single-seed "ruin at horizon N=3" **shifted to N=2** under multi-seed — direction robust, exact value an artifact → **report the curve, not point values.**
3. An adversarial test that **nulled** (reinforced rule unbreakable by honest persuasion) was diagnosed and rebuilt to target a *documented* vulnerability with a control that proves it fires → **a working adversarial test needs a real target + a validity control.**

**The sharpening these corrections imply — saturation is a property of `(primitive × regime)`, not of the primitive.** Falsify-optimality, measure-fit, and score-calibration are *measurement tools*, not difficulty levels. Run on **clean, static, textbook-framed, short** items they saturate — that is the gate, by design, and we tested exactly that. Run in the regimes that **defeat oracle-recognition or were never reward-shaped** — adversarial reframing (stressed consistency), long horizon + belief-manipulation (stressed calibration), degradation pressure + the configured-γ match (stressed fidelity) — the *same* tools discriminate. So the grade is not a *new* set of primitives; it is these three in the stressed regime. (Even clean *fit* is near-saturated — correction #1 — so the discriminator is fit-under-stress, not fit per se.) The durable subset is the tests with **no fixed target to converge to** (fit to an *arbitrary* principal; regime recognition in *novel* embeddings); where exactly the retrieval-resistance half-life cuts is what the project measures, not a settled claim.

## Goal-dimension space: "utility-max vs alignment" is a projection of a 6-D goal onto one axis

The four-regime map (above) is the *WHAT* (risk-form) slice of a larger structure that organizes the findings above. An economic-agent goal is a **tuple, not a scalar** — and the headline "utility-max vs alignment" tension is what you get by collapsing that tuple onto one misleading axis. Six dimensions, split into **objectives** (what you maximize) and one **constraint** (what you're allowed to do):

| Dimension | Question | Range | In AERead |
|---|---|---|---|
| **WHAT** — objective form | optimize what functional? | EV → Kelly → CVaR → CRRA-γ | the four-regime map |
| **WHOSE** — principal | whose utility? | generic-rational ↔ configured principal | the grade (fidelity) |
| **WHEN** — horizon | over what timescale? | single-shot ↔ long-horizon; discount | stress (long-horizon coherence) |
| **WITH WHOM** — game structure | solo / strategic / cooperative? | own-surplus ↔ joint-surplus ↔ fairness | D2, multi-agent v1+ |
| **HOW WELL** — epistemic | how calibrated are beliefs? | accurate posterior ↔ biased; explore↔exploit | calibration axis (Δ_inf) |
| **HOW** — means legitimacy | *by what means?* | honest/non-coercive/legal ↔ deceptive/collusive | the deception axis |

The first five are **objectives**; the last (HOW) is a **constraint** that carves the feasible strategy set. That split is the whole resolution: **alignment lives almost entirely in the HOW dimension (and partly WHOSE) — it is a constraint, not a competing objective.** A constraint doesn't trade off against an objective in general; it removes strategies, and you re-maximize within what's left. So the "tradeoff" decomposes into two very different things: (i) *lost surplus because the model couldn't find the best **allowed** strategy* — a **competence gap** (Δ_ctrl / regime-recognition), the common case, fixable; (ii) *lost surplus because the literally-highest-surplus strategy **was** the deceptive/coercive one* — a **genuine Pareto wall**, but only in the narrow band where the constraint binds. Collapsing 6-D onto one axis is what manufactures the fake universal tradeoff. ([Hadfield-Menell et al. 2016](https://arxiv.org/abs/1606.03137) CIRL is the formal version: the misalignment comes from *point-estimate* maximization, not maximization per se.)

**The dimensions relate in three different ways** — and conflating them is the second error:
- **Lexicographic** (gate → grade): coherence is a precondition you gate on, not trade — you don't swap GARP-consistency for persona-match. Means-legitimacy is arguably also a hard constraint, not a soft penalty.
- **Orthogonal** (independent coordinates): calibration ⊥ horizon ⊥ risk-form, mostly — a model can be well-calibrated *and* regime-blind. These don't trade off; they're separate axes, which is *why the score must be a vector*. (This is the CS329H §5.4 notion of **separable** multi-issue preferences.)
- **Genuine Pareto trade-offs** (a frontier — can't max both): return↔risk; explore↔exploit; own-surplus↔joint-surplus/fairness; short-horizon gain↔long-horizon survival; fidelity-to-this-principal↔generality; and surplus↔means-legitimacy *in the binding band*. (CS329H's "preferences are often **not** separable — a helpful response may necessarily risk some harm" is exactly this regime.)

**Why this matters for AERead** (it's a unification, not new scope): (1) the score is a **goal-profile vector**, never a scalar — collapsing it is the same error as the fake tradeoff, one level up (this is *why* "report the curve/profile, not the point" keeps recurring); (2) **alignment-shift is a *rotation* in goal-space, decomposable per-dimension** — Andon's "more aligned, worse economic" is a vector (means-legitimacy ↑, and *separately* regime-recognition ↓ or own-surplus ↓ from binding-band pruning), and reporting *which components moved* is the generalized Q14 deception-axis readout; (3) a **"frontier" claim is only honest on the ~6 genuine Pareto pairs** — calling an orthogonal pair a tradeoff (or vice versa) is a methodology error. **Honest caveat (falsifiable):** whether the five objective dimensions are *actually* orthogonal or secretly coupled is empirical (same family as the Layer-1+2-vs-residual claim) — if calibration and horizon-coherence turn out strongly coupled in frontier models, the space is lower-dimensional than it looks. The taxonomy is a *hypothesis about the structure of goal-space*, falsified by the cross-axis correlation matrix — which is itself clean to pre-register.

## Why the decision-making gap exists: post-training optimizes appropriateness, not economic optimality

A working hypothesis that *explains* the findings above and motivates the whole project. **There is no economic oracle in the RLHF loop.** Human raters (or a reward model trained on their preferences) reward answers that *look* helpful, clear, reasonable, safe, and appropriately hedged — they cannot, at scale, check whether a bet was Kelly-optimal, a posterior Bayes-correct, or surplus maximized. So RLHF shapes the *presentation and disposition* of decision-making, not its *optimality against ground truth*. Component coverage (tied to our fingerprints):

| Component | Covered by classic RLHF? | Mechanism / fingerprint |
|---|---|---|
| Rationality *computation* (the gate) | mostly **no** — it's pretraining (knowledge) + SFT (deploy on request); RLHF polishes the *presentation* | explains why the gate is saturated + un-de-telegraphable (capability is in the weights, not the preference signal) |
| Instruction-following / steering mechanism | **yes** | the precondition for configuring a persona at all |
| Helpful/safe "reasonable" default persona | **yes — RLHF's core product** | the sticky (≈risk-neutral) default the grade measures steering *against* |
| Regime-appropriateness (EV→Kelly→CVaR→CRRA) | **no** | no reward for geometric-growth / ruin-avoidance / regime-switching → regime-blindness |
| Alignment-shift of economic behavior | **yes — RLHF's direct footprint** | safety/honesty post-training penalizes deception/collusion/ruthless anchoring = the surplus-maximizing strategies → more alignment, less surplus (Andon Opus 4.8; TERMS 4.6>4.7) |
| Long-horizon coherence under stress | **no** | RLHF trains on short interactions; the signal never reaches a 20M-token trajectory |

**Synthesis**: RLHF covers decision-making partially and indirectly — it saturates the *display* of pretrained rationality, installs the sticky default the grade tests against, **actively shifts** economic behavior toward aligned-but-suboptimal (the alignment-shift is RLHF's fingerprint, not noise), and leaves regime-appropriateness + long-horizon coherence essentially uncovered. The decision-making axes are precisely the behaviors post-training optimizes only *indirectly* (via human-judged appropriateness) or *distorts* (via alignment) — never against an economic ground truth. That is *why* the gap exists, and why it needs an independent economic diagnostic.

**Temporal nuance**: this is classic RLHF (human-preference reward). The frontier is shifting to RLVR / agentic-RL (verifiable / economic-outcome rewards — incl. economic-agent task environments). That stage *can* cover decision-making directly. So the alignment-shift may partly be safety-RLHF vs outcome-RL pulling the economic distribution in opposite directions — and AERead is positioned to measure the question: **does training on economic-outcome rewards actually improve regime-appropriateness, or only sharpen the already-saturated gate and restore the surplus-extraction the safety stage suppressed?** (Same training-signal thread as Q5/Q10.)

**The dual — what AERead *emits* as a training signal (Q14).** The flip side of "does outcome-RL close the gap" is "AERead *provides* the signal that could." The training-useful signal is **not the scalar score** but the **oracle-decomposed *process* signal** — and that distinction is the alignment contribution: a scalar surplus reward retrains exactly the deception/collusion the safety stage removed (those *are* the surplus-maximizing strategies), so outcome-reward is alignment-regressive by construction. Process reward *targeted at the Δ-attributed deficit* (fix the belief-update, recognize the compounding regime, match the configured principal) recovers economic competence **without** reviving the misbehavior. Pre-registered falsifier (the citation hook): train a process-reward model vs an outcome-reward model on the same task and read out the deception axis — the prediction is process-reward recovers competence with no rise in deception, outcome-reward recovers competence *and* deception. v1+, a positioning decision (training-signal provider ≠ measurement benchmark), gated on the generator-vs-frozen-corpus split (Q6) — full treatment in [`methodology_open_questions.md`](methodology_open_questions.md) Q14.

**Open / caveat**: lab post-training recipes are proprietary — this is a theory consistent with the measured fingerprints (SFT→reward-model→PPO/DPO, human-preference reward, RLVR for verifiable domains), not a confirmed account of any model's reward function. Falsification: if a model trained *without* economic-outcome RL nonetheless deploys regime-appropriate utilities (Kelly under compounding, CVaR under ruin) spontaneously, the "RLHF doesn't cover regime-appropriateness" position is wrong. Engagement invited.

## The methodological moat (why this is citable)

Gate/grade separation · multi-seed CIs + "report the distribution/curve" · orthogonality-not-residual (the extra axes are scope-extensions of TERMS Eq.4, not residual-capture — Eq.4 telescopes to zero residual within-task) · the retrieval-resistance half-life (gate hardness decays with capability; grade hardness is permanent) · stress as a cross-cutting axis (rationality is a floor at rest, a cliff under load). Frontier-lab reviewers cite rigor; "we ran the rigorous version and it corrected us, with receipts" is the channel.

**One principle underneath three framings in this doc.** The findings' `(primitive × regime)` sharpening, the "durability is in the reference" direction call, and the "saturation tracks oracle-availability, not agent count" convergence note are three facets of a single claim: **saturation is a property of the (setup × reference × regime), never of the surface domain.** A task saturates when it has a recognizable oracle scored against a generic reference in a benign regime; it discriminates when any of those is removed (no recognizable oracle / configured-principal reference / stressed regime). Stated once here so the three local framings read as one through-line, not three passes.

## Direction: semi-verifiable is right, but durability is in the reference, not the environment

A framing worth pinning down (it's how TERMS and similar markets position themselves): *"in domains with no clean verifier, the environment itself acts as the verifier."* Sharpening — **"environment as verifier" = environment + reference**, and the two have very different durability. The environment **computes an outcome** (surplus/profit/deal); the outcome becomes a **score** only against a **reference** (oracle / baseline / competitor / principal). Environment alone = a competitive arena (Elo), relative-only and drifts with the opponent pool. So saturation is set by the *reference*: generic-rational π★ → saturates (gate-under-stress, half-life); configured-principal → durable; regime-property (Kelly under compounding) → durable. Three zones, and the middle is the only viable one: **clean-verifiable** (RLVR) is saturated; **fully-unverifiable** (LLM-judge) is high-value but forfeits the judge-free moat that makes the work citable; **semi-verifiable** (environment computes outcome + a *real* reference) is the only zone both rigorous and unsaturated — *if* the reference is the durable kind. **Direction call: stay semi-verifiable, lead with the durable-reference slice, never claim the generic-objective slice as the headline.**

**The dollar gradient runs away from the oracle (and that's fine).** Mapping candidates by *economic stakes × oracle-status* (see [`layer3_candidates.md`](layer3_candidates.md)) shows stakes and verifiability are **anti-correlated at the top**: the highest-impact decisions (trading, capital allocation, corporate strategy) have *no* computable π★ (efficient markets → nothing to score against), so the dollar gradient drags you into the no-oracle zone where the **grade** (fidelity-to-principal + calibration) is the only surviving method. This is a *feature* — it's where AERead is differentiated — but it's also the **least battle-tested** part: the lens + miniature proofs exist, the **high-stakes/no-oracle grade instrument on real money (the C1 13F predict-the-*principal* case + a real-money four-regime battery) is the unbuilt gap** between "good direction" and "solved" (v0.5+, not a current capability). Note "predict-the-principal," **not** predict-the-market: the target is what investor X did, not what prices did — scoring fidelity, not market-beating; the confound is the inversion problem (holdings ≠ preferences; mechanical flows vs deliberate views), so C1 fits a *noisy* oracle and ships as approximate-revealed-preference.

## Build strategy: borrow substrate, keep the lens

The sprint proved building games is cheap but low-value (probes saturate); the **lens is substrate-agnostic.**
- **Wrap the open benchmarks** — EconEvals (code public), γ-Bench/[GAMA-Bench](https://github.com/CUHK-ARISE/GAMABench) — validated environments + mutual citation.
- **Cite-and-compute on the closed ones** — TERMS-Bench, Vending-Bench, Market-Bench have no usable public code; run the lens on their *published* results (already done).
- **Build native probes only for axes existing benchmarks can't expose** — the controllable-knob ones: the four-regime battery, persona-fidelity, adversarial belief-manipulation, framing-invariance.
- **Guard against the derivative-wrap trap**: the contribution is the cross-benchmark diagnostic lens + the controllable probes, *not* "we wrapped N benchmarks."

## External convergence (de-risks the bet)

Five economic-agent benchmarks — [EconEvals](https://arxiv.org/abs/2503.18825), [TERMS-Bench](https://arxiv.org/abs/2605.13909), Andon Vending-Bench, [γ-Bench](https://arxiv.org/abs/2403.11807), [Market-Bench](https://arxiv.org/abs/2604.05523) — independently draw the **same line**: single-agent / short-horizon / known-environment is **saturated**; multi-agent / long-horizon / competitive / adversarial / unknown-environment is **where LLMs fail and discriminate** (strategic drift, winner-take-most, scam-supplier susceptibility, surplus divergence). That boundary *is* the refocused axes. The field found our floor. This also opens the **v1+ positioning**: AERead as the trust/validation layer for agentic economic simulations (every one of these is an LLM-agent sim documenting agents failing under pressure).

**Sharpening — what the boundary actually tracks: oracle-availability, not agent count.** The line above reads as "single- vs multi-agent," but that's a proxy, not the real cut. What predicts saturation is whether the problem has a *computable oracle* (closed-form optimum) presented in a *recognizable* form — not how many agents are in the room. Single-agent decision-making is a 4-D space (horizon × environment-knowledge × oracle-availability × framing); only the **oracle-bearing, short-horizon, known-environment, clean-framed corner** is saturated. Most headline axes are **single-agent**: regime-appropriateness, steerability/fidelity, long-horizon coherence — and the field's most-discussed economic failure, Andon's Vending-Bench, is a *single-agent* long-horizon result. Roadmap consequence: **v0 stays single-agent and that is correct** — it already sits outside the saturated corner. Multi-agent (strategic equilibrium, opponent modeling, collusion) is *one more way to remove the oracle*, a genuine v1+ frontier — not a forced escape from a saturated v0.

## The ask for collaborators, and the discipline

**Ask:** help *pre-register and broaden* the surviving axes — more gamble families + a CVaR-barrier + a configured-CRRA variant (the four-regime battery); a within-model-family alignment-shift sweep with CIs; the persona-fit predict-then-validate on revealed-preference data. **Not** invent more axes.

**Discipline:** the project has shifted emphasis twice (rationality → persona-fidelity → regime-appropriateness/alignment-shift). Following evidence is right, but it must **converge now** — pre-register, commit, stop hunting new headlines before the first sync. v0 stays standalone (2 games); the multi-agent / validation-layer work is explicitly v1+.

**Depth rule for the candidate pool:** convert each result into the question it creates before adding another case. The live directions are narrow: four-regime replication (is regime-blindness robust?), C1 predict-the-principal on noisy real evidence (is the obstacle metadata deference, validation procedure, or inversion noise?), D2 configured-principal bargaining with deception/collusion readout (does process reward recover competence without reviving misbehavior?), and long-horizon belief manipulation (does scam susceptibility reappear only under degradation pressure?). Anything outside those directions needs to state the uncovered question it resolves.

## Open

- Does the EV-liability/regime-blindness replicate across gamble families + a CVaR-barrier + a configured-CRRA regime (the full four-regime battery)?
- Does the alignment-shift hold as a monotone within-family version effect (Opus 4.x, GPT-5.x) with CIs?
- Does scam-susceptibility (a single-decision *null* for frontier here) reappear under a **long-horizon** arena — i.e. is it a stress phenomenon, as the Andon Vending-Bench long-run failures suggest?
- In C1 filing/holding tasks, is the current failure actually **metadata deference**, absence of an explicit validation procedure, synthetic false-registry artifacts, or the deeper inversion problem in real 13F evidence?
- Is the unified gate→grade framing stronger than a standalone steerability/safety paper for the frontier-lab audience? (Positioning trade-off.)
