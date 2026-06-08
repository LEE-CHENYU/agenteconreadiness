# Aggregation, gauge & game coverage (methodology)

**Summary.** Four load-bearing results about *what an exploitability benchmark can and cannot be*, derived
from the RPS-vs-Kuhn minimal pair: (1) **no universal scalar** exploitability score exists; (2) the obstruction
is **gauge-freedom + multi-dimensionality**; (3) the honest object is a **decomposable vector/tensor**, with a
scalar as a deployment-conditional projection; (4) **game construction is infinite but spanned by a small
primitive basis**, so coverage is a covering-design problem. This page is the synthesis; the formal aggregation
lives in [`exploitation_foundations.md`](../exploitation_foundations.html).

## 1. No universal scalar (the impossibility)
RPS and Kuhn are the minimal witness. They share a canonical object — **regret-to-the-unexploitable-benchmark**
(`eps = best-response value − value`, `≥0`, `=0` iff unexploitable, both *exactly* computable) — so the
**sign, the zero, and the dominance partial order** are gauge-free and comparable. But a *unique, choice-free,
faithful scalar* aggregating across them **cannot exist**, blocked by two obstructions:

| | RPS | Kuhn |
|---|---|---|
| game value | 0 (symmetric) | −1/18 (asymmetric) |
| equilibrium | unique, fully mixed | a 1-parameter mixed family |
| scale | per-round, ∈ [0,1] | antes/hand, ∈ [0, ≈1.28] |
| `eps` means | predictability | inference + bet-sizing under hidden info |
| measurement | estimated (noise floor ≈0.14) | exact (floor 0) |

## 2. Gauge (defined)
A **gauge** is a freely-chosen convention you must fix to assign numbers, which leaves the underlying object
unchanged but changes the numbers (and any comparison crossing the choice) — like a voltage reference or °C/°F.
Two gauges bind here:
- **Affine payoff gauge** — zero-sum payoffs are vNM utilities, defined up to a positive affine map `ax+b`.
  Rescale RPS {−1,0,1}→{−100,0,100}: same game, exploitability ×100. So there is *no intrinsic cardinal
  exchange rate* between RPS-units and Kuhn-units.
- **Normalization-denominator gauge** — mapping a game onto [0,1] needs a "max extractable" denominator, and
  *max over what* is a choice.

**Gauge-invariant** (real): sign, zero, *within-game* ratios, the dominance order. **Gauge-dependent**
(artifacts): magnitudes, cross-game sums. Crucial: a **fixed, disclosed** gauge is perfectly usable —
comparisons within it are fine; only a **canonical** (choice-free) gauge is impossible.

**The two obstructions to a unique scalar:** (a) *gauge-freedom* → no intrinsic cross-game exchange rate;
(b) *multi-dimensionality* → the profile is ≥2-D (empirically ≈3; RPS and Kuhn load on different
[PCA axes](pca-experiment.html)), so any scalar is a weighted projection whose ranking **reorders under
reweighting** (a Pareto/Arrow-type impossibility). Concrete witness: a cycle-in-RPS-but-clean-Kuhn model vs a
random-in-RPS-but-backwards-Kuhn model flip order depending on the weights — and nothing in the games
privileges either weighting. The obstruction bites **exactly on the Pareto-incomparable pairs**; on
dominance-comparable pairs all aggregations agree.

## 3. Vector vs scalar (resolved) — and decomposition-first
It is a **false dichotomy**: the vector is the object, the scalar is `ρ(vector)` — a projection.
- **Canonical:** the vector's sign/zero + the **dominance partial order** (weight-free). *Not* the magnitudes
  or any total order.
- **The trade:** vector = honest-but-**partial** order (leaves incomparable pairs unranked, truthfully);
  scalar = complete-but-**arbitrary** order. You cannot have complete *and* canonical.
- **Conditional canonicity:** a scalar **is** canonical *once a deployment is named* — the exposure-weighted
  expected dollar regret `Σ ωᵢ eᵢ` (`ω = λ·s`, frequency × stake). So **"scalar vs vector" = "committed to a
  deployment vs deployment-neutral."** A benchmark is neutral → it **ships the vector**; a deployer supplies
  `ω` and computes their own scalar.
- **Granularity:** not raw-per-case (over-decomposed, redundant) nor 1 (over-collapsed) — the **rank (≈3
  axes)**, the only granularity that is both faithful and legible.

So the primary object is a **two-directional decomposition** — a tensor `E[model, axis, source]`:
- **across axes (*where*)**: the PCA structure (randomization / EV-calc / coherence / strategic);
- **within a case by source (*why*)**: TERMS-Bench's `Δ_inf / Δ_unc / Δ_ctrl`.

Decomposition has its *own* gauge — additive attribution is order-dependent; the canonical fix is **Shapley**
(average over orders; [Economy of Minds](self-undermining-dynamic-evaluation.html) Thm 4 shows bucket-brigade
payments recover it), a milder, standard choice than the scalar's. **Prior art** is hierarchical: most popular
benchmarks decompose only **by sub-task** (MMLU subjects, BIG-bench, MT-Bench, AgentBench — weak); a few
decompose **by aspect** (HELM's metric matrix — the flagship "refuse one number"; DecodingTrust's 8
perspectives); fewer use **latent traits** (IRT / tinyBenchmarks); and only TERMS-Bench / EconEvals do
**causal-source** decomposition — the rare, deep kind AERead targets, on an *exact verifiable oracle*.

**Stance:** ship the ≈3-axis vector (+ `Δ`-source on demand) as the artifact; the dominance order is the
canonical ranking; a single **pre-registered, labelled** scalar is the leaderboard entry-point (gauge+weights
printed, marked a *deployment view, not a model property*); per-stakeholder scalars are computed downstream.

## 4. Evaluation vs training (and why the model trains case-by-case)
Three levels, often conflated:

| level | object | gauge status | used for |
|---|---|---|---|
| per-decision | regret on one (state, action) within one game | the game's **own** units (no cross-game choice) | the **training gradient** |
| per-axis vector | the ≈3-D profile | components gauge-fixed; cross-game magnitudes gauge-dependent | **evaluation / reporting** |
| scalar | one number | needs gauge **+** weights | leaderboard headline |

Consequences:
- The vector/scalar/gauge debate is an **evaluation/reporting** problem — it does **not** touch the training
  gradient, which is the **per-decision** signal living *inside* one game in that game's own units.
- So **per-case (single-task) training sidesteps aggregation entirely.** The gauge re-enters only for
  **joint multi-task training**, whose loss weights `wᵢ` are **the same `ω`** as the evaluation-aggregation
  gauge — i.e. *the aggregation gauge is a training hyperparameter that shapes the model.*
- **Rank = transfer.** The profile's low rank (9 cases → ≈3 axes; PC1 = 43%) *is* the measure of shared/
  transferable competence: correlation across cases = transfer. Full-rank (every game orthogonal) → no
  transfer → "just ship the envs" (the falsifier). So the dimensionality is the evidence the enterprise is
  meaningful — and **cross-axis** held-out transfer is the strong anti-overfitting test.
- **Overfitting-freedom** is *not* provided by the profile — it comes from the **held-out split +
  contamination-resistant procedural generation** ([contamination-resistance](contamination-resistance.html))
  operating *in* the coordinate system the profile defines: cross-model low rank says shared competence
  exists; within-model held-out says *this* model has it rather than memorized it.

## 5. Game coverage — construction is infinite, the core is small
**Construction DOF is effectively infinite**, but exploitability is spanned by a small **structural-primitive
basis** (≈7 knobs ≈ the [optimization-level × information-structure](games-by-solvability.html) taxonomy):
information structure · randomization required · computation load · sequentiality/recall · representation
invariance · adaptivity · action-set scale. The **discriminative rank is even smaller** (≈3) because some
primitives co-vary in current models and some are saturated (pricing/procure had zero variance) — **3 is the
*current* rank, not a fundamental cap**; it can grow as models improve or as un-probed primitives are added.

**Coverage method** (cover the finite basis, not the infinite game space):
1. feature-vector each game by its primitive settings;
2. **covering design** (t-wise covering array) — span every primitive and every *pair* with few games;
3. **parameterized per-cell generation** (per-instance oracle → regenerable, contamination-resistant);
4. **PCA / correlation pruning** — drop zero-variance / redundant cells, keep axis-openers;
5. **active "uncovered-cell" loop** (completeness critic) — target the missing primitive combo / the model
   failure unexplained by current axes; stop when added games stop opening axes; **log what stays uncovered**.

**Bounds (honest):** coverage is capped by **oracle-tractability** (L3 / no-clean-oracle cells excluded);
completeness is **unprovable** (unknown primitives — the critic mitigates, can't guarantee); and the target
**moves with capability** (re-derive per model generation).

**See also.** [comparability & output format](comparability-output-format.html) ·
[research design](research-design.html) · [PCA experiment](pca-experiment.html) ·
[games by solvability](games-by-solvability.html) · [contamination resistance](contamination-resistance.html).
