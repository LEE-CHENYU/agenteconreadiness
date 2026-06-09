# Coverage expansion: 12 new cases, and why the axis count isn't the headline

**Summary.** We built 12 new exploitation cases across the multi-agent / market / mechanism quadrant — each
with an exact (or declared-prior) oracle, a de-leaded prompt, an independent oracle-verification, and (with two
exceptions) frontier-discrimination. We then asked whether they add *latent axes*. The answer is methodological:
**the latent-axis count is not robustly estimable from the available models — it is sensitive to the model
panel — so AERead reports exploitability *per case*, not as a global axis-count.** On a consistent frontier
panel the construct is low-rank (~4–6).

## What we built (the robust layer)
12 cases: `bandit`, `stackelberg`, `vickrey`, `bertrand_ic`, `allais`, `blotto`, `winners_curse`,
`blotto_maximin`, `stackelberg_robust`, `allpay`, `bargaining_responder`, `pandora`. Each oracle is
independently re-derived; per-case cross-model discrimination is measured. **This per-case layer is what AERead
reports** — exact oracle + discrimination, contamination-resistant via per-instance regeneration.

## Why the axis count is not the headline
A model×case PCA does not yield a stable axis count on this data, for three reasons:

1. **It depends on the model panel.** On the *identical* cases, the rank is low (~4) on frontier models but
   inflates once small (1B–30B) models are added — weaker models fail more erratically, manufacturing extra
   apparent components. Centering out capability *level* does not remove this.
2. **Per-case groupings are unstable across panels.** Which axis a case appears to belong to shifts with the
   set of models included, driven by which cases happen to have variance in each panel.
3. **The count is under-determined.** There are only ~10–15 distinct frontier-class model lineages, and PCA
   rank ≤ (models − 1), so a 20+ case axis-count cannot be resolved on frontier models alone.

**So the reportable object is per-case** (exact oracle + cross-model discrimination). The latent-axis grouping
is a useful design lens, but the frontier construct is low-rank (~4–6), and that is as precise as the available
models support.

## A per-case finding worth noting
**`bargaining_responder` is flat:** every model — 1B to frontier — accepts strictly-positive ultimatum offers.
Frontier LLMs show **no fairness / spite-driven rejection** of lopsided splits, so the case is economically
"rational" and does not discriminate. (It refutes the conjecture that LLMs inherit human ultimatum behaviour.)

## What would sharpen it
The binding constraint is the number of *frontier-class* lineages, not cases. A larger frontier panel would
firm the rank within the ~4–6 band; pairwise per-case redundancy tests within a single model tier are the
alternative to a global axis-count. Until then, AERead reports verified, discriminating cases.

**See also.** [Test results](exploitability-test-results.html) · [PCA experiment](pca-experiment.html) ·
[games by solvability](games-by-solvability.html) · [research design](research-design.html).
