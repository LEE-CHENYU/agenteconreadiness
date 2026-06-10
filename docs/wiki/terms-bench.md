# TERMS-Bench (the "Susan Athey" paper)

**Summary.** TERMS-Bench (Erica Zhang, Fangzhao Zhang, Pappu, El, Blanchet, **Athey**, Liu, Zou — Stanford
Engineering + Economics + GSB, 2026) is a **bilateral-negotiation outcome benchmark**. **Susan Athey** is among
the co-authors (with Jose Blanchet and James Zou). Its methodological contribution is a
**decomposition of the surplus gap** into three sources — `U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl`
(information gap + uncertainty gap + control gap). This is the paper referred to in the sync as the "Susan
Athey paper": a *decomposable but single-setting* methodology.

**Empirical conclusion of the decomposition (13 LLM agents).** The headline is that **deal rate is
non-diagnostic**: *"frontier models saturate deal rate yet diverge in surplus extraction, cue use,
belief calibration, and compliance."* The decomposition localizes that divergence to **control, not
information** — the dominant share of lost surplus is the **control gap** (`Δ_ctrl`): agents
underperform the Bayes-optimal counterpart *even when handed the correct posterior or the counterpart's
type outright*, so the bottleneck is acting well on good beliefs, not forming them. (Honest caveat the
paper flags: against the *discretized* oracle a full-reveal agent can exceed it in places — a negative
`Δ_ctrl` — so the exact magnitudes carry a discretization/gauge caveat; the robust claim is directional.)
Two corroborating findings: **informative cues *reduce* surplus for every agent** (`α_cue < 0` — warm
cues trigger over-concession, pressure cues brittleness), and **online belief error is flat-or-rising
across the 10 rounds** (updating does not improve with interaction). AERead generalizes the
*decomposition* while reading the *result* as evidence that the live frontier separator is strategic
action against an opponent — the same axis as the [results-page](results.html) competition direction.
See [arXiv 2605.13909](https://arxiv.org/abs/2605.13909) (full-text HTML for the per-gap results).

**As used in the 2026-06-05 sync.** It anchors the central design contrast. TERMS-Bench is **decomposable**
(it tells you *which* step failed) but is essentially **one setting** (bargaining); [Vending-Bench](vending-bench.html)
is the opposite (aggregated dollar value, **not** decomposable). AERead's targeted novelty is the missing
middle: **aggregate across many economic-decision games** while staying comparable — and measure **worst-case
exploitability** (defensive) rather than negotiation surplus (offensive). The decomposition idea is what we
generalize; the single-setting scope is what we extend.

**Relevant part of our docs.** Where we adopt/generalize the `Δ_inf/Δ_unc/Δ_ctrl` decomposition (conditional
on a formalization of when an OracleDecomposable task admits it): [`methodology.md`](../methodology.html).

**External references.** [arXiv 2605.13909](https://arxiv.org/abs/2605.13909) ·
[live leaderboard: terms-bench.github.io](https://terms-bench.github.io).

> Note on identification: "苏珊AC / 苏圣恩" in the audio = **Susan Athey**, a co-author of TERMS-Bench. If the
> intended reference was instead Athey's structural demand-estimation line (Ruiz–Athey–Blei, *SHOPPER*), say so
> and I'll add that page.
