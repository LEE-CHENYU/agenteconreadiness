# Markov Decision Process (MDP) — and non-MDP / imperfect recall

**Summary.** An MDP is a decision problem `(states, actions, transitions, reward)` in which the **Markov
property** holds: the optimal action depends only on the *current* state, not the full history. This matters
for the exploitation channel because **best-response is exactly and efficiently solvable when the model's
decision problem is an MDP** (value iteration / linear programming); when it is *not* an MDP — non-Markovian
history dependence, continuous/large state, or **imperfect recall** — exact best-response is intractable and
RL gives only a **lower bound**.

**As used in the 2026-06-05 sync.** The "is this game theory or single-agent decision-making?" debate turned
on this: we treat the model's strategy as a *fixed strategy* (an environment) and best-respond to it. Whether
that best-response is exact or approximate is set by the **optimization level**:

| level | structure | solver |
|---|---|---|
| L0 | one-shot | argmax / LP (exact) |
| L1–L2 | finite (repeated / small extensive-form) | value iteration / game-tree (exact) |
| L3 | non-MDP: imperfect recall, continuous, epistemic | RL — **lower bound**, no certificate |

LLM long-horizon play sits at **L3** (see [imperfect recall](imperfect-recall.html)): the context window is
finite, so the decision problem is not a clean MDP over full history.

**Relevant part of our docs.** The full level taxonomy and why non-MDP cases only admit a lower bound:
[`exploitation_foundations.md` → "Finding the best response: cases by optimization level"](../exploitation_foundations.html).

**External reference.** [Markov decision process (overview)](https://en.wikipedia.org/wiki/Markov_decision_process).
