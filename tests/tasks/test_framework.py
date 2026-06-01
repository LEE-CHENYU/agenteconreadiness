# Split from the former monolithic tests/test_tasks.py — framework cluster (21 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit
# underscore-prefixed names are skipped by `import *`; import explicitly
from tests.tasks._shared import (  # noqa: F401
    _AlternatingTradeAgent,
    _ArtifactStressMixtureAgent,
    _WrongTradeAgent,
    _extract_openai_response_text,
)


class FrameworkTests(unittest.TestCase):

    def test_openai_aliases_are_restricted(self):
        self.assertEqual(resolve_openai_model("gpt-5.5"), "gpt-5.5")
        self.assertEqual(resolve_openai_model("mini"), "gpt-5.4-mini")
        self.assertEqual(resolve_openai_model("nano"), "gpt-5.4-nano")
        with self.assertRaises(ValueError):
            resolve_openai_model("anthropic/claude-sonnet-4.6")

    def test_openai_agent_defaults_are_eval_safe(self):
        agent = OpenAIResponsesAgent(model="gpt-5.5")
        self.assertEqual(agent.max_output_tokens, 4096)
        self.assertEqual(agent.reasoning_effort, "low")
        self.assertEqual(agent.text_verbosity, "low")

    def test_openai_response_extraction_collects_all_text_chunks(self):
        response = SimpleNamespace(
            status="completed",
            output_text="",
            output=[
                SimpleNamespace(
                    content=[
                        SimpleNamespace(text="FINAL_ONE: a"),
                        SimpleNamespace(text="FINAL_TWO: b"),
                    ]
                )
            ],
        )
        self.assertEqual(_extract_openai_response_text(response), "FINAL_ONE: a\nFINAL_TWO: b")

    def test_openai_response_extraction_raises_on_incomplete(self):
        response = SimpleNamespace(
            status="incomplete",
            incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            output_text="",
            output=[],
        )
        with self.assertRaisesRegex(RuntimeError, "max_output_tokens"):
            _extract_openai_response_text(response)

    def test_openai_response_extraction_raises_on_textless_completed_response(self):
        response = {"status": "completed", "output_text": "", "output": [{"content": []}]}
        with self.assertRaisesRegex(RuntimeError, "no text output"):
            _extract_openai_response_text(response)

    def test_sample_limit_slices_task_cases(self):
        results = run_tasks("procurement", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_sample_limit_slices_counterfactual_sets(self):
        results = run_tasks("procurement_counterfactual", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_sets"], 1)
        self.assertEqual(results[0]["n_trials"], 3)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_stability_probe_reports_stable_oracle(self):
        payload = run_stability_probe(
            task="principal_holding_prediction_blind_notes",
            agent=OfflineAgent("oracle"),
            repeat_count=3,
            sample_limit=1,
        )
        self.assertEqual(payload["repeat_count"], 3)
        self.assertEqual(payload["primary_metric"], "mean_score_regret")
        self.assertLess(payload["primary_range"], 1e-9)
        self.assertEqual(payload["parse_rate_min"], 1.0)
        self.assertEqual(payload["unstable_case_rate"], 0.0)
        self.assertEqual(payload["case_status_counts"], {"stable_oracle": 1})
        self.assertEqual(payload["modal_reference_counts"], {})
        self.assertEqual(payload["non_oracle_modal_reference_counts"], {})
        self.assertIsNone(payload["attributed_non_oracle_modal_case_rate"])
        self.assertEqual(payload["stable_oracle_case_rate"], 1.0)
        self.assertEqual(payload["mean_case_oracle_hit_rate"], 1.0)
        self.assertEqual(payload["case_stability"][0]["status"], "stable_oracle")
        self.assertEqual(payload["case_stability"][0]["modal_reference_matches"], [])
        self.assertEqual(
            payload["case_stability"][0]["reference_choices"]["generic_style"],
            "add_quality_utility",
        )
        self.assertNotIn("generic_style", payload["case_stability"][0]["reference_hit_rates"])
        self.assertEqual(payload["case_stability"][0]["unique_choice_count"], 1)
        self.assertEqual(payload["case_stability"][0]["parse_fail_rate"], 0.0)
        self.assertGreater(payload["case_stability"][0]["oracle_margin"], 0.05)

    def test_stability_probe_detects_choice_instability(self):
        payload = run_stability_probe(
            task="principal_holding_prediction_blind_notes",
            agent=_AlternatingTradeAgent(),
            repeat_count=4,
            sample_limit=1,
        )
        self.assertEqual(payload["repeat_count"], 4)
        self.assertGreater(payload["primary_range"], 0.0)
        self.assertEqual(payload["unstable_case_rate"], 1.0)
        self.assertEqual(payload["unstable_oracle_modal_case_rate"], 1.0)
        self.assertEqual(payload["case_status_counts"], {"unstable_oracle_modal": 1})
        self.assertEqual(payload["modal_reference_counts"], {})
        self.assertEqual(payload["case_stability"][0]["reference_hit_rates"]["max_return"], 0.5)
        self.assertEqual(payload["case_stability"][0]["reference_hit_rates"]["second_best"], 0.5)
        self.assertEqual(payload["mean_case_oracle_hit_rate"], 0.5)
        self.assertEqual(payload["case_stability"][0]["status"], "unstable_oracle_modal")
        self.assertEqual(payload["case_stability"][0]["unique_choice_count"], 2)
        self.assertGreater(payload["case_stability"][0]["oracle_margin"], 0.05)

    def test_stability_probe_detects_stable_wrong_choice(self):
        payload = run_stability_probe(
            task="principal_holding_prediction_blind_notes",
            agent=_WrongTradeAgent(),
            repeat_count=3,
            sample_limit=1,
        )
        self.assertEqual(payload["unstable_case_rate"], 0.0)
        self.assertEqual(payload["stable_non_oracle_case_rate"], 1.0)
        self.assertEqual(payload["case_status_counts"], {"stable_non_oracle": 1})
        self.assertEqual(payload["modal_reference_counts"], {"max_return": 1, "second_best": 1})
        self.assertEqual(
            payload["non_oracle_modal_reference_counts"],
            {"max_return": 1, "second_best": 1},
        )
        self.assertEqual(payload["attributed_non_oracle_modal_case_rate"], 1.0)
        self.assertEqual(payload["mean_case_oracle_hit_rate"], 0.0)
        self.assertEqual(payload["case_stability"][0]["status"], "stable_non_oracle")
        self.assertEqual(
            payload["case_stability"][0]["modal_reference_matches"],
            ["max_return", "second_best"],
        )
        self.assertEqual(payload["case_stability"][0]["unique_choice_count"], 1)

    def test_stability_sweep_compares_repeat_outcomes(self):
        payload = run_stability_sweep(
            task="principal_holding_prediction_blind_notes",
            agent_specs=["offline:oracle", "offline:low_turnover"],
            repeat_count=2,
            sample_limit=1,
        )
        self.assertEqual(payload["repeat_count"], 2)
        self.assertEqual(payload["sample_limit"], 1)
        self.assertEqual([run["agent"] for run in payload["runs"]], ["offline:oracle", "offline:low_turnover"])
        oracle, low_turnover = payload["runs"]
        self.assertEqual(oracle["case_status_counts"], {"stable_oracle": 1})
        self.assertEqual(low_turnover["case_status_counts"], {"stable_non_oracle": 1})
        self.assertEqual(
            low_turnover["non_oracle_modal_reference_counts"],
            {"low_turnover": 1, "mechanical_flow": 1},
        )
        self.assertEqual(low_turnover["attributed_non_oracle_modal_case_rate"], 1.0)
        case_rows = stability_sweep_case_table(payload)
        self.assertEqual(len(case_rows), 2)
        self.assertEqual(
            [row["agent"] for row in case_rows],
            ["offline:oracle", "offline:low_turnover"],
        )
        self.assertEqual(
            {row["status"] for row in case_rows},
            {"stable_oracle", "stable_non_oracle"},
        )
        self.assertEqual(
            case_rows[1]["modal_reference_matches"],
            ["low_turnover", "mechanical_flow"],
        )

    def test_case_key_filter_targets_c1_depth_case(self):
        results = run_tasks(
            "principal_holding_prediction_blind_notes",
            OfflineAgent("oracle"),
            case_keys=["pension_outflow_quality_signal"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertEqual(
            results[0]["trials"][0]["case"]["key"],
            "pension_outflow_quality_signal",
        )
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_case_key_filter_rejects_unknown_case(self):
        with self.assertRaisesRegex(ValueError, "Unknown case key"):
            run_tasks(
                "principal_holding_prediction_blind_notes",
                OfflineAgent("oracle"),
                case_keys=["missing_case"],
            )

    def test_stability_probe_counts_non_modal_shortcut_mixture(self):
        payload = run_stability_probe(
            task="principal_holding_filing_artifact_stress",
            agent=_ArtifactStressMixtureAgent(),
            repeat_count=3,
            case_keys=["multi_artifact_close_runner_up"],
        )
        row = payload["case_stability"][0]
        self.assertEqual(row["status"], "unstable_oracle_modal")
        self.assertEqual(row["modal_reference_matches"], [])
        self.assertEqual(row["choice_counts"]["sec_stress_b"], 1)
        self.assertEqual(row["choice_counts"]["sec_stress_a"], 1)
        self.assertEqual(row["choice_counts"]["sec_stress_f"], 1)
        self.assertEqual(row["reference_hit_counts"]["artifact_blind"], 1)
        self.assertEqual(row["reference_hit_counts"]["market_value"], 1)
        self.assertEqual(row["active_reference_matches"], ["artifact_blind", "market_value"])
        self.assertAlmostEqual(row["reference_hit_rates"]["artifact_blind"], 1 / 3)
        self.assertAlmostEqual(row["reference_hit_rates"]["market_value"], 1 / 3)
        self.assertAlmostEqual(row["non_oracle_choice_rate"], 2 / 3)
        self.assertEqual(row["attributed_non_oracle_choice_rate"], 1.0)
        self.assertEqual(payload["modal_reference_counts"], {})
        self.assertEqual(
            payload["choice_reference_hit_counts"],
            {"artifact_blind": 1, "market_value": 1},
        )
        self.assertAlmostEqual(payload["choice_reference_hit_rates"]["artifact_blind"], 1 / 3)
        self.assertAlmostEqual(payload["non_oracle_choice_rate"], 2 / 3)
        self.assertEqual(payload["attributed_non_oracle_choice_rate"], 1.0)
        self.assertEqual(payload["multi_reference_case_rate"], 1.0)
        output = format_stability(payload)
        self.assertIn("choice_reference_hit_counts=artifact_blind:1, market_value:1", output)
        self.assertIn("multi_reference_cases=1", output)

    def test_format_stability_sweep_includes_reference_counts(self):
        payload = run_stability_sweep(
            task="principal_holding_prediction_blind_notes",
            agent_specs=["offline:oracle", "offline:low_turnover"],
            repeat_count=2,
            sample_limit=1,
        )
        output = format_stability_sweep(payload)
        self.assertIn("AERead stability sweep", output)
        self.assertIn("offline:oracle", output)
        self.assertIn("offline:low_turno", output)
        self.assertIn("low_turnover:1", output)
        self.assertIn("Choice reference mix", output)
        self.assertIn("low_turnover:2", output)
        self.assertIn("Per-case stability drilldown", output)
        self.assertIn("pension_outflow_quality_sign", output)
        self.assertIn("stable_non_oracle", output)

    def test_format_stability_sweep_includes_case_filter(self):
        payload = run_stability_sweep(
            task="principal_holding_prediction_blind_notes",
            agent_specs=["offline:oracle", "offline:low_turnover"],
            repeat_count=2,
            case_keys=["pension_outflow_quality_signal"],
        )
        output = format_stability_sweep(payload)
        self.assertIn("cases=pension_outflow_quality_signal", output)
        self.assertIn("pension_outflow_quality_sign", output)
        self.assertNotIn("endowment_index_noise_growth", output)

    def test_prompts_do_not_expose_oracle_answers(self):
        regime = regime_prompt(DEFAULT_GAMBLES[0], "kelly")
        regime_relationship = regime_relationship_prompt(DEFAULT_RELATIONSHIP_GAMBLES[0], "kelly")
        regime_holdout = regime_holdout_prompt(DEFAULT_HOLDOUT_GAMBLES[0], "kelly")
        regime_law_audit = regime_law_audit_prompt(DEFAULT_LAW_AUDIT_CASES[0])
        alignment_tax = alignment_tax_prompt(ALIGNMENT_CASES[0])
        procurement = procurement_prompt(PROCUREMENT_CASES[0])
        procurement_bundle = procurement_bundle_prompt(PROCUREMENT_BUNDLE_CASES[0])
        procurement_bundle_natural = procurement_bundle_natural_prompt(PROCUREMENT_BUNDLE_CASES[0])
        procurement_bundle_evidence = procurement_bundle_evidence_prompt(PROCUREMENT_BUNDLE_CASES[0])
        procurement_bundle_noisy_evidence = procurement_bundle_noisy_evidence_prompt(PROCUREMENT_BUNDLE_CASES[0])
        procurement_bundle_history = procurement_bundle_history_prompt(PROCUREMENT_BUNDLE_CASES[0])
        procurement_bundle_reserve = procurement_bundle_reserve_prompt(PROCUREMENT_BUNDLE_CASES[0])
        procurement_vendor_update = procurement_vendor_update_prompt(PROCUREMENT_VENDOR_UPDATE_CASES[0])
        procurement_vendor_update_noisy = procurement_vendor_update_noisy_prompt(
            PROCUREMENT_VENDOR_UPDATE_NOISY_CASES[0]
        )
        procurement_counterfactual = procurement_prompt(COUNTERFACTUAL_SETS[0].preference_flip)
        pricing = pricing_prompt(PRICING_CASES[0], "reveal")
        pricing_counterfactual = pricing_counterfactual_prompt(
            PRICING_COUNTERFACTUAL_SETS[0].perturbed,
            "perturbed",
        )
        pricing_cross = pricing_cross_prompt(PRICING_CROSS_CASES[0])
        pricing_multi = pricing_multi_prompt(PRICING_MULTI_CASES[0])
        pricing_multi_natural = pricing_multi_natural_prompt(PRICING_MULTI_CASES[0])
        pricing_multi_capacity = pricing_multi_capacity_prompt(PRICING_MULTI_CAPACITY_CASES[0])
        pricing_multi_capacity_noisy = pricing_multi_capacity_noisy_prompt(
            PRICING_MULTI_CAPACITY_NOISY_CASES[0]
        )
        pricing_inventory_markdown = pricing_inventory_markdown_prompt(PRICING_INVENTORY_MARKDOWN_CASES[0])
        pricing_inventory_markdown_noisy = pricing_inventory_markdown_noisy_prompt(
            PRICING_INVENTORY_MARKDOWN_NOISY_CASES[0]
        )
        pricing_multi_markdown_noisy = pricing_multi_markdown_noisy_prompt(
            PRICING_MULTI_MARKDOWN_NOISY_CASES[0]
        )
        pricing_inventory_replenishment_noisy = pricing_inventory_replenishment_noisy_prompt(
            PRICING_INVENTORY_REPLENISHMENT_NOISY_CASES[0]
        )
        pricing_hidden_intervention = pricing_hidden_intervention_prompt(PRICING_HIDDEN_INTERVENTION_CASES[0])
        pricing_law_audit = pricing_law_audit_prompt(PRICING_LAW_CASES[0])
        pricing_evidence_law = pricing_evidence_law_prompt(PRICING_EVIDENCE_LAW_CASES[0])
        pricing_evidence_holdout = pricing_evidence_law_prompt(PRICING_EVIDENCE_HOLDOUT_CASES[0])
        strategic = strategic_prompt(DRIFT_CASES[0], 1, [])
        forecast = forecast_prompt(FORECAST_CASES[0])
        forecast_aggregate = forecast_aggregate_prompt(FORECAST_AGGREGATE_CASES[0])
        forecast_curve = forecast_curve_prompt(FORECAST_CURVE_CASES[0])
        forecast_curve_implicit = forecast_curve_implicit_prompt(FORECAST_CURVE_CASES[0])
        forecast_curve_noisy = forecast_curve_noisy_prompt(FORECAST_NOISY_CURVE_CASES[0])
        forecast_curve_natural = forecast_curve_natural_prompt(FORECAST_NOISY_CURVE_CASES[0])
        forecast_shift = forecast_shift_prompt(FORECAST_SHIFT_CASES[0])
        forecast_rolling = forecast_rolling_prompt(FORECAST_ROLLING_CASES[0])
        forecast_rolling_log = forecast_rolling_log_prompt(FORECAST_ROLLING_LOG_CASES[0])
        forecast_rolling_noisy_log = forecast_rolling_noisy_log_prompt(
            FORECAST_ROLLING_NOISY_LOG_CASES[0]
        )
        forecast_event_log = forecast_event_log_prompt(FORECAST_EVENT_LOG_CASES[0])
        forecast_operational_log = forecast_operational_log_prompt(
            FORECAST_OPERATIONAL_LOG_CASES[0]
        )
        exploration = exploration_prompt(EXPLORATION_CASES[0])
        market_policy = market_policy_prompt(MARKET_POLICY_CASES[0])
        market_policy_inventory = market_policy_inventory_prompt(MARKET_INVENTORY_POLICY_CASES[0])
        market_trace_inventory = market_trace_inventory_prompt(MARKET_TRACE_INVENTORY_CASES[0])
        market_trace_markdown = market_trace_markdown_prompt(MARKET_TRACE_INVENTORY_CASES[0])
        market_trace_replenishment = market_trace_replenishment_prompt(
            MARKET_TRACE_REPLENISHMENT_CASES[0]
        )
        market_trace_replenishment_natural = market_trace_replenishment_natural_prompt(
            MARKET_TRACE_REPLENISHMENT_CASES[0]
        )
        market_trace_replenishment_noisy = market_trace_replenishment_noisy_prompt(
            MARKET_TRACE_REPLENISHMENT_NOISY_CASES[0]
        )
        belief_bargaining = belief_bargaining_prompt(BELIEF_BARGAINING_CASES[0])
        belief_interaction = belief_interaction_prompt(BELIEF_INTERACTION_CASES[0])
        principal = principal_prompt(PRINCIPAL_CASES[0])
        portfolio = portfolio_prompt(PORTFOLIO_CASES[0])
        revealed_allocation = revealed_allocation_prompt(REVEALED_ALLOCATION_CASES[0])
        principal_holding = principal_holding_prompt(PRINCIPAL_HOLDING_CASES[0])
        noisy_principal_holding = noisy_principal_holding_prompt(NOISY_PRINCIPAL_HOLDING_CASES[0])
        principal_holding_notes_prompts = [
            principal_holding_notes_prompt(case) for case in PRINCIPAL_HOLDING_NOTES_CASES
        ]
        principal_holding_blind_notes_prompts = [
            principal_holding_blind_notes_prompt(case)
            for case in PRINCIPAL_HOLDING_BLIND_NOTES_CASES
        ]
        ambiguity = ambiguity_prompt(AMBIGUITY_CASES[0])
        matching = matching_prompt(MATCHING_CASES[0])
        screening = screening_prompt(SCREENING_CASES[0])
        moral_hazard = moral_hazard_prompt(MORAL_HAZARD_CASES[0])
        common_value = common_value_prompt(COMMON_VALUE_CASES[0])
        mechanism = mechanism_prompt(MECHANISM_CASES[0])
        mechanism_repeated = mechanism_repeated_prompt(MECHANISM_REPEATED_CASES[0])
        mechanism_repeated_natural = mechanism_repeated_natural_prompt(MECHANISM_REPEATED_CASES[0])
        mechanism_response = mechanism_response_prompt(MECHANISM_RESPONSE_CASES[0])
        mechanism_elasticity = mechanism_elasticity_prompt(MECHANISM_RESPONSE_CASES[0])
        mechanism_strategic_response = mechanism_strategic_response_prompt(MECHANISM_STRATEGIC_CASES[0])
        mechanism_strategic_equilibrium = mechanism_strategic_equilibrium_prompt(MECHANISM_STRATEGIC_CASES[0])
        mechanism_interaction_trace = mechanism_interaction_trace_prompt(MECHANISM_TRACE_CASES[0])
        mechanism_trace_equilibrium = mechanism_trace_equilibrium_prompt(
            MECHANISM_TRACE_EQUILIBRIUM_CASES[0]
        )
        mechanism_trace_equilibrium_natural = mechanism_trace_equilibrium_natural_prompt(
            MECHANISM_TRACE_EQUILIBRIUM_CASES[0]
        )
        mechanism_trace_equilibrium_noisy = mechanism_trace_equilibrium_noisy_prompt(
            MECHANISM_TRACE_EQUILIBRIUM_NOISY_CASES[0]
        )
        experiment = experiment_prompt(EXPERIMENT_CASES[0])
        retail = retail_prompt(RETAIL_CASES[-1])
        supplier_scam = supplier_scam_prompt(
            SUPPLIER_SCAM_CASES[0],
            SUPPLIER_SCAM_CASES[0].rounds[0],
            1,
            SUPPLIER_SCAM_CASES[0].initial_cash,
        )
        supplier_scam_natural = supplier_scam_natural_prompt(
            SUPPLIER_SCAM_CASES[0],
            SUPPLIER_SCAM_CASES[0].rounds[0],
            1,
            SUPPLIER_SCAM_CASES[0].initial_cash,
        )
        self.assertNotIn("oracle", regime)
        self.assertNotIn("oracle", regime_relationship)
        self.assertNotIn("oracle", regime_holdout)
        self.assertNotIn("oracle", regime_law_audit)
        self.assertNotIn("oracle", alignment_tax)
        self.assertNotIn("oracle", procurement)
        self.assertNotIn("oracle", procurement_bundle)
        self.assertNotIn("oracle", procurement_bundle_natural)
        self.assertNotIn("oracle", procurement_bundle_evidence)
        self.assertNotIn("oracle", procurement_bundle_noisy_evidence)
        self.assertNotIn("oracle", procurement_bundle_history)
        self.assertNotIn("oracle", procurement_bundle_reserve)
        self.assertNotIn("oracle", procurement_vendor_update)
        self.assertNotIn("oracle", procurement_counterfactual)
        self.assertNotIn("oracle", pricing)
        self.assertNotIn("oracle", pricing_counterfactual)
        self.assertNotIn("oracle", pricing_cross)
        self.assertNotIn("oracle", pricing_multi)
        self.assertNotIn("oracle", pricing_multi_natural)
        self.assertNotIn("oracle", pricing_multi_capacity)
        self.assertNotIn("oracle", pricing_multi_capacity_noisy)
        self.assertNotIn("oracle", pricing_inventory_markdown)
        self.assertNotIn("oracle", pricing_inventory_markdown_noisy)
        self.assertNotIn("oracle", pricing_multi_markdown_noisy)
        self.assertNotIn("oracle", pricing_inventory_replenishment_noisy)
        self.assertNotIn("oracle", pricing_hidden_intervention)
        self.assertNotIn("oracle", pricing_law_audit)
        self.assertNotIn("oracle", pricing_evidence_law)
        self.assertNotIn("oracle", pricing_evidence_holdout)
        self.assertNotIn("oracle", strategic)
        self.assertNotIn("oracle", forecast)
        self.assertNotIn("oracle", forecast_aggregate)
        self.assertNotIn("oracle", forecast_curve)
        self.assertNotIn("oracle", forecast_curve_implicit)
        self.assertNotIn("oracle", forecast_curve_noisy)
        self.assertNotIn("oracle", forecast_curve_natural)
        self.assertNotIn("oracle", forecast_shift)
        self.assertNotIn("oracle", forecast_rolling)
        self.assertNotIn("oracle", forecast_rolling_log)
        self.assertNotIn("oracle", forecast_rolling_noisy_log)
        self.assertNotIn("oracle", forecast_event_log)
        self.assertNotIn("oracle", forecast_operational_log)
        self.assertNotIn("oracle", exploration)
        self.assertNotIn("oracle", market_policy)
        self.assertNotIn("oracle", market_policy_inventory)
        self.assertNotIn("oracle", market_trace_inventory)
        self.assertNotIn("oracle", market_trace_markdown)
        self.assertNotIn("oracle", market_trace_replenishment)
        self.assertNotIn("oracle", market_trace_replenishment_natural)
        self.assertNotIn("oracle", market_trace_replenishment_noisy)
        self.assertNotIn("oracle", belief_bargaining)
        self.assertNotIn("oracle", belief_interaction)
        self.assertNotIn("oracle", principal)
        self.assertNotIn("oracle", portfolio)
        self.assertNotIn("oracle", revealed_allocation)
        self.assertNotIn("oracle", principal_holding)
        self.assertNotIn("oracle", noisy_principal_holding)
        for principal_holding_notes in principal_holding_notes_prompts:
            self.assertNotIn("oracle", principal_holding_notes)
            self.assertNotIn("event_type", principal_holding_notes)
            self.assertNotIn("tax_loss", principal_holding_notes)
            self.assertNotIn("index_rebalance", principal_holding_notes)
            self.assertNotIn("redemption", principal_holding_notes)
            self.assertNotIn("fund_flow", principal_holding_notes)
            self.assertNotIn("redeem_to_cash", principal_holding_notes)
            self.assertNotIn("tax_loss_swap", principal_holding_notes)
            self.assertNotIn("meet_redemption", principal_holding_notes)
            self.assertNotIn("client_redemption_trim", principal_holding_notes)
            self.assertNotIn("passive_index_topup", principal_holding_notes)
            self.assertNotIn("risk_committee_index_trim", principal_holding_notes)
        for principal_holding_blind_notes in principal_holding_blind_notes_prompts:
            self.assertNotIn("oracle", principal_holding_blind_notes)
            self.assertNotIn("event_type", principal_holding_blind_notes)
            self.assertNotIn("capital-preservation", principal_holding_blind_notes)
            self.assertNotIn("growth endowment", principal_holding_blind_notes)
            self.assertNotIn("value-disciplined", principal_holding_blind_notes)
            self.assertNotIn("concentrated quality", principal_holding_blind_notes)
            self.assertNotIn("QUALITY_INS", principal_holding_blind_notes)
            self.assertNotIn("AI_BETA", principal_holding_blind_notes)
            self.assertNotIn("BANK_VALUE", principal_holding_blind_notes)
            self.assertNotIn("tax_loss", principal_holding_blind_notes)
            self.assertNotIn("index_rebalance", principal_holding_blind_notes)
            self.assertNotIn("redemption", principal_holding_blind_notes)
            self.assertNotIn("fund_flow", principal_holding_blind_notes)
        self.assertNotIn("oracle", ambiguity)
        self.assertNotIn("oracle", matching)
        self.assertNotIn("oracle", screening)
        self.assertNotIn("oracle", moral_hazard)
        self.assertNotIn("oracle", common_value)
        self.assertNotIn("oracle", mechanism)
        self.assertNotIn("oracle", mechanism_repeated)
        self.assertNotIn("oracle", mechanism_repeated_natural)
        self.assertNotIn("oracle", mechanism_response)
        self.assertNotIn("oracle", mechanism_elasticity)
        self.assertNotIn("oracle", mechanism_strategic_response)
        self.assertNotIn("oracle", mechanism_strategic_equilibrium)
        self.assertNotIn("oracle", mechanism_interaction_trace)
        self.assertNotIn("oracle", mechanism_trace_equilibrium)
        self.assertNotIn("oracle", mechanism_trace_equilibrium_natural)
        self.assertNotIn("oracle", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("oracle", experiment)
        self.assertNotIn("oracle", retail)
        self.assertNotIn("oracle", supplier_scam)
        self.assertNotIn("oracle", supplier_scam_natural)
        self.assertNotIn("kelly_fraction", regime)
        self.assertNotIn("kelly_fraction", regime_relationship)
        self.assertNotIn("kelly_fraction", regime_holdout)
        self.assertNotIn("kelly_fraction", regime_law_audit)
        self.assertNotIn("oracle_price", pricing)
        self.assertNotIn("oracle_price", pricing_counterfactual)
        self.assertNotIn("oracle_price", pricing_cross)
        self.assertNotIn("oracle_price", pricing_multi)
        self.assertNotIn("oracle_price", pricing_multi_natural)
        self.assertNotIn("oracle_price", pricing_multi_capacity)
        self.assertNotIn("oracle_price", pricing_multi_capacity_noisy)
        self.assertNotIn("oracle_price", pricing_inventory_markdown)
        self.assertNotIn("oracle_price", pricing_inventory_markdown_noisy)
        self.assertNotIn("oracle_price", pricing_multi_markdown_noisy)
        self.assertNotIn("oracle_price", pricing_inventory_replenishment_noisy)
        self.assertNotIn("oracle_price", pricing_hidden_intervention)
        self.assertNotIn("oracle_price", pricing_law_audit)
        self.assertNotIn("oracle_price", pricing_evidence_law)
        self.assertNotIn("oracle_price", pricing_evidence_holdout)
        self.assertNotIn("oracle_price", market_policy_inventory)
        self.assertNotIn("oracle_price", market_trace_inventory)
        self.assertNotIn("oracle_price", market_trace_markdown)
        self.assertNotIn("oracle_price", market_trace_replenishment)
        self.assertNotIn("oracle_price", market_trace_replenishment_natural)
        self.assertNotIn("oracle_price", market_trace_replenishment_noisy)
        self.assertNotIn("opponent_price", market_trace_replenishment_natural)
        self.assertNotIn("opponent_price", market_trace_replenishment_noisy)
        self.assertNotIn("opponent_fill_rate", market_trace_replenishment_natural)
        self.assertNotIn("opponent_fill_rate", market_trace_replenishment_noisy)
        self.assertNotIn("opponent_remaining_inventory_share", market_trace_replenishment_natural)
        self.assertNotIn("opponent_remaining_inventory_share", market_trace_replenishment_noisy)
        self.assertNotIn("replenishment_unit_cost", market_trace_replenishment_natural)
        self.assertNotIn("replenishment_unit_cost", market_trace_replenishment_noisy)
        self.assertNotIn("replenishment_setup_cost", market_trace_replenishment_natural)
        self.assertNotIn("replenishment_setup_cost", market_trace_replenishment_noisy)
        self.assertNotIn("max_replenishment_units", market_trace_replenishment_natural)
        self.assertNotIn("max_replenishment_units", market_trace_replenishment_noisy)
        self.assertNotIn("replenishment_storage_capacity", market_trace_replenishment_natural)
        self.assertNotIn("replenishment_storage_capacity", market_trace_replenishment_noisy)
        self.assertNotIn("raw_mean_probability", forecast_curve_natural)
        self.assertNotIn("observed_event_count", forecast_curve_natural)
        self.assertNotIn("first_period_revenue", mechanism_repeated_natural)
        self.assertNotIn("manipulation_growth", mechanism_repeated_natural)
        self.assertNotIn("best_mechanism", mechanism_response)
        self.assertNotIn("base_stay_rate", mechanism_elasticity)
        self.assertNotIn("take_exit_sensitivity", mechanism_elasticity)
        self.assertNotIn("trust_decay", mechanism_elasticity)
        self.assertNotIn("best_mechanism", mechanism_strategic_response)
        self.assertNotIn("best_mechanism", mechanism_strategic_equilibrium)
        self.assertNotIn("best_mechanism", mechanism_interaction_trace)
        self.assertNotIn("best_mechanism", mechanism_trace_equilibrium)
        self.assertNotIn("best_mechanism", mechanism_trace_equilibrium_natural)
        self.assertNotIn("best_mechanism", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("mechanism_id=", mechanism_trace_equilibrium_natural)
        self.assertNotIn("mechanism_id=", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("sponsor_take", mechanism_trace_equilibrium_natural)
        self.assertNotIn("sponsor_take", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("strategic_gain", mechanism_trace_equilibrium_natural)
        self.assertNotIn("strategic_gain", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("peer_contagion", mechanism_trace_equilibrium_natural)
        self.assertNotIn("peer_contagion", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("audit_strength", mechanism_trace_equilibrium_natural)
        self.assertNotIn("audit_strength", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("detection_cost", mechanism_trace_equilibrium_natural)
        self.assertNotIn("detection_cost", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("response_update_rate", mechanism_trace_equilibrium_natural)
        self.assertNotIn("response_update_rate", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("active_participants", mechanism_trace_equilibrium_natural)
        self.assertNotIn("active_participants", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("strategic_share", mechanism_trace_equilibrium_natural)
        self.assertNotIn("strategic_share", mechanism_trace_equilibrium_noisy)
        self.assertNotIn("compatibility bonuses", procurement_bundle_natural.lower())
        self.assertNotIn("durability_weight", procurement_bundle_natural)
        self.assertNotIn("price_weight", procurement_bundle_natural)
        self.assertNotIn("compatibility bonuses", procurement_bundle_evidence.lower())
        self.assertNotIn("service_fit_delta", procurement_bundle_evidence)
        self.assertNotIn("bonus=", procurement_bundle_evidence)
        self.assertNotIn("durability_weight", procurement_bundle_evidence)
        self.assertNotIn("price_weight", procurement_bundle_evidence)
        self.assertNotIn("compatibility bonuses", procurement_bundle_noisy_evidence.lower())
        self.assertNotIn("service_fit_delta", procurement_bundle_noisy_evidence)
        self.assertNotIn("bonus=", procurement_bundle_noisy_evidence)
        self.assertNotIn("durability_weight", procurement_bundle_noisy_evidence)
        self.assertNotIn("price_weight", procurement_bundle_noisy_evidence)
        self.assertNotIn("compatibility bonuses", procurement_bundle_history.lower())
        self.assertNotIn("service_fit_delta", procurement_bundle_history)
        self.assertNotIn("bonus=", procurement_bundle_history)
        self.assertNotIn("durability_weight", procurement_bundle_history)
        self.assertNotIn("price_weight", procurement_bundle_history)
        self.assertNotIn("compatibility bonuses", procurement_bundle_reserve.lower())
        self.assertNotIn("service_fit_delta", procurement_bundle_reserve)
        self.assertNotIn("bonus=", procurement_bundle_reserve)
        self.assertNotIn("durability_weight", procurement_bundle_reserve)
        self.assertNotIn("price_weight", procurement_bundle_reserve)
        self.assertNotIn("oracle_plan", procurement_vendor_update)
        self.assertNotIn("expected_reliability", procurement_vendor_update)
        self.assertNotIn("score_regret", procurement_vendor_update)
        self.assertNotIn("oracle", procurement_vendor_update_noisy)
        self.assertNotIn("oracle_plan", procurement_vendor_update_noisy)
        self.assertNotIn("expected_reliability", procurement_vendor_update_noisy)
        self.assertNotIn("score_regret", procurement_vendor_update_noisy)

    def test_offline_sweep_ranks_interaction_plan_above_single_offer(self):
        sweep = run_sweep(
            task="belief_bargaining_interaction",
            agent_specs=["offline:oracle", "offline:single_offer"],
        )
        rows = rank_rows(comparison_table(sweep))
        belief_rows = [row for row in rows if row["task"] == "belief_bargaining_interaction"]
        self.assertEqual(belief_rows[0]["agent"], "offline:oracle")
        self.assertEqual(belief_rows[1]["agent"], "offline:single_offer")

    def test_rank_rows_keeps_missing_metrics_last(self):
        rows = [
            {"agent": "missing", "task": "procurement", "metric": "accuracy", "direction": "higher", "value": None},
            {"agent": "low", "task": "procurement", "metric": "accuracy", "direction": "higher", "value": 0.25},
            {"agent": "high", "task": "procurement", "metric": "accuracy", "direction": "higher", "value": 0.75},
        ]
        ranked = rank_rows(rows)
        self.assertEqual([row["agent"] for row in ranked], ["high", "low", "missing"])

    def test_parse_rate_counts_scoreable_chosen_fields(self):
        result = {
            "task": "procurement",
            "trials": [
                {"chosen_product": "a", "chosen_revenue": None},
                {"chosen_product": None, "chosen_revenue": None},
                {"raw_response": "no final answer"},
            ],
        }
        self.assertEqual(parse_rate(result), 0.5)

    def test_sweep_table_surfaces_parse_rate(self):
        sweep = run_sweep(task="procurement", agent_specs=["offline:oracle"])
        rows = comparison_table(sweep)
        self.assertEqual(rows[0]["parse_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()

