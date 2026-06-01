# Split from the former monolithic tests/test_tasks.py — forecast cluster (31 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class ForecastTests(unittest.TestCase):

    def test_sample_limit_slices_forecast_aggregate_cases(self):
        results = run_tasks("forecast_aggregate", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_cases(self):
        results = run_tasks("forecast_curve", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_implicit_cases(self):
        results = run_tasks("forecast_curve_implicit", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_noisy_cases(self):
        results = run_tasks("forecast_curve_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_curve_natural_cases(self):
        results = run_tasks("forecast_curve_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_shift_calibration_cases(self):
        results = run_tasks("forecast_shift_calibration", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_rolling_calibration_cases(self):
        results = run_tasks("forecast_rolling_calibration", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_rolling_log_calibration_cases(self):
        results = run_tasks("forecast_rolling_log_calibration", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_rolling_log_noisy_cases(self):
        results = run_tasks("forecast_rolling_log_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_event_log_calibration_cases(self):
        results = run_tasks("forecast_event_log_calibration", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_sample_limit_slices_forecast_operational_log_calibration_cases(self):
        results = run_tasks(
            "forecast_operational_log_calibration",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_brier_regret"], 1e-9)

    def test_forecast_calibration_flags_base_rate_underreaction(self):
        calibrated = run_forecast_calibration_game(OfflineAgent("oracle"))
        base_rate = run_forecast_calibration_game(OfflineAgent("base_rate"))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(base_rate["mean_expected_brier_regret"], 0.1)
        self.assertEqual(calibrated["base_rate_miss_rate"], 0.0)
        self.assertEqual(base_rate["base_rate_miss_rate"], 1.0)

    def test_forecast_calibration_flags_overconfidence(self):
        calibrated = run_forecast_calibration_game(OfflineAgent("oracle"))
        overconfident = run_forecast_calibration_game(OfflineAgent("overconfident"))
        self.assertLess(calibrated["mean_posterior_l1_error"], 1e-9)
        self.assertGreater(overconfident["mean_expected_brier_regret"], 0.05)
        self.assertGreater(overconfident["overconfidence_rate"], 0.8)

    def test_forecast_calibration_flags_reliability_blind_signals(self):
        calibrated = run_forecast_calibration_game(OfflineAgent("oracle"))
        raw_likelihood = run_forecast_calibration_game(OfflineAgent("raw_likelihood"))
        case_keys = {trial["case"]["key"] for trial in calibrated["trials"]}
        self.assertIn("thin_slice_fraud_spike", case_keys)
        self.assertIn("regional_renewal_shift", case_keys)
        self.assertIn("thin_qa_cluster", case_keys)
        self.assertEqual(calibrated["reliability_miss_rate"], 0.0)
        self.assertEqual(raw_likelihood["reliability_miss_rate"], 1.0)
        self.assertGreater(raw_likelihood["mean_expected_brier_regret"], 0.05)

    def test_forecast_aggregate_flags_raw_scores_and_no_shrink_bins(self):
        calibrated = run_forecast_aggregate_game(OfflineAgent("oracle"))
        raw_score = run_forecast_aggregate_game(OfflineAgent("raw_score"))
        empirical_bin = run_forecast_aggregate_game(OfflineAgent("empirical_bin"))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.05)
        self.assertEqual(raw_score["raw_score_miss_rate"], 1.0)
        self.assertGreater(empirical_bin["mean_expected_brier_regret"], 0.005)
        self.assertEqual(empirical_bin["shrinkage_miss_rate"], 1.0)

    def test_forecast_curve_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_game(OfflineAgent("nearest_bin"))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertEqual(raw_score["raw_score_miss_rate"], 1.0)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_curve_implicit_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_implicit_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_implicit_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_implicit_game(OfflineAgent("nearest_bin"))
        self.assertEqual(calibrated["task"], "forecast_curve_implicit")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertEqual(raw_score["raw_score_miss_rate"], 1.0)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_curve_noisy_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_noisy_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_noisy_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_noisy_game(OfflineAgent("nearest_bin"))
        self.assertEqual(calibrated["task"], "forecast_curve_noisy")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_curve_natural_flags_raw_scores_and_nearest_bin_shortcuts(self):
        calibrated = run_forecast_curve_natural_game(OfflineAgent("oracle"))
        raw_score = run_forecast_curve_natural_game(OfflineAgent("raw_score"))
        nearest = run_forecast_curve_natural_game(OfflineAgent("nearest_bin"))
        self.assertEqual(calibrated["task"], "forecast_curve_natural")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(nearest["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest["nearest_bin_miss_rate"], 0.5)

    def test_forecast_shift_calibration_flags_source_curve_and_bridge_shortcuts(self):
        calibrated = run_forecast_shift_calibration_game(OfflineAgent("oracle"))
        raw_score = run_forecast_shift_calibration_game(OfflineAgent("raw_score"))
        source_curve = run_forecast_shift_calibration_game(OfflineAgent("source_curve"))
        nearest_bridge = run_forecast_shift_calibration_game(OfflineAgent("nearest_bridge"))
        bridge_empirical = run_forecast_shift_calibration_game(OfflineAgent("bridge_empirical"))
        self.assertEqual(calibrated["task"], "forecast_shift_calibration")
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.01)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(source_curve["mean_expected_brier_regret"], 0.01)
        self.assertEqual(source_curve["source_curve_miss_rate"], 1.0)
        self.assertGreater(nearest_bridge["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(nearest_bridge["nearest_bridge_miss_rate"], 0.5)
        self.assertGreater(bridge_empirical["mean_expected_brier_regret"], 0.005)

    def test_forecast_rolling_calibration_flags_stale_and_pooled_history(self):
        calibrated = run_forecast_rolling_calibration_game(OfflineAgent("oracle"))
        raw_score = run_forecast_rolling_calibration_game(OfflineAgent("raw_score"))
        stale_window = run_forecast_rolling_calibration_game(OfflineAgent("stale_window"))
        pooled_history = run_forecast_rolling_calibration_game(OfflineAgent("pooled_history"))
        self.assertEqual(calibrated["task"], "forecast_rolling_calibration")
        self.assertEqual(calibrated["n_trials"], len(FORECAST_ROLLING_CASES))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(stale_window["mean_expected_brier_regret"], 0.01)
        self.assertGreater(stale_window["stale_window_miss_rate"], 0.5)
        self.assertGreater(pooled_history["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(pooled_history["pooled_history_miss_rate"], 0.5)

    def test_forecast_rolling_log_calibration_flags_time_log_shortcuts(self):
        calibrated = run_forecast_rolling_log_calibration_game(OfflineAgent("oracle"))
        raw_score = run_forecast_rolling_log_calibration_game(OfflineAgent("raw_score"))
        stale_window = run_forecast_rolling_log_calibration_game(OfflineAgent("stale_window"))
        pooled_history = run_forecast_rolling_log_calibration_game(OfflineAgent("pooled_history"))
        latest_window = run_forecast_rolling_log_calibration_game(OfflineAgent("latest_window"))
        self.assertEqual(calibrated["task"], "forecast_rolling_log_calibration")
        self.assertEqual(calibrated["n_trials"], len(FORECAST_ROLLING_LOG_CASES))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(stale_window["mean_expected_brier_regret"], 0.01)
        self.assertGreater(stale_window["stale_window_miss_rate"], 0.5)
        self.assertGreater(pooled_history["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(pooled_history["pooled_history_miss_rate"], 0.5)
        self.assertGreater(latest_window["mean_expected_brier_regret"], 0.0002)
        self.assertGreater(latest_window["latest_window_miss_rate"], 0.5)

    def test_forecast_rolling_log_noisy_flags_implicit_time_log_shortcuts(self):
        calibrated = run_forecast_rolling_log_noisy_game(OfflineAgent("oracle"))
        raw_score = run_forecast_rolling_log_noisy_game(OfflineAgent("raw_score"))
        stale_window = run_forecast_rolling_log_noisy_game(OfflineAgent("stale_window"))
        pooled_history = run_forecast_rolling_log_noisy_game(OfflineAgent("pooled_history"))
        latest_window = run_forecast_rolling_log_noisy_game(OfflineAgent("latest_window"))
        self.assertEqual(calibrated["task"], "forecast_rolling_log_noisy")
        self.assertEqual(calibrated["n_trials"], len(FORECAST_ROLLING_NOISY_LOG_CASES))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(stale_window["mean_expected_brier_regret"], 0.01)
        self.assertGreater(stale_window["stale_window_miss_rate"], 0.5)
        self.assertGreater(pooled_history["mean_expected_brier_regret"], 0.002)
        self.assertGreater(pooled_history["pooled_history_miss_rate"], 0.5)
        self.assertGreater(latest_window["mean_expected_brier_regret"], 0.001)
        self.assertGreater(latest_window["latest_window_miss_rate"], 0.5)

    def test_forecast_event_log_calibration_flags_item_log_shortcuts(self):
        calibrated = run_forecast_event_log_calibration_game(OfflineAgent("oracle"))
        raw_score = run_forecast_event_log_calibration_game(OfflineAgent("raw_score"))
        stale_window = run_forecast_event_log_calibration_game(OfflineAgent("stale_window"))
        pooled_history = run_forecast_event_log_calibration_game(OfflineAgent("pooled_history"))
        latest_window = run_forecast_event_log_calibration_game(OfflineAgent("latest_window"))
        self.assertEqual(calibrated["task"], "forecast_event_log_calibration")
        self.assertEqual(calibrated["n_trials"], len(FORECAST_EVENT_LOG_CASES))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(stale_window["mean_expected_brier_regret"], 0.01)
        self.assertGreater(stale_window["stale_window_miss_rate"], 0.5)
        self.assertGreater(pooled_history["mean_expected_brier_regret"], 0.002)
        self.assertGreater(pooled_history["pooled_history_miss_rate"], 0.5)
        self.assertGreater(latest_window["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(latest_window["latest_window_miss_rate"], 0.5)

    def test_forecast_operational_log_calibration_flags_context_shortcuts(self):
        calibrated = run_forecast_operational_log_calibration_game(OfflineAgent("oracle"))
        raw_score = run_forecast_operational_log_calibration_game(OfflineAgent("raw_score"))
        stale_window = run_forecast_operational_log_calibration_game(OfflineAgent("stale_window"))
        pooled_history = run_forecast_operational_log_calibration_game(OfflineAgent("pooled_history"))
        latest_window = run_forecast_operational_log_calibration_game(OfflineAgent("latest_window"))
        policy_blind = run_forecast_operational_log_calibration_game(OfflineAgent("policy_blind"))
        route_blind = run_forecast_operational_log_calibration_game(OfflineAgent("route_blind"))
        self.assertEqual(calibrated["task"], "forecast_operational_log_calibration")
        self.assertEqual(calibrated["n_trials"], len(FORECAST_OPERATIONAL_LOG_CASES))
        self.assertLess(calibrated["mean_expected_brier_regret"], 1e-9)
        self.assertGreater(raw_score["mean_expected_brier_regret"], 0.02)
        self.assertGreater(raw_score["raw_score_miss_rate"], 0.5)
        self.assertGreater(stale_window["mean_expected_brier_regret"], 0.01)
        self.assertGreater(stale_window["stale_window_miss_rate"], 0.5)
        self.assertGreater(pooled_history["mean_expected_brier_regret"], 0.002)
        self.assertGreater(pooled_history["pooled_history_miss_rate"], 0.5)
        self.assertGreater(latest_window["mean_expected_brier_regret"], 0.0005)
        self.assertGreater(latest_window["latest_window_miss_rate"], 0.5)
        self.assertGreater(policy_blind["mean_expected_brier_regret"], 0.002)
        self.assertGreater(policy_blind["policy_blind_miss_rate"], 0.5)
        self.assertGreater(route_blind["mean_expected_brier_regret"], 0.002)
        self.assertGreater(route_blind["route_blind_miss_rate"], 0.5)

    def test_offline_sweep_ranks_calibrated_above_base_rate_on_forecast(self):
        sweep = run_sweep(
            task="forecast_calibration",
            agent_specs=["offline:oracle", "offline:underreact", "offline:base_rate"],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [row for row in rows if row["task"] == "forecast_calibration"]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[1]["agent"], "offline:underreact")
        self.assertEqual(forecast_rows[2]["agent"], "offline:base_rate")

    def test_offline_sweep_ranks_oracle_above_rolling_calibration_baselines(self):
        sweep = run_sweep(
            task="forecast_rolling_calibration",
            agent_specs=[
                "offline:oracle",
                "offline:pooled_history",
                "offline:stale_window",
                "offline:raw_score",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [row for row in rows if row["task"] == "forecast_rolling_calibration"]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[1]["agent"], "offline:pooled_history")
        self.assertEqual(forecast_rows[2]["agent"], "offline:stale_window")
        self.assertEqual(forecast_rows[3]["agent"], "offline:raw_score")

    def test_offline_sweep_ranks_oracle_above_rolling_log_calibration_baselines(self):
        sweep = run_sweep(
            task="forecast_rolling_log_calibration",
            agent_specs=[
                "offline:oracle",
                "offline:latest_window",
                "offline:pooled_history",
                "offline:stale_window",
                "offline:raw_score",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [
            row for row in rows if row["task"] == "forecast_rolling_log_calibration"
        ]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[-1]["agent"], "offline:raw_score")

    def test_offline_sweep_ranks_oracle_above_rolling_log_noisy_baselines(self):
        sweep = run_sweep(
            task="forecast_rolling_log_noisy",
            agent_specs=[
                "offline:oracle",
                "offline:latest_window",
                "offline:pooled_history",
                "offline:stale_window",
                "offline:raw_score",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [row for row in rows if row["task"] == "forecast_rolling_log_noisy"]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[1]["agent"], "offline:latest_window")
        self.assertEqual(forecast_rows[2]["agent"], "offline:pooled_history")
        self.assertEqual(forecast_rows[3]["agent"], "offline:raw_score")
        self.assertEqual(forecast_rows[4]["agent"], "offline:stale_window")

    def test_offline_sweep_ranks_oracle_above_event_log_calibration_baselines(self):
        sweep = run_sweep(
            task="forecast_event_log_calibration",
            agent_specs=[
                "offline:oracle",
                "offline:latest_window",
                "offline:pooled_history",
                "offline:stale_window",
                "offline:raw_score",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [row for row in rows if row["task"] == "forecast_event_log_calibration"]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[-1]["agent"], "offline:raw_score")

    def test_offline_sweep_ranks_oracle_above_operational_log_calibration_baselines(self):
        sweep = run_sweep(
            task="forecast_operational_log_calibration",
            agent_specs=[
                "offline:oracle",
                "offline:latest_window",
                "offline:policy_blind",
                "offline:route_blind",
                "offline:pooled_history",
                "offline:stale_window",
                "offline:raw_score",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        forecast_rows = [
            row for row in rows if row["task"] == "forecast_operational_log_calibration"
        ]
        self.assertEqual(forecast_rows[0]["agent"], "offline:oracle")
        self.assertEqual(forecast_rows[-1]["agent"], "offline:raw_score")

