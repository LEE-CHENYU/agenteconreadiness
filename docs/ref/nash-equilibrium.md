# Nash equilibrium (and why we don't measure it)

**Summary.** A **Nash equilibrium** is a strategy profile in which no player can gain by unilaterally
deviating. Computing it requires solving a **fixed point** over *all* players' strategies simultaneously.

**As used in the 2026-06-05 sync.** A deliberate scoping decision: AERead does **not** lead with
Nash-finding (other benchmarks already simulate equilibria — prisoner's dilemma, etc.). We measure **one-sided
best-response against a *fixed* model snapshot** ([exploitability](best-response-exploitability.html)), which
needs **no** equilibrium computation — you only best-respond to one frozen strategy. Game theory is used as a
*tool* to compute the optimal benchmark value independent of the LLM's own learning, then compared.

**Relevant part of our docs.**
[`exploitation_foundations.md` → "What we focus on: best-response, not Nash, not negotiation-surplus"](../exploitation_foundations.html).

**External reference.** [Nash, "Equilibrium Points in n-Person Games" (1950), PNAS](https://doi.org/10.1073/pnas.36.1.48).
