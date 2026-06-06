# Vending-Bench

**Summary.** Vending-Bench (Andon Labs, 2025) is a **long-horizon coherence** benchmark: an LLM runs a
simulated vending business — procure stock, set prices, pay fees — over a very long horizon (~20M tokens),
scored by **final net worth**, a single dollar value. Its strength is a real end-to-end **dollar outcome**;
its weakness is that the score is **not decomposable** — you cannot attribute the ±$ to which sub-task failed.

**As used in the 2026-06-05 sync.** It is the "aggregated but non-decomposable" pole of the central contrast
(vs [TERMS-Bench](terms-bench.html), "decomposable but single-setting"). Useful for general cross-model
ranking, but it can't localize *why* a model failed or serve cleanly as a training signal — which motivates
AERead's aggregation-with-decomposability target. (Separately cited in our methodology for the observed
**alignment ↔ economic-performance tension**: Opus 4.8 shows better alignment but falls for scam suppliers and
non-convergent planning loops.)

**External references.** [arXiv 2502.15840](https://arxiv.org/abs/2502.15840) ·
[Andon Labs writeup](https://andonlabs.com/blog/opus-4-8-vending-bench).
