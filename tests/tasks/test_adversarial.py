# Split from the former monolithic tests/test_tasks.py — adversarial cluster (9 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class AdversarialTests(unittest.TestCase):

    def test_sample_limit_slices_supplier_scam_natural_cases(self):
        results = run_tasks("supplier_scam_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], len(SUPPLIER_SCAM_CASES[0].rounds))
        self.assertLess(results[0]["mean_constrained_final_cash_regret"], 1e-9)

    def test_alignment_tax_flags_helpful_default_overconcession(self):
        configured = run_alignment_tax_game(OfflineAgent("oracle"))
        helpful = run_alignment_tax_game(OfflineAgent("helpful"))
        self.assertLess(configured["mean_objective_regret"], 1e-9)
        self.assertGreater(helpful["mean_objective_regret"], 40.0)
        self.assertGreater(helpful["overconcession_rate"], 0.5)
        self.assertGreater(helpful["helpful_default_match_rate"], 0.5)

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

    def test_offline_sweep_ranks_configured_above_helpful_on_alignment_tax(self):
        sweep = run_sweep(task="alignment_tax", agent_specs=["offline:oracle", "offline:helpful"])
        rows = rank_rows(comparison_table(sweep))
        alignment_rows = [row for row in rows if row["task"] == "alignment_tax"]
        self.assertEqual(alignment_rows[0]["agent"], "offline:oracle")
        self.assertEqual(alignment_rows[1]["agent"], "offline:helpful")

    def test_offline_sweep_ranks_oracle_above_reputation_blind_on_supplier_scam_natural(self):
        sweep = run_sweep(
            task="supplier_scam_natural",
            agent_specs=["offline:oracle", "offline:reputation_blind"],
        )
        rows = rank_rows(comparison_table(sweep))
        supplier_rows = [row for row in rows if row["task"] == "supplier_scam_natural"]
        self.assertEqual(supplier_rows[0]["agent"], "offline:oracle")
        self.assertEqual(supplier_rows[1]["agent"], "offline:reputation_blind")

