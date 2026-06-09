# Coverage expansion: 12 new cases, and why we don't claim a new axis count

**Summary.** We built 12 new exploitation cases across the multi-agent / market / mechanism quadrant — all with
exact (or declared-prior) oracles, de-leaded prompts, independently oracle-verified, and (with two exceptions)
frontier-discriminating. We then tried to test whether they add *latent axes* via PCA. The honest result is a
**negative methodological finding: the latent-axis count is not robustly estimable with the available models.**
The PCA rank is highly sensitive to the model set, and a "fold" taxonomy an earlier draft of this page reported
did **not** replicate across model sets — so it is retracted. What survives is per-case, not per-axis: the
original frontier structure is low-rank (~4), the 12 new cases are built and (mostly) discriminate, and there is
one clean flat result on ultimatum bargaining.

## What we built (this part is solid)
12 cases, each oracle-verified by an *independent* re-derivation, de-leaded, and beats-random: `bandit`,
`stackelberg`, `vickrey`, `bertrand_ic`, `allais`, `blotto`, `winners_curse`, `blotto_maximin`,
`stackelberg_robust`, `allpay`, `bargaining_responder`, `pandora`. Per-case cross-model discrimination (std over
18 models) shows all are live (0.11–0.39) **except `bargaining_responder` (0.000 — see below)** and `vickrey`
(weak, 0.11).

## The negative methodological finding (the real result)
We attempted a model×case PCA to count latent axes. It does not hold up, for three reasons:

1. **Rank is a model-set artifact.** On the *identical* original cases, a capability-removed PCA (row-centered)
   gives **4 components on frontier models but 7 once small (1B–30B) models are added.** Row-centering removes
   each model's capability *level* but not its *idiosyncrasy* — weaker models fail more erratically, which
   manufactures extra apparent components. So a "rank rose to ~8" framing is mostly the model set, not the new
   cases.
2. **The "fold test" did not replicate.** Nearest-anchor correlations flip entirely between model sets: e.g.
   `blotto`/`stackelberg` read as folding into `gamble` (calculation) on the mixed set but into `kuhn` on
   frontier-only; `blotto_maximin` reads "distinct" on the mixed set but folds into `kuhn` (0.72) on
   frontier-only. The assignments are driven by which cases happen to have variance in each set — `gamble` is
   near-constant on frontier, so nothing can fold into it there, while small models leak on `gamble` and create
   spurious "folds-into-calc" correlations. **We retract the fold taxonomy** as unsupported by the data.
3. **The count is under-determined.** A clean frontier-only PCA needs many more models than the ~8 distinct
   frontier-class models that exist (PCA rank ≤ models − 1), so the axis count for a 20+ case battery cannot be
   resolved on frontier models at all.

**Conclusion:** characterize exploitability **per case** (oracle + discrimination), not via a fragile global
PCA axis-count. The latent-axis framing is a useful hypothesis but is not currently estimable to a defensible
number. The original ~4-rank result stands *only* as a frontier-model statement (see
[PCA experiment](pca-experiment.html)), and even that rests on ~8 models, so treat it as soft.

## A solid per-case finding
**`bargaining_responder` is flat (std 0.000):** every model — 1B to frontier — accepts strictly-positive
ultimatum offers. Frontier LLMs show **no ultimatum / fairness-driven rejection** of small positive offers, so
the case is economically "rational" and does not discriminate. A real result (it refutes the conjecture that
LLMs inherit human spite on lopsided splits), independent of the PCA issues.

## What would resolve the axis question
The binding constraint is the number of *frontier-class* models, not cases. Resolving the latent-axis count
would need many more high-capability models on a fixed case set (without the small-model capability confound),
or abandoning the global axis-count in favor of pairwise per-case redundancy tests *within a consistent model
tier*. Until then, AERead reports verified, discriminating cases — not a claimed axis count.

**See also.** [PCA experiment](pca-experiment.html) · [games by solvability](games-by-solvability.html) ·
[research design](research-design.html).
