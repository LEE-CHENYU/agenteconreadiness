# Split from the former monolithic tests/test_tasks.py — procurement cluster (26 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class ProcurementTests(unittest.TestCase):

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

    def test_sample_limit_slices_procurement_vendor_update_noisy_cases(self):
        results = run_tasks("procurement_vendor_update_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

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

    def test_procurement_vendor_update_noisy_flags_reputation_blindness(self):
        configured = run_procurement_vendor_update_noisy_game(OfflineAgent("oracle"))
        reputation_blind = run_procurement_vendor_update_noisy_game(OfflineAgent("reputation_blind"))
        myopic = run_procurement_vendor_update_noisy_game(OfflineAgent("myopic"))
        self.assertEqual(configured["task"], "procurement_vendor_update_noisy")
        self.assertEqual(configured["n_trials"], len(PROCUREMENT_VENDOR_UPDATE_NOISY_CASES))
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(reputation_blind["mean_score_regret"], 5.0)
        self.assertGreater(reputation_blind["reputation_blind_miss_rate"], 0.5)
        self.assertGreater(myopic["mean_score_regret"], 1.0)

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

    def test_offline_sweep_ranks_oracle_above_reputation_blind_on_noisy_procurement_vendor_update(self):
        sweep = run_sweep(
            task="procurement_vendor_update_noisy",
            agent_specs=["offline:oracle", "offline:reputation_blind", "offline:myopic"],
        )
        rows = rank_rows(comparison_table(sweep))
        procurement_rows = [row for row in rows if row["task"] == "procurement_vendor_update_noisy"]
        self.assertEqual(procurement_rows[0]["agent"], "offline:oracle")
        self.assertEqual(procurement_rows[1]["agent"], "offline:myopic")
        self.assertEqual(procurement_rows[2]["agent"], "offline:reputation_blind")

