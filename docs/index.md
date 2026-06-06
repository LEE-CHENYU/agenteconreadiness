# AgentEcon Readiness (AERead)

A methodology and a set of instruments for measuring how well LLMs make **economic
decisions** — leading with the **exact-exploitability (best-response) channel**: the
value an optimal adversary can extract from a model's strategy, which is `0` only
when the model is perfectly coherent.

This page is a v0 reference index for the docs cited in design discussions.

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

## Reference pages

Short explainers for terms and works cited in design discussions — **[ref/](ref/)**
(MDP, imperfect recall, best-response/exploitability, Nash equilibrium, Kuhn poker,
TERMS-Bench, Vending-Bench, current test results).

## Broader methodology

- [Methodology overview](methodology.html)
- [Prior-art brief](prior_art_brief.html)
- [Open questions](methodology_open_questions.html)
- [AERead environment design](aeread_env_design.html)
- [Architecture](ARCHITECTURE.html)

---

Repository: [github.com/LEE-CHENYU/agenteconreadiness](https://github.com/LEE-CHENYU/agenteconreadiness)
