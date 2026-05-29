import unittest

from aeread_lab.models import OfflineAgent, resolve_openai_model
from aeread_lab.reporting import comparison_table, rank_rows
from aeread_lab.runner import run_sweep
from aeread_lab.tasks.adversarial import run_scam_arena
from aeread_lab.tasks.auction import run_auction_game
from aeread_lab.tasks.bargaining import run_bargaining_game
from aeread_lab.tasks.market import run_market_game
from aeread_lab.tasks.pricing import DEFAULT_CASES as PRICING_CASES
from aeread_lab.tasks.pricing import _prompt as pricing_prompt
from aeread_lab.tasks.pricing import run_pricing_game
from aeread_lab.tasks.procurement import DEFAULT_CASES as PROCUREMENT_CASES
from aeread_lab.tasks.procurement import _prompt as procurement_prompt
from aeread_lab.tasks.procurement import run_procurement_game
from aeread_lab.tasks.regime import DEFAULT_GAMBLES, _prompt as regime_prompt


class TaskSmokeTests(unittest.TestCase):
    def test_openai_aliases_are_restricted(self):
        self.assertEqual(resolve_openai_model("gpt-5.5"), "gpt-5.5")
        self.assertIn("gpt-5.5", resolve_openai_model("mini"))
        with self.assertRaises(ValueError):
            resolve_openai_model("anthropic/claude-sonnet-4.6")

    def test_procurement_oracle_offline(self):
        summary = run_procurement_game(OfflineAgent("oracle"))
        self.assertEqual(summary["accuracy"], 1.0)

    def test_pricing_oracle_offline(self):
        summary = run_pricing_game(OfflineAgent("oracle"))
        self.assertLess(summary["mean_revenue_gap"], 1e-9)

    def test_prompts_do_not_expose_oracle_answers(self):
        regime = regime_prompt(DEFAULT_GAMBLES[0], "kelly")
        procurement = procurement_prompt(PROCUREMENT_CASES[0])
        pricing = pricing_prompt(PRICING_CASES[0], "reveal")
        self.assertNotIn("oracle", regime)
        self.assertNotIn("oracle", procurement)
        self.assertNotIn("oracle", pricing)
        self.assertNotIn("kelly_fraction", regime)
        self.assertNotIn("oracle_price", pricing)

    def test_bargaining_splits_gate_from_grade(self):
        grade_summary = run_bargaining_game(OfflineAgent("oracle"))
        gate_summary = run_bargaining_game(OfflineAgent("gate"))
        self.assertLess(grade_summary["mean_grade_error"], 1e-9)
        self.assertEqual(gate_summary["mean_gate_surplus_gap"], 0.0)
        self.assertGreater(gate_summary["mean_grade_error"], 0.1)

    def test_market_flags_collusive_price_drift(self):
        competitive = run_market_game(OfflineAgent("oracle"))
        collusive = run_market_game(OfflineAgent("collusive"))
        self.assertLess(competitive["mean_equilibrium_price_gap"], 0.01)
        self.assertGreater(collusive["mean_equilibrium_price_gap"], 0.9)
        self.assertGreaterEqual(collusive["collusion_rate"], 0.9)

    def test_auction_splits_revenue_from_configured_objective(self):
        configured = run_auction_game(OfflineAgent("oracle"))
        revenue = run_auction_game(OfflineAgent("revenue"))
        self.assertLess(configured["mean_reserve_error"], 1e-9)
        self.assertGreater(revenue["mean_reserve_error"], 0.1)

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

    def test_offline_sweep_ranks_oracle_above_gate_on_bargaining_grade(self):
        sweep = run_sweep(task="bargaining", agent_specs=["offline:oracle", "offline:gate"])
        rows = rank_rows(comparison_table(sweep))
        bargaining_rows = [row for row in rows if row["task"] == "bargaining"]
        self.assertEqual(bargaining_rows[0]["agent"], "offline:oracle")
        self.assertEqual(bargaining_rows[1]["agent"], "offline:gate")

    def test_offline_sweep_ranks_competitive_above_collusive_on_market(self):
        sweep = run_sweep(task="market", agent_specs=["offline:oracle", "offline:collusive"])
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:collusive")

    def test_offline_sweep_ranks_configured_above_revenue_on_auction(self):
        sweep = run_sweep(task="auction", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        auction_rows = [row for row in rows if row["task"] == "auction"]
        self.assertEqual(auction_rows[0]["agent"], "offline:oracle")
        self.assertEqual(auction_rows[1]["agent"], "offline:revenue")

    def test_rank_rows_keeps_missing_metrics_last(self):
        rows = [
            {"agent": "missing", "task": "procurement", "metric": "accuracy", "direction": "higher", "value": None},
            {"agent": "low", "task": "procurement", "metric": "accuracy", "direction": "higher", "value": 0.25},
            {"agent": "high", "task": "procurement", "metric": "accuracy", "direction": "higher", "value": 0.75},
        ]
        ranked = rank_rows(rows)
        self.assertEqual([row["agent"] for row in ranked], ["high", "low", "missing"])


if __name__ == "__main__":
    unittest.main()
