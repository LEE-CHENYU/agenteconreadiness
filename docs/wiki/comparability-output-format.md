# Comparability & output format (scalar vs vector)

**Summary.** The central open question from the 2026-06-05 sync: each game produces exploitability in a *different
currency* (per-round value, EV-per-bet, regret fraction, antes/hand), so before you can aggregate you must make
them **comparable** (commensuration), and then decide whether the headline is a **scalar or a vector**. Our
position: commensurate every case to **[0,1] "fraction of extractable surplus conceded,"** report a **vector**
over the ~3 [PCA axes](pca-experiment.html) plus a single ranking, and reserve a dollar scalar for a specific
deployment.

## Commensuration: pick one currency, own its cost

Heterogeneous-task benchmarks all use one of five strategies:

| strategy | common unit | example | cost |
|---|---|---|---|
| reference-anchored normalization | `(model−naive)/(optimal−naive)` → [0,1] | DQN human-normalized; BIG-bench | needs defensible anchors; hides magnitude |
| common numeraire | dollars / equivalent variation | economics; our regret-in-$ | summing $ only valid under **exposure weights** |
| rank / pairwise | win-rate / Elo | Chatbot Arena, HELM | discards *how much* better |
| latent-trait (IRT) | ability θ | psychometrics, tinyBenchmarks | assumes — and must test — one latent factor |
| proper scoring rules | nats / bits | forecasting / calibration | only when the output is a probability |

AERead already has the **same concept** in every case — *regret = adversary extraction, optimal = 0* — so it
inherits economics' money-metric numeraire (an advantage over GLUE-style macro-averaging of incommensurable
metrics).

## Scalar or vector?

Two bounds:

1. **Scale still differs within "regret."** Most cases are pre-normalized to [0,1]; [Kuhn](kuhn-poker.html)
   (antes/hand) and `adaptive_rps` (a *curve*) must be normalized/reduced first (a curve → area-under-extraction
   = cumulative regret).
2. **The construct is not unidimensional.** The [PCA experiment](pca-experiment.html) finds ~3 axes; a single
   scalar would erase the calc-vs-coherence and strategic dissociations that *are* the finding.

**Consequent default:** per-case normalized exploitability ∈ [0,1] → a **profile vector** over the axes + one
mean-win-rate for ranking (the HELM stance); a dollar scalar **only** for a within-deployment exposure-weighted
sum (the one place adding dollars is licensed). The two decisions — *commensuration* (which unit) and *the
functional* (mean / max / CVaR over the vector) — are kept separate.

**Relevant part of our docs.** Full treatment:
[`exploitation_foundations.md` → "Making cases comparable" and "Aggregating across cases"](../exploitation_foundations.html).
Connects to the broader [research design](research-design.html) (aggregation is step 1 of the plan).
