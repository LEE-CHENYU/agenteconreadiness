# AgentEcon Readiness (AERead)

**Is your agent ready for the economy?**

AERead is a unified benchmark for LLM rational economic decision-making. It measures performance on **real-world economic use cases** — procurement, vendor selection, persona-fit investment, bargaining, agentic tool selection — by **economic value** (dollar surplus, oracle-gap utility, predictive accuracy on revealed-preference data).

The leaderboard reports a deployment verdict; the drill-down page reports *why* a model failed via a 5-axis failure taxonomy.

---

## Status

Pre-launch. v0 runtime in development; methodology paper targeting NeurIPS / COLM 2026. This repo is currently private and serves as the canonical artifact for the research-collaboration proposal.

## Repository contents

| File | Purpose |
|---|---|
| [`docs/proposal.md`](docs/proposal.md) | Research-collaboration proposal v0.2 (the document this repo was created to host) |
| [`docs/methodology.md`](docs/methodology.md) | Condensed methodology: 3-layer pipeline + 5-axis failure taxonomy + OracleDecomposable abstraction |
| [`docs/reading_list.txt`](docs/reading_list.txt) | T1 / T2 / T3 prior-art reading list with [AXIS-N] anchor flags |
| [`docs/papers/_INDEX.md`](docs/papers/_INDEX.md) | Annotated index of cited papers (curated reading guide) |
| [`docs/papers/references_master.yaml`](docs/papers/references_master.yaml) | Machine-readable bibliography (~160 entries, deduped from 3 anchor papers) |

## The thesis

LLM agents are being deployed for economic decisions — a 2025 Anthropic publication reports **5.9% of Claude API conversations are economic decisions**; JPMorgan announced LLM-agent shareholder voting; Visa announced AI shopping agents. Whether these deployments satisfy the rationality assumptions the use cases presuppose has not been validated at scale.

Three Q1-2026 benchmark papers from elite teams stake claims in three separate corners of this problem:

- **Stanford TERMS-Bench** (Zhang/Athey/Roth-advising, May 2026) — bilateral negotiation outcome layer
- **Harvard EconEvals** (Fish/Gonczarowski, Feb 2026) — procurement/scheduling/pricing parameter + outcome layer
- **MIT Revealed Rationality** (Andrews, Feb 2026) — label-free representation-theorem penalties at the axiom layer

None integrate the three. **AERead is the integrated benchmark.**

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
3. **Calibration** — agent's economic parameters are misfit (Mazeika 2025)
4. **Computational floor** — agent can't execute the math (novel)
5. **Meta-cognitive** — agent's confidence is uncalibrated (Yamin / Chadwick)

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
- Three submission paths (web form / Colab / PR)
- Integration AS lm-evaluation-harness task family — so labs already running `lm_eval` have us installed
- Cache layer never invalidates — reviewer reproducibility is a hard guarantee

## License

MIT. See [LICENSE](LICENSE).

## Contact

Cheney Li — fretin13@gmail.com
