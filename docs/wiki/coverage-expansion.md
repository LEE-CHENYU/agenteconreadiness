# Coverage expansion: which game types open a new exploitability axis

**Summary.** The exploitability construct looked like it plateaued at ~4 latent axes. We tested whether that
was a real ceiling or a *sampling artifact* of generating cases only from the single-agent + zero-sum quadrant.
We built **12 new cases** across the multi-agent / market / mechanism quadrant and ran an 18-model
capability-controlled PCA. The plateau was a sampling artifact — rank rises to **~7–8**, with **four new
axis-groupings**. The sharpest result is a *method* finding: **the same game opens a new axis or folds into
"calculation" depending on whether its exploit route is worst-case-strategic or just hard arithmetic** — the
worst-case forms of Blotto and Stackelberg separate cleanly, while their full-information (compute-the-optimum)
forms fold into the calculation axis.

## Method
- **12 new cases** (each with an exact or declared-prior oracle, de-leaded prompt, beats-random, and an
  *independent* adversarial oracle re-derivation): `bandit, stackelberg, vickrey, bertrand_ic, allais, blotto,
  winners_curse`, the worst-case variants `blotto_maximin, stackelberg_robust`, and `allpay,
  bargaining_responder, pandora`.
- **Eval:** 18 models (1B → frontier) × 27 cases (`sprint/expand_eval.py` + `sprint/expand_run.py`).
- **Capability confound + fix.** Spanning 1B→frontier makes the top PCA component a *capability* factor
  (small models leak everywhere, frontier robust everywhere) that lumps all cases into one cluster. Fix =
  **remove each model's mean before PCA (row-center)**, then a focused PCA on the 4 axis-anchors + the new
  cases. (The raw PCA's "PC1 = 53%" is this capability factor, not construct structure — don't read axes off it.)

## Verdict — rank 4 → ~7–8; the sampling-artifact hypothesis holds
The 4 original axes persist (`rps` randomization, `kuhn` strategic/extensive-form, `gamble` calculation,
`intertemporal` time). Four **new no-anchor groupings** emerge from the capability-removed clustering:

| new axis | members | what it measures |
|---|---|---|
| **worst-case adversarial defense** | `blotto_maximin`, `stackelberg_robust` | committing/allocating against a best-responder (worst-case / robust over hidden types) |
| **dynamic / mechanism** | `bandit`, `vickrey` | sequential-learning value + dominant-strategy truthfulness |
| **adverse selection** | `winners_curse` | conditioning on winning |
| **reservation search** | `pandora` | option-value stopping with recall |

## The fold test (the headline method finding)
Nearest-anchor correlation (capability-removed) splits the 12 cleanly:

| folds into **calculation** (`gamble`) | opens / attaches to a **new** axis |
|---|---|
| `blotto` (full-info best-response) 0.70 | `blotto_maximin` (worst-case) — **distinct** (max anchor 0.23) |
| `stackelberg` (full-info LP) 0.61 | `stackelberg_robust` (worst-case) — distinct from `gamble` |
| `bertrand_ic` 0.65 · `allpay` 0.68 | `bandit`, `winners_curse`, `pandora` — distinct |

**Same game, opposite outcome.** Full-info Blotto/Stackelberg are "compute the optimum given everything" → they
correlate with the calculation axis (0.70 / 0.61). Their *worst-case* forms (commit against a best-responder;
commit robustly across hidden follower types) **separate into their own axis**. The dimension a case opens is
determined by its **exploit route** (worst-case strategy vs arithmetic), **not its topic**: `allpay` and
`bertrand_ic` fold despite "strategic" topics, because their cheapest exploit is computational. This is the
operational test for whether a candidate case adds a dimension or just re-tests `gamble`.

## Two case-level findings
- **`bargaining_responder` is flat** (std = 0.000): *every* model accepts strictly-positive offers — **no
  ultimatum / fairness-driven rejection**. Frontier LLMs are economically rational on ultimatum acceptance, so
  the case does not discriminate. A real finding (it refutes the conjecture that LLMs inherit human spite on
  small offers), not a build defect — it just isn't a benchmark *separator*.
- **`allais` folds toward randomization/coherence** (rps 0.65) — a within-subject coherence test, not a new
  dimension. Consistent with its design (charge only the common-ratio ranking flip).

## Caveats
- **12 of 31 models errored** (OpenRouter throttling under 6-way concurrency) → 18 usable. Still rows > cols
  for the focused 16-case PCA (better-powered than the prior 13-model run), but the dropped set skews the
  remaining model mix. A clean frontier-weighted re-run without throttling would firm the exact rank count.
- **Cluster boundaries (t = 0.55):** `{blotto_maximin, stackelberg_robust}` and `{winners_curse}` are robustly
  distinct (low anchor correlation); `{bandit, vickrey}` is a softer grouping (`vickrey` 0.54-rps / 0.51-gamble
  — borderline).
- Treat the axis claim as falsifiable: the fold test is the check, and it was applied per-case here.

**See also.** [PCA experiment](pca-experiment.html) · [games by solvability](games-by-solvability.html) ·
[Opus version drift](opus-version-drift.html) · [research design](research-design.html).
