# Split from the former monolithic tests/test_tasks.py — strategic_misc cluster (29 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class StrategicMiscTests(unittest.TestCase):

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

    def test_offline_sweep_ranks_disciplined_above_myopic_on_strategic_drift(self):
        sweep = run_sweep(task="strategic_drift", agent_specs=["offline:oracle", "offline:myopic"])
        rows = rank_rows(comparison_table(sweep))
        drift_rows = [row for row in rows if row["task"] == "strategic_drift"]
        self.assertEqual(drift_rows[0]["agent"], "offline:oracle")
        self.assertEqual(drift_rows[1]["agent"], "offline:myopic")

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

