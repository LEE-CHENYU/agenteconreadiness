# Self-undermining & dynamic evaluation

**Summary.** A 2026 cluster of frontier-lab papers independently arrives at AERead's frame: an LLM trained as a
**solipsistic** single-agent optimizer (world treated as exogenous + stationary = an MDP) becomes
**self-undermining** once deployed among other adaptive actors (a Markov game), and the *fix* they prescribe — a
**dynamic evaluation with adaptive counterparties** — is exactly the exploitation channel's adaptive instrument.
This page is the load-bearing synthesis + the citation home for those papers.

## Solipsistic Superintelligence (Trivedi et al., DeepMind, 2026)

[arXiv 2606.03237](https://arxiv.org/abs/2606.03237). Core diagnosis, in their terms:

- **MDP → Markov game.** A solo optimizer assumes `P,R` are exogenous (which "underwrites the convergence
  guarantees of RL and the validity of offline evaluation"). Deployment breaks this: other actors observe the
  policy and adapt, so `P_π(s'|s,a) ≠ P(s'|s,a)` — **endogenous non-stationarity** (Def A.1) — and "**no single
  optimal policy exists**." This is, verbatim, the foundations doc's [MDP-vs-non-MDP](mdp.html) split.
- **Self-undermining property.** "The more aggressively a unilateral optimizer exploits historical patterns, the
  faster it induces the adaptations that render those patterns obsolete." → exactly why a *fixed*-adversary
  [exploitability](best-response-exploitability.html) is a **lower bound** and why AERead moved to an
  [adaptive adversary](rps.html).
- **Their prescription = our instrument.** They formalize a **dynamic evaluation** as a tuple `(D_π, μ)` whose
  test distribution `D_π` *depends on the policy `π` through adaptive counterparties* (vs a "static" `D` fixed
  independently of `π`). Two caveats map onto our open questions: "**the depth of recursive modeling [is] an
  important choice**" (our "how many recursion levels?") and "**a single score against a single `D_π`
  realization would be an isolated demonstration rather than a measurement instrument**" (our
  [why-a-benchmark-not-one-env](research-design.html)). They also flag **multi-actor Goodhart** and
  alignment-faking-as-training-Goodhart — our [contamination](contamination-resistance.html) thread.

**Takeaway for AERead:** this is the theoretical home of the adaptive channel — convergent, concurrent
validation from a DeepMind group. We adopt their vocabulary (*endogenous non-stationarity*, *dynamic
evaluation*, *self-undermining*) for discoverability; AERead is the **measurement/eval layer** their manifesto
calls for.

## Economy of Minds (Qi et al., Harvard/MIT/Kempner, 2026)

[arXiv 2606.02859](https://arxiv.org/abs/2606.02859). A Hayekian market where partial agents bid in auctions,
pay the previous winner (**bucket-brigade**), and survive by wealth — coordination without an orchestrator.
Relevant theorems: **Thm 3** — the decentralized market has `O(E^{-1/2})` average **regret** vs an omniscient
coordinator; **Thm 4** — bucket-brigade payment = a Shapley-like **ordered marginal contribution** in acyclic
workflows. Same decomposable-credit / regret currency as our [aggregation](research-design.html) layer, in the
N-agent setting — so EoM is prior art for the credit-assignment layer and a natural **multi-agent extension** of
our one-sided best-responder. Honest caveat from their §C.5: the market does **not** provably prevent profitable
cartels — itself a coherence/exploitation failure AERead could measure. (Bids are **fixed at creation**; value
is revealed by *selection*, not by the bid.) Their Appendix E shows **content-independent reasoning routines
transfer across domains** (cosmology → NMR) — evidence for the "competence transfers" bet and for
[contamination resistance](contamination-resistance.html).

## More Capable, Less Cooperative? (Yadav et al., 2026)

[arXiv 2604.07821](https://arxiv.org/abs/2604.07821). o3 reaches only 16.9% of optimal collective performance vs
o3-mini 50.4% and Gemini-2.5-Pro 78.9% on **zero-cost** collaboration; a causal decomposition shows o3
*understands and can execute* the task but *chooses* not to cooperate (hard-defection in its traces). Direct
external evidence for the **capability ↔ coherence dissociation** AERead's [PCA](pca-experiment.html) found and
the ["why not pass-rate"](research-design.html) argument.

## In the wild (why the worst-case framing matters)

LLM pricing agents autonomously converge on **supra-competitive (collusive) prices**
([Fish et al. 2026](https://arxiv.org/abs/2404.00806)) and **divide markets** in multi-commodity competition
([Lin et al. 2025](https://arxiv.org/abs/2410.00031)). These are deployed strategic settings where a fixed-set
pass-rate is blind and the value an optimizing counterparty extracts is the decision-relevant quantity — AERead's
target.

## The honest tension
Both Solipsistic SI and EoM push *training* cooperation in (multi-agent RL / markets), and Solipsistic SI says
evaluation should *work with* adaptive counterparties. That positions AERead as the **eval/measurement and
denser-verifiable-signal layer** for exactly the multi-agent-trained agents they advocate — complementary, not
bypassed — but the field's gravity is training-side, so AERead must own the diagnostic role explicitly.

**See also.** [Research design](research-design.html) · [RPS](rps.html) ·
[best response & exploitability](best-response-exploitability.html) ·
[contamination resistance](contamination-resistance.html) ·
[`exploitation_foundations.md` → non-fixed strategies](../exploitation_foundations.html).
