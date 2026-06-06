# RLVR (reinforcement learning from verifiable rewards)

**Summary.** RLVR trains a model against a **computable, verifiable reward** — a checker that scores an output
correct/incorrect by rule — rather than a **learned reward model** (RLHF). It matters here because AERead's
[exploitability](best-response-exploitability.html) is computed from a **hand-specified payoff oracle**, so the
channel is **RLVR-compatible**: the exploitability gap is a verifiable training signal, not a learned one. This
is what makes the "can the benchmark be fed to a training loop?" question from the 2026-06-05 sync answerable in
principle.

## Why verifiable vs learned matters

- **RLHF** optimizes a *learned* reward (human-preference model) — it has no economic oracle in the loop, so it
  rewards *appropriateness*, not *optimality*, and can shift economic behavior toward aligned-but-suboptimal.
- **RLVR** optimizes a *verifiable* reward — the reward is a function of the observable outcome, checkable
  exactly. Exploitability qualifies: given the model's play, the optimal adversary's extracted value is computed
  by a solver, not judged.

## The oracle discipline (don't turn RLVR into RLHF)

A design rule that came up in the sync: the **payoff function is hand-specified and never learned**. There are
two oracles, and only one is RL-able:

- the **best-response strategy** (how to exploit a fixed model) — *may* be approximated by RL;
- the **payoff function** (what an outcome is worth) — **never** learned. Learning it would re-introduce a
  judge/reward-model and collapse the verifiable signal back into an RLHF-style confound.

So the channel stays a clean verifiable signal: the [solver](games-by-solvability.html) can be RL, but the
reward definition is a fixed computable oracle.

## Using exploitability as a training signal

If you train against it, the distinctions matter:

- **Aggregate = eval, per-decision = gradient.** Never backprop the suite-level magnitude `G(m)` — it's too
  sparse for credit assignment (like training on final test accuracy). Feed the **decomposed per-decision**
  exploitability gap and *watch* the aggregate fall. This is why decomposability matters: a non-decomposable
  blob ([Vending-Bench](vending-bench.html)) is un-trainable; a per-step decomposition is. As a reward it also
  beats pass/fail — a continuous money-metric regret is a **denser** gradient than a binary outcome.
- **Fixed-adversary Goodhart → use self-play.** Against a fixed solver, the model learns to beat *that solver*,
  not to become coherent (gpt-5.5 counter-exploited the fixed 1st-order adversary). A **co-adapting / no-regret
  adversary** has theory behind it — CFR average-regret → 0 ⇒ ε-[Nash](nash-equilibrium.html) ⇒ genuinely
  unexploitable.
- **Degenerate hedge → multi-objective.** Minimizing exploitability *alone* has a trivial optimum: be
  non-committal (uniform-random, refuse to price) — unexploitable and useless. Because coherence and capability
  are [separate axes](pca-experiment.html), the target is **`maximize capability − λ·exploitability`**, not
  exploitability alone.
- **Held-out Goodhart test.** Train on cases A; if held-out cases B don't improve, you gamed A — the same
  generalization split the benchmark exists for.

**Relevant part of our docs / code.** The two-oracles distinction:
[`exploitation_foundations.md` → "The two oracles"](../exploitation_foundations.html); the repo's `aeread_lab/`
includes an `rlvr` channel built on this verifiable-reward principle.

**External reference.** RLVR as a training paradigm: [Tülu 3 (Lambert et al. 2024), arXiv 2411.15124](https://arxiv.org/abs/2411.15124).
