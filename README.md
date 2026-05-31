# AgentEcon Readiness (AERead)

**Is your agent ready for the economy?**

AERead is an **economic-decision diagnostic for LLM agents**. It measures performance on **real-world economic use cases** — procurement, vendor selection, persona-fit investment, bargaining, agentic tool selection — by **economic value** (dollar surplus, oracle-gap utility, predictive accuracy on revealed-preference data).

A 2026-05-29 validation sprint sharpened the thesis: "is the agent *rational*?" is a **saturated floor** for frontier models (table stakes, not a discriminator). The discriminating, durable axes are the **grade** — **regime-appropriateness** (does it deploy the right utility: EV / Kelly / CVaR / CRRA?), the **alignment↔economic-behavior shift**, and **steerability** (faithful representation of a configured principal). Read as a hierarchy this is a **gate → grade** pipeline; the contribution is the **diagnostic lens**, not a new game suite. The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed via a 5-axis failure taxonomy.

> **Start here:** [`docs/refocus.md`](docs/refocus.md) — the post-sprint synthesis (current state). Then [`docs/proposal.md`](docs/proposal.md) (the collaboration ask, v0.4) and [`docs/methodology.md`](docs/methodology.md) (the framework).

---

## Status

Pre-launch. v0 runtime in development; methodology paper targeting NeurIPS / COLM 2026. This repo is public and serves as the canonical artifact for the research-collaboration proposal + methodology.

## Pre-commercial final goal: methodological engagement from frontier labs

AERead's pre-commercial deliverable is the methodology paper + reproducible v0 runtime. The citation channel we're optimizing for is **methodological engagement** from frontier-lab safety + economics-of-AI researchers — not adoption traction alone. Every design choice is structured to invite engagement *before* the methodology paper circulates:

- Fourteen open methodological questions (Q1-Q14, incl. Q14 — what training signal AERead emits: the oracle-decomposed *process* signal recovers economic competence without reviving the misbehavior alignment removed) with stated working positions + "Open:" invitations — full bodies in [`docs/methodology_open_questions.md`](docs/methodology_open_questions.md); navigation pointer + topic-index in [`docs/methodology.md`](docs/methodology.md#critical-methodological-questions-open-qa)
- Pre-registered factorial hypothesis with per-domain explanatory-power estimates (60-75% discrete-action procurement → 50-70% continuous-action pricing → 25-50% long-horizon agents) + falsification criteria — [`docs/methodology_open_questions.md` § Q7](docs/methodology_open_questions.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual)
- Counterexample submission channel for the OracleDecomposable abstraction — [`docs/methodology.md` § How to engage](docs/methodology.md#how-to-engage-pre-commercial-final-goal)
- OpenSpiel-compatible substrate with 10-hard-constraint contribution API (post-v0-paper follow-up paper, NOT v0.5) — [`docs/aeread_env_design.md`](docs/aeread_env_design.md)
- Depth-first candidate map for Layer 3 use cases: value × testability, plus the uncovered questions current results create — [`docs/layer3_candidates.md`](docs/layer3_candidates.md)

Engagement channel: contact details in [`docs/proposal.md` §15](docs/proposal.md).

## Repository contents

| File | Purpose |
|---|---|
| [`docs/proposal.md`](docs/proposal.md) | Research-collaboration proposal (the document this repo was created to host) |
| [`docs/v0_sprint.md`](docs/v0_sprint.md) | **Consolidated operational view** — v0 implementation scope, ownership map for the ~13 workstreams, phase timeline, v0.5+ deferral roadmap. One-stop scan for the team. |
| [`docs/refocus.md`](docs/refocus.md) | **Read first** — post-validation-sprint synthesis (2026-05-29): rationality is a saturated floor; the discriminating axes are regime-appropriateness + alignment-shift + steerability; the contribution is the diagnostic lens (gate→grade); goal-dimension space; semi-verifiable direction |
| [`docs/methodology.md`](docs/methodology.md) | Methodology framework: 3-layer pipeline + 5-axis failure taxonomy + gate→grade reading + OracleDecomposable abstraction + topic-index pointer to the 14-Q open-questions doc |
| [`docs/methodology_open_questions.md`](docs/methodology_open_questions.md) | Full bodies + tables for the 14 open methodological questions (Q1-Q14) — function misspecification / numeric scoring / qualitative scoring / generalization battery / RL mechanisms / training-signal contamination / Layer 1+2 residual hypothesis / OpenSpiel substrate / emergence / training-signal validation / gate-vs-grade / stress as a cross-cutting axis / adversarial co-evolution / training-signal emission (process-vs-outcome) |
| [`docs/aeread_env_design.md`](docs/aeread_env_design.md) | Post-v0-paper substrate roadmap — forward-looking OpenSpiel-compatible substrate design for a separate follow-up paper (NOT v0.5) |
| [`docs/prior_art_brief.md`](docs/prior_art_brief.md) | 3-page primer on the anchor benchmarks AERead integrates (TERMS-Bench / Andrews 2026 / EconEvals) — what each contributes + what AERead inherits + extends |
| [`docs/layer3_candidates.md`](docs/layer3_candidates.md) | Depth-first Layer 3 candidate map: value × testability, economic-stakes × oracle-status, and result-driven uncovered directions for v0.5+ |
| [`docs/reading_list.txt`](docs/reading_list.txt) | T1 / T2 / T3 prior-art reading list with [AXIS-N] anchor flags |
| [`docs/papers/links.md`](docs/papers/links.md) | One-stop citation links — every cited paper mapped to a public URL or repo-hosted PDF |
| [`docs/papers/_INDEX.md`](docs/papers/_INDEX.md) | Deep-dive synopses (~5-6 paragraphs each) for 12 supporting-literature papers — complements `reading_list.txt` (the priority guide) |
| [`docs/papers/references_master.yaml`](docs/papers/references_master.yaml) | Machine-readable bibliography (~160 entries, deduped from 3 anchor papers) |
| [`docs/papers/pdfs/`](docs/papers/pdfs/) | PDFs of cited papers without public URLs (Andrews 2026, Chadwick 2025, Gneiting & Raftery 2007) |

## The thesis

LLM agents are being deployed for economic decisions — a 2025 Anthropic publication reports **5.9% of Claude API conversations are economic decisions**; JPMorgan announced LLM-agent shareholder voting; Visa announced AI shopping agents. Whether these deployments satisfy the rationality assumptions the use cases presuppose has not been validated at scale.

Three recent benchmark papers from elite teams (spanning March 2025 to May 2026) stake claims in three separate corners of this problem:

- **Harvard EconEvals** (Fish/Gonczarowski, March 2025) — procurement/scheduling/pricing parameter + outcome layer
- **MIT Revealed Rationality** (Andrews, February 2026) — label-free representation-theorem penalties at the axiom layer
- **Stanford TERMS-Bench** (Zhang/Athey/Roth-advising, May 2026) — bilateral negotiation outcome layer

None we know of integrate the three — but, post-sprint, **integration is the *substrate*, not the contribution** (AERead borrows these environments). The contribution is the **diagnostic lens** (gate→grade + the headline axes: regime-appropriateness, alignment-shift, steerability) run across them, plus controllable probes for what they can't expose. The field independently draws the same line we did: single-agent / short-horizon / known-environment is saturated; the deployment-pressure regimes are where models discriminate (see [`docs/refocus.md`](docs/refocus.md)).

## Core methodology

### The 3-layer pipeline (canonical revealed-preference), read as gate → grade

Layer 1 (existence/coherence) is the **gate** — a pass/fail floor frontier models clear (saturated); Layers 2–3 culminating in fidelity to a configured/revealed principal are the **grade** — the discriminating headline. The table is the machinery; the gate→grade reading is the prioritization.

| Layer | Question | Method | Gate/grade |
|---|---|---|---|
| 1 — existence | Does any rationalizing utility exist? | Axiomatic compliance (CCEI / GARP / WARP / transitivity / monotonicity) | **gate** (floor) |
| 2 — identification | Within a functional class, which utility parameters fit? | Multi-class MLE on training portion; Bayesian posterior over classes | machinery |
| 3 — predictive validity | Does the identified utility predict held-out choices? | Predict-then-validate on held-out test set; predictive accuracy as headline score | **grade** (headline) |

### The 5-axis failure taxonomy

When a model scores low, the diagnostic page identifies which axis is to blame:

1. **Information** — agent lacks knowledge of hidden state (TERMS-Bench / OracleDecomposable)
2. **Consistency** — agent's preferences violate axioms (Andrews 2026)
3. **Calibration** — agent's economic parameters are misfit (Mazeika 2025; Guo 2017 ECE; Gneiting-Raftery 2007 proper scoring rules)
4. **Computational floor** — agent can't execute the math (EconEvals 2025 competency-as-prerequisite is the closest precedent; AERead extends to per-axis quantity-substitution decomposition)
5. **Meta-cognitive** — agent's confidence is uncalibrated (Yamin 2026; Zhu & Griffiths 2024; Chadwick 2025)

See [`docs/methodology.md`](docs/methodology.md) for the full description.

## Methodological commitments

1. **Descriptive measurement, not normative ranking** — higher AERead scores ≠ better-aligned
2. **Measurement-model pluralism** — 4-6 competing models per axiom; Bayesian posterior
3. **Judge-free by construction** — no LLM evaluates another LLM in the scoring pipeline
4. **Context-conditional axiomatization** — personas degrade axiom compliance; this is measured, not assumed away
5. **Cross-layer attribution + oracle-gap decomposition** — actionable diagnostic signal, not just a score

## Plug-and-play design

Adoption traction analysis (25 benchmarks studied) found that benchmarks > 200 cites without a live leaderboard + frontier-lab partner + ≤ 5-minute clone-to-first-output do not exist. AERead therefore commits to:

- Zero-code task contribution via YAML
- One-line evaluation: `pip install aeread && aeread evaluate --model claude-opus-4-8 --task all`
- **v0: one submission path** (web form); Colab + PR paths defer to v0.5+
- Integration AS lm-evaluation-harness task family — so labs already running `lm_eval` have us installed
- Cache layer never invalidates — good-hygiene reproducibility (cache hashes externally auditable; signed-ScoreRecord cryptographic provenance defers to v0.5+)

## License

MIT. See [LICENSE](LICENSE).

## Contact

Chenyu Li — fretin13@gmail.com
