# Split from the former monolithic tests/test_tasks.py — regime cluster (10 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class RegimeTaskTests(unittest.TestCase):

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

