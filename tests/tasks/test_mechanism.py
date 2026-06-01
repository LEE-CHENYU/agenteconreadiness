# Split from the former monolithic tests/test_tasks.py — mechanism cluster (29 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class MechanismTests(unittest.TestCase):

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

    def test_sample_limit_slices_mechanism_trace_equilibrium_natural_cases(self):
        results = run_tasks("mechanism_trace_equilibrium_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_mechanism_trace_equilibrium_noisy_cases(self):
        results = run_tasks("mechanism_trace_equilibrium_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

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

    def test_mechanism_trace_equilibrium_natural_preserves_oracle_and_baselines(self):
        configured = run_mechanism_trace_equilibrium_natural_game(OfflineAgent("oracle"))
        revenue = run_mechanism_trace_equilibrium_natural_game(OfflineAgent("revenue"))
        projection = run_mechanism_trace_equilibrium_natural_game(OfflineAgent("trace_projection"))
        equilibrium_blind = run_mechanism_trace_equilibrium_natural_game(OfflineAgent("equilibrium_blind"))
        self.assertEqual(configured["task"], "mechanism_trace_equilibrium_natural")
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 100000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(projection["mean_score_regret"], 100000.0)
        self.assertGreater(projection["trace_projection_miss_rate"], 0.5)
        self.assertGreater(equilibrium_blind["mean_score_regret"], 100000.0)
        self.assertGreater(equilibrium_blind["equilibrium_blind_miss_rate"], 0.5)

    def test_mechanism_trace_equilibrium_noisy_preserves_oracle_and_baselines(self):
        configured = run_mechanism_trace_equilibrium_noisy_game(OfflineAgent("oracle"))
        revenue = run_mechanism_trace_equilibrium_noisy_game(OfflineAgent("revenue"))
        projection = run_mechanism_trace_equilibrium_noisy_game(OfflineAgent("trace_projection"))
        equilibrium_blind = run_mechanism_trace_equilibrium_noisy_game(OfflineAgent("equilibrium_blind"))
        self.assertEqual(configured["task"], "mechanism_trace_equilibrium_noisy")
        self.assertEqual(configured["n_trials"], len(MECHANISM_TRACE_EQUILIBRIUM_NOISY_CASES))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 100000.0)
        self.assertEqual(revenue["revenue_default_miss_rate"], 1.0)
        self.assertGreater(projection["mean_score_regret"], 100000.0)
        self.assertGreater(projection["trace_projection_miss_rate"], 0.5)
        self.assertGreater(equilibrium_blind["mean_score_regret"], 100000.0)
        self.assertGreater(equilibrium_blind["equilibrium_blind_miss_rate"], 0.5)

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

    def test_offline_sweep_ranks_trace_equilibrium_natural_above_revenue(self):
        sweep = run_sweep(task="mechanism_trace_equilibrium_natural", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_trace_equilibrium_natural"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_trace_equilibrium_noisy_above_revenue(self):
        sweep = run_sweep(task="mechanism_trace_equilibrium_noisy", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism_trace_equilibrium_noisy"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

