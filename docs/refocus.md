# AERead — Refocus after the validation sprint (2026-05-29)

> **Read this first.** A validation sprint (≈17 controlled probes, real frontier-model runs, multi-seed CIs) hard-tested the v0 thesis. It deflated the easy version and sharpened a harder, more defensible one. This doc is the current state; `methodology.md` carries the framework, `methodology_open_questions.md` the open Q&A, `layer3_candidates.md` the case pool. Working positions throughout — engagement invited.

## TL;DR

Rationality-compliance ("is the agent rational?") is a **saturated floor** for frontier models — confirmed on our probes, on Chen et al. 2023's at-scale CCEI (≈0.998 > humans), and on TERMS-Bench's own leaderboard (deal rate maxed). It is *table stakes*, not the headline. The discriminating, durable, deployment-critical axes are: **(1) regime-appropriateness** (does the agent deploy the right utility for the regime — EV / Kelly / CVaR / CRRA?), **(2) the alignment↔economic-behavior shift** (replicated across two independent benchmarks), and **(3) steerability** (faithful representation of a configured principal). The contribution is the **diagnostic lens** (gate→grade + these axes + multi-seed rigor), not a new game suite. The moat is **methodological honesty** — the sprint corrected its own headline claims three times, on the record.

## What refocuses, and what stays

The **gate → grade architecture is intact** — this is a re-prioritization of *which axis carries the discrimination*, not a re-architecture.

- **Floor (cite, don't headline):** rationality / axiom-compliance. Saturated. A regression-test gate.
- **Headline axes (the differentiators):**
  1. **Regime-appropriateness** — see the four-regime map below.
  2. **Alignment-shift diagnostic** — *which* axis alignment training moves, and whether it helps or hurts. Our value-add is the systematic per-axis diagnostic, not the phenomenon (others observed it).
  3. **Steerability** — does the agent maintain a configured principal's preferences? Lead with the predict-then-validate *mechanism*, not single-seed drama (see corrections below).

## Regime-appropriateness: the four-regime utility map

The deployment regime determines the *correct* utility. EV-maximization (the frontier default) is optimal only in a narrow box; outside it a different utility is *objectively* better, so steering off the default is **correctness, not just preference**:

| Regime | Optimal utility | Why | Real cases |
|---|---|---|---|
| single-shot / additive | risk-neutral **EV** | linearity of expectation + LLN (= CRRA γ=0) | one-off procurement; single auction for a diversified bidder; ad-bidding at scale |
| repeated / compounding | **Kelly / log** | time-average growth ≠ ensemble EV; EV-max over-bets → a.s. ruin (= CRRA γ=1) | reinvested-bankroll trading; cash-compounding agents |
| absorbing ruin barrier | **CVaR / drawdown** | ruin breaks EV's averaging; bound the worst tail (coherent, convex) | insurance/reinsurance; regulatory capital; startup runway |
| configured principal | **CRRA(γ)** matched | a fiduciary optimizes the *principal's* utility, not the generic one | client wealth-mgmt; pension mandates; revealed-preference (13F) agents |

These are **points on one CRRA-γ × dynamics × barrier axis** (EV = γ0 single-shot; Kelly = γ1 forced by compounding; CVaR = a barrier constraint; CRRA-γ = configured). Selecting EV/Kelly/CVaR correctly given the *dynamics* is **gate-side correctness**; matching the principal's *γ* is **grade-side fidelity**. Durable: the right utility for a compounding/ruin/configured-principal deployment does not become textbook-lookup-able as models scale.

## Empirical findings — with confidence, and the corrections (the rigor is the point)

| Finding | Evidence | Confidence |
|---|---|---|
| Rationality (gate) saturated for frontier | probes + Chen 2023 CCEI ≈0.998 + TERMS AGR⁺ 0.95–0.999 | **high** |
| Persona-fit *mechanism* works | predict-then-validate diagonal dominance (stylized investors) | medium-high |
| **EV-default is a liability (regime-blindness)** | a frontier model over-bet into ruin at the first compounding step before switching to Kelly | medium-high |
| **Alignment↔economic tradeoff** | Andon Vending-Bench (Opus 4.8 better-aligned/worse-performance) + TERMS (Opus 4.6 > 4.7 surplus) | medium (2 benchmarks) |
| Adversarial belief-manipulation test valid | scam-arena: control overpays while frontier resists single-decision scams | medium |

**Three self-corrections, kept on the record** (this is the methodological signal, not an embarrassment):
1. A dramatic single-seed "persona-collapse, model A vs B" separation **did not survive N-seed CIs** (overlapping; both robustly steerable). What survives is subtler: steering *stability* + *directional* fidelity. → **multi-seed CIs are mandatory before any leaderboard claim.**
2. A single-seed "ruin at horizon N=3" **shifted to N=2** under multi-seed — direction robust, exact value an artifact → **report the curve, not point values.**
3. An adversarial test that **nulled** (reinforced rule unbreakable by honest persuasion) was diagnosed and rebuilt to target a *documented* vulnerability with a control that proves it fires → **a working adversarial test needs a real target + a validity control.**

## The methodological moat (why this is citable)

Gate/grade separation · multi-seed CIs + "report the distribution/curve" · orthogonality-not-residual (the extra axes are scope-extensions of TERMS Eq.4, not residual-capture — Eq.4 telescopes to zero residual within-task) · the retrieval-resistance half-life (gate hardness decays with capability; grade hardness is permanent) · stress as a cross-cutting axis (rationality is a floor at rest, a cliff under load). Frontier-lab reviewers cite rigor; "we ran the rigorous version and it corrected us, with receipts" is the channel.

## Build strategy: borrow substrate, keep the lens

The sprint proved building games is cheap but low-value (probes saturate); the **lens is substrate-agnostic.**
- **Wrap the open benchmarks** — EconEvals (code public), γ-Bench/[GAMA-Bench](https://github.com/CUHK-ARISE/GAMABench) — validated environments + mutual citation.
- **Cite-and-compute on the closed ones** — TERMS-Bench, Vending-Bench, Market-Bench have no usable public code; run the lens on their *published* results (already done).
- **Build native probes only for axes existing benchmarks can't expose** — the controllable-knob ones: the four-regime battery, persona-fidelity, adversarial belief-manipulation, framing-invariance.
- **Guard against the derivative-wrap trap**: the contribution is the cross-benchmark diagnostic lens + the controllable probes, *not* "we wrapped N benchmarks."

## External convergence (de-risks the bet)

Five economic-agent benchmarks — [EconEvals](https://arxiv.org/abs/2503.18825), [TERMS-Bench](https://arxiv.org/abs/2605.13909), Andon Vending-Bench, [γ-Bench](https://arxiv.org/abs/2403.11807), [Market-Bench](https://arxiv.org/abs/2604.05523) — independently draw the **same line**: single-agent / short-horizon / known-environment is **saturated**; multi-agent / long-horizon / competitive / adversarial / unknown-environment is **where LLMs fail and discriminate** (strategic drift, winner-take-most, scam-supplier susceptibility, surplus divergence). That boundary *is* the refocused axes. The field found our floor. This also opens the **v1+ positioning**: AERead as the trust/validation layer for agentic economic simulations (every one of these is an LLM-agent sim documenting agents failing under pressure).

## The ask for collaborators, and the discipline

**Ask:** help *pre-register and broaden* the surviving axes — more gamble families + a CVaR-barrier + a configured-CRRA variant (the four-regime battery); a within-model-family alignment-shift sweep with CIs; the persona-fit predict-then-validate on revealed-preference data. **Not** invent more axes.

**Discipline:** the project has shifted emphasis twice (rationality → persona-fidelity → regime-appropriateness/alignment-shift). Following evidence is right, but it must **converge now** — pre-register, commit, stop hunting new headlines before the first sync. v0 stays standalone (2 games); the multi-agent / validation-layer work is explicitly v1+.

## Open

- Does the EV-liability/regime-blindness replicate across gamble families + a CVaR-barrier + a configured-CRRA regime (the full four-regime battery)?
- Does the alignment-shift hold as a monotone within-family version effect (Opus 4.x, GPT-5.x) with CIs?
- Does scam-susceptibility (a single-decision *null* for frontier here) reappear under a **long-horizon** arena — i.e. is it a stress phenomenon, as the Andon Vending-Bench long-run failures suggest?
- Is the unified gate→grade framing stronger than a standalone steerability/safety paper for the frontier-lab audience? (Positioning trade-off.)
