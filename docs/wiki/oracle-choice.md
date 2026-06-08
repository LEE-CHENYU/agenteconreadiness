# Oracle choice & competing rationality standards

**Summary.** Exploitability is defined *relative to an oracle*, so the oracle is not a detail — **it is the
measurement**, and choosing it can mean choosing among **mutually-incompatible notions of "rational."** The
policy: (0) **prefer preference-free consistency oracles** that need no normative pick; (1) where a substantive
objective is unavoidable, **default to the lab/peer-standard textbook-rational oracle, declared as a
convention, not truth**; (2) **expose the oracle as a swappable parameter** so deployments arm their own; and
report **mutually-incompatible-standard** dimensions as *characterizations under a named standard*, not as
failures.

## 1. The oracle is the measurement
`eps` is the regret to the oracle's reference point — there is no oracle-free exploitability. Change the oracle
→ change what counts as "coherent" → change the score and the ranking. But the **sensitivity splits by oracle
class**:

- **Consistency / money-pump oracles** (parameter-free): proc_invariance, calib_book (de Finetti), seq_order
  (no-arbitrage), intertemporal-as-reversal, GARP. They score *internal inconsistency* — they don't pick a
  "correct" preference, only that choices be mutually consistent. **Robust:** essentially every reasonable
  consistency axiom agrees a guaranteed self-arbitrage is bad; the verdict barely moves within this class.
- **Substantive-optimality oracles** (a specified objective/utility): EVPI (voi_pay), profit-max (pricing),
  Bayes-optimal policy (TERMS), EV-max (gamble). They define a "right answer" relative to a chosen objective.
  **Sensitive:** swap the objective and the optimum — and the exploitability ranking — moves.

## 2. Oracles can conflict — sometimes irreconcilably
Two senses, the second fundamental:

- **(a) Same construct, competing standards.** Exponential-stationarity calls a preference reversal incoherent;
  a hyperbolic-discounting oracle calls the same reversal the predictable output of a valid (non-standard)
  preference — under it the "reversers" score 0. Which axiom is normative is the descriptive-vs-normative
  debate.
- **(b) Across standards, satisfying one *requires* violating another** (not hypothetical):
  - **[Ellsberg](https://en.wikipedia.org/wiki/Ellsberg_paradox):** maxmin-EU (ambiguity aversion) is a
    coherent decision theory, but it **necessarily violates Savage's sure-thing principle** (the SEU axiom).
    You cannot satisfy both — an agent coherent under maxmin is "exploitable" under the SEU oracle and vice
    versa. The paradox *is* the proof the two standards are incompatible.
  - **Risk:** the EV-max oracle penalizes declining a +EV bet, but a risk-averse (concave-utility) agent
    *correctly* declines some +EV bets — EV-coherence conflicts with risk-averse-EU-coherence.
  - **Horizon:** single-shot EV-max vs Kelly/ruin-aversion — a model "exploitable" on one-shot EV can be
    optimal under ruin-aversion.

So there exist behaviors coherent under oracle A and exploitable under oracle B where **both A and B are
defensible rationality standards.** Not a measurement bug — decision theory admits multiple incompatible
notions of "rational."

## 3. The selection policy

**Step 0 — prefer preference-free oracles (dodge the pick).** Wherever a dimension *can* be framed as a
consistency / money-pump / arbitrage test, do so: it needs **no normative choice** (no preference *wants* to be
Dutch-booked). This is the robust, conflict-free spine and the most citation-defensible part — a reviewer can't
say "but my preference rationalizes the loss." Maximize this share.

**Step 1 — when a substantive objective is unavoidable, default to the lab/peer standard, *as a declared
convention*.** Use **risk-neutral expected-utility / SEU-Bayesian updating / exponential discounting /
single-objective profit-cost-max** — the "simulator-relative Bayes-optimal" oracle that
[TERMS-Bench](terms-bench.html) and EconEvals already use. Why this default:
1. **It's what training implicitly targets** — RLHF pushes models toward textbook-rational behavior, so
   measuring against it asks "did the model achieve what its own training aimed for?"
2. **Comparability / citation** — it matches peer benchmarks, so results are legible to labs.
3. **Least-assumption** — risk-neutral has no risk parameter to fit; SEU is the dominant model.
Declare it as a convention, **not truth** (descriptive-not-normative): the headline is *"exploitability under
the textbook-rational oracle,"* never *"irrationality."*

**Step 2 — expose the oracle as a swappable parameter ("arm others").**
- **Per deployment** → swap in the **configured principal's** objective (risk-averse pension fund, ruin-averse
  trader, fairness-weighted regulator). Same case, re-scored under the deployment's standard — the oracle is
  canonical *once a principal is named* (the same structure as a scalar being canonical once a deployment is
  named; see [aggregation, gauge & coverage](aggregation-gauge-coverage.html)).
- **For contested dimensions** → report under **multiple** oracles (multi-class robustness: EV + CRRA + CARA;
  exponential + hyperbolic) and let the divergence be the output (the non-identification discipline).

**Special handling — the mutually-incompatible-standard dimensions (Ellsberg / risk / horizon).** Do **not**
score them as failures under one oracle. Report them as **characterizations under a named standard**
("ambiguity-averse to degree X," "risk-averse with implied curvature Y"), not as exploitability — picking
SEU-as-truth silently takes a side in an unresolved debate.

## 4. The model-ladenness spectrum
Each construct sits at a different point on "how much decision model is assumed":

| construct | model-ladenness | example |
|---|---|---|
| **across-case axes** (PCA) | **model-free / empirical** — no decision model assumed | the ~4 discovered axes |
| **consistency oracle** | **axiom-specified, parameter-free** — a coherence axiom, no fitted parameters | intertemporal-as-reversal, proc_invariance, calib_book |
| **substantive-optimality oracle** | **objective-specified** — a chosen utility/objective (the contestable layer) | gamble EV, voi_pay EVPI, pricing |
| **within-case `Δ_inf/Δ_unc/Δ_ctrl`** ([TERMS](terms-bench.html)) | **fully model-specified** — Bayesian-EU agent + reference-policy ladder | the source decomposition |

## The policy in one line
**Preference-free consistency oracles are the canonical, conflict-free headline (no pick); for unavoidable
substantive objectives, default to the lab/peer-standard textbook-rational oracle declared as a convention;
expose the oracle as a parameter so deployments arm their own; and report mutually-incompatible-standard
dimensions as characterizations under a named standard, never as failures.**

**See also.** [aggregation, gauge & coverage](aggregation-gauge-coverage.html) ·
[best response & exploitability](best-response-exploitability.html) ·
[contributing cases](contributing-cases.html) · [TERMS-Bench](terms-bench.html) ·
[`exploitation_foundations.md` → "The two oracles"](../exploitation_foundations.html).
