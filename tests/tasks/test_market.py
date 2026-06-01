# Split from the former monolithic tests/test_tasks.py — market cluster (18 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class MarketTests(unittest.TestCase):

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

    def test_sample_limit_slices_market_trace_replenishment_cases(self):
        results = run_tasks("market_trace_replenishment", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-6)

    def test_sample_limit_slices_market_trace_replenishment_natural_cases(self):
        results = run_tasks("market_trace_replenishment_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-6)

    def test_sample_limit_slices_market_trace_replenishment_noisy_cases(self):
        results = run_tasks("market_trace_replenishment_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_constrained_terminal_cash_regret"], 1e-6)

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

    def test_market_trace_replenishment_natural_preserves_trace_and_order_baselines(self):
        adaptive = run_market_trace_replenishment_natural_game(OfflineAgent("oracle"))
        no_replenishment = run_market_trace_replenishment_natural_game(
            OfflineAgent("no_replenishment")
        )
        one_price = run_market_trace_replenishment_natural_game(OfflineAgent("one_price"))
        trace_blind = run_market_trace_replenishment_natural_game(OfflineAgent("trace_blind"))
        replenishment_blind = run_market_trace_replenishment_natural_game(
            OfflineAgent("replenishment_blind")
        )
        self.assertEqual(adaptive["task"], "market_trace_replenishment_natural")
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

    def test_market_trace_replenishment_noisy_preserves_trace_and_order_baselines(self):
        adaptive = run_market_trace_replenishment_noisy_game(OfflineAgent("oracle"))
        no_replenishment = run_market_trace_replenishment_noisy_game(
            OfflineAgent("no_replenishment")
        )
        one_price = run_market_trace_replenishment_noisy_game(OfflineAgent("one_price"))
        trace_blind = run_market_trace_replenishment_noisy_game(OfflineAgent("trace_blind"))
        replenishment_blind = run_market_trace_replenishment_noisy_game(
            OfflineAgent("replenishment_blind")
        )
        self.assertEqual(adaptive["task"], "market_trace_replenishment_noisy")
        self.assertEqual(adaptive["n_trials"], len(MARKET_TRACE_REPLENISHMENT_NOISY_CASES))
        self.assertLess(adaptive["mean_constrained_terminal_cash_regret"], 1e-6)
        self.assertEqual(adaptive["reserve_violation_rate"], 0.0)
        self.assertGreater(no_replenishment["mean_constrained_terminal_cash_regret"], 1000.0)
        self.assertGreater(no_replenishment["no_replenishment_miss_rate"], 0.25)
        self.assertGreater(one_price["mean_constrained_terminal_cash_regret"], 1.0)
        self.assertGreater(trace_blind["mean_constrained_terminal_cash_regret"], 20.0)
        self.assertGreater(trace_blind["trace_blind_miss_rate"], 0.25)
        self.assertGreater(
            replenishment_blind["mean_constrained_terminal_cash_regret"],
            100.0,
        )
        self.assertGreater(replenishment_blind["replenishment_blind_miss_rate"], 0.25)

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

    def test_offline_sweep_ranks_natural_trace_replenishment_above_no_restock(self):
        sweep = run_sweep(
            task="market_trace_replenishment_natural",
            agent_specs=["offline:oracle", "offline:no_replenishment"],
        )
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market_trace_replenishment_natural"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:no_replenishment")

    def test_offline_sweep_ranks_noisy_trace_replenishment_above_no_restock(self):
        sweep = run_sweep(
            task="market_trace_replenishment_noisy",
            agent_specs=["offline:oracle", "offline:no_replenishment"],
        )
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market_trace_replenishment_noisy"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:no_replenishment")

