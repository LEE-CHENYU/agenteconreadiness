# PCA experiment (latent axes of exploitability)

**Summary.** To check whether the games measure **distinct** failure modes (and therefore whether a single
scalar could ever summarize a model), we build a **model × case** matrix of exploitability, z-score per case,
and run PCA. The result: the construct is **not unidimensional** — ~3 interpretable axes over 4 case clusters —
which is the empirical argument against collapsing AERead to one number.

## Method

- Tool: `sprint/exploit_pca.py` (research tooling — numpy/scipy, not part of the artifact-proof package).
- Build a live matrix: each model plays each [statically-solvable](games-by-solvability.html) case; the entry is
  its exploitability (`eps_cond` for matrix games, `eps`/regret otherwise).
- Z-score per case (so a case's *spread* across models, not its absolute scale, drives the axes), then SVD;
  cluster cases by correlation distance.

## Result (10 models × 9 cases)

**4 stable case clusters:** `{rps, cyclic7, wrps}` (randomization / equilibrium), `{proc_invariance,
cross_modality}` (procedure coherence), `{gamble}` (EV calculation), `{kuhn_poker}` (strategic / extensive-form).

**3 interpretable axes** (4 components to 90% variance):

| axis | var | type | what it measures |
|---|---|---|---|
| **PC1** | 43% | general factor (almost all cases load one way) | overall exploitability — broadly leaky vs broadly robust. Gamble ~0; Kuhn flips sign |
| **PC2** | 26% | contrast (mixed signs) | *where* the leak sits — surface calc/randomization vs procedure coherence. Gemini-2.5-pro the extreme |
| **PC3** | 15% | near-single-case (`kuhn` +0.80) | strategic / sequential play, an independent dimension |

## Interpretation

A single latent `θ` (the IRT precondition) would **destroy** the dissociation: PC1 alone discards two
independent failure modes (coherence on PC2, strategic play on PC3). So the honest output is a **profile
vector** over the axes plus a ranking, not one scalar — see the commensuration section of
[`exploitation_foundations.md`](../exploitation_foundations.html).

**Caveats.** 3 of the 10 models returned mostly-unparseable output and were mean-imputed (discard their
coordinates); `pricing`/`procure` dropped as zero-variance (saturated — a signal they need hardening); PC2's
gamble loading is amplified by z-scoring (tiny raw spread). The axis *structure* is robust to these; exact
loadings are not.

**See also.** [Test results](exploitability-test-results.html) · [research design](research-design.html).
