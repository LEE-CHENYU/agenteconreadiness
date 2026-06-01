# Split from the former monolithic tests/test_tasks.py — pricing cluster (49 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class PricingTests(unittest.TestCase):

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

    def test_sample_limit_slices_pricing_multi_product_capacity_noisy_cases(self):
        results = run_tasks("pricing_multi_product_capacity_noisy", OfflineAgent("oracle"), sample_limit=1)
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

    def test_sample_limit_slices_pricing_multi_product_markdown_noisy_cases(self):
        results = run_tasks("pricing_multi_product_markdown_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_price_l1_error"], 0.01)

    def test_sample_limit_slices_pricing_inventory_replenishment_noisy_cases(self):
        results = run_tasks("pricing_inventory_replenishment_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_decision_l1_error"], 0.01)

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

    def test_sample_limit_slices_market_trace_markdown_cases(self):
        results = run_tasks("market_trace_markdown", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-6)

    def test_sample_limit_slices_mechanism_elasticity_inference_cases(self):
        results = run_tasks("mechanism_elasticity_inference", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

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

    def test_pricing_multi_product_capacity_noisy_flags_capacity_blind_pricing(self):
        configured = run_pricing_multi_product_capacity_noisy_game(OfflineAgent("oracle"))
        capacity_blind = run_pricing_multi_product_capacity_noisy_game(
            OfflineAgent("capacity_blind")
        )
        independent = run_pricing_multi_product_capacity_noisy_game(OfflineAgent("independent"))
        self.assertEqual(configured["task"], "pricing_multi_product_capacity_noisy")
        self.assertEqual(configured["n_trials"], len(PRICING_MULTI_CAPACITY_NOISY_CASES))
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

    def test_pricing_multi_product_markdown_noisy_flags_depletion_and_cross_blind_pricing(self):
        configured = run_pricing_multi_product_markdown_noisy_game(OfflineAgent("oracle"))
        myopic = run_pricing_multi_product_markdown_noisy_game(OfflineAgent("myopic"))
        capacity_blind = run_pricing_multi_product_markdown_noisy_game(OfflineAgent("capacity_blind"))
        independent = run_pricing_multi_product_markdown_noisy_game(OfflineAgent("independent"))
        self.assertEqual(configured["task"], "pricing_multi_product_markdown_noisy")
        self.assertEqual(configured["n_trials"], len(PRICING_MULTI_MARKDOWN_NOISY_CASES))
        self.assertLess(configured["mean_price_l1_error"], 0.01)
        self.assertEqual(configured["myopic_miss_rate"], 0.0)
        self.assertEqual(configured["capacity_blind_miss_rate"], 0.0)
        self.assertEqual(configured["independent_miss_rate"], 0.0)
        self.assertGreater(myopic["mean_price_l1_error"], 5.0)
        self.assertGreater(myopic["myopic_miss_rate"], 0.5)
        self.assertGreater(capacity_blind["mean_price_l1_error"], 5.0)
        self.assertGreater(capacity_blind["capacity_blind_miss_rate"], 0.5)
        self.assertGreater(independent["mean_price_l1_error"], 5.0)
        self.assertGreater(independent["independent_miss_rate"], 0.5)

    def test_pricing_inventory_replenishment_noisy_flags_restock_and_myopic_plans(self):
        configured = run_pricing_inventory_replenishment_noisy_game(OfflineAgent("oracle"))
        no_restock = run_pricing_inventory_replenishment_noisy_game(OfflineAgent("no_restock"))
        myopic = run_pricing_inventory_replenishment_noisy_game(OfflineAgent("myopic"))
        capacity_fill = run_pricing_inventory_replenishment_noisy_game(OfflineAgent("capacity_fill"))
        self.assertEqual(configured["task"], "pricing_inventory_replenishment_noisy")
        self.assertEqual(configured["n_trials"], len(PRICING_INVENTORY_REPLENISHMENT_NOISY_CASES))
        self.assertLess(configured["mean_decision_l1_error"], 0.01)
        self.assertEqual(configured["no_restock_miss_rate"], 0.0)
        self.assertEqual(configured["myopic_miss_rate"], 0.0)
        self.assertEqual(configured["capacity_fill_miss_rate"], 0.0)
        self.assertGreater(no_restock["mean_decision_l1_error"], 20.0)
        self.assertEqual(no_restock["no_restock_miss_rate"], 1.0)
        self.assertGreater(myopic["mean_decision_l1_error"], 20.0)
        self.assertEqual(myopic["myopic_miss_rate"], 1.0)
        self.assertGreater(capacity_fill["mean_decision_l1_error"], 20.0)
        self.assertEqual(capacity_fill["capacity_fill_miss_rate"], 1.0)

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

    def test_market_flags_collusive_price_drift(self):
        competitive = run_market_game(OfflineAgent("oracle"))
        collusive = run_market_game(OfflineAgent("collusive"))
        self.assertLess(competitive["mean_equilibrium_price_gap"], 0.01)
        self.assertGreater(collusive["mean_equilibrium_price_gap"], 0.08)
        self.assertGreaterEqual(collusive["collusion_rate"], 0.9)

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

    def test_offline_sweep_ranks_oracle_above_capacity_blind_on_pricing_multi_product_capacity_noisy(self):
        sweep = run_sweep(
            task="pricing_multi_product_capacity_noisy",
            agent_specs=["offline:oracle", "offline:capacity_blind", "offline:independent"],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_multi_product_capacity_noisy"]
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

    def test_offline_sweep_ranks_oracle_above_baselines_on_pricing_multi_product_markdown_noisy(self):
        sweep = run_sweep(
            task="pricing_multi_product_markdown_noisy",
            agent_specs=[
                "offline:oracle",
                "offline:myopic",
                "offline:capacity_blind",
                "offline:independent",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_multi_product_markdown_noisy"]
        self.assertEqual(pricing_rows[0]["agent"], "offline:oracle")
        self.assertEqual(pricing_rows[1]["agent"], "offline:capacity_blind")

    def test_offline_sweep_ranks_oracle_above_baselines_on_pricing_inventory_replenishment_noisy(self):
        sweep = run_sweep(
            task="pricing_inventory_replenishment_noisy",
            agent_specs=[
                "offline:oracle",
                "offline:no_restock",
                "offline:myopic",
                "offline:capacity_fill",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        pricing_rows = [row for row in rows if row["task"] == "pricing_inventory_replenishment_noisy"]
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

    def test_offline_sweep_ranks_elasticity_inference_mechanism_above_revenue(self):
        sweep = run_sweep(task="mechanism_elasticity_inference", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_elasticity_inference"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

