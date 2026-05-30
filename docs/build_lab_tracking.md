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
| 58 | `review/58-mechanism-elasticity-inference` | hidden-elasticity mechanism choice | oracle score regret 0; same offline dynamic range as PR 57; live `nano` regret 23.5998 with parse 1.00 |
| 59 | `review/59-mechanism-strategic-response` | multi-agent strategic-response mechanism choice | oracle score regret 0; revenue baseline regret 118159; one-period and response-blind regret 52103.9; live `nano` regret 15152.2 with parse 1.00 |
| 60 | `review/60-mechanism-strategic-equilibrium` | strategic-equilibrium mechanism choice | oracle score regret 0; revenue baseline regret 385487; response-blind regret 238424; live `nano` regret 31048.2 with parse 1.00 |
| 61 | `review/61-regime-law-holdout` | generated regime-law holdout family | oracle mean absolute error 0 across 32 holdout prompts; EV and half baselines obey relationship laws but fail fit; live `nano` mean error 0.402735 with law violation 0.62 |
| 62 | `review/62-regime-law-audit` | generated regime-law validity audit | oracle accuracy 1.00 across 40 law claims; always-valid baseline accuracy 0.75 and invalid-accept 1.00; live `nano` accuracy 0.825 with invalid-accept 0.10 and valid-reject 0.20 |
| 63 | `review/63-pricing-law-audit` | pricing comparative-statics law audit | oracle accuracy 1.00 across 10 pricing-law claims; always-valid and always-invalid baselines both accuracy 0.50; live `nano` accuracy 1.00 with parse 1.00 |
| 64 | `review/64-pricing-evidence-law-audit` | evidence-derived pricing-law audit | oracle accuracy 1.00 across 8 evidence-derived law claims; always-valid and always-invalid baselines both accuracy 0.50; live `nano` accuracy 1.00 with parse 1.00 |
| 65 | `review/65-pricing-evidence-law-holdout` | generated pricing evidence-law holdout | oracle accuracy 1.00 across 24 neutral-ID holdout law claims; always-valid and always-invalid baselines both accuracy 0.50; live `nano` accuracy 1.00 with parse 1.00 |
| 66 | `review/66-pricing-cross-elasticity` | cross-product pricing evidence | oracle mean price error 0.0016 across 6 prompts; own-price-only baseline error 8.4246 and cross-blind miss 1.00; live `nano` error 1.4380 with parse 1.00 |
| 67 | `review/67-pricing-multi-product` | joint multi-product pricing | oracle two-price L1 error 0.0034 across 6 prompts; independent single-product baseline error 19.2972 and independent miss 1.00; live `nano` error 7.6586 with parse 1.00 |
| 68 | `review/68-pricing-multi-natural` | natural-label joint pricing | same offline oracle/baseline separation as PR 67; live `nano` error 40.8911 with parse 1.00 |
| 69 | `review/69-supplier-scam-natural` | natural-label supplier-scam stress | same offline oracle/baseline separation as `supplier_scam`; live `nano` constrained regret 50.57 and reputation miss 1.00 with parse 1.00 |
| 70 | `review/70-market-policy-inventory` | inventory-constrained opponent-policy adaptation | oracle constrained terminal-cash regret 0; inventory-blind regret 1595.31, last-price regret 2204.75, static-Nash regret 3450.07; live `nano` regret 165.418 with parse 1.00 |
| 71 | `review/71-belief-bargaining-interaction` | two-offer belief-bargaining interaction policy | oracle expected-surplus gap 0; single-cue gap 18.0089, single-offer gap 20.4725, prior gap 30.9023; live `nano` gap 3.7145 with parse 1.00 |
| 72 | `review/72-procurement-bundle` | combinatorial procurement bundle choice | oracle score regret 0; compatibility-blind regret 0.30145, category-blind regret 2.75435, cheapest-pair regret 5.6315; live `nano` solves with parse 1.00 |
| 73 | `review/73-procurement-bundle-natural` | natural-label procurement bundle choice | same offline oracle/baseline separation as `procurement_bundle`; live `nano` still solves with parse 1.00 |
| 74 | `review/74-procurement-bundle-evidence` | outcome-evidence procurement bundle choice | same offline oracle/baseline separation as `procurement_bundle`; live `nano` still solves with parse 1.00 |
| 75 | `review/75-procurement-bundle-noisy-evidence` | noisy outcome-evidence procurement bundle choice | same offline oracle/baseline separation as `procurement_bundle`; live `nano` still solves with parse 1.00 |
| 76 | `review/76-procurement-bundle-history` | deployment-history procurement bundle choice | same offline oracle/baseline separation as `procurement_bundle`; live `nano` still solves with parse 1.00 |
| 77 | `review/77-procurement-bundle-reserve` | reserve-sensitive procurement bundle choice | oracle score regret 0; compatibility-blind regret 0.1452, category-blind regret 5.50615, cheapest-pair regret 5.549; live `nano` still solves with parse 1.00 |
| 78 | `review/78-pricing-multi-capacity` | capacity-constrained joint pricing | oracle two-price L1 error 0; capacity-blind error 12.635, independent error 23.8125; live `nano` error 13.235 with parse 1.00 |
| 79 | `review/79-pricing-inventory-markdown` | sequential inventory markdown pricing | oracle early/late price L1 error 0; myopic single-period error 30.615, rounded error 5.8125; live `nano` error 6.7725 with parse 1.00 |
| 80 | `review/80-pricing-markdown-noisy` | noisy natural-label inventory markdown pricing | oracle early/late price L1 error 0; myopic single-period error 30.4475, rounded error 5.3125; live `nano` error 9.3825 with parse 1.00 |
| 81 | `review/81-procurement-vendor-update` | sequential vendor-update procurement | oracle score regret 0; myopic regret 6.43164, reputation-blind regret 25.7697; live `nano` regret 71.8555 with parse 1.00 |
| 82 | `review/82-mechanism-interaction-trace` | mechanism choice from observed interaction traces | oracle score regret 0; revenue/one-period/trace-blind regret 63564; live `nano` regret 35176.2 with parse 1.00 |
| 83 | `review/83-pricing-hidden-intervention` | pricing with hidden non-price intervention adjustment | oracle price error 0.00275; intervention-blind error 33.4577; live `nano` error 5.6485 with parse 1.00 |
| 84 | `review/84-forecast-shift-calibration` | source-to-target cohort-shift forecast calibration | oracle expected Brier regret 0; nearest-bridge regret 0.00197587, source-curve regret 0.0289593, raw-score regret 0.0432897; live `nano` regret 0.0151186 with parse 1.00 |
| 85 | `review/85-market-trace-inventory` | trace-based inventory pricing | oracle constrained terminal-cash regret 0; trace-blind regret 960.911, inventory-blind regret 1509.83, last-price regret 2125.34, static-Nash regret 3378.04; live `nano` regret 4226.05 with parse 1.00 |
| 86 | `review/86-market-trace-markdown` | staged trace-based inventory pricing | oracle constrained terminal-cash regret near 0; one-price regret 15.8076, trace-blind regret 904.786, inventory-blind regret 1525.64, static-Nash regret 3393.85; live `nano` regret 5775.24 with parse 1.00 |
| 87 | `review/87-market-trace-replenishment` | trace-based replenishment planning | oracle constrained terminal-cash regret near 0; one-price regret 15.8076, replenishment-blind regret 902.079, trace-blind regret 2269.28, no-replenishment regret 3287.08; live `nano` regret 7644.80 with parse 1.00 |
| 88 | `review/88-mechanism-trace-equilibrium` | mechanism trace equilibrium | oracle score regret 0; equilibrium-blind regret 143099, revenue/trace-projection regret 258815; live `nano` regret 93836.23 with parse 1.00 |
| 89 | `review/89-mechanism-trace-equilibrium-natural` | natural-label mechanism trace equilibrium | same offline oracle/baseline separation as PR 88; live `nano` regret 43035.17 with parse 1.00 |
| 90 | `review/90-market-trace-replenishment-natural` | natural-label trace replenishment planning | same offline oracle/baseline separation as PR 87; live `nano` regret 7412.39 with parse 1.00 |
| 91 | `review/91-pricing-multi-capacity-noisy` | noisy finite-stock joint pricing | oracle two-price L1 error 0; capacity-blind error 13.4225, independent error 33.52; live `nano` error 30.0375 with parse 1.00 |
| 92 | `review/92-market-trace-replenishment-noisy` | noisy natural trace replenishment planning | oracle constrained terminal-cash regret near 0; one-price regret 3.95377, replenishment-blind regret 878.23, trace-blind regret 2542.69, no-replenishment regret 3286.21; live `nano` regret 8802.45 with parse 1.00 |
| 93 | `review/93-mechanism-trace-equilibrium-noisy` | noisy local mechanism trace equilibrium | oracle score regret 0; trace-blind regret 193.156, equilibrium-blind regret 143597, trace-projection regret 190149, revenue regret 260868; live `nano` regret 60204.84 with parse 1.00 |
| 94 | `review/94-pricing-multi-product-markdown-noisy` | noisy multi-product markdown pricing | oracle four-price L1 error 0; capacity-blind error 40.99, myopic error 47.9375, independent error 69.9625; live `nano` error 61.3 with parse 1.00 |
| 95 | `review/95-pricing-inventory-replenishment-noisy` | noisy replenishment pricing | oracle launch/restock/clearance decision L1 error 0; no-restock error 62.3125, myopic/capacity-fill error 36.01; live `nano` error 27.98 with parse 1.00 |
| 96 | `review/96-procurement-vendor-update-noisy` | noisy receiving-ledger vendor-update procurement | oracle score regret 0; myopic regret 6.43164, reputation-blind/cheapest regret 25.7697; live `nano` regret 84.9162 with parse 1.00 |
| 97 | `review/97-forecast-rolling-calibration` | rolling time-local calibration | oracle expected Brier regret 0; pooled-history regret 0.00274588, stale-window regret 0.05431, raw-score regret 0.0652963; live `nano` solves with parse 1.00 |

## Task result ledger

All results below are from the current private review stack on 2026-05-29/30
unless explicitly marked as historical/upstream.

| Task | Axis / purpose | Current offline result | Interpretation / limitation |
|---|---|---|---|
| `regime` | four-regime EV/Kelly/CVaR/CRRA utility selection | oracle mean absolute error 0 across 32 trials; EV baseline error 0.586033; EV CVaR drawdown-violation rate 0.88; all targeted parses 1.00 | broadened to even-money, skewed, thin-edge, negative-EV, small-edge, and hard-barrier gamble families |
| `regime_relationship` | generator-verifier relationship laws for regime fractions | oracle mean absolute error 0 across 16 generated prompts; EV-only baseline mean error 0.672542 with law violation 0 and fit-fail 1.00; wrong-regime baseline mean error 0.472292 with law violation 1.00 | first runnable source `7cb0ca8` generator-verifier method: verify the relationship, but pair it with fit so degenerate monotone answers do not pass |
| `regime_holdout` | broader generated holdout for regime relationship laws | oracle mean absolute error 0 across 32 generated holdout prompts; EV-only baseline mean error 0.593282 with law violation 0 and fit-fail 0.875; half baseline mean error 0.437032 with law violation 0 and fit-fail 1.00; wrong-regime baseline law violation 0.875 | extends PR 45 beyond fixed generated fixtures; live `nano` parses but violates laws on 62% of groups and fails fit on every group, so the generator-verifier fit channel remains necessary |
| `regime_law_audit` | generated verifier for valid/invalid regime-law claims | oracle accuracy 1.00 across 40 law-audit prompts; always-valid baseline accuracy 0.75 with invalid-accept 1.00; always-invalid accuracy 0.25 with valid-reject 1.00; inverted baseline accuracy 0.00 | separates verifier-side law validity from numeric fraction fit; live `nano` parses with accuracy 0.825, invalid-accept 0.10, and valid-reject 0.20 |
| `alignment_tax` | RLHF appropriateness vs configured economic objective | oracle objective regret 0; helpful default regret 71.725; profit-only regret 62.35; helpful overconcession rate 1.00 | operationalizes the new upstream theory: human-approval defaults can sacrifice economic optimality even when all actions are compliant |
| `principal_inference` | infer configured principal CRRA parameter | oracle error 0; generic-gamma error 0.408333 | grade-side CRRA mismatch is mechanically measurable |
| `portfolio` | configured-principal portfolio choice | oracle regret 0; max-return regret 0.599325; low-risk regret 0.0241 | separates return-chasing from configured utility |
| `revealed_allocation` | stylized 13F-style revealed-preference continuous allocation | oracle utility regret 0; max-return regret 0.0693568; low-risk regret 0.0504201; equal-weight regret 0.0182864; parse 1.00 | first continuous allocation version of the configured-principal grade; still synthetic traces |
| `ambiguity` | maxmin/alpha-maxmin under Knightian ambiguity | oracle configured regret 0 across 5 cases; reference-prior regret 11.5796; pure-maxmin regret 2.32038; optimistic regret 14.5817 | now includes signal-updated priors and configured alpha; exposes both single-prior collapse and wrong ambiguity-attitude extremes |
| `bargaining` | D2/TERMS-style gate plus grade, now with alternating-offer and hidden-reservation variants | oracle grade error 0 across 6 cases; generic gate baseline grade error 0.374225; round-blind alternating-offer miss 1.00; optimistic-budget hidden-reservation miss 1.00 | confirms "gate-only surplus extraction" is not grade fidelity and adds first protocol/reservation-depth stressors |
| `belief_bargaining` | cue use, posterior bargaining, multi-turn opponent modeling, and strategic cheap-talk likelihoods | oracle surplus gap 0 across 9 prompts; prior baseline gap 13.6088; single-cue baseline gap 33.5649 with multi-turn miss 1.00; literal-claim baseline gap 60.1056; live `nano` strategic base gap 52.4859 but scaffold gap 0 | implements the bargaining-Bayes falsifier from source `7cb0ca8`: when posterior state is externalized, `nano` closes the strategic cheap-talk gap, isolating implicit sequential belief-state failure |
| `belief_bargaining_interaction` | two-offer bargaining policy with rejection-contingent fallback pricing | oracle expected-surplus gap 0 across 4 interaction cases; single-cue baseline gap 18.0089; single-offer baseline gap 20.4725 with single-offer miss 1.00; prior-plan baseline gap 30.9023 | moves beyond static cue pricing by requiring an opening price plus a fallback price, where rejection of the opener is informative about buyer WTP |
| `market` | simultaneous price competition plus inventory/capital survival pricing | oracle price gap 0.000016 across 5 cases; collusive gap 0.114756 and collusion rate 1.00 on one-shot cases; liquidation gap 0.451656 with survival cash gap 4614.45 and reserve violation 1.00 | separates collusion drift from inventory-survival and liquidation failures |
| `market_policy_shift` | repeated-market opponent-policy shift | oracle profit regret 0 across 4 policy-shift cases; static-Nash baseline regret 541.191 with static miss 1.00; sticky-last-price baseline regret 189.006 with last-price miss 1.00; collusive baseline regret 1784.78; live `nano` regret 18.691 with parse 1.00 | first market probe beyond static price fields: infer competitor next price from price-history and policy-shift signal before best-responding |
| `market_policy_inventory` | repeated-market opponent-policy shift with finite inventory, obligations, holding costs, and terminal reserve | oracle constrained terminal-cash regret 0 across 4 inventory-policy cases; inventory-blind baseline regret 1595.31 with inventory-blind miss 1.00; sticky-last-price regret 2204.75; static-Nash regret 3450.07 | combines opponent next-price inference with survival-style inventory pricing, so one-period policy-aware best response is not sufficient |
| `market_trace_inventory` | trace-based inventory pricing from observed competitor fill and remaining-stock rows | oracle constrained terminal-cash regret 0 across 4 trace cases; trace-blind baseline regret 960.911 with trace-blind miss 1.00; inventory-blind regret 1509.83 with inventory-blind miss 0.75; last-price regret 2125.34; static-Nash regret 3378.04; live `nano` regret 4226.05 with parse 1.00 and reserve violation 0.50 | removes explicit opponent-policy labels and requires reading market traces before inventory-aware pricing; live `nano` overprices two sell-through cases and violates reserve despite strong offline controls |
| `market_trace_markdown` | early/late trace-based inventory pricing from observed competitor fill and remaining-stock rows | oracle constrained terminal-cash regret near 0 across 4 staged trace cases; one-price baseline regret 15.8076; trace-blind regret 904.786; inventory-blind regret 1525.64; static-Nash regret 3393.85; live `nano` regret 5775.24 with parse 1.00, price L1 65.295, and reserve violation 0.50 | extends PR 85 from a fixed posted price to a staged early/late plan; live `nano` misses both trace inference and staged sell-through timing, producing the largest market gap so far |
| `market_trace_replenishment` | early/late trace-based pricing with an optional replenishment buy before the late window | oracle constrained terminal-cash regret near 0 across 4 replenishment cases; one-price baseline regret 15.8076; replenishment-blind regret 902.079; trace-blind regret 2269.28; no-replenishment regret 3287.08; live `nano` regret 7644.80 with parse 1.00, decision L1 81.7674, and reserve violation 0.50 | extends PR 86 from a price-only staged plan to a coupled price/order plan; live `nano` misses both trace inference and the stockout-vs-overbuy replenishment tradeoff, producing the largest market gap so far |
| `market_trace_replenishment_natural` | natural-label early/late trace-based pricing with optional restock before the late window | oracle constrained terminal-cash regret near 0 across 4 natural replenishment cases; one-price baseline regret 15.8076; replenishment-blind regret 902.079; trace-blind regret 2269.28; no-replenishment regret 3287.08; live `nano` regret 7412.39 with parse 1.00, decision L1 74.7824, and reserve violation 0.50 | keeps PR 87's oracle while replacing machine-readable competitor and replenishment labels with rival shelf observations, cash floor, and restock language; live `nano` preserves the large trace/replenishment gap |
| `market_trace_replenishment_noisy` | natural-label early/late trace-based pricing with optional restock from lumpy regional shelf observations | oracle constrained terminal-cash regret near 0 across 4 noisy replenishment cases; one-price baseline regret 3.95377; replenishment-blind regret 878.23; trace-blind regret 2542.69; no-replenishment regret 3286.21; live `nano` regret 8802.45 with parse 1.00, decision L1 78.2524, and reserve violation 0.25 | adds PR 80-style lumpy evidence to the strongest market trace-replenishment surface; live `nano` misses the noisy trace-conditioned stockout-vs-overbuy tradeoff even more strongly than PR 87/90 |
| `matching` | stability/access-aware matching | oracle regret 0; access regret 51.675; max-value regret 175.037 | separates value maximization from stability/access constraints |
| `screening` | adverse-selection contract menus | oracle regret 0; constraint-blind regret 37.7125; max-profit regret 71.5061 | exposes IC/IR blind menus |
| `moral_hazard` | hidden-action contract design | oracle profit regret 0; high-bonus regret 20.5875; hidden-action blind/fixed regret 49.3375 | exposes assuming effort for free |
| `auction` | configured reserve choice | oracle reserve error 0; revenue baseline error 0.221354 | separates Myerson revenue reserve from configured objective |
| `common_value` | winner's curse guardrail | oracle profit regret 0; winner-curse blind regret 17.3875; aggressive regret 46.72 | good capability-scaling guardrail; historical live run found smaller OpenAI models miss and `gpt-5.5` solves |
| `mechanism` | choose among allocation mechanisms with strategic-risk and incentive-compatibility checks | oracle score regret 0 across 6 cases; revenue regret 62.8342; risk-blind regret 17.6667; IC-blind regret 18.4342 and IC-blind miss 1.00 | separates revenue default, risk blindness, and incentive-compatibility blindness |
| `mechanism_repeated` | repeated mechanism choice with retention and manipulation dynamics | oracle score regret 0 across 4 repeated cases; revenue baseline regret 697.695 with revenue miss 1.00; one-period baseline regret 567.864; risk/manipulation-blind baseline regret 226.083; live `nano` regret 0 with parse 1.00 | validates the repeated/equilibrium mechanism harness, but current formulaic version does not separate live `nano` |
| `mechanism_repeated_natural` | natural-label repeated mechanism choice with the same repeated-program oracle | oracle score regret 0 across 4 repeated cases; revenue baseline regret 697.695 with revenue miss 1.00; one-period baseline regret 567.864; risk/manipulation-blind baseline regret 226.083; live `nano` regret 3.50137 with parse 1.00 | hides explicit revenue/manipulation field names behind pilot-outcome labels; weaker than the strongest calibration failures, but it reopens a live mechanism fit gap without changing the oracle |
| `mechanism_participant_response` | mechanism choice with simulated participant retention and exit response | oracle score regret 0 across 4 response cases; revenue baseline regret 1771.34 with revenue miss 1.00; one-period baseline regret 69.0158; response-blind baseline regret 69.0158; live `nano` regret 23.5998 with parse 1.00 | moves mechanism stress from static repeated scoring to endogenous participant-count dynamics; live gap is larger than PR 56 but still not a named-baseline collapse |
| `mechanism_elasticity_inference` | mechanism choice with retention sensitivity inferred from pilot observations | oracle score regret 0 across 4 response cases; revenue baseline regret 1771.34 with revenue miss 1.00; one-period baseline regret 69.0158; response-blind baseline regret 69.0158; live `nano` regret 23.5998 with parse 1.00 | validates a hidden-elasticity prompt surface over the same oracle, but does not add live separation beyond PR 57 |
| `mechanism_strategic_response` | mechanism choice with multi-agent strategic-share dynamics | oracle score regret 0 across 4 strategic-response cases; revenue baseline regret 118159 with revenue miss 1.00; one-period baseline regret 52103.9; response-blind baseline regret 52103.9; live `nano` regret 15152.2 with parse 1.00 | adds peer contagion, audit deterrence, manipulation harm, and retention loss; live `nano` has a large nonzero gap without collapsing to the simple baselines |
| `mechanism_strategic_equilibrium` | mechanism choice after solving self-consistent strategic-share equilibrium | oracle score regret 0 across 4 strategic-equilibrium cases; revenue baseline regret 385487 with revenue miss 1.00; response-blind initial-share baseline regret 238424; live `nano` regret 31048.2 with parse 1.00 | makes equilibrium solving the target rather than forward simulation; the live gap roughly doubles PR 59 while parse remains clean |
| `mechanism_interaction_trace` | mechanism choice from observed pilot interaction traces | oracle score regret 0 across 4 trace cases; revenue/one-period/trace-blind baselines regret 63564 with miss rate 1.00; live `nano` regret 35176.2 with parse 1.00 | implements the post-PR60 mechanism frontier note: infer future participant and strategic-share dynamics from realized interaction traces rather than static mechanism fields |
| `mechanism_trace_equilibrium` | mechanism choice from pilot traces plus self-consistent strategic-share response | oracle score regret 0 across 4 trace-equilibrium cases; equilibrium-blind baseline regret 143099; revenue and trace-projection baselines regret 258815; live `nano` regret 93836.23 with parse 1.00, revenue miss 0.25, trace-projection miss 0.25, and equilibrium-blind miss 0.00 | combines PR 60 equilibrium solving with PR 82 observed interaction traces; live `nano` has a larger mechanism gap than either prior mechanism trace/equilibrium variant while trace-blind remains a reported non-failure diagnostic |
| `mechanism_trace_equilibrium_natural` | natural-label mechanism choice from pilot outcome traces plus self-consistent strategic-share response | oracle score regret 0 across 4 natural trace-equilibrium cases; equilibrium-blind baseline regret 143099; revenue and trace-projection baselines regret 258815; live `nano` regret 43035.17 with parse 1.00 | keeps PR 88's oracle but removes explicit strategic-response field names; validates that the trace-equilibrium mechanism frontier survives pilot-outcome wording, though the live gap is smaller than the explicit PR 88 prompt |
| `mechanism_trace_equilibrium_noisy` | natural-label mechanism choice from noisy local pilot sheets plus self-consistent strategic-share response | oracle score regret 0 across 4 noisy trace-equilibrium cases; trace-blind baseline regret 193.156; equilibrium-blind baseline regret 143597; trace-projection baseline regret 190149; revenue baseline regret 260868; live `nano` regret 60204.84 with parse 1.00 | adds lumpy local-pilot variation to the PR 89 natural surface; the oracle is preserved while projection, equilibrium-blind, and revenue defaults remain large failures; live `nano` gap increases versus PR 89 without becoming a named-baseline collapse |
| `strategic_drift` | repeated strategic discipline under deterministic, imperfect-information, and N-player stress | oracle drift 0 across 55 rounds; stress-blind drift 0.163636 overall and 0.4737 on stress rounds; myopic drift 0.927273 | now scores against the accessible posterior/control bar for noisy-signal and N-player externality cases rather than an omniscient hidden-state answer |
| `forecast_calibration` | proper-scoring calibration when ex-ante omniscient labels are not a fair bar | oracle expected Brier regret 0 across 9 cases; underreact regret 0.0851473; raw-likelihood/reliability-blind regret 0.0920597 with reliability miss 1.00; base-rate regret 0.151373; overconfident regret 0.199375; live `nano` posterior L1 about 0.00025 and reliability miss 0 | direct implementation of the no-oracle methodology plus reliability-weighted evidence stress; useful as calibration plumbing, but still not currently a `nano` failure set |
| `forecast_aggregate` | aggregate-bin recalibration under distribution shift and small-bin uncertainty | oracle expected Brier regret 0 across 5 aggregate-bin cases; raw-score baseline regret 0.088221 with raw-score miss 1.00; no-shrink empirical-bin baseline regret 0.0668155 with shrinkage miss 1.00; base-rate baseline regret 0.00800648 | follows the ledger's post-PR42 recommendation: move beyond explicit Bayes updates into aggregate calibration bins with shrinkage and distribution-shift-style recalibration |
| `forecast_curve` | held-out aggregate calibration curve | oracle expected Brier regret 0 across 3 curve cases; raw-score baseline regret 0.089779 with raw-score miss 1.00; nearest-bin baseline regret 0.002067 with nearest-bin miss 1.00; base-rate baseline regret 0.043793 | extends aggregate calibration beyond one bin: shrink historical bins and interpolate to a held-out raw score |
| `forecast_curve_implicit` | implicit held-out aggregate calibration curve | oracle expected Brier regret 0 across 3 curve cases; raw-score baseline regret 0.089779 with raw-score miss 1.00; nearest-bin baseline regret 0.002067 with nearest-bin miss 1.00; base-rate baseline regret 0.043793; live `nano` regret 0.0890095 with parse 1.00 and raw-score miss 0.50 | preserves the same calibration target as `forecast_curve` but removes the explicit shrink/interpolate recipe; first calibration-curve variant that separates live `nano` |
| `forecast_curve_noisy` | dense/noisy implicit calibration curve | oracle expected Brier regret 0 across 4 noisy curve cases; raw-score baseline regret 0.0566631 with raw-score miss 1.00; nearest-bin baseline regret 0.00224894 with nearest-bin miss 1.00; base-rate baseline regret 0.0274858; live `nano` regret 0.00141703 with parse 1.00 and nearest-bin miss 0.50 | denser non-monotone tables reduce the raw-score failure but reveal sparse/noisy-bin overshooting; useful as a fit-stress signal, not as strong as PR 51 |
| `forecast_curve_natural` | natural-label dense/noisy calibration curve | oracle expected Brier regret 0 across 4 noisy curve cases; raw-score baseline regret 0.0566631 with raw-score miss 1.00; nearest-bin baseline regret 0.00224894 with nearest-bin miss 1.00; base-rate baseline regret 0.0274858; live `nano` regret 0.0197592 with parse 1.00, raw-score miss 0.67, and nearest-bin miss 0.75 | replacing machine-readable calibration row names with natural outcome-table labels reopens a clear live `nano` failure while preserving parse |
| `forecast_shift_calibration` | source-to-target cohort-shift calibration | oracle expected Brier regret 0 across 4 bridge cases; raw-score baseline regret 0.0432897 with raw-score miss 1.00; source-curve baseline regret 0.0289593 with source-curve miss 1.00; nearest-bridge baseline regret 0.00197587 with nearest-bridge miss 0.75; live `nano` regret 0.0151186 with parse 1.00, raw-score miss 0.75, source-curve miss 0.50, and nearest-bridge miss 0.00 | extends the calibration frontier from a single shifted curve to source-cohort transfer with a small target bridge sample; `nano` often notices the bridge direction but under-applies the local cohort adjustment |
| `forecast_rolling_calibration` | rolling time-local calibration after recent cohort drift | oracle expected Brier regret near 0 across 4 rolling-window cases; raw-score baseline regret 0.0652963 with raw-score miss 1.00; stale-window baseline regret 0.05431 with stale-window miss 1.00; pooled-history baseline regret 0.00274588 with pooled-history miss 1.00; live `nano` regret rounds to 0 with parse 1.00 | validates the rolling-calibration harness and baselines, but the explicit recency-weight prompt is saturated for live `nano`; harder calibration work should naturalize or hide the time-local weighting rule |
| `exploration` | unknown-environment exploration | oracle EV gap 0; exploit-only gap 193.3 | EconEvals-style exploration failure is mechanically exposed |
| `experiment_design` | noisy experiment design and adaptive posterior updates | oracle EV gap 0 across 5 cases; single-step baseline EV gap 14.6 and multi-step miss 1.00; greedy gap 168.204 and experiment miss 1.00 | exposes both skipping valuable experiments and failing to value a cheap first screen that unlocks a confirmatory second test |
| `retail` | cash/runway survival under one-cycle and multi-period inventory paths | oracle order error 0 across 5 cases; EV-order ruin probability 0.251; single-cycle baseline order error 0.0718266, multi-period cash gap 425.2572, and multi-period miss rate 1.00 | now covers both reserve-breaking over-ordering and horizon-blind under-ordering; live `nano` parses all cases but slightly over-orders both multi-period cases, creating small reserve risk |
| `procurement` | v0 qualitative procurement | oracle accuracy 1.00; first baseline 0.50 | current live OpenAI smoke also parses cleanly |
| `procurement_counterfactual` | procurement paraphrase consistency and principal preference flips | oracle accuracy 1.00 across 6 prompts; comfort baseline accuracy 0.666667 with paraphrase inconsistency 0, preference-flip miss 1.00, and sticky-base-on-flip 1.00; first baseline accuracy 0.166667 | implements the proposal's procurement counterfactual variants: wording changes should preserve the choice, but changed principal weights should move it |
| `procurement_bundle` | two-product bundle choice under category, budget, and compatibility constraints | oracle score regret 0 across 4 prompts; compatibility-blind regret 0.30145 with compatibility miss 1.00; category-blind regret 2.75435; cheapest-pair regret 5.6315 | adds a combinatorial procurement surface where item-wise utility is insufficient because pair compatibility can change the optimal bundle |
| `procurement_bundle_natural` | natural-label two-product bundle choice under line coverage, spend, and package-fit notes | same oracle and offline baseline dynamic range as `procurement_bundle`; live `nano` score regret 0 with parse 1.00 | validates that the bundle oracle survives SKU/package-fit wording, but the natural labels alone do not create a live model gap |
| `procurement_bundle_evidence` | infer package fit from two-SKU deployment outcome rows | same oracle and offline baseline dynamic range as `procurement_bundle`; live `nano` score regret 0 with parse 1.00 | removes listed fit deltas and asks the agent to use rollout hours, support tickets, and operator acceptance evidence; this validates the outcome-evidence surface but remains too easy for live `nano` |
| `procurement_bundle_noisy_evidence` | aggregate noisy deployment outcome rows before choosing the two-SKU package | same oracle and offline baseline dynamic range as `procurement_bundle`; live `nano` score regret 0 with parse 1.00 | adds conflicting row-level measurements, but `nano` still aggregates them correctly; future procurement work needs structural history or hidden interactions |
| `procurement_bundle_history` | aggregate multi-period deployment history before choosing the two-SKU package | same oracle and offline baseline dynamic range as `procurement_bundle`; live `nano` score regret 0 with parse 1.00 | converts rollout hours, prevented tickets, and rework reductions into a package-history value, but live `nano` still solves it; procurement likely needs endogenous budget/reserve dynamics rather than more static pair evidence |
| `procurement_bundle_reserve` | account for support-tail cost and reserve shortfall in the two-SKU package choice | oracle score regret 0 across 4 prompts; compatibility-blind regret 0.1452, category-blind regret 5.50615, cheapest-pair regret 5.549; live `nano` score regret 0 with parse 1.00 | adds reserve shortfall arithmetic and all-feasible-pair support scenarios, but live `nano` still solves it; procurement should stop adding two-SKU arithmetic variants unless the action becomes sequential |
| `procurement_vendor_update` | three-round vendor plan under delivery-history updates and reserve pressure | oracle score regret 0 across 4 sequential cases; myopic baseline regret 6.43164; reputation-blind and cheapest baselines regret 25.7697 with reputation miss 1.00; live `nano` regret 71.8555 with parse 1.00 | moves procurement from static bundle arithmetic to sequential vendor policy; live `nano` overpays for premium reliability in some rounds and misses the reserve-aware vendor sequence |
| `procurement_vendor_update_noisy` | three-round vendor plan from noisy receiving-ledger rows | oracle score regret 0 across 4 sequential cases; myopic baseline regret 6.43164; reputation-blind and cheapest baselines regret 25.7697 with reputation miss 1.00; live `nano` regret 84.9162 with parse 1.00 | hides aggregate on-time counts behind lumpy receiving areas; live `nano` overweights premium/reliable vendors even more strongly than the aggregate prompt while still avoiding a named baseline collapse |
| `pricing` | v0 continuous pricing | oracle revenue gap 0; rounded baseline gap 87.5 | validates continuous-action scoring |
| `pricing_counterfactual` | pricing posterior evidence perturbations | oracle posterior price error 0.002394 across 8 exact/noisy prompts; stale-price baseline price error 4.37114 with counterfactual-shift miss 1.00 and sticky-base-price 1.00; rounded baseline price error 2.40776 | implements the proposal's pricing sales-evidence perturbation variant: changed evidence should change the posterior revenue-maximizing price |
| `pricing_cross_elasticity` | pricing evidence with related-product price variation | oracle mean absolute price error 0.0016 across 6 prompts; own-price-only baseline error 8.4246, revenue gap 319.051, and cross-blind miss 1.00; rounded baseline error 1.9655 | moves past deterministic one-product law labels into cross-elasticity estimation; live `nano` parses and avoids own-only collapse but leaves a nonzero price/revenue gap |
| `pricing_multi_product` | joint pricing for two cross-demand products | oracle two-price L1 error 0.0034 across 6 prompts; independent single-product baseline error 19.2972, revenue gap 627.386, and independent miss 1.00; rounded baseline error 4.78782 | extends cross-elasticity from setting one focal price to jointly optimizing both product prices; live `nano` parses and has a larger nonzero gap without simply copying the independent baseline |
| `pricing_multi_product_natural` | natural-label joint pricing for two cross-demand products | oracle two-price L1 error 0.0034 across 6 prompts; independent single-product baseline error 19.2972, revenue gap 627.386, and independent miss 1.00; rounded baseline error 4.78782 | removes the explicit demand-equation recipe from PR 67; live `nano` parses but reverts to low campaign-row prices, creating a much larger gap than the formula-guided version |
| `pricing_multi_product_capacity` | joint pricing with finite stock caps under cross-demand | oracle two-price L1 error 0 across 4 capacity prompts; capacity-blind error 12.635 with capacity-blind miss 0.75; independent error 23.8125; live `nano` error 13.235 with parse 1.00 | adds inventory/capacity constraints to the joint-pricing live-gap line; live `nano` remains far from oracle without simply matching the named capacity-blind baseline |
| `pricing_multi_product_capacity_noisy` | joint pricing with finite stock caps under lumpy regional cross-demand evidence | oracle two-price L1 error 0 across 4 noisy capacity prompts; capacity-blind error 13.4225 with capacity-blind miss 0.75; independent error 33.52; live `nano` error 30.0375 with parse 1.00 | combines PR 78 finite-stock joint pricing with PR 80-style noisy evidence; live `nano` misses noisy complement/capacity cases without collapsing exactly to capacity-blind or independent baselines |
| `pricing_inventory_markdown` | sequential early/late pricing against one shared inventory pool | oracle early/late price L1 error 0 across 4 markdown prompts; myopic single-period baseline error 30.615 with myopic miss 1.00; rounded baseline error 5.8125; live `nano` error 6.7725 with parse 1.00 | shifts pricing from static stock caps to intertemporal stock allocation; live `nano` preserves the qualitative raise-early/late-price pattern but misses the optimum and trails the rounded baseline |
| `pricing_inventory_markdown_noisy` | noisy natural-label sequential markdown pricing | oracle early/late price L1 error 0 across 4 lumpy regional prompts; myopic single-period baseline error 30.4475 with myopic miss 1.00; rounded baseline error 5.3125; live `nano` error 9.3825 with parse 1.00 | lumpy launch/clearance evidence strengthens the PR 79 live gap while preserving clean parsing and the same deterministic oracle |
| `pricing_multi_product_markdown_noisy` | noisy two-product sequential markdown pricing with cross-demand and product-specific stock depletion | oracle four-price L1 error 0 across 4 lumpy launch/clearance prompts; capacity-blind baseline error 40.99; myopic baseline error 47.9375 with myopic miss 1.00; independent baseline error 69.9625; live `nano` error 61.3 with parse 1.00 | combines PR 91 noisy finite-stock joint pricing with PR 80 sequential markdown structure; live `nano` misses depletion/cross-window pricing without collapsing to any named baseline |
| `pricing_inventory_replenishment_noisy` | noisy sequential pricing with a mid-campaign replenishment quantity | oracle launch/restock/clearance decision L1 error 0 across 4 lumpy prompts; no-restock baseline error 62.3125 with no-restock miss 1.00; myopic and capacity-fill baselines error 36.01 with miss 1.00; live `nano` error 27.98 with parse 1.00 | changes the pricing action space from staged prices to a coupled price/order plan; live `nano` under-orders or overfills restock without collapsing to the named baselines |
| `pricing_hidden_intervention` | normal-campaign pricing after removing fixed intervention units and exposure multipliers | oracle mean price error 0.00275 across 4 noisy intervention cases; rounded baseline error 2.29931; intervention-blind baseline error 33.4577 with intervention-blind miss 1.00; live `nano` error 5.6485 with parse 1.00 | implements the hidden-intervention pricing frontier: `nano` handles parse and avoids the cap-price blind baseline, but misses the two-step adjustment plus noisy fit on two cases |
| `pricing_law_audit` | generated verifier for pricing comparative-static claims | oracle accuracy 1.00 across 10 law-audit prompts; always-valid and always-invalid baselines both accuracy 0.50; inverted baseline accuracy 0.00 | first cross-domain generator-verifier audit beyond regime laws; live `nano` solves this explicit pricing comparative-statics set, so harder pricing-law generation needs cap/constraint interactions or less formulaic framing |
| `pricing_evidence_law_audit` | evidence-derived verifier for pricing-law claims | oracle accuracy 1.00 across 8 prompts built from baseline/updated sales rows; always-valid and always-invalid baselines both accuracy 0.50; inverted baseline accuracy 0.00 | removes explicit alpha/beta parameters from the law audit and reuses posterior evidence cases, but live `nano` still solves this first evidence-derived set |
| `pricing_evidence_law_holdout` | generated evidence-derived verifier for pricing-law claims | oracle accuracy 1.00 across 24 neutral-ID holdout prompts spanning intercept, slope, cap, mixed, and intervention families; always-valid and always-invalid baselines both accuracy 0.50; inverted baseline accuracy 0.00 | fixes law-audit case-ID label leakage and expands the evidence-derived family, but live `nano` still solves this deterministic linear holdout |
| `scam` | adversarial belief-manipulation arena | oracle overpay 0; careful overpay 6.66667; credulous overpay 133.333; instrument fires | working judge-free dynamic range; single-shot frontier scam resistance should not be confused with long-horizon Vending-Bench failures |
| `supplier_scam` | long-horizon supplier-scam under cash/runway, inventory-timing, and reputation-update constraints | oracle constrained final-cash regret 0 across 11 rounds; credulous constrained regret 304.186 with scam-supplier rate 0.545; timing-blind constrained regret 99.6365 with timing-reserve violation rate 0.1818; reputation-blind constrained regret 23.385 with reputation miss 1.00; live `nano` constrained regret 53.4815 and reputation miss 1.00 | now separates inflated-claim credulity, delayed-inventory cash-lockup failures, and failure-history/reputation update misses |
| `supplier_scam_natural` | natural-label long-horizon supplier-scam under cash/runway, timing, and reputation constraints | oracle constrained final-cash regret 0 across 11 rounds; same credulous, timing-blind, and reputation-blind dynamic range as `supplier_scam`; live `nano` constrained regret 50.57 and reputation miss 1.00 | preserves the supplier reputation-update failure while replacing schema labels with business-language audit, delivery-history, and cash-obligation labels |

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
PR 58 hides the participant-response elasticity fields behind pilot stay-rate observations.
PR 59 adds multi-agent strategic-share response with peer contagion and audit deterrence.
PR 60 adds self-consistent strategic-share equilibrium solving.
PR 61 adds a generated regime-law holdout family for broader generator-verifier probes.
PR 62 adds generated valid/invalid law-claim auditing for the verifier side.
PR 63 adds a cross-domain pricing comparative-statics law audit.
PR 64 adds an evidence-derived pricing-law audit without explicit alpha/beta fields.
PR 65 adds a generated evidence-law holdout and neutralizes pricing-law case IDs
that previously exposed valid/invalid labels through the printed `case` field.
PR 66 adds cross-product pricing evidence with related-price variation.
PR 67 adds joint multi-product pricing and an environment override for longer
OpenAI output budgets on live stress prompts.
PR 68 adds a natural-label joint-pricing prompt over the same oracle.
PR 69 adds natural-label supplier-scam rows over the same long-horizon trust
and cash oracle.
PR 70 adds inventory-constrained market-policy adaptation over the existing
opponent-policy-shift path.
PR 71 adds a two-offer belief-bargaining interaction policy.
PR 72 adds a combinatorial procurement bundle task with category coverage,
budget feasibility, and pairwise compatibility.
PR 73 adds a natural-label prompt over the same procurement bundle oracle.
PR 74 replaces listed package-fit deltas with deployment outcome evidence.
PR 75 adds noisy repeated deployment measurements for the same package-fit signal.
PR 76 converts multi-period deployment history into the package-fit signal.
PR 77 adds support-tail cost and reserve-shortfall pressure to the bundle choice.
PR 78 pivots back to pricing with finite-stock joint pricing constraints.
PR 94 combines noisy multi-product finite-stock pricing with sequential
launch/clearance depletion and product-specific liquidation floors.
PR 95 adds a noisy replenishment pricing task with launch price, restock
quantity, and clearance price decisions.
PR 96 adds a noisy receiving-ledger version of the sequential vendor-update
procurement task.
PR 97 adds rolling time-local calibration with recency-weighted calibration
windows.

| Check | Command | Result |
|---|---|---|
| Unit tests | `python -m pytest` | 222 tests passed after PR 97 |
| Full offline oracle task pass | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 76 task runners executed; oracle errors/regrets zero or expected near-zero; includes `mechanism_trace_equilibrium_noisy` with n=4, score regret 0 and all named miss diagnostics 0; includes `market_trace_replenishment_noisy` with n=4, constrained terminal-cash regret near 0, decision L1 0, reserve violation 0, no-replenishment miss 0, one-price miss 0, trace-blind miss 0, and replenishment-blind miss 0; includes `pricing_inventory_replenishment_noisy` with n=4, decision L1 error 0 and revenue gap 0; includes `procurement_vendor_update_noisy` with n=4, score regret 0, parse 1.00, and named miss diagnostics 0; includes `forecast_rolling_calibration` with n=4, expected Brier regret near 0 and named miss diagnostics 0; scam control `instrument_fires=True`; alignment-tax regret 0; revealed-allocation regret 0 |
| Regime holdout differential sweep | `python3 -m aeread_lab.cli --sweep --task regime_holdout --agents offline:oracle,offline:ev,offline:half,offline:wrong_regime --no-cache` | oracle rank 1 with mean absolute error 0; wrong-regime mean error 0.416013 with law violation 0.875; half baseline mean error 0.437032 with law violation 0 and fit-fail 1.00; EV-only mean error 0.593282 with law violation 0 and fit-fail 0.875; parse 1.00 |
| Regime law-audit sweep | `python3 -m aeread_lab.cli --sweep --task regime_law_audit --agents offline:oracle,offline:law_accept,offline:law_reject,offline:law_invert --no-cache` | oracle rank 1 with accuracy 1.00; always-valid/accept baseline accuracy 0.75 with invalid-accept 1.00; always-invalid/reject accuracy 0.25 with valid-reject 1.00; inverted baseline accuracy 0.00; parse 1.00 |
| Pricing law-audit sweep | `python3 -m aeread_lab.cli --sweep --task pricing_law_audit --agents offline:oracle,offline:law_accept,offline:law_reject,offline:law_invert --no-cache` | oracle rank 1 with accuracy 1.00; always-valid and always-invalid baselines both accuracy 0.50; inverted baseline accuracy 0.00; parse 1.00 |
| Pricing evidence-law-audit sweep | `python3 -m aeread_lab.cli --sweep --task pricing_evidence_law_audit --agents offline:oracle,offline:law_accept,offline:law_reject,offline:law_invert --no-cache` | oracle rank 1 with accuracy 1.00; always-valid and always-invalid baselines both accuracy 0.50; inverted baseline accuracy 0.00; parse 1.00 |
| Pricing evidence-law-holdout sweep | `python3 -m aeread_lab.cli --sweep --task pricing_evidence_law_holdout --agents offline:oracle,offline:law_accept,offline:law_reject,offline:law_invert --no-cache` | oracle rank 1 with accuracy 1.00; always-valid and always-invalid baselines both accuracy 0.50; inverted baseline accuracy 0.00; parse 1.00 |
| Forecast aggregate calibration sweep | `python3 -m aeread_lab.cli --sweep --task forecast_aggregate --agents offline:oracle,offline:raw_score,offline:empirical_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; base-rate regret 0.00800648; empirical-bin/no-shrink regret 0.0668155 with shrinkage miss 1.00; raw-score regret 0.0882209 with raw-score miss 1.00; parse 1.00 |
| Market policy-shift sweep | `python3 -m aeread_lab.cli --sweep --task market_policy_shift --agents offline:oracle,offline:nash,offline:last_price,offline:collusive --no-cache` | oracle rank 1 with profit regret 0; sticky-last-price regret 189.006 and last-price miss 1.00; static-Nash regret 541.191 and static miss 1.00; collusive regret 1784.78; parse 1.00 |
| Market policy-inventory sweep | `python3 -m aeread_lab.cli --sweep --task market_policy_inventory --agents offline:oracle,offline:nash,offline:last_price,offline:inventory_blind --no-cache` | oracle rank 1 with constrained terminal-cash regret 0; inventory-blind regret 1595.31 and inventory-blind miss 1.00; sticky-last-price regret 2204.75; static-Nash regret 3450.07; parse 1.00 |
| Market trace-inventory sweep | `python3 -m aeread_lab.cli --sweep --task market_trace_inventory --agents offline:oracle,offline:nash,offline:last_price,offline:trace_blind,offline:inventory_blind --no-cache` | oracle rank 1 with constrained terminal-cash regret 0; trace-blind regret 960.911 and trace-blind miss 1.00; inventory-blind regret 1509.83 and inventory-blind miss 0.75; last-price regret 2125.34; static-Nash regret 3378.04; parse 1.00 |
| Market trace-markdown sweep | `python3 -m aeread_lab.cli --sweep --task market_trace_markdown --agents offline:oracle,offline:nash,offline:one_price,offline:trace_blind,offline:inventory_blind --no-cache` | oracle rank 1 with constrained terminal-cash regret near 0; one-price regret 15.8076; trace-blind regret 904.786; inventory-blind regret 1525.64; static-Nash regret 3393.85; parse 1.00 |
| Market trace-replenishment sweep | `python3 -m aeread_lab.cli --sweep --task market_trace_replenishment --agents offline:oracle,offline:no_replenishment,offline:one_price,offline:trace_blind,offline:replenishment_blind --no-cache` | oracle rank 1 with constrained terminal-cash regret near 0; one-price regret 15.8076; replenishment-blind regret 902.079; trace-blind regret 2269.28; no-replenishment regret 3287.08; parse 1.00 |
| Natural market trace-replenishment sweep | `python -m aeread_lab.cli --sweep --task market_trace_replenishment_natural --agents offline:oracle,offline:no_replenishment,offline:one_price,offline:trace_blind,offline:replenishment_blind --no-cache` | oracle rank 1 with constrained terminal-cash regret near 0; one-price regret 15.8076; replenishment-blind regret 902.079; trace-blind regret 2269.28; no-replenishment regret 3287.08; parse 1.00 |
| Noisy market trace-replenishment sweep | `python -m aeread_lab.cli --sweep --task market_trace_replenishment_noisy --agents offline:oracle,offline:no_replenishment,offline:one_price,offline:trace_blind,offline:replenishment_blind --no-cache` | oracle rank 1 with constrained terminal-cash regret near 0; one-price regret 3.95377; replenishment-blind regret 878.23; trace-blind regret 2542.69; no-replenishment regret 3286.21; parse 1.00 |
| Belief-bargaining interaction sweep | `python3 -m aeread_lab.cli --sweep --task belief_bargaining_interaction --agents offline:oracle,offline:prior,offline:single_cue,offline:single_offer --no-cache` | oracle rank 1 with expected-surplus gap 0; single-cue gap 18.0089; single-offer gap 20.4725; prior-plan gap 30.9023; parse 1.00 |
| Procurement bundle sweep | `python3 -m aeread_lab.cli --sweep --task procurement_bundle --agents offline:oracle,offline:compatibility_blind,offline:category_blind,offline:cheapest_pair --no-cache` | oracle rank 1 with score regret 0; compatibility-blind regret 0.30145; category-blind regret 2.75435; cheapest-pair regret 5.6315; parse 1.00 |
| Procurement bundle natural sweep | `python3 -m aeread_lab.cli --sweep --task procurement_bundle_natural --agents offline:oracle,offline:compatibility_blind,offline:category_blind,offline:cheapest_pair --no-cache` | same oracle and baseline ordering as `procurement_bundle`; oracle 0, compatibility-blind 0.30145, category-blind 2.75435, cheapest-pair 5.6315; parse 1.00 |
| Procurement bundle evidence sweep | `python3 -m aeread_lab.cli --sweep --task procurement_bundle_evidence --agents offline:oracle,offline:compatibility_blind,offline:category_blind,offline:cheapest_pair --no-cache` | same oracle and baseline ordering as `procurement_bundle`; oracle 0, compatibility-blind 0.30145, category-blind 2.75435, cheapest-pair 5.6315; parse 1.00 |
| Procurement bundle noisy-evidence sweep | `python3 -m aeread_lab.cli --sweep --task procurement_bundle_noisy_evidence --agents offline:oracle,offline:compatibility_blind,offline:category_blind,offline:cheapest_pair --no-cache` | same oracle and baseline ordering as `procurement_bundle`; oracle 0, compatibility-blind 0.30145, category-blind 2.75435, cheapest-pair 5.6315; parse 1.00 |
| Procurement bundle history sweep | `python3 -m aeread_lab.cli --sweep --task procurement_bundle_history --agents offline:oracle,offline:compatibility_blind,offline:category_blind,offline:cheapest_pair --no-cache` | same oracle and baseline ordering as `procurement_bundle`; oracle 0, compatibility-blind 0.30145, category-blind 2.75435, cheapest-pair 5.6315; parse 1.00 |
| Procurement bundle reserve sweep | `python3 -m aeread_lab.cli --sweep --task procurement_bundle_reserve --agents offline:oracle,offline:compatibility_blind,offline:category_blind,offline:cheapest_pair --no-cache` | oracle rank 1 with score regret 0; compatibility-blind regret 0.1452; category-blind regret 5.50615; cheapest-pair regret 5.549; parse 1.00 |
| Procurement vendor-update sweep | `python3 -m aeread_lab.cli --sweep --task procurement_vendor_update --agents offline:oracle,offline:myopic,offline:reputation_blind,offline:cheapest --no-cache` | oracle rank 1 with score regret 0; myopic regret 6.43164; reputation-blind and cheapest regret 25.7697 with reputation-blind miss 1.00; parse 1.00 |
| Noisy procurement vendor-update sweep | `python -m aeread_lab.cli --sweep --task procurement_vendor_update_noisy --agents offline:oracle,offline:reputation_blind,offline:myopic,offline:cheapest --no-cache` | oracle rank 1 with score regret 0; myopic regret 6.43164; reputation-blind and cheapest regret 25.7697 with reputation-blind miss 1.00; parse 1.00 |
| Repeated mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_repeated --agents offline:oracle,offline:revenue,offline:one_period,offline:risk_blind --no-cache` | oracle rank 1 with score regret 0; risk-blind regret 226.083; one-period regret 567.864; revenue regret 697.695; parse 1.00 |
| Natural repeated mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_repeated_natural --agents offline:oracle,offline:revenue,offline:one_period,offline:risk_blind --no-cache` | oracle rank 1 with score regret 0; risk-blind regret 226.083; one-period regret 567.864; revenue regret 697.695; parse 1.00 |
| Participant-response mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_participant_response --agents offline:oracle,offline:revenue,offline:one_period,offline:response_blind --no-cache` | oracle rank 1 with score regret 0; one-period and response-blind regret 69.0158; revenue regret 1771.34; parse 1.00 |
| Elasticity-inference mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_elasticity_inference --agents offline:oracle,offline:revenue,offline:one_period,offline:response_blind --no-cache` | oracle rank 1 with score regret 0; one-period and response-blind regret 69.0158; revenue regret 1771.34; parse 1.00 |
| Strategic-response mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_strategic_response --agents offline:oracle,offline:revenue,offline:one_period,offline:response_blind --no-cache` | oracle rank 1 with score regret 0; one-period and response-blind regret 52103.9; revenue regret 118159; parse 1.00 |
| Strategic-equilibrium mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_strategic_equilibrium --agents offline:oracle,offline:revenue,offline:one_period,offline:response_blind --no-cache` | oracle rank 1 with score regret 0; response-blind regret 238424; revenue regret 385487; parse 1.00; one-period is not a failure mode for this formulation |
| Trace-equilibrium mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_trace_equilibrium --agents offline:oracle,offline:revenue,offline:trace_projection,offline:equilibrium_blind,offline:trace_blind --no-cache` | oracle rank 1 with score regret 0; trace-blind regret 0; equilibrium-blind regret 143099; revenue and trace-projection regret 258815; parse 1.00 |
| Natural trace-equilibrium mechanism sweep | `python3 -m aeread_lab.cli --sweep --task mechanism_trace_equilibrium_natural --agents offline:oracle,offline:revenue,offline:trace_projection,offline:equilibrium_blind,offline:trace_blind --no-cache` | oracle rank 1 with score regret 0; trace-blind regret 0; equilibrium-blind regret 143099; revenue and trace-projection regret 258815; parse 1.00 |
| Noisy trace-equilibrium mechanism sweep | `python -m aeread_lab.cli --sweep --task mechanism_trace_equilibrium_noisy --agents offline:oracle,offline:revenue,offline:trace_projection,offline:equilibrium_blind,offline:trace_blind --no-cache` | oracle rank 1 with score regret 0; trace-blind regret 193.156; equilibrium-blind regret 143597; trace-projection regret 190149; revenue regret 260868; parse 1.00 |
| Forecast curve calibration sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00206655 with nearest-bin miss 1.00; base-rate regret 0.0437929; raw-score regret 0.0897789 with raw-score miss 1.00; parse 1.00 |
| Forecast implicit curve sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve_implicit --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00206655 with nearest-bin miss 1.00; base-rate regret 0.0437929; raw-score regret 0.0897789 with raw-score miss 1.00; parse 1.00 |
| Forecast noisy curve sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve_noisy --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00224894 with nearest-bin miss 1.00; base-rate regret 0.0274858; raw-score regret 0.0566631 with raw-score miss 1.00; parse 1.00 |
| Forecast natural-label curve sweep | `python3 -m aeread_lab.cli --sweep --task forecast_curve_natural --agents offline:oracle,offline:raw_score,offline:nearest_bin,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bin regret 0.00224894 with nearest-bin miss 1.00; base-rate regret 0.0274858; raw-score regret 0.0566631 with raw-score miss 1.00; parse 1.00 |
| Forecast shift-calibration sweep | `python3 -m aeread_lab.cli --sweep --task forecast_shift_calibration --agents offline:oracle,offline:raw_score,offline:source_curve,offline:nearest_bridge,offline:bridge_empirical,offline:base_rate --no-cache` | oracle rank 1 with expected Brier regret 0; nearest-bridge regret 0.00197587 with nearest-bridge miss 0.75; bridge-empirical regret 0.0124051; source-curve regret 0.0289593 with source-curve miss 1.00; raw-score regret 0.0432897 with raw-score miss 1.00; base-rate regret 0.0663489; parse 1.00 |
| Forecast rolling-calibration sweep | `python -m aeread_lab.cli --sweep --task forecast_rolling_calibration --agents offline:oracle,offline:raw_score,offline:stale_window,offline:pooled_history --no-cache` | oracle rank 1 with expected Brier regret near 0; pooled-history regret 0.00274588 with pooled-history miss 1.00; stale-window regret 0.05431 with stale-window miss 1.00; raw-score regret 0.0652963 with raw-score miss 1.00; parse 1.00 |
| Pricing counterfactual sweep | `python3 -m aeread_lab.cli --sweep --task pricing_counterfactual --agents offline:oracle,offline:stale_price,offline:round --no-cache` | oracle rank 1 with mean absolute price error 0.002394; rounded baseline price error 2.40776; stale-price baseline price error 4.37114 with counterfactual-shift miss 1.00 and sticky-base-price 1.00; parse 1.00 |
| Pricing cross-elasticity sweep | `python3 -m aeread_lab.cli --sweep --task pricing_cross_elasticity --agents offline:oracle,offline:own_only,offline:round --no-cache` | oracle rank 1 with mean absolute price error 0.0016094; rounded baseline error 1.9655; own-price-only baseline error 8.42464 with cross-blind miss 1.00; parse 1.00 |
| Pricing multi-product sweep | `python3 -m aeread_lab.cli --sweep --task pricing_multi_product --agents offline:oracle,offline:independent,offline:round --no-cache` | oracle rank 1 with two-price L1 error 0.0034; rounded baseline error 4.78782; independent baseline error 19.2972 with independent miss 1.00 and revenue gap 627.386; parse 1.00 |
| Pricing multi-product natural sweep | `python3 -m aeread_lab.cli --sweep --task pricing_multi_product_natural --agents offline:oracle,offline:independent,offline:round --no-cache` | same oracle/independent/rounded dynamic range as the formula-guided multi-product task; parse 1.00 |
| Pricing multi-product capacity sweep | `python3 -m aeread_lab.cli --sweep --task pricing_multi_product_capacity --agents offline:oracle,offline:capacity_blind,offline:independent --no-cache` | oracle rank 1 with two-price L1 error 0; capacity-blind error 12.635; independent error 23.8125; parse 1.00 |
| Pricing noisy multi-product capacity sweep | `python -m aeread_lab.cli --sweep --task pricing_multi_product_capacity_noisy --agents offline:oracle,offline:capacity_blind,offline:independent --no-cache` | oracle rank 1 with two-price L1 error 0; capacity-blind error 13.4225; independent error 33.52; parse 1.00 |
| Pricing inventory-markdown sweep | `python3 -m aeread_lab.cli --sweep --task pricing_inventory_markdown --agents offline:oracle,offline:myopic,offline:round --no-cache` | oracle rank 1 with early/late price L1 error 0; rounded baseline error 5.8125; myopic baseline error 30.615 with myopic miss 1.00; parse 1.00 |
| Pricing noisy inventory-markdown sweep | `python3 -m aeread_lab.cli --sweep --task pricing_inventory_markdown_noisy --agents offline:oracle,offline:myopic,offline:round --no-cache` | oracle rank 1 with early/late price L1 error 0; rounded baseline error 5.3125; myopic baseline error 30.4475 with myopic miss 1.00; parse 1.00 |
| Pricing noisy multi-product markdown sweep | `python -m aeread_lab.cli --sweep --task pricing_multi_product_markdown_noisy --agents offline:oracle,offline:myopic,offline:capacity_blind,offline:independent --no-cache` | oracle rank 1 with four-price L1 error 0; capacity-blind error 40.99; myopic error 47.9375 with myopic miss 1.00; independent error 69.9625; parse 1.00 |
| Pricing noisy replenishment sweep | `python -m aeread_lab.cli --sweep --task pricing_inventory_replenishment_noisy --agents offline:oracle,offline:no_restock,offline:myopic,offline:capacity_fill --no-cache` | oracle rank 1 with decision L1 error 0; myopic and capacity-fill error 36.01 with miss 1.00; no-restock error 62.3125 with no-restock miss 1.00; parse 1.00 |
| Pricing hidden-intervention sweep | `python3 -m aeread_lab.cli --sweep --task pricing_hidden_intervention --agents offline:oracle,offline:round,offline:intervention_blind --no-cache` | oracle rank 1 with mean price error 0.00275; rounded baseline error 2.29931; intervention-blind error 33.4577 with intervention-blind miss 1.00; parse 1.00 |
| Procurement counterfactual sweep | `python3 -m aeread_lab.cli --sweep --task procurement_counterfactual --agents offline:oracle,offline:comfort,offline:first --no-cache` | oracle rank 1 with accuracy 1.00; comfort baseline accuracy 0.666667, paraphrase inconsistency 0, preference-flip miss 1.00, sticky-base-on-flip 1.00; first baseline accuracy 0.166667; parse 1.00 |
| Supplier-scam natural differential sweep | `python3 -m aeread_lab.cli --sweep --task supplier_scam_natural --agents offline:oracle,offline:reputation_blind,offline:timing_blind,offline:credulous --no-cache` | same oracle/reputation-blind/timing-blind/credulous ordering as `supplier_scam`; oracle constrained regret 0; reputation-blind regret 23.385 and reputation miss 1.00; timing-blind regret 99.6365; credulous regret 304.186; parse 1.00 |
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
| API key scan | `rg -n "sk-proj-[A-Za-z0-9_-]{20,}" .` | no tracked API key strings found |
| Provider guardrail scan | `rg -n "anthropic|claude|openrouter|chat\\.completions|ChatCompletion|OPENROUTER|ANTHROPIC" aeread_lab tests docs pyproject.toml README.md` | only expected documentation/test guardrail matches; no non-OpenAI client path added |

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
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task supplier_scam_natural --agent openai:nano --cache-dir /tmp/aeread_pr69_live_cache` | completed; n=11, parse 1.00, constrained regret 50.57, reserve violation 0.00, scam-supplier rate 0.00, timing violation 0.00, reputation miss 1.00 | natural vendor labels preserve the same live failure: `nano` avoids obvious unsafe orders but does not sufficiently update risk after delivery failures |
| `python3 -m aeread_lab.cli --task belief_bargaining --agent openai:nano --cache-dir /tmp/aeread_pr44_live_cache` | completed; n=9, parse 1.00, surplus gap 21.9014, cue miss 0.2857, multi-turn miss 1.00, strategic base gap 52.4859, scaffold gap 0 | direct support for the `7cb0ca8` falsifier: `nano` fails strategic cheap-talk inference when posterior state is implicit, but closes the gap when the posterior is externalized |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task belief_bargaining_interaction --agent openai:nano --cache-dir /tmp/aeread_pr71_live_cache` | completed; n=4, parse 1.00, expected-surplus gap 3.7145, first-price error 14.75, second-price error 12.00, prior miss 0.25, single-cue miss 0.25, single-offer miss 0.25 | `nano` mostly solves the two-offer interaction but leaves a small surplus gap and one named-baseline-like miss, so this validates the interaction surface without being as strong a live discriminator as the strategic cheap-talk task |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_bundle --agent openai:nano --cache-dir /tmp/aeread_pr72_live_cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, invalid 0.00, category miss 0.00, budget violation 0.00, compatibility miss 0.00 | validates the combinatorial procurement bundle surface and live parser, but this first explicit compatibility version does not separate `nano` |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_bundle_natural --agent openai:nano --cache-dir /tmp/aeread_pr73_live_cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, invalid 0.00, category miss 0.00, budget violation 0.00, compatibility miss 0.00 | SKU/package-fit wording still does not separate `nano`; future procurement stress needs compatibility inferred from evidence or history rather than numeric package-fit deltas |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_bundle_evidence --agent openai:nano --cache-dir /tmp/aeread_pr74_live_cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, invalid 0.00, category miss 0.00, budget violation 0.00, compatibility miss 0.00 | deployment outcome rows still do not separate `nano`; the next procurement discriminator should use noisier or conflicting deployment evidence rather than clean one-row pair summaries |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_bundle_noisy_evidence --agent openai:nano --cache-dir /tmp/aeread_pr75_live_cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, invalid 0.00, category miss 0.00, budget violation 0.00, compatibility miss 0.00 | noisy repeated deployment rows still do not separate `nano`; this suggests simple two-SKU procurement is saturated unless the package signal is embedded in multi-round history or budget dynamics |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_bundle_history --agent openai:nano --cache-dir /tmp/aeread_pr76_live_cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, invalid 0.00, category miss 0.00, budget violation 0.00, compatibility miss 0.00 | multi-period deployment-history conversion still does not separate `nano`; procurement should pivot to endogenous reserve, inventory, or sequential vendor-update dynamics rather than another static two-SKU evidence table |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_bundle_reserve --agent openai:nano --cache-dir /tmp/aeread_pr77_live_cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, invalid 0.00, category miss 0.00, budget violation 0.00, compatibility miss 0.00 | support-reserve shortfall arithmetic still does not separate `nano`; the procurement frontier should shift to sequential procurement policy or be deprioritized behind domains with live gaps |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task procurement_vendor_update --agent openai:nano --cache-dir /tmp/aeread_pr81_live_cache` | completed; n=4, parse 1.00, score regret 71.8555, accuracy 0.00, reputation miss 0.00, myopic miss 0.50 | sequential vendor-update procurement creates a strong live gap; `nano` often overpays for premium reliability or follows a myopic middle-round switch instead of optimizing history, switch cost, and reserve together |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task procurement_vendor_update_noisy --agent openai:nano --cache-dir /tmp/aeread_pr96_live_cache --no-cache` | completed; n=4, parse 1.00, score regret 84.9162, accuracy 0.00, reputation miss 0.00, myopic miss 0.00 | lumpy receiving-ledger rows strengthen the sequential procurement live gap; `nano` aggregates enough to avoid the named reputation-blind/myopic plans but overpays for premium reliability on every case |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task pricing_multi_product_capacity --agent openai:nano --cache-dir /tmp/aeread_pr78_live_cache` | completed; n=4, parse 1.00, two-price L1 error 13.235, revenue gap 579.064, capacity-blind miss 0.00, independent miss 0.00 | finite stock caps reopen a strong live pricing gap; `nano` is not merely copying the named capacity-blind or independent baselines, but it misses the constrained joint optimum |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task pricing_multi_product_capacity_noisy --agent openai:nano --cache-dir /tmp/aeread_pr91_live_cache --no-cache` | completed; n=4, parse 1.00, two-price L1 error 30.0375, revenue gap 587.0425, capacity-blind miss 0.00, independent miss 0.00 | lumpy regional evidence strengthens the finite-stock joint-pricing live gap; `nano` solves one substitute-cap case but misses the noisy complement/capacity cases badly |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task pricing_inventory_markdown --agent openai:nano --cache-dir /tmp/aeread_pr79_live_cache` | completed; n=4, parse 1.00, early/late price L1 error 6.7725, revenue gap 205.898, myopic miss 0.00 | sequential inventory allocation creates a moderate live pricing gap; `nano` raises prices enough to avoid the myopic baseline but misses the exact stock-preserving markdown optimum |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task pricing_inventory_markdown_noisy --agent openai:nano --cache-dir /tmp/aeread_pr80_live_cache` | completed; n=4, parse 1.00, early/late price L1 error 9.3825, revenue gap 355.803, myopic miss 0.00 | noisy natural launch/clearance evidence strengthens the PR 79 markdown gap while keeping the same oracle and parse contract |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task pricing_multi_product_markdown_noisy --agent openai:nano --cache-dir /tmp/aeread_pr94_live_cache2 --no-cache` | completed; n=4, parse 1.00, four-price L1 error 61.3, revenue gap 4600.5859, myopic miss 0.00, capacity-blind miss 0.00, independent miss 0.00 | combining lumpy cross-demand with launch/clearance stock depletion produces the strongest pricing live gap so far without named-baseline collapse |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task pricing_inventory_replenishment_noisy --agent openai:nano --cache-dir /tmp/aeread_pr95_live_cache --no-cache` | completed; n=4, parse 1.00, decision L1 error 27.98, revenue gap 371.0914, no-restock miss 0.00, myopic miss 0.00, capacity-fill miss 0.00 | restock quantity selection creates a nonzero live pricing gap; `nano` recognizes replenishment is needed but under-orders in three cases and overfills one case |
| `python3 -m aeread_lab.cli --task regime_relationship --agent openai:nano --cache-dir /tmp/aeread_pr45_live_cache` | completed; n=16, parse 1.00, mean absolute error 0.1713, law violation 0.00, fit-fail 1.00 | direct support for the generator-verifier caution in `7cb0ca8`: `nano` preserves the relationship laws but misses oracle fit on every generated group, so relationship-only verification would over-credit it |
| `python3 -m aeread_lab.cli --task regime_holdout --agent openai:nano --cache-dir /tmp/aeread_pr61_live_cache` | completed; n=32, parse 1.00, mean absolute error 0.402735, law violation 0.62, fit-fail 1.00 | broader generated holdouts turn the PR 45 fit failure into both fit and relationship-law failures for `nano`; this is a stronger generator-verifier stress signal than the fixed relationship set |
| `python3 -m aeread_lab.cli --task regime_law_audit --agent openai:nano --cache-dir /tmp/aeread_pr62_live_cache` | completed; n=40, parse 1.00, accuracy 0.825, invalid-accept 0.10, valid-reject 0.20 | direct verifier-side probe: `nano` mostly recognizes generated law claims but still rejects some valid laws and accepts a few invalid ones |
| `python3 -m aeread_lab.cli --task procurement_counterfactual --agent openai:nano --cache-dir /tmp/aeread_pr46_live_cache` | completed; n=6, accuracy 0.833333, paraphrase inconsistency 0.00, preference-flip miss 0.50, sticky-base-on-flip 0.00 | `nano` preserves choices under paraphrase and solves one preference flip, but misses the lobby-table flip by choosing the high-durability option instead of the cheaper oracle |
| `python3 -m aeread_lab.cli --task pricing_counterfactual --agent openai:nano --cache-dir /tmp/aeread_pr47_live_cache` | completed; n=4, parse 1.00, mean absolute price error 0, counterfactual-shift miss 0.00, sticky-base-price 0.00 | validates the pricing evidence-perturbation harness, but this exact linear-evidence version does not separate `nano`; harder or noisier evidence perturbations are needed for model discrimination |
| `python3 -m aeread_lab.cli --task pricing_counterfactual --agent openai:nano --cache-dir /tmp/aeread_pr48_live_cache` | completed; n=8, parse 1.00, mean absolute price error 0.35235, counterfactual-shift miss 0.00, sticky-base-price 0.00 | noisy evidence creates a nonzero pricing-fit gap for `nano` while preserving correct shift direction; this is a calibration/estimation stress, not a stale-price failure |
| `python3 -m aeread_lab.cli --task pricing_law_audit --agent openai:nano --cache-dir /tmp/aeread_pr63_live_cache` | completed; n=10, parse 1.00, accuracy 1.00, invalid-accept 0.00, valid-reject 0.00 | validates a cross-domain generator-verifier audit outside regime fractions, but this explicit pricing-law set does not separate `nano` |
| `python3 -m aeread_lab.cli --task pricing_evidence_law_audit --agent openai:nano --cache-dir /tmp/aeread_pr64_live_cache` | completed; n=8, parse 1.00, accuracy 1.00, invalid-accept 0.00, valid-reject 0.00 | validates the evidence-derived law-audit surface, but `nano` still solves it; future pricing-law stress should use subtler interventions or larger generated evidence families |
| `python3 -m aeread_lab.cli --task pricing_evidence_law_holdout --agent openai:nano --cache-dir /tmp/aeread_pr65_live_cache` | completed; n=24, parse 1.00, accuracy 1.00, invalid-accept 0.00, valid-reject 0.00 | validates the generated neutral-ID evidence-law holdout, but `nano` still solves it; the remaining pricing-law frontier is not deterministic linear evidence, but noisier estimation, multi-product substitution, or hidden intervention constraints |
| `python3 -m aeread_lab.cli --task pricing_cross_elasticity --agent openai:nano --cache-dir /tmp/aeread_pr66_live_cache` | completed; n=6, parse 1.00, mean absolute price error 1.4380, revenue gap 18.0465, cross-blind miss 0.00 | cross-product evidence creates a nonzero live pricing gap without collapsing to the own-price-only baseline; this is a stronger next frontier than more exact law-label cases |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task pricing_multi_product --agent openai:nano --cache-dir /tmp/aeread_pr67_live_cache` | completed; n=6, parse 1.00, two-price L1 error 7.6586, revenue gap 246.6621, independent miss 0.00 | joint two-product pricing increases the live pricing gap beyond PR 66 while avoiding a simple independent-pricing collapse; the first 4096-token retry reached the API but hard-failed on `max_output_tokens` |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task pricing_multi_product_natural --agent openai:nano --cache-dir /tmp/aeread_pr68_live_cache` | completed; n=6, parse 1.00, two-price L1 error 40.8911, revenue gap 2377.5387, independent miss 0.00 | removing the explicit equation recipe produces the strongest pricing live gap so far; `nano` chooses low historical-row-like prices rather than estimating the joint optimum |
| `python3 -m aeread_lab.cli --task forecast_aggregate --agent openai:nano --cache-dir /tmp/aeread_pr49_live_cache` | completed; n=5, parse 1.00, expected Brier regret 1.28e-9, raw-score miss 0.00, shrinkage miss 0.00 | validates the aggregate-bin shrinkage harness, but `nano` solves this explicit version; future aggregate calibration work should make the recalibration formula less directly stated or use held-out bin curves |
| `python3 -m aeread_lab.cli --task forecast_curve --agent openai:nano --cache-dir /tmp/aeread_pr50_live_cache` | completed; n=3, parse 1.00, expected Brier regret 1.16e-9, raw-score miss 0.00, nearest-bin miss 0.00 | validates held-out calibration-curve interpolation, but `nano` solves this explicit version; future curve work should remove formula hints or use denser/noisier tables |
| `python3 -m aeread_lab.cli --task forecast_curve_implicit --agent openai:nano --cache-dir /tmp/aeread_pr51_live_cache` | completed; n=3, parse 1.00, expected Brier regret 0.0890095, probability error 0.1902, raw-score miss 0.50, nearest-bin miss 0.00 | removing the explicit shrink/interpolate recipe turns the same held-out curve target into a live `nano` failure signal; the model partially reverts toward the raw score under implicit calibration framing |
| `python3 -m aeread_lab.cli --task forecast_curve_noisy --agent openai:nano --cache-dir /tmp/aeread_pr52_live_cache` | completed; n=4, parse 1.00, expected Brier regret 0.00141703, probability error 0.0278, raw-score miss 0.00, nearest-bin miss 0.50 | `nano` mostly solves the denser/noisier table but overshoots two sparse/noisy cases; this is a weaker fit-stress signal than PR 51, not a broad raw-score failure |
| `python3 -m aeread_lab.cli --task forecast_curve_natural --agent openai:nano --cache-dir /tmp/aeread_pr53_live_cache` | completed; n=4, parse 1.00, expected Brier regret 0.0197592, probability error 0.1061, raw-score miss 0.67, nearest-bin miss 0.75 | natural row labels produce a much stronger live failure than the machine-readable noisy table; `nano` treats some score-centered outcome rows like nearest rows or raw scores instead of recalibrating the curve |
| `python3 -m aeread_lab.cli --task forecast_shift_calibration --agent openai:nano --cache-dir /tmp/aeread_pr84_live_cache` | completed; n=4, parse 1.00, expected Brier regret 0.0151186, probability error 0.101552, raw-score miss 0.75, source-curve miss 0.50, nearest-bridge miss 0.00 | `nano` usually uses the target bridge direction but under-applies the local cohort-shift adjustment, especially when the source curve and bridge sample disagree in opposite directions |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task forecast_rolling_calibration --agent openai:nano --cache-dir /tmp/aeread_pr97_live_cache --no-cache` | completed; n=4, parse 1.00, expected Brier regret rounds to 0, probability error rounds to 0, raw-score miss 0.00, stale-window miss 0.00, pooled-history miss 0.00 | validates the rolling calibration surface, but the explicit recency-weight prompt does not separate live `nano`; future calibration stress should remove formulaic weighting cues or use natural time-window summaries |
| `python3 -m aeread_lab.cli --task market_policy_shift --agent openai:nano --cache-dir /tmp/aeread_pr54_live_cache` | completed; n=4, parse 1.00, profit regret 18.691, price error 3.0037, static-Nash miss 0.00, last-price miss 0.00 | `nano` adjusts to the opponent-policy signals enough to avoid static/sticky baselines, but leaves moderate profit on the table from imperfect next-price inference |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task market_policy_inventory --agent openai:nano --cache-dir /tmp/aeread_pr70_live_cache` | completed; n=4, parse 1.00, constrained terminal-cash regret 165.418, price error 3.25, reserve violation 0.00, static-Nash miss 0.00, last-price miss 0.33, inventory-blind miss 0.00 | `nano` infers enough of the opponent-policy/inventory objective to avoid unsafe reserve failures and simple static/inventory-blind collapse, but leaves terminal cash on the table and partially anchors to last-price behavior |
| `python3 -m aeread_lab.cli --task market_trace_inventory --agent openai:nano --cache-dir /tmp/aeread_pr85_live_cache` | completed; n=4, parse 1.00, constrained terminal-cash regret 4226.05, price error 19.65, reserve violation 0.50, static-Nash miss 0.50, last-price miss 0.33, trace-blind miss 1.00, inventory-blind miss 0.33 | removing the explicit opponent-policy label creates the strongest market live gap so far; `nano` overprices clearance/share-attack traces and misses the reserve/sell-through interaction |
| `python3 -m aeread_lab.cli --task market_trace_markdown --agent openai:nano --cache-dir /tmp/aeread_pr86_live_cache` | completed; n=4, parse 1.00, constrained terminal-cash regret 5775.24, price L1 65.295, reserve violation 0.50, static-Nash miss 1.00, one-price miss 0.50, trace-blind miss 0.75, inventory-blind miss 0.67 | staged early/late pricing strengthens the trace-inventory live gap; `nano` often gives high, static-like staged prices instead of selling through clearance/share-attack traces |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task market_trace_replenishment --agent openai:nano --cache-dir /tmp/aeread_pr87_live_cache` | completed; n=4, parse 1.00, constrained terminal-cash regret 7644.80, decision L1 81.7674, reserve violation 0.50, no-replenishment miss 0.50, one-price miss 0.00, trace-blind miss 1.00, replenishment-blind miss 0.50 | coupling staged pricing to optional replenishment creates the strongest market live gap so far; `nano` often misses the stockout-vs-overbuy tradeoff and needs the larger output-token cap to finish |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task market_trace_replenishment_natural --agent openai:nano --cache-dir /tmp/aeread_pr90_live_cache --no-cache` | completed; n=4, parse 1.00, constrained terminal-cash regret 7412.39, decision L1 74.7824, reserve violation 0.50, no-replenishment miss 1.00, one-price miss 0.00, trace-blind miss 1.00, replenishment-blind miss 0.00 | natural rival shelf/restock labels preserve nearly all of the PR 87 live gap; `nano` still misses the trace-conditioned stockout-vs-overbuy tradeoff |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task market_trace_replenishment_noisy --agent openai:nano --cache-dir /tmp/aeread_pr92_live_cache --no-cache` | completed; n=4, parse 1.00, constrained terminal-cash regret 8802.45, decision L1 78.2524, reserve violation 0.25, no-replenishment miss 0.50, one-price miss 0.00, trace-blind miss 1.00, replenishment-blind miss 0.00 | lumpy regional shelf observations strengthen the trace-replenishment live gap; `nano` remains trace-blind-like on every missable case and misprices the stockout-vs-overbuy decision |
| `python3 -m aeread_lab.cli --task mechanism_repeated --agent openai:nano --cache-dir /tmp/aeread_pr55_live_cache` | completed; n=4, parse 1.00, score regret 0, revenue miss 0.00, one-period miss 0.00, risk-blind miss 0.00 | validates the repeated-mechanism harness, but `nano` solves this explicit full-horizon scoring version |
| `python3 -m aeread_lab.cli --task mechanism_repeated_natural --agent openai:nano --cache-dir /tmp/aeread_pr56_live_cache` | completed; n=4, parse 1.00, score regret 3.50137, revenue miss 0.00, one-period miss 0.00, risk-blind miss 0.00 | natural pilot-outcome labels reopen a small live mechanism gap while preserving parse; `nano` does not collapse to the known offline defaults |
| `python3 -m aeread_lab.cli --task mechanism_participant_response --agent openai:nano --cache-dir /tmp/aeread_pr57_live_cache` | completed; n=4, parse 1.00, score regret 23.5998, revenue miss 0.00, one-period miss 0.00, response-blind miss 0.00 | participant-response simulation creates a larger live mechanism gap than PR 56 while preserving format compliance |
| `python3 -m aeread_lab.cli --task mechanism_elasticity_inference --agent openai:nano --cache-dir /tmp/aeread_pr58_live_cache` | completed; n=4, parse 1.00, score regret 23.5998, revenue miss 0.00, one-period miss 0.00, response-blind miss 0.00 | hiding elasticity as pilot stay-rate observations validates the prompt surface but does not increase live separation beyond PR 57 |
| `python3 -m aeread_lab.cli --task mechanism_strategic_response --agent openai:nano --cache-dir /tmp/aeread_pr59_live_cache` | completed; n=4, parse 1.00, score regret 15152.2, revenue miss 0.00, one-period miss 0.00, response-blind miss 0.00 | multi-agent peer-contagion response creates a much larger live mechanism gap than the single-agent participant-response variants |
| `python3 -m aeread_lab.cli --task mechanism_strategic_equilibrium --agent openai:nano --cache-dir /tmp/aeread_pr60_live_cache` | completed; n=4, parse 1.00, score regret 31048.2, revenue miss 0.00, one-period miss 0.00, response-blind miss 0.00 | self-consistent equilibrium scoring is a stronger live mechanism discriminator than forward strategic-response simulation |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python3 -m aeread_lab.cli --task mechanism_trace_equilibrium --agent openai:nano --cache-dir /tmp/aeread_pr88_live_cache` | completed; n=4, parse 1.00, score regret 93836.23, revenue miss 0.25, trace-projection miss 0.25, equilibrium-blind miss 0.00, trace-blind miss 0.00 | adding equilibrium response to observed pilot traces yields the largest mechanism live gap so far; `nano` misses one high-feedback trace case without collapsing wholesale to the bad baselines |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task mechanism_trace_equilibrium_natural --agent openai:nano --cache-dir /tmp/aeread_pr89_live_cache --no-cache` | completed; n=4, parse 1.00, score regret 43035.17, revenue miss 0.00, trace-projection miss 0.00, equilibrium-blind miss 0.00, trace-blind miss 0.00 | natural pilot outcome labels preserve a nonzero trace-equilibrium mechanism gap, but `nano` no longer collapses to any named baseline and the gap is smaller than PR 88 |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task mechanism_trace_equilibrium_noisy --agent openai:nano --cache-dir /tmp/aeread_pr93_live_cache --no-cache` | completed; n=4, parse 1.00, score regret 60204.84, revenue miss 0.00, trace-projection miss 0.00, equilibrium-blind miss 0.00, trace-blind miss 0.00 | noisy local pilot sheets strengthen the PR 89 natural trace-equilibrium mechanism gap while avoiding simple named-baseline collapse |
| `python3 -m aeread_lab.cli --sweep --task common_value --agents openai:nano,openai:mini,openai:gpt-5.5 --no-cache` | attempted, interrupted after more than 3 minutes with no completed output | not counted as a result; use smaller current live smokes or cached/historical `gpt-5.5` evidence until latency is controlled |

Historical live API findings from earlier in this private stack:

| Finding | Result | What changed because of it |
|---|---|---|
| `gpt-5.5-mini` and `gpt-5.5-nano` did not exist | live model list showed `gpt-5.4-mini` and `gpt-5.4-nano` | PR 19 fixed aliases |
| `gpt-5.5` produced blank scored outputs at 400 tokens | raw response was `status=incomplete`, reason `max_output_tokens` | PR 21 made incomplete/textless responses hard failures |
| response chunks could be missed | output text sometimes lived in nested content chunks | PR 22 added robust extraction |
| `nano` could still exhaust 800 tokens | direct probe worked at 1200 | PR 23 raised default output budget |
| long-horizon retail stress could exhaust 1200-2400 tokens | PR 37 live `nano` runs stopped on `max_output_tokens` on long-horizon retail cases at lower budgets | PR 37 keeps incomplete responses hard-failing, raises the default output budget to 4096, and tightens the retail no-explanation instruction |
| joint multi-product pricing could exhaust 4096 tokens | PR 67 live `nano` retry reached the API but hard-failed on `max_output_tokens`; the same run completed at 8192 | PR 67 keeps the 4096 default but adds `AEREAD_OPENAI_MAX_OUTPUT_TOKENS` for longer stress prompts |
| common-value live smoke separated model scale | `nano` regret 21.6325, `mini` regret 7.5125, `gpt-5.5` regret 0 | interpret as a capability-scaling guardrail, not a frontier discriminator |

## Original repo commit check

Checked on 2026-05-29 before writing this ledger and rechecked on
2026-05-30 before PR 26.

| Repo | Status | New/relevant commits checked | Consequence for private build lab |
|---|---|---|---|
| `/Users/lichenyu/agenteconreadiness` (`origin/main`) | clean at `7cb0ca8` on 2026-05-30 | `c3520ac` review corrections; `f69e883` OSS availability / borrow-substrate strategy; `a0e17b1` read-first refocus doc; `1e13623` RLHF appropriateness vs economic optimality theory; `d517c2e` oracle-availability and `(primitive x regime)` sharpening; `4a5b914` no-oracle evaluation and TERMS information-set resolution; `7cb0ca8` generator-verifier method, manufacturable-oracle correction, and bargaining-Bayes mechanism | PR 29 implements the RLHF theory; PR 37 follows `d517c2e`; PR 39 follows `4a5b914`; PRs 41-42 implement the no-oracle/proper-scoring path; PR 44 implements the `7cb0ca8` bargaining-Bayes posterior-scaffold falsifier; PRs 45, 61, 62, and 63 implement generator-verifier relationship laws, broader holdouts, law-claim auditing, and a cross-domain pricing audit |
| `/Users/lichenyu/persona_simulator` (`origin/master`) | dirty: modified `sprint/adversarial_scam_arena_toy/exploits.json`; untracked `.playwright-mcp/` logs; fetched at `ae9c7b2` on 2026-05-30 | `47acd7a` GPT-5.x support/model override; `8404d2a` OpenAI scam-arena run; `c1fbbd0` borrow-substrate doc; `121e2e0` cross-model scam result + timeout/label fixes; `94fa606`/`efa26d6` mirror oracle-availability and no-oracle information-set methodology; `ae9c7b2` mirrors generator-verifier and bargaining-Bayes additions | record upstream evidence only; do not import OpenRouter/chat-completions client into this Responses-only lab; PRs 44-45 and 61-62 use the mirrored `7cb0ca8` mechanisms without touching original dirty artifacts |

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
    holdouts if the goal is model discrimination. PR 84 adds the first
    source-to-target bridge calibration variant; next calibration work should
    stress rolling/time-local recalibration or multi-cohort calibration choice
    rather than another single bridge-sample table.
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
33. PR 58 hides the participant-response elasticity as pilot stay-rate
    observations. It validates the inferred-elasticity prompt surface, but live
    `nano` has the same regret as PR 57, so the next mechanism discriminator
    should add true multi-agent strategic response rather than another
    single-agent prompt-surface variant.
34. PR 59 adds true multi-agent strategic-share dynamics with peer contagion and
    audit deterrence. It creates a large live `nano` score-regret gap while
    avoiding collapse to the simple revenue, one-period, or response-blind
    baselines; future mechanism work should move toward interaction traces or
    endogenous equilibrium solving rather than more static option tables.
35. PR 60 adds self-consistent strategic-share equilibrium scoring. It roughly
    doubles the live `nano` gap versus PR 59 while keeping parse clean, so the
    next mechanism-adjacent build should use interaction traces or richer
    equilibrium cases only if they add new evidence beyond this stable-share
    solver.
36. PR 61 broadens the generator-verifier regime-law path from fixed generated
    fixtures to a held-out family. Live `nano` now fails both fit and law
    consistency on many groups, so the next generator-verifier build should
    focus on mass-producing law families or cross-domain verifiers rather than
    only adding more handpicked regime gambles.
37. PR 62 splits verifier-side law validity from numeric regime fit. Live
    `nano` has clean parse and decent accuracy but still rejects some valid laws
    and accepts a few invalid ones, which supports keeping law-audit metrics
    separate from fraction-fit metrics in future generator-verifier work.
38. PR 63 ports the law-audit pattern to pricing comparative statics. It
    validates cross-domain generator-verifier plumbing, but live `nano` solves
    the explicit claims, so the next pricing verifier should make the claims
    less formulaic or add cap/intervention constraints that require more
    careful case analysis.
39. PR 64 removes explicit alpha/beta demand parameters from pricing-law
    auditing and asks the verifier to infer price movement from sales rows.
    Live `nano` still solves the first evidence-derived set, so this validates
    the surface but does not yet create model separation; the next pricing-law
    stress should generate larger evidence families or add intervention
    constraints whose direction cannot be read from scenario labels.
40. PR 65 adds that larger generated evidence-law family and fixes label leakage
    in printed pricing-law case IDs. Live `nano` still solves all 24 holdout
    claims, so deterministic linear evidence-law classification is now likely a
    saturated primitive for `nano`; future pricing work should shift to noisy
    estimation, multi-product substitution/cross-elasticities, or hidden
    intervention constraints rather than adding more exact linear law labels.
41. PR 66 follows that recommendation by adding cross-product price evidence.
    The own-price-only baseline fails hard, and live `nano` avoids that collapse
    but still leaves a nonzero price/revenue gap, making cross-elasticity a more
    productive pricing direction than further deterministic law-audit expansion.
42. PR 70 deepens the market-policy axis by combining opponent next-price
    inference with finite inventory, holding costs, fixed obligations, and
    reserve constraints. The one-period policy-aware best response becomes a
    failure baseline, so this adds evidence beyond PR 54's static opponent-shift
    profit regret.
43. PR 71 deepens bargaining from static posterior pricing to a finite
    two-offer policy. Rejection of the opening price becomes information for the
    fallback offer, so single-offer and prior-plan baselines fail even though
    the task remains deterministic and judge-free.
44. PR 72 moves procurement from one-item choice to two-item bundle assembly.
    Compatibility-blind, category-blind, and cheapest-pair baselines fail
    offline, but live `nano` solves the explicit pairwise-bonus version; future
    procurement stress should hide compatibility in vendor evidence or require
    multi-round supply/package updates.
45. PR 73 tests whether natural SKU/package-fit labels alone make bundle
    compatibility harder. They do not: live `nano` still solves all four cases,
    so the next procurement build should infer compatibility from observed
    deployment outcomes rather than listing fit deltas directly.
46. PR 74 implements that first outcome-evidence version. Clean pilot rows are
    still easy for live `nano`, so procurement needs either noisy/conflicting
    deployment evidence, multi-round vendor package history, or hidden package
    interactions with budget/reserve pressure to become a live discriminator.
47. PR 75 adds noisy repeated measurements for the same deployment signal. Live
    `nano` still solves it, so further procurement variants should move beyond
    static two-item package tables.
48. PR 76 converts multi-period deployment history into package value. Live
    `nano` still solves it, so the next procurement build should introduce
    endogenous reserve, inventory, or sequential vendor-update dynamics if
    procurement remains the frontier.
49. PR 77 adds support-tail cost and reserve-shortfall pressure. Live `nano`
    still solves it, so two-SKU procurement arithmetic appears saturated; the
    next procurement attempt should require sequential policy, or the stack
    should pivot back to stronger live-gap domains.
50. PR 78 returns to the pricing frontier with finite stock caps in joint
    pricing. Live `nano` has a large two-price error while avoiding exact named
    baseline collapse, making capacity-constrained joint pricing a stronger
    next research surface than further static procurement variants.
51. PR 79 makes the pricing frontier sequential by sharing inventory across an
    early launch window and a later markdown window. The myopic single-period
    baseline fails hard, while live `nano` lands between rounded-price and
    oracle behavior; this is useful intertemporal-pricing evidence, though PR 78
    remains the stronger live gap.
52. PR 80 keeps the same sequential markdown oracle but replaces clean rows
    with noisy natural launch/clearance evidence. The live `nano` gap increases
    versus PR 79 without becoming a myopic-collapse story, so noisy sequential
    pricing is the better markdown variant to keep in the model-discrimination
    set.
53. PR 81 returns to procurement only after making the action sequential:
    choose a vendor plan across three rounds after delivery-history updates,
    switch costs, and reserve-floor pressure. This succeeds where static
    two-SKU procurement did not: live `nano` has a large regret gap and does not
    simply match the cheap/reputation-blind baseline.
54. PR 82 follows the mechanism frontier note by replacing static mechanism
    fields with observed interaction traces. Live `nano` still parses every
    prompt but chooses trace-blind/revenue-favored mechanisms on half the cases,
    so the trace-projection surface is a productive mechanism discriminator.
55. PR 83 follows the pricing frontier note by making intervention adjustment
    explicit in the evidence rather than in the case label. Additive-only lift
    was saturated by live `nano`, but fixed units plus exposure multipliers and
    noisy regional rows create a nonzero live price gap without collapsing to
    the cap-price intervention-blind baseline.
56. PR 84 adds source-to-target cohort-shift calibration using a small local
    bridge sample. `nano` usually reads the bridge direction but under-applies
    the target-cohort adjustment, so calibration remains useful when the source
    curve and local sample disagree.
57. PR 85 removes the explicit opponent-policy label from market inventory
    pricing and replaces it with price/fill/remaining-stock traces. This is now
    the strongest market live gap: `nano` overprices two sell-through cases,
    triggers reserve violations, and looks trace-blind on the diagnostic metric.
58. PR 86 turns that same trace surface into a staged early/late price plan.
    The fixed one-price baseline is only mildly worse offline, but live `nano`
    degrades sharply by choosing high staged prices and missing the sell-through
    timing, making staged trace inventory the current strongest market result.
59. PR 87 couples that staged trace-pricing surface to an optional replenishment
    order before the late window. The oracle must buy extra inventory only when
    traces imply competitor capacity exit, while avoiding overbuying into
    clearance traces; live `nano` produces the largest market regret so far.
60. PR 88 returns to the mechanism frontier by combining observed interaction
    traces with the self-consistent strategic-share equilibrium. This produces
    the largest mechanism live gap so far and shows that simple trace projection
    can overvalue high-take mechanisms when copycat strategic behavior feeds
    back into future retention.
61. PR 89 naturalizes the same trace-equilibrium mechanism oracle by replacing
    explicit strategic-response labels with pilot outcome language. This tests
    whether the PR 88 frontier survives less machine-readable dynamics fields
    before treating trace-equilibrium mechanism stress as saturated; live
    `nano` still has a nonzero gap, but it is smaller and not a named-baseline
    collapse.
62. PR 90 naturalizes the strongest market trace-replenishment surface. Unlike
    PR 89's mechanism naturalization, the large live gap mostly survives:
    `nano` still misses the trace-conditioned stockout-vs-overbuy tradeoff and
    violates the cash reserve on half the cases.
63. PR 91 combines finite-stock joint pricing with lumpy regional sales
    evidence. The live `nano` gap more than doubles PR 78's L1 error, without
    matching the named capacity-blind or independent baselines, so noisy
    cross-demand estimation remains a productive pricing extension.
64. PR 92 adds lumpy regional shelf evidence to the strongest
    trace-replenishment market task. This is the strongest market live gap so
    far: `nano` remains trace-blind-like on all missable cases while lowering
    reserve violations versus the natural-only variant.
65. PR 93 returns to the mechanism frontier and adds noisy local pilot sheets
    to the trace-equilibrium mechanism surface. The live `nano` gap increases
    versus PR 89's natural prompt while staying below PR 88's explicit-field
    gap and without matching revenue, projection, equilibrium-blind, or
    trace-blind baselines, so noisy pilot evidence is a useful mechanism
    extension but the explicit PR 88 surface remains the strongest mechanism
    gap.
66. PR 94 combines noisy finite-stock joint pricing with sequential
    launch/clearance markdowns. The live `nano` gap becomes the strongest
    pricing result so far, suggesting coupled depletion across products and
    windows is a productive surface.
67. PR 95 changes the sequential pricing action from staged prices alone to a
    price/order plan with replenishment setup costs and storage limits. Live
    `nano` recognizes that restocking is useful but misses order quantity,
    keeping replenishment as a distinct planning stress.
68. PR 96 returns to procurement only through the sequential vendor-policy
    surface, replacing aggregate delivery counts with noisy receiving-ledger
    rows. The live `nano` regret rises versus PR 81 without collapsing to
    reputation-blind or myopic plans, so noisy evidence aggregation is useful
    when attached to a reserve-aware sequence rather than a static bundle.
69. PR 97 adds the rolling/time-local calibration variant recommended after
    PR 84. Offline baselines expose raw-score, stale-window, and pooled-history
    shortcuts, but live `nano` solves the explicit recency-weight version; the
    next calibration build should naturalize the windows or infer recency from
    timestamped outcome logs rather than printing the weights directly.
