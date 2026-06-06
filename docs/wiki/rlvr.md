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

**Relevant part of our docs / code.** The two-oracles distinction:
[`exploitation_foundations.md` → "The two oracles"](../exploitation_foundations.html); the repo's `aeread_lab/`
includes an `rlvr` channel built on this verifiable-reward principle.

**External reference.** RLVR as a training paradigm: [Tülu 3 (Lambert et al. 2024), arXiv 2411.15124](https://arxiv.org/abs/2411.15124).
