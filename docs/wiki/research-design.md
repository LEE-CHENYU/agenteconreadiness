# Research design logic

**Summary.** AERead's exploitation channel measures an LLM's economic decision-making by the **value an optimal
adversary can extract from it** — its [exploitability](best-response-exploitability.html). The design choices
below all follow from one goal stated in the 2026-06-05 sync: produce a number (or small vector) that is
**comparable across heterogeneous games** and **decomposable** (tells you *where* a model fails), which no
existing benchmark delivers.

## The gap we are filling

Two reference points bracket the problem:

- **[Vending-Bench](vending-bench.html)** — aggregates many real-world sub-tasks into one dollar value, but is
  **not decomposable** (you can't attribute the ±$ to a sub-task).
- **[TERMS-Bench](terms-bench.html)** (the Athey-advised paper) — **decomposable** but essentially
  **single-setting** (bargaining).

The unfilled middle — **aggregate across many economic-decision games while staying comparable and
decomposable** — is the targeted contribution. Testing one model on one task is trivial; the novelty is the
**aggregation**.

## The instrument: exploitability, lower = better

Fix the model's strategy and compute the [best response](best-response-exploitability.html). Exploitability =
the surplus that optimal response extracts; `0` = perfect defense. Any inconsistency — bad arithmetic, a
predictable pattern, a procedure-dependent preference — admits a test that extracts value. This is a
**defensive / worst-case** measure (most a model can *lose*), the dual of the *offensive* framing (best a model
can *win* vs a fixed opponent).

## Why it is a *game*, not just single-agent decision-making

A recurring question in the sync. The resolution: we treat the model's strategy as a **fixed strategy**, freeze
it as an **environment**, and best-respond — using a solver, RL, or another model (we are not the LLM; we are
the best-responder). The **game** content is whether the model can **infer hidden information and adapt** (e.g.
[RPS](rps.html) requires reacting to an evolving opponent — the "I think that you think" recursion). Single-agent
cases (pricing, gamble) carry no such content. [Imperfect recall](imperfect-recall.html) (finite context window)
is what makes long-horizon games diagnostic.

## Game theory as the tool, not the goal

We deliberately do **not** lead with equilibrium-finding ([Nash](nash-equilibrium.html)) — others already do
that. Game theory is the **tool** that computes the optimal benchmark value *independent of the LLM's own
learning*; the headline is a capability measure, not a theorem.

## Why one general agent (not per-task models)

Future agents must handle *all* environments, and competence **transfers** across tasks (poker skill helps RPS,
as math reasoning transfers across domains). A single cross-game leaderboard therefore measures — and could
train — transferable decision-making, which per-task models can't express.

## The two-step plan

1. **Aggregation / commensuration** — make results comparable across games (the novel, unfilled part). See the
   commensuration section of [`exploitation_foundations.md`](../exploitation_foundations.html).
2. **Common diagnostic** — a cross-game explanation of *where/why* a model fails (à la TERMS-Bench's
   `Δ_inf/Δ_unc/Δ_ctrl`), and ideally a fix. Depends on step 1.

## How the rest of the wiki maps to this

- Which games are exactly solvable vs lower-bound: [games by solvability](games-by-solvability.html).
- The first empirical pass at "are the games measuring distinct things": [PCA experiment](pca-experiment.html)
  and [test results](exploitability-test-results.html).
