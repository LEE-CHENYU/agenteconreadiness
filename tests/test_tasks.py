import unittest

from aeread_lab.models import OfflineAgent, resolve_openai_model
from aeread_lab.tasks.adversarial import run_scam_arena
from aeread_lab.tasks.pricing import run_pricing_game
from aeread_lab.tasks.procurement import run_procurement_game


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

    def test_scam_controls_have_dynamic_range(self):
        summary = run_scam_arena(
            defender=OfflineAgent("careful"),
            attacker=OfflineAgent("credulous"),
        )
        self.assertTrue(summary["instrument_fires"])
        self.assertGreater(summary["controls"]["credulous_mean_overpayment"], 25.0)
        self.assertGreaterEqual(summary["mean_susceptibility"], 0.0)


if __name__ == "__main__":
    unittest.main()
