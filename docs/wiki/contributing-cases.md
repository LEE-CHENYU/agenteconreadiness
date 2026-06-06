# Contributing cases

**Summary.** The case library can accept **open contributions**, but behind a **strict gate** — because the
channel's whole value is that every case has a **verifiable payoff oracle** (a computable reward, not a learned
one). A single fuzzy- or learned-payoff case would turn the channel from [RLVR into RLHF](rlvr.html). You do
**not** need a game-theory background: you never derive the best-response (the solver does), only the **rules +
what an outcome is worth**, and even that is scaffolded.

## What a submission must include

A case ships as code, exactly like the built-in cases:

1. A **payoff** `A` — a computable function of the observable outcome (code or closed form).
2. The **unexploitable reference** — the equilibrium strategy / optimal choice (so the floor is defined).
3. A **pure-stdlib scorer + unit tests** with golden values for known strategies.
4. **Single-letter / anchored answers** (artifact-proof to parse).

You do *not* provide the best-responder — see [games by solvability](games-by-solvability.html) for which
levels are solved exactly vs. lower-bounded.

## The acceptance gate (3 layers)

**1. Oracle gate** (eligibility): computable `A`; best-response tractable at its [level](mdp.html) (L0–L2
exact; L3 only as an explicitly-labelled lower bound); a closed/regular game family; **parameterizable with a
per-instance oracle** (so the scored set can be regenerated — see
[contamination resistance](contamination-resistance.html)), with the solution genuinely varying with the
parameters.

**2. Automated CI** (rejects the obvious failures with no reviewer): scorer + golden tests pass; a **baseline
run proves discrimination** — the equilibrium/oracle strategy scores ≈ 0 (the floor) *and* a naive baseline
(random/uniform) scores clearly above the noise floor. This auto-rejects **saturated / zero-variance** cases
(the `pricing`/`procure` lesson — everyone scored 0.00, no signal); plus an artifact-proof parse check.

**3. Human review** (the judgment calls): economic meaning (does the payoff encode a real preference?);
**[PCA](pca-experiment.html) non-redundancy** (does it open a new axis or duplicate randomization / coherence /
strategic?); difficulty calibration (discriminates across the frontier).

**Staging & versioning:** accepted → **`candidate`** (reported, not in the headline aggregate) → **`core`**
once it shows added discriminating signal. Adding a case changes the aggregate, so **core sets are
release-frozen** (v0, v0.1…) for comparability.

## Authoring a payoff without econ/GT background

The barrier is only "rules + outcome value." Three scaffolds:

**(a) Pick a payoff primitive — fill the slots.** Most economic decisions reduce to four shapes the channel
already implements:

| If the decision is… | use primitive | you provide |
|---|---|---|
| adversarial / "be unpredictable" | zero-sum **matrix game** | actions + win/lose/tie values |
| accept or reject a bet | **+EV/−EV menu** | probabilities + payoffs |
| pick the best option | **regret-vs-oracle** | the menu + a value function (oracle = argmax) |
| sequential, hidden info | small **extensive-form** | the game tree (best-response is automatic) |

The payoff is *constructed*, not derived.

**(b) LLM-propose → machine-verify.** Describe the scenario in plain language; an LLM **drafts** `A` + oracle.
It is **never trusted** — accepted only if the equilibrium scores 0 and the unit tests pass. Proposal is cheap;
**verification** is what counts. The payoff is never a runtime-learned model output (that is the
[RLHF trap](rlvr.html)) — an LLM may *write* it, but it must stay hand-checkable.

**(c) Payoff-from-a-scenario decision tree.** *Single right answer given the rules? → regret oracle. About not
being predicted? → matrix game. Sequential with hidden info? → extensive-form.* Plus a few worked submissions
to copy.

**See also.** [Best response & exploitability](best-response-exploitability.html) ·
[games by solvability](games-by-solvability.html) ·
[`exploitation_foundations.md` → "The exactness ↔ coverage tradeoff"](../exploitation_foundations.html).
