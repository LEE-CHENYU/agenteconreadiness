# AgentEcon Readiness (AERead)

**Is your agent ready for the economy?**

AERead is a unified benchmark for LLM rational economic decision-making. It measures performance on **real-world economic use cases** — procurement, vendor selection, persona-fit investment, bargaining, agentic tool selection — by **economic value** (dollar surplus, oracle-gap utility, predictive accuracy on revealed-preference data).

The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed via a 5-axis failure taxonomy.

---

## Status

Pre-launch. v0 runtime in development; methodology paper targeting NeurIPS / COLM 2026. This repo is currently private and serves as the canonical artifact for the research-collaboration proposal.

## Pre-commercial final goal: methodological engagement from frontier labs

AERead's pre-commercial deliverable is the methodology paper + reproducible v0 runtime. The citation channel we're optimizing for is **methodological engagement** from frontier-lab safety + economics-of-AI researchers — not adoption traction alone. Every design choice is structured to invite engagement *before* the methodology paper circulates:

- Nine open methodological questions with stated working positions + "Open:" invitations — function misspecification (Q1), numeric-feature evaluation (Q2), qualitative-feature scoring discipline (Q3), generalization battery (Q4), RL training-signal mechanisms (Q5), TERMS-Bench-as-training-signal overfitting + AERead-Train/Dev/Cert (Q6), Layer 1+2 vs Layer 3 residual hypothesis (Q7), OpenSpiel-compatible environment substrate (Q8), operational emergence definition (Q9) — [`docs/methodology.md` § Critical methodological questions](docs/methodology.md#critical-methodological-questions-open-qa)
- Pre-registered factorial hypothesis with per-domain explanatory-power estimates (60-75% procurement → 25-50% long-horizon agents) + falsification criteria — [`docs/methodology.md` § Q7](docs/methodology.md#q7--how-much-of-the-per-model-task-gap-do-layers-1--2-explain-whats-the-residual)
- Counterexample submission channel for the OracleDecomposable abstraction — [`docs/methodology.md` § How to engage](docs/methodology.md#how-to-engage-pre-commercial-final-goal)
- OpenSpiel-compatible substrate with 10-hard-constraint contribution API (v0.5) — [`docs/aeread_env_design.md`](docs/aeread_env_design.md)
- Open candidate pool for new Layer 3 use cases on a value × testability matrix — [`docs/layer3_candidates.md`](docs/layer3_candidates.md)

Engagement channel: contact details in [`docs/proposal.md` §15](docs/proposal.md).

## Repository contents

| File | Purpose |
|---|---|
| [`docs/proposal.md`](docs/proposal.md) | Research-collaboration proposal (the document this repo was created to host) |
| [`docs/methodology.md`](docs/methodology.md) | Condensed methodology: 3-layer pipeline + 5-axis failure taxonomy + OracleDecomposable abstraction |
| [`docs/prior_art_brief.md`](docs/prior_art_brief.md) | 3-page primer on the anchor benchmarks AERead integrates (TERMS-Bench / Andrews 2026 / EconEvals) — what each contributes + what AERead inherits + extends |
| [`docs/layer3_candidates.md`](docs/layer3_candidates.md) | Open candidate pool of ~25 Layer 3 real-world economic decision use cases on a value × testability matrix (v0 + expansion roadmap) |
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

None we know of integrate the three. **AERead is the integrated benchmark.**

## Core methodology

### The 3-layer pipeline (canonical revealed-preference)

| Layer | Question | Method |
|---|---|---|
| 1 — existence | Does any rationalizing utility exist? | Axiomatic compliance (CCEI / GARP / WARP / transitivity / monotonicity) |
| 2 — identification | Within a functional class, which utility parameters fit? | Multi-class MLE on training portion; Bayesian posterior over classes |
| 3 — predictive validity | Does the identified utility predict held-out choices? | Predict-then-validate on held-out test set; predictive accuracy as headline score |

### The 5-axis failure taxonomy

When a model scores low, the diagnostic page identifies which axis is to blame:

1. **Information** — agent lacks knowledge of hidden state (TERMS-Bench / OracleDecomposable)
2. **Consistency** — agent's preferences violate axioms (Andrews 2026)
3. **Calibration** — agent's economic parameters are misfit (Mazeika 2025; Guo 2017 ECE; Gneiting-Raftery 2007 proper scoring rules)
4. **Computational floor** — agent can't execute the math (novel)
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
- One-line evaluation: `pip install aeread && aeread evaluate --model claude-opus-4-7 --task all`
- **v0: one submission path** (web form); Colab + PR paths defer to v0.5+
- Integration AS lm-evaluation-harness task family — so labs already running `lm_eval` have us installed
- Cache layer never invalidates — reviewer reproducibility is a hard guarantee (signed-ScoreRecord enforcement defers to v0.5+)

## License

MIT. See [LICENSE](LICENSE).

## Contact

Cheney Li — fretin13@gmail.com
