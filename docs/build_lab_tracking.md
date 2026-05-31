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

Depth, not case count, is the operating rule. A new fixture counts only when it
closes or sharpens a question raised by prior results: which shortcut fired,
whether the miss is repeat-reliable, whether the evidence channel was too
scaffolded, and whether the same mechanism survives in real-derived data.

Current uncovered directions from the tests:

- C1 filing inference: implicit corporate-action adjustment is the active
  frontier. PR 119 showed repeated `nano` artifact-blind misses under natural
  notes; PR 120 shows that removing notes can also trigger `gpt-5.5`
  reported-value misses. PR 121 controls that evidence channel by making the
  implicit split-like rows value-stable, and live repeats stabilize both
  `nano` and `gpt-5.5`. The current question is now whether real
  corporate-action metadata restores stability under noisier filing traces, and
  whether artifact blindness or reported-value drift is the durable shortcut
  when row-ratio and value-stability evidence disagree.
- Real-derived C1 runner-up ambiguity: the Tiger `mini` runner-up miss did not
  reproduce in build-lab repeats. The question is which real filing trace
  creates repeat-reliable runner-up confusion under a clear dollar-material
  objective, not how many public traces can be listed.
- Calibration and market traces: live gaps are strongest when the model must
  choose the reference class or infer opponent/inventory state from logs. The
  next questions are context selection and state reconstruction, not more
  explicit formula or static demand cases.
- Mechanism and procurement: explicit static variants saturate quickly. The
  uncovered directions are sequential response, participant dynamics,
  equilibrium feedback, noisy ledgers, and reserve pressure.
- De-prioritized unless they answer one of those questions: more clean
  annotated split examples, static two-SKU procurement variants, deterministic
  linear pricing-law holdouts, or additional cases without a named failure
  mechanism.

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
| 98 | `review/98-forecast-rolling-log-calibration` | natural dated-log rolling calibration | oracle expected Brier regret 0; pooled-history regret 0.00770432, latest-window regret 0.00943152, stale-window regret 0.0733895, raw-score regret 0.0758964; live `nano` regret 0.0005 with parse 1.00 |
| 99 | `review/99-forecast-rolling-log-noisy` | noisy implicit dated-log calibration | oracle expected Brier regret 0; latest-window regret 0.00539115, pooled-history regret 0.0128398, raw-score regret 0.067316, stale-window regret 0.0824273; live `nano` regret 0.0011 with parse 1.00 |
| 100 | `review/100-forecast-event-log-calibration` | item-level event-log calibration | oracle expected Brier regret 0; latest-window regret 0.00206831, pooled-history regret 0.00801568, stale-window regret 0.0322748, raw-score regret 0.0723108; live `nano` regret 0.0037 with parse 1.00 |
| 101 | `review/101-forecast-operational-log-calibration` | operational-context event-log calibration | oracle expected Brier regret 0; latest-window regret 0.0038317, route-blind regret 0.00673929, policy-blind regret 0.00793932, pooled-history regret 0.0355321, stale-window regret 0.0403488, raw-score regret 0.086681; live `nano` regret 0.0019 with parse 1.00 |
| 102 | `review/102-principal-holdings-prediction` | predict-the-principal holding-change MVP | oracle score regret 0; generic-style regret 0.539663, low-turnover regret 0.6755, market-return regret 0.775725; live `nano` solves with parse 1.00 |
| 103 | `review/103-principal-holding-noisy` | noisy predict-the-principal holding-change task | oracle score regret 0; mechanical-flow regret 0.35775, generic-style regret 0.539663, low-turnover regret 0.6755, market-return regret 0.775725; live `nano` still solves with parse 1.00 |
| 104 | `review/104-principal-holding-notes` | filing-note predict-the-principal task | oracle score regret 0; mechanical-flow regret 0.35775, generic-style regret 0.539663, low-turnover regret 0.6755, market-return regret 0.775725; live `nano` still solves with parse 1.00 |
| 105 | `review/105-principal-holding-blind-notes` | profile/security-label-blind C1 filing-note task | oracle score regret 0; same shortcut-baseline spread as PR 104; five fresh live `nano` passes range from score regret 0 to 0.2433, accuracy 0.50-1.00 |
| 106 | `review/106-stability-probe` | repeat-run stability probe | `--repeat N --no-cache` reports primary-metric range, parse/accuracy range, unstable-case rate, and modal per-case choices; first live `nano` smoke on blind C1 has score-regret range 0-0.63135 on one case |
| 107 | `review/107-principal-holding-margins` | C1 oracle-margin diagnostics | holding-prediction tasks now report oracle margin and second-best trade; first blind C1 live instability occurred at margin 0.1767, so it is not just a near-tie ambiguity |
| 108 | `review/108-stability-outcome-attribution` | repeat-stability outcome attribution | stability probe now separates stable-oracle, stable-wrong, unstable-oracle-modal, unstable-wrong-modal, and parse-modal cases; full blind C1 live repeat has 3 stable-oracle cases and 1 unstable-wrong-modal case |
| 109 | `review/109-stability-baseline-attribution` | repeat-stability baseline attribution | stability probe now labels modal non-oracle reference matches; the live blind C1 wrong-modal case is attributed to `low_turnover` + `mechanical_flow` |
| 110 | `review/110-stability-sweep` | cross-agent repeat-stability sweeps | `--sweep --repeat N --no-cache` now runs repeat-stability probes per agent; first alias probe separates `mini` from `nano`/`gpt-5.5` on the first blind C1 case |
| 111 | `review/111-stability-sweep-cases` | per-case stability sweep drilldown | sweep reports now include case × agent status, modal choice, oracle margin, oracle-hit rate, and matched non-oracle references, so cross-agent differences can be localized without adding more synthetic cases |
| 112 | `review/112-case-key-filter` | keyed case targeting for depth probes | `--case <key>` now filters keyed case tasks, sweeps, and repeat-stability probes; the pension C1 failure can be rerun directly instead of relying on `--limit 1` or adding cases |
| 113 | `review/113-real-filing-trace` | real-derived C1 filing trace | public SEC-derived Berkshire 13F rows create one neutralized trace where the dollar-material share action beats market-value, low-turnover, max-position, and previous-trend shortcuts |
| 114 | `review/114-raw-filing-trace` | raw-row real-derived C1 filing trace | same public SEC-derived trace, but the model sees only period filing rows and issuer choices instead of a precomputed candidate-change table; first raw live probes exposed a percent-change shortcut, now captured as a named baseline |
| 115 | `review/115-filing-runner-up-depth` | targeted real-derived filing trace depth probe | Tiger Global SEC-derived trace adds a runner-up dollar-material diagnostic; one review-copy live `mini` run hit the second-best action, while build-lab reruns were stable-oracle, making reproducibility the next depth question |
| 116 | `review/116-filing-artifact-depth` | filing-artifact depth probe | split-adjusted filing trace and natural-note variant separate discretionary action from raw corporate-action share movement; offline baselines fire, but live aliases solve both, making less-scaffolded artifact ambiguity the next depth target |
| 117 | `review/117-filing-artifact-stress` | composite filing-artifact stress probe | combines multiple split artifacts, a close runner-up action, value drift, and percent salience; live `nano` becomes unstable while `mini` and `gpt-5.5` stay stable-oracle |
| 118 | `review/118-stability-shortcut-mixture` | choice-level shortcut-mixture attribution for repeat probes | stability summaries now count all repeated choices that hit named non-oracle references, not only the modal choice, so oracle-modal unstable runs still surface artifact-blind/value-drift shortcut mixtures |
| 119 | `review/119-artifact-stress-choice-mix` | live choice-mixture drilldown on the artifact-stress case | repeat-9 OpenAI sweep confirms `mini` and `gpt-5.5` are stable-oracle; `nano` is oracle-modal with 3/9 non-oracle choices, all attributed to artifact-blind raw-share movement |
| 120 | `review/120-implicit-filing-artifact` | implicit artifact-inference C1 stress | removes the artifact-note section from the composite stress prompt; offline baselines preserve dynamic range, and live repeats turn the next question into which evidence channel makes implicit corporate-action adjustment stable |
| 121 | `review/121-implicit-value-stability` | value-stable implicit artifact control | keeps the no-note split-like row-ratio probe but removes the conflicting reported-value jump from one artifact row; live repeats become stable-oracle, so PR120's top-alias miss is an evidence-channel conflict result rather than no-notes alone |

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
| `principal_holding_prediction` | predict-the-principal 13F-style next holding-change task | oracle score regret 0 across 4 synthetic principal-history cases; minimum oracle margin 0.1735; market-return baseline regret 0.775725 with market-return miss 1.00; low-turnover baseline regret 0.6755 with low-turnover miss 1.00; generic-style baseline regret 0.539663 with generic-style miss 1.00; live `nano` solves with parse 1.00 | first runnable C1-style instrument that scores fidelity to a named principal's revealed next choice rather than market return; useful wiring and doctrine, but the clean synthetic histories are saturated for live `nano` |
| `principal_holding_prediction_noisy` | noisy predict-the-principal 13F-style holding-change task | oracle score regret 0 across 4 noisy principal-history cases; mechanical-flow baseline regret 0.35775 with mechanical-flow miss 1.00; market-return baseline regret 0.775725 with market-return miss 1.00; low-turnover baseline regret 0.6755 with low-turnover miss 1.00; generic-style baseline regret 0.539663 with generic-style miss 1.00; live `nano` still solves with parse 1.00 | first inversion-problem version of C1: separate discretionary choices from fund-flow, redemption, index-rebalance, and tax-loss rows; explicit event labels make the task saturated for live `nano`, so the next version should use less explicit filing notes or real-derived histories |
| `principal_holding_prediction_notes` | filing-note predict-the-principal 13F-style holding-change task | oracle score regret 0 across the same 4 noisy principal-history cases; mechanical-flow baseline regret 0.35775 with mechanical-flow miss 1.00; market-return baseline regret 0.775725 with market-return miss 1.00; low-turnover baseline regret 0.6755 with low-turnover miss 1.00; generic-style baseline regret 0.539663 with generic-style miss 1.00; live `nano` still solves with parse 1.00 | removes explicit event-type labels from PR 103 and asks the model to infer filing artifacts from notes about cash schedules, benchmark tickets, risk committee moves, and year-end paired swaps; still saturated for live `nano` |
| `principal_holding_prediction_blind_notes` | label-blind predict-the-principal 13F-style holding-change task | oracle score regret 0 across the same 4 noisy cases; minimum oracle margin 0.1735; mechanical-flow baseline regret 0.35775 with mechanical-flow miss 1.00; market-return baseline regret 0.775725; low-turnover baseline regret 0.6755; generic-style baseline regret 0.539663; five fresh live `nano` passes produce score regrets 0.2433, 0, 0.1578, 0, 0.0434 with accuracy 0.50, 1.00, 0.75, 1.00, 0.75 | neutralizes account/profile/security labels and collapses discretionary notes to generic PM packets; unlike PR 102-104, the live signal becomes sample-unstable, so C1 depth should now measure stability under label removal and move to real-derived traces rather than adding more synthetic variants |
| `principal_holding_filing_trace` | real-derived 13F filing-trace C1 task | oracle score regret 0 across two public SEC-derived traces; second-best baseline regret 0.536452; market-value regret 0.805903; percent-change regret 0.809772; previous-trend regret 0.931789; low-turnover and max-position regret 1; minimum oracle margin 0.3174 | first C1 trace populated from actual SEC 13F rows; depth value is not case count, but the test-derived question. The Tiger trace keeps the same objective but adds a runner-up action ambiguity, separating "wrong shortcut" misses from "nearly right but second-best action" misses |
| `principal_holding_filing_trace_raw` | raw-row real-derived 13F filing-trace C1 task | same offline dynamic range as `principal_holding_filing_trace`; targeted Tiger raw sweep has second-best regret 0.317432, market-value regret 0.611807, trend regret 0.863578, percent-change regret 0.864072, and low-turnover/max-position regret 1; first review-copy Tiger live sweep produced one `mini` second-best miss, but build-lab repeat-3 and repeat-6 reruns were stable-oracle | removes the precomputed candidate-change scaffold from PR 113 and requires inferring the dollar-material share-action issuer from period filing rows. PR 114 exposed percent-change ambiguity on the Berkshire trace; PR 115 shows the next depth question is whether plausible runner-up dollar-material actions create reproducible instability or only occasional near-miss flips |
| `principal_holding_filing_artifact` | filing-artifact C1 trace with structured corporate-action factor | oracle score regret 0 on the split-adjusted trace; artifact-blind and market-value baselines regret 1; percent-change regret 0.691445; second-best regret 0.20561; oracle margin 0.20561 | follows the PR 115 open question about filing artifacts. The task proves the harness can separate a mechanical split-driven raw share jump from the discretionary dollar-material reduction, but the structured adjustment factor is still too explicit for live aliases |
| `principal_holding_filing_artifact_natural` | filing-artifact C1 trace with natural corporate-action notes | same offline dynamic range as the structured artifact task; live repeat-3 on `nano`, `mini`, and `gpt-5.5` is stable-oracle | removes `adjustment_factor=` from the prompt and leaves the 4-for-1 split as natural note text. Current live aliases still solve, so this is a depth control rather than a tier separator; the next artifact probe needs weaker/noisier notes or artifact plus runner-up ambiguity |
| `principal_holding_filing_artifact_stress` | composite filing-artifact C1 stress with multiple natural-note artifacts and a close runner-up | oracle score regret 0; second-best regret 0.0645161; percent-change regret 0.774194; artifact-blind and market-value baselines regret 1; oracle margin 0.0645161 | follows PR 116's limitation rather than adding clean cases. The live result separates aliases: `mini` and `gpt-5.5` solve, while `nano` is unstable across fresh repeats, with misses attributed to value-drift in one run and artifact-blind raw share movement in the drilldown |
| `principal_holding_filing_artifact_implicit` | composite artifact C1 stress with no artifact-note section | oracle score regret 0; second-best regret 0.0645161; percent-change regret 0.774194; artifact-blind and market-value baselines regret 1; oracle margin 0.0645161 | uses the same composite stress fixture as PR 117 but removes the note channel, forcing split-like artifact inference from row patterns. This is a depth move on the PR 119 finding: the question is whether implicit artifact adjustment needs stronger row-ratio evidence, value-stability evidence, or real corporate-action context, not whether another annotated split case can be added |
| `principal_holding_filing_artifact_implicit_stable` | no-note artifact C1 control with value-stable split-like rows | oracle score regret 0; second-best regret 0.0645161; percent-change regret 0.774194; artifact-blind and market-value baselines regret 1; oracle margin 0.0645161 | keeps the PR120 no-note row-ratio task but changes the split-like value-drift artifact into a value-stable row. Live repeat-3 across all aliases and repeat-6 on `nano`/`gpt-5.5` are stable-oracle, so the PR120 `gpt-5.5` market-value miss is best read as a conflict between row-ratio and reported-value channels |
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
| `forecast_rolling_log_calibration` | natural dated-log calibration after recent cohort drift | oracle expected Brier regret near 0 across 4 dated-log cases; raw-score baseline regret 0.0758964 with raw-score miss 1.00; stale-window baseline regret 0.0733895 with stale-window miss 1.00; pooled-history baseline regret 0.00770432 with pooled-history miss 1.00; latest-window baseline regret 0.00943152 with latest-window miss 1.00; live `nano` regret 0.0005 with parse 1.00 and no named shortcut miss | removes explicit recency weights from PR 97 and forces recency inference from dated outcome batches; this creates a small live gap without a simple named failure mode, so the next harder version should add noisier uneven logs or omit the half-life hint |
| `forecast_rolling_log_noisy` | noisy implicit dated-log calibration after recent cohort drift | oracle expected Brier regret near 0 across 4 noisy dated-log cases; raw-score baseline regret 0.067316 with raw-score miss 1.00; stale-window baseline regret 0.0824273 with stale-window miss 1.00; pooled-history baseline regret 0.0128398 with pooled-history miss 1.00; latest-window baseline regret 0.00539115 with latest-window miss 1.00; live `nano` regret 0.0011 with parse 1.00 and no named shortcut miss | removes the machine-readable half-life value and adds uneven thin recent logs; this increases the live gap versus PR 98 while keeping parse stable, but the model still tracks direction well enough to avoid raw/stale/pooled/latest collapse |
| `forecast_event_log_calibration` | item-level recency and score-local calibration from dated records | oracle expected Brier regret near 0 across 4 item-log cases; raw-score baseline regret 0.0723108 with raw-score miss 1.00; stale-window baseline regret 0.0322748 with stale-window miss 1.00; pooled-history baseline regret 0.00801568 with pooled-history miss 1.00; latest-window baseline regret 0.00206831 with latest-window miss 1.00; live `nano` regret 0.0037 with parse 1.00, raw-score miss 0.33, pooled-history miss 0.33, and latest-window miss 0.25 | moves beyond pre-aggregated dated bins into individual scored records; this creates the strongest rolling-calibration live gap so far and begins to surface named shortcut behavior again |
| `forecast_operational_log_calibration` | policy- and route-local calibration from operational event logs | oracle expected Brier regret near 0 across 4 operational-log cases; raw-score baseline regret 0.086681 with raw-score miss 1.00; stale-window baseline regret 0.0403488 with stale-window miss 1.00; pooled-history baseline regret 0.0355321 with pooled-history miss 1.00; policy-blind baseline regret 0.00793932 with policy-blind miss 1.00; route-blind baseline regret 0.00673929 with route-blind miss 1.00; latest-window baseline regret 0.0038317 with latest-window miss 1.00; live `nano` regret 0.0019 with parse 1.00, policy-blind miss 0.25, route-blind miss 0.25, pooled-history miss 0.25, and latest-window miss 0.33 | extends PR 100 by making reference-class choice operational: same-score records from different policy/route contexts are intentionally misleading; this opens policy/route-blind diagnostics while live `nano` remains below the easiest named baselines |
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
PR 98 naturalizes the rolling calibration surface as dated outcome-log batches.
PR 99 removes the printed half-life value and adds uneven noisy dated score bands.
PR 100 moves the rolling calibration surface to individual scored event logs.
PR 101 adds operational policy/route filtering to the item-level event-log
calibration surface.
PR 102 adds the first predict-the-principal holding-change MVP for the C1
direction.
PR 103 adds the first noisy inversion-problem version of the C1 holding-change
task with fund-flow, redemption, index-rebalance, and tax-loss rows.
PR 104 removes those explicit event-type labels and replaces them with
filing-note strings while preserving the same mechanical-flow diagnostic.
PR 105 neutralizes profile and security labels in the C1 filing-note prompt to
test whether prior live success depended on label shortcuts rather than
revealed-style inference.

| Check | Command | Result |
|---|---|---|
| Unit tests | `python -m pytest` | 246 tests passed after PR 105 |
| Full offline oracle task pass after PR 105 | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all then-current 84 task runners executed; oracle errors/regrets zero or expected near-zero; includes `principal_holding_prediction_blind_notes` with n=4, score regret 0, accuracy 1.00, and named miss diagnostics 0; includes `principal_holding_prediction_notes` with n=4, score regret 0, accuracy 1.00, and named miss diagnostics 0; includes `principal_holding_prediction_noisy` with n=4, score regret 0, accuracy 1.00, and named miss diagnostics 0; includes `principal_holding_prediction` with n=4, score regret 0, accuracy 1.00, and named miss diagnostics 0; includes `mechanism_trace_equilibrium_noisy` with n=4, score regret 0 and all named miss diagnostics 0; includes `market_trace_replenishment_noisy` with n=4, constrained terminal-cash regret near 0, decision L1 0, reserve violation 0, no-replenishment miss 0, one-price miss 0, trace-blind miss 0, and replenishment-blind miss 0; includes `pricing_inventory_replenishment_noisy` with n=4, decision L1 error 0 and revenue gap 0; includes `procurement_vendor_update_noisy` with n=4, score regret 0, parse 1.00, and named miss diagnostics 0; includes `forecast_rolling_calibration` with n=4, expected Brier regret near 0 and named miss diagnostics 0; includes `forecast_rolling_log_calibration` with n=4, expected Brier regret near 0 and named miss diagnostics 0; includes `forecast_rolling_log_noisy` with n=4, expected Brier regret near 0 and named miss diagnostics 0; includes `forecast_event_log_calibration` with n=4, expected Brier regret near 0 and named miss diagnostics 0; includes `forecast_operational_log_calibration` with n=4, expected Brier regret near 0 and policy/route-blind miss diagnostics 0; scam control `instrument_fires=True`; alignment-tax regret 0; revealed-allocation regret 0 |
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
| Forecast rolling-log calibration sweep | `python -m aeread_lab.cli --sweep --task forecast_rolling_log_calibration --agents offline:oracle,offline:raw_score,offline:stale_window,offline:pooled_history,offline:latest_window --no-cache` | oracle rank 1 with expected Brier regret near 0; pooled-history regret 0.00770432 with pooled-history miss 1.00; latest-window regret 0.00943152 with latest-window miss 1.00; stale-window regret 0.0733895 with stale-window miss 1.00; raw-score regret 0.0758964 with raw-score miss 1.00; parse 1.00 |
| Forecast noisy rolling-log calibration sweep | `python -m aeread_lab.cli --sweep --task forecast_rolling_log_noisy --agents offline:oracle,offline:raw_score,offline:stale_window,offline:pooled_history,offline:latest_window --no-cache` | oracle rank 1 with expected Brier regret near 0; latest-window regret 0.00539115 with latest-window miss 1.00; pooled-history regret 0.0128398 with pooled-history miss 1.00; raw-score regret 0.067316 with raw-score miss 1.00; stale-window regret 0.0824273 with stale-window miss 1.00; parse 1.00 |
| Forecast event-log calibration sweep | `python -m aeread_lab.cli --sweep --task forecast_event_log_calibration --agents offline:oracle,offline:raw_score,offline:stale_window,offline:pooled_history,offline:latest_window --no-cache` | oracle rank 1 with expected Brier regret near 0; latest-window regret 0.00206831 with latest-window miss 1.00; pooled-history regret 0.00801568 with pooled-history miss 1.00; stale-window regret 0.0322748 with stale-window miss 1.00; raw-score regret 0.0723108 with raw-score miss 1.00; parse 1.00 |
| Forecast operational-log calibration sweep | `python -m aeread_lab.cli --sweep --task forecast_operational_log_calibration --agents offline:oracle,offline:latest_window,offline:policy_blind,offline:route_blind,offline:pooled_history,offline:stale_window,offline:raw_score --no-cache` | oracle rank 1 with expected Brier regret near 0; latest-window regret 0.0038317 with latest-window miss 1.00; route-blind regret 0.00673929 with route-blind miss 1.00; policy-blind regret 0.00793932 with policy-blind miss 1.00; pooled-history regret 0.0355321 with pooled-history miss 1.00; stale-window regret 0.0403488 with stale-window miss 1.00; raw-score regret 0.086681 with raw-score miss 1.00; parse 1.00 |
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
| Principal holding prediction sweep | `python -m aeread_lab.cli --sweep --task principal_holding_prediction --agents offline:oracle,offline:generic_style,offline:low_turnover,offline:max_return --no-cache` | oracle rank 1 with score regret 0; generic-style regret 0.539663; low-turnover regret 0.6755; max-return/market-return regret 0.775725; parse 1.00 |
| Noisy principal holding prediction sweep | `python -m aeread_lab.cli --sweep --task principal_holding_prediction_noisy --agents offline:oracle,offline:mechanical_flow,offline:generic_style,offline:low_turnover,offline:max_return --no-cache` | oracle rank 1 with score regret 0; mechanical-flow regret 0.35775; generic-style regret 0.539663; low-turnover regret 0.6755; max-return/market-return regret 0.775725; parse 1.00 |
| Filing-note principal holding prediction sweep | `python -m aeread_lab.cli --sweep --task principal_holding_prediction_notes --agents offline:oracle,offline:mechanical_flow,offline:generic_style,offline:low_turnover,offline:max_return --no-cache` | oracle rank 1 with score regret 0; mechanical-flow regret 0.35775; generic-style regret 0.539663; low-turnover regret 0.6755; max-return/market-return regret 0.775725; parse 1.00 |
| Blind-note principal holding prediction sweep | `python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents offline:oracle,offline:mechanical_flow,offline:generic_style,offline:low_turnover,offline:max_return --no-cache` | oracle rank 1 with score regret 0; mechanical-flow regret 0.35775; generic-style regret 0.539663; low-turnover regret 0.6755; max-return/market-return regret 0.775725; parse 1.00 |
| Blind-note margin smoke | `python -m aeread_lab.cli --task principal_holding_prediction_blind_notes --agent offline:oracle --no-cache` | score regret 0; accuracy 1.00; minimum oracle margin 0.1735, so the synthetic C1 targets are not near-tie cases |
| Stability outcome-attribution smoke | `python -m aeread_lab.cli --task principal_holding_prediction_blind_notes --agent offline:oracle --repeat 3 --limit 1 --no-cache` | status count `stable_oracle:1`, stable-oracle case rate 1.00, mean case oracle-hit rate 1.00, parse-modal rate 0 |
| Stability baseline-attribution smoke | `python -m pytest tests/test_tasks.py -k 'stability_probe'` | synthetic stable non-oracle modal is attributed to `max_return` + `second_best`, proving the attribution layer only counts named references that differ from the oracle |
| Stability sweep smoke | `python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents offline:oracle,offline:low_turnover --repeat 2 --limit 1 --no-cache` | oracle rank 1 with mean score regret 0 and stable-oracle rate 1.00; low-turnover mean score regret 0.63135 with non-oracle modal rate 1.00 and refs `low_turnover`, `mechanical_flow` |
| Stability sweep drilldown smoke | `python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents offline:oracle,offline:low_turnover --repeat 2 --limit 1 --no-cache` | report includes `Per-case stability drilldown`; `pension_outflow_quality_signal` is stable-oracle for oracle and stable-non-oracle for low-turnover, with modal `move_to_cash` matching `low_turnover` + `mechanical_flow` at oracle margin 0.1767 |
| Keyed C1 case-targeting smoke | `python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents offline:oracle,offline:low_turnover --repeat 2 --case pension_outflow_quality_signal --no-cache` | report header includes `cases=pension_outflow_quality_signal`; the exact pension C1 failure is rerun without depending on task order, preserving the same oracle/low-turnover separation |
| Real-derived C1 filing-trace oracle smoke | `python -m aeread_lab.cli --task principal_holding_filing_trace --agent offline:oracle --no-cache` | n=2, score regret 0, accuracy 1.00, minimum oracle margin 0.3174, and all named shortcut miss rates, including percent-change and second-best miss, are 0 for the oracle |
| Real-derived C1 filing-trace shortcut sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace --agents offline:oracle,offline:market_value,offline:low_turnover,offline:max_position,offline:trend,offline:percent_change,offline:second_best --no-cache` | oracle rank 1 with score regret 0; second-best regret 0.536452; market-value regret 0.805903; percent-change regret 0.809772; previous-trend regret 0.931789; low-turnover and max-position regret 1; this is a depth probe for dollar-material share action versus filing-value drift, percentage-change salience, and runner-up action ambiguity |
| Real-derived C1 filing-trace keyed sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace --agents offline:oracle,offline:market_value --repeat 2 --case brk_2026q1_energy_rebalance --no-cache` | report header includes `cases=brk_2026q1_energy_rebalance`; oracle is stable-oracle with modal `reduce_chevron`, while market-value is stable-non-oracle with modal `price_drift_oxy` and matched reference `market_value` |
| Raw-row real-derived C1 filing-trace tests | `python -m pytest tests/test_tasks.py -k 'filing_trace or principal_holding'` | 16 selected tests passed; raw prompt includes final-period `filing_row` rows and omits `candidate_trade` / `prior_shares` scaffold fields; Tiger keyed tests verify the runner-up second-best diagnostic |
| Raw-row real-derived C1 filing-trace shortcut sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents offline:oracle,offline:market_value,offline:low_turnover,offline:max_position,offline:trend,offline:percent_change,offline:second_best --no-cache` | oracle rank 1 with score regret 0; second-best regret 0.536452; market-value regret 0.805903; percent-change regret 0.809772; previous-trend regret 0.931789; low-turnover and max-position regret 1 |
| Raw-row real-derived C1 filing-trace keyed sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents offline:oracle,offline:percent_change --repeat 2 --case brk_2026q1_energy_rebalance --no-cache` | oracle is stable-oracle with modal `sec_chevron`; percent-change is stable-non-oracle with modal `sec_constellation` and matched reference `percent_change` |
| Tiger raw-row C1 runner-up keyed sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents offline:oracle,offline:second_best --repeat 2 --case tiger_2026q1_megacap_rotation --no-cache` | oracle is stable-oracle with modal `sec_tiger_e`; second-best is stable-non-oracle with modal `sec_tiger_h`, regret 0.317432, and matched reference `second_best` |
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
| Sampled all-task oracle smoke | `python3 -m aeread_lab.cli --task all --agent offline:oracle --limit 1 --no-cache` | all then-current task runners executed with first deterministic case/gamble only; scam remained instrumented |
| Sampled JSON smoke | `python3 -m aeread_lab.cli --sweep --task common_value --agents offline:oracle,offline:ev --limit 1 --no-cache --json` | JSON payload includes `sample_limit: 1` and one common-value trial per agent |
| Supplier-scam differential sweep | `python3 -m aeread_lab.cli --sweep --task supplier_scam --agents offline:oracle,offline:reputation_blind,offline:timing_blind,offline:credulous --no-cache` | oracle rank 1 with constrained regret 0; reputation-blind constrained regret 23.385 and reputation miss 1.00; timing-blind constrained regret 99.6365 and timing violation 0.1818; credulous constrained regret 304.186 and scam-supplier rate 0.545; parse 1.00 |
| Supplier-scam reputation-blind smoke | `python3 -m aeread_lab.cli --task supplier_scam --agent offline:reputation_blind --no-cache` | constrained final-cash regret 23.385; reputation miss 1.00; reserve and timing violations 0.00 |
| Principal/portfolio/ambiguity sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Bargaining/belief/market sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 for bargaining and market; bargaining now includes alternating/hidden variants; belief prior baseline fails; high-anchor ties current primary metric |
| Matching/screening/mechanism sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1 on all; bad baselines expose intended failure modes |
| Strategic/exploration/experiment/retail/scam sweeps | task-specific sweeps with oracle and known-bad/control baselines | oracle rank 1 on the tracked primary metrics; strategic drift now exposes stress-drift and myopic-miss rates; retail ranks by order error and exposes both ruin and multi-period miss metrics; scam dynamic range validated |
| Auction/procurement/pricing sweeps | task-specific sweeps with oracle and known-bad baselines | oracle rank 1; procurement/pricing parse 1.00 |
| All-task JSON smoke | `python3 -m aeread_lab.cli --sweep --task all --agents offline:oracle,offline:ev --no-cache --json` | saved 2 runs and 40 result rows to `/tmp/aeread_review_all_oracle_ev_sweep.json` |
| Full all-task oracle after stability probe | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all then-current 84 task runners execute; oracle path remains score/regret clean, including `principal_holding_prediction_blind_notes` |
| PR113 focused C1 filing-trace tests | `python -m pytest tests/test_tasks.py -k 'filing_trace or principal_holding'` | 10 selected tests passed; the real-derived filing trace oracle beats shortcut baselines and `--case brk_2026q1_energy_rebalance` targets the SEC-derived fixture |
| PR113 full pytest | `python -m pytest` | 256 tests passed |
| PR113 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 85 current task runners execute; oracle path remains score/regret clean, including `principal_holding_filing_trace` with n=1, score regret 0, accuracy 1.00, and oracle margin 0.7555 |
| PR114 focused raw-row filing-trace tests | `python -m pytest tests/test_tasks.py -k 'filing_trace or principal_holding'` | 13 selected tests passed; raw-row prompt removes the candidate-change scaffold while preserving oracle/shortcut separation |
| PR114 full pytest | `python -m pytest` | 259 tests passed |
| PR114 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 86 current task runners execute; oracle path remains score/regret clean, including `principal_holding_filing_trace_raw` with n=1, score regret 0, accuracy 1.00, and oracle margin 0.7555 |
| PR114 percent-change diagnostic update | `python -m pytest tests/test_tasks.py -k 'filing_trace or principal_holding'`; `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents offline:oracle,offline:market_value,offline:low_turnover,offline:max_position,offline:trend,offline:percent_change --no-cache`; `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace --agents offline:oracle,offline:market_value,offline:low_turnover,offline:max_position,offline:trend,offline:percent_change --no-cache` | focused tests passed; explicit and raw filing-trace sweeps rank oracle first with score regret 0; percent-change baseline regret is 0.7555, isolating the discovered `sec_constellation` / `reduce_constellation` shortcut from the dollar-material oracle target |
| PR115 focused runner-up filing-trace tests | `python -m pytest tests/test_tasks.py -k 'filing_trace or principal_holding'` | 16 selected tests passed; Tiger keyed fixtures prove oracle, market-value, percent-change, and second-best references are distinct, and stability attribution labels the runner-up second-best baseline |
| PR115 Tiger raw shortcut sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents offline:oracle,offline:market_value,offline:low_turnover,offline:max_position,offline:trend,offline:percent_change,offline:second_best --case tiger_2026q1_megacap_rotation --no-cache` | oracle rank 1; second-best regret 0.317432; market-value regret 0.611807; trend regret 0.863578; percent-change regret 0.864072; low-turnover and max-position regret 1 |
| PR115 full pytest | `python -m pytest` | 262 tests passed |
| PR115 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 86 current task runners execute; oracle path remains score/regret clean, including both filing-trace tasks with n=2, score regret 0, accuracy 1.00, minimum oracle margin 0.3174, and all named miss diagnostics 0 |
| PR116 focused filing-artifact tests | `python -m pytest tests/test_tasks.py -k 'filing_artifact or filing_trace or principal_holding'` | 24 selected tests passed; structured and natural artifact prompts, offline shortcut separation, keyed fixture, and artifact-blind stability attribution are covered |
| PR116 structured filing-artifact sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact --agents offline:oracle,offline:artifact_blind,offline:market_value,offline:percent_change,offline:second_best --no-cache` | oracle rank 1; second-best regret 0.20561; percent-change regret 0.691445; artifact-blind and market-value regret 1 |
| PR116 natural-note filing-artifact sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_natural --agents offline:oracle,offline:artifact_blind,offline:market_value,offline:percent_change,offline:second_best --no-cache` | same offline ranking as the structured artifact task, but the prompt removes the structured `adjustment_factor=` field |
| PR116 full pytest | `python -m pytest` | 270 tests passed |
| PR116 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 88 current task runners execute; oracle path remains score/regret clean, including structured and natural filing-artifact tasks with n=1, score regret 0, accuracy 1.00, and oracle margin 0.2056 |
| PR117 focused filing-artifact stress tests | `python -m pytest tests/test_tasks.py -k 'filing_artifact or filing_trace or principal_holding'` | 28 selected tests passed; composite stress prompt, offline shortcut separation, keyed fixture, and close runner-up margin are covered |
| PR117 filing-artifact stress sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents offline:oracle,offline:artifact_blind,offline:market_value,offline:percent_change,offline:second_best --no-cache` | oracle rank 1; second-best regret 0.0645161; percent-change regret 0.774194; artifact-blind and market-value regret 1 |
| PR117 filing-artifact stress keyed stability | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents offline:oracle,offline:second_best --repeat 2 --case multi_artifact_close_runner_up --no-cache` | oracle is stable-oracle with modal `sec_stress_b`; second-best is stable-non-oracle with modal `sec_stress_c`, regret 0.0645161, and matched reference `second_best` |
| PR117 full pytest | `python -m pytest` | 274 tests passed |
| PR117 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 89 current task runners execute; oracle path remains clean, including `principal_holding_filing_artifact_stress` with n=1, score regret 0, accuracy 1.00, and oracle margin 0.0645 |
| PR118 focused stability-mixture tests | `python -m pytest tests/test_tasks.py -k 'stability or filing_artifact or filing_trace or principal_holding'` | 36 selected tests passed; repeat probes now preserve modal attribution while also counting non-modal artifact-blind and market-value shortcut hits across repeated choices |
| PR118 stability-mixture display smoke | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents offline:oracle,offline:artifact_blind,offline:market_value --repeat 2 --case multi_artifact_close_runner_up --no-cache` | stability sweep prints a `Choice reference mix` section; artifact-blind and market-value baselines each have non-oracle choice rate 1.00, attributed rate 1.00, and choice reference counts of 2 for their named shortcut |
| PR118 full pytest | `python -m pytest` | 275 tests passed |
| PR118 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 89 current task runners execute; oracle path remains clean; PR118 changes reporting/attribution only and does not alter task oracles |
| PR119 artifact-stress choice-mixture live repeat | `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 9 --case multi_artifact_close_runner_up --no-cache` | completed in the review copy; `mini` and `gpt-5.5` are stable-oracle with score regret 0; `nano` is unstable-oracle-modal with mean score regret 0.333333, accuracy 0.666667, oracle-hit 0.666667, non-oracle choice rate 0.333333, attributed non-oracle rate 1.00, and choice reference counts `artifact_blind:3` |
| PR120 focused implicit-artifact tests | `python -m pytest tests/test_tasks.py -k 'filing_artifact or filing_trace or principal_holding'` | 32 selected tests passed; the no-note prompt omits all `artifact_note` lines, the offline oracle infers common split ratios from row patterns, and shortcut baselines remain separated |
| PR120 implicit artifact shortcut sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_implicit --agents offline:oracle,offline:artifact_blind,offline:market_value,offline:percent_change,offline:second_best --no-cache` | oracle rank 1; second-best regret 0.0645161; percent-change regret 0.774194; artifact-blind and market-value regret 1 |
| PR120 full pytest | `python -m pytest` | 279 tests passed |
| PR120 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 90 current task runners execute; oracle path remains clean, including `principal_holding_filing_artifact_implicit` with `n=1`, score regret 0, accuracy 1.00, and oracle margin 0.0645 |
| PR121 focused value-stable implicit-artifact tests | `python -m pytest tests/test_tasks.py -k 'filing_artifact or filing_trace or principal_holding'` | 36 selected tests passed; the value-stable no-note prompt omits artifact notes, preserves close-runner-up structure, and moves the market-value shortcut from the split-like artifact row to the pure value-drift row |
| PR121 value-stable implicit shortcut sweep | `python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_implicit_stable --agents offline:oracle,offline:artifact_blind,offline:market_value,offline:percent_change,offline:second_best --no-cache` | oracle rank 1; second-best regret 0.0645161; percent-change regret 0.774194; artifact-blind and market-value regret 1 |
| PR121 value-stable implicit live repeat | `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_implicit_stable --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case multi_artifact_value_stable_close_runner_up --no-cache` | all three aliases are stable-oracle with parse floor 1.00, score regret 0, accuracy 1.00, and modal `sec_stress_b` |
| PR121 value-stable implicit live follow-up | `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_implicit_stable --agents openai:nano,openai:gpt-5.5 --repeat 6 --case multi_artifact_value_stable_close_runner_up --no-cache` | `nano` and `gpt-5.5` remain stable-oracle with parse floor 1.00, score regret 0, accuracy 1.00, and modal `sec_stress_b` |
| PR121 full pytest | `python -m pytest` | 283 tests passed |
| PR121 full all-task oracle | `python -m aeread_lab.cli --task all --agent offline:oracle --no-cache` | all 91 current task runners execute; oracle path remains clean, including `principal_holding_filing_artifact_implicit_stable` with `n=1`, score regret 0, accuracy 1.00, and oracle margin 0.0645 |
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
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task forecast_rolling_log_calibration --agent openai:nano --cache-dir /tmp/aeread_pr98_live_cache --no-cache` | completed; n=4, parse 1.00, expected Brier regret 0.0005, probability error 0.0119, raw-score miss 0.00, stale-window miss 0.00, pooled-history miss 0.00, latest-window miss 0.00 | dated outcome logs create a small live gap without collapsing into a named shortcut; `nano` uses recency direction but does not exactly match the time-decay oracle |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task forecast_rolling_log_noisy --agent openai:nano --cache-dir /tmp/aeread_pr99_live_cache --no-cache` | completed; n=4, parse 1.00, expected Brier regret 0.0011, probability error 0.0284, raw-score miss 0.00, stale-window miss 0.00, pooled-history miss 0.00, latest-window miss 0.00 | removing the printed half-life and adding uneven thin recent logs increases the live gap versus PR 98, but `nano` still avoids the named shortcut baselines |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task forecast_event_log_calibration --agent openai:nano --cache-dir /tmp/aeread_pr100_live_cache --no-cache` | completed; n=4, parse 1.00, expected Brier regret 0.0037, probability error 0.0480, raw-score miss 0.33, stale-window miss 0.00, pooled-history miss 0.33, latest-window miss 0.25 | individual scored records create a stronger live calibration gap than PR 99 and start to trigger named shortcut diagnostics again |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task forecast_operational_log_calibration --agent openai:nano --cache-dir /tmp/aeread_pr101_live_cache --no-cache` | completed; n=4, parse 1.00, expected Brier regret 0.0019, probability error 0.0389, raw-score miss 0.33, stale-window miss 0.00, pooled-history miss 0.25, latest-window miss 0.33, policy-blind miss 0.25, route-blind miss 0.25 | adding policy/route-local reference classes keeps a nonzero live calibration gap and starts to expose operational-context misses, though the live gap is smaller than PR 100 and below the easiest named baselines |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task principal_holding_prediction --agent openai:nano --cache-dir /tmp/aeread_pr102_live_cache --no-cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, market-return miss 0.00, low-turnover miss 0.00, generic-style miss 0.00 | the first predict-the-principal MVP validates the interface and C1 framing, but the clean synthetic histories are saturated for live `nano`; the next version needs noisy/mechanical-flow confounds or real 13F-derived histories |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task principal_holding_prediction_noisy --agent openai:nano --cache-dir /tmp/aeread_pr103_live_cache --no-cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, market-return miss 0.00, low-turnover miss 0.00, generic-style miss 0.00, mechanical-flow miss 0.00 | explicit event-type filing labels are enough for live `nano` to separate discretionary choices from mechanical rows; the next C1 version should use less explicit notes, ambiguous filing contexts, or real-derived histories |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task principal_holding_prediction_notes --agent openai:nano --cache-dir /tmp/aeread_pr104_live_cache_neutral_ids --no-cache` | completed; n=4, parse 1.00, score regret 0, accuracy 1.00, market-return miss 0.00, low-turnover miss 0.00, generic-style miss 0.00, mechanical-flow miss 0.00 | filing notes without explicit event-type labels or descriptive history IDs are still enough for live `nano`; the next C1 version needs more ambiguous raw-note phrasing, conflicting notes, or real-derived histories |
| five fresh `openai:nano` passes on `principal_holding_prediction_blind_notes` with `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192` | completed; parse 1.00 throughout; four passes used `--no-cache`, one was an empty-cache JSON trace; score regrets 0.2433 / 0 / 0.1578 / 0 / 0.0434; accuracies 0.50 / 1.00 / 0.75 / 1.00 / 0.75 | removing profile/security labels turns the C1 synthetic task from saturated into sample-unstable. This is a depth result: the next C1 question is stability and real-data validity, not more synthetic cases. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task principal_holding_prediction_blind_notes --agent openai:nano --repeat 3 --limit 1 --no-cache` | completed; repeats 3, sample_limit 1, parse-rate range 1.00-1.00, score-regret range 0-0.63135, accuracy range 0.00-1.00, unstable-case rate 1.00, oracle margin 0.1767 on the flipped case | PR 106 turns the manual PR 105 observation into a reusable depth probe; PR 107 shows the flip is not a near-tie artifact, because the first-case margin is well above the low-margin threshold. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task principal_holding_prediction_blind_notes --agent openai:nano --repeat 3 --no-cache` | completed; repeats 3 across all 4 blind-note C1 cases, parse-rate range 1.00-1.00, score-regret range 0-0.157838, accuracy range 0.75-1.00, unstable-case rate 0.25; status counts `stable_oracle:3`, `unstable_non_oracle_modal:1`; mean case oracle-hit 0.833333 | PR 108 localizes the live C1 instability: it is not global sampling noise across the task, but one persistent label-blind filing-inversion case (`pension_outflow_quality_signal`) whose modal live choice is the mechanical-flow trade `move_to_cash` despite oracle margin 0.1767. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --task principal_holding_prediction_blind_notes --agent openai:nano --repeat 3 --no-cache` after baseline attribution | completed; repeats 3 across all 4 blind-note C1 cases, parse-rate range 1.00-1.00, score-regret range 0-0.157838, accuracy range 0.75-1.00, unstable-case rate 0.25; status counts `stable_oracle:3`, `unstable_non_oracle_modal:1`; modal non-oracle reference counts `low_turnover:1`, `mechanical_flow:1`; attributed non-oracle-modal case rate 1.00 | PR 109 makes the shortcut attribution explicit: the unstable wrong-modal C1 case is the pension filing-noise case, and its modal `move_to_cash` answer matches both low-turnover and mechanical-flow references while remaining non-oracle. The next C1 depth step is not more synthetic cases but real-derived traces that test whether this flow/turnover shortcut survives. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 2 --limit 1 --no-cache` | completed; `nano` and `gpt-5.5` both stable-oracle with score regret 0, parse floor 1.00, stable-oracle rate 1.00; `mini` stable non-oracle with score regret 0.63135, accuracy 0, non-oracle modal rate 1.00, refs `low_turnover`, `mechanical_flow` | PR 110 makes the C1 shortcut visibly capability-sensitive on the same repeated first case: `mini` falls to the flow/turnover shortcut while `nano` and `gpt-5.5` do not in this small probe. The right next live use of the sweep is full-case alias stability, not more cases. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 2 --no-cache` | completed in the build-lab copy; `gpt-5.5` stable-oracle on all 4 cases with score regret 0 and accuracy 1.00; `nano` mean score regret 0.0789188, accuracy 0.875, stable-oracle on 3 cases and unstable-oracle-modal on the pension case; `mini` mean score regret 0.423456, accuracy 0.125, non-oracle modal rate 1.00, with shortcut matches spanning `generic_style`, `low_turnover`, `max_return`, `second_best`, and `mechanical_flow` | PR 111's drilldown converts the full-case alias result into a clear research question: C1 label-blind filing inference is solved by `gpt-5.5`, mostly solved but sampling-unstable for `nano` on the pension flow case, and systematically shortcut-driven for `mini`. The next depth step is real-derived filing traces or repeated full-case sweeps, not synthetic case expansion. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_prediction_blind_notes --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case pension_outflow_quality_signal --no-cache` | completed in the build-lab copy; `gpt-5.5` stable-oracle with score regret 0 and accuracy 1.00; `nano` unstable-oracle-modal with mean score regret 0.21045 and oracle-hit rate 0.666667; `mini` unstable-non-oracle-modal with mean score regret 0.4209, oracle-hit rate 0.333333, and modal `move_to_cash` matching `low_turnover` + `mechanical_flow` | PR 112's keyed probe confirms the pension C1 failure is not an ordering artifact: the exact case remains the tier separator. `gpt-5.5` solves it, `nano` samples between oracle and shortcut, and `mini` modal-collapses to the flow/turnover shortcut. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_trace --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 2 --case brk_2026q1_energy_rebalance --no-cache` | completed in the build-lab copy; all three aliases parse 1.00, score regret 0, accuracy 1.00, stable-oracle rate 1.00, and modal `reduce_chevron` on the public SEC-derived trace | PR 113 validates the real-derived C1 harness but does not create a live failure on the first trace. The result shifts the next question from breadth to trace difficulty: find real filing sequences where share action is entangled with flow/turnover noise, corporate actions, or stale value drift while keeping the same shortcut attribution machinery. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 2 --case brk_2026q1_energy_rebalance --no-cache` | completed in the build-lab copy after adding the percent-change diagnostic and explicit dollar-material wording; all three aliases parse 1.00, score regret 0, accuracy 1.00, stable-oracle rate 1.00, and modal `sec_chevron` on the public SEC-derived trace | The first raw-row probe before this clarification exposed the missing diagnostic: smaller aliases sometimes chose `sec_constellation`, the largest percentage reduction, instead of `sec_chevron`, the largest dollar-material share action. PR 114 now treats percent-change as a named shortcut; with the target made explicit, the current trace is solved, so the next depth question is to find real traces where percentage salience, value drift, filing artifacts, or quarter-to-quarter noise remain hard even under a clear dollar-material objective. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case tiger_2026q1_megacap_rotation --no-cache` | first completed in the review copy; `nano` and `gpt-5.5` were stable-oracle with score regret 0; `mini` was unstable-oracle-modal with mean score regret 0.105811, accuracy 0.666667, primary range 0.317432, and one runner-up miss | PR 115's first live run showed the exact failure mode the new diagnostic was built to separate: the non-oracle `mini` choice was the plausible runner-up dollar-material reduction, not percent-change, value drift, turnover, max-position, or trend collapse. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents openai:mini --repeat 6 --case tiger_2026q1_megacap_rotation --no-cache --json` | first completed in the review copy; `mini` choice counts were `sec_tiger_e:5`, `sec_tiger_h:1`, parse 1.00, oracle-hit 0.833333, primary mean 0.0529053, and the non-oracle choice matched `second_best` | gives the attribution for the observed miss, but not yet a reproducible live gap. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case tiger_2026q1_megacap_rotation --no-cache` | completed in the build-lab copy after cherry-pick; all three aliases were stable-oracle with parse 1.00, score regret 0, accuracy 1.00, and modal `sec_tiger_e` | the runner-up diagnostic remains useful, but this rerun prevents overclaiming: Tiger is not yet a reliable tier separator. The next depth target is a trace where runner-up, value-drift, or filing-artifact ambiguity reproduces across fresh repeats. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_trace_raw --agents openai:mini --repeat 6 --case tiger_2026q1_megacap_rotation --no-cache --json` | completed in the build-lab copy after cherry-pick; `mini` choice counts were `sec_tiger_e:6`, parse 1.00, oracle-hit 1.00, primary mean 0, and all shortcut hit rates 0 | confirms the current Tiger trace is a diagnostic for runner-up attribution and stochastic reproducibility, not a solved live failure. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case split_adjustment_vs_discretionary_reduction --no-cache` | completed in the review copy; all three aliases were stable-oracle with parse 1.00, score regret 0, accuracy 1.00, and modal `sec_artifact_b` | the structured artifact-adjustment probe is solved live. Its value is diagnostic coverage: a future miss can now be attributed to raw artifact-blind share movement, value drift, percent change, or runner-up adjusted action. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_natural --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case split_adjustment_vs_discretionary_reduction --no-cache` | completed in the review copy; all three aliases were stable-oracle with parse 1.00, score regret 0, accuracy 1.00, and modal `sec_artifact_b` | removing the structured factor is still not enough to create a live failure. The next artifact-depth build should combine the artifact with ambiguous runner-up dollar actions, noisier notes, or multiple simultaneous corporate actions. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_natural --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case split_adjustment_vs_discretionary_reduction --no-cache` | completed in the build-lab copy after cherry-pick; all three aliases again stable-oracle with parse 1.00, score regret 0, accuracy 1.00, and modal `sec_artifact_b` | confirms the natural-note artifact probe is a validated diagnostic but not a current live tier separator. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case multi_artifact_close_runner_up --no-cache` | completed in the review copy; `mini` and `gpt-5.5` are stable-oracle with score regret 0; `nano` is unstable-non-oracle-modal with mean score regret 0.666667, accuracy 0.333333, primary range 1, and modal `sec_stress_f` matching `market_value` | combining multiple artifacts with a close runner-up reopens a live C1 gap. In this first run, `nano` collapses toward reported-value drift rather than the runner-up action. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents openai:nano --repeat 6 --case multi_artifact_close_runner_up --no-cache --json` | completed in the review copy; `nano` choice counts are `sec_stress_b:4`, `sec_stress_a:2`, parse 1.00, oracle-hit 0.666667, primary mean 0.333333, and the non-oracle choices match `artifact_blind` | the drilldown shows the live gap is stochastic and not a single fixed shortcut: a fresh run becomes oracle-modal but still has artifact-blind raw-share misses. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case multi_artifact_close_runner_up --no-cache` | completed in the build-lab copy after cherry-pick; `mini` and `gpt-5.5` are stable-oracle with score regret 0; `nano` is again unstable-non-oracle-modal with mean score regret 0.666667, accuracy 0.333333, primary range 1, but modal `sec_stress_a` now matches `artifact_blind` | confirms the live tier split is reproducible while the exact `nano` shortcut is not fixed: fresh repeats alternate between reported-value artifact drift and raw-share artifact blindness, so the next question is repeat reliability and shortcut-mixture attribution. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_stress --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 9 --case multi_artifact_close_runner_up --no-cache` | completed in the review copy after PR 118 choice-mix instrumentation; `mini` and `gpt-5.5` are stable-oracle with score regret 0; `nano` is unstable-oracle-modal with mean score regret 0.333333, accuracy 0.666667, oracle-hit 0.666667, non-oracle choice rate 0.333333, attributed non-oracle rate 1.00, and choice reference counts `artifact_blind:3` | the longer live drilldown answers the PR 117/118 question: the tier split persists, but the durable `nano` failure signal is artifact-blind raw-share movement, not runner-up confusion; the earlier market-value modal miss looks stochastic rather than the dominant shortcut on this case. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_implicit --agents openai:nano,openai:mini,openai:gpt-5.5 --repeat 3 --case multi_artifact_close_runner_up --no-cache` | completed in the review copy; `mini` is stable-oracle with score regret 0; `nano` is unstable-oracle-modal with mean score regret 0.333333 and one artifact-blind choice; `gpt-5.5` is unstable-oracle-modal with mean score regret 0.333333 and one market-value choice | removing artifact notes reopens the C1 artifact-inference gap beyond `nano`: the top alias can also miss when it has to infer the split-like adjustment from row patterns alone. |
| `AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli --sweep --task principal_holding_filing_artifact_implicit --agents openai:nano,openai:gpt-5.5 --repeat 6 --case multi_artifact_close_runner_up --no-cache` | completed in the review copy; `nano` is stable-oracle with score regret 0; `gpt-5.5` is unstable-oracle-modal with mean score regret 0.333333, accuracy 0.666667, oracle-hit 0.666667, non-oracle choice rate 0.333333, attributed non-oracle rate 1.00, and choice reference counts `market_value:2` | the follow-up prevents overclaiming a persistent `nano` gap on the implicit version, but strengthens the new result: no-note artifact inference can trigger reported-value-drift misses in `gpt-5.5`, so the next depth question is whether stronger implicit evidence or a real corporate-action trace restores top-alias stability. |
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

Checked on 2026-05-29 before writing this ledger and rechecked through
2026-05-30 before PR 106.

| Repo | Status | New/relevant commits checked | Consequence for private build lab |
|---|---|---|---|
| `/Users/lichenyu/agenteconreadiness` (`origin/main`) | clean at `74d7b21` on 2026-05-30 | `c3520ac` review corrections; `f69e883` OSS availability / borrow-substrate strategy; `a0e17b1` read-first refocus doc; `1e13623` RLHF appropriateness vs economic optimality theory; `d517c2e` oracle-availability and `(primitive x regime)` sharpening; `4a5b914` no-oracle evaluation and TERMS information-set resolution; `7cb0ca8` generator-verifier method, manufacturable-oracle correction, and bargaining-Bayes mechanism; `7761475` refocus de-redundancy; `18e60cc` proposal v0.4 floor→grade→diagnostic-lens reframe; `74d7b21` diagnostic-lens-across-environments first-mover wording | PR 29 implements the RLHF theory; PR 37 follows `d517c2e`; PR 39 follows `4a5b914`; PRs 41-42 implement the no-oracle/proper-scoring path; PR 44 implements the `7cb0ca8` bargaining-Bayes posterior-scaffold falsifier; PRs 45, 61, 62, and 63 implement generator-verifier relationship laws, broader holdouts, law-claim auditing, and a cross-domain pricing audit; PR 106 follows the v0.4 depth framing by measuring repeat reliability instead of adding case breadth |
| `/Users/lichenyu/persona_simulator` (`origin/master`) | dirty: modified `sprint/adversarial_scam_arena_toy/exploits.json`; untracked `.playwright-mcp/` logs; fetched at `1a6af5f` on 2026-05-30 | `47acd7a` GPT-5.x support/model override; `8404d2a` OpenAI scam-arena run; `c1fbbd0` borrow-substrate doc; `121e2e0` cross-model scam result + timeout/label fixes; `94fa606`/`efa26d6` mirror oracle-availability and no-oracle information-set methodology; `ae9c7b2` mirrors generator-verifier and bargaining-Bayes additions; `1a6af5f` points superseded pitch banner at proposal v0.4 | record upstream evidence only; do not import OpenRouter/chat-completions client into this Responses-only lab; PRs 44-45 and 61-62 use the mirrored `7cb0ca8` mechanisms without touching original dirty artifacts |

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
70. PR 98 replaces explicit recency weights with dated outcome-log batches and
    a recency horizon. Offline baselines expose raw-score, stale-window,
    pooled-history, and latest-only shortcuts; live `nano` now has small
    nonzero regret but still avoids the named shortcuts, so a harder successor
    should make the logs noisier or require inferring recency without the
    half-life hint.
71. PR 99 removes the printed half-life value and makes the dated logs thinner
    and uneven. Live `nano` regret increases versus PR 98 while named shortcut
    diagnostics stay at zero, suggesting the model handles the qualitative
    recency direction but loses precision when the time-decay policy is implicit.
72. PR 100 moves from pre-aggregated dated score bands to individual scored
    records with score-local and recency-local weighting. This produces the
    strongest rolling-calibration live gap so far and reintroduces named misses
    for raw-score, pooled-history, and latest-window shortcuts.
73. PR 101 adds operational policy/route context to the individual event-log
    calibration surface. Offline baselines now expose policy-blind and
    route-blind reference-class failures, and live `nano` shows small but
    nonzero policy/route miss rates. Because the live gap is smaller than PR
    100, the next calibration frontier should either make operational context
    less explicitly labeled or move toward the high-stakes predict-then-validate
    grade instrument rather than adding more obvious metadata fields.
74. PR 102 starts the high-stakes grade direction with a synthetic
    predict-the-principal holding-change task. Offline baselines confirm the
    target is not market return, low turnover, or a generic style; live `nano`
    solves the clean histories, so the next C1 build should add the documented
    inversion problem: mechanical flows, index rebalancing, tax-loss trades, or
    noisy real 13F-derived histories.
75. PR 103 adds that inversion-problem surface with explicit event-type labels
    for discretionary versus mechanical filing rows. Offline baselines now
    expose mechanical-flow overfitting, but live `nano` still solves the task;
    the next C1 step should remove explicit labels, convert them to ambiguous
    filing notes, or move to real-derived 13F histories.
76. PR 104 removes the explicit event-type labels and replaces them with
    filing-note strings. This preserves the offline mechanical-flow diagnostic,
    but live `nano` still solves all four cases, so the next C1 step should use
    conflicting/raw note language or real-derived holdings histories rather than
    clearer synthetic notes.
77. PR 105 neutralizes the remaining principal/profile/security labels and
    collapses discretionary notes into generic raw PM packets. This changes C1
    from saturated to sample-unstable, so the immediate question is not breadth
    of cases; it is whether a fresh live run is repeat-reliable under label
    removal.
78. PR 106 adds that repeat-reliability measurement. The stability probe
    confirms the first blind C1 case can flip across three fresh `nano` calls
    while preserving parse, so single-run live success should not be treated as
    saturation evidence. C1 should now move toward real-derived traces and
    repeat/stability reporting, not more synthetic label variants.
79. PR 107 adds target-margin diagnostics to the C1 holding-prediction family.
    The first blind C1 instability appears at oracle margin 0.1767 and the
    full blind set has minimum margin 0.1735, so the observed live flip is not
    explained away as a near-tie. The next C1 step should stress real-derived
    filing traces or repeated live stability, not more hand-written cases.
80. PR 108 adds case-outcome attribution to repeat stability. The full live
    blind C1 repeat shows three stable-oracle cases and one
    unstable-non-oracle-modal case, with parse stable throughout. That makes
    the next question narrower: why does `pension_outflow_quality_signal`
    drift toward the mechanical-flow trade under label-blind notes, and does
    that failure survive real-derived 13F traces?
81. PR 109 attributes stability modal choices to named non-oracle references.
    The live blind C1 wrong-modal case is now machine-labeled as matching both
    the low-turnover and mechanical-flow references. That narrows the C1 failure
    hypothesis from generic instability to a flow/turnover shortcut under
    label-blind filing notes.
82. PR 110 turns repeat stability into a cross-agent sweep. The first alias
    probe on the pension C1 case shows `mini` taking the flow/turnover shortcut
    while `nano` and `gpt-5.5` remain stable-oracle across two fresh calls. This
    gives the build lab a cheap way to ask whether a depth failure is
    model-specific before spending on full-case repeats.
83. PR 111 adds per-case drilldown to the stability sweep report. This keeps the
    C1 work on the depth track: every cross-agent result now points back to the
    exact case, modal choice, oracle margin, and shortcut references that raised
    the question. The next useful C1 spend is full-case live alias stability or
    real-derived filing traces, not a larger synthetic case list.
84. The first full-case live alias stability sweep confirms that the C1 issue is
    capability-sensitive rather than a generic benchmark flaw. `gpt-5.5` is
    stable-oracle across all four blind-note cases; `nano` is correct on three
    cases but remains sampling-unstable on the pension flow case; `mini` is
    shortcut-driven across the whole set. That makes the uncovered direction
    narrower: test realistic filing-derived traces and repeat reliability by
    model tier before adding any new hand-written C1 scenarios.
85. PR 112 adds keyed case targeting. The important operational change is that
    follow-up probes can now name `pension_outflow_quality_signal` directly
    with `--case`, so the C1 depth loop can re-test the discovered failure
    across models and repeats without relying on ordering (`--limit 1`) or
    adding more scenarios.
86. The first keyed live pension-case repeat keeps the same tier split: `gpt-5.5`
    is stable-oracle, `nano` is unstable but oracle-modal, and `mini` is
    unstable with a non-oracle flow/turnover modal. That makes the next C1
    question even narrower: does this inversion failure persist when the same
    trace format is populated from actual 13F-derived filing rows?
87. PR 113 begins that real-derived trace path with one public SEC 13F-HR
    sequence instead of another synthetic case. The point is depth, not breadth:
    the uncovered direction is whether models separate a dollar-material
    share-driven principal action from market-value drift, no-change turnover,
    large-position salience, and previous-quarter trend when the rows are actual filings. The
    next questions raised by this result are model-tier stability on the real
    trace, whether the same shortcut taxonomy explains live misses, and how much
    quarterly 13F noise limits predict-the-principal fidelity even when the
    scoring target is a disclosed action rather than market performance.
88. The first live PR 113 alias sweep is stable-oracle for `nano`, `mini`, and
    `gpt-5.5` on the Berkshire trace. That should not be read as C1 saturation:
    it says this particular real filing sequence has a large share-action margin
    and clean enough evidence for all aliases. The next real-derived step should
    search for filing sequences with actual ambiguity, such as apparent
    fund-flow/turnover noise, corporate-action-like share changes, partial exits
    across adjacent quarters, or value drift that competes with a smaller
    material action, then reuse the same keyed stability and shortcut-attribution
    reporting.
89. PR 114 removes the precomputed candidate-change table before searching for
    more public filing traces. This is a depth control: if the same real-derived
    trace only works when share deltas are already packaged as candidate fields,
    the benchmark would be measuring scaffold use rather than filing-trace
    inference. The raw-row oracle and shortcut baselines preserve the PR 113
    result while shifting the model-visible problem to period-row comparison.
90. The first raw-row live probes exposed the first useful PR 114 question:
    smaller aliases could choose `sec_constellation`, the largest percentage
    share reduction, instead of `sec_chevron`, the largest approximate dollar
    value of share-count change. PR 114 therefore adds `percent_change` as a
    named shortcut baseline and tightens the target wording to dollar-material
    action. The clarified raw repeat sweep is stable-oracle for `nano`, `mini`,
    and `gpt-5.5`, so the open direction is not case count; it is whether real
    filing traces can be found where percent-change salience, reported-value
    drift, mechanical filing artifacts, or quarterly disclosure noise still
    break predict-the-principal fidelity under the same explicit objective.
91. PR 115 follows that depth criterion with one targeted Tiger Global trace
    found by SEC-source search because its oracle is distinct from
    percent-change, market-value, max-position, no-change turnover, previous
    trend, and runner-up dollar-action references. This is not a breadth move:
    the value is that the first `mini` review-copy live run produced exactly
    the named second-best near miss, while the build-lab repeat-3 and repeat-6
    reruns were stable-oracle. The next C1 question is now narrower again:
    distinguish true shortcut collapse from non-reproducible runner-up flips,
    and test whether richer filing artifacts create stable non-oracle modes
    rather than occasional near-miss samples.
92. PR 116 follows the filing-artifact branch rather than adding count breadth.
    It adds a split-adjusted filing trace plus a natural-note variant where the
    same raw rows can support four wrong explanations: unadjusted artifact-blind
    share movement, reported-value drift, percentage-change salience, and the
    runner-up adjusted action. Offline baselines validate the diagnostic, but
    live `nano`, `mini`, and `gpt-5.5` solve both structured and natural-note
    versions. The resulting question is sharper: the current artifact evidence
    is too clean, so the next useful C1 artifact probe should combine corporate
    actions with runner-up ambiguity, multiple simultaneous artifacts, or weaker
    natural notes instead of adding more clean split examples.
93. PR 117 implements that composite artifact stressor: two natural-note split
    artifacts, a value-drift distractor, a percentage-change distractor, and a
    close second-best discretionary action under the same adjusted
    dollar-material objective. This is again a depth move, not breadth. It
    creates a live tier signal: `mini` and `gpt-5.5` are stable-oracle on the
    first stress sweep, while `nano` is unstable. The exact `nano` shortcut is
    stochastic across fresh repeats: one review run is non-oracle-modal on the
    market-value artifact, the longer drilldown is oracle-modal with two
    artifact-blind raw-share misses, and the build-lab repeat-3 rerun is
    non-oracle-modal on the artifact-blind split row. That narrows the next
    question to repeat reliability and shortcut-mixture attribution, not more
    clean artifact cases.
94. PR 118 implements the attribution half of that question without adding a
    new benchmark case. Existing modal reference labels are still the headline
    readout, but stability summaries now also aggregate choice-level reference
    hits across every repeat. This matters for PR 117-style results: an
    oracle-modal run can still contain artifact-blind misses, and two fresh
    non-oracle-modal runs can disagree on whether the modal shortcut is
    artifact blindness or reported-value drift. The new choice mix reports
    non-oracle choice rate, attributed non-oracle choice rate, multi-reference
    case rate, and per-reference hit counts so the next live C1 drilldowns can
    measure shortcut mixtures directly instead of inferring them by hand.
95. PR 119 uses the PR 118 instrument on the exact PR 117 stress case rather
    than adding another case. In a repeat-9 OpenAI sweep, `mini` and `gpt-5.5`
    remain stable-oracle, while `nano` becomes oracle-modal but still misses
    3/9 times. All non-oracle `nano` choices hit the artifact-blind split row;
    no runner-up or market-value hits appear in this longer run. That changes
    the next C1 question: the current persistent failure is raw corporate-action
    artifact blindness under noisy natural notes, not simply generic
    value-drift salience or close-runner-up confusion.
96. PR 120 asks the next narrower question by removing the artifact-note channel
    from the same composite stress fixture. The implicit prompt tells agents to
    infer split-like artifacts from raw row patterns, while the offline oracle
    uses common integer split ratios to preserve the same mechanical target and
    shortcut baselines. The first live repeat-3 shows `mini` solving, `nano`
    making one artifact-blind miss, and `gpt-5.5` making one market-value miss;
    the repeat-6 follow-up has `nano` solving and `gpt-5.5` still missing twice
    toward market value. This makes implicit corporate-action inference a real
    high-end stressor, not just a small-model artifact-blindness issue. The
    next question is evidence-channel specific: do models need stronger row
    ratio evidence, value-stability evidence, real corporate-action context, or
    longer filing history before they stop treating raw reported values as the
    principal's discretionary signal?
97. PR 121 follows that evidence-channel question rather than adding breadth.
    It keeps the no-note row-ratio setup and the close runner-up, but makes the
    split-like artifact rows internally value-stable. That turns the PR 120
    ambiguity into a controlled ablation. The live repeat-3 control is
    stable-oracle for `nano`, `mini`, and `gpt-5.5`, and the repeat-6
    `nano`/`gpt-5.5` follow-up also stays stable-oracle. The previous top-alias
    miss is therefore not caused by missing artifact notes alone; it appears
    when no-note row-ratio evidence conflicts with reported-value movement.
