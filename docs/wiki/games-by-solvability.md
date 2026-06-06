# Games categorized by solvability

**Summary.** Each case is placed by **how hard it is to compute the optimal adversary's best response** — which
sets whether the exploitability number is **exact** or a **lower bound**. The axis is the
[MDP ↔ non-MDP](mdp.html) optimization level: the more structure (one-shot → finite → non-MDP), the more exactly
solvable. This is the categorization discussed in the 2026-06-05 sync for choosing which games to include.

| level | structure | best-response solver | exact? | cases |
|---|---|---|---|---|
| **L0** | one-shot decision with a computable oracle | `argmax` / linear program | **exact** | `gamble` (accept iff +EV), `pricing`, `procure`, `proc_invariance`, `cross_modality` |
| **L1–L2 (small)** | finite repeated / small extensive-form, perfect info-set enumeration | value iteration / full game-tree traversal | **exact** | `rps`, `cyclic7`, `wrps` (best fixed + 1st-order conditional response); [`kuhn_poker`](kuhn-poker.html) (exact game-tree best response) |
| **L2 (large) / L3** | repeated play vs an adapting opponent; continuous / [imperfect-recall](imperfect-recall.html) | RL / online best-responder | **lower bound** (no certificate) | `adaptive_rps` (dynamic); long-horizon poker (context compaction → imperfect recall) |

**Why the level matters.** At L0–L2-small the channel is **sharp** — a verifiable payoff oracle exists and the
best response is tractable, so exploitability is the *true* worst case. At L2-large/L3 the best-responder is an
approximation, so the number is a **lower bound** — e.g. [`adaptive_rps`](rps.html) uses a *fixed* online
predictor as the adversary, which a strong model can itself out-play (so the metric under-measures top models).

**Selection rule for new games.** Include a case only if (1) its payoff `A` is a computable function of the
observable outcome, and (2) best-response-vs-fixed-policy is tractable at its level. Games with no clean oracle
or that sit at L3 either stay out or get proxied by a verifiable sub-objective.

**Relevant part of our docs.** Full derivation:
[`exploitation_foundations.md` → "Finding the best response: cases by optimization level"](../exploitation_foundations.html)
and the [MDP](mdp.html) page.
