# AgentEcon Readiness (AERead)

A methodology and a set of instruments for measuring how well LLMs make **economic
decisions** — leading with the **exact-exploitability (best-response) channel**: the
value an optimal adversary can extract from a model's strategy, which is `0` only
when the model is perfectly coherent.

This page is a v0 reference index for the docs cited in design discussions.

**New:** [**AERead — results so far**](wiki/results.html) is a single comprehensive read of
the findings to date — the Opus 4.8 Kuhn regression, the randomization deficit and its
architectural fix, the coverage/PCA construct, the exact-oracle store-sim boundary, and the
open competition direction.

## Exploitation channel

- **[Channel writeup — `exploitation_channel.md`](exploitation_channel.html)**
  The cases (RPS, weighted-RPS, gamble, pricing/procurement, procedure-invariance,
  cross-modality, Kuhn poker, adaptive RPS), what each measures, the noise floor,
  and live results.
- **[Methodology & foundations — `exploitation_foundations.md`](exploitation_foundations.html)**
  The payoff matrix as primitive, the two oracles, optimization levels (MDP ↔
  non-MDP), best-response vs Nash vs negotiation-surplus, estimating a model's fixed
  policy, commensuration, and aggregation.
- **Source — `channel.py`:**
  [`aeread_lab/exploitation/channel.py`](https://github.com/LEE-CHENYU/agenteconreadiness/blob/main/aeread_lab/exploitation/channel.py)

## Wiki

Short explainers for the design logic, terms, and works behind the channel — **[wiki/](wiki/)**:

- **Research design** — [design logic](wiki/research-design.html),
  [comparability & output format (scalar vs vector)](wiki/comparability-output-format.html),
  [games by solvability](wiki/games-by-solvability.html),
  [RLVR](wiki/rlvr.html)
- **Concepts** — [MDP](wiki/mdp.html), [imperfect recall](wiki/imperfect-recall.html),
  [best response & exploitability](wiki/best-response-exploitability.html),
  [Nash equilibrium](wiki/nash-equilibrium.html), [RPS](wiki/rps.html), [Kuhn poker](wiki/kuhn-poker.html)
- **External** — [TERMS-Bench](wiki/terms-bench.html), [Vending-Bench](wiki/vending-bench.html)
- **Results** — [results so far (overview)](wiki/results.html),
  [PCA experiment](wiki/pca-experiment.html),
  [test results](wiki/exploitability-test-results.html)

---

**Contributors:** Yuchen Fang, Zihao Li, Allen Han, Zeyu Sun. (Maintainer: [LEE-CHENYU](https://github.com/LEE-CHENYU) / Chenyu Li — see footer.)

Repository: [github.com/LEE-CHENYU/agenteconreadiness](https://github.com/LEE-CHENYU/agenteconreadiness)
