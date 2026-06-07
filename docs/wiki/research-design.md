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

## Scope & necessity (why not pass-rate; why a benchmark, not just envs)

**Why not just pass-rate (Terminal-Bench / SWE-bench)?** Same family (verifiable, oracle-scored), but
different on three axes: **average vs worst-case**, **capability vs coherence**, **binary vs magnitude**.
Pass-rate is the right tool — and more legible — for non-adversarial tasks with a clean success criterion;
most "general reasoning" lives there. Exploitability earns its added complexity in exactly one regime:
**adversarial/strategic deployment + answer-free decisions + the loss magnitude matters.** The failure it
catches that a fixed-set pass-rate structurally cannot: **high capability + incoherence** — a model that
passes 95% of a fixed pricing set yet is money-pumped by a counterparty who optimizes against it. So the claim
is scoped to *worst-case extractable value for economic agents under strategic pressure*, not "general
reasoning."

**Why a benchmark, not just per-case environments?** Training *is* per-case — for a single deployed agent you
train its env and skip the benchmark. The benchmark does a different job: (1) **generalization** — a held-out
split across diverse cases tests whether coherence *transfers* or you merely memorized N envs (train on A,
score on unseen B); (2) it is the **anti-Goodhart catcher** for per-case training (which *will* overfit its
envs); (3) **coverage** — the [PCA](pca-experiment.html) axes *define* what "general coherence" means; (4) a
frozen **shared yardstick**. Per-case train + per-case eval proves only memorization; the benchmark is the
held-out test that separates a generally-coherent model from N memorized skills.

**Falsifier.** All of this is worth it **iff coherence generalizes** — iff a transferable general factor
exists, not N independent skills. The [PCA](pca-experiment.html) PC1 (43% general "broadly exploitable vs
robust" factor) is early evidence it does; **if a held-out run showed zero transfer, the premise — and the
benchmark — would collapse to "just ship the envs."**

**Convergent external framing.** A 2026 frontier-lab line independently reaches this frame:
[Solipsistic SI (Trivedi et al.)](https://arxiv.org/abs/2606.03237) formalizes the MDP→Markov-game
**self-undermining property** and prescribes a **dynamic evaluation `(D_π, μ)` with adaptive counterparties** —
the adaptive channel's exact instrument — while noting a "single `D_π` realization is a demonstration, not a
measurement instrument" (the why-a-benchmark point). [More Capable, Less Cooperative?](https://arxiv.org/abs/2604.07821)
is external evidence for the capability↔coherence dissociation. See
[self-undermining & dynamic evaluation](self-undermining-dynamic-evaluation.html).

## The two-step plan

1. **Aggregation / commensuration** — make results comparable across games (the novel, unfilled part). See the
   commensuration section of [`exploitation_foundations.md`](../exploitation_foundations.html).
2. **Common diagnostic** — a cross-game explanation of *where/why* a model fails (à la TERMS-Bench's
   `Δ_inf/Δ_unc/Δ_ctrl`), and ideally a fix. Depends on step 1.

## How the rest of the wiki maps to this

- Which games are exactly solvable vs lower-bound: [games by solvability](games-by-solvability.html).
- The first empirical pass at "are the games measuring distinct things": [PCA experiment](pca-experiment.html)
  and [test results](exploitability-test-results.html).
