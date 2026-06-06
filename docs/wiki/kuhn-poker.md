# Kuhn poker

**Summary.** The canonical **exactly-solvable** poker: a 3-card deck (J < Q < K), ante 1, a single bet of 1.
Small enough that the equilibrium and any strategy's exploitability are computed by full game-tree traversal,
yet it has real poker structure (betting, bluffing, hidden information).

**As used in the 2026-06-05 sync.** It is the channel's first **sequential / extensive-form, hidden-information**
case. The model plays P1 and reveals a strategy at its 6 information sets; the opponent's **exact best
response** is closed-form (no RL). **Exploitability = best-response value − equilibrium value (1/18), in
antes/hand** — `≥ 0`, and `0` only for the (mixed) equilibrium, so any deterministic pure strategy is `> 0`.
It tests strategic/sequential play, which the [PCA](exploitability-test-results.html) shows is an **independent
axis** from one-shot randomization and coherence.

**Relevant part of our docs.**
[`exploitation_channel.md` → "Kuhn poker"](../exploitation_channel.html).

**External reference.** [Kuhn poker (overview)](https://en.wikipedia.org/wiki/Kuhn_poker).
