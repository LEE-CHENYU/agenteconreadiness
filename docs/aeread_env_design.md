# AERead-env: OpenSpiel-compatible benchmark substrate for LLM economic agency

> **Status: post-v0-paper substrate roadmap. NOT a v0 first-paper deliverable, NOT a v0.5 commitment.**
>
> This document is a forward-looking design spec for the *eventual* AERead benchmark substrate. The v0 first paper (per [proposal §2](proposal.md#2-the-3-layer-hierarchy-canonical-revealed-preference-pipeline)) ships 2 standalone games (ProductProcurementGame + VendorSelectionGame) — no shared substrate. Each game is implemented standalone in v0 to keep scope tractable for a 3-4 person team over a 16-week timeline.
>
> The substrate framework below describes what AERead *could* become after the v0 paper publishes + frontier-lab citation channel is established. Building the substrate is naturally a **second paper** ("AERead-env: an OpenSpiel-compatible substrate for economic-agency evaluation") rather than a v0.5 extension. The 4-game MVP + 6 first-class interfaces below is months of engineering — it's worth doing only after v0 establishes traction.
>
> Referenced from [`methodology.md`](methodology.md) Q8 (which now also describes Q8 as post-v0-paper scope, not v0.5).

## Positioning

**Not** "OpenSpiel for economic games." That framing is too broad, invites unflattering comparison with the existing DeepMind library, and obscures the contribution. The actual positioning:

> **An OpenSpiel-compatible economic-agency evaluation layer for LLMs** — combining oracle decomposition, revealed-preference diagnostics, qualitative-evidence interpretation, utility/belief calibration, and hidden-OOD generalization tests on top of generic game substrates. Shorthand: **OracleDecomposition Environments for LLM Economic Agency**.

OpenSpiel already covers the generic game substrate (n-player, zero-sum/cooperative/general-sum, one-shot/sequential, perfect/imperfect-information). AERead-env is **the economic-agency evaluation layer on top** — the diagnostic + evaluation infrastructure that turns a game into a benchmark for LLM economic decision-making. The four explicit additions on top of OpenSpiel-style substrates are: (1) oracle decomposition (Δ_inf / Δ_unc / Δ_ctrl), (2) revealed-preference diagnostics (axiom checks + within-class identification), (3) qualitative-evidence interpretation (structured ordinal states, not hidden cardinal truth — per methodology Q3), (4) hidden-OOD generalization protocol (axis-OOD + compositional + far-OOD + fresh seasons).

This positioning matters strategically. Major model labs cite **diagnostic + evaluation frameworks**, not "yet another game library." Adoption traction analysis (see source-repo notes) shows the "-Bench" suffix caps citations at low single-digit numbers even with elite-PI authorship; the deployment-verdict / diagnostic framing is what GDPval-style benchmarks use to break out.

## Why this matters for AERead

Three concrete reasons AERead needs an environment substrate, not just a leaderboard:

1. **RL training signal** — the methodology-paper claim that AERead's per-axis penalties can serve as training signal requires AERead to expose oracle-grounded rewards + factorial intervention data, not just black-box scores. The environment substrate is the academic foundation for that claim — and the integration surface frontier labs need before they cite the methodology paper as load-bearing for their own training pipelines.
2. **Generalizable diagnostic** — a single-task benchmark can't distinguish task-specific weakness from cross-task pattern. The substrate's structural-diversity goal makes per-axis 5-factor scores generalizable.
3. **Community contribution** — frontier-lab adoption requires a path for external researchers to contribute new games. The substrate's submission API + anti-shortcut audit + OOD-axis declaration is the contribution interface.

## Key design goals (7)

### 1. OpenSpiel compatibility, not replacement

The environment substrate's `Game` API mirrors OpenSpiel's:
- `reset(seed)` / `observe(state)` / `legal_actions(state)` / `step(state, action)` / `is_terminal(state)` / `returns(state)` / `metadata()`

Plus AERead-specific economic-evaluation hooks:
- `oracle_policy(state)` — the reference / oracle policy that AERead's evaluation calls
- `oracle_value(state)` — the oracle's value function
- `decompose_gap(observed_action, state)` — gap decomposition (Δ_inf / Δ_unc / Δ_ctrl per TERMS-Bench Eq. 4)
- `counterfactual(state, intervention)` — apply a diagnostic intervention (state reveal / belief substitution / paraphrase / option-set perturbation)
- `behavioral_representation(state, action_trace)` — extract revealed-preference primitives from a trajectory

Compatible enough that someone using OpenSpiel can drop in an AERead-env game with minimal API translation. Different enough to expose the economic-evaluation machinery OpenSpiel doesn't have.

### 2. Structural diversity by design

Each game declares its structural footprint:
- **Agents**: 1 / 2 / N
- **Time**: one-shot / sequential / repeated
- **Information**: perfect / imperfect / private-type / asymmetric
- **Action space**: discrete / continuous / structured (combinatorial)
- **Payoff**: outcome / preference-revealed / market / mechanism-grounded
- **Strategic**: solo / cooperative / competitive / mixed
- **Oracle**: exact / approximate / dominance-only / human-reference / market-simulation

Release cannot be 90% single-shot multiple-choice. The MVP scope of 4 games (below) is explicitly chosen to maximize structural diversity within a small footprint.

### 3. Oracle decomposition as the common abstraction

Not "all games share the same utility function" — that's wrong. Different games have different utility structures.

But: **all games admit the same intervention decomposition.** Every game answers "if we revealed the hidden state, would the model have chosen better?" / "if we removed uncertainty, would the model have chosen better?" / "if we paraphrased the prompt, would the choice flip?" The oracle decomposition pattern (from TERMS-Bench's Δ_inf / Δ_unc / Δ_ctrl) is the **shared abstraction**, not the utility form.

### 4. LLM-native observations + actions

Both **symbolic ground state** (the hidden truth — used to compute oracle gap + diagnostic) and **textual observation** (what the LLM sees) are exposed separately. This is hard constraint #1.

Action space is **structured action schema** (JSON-like: `{action: "purchase", product_id: "X", quantity: 5}`) with optional natural-language trace. Models can output both; scoring uses the structured action; the trace feeds Axis 5 meta-cognitive scoring (Qiu 2026 supervised trace mimicry).

### 5. Generalization-first splits

Six split categories mandatory per game:
- **dev** — public, with answers (training generator + baseline)
- **hidden IID** — same distribution as dev, no answers public (anti-leakage)
- **axis-OOD** — one axis (domain / buyer_type / language template / utility regime / risk model / opponent policy) shifted
- **compositional-OOD** — two axes shifted
- **far-OOD** — multiple axes shifted, semantically distinct distribution
- **fresh** — held-out, post-publication generation (anti-contamination)

Each game's `metadata()` declares which OOD axes it can shift. Contributors must declare these at submission time.

### 6. Diagnostic interventions as first-class objects

Every game declares its supported counterfactual interventions. The minimum:
- **baseline** — vanilla game state
- **paraphrase** — same state, different prompt wording (Axis 2 consistency check)
- **constraint-explicit** — make constraints explicit vs implicit (Axis 4 computational floor)
- **state-revealed** — show the model the hidden state directly (Axis 1 information)

Optional extras per game type:
- **preference-change** — change utility weights mid-game
- **dominated-option** — add a strictly dominated alternative (sanity check)
- **belief-substitution** — replace the model's belief with a known prior
- **adversarial-paraphrase** — semantically equivalent but cosmetically misleading

These are not test-time augmentations — they are **factorial intervention design** at evaluation time, producing main effects + interactions + residual variance per the methodology paper §3 contribution claim.

### 7. Multiple oracle types

Not every economic game has a closed-form optimal policy. Oracle support tiers:
- **exact** — LP / DP / closed-form (ProductProcurementGame, simple matching)
- **Bayes** — Bayes-optimal given declared prior (NegotiationGame with declared opponent prior)
- **approximate** — bounded approximation with declared gap (PricingCompetitionGame multi-agent equilibrium)
- **dominance-only** — partial order (some moves strictly dominate; no exact best move ranking)
- **robust-tier** — minimax-style under uncertainty about opponent
- **human-reference** — expert / panel reference policy (when no algorithmic oracle exists)
- **market-simulation** — counterfactual simulator (for adaptive / repeated environments)

Each game declares its oracle certainty in metadata. Scoring transparency: a model isn't penalized for not matching an oracle when only dominance is declared.

## Substrate MVP scope (4 games — post-v0-paper follow-up paper; v0 first paper has NO shared substrate)

Per the top-of-doc banner: this substrate is a **post-v0-paper follow-up paper**, NOT v0 or v0.5. The v0 first paper ships 2 standalone games (ProductProcurementGame + VendorSelectionGame) implemented independently — no shared `aeread_env/` substrate code yet. The 4-game MVP below is the substrate scope for the follow-up paper, which only happens if the v0 paper establishes traction.

The 4 games span the structural-diversity matrix in design goal #2:

### ProductProcurementGame — v0 first paper, game 1
- Single-agent, one-shot
- Information: imperfect (qualitative evidence about products: reviews, specs, marketing)
- Action: structured purchase decision (product_id, quantity, optional bundle)
- Payoff: revealed-preference fit + dollar-equivalent surplus (per Q3 4-tier optimality scoring)
- Oracle (v0): **optimal under a single declared utility-weight vector per buyer profile** (per Q3 v0 scope — single-vector scoring); v0.5+ extension is the robust-optimal-across-plausible-utility-weight-family upgrade per Q3 v0.5+ scope. Either way, NOT a hidden-cardinal exact-optimum from a 0-1 scalar (that's the fake-precision failure Q3 prevents).
- Tests: Axis 1 (information processing from reviews) + Axis 4 (constraint satisfaction) + qualitative-evidence interpretation residual

### VendorSelectionGame — v0 first paper, game 2
- Single-agent, risk/uncertainty
- Information: supplier evidence (reliability history, lead-time variance)
- Action: select vendor + quantity, with explicit risk acknowledgment
- Payoff: expected cost - risk premium, revealed via stochastic resolution
- Oracle: **exact** (Bayes risk minimization given declared utility curvature)
- Tests: Axis 3 (calibration on risk) + Axis 4 (reliability-cost tradeoff) + belief-calibration residual
- Distinct from ProductProcurementGame: probabilistic risk + Bayes oracle here vs qualitative evidence + robust-utility oracle in C2. The pair demonstrates Eq. 4 across two distinct procurement-style structures.

### NegotiationGame — v0.5 roadmap
- Two-agent, sequential
- Information: private type (opponent's reservation value hidden)
- Action: structured offer/counteroffer with optional textual justification
- Payoff: agreed price - own reservation (zero if no agreement)
- Oracle: **Bayes-optimal** given declared opponent prior
- Tests: Axis 1 (belief update from opponent moves) + Axis 5 (calibration of belief stated vs revealed)

### PricingCompetitionGame — v0.5+ roadmap
- Multi-agent or repeated against simulator
- Information: imperfect (market state, opponent prices revealed with lag)
- Action: structured price posting
- Payoff: revenue captured over T rounds
- Oracle: **approximate** (declared gap to multi-agent equilibrium)
- Tests: Axis 2 (consistency across rounds) + Axis 4 (computational floor on adaptive policy)

This 4-game MVP costs ~$15-30K + 6-10 weeks of engineering. Each game can be developed independently. Submission/contribution API enables external researchers to add a 5th, 6th, etc.

## 10 hard constraints

Locked into the framework. Contributors must satisfy all 10 at submission time:

1. **Symbolic ground state exposed separately from text observations.** A model failing to parse the text observation is a text-understanding failure, not a decision-making failure. AERead-env separates these so the 5-axis attribution stays clean.
2. **Legal actions + invalid-action penalty taxonomy.** Six categories: invalid / constraint-violating / dominated / suboptimal / acceptable / optimal. Constraint-violating ≠ dominated; both signal different axis failures.
3. **At least one oracle or reference policy per game.** No oracle, no benchmark. Even when only dominance is declared, some reference is needed.
4. **At least one diagnostic intervention per game.** Minimum: baseline + paraphrase + constraint-explicit + state-revealed. No baseline-only games (those can't decompose failures).
5. **Declared OOD axes per game.** Domain / buyer_type / language_template / utility_regime / risk_model / opponent_policy — each contributor lists which apply.
6. **Anti-shortcut audits before inclusion.** No spurious correlates: option order, product_id, text length, price, brand mention, marketing positivity, hidden label leakage. None should predict the answer with > random baseline at acceptance.
7. **Seedable + reproducible.** `reset(seed=...)` / `generate_instance(seed=...)` / no uncontrolled randomness. Two runs with same seed must produce identical trajectories.
8. **Public + private split separation.** Public train generator, public dev set, private hidden certification (no answers shared), private hidden OOD set (no axis info shared until paper publication).
9. **Decomposable metrics.** Every game returns: outcome_score + constraint_violations + oracle_gap + dominated_action_taken + calibration_error + per-axis diagnostic_breakdown. Never a single opaque number.
10. **Declare what the game is NOT testing.** Prevents overclaiming. Example: ProductProcurementGame does NOT test multi-period adaptation, opponent modeling, or robust-decision-under-ambiguity. This forces honest scope statements.

## Architecture: six first-class interfaces

The substrate exposes six first-class interfaces. Each maps to a top-level directory in the module sketch.

| Interface | What it owns | Why first-class |
|---|---|---|
| **Game Interface** (`core/`) | state, observation, actions, transition, payoff | OpenSpiel-compatible game substrate |
| **Oracle Interface** (`oracles/`) | exact / Bayes / approximate / dominance / robust-tier / reference-policy / human-reference / market-sim | No oracle, no benchmark (constraint #3); 7 oracle types for non-closed-form games |
| **Behavioral Representation Interface** (`behavioral_rep/`) | utility calibration (KT '79 / CRRA / CARA / CPT '92 / Kelly-Markowitz multi-class fits); belief calibration (Brier / CRPS / ECE diagnostic); risk calibration; policy fitting | Methodology Layer 2 identification + Axis 3 calibration are first-class diagnostic outputs of every game — not afterthoughts wrapped around the oracle. Multi-class robustness (per methodology Q1) is implemented here. |
| **Diagnostic Intervention Interface** (`diagnostics/`) | reveal information / paraphrase / remove noise / relax constraint / change buyer / change opponent / change utility regime / Dutch-book probe / dominated-option injection | Factorial intervention design (per §3 methodology contribution claim) requires interventions to be first-class objects, not test-time augmentations |
| **Generalization Protocol** (`eval/splits.py`) | dev / hidden IID / axis-OOD / compositional-OOD / far-OOD / fresh seasons / counterfactual battery | Per Q1 hold-out-dimensions framing + AERead-Train/Dev/Cert tier separation |
| **LLM Adapter** (`adapters/`) | prompt formatting, structured action schema, tool-use handling, OpenSpiel + Gymnasium + lm-evaluation-harness bridges | Three adoption channels (OpenSpiel for RL research, Gymnasium for RL practitioner, lm-eval-harness for LLM eval) require explicit bridge code |

The **`behavioral_rep/`** module is the engineering counterpart to methodology Layer 2 (identification) — it's where multi-class utility fits live, where Bayesian posteriors over functional classes are computed, and where per-axis calibration scores (Brier, CRPS) get assembled. Treating it as a separate top-level module — rather than burying it inside `diagnostics/` — makes the 6-layer diagnostic stack (per methodology.md "Architecture mapping" section) visible at the architecture level.

**Module sketch**:

```
aeread_env/
  core/
    game.py            # base Game class with OpenSpiel-compatible API
    state.py           # symbolic ground state + textual observation
    action.py          # structured action schema + trace
    observation.py     # textual + symbolic observation wrappers
    trajectory.py      # full episode with intervention metadata
    registry.py        # game registration + metadata validation
  oracles/
    exact.py           # LP / DP / closed-form oracles
    bayes.py           # Bayes-optimal under declared prior
    dominance.py       # partial-order oracles
    approximate.py     # bounded-gap oracles
    robust_tier.py     # minimax oracles
    reference_policy.py # declared-policy reference for partial oracles
    human_reference.py # panel / expert reference
    market_sim.py      # counterfactual simulator
  behavioral_rep/
    utility_calibration.py  # multi-class MLE fits (KT/CRRA/CARA/CPT/Kelly-Markowitz)
    belief_calibration.py   # Brier / CRPS / ECE; Dutch-book probes
    risk_calibration.py     # within-class risk-preference parameter fits
    policy_fitting.py       # behavioral cloning of observed policy for diagnostic
  diagnostics/
    decomposition.py   # gap decomposition (Δ_inf / Δ_unc / Δ_ctrl)
    interventions.py   # paraphrase / state-reveal / constraint-explicit / etc.
    axioms.py          # de Finetti / Afriat / SARSEU checks
    calibration.py     # Brier / CRPS / ECE diagnostic
    robustness.py      # anti-shortcut audits
  games/
    procurement/
    negotiation/
    vendor_selection/
    pricing/
  adapters/
    llm_prompt.py      # textual observation rendering
    open_spiel_bridge.py
    gymnasium_bridge.py
  eval/
    runner.py
    scorer.py
    splits.py          # split manifest enforcement
    leaderboard.py
```

## Open design questions

1. **Naming**. "AERead-env" works as a working title. Alternatives: "OracleDecomp-env" (clearer about the abstraction), "Econ-Diagnostic-Suite" (clearer about the use case). Decision: defer until v0.5 ship.
2. **OpenSpiel integration depth**. Should AERead-env import OpenSpiel as a dependency (loose coupling — wrap their Game class) or just mirror the API? Loose coupling is easier; full integration may attract DeepMind attention. Decision: start with API mirror; consider tighter integration in v1 if collaboration emerges.
3. **lm-evaluation-harness integration**. EleutherAI's harness is the de-facto LLM eval framework. AERead-env should ship a harness adapter from day one. Cost: ~1 week additional engineering.
4. **Multi-agent infrastructure**. PricingCompetitionGame needs N-agent simulator infrastructure. Open question: is this in-scope for v0.5 or do we use the simpler repeated-vs-simulator setup?
5. **Contribution workflow**. How does an external researcher submit a new game? Likely PR + automated test suite (the 10 hard constraints become automated checks). v1 work.

## Sequencing (revised — NOT a v0.5 commitment)

- **v0 first paper**: 2 standalone games (C2 ProductProcurementGame + D3 VendorSelectionGame); no shared environment substrate. Each game is implemented standalone in v0 to fit the 3-4 person team × 16-week timeline.
- **v0.5+**: small extensions on the 2 v0 games (the deferred items per methodology.md Q3/Q4/Q5/Q6 v0.5+ tags) — NOT the AERead-env substrate.
- **Post-v0 follow-up paper** (timing depends on v0 traction; not pre-committed): the AERead-env substrate as described in this doc. Becomes a *separate* paper ("AERead-env: an OpenSpiel-compatible substrate for economic-agency evaluation") rather than v0.5 or v1 of the v0 paper. The 4-game MVP + 6-interface architecture is months of engineering — worth doing only if the v0 paper establishes traction + a frontier-lab partner pre-commits to citing the substrate paper.
- **Conditional v1+**: if a follow-up paper publishes, then community-contribution API + lm-evaluation-harness adapter + 1-2 community-contributed games extend the substrate.

Engineering ownership: post-v0-paper-publication conversation, not part of the v0 collaboration ask. The 4-game MVP is naturally Cheney+Yuecheng's joint scope IF the substrate paper happens — but that's a separate decision from the v0 ownership map in proposal §9.5.

## References

- OpenSpiel (DeepMind): https://github.com/deepmind/open_spiel
- TERMS-Bench oracle decomposition: [`papers/links.md`](papers/links.md) Anchor papers
- Andrews 2026 training-time penalty mechanism: [`papers/links.md`](papers/links.md) 5-axis anchors
- AERead methodology Q&A: [`methodology.md`](methodology.md) "Critical methodological questions"
- AERead Layer 3 candidate matrix: [`layer3_candidates.md`](layer3_candidates.md) F12 / F15 / F16 / F17
- lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness
