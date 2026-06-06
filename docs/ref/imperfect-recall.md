# Imperfect recall

**Summary.** A decision-maker has **imperfect recall** when it may *forget* information it previously knew, so
its strategy is a map over a **summary** of the history rather than the full history. LLMs have this
**structurally**: a finite context window means that after compaction/summarization, early state is dropped.

**As used in the 2026-06-05 sync.** This is why long-horizon games are diagnostic. Over, say, 1000 rounds of
poker, the model compacts its context, forgets earlier moves, and becomes **inconsistent** in a way a
perfect-recall agent would not — and a best-responder can exploit that inconsistency. In economic terms,
imperfect recall = a **constrained strategy space** (the strategy is defined over a coarsening of history).
The added complexity of a game determines *which* inconsistencies become exploitable.

**Relevant part of our docs.** The non-fixed / L3 discussion:
[`exploitation_foundations.md` → "Next step: non-fixed (adaptive) strategies"](../exploitation_foundations.html)
and the [MDP](mdp.html) level table.

**External reference.** [Piccione & Rubinstein, "On the Interpretation of Decision Problems with Imperfect
Recall" (1997)](https://doi.org/10.1006/game.1997.0536).
