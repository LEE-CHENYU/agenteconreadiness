# Opus version drift (4.5 → 4.8): a decomposition case study

**Summary.** We measured the [exploitability](best-response-exploitability.html) of four consecutive
Opus versions (4.5, 4.6, 4.7, 4.8) on the eight discriminating cases, at temperature 0 with error bars.
Across versions there is **no uniform change** — but on **Kuhn poker** the newest version (4.8) is the
**single most exploitable**, by an exact, reproducible margin (0.11 → 0.28). The finding is *invisible in
any aggregate score*: averaged over the eight dimensions, 4.8 looks like a mid-pack **improvement** over 4.5.
The regression only appears when the axes are kept separate — the clearest evidence yet that AERead's output
must be a profile [vector, not a scalar](comparability-output-format.html).

## The matrix

Lower = better; 0 = unexploitable (value an optimal adversary extracts). Temp 0. Error bars: K=5
stimulus-varied draws (matrix/gamble) · exact (kuhn, sd=0) · mean over n=10 instances (intertemporal).

| dim | 4.5 | 4.6 | 4.7 | 4.8 | endpoint verdict |
|---|---|---|---|---|---|
| **kuhn_poker** | 0.11 | 0.11 | 0.11 | **0.28** | **real** (exact, sd=0) |
| intertemporal | 0.61±.40 | 0.09±.28 | 0.09±.13 | 0.08±.12 | real drop — but **entirely at 4.5→4.6** |
| rps | 0.34 | 0.34 | 0.26 | 0.33 | within-noise (0.6σ) |
| cyclic7 | 0.87 | 0.69 | 0.93 | 0.81 | within-noise endpoint (non-monotone scatter) |
| wrps | 0.33 | 0.25 | 0.25 | 0.32 | within-noise (0.4σ) |
| gamble | 0.03 | 0.03 | 0.00 | 0.00 | within-noise (boundary artifact) |
| proc_invariance | 0.00 | 0.00 | 0.00 | 0.00 | no reversals (4 cells — low power) |
| cross_modality | 0.00 | 0.00 | 0.00 | 0.00 | no reversals (1 rate — low power) |

**Method:** `sprint/opus_cmp.py` (research tooling, not part of the artifact-proof package). Matrix/gamble
cells average K=5 deterministic *stimulus-varied* samples — the prompt carries a `(match #N)` tag, so the
draws differ without temperature and the error bars are reproducible. Kuhn is an **exact** closed-form
best-response computation from the model's single elicited strategy (no sampling noise). Intertemporal is the
mean reversal-consistency over n=10 instances.

## Headline: the Kuhn regression, attributed to one decision

4.8 is the only version that **bluffs**. The elicited pure P1 strategies:

- **4.5** — checks every card on the open (never bets): `eps 0.11`
- **4.7** — value-bets K, never bluffs: `eps 0.11`
- **4.8** — value-bets K **and bluffs J with probability 1**: `eps 0.28`

Bluffing the worst hand is *correct* in [Kuhn poker](kuhn-poker.html) — but only at the equilibrium frequency
q ≈ ⅓, a **mixed** action. 4.8 bluffs with q = 1 (**pure**), so an optimal opponent best-responds by calling
with Q and K, lifting P2's best-response value to ⅓ (vs ⅙ against 4.7). The whole 0.11 → 0.28 gap attributes
to **one information set** — the open-J decision — worth exactly **+1/6** of exploitability. (Verified against
the live best-response code by exact enumeration of all six deals.)

The direction is right (toward bluffing); 4.8 *overshoots* to q = 1 because a temperature-0 policy cannot
emit q = ⅓. So the newest, most strategically **informed** version is the most **exploitable** on this game —
through its sophistication, not despite it.

## Does decomposition make sense? Yes — at two levels

**1. Across dimensions — the aggregate hides the regression.** Mean exploitability over the eight
dimensions (lower = better):

| | 4.5 | 4.6 | 4.7 | 4.8 |
|---|---|---|---|---|
| 8-dim mean | 0.29 | 0.19 | 0.21 | **0.23** |

By the scalar, 4.8 is *better than 4.5 and mid-pack* — because the unrelated intertemporal **improvement**
(an old 4.6 fix) nets against the Kuhn **regression** and washes it out. One number reports "4.8 is fine"; the
per-axis vector reports the opposite on the strategic axis. **Aggregation nets a regression against an
unrelated improvement and calls it "no change"; decomposition localizes the regression to extensive-form
play.** This is the [PCA experiment](pca-experiment.html)'s "not unidimensional" claim made concrete on a real
deployment-readiness comparison.

**2. Within a game — exploitability decomposes across decision nodes.** Best-response regret is not only a
scalar per game; it attributes to specific information sets. Here the 4.7 → 4.8 difference localizes entirely
to the open-J node (+1/6), so we can say not "4.8 is more exploitable" but "4.8 is more exploitable *at the
J-bluff decision, by exactly 1/6, and nowhere else.*" This is the **counterfactual-regret** decomposition
that CFR exploits: the sum of per-information-set counterfactual regrets bounds total exploitability, and is
*exact* when the opponent's best response factorizes — as it does here, since only the post-bet subtree
changes. **Caveat:** in a general extensive-form game the per-node attribution is a bound, not always a clean
independent sum (the opponent's best response is global); the exact additivity here follows from only one node
changing.

So "decomposition" is load-bearing in both senses the project cares about: the **output format** (a profile
vector over axes — because the scalar hid the only alignment-relevant signal) and the **diagnosis** (which
decision, in which game, leaks).

## What this does *not* show (adversarially verified caveats)

- **Not a trend.** n = 4 versions is no trend test. The endpoint 4.5→4.8 change is non-significant for
  rps/cyclic7/wrps/gamble; the honest statement is **"no net endpoint change,"** not "the randomization
  deficit is (or isn't) being trained away." Adjacent-version wobble is significant in *both* directions —
  idiosyncrasy/noise, not a generational trajectory.
- **The intertemporal "fix" is one step,** not a smooth improvement: the entire drop is 4.5→4.6 (flat after),
  and the 4.5 anchor is high-variance (sd 0.40).
- **No pure strategy is unexploitable.** "0.11" is *not* an equilibrium floor — exploitability bottoms at the
  mixed q ≈ ⅓ (eps 0.056) and rises on both sides; 4.5/4.7 *under*-bluff (q = 0), 4.8 *over*-bluffs (q = 1).
  4.8 is simply the most exploitable pure strategy, not "the one that left equilibrium."
- **The framing-coherence zeros are low-power nulls,** not a tested ceiling: proc_invariance is 4 cells,
  cross_modality a single deterministic rate. "No reversals observed" (rule-of-three upper bound), not
  "all-pass."
- **Same family, different subtype.** The Kuhn miss (wrong *frequency* on the correct support {J,K}) and the
  RPS/cyclic7 miss (support *collapse*, punished via sequence autocorrelation) are both "failure to mix," but
  no per-model correlation between them is shown — a shared theme, not a demonstrated common cause.
- **Vending-Bench is an open question, not a tie.** Whether single-shot mixing failure predicts the
  long-horizon coherence failures (the "Opus 4.8 falls for scam suppliers" theme) is **untested here** — and
  the [Vending-Bench](vending-bench.html) note classifies that as a long-horizon/stress effect that does *not*
  reproduce in single clean decisions. Kuhn is single-shot. Don't transfer.

**See also.** [Test results](exploitability-test-results.html) · [PCA experiment](pca-experiment.html) ·
[vector vs scalar](comparability-output-format.html) · [Kuhn poker](kuhn-poker.html) ·
[best response & exploitability](best-response-exploitability.html).
