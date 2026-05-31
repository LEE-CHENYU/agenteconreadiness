# AERead build lab

This copy contains a runnable research scaffold for the current AERead direction.
It is deliberately small and judge-free: task generators expose symbolic ground
truth to the harness, model-visible prompts do not expose oracle answers,
scoring is mechanical, and live API use is restricted to OpenAI model aliases
only.

Current source-doc alignment: the 2026-05-30 refocus/methodology sharpening says
saturation is a `(primitive x regime)` property and tracks oracle availability
under stress, not agent count. Where omniscient optima are not a fair agent bar,
the lab scores against accessible posterior/control targets, local oracles,
proper scoring, bounds, and revealed-preference fit.

## What is implemented

| Build | Why it matters | Command |
|---|---|---|
| `regime` | Four-regime utility battery across even-money, skewed, thin-edge, negative-EV, and hard-barrier gamble families: EV single-shot, Kelly compounding, CVaR under ruin, configured-principal CRRA. This is the re-centered regime-appropriateness axis. | `python -m aeread_lab.cli --task regime --agent offline:oracle` |
| `regime_relationship` | Generator-verifier prototype for regime laws: procedurally generated gambles must satisfy EV >= Kelly, Kelly >= CVaR, and Kelly >= CRRA while also matching oracle fractions closely enough to catch degenerate relationship-only answers. | `python -m aeread_lab.cli --task regime_relationship --agent offline:oracle` |
| `regime_holdout` | Generated holdout regime-law family: broader gamble shapes reuse the same relationship laws but require fresh fit to the EV, Kelly, CVaR, and CRRA fractions instead of memorized fixture patterns. | `python -m aeread_lab.cli --task regime_holdout --agent offline:oracle` |
| `regime_law_audit` | Generated law-audit verifier: classify proposed EV/Kelly/CVaR/CRRA relationship claims as valid or invalid for generated gambles, measuring invalid-law acceptance separately from numeric fit. | `python -m aeread_lab.cli --task regime_law_audit --agent offline:oracle` |
| `alignment_tax` | RLHF-appropriateness probe: all listed actions are compliant, but the helpful/customer-approved default can sacrifice configured economic value. | `python -m aeread_lab.cli --task alignment_tax --agent offline:oracle` |
| `principal_inference` | Grade-side revealed-preference task: infer a principal's CRRA risk parameter from prior choices before allocating in a new scenario. | `python -m aeread_lab.cli --task principal_inference --agent offline:oracle` |
| `portfolio` | Multi-asset configured-principal allocation: choose portfolios using CRRA-style variance, tail risk, concentration, and mandate-fit terms. | `python -m aeread_lab.cli --task portfolio --agent offline:oracle` |
| `revealed_allocation` | Stylized 13F-style revealed-preference allocation: infer risk preference from historical portfolio choices, then output continuous target weights. | `python -m aeread_lab.cli --task revealed_allocation --agent offline:oracle` |
| `principal_holding_prediction` | Predict-the-principal 13F-style holding-change task: infer a named principal's revealed trade style from prior disclosures and predict the next disclosed trade, scoring fidelity rather than market return. | `python -m aeread_lab.cli --task principal_holding_prediction --agent offline:oracle` |
| `principal_holding_prediction_noisy` | Noisy predict-the-principal holding-change task: separate discretionary 13F-style choices from mechanical fund-flow, index-rebalance, redemption, and tax-loss rows before predicting the next disclosed discretionary trade. | `python -m aeread_lab.cli --task principal_holding_prediction_noisy --agent offline:oracle` |
| `principal_holding_prediction_notes` | Filing-note predict-the-principal task: infer which 13F-style rows reflect manager intent versus outside cash, benchmark, risk-ticket, or year-end bookkeeping artifacts without explicit event-type labels. | `python -m aeread_lab.cli --task principal_holding_prediction_notes --agent offline:oracle` |
| `principal_holding_prediction_blind_notes` | Blind filing-note predict-the-principal task: neutralize account/profile/security labels and use generic raw notes to test whether C1 performance depends on label shortcuts rather than revealed-style inference. | `python -m aeread_lab.cli --task principal_holding_prediction_blind_notes --agent offline:oracle` |
| `principal_holding_filing_trace` | Real-derived C1 filing trace: populate a neutralized predict-the-principal task from public SEC 13F-HR rows and test dollar-material share-driven action against market-value drift, low-turnover, max-position, previous-trend, and percent-change shortcuts. | `python -m aeread_lab.cli --task principal_holding_filing_trace --agent offline:oracle` |
| `principal_holding_filing_trace_raw` | Raw-row real-derived C1 filing trace: remove the precomputed candidate-change table and require the same dollar-material share-action inference directly from neutralized SEC filing rows. | `python -m aeread_lab.cli --task principal_holding_filing_trace_raw --agent offline:oracle` |
| `ambiguity` | Knightian uncertainty task: maxmin and alpha-maxmin choice across plausible priors, with optional signal updates instead of collapsing to one reference prior. | `python -m aeread_lab.cli --task ambiguity --agent offline:oracle` |
| `bargaining` | D2/TERMS-style gate+grade wrapper: generic seller surplus extraction vs configured-principal surplus sharing across take-it-or-leave-it, alternating-offer, and hidden-reservation cases. | `python -m aeread_lab.cli --task bargaining --agent offline:oracle` |
| `belief_bargaining` | TERMS-style cue use and belief calibration: update buyer WTP beliefs from one-shot cues, multi-turn signal sequences, and strategic cheap-talk likelihoods before pricing; paired scaffold prompts externalize posterior state. | `python -m aeread_lab.cli --task belief_bargaining --agent offline:oracle` |
| `belief_bargaining_interaction` | Two-offer belief bargaining: choose an opening price and fallback price after rejection, using observed signals and the fact that rejection updates buyer WTP beliefs. | `python -m aeread_lab.cli --task belief_bargaining_interaction --agent offline:oracle` |
| `market` | Market-Bench-style price competition plus inventory-survival pricing: competitive Nash pricing vs collusive/high-price drift, liquidation, and reserve-aware inventory pricing. | `python -m aeread_lab.cli --task market --agent offline:oracle` |
| `market_policy_shift` | Repeated-market opponent-policy shift: infer a competitor's next price from observed price history and choose the current best response instead of reusing static Nash or last-period behavior. | `python -m aeread_lab.cli --task market_policy_shift --agent offline:oracle` |
| `market_policy_inventory` | Inventory-constrained opponent-policy adaptation: infer the competitor's next price, then choose a non-collusive posted price that maximizes terminal cash across finite inventory, holding costs, obligations, and reserve constraints. | `python -m aeread_lab.cli --task market_policy_inventory --agent offline:oracle` |
| `market_trace_inventory` | Trace-based inventory pricing: infer competitor next price from observed price, fill-rate, and remaining-stock rows before optimizing finite-inventory terminal cash. | `python -m aeread_lab.cli --task market_trace_inventory --agent offline:oracle` |
| `market_trace_markdown` | Trace-based staged inventory pricing: infer competitor next price from market trace rows, then choose early and late prices across the inventory horizon. | `python -m aeread_lab.cli --task market_trace_markdown --agent offline:oracle` |
| `market_trace_replenishment` | Trace-based replenishment planning: infer competitor next price from market trace rows, then choose early/late prices and whether to buy inventory before the late window. | `python -m aeread_lab.cli --task market_trace_replenishment --agent offline:oracle` |
| `market_trace_replenishment_natural` | Natural-label trace replenishment planning: preserve the same price/order oracle while presenting rival shelf observations, cash floors, and restock limits in business language. | `python -m aeread_lab.cli --task market_trace_replenishment_natural --agent offline:oracle` |
| `market_trace_replenishment_noisy` | Noisy trace replenishment planning: infer rival next price from lumpy regional shelf observations, then choose early/late prices and restock units under cash and storage limits. | `python -m aeread_lab.cli --task market_trace_replenishment_noisy --agent offline:oracle` |
| `matching` | Matching-market design: choose stable/access-aware matching rules instead of value-only assignments with blocking-pair risk. | `python -m aeread_lab.cli --task matching --agent offline:oracle` |
| `screening` | Adverse-selection contract screening: choose incentive-compatible/participation-safe menus instead of profit-only menus. | `python -m aeread_lab.cli --task screening --agent offline:oracle` |
| `moral_hazard` | Hidden-action contract design: choose incentive contracts that actually induce effort instead of assuming first-best effort for free. | `python -m aeread_lab.cli --task moral_hazard --agent offline:oracle` |
| `auction` | Mechanism-design reserve task: Myerson revenue reserve vs welfare/access reserves under configured objectives. | `python -m aeread_lab.cli --task auction --agent offline:oracle` |
| `common_value` | Winner's-curse auction guardrail: condition on winning as adverse information instead of bidding from a private signal as if it were private value. Live smoke: smaller OpenAI models miss; `gpt-5.5` solves. | `python -m aeread_lab.cli --task common_value --agent offline:oracle` |
| `mechanism` | Mechanism-choice task: choose among auction/allocation rules using configured principal weights, strategic-risk penalties, and incentive-compatibility checks. | `python -m aeread_lab.cli --task mechanism --agent offline:oracle` |
| `mechanism_repeated` | Repeated mechanism-choice task: optimize total configured score across retention, manipulation growth, and review costs instead of first-period revenue. | `python -m aeread_lab.cli --task mechanism_repeated --agent offline:oracle` |
| `mechanism_repeated_natural` | Natural-label repeated mechanism-choice task: preserve the same repeated-program oracle while hiding explicit revenue/manipulation field names behind pilot-outcome labels. | `python -m aeread_lab.cli --task mechanism_repeated_natural --agent offline:oracle` |
| `mechanism_participant_response` | Participant-response mechanism task: simulate active participant counts as high take rates and gaming pressure erode retention over repeated program periods. | `python -m aeread_lab.cli --task mechanism_participant_response --agent offline:oracle` |
| `mechanism_elasticity_inference` | Hidden-elasticity mechanism task: infer retention sensitivity from pilot stay-rate observations before simulating participant response. | `python -m aeread_lab.cli --task mechanism_elasticity_inference --agent offline:oracle` |
| `mechanism_strategic_response` | Multi-agent strategic-response mechanism task: simulate strategic participant share under peer contagion, audit deterrence, manipulation harm, and retention loss. | `python -m aeread_lab.cli --task mechanism_strategic_response --agent offline:oracle` |
| `mechanism_strategic_equilibrium` | Strategic-equilibrium mechanism task: solve the self-consistent strategic participant share before valuing the repeated program. | `python -m aeread_lab.cli --task mechanism_strategic_equilibrium --agent offline:oracle` |
| `mechanism_interaction_trace` | Interaction-trace mechanism task: project future participant counts and strategic share from observed pilot traces before choosing the remaining program mechanism. | `python -m aeread_lab.cli --task mechanism_interaction_trace --agent offline:oracle` |
| `mechanism_trace_equilibrium` | Trace-equilibrium mechanism task: infer the last pilot state and trace momentum, then solve the self-consistent strategic share before valuing the future program. | `python -m aeread_lab.cli --task mechanism_trace_equilibrium --agent offline:oracle` |
| `mechanism_trace_equilibrium_natural` | Natural-label trace-equilibrium mechanism task: preserve the same trace/equilibrium oracle while hiding the strategic-response field names behind pilot outcome language. | `python -m aeread_lab.cli --task mechanism_trace_equilibrium_natural --agent offline:oracle` |
| `mechanism_trace_equilibrium_noisy` | Noisy trace-equilibrium mechanism task: preserve the same strategic-share oracle while presenting lumpy local pilot sheets instead of clean interaction traces. | `python -m aeread_lab.cli --task mechanism_trace_equilibrium_noisy --agent offline:oracle` |
| `strategic_drift` | γ-Bench-style repeated strategic discipline: preserve long-horizon relationship value under deterministic, imperfect-information, and N-player stress instead of drifting to myopic grabs. | `python -m aeread_lab.cli --task strategic_drift --agent offline:oracle` |
| `forecast_calibration` | No-oracle-style probability calibration: combine base rates, likelihood-ratio signals, and reliability-weighted evidence, then score forecasts with proper Brier/log-loss metrics against realized outcome frequencies. | `python -m aeread_lab.cli --task forecast_calibration --agent offline:oracle` |
| `forecast_aggregate` | Aggregate-bin calibration stress: recalibrate raw model scores from observed bin outcomes with empirical-Bayes shrinkage, catching both raw-score reuse and no-shrink small-bin overreaction. | `python -m aeread_lab.cli --task forecast_aggregate --agent offline:oracle` |
| `forecast_curve` | Held-out calibration-curve stress: shrink historical bins and interpolate to a new raw score, catching raw-score reuse and nearest-bin shortcuts. | `python -m aeread_lab.cli --task forecast_curve --agent offline:oracle` |
| `forecast_curve_implicit` | Implicit held-out calibration-curve stress: use the same scoring target as `forecast_curve` but present the table without the explicit shrink/interpolate recipe. | `python -m aeread_lab.cli --task forecast_curve_implicit --agent offline:oracle` |
| `forecast_curve_noisy` | Dense/noisy implicit calibration-curve stress: use larger non-monotone holdout tables with sparse bins, testing raw-score reuse and nearest-row shortcuts under sample-size noise. | `python -m aeread_lab.cli --task forecast_curve_noisy --agent offline:oracle` |
| `forecast_curve_natural` | Natural-label calibration-curve stress: present the dense/noisy table with outcome-row labels instead of machine-readable calibration terms. | `python -m aeread_lab.cli --task forecast_curve_natural --agent offline:oracle` |
| `forecast_shift_calibration` | Cohort-shift calibration stress: combine a source-cohort score curve with a small target-cohort bridge sample, catching raw-score reuse, source-curve-only reuse, and nearest-bridge shortcuts. | `python -m aeread_lab.cli --task forecast_shift_calibration --agent offline:oracle` |
| `forecast_rolling_calibration` | Rolling time-local calibration stress: combine successive calibration windows with recency weights, catching raw-score reuse, stale-window reuse, and pooled-history shortcuts. | `python -m aeread_lab.cli --task forecast_rolling_calibration --agent offline:oracle` |
| `forecast_rolling_log_calibration` | Natural time-log calibration stress: infer a recency-weighted score calibration from dated outcome batches, catching raw-score reuse, stale-window reuse, pooled-history shortcuts, and newest-batch overreaction. | `python -m aeread_lab.cli --task forecast_rolling_log_calibration --agent offline:oracle` |
| `forecast_rolling_log_noisy` | Noisy implicit time-log calibration stress: infer recency-weighted calibration from uneven dated score bands without a printed half-life value, catching raw-score reuse, stale-window reuse, pooled-history shortcuts, and newest-batch overreaction. | `python -m aeread_lab.cli --task forecast_rolling_log_noisy --agent offline:oracle` |
| `forecast_event_log_calibration` | Item-level event-log calibration stress: infer recency-weighted, score-local calibration from dated individual scored records instead of pre-aggregated bins. | `python -m aeread_lab.cli --task forecast_event_log_calibration --agent offline:oracle` |
| `forecast_operational_log_calibration` | Operational-context event-log calibration stress: infer recency-weighted, score-local calibration from individual records while filtering to the current policy and route instead of pooling superficially similar logs. | `python -m aeread_lab.cli --task forecast_operational_log_calibration --agent offline:oracle` |
| `exploration` | EconEvals-style unknown-environment learning: decide when information value justifies a pilot before deployment. | `python -m aeread_lab.cli --task exploration --agent offline:oracle` |
| `experiment_design` | Imperfect-signal experiment design: choose whether and how to run one-step or adaptive two-step noisy experiments before deployment, then update by Bayes rule. | `python -m aeread_lab.cli --task experiment_design --agent offline:oracle` |
| `retail` | Vending-Bench-style inventory/runway management: one-cycle and multi-period demand paths with carrying costs, terminal salvage, and reserve checks at every period. | `python -m aeread_lab.cli --task retail --agent offline:oracle` |
| `procurement` | v0 `ProductProcurementGame`: discrete-action qualitative procurement with a utility-vector oracle. | `python -m aeread_lab.cli --task procurement --agent offline:oracle` |
| `procurement_counterfactual` | Procurement paraphrase and preference-flip probe: the same products preserve the oracle under wording changes but require a different choice when the principal's weights change. | `python -m aeread_lab.cli --task procurement_counterfactual --agent offline:oracle` |
| `procurement_bundle` | Combinatorial procurement bundle choice: pick exactly two products under budget and category coverage, adding pairwise compatibility to item utility. | `python -m aeread_lab.cli --task procurement_bundle --agent offline:oracle` |
| `procurement_bundle_natural` | Natural-label procurement bundle choice: same two-product oracle as `procurement_bundle`, but product rows use SKU/package-fit language instead of explicit compatibility-bonus labels. | `python -m aeread_lab.cli --task procurement_bundle_natural --agent offline:oracle` |
| `procurement_bundle_evidence` | Outcome-evidence procurement bundle choice: infer two-SKU package fit from prior deployment rows rather than listed compatibility bonuses. | `python -m aeread_lab.cli --task procurement_bundle_evidence --agent offline:oracle` |
| `procurement_bundle_noisy_evidence` | Noisy outcome-evidence bundle choice: aggregate multiple conflicting deployment rows per SKU pair before selecting the two-product package. | `python -m aeread_lab.cli --task procurement_bundle_noisy_evidence --agent offline:oracle` |
| `procurement_bundle_history` | Deployment-history bundle choice: aggregate multi-period rollout history through an operational field-value conversion before selecting the two-product package. | `python -m aeread_lab.cli --task procurement_bundle_history --agent offline:oracle` |
| `procurement_bundle_reserve` | Reserve-sensitive bundle choice: combine item priorities with support-tail cost and reserve shortfall before selecting the two-product package. | `python -m aeread_lab.cli --task procurement_bundle_reserve --agent offline:oracle` |
| `procurement_vendor_update` | Sequential vendor-update procurement: choose a three-round vendor plan after delivery-history updates, switch costs, and reserve-floor penalties. | `python -m aeread_lab.cli --task procurement_vendor_update --agent offline:oracle` |
| `procurement_vendor_update_noisy` | Noisy sequential vendor-update procurement: infer delivery reliability from lumpy receiving-ledger rows before choosing the three-round vendor plan under switch costs and reserve-floor penalties. | `python -m aeread_lab.cli --task procurement_vendor_update_noisy --agent offline:oracle` |
| `pricing` | v0 `SimplePricingGame`: continuous price choice with base/posterior/reveal conditions and a closed-form revenue oracle. | `python -m aeread_lab.cli --task pricing --agent offline:oracle` |
| `pricing_counterfactual` | Pricing evidence-perturbation probe: exact and noisy posterior demand evidence changes the revenue-maximizing price, and stale base prices are scored as counterfactual-shift misses. | `python -m aeread_lab.cli --task pricing_counterfactual --agent offline:oracle` |
| `pricing_cross_elasticity` | Cross-product pricing evidence: fit focal demand from own-price and related-price variation, catching single-product fits that ignore substitution or complement effects. | `python -m aeread_lab.cli --task pricing_cross_elasticity --agent offline:oracle` |
| `pricing_multi_product` | Joint multi-product pricing: fit two cross-demand equations and choose both prices together, catching independent single-product pricing under substitution or complement effects. | `python -m aeread_lab.cli --task pricing_multi_product --agent offline:oracle` |
| `pricing_multi_product_natural` | Natural-label joint pricing: use campaign outcome rows without the explicit demand-equation recipe while preserving the same two-price oracle. | `python -m aeread_lab.cli --task pricing_multi_product_natural --agent offline:oracle` |
| `pricing_multi_product_capacity` | Capacity-constrained joint pricing: choose two cross-demand prices with finite stock caps, catching unconstrained joint pricing that over-demands available inventory. | `python -m aeread_lab.cli --task pricing_multi_product_capacity --agent offline:oracle` |
| `pricing_multi_product_capacity_noisy` | Noisy capacity-constrained joint pricing: fit cross-demand from lumpy regional two-product sales rows, then choose finite-stock prices instead of unconstrained or independent prices. | `python -m aeread_lab.cli --task pricing_multi_product_capacity_noisy --agent offline:oracle` |
| `pricing_inventory_markdown` | Sequential markdown pricing: choose early and late prices for one shared inventory pool, catching myopic single-period pricing that sells through stock before the later window. | `python -m aeread_lab.cli --task pricing_inventory_markdown --agent offline:oracle` |
| `pricing_inventory_markdown_noisy` | Noisy sequential markdown pricing: infer launch and clearance demand from lumpy regional rows before choosing prices for one shared stock pool. | `python -m aeread_lab.cli --task pricing_inventory_markdown_noisy --agent offline:oracle` |
| `pricing_multi_product_markdown_noisy` | Noisy two-product sequential markdown pricing: infer cross-demand in launch and clearance windows, then choose four prices under product-specific stock, depletion, and liquidation floors. | `python -m aeread_lab.cli --task pricing_multi_product_markdown_noisy --agent offline:oracle` |
| `pricing_inventory_replenishment_noisy` | Noisy sequential replenishment pricing: infer launch and clearance demand, then choose launch price, mid-campaign restock quantity, and clearance price under setup cost, unit cost, storage capacity, and liquidation value. | `python -m aeread_lab.cli --task pricing_inventory_replenishment_noisy --agent offline:oracle` |
| `pricing_hidden_intervention` | Hidden-intervention pricing: remove fixed intervention units and exposure multipliers from observed sales before fitting normal demand and choosing the next campaign price. | `python -m aeread_lab.cli --task pricing_hidden_intervention --agent offline:oracle` |
| `pricing_law_audit` | Cross-domain generator-verifier audit for pricing: classify generated comparative-static claims about the revenue-maximizing price as valid or invalid under demand and cap changes. | `python -m aeread_lab.cli --task pricing_law_audit --agent offline:oracle` |
| `pricing_evidence_law_audit` | Evidence-derived pricing-law audit: classify price-movement claims from baseline and updated sales rows, without exposing alpha/beta demand parameters. | `python -m aeread_lab.cli --task pricing_evidence_law_audit --agent offline:oracle` |
| `pricing_evidence_law_holdout` | Generated evidence-law holdout: a larger neutral-ID family of sales-row pricing-law claims with intercept, slope, cap, mixed, and intervention cases. | `python -m aeread_lab.cli --task pricing_evidence_law_holdout --agent offline:oracle` |
| `scam` | Adversarial belief-manipulation arena: scam-supplier style value inflation with credulous and skeptical controls. | `python -m aeread_lab.cli --task scam --agent offline:careful --attacker offline:credulous` |
| `supplier_scam` | Long-horizon supplier-scam stress: repeated restocking under cash/runway constraints, where inflated claims, delayed-inventory lockups, and degraded supplier reputation must be discounted. | `python -m aeread_lab.cli --task supplier_scam --agent offline:oracle` |
| `supplier_scam_natural` | Natural-label supplier stress: same long-horizon trust/cash oracle as `supplier_scam`, but vendor rows use business-language risk, audit, timing, and delivery-history labels. | `python -m aeread_lab.cli --task supplier_scam_natural --agent offline:oracle` |

## OpenAI-only API path

The only live API adapter is `aeread_lab.models.OpenAIResponsesAgent`. It accepts
only these aliases:

- `gpt-5.5`
- `mini` (defaults to `gpt-5.4-mini`; override with `AEREAD_OPENAI_MODEL_MINI`)
- `nano` (defaults to `gpt-5.4-nano`; override with `AEREAD_OPENAI_MODEL_NANO`)

Example:

```bash
OPENAI_API_KEY=... python -m aeread_lab.cli --task regime --agent openai:nano
```

Run the full OpenAI-only model sweep with:

```bash
OPENAI_API_KEY=... python -m aeread_lab.cli --sweep --task all \
  --agents openai:gpt-5.5,openai:mini,openai:nano
```

There is no Anthropic/OpenRouter path in this build lab.

The adapter uses low reasoning effort, low text verbosity, `store=false`, and a
4096-token output budget by default. Set `AEREAD_OPENAI_MAX_OUTPUT_TOKENS` for
longer live stress prompts. It raises on incomplete or textless responses
instead of silently scoring blank model outputs.

## Sweep runner and cache

The sweep runner compares agents on the primary mechanical metric for each task:
it also reports `parse`, the fraction of trials with a valid task-specific
`FINAL_*` answer. Treat low parse rate as an eval-format failure before
interpreting the economic metric.

- `regime`: lower mean absolute error to the regime-correct oracle is better.
- `regime_relationship`: lower mean absolute error is the primary fit signal;
  relationship-law violation, fit-fail, and combined fail rates are reported
  separately.
- `regime_holdout`: lower mean absolute error is the primary generated-holdout
  fit signal; relationship-law violation and fit-fail rates are reported
  separately to catch law-only but numerically wrong answers.
- `regime_law_audit`: higher valid/invalid law-classification accuracy is
  better; invalid-law acceptance and valid-law rejection rates are reported
  separately.
- `alignment_tax`: lower configured-objective regret is better; overconcession
  and helpful-default match rates are reported separately.
- `principal_inference`: lower fraction error to the revealed-principal oracle
  is better; generic-gamma gap is reported separately.
- `portfolio`: lower configured-principal utility regret is better; max-return
  and low-risk miss rates are reported separately.
- `revealed_allocation`: lower utility regret and lower weight L1 error to the
  revealed-principal allocation are better.
- `principal_holding_prediction`: lower score regret to the inferred
  principal-style next holding change is better; accuracy, market-return miss,
  low-turnover miss, generic-style miss rates, and oracle target margin are
  reported separately.
- `principal_holding_prediction_noisy`: lower score regret to the inferred
  discretionary principal-style next holding change is better; market-return,
  low-turnover, generic-style, mechanical-flow miss rates, and oracle target
  margin are reported separately.
- `principal_holding_prediction_notes`: lower score regret to the inferred
  discretionary principal-style next holding change is better; the prompt hides
  event-type labels behind filing notes, and the same shortcut miss rates plus
  oracle target margin are reported separately.
- `principal_holding_prediction_blind_notes`: lower score regret to the inferred
  discretionary principal-style next holding change is better after neutralizing
  account/profile/security labels; the same shortcut miss rates plus oracle
  target margin are reported separately.
- `principal_holding_filing_trace`: lower score regret to the dollar-material
  share-driven action in public SEC-derived filing rows is better; accuracy,
  market-value-drift, low-turnover, max-position, previous-trend,
  percent-change miss rates, and oracle target margin are reported separately.
- `principal_holding_filing_trace_raw`: lower score regret to the dollar-material
  share-driven issuer in public SEC-derived rows is better after removing the
  candidate-change scaffold; the same shortcut miss rates and oracle target
  margin are reported separately.
- `ambiguity`: lower configured ambiguity regret is better; reference-prior,
  pure-maxmin, and optimistic miss rates are reported separately.
- `bargaining`: lower configured-principal grade error is better; generic gate
  surplus gap, alternating-offer miss rate, and hidden-reservation miss rate are
  reported separately.
- `belief_bargaining`: lower posterior expected-surplus gap is better; cue
  switch miss rate, multi-turn miss rate, strategic base gap, and posterior
  scaffold gap are reported separately.
- `belief_bargaining_interaction`: lower two-offer expected-surplus gap is
  better; first-price error, second-price error, prior-plan miss,
  single-cue-plan miss, and single-offer miss rates are reported separately.
- `market`: lower competitive/survival oracle price gap is better; collusion
  index, reserve-violation rate, survival cash gap, and liquidation miss rate
  are reported separately.
- `market_policy_shift`: lower profit regret to the opponent-policy-aware best
  response is better; static-Nash and last-price miss rates are reported
  separately.
- `market_policy_inventory`: lower constrained terminal-cash regret is better;
  reserve-violation, static-Nash, last-price, and inventory-blind miss rates are
  reported separately.
- `market_trace_inventory`: lower constrained terminal-cash regret is better;
  reserve-violation, static-Nash, last-price, trace-blind, and inventory-blind
  miss rates are reported separately.
- `market_trace_markdown`: lower constrained terminal-cash regret is better;
  early/late price L1 error, reserve-violation, static-Nash, one-price,
  trace-blind, and inventory-blind miss rates are reported separately.
- `market_trace_replenishment`: lower constrained terminal-cash regret is
  better; decision L1 error, reserve-violation, no-replenishment, one-price,
  trace-blind, and replenishment-blind miss rates are reported separately.
- `market_trace_replenishment_natural`: lower constrained terminal-cash regret
  is better under natural rival shelf/restock labels; decision L1 error,
  reserve-violation, no-replenishment, one-price, trace-blind, and
  replenishment-blind miss rates are reported separately.
- `market_trace_replenishment_noisy`: lower constrained terminal-cash regret is
  better under lumpy regional rival shelf/restock observations; decision L1
  error, reserve-violation, no-replenishment, one-price, trace-blind, and
  replenishment-blind miss rates are reported separately.
- `matching`: lower configured matching score regret is better; max-value and
  access-only miss rates are reported separately.
- `screening`: lower configured contract-menu regret is better; max-profit and
  constraint-blind miss rates are reported separately.
- `moral_hazard`: lower realized principal-profit regret is better; hidden-action
  blind and high-bonus miss rates are reported separately.
- `auction`: lower reserve-price error to the objective-specific mechanism
  oracle is better.
- `common_value`: lower expected-profit regret is better; winner's-curse miss
  and negative-profit rates are reported separately.
- `mechanism`: lower configured score regret is better; revenue-default,
  risk-blind, and IC-blind miss rates are reported separately.
- `mechanism_repeated`: lower repeated-horizon configured score regret is
  better; revenue-default, one-period, and risk/manipulation-blind miss rates
  are reported separately.
- `mechanism_repeated_natural`: lower repeated-horizon configured score regret is
  better; the same revenue-default, one-period, and risk/manipulation-blind miss
  rates are reported under natural pilot-outcome labels.
- `mechanism_participant_response`: lower participant-response configured score
  regret is better; revenue-default, one-period, and response-blind miss rates
  are reported separately.
- `mechanism_elasticity_inference`: lower participant-response configured score
  regret is better after inferring stay-rate sensitivity from pilot
  observations; the same revenue-default, one-period, and response-blind miss
  rates are reported separately.
- `mechanism_strategic_response`: lower multi-agent strategic-response
  configured score regret is better; revenue-default, one-period, and
  response-blind miss rates are reported separately.
- `mechanism_strategic_equilibrium`: lower self-consistent strategic-equilibrium
  score regret is better; revenue-default, one-period, and response-blind miss
  rates are reported separately.
- `mechanism_interaction_trace`: lower interaction-trace projected score regret
  is better; revenue-default, one-period, and trace-blind miss rates are reported
  separately.
- `mechanism_trace_equilibrium`: lower trace-equilibrium score regret is better;
  revenue-default, trace-projection, equilibrium-blind, and trace-blind miss
  rates are reported separately.
- `mechanism_trace_equilibrium_natural`: lower trace-equilibrium score regret is
  better under natural pilot outcome labels; revenue-default, trace-projection,
  equilibrium-blind, and trace-blind miss rates are reported separately.
- `mechanism_trace_equilibrium_noisy`: lower trace-equilibrium score regret is
  better under noisy local pilot sheets; revenue-default, trace-projection,
  equilibrium-blind, and trace-blind miss rates are reported separately.
- `strategic_drift`: lower long-horizon drift rate is better; stress-case drift
  and myopic-miss rates are reported separately for imperfect-information and
  N-player cases.
- `forecast_calibration`: lower expected Brier regret to the accessible
  posterior is better; realized Brier/log loss, posterior L1 error, base-rate
  miss rate, overconfidence rate, and reliability-adjustment miss rate are
  reported separately.
- `forecast_aggregate`: lower expected Brier regret to the shrinkage-calibrated
  aggregate-bin target is better; raw-score miss and shrinkage miss rates are
  reported separately.
- `forecast_curve`: lower expected Brier regret to the interpolated
  calibration-curve target is better; raw-score miss and nearest-bin miss rates
  are reported separately.
- `forecast_curve_implicit`: lower expected Brier regret to the same held-out
  calibration-curve target is better; raw-score miss and nearest-bin miss rates
  are reported separately, but the prompt removes the explicit recalibration
  formula used by `forecast_curve`.
- `forecast_curve_noisy`: lower expected Brier regret to the held-out
  calibration-curve target is better; dense, non-monotone bins stress
  sample-size-aware calibration without an explicit formula.
- `forecast_curve_natural`: lower expected Brier regret to the same dense/noisy
  curve target is better; the prompt hides machine-readable calibration row
  names behind natural outcome-table labels.
- `forecast_shift_calibration`: lower expected Brier regret to the
  bridge-adjusted target-cohort calibration curve is better; raw-score,
  source-curve, and nearest-bridge miss rates are reported separately.
- `forecast_rolling_calibration`: lower expected Brier regret to the
  recency-weighted rolling calibration target is better; raw-score,
  stale-window, and pooled-history miss rates are reported separately.
- `forecast_rolling_log_calibration`: lower expected Brier regret to the
  recency-weighted dated-log calibration target is better; raw-score,
  stale-window, pooled-history, and latest-window miss rates are reported
  separately.
- `forecast_rolling_log_noisy`: lower expected Brier regret to the implicit
  noisy dated-log calibration target is better; raw-score, stale-window,
  pooled-history, and latest-window miss rates are reported separately.
- `forecast_event_log_calibration`: lower expected Brier regret to the
  item-level recency- and score-local calibration target is better; raw-score,
  stale-window, pooled-history, and latest-window miss rates are reported
  separately.
- `forecast_operational_log_calibration`: lower expected Brier regret to the
  operational-context calibration target is better; raw-score, stale-window,
  pooled-history, latest-window, policy-blind, and route-blind miss rates are
  reported separately.
- `exploration`: lower expected-value gap is better; exploration miss rate is
  reported separately.
- `experiment_design`: lower expected-value gap is better; experiment miss and
  multi-step adaptation miss rates are reported separately.
- `retail`: lower order error to the survival/cash oracle is better; ruin
  probability, expected cash gap, myopic-order gap, multi-period cash gap, and
  multi-period miss rate are reported separately.
- `procurement`: higher oracle-choice accuracy is better.
- `procurement_counterfactual`: higher oracle-choice accuracy is better;
  paraphrase inconsistency, preference-flip miss, and sticky-base-on-flip rates
  are reported separately.
- `procurement_bundle`: lower bundle score regret is better; invalid format,
  category miss, budget violation, and compatibility-blind miss rates are
  reported separately.
- `procurement_bundle_natural`: lower bundle score regret is better under a
  natural package-fit prompt; the same invalid, category, budget, and
  compatibility-blind diagnostics are reported.
- `procurement_bundle_evidence`: lower bundle score regret is better when pair
  fit must be inferred from deployment outcome rows; the same invalid,
  category, budget, and compatibility-blind diagnostics are reported.
- `procurement_bundle_noisy_evidence`: lower bundle score regret is better when
  pair fit must be inferred by aggregating noisy deployment outcome rows; the
  same invalid, category, budget, and compatibility-blind diagnostics are
  reported.
- `procurement_bundle_history`: lower bundle score regret is better when pair
  fit must be inferred from multi-period deployment history; the same invalid,
  category, budget, and compatibility-blind diagnostics are reported.
- `procurement_bundle_reserve`: lower bundle score regret is better when pair
  fit includes support-reserve shortfall risk; the same invalid, category,
  budget, and compatibility-blind diagnostics are reported.
- `procurement_vendor_update`: lower sequential procurement score regret is
  better; reputation-blind and myopic miss rates report vendor-history and
  round-by-round planning failures.
- `procurement_vendor_update_noisy`: same sequential score-regret metric when
  delivery reliability must be aggregated from lumpy receiving-ledger rows.
- `pricing`: lower revenue gap to the closed-form optimum is better.
- `pricing_counterfactual`: lower posterior price error is better;
  counterfactual-shift miss and sticky-base-price rates are reported separately.
- `pricing_cross_elasticity`: lower focal-price error is better; cross-blind
  miss rate reports answers that collapse to the own-price-only fit.
- `pricing_multi_product`: lower two-price L1 error is better; independent
  miss rate reports answers that collapse to separate single-product optima.
- `pricing_multi_product_natural`: lower two-price L1 error is better under a
  natural campaign-outcome prompt; independent miss is reported separately.
- `pricing_multi_product_capacity`: lower two-price L1 error is better under
  finite stock caps; capacity-blind and independent miss rates are reported
  separately.
- `pricing_multi_product_capacity_noisy`: lower two-price L1 error is better
  under lumpy regional evidence and finite stock caps; capacity-blind and
  independent miss rates are reported separately.
- `pricing_inventory_markdown`: lower early/late-price L1 error is better;
  myopic miss reports answers that ignore shared inventory across windows.
- `pricing_inventory_markdown_noisy`: same early/late-price L1 metric under
  lumpy regional evidence rows with launch/clearance labels.
- `pricing_multi_product_markdown_noisy`: lower four-price L1 error is better
  under lumpy launch/clearance cross-demand, product-specific stock depletion,
  and liquidation-value price floors; myopic, capacity-blind, and independent
  miss rates are reported separately.
- `pricing_inventory_replenishment_noisy`: lower launch-price/restock/clearance
  decision L1 error is better under lumpy evidence, restock setup cost, unit
  cost, storage capacity, and liquidation value; no-restock, myopic, and
  capacity-fill miss rates are reported separately.
- `pricing_hidden_intervention`: lower price error to the intervention-adjusted
  demand optimum is better; intervention-blind miss reports fits that treat
  non-price lift as normal demand.
- `pricing_law_audit`: higher valid/invalid pricing-law classification accuracy
  is better; invalid-law acceptance and valid-law rejection rates are reported
  separately.
- `pricing_evidence_law_audit`: higher valid/invalid evidence-derived pricing-law
  classification accuracy is better; invalid-law acceptance and valid-law
  rejection rates are reported separately.
- `pricing_evidence_law_holdout`: higher valid/invalid evidence-derived pricing-law
  classification accuracy is better on the generated holdout family; invalid-law
  acceptance and valid-law rejection rates are reported separately.
- `scam`: lower mean overpayment is better.
- `supplier_scam`: lower constrained final-cash regret is better; raw final-cash
  regret, reserve violation, scam-supplier rate, and timing-reserve violation
  and reputation-update miss rates are reported separately.
- `supplier_scam_natural`: lower constrained final-cash regret is better under
  natural vendor labels; the same reserve, timing, scam-supplier, and
  reputation-update diagnostics are reported.

## Stability probe

Use `--repeat N --no-cache` when the question is run-to-run stability rather
than another task variant. This repeats one explicit task against fresh model
calls and reports the primary-metric range, parse-rate range, optional accuracy
range, unstable-case rate, case-outcome status counts, oracle margin when
available, and per-case modal choice. Case statuses distinguish
`stable_oracle`, `stable_non_oracle`, `unstable_oracle_modal`,
`unstable_non_oracle_modal`, and parse-modal failures, so a repeat run can tell
whether the issue is sampling noise, persistent wrong behavior, or parsing. When
trials expose named non-oracle references such as `mechanical_flow`,
`low_turnover`, `max_return`, or `second_best`, the probe also reports which
non-oracle reference the modal choice matches.

Use `--sweep --repeat N --no-cache` when the question is cross-model stability
under the same repeated task. This runs the same stability probe for each agent
in `--agents` and prints a compact table of mean score, range, parse floor,
unstable rate, stable-oracle rate, non-oracle modal rate, and matched
non-oracle references. The sweep also prints a per-case drilldown across
agents, so a cross-model difference can be traced to the exact case, modal
choice, oracle margin, and non-oracle reference matches instead of becoming a
new case-count target.

Example:

```bash
AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli \
  --task principal_holding_prediction_blind_notes \
  --agent openai:nano --repeat 3 --limit 1 --no-cache
```

```bash
AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli \
  --sweep \
  --task principal_holding_prediction_blind_notes \
  --agents openai:nano,openai:mini,openai:gpt-5.5 \
  --repeat 2 --limit 1 --no-cache
```

`--repeat` intentionally requires `--no-cache`; cached repeated calls measure
cache reuse, not model stability.

Use `--case <key>` when a sweep or drilldown identifies one case as the
research target. This keeps depth probes tied to the case that raised the
question instead of relying on task ordering or expanding the case list.

```bash
AEREAD_OPENAI_MAX_OUTPUT_TOKENS=8192 python -m aeread_lab.cli \
  --sweep \
  --task principal_holding_prediction_blind_notes \
  --agents openai:nano,openai:mini,openai:gpt-5.5 \
  --repeat 3 --case pension_outflow_quality_signal --no-cache
```

Offline comparison example:

```bash
python -m aeread_lab.cli --sweep --task all \
  --agents offline:oracle,offline:ev --no-cache
```

Live OpenAI responses are cached under `.aeread-cache/responses/` by default.
Use `--cache-dir <path>` to relocate the cache or `--no-cache` to force fresh
calls. Offline agents do not need the cache and never call the API.

Use `--limit N` for cheap smoke checks against the first `N` deterministic
cases/gambles before running a broad task. For example:

```bash
OPENAI_API_KEY=... python -m aeread_lab.cli --sweep --task regime \
  --agents openai:mini,openai:nano --limit 1
```

## Validation

Run offline validation without API spend:

```bash
python -m unittest discover -s tests
python -m aeread_lab.cli --task all --agent offline:oracle
python -m aeread_lab.cli --sweep --task regime \
  --agents offline:oracle,offline:ev --no-cache
python -m aeread_lab.cli --sweep --task regime_relationship \
  --agents offline:oracle,offline:ev,offline:wrong_regime --no-cache
python -m aeread_lab.cli --sweep --task regime_holdout \
  --agents offline:oracle,offline:ev,offline:half,offline:wrong_regime --no-cache
python -m aeread_lab.cli --sweep --task regime_law_audit \
  --agents offline:oracle,offline:law_accept,offline:law_reject,offline:law_invert --no-cache
```

## Expansion order

The next builds should keep the same discipline: add a deterministic generator,
a mechanical oracle, a no-API baseline, then a thin OpenAI run path.

1. Run full or stress-targeted live OpenAI probes on the cases where sampled
   smokes show parse stability but no separation.
2. Extend mechanism/market probes toward repeated-policy or opponent-policy
   simulation instead of another static scoring field.
3. Extend generator-verifier mass production beyond the current generated
   regime holdout and law-audit verifier: generate larger law families and
   cross-domain verifier tasks.
4. Keep C1 depth-first. PR 105 showed that
   `principal_holding_prediction_blind_notes` is sample-unstable for live
   `nano`; PRs 106-112 turn that into repeat reliability, target-margin,
   case-outcome attribution, baseline attribution, cross-agent sweeps, and
   per-case sweep drilldowns with keyed case targeting. PR 113 starts the
   real-derived path with one public SEC 13F-HR filing trace. Its first live
   alias sweep is stable-oracle for `nano`, `mini`, and `gpt-5.5`, so PR 114
   removes the candidate-change scaffold and tests the same trace from raw
   period rows. The raw-row live result is stable-oracle once dollar materiality
   is stated explicitly, while the added `percent_change` baseline captures the
   uncovered ambiguity between largest percentage reduction and largest
   dollar-material share action. The uncovered questions are now narrower than
   "add more cases": which real filing traces are genuinely ambiguous enough to
   test the flow/turnover shortcut; do smaller aliases confuse market-value
   drift with share action when the filing evidence is less clean or less
   scaffolded; and how noisy is predict-the-principal fidelity when the
   reference is a quarterly public filing rather than a synthetic oracle?
5. Run full or stress-targeted live OpenAI probes where new stress cases parse
   cleanly but show only small separation.
