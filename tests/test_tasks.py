import unittest
from types import SimpleNamespace

from aeread_lab.models import (
    OfflineAgent,
    OpenAIResponsesAgent,
    _extract_openai_response_text,
    resolve_openai_model,
)
from aeread_lab.reporting import comparison_table, parse_rate, rank_rows
from aeread_lab.runner import run_sweep, run_tasks
from aeread_lab.tasks.adversarial import run_scam_arena
from aeread_lab.tasks.alignment_tax import DEFAULT_CASES as ALIGNMENT_CASES
from aeread_lab.tasks.alignment_tax import _prompt as alignment_tax_prompt
from aeread_lab.tasks.alignment_tax import run_alignment_tax_game
from aeread_lab.tasks.ambiguity import DEFAULT_CASES as AMBIGUITY_CASES
from aeread_lab.tasks.ambiguity import _prompt as ambiguity_prompt
from aeread_lab.tasks.ambiguity import run_ambiguity_game
from aeread_lab.tasks.auction import run_auction_game
from aeread_lab.tasks.bargaining import run_bargaining_game
from aeread_lab.tasks.belief_bargaining import DEFAULT_CASES as BELIEF_BARGAINING_CASES
from aeread_lab.tasks.belief_bargaining import INTERACTION_CASES as BELIEF_INTERACTION_CASES
from aeread_lab.tasks.belief_bargaining import _interaction_prompt as belief_interaction_prompt
from aeread_lab.tasks.belief_bargaining import _prompt as belief_bargaining_prompt
from aeread_lab.tasks.belief_bargaining import run_belief_bargaining_game
from aeread_lab.tasks.belief_bargaining import run_belief_bargaining_interaction_game
from aeread_lab.tasks.common_value import DEFAULT_CASES as COMMON_VALUE_CASES
from aeread_lab.tasks.common_value import _prompt as common_value_prompt
from aeread_lab.tasks.common_value import run_common_value_game
from aeread_lab.tasks.experiment_design import DEFAULT_CASES as EXPERIMENT_CASES
from aeread_lab.tasks.experiment_design import _prompt as experiment_prompt
from aeread_lab.tasks.experiment_design import run_experiment_design_game
from aeread_lab.tasks.exploration import DEFAULT_CASES as EXPLORATION_CASES
from aeread_lab.tasks.exploration import _prompt as exploration_prompt
from aeread_lab.tasks.exploration import run_exploration_game
from aeread_lab.tasks.forecast_calibration import AGGREGATE_CASES as FORECAST_AGGREGATE_CASES
from aeread_lab.tasks.forecast_calibration import CURVE_CASES as FORECAST_CURVE_CASES
from aeread_lab.tasks.forecast_calibration import DEFAULT_CASES as FORECAST_CASES
from aeread_lab.tasks.forecast_calibration import NOISY_CURVE_CASES as FORECAST_NOISY_CURVE_CASES
from aeread_lab.tasks.forecast_calibration import SHIFT_CALIBRATION_CASES as FORECAST_SHIFT_CASES
from aeread_lab.tasks.forecast_calibration import _aggregate_prompt as forecast_aggregate_prompt
from aeread_lab.tasks.forecast_calibration import (
    _curve_implicit_prompt as forecast_curve_implicit_prompt,
)
from aeread_lab.tasks.forecast_calibration import _curve_natural_prompt as forecast_curve_natural_prompt
from aeread_lab.tasks.forecast_calibration import _curve_noisy_prompt as forecast_curve_noisy_prompt
from aeread_lab.tasks.forecast_calibration import _curve_prompt as forecast_curve_prompt
from aeread_lab.tasks.forecast_calibration import _prompt as forecast_prompt
from aeread_lab.tasks.forecast_calibration import _shift_prompt as forecast_shift_prompt
from aeread_lab.tasks.forecast_calibration import run_forecast_aggregate_game
from aeread_lab.tasks.forecast_calibration import run_forecast_calibration_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_implicit_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_natural_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_noisy_game
from aeread_lab.tasks.forecast_calibration import run_forecast_shift_calibration_game
from aeread_lab.tasks.market import INVENTORY_POLICY_CASES as MARKET_INVENTORY_POLICY_CASES
from aeread_lab.tasks.market import POLICY_SHIFT_CASES as MARKET_POLICY_CASES
from aeread_lab.tasks.market import TRACE_INVENTORY_CASES as MARKET_TRACE_INVENTORY_CASES
from aeread_lab.tasks.market import TRACE_REPLENISHMENT_CASES as MARKET_TRACE_REPLENISHMENT_CASES
from aeread_lab.tasks.market import _policy_inventory_prompt as market_policy_inventory_prompt
from aeread_lab.tasks.market import _policy_shift_prompt as market_policy_prompt
from aeread_lab.tasks.market import _trace_inventory_prompt as market_trace_inventory_prompt
from aeread_lab.tasks.market import _trace_markdown_prompt as market_trace_markdown_prompt
from aeread_lab.tasks.market import _trace_replenishment_prompt as market_trace_replenishment_prompt
from aeread_lab.tasks.market import (
    run_market_game,
    run_market_policy_inventory_game,
    run_market_policy_shift_game,
    run_market_trace_inventory_game,
    run_market_trace_markdown_game,
    run_market_trace_replenishment_game,
)
from aeread_lab.tasks.matching import DEFAULT_CASES as MATCHING_CASES
from aeread_lab.tasks.matching import _prompt as matching_prompt
from aeread_lab.tasks.matching import run_matching_game
from aeread_lab.tasks.mechanism import DEFAULT_CASES as MECHANISM_CASES
from aeread_lab.tasks.mechanism import INTERACTION_TRACE_CASES as MECHANISM_TRACE_CASES
from aeread_lab.tasks.mechanism import PARTICIPANT_RESPONSE_CASES as MECHANISM_RESPONSE_CASES
from aeread_lab.tasks.mechanism import REPEATED_CASES as MECHANISM_REPEATED_CASES
from aeread_lab.tasks.mechanism import STRATEGIC_RESPONSE_CASES as MECHANISM_STRATEGIC_CASES
from aeread_lab.tasks.mechanism import TRACE_EQUILIBRIUM_CASES as MECHANISM_TRACE_EQUILIBRIUM_CASES
from aeread_lab.tasks.mechanism import _participant_elasticity_prompt as mechanism_elasticity_prompt
from aeread_lab.tasks.mechanism import _participant_response_prompt as mechanism_response_prompt
from aeread_lab.tasks.mechanism import _prompt as mechanism_prompt
from aeread_lab.tasks.mechanism import _repeated_natural_prompt as mechanism_repeated_natural_prompt
from aeread_lab.tasks.mechanism import _repeated_prompt as mechanism_repeated_prompt
from aeread_lab.tasks.mechanism import _strategic_equilibrium_prompt as mechanism_strategic_equilibrium_prompt
from aeread_lab.tasks.mechanism import _strategic_response_prompt as mechanism_strategic_response_prompt
from aeread_lab.tasks.mechanism import _interaction_trace_prompt as mechanism_interaction_trace_prompt
from aeread_lab.tasks.mechanism import _trace_equilibrium_prompt as mechanism_trace_equilibrium_prompt
from aeread_lab.tasks.mechanism import (
    run_mechanism_elasticity_inference_game,
    run_mechanism_game,
    run_mechanism_interaction_trace_game,
    run_mechanism_participant_response_game,
    run_mechanism_repeated_game,
    run_mechanism_repeated_natural_game,
    run_mechanism_strategic_equilibrium_game,
    run_mechanism_strategic_response_game,
    run_mechanism_trace_equilibrium_game,
)
from aeread_lab.tasks.moral_hazard import DEFAULT_CASES as MORAL_HAZARD_CASES
from aeread_lab.tasks.moral_hazard import _prompt as moral_hazard_prompt
from aeread_lab.tasks.moral_hazard import run_moral_hazard_game
from aeread_lab.tasks.portfolio import DEFAULT_CASES as PORTFOLIO_CASES
from aeread_lab.tasks.portfolio import _prompt as portfolio_prompt
from aeread_lab.tasks.portfolio import run_portfolio_game
from aeread_lab.tasks.pricing import COUNTERFACTUAL_SETS as PRICING_COUNTERFACTUAL_SETS
from aeread_lab.tasks.pricing import CROSS_ELASTICITY_CASES as PRICING_CROSS_CASES
from aeread_lab.tasks.pricing import DEFAULT_CASES as PRICING_CASES
from aeread_lab.tasks.pricing import DEFAULT_LAW_CASES as PRICING_LAW_CASES
from aeread_lab.tasks.pricing import EVIDENCE_LAW_CASES as PRICING_EVIDENCE_LAW_CASES
from aeread_lab.tasks.pricing import HOLDOUT_EVIDENCE_LAW_CASES as PRICING_EVIDENCE_HOLDOUT_CASES
from aeread_lab.tasks.pricing import HIDDEN_INTERVENTION_CASES as PRICING_HIDDEN_INTERVENTION_CASES
from aeread_lab.tasks.pricing import INVENTORY_MARKDOWN_CASES as PRICING_INVENTORY_MARKDOWN_CASES
from aeread_lab.tasks.pricing import INVENTORY_MARKDOWN_NOISY_CASES as PRICING_INVENTORY_MARKDOWN_NOISY_CASES
from aeread_lab.tasks.pricing import MULTI_PRODUCT_CAPACITY_CASES as PRICING_MULTI_CAPACITY_CASES
from aeread_lab.tasks.pricing import MULTI_PRODUCT_CASES as PRICING_MULTI_CASES
from aeread_lab.tasks.pricing import _counterfactual_prompt as pricing_counterfactual_prompt
from aeread_lab.tasks.pricing import _cross_elasticity_prompt as pricing_cross_prompt
from aeread_lab.tasks.pricing import _evidence_law_audit_prompt as pricing_evidence_law_prompt
from aeread_lab.tasks.pricing import _inventory_markdown_noisy_prompt as pricing_inventory_markdown_noisy_prompt
from aeread_lab.tasks.pricing import _inventory_markdown_prompt as pricing_inventory_markdown_prompt
from aeread_lab.tasks.pricing import _hidden_intervention_prompt as pricing_hidden_intervention_prompt
from aeread_lab.tasks.pricing import _law_audit_prompt as pricing_law_audit_prompt
from aeread_lab.tasks.pricing import _multi_product_capacity_prompt as pricing_multi_capacity_prompt
from aeread_lab.tasks.pricing import _multi_product_natural_prompt as pricing_multi_natural_prompt
from aeread_lab.tasks.pricing import _multi_product_prompt as pricing_multi_prompt
from aeread_lab.tasks.pricing import _prompt as pricing_prompt
from aeread_lab.tasks.pricing import run_pricing_counterfactual_game
from aeread_lab.tasks.pricing import run_pricing_cross_elasticity_game
from aeread_lab.tasks.pricing import run_pricing_evidence_law_audit_game
from aeread_lab.tasks.pricing import run_pricing_evidence_law_holdout_game
from aeread_lab.tasks.pricing import run_pricing_game
from aeread_lab.tasks.pricing import run_pricing_hidden_intervention_game
from aeread_lab.tasks.pricing import run_pricing_inventory_markdown_game
from aeread_lab.tasks.pricing import run_pricing_inventory_markdown_noisy_game
from aeread_lab.tasks.pricing import run_pricing_law_audit_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_capacity_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_natural_game
from aeread_lab.tasks.principal_inference import DEFAULT_CASES as PRINCIPAL_CASES
from aeread_lab.tasks.principal_inference import _prompt as principal_prompt
from aeread_lab.tasks.principal_inference import run_principal_inference_game
from aeread_lab.tasks.procurement import COUNTERFACTUAL_SETS
from aeread_lab.tasks.procurement import DEFAULT_CASES as PROCUREMENT_CASES
from aeread_lab.tasks.procurement import PROCUREMENT_BUNDLE_CASES
from aeread_lab.tasks.procurement import PROCUREMENT_VENDOR_UPDATE_CASES
from aeread_lab.tasks.procurement import _bundle_evidence_prompt as procurement_bundle_evidence_prompt
from aeread_lab.tasks.procurement import _bundle_history_prompt as procurement_bundle_history_prompt
from aeread_lab.tasks.procurement import _bundle_natural_prompt as procurement_bundle_natural_prompt
from aeread_lab.tasks.procurement import _bundle_noisy_evidence_prompt as procurement_bundle_noisy_evidence_prompt
from aeread_lab.tasks.procurement import _bundle_prompt as procurement_bundle_prompt
from aeread_lab.tasks.procurement import _bundle_reserve_prompt as procurement_bundle_reserve_prompt
from aeread_lab.tasks.procurement import _prompt as procurement_prompt
from aeread_lab.tasks.procurement import _vendor_update_prompt as procurement_vendor_update_prompt
from aeread_lab.tasks.procurement import run_procurement_bundle_evidence_game
from aeread_lab.tasks.procurement import run_procurement_bundle_game
from aeread_lab.tasks.procurement import run_procurement_bundle_history_game
from aeread_lab.tasks.procurement import run_procurement_bundle_natural_game
from aeread_lab.tasks.procurement import run_procurement_bundle_noisy_evidence_game
from aeread_lab.tasks.procurement import run_procurement_bundle_reserve_game
from aeread_lab.tasks.procurement import run_procurement_counterfactual_game
from aeread_lab.tasks.procurement import run_procurement_game
from aeread_lab.tasks.procurement import run_procurement_vendor_update_game
from aeread_lab.tasks.regime import (
    DEFAULT_GAMBLES,
    DEFAULT_HOLDOUT_GAMBLES,
    DEFAULT_LAW_AUDIT_CASES,
    DEFAULT_RELATIONSHIP_GAMBLES,
    _holdout_prompt as regime_holdout_prompt,
    _law_audit_prompt as regime_law_audit_prompt,
    _prompt as regime_prompt,
    _relationship_prompt as regime_relationship_prompt,
    run_regime_holdout_verifier,
    run_regime_law_audit_game,
    run_regime_relationship_verifier,
)
from aeread_lab.tasks.revealed_allocation import DEFAULT_CASES as REVEALED_ALLOCATION_CASES
from aeread_lab.tasks.revealed_allocation import _prompt as revealed_allocation_prompt
from aeread_lab.tasks.revealed_allocation import run_revealed_allocation_game
from aeread_lab.tasks.retail import DEFAULT_CASES as RETAIL_CASES
from aeread_lab.tasks.retail import _prompt as retail_prompt
from aeread_lab.tasks.retail import run_retail_game
from aeread_lab.tasks.screening import DEFAULT_CASES as SCREENING_CASES
from aeread_lab.tasks.screening import _prompt as screening_prompt
from aeread_lab.tasks.screening import run_screening_game
from aeread_lab.tasks.strategic_drift import DEFAULT_CASES as DRIFT_CASES
from aeread_lab.tasks.strategic_drift import _prompt as strategic_prompt
from aeread_lab.tasks.strategic_drift import run_strategic_drift_game
from aeread_lab.tasks.supplier_scam import DEFAULT_CASES as SUPPLIER_SCAM_CASES
from aeread_lab.tasks.supplier_scam import _natural_prompt as supplier_scam_natural_prompt
from aeread_lab.tasks.supplier_scam import _prompt as supplier_scam_prompt
from aeread_lab.tasks.supplier_scam import run_supplier_scam_game
from aeread_lab.tasks.supplier_scam import run_supplier_scam_natural_game


class TaskSmokeTests(unittest.TestCase):
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

    def test_sample_limit_slices_regime_gambles(self):
        sweep = run_sweep(task="regime", agent_specs=["offline:oracle"], sample_limit=1)
        result = sweep["runs"][0]["results"][0]
        self.assertEqual(sweep["sample_limit"], 1)
        self.assertEqual(result["n_trials"], 4)

    def test_sample_limit_slices_regime_relationship_gambles(self):
        sweep = run_sweep(task="regime_relationship", agent_specs=["offline:oracle"], sample_limit=1)
        result = sweep["runs"][0]["results"][0]
        self.assertEqual(sweep["sample_limit"], 1)
        self.assertEqual(result["n_groups"], 1)
        self.assertEqual(result["n_trials"], 4)

    def test_sample_limit_slices_regime_holdout_gambles(self):
        sweep = run_sweep(task="regime_holdout", agent_specs=["offline:oracle"], sample_limit=1)
        result = sweep["runs"][0]["results"][0]
        self.assertEqual(sweep["sample_limit"], 1)
        self.assertEqual(result["n_groups"], 1)
        self.assertEqual(result["n_trials"], 4)

    def test_sample_limit_slices_regime_law_audit_cases(self):
        sweep = run_sweep(task="regime_law_audit", agent_specs=["offline:oracle"], sample_limit=1)
        result = sweep["runs"][0]["results"][0]
        self.assertEqual(sweep["sample_limit"], 1)
        self.assertEqual(result["n_trials"], 1)
        self.assertEqual(result["accuracy"], 1.0)

    def test_sample_limit_slices_task_cases(self):
        results = run_tasks("procurement", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_sample_limit_slices_counterfactual_sets(self):
        results = run_tasks("procurement_counterfactual", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_sets"], 1)
        self.assertEqual(results[0]["n_trials"], 3)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_sample_limit_slices_pricing_counterfactual_sets(self):
        results = run_tasks("pricing_counterfactual", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_sets"], 1)
        self.assertEqual(results[0]["n_trials"], 2)
        self.assertEqual(results[0]["counterfactual_shift_miss_rate"], 0.0)

    def test_sample_limit_slices_pricing_cross_elasticity_cases(self):
        results = run_tasks("pricing_cross_elasticity", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_absolute_price_error"], 0.01)

    def test_sample_limit_slices_pricing_multi_product_cases(self):
        results = run_tasks("pricing_multi_product", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_price_l1_error"], 0.01)

    def test_sample_limit_slices_pricing_multi_product_natural_cases(self):
        results = run_tasks("pricing_multi_product_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_price_l1_error"], 0.01)

    def test_sample_limit_slices_pricing_multi_product_capacity_cases(self):
        results = run_tasks("pricing_multi_product_capacity", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_price_l1_error"], 0.01)

    def test_sample_limit_slices_pricing_inventory_markdown_cases(self):
        results = run_tasks("pricing_inventory_markdown", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_price_l1_error"], 0.01)

    def test_sample_limit_slices_pricing_inventory_markdown_noisy_cases(self):
        results = run_tasks("pricing_inventory_markdown_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_price_l1_error"], 0.01)

    def test_sample_limit_slices_pricing_hidden_intervention_cases(self):
        results = run_tasks("pricing_hidden_intervention", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_absolute_price_error"], 0.01)

    def test_sample_limit_slices_pricing_law_audit_cases(self):
        results = run_tasks("pricing_law_audit", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_sample_limit_slices_pricing_evidence_law_audit_cases(self):
        results = run_tasks("pricing_evidence_law_audit", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_sample_limit_slices_pricing_evidence_law_holdout_cases(self):
        results = run_tasks("pricing_evidence_law_holdout", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_sample_limit_slices_forecast_aggregate_cases(self):
        results = run_tasks("forecast_aggregate", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_cases(self):
        results = run_tasks("forecast_curve", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_implicit_cases(self):
        results = run_tasks("forecast_curve_implicit", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_noisy_cases(self):
        results = run_tasks("forecast_curve_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_natural_cases(self):
        results = run_tasks("forecast_curve_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_shift_calibration_cases(self):
        results = run_tasks("forecast_shift_calibration", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_belief_bargaining_interaction_cases(self):
        results = run_tasks("belief_bargaining_interaction", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_surplus_gap"], 1e-9)

    def test_sample_limit_slices_market_policy_shift_cases(self):
        results = run_tasks("market_policy_shift", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_profit_regret"], 1e-9)

    def test_sample_limit_slices_market_policy_inventory_cases(self):
        results = run_tasks("market_policy_inventory", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-9)

    def test_sample_limit_slices_market_trace_inventory_cases(self):
        results = run_tasks("market_trace_inventory", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-9)

    def test_sample_limit_slices_market_trace_markdown_cases(self):
        results = run_tasks("market_trace_markdown", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-6)

    def test_sample_limit_slices_market_trace_replenishment_cases(self):
        results = run_tasks("market_trace_replenishment", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-6)

    def test_sample_limit_slices_procurement_bundle_cases(self):
        results = run_tasks("procurement_bundle", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_procurement_bundle_natural_cases(self):
        results = run_tasks("procurement_bundle_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_procurement_bundle_evidence_cases(self):
        results = run_tasks("procurement_bundle_evidence", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_procurement_bundle_noisy_evidence_cases(self):
        results = run_tasks("procurement_bundle_noisy_evidence", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_procurement_bundle_history_cases(self):
        results = run_tasks("procurement_bundle_history", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_procurement_bundle_reserve_cases(self):
        results = run_tasks("procurement_bundle_reserve", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_procurement_vendor_update_cases(self):
        results = run_tasks("procurement_vendor_update", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_repeated_cases(self):
        results = run_tasks("mechanism_repeated", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_repeated_natural_cases(self):
        results = run_tasks("mechanism_repeated_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_participant_response_cases(self):
        results = run_tasks("mechanism_participant_response", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_elasticity_inference_cases(self):
        results = run_tasks("mechanism_elasticity_inference", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_strategic_response_cases(self):
        results = run_tasks("mechanism_strategic_response", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_strategic_equilibrium_cases(self):
        results = run_tasks("mechanism_strategic_equilibrium", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_interaction_trace_cases(self):
        results = run_tasks("mechanism_interaction_trace", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_trace_equilibrium_cases(self):
        results = run_tasks("mechanism_trace_equilibrium", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_supplier_scam_natural_cases(self):
        results = run_tasks("supplier_scam_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], len(SUPPLIER_SCAM_CASES[0].rounds))
        self.assertLess(results[0]["mean_constrained_final_cash_regret"], 1e-9)

    def test_procurement_oracle_offline(self):
        summary = run_procurement_game(OfflineAgent("oracle"))
        self.assertEqual(summary["accuracy"], 1.0)

    def test_procurement_counterfactual_flags_preference_stickiness(self):
        configured = run_procurement_counterfactual_game(OfflineAgent("oracle"))
        comfort = run_procurement_counterfactual_game(OfflineAgent("comfort"))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertEqual(configured["paraphrase_correct_rate"], 1.0)
        self.assertEqual(configured["preference_flip_miss_rate"], 0.0)
        self.assertEqual(comfort["paraphrase_inconsistency_rate"], 0.0)
        self.assertEqual(comfort["preference_flip_miss_rate"], 1.0)
        self.assertEqual(comfort["sticky_base_on_flip_rate"], 1.0)

    def test_procurement_bundle_flags_category_and_compatibility_blindness(self):
        configured = run_procurement_bundle_game(OfflineAgent("oracle"))
        category_blind = run_procurement_bundle_game(OfflineAgent("category_blind"))
        compatibility_blind = run_procurement_bundle_game(OfflineAgent("compatibility_blind"))
        cheapest = run_procurement_bundle_game(OfflineAgent("cheapest_pair"))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["invalid_rate"], 0.0)
        self.assertGreater(category_blind["mean_score_regret"], 1.0)
        self.assertGreater(category_blind["category_miss_rate"], 0.2)
        self.assertGreater(compatibility_blind["mean_score_regret"], 0.1)
        self.assertGreater(compatibility_blind["compatibility_blind_miss_rate"], 0.5)
        self.assertGreater(cheapest["mean_score_regret"], 0.5)

    def test_procurement_bundle_natural_flags_compatibility_blindness(self):
        configured = run_procurement_bundle_natural_game(OfflineAgent("oracle"))
        compatibility_blind = run_procurement_bundle_natural_game(OfflineAgent("compatibility_blind"))
        self.assertEqual(configured["task"], "procurement_bundle_natural")
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(compatibility_blind["mean_score_regret"], 0.1)
        self.assertGreater(compatibility_blind["compatibility_blind_miss_rate"], 0.5)

    def test_procurement_bundle_evidence_flags_outcome_blindness(self):
        configured = run_procurement_bundle_evidence_game(OfflineAgent("oracle"))
        compatibility_blind = run_procurement_bundle_evidence_game(OfflineAgent("compatibility_blind"))
        self.assertEqual(configured["task"], "procurement_bundle_evidence")
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["invalid_rate"], 0.0)
        self.assertGreater(compatibility_blind["mean_score_regret"], 0.1)
        self.assertGreater(compatibility_blind["compatibility_blind_miss_rate"], 0.5)

    def test_procurement_bundle_noisy_evidence_flags_outcome_blindness(self):
        configured = run_procurement_bundle_noisy_evidence_game(OfflineAgent("oracle"))
        compatibility_blind = run_procurement_bundle_noisy_evidence_game(OfflineAgent("compatibility_blind"))
        self.assertEqual(configured["task"], "procurement_bundle_noisy_evidence")
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["invalid_rate"], 0.0)
        self.assertGreater(compatibility_blind["mean_score_regret"], 0.1)
        self.assertGreater(compatibility_blind["compatibility_blind_miss_rate"], 0.5)

    def test_procurement_bundle_history_flags_history_blindness(self):
        configured = run_procurement_bundle_history_game(OfflineAgent("oracle"))
        compatibility_blind = run_procurement_bundle_history_game(OfflineAgent("compatibility_blind"))
        self.assertEqual(configured["task"], "procurement_bundle_history")
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["invalid_rate"], 0.0)
        self.assertGreater(compatibility_blind["mean_score_regret"], 0.1)
        self.assertGreater(compatibility_blind["compatibility_blind_miss_rate"], 0.5)

    def test_procurement_bundle_reserve_flags_reserve_blindness(self):
        configured = run_procurement_bundle_reserve_game(OfflineAgent("oracle"))
        compatibility_blind = run_procurement_bundle_reserve_game(OfflineAgent("compatibility_blind"))
        self.assertEqual(configured["task"], "procurement_bundle_reserve")
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["invalid_rate"], 0.0)
        self.assertGreater(compatibility_blind["mean_score_regret"], 0.1)
        self.assertGreater(compatibility_blind["compatibility_blind_miss_rate"], 0.5)

    def test_procurement_vendor_update_flags_reputation_blindness(self):
        configured = run_procurement_vendor_update_game(OfflineAgent("oracle"))
        reputation_blind = run_procurement_vendor_update_game(OfflineAgent("reputation_blind"))
        myopic = run_procurement_vendor_update_game(OfflineAgent("myopic"))
        self.assertEqual(configured["task"], "procurement_vendor_update")
        self.assertEqual(configured["n_trials"], len(PROCUREMENT_VENDOR_UPDATE_CASES))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(reputation_blind["mean_score_regret"], 5.0)
        self.assertGreater(reputation_blind["reputation_blind_miss_rate"], 0.5)
        self.assertGreater(myopic["mean_score_regret"], 1.0)

    def test_pricing_oracle_offline(self):
        summary = run_pricing_game(OfflineAgent("oracle"))
        self.assertLess(summary["mean_revenue_gap"], 1e-9)

    def test_pricing_counterfactual_flags_stale_prices(self):
        configured = run_pricing_counterfactual_game(OfflineAgent("oracle"))
        stale = run_pricing_counterfactual_game(OfflineAgent("stale_price"))
        self.assertLess(configured["mean_absolute_price_error"], 0.01)
        self.assertEqual(configured["counterfactual_shift_miss_rate"], 0.0)
        self.assertGreater(stale["mean_absolute_price_error"], 2.0)
        self.assertEqual(stale["counterfactual_shift_miss_rate"], 1.0)
        self.assertEqual(stale["sticky_base_price_rate"], 1.0)

    def test_pricing_cross_elasticity_flags_own_only_fit(self):
        configured = run_pricing_cross_elasticity_game(OfflineAgent("oracle"))
        own_only = run_pricing_cross_elasticity_game(OfflineAgent("own_only"))
        self.assertEqual(configured["task"], "pricing_cross_elasticity")
        self.assertEqual(configured["n_trials"], len(PRICING_CROSS_CASES))
        self.assertLess(configured["mean_absolute_price_error"], 0.01)
        self.assertEqual(configured["cross_blind_miss_rate"], 0.0)
        self.assertGreater(own_only["mean_absolute_price_error"], 5.0)
        self.assertGreater(own_only["cross_blind_miss_rate"], 0.6)

    def test_pricing_multi_product_flags_independent_pricing(self):
        configured = run_pricing_multi_product_game(OfflineAgent("oracle"))
        independent = run_pricing_multi_product_game(OfflineAgent("independent"))
        self.assertEqual(configured["task"], "pricing_multi_product")
        self.assertEqual(configured["n_trials"], len(PRICING_MULTI_CASES))
        self.assertLess(configured["mean_price_l1_error"], 0.01)
        self.assertEqual(configured["independent_miss_rate"], 0.0)
        self.assertGreater(independent["mean_price_l1_error"], 8.0)
        self.assertGreater(independent["independent_miss_rate"], 0.6)

    def test_pricing_multi_product_natural_flags_independent_pricing(self):
        configured = run_pricing_multi_product_natural_game(OfflineAgent("oracle"))
        independent = run_pricing_multi_product_natural_game(OfflineAgent("independent"))
        self.assertEqual(configured["task"], "pricing_multi_product_natural")
        self.assertEqual(configured["n_trials"], len(PRICING_MULTI_CASES))
        self.assertLess(configured["mean_price_l1_error"], 0.01)
        self.assertEqual(configured["independent_miss_rate"], 0.0)
        self.assertGreater(independent["mean_price_l1_error"], 8.0)
        self.assertGreater(independent["independent_miss_rate"], 0.6)

    def test_pricing_multi_product_capacity_flags_capacity_blind_pricing(self):
        configured = run_pricing_multi_product_capacity_game(OfflineAgent("oracle"))
        capacity_blind = run_pricing_multi_product_capacity_game(OfflineAgent("capacity_blind"))
        independent = run_pricing_multi_product_capacity_game(OfflineAgent("independent"))
        self.assertEqual(configured["task"], "pricing_multi_product_capacity")
        self.assertEqual(configured["n_trials"], len(PRICING_MULTI_CAPACITY_CASES))
        self.assertLess(configured["mean_price_l1_error"], 0.01)
        self.assertEqual(configured["capacity_blind_miss_rate"], 0.0)
        self.assertGreater(capacity_blind["mean_price_l1_error"], 5.0)
        self.assertGreater(capacity_blind["capacity_blind_miss_rate"], 0.5)
        self.assertGreater(independent["mean_price_l1_error"], 5.0)

    def test_pricing_inventory_markdown_flags_myopic_pricing(self):
        configured = run_pricing_inventory_markdown_game(OfflineAgent("oracle"))
        myopic = run_pricing_inventory_markdown_game(OfflineAgent("myopic"))
        self.assertEqual(configured["task"], "pricing_inventory_markdown")
        self.assertEqual(configured["n_trials"], len(PRICING_INVENTORY_MARKDOWN_CASES))
        self.assertLess(configured["mean_price_l1_error"], 0.01)
        self.assertEqual(configured["myopic_miss_rate"], 0.0)
        self.assertGreater(myopic["mean_price_l1_error"], 5.0)
        self.assertGreater(myopic["myopic_miss_rate"], 0.5)

    def test_pricing_inventory_markdown_noisy_flags_myopic_pricing(self):
        configured = run_pricing_inventory_markdown_noisy_game(OfflineAgent("oracle"))
        myopic = run_pricing_inventory_markdown_noisy_game(OfflineAgent("myopic"))
        self.assertEqual(configured["task"], "pricing_inventory_markdown_noisy")
        self.assertEqual(configured["n_trials"], len(PRICING_INVENTORY_MARKDOWN_NOISY_CASES))
        self.assertLess(configured["mean_price_l1_error"], 0.01)
        self.assertEqual(configured["myopic_miss_rate"], 0.0)
        self.assertGreater(myopic["mean_price_l1_error"], 5.0)
        self.assertGreater(myopic["myopic_miss_rate"], 0.5)

    def test_pricing_hidden_intervention_flags_lift_blind_pricing(self):
        configured = run_pricing_hidden_intervention_game(OfflineAgent("oracle"))
        blind = run_pricing_hidden_intervention_game(OfflineAgent("intervention_blind"))
        rounded = run_pricing_hidden_intervention_game(OfflineAgent("round"))
        self.assertEqual(configured["task"], "pricing_hidden_intervention")
        self.assertEqual(configured["n_trials"], len(PRICING_HIDDEN_INTERVENTION_CASES))
        self.assertLess(configured["mean_absolute_price_error"], 0.01)
        self.assertGreater(blind["mean_absolute_price_error"], 25.0)
        self.assertGreater(blind["mean_revenue_gap"], 1000.0)
        self.assertEqual(blind["intervention_blind_miss_rate"], 1.0)
        self.assertLess(rounded["mean_absolute_price_error"], blind["mean_absolute_price_error"])

    def test_pricing_law_audit_flags_invalid_acceptance(self):
        configured = run_pricing_law_audit_game(OfflineAgent("oracle"))
        accept = run_pricing_law_audit_game(OfflineAgent("law_accept"))
        reject = run_pricing_law_audit_game(OfflineAgent("law_reject"))
        inverted = run_pricing_law_audit_game(OfflineAgent("law_invert"))
        self.assertEqual(configured["task"], "pricing_law_audit")
        self.assertEqual(configured["n_trials"], len(PRICING_LAW_CASES))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertEqual(configured["invalid_accept_rate"], 0.0)
        self.assertEqual(configured["valid_reject_rate"], 0.0)
        self.assertGreater(accept["invalid_accept_rate"], 0.9)
        self.assertGreater(reject["valid_reject_rate"], 0.9)
        self.assertEqual(inverted["accuracy"], 0.0)

    def test_pricing_evidence_law_audit_flags_invalid_acceptance(self):
        configured = run_pricing_evidence_law_audit_game(OfflineAgent("oracle"))
        accept = run_pricing_evidence_law_audit_game(OfflineAgent("law_accept"))
        reject = run_pricing_evidence_law_audit_game(OfflineAgent("law_reject"))
        inverted = run_pricing_evidence_law_audit_game(OfflineAgent("law_invert"))
        self.assertEqual(configured["task"], "pricing_evidence_law_audit")
        self.assertEqual(configured["n_trials"], len(PRICING_EVIDENCE_LAW_CASES))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertEqual(configured["invalid_accept_rate"], 0.0)
        self.assertEqual(configured["valid_reject_rate"], 0.0)
        self.assertGreater(accept["invalid_accept_rate"], 0.9)
        self.assertGreater(reject["valid_reject_rate"], 0.9)
        self.assertEqual(inverted["accuracy"], 0.0)

    def test_pricing_evidence_law_holdout_flags_invalid_acceptance(self):
        configured = run_pricing_evidence_law_holdout_game(OfflineAgent("oracle"))
        accept = run_pricing_evidence_law_holdout_game(OfflineAgent("law_accept"))
        reject = run_pricing_evidence_law_holdout_game(OfflineAgent("law_reject"))
        inverted = run_pricing_evidence_law_holdout_game(OfflineAgent("law_invert"))
        self.assertEqual(configured["task"], "pricing_evidence_law_holdout")
        self.assertGreater(len(PRICING_EVIDENCE_HOLDOUT_CASES), len(PRICING_EVIDENCE_LAW_CASES))
        self.assertEqual(configured["n_trials"], len(PRICING_EVIDENCE_HOLDOUT_CASES))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertEqual(configured["invalid_accept_rate"], 0.0)
        self.assertEqual(configured["valid_reject_rate"], 0.0)
        self.assertGreater(accept["invalid_accept_rate"], 0.9)
        self.assertGreater(reject["valid_reject_rate"], 0.9)
        self.assertEqual(inverted["accuracy"], 0.0)

    def test_pricing_law_case_ids_do_not_leak_labels(self):
        for case in [*PRICING_LAW_CASES, *PRICING_EVIDENCE_LAW_CASES, *PRICING_EVIDENCE_HOLDOUT_CASES]:
            self.assertNotIn("valid", case.key)
            self.assertNotIn("invalid", case.key)

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
        pricing_inventory_markdown = pricing_inventory_markdown_prompt(PRICING_INVENTORY_MARKDOWN_CASES[0])
        pricing_inventory_markdown_noisy = pricing_inventory_markdown_noisy_prompt(
            PRICING_INVENTORY_MARKDOWN_NOISY_CASES[0]
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
        exploration = exploration_prompt(EXPLORATION_CASES[0])
        market_policy = market_policy_prompt(MARKET_POLICY_CASES[0])
        market_policy_inventory = market_policy_inventory_prompt(MARKET_INVENTORY_POLICY_CASES[0])
        market_trace_inventory = market_trace_inventory_prompt(MARKET_TRACE_INVENTORY_CASES[0])
        market_trace_markdown = market_trace_markdown_prompt(MARKET_TRACE_INVENTORY_CASES[0])
        market_trace_replenishment = market_trace_replenishment_prompt(
            MARKET_TRACE_REPLENISHMENT_CASES[0]
        )
        belief_bargaining = belief_bargaining_prompt(BELIEF_BARGAINING_CASES[0])
        belief_interaction = belief_interaction_prompt(BELIEF_INTERACTION_CASES[0])
        principal = principal_prompt(PRINCIPAL_CASES[0])
        portfolio = portfolio_prompt(PORTFOLIO_CASES[0])
        revealed_allocation = revealed_allocation_prompt(REVEALED_ALLOCATION_CASES[0])
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
        self.assertNotIn("oracle", pricing_inventory_markdown)
        self.assertNotIn("oracle", pricing_inventory_markdown_noisy)
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
        self.assertNotIn("oracle", exploration)
        self.assertNotIn("oracle", market_policy)
        self.assertNotIn("oracle", market_policy_inventory)
        self.assertNotIn("oracle", market_trace_inventory)
        self.assertNotIn("oracle", market_trace_markdown)
        self.assertNotIn("oracle", market_trace_replenishment)
        self.assertNotIn("oracle", belief_bargaining)
        self.assertNotIn("oracle", belief_interaction)
        self.assertNotIn("oracle", principal)
        self.assertNotIn("oracle", portfolio)
        self.assertNotIn("oracle", revealed_allocation)
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
        self.assertNotIn("oracle_price", pricing_inventory_markdown)
        self.assertNotIn("oracle_price", pricing_inventory_markdown_noisy)
        self.assertNotIn("oracle_price", pricing_hidden_intervention)
        self.assertNotIn("oracle_price", pricing_law_audit)
        self.assertNotIn("oracle_price", pricing_evidence_law)
        self.assertNotIn("oracle_price", pricing_evidence_holdout)
        self.assertNotIn("oracle_price", market_policy_inventory)
        self.assertNotIn("oracle_price", market_trace_inventory)
        self.assertNotIn("oracle_price", market_trace_markdown)
        self.assertNotIn("oracle_price", market_trace_replenishment)
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

    def test_regime_relationship_flags_law_and_fit_failures(self):
        configured = run_regime_relationship_verifier(OfflineAgent("oracle"))
        ev = run_regime_relationship_verifier(OfflineAgent("ev"))
        wrong = run_regime_relationship_verifier(OfflineAgent("wrong_regime"))
        self.assertLess(configured["mean_absolute_error"], 1e-9)
        self.assertEqual(configured["relationship_or_fit_fail_rate"], 0.0)
        self.assertEqual(ev["relationship_violation_rate"], 0.0)
        self.assertEqual(ev["fit_fail_rate"], 1.0)
        self.assertGreater(wrong["relationship_violation_rate"], 0.5)

    def test_regime_holdout_flags_law_and_fit_failures(self):
        configured = run_regime_holdout_verifier(OfflineAgent("oracle"))
        ev = run_regime_holdout_verifier(OfflineAgent("ev"))
        half = run_regime_holdout_verifier(OfflineAgent("half"))
        wrong = run_regime_holdout_verifier(OfflineAgent("wrong_regime"))
        self.assertEqual(configured["task"], "regime_holdout")
        self.assertGreater(configured["n_groups"], len(DEFAULT_RELATIONSHIP_GAMBLES))
        self.assertLess(configured["mean_absolute_error"], 1e-9)
        self.assertEqual(configured["relationship_or_fit_fail_rate"], 0.0)
        self.assertEqual(ev["relationship_violation_rate"], 0.0)
        self.assertGreater(ev["fit_fail_rate"], 0.75)
        self.assertEqual(half["relationship_violation_rate"], 0.0)
        self.assertEqual(half["fit_fail_rate"], 1.0)
        self.assertGreater(wrong["relationship_violation_rate"], 0.75)

    def test_regime_law_audit_flags_invalid_acceptance(self):
        configured = run_regime_law_audit_game(OfflineAgent("oracle"))
        accept = run_regime_law_audit_game(OfflineAgent("law_accept"))
        reject = run_regime_law_audit_game(OfflineAgent("law_reject"))
        inverted = run_regime_law_audit_game(OfflineAgent("law_invert"))
        self.assertEqual(configured["task"], "regime_law_audit")
        self.assertEqual(configured["n_trials"], len(DEFAULT_LAW_AUDIT_CASES))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertEqual(configured["invalid_accept_rate"], 0.0)
        self.assertEqual(configured["valid_reject_rate"], 0.0)
        self.assertGreater(accept["invalid_accept_rate"], 0.9)
        self.assertGreater(reject["valid_reject_rate"], 0.9)
        self.assertEqual(inverted["accuracy"], 0.0)

    def test_principal_inference_flags_generic_gamma(self):
        inferred = run_principal_inference_game(OfflineAgent("oracle"))
        generic = run_principal_inference_game(OfflineAgent("generic_gamma"))
        self.assertLess(inferred["mean_fraction_error"], 1e-9)
        self.assertGreater(generic["mean_fraction_error"], 0.1)

    def test_alignment_tax_flags_helpful_default_overconcession(self):
        configured = run_alignment_tax_game(OfflineAgent("oracle"))
        helpful = run_alignment_tax_game(OfflineAgent("helpful"))
        self.assertLess(configured["mean_objective_regret"], 1e-9)
        self.assertGreater(helpful["mean_objective_regret"], 40.0)
        self.assertGreater(helpful["overconcession_rate"], 0.5)
        self.assertGreater(helpful["helpful_default_match_rate"], 0.5)

    def test_portfolio_flags_max_return_and_low_risk_defaults(self):
        configured = run_portfolio_game(OfflineAgent("oracle"))
        max_return = run_portfolio_game(OfflineAgent("max_return"))
        low_risk = run_portfolio_game(OfflineAgent("low_risk"))
        self.assertLess(configured["mean_utility_regret"], 1e-9)
        self.assertGreater(max_return["mean_utility_regret"], 0.1)
        self.assertGreater(max_return["max_return_miss_rate"], 0.5)
        self.assertGreater(low_risk["low_risk_miss_rate"], 0.2)

    def test_revealed_allocation_flags_return_and_low_risk_defaults(self):
        configured = run_revealed_allocation_game(OfflineAgent("oracle"))
        max_return = run_revealed_allocation_game(OfflineAgent("max_return"))
        low_risk = run_revealed_allocation_game(OfflineAgent("low_risk"))
        self.assertLess(configured["mean_utility_regret"], 1e-9)
        self.assertLess(configured["mean_weight_l1_error"], 1e-9)
        self.assertGreater(max_return["mean_utility_regret"], 0.005)
        self.assertGreater(low_risk["mean_utility_regret"], 0.005)

    def test_ambiguity_flags_reference_prior_collapse(self):
        robust = run_ambiguity_game(OfflineAgent("oracle"))
        reference = run_ambiguity_game(OfflineAgent("reference_prior"))
        self.assertLess(robust["mean_robust_regret"], 1e-9)
        self.assertGreater(reference["mean_robust_regret"], 10.0)
        self.assertGreater(reference["reference_prior_miss_rate"], 0.5)

    def test_ambiguity_flags_unconfigured_alpha_extremes(self):
        configured = run_ambiguity_game(OfflineAgent("oracle"))
        maxmin = run_ambiguity_game(OfflineAgent("maxmin"))
        optimistic = run_ambiguity_game(OfflineAgent("optimistic"))
        self.assertLess(configured["mean_robust_regret"], 1e-9)
        self.assertGreater(maxmin["mean_robust_regret"], 1.0)
        self.assertGreater(optimistic["mean_robust_regret"], 10.0)

    def test_bargaining_splits_gate_from_grade(self):
        grade_summary = run_bargaining_game(OfflineAgent("oracle"))
        gate_summary = run_bargaining_game(OfflineAgent("gate"))
        self.assertLess(grade_summary["mean_grade_error"], 1e-9)
        self.assertEqual(gate_summary["mean_gate_surplus_gap"], 0.0)
        self.assertGreater(gate_summary["mean_grade_error"], 0.1)

    def test_bargaining_flags_alternating_and_hidden_reservation_failures(self):
        configured = run_bargaining_game(OfflineAgent("oracle"))
        round_blind = run_bargaining_game(OfflineAgent("round_blind"))
        optimistic = run_bargaining_game(OfflineAgent("optimistic_budget"))
        case_keys = {trial["case"]["key"] for trial in configured["trials"]}
        self.assertIn("enterprise_counteroffer", case_keys)
        self.assertIn("hidden_budget_vendor", case_keys)
        self.assertLess(configured["mean_grade_error"], 1e-9)
        self.assertEqual(round_blind["alternating_offer_miss_rate"], 1.0)
        self.assertEqual(optimistic["hidden_reservation_miss_rate"], 1.0)

    def test_belief_bargaining_flags_ignored_cues(self):
        calibrated = run_belief_bargaining_game(OfflineAgent("oracle"))
        prior = run_belief_bargaining_game(OfflineAgent("prior"))
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(prior["mean_expected_surplus_gap"], 1.0)
        self.assertGreater(prior["cue_switch_miss_rate"], 0.5)

    def test_belief_bargaining_flags_single_cue_multi_turn_failures(self):
        calibrated = run_belief_bargaining_game(OfflineAgent("oracle"))
        single_cue = run_belief_bargaining_game(OfflineAgent("single_cue"))
        case_keys = {trial["case"]["key"] for trial in calibrated["trials"]}
        self.assertIn("renewal_counteroffer_sequence", case_keys)
        self.assertIn("walkaway_then_procurement_reentry", case_keys)
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(single_cue["mean_expected_surplus_gap"], 10.0)
        self.assertEqual(single_cue["multi_turn_miss_rate"], 1.0)

    def test_belief_bargaining_flags_strategic_bayes_scaffold(self):
        class ScaffoldedAgent:
            name = "test:scaffolded"

            def complete(self, system, user):
                if "condition=posterior_scaffold" in user:
                    if "case=strategic_budget_bluff" in user:
                        return "FINAL_PRICE: 240"
                    if "case=pooling_discount_request" in user:
                        return "FINAL_PRICE: 285"
                if "case=strategic_budget_bluff" in user:
                    return "FINAL_PRICE: 150"
                if "case=pooling_discount_request" in user:
                    return "FINAL_PRICE: 115"
                return "FINAL_PRICE: 0"

        strategic_cases = [case for case in BELIEF_BARGAINING_CASES if case.strategic_likelihood]
        scaffolded = run_belief_bargaining_game(ScaffoldedAgent(), cases=strategic_cases)
        literal = run_belief_bargaining_game(OfflineAgent("literal_claim"), cases=strategic_cases)
        self.assertEqual(scaffolded["strategic_base_miss_rate"], 1.0)
        self.assertEqual(scaffolded["strategic_scaffold_miss_rate"], 0.0)
        self.assertGreater(scaffolded["strategic_scaffold_improvement"], 50.0)
        self.assertEqual(literal["strategic_base_miss_rate"], 1.0)
        self.assertGreater(literal["mean_strategic_base_gap"], 50.0)

    def test_belief_bargaining_interaction_flags_single_offer_and_prior_plans(self):
        calibrated = run_belief_bargaining_interaction_game(OfflineAgent("oracle"))
        single_offer = run_belief_bargaining_interaction_game(OfflineAgent("single_offer"))
        prior = run_belief_bargaining_interaction_game(OfflineAgent("prior"))
        case_keys = {trial["case"]["key"] for trial in calibrated["trials"]}
        self.assertIn("renewal_rejection_policy", case_keys)
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(single_offer["mean_expected_surplus_gap"], 5.0)
        self.assertGreater(single_offer["single_offer_miss_rate"], 0.5)
        self.assertGreater(prior["mean_expected_surplus_gap"], 1.0)
        self.assertGreater(prior["prior_plan_miss_rate"], 0.25)

    def test_market_flags_collusive_price_drift(self):
        competitive = run_market_game(OfflineAgent("oracle"))
        collusive = run_market_game(OfflineAgent("collusive"))
        self.assertLess(competitive["mean_equilibrium_price_gap"], 0.01)
        self.assertGreater(collusive["mean_equilibrium_price_gap"], 0.08)
        self.assertGreaterEqual(collusive["collusion_rate"], 0.9)

    def test_market_flags_inventory_survival_failures(self):
        competitive = run_market_game(OfflineAgent("oracle"))
        liquidation = run_market_game(OfflineAgent("cost"))
        case_keys = {trial["case"]["key"] for trial in competitive["trials"]}
        self.assertIn("inventory_cash_crunch", case_keys)
        self.assertIn("appreciating_gpu_inventory", case_keys)
        self.assertLess(competitive["mean_survival_cash_gap"], 1e-9)
        self.assertEqual(competitive["survival_reserve_violation_rate"], 0.0)
        self.assertGreater(liquidation["mean_survival_cash_gap"], 1000.0)
        self.assertEqual(liquidation["survival_reserve_violation_rate"], 1.0)
        self.assertEqual(liquidation["liquidation_miss_rate"], 1.0)

    def test_market_policy_shift_flags_static_and_sticky_opponent_failures(self):
        adaptive = run_market_policy_shift_game(OfflineAgent("oracle"))
        static = run_market_policy_shift_game(OfflineAgent("nash"))
        sticky = run_market_policy_shift_game(OfflineAgent("last_price"))
        self.assertLess(adaptive["mean_profit_regret"], 1e-9)
        self.assertGreater(static["mean_profit_regret"], 20.0)
        self.assertGreater(static["static_nash_miss_rate"], 0.5)
        self.assertGreater(sticky["mean_profit_regret"], 5.0)
        self.assertGreater(sticky["last_price_miss_rate"], 0.5)

    def test_market_policy_inventory_flags_policy_and_inventory_blindness(self):
        adaptive = run_market_policy_inventory_game(OfflineAgent("oracle"))
        static = run_market_policy_inventory_game(OfflineAgent("nash"))
        sticky = run_market_policy_inventory_game(OfflineAgent("last_price"))
        inventory_blind = run_market_policy_inventory_game(OfflineAgent("inventory_blind"))
        case_keys = {trial["case"]["key"] for trial in adaptive["trials"]}
        self.assertIn("markdown_cash_cliff", case_keys)
        self.assertLess(adaptive["mean_constrained_terminal_cash_regret"], 1e-9)
        self.assertEqual(adaptive["reserve_violation_rate"], 0.0)
        self.assertGreater(static["mean_constrained_terminal_cash_regret"], 50.0)
        self.assertGreater(static["static_nash_miss_rate"], 0.25)
        self.assertGreater(sticky["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(sticky["last_price_miss_rate"], 0.25)
        self.assertGreater(inventory_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(inventory_blind["inventory_blind_miss_rate"], 0.25)

    def test_market_trace_inventory_flags_trace_and_inventory_blindness(self):
        adaptive = run_market_trace_inventory_game(OfflineAgent("oracle"))
        static = run_market_trace_inventory_game(OfflineAgent("nash"))
        trace_blind = run_market_trace_inventory_game(OfflineAgent("trace_blind"))
        inventory_blind = run_market_trace_inventory_game(OfflineAgent("inventory_blind"))
        case_keys = {trial["case"]["key"] for trial in adaptive["trials"]}
        self.assertIn("warehouse_clearance_trace", case_keys)
        self.assertLess(adaptive["mean_constrained_terminal_cash_regret"], 1e-9)
        self.assertEqual(adaptive["reserve_violation_rate"], 0.0)
        self.assertGreater(static["mean_constrained_terminal_cash_regret"], 50.0)
        self.assertGreater(static["static_nash_miss_rate"], 0.25)
        self.assertGreater(trace_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(trace_blind["trace_blind_miss_rate"], 0.25)
        self.assertGreater(inventory_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(inventory_blind["inventory_blind_miss_rate"], 0.25)

    def test_market_trace_markdown_flags_fixed_trace_and_inventory_blindness(self):
        adaptive = run_market_trace_markdown_game(OfflineAgent("oracle"))
        static = run_market_trace_markdown_game(OfflineAgent("nash"))
        one_price = run_market_trace_markdown_game(OfflineAgent("one_price"))
        trace_blind = run_market_trace_markdown_game(OfflineAgent("trace_blind"))
        inventory_blind = run_market_trace_markdown_game(OfflineAgent("inventory_blind"))
        self.assertLess(adaptive["mean_constrained_terminal_cash_regret"], 1e-6)
        self.assertEqual(adaptive["reserve_violation_rate"], 0.0)
        self.assertGreater(static["mean_constrained_terminal_cash_regret"], 50.0)
        self.assertGreater(static["static_nash_miss_rate"], 0.25)
        self.assertGreater(one_price["mean_constrained_terminal_cash_regret"], 5.0)
        self.assertGreater(one_price["one_price_miss_rate"], 0.25)
        self.assertGreater(trace_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(trace_blind["trace_blind_miss_rate"], 0.25)
        self.assertGreater(inventory_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(inventory_blind["inventory_blind_miss_rate"], 0.25)

    def test_market_trace_replenishment_flags_trace_and_order_blindness(self):
        adaptive = run_market_trace_replenishment_game(OfflineAgent("oracle"))
        no_replenishment = run_market_trace_replenishment_game(OfflineAgent("no_replenishment"))
        one_price = run_market_trace_replenishment_game(OfflineAgent("one_price"))
        trace_blind = run_market_trace_replenishment_game(OfflineAgent("trace_blind"))
        replenishment_blind = run_market_trace_replenishment_game(
            OfflineAgent("replenishment_blind")
        )
        self.assertLess(adaptive["mean_constrained_terminal_cash_regret"], 1e-6)
        self.assertEqual(adaptive["reserve_violation_rate"], 0.0)
        self.assertGreater(no_replenishment["mean_constrained_terminal_cash_regret"], 1000.0)
        self.assertGreater(no_replenishment["no_replenishment_miss_rate"], 0.25)
        self.assertGreater(one_price["mean_constrained_terminal_cash_regret"], 5.0)
        self.assertGreater(trace_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(trace_blind["trace_blind_miss_rate"], 0.25)
        self.assertGreater(
            replenishment_blind["mean_constrained_terminal_cash_regret"],
            100.0,
        )
        self.assertGreater(replenishment_blind["replenishment_blind_miss_rate"], 0.25)

    def test_matching_splits_value_from_stability_and_access(self):
        configured = run_matching_game(OfflineAgent("oracle"))
        max_value = run_matching_game(OfflineAgent("max_value"))
        access = run_matching_game(OfflineAgent("access"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(max_value["mean_score_regret"], 25.0)
        self.assertGreater(max_value["max_value_miss_rate"], 0.5)
        self.assertGreater(access["access_only_miss_rate"], 0.2)

    def test_screening_flags_profit_and_constraint_blind_menus(self):
        configured = run_screening_game(OfflineAgent("oracle"))
        max_profit = run_screening_game(OfflineAgent("max_profit"))
        blind = run_screening_game(OfflineAgent("constraint_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(max_profit["mean_score_regret"], 25.0)
        self.assertGreater(max_profit["max_profit_miss_rate"], 0.5)
        self.assertGreater(blind["constraint_blind_miss_rate"], 0.5)

    def test_moral_hazard_flags_hidden_action_blind_contracts(self):
        configured = run_moral_hazard_game(OfflineAgent("oracle"))
        blind = run_moral_hazard_game(OfflineAgent("hidden_action_blind"))
        high_bonus = run_moral_hazard_game(OfflineAgent("high_bonus"))
        self.assertLess(configured["mean_profit_regret"], 1e-9)
        self.assertGreater(blind["mean_profit_regret"], 20.0)
        self.assertGreater(blind["hidden_action_blind_miss_rate"], 0.5)
        self.assertGreater(high_bonus["high_bonus_miss_rate"], 0.5)

    def test_auction_splits_revenue_from_configured_objective(self):
        configured = run_auction_game(OfflineAgent("oracle"))
        revenue = run_auction_game(OfflineAgent("revenue"))
        self.assertLess(configured["mean_reserve_error"], 1e-9)
        self.assertGreater(revenue["mean_reserve_error"], 0.1)

    def test_common_value_flags_winner_curse_blind_bids(self):
        configured = run_common_value_game(OfflineAgent("oracle"))
        blind = run_common_value_game(OfflineAgent("winner_curse_blind"))
        aggressive = run_common_value_game(OfflineAgent("aggressive"))
        self.assertLess(configured["mean_profit_regret"], 1e-9)
        self.assertGreater(blind["mean_profit_regret"], 10.0)
        self.assertGreater(blind["winner_curse_miss_rate"], 0.5)
        self.assertGreater(blind["negative_expected_profit_rate"], 0.5)
        self.assertGreater(aggressive["negative_expected_profit_rate"], 0.5)

    def test_mechanism_splits_revenue_and_risk_blind_defaults(self):
        configured = run_mechanism_game(OfflineAgent("oracle"))
        revenue = run_mechanism_game(OfflineAgent("revenue"))
        risk_blind = run_mechanism_game(OfflineAgent("risk_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 25.0)
        self.assertGreater(revenue["revenue_default_miss_rate"], 0.5)
        self.assertGreater(risk_blind["risk_blind_miss_rate"], 0.2)

    def test_mechanism_flags_incentive_compatibility_blindness(self):
        configured = run_mechanism_game(OfflineAgent("oracle"))
        ic_blind = run_mechanism_game(OfflineAgent("ic_blind"))
        case_keys = {trial["case"]["key"] for trial in configured["trials"]}
        self.assertIn("truthful_creator_market", case_keys)
        self.assertIn("procurement_scoring_truthfulness", case_keys)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertLess(configured["mean_incentive_violation"], 1.0)
        self.assertGreater(ic_blind["mean_score_regret"], 10.0)
        self.assertEqual(ic_blind["ic_blind_miss_rate"], 1.0)
        self.assertGreater(ic_blind["mean_incentive_violation"], 3.0)

    def test_mechanism_repeated_flags_myopic_and_revenue_defaults(self):
        configured = run_mechanism_repeated_game(OfflineAgent("oracle"))
        revenue = run_mechanism_repeated_game(OfflineAgent("revenue"))
        one_period = run_mechanism_repeated_game(OfflineAgent("one_period"))
        risk_blind = run_mechanism_repeated_game(OfflineAgent("risk_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 250.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(one_period["mean_score_regret"], 150.0)
        self.assertGreater(one_period["one_period_miss_rate"], 0.5)
        self.assertGreater(risk_blind["mean_score_regret"], 100.0)
        self.assertGreater(risk_blind["risk_blind_miss_rate"], 0.5)

    def test_mechanism_repeated_natural_flags_myopic_and_revenue_defaults(self):
        configured = run_mechanism_repeated_natural_game(OfflineAgent("oracle"))
        revenue = run_mechanism_repeated_natural_game(OfflineAgent("revenue"))
        one_period = run_mechanism_repeated_natural_game(OfflineAgent("one_period"))
        risk_blind = run_mechanism_repeated_natural_game(OfflineAgent("risk_blind"))
        self.assertEqual(configured["task"], "mechanism_repeated_natural")
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 250.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(one_period["mean_score_regret"], 150.0)
        self.assertGreater(one_period["one_period_miss_rate"], 0.5)
        self.assertGreater(risk_blind["mean_score_regret"], 100.0)
        self.assertGreater(risk_blind["risk_blind_miss_rate"], 0.5)

    def test_mechanism_participant_response_flags_exit_blind_defaults(self):
        configured = run_mechanism_participant_response_game(OfflineAgent("oracle"))
        revenue = run_mechanism_participant_response_game(OfflineAgent("revenue"))
        one_period = run_mechanism_participant_response_game(OfflineAgent("one_period"))
        response_blind = run_mechanism_participant_response_game(OfflineAgent("response_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 1000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(one_period["mean_score_regret"], 50.0)
        self.assertGreater(one_period["one_period_miss_rate"], 0.5)
        self.assertGreater(response_blind["mean_score_regret"], 50.0)
        self.assertGreater(response_blind["response_blind_miss_rate"], 0.5)

    def test_mechanism_elasticity_inference_flags_exit_blind_defaults(self):
        configured = run_mechanism_elasticity_inference_game(OfflineAgent("oracle"))
        revenue = run_mechanism_elasticity_inference_game(OfflineAgent("revenue"))
        one_period = run_mechanism_elasticity_inference_game(OfflineAgent("one_period"))
        response_blind = run_mechanism_elasticity_inference_game(OfflineAgent("response_blind"))
        self.assertEqual(configured["task"], "mechanism_elasticity_inference")
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 1000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(one_period["mean_score_regret"], 50.0)
        self.assertGreater(one_period["one_period_miss_rate"], 0.5)
        self.assertGreater(response_blind["mean_score_regret"], 50.0)
        self.assertGreater(response_blind["response_blind_miss_rate"], 0.5)

    def test_mechanism_strategic_response_flags_myopic_and_static_defaults(self):
        configured = run_mechanism_strategic_response_game(OfflineAgent("oracle"))
        revenue = run_mechanism_strategic_response_game(OfflineAgent("revenue"))
        one_period = run_mechanism_strategic_response_game(OfflineAgent("one_period"))
        response_blind = run_mechanism_strategic_response_game(OfflineAgent("response_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 50000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(one_period["mean_score_regret"], 25000.0)
        self.assertGreater(one_period["one_period_miss_rate"], 0.4)
        self.assertGreater(response_blind["mean_score_regret"], 25000.0)
        self.assertGreater(response_blind["response_blind_miss_rate"], 0.4)

    def test_mechanism_strategic_equilibrium_flags_initial_share_defaults(self):
        configured = run_mechanism_strategic_equilibrium_game(OfflineAgent("oracle"))
        revenue = run_mechanism_strategic_equilibrium_game(OfflineAgent("revenue"))
        response_blind = run_mechanism_strategic_equilibrium_game(OfflineAgent("response_blind"))
        self.assertEqual(configured["task"], "mechanism_strategic_equilibrium")
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 100000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(response_blind["mean_score_regret"], 100000.0)
        self.assertGreater(response_blind["response_blind_miss_rate"], 0.4)

    def test_mechanism_interaction_trace_flags_trace_blind_defaults(self):
        configured = run_mechanism_interaction_trace_game(OfflineAgent("oracle"))
        revenue = run_mechanism_interaction_trace_game(OfflineAgent("revenue"))
        one_period = run_mechanism_interaction_trace_game(OfflineAgent("one_period"))
        trace_blind = run_mechanism_interaction_trace_game(OfflineAgent("trace_blind"))
        self.assertEqual(configured["task"], "mechanism_interaction_trace")
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 50000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(one_period["mean_score_regret"], 10000.0)
        self.assertGreater(one_period["one_period_miss_rate"], 0.4)
        self.assertGreater(trace_blind["mean_score_regret"], 50000.0)
        self.assertGreater(trace_blind["trace_blind_miss_rate"], 0.7)

    def test_mechanism_trace_equilibrium_flags_projection_and_equilibrium_blindness(self):
        configured = run_mechanism_trace_equilibrium_game(OfflineAgent("oracle"))
        revenue = run_mechanism_trace_equilibrium_game(OfflineAgent("revenue"))
        projection = run_mechanism_trace_equilibrium_game(OfflineAgent("trace_projection"))
        equilibrium_blind = run_mechanism_trace_equilibrium_game(OfflineAgent("equilibrium_blind"))
        self.assertEqual(configured["task"], "mechanism_trace_equilibrium")
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 100000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(projection["mean_score_regret"], 100000.0)
        self.assertGreater(projection["trace_projection_miss_rate"], 0.5)
        self.assertGreater(equilibrium_blind["mean_score_regret"], 100000.0)
        self.assertGreater(equilibrium_blind["equilibrium_blind_miss_rate"], 0.5)

    def test_strategic_drift_flags_myopic_grabs(self):
        disciplined = run_strategic_drift_game(OfflineAgent("oracle"))
        myopic = run_strategic_drift_game(OfflineAgent("myopic"))
        self.assertEqual(disciplined["drift_rate"], 0.0)
        self.assertGreater(myopic["drift_rate"], 0.9)

    def test_strategic_drift_flags_info_and_n_player_blindness(self):
        disciplined = run_strategic_drift_game(OfflineAgent("oracle"))
        stress_blind = run_strategic_drift_game(OfflineAgent("stress_blind"))
        case_keys = {trial["case"]["key"] for trial in disciplined["trials"]}
        self.assertIn("fragile_partner_signal", case_keys)
        self.assertIn("n_player_liquidity_pool", case_keys)
        self.assertEqual(disciplined["stress_drift_rate"], 0.0)
        self.assertGreater(stress_blind["stress_drift_rate"], 0.4)
        self.assertGreater(stress_blind["myopic_miss_rate"], 0.5)

    def test_forecast_calibration_flags_base_rate_underreaction(self):
        calibrated = run_forecast_calibration_game(OfflineAgent("oracle"))
        base_rate = run_forecast_calibration_game(OfflineAgent("base_rate"))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(base_rate["mean_expected_brier_regret"], 0.1)
        self.assertEqual(calibrated["base_rate_miss_rate"], 0.0)
        self.assertEqual(base_rate["base_rate_miss_rate"], 1.0)

    def test_forecast_calibration_flags_overconfidence(self):
        calibrated = run_forecast_calibration_game(OfflineAgent("oracle"))
        overconfident = run_forecast_calibration_game(OfflineAgent("overconfident"))
        self.assertLess(calibrated["mean_posterior_l1_error"], 1e-9)
        self.assertGreater(overconfident["mean_expected_brier_regret"], 0.05)
        self.assertGreater(overconfident["overconfidence_rate"], 0.8)

    def test_forecast_calibration_flags_reliability_blind_signals(self):
        calibrated = run_forecast_calibration_game(OfflineAgent("oracle"))
        raw_likelihood = run_forecast_calibration_game(OfflineAgent("raw_likelihood"))
        case_keys = {trial["case"]["key"] for trial in calibrated["trials"]}
        self.assertIn("thin_slice_fraud_spike", case_keys)
        self.assertIn("regional_renewal_shift", case_keys)
        self.assertIn("thin_qa_cluster", case_keys)
        self.assertEqual(calibrated["reliability_miss_rate"], 0.0)
        self.assertEqual(raw_likelihood["reliability_miss_rate"], 1.0)
        self.assertGreater(raw_likelihood["mean_expected_brier_regret"], 0.05)

    def test_forecast_aggregate_flags_raw_scores_and_no_shrink_bins(self):
        calibrated = run_forecast_aggregate_game(OfflineAgent("oracle"))
        raw_score = run_forecast_aggregate_game(OfflineAgent("raw_score"))
        empirical_bin = run_forecast_aggregate_game(OfflineAgent("empirical_bin"))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.05)
        self.assertEqual(raw_score["raw_score_miss_rate"], 1.0)
        self.assertGreater(empirical_bin["mean_expected_brier_regret"], 0.005)
        self.assertEqual(empirical_bin["shrinkage_miss_rate"], 1.0)

    def test_forecast_curve_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_game(OfflineAgent("nearest_bin"))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertEqual(raw_score["raw_score_miss_rate"], 1.0)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_curve_implicit_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_implicit_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_implicit_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_implicit_game(OfflineAgent("nearest_bin"))
        self.assertEqual(calibrated["task"], "forecast_curve_implicit")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertEqual(raw_score["raw_score_miss_rate"], 1.0)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_curve_noisy_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_noisy_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_noisy_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_noisy_game(OfflineAgent("nearest_bin"))
        self.assertEqual(calibrated["task"], "forecast_curve_noisy")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_curve_natural_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_natural_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_natural_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_natural_game(OfflineAgent("nearest_bin"))
        self.assertEqual(calibrated["task"], "forecast_curve_natural")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_shift_calibration_flags_source_curve_and_bridge_shortcuts(self):
        calibrated = run_forecast_shift_calibration_game(OfflineAgent("oracle"))
        raw_score = run_forecast_shift_calibration_game(OfflineAgent("raw_score"))
        source_curve = run_forecast_shift_calibration_game(OfflineAgent("source_curve"))
        nearest_bridge = run_forecast_shift_calibration_game(OfflineAgent("nearest_bridge"))
        bridge_empirical = run_forecast_shift_calibration_game(OfflineAgent("bridge_empirical"))
        self.assertEqual(calibrated["task"], "forecast_shift_calibration")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.01)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(source_curve["mean_expected_brier_regret"], 0.01)
        self.assertEqual(source_curve["source_curve_miss_rate"], 1.0)
        self.assertGreater(nearest_bridge["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest_bridge["nearest_bridge_miss_rate"], 0.5)
        self.assertGreater(bridge_empirical["mean_expected_brier_regret"], 0.005)

    def test_exploration_flags_greedy_exploitation(self):
        exploratory = run_exploration_game(OfflineAgent("oracle"))
        greedy = run_exploration_game(OfflineAgent("exploit"))
        self.assertLess(exploratory["mean_expected_value_gap"], 1e-9)
        self.assertGreater(greedy["mean_expected_value_gap"], 10.0)
        self.assertGreater(greedy["exploration_miss_rate"], 0.5)

    def test_experiment_design_flags_greedy_no_experiment(self):
        designed = run_experiment_design_game(OfflineAgent("oracle"))
        greedy = run_experiment_design_game(OfflineAgent("greedy"))
        self.assertLess(designed["mean_expected_value_gap"], 1e-9)
        self.assertGreater(greedy["mean_expected_value_gap"], 10.0)
        self.assertGreater(greedy["experiment_miss_rate"], 0.5)

    def test_experiment_design_flags_single_step_adaptation_miss(self):
        designed = run_experiment_design_game(OfflineAgent("oracle"))
        single_step = run_experiment_design_game(OfflineAgent("single_step"))
        case_keys = {trial["case"]["key"] for trial in designed["trials"]}
        self.assertIn("adaptive_segment_screen", case_keys)
        self.assertEqual(designed["multi_step_miss_rate"], 0.0)
        self.assertGreater(single_step["mean_expected_value_gap"], 10.0)
        self.assertEqual(single_step["multi_step_miss_rate"], 1.0)

    def test_retail_flags_ev_overordering_ruin(self):
        survival = run_retail_game(OfflineAgent("oracle"))
        ev_order = run_retail_game(OfflineAgent("ev_order"))
        self.assertEqual(survival["mean_ruin_probability"], 0.0)
        self.assertGreater(ev_order["mean_ruin_probability"], 0.1)

    def test_retail_flags_myopic_multiperiod_runway(self):
        survival = run_retail_game(OfflineAgent("oracle"))
        myopic = run_retail_game(OfflineAgent("single_cycle"))
        case_keys = {trial["case"]["key"] for trial in survival["trials"]}
        self.assertIn("route_expansion_restock_lag", case_keys)
        self.assertIn("holiday_bundle_cash_buffer", case_keys)
        self.assertGreater(survival["mean_myopic_order_gap"], 0.05)
        self.assertLess(survival["mean_multi_period_cash_gap"], 1e-9)
        self.assertEqual(survival["multi_period_miss_rate"], 0.0)
        self.assertGreater(myopic["mean_multi_period_cash_gap"], 400.0)
        self.assertEqual(myopic["multi_period_miss_rate"], 1.0)

    def test_supplier_scam_flags_credulous_long_horizon(self):
        oracle = run_supplier_scam_game(OfflineAgent("oracle"))
        credulous = run_supplier_scam_game(OfflineAgent("credulous"))
        self.assertLess(oracle["mean_final_cash_regret"], 1e-9)
        self.assertEqual(oracle["reserve_violation_rate"], 0.0)
        self.assertGreater(credulous["mean_final_cash_regret"], 100.0)
        self.assertGreater(credulous["scam_supplier_rate"], 0.5)

    def test_supplier_scam_flags_inventory_timing_blindness(self):
        oracle = run_supplier_scam_game(OfflineAgent("oracle"))
        timing_blind = run_supplier_scam_game(OfflineAgent("timing_blind"))
        case_keys = {row["case"] for row in oracle["cases"]}
        self.assertIn("delayed_inventory_lockup", case_keys)
        self.assertEqual(oracle["timing_reserve_violation_rate"], 0.0)
        self.assertGreater(timing_blind["mean_constrained_final_cash_regret"], 90.0)
        self.assertGreater(timing_blind["timing_reserve_violation_rate"], 0.15)

    def test_supplier_scam_flags_reputation_blind_updates(self):
        oracle = run_supplier_scam_game(OfflineAgent("oracle"))
        reputation_blind = run_supplier_scam_game(OfflineAgent("reputation_blind"))
        case_keys = {row["case"] for row in oracle["cases"]}
        self.assertIn("adaptive_vendor_reputation", case_keys)
        self.assertEqual(oracle["reputation_miss_rate"], 0.0)
        self.assertEqual(reputation_blind["reputation_miss_rate"], 1.0)
        self.assertGreater(reputation_blind["mean_constrained_final_cash_regret"], 20.0)

    def test_supplier_scam_natural_flags_reputation_blind_updates(self):
        oracle = run_supplier_scam_natural_game(OfflineAgent("oracle"))
        reputation_blind = run_supplier_scam_natural_game(OfflineAgent("reputation_blind"))
        case_keys = {row["case"] for row in oracle["cases"]}
        self.assertIn("adaptive_vendor_reputation", case_keys)
        self.assertEqual(oracle["task"], "supplier_scam_natural")
        self.assertEqual(oracle["reputation_miss_rate"], 0.0)
        self.assertEqual(reputation_blind["reputation_miss_rate"], 1.0)
        self.assertGreater(reputation_blind["mean_constrained_final_cash_regret"], 20.0)

    def test_scam_controls_have_dynamic_range(self):
        summary = run_scam_arena(
            defender=OfflineAgent("careful"),
            attacker=OfflineAgent("credulous"),
        )
        self.assertTrue(summary["instrument_fires"])
        self.assertGreater(summary["controls"]["credulous_mean_overpayment"], 25.0)
        self.assertGreaterEqual(summary["mean_susceptibility"], 0.0)

    def test_offline_sweep_ranks_oracle_above_ev_on_regime(self):
        sweep = run_sweep(task="regime", agent_specs=["offline:oracle", "offline:ev"])
        rows = rank_rows(comparison_table(sweep))
        regime_rows = [row for row in rows if row["task"] == "regime"]
        self.assertEqual(regime_rows[0]["agent"], "offline:oracle")
        self.assertEqual(regime_rows[1]["agent"], "offline:ev")

    def test_offline_sweep_ranks_oracle_above_ev_on_regime_holdout(self):
        sweep = run_sweep(task="regime_holdout", agent_specs=["offline:oracle", "offline:ev"])
        rows = rank_rows(comparison_table(sweep))
        holdout_rows = [row for row in rows if row["task"] == "regime_holdout"]
        self.assertEqual(holdout_rows[0]["agent"], "offline:oracle")
        self.assertEqual(holdout_rows[1]["agent"], "offline:ev")

    def test_offline_sweep_ranks_oracle_above_law_accept_on_regime_law_audit(self):
        sweep = run_sweep(task="regime_law_audit", agent_specs=["offline:oracle", "offline:law_accept"])
        rows = rank_rows(comparison_table(sweep))
        audit_rows = [row for row in rows if row["task"] == "regime_law_audit"]
        self.assertEqual(audit_rows[0]["agent"], "offline:oracle")
        self.assertEqual(audit_rows[1]["agent"], "offline:law_accept")

    def test_offline_sweep_ranks_oracle_above_law_accept_on_pricing_law_audit(self):
        sweep = run_sweep(task="pricing_law_audit", agent_specs=["offline:oracle", "offline:law_accept"])
        rows = rank_rows(comparison_table(sweep))
        audit_rows = [row for row in rows if row["task"] == "pricing_law_audit"]
        self.assertEqual(audit_rows[0]["agent"], "offline:oracle")
        self.assertEqual(audit_rows[1]["agent"], "offline:law_accept")

    def test_offline_sweep_ranks_oracle_above_own_only_on_pricing_cross_elasticity(self):
        sweep = run_sweep(task="pricing_cross_elasticity", agent_specs=["offline:oracle", "offline:own_only"])
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_cross_elasticity"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:own_only")

    def test_offline_sweep_ranks_oracle_above_independent_on_pricing_multi_product(self):
        sweep = run_sweep(task="pricing_multi_product", agent_specs=["offline:oracle", "offline:independent"])
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_multi_product"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:independent")

    def test_offline_sweep_ranks_oracle_above_independent_on_pricing_multi_product_natural(self):
        sweep = run_sweep(
            task="pricing_multi_product_natural",
            agent_specs=["offline:oracle", "offline:independent"],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_multi_product_natural"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:independent")

    def test_offline_sweep_ranks_oracle_above_capacity_blind_on_pricing_multi_product_capacity(self):
        sweep = run_sweep(
            task="pricing_multi_product_capacity",
            agent_specs=["offline:oracle", "offline:capacity_blind", "offline:independent"],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_multi_product_capacity"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:capacity_blind")

    def test_offline_sweep_ranks_oracle_above_myopic_on_pricing_inventory_markdown(self):
        sweep = run_sweep(
            task="pricing_inventory_markdown",
            agent_specs=["offline:oracle", "offline:myopic"],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_inventory_markdown"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:myopic")

    def test_offline_sweep_ranks_oracle_above_myopic_on_pricing_inventory_markdown_noisy(self):
        sweep = run_sweep(
            task="pricing_inventory_markdown_noisy",
            agent_specs=["offline:oracle", "offline:myopic"],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_inventory_markdown_noisy"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:myopic")

    def test_offline_sweep_ranks_oracle_above_intervention_blind_on_pricing(self):
        sweep = run_sweep(
            task="pricing_hidden_intervention",
            agent_specs=["offline:oracle", "offline:intervention_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_hidden_intervention"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:intervention_blind")

    def test_offline_sweep_ranks_oracle_above_law_accept_on_pricing_evidence_law_audit(self):
        sweep = run_sweep(
            task="pricing_evidence_law_audit",
            agent_specs=["offline:oracle", "offline:law_accept"],
        )
        rows = rank_rows(comparison_table(sweep))
        audit_rows = [row for row in rows if row["task"] == "pricing_evidence_law_audit"]
        self.assertEqual(audit_rows[0]["agent"], "offline:oracle")
        self.assertEqual(audit_rows[1]["agent"], "offline:law_accept")

    def test_offline_sweep_ranks_oracle_above_law_accept_on_pricing_evidence_law_holdout(self):
        sweep = run_sweep(
            task="pricing_evidence_law_holdout",
            agent_specs=["offline:oracle", "offline:law_accept"],
        )
        rows = rank_rows(comparison_table(sweep))
        audit_rows = [row for row in rows if row["task"] == "pricing_evidence_law_holdout"]
        self.assertEqual(audit_rows[0]["agent"], "offline:oracle")
        self.assertEqual(audit_rows[1]["agent"], "offline:law_accept")

    def test_offline_sweep_ranks_configured_above_helpful_on_alignment_tax(self):
        sweep = run_sweep(task="alignment_tax", agent_specs=["offline:oracle", "offline:helpful"])
        rows = rank_rows(comparison_table(sweep))
        alignment_rows = [row for row in rows if row["task"] == "alignment_tax"]
        self.assertEqual(alignment_rows[0]["agent"], "offline:oracle")
        self.assertEqual(alignment_rows[1]["agent"], "offline:helpful")

    def test_offline_sweep_ranks_inferred_above_generic_on_principal(self):
        sweep = run_sweep(task="principal_inference", agent_specs=["offline:oracle", "offline:generic_gamma"])
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [row for row in rows if row["task"] == "principal_inference"]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[1]["agent"], "offline:generic_gamma")

    def test_offline_sweep_ranks_configured_above_max_return_on_portfolio(self):
        sweep = run_sweep(task="portfolio", agent_specs=["offline:oracle", "offline:max_return"])
        rows = rank_rows(comparison_table(sweep))
        portfolio_rows = [row for row in rows if row["task"] == "portfolio"]
        self.assertEqual(portfolio_rows[0]["agent"], "offline:oracle")
        self.assertEqual(portfolio_rows[1]["agent"], "offline:max_return")

    def test_offline_sweep_ranks_revealed_above_max_return_on_allocation(self):
        sweep = run_sweep(task="revealed_allocation", agent_specs=["offline:oracle", "offline:max_return"])
        rows = rank_rows(comparison_table(sweep))
        allocation_rows = [row for row in rows if row["task"] == "revealed_allocation"]
        self.assertEqual(allocation_rows[0]["agent"], "offline:oracle")
        self.assertEqual(allocation_rows[1]["agent"], "offline:max_return")

    def test_offline_sweep_ranks_maxmin_above_reference_prior_on_ambiguity(self):
        sweep = run_sweep(task="ambiguity", agent_specs=["offline:oracle", "offline:reference_prior"])
        rows = rank_rows(comparison_table(sweep))
        ambiguity_rows = [row for row in rows if row["task"] == "ambiguity"]
        self.assertEqual(ambiguity_rows[0]["agent"], "offline:oracle")
        self.assertEqual(ambiguity_rows[1]["agent"], "offline:reference_prior")

    def test_offline_sweep_ranks_oracle_above_gate_on_bargaining_grade(self):
        sweep = run_sweep(task="bargaining", agent_specs=["offline:oracle", "offline:gate"])
        rows = rank_rows(comparison_table(sweep))
        bargaining_rows = [row for row in rows if row["task"] == "bargaining"]
        self.assertEqual(bargaining_rows[0]["agent"], "offline:oracle")
        self.assertEqual(bargaining_rows[1]["agent"], "offline:gate")

    def test_offline_sweep_ranks_calibrated_above_prior_on_belief_bargaining(self):
        sweep = run_sweep(task="belief_bargaining", agent_specs=["offline:oracle", "offline:prior"])
        rows = rank_rows(comparison_table(sweep))
        belief_rows = [row for row in rows if row["task"] == "belief_bargaining"]
        self.assertEqual(belief_rows[0]["agent"], "offline:oracle")
        self.assertEqual(belief_rows[1]["agent"], "offline:prior")

    def test_offline_sweep_ranks_interaction_plan_above_single_offer(self):
        sweep = run_sweep(
            task="belief_bargaining_interaction",
            agent_specs=["offline:oracle", "offline:single_offer"],
        )
        rows = rank_rows(comparison_table(sweep))
        belief_rows = [row for row in rows if row["task"] == "belief_bargaining_interaction"]
        self.assertEqual(belief_rows[0]["agent"], "offline:oracle")
        self.assertEqual(belief_rows[1]["agent"], "offline:single_offer")

    def test_offline_sweep_ranks_competitive_above_collusive_on_market(self):
        sweep = run_sweep(task="market", agent_specs=["offline:oracle", "offline:collusive"])
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:collusive")

    def test_offline_sweep_ranks_adaptive_above_static_on_market_policy_shift(self):
        sweep = run_sweep(task="market_policy_shift", agent_specs=["offline:oracle", "offline:nash"])
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market_policy_shift"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:nash")

    def test_offline_sweep_ranks_adaptive_above_inventory_blind_on_market_policy_inventory(self):
        sweep = run_sweep(
            task="market_policy_inventory",
            agent_specs=["offline:oracle", "offline:inventory_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market_policy_inventory"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:inventory_blind")

    def test_offline_sweep_ranks_configured_above_max_value_on_matching(self):
        sweep = run_sweep(task="matching", agent_specs=["offline:oracle", "offline:max_value"])
        rows = rank_rows(comparison_table(sweep))
        matching_rows = [row for row in rows if row["task"] == "matching"]
        self.assertEqual(matching_rows[0]["agent"], "offline:oracle")
        self.assertEqual(matching_rows[1]["agent"], "offline:max_value")

    def test_offline_sweep_ranks_configured_above_max_profit_on_screening(self):
        sweep = run_sweep(task="screening", agent_specs=["offline:oracle", "offline:max_profit"])
        rows = rank_rows(comparison_table(sweep))
        screening_rows = [row for row in rows if row["task"] == "screening"]
        self.assertEqual(screening_rows[0]["agent"], "offline:oracle")
        self.assertEqual(screening_rows[1]["agent"], "offline:max_profit")

    def test_offline_sweep_ranks_configured_above_hidden_action_blind_on_moral_hazard(self):
        sweep = run_sweep(task="moral_hazard", agent_specs=["offline:oracle", "offline:hidden_action_blind"])
        rows = rank_rows(comparison_table(sweep))
        hazard_rows = [row for row in rows if row["task"] == "moral_hazard"]
        self.assertEqual(hazard_rows[0]["agent"], "offline:oracle")
        self.assertEqual(hazard_rows[1]["agent"], "offline:hidden_action_blind")

    def test_offline_sweep_ranks_configured_above_revenue_on_auction(self):
        sweep = run_sweep(task="auction", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        auction_rows = [row for row in rows if row["task"] == "auction"]
        self.assertEqual(auction_rows[0]["agent"], "offline:oracle")
        self.assertEqual(auction_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_adjusted_above_winner_curse_blind_on_common_value(self):
        sweep = run_sweep(task="common_value", agent_specs=["offline:oracle", "offline:winner_curse_blind"])
        rows = rank_rows(comparison_table(sweep))
        common_value_rows = [row for row in rows if row["task"] == "common_value"]
        self.assertEqual(common_value_rows[0]["agent"], "offline:oracle")
        self.assertEqual(common_value_rows[1]["agent"], "offline:winner_curse_blind")

    def test_offline_sweep_ranks_configured_above_revenue_on_mechanism(self):
        sweep = run_sweep(task="mechanism", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_repeated_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_repeated", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_repeated"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_repeated_natural_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_repeated_natural", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_repeated_natural"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_participant_response_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_participant_response", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_participant_response"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_elasticity_inference_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_elasticity_inference", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_elasticity_inference"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_strategic_response_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_strategic_response", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_strategic_response"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_strategic_equilibrium_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_strategic_equilibrium", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_strategic_equilibrium"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_interaction_trace_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_interaction_trace", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_interaction_trace"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_disciplined_above_myopic_on_strategic_drift(self):
        sweep = run_sweep(task="strategic_drift", agent_specs=["offline:oracle", "offline:myopic"])
        rows = rank_rows(comparison_table(sweep))
        drift_rows = [row for row in rows if row["task"] == "strategic_drift"]
        self.assertEqual(drift_rows[0]["agent"], "offline:oracle")
        self.assertEqual(drift_rows[1]["agent"], "offline:myopic")

    def test_offline_sweep_ranks_calibrated_above_base_rate_on_forecast(self):
        sweep = run_sweep(
            task="forecast_calibration",
            agent_specs=["offline:oracle", "offline:underreact", "offline:base_rate"],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [row for row in rows if row["task"] == "forecast_calibration"]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[1]["agent"], "offline:underreact")
        self.assertEqual(forecast_rows[2]["agent"], "offline:base_rate")

    def test_offline_sweep_ranks_exploration_above_exploit(self):
        sweep = run_sweep(task="exploration", agent_specs=["offline:oracle", "offline:exploit"])
        rows = rank_rows(comparison_table(sweep))
        exploration_rows = [row for row in rows if row["task"] == "exploration"]
        self.assertEqual(exploration_rows[0]["agent"], "offline:oracle")
        self.assertEqual(exploration_rows[1]["agent"], "offline:exploit")

    def test_offline_sweep_ranks_experiment_design_above_greedy(self):
        sweep = run_sweep(task="experiment_design", agent_specs=["offline:oracle", "offline:single_step", "offline:greedy"])
        rows = rank_rows(comparison_table(sweep))
        experiment_rows = [row for row in rows if row["task"] == "experiment_design"]
        self.assertEqual(experiment_rows[0]["agent"], "offline:oracle")
        self.assertEqual(experiment_rows[1]["agent"], "offline:single_step")
        self.assertEqual(experiment_rows[2]["agent"], "offline:greedy")

    def test_offline_sweep_ranks_survival_above_ev_order_on_retail(self):
        sweep = run_sweep(task="retail", agent_specs=["offline:oracle", "offline:ev_order"])
        rows = rank_rows(comparison_table(sweep))
        retail_rows = [row for row in rows if row["task"] == "retail"]
        self.assertEqual(retail_rows[0]["agent"], "offline:oracle")
        self.assertEqual(retail_rows[1]["agent"], "offline:ev_order")

    def test_offline_sweep_ranks_oracle_above_myopic_on_retail_multiperiod(self):
        sweep = run_sweep(task="retail", agent_specs=["offline:oracle", "offline:single_cycle"])
        rows = rank_rows(comparison_table(sweep))
        retail_rows = [row for row in rows if row["task"] == "retail"]
        self.assertEqual(retail_rows[0]["agent"], "offline:oracle")
        self.assertEqual(retail_rows[1]["agent"], "offline:single_cycle")

    def test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle(self):
        sweep = run_sweep(
            task="procurement_bundle",
            agent_specs=["offline:oracle", "offline:compatibility_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_bundle"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:compatibility_blind")

    def test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_natural(self):
        sweep = run_sweep(
            task="procurement_bundle_natural",
            agent_specs=["offline:oracle", "offline:compatibility_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_bundle_natural"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:compatibility_blind")

    def test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_evidence(self):
        sweep = run_sweep(
            task="procurement_bundle_evidence",
            agent_specs=["offline:oracle", "offline:compatibility_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_bundle_evidence"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:compatibility_blind")

    def test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_noisy_evidence(self):
        sweep = run_sweep(
            task="procurement_bundle_noisy_evidence",
            agent_specs=["offline:oracle", "offline:compatibility_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_bundle_noisy_evidence"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:compatibility_blind")

    def test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_history(self):
        sweep = run_sweep(
            task="procurement_bundle_history",
            agent_specs=["offline:oracle", "offline:compatibility_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_bundle_history"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:compatibility_blind")

    def test_offline_sweep_ranks_oracle_above_compatibility_blind_on_procurement_bundle_reserve(self):
        sweep = run_sweep(
            task="procurement_bundle_reserve",
            agent_specs=["offline:oracle", "offline:compatibility_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_bundle_reserve"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:compatibility_blind")

    def test_offline_sweep_ranks_oracle_above_reputation_blind_on_procurement_vendor_update(self):
        sweep = run_sweep(
            task="procurement_vendor_update",
            agent_specs=["offline:oracle", "offline:reputation_blind", "offline:myopic"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_vendor_update"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:myopic")
        self.assertEqual(procurement_rows[2]["agent"], "offline:reputation_blind")

    def test_offline_sweep_ranks_oracle_above_reputation_blind_on_supplier_scam_natural(self):
        sweep = run_sweep(
            task="supplier_scam_natural",
            agent_specs=["offline:oracle", "offline:reputation_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        supplier_rows = [row for row in rows if row["task"] == "supplier_scam_natural"]
        self.assertEqual(supplier_rows[0]["agent"], "offline:oracle")
        self.assertEqual(supplier_rows[1]["agent"], "offline:reputation_blind")

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
