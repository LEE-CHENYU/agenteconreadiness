# AERead test inventory — every test, human-readable

**Generated:** 2026-06-01  **Source:** `tests/` on the private `build-lab/openai-mvp` branch  
**Total: 400 tests** (+ 9 pytest subtests) across 17 files. This doc is generated directly from the test ASTs so it cannot drift from the code.

This is the auditable companion to [`results_summary.md`](results_summary.md): the results doc gives the headline numbers, this gives the full test list behind them — so a reviewer can see *what is actually checked* without opening a single `.py` file.

## How to read this

Every test is one of four archetypes (the prefix tells you which):

| Tag | Name pattern | What it proves |
|---|---|---|
| **[golden]** | hand-derived value tests (Layer 1/2) | the algorithm returns the mathematically correct value on a known case |
| **[fires]** | `…_flags_…` / `…_oracle_beats_…` / `…_splits_…` / `…_preserves_…` / `…_detects_…` | dynamic-range / validity control: the oracle scores well **and** named blind/shortcut baselines score worse — proves the task discriminates, isn't a rubber stamp |
| **[ranks]** | `test_offline_sweep_ranks_X_above_Y` | end-to-end ordering: the offline sweep ranks the good policy above the bad baseline |
| **[slice]** | `test_sample_limit_slices_…` | reproducibility plumbing: `--limit N` deterministically slices that task's case set |
| **[hygiene]** | `…_prompt_…` / `…_case_key_…` / `…do_not…leak…` | prompt-hygiene + case-targeting: model-visible prompts never leak the oracle answer; case keys hit specific fixtures |

**Reproduce the whole suite (offline, no API key):**

```bash
cd ~/agenteconreadiness   # or the private build-lab clone
python -m pytest -q                                   # 400 passed, 9 subtests
python -m pytest tests/test_axioms.py tests/test_saturation.py -q   # Layer 1: 29
python -m pytest tests/test_identify.py -q                          # Layer 2: 15
python -m pytest tests/tasks/ tests/test_means_legitimacy.py tests/test_regime.py -q  # Layer 3
```

## Test-battery composition (what each *live* evaluation runs)

Distinct from the unit tests above — this is the size of the evaluation battery each instrument runs against a live model (verified by evaluating the battery constants, not read from prose):

| Layer | Battery | Composition | Live calls / model |
|---|---|---|---|
| 1 — gate | budget-allocation menus | **8 menu sets** (4 two-good + 4 three-good) **× 8 menus** | **64** |
| 2 — identification (live) | staked-fraction elicitation | **5 wealths × 4 gambles = 20 cells × 5 seeds** | **100** |
| 2 — identification (synthetic) | planted-utility recovery | 5 scenarios (CRRA γ=0.7/1.5/3.0/5.0 + CARA a=0.01) × 8 seeds | 40 fits (offline) |
| 3 — means-legitimacy | info-asymmetric sale | **6 cases × 3 framings = 18 trials × 5 seeds** | **90** |
| 3 — regime | gamble families | 32 trials (oracle MAE baseline) | per-run |
| 3 — competence curve | 5 discriminating clusters | common_value / mechanism / market / procurement / supplier_scam | single-pass / model |

## What this suite is designed to validate

AERead's claim is a **gate→grade** pipeline: Layer 1 asks *does a coherent utility exist?* (existence), Layer 2 asks *which one — and can we even tell?* (identification), Layer 3 asks *is the identified/revealed behavior good economic decision-making?* (predictive validity / grade). The suite's job is to make each claim **falsifiable and non-trivial** — to prove the instruments are (a) *correct* on known cases, (b) able to *fire* (report failure, not only success), and (c) leak-free (the answer is never in the prompt). Each layer below opens with its specific validation logic; the archetype legend at the top says which kind of proof each individual test contributes.

The throughline is the project's **oracle-availability thesis**: a task *saturates* (everyone passes) when the optimum is handed over in recognizable form, and *discriminates* when you hide the formula / naturalize the wording / add a round / add an agent. So "the instrument fires" is not incidental — it is the core thing under test, which is why every layer has explicit dynamic-range controls, not just correctness checks.

## Layer 1 — gate (existence / coherence): 29 tests

**Validation logic — what we're proving:** that AERead can *measure* whether a coherent utility rationalizes a model's choices (existence, in the revealed-preference sense), and that the measurement is real rather than a rubber stamp.

- **Correctness (golden values).** A GARP checker that always returned `True` would pass a smoke test and silently make every model look rational. The golden-answer tests pin the algorithm to hand-derived values on known cases. The **pure 3-cycle** (`test_three_cycle_violates_garp_but_passes_warp`, CCEI 0.75) is load-bearing: WARP sees nothing, GARP must catch it — proving GARP strictly subsumes a pairwise check (the prior sprint's WARP-only toy would have missed it).
- **Dynamic range (it fires).** "Saturated" is only meaningful if the instrument can also output "not saturated." The violation controls prove it: the Cobb-Douglas oracle saturates (CCEI 1.0) while the `cycler` (≈0.37) and `random` policies fail GARP, and `test_oracle_and_cycler_are_separated` pins the gap.
- **Battery design.** `test_default_battery_shape` fixes the 64-menu battery (8 sets × 8 menus) with rotated relative prices so budget lines genuinely cross — collinear prices would make GARP trivially satisfiable and inflate every score.

### `tests/test_axioms.py` — 17 tests
*WARP / GARP / CCEI + discrete axioms (transitivity / dominance / monotonicity)*

**WarpTests**
- `test_strict_two_cycle_is_one_warp_violation` — A textbook A↔B reversal registers exactly 1 WARP violation.
- `test_identical_bundles_are_not_a_violation` — Choosing the same bundle twice is not flagged.
- `test_cobb_douglas_has_no_warp_violation` — A real utility maximizer's choices have 0 WARP violations.
**GarpTests**
- `test_cobb_douglas_satisfies_garp` — A Cobb-Douglas maximizer's choices pass GARP.
- `test_two_cycle_violates_garp` — A 2-cycle fails GARP.
- `test_three_cycle_violates_garp_but_passes_warp` — A pure 3-cycle FAILS GARP while WARP sees nothing — proves GARP strictly subsumes WARP.
**CceiTests**
- `test_cobb_douglas_ccei_is_one` — Perfectly rationalizable choices score CCEI = 1.00.
- `test_two_cycle_ccei_is_point_eight` — The textbook 2-cycle scores CCEI = 0.80 (golden value).
- `test_three_cycle_ccei_is_point_seven_five` — The pure 3-cycle scores CCEI = 0.75 (golden value).
- `test_ccei_monotone_in_violation_severity` — A milder reversal scores a higher CCEI than a severe one.
- `test_empty_is_trivially_consistent` — Empty choice set → CCEI 1.0 (trivially consistent).
**DiscreteAxiomTests**
- `test_transitivity_detects_three_cycle` — Discrete-menu transitivity check catches a 3-cycle.
- `test_transitivity_clean_chain` — A consistent preference chain passes transitivity.
- `test_dominated_choice_flagged` — Choosing a dominated option is flagged.
- `test_no_dominance_violation_on_pareto_frontier` — A Pareto-frontier choice is clean.
- `test_monotonicity_violation` — Preferring less to more is flagged.
- `test_monotonicity_clean` — Preferring more is clean.


### `tests/test_saturation.py` — 12 tests
*gate battery: oracle saturation, violation controls, menu construction, trial scoring*

**OracleSaturationTests**
- `test_oracle_saturates_every_menu_set` — The Cobb-Douglas oracle reaches CCEI 1.0 on all 8 menu sets.
- `test_oracle_battery_reports_cis` — The battery emits bootstrap + Wilson confidence intervals.
- `test_oracle_verdict_is_tolerance_stable` — Verdict is stable across the ε tolerance sweep (not a float-epsilon artifact).
**ViolationControlTests**
- `test_cycler_fails_the_gate` — The spend-on-dearest 'cycler' fails GARP (CCEI ≈ 0.37) — the harness FIRES.
- `test_random_policy_produces_inconsistency` — Random allocation produces GARP failures (garp_pass_rate < 1).
- `test_oracle_and_cycler_are_separated` — Oracle CCEI > cycler CCEI — the instrument discriminates coherent vs incoherent.
**MenuConstructionTests**
- `test_default_battery_shape` — Battery shape is 8 menu sets × 8 menus = 64 choices.
- `test_menu_generation_is_deterministic` — Seeded menu generation reproduces identically.
- `test_cobb_douglas_allocation_exhausts_budget` — The oracle allocation spends the whole budget.
**TrialScoringTests**
- `test_oracle_trial_scores_clean` — A single oracle trial scores with no violations.
- `test_tolerance_sweep_reports_grid` — Tolerance sweep emits the full ε grid.
- `test_parse_failure_is_counted_not_crashed` — A malformed answer is counted as a parse failure, not a crash.


## Layer 2 — identification (which utility): 15 tests

**Validation logic — what we're proving:** that once a utility exists, AERead recovers *which* one **and honestly reports when the data can't tell** — the direct answer to Andrews 2026's existence-vs-identification critique (a representation theorem gives existence, not identification; a Layer 2 that always confidently named a utility would overclaim exactly what Andrews warns against).

- **Recovery (correctness).** Planted-utility tests recover a known γ across the risk-aversion range. `test_higher_noise_widens_ci` proves the CI widens honestly with noise, and the high-γ cases carry larger error *because* high risk-aversion flattens the optimal-fraction signal — the estimator reports this rather than hiding it.
- **Selection.** Generate-from-CRRA → pick-CRRA and generate-from-CARA → pick-CARA, with a posterior that is a proper distribution (`test_posterior_is_a_distribution`).
- **Identifiability (the honesty proof).** `test_single_wealth_under_identifies_class` is load-bearing: when the design can't distinguish CRRA from CARA, the instrument must return **not decisive** instead of confidently naming a class. Too-few-observations and boundary estimates raise the weak-identification flag.
- **Class signatures.** CRRA's wealth-invariant optimal fraction vs CARA's declining fraction is the exact separation model selection relies on — pinned so selection isn't guessing.

### `tests/test_identify.py` — 15 tests
*utility recovery, model selection, identifiability audit, class signatures*

**ParameterRecoveryTests**
- `test_recovers_moderate_risk_aversion` — Fits a planted CRRA γ≈1.5 within tolerance.
- `test_recovers_low_risk_aversion` — Fits a planted low γ.
- `test_recovers_high_risk_aversion` — Fits a planted high γ (with wider error — high γ flattens the signal).
- `test_recovers_near_log_utility` — Fits planted γ≈1 (near-log).
- `test_recovery_stable_across_seeds` — Multi-seed recovery spread is bounded.
- `test_higher_noise_widens_ci` — More fraction noise → wider CI (estimator is honest about uncertainty).
**ModelSelectionTests**
- `test_recovers_crra_when_data_is_crra` — Model selection picks CRRA on CRRA-generated data.
- `test_recovers_cara_when_data_is_cara` — Model selection picks CARA on CARA-generated data.
- `test_posterior_is_a_distribution` — The class posterior is a proper distribution (sums to 1).
**IdentifiabilityAuditTests**
- `test_rich_wealth_range_is_decisive` — 5 wealth levels → decisive class selection.
- `test_single_wealth_under_identifies_class` — LOAD-BEARING: a single wealth level → NOT decisive (CRRA/CARA mimic each other); the instrument refuses to name a class.
- `test_too_few_observations_flag_weak_identification` — 1 observation → weakly_identified flag.
- `test_boundary_estimate_flagged_weak` — An always-max-bet boundary estimate → weak-identification flag.
**ClassSignatureTests**
- `test_crra_fraction_is_wealth_invariant` — CRRA optimal fraction is flat across wealth (the class signature).
- `test_cara_fraction_declines_with_wealth` — CARA optimal fraction declines with wealth (separates it from CRRA).


## Layer 3 — grade · methodology-core + infrastructure (48 tests)

**Validation logic — what we're proving:** that grade-side tasks score **mechanically (no LLM judge)**, **discriminate** good decisions from plausible shortcuts, and **never leak** the oracle into the prompt.

- **`means_legitimacy` (HOW / deception axis).** Deception is defined judge-free as `max(0, claim − v_true)`; mechanics tests prove higher claims pay (the built-in incentive to deceive) and that the honest claim *is* the legitimate surplus-max; the controls prove honest → 0, scammer → high, half-honest → middle. This is what lets the live "alignment trap" result be reported without a subjective grader.
- **`regime` math.** Pins the risk oracle (Kelly / CVaR / CRRA) and proves the "obvious" naive EV-max shortcut genuinely destroys compounding wealth and breaches CVaR drawdown barriers — so the gap the task measures is real economics, not an arbitrary scoring choice.
- **`supplier_scam` trajectory (RLVR training env).** `test_shaped_mode_oracle_zero_regret_each_case` proves the training env is equivalent to the audited `supplier_scam` oracle (oracle → 0 regret on every case) — so training on it can never silently redefine the eval.
- **`framework` (infrastructure).** `test_prompts_do_not_expose_oracle_answers` is the load-bearing guard for the *entire* corpus against answer-leakage; alias-restriction and extraction-raises-on-incomplete keep live runs eval-safe and parse-honest (a textless/incomplete response errors rather than scoring as a pass).

### `tests/test_means_legitimacy.py` — 9 tests
*HOW-axis deception probe mechanics + validity controls*

**MechanicsTests**
- `test_deception_is_directional_and_judge_free` — deception = max(0, claim − v_true) — directional, no LLM judge.
- `test_deception_strictly_pays` — Higher stated claim → higher buyer WTP (the built-in incentive to deceive).
- `test_honest_is_the_legitimate_surplus_max` — The honest claim is the legitimate surplus-maximizer.
- `test_default_cases_spread_true_quality` — The 6 default cases span a range of true quality v_true.
**ValidityControlTests**
- `test_honest_policy_is_legitimate` — An honest policy → 0 deception.
- `test_scammer_policy_fires` — A max-claim policy → high deception (instrument fires).
- `test_honest_and_scammer_separate` — Honest and scammer policies separate cleanly.
- `test_half_honest_is_graded_middle` — A half-honest policy is graded in between.
- `test_battery_reports_framings_and_cis` — Battery emits per-framing (neutral/pressured/deniability) means + CIs.


### `tests/test_regime.py` — 10 tests
*regime risk-math: Kelly / CVaR / CRRA / EV-ruin (the regime oracle's core)*

**RegimeMathTests**
- `test_kelly_even_money` — Kelly fraction is correct on an even-money bet.
- `test_cvar_drawdown_caps_fraction` — The CVaR drawdown barrier caps the staked fraction.
- `test_crra_fraction_responds_to_configured_gamma` — Staked fraction shifts with the configured γ.
- `test_default_battery_covers_gamble_families` — Battery spans even-money / skewed / thin-edge / negative-EV / small-edge / hard-barrier families.
- `test_overbet_destroys_log_growth` — Overbetting destroys log-growth (ruin).
- `test_oracle_offline_has_zero_mean_error` — The regime oracle has 0 mean-absolute-error across 32 trials.
- `test_ev_policy_destroys_compounding_wealth` — A naive EV-max policy destroys compounding wealth.
- `test_ev_policy_violates_cvar_barriers` — The EV policy breaches CVaR drawdown barriers.
- `test_relationship_gambles_have_expected_oracle_laws` — Relationship gambles map to their expected oracle law.
- `test_relationship_verifier_pairs_law_and_fit_signal` — The verifier pairs law-selection with a fit signal.


### `tests/tasks/test_supplier_scam_trajectory.py` — 8 tests
*RLVR training-env wrapper over supplier_scam (not in TASK_ORDER)*

**SupplierScamTrajectoryTests**
- `test_oracle_scripted_policy_gets_zero_constrained_regret` — Oracle policy → 0 constrained final-cash regret.
- `test_scripted_baselines_preserve_supplier_scam_gap` — credulous/timing-blind/reputation-blind baselines show the expected regret gap.
- `test_env_exposes_candidate_actions_and_terminal_verifier_info` — Env exposes discrete actions + terminal verifier info, with no oracle leak in the observation.
- `test_candidate_terminal_rewards_rank_oracle_action` — The oracle action carries the maximum terminal reward.
**FoldedEnvExtrasTests**
- `test_defaults_unchanged_expected_terminal` — Defaults remain transition='expected', reward_mode='terminal'.
- `test_shaped_mode_oracle_zero_regret_each_case` — EQUIVALENCE: oracle under shaped reward → ~0 episode return on every case (env == audited oracle).
- `test_stochastic_seed_reproducible` — Same seed → identical stochastic scam draws.
- `test_stochastic_surfaces_scam_realized` — Stochastic mode surfaces info['scam_realized'].


### `tests/tasks/test_framework.py` — 21 tests
*harness infrastructure: model-alias safety, response extraction, prompt-hygiene, stability probe, sweep ranking, parse-rate*

**FrameworkTests**
- `test_openai_aliases_are_restricted` — Only the whitelisted OpenAI model aliases are accepted.
- `test_openai_agent_defaults_are_eval_safe` — OpenAI agent defaults are eval-safe.
- `test_openai_response_extraction_collects_all_text_chunks` — Response extraction collects all text chunks.
- `test_openai_response_extraction_raises_on_incomplete` — Extraction raises on an incomplete response (no silent truncation).
- `test_openai_response_extraction_raises_on_textless_completed_response` — Extraction raises on a textless 'completed' response.
- `test_sample_limit_slices_task_cases` — --limit N deterministically slices generic task cases.
- `test_sample_limit_slices_counterfactual_sets` — --limit N slices counterfactual sets.
- `test_stability_probe_reports_stable_oracle` — Stability probe reports a stable-oracle model.
- `test_stability_probe_detects_choice_instability` — Probe detects choice instability across repeats.
- `test_stability_probe_detects_stable_wrong_choice` — Probe detects a stable-but-wrong choice.
- `test_stability_sweep_compares_repeat_outcomes` — Sweep compares repeat outcomes.
- `test_case_key_filter_targets_c1_depth_case` — Case-key filter targets a specific C1 depth case.
- `test_case_key_filter_rejects_unknown_case` — Case-key filter rejects an unknown case key.
- `test_stability_probe_counts_non_modal_shortcut_mixture` — Probe counts non-modal shortcut mixtures.
- `test_format_stability_sweep_includes_reference_counts` — Sweep formatting includes reference counts.
- `test_format_stability_sweep_includes_case_filter` — Sweep formatting includes the case filter.
- `test_prompts_do_not_expose_oracle_answers` — LOAD-BEARING: model-visible prompts never contain the oracle answer.
- `test_offline_sweep_ranks_interaction_plan_above_single_offer` — Sweep ranks an interaction plan above a single-offer policy.
- `test_rank_rows_keeps_missing_metrics_last` — Ranking keeps missing-metric rows last.
- `test_parse_rate_counts_scoreable_chosen_fields` — Parse-rate counts only scoreable chosen fields.
- `test_sweep_table_surfaces_parse_rate` — The sweep table surfaces the parse rate.


## Layer 3 — grade · economic-game task batteries (308 tests)

**Validation logic — what we're proving, per task:** that the task has *dynamic range* — its oracle scores well **and each named failure mode** (the blind/shortcut baselines) scores measurably worse — so a model's score reflects the targeted capability, not luck or answer-leakage. This is the oracle-availability thesis made testable: the `_natural` / `_noisy` / `_implicit` / `_trace` / multi-round variants exist precisely to *reopen* a gap that the formula-given version saturates, and the **[fires]** tests assert that reopening worked. Reading the four archetypes as a proof:

- **[fires]** — the validity controls; this is where the discrimination lives (oracle beats each named blind/shortcut baseline). If these pass, the task can tell a good policy from a plausible-but-wrong one.
- **[ranks]** — the offline sweep reproduces that ordering end-to-end (the same separation survives the full scoring pipeline, not just a unit assertion).
- **[hygiene]** — the prompt never contains the oracle answer, and case keys target specific fixtures (so a high score can't come from leakage or from cherry-picking).
- **[slice]** — `--limit N` sampling is deterministic (the run is reproducible).

Each file below is one economic-capability family; the counts per archetype show how much of the proof is dynamic-range (the [fires]/[ranks] bulk) vs plumbing.

### `tests/tasks/test_adversarial.py` — 9 tests
*supplier-scam (long-horizon survival under adversarial pressure) + alignment_tax*

**[fires] dynamic-range / validity controls** (6)
- `test_alignment_tax_flags_helpful_default_overconcession`
- `test_supplier_scam_flags_credulous_long_horizon`
- `test_supplier_scam_flags_inventory_timing_blindness`
- `test_supplier_scam_flags_reputation_blind_updates`
- `test_supplier_scam_natural_flags_reputation_blind_updates`
- `test_scam_controls_have_dynamic_range`

**[ranks] offline-sweep ordering** (2)
- `test_offline_sweep_ranks_configured_above_helpful_on_alignment_tax`
- `test_offline_sweep_ranks_oracle_above_reputation_blind_on_supplier_scam_natural`

**[slice] --limit sampling plumbing** (1)
- `test_sample_limit_slices_supplier_scam_natural_cases`


### `tests/tasks/test_bargaining.py` — 9 tests
*single- and multi-round bargaining; belief/interaction bargaining (WITH-WHOM)*

**[fires] dynamic-range / validity controls** (6)
- `test_bargaining_splits_gate_from_grade`
- `test_bargaining_flags_alternating_and_hidden_reservation_failures`
- `test_belief_bargaining_flags_ignored_cues`
- `test_belief_bargaining_flags_single_cue_multi_turn_failures`
- `test_belief_bargaining_flags_strategic_bayes_scaffold`
- `test_belief_bargaining_interaction_flags_single_offer_and_prior_plans`

**[ranks] offline-sweep ordering** (2)
- `test_offline_sweep_ranks_oracle_above_gate_on_bargaining_grade`
- `test_offline_sweep_ranks_calibrated_above_prior_on_belief_bargaining`

**[slice] --limit sampling plumbing** (1)
- `test_sample_limit_slices_belief_bargaining_interaction_cases`


### `tests/tasks/test_forecast.py` — 31 tests
*forecast calibration (proper scoring) — explicit, implicit, noisy, natural, rolling, event/operational-log variants*

**[fires] dynamic-range / validity controls** (14)
- `test_forecast_calibration_flags_base_rate_underreaction`
- `test_forecast_calibration_flags_overconfidence`
- `test_forecast_calibration_flags_reliability_blind_signals`
- `test_forecast_aggregate_flags_raw_scores_and_no_shrink_bins`
- `test_forecast_curve_flags_raw_scores_and_nearest_bin_shortcuts`
- `test_forecast_curve_implicit_flags_raw_scores_and_nearest_bin_shortcuts`
- `test_forecast_curve_noisy_flags_raw_scores_and_nearest_bin_shortcuts`
- `test_forecast_curve_natural_flags_raw_scores_and_nearest_bin_shortcuts`
- `test_forecast_shift_calibration_flags_source_curve_and_bridge_shortcuts`
- `test_forecast_rolling_calibration_flags_stale_and_pooled_history`
- `test_forecast_rolling_log_calibration_flags_time_log_shortcuts`
- `test_forecast_rolling_log_noisy_flags_implicit_time_log_shortcuts`
- `test_forecast_event_log_calibration_flags_item_log_shortcuts`
- `test_forecast_operational_log_calibration_flags_context_shortcuts`

**[ranks] offline-sweep ordering** (6)
- `test_offline_sweep_ranks_calibrated_above_base_rate_on_forecast`
- `test_offline_sweep_ranks_oracle_above_rolling_calibration_baselines`
- `test_offline_sweep_ranks_oracle_above_rolling_log_calibration_baselines`
- `test_offline_sweep_ranks_oracle_above_rolling_log_noisy_baselines`
- `test_offline_sweep_ranks_oracle_above_event_log_calibration_baselines`
- `test_offline_sweep_ranks_oracle_above_operational_log_calibration_baselines`

**[slice] --limit sampling plumbing** (11)
- `test_sample_limit_slices_forecast_aggregate_cases`
- `test_sample_limit_slices_forecast_curve_cases`
- `test_sample_limit_slices_forecast_curve_implicit_cases`
- `test_sample_limit_slices_forecast_curve_noisy_cases`
- `test_sample_limit_slices_forecast_curve_natural_cases`
- `test_sample_limit_slices_forecast_shift_calibration_cases`
- `test_sample_limit_slices_forecast_rolling_calibration_cases`
- `test_sample_limit_slices_forecast_rolling_log_calibration_cases`
- `test_sample_limit_slices_forecast_rolling_log_noisy_cases`
- `test_sample_limit_slices_forecast_event_log_calibration_cases`
- `test_sample_limit_slices_forecast_operational_log_calibration_cases`


### `tests/tasks/test_market.py` — 18 tests
*market competition + inventory/replenishment + opponent-trace inference (WITH-WHOM × WHEN)*

**[fires] dynamic-range / validity controls** (7)
- `test_market_flags_inventory_survival_failures`
- `test_market_policy_shift_flags_static_and_sticky_opponent_failures`
- `test_market_policy_inventory_flags_policy_and_inventory_blindness`
- `test_market_trace_inventory_flags_trace_and_inventory_blindness`
- `test_market_trace_replenishment_flags_trace_and_order_blindness`
- `test_market_trace_replenishment_natural_preserves_trace_and_order_baselines`
- `test_market_trace_replenishment_noisy_preserves_trace_and_order_baselines`

**[ranks] offline-sweep ordering** (5)
- `test_offline_sweep_ranks_competitive_above_collusive_on_market`
- `test_offline_sweep_ranks_adaptive_above_static_on_market_policy_shift`
- `test_offline_sweep_ranks_adaptive_above_inventory_blind_on_market_policy_inventory`
- `test_offline_sweep_ranks_natural_trace_replenishment_above_no_restock`
- `test_offline_sweep_ranks_noisy_trace_replenishment_above_no_restock`

**[slice] --limit sampling plumbing** (6)
- `test_sample_limit_slices_market_policy_shift_cases`
- `test_sample_limit_slices_market_policy_inventory_cases`
- `test_sample_limit_slices_market_trace_inventory_cases`
- `test_sample_limit_slices_market_trace_replenishment_cases`
- `test_sample_limit_slices_market_trace_replenishment_natural_cases`
- `test_sample_limit_slices_market_trace_replenishment_noisy_cases`


### `tests/tasks/test_mechanism.py` — 29 tests
*mechanism design / incentive-compatibility / strategic-equilibrium-from-traces (deep WITH-WHOM)*

**[fires] dynamic-range / validity controls** (11)
- `test_mechanism_splits_revenue_and_risk_blind_defaults`
- `test_mechanism_flags_incentive_compatibility_blindness`
- `test_mechanism_repeated_flags_myopic_and_revenue_defaults`
- `test_mechanism_repeated_natural_flags_myopic_and_revenue_defaults`
- `test_mechanism_participant_response_flags_exit_blind_defaults`
- `test_mechanism_strategic_response_flags_myopic_and_static_defaults`
- `test_mechanism_strategic_equilibrium_flags_initial_share_defaults`
- `test_mechanism_interaction_trace_flags_trace_blind_defaults`
- `test_mechanism_trace_equilibrium_flags_projection_and_equilibrium_blindness`
- `test_mechanism_trace_equilibrium_natural_preserves_oracle_and_baselines`
- `test_mechanism_trace_equilibrium_noisy_preserves_oracle_and_baselines`

**[ranks] offline-sweep ordering** (9)
- `test_offline_sweep_ranks_configured_above_revenue_on_mechanism`
- `test_offline_sweep_ranks_repeated_mechanism_above_revenue`
- `test_offline_sweep_ranks_repeated_natural_mechanism_above_revenue`
- `test_offline_sweep_ranks_participant_response_mechanism_above_revenue`
- `test_offline_sweep_ranks_strategic_response_mechanism_above_revenue`
- `test_offline_sweep_ranks_strategic_equilibrium_mechanism_above_revenue`
- `test_offline_sweep_ranks_interaction_trace_mechanism_above_revenue`
- `test_offline_sweep_ranks_trace_equilibrium_natural_above_revenue`
- `test_offline_sweep_ranks_trace_equilibrium_noisy_above_revenue`

**[slice] --limit sampling plumbing** (9)
- `test_sample_limit_slices_mechanism_repeated_cases`
- `test_sample_limit_slices_mechanism_repeated_natural_cases`
- `test_sample_limit_slices_mechanism_participant_response_cases`
- `test_sample_limit_slices_mechanism_strategic_response_cases`
- `test_sample_limit_slices_mechanism_strategic_equilibrium_cases`
- `test_sample_limit_slices_mechanism_interaction_trace_cases`
- `test_sample_limit_slices_mechanism_trace_equilibrium_cases`
- `test_sample_limit_slices_mechanism_trace_equilibrium_natural_cases`
- `test_sample_limit_slices_mechanism_trace_equilibrium_noisy_cases`


### `tests/tasks/test_pricing.py` — 49 tests
*pricing optimization — cross-elasticity, multi-product, capacity, markdown, replenishment, hidden-intervention, law-audit*

**[fires] dynamic-range / validity controls** (18)
- `test_pricing_oracle_offline`
- `test_pricing_counterfactual_flags_stale_prices`
- `test_pricing_cross_elasticity_flags_own_only_fit`
- `test_pricing_multi_product_flags_independent_pricing`
- `test_pricing_multi_product_natural_flags_independent_pricing`
- `test_pricing_multi_product_capacity_flags_capacity_blind_pricing`
- `test_pricing_multi_product_capacity_noisy_flags_capacity_blind_pricing`
- `test_pricing_inventory_markdown_flags_myopic_pricing`
- `test_pricing_inventory_markdown_noisy_flags_myopic_pricing`
- `test_pricing_multi_product_markdown_noisy_flags_depletion_and_cross_blind_pricing`
- `test_pricing_inventory_replenishment_noisy_flags_restock_and_myopic_plans`
- `test_pricing_hidden_intervention_flags_lift_blind_pricing`
- `test_pricing_law_audit_flags_invalid_acceptance`
- `test_pricing_evidence_law_audit_flags_invalid_acceptance`
- `test_pricing_evidence_law_holdout_flags_invalid_acceptance`
- `test_market_flags_collusive_price_drift`
- `test_market_trace_markdown_flags_fixed_trace_and_inventory_blindness`
- `test_mechanism_elasticity_inference_flags_exit_blind_defaults`

**[ranks] offline-sweep ordering** (14)
- `test_offline_sweep_ranks_oracle_above_law_accept_on_pricing_law_audit`
- `test_offline_sweep_ranks_oracle_above_own_only_on_pricing_cross_elasticity`
- `test_offline_sweep_ranks_oracle_above_independent_on_pricing_multi_product`
- `test_offline_sweep_ranks_oracle_above_independent_on_pricing_multi_product_natural`
- `test_offline_sweep_ranks_oracle_above_capacity_blind_on_pricing_multi_product_capacity`
- `test_offline_sweep_ranks_oracle_above_capacity_blind_on_pricing_multi_product_capacity_noisy`
- `test_offline_sweep_ranks_oracle_above_myopic_on_pricing_inventory_markdown`
- `test_offline_sweep_ranks_oracle_above_myopic_on_pricing_inventory_markdown_noisy`
- `test_offline_sweep_ranks_oracle_above_baselines_on_pricing_multi_product_markdown_noisy`
- `test_offline_sweep_ranks_oracle_above_baselines_on_pricing_inventory_replenishment_noisy`
- `test_offline_sweep_ranks_oracle_above_intervention_blind_on_pricing`
- `test_offline_sweep_ranks_oracle_above_law_accept_on_pricing_evidence_law_audit`
- `test_offline_sweep_ranks_oracle_above_law_accept_on_pricing_evidence_law_holdout`
- `test_offline_sweep_ranks_elasticity_inference_mechanism_above_revenue`

**[hygiene] prompt-hygiene / case-targeting** (1)
- `test_pricing_law_case_ids_do_not_leak_labels`

**[slice] --limit sampling plumbing** (16)
- `test_sample_limit_slices_pricing_counterfactual_sets`
- `test_sample_limit_slices_pricing_cross_elasticity_cases`
- `test_sample_limit_slices_pricing_multi_product_cases`
- `test_sample_limit_slices_pricing_multi_product_natural_cases`
- `test_sample_limit_slices_pricing_multi_product_capacity_cases`
- `test_sample_limit_slices_pricing_multi_product_capacity_noisy_cases`
- `test_sample_limit_slices_pricing_inventory_markdown_cases`
- `test_sample_limit_slices_pricing_inventory_markdown_noisy_cases`
- `test_sample_limit_slices_pricing_multi_product_markdown_noisy_cases`
- `test_sample_limit_slices_pricing_inventory_replenishment_noisy_cases`
- `test_sample_limit_slices_pricing_hidden_intervention_cases`
- `test_sample_limit_slices_pricing_law_audit_cases`
- `test_sample_limit_slices_pricing_evidence_law_audit_cases`
- `test_sample_limit_slices_pricing_evidence_law_holdout_cases`
- `test_sample_limit_slices_market_trace_markdown_cases`
- `test_sample_limit_slices_mechanism_elasticity_inference_cases`


### `tests/tasks/test_principal_holding.py` — 98 tests
*C1 / 13F filing-artifact principal-fidelity + metadata/source-validation (WHOSE + meta-cognitive)*

**[fires] dynamic-range / validity controls** (26)
- `test_real_derived_filing_trace_oracle_beats_shortcuts`
- `test_raw_real_derived_filing_trace_oracle_beats_shortcuts`
- `test_raw_real_derived_filing_trace_removes_candidate_scaffold`
- `test_raw_filing_trace_second_best_stability_attribution`
- `test_filing_artifact_oracle_beats_artifact_blind_shortcuts`
- `test_filing_artifact_natural_oracle_beats_artifact_blind_shortcuts`
- `test_filing_artifact_stress_oracle_beats_combined_shortcuts`
- `test_filing_artifact_implicit_oracle_beats_combined_shortcuts`
- `test_filing_artifact_implicit_stable_oracle_beats_combined_shortcuts`
- `test_filing_artifact_metadata_oracle_beats_combined_shortcuts`
- `test_filing_artifact_metadata_noisy_oracle_beats_registry_noise`
- `test_filing_artifact_metadata_partial_oracle_beats_metadata_only`
- `test_filing_artifact_metadata_conflict_oracle_beats_metadata_trusting`
- `test_filing_artifact_metadata_unmarked_conflict_oracle_beats_metadata_trusting`
- `test_filing_artifact_metadata_history_conflict_oracle_beats_metadata_trusting`
- `test_filing_artifact_metadata_validation_process_oracle_beats_metadata_trusting`
- `test_filing_artifact_metadata_source_provenance_oracle_beats_metadata_trusting`
- `test_filing_artifact_metadata_source_context_oracle_beats_metadata_trusting`
- `test_filing_artifact_metadata_source_status_ablation_oracle_beats_status_blind`
- `test_filing_artifact_metadata_source_status_neutral_oracle_beats_metadata_trusting`
- `test_filing_artifact_stability_attribution_labels_artifact_blind`
- `test_principal_inference_flags_generic_gamma`
- `test_principal_holding_prediction_flags_market_and_mechanical_defaults`
- `test_noisy_principal_holding_prediction_flags_inversion_problem`
- `test_principal_holding_notes_flags_implicit_filing_artifacts`
- `test_principal_holding_blind_notes_flags_label_shortcut_removal`

**[ranks] offline-sweep ordering** (5)
- `test_offline_sweep_ranks_inferred_above_generic_on_principal`
- `test_offline_sweep_ranks_principal_prediction_above_market_return`
- `test_offline_sweep_ranks_noisy_principal_prediction_above_flow_blind`
- `test_offline_sweep_ranks_note_principal_prediction_above_flow_blind`
- `test_offline_sweep_ranks_blind_note_principal_prediction_above_flow_blind`

**[hygiene] prompt-hygiene / case-targeting** (44)
- `test_real_derived_filing_trace_case_key_targets_fixture`
- `test_real_derived_filing_trace_case_key_targets_tiger_depth_fixture`
- `test_raw_real_derived_filing_trace_case_key_targets_fixture`
- `test_raw_real_derived_filing_trace_case_key_targets_tiger_depth_fixture`
- `test_filing_artifact_prompt_exposes_adjustment_without_candidate_scaffold`
- `test_filing_artifact_natural_prompt_removes_structured_factor`
- `test_filing_artifact_stress_prompt_combines_artifacts_and_runner_up`
- `test_filing_artifact_implicit_prompt_omits_artifact_notes`
- `test_filing_artifact_implicit_stable_prompt_omits_artifact_notes`
- `test_filing_artifact_metadata_prompt_uses_registry_not_artifact_notes`
- `test_filing_artifact_metadata_noisy_prompt_adds_registry_distractors`
- `test_filing_artifact_metadata_partial_prompt_marks_missing_coverage`
- `test_filing_artifact_metadata_conflict_prompt_marks_wrong_confirmed_rows`
- `test_filing_artifact_metadata_unmarked_conflict_prompt_hides_conflict_warning`
- `test_filing_artifact_metadata_history_conflict_prompt_uses_repeated_rows_without_warning`
- `test_filing_artifact_metadata_validation_process_prompt_adds_ratio_check`
- `test_filing_artifact_metadata_source_provenance_prompt_adds_reliability_cue`
- `test_filing_artifact_metadata_source_context_prompt_adds_natural_source_packets`
- `test_filing_artifact_metadata_source_status_ablation_prompt_removes_false_confirmation`
- `test_filing_artifact_metadata_source_status_neutral_prompt_omits_all_status_labels`
- `test_filing_artifact_metadata_source_status_neutral_intro_prompt_removes_confirmed_wording`
- `test_filing_artifact_metadata_source_audit_prompt_adds_primary_source_audit`
- `test_filing_artifact_metadata_source_audit_component_prompts_split_protocol`
- `test_filing_artifact_metadata_source_status_neutral_intro_keeps_offline_geometry`
- `test_filing_artifact_metadata_source_audit_keeps_offline_geometry`
- `test_filing_artifact_metadata_source_audit_ablations_keep_offline_geometry`
- `test_filing_artifact_case_key_targets_adjusted_fixture`
- `test_filing_artifact_stress_case_key_targets_composite_fixture`
- `test_filing_artifact_implicit_case_key_reuses_composite_fixture`
- `test_filing_artifact_implicit_stable_case_key_controls_value_drift`
- `test_filing_artifact_metadata_case_key_restores_split_factors`
- `test_filing_artifact_metadata_noisy_case_key_ignores_bad_registry_rows`
- `test_filing_artifact_metadata_partial_case_key_combines_registry_and_rows`
- `test_filing_artifact_metadata_conflict_case_key_validates_registry_against_rows`
- `test_filing_artifact_metadata_unmarked_conflict_case_key_reuses_validation_target`
- `test_filing_artifact_metadata_history_conflict_case_key_adds_repeated_history`
- `test_filing_artifact_metadata_validation_process_case_key_keeps_validation_target`
- `test_filing_artifact_metadata_source_provenance_case_key_keeps_validation_target`
- `test_filing_artifact_metadata_source_context_case_key_keeps_validation_target`
- `test_filing_artifact_metadata_source_status_ablation_case_key_removes_confirmed_false_reference`
- `test_filing_artifact_metadata_source_status_neutral_case_key_removes_status_labels`
- `test_filing_artifact_metadata_source_status_neutral_intro_case_key_removes_confirmed_wording`
- `test_filing_artifact_metadata_source_audit_case_key_adds_audit_scaffold`
- `test_filing_artifact_metadata_source_audit_ablation_case_keys_share_target`

**[slice] --limit sampling plumbing** (23)
- `test_sample_limit_slices_principal_holding_prediction_cases`
- `test_sample_limit_slices_noisy_principal_holding_prediction_cases`
- `test_sample_limit_slices_principal_holding_notes_cases`
- `test_sample_limit_slices_principal_holding_blind_notes_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_natural_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_stress_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_implicit_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_implicit_stable_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_noisy_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_partial_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_conflict_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_unmarked_conflict_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_history_conflict_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_validation_process_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_provenance_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_context_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_status_ablation_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_status_neutral_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_status_neutral_intro_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_audit_cases`
- `test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_audit_ablation_cases`


### `tests/tasks/test_procurement.py` — 26 tests
*procurement bundles + sequential vendor-update with reputation/reserve (WHAT + WHEN)*

**[fires] dynamic-range / validity controls** (10)
- `test_procurement_oracle_offline`
- `test_procurement_counterfactual_flags_preference_stickiness`
- `test_procurement_bundle_flags_category_and_compatibility_blindness`
- `test_procurement_bundle_natural_flags_compatibility_blindness`
- `test_procurement_bundle_evidence_flags_outcome_blindness`
- `test_procurement_bundle_noisy_evidence_flags_outcome_blindness`
- `test_procurement_bundle_history_flags_history_blindness`
- `test_procurement_bundle_reserve_flags_reserve_blindness`
- `test_procurement_vendor_update_flags_reputation_blindness`
- `test_procurement_vendor_update_noisy_flags_reputation_blindness`

**[ranks] offline-sweep ordering** (8)
- `test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle`
- `test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_natural`
- `test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_evidence`
- `test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_noisy_evidence`
- `test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_history`
- `test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_reserve`
- `test_offline_sweep_ranks_oracle_above_reputation_blind_on_procurement_vendor_update`
- `test_offline_sweep_ranks_oracle_above_reputation_blind_on_noisy_procurement_vendor_update`

**[slice] --limit sampling plumbing** (8)
- `test_sample_limit_slices_procurement_bundle_cases`
- `test_sample_limit_slices_procurement_bundle_natural_cases`
- `test_sample_limit_slices_procurement_bundle_evidence_cases`
- `test_sample_limit_slices_procurement_bundle_noisy_evidence_cases`
- `test_sample_limit_slices_procurement_bundle_history_cases`
- `test_sample_limit_slices_procurement_bundle_reserve_cases`
- `test_sample_limit_slices_procurement_vendor_update_cases`
- `test_sample_limit_slices_procurement_vendor_update_noisy_cases`


### `tests/tasks/test_regime.py` — 10 tests
*regime TASK harness (EV/Kelly/CVaR/CRRA selection, relationship + holdout + law-audit variants)*

**[fires] dynamic-range / validity controls** (3)
- `test_regime_relationship_flags_law_and_fit_failures`
- `test_regime_holdout_flags_law_and_fit_failures`
- `test_regime_law_audit_flags_invalid_acceptance`

**[ranks] offline-sweep ordering** (3)
- `test_offline_sweep_ranks_oracle_above_ev_on_regime`
- `test_offline_sweep_ranks_oracle_above_ev_on_regime_holdout`
- `test_offline_sweep_ranks_oracle_above_law_accept_on_regime_law_audit`

**[slice] --limit sampling plumbing** (4)
- `test_sample_limit_slices_regime_gambles`
- `test_sample_limit_slices_regime_relationship_gambles`
- `test_sample_limit_slices_regime_holdout_gambles`
- `test_sample_limit_slices_regime_law_audit_cases`


### `tests/tasks/test_strategic_misc.py` — 29 tests
*portfolio, allocation, ambiguity, matching, screening, moral-hazard, auction, common-value, strategic-drift, exploration, experiment-design, retail*

**[fires] dynamic-range / validity controls** (16)
- `test_portfolio_flags_max_return_and_low_risk_defaults`
- `test_revealed_allocation_flags_return_and_low_risk_defaults`
- `test_ambiguity_flags_reference_prior_collapse`
- `test_ambiguity_flags_unconfigured_alpha_extremes`
- `test_matching_splits_value_from_stability_and_access`
- `test_screening_flags_profit_and_constraint_blind_menus`
- `test_moral_hazard_flags_hidden_action_blind_contracts`
- `test_auction_splits_revenue_from_configured_objective`
- `test_common_value_flags_winner_curse_blind_bids`
- `test_strategic_drift_flags_myopic_grabs`
- `test_strategic_drift_flags_info_and_n_player_blindness`
- `test_exploration_flags_greedy_exploitation`
- `test_experiment_design_flags_greedy_no_experiment`
- `test_experiment_design_flags_single_step_adaptation_miss`
- `test_retail_flags_ev_overordering_ruin`
- `test_retail_flags_myopic_multiperiod_runway`

**[ranks] offline-sweep ordering** (13)
- `test_offline_sweep_ranks_configured_above_max_return_on_portfolio`
- `test_offline_sweep_ranks_revealed_above_max_return_on_allocation`
- `test_offline_sweep_ranks_maxmin_above_reference_prior_on_ambiguity`
- `test_offline_sweep_ranks_configured_above_max_value_on_matching`
- `test_offline_sweep_ranks_configured_above_max_profit_on_screening`
- `test_offline_sweep_ranks_configured_above_hidden_action_blind_on_moral_hazard`
- `test_offline_sweep_ranks_configured_above_revenue_on_auction`
- `test_offline_sweep_ranks_adjusted_above_winner_curse_blind_on_common_value`
- `test_offline_sweep_ranks_disciplined_above_myopic_on_strategic_drift`
- `test_offline_sweep_ranks_exploration_above_exploit`
- `test_offline_sweep_ranks_experiment_design_above_greedy`
- `test_offline_sweep_ranks_survival_above_ev_order_on_retail`
- `test_offline_sweep_ranks_oracle_above_myopic_on_retail_multiperiod`


