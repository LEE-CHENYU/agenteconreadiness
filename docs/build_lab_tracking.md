# AERead OpenAI Build Lab - Master Tracking Ledger

Last updated: 2026-05-30

This is the review ledger for the private OpenAI-only build-lab stack. It tracks
what each atomic PR adds, what each task currently measures, which commands were
run, the observed results, and which claims are still only provisional.

Private review repo:
`https://github.com/LEE-CHENYU/aeread-openai-build-lab-review`

Working copies:

| Path | Role | Current expectation |
|---|---|---|
| `/Users/lichenyu/aeread_review_split` | private stacked PR repo | atomic review branches only |
| `/Users/lichenyu/agenteconreadiness_build_lab_20260529` | integrated build lab | cherry-picked stack for end-to-end checks |
| `/Users/lichenyu/agenteconreadiness` | original methodology repo | source-of-truth docs; do not mutate for build-lab PRs |
| `/Users/lichenyu/persona_simulator` | original sprint/rationale repo | source-of-truth sprint toys; do not mutate for build-lab PRs |

## Current validation stance

The current stack is useful as a private review scaffold, not as a leaderboard.
The validated path is:

1. Add a deterministic generator.
2. Add a mechanical oracle.
3. Add a no-API offline baseline that exposes the intended failure mode.
4. Add a thin OpenAI Responses API path.
5. Treat parse rate as a first-class result; do not interpret economic metrics
   when parse rate is below 1.00.

The strongest current evidence is not "new games are better"; it is that the
regime-appropriateness and deployment-pressure lens can be made runnable,
judge-free, and API-testable while staying OpenAI-only.

## Private PR stack

| PR | Branch | Adds | Current result |
|---:|---|---|---|
| 1 | `review/01-openai-runtime` | OpenAI-only runtime scaffold and offline oracle path | validated by unit tests and offline oracle run |
| 2 | `review/02-cached-sweep` | cached sweep runner | validated by sweep output and cache-disabled runs |
| 3 | `review/03-bargaining-gate-grade` | bargaining gate/grade task | oracle 0 grade error; gate baseline exposes grade error |
| 4 | `review/04-market-competition` | market price competition task | oracle near-zero equilibrium gap; collusive/high/cost baselines fail |
| 5 | `review/05-prompt-hygiene` | removes oracle leakage from prompts | covered by prompt hygiene unit test |
| 6 | `review/06-auction-mechanism` | configured reserve mechanism task | oracle 0 reserve error; revenue default fails configured objectives |
| 7 | `review/07-strategic-drift` | repeated strategic drift task | oracle drift 0; myopic drift 1.00 |
| 8 | `review/08-exploration` | unknown-environment exploration task | oracle gap 0; exploit-only baseline gap 193.3 |
| 9 | `review/09-retail-survival` | retail/runway survival task | oracle ruin 0; current greedy baseline does not separate on primary ruin |
| 10 | `review/10-belief-bargaining` | belief/cue bargaining task | oracle gap 0; prior baseline gap 8.84271 |
| 11 | `review/11-principal-inference` | CRRA principal inference task | oracle fraction error 0; generic-gamma error 0.408333 |
| 12 | `review/12-ambiguity-maxmin` | maxmin ambiguity task | oracle regret 0; reference-prior regret 17.9167 |
| 13 | `review/13-mechanism-choice` | mechanism-choice task | oracle score regret 0; revenue/risk-blind baselines fail |
| 14 | `review/14-experiment-design` | noisy experiment design task | oracle gap 0; greedy baseline gap 141.505 |
| 15 | `review/15-portfolio-choice` | configured portfolio choice task | oracle regret 0; max-return regret 0.599325 |
| 16 | `review/16-matching-market` | matching market task | oracle regret 0; max-value/access baselines fail |
| 17 | `review/17-contract-screening` | adverse-selection contract screening task | oracle regret 0; max-profit/constraint-blind baselines fail |
| 18 | `review/18-moral-hazard` | hidden-action moral hazard task | oracle regret 0; hidden-action blind regret 49.3375 |
| 19 | `review/19-openai-mini-nano-aliases` | OpenAI alias correction | `mini -> gpt-5.4-mini`; `nano -> gpt-5.4-nano` |
| 20 | `review/20-common-value-auction` | common-value auction/winner's-curse guardrail | oracle regret 0; winner-curse blind regret 17.3875 |
| 21 | `review/21-openai-response-budget` | safer OpenAI Responses settings | low reasoning, low verbosity, `store=false`, incomplete-response errors |
| 22 | `review/22-response-content-extraction` | robust OpenAI response text extraction | text chunks collected; incomplete/textless responses fail loudly |
| 23 | `review/23-openai-nano-budget` | nano-safe output budget | default output budget raised to 1200 |
| 24 | `review/24-parse-rate-reporting` | parse-rate reporting in sweeps | live/offline sweeps display parse rate |
| 25 | `review/25-master-tracking-doc` | this master tracking ledger | validation results recorded here |
| 26 | `review/26-regime-breadth` | broader regime battery and barrier-violation reporting | oracle rank 1 on 32 trials; EV baseline error 0.586033 and CVaR violation 0.88 |
| 27 | `review/27-sampled-runs` | sampled run limit for cheap live smokes | `--limit 1` slices broad tasks and JSON sweeps carry `sample_limit` |
| 28 | `review/28-supplier-scam` | long-horizon supplier-scam stress task | oracle final-cash regret 0; credulous regret 551.97 and scam-supplier rate 1.00 |
| 29 | `review/29-alignment-tax` | RLHF appropriateness vs configured economic objective task | oracle regret 0; helpful default regret 71.725 and overconcession rate 1.00 |
| 30 | `review/30-revealed-allocation` | stylized 13F-style revealed-preference allocation | oracle regret 0; max-return regret 0.0693568; low-risk regret 0.0504201 |
| 31 | `review/31-alpha-maxmin-ambiguity` | alpha-maxmin ambiguity plus signal-updated priors | oracle regret 0; maxmin regret 2.32038; optimistic regret 14.5817 |
| 32 | `review/32-alternating-bargaining` | alternating-offer and hidden-reservation bargaining variants | oracle grade error 0; gate error 0.374225; round-blind alt miss 1.00; optimistic-budget hidden miss 1.00 |
| 33 | `review/33-live-sampled-validation` | sampled live OpenAI validation for alignment-tax, bargaining, and supplier-scam | `nano`, `mini`, and `gpt-5.5` all parse 1.00 and score 0 on first sampled case for each task |
| 34 | `review/34-multiturn-belief-bargaining` | multi-turn belief-bargaining signal updates | oracle surplus gap 0; prior gap 5.30563; single-cue gap 18.4281 and multi-turn miss 1.00 |
| 35 | `review/35-mechanism-ic-simulation` | incentive-compatibility simulation for mechanism choice | oracle score regret 0; IC-blind regret 18.4342 and IC-blind miss 1.00 |
| 36 | `review/36-market-inventory-survival` | market inventory-survival pricing | oracle price gap 0; liquidation survival gap 4614.45 with reserve violation 1.00; live `nano` survival gap 551.9892 |
| 37 | `review/37-retail-multiperiod-runway` | multi-period retail inventory/runway stress | oracle order error 0; EV-order ruin probability 0.251; single-cycle baseline multi-period cash gap 425.2572 and miss rate 1.00; live `nano` parses and slightly over-orders both multi-period cases |
| 38 | `review/38-supplier-scam-inventory-timing` | supplier-scam inventory timing and lockup stress | oracle constrained regret 0; timing-blind constrained regret 132.849 with timing-violation rate 0.25; credulous constrained regret 374.401; live `nano` parses and safely avoids delayed lockup but leaves cash on the table |
| 39 | `review/39-strategic-drift-info-stress` | strategic drift under imperfect information and N-player externalities | oracle drift 0 across 55 rounds; stress-blind drift 0.163636 overall and 0.4737 on stress rounds; myopic drift 0.927273; targeted live `nano` stress probe parsed 19/19 with drift 0.1579 |
| 40 | `review/40-adaptive-experiment-design` | adaptive two-step experiment design | oracle EV gap 0; single-step baseline EV gap 14.6 and multi-step miss 1.00; greedy gap 168.204 |
| 41 | `review/41-forecast-calibration` | no-oracle-style proper-scoring forecast calibration | oracle expected Brier regret 0; overconfident regret 0.116824; underreact regret 0.122238; base-rate regret 0.217312 and miss rate 1.00; live `nano` parses and solves the first calibration set |
| 42 | `review/42-calibration-reliability-stress` | reliability-weighted calibration stress | oracle expected Brier regret 0 across 9 cases; raw-likelihood/reliability-blind regret 0.09206 and reliability miss 1.00; live `nano` still solves with reliability miss 0 |
| 43 | `review/43-supplier-reputation-updates` | adaptive supplier reputation updates | oracle constrained regret 0 across 11 rounds; reputation-blind regret 23.385 with reputation miss 1.00; live `nano` reputation miss 1.00 and constrained regret 53.4815 |
| 44 | `review/44-bargaining-bayes-scaffold` | bargaining-Bayes posterior scaffold falsifier | oracle surplus gap 0 across 9 belief-bargaining prompts; literal-claim gap 60.1056; live `nano` strategic base gap 52.4859 but scaffold gap 0 |
| 45 | `review/45-regime-relationship-verifier` | generator-verifier regime relationship laws plus fit signal | oracle mean absolute error 0 across 16 generated regime prompts; EV-only baseline has law violation 0 but fit-fail 1.00; wrong-regime baseline has law violation 1.00 |
| 46 | `review/46-procurement-counterfactual-framing` | procurement paraphrase and preference-flip counterfactuals | oracle accuracy 1.00 across 6 counterfactual prompts; comfort-sticky baseline keeps paraphrase consistency but has preference-flip miss 1.00 |
| 47 | `review/47-pricing-evidence-counterfactual` | pricing sales-evidence perturbation counterfactuals | oracle posterior price error 0.00125 across 4 prompts; stale-price baseline has shift miss 1.00 and sticky-base-price 1.00 |
| 48 | `review/48-pricing-noisy-evidence-stress` | noisy pricing evidence perturbation stress | oracle posterior price error 0.002394 across 8 prompts; stale-price baseline keeps shift miss 1.00 and sticky-base-price 1.00 |
| 49 | `review/49-forecast-aggregate-bins` | aggregate-bin forecast calibration with shrinkage | oracle expected Brier regret 0 across 5 aggregate-bin prompts; raw-score baseline regret 0.088221 with raw-score miss 1.00; no-shrink empirical-bin baseline shrinkage miss 1.00 |
| 50 | `review/50-forecast-calibration-curve` | held-out forecast calibration curve | oracle expected Brier regret 0 across 3 curve prompts; raw-score baseline regret 0.089779 with raw-score miss 1.00; nearest-bin baseline miss 1.00 |
| 51 | `review/51-forecast-curve-implicit` | implicit held-out calibration curve | oracle expected Brier regret 0; raw-score baseline regret 0.089779; live `nano` regret 0.0890095 with parse 1.00 |
| 52 | `review/52-forecast-curve-noisy` | dense/noisy implicit calibration curve | oracle expected Brier regret 0; raw-score baseline regret 0.0566631; live `nano` regret 0.00141703 with parse 1.00 |
| 53 | `review/53-forecast-curve-natural` | natural-label dense/noisy calibration curve | oracle expected Brier regret 0; raw-score baseline regret 0.0566631; live `nano` regret 0.0197592 with parse 1.00 |
| 54 | `review/54-market-policy-shift` | repeated-market opponent-policy shift | oracle profit regret 0; static-Nash regret 541.191; sticky-last-price regret 189.006; live `nano` regret 18.691 with parse 1.00 |
| 55 | `review/55-mechanism-repeated` | repeated mechanism choice | oracle score regret 0; revenue baseline regret 697.695; one-period regret 567.864; risk-blind regret 226.083; live `nano` solves the explicit version |
| 56 | `review/56-mechanism-natural-repeated` | natural-label repeated mechanism choice | oracle score regret 0; same offline dynamic range as PR 55; live `nano` regret 3.50137 with parse 1.00 |
| 57 | `review/57-mechanism-participant-response` | participant-response mechanism choice | oracle score regret 0; revenue baseline regret 1771.34; one-period and response-blind regret 69.0158; live `nano` regret 23.5998 with parse 1.00 |

## Task result ledger

All results below are from the current private review stack on 2026-05-29/30
unless explicitly marked as historical/upstream.

| Task | Axis / purpose | Current offline result | Interpretation / limitation |
|---|---|---|---|
| `regime` | four-regime EV/Kelly/CVaR/CRRA utility selection | oracle mean absolute error 0 across 32 trials; EV baseline error 0.586033; EV CVaR drawdown-violation rate 0.88; all targeted parses 1.00 | broadened to even-money, skewed, thin-edge, negative-EV, small-edge, and hard-barrier gamble families |
| `regime_relationship` | generator-verifier relationship laws for regime fractions | oracle mean absolute error 0 across 16 generated prompts; EV-only baseline mean error 0.672542 with law violation 0 and fit-fail 1.00; wrong-regime baseline mean error 0.472292 with law violation 1.00 | first runnable source `7cb0ca8` generator-verifier method: verify the relationship, but pair it with fit so degenerate monotone answers do not pass |
| `alignment_tax` | RLHF appropriateness vs configured economic objective | oracle objective regret 0; helpful default regret 71.725; profit-only regret 62.35; helpful overconcession rate 1.00 | operationalizes the new upstream theory: human-approval defaults can sacrifice economic optimality even when all actions are compliant |
| `principal_inference` | infer configured principal CRRA parameter | oracle error 0; generic-gamma error 0.408333 | grade-side CRRA mismatch is mechanically measurable |
| `portfolio` | configured-principal portfolio choice | oracle regret 0; max-return regret 0.599325; low-risk regret 0.0241 | separates return-chasing from configured utility |
| `revealed_allocation` | stylized 13F-style revealed-preference continuous allocation | oracle utility regret 0; max-return regret 0.0693568; low-risk regret 0.0504201; equal-weight regret 0.0182864; parse 1.00 | first continuous allocation version of the configured-principal grade; still synthetic traces |
| `ambiguity` | maxmin/alpha-maxmin under Knightian ambiguity | oracle configured regret 0 across 5 cases; reference-prior regret 11.5796; pure-maxmin regret 2.32038; optimistic regret 14.5817 | now includes signal-updated priors and configured alpha; exposes both single-prior collapse and wrong ambiguity-attitude extremes |
| `bargaining` | D2/TERMS-style gate plus grade, now with alternating-offer and hidden-reservation variants | oracle grade error 0 across 6 cases; generic gate baseline grade error 0.374225; round-blind alternating-offer miss 1.00; optimistic-budget hidden-reservation miss 1.00 | confirms "gate-only surplus extraction" is not grade fidelity and adds first protocol/reservation-depth stressors |
| `belief_bargaining` | cue use, posterior bargaining, multi-turn opponent modeling, and strategic cheap-talk likelihoods | oracle surplus gap 0 across 9 prompts; prior baseline gap 13.6088; single-cue baseline gap 33.5649 with multi-turn miss 1.00; literal-claim baseline gap 60.1056; live `nano` strategic base gap 52.4859 but scaffold gap 0 | implements the bargaining-Bayes falsifier from source `7cb0ca8`: when posterior state is externalized, `nano` closes the strategic cheap-talk gap, isolating implicit sequential belief-state failure |
| `market` | simultaneous price competition plus inventory/capital survival pricing | oracle price gap 0.000016 across 5 cases; collusive gap 0.114756 and collusion rate 1.00 on one-shot cases; liquidation gap 0.451656 with survival cash gap 4614.45 and reserve violation 1.00 | separates collusion drift from inventory-survival and liquidation failures |
| `market_policy_shift` | repeated-market opponent-policy shift | oracle profit regret 0 across 4 policy-shift cases; static-Nash baseline regret 541.191 with static miss 1.00; sticky-last-price baseline regret 189.006 with last-price miss 1.00; collusive baseline regret 1784.78; live `nano` regret 18.691 with parse 1.00 | first market probe beyond static price fields: infer competitor next price from price-history and policy-shift signal before best-responding |
| `matching` | stability/access-aware matching | oracle regret 0; access regret 51.675; max-value regret 175.037 | separates value maximization from stability/access constraints |
| `screening` | adverse-selection contract menus | oracle regret 0; constraint-blind regret 37.7125; max-profit regret 71.5061 | exposes IC/IR blind menus |
| `moral_hazard` | hidden-action contract design | oracle profit regret 0; high-bonus regret 20.5875; hidden-action blind/fixed regret 49.3375 | exposes assuming effort for free |
| `auction` | configured reserve choice | oracle reserve error 0; revenue baseline error 0.221354 | separates Myerson revenue reserve from configured objective |
| `common_value` | winner's curse guardrail | oracle profit regret 0; winner-curse blind regret 17.3875; aggressive regret 46.72 | good capability-scaling guardrail; historical live run found smaller OpenAI models miss and `gpt-5.5` solves |
| `mechanism` | choose among allocation mechanisms with strategic-risk and incentive-compatibility checks | oracle score regret 0 across 6 cases; revenue regret 62.8342; risk-blind regret 17.6667; IC-blind regret 18.4342 and IC-blind miss 1.00 | separates revenue default, risk blindness, and incentive-compatibility blindness |
| `mechanism_repeated` | repeated mechanism choice with retention and manipulation dynamics | oracle score regret 0 across 4 repeated cases; revenue baseline regret 697.695 with revenue miss 1.00; one-period baseline regret 567.864; risk/manipulation-blind baseline regret 226.083; live `nano` regret 0 with parse 1.00 | validates the repeated/equilibrium mechanism harness, but current formulaic version does not separate live `nano` |
| `mechanism_repeated_natural` | natural-label repeated mechanism choice with the same repeated-program oracle | oracle score regret 0 across 4 repeated cases; revenue baseline regret 697.695 with revenue miss 1.00; one-period baseline regret 567.864; risk/manipulation-blind baseline regret 226.083; live `nano` regret 3.50137 with parse 1.00 | hides explicit revenue/manipulation field names behind pilot-outcome labels; weaker than the strongest calibration failures, but it reopens a live mechanism fit gap without changing the oracle |
| `mechanism_participant_response` | mechanism choice with simulated participant retention and exit response | oracle score regret 0 across 4 response cases; revenue baseline regret 1771.34 with revenue miss 1.00; one-period baseline regret 69.0158; response-blind baseline regret 69.0158; live `nano` regret 23.5998 with parse 1.00 | moves mechanism stress from static repeated scoring to endogenous participant-count dynamics; live gap is larger than PR 56 but still not a named-baseline collapse |
| `strategic_drift` | repeated strategic discipline under deterministic, imperfect-information, and N-player stress | oracle drift 0 across 55 rounds; stress-blind drift 0.163636 overall and 0.4737 on stress rounds; myopic drift 0.927273 | now scores against the accessible posterior/control bar for noisy-signal and N-player externality cases rather than an omniscient hidden-state answer |
| `forecast_calibration` | proper-scoring calibration when ex-ante omniscient labels are not a fair bar | oracle expected Brier regret 0 across 9 cases; underreact regret 0.0851473; raw-likelihood/reliability-blind regret 0.0920597 with reliability miss 1.00; base-rate regret 0.151373; overconfident regret 0.199375; live `nano` posterior L1 about 0.00025 and reliability miss 0 | direct implementation of the no-oracle methodology plus reliability-weighted evidence stress; useful as calibration plumbing, but still not currently a `nano` failure set |
| `forecast_aggregate` | aggregate-bin recalibration under distribution shift and small-bin uncertainty | oracle expected Brier regret 0 across 5 aggregate-bin cases; raw-score baseline regret 0.088221 with raw-score miss 1.00; no-shrink empirical-bin baseline regret 0.0668155 with shrinkage miss 1.00; base-rate baseline regret 0.00800648 | follows the ledger's post-PR42 recommendation: move beyond explicit Bayes updates into aggregate calibration bins with shrinkage and distribution-shift-style recalibration |
| `forecast_curve` | held-out aggregate calibration curve | oracle expected Brier regret 0 across 3 curve cases; raw-score baseline regret 0.089779 with raw-score miss 1.00; nearest-bin baseline regret 0.002067 with nearest-bin miss 1.00; base-rate baseline regret 0.043793 | extends aggregate calibration beyond one bin: shrink historical bins and interpolate to a held-out raw score |
| `forecast_curve_implicit` | implicit held-out aggregate calibration curve | oracle expected Brier regret 0 across 3 curve cases; raw-score baseline regret 0.089779 with raw-score miss 1.00; nearest-bin baseline regret 0.002067 with nearest-bin miss 1.00; base-rate baseline regret 0.043793; live `nano` regret 0.0890095 with parse 1.00 and raw-score miss 0.50 | preserves the same calibration target as `forecast_curve` but removes the explicit shrink/interpolate recipe; first calibration-curve variant that separates live `nano` |
| `forecast_curve_noisy` | dense/noisy implicit calibration curve | oracle expected Brier regret 0 across 4 noisy curve cases; raw-score baseline regret 0.0566631 with raw-score miss 1.00; nearest-bin baseline regret 0.00224894 with nearest-bin miss 1.00; base-rate baseline regret 0.0274858; live `nano` regret 0.00141703 with parse 1.00 and nearest-bin miss 0.50 | denser non-monotone tables reduce the raw-score failure but reveal sparse/noisy-bin overshooting; useful as a fit-stress signal, not as strong as PR 51 |
| `forecast_curve_natural` | natural-label dense/noisy calibration curve | oracle expected Brier regret 0 across 4 noisy curve cases; raw-score baseline regret 0.0566631 with raw-score miss 1.00; nearest-bin baseline regret 0.00224894 with nearest-bin miss 1.00; base-rate baseline regret 0.0274858; live `nano` regret 0.0197592 with parse 1.00, raw-score miss 0.67, and nearest-bin miss 0.75 | replacing machine-readable calibration row names with natural outcome-table labels reopens a clear live `nano` failure while preserving parse |
| `exploration` | unknown-environment exploration | oracle EV gap 0; exploit-only gap 193.3 | EconEvals-style exploration failure is mechanically exposed |
| `experiment_design` | noisy experiment design and adaptive posterior updates | oracle EV gap 0 across 5 cases; single-step baseline EV gap 14.6 and multi-step miss 1.00; greedy gap 168.204 and experiment miss 1.00 | exposes both skipping valuable experiments and failing to value a cheap first screen that unlocks a confirmatory second test |
| `retail` | cash/runway survival under one-cycle and multi-period inventory paths | oracle order error 0 across 5 cases; EV-order ruin probability 0.251; single-cycle baseline order error 0.0718266, multi-period cash gap 425.2572, and multi-period miss rate 1.00 | now covers both reserve-breaking over-ordering and horizon-blind under-ordering; live `nano` parses all cases but slightly over-orders both multi-period cases, creating small reserve risk |
| `procurement` | v0 qualitative procurement | oracle accuracy 1.00; first baseline 0.50 | current live OpenAI smoke also parses cleanly |
| `procurement_counterfactual` | procurement paraphrase consistency and principal preference flips | oracle accuracy 1.00 across 6 prompts; comfort baseline accuracy 0.666667 with paraphrase inconsistency 0, preference-flip miss 1.00, and sticky-base-on-flip 1.00; first baseline accuracy 0.166667 | implements the proposal's procurement counterfactual variants: wording changes should preserve the choice, but changed principal weights should move it |
| `pricing` | v0 continuous pricing | oracle revenue gap 0; rounded baseline gap 87.5 | validates continuous-action scoring |
| `pricing_counterfactual` | pricing posterior evidence perturbations | oracle posterior price error 0.002394 across 8 exact/noisy prompts; stale-price baseline price error 4.37114 with counterfactual-shift miss 1.00 and sticky-base-price 1.00; rounded baseline price error 2.40776 | implements the proposal's pricing sales-evidence perturbation variant: changed evidence should change the posterior revenue-maximizing price |
| `scam` | adversarial belief-manipulation arena | oracle overpay 0; careful overpay 6.66667; credulous overpay 133.333; instrument fires | working judge-free dynamic range; single-shot frontier scam resistance should not be confused with long-horizon Vending-Bench failures |
| `supplier_scam` | long-horizon supplier-scam under cash/runway, inventory-timing, and reputation-update constraints | oracle constrained final-cash regret 0 across 11 rounds; credulous constrained regret 304.186 with scam-supplier rate 0.545; timing-blind constrained regret 99.6365 with timing-reserve violation rate 0.1818; reputation-blind constrained regret 23.385 with reputation miss 1.00; live `nano` constrained regret 53.4815 and reputation miss 1.00 | now separates inflated-claim credulity, delayed-inventory cash-lockup failures, and failure-history/reputation update misses |

## Current validation run

Commands run from `/Users/lichenyu/aeread_review_split`. Full-stack checks before
PR 26 were run on `review/25-master-tracking-doc`; PR 26-specific checks were
run on `review/26-regime-breadth`; PR 27-specific checks were run on
`review/27-sampled-runs`; PR 28-specific checks were run on
`review/28-supplier-scam`; PR 29-specific checks were run on
`review/29-alignment-tax`; PR 30-specific checks were run on
`review/30-revealed-allocation`; PR 31-specific checks were run on
`review/31-alpha-maxmin-ambiguity`; PR 32-specific checks were run on
`review/32-alternating-bargaining`; PRs 33-44 add sampled live validation,
multi-turn belief updates, mechanism IC checks, market inventory-survival, and
multi-period retail runway, supplier-timing, and strategic no-oracle/posterior
stress checks, adaptive experiment design, proper-scoring forecast calibration,
reliability-weighted calibration stress, and adaptive supplier reputation updates.
PR 44 adds the source `7cb0ca8` bargaining-Bayes posterior-scaffold falsifier.
PR 45 adds the source `7cb0ca8` generator-verifier relationship-law prototype.
PR 46 adds the proposal-specified procurement paraphrase/preference-flip
counterfactuals.
PR 47 adds the proposal-specified pricing sales-evidence perturbation
counterfactuals. PR 48 extends the same task with noisy evidence stress.
PR 49 adds aggregate-bin forecast calibration with shrinkage.
PR 50 adds held-out calibration-curve interpolation.
PR 51 adds implicit held-out calibration-curve presentation without the explicit
shrink/interpolate recipe.
PR 52 adds dense/noisy implicit calibration-curve cases with sparse,
non-monotone bins.
PR 53 adds natural-label calibration rows for the same dense/noisy curve cases.
PR 54 adds repeated-market opponent-policy-shift pricing.
PR 55 adds repeated mechanism choice with retention and manipulation dynamics.
PR 56 adds a natural-label repeated-mechanism prompt over the same oracle.
PR 57 adds participant-response simulation for repeated mechanism choice.

| Check | Command | Result |
|---|---|---|
| Unit tests | `python3 -m unittest discover -s tests -p 'test_*.py'` | 106 tests passed after PR 57 |
| Full offline oracle task pass | `python3 -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 36 task runners executed; oracle errors/regrets zero or expected near-zero; regime-relationship n=16 with mean absolute error 0, law violation 0, and fit-fail 0; procurement-counterfactual n=6 with accuracy 1.00, paraphrase inconsistency 0, flip miss 0, and sticky flip 0; pricing-counterfactual n=8 with price error 0.0024, shift miss 0, and sticky price 0; market-policy-shift n=4 with profit regret 0, static Nash miss 0, and last-price miss 0; mechanism-repeated n=4 with score regret 0, revenue miss 0, one-period miss 0, and risk-blind miss 0; mechanism-repeated-natural n=4 with score regret 0, revenue miss 0, one-period miss 0, and risk-blind miss 0; mechanism-participant-response n=4 with score regret 0, revenue miss 0, one-period miss 0, and response-blind miss 0; forecast-aggregate n=5 with expected Brier regret 0, raw-score miss 0, and shrinkage miss 0; forecast-curve n=3 with expected Brier regret 0, raw-score miss 0, and nearest-bin miss 0; forecast_curve_implicit n=3 with expected Brier regret 0, raw-score miss 0, and nearest-bin miss 0; forecast_curve_noisy n=4 with expected Brier regret 0, raw-score miss 0, and nearest-bin miss 0; forecast_curve_natural n=4 with expected Brier regret 0, raw-score miss 0, and nearest-bin miss 0; bargaining n=6 with grade error 0; belief-bargaining n=9 with surplus gap 0, strategic base gap 0, and scaffold gap 0; market n=5 with price gap 0 and survival gap 0; mechanism n=6 with score regret 0; strategic-drift n=55 with drift 0 and stress drift 0; forecast-calibration n=9 with expected Brier regret 0, posterior L1 0, and reliability miss 0; experiment-design n=5 with EV gap 0 and multi-step miss 0; retail n=5 with order error 0 and multi-period miss 0; supplier-scam n=11 with constrained regret 0, timing violation 0, and reputation miss 0; scam control `instrument_fires=True`; alignment-tax regret 0; revealed-allocation regret 0 |
| Forecast aggregate calibration sweep | `python3 -m aeread_lab.cli --sweep --task forecast_aggregate --agents offline:oracle,offline:raw_score,offline:empirical_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; base-rate regret 0.00800648; empirical-bin/no-shrink regret 0.0668155 with shrinkage miss 1.00; raw-score regret 0.0882209 with raw-score miss 1.00; parse 1.00 |
| Market policy-shift sweep | `python3 -m aeread_lab.cli --sweep --task market_policy_shift --agents offline:oracle,offline:nash,offline:last_price,offline:collusive --no-cache` | oracle rank 1 with profit regret 0; sticky-last-price regret 189.006 and last-price miss 1.00; static-Nash regret 541.191 and static miss 1.00; collusive regret 1784.78; parse 1.00 |
| Repeated mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_repeated --agents offline:oracle,offline:revenue,offline:one_period,offline:risk_blind --no-cache` | oracle rank 1 with score regret 0; risk-blind regret 226.083; one-period regret 567.864; revenue regret 697.695; parse 1.00 |
| Natural repeated mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_repeated_natural --agents offline:oracle,offline:revenue,offline:one_period,offline:risk_blind --no-cache` | oracle rank 1 with score regret 0; risk-blind regret 226.083; one-period regret 567.864; revenue regret 697.695; parse 1.00 |
| Participant-response mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_participant_response --agents offline:oracle,offline:revenue,offline:one_period,offline:response_blind --no-cache` | oracle rank 1 with score regret 0; one-period and response-blind regret 69.0158; revenue regret 1771.34; parse 1.00 |
| Forecast curve calibration sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00206655 with nearest-bin miss 1.00; base-rate regret 0.0437929; raw-score regret 0.0897789 with raw-score miss 1.00; parse 1.00 |
| Forecast implicit curve sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve_implicit --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00206655 with nearest-bin miss 1.00; base-rate regret 0.0437929; raw-score regret 0.0897789 with raw-score miss 1.00; parse 1.00 |
| Forecast noisy curve sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve_noisy --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00224894 with nearest-bin miss 1.00; base-rate regret 0.0274858; raw-score regret 0.0566631 with raw-score miss 1.00; parse 1.00 |
| Forecast natural-label curve sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve_natural --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00224894 with nearest-bin miss 1.00; base-rate regret 0.0274858; raw-score regret 0.0566631 with raw-score miss 1.00; parse 1.00 |
| Pricing counterfactual sweep | `python3 -m aeread_lab.cli --sweep --task pricing_counterfactual --agents offline:oracle,offline:stale_price,offline:round --no-cache` | oracle rank 1 with mean absolute price error 0.002394; rounded baseline price error 2.40776; stale-price baseline price error 4.37114 with counterfactual-shift miss 1.00 and sticky-base-price 1.00; parse 1.00 |
| Procurement counterfactual sweep | `python3 -m aeread_lab.cli --sweep --task procurement_counterfactual --agents offline:oracle,offline:comfort,offline:first --no-cache` | oracle rank 1 with accuracy 1.00; comfort baseline accuracy 0.666667, paraphrase inconsistency 0, preference-flip miss 1.00, sticky-base-on-flip 1.00; first baseline accuracy 0.166667; parse 1.00 |
| Regime relationship differential sweep | `python3 -m aeread_lab.cli --sweep --task regime_relationship --agents offline:oracle,offline:ev,offline:wrong_regime --no-cache` | oracle rank 1 with mean absolute error 0; EV-only mean error 0.672542 with law violation 0 and fit-fail 1.00; wrong-regime mean error 0.472292 with law violation 1.00; parse 1.00 |
| Regime differential sweep | `python3 -m aeread_lab.cli --sweep --task regime --agents offline:oracle,offline:ev,offline:kelly,offline:cvar,offline:half --no-cache` | oracle rank 1; EV baseline error 0.586033; CVaR/Kelly baselines error 0.224185; half baseline error 0.429783; parse 1.00 for all rows |
| Alignment-tax differential sweep | `python3 -m aeread_lab.cli --sweep --task alignment_tax --agents offline:oracle,offline:helpful,offline:profit --no-cache` | oracle rank 1; profit-only regret 62.35; helpful regret 71.725; parse 1.00 |
| Alignment-tax helpful smoke | `python3 -m aeread_lab.cli --task alignment_tax --agent offline:helpful --no-cache` | objective regret 71.725; overconcession 1.00; helpful-default match 1.00 |
| Revealed-allocation differential sweep | `python3 -m aeread_lab.cli --sweep --task revealed_allocation --agents offline:oracle,offline:max_return,offline:low_risk,offline:equal --no-cache` | oracle rank 1; equal regret 0.0182864; low-risk regret 0.0504201; max-return regret 0.0693568; parse 1.00 |
| Revealed-allocation oracle JSON smoke | `python3 -m aeread_lab.cli --task revealed_allocation --agent offline:oracle --no-cache --json` | 3 trials; inferred gammas 2.56, 0.10, 1.53; oracle utility regret 0 and weight L1 error 0 |
| Alpha-maxmin ambiguity sweep | `python3 -m aeread_lab.cli --sweep --task ambiguity --agents offline:oracle,offline:reference_prior,offline:maxmin,offline:optimistic --no-cache` | oracle rank 1; maxmin regret 2.32038; reference-prior regret 11.5796; optimistic regret 14.5817; parse 1.00 |
| Ambiguity maxmin/optimistic smokes | `python3 -m aeread_lab.cli --task ambiguity --agent offline:maxmin --no-cache` and `python3 -m aeread_lab.cli --task ambiguity --agent offline:optimistic --no-cache` | maxmin misses the configured-alpha case; optimistic miss rate 1.00 where optimism differs from oracle |
| Alternating/hidden bargaining sweep | `python3 -m aeread_lab.cli --sweep --task bargaining --agents offline:oracle,offline:gate,offline:round_blind,offline:optimistic_budget --no-cache` | oracle rank 1 with grade error 0; gate grade error 0.374225; round-blind grade error 0.0122222 and alternating miss 1.00; optimistic-budget grade error 0.0435819 and hidden miss 1.00; parse 1.00 |
| Bargaining oracle smoke | `python3 -m aeread_lab.cli --task bargaining --agent offline:oracle --no-cache` | 6 trials; expected agreement 0.84; mean grade error 0; gate gap 46.3942; alt miss 0.00; hidden miss 0.00 |
| Bargaining-Bayes scaffold sweep | `python3 -m aeread_lab.cli --sweep --task belief_bargaining --agents offline:oracle,offline:literal_claim,offline:single_cue,offline:prior --no-cache` | oracle rank 1 with surplus gap 0; prior gap 13.6088; single-cue gap 33.5649 and multi-turn miss 1.00; literal-claim gap 60.1056; parse 1.00 |
| Mechanism IC sweep | `python3 -m aeread_lab.cli --sweep --task mechanism --agents offline:oracle,offline:revenue,offline:risk_blind,offline:ic_blind --no-cache` | oracle rank 1 with score regret 0; risk-blind regret 17.6667; IC-blind regret 18.4342 and IC miss 1.00; revenue regret 62.8342; parse 1.00 |
| Market inventory-survival sweep | `python3 -m aeread_lab.cli --sweep --task market --agents offline:oracle,offline:collusive,offline:nash,offline:cost --no-cache` | oracle rank 1 with price gap 0.000016; Nash-only gap 0.0680322; collusive gap 0.114756 and collusion rate 1.00; cost/liquidation gap 0.451656, survival gap 4614.45, reserve violation 1.00 |
| Strategic drift information-stress sweep | `python3 -m aeread_lab.cli --sweep --task strategic_drift --agents offline:oracle,offline:stress_blind,offline:myopic --no-cache` | oracle rank 1 with drift 0; stress-blind drift 0.163636 overall and 0.4737 on stress rounds; myopic drift 0.927273; parse 1.00 |
| Adaptive experiment-design sweep | `python3 -m aeread_lab.cli --sweep --task experiment_design --agents offline:oracle,offline:single_step,offline:greedy --no-cache` | oracle rank 1 with EV gap 0; single-step EV gap 14.6 and multi-step miss 1.00; greedy EV gap 168.204 and experiment miss 1.00; parse 1.00 |
| Forecast calibration reliability sweep | `python3 -m aeread_lab.cli --sweep --task forecast_calibration --agents offline:oracle,offline:raw_likelihood,offline:underreact,offline:base_rate,offline:overconfident --no-cache` | oracle rank 1 with expected Brier regret 0; underreact regret 0.0851473; raw-likelihood/reliability-blind regret 0.0920597 and reliability miss 1.00; base-rate regret 0.151373; overconfident regret 0.199375; parse 1.00 |
| Retail multi-period sweep | `python3 -m aeread_lab.cli --sweep --task retail --agents offline:oracle,offline:ev_order,offline:single_cycle,offline:zero --no-cache` | oracle rank 1 with order error 0; single-cycle order error 0.0718266; EV-order order error 0.166173 and ruin probability 0.251; zero-order error 0.582994 and ruin probability 0.6 |
| Retail oracle/myopic smokes | `python3 -m aeread_lab.cli --task retail --agent offline:oracle --no-cache` and `python3 -m aeread_lab.cli --task retail --agent offline:single_cycle --no-cache` | oracle n=5 with cash gap 0, order error 0, ruin 0, multi-period miss 0; single-cycle n=5 with cash gap 170.1029, multi-period cash gap 425.2572, multi-period miss 1.00 |
| Regime oracle/barrier smoke | `python3 -m aeread_lab.cli --task regime --agent offline:oracle --no-cache` | 32 trials; oracle mean absolute error 0; wealth destruction 0.00; CVaR drawdown violation 0.00 |
| Sampled regime sweep | `python3 -m aeread_lab.cli --sweep --task regime --agents offline:oracle,offline:ev --limit 1 --no-cache` | 4 regime trials from one gamble; oracle rank 1; parse 1.00 |
| Sampled all-task oracle smoke | `python3 -m aeread_lab.cli --task all --agent offline:oracle --limit 1 --no-cache` | all 29 task runners execute with first deterministic case/gamble only; scam remains instrumented |
| Sampled JSON smoke | `python3 -m aeread_lab.cli --sweep --task common_value --agents offline:oracle,offline:ev --limit 1 --no-cache --json` | JSON payload includes `sample_limit: 1` and one common-value trial per agent |
| Supplier-scam differential sweep | `python3 -m aeread_lab.cli --sweep --task supplier_scam --agents offline:oracle,offline:reputation_blind,offline:timing_blind,offline:credulous --no-cache` | oracle rank 1 with constrained regret 0; reputation-blind constrained regret 23.385 and reputation miss 1.00; timing-blind constrained regret 99.6365 and timing violation 0.1818; credulous constrained regret 304.186 and scam-supplier rate 0.545; parse 1.00 |
| Supplier-scam reputation-blind smoke | `python3 -m aeread_lab.cli --task supplier_scam --agent offline:reputation_blind --no-cache` | constrained final-cash regret 23.385; reputation miss 1.00; reserve and timing violations 0.00 |
| Principal/portfolio/ambiguity sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Bargaining/belief/market sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 for bargaining and market; bargaining now includes alternating/hidden variants; belief prior baseline fails; high-anchor ties current primary metric |
| Matching/screening/mechanism sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Strategic/exploration/experiment/retail/scam sweeps | task-specific sweeps with oracle and known-bad/control baselines | oracle rank 1 on the tracked primary metrics; strategic drift now exposes stress-drift and myopic-miss rates; retail ranks by order error and exposes both ruin and multi-period miss metrics; scam dynamic range validated |
| Auction/procurement/pricing sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1; procurement/pricing parse 1.00 |
| All-task JSON smoke | `python3 -m aeread_lab.cli --sweep --task all --agents offline:oracle,offline:ev --no-cache --json` | saved 2 runs and 40 result rows to `/tmp/aeread_review_all_oracle_ev_sweep.json` |
| Whitespace check | `git diff --check` | passed with no output |
| Provider guardrail scan | `rg -n "OpenRouter|Anthropic|anthropic/|claude|OPENAI_BASE_URL|sk-proj" aeread_lab tests docs/build_lab.md docs/build_lab_tracking.md pyproject.toml` | only expected documentation/test guardrail matches; no API key string in tracked files |

### Live OpenAI API validation

The API key is read from ignored local `.env` files for live smokes. The key is
not committed, and live commands source `.env` only for the subprocess.

| Live check | Result | Interpretation |
|---|---|---|
| `python3 -m aeread_lab.cli --sweep --task procurement --agents openai:nano,openai:mini --no-cache` | completed; `openai:mini` accuracy 1.00, parse 1.00; `openai:nano` accuracy 0.50, parse 1.00 | current OpenAI Responses path, alias mapping, output budget, parsing, and parse-rate reporting work for mini/nano |
| `python3 -m aeread_lab.cli --sweep --task bargaining --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr32_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | confirms the `.env` live path and all allowed OpenAI aliases work after PR 32 |
| `python3 -m aeread_lab.cli --task bargaining --agent openai:nano --cache-dir /tmp/aeread_pr32_live_cache` | completed; n=6, parse path valid, mean grade error 0.1231, alternating miss 1.00, hidden miss 1.00 | first live signal that `nano` misses both new bargaining stressors |
| `python3 -m aeread_lab.cli --sweep --task alignment_tax --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr33_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | sampled alignment-tax smoke validates the live path but does not separate models on the easiest case |
| `python3 -m aeread_lab.cli --sweep --task bargaining --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr33_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | cached rerun confirms sampled bargaining stability across all allowed aliases |
| `python3 -m aeread_lab.cli --sweep --task supplier_scam --agents openai:nano,openai:mini,openai:gpt-5.5 --limit 1 --cache-dir /tmp/aeread_pr33_live_cache` | completed; all three aliases parse 1.00 and score 0 on the first sampled case | sampled supplier-scam smoke validates parse/model plumbing; deeper stress cases are needed for separation |
| `python3 -m aeread_lab.cli --task belief_bargaining --agent openai:nano --cache-dir /tmp/aeread_pr34_live_cache` | completed; n=5, mean surplus gap 18.4281, cue miss 0.00, multi-turn miss 1.00 | first live signal that `nano` handles one-shot cues but misses the new multi-turn signal updates |
| `python3 -m aeread_lab.cli --task mechanism --agent openai:nano --cache-dir /tmp/aeread_pr35_live_cache` | completed; n=6, score regret 0, IC miss 0.00, mean IC violation 0.1192 | IC probe parses live and `nano` solves this first mechanism-IC set |
| `python3 -m aeread_lab.cli --task market --agent openai:nano --cache-dir /tmp/aeread_pr36_live_cache` | completed; n=5, price gap 0.0536, collusion 0.00, survival cash gap 551.9892, reserve violation 0.00 | `nano` avoids collusion and reserve failure but leaves material inventory-survival cash on the table |
| `python3 -m aeread_lab.cli --task retail --agent openai:nano --cache-dir /tmp/aeread_pr37_live_cache_v4` | completed after raising the default output budget to 4096; n=5, order error 0.0228, ruin probability 0.0103, multi-period miss 1.00 | `nano` parses the longer stress prompts and solves the one-cycle cases, but slightly over-orders both multi-period cases enough to create small reserve risk |
| `python3 -m aeread_lab.cli --task supplier_scam --agent openai:nano --cache-dir /tmp/aeread_pr38_live_cache` | completed; n=8, parse 1.00, constrained regret 50.6953, reserve violation 0.00, scam-supplier rate 0.00, timing violation 0.00 | `nano` solves the legacy scam cases and avoids unsafe delayed lockup, but is conservative on delayed-inventory rounds and leaves 152.086 final cash on the table in that case |
| targeted stress-only `openai:nano` strategic-drift script using `DEFAULT_CASES[-2:]` and `/tmp/aeread_pr39_live_cache` | completed; n=19, parsed 19/19, drift 0.1579, stress drift 0.1579, myopic miss 0.13 | validates the new imperfect-information/N-player prompt fields; `nano` drifts once late in the fragile-signal case and twice in the N-player case |
| `python3 -m aeread_lab.cli --task experiment_design --agent openai:nano --cache-dir /tmp/aeread_pr40_live_cache` | completed; n=5, all choices parsed, EV gap 168.204, experiment miss 1.00, multi-step miss 1.00 | `nano` chooses immediate deployment on every case, including the new adaptive two-step screen, so it cleanly exposes an experimentation/information-value failure |
| `python3 -m aeread_lab.cli --task forecast_calibration --agent openai:nano --cache-dir /tmp/aeread_pr41_live_cache` | completed; n=6, parse 1.00, expected Brier regret prints as 0.0000, realized Brier 0.1882, posterior L1 0.0003, base-rate miss 0.00, overconfidence 0.00 | the first no-oracle/proper-scoring set validates the calibration plumbing but does not separate `nano`; harder calibration/framing stress is needed before using this as a model-discrimination result |
| `python3 -m aeread_lab.cli --task forecast_calibration --agent openai:nano --cache-dir /tmp/aeread_pr42_live_cache` | completed; n=9, parse 1.00, expected Brier regret 1.09e-7, posterior L1 0.000251, base-rate miss 0.00, overconfidence 0.00, reliability miss 0.00 | reliability-weighted evidence also validates live; `nano` follows the log-likelihood shrinkage instruction, so calibration still needs less explicit framing or aggregate-bin stress to separate models |
| `python3 -m aeread_lab.cli --task supplier_scam --agent openai:nano --cache-dir /tmp/aeread_pr43_live_cache` | completed; n=11, parse 1.00, constrained regret 53.4815, reserve violation 0.00, scam-supplier rate 0.00, timing violation 0.00, reputation miss 1.00 | `nano` handles legacy supplier-scam rounds and avoids reserve failures, but ignores failure-history updates and continues buying from the degraded supplier in both reputation-sensitive rounds |
| `python3 -m aeread_lab.cli --task belief_bargaining --agent openai:nano --cache-dir /tmp/aeread_pr44_live_cache` | completed; n=9, parse 1.00, surplus gap 21.9014, cue miss 0.2857, multi-turn miss 1.00, strategic base gap 52.4859, scaffold gap 0 | direct support for the `7cb0ca8` falsifier: `nano` fails strategic cheap-talk inference when posterior state is implicit, but closes the gap when the posterior is externalized |
| `python3 -m aeread_lab.cli --task regime_relationship --agent openai:nano --cache-dir /tmp/aeread_pr45_live_cache` | completed; n=16, parse 1.00, mean absolute error 0.1713, law violation 0.00, fit-fail 1.00 | direct support for the generator-verifier caution in `7cb0ca8`: `nano` preserves the relationship laws but misses oracle fit on every generated group, so relationship-only verification would over-credit it |
| `python3 -m aeread_lab.cli --task procurement_counterfactual --agent openai:nano --cache-dir /tmp/aeread_pr46_live_cache` | completed; n=6, accuracy 0.833333, paraphrase inconsistency 0.00, preference-flip miss 0.50, sticky-base-on-flip 0.00 | `nano` preserves choices under paraphrase and solves one preference flip, but misses the lobby-table flip by choosing the high-durability option instead of the cheaper oracle |
| `python3 -m aeread_lab.cli --task pricing_counterfactual --agent openai:nano --cache-dir /tmp/aeread_pr47_live_cache` | completed; n=4, parse 1.00, mean absolute price error 0, counterfactual-shift miss 0.00, sticky-base-price 0.00 | validates the pricing evidence-perturbation harness, but this exact linear-evidence version does not separate `nano`; harder or noisier evidence perturbations are needed for model discrimination |
| `python3 -m aeread_lab.cli --task pricing_counterfactual --agent openai:nano --cache-dir /tmp/aeread_pr48_live_cache` | completed; n=8, parse 1.00, mean absolute price error 0.35235, counterfactual-shift miss 0.00, sticky-base-price 0.00 | noisy evidence creates a nonzero pricing-fit gap for `nano` while preserving correct shift direction; this is a calibration/estimation stress, not a stale-price failure |
| `python3 -m aeread_lab.cli --task forecast_aggregate --agent openai:nano --cache-dir /tmp/aeread_pr49_live_cache` | completed; n=5, parse 1.00, expected Brier regret 1.28e-9, raw-score miss 0.00, shrinkage miss 0.00 | validates the aggregate-bin shrinkage harness, but `nano` solves this explicit version; future aggregate calibration work should make the recalibration formula less directly stated or use held-out bin curves |
| `python3 -m aeread_lab.cli --task forecast_curve --agent openai:nano --cache-dir /tmp/aeread_pr50_live_cache` | completed; n=3, parse 1.00, expected Brier regret 1.16e-9, raw-score miss 0.00, nearest-bin miss 0.00 | validates held-out calibration-curve interpolation, but `nano` solves this explicit version; future curve work should remove formula hints or use denser/noisier tables |
| `python3 -m aeread_lab.cli --task forecast_curve_implicit --agent openai:nano --cache-dir /tmp/aeread_pr51_live_cache` | completed; n=3, parse 1.00, expected Brier regret 0.0890095, probability error 0.1902, raw-score miss 0.50, nearest-bin miss 0.00 | removing the explicit shrink/interpolate recipe turns the same held-out curve target into a live `nano` failure signal; the model partially reverts toward the raw score under implicit calibration framing |
| `python3 -m aeread_lab.cli --task forecast_curve_noisy --agent openai:nano --cache-dir /tmp/aeread_pr52_live_cache` | completed; n=4, parse 1.00, expected Brier regret 0.00141703, probability error 0.0278, raw-score miss 0.00, nearest-bin miss 0.50 | `nano` mostly solves the denser/noisier table but overshoots two sparse/noisy cases; this is a weaker fit-stress signal than PR 51, not a broad raw-score failure |
| `python3 -m aeread_lab.cli --task forecast_curve_natural --agent openai:nano --cache-dir /tmp/aeread_pr53_live_cache` | completed; n=4, parse 1.00, expected Brier regret 0.0197592, probability error 0.1061, raw-score miss 0.67, nearest-bin miss 0.75 | natural row labels produce a much stronger live failure than the machine-readable noisy table; `nano` treats some score-centered outcome rows like nearest rows or raw scores instead of recalibrating the curve |
| `python3 -m aeread_lab.cli --task market_policy_shift --agent openai:nano --cache-dir /tmp/aeread_pr54_live_cache` | completed; n=4, parse 1.00, profit regret 18.691, price error 3.0037, static-Nash miss 0.00, last-price miss 0.00 | `nano` adjusts to the opponent-policy signals enough to avoid static/sticky baselines, but leaves moderate profit on the table from imperfect next-price inference |
| `python3 -m aeread_lab.cli --task mechanism_repeated --agent openai:nano --cache-dir /tmp/aeread_pr55_live_cache` | completed; n=4, parse 1.00, score regret 0, revenue miss 0.00, one-period miss 0.00, risk-blind miss 0.00 | validates the repeated-mechanism harness, but `nano` solves this explicit full-horizon scoring version |
| `python3 -m aeread_lab.cli --task mechanism_repeated_natural --agent openai:nano --cache-dir /tmp/aeread_pr56_live_cache` | completed; n=4, parse 1.00, score regret 3.50137, revenue miss 0.00, one-period miss 0.00, risk-blind miss 0.00 | natural pilot-outcome labels reopen a small live mechanism gap while preserving parse; `nano` does not collapse to the known offline defaults |
| `python3 -m aeread_lab.cli --task mechanism_participant_response --agent openai:nano --cache-dir /tmp/aeread_pr57_live_cache` | completed; n=4, parse 1.00, score regret 23.5998, revenue miss 0.00, one-period miss 0.00, response-blind miss 0.00 | participant-response simulation creates a larger live mechanism gap than PR 56 while preserving format compliance |
| `python3 -m aeread_lab.cli --sweep --task common_value --agents openai:nano,openai:mini,openai:gpt-5.5 --no-cache` | attempted, interrupted after more than 3 minutes with no completed output | not counted as a result; use smaller current live smokes or cached/historical `gpt-5.5` evidence until latency is controlled |

Historical live API findings from earlier in this private stack:

| Finding | Result | What changed because of it |
|---|---|---|
| `gpt-5.5-mini` and `gpt-5.5-nano` did not exist | live model list showed `gpt-5.4-mini` and `gpt-5.4-nano` | PR 19 fixed aliases |
| `gpt-5.5` produced blank scored outputs at 400 tokens | raw response was `status=incomplete`, reason `max_output_tokens` | PR 21 made incomplete/textless responses hard failures |
| response chunks could be missed | output text sometimes lived in nested content chunks | PR 22 added robust extraction |
| `nano` could still exhaust 800 tokens | direct probe worked at 1200 | PR 23 raised default output budget |
| long-horizon retail stress could exhaust 1200-2400 tokens | PR 37 live `nano` runs stopped on `max_output_tokens` on long-horizon retail cases at lower budgets | PR 37 keeps incomplete responses hard-failing, raises the default output budget to 4096, and tightens the retail no-explanation instruction |
| common-value live smoke separated model scale | `nano` regret 21.6325, `mini` regret 7.5125, `gpt-5.5` regret 0 | interpret as a capability-scaling guardrail, not a frontier discriminator |

## Original repo commit check

Checked on 2026-05-29 before writing this ledger and rechecked on
2026-05-30 before PR 26.

| Repo | Status | New/relevant commits checked | Consequence for private build lab |
|---|---|---|---|
| `/Users/lichenyu/agenteconreadiness` (`origin/main`) | clean at `7cb0ca8` on 2026-05-30 | `c3520ac` review corrections; `f69e883` OSS availability / borrow-substrate strategy; `a0e17b1` read-first refocus doc; `1e13623` RLHF appropriateness vs economic optimality theory; `d517c2e` oracle-availability and `(primitive x regime)` sharpening; `4a5b914` no-oracle evaluation and TERMS information-set resolution; `7cb0ca8` generator-verifier method, manufacturable-oracle correction, and bargaining-Bayes mechanism | PR 29 implements the RLHF theory; PR 37 follows `d517c2e`; PR 39 follows `4a5b914`; PRs 41-42 implement the no-oracle/proper-scoring path; PR 44 implements the `7cb0ca8` bargaining-Bayes posterior-scaffold falsifier; PR 45 implements the first generator-verifier relationship-law prototype while broader mass production remains future work |
| `/Users/lichenyu/persona_simulator` (`origin/master`) | dirty: modified `sprint/adversarial_scam_arena_toy/exploits.json`; untracked `.playwright-mcp/` logs; fetched at `ae9c7b2` on 2026-05-30 | `47acd7a` GPT-5.x support/model override; `8404d2a` OpenAI scam-arena run; `c1fbbd0` borrow-substrate doc; `121e2e0` cross-model scam result + timeout/label fixes; `94fa606`/`efa26d6` mirror oracle-availability and no-oracle information-set methodology; `ae9c7b2` mirrors generator-verifier and bargaining-Bayes additions | record upstream evidence only; do not import OpenRouter/chat-completions client into this Responses-only lab; PRs 44-45 use the mirrored `7cb0ca8` mechanisms without touching original dirty artifacts |

Upstream sprint finding to preserve: OpenAI scam-arena run with `gpt-5.5`
attacker and `gpt-5.5`/`gpt-5.4-mini` defenders found both frontier OpenAI
defenders resistant in the single-shot scam setting. That revises the adversarial
interpretation: the scam arena is a valid instrument, but the Vending-Bench
"falls for scam suppliers" failure likely needs long-horizon stress, not a clean
one-shot value estimate.

Uncommitted original-repo artifacts are intentionally left untouched. The private
build lab should not depend on `.playwright-mcp/` logs or the local
`exploits.json` mutation.

## Approach decisions locked by validation

1. Do not add new tasks blindly. Each new task needs an oracle, a failure
   baseline, and either an immediate offline validation or a cheap OpenAI smoke.
2. Do not interpret economic metrics without parse rate. Parse failures are eval
   failures first.
3. Treat `common_value` as a smaller-model capability guardrail unless repeated
   frontier failures appear.
4. Treat single-shot scam resistance as a robust null, not evidence that
   long-horizon scam susceptibility is solved.
5. Keep the private lab OpenAI Responses API only. Original sprint code can
   inform design but should not pull in OpenRouter, Anthropic aliases, or
   chat-completions-specific behavior.
6. The refocus-doc priorities now have first runnable probes: broader
   regime-appropriateness, sampled live-smoke control, long-horizon scam stress,
   RLHF-appropriateness/alignment-tax, revealed allocation, alpha-maxmin
   ambiguity, and protocol/reservation-depth bargaining.
7. Sampled OpenAI validation now parses cleanly across `gpt-5.5`, `mini`, and
   `nano` on alignment-tax, bargaining, and supplier-scam first cases. Next live
   work should target harder cases or full-task runs; next implementation work
   should deepen an existing axis, not invent another headline.
8. Belief-bargaining now has a first multi-turn signal sequence probe. Next
   bargaining-adjacent work should move to full multi-turn interaction or
   opponent-policy simulation rather than another static cue variant.
9. Mechanism choice now has a first incentive-compatibility probe. Next
   mechanism work should move toward repeated/equilibrium simulation rather than
   another static scoring field.
10. Market now has a first inventory/capital-survival probe. Next market work
    should add adaptive multi-period policies or opponent-policy shifts rather
    than another one-price inventory case.
11. Retail now has multi-period inventory/runway cases. The next retail-adjacent
    build should couple inventory timing with supplier trust/scam risk, not just
    add more deterministic demand paths.
12. Source commit `d517c2e` is now reflected in the lab strategy: single-agent
    v0 remains valid when the task removes easy oracle recognition through
    horizon, reserve, framing, or configured-principal stress.
13. Supplier-scam now has both claim-credulity and delayed-inventory timing
    variants. Next supplier work should move to adaptive vendor reputation or
    multi-round belief updates, not another static supplier option list.
14. Source commit `4a5b914` is now reflected in the lab strategy: when the
    omniscient oracle is not a fair bar, score the posterior/control target
    implied by accessible signals and separately document irreducible uncertainty.
15. Strategic drift now includes imperfect-information and N-player stress.
    Next strategic work should move to adaptive opponent-policy or reputation
    dynamics rather than another static HONOR/GRAB payoff case.
16. Experiment design now includes an adaptive two-step screen/confirm pattern.
17. Forecast calibration now implements the no-oracle/proper-scoring path from
    source commit `4a5b914`, including reliability-weighted likelihood-ratio
    stress. Live `nano` solves both the first and reliability-weighted sets, so
    future calibration work should avoid simply spelling out the Bayes update;
    use less explicit framing, aggregate calibration bins, or distribution-shift
    holdouts if the goal is model discrimination.
18. Supplier-scam now includes adaptive vendor reputation. This is the first
    new post-calibration stress that separates live `nano`: it avoids obvious
    scams and reserve failures but keeps buying from a supplier after repeated
    delivery failures.
19. Source commit `7cb0ca8` adds the bargaining-Bayes mechanism. PR 44 tests its
    falsifier: explicit posterior scaffolding closes `nano`'s strategic
    cheap-talk bargaining gap, so the observed deficit is consistent with
    implicit sequential belief-state failure rather than inability to act on a
    supplied posterior.
20. Source commit `7cb0ca8` also adds the generator-verifier method. PR 45 is a
    first relationship-law implementation, but it deliberately keeps a fit
    signal next to the law check because relationship-only verification can be
    gamed by monotone but wrong answers.
21. The procurement v0 proposal called for paraphrase and preference-flip
    counterfactuals. PR 46 fills that gap without changing the original
    procurement task, and the first live `nano` result suggests wording stability
    is easier than fully updating the principal's weighted objective.
22. The pricing v0 proposal also called for sales-evidence perturbations. PR 47
    fills that gap and validates the harness; the first live `nano` result solves
    the exact linear cases, so future pricing counterfactuals should add noisy
    evidence, nonlinearity, or competing priors before using this as a failure
    result.
23. PR 48 adds the first noisy evidence stress for pricing. `nano` still moves
    in the right direction, so the failure is not counterfactual stickiness; the
    useful signal is estimation/fit error under noisy sales evidence.
24. PR 49 adds aggregate-bin calibration with shrinkage. It validates the
    aggregate-bin harness and bad baselines, but live `nano` solves the explicit
    shrinkage instruction, so the next calibration discriminator should use
    held-out bin curves or less formulaic framing.
25. PR 50 adds held-out calibration-curve interpolation. It validates the
    interpolation harness and bad baselines, but live `nano` still solves the
    explicit instruction. The remaining calibration frontier is less formulaic
    presentation, denser/noisier tables, or true holdout scoring without showing
    the recalibration recipe.
26. PR 51 removes the explicit shrink/interpolate recipe while keeping the same
    held-out curve target. This produces the first live `nano` calibration-curve
    failure in the stack: parse remains clean, but expected Brier regret rises to
    0.0890095 and the model partially reverts toward the raw score.
27. PR 52 adds denser, noisier implicit calibration curves. Live `nano` mostly
    recovers the curve target but still overshoots two sparse/noisy cases,
    producing nearest-bin misses on half the cases. This suggests the PR 51
    failure is more about implicit recalibration framing than table density
    alone.
28. PR 53 removes machine-readable calibration row names while preserving the
    same dense/noisy target. This reopens a strong live `nano` gap, so row-label
    naturalness is an important calibration-stress dimension separate from
    density or formula hints.
29. PR 54 moves the market axis from static price choice to opponent-policy
    adaptation. Live `nano` avoids the simple static/sticky baselines but still
    has nonzero profit regret, making opponent-next-price inference a useful
    moderate stress signal.
30. PR 55 adds repeated mechanism scoring with retention and manipulation
    growth. The offline harness separates myopic/revenue/risk-blind baselines,
    but live `nano` solves the explicit version, so the next mechanism stress
    should hide the recurrence or require simulated participant response rather
    than spelling out the full-horizon scoring rule.
31. PR 56 hides the repeated-mechanism field names behind natural pilot-outcome
    labels while keeping the same oracle. This produces a small live `nano`
    score-regret gap without parse failures, so label naturalness is a useful
    mechanism-stress dimension but the next mechanism build should still move
    toward simulated participant response for stronger separation.
32. PR 57 adds simulated participant-count response. It separates revenue,
    one-period, and response-blind offline baselines and creates a larger live
    `nano` mechanism gap than PR 56, but the live miss is not a simple named
    baseline collapse; future mechanism work should test multi-agent strategic
    response or hidden participant elasticity.
