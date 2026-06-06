# TERMS-Bench (the "Susan Athey" paper)

**Summary.** TERMS-Bench (Zhang, Zhang, Pappu, El, Blanchet, **Athey**, Liu, Zou — Stanford Engineering +
Economics + GSB, May 2026; senior-advised by **Susan Athey**, Jose Blanchet, James Zou, with early feedback
from Alvin Roth) is a **bilateral-negotiation outcome benchmark**. Its methodological contribution is a
**decomposition of the surplus gap** into three sources — `U(π★) − U(π_base) = Δ_inf + Δ_unc + Δ_ctrl`
(information gap + uncertainty gap + control gap). This is the paper referred to in the sync as the "Susan
Athey paper": a *decomposable but single-setting* methodology.

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

> Note on identification: "苏珊AC / 苏圣恩" in the audio = **Susan Athey**, senior advisor on TERMS-Bench. If the
> intended reference was instead Athey's structural demand-estimation line (Ruiz–Athey–Blei, *SHOPPER*), say so
> and I'll add that page.
