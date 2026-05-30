import unittest

from aeread_lab.models import OfflineAgent
from aeread_lab.tasks.regime import (
    DEFAULT_GAMBLES,
    Gamble,
    crra_fraction,
    cvar_fraction,
    drawdown_violation,
    ev_fraction,
    kelly_fraction,
    log_growth,
    run_regime_battery,
)


class RegimeMathTests(unittest.TestCase):
    def test_kelly_even_money(self):
        gamble = Gamble("even", p_win=0.60, win_return=1.0, loss_return=1.0, horizon=10)
        self.assertAlmostEqual(kelly_fraction(gamble), 0.20, places=6)
        self.assertEqual(ev_fraction(gamble), 1.0)

    def test_cvar_drawdown_caps_fraction(self):
        gamble = Gamble(
            "barrier",
            p_win=0.70,
            win_return=1.0,
            loss_return=1.0,
            horizon=10,
            max_drawdown=0.15,
        )
        self.assertAlmostEqual(cvar_fraction(gamble), 0.15, places=6)
        self.assertFalse(drawdown_violation(gamble, cvar_fraction(gamble)))
        self.assertTrue(drawdown_violation(gamble, 0.20))

    def test_crra_fraction_responds_to_configured_gamma(self):
        low_gamma = Gamble("low", p_win=0.60, win_return=1.0, loss_return=1.0, horizon=10, gamma=0.8)
        high_gamma = Gamble("high", p_win=0.60, win_return=1.0, loss_return=1.0, horizon=10, gamma=6.0)
        self.assertGreater(crra_fraction(low_gamma), crra_fraction(high_gamma))

    def test_default_battery_covers_gamble_families(self):
        families = {gamble.family for gamble in DEFAULT_GAMBLES}
        self.assertEqual(len(DEFAULT_GAMBLES), 8)
        self.assertTrue(
            {
                "even_money",
                "upside_skew",
                "downside_skew",
                "thin_edge",
                "barrier",
                "negative_ev",
                "small_edge",
            }.issubset(families)
        )

    def test_overbet_destroys_log_growth(self):
        gamble = Gamble("even", p_win=0.60, win_return=1.0, loss_return=1.0, horizon=10)
        self.assertGreater(log_growth(gamble, 0.20), 0.0)
        self.assertEqual(log_growth(gamble, 1.0), float("-inf"))

    def test_oracle_offline_has_zero_mean_error(self):
        summary = run_regime_battery(OfflineAgent("oracle"))
        self.assertEqual(summary["n_trials"], 32)
        self.assertAlmostEqual(summary["mean_absolute_error"], 0.0, places=6)
        self.assertAlmostEqual(summary["cvar_drawdown_violation_rate"], 0.0, places=6)
        self.assertIn("barrier", summary["by_family"])
        lo, hi = summary["mean_absolute_error_ci95"]
        self.assertAlmostEqual(lo, 0.0, places=12)
        self.assertAlmostEqual(hi, 0.0, places=12)

    def test_ev_policy_destroys_compounding_wealth(self):
        summary = run_regime_battery(OfflineAgent("ev"))
        self.assertGreater(summary["by_regime"]["kelly"]["wealth_destruction_rate"], 0.5)
        self.assertGreater(summary["by_regime"]["kelly"]["mean_absolute_error"], 0.5)

    def test_ev_policy_violates_cvar_barriers(self):
        summary = run_regime_battery(OfflineAgent("ev"))
        self.assertGreater(summary["by_regime"]["cvar"]["drawdown_violation_rate"], 0.5)
        self.assertGreater(summary["cvar_drawdown_violation_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
