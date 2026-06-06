# Kuhn poker

**Summary.** The canonical **exactly-solvable** poker: a 3-card deck (J < Q < K), ante 1, a single bet of 1.
Small enough that the equilibrium and any strategy's exploitability are computed by full game-tree traversal,
yet it has real poker structure (betting, bluffing, hidden information).

**As used in the 2026-06-05 sync.** It is the channel's first **sequential / extensive-form, hidden-information**
case, and an [L1–L2 exactly-solvable](games-by-solvability.html) one.

**Basic test setting.** API only; the model plays P1 and reveals an action at each of its **6 information sets**
(open check/bet for J/Q/K; fold/call for J/Q/K after a check-then-bet) — all single-letter, artifact-proof. The
opponent's **exact best response** is a closed-form game-tree computation (no RL). **Exploitability =
best-response value − equilibrium value (1/18), in antes/hand** — `≥ 0`, and `0` only for the (mixed)
equilibrium, so any deterministic pure strategy is `> 0`.

**Test results.** Across pure strategies, exploitability ranges from a **0.11 pure-strategy floor** (Haiku,
Sonnet — opposite styles) up to ~0.44 for strategically-backwards play (Gemini bluffs the worst card,
slowplays the best). gpt-5.5 plays the right *support* but over-bluffs (0.28). Full table + the cross-axis
dissociation: [test results](exploitability-test-results.html) and
[`exploitation_channel.md` → "Kuhn poker"](../exploitation_channel.html). The [PCA](pca-experiment.html) shows
strategic/sequential play is an **independent axis** from one-shot randomization and coherence.

**External reference.** [Kuhn poker (overview)](https://en.wikipedia.org/wiki/Kuhn_poker).
