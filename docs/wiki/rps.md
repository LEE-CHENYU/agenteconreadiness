# Rock-Paper-Scissors (RPS)

**Summary.** RPS is the channel's worked example and its sharpest *randomization* probe: the unique unexploitable
strategy is uniform `(1/3, 1/3, 1/3)`, so any predictable structure in a model's play is directly extractable.
Models are notably bad at this — they cannot emit good randomness — so dynamic matrix games are where they lose
most.

## Basic test setting

- **API only — no model training.** The model is given the rules and plays round-by-round, emitting one move per
  round (single-letter `R`/`P`/`S`, artifact-proof to parse).
- The harness records the move history and computes two exact exploitability measures per round (`eps_cond ≥
  eps_marg`):
  - **`eps_marg`** — the best *fixed* counter-action against the model's move **frequencies**.
  - **`eps_cond`** — the best **1st-order pattern-aware** exploiter, using `P(next move | last move)` — catches
    uniform-but-predictable play (e.g. a `R,P,S,R,P,S` cycle: `eps_marg = 0` but `eps_cond = 1`).
- **Adaptive variant** ([`adaptive_rps`](games-by-solvability.html)): the model plays `T` rounds against an
  adversary that best-responds round-by-round to its observed play, and we track the per-round extraction
  *trend* (a [lower bound](games-by-solvability.html), since the fixed adversary is itself beatable).

## Test results

- **Static:** models with predictable play (e.g. cyclers) are highly exploitable on `eps_cond`; weighted-RPS
  adds an equilibrium-computation load (uniform play is *not* optimal there).
- **Adaptive:** four regimes — gpt-5.5 *counter-exploits* the adversary, Sonnet 4.6 stays near the floor,
  DeepSeek-V3 self-corrects, Haiku 4.5 degrades. Full numbers: [test results](exploitability-test-results.html)
  and the channel writeup [`exploitation_channel.md`](../exploitation_channel.html).

**Why it's a [game](research-design.html), not single-agent.** RPS requires *reacting to an evolving opponent*
— the inference/adaptation content that distinguishes it from one-shot decisions.
