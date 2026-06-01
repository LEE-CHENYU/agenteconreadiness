# Split from the former monolithic tests/test_tasks.py — principal_holding cluster (98 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class PrincipalHoldingTests(unittest.TestCase):

    def test_sample_limit_slices_principal_holding_prediction_cases(self):
        results = run_tasks("principal_holding_prediction", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_noisy_principal_holding_prediction_cases(self):
        results = run_tasks("principal_holding_prediction_noisy", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_notes_cases(self):
        results = run_tasks("principal_holding_prediction_notes", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_blind_notes_cases(self):
        results = run_tasks("principal_holding_prediction_blind_notes", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_cases(self):
        results = run_tasks("principal_holding_filing_artifact", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_natural_cases(self):
        results = run_tasks("principal_holding_filing_artifact_natural", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_stress_cases(self):
        results = run_tasks("principal_holding_filing_artifact_stress", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_implicit_cases(self):
        results = run_tasks("principal_holding_filing_artifact_implicit", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_implicit_stable_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_implicit_stable",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_noisy_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_noisy",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_partial_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_partial",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_conflict_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_conflict",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_unmarked_conflict_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_unmarked_conflict",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_history_conflict_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_history_conflict",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_validation_process_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_validation_process",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_provenance_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_provenance",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_context_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_context",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_status_ablation_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_ablation",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_status_neutral_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_status_neutral_intro_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral_intro",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_audit_cases(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_audit",
            OfflineAgent("oracle"),
            sample_limit=1,
        )
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_sample_limit_slices_principal_holding_filing_artifact_metadata_source_audit_ablation_cases(self):
        for task in (
            "principal_holding_filing_artifact_metadata_source_audit_primary_only",
            "principal_holding_filing_artifact_metadata_source_audit_backfill_only",
            "principal_holding_filing_artifact_metadata_source_audit_ratio_only",
        ):
            with self.subTest(task=task):
                results = run_tasks(task, OfflineAgent("oracle"), sample_limit=1)
                self.assertEqual(results[0]["n_trials"], 1)
                self.assertLess(results[0]["mean_score_regret"], 1e-9)

    def test_real_derived_filing_trace_oracle_beats_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_trace",
                agent_specs=[
                    "offline:oracle",
                    "offline:market_value",
                    "offline:low_turnover",
                    "offline:max_position",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.7)
        self.assertGreater(by_agent["offline:low_turnover"]["value"], 0.9)
        self.assertGreater(by_agent["offline:max_position"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.3)

    def test_real_derived_filing_trace_case_key_targets_fixture(self):
        results = run_tasks(
            "principal_holding_filing_trace",
            OfflineAgent("oracle"),
            case_keys=["brk_2026q1_energy_rebalance"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["case"]["manager_cik"], "0001067983")
        self.assertEqual(trial["principal_trade"], "reduce_chevron")
        self.assertEqual(trial["market_value_trade"], "price_drift_oxy")
        self.assertEqual(trial["percent_change_trade"], "reduce_constellation")
        self.assertEqual(trial["second_best_trade"], "reduce_constellation")
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_real_derived_filing_trace_case_key_targets_tiger_depth_fixture(self):
        results = run_tasks(
            "principal_holding_filing_trace",
            OfflineAgent("oracle"),
            case_keys=["tiger_2026q1_megacap_rotation"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["case"]["manager_cik"], "0001167483")
        self.assertEqual(trial["principal_trade"], "reduce_tiger_e")
        self.assertEqual(trial["market_value_trade"], "add_tiger_g")
        self.assertEqual(trial["percent_change_trade"], "add_tiger_c")
        self.assertEqual(trial["second_best_trade"], "reduce_tiger_h")
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_raw_real_derived_filing_trace_oracle_beats_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_trace_raw",
                agent_specs=[
                    "offline:oracle",
                    "offline:market_value",
                    "offline:low_turnover",
                    "offline:max_position",
                    "offline:trend",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.7)
        self.assertGreater(by_agent["offline:low_turnover"]["value"], 0.9)
        self.assertGreater(by_agent["offline:max_position"]["value"], 0.9)
        self.assertGreater(by_agent["offline:trend"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.3)

    def test_raw_real_derived_filing_trace_removes_candidate_scaffold(self):
        prompt = principal_holding_filing_trace_raw_prompt(
            PRINCIPAL_HOLDING_FILING_TRACE_CASES[0]
        )
        self.assertIn("filing_row period=2026q1", prompt)
        self.assertIn("issuer_choices=sec_amex", prompt)
        self.assertNotIn("candidate_trade=", prompt)
        self.assertNotIn("prior_shares=", prompt)

    def test_raw_real_derived_filing_trace_case_key_targets_fixture(self):
        results = run_tasks(
            "principal_holding_filing_trace_raw",
            OfflineAgent("oracle"),
            case_keys=["brk_2026q1_energy_rebalance"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_chevron")
        self.assertEqual(trial["market_value_trade"], "sec_oxy")
        self.assertEqual(trial["percent_change_trade"], "sec_constellation")
        self.assertEqual(trial["second_best_trade"], "sec_constellation")
        self.assertEqual(trial["chosen_trade"], "sec_chevron")
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_raw_real_derived_filing_trace_case_key_targets_tiger_depth_fixture(self):
        results = run_tasks(
            "principal_holding_filing_trace_raw",
            OfflineAgent("oracle"),
            case_keys=["tiger_2026q1_megacap_rotation"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_tiger_e")
        self.assertEqual(trial["market_value_trade"], "sec_tiger_g")
        self.assertEqual(trial["percent_change_trade"], "sec_tiger_c")
        self.assertEqual(trial["second_best_trade"], "sec_tiger_h")
        self.assertEqual(trial["chosen_trade"], "sec_tiger_e")
        self.assertEqual(results[0]["accuracy"], 1.0)

    def test_raw_filing_trace_second_best_stability_attribution(self):
        payload = run_stability_sweep(
            task="principal_holding_filing_trace_raw",
            agent_specs=["offline:oracle", "offline:second_best"],
            repeat_count=2,
            case_keys=["tiger_2026q1_megacap_rotation"],
        )
        rows = stability_sweep_case_table(payload)
        second_best_row = next(row for row in rows if row["agent"] == "offline:second_best")
        self.assertEqual(second_best_row["status"], "stable_non_oracle")
        self.assertEqual(second_best_row["modal_choice"], "sec_tiger_h")
        self.assertEqual(second_best_row["modal_reference_matches"], ["second_best"])

    def test_filing_artifact_prompt_exposes_adjustment_without_candidate_scaffold(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_CASES[0]
        )
        self.assertIn("artifact_note issuer=sec_artifact_a adjustment_factor=4", prompt)
        self.assertIn("filing_row period=2026q1", prompt)
        self.assertIn("issuer_choices=sec_artifact_a", prompt)
        self.assertNotIn("candidate_trade=", prompt)

    def test_filing_artifact_natural_prompt_removes_structured_factor(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_CASES[0],
            include_factor=False,
        )
        self.assertIn("artifact_note issuer=sec_artifact_a note=", prompt)
        self.assertIn("4-for-1 share split", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_stress_prompt_combines_artifacts_and_runner_up(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_STRESS_CASES[0],
            include_factor=False,
        )
        self.assertIn("five-for-one split", prompt)
        self.assertIn("three-for-one split", prompt)
        self.assertIn("reduction is close to the largest adjusted action", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_implicit_prompt_omits_artifact_notes(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_STRESS_CASES[0],
            include_factor=False,
            include_notes=False,
        )
        self.assertIn("No separate corporate-action notes are provided", prompt)
        self.assertIn("infer split-like artifacts", prompt.lower())
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("five-for-one split", prompt)
        self.assertNotIn("three-for-one split", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_implicit_stable_prompt_omits_artifact_notes(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_IMPLICIT_STABLE_CASES[0],
            include_factor=False,
            include_notes=False,
        )
        self.assertIn("No separate corporate-action notes are provided", prompt)
        self.assertIn("infer split-like artifacts", prompt.lower())
        self.assertIn("reported_value=315000000 shares=3000000", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("three-for-one split", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_prompt_uses_registry_not_artifact_notes(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_STRESS_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
        )
        self.assertIn("No separate corporate-action notes are provided", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_a action=stock_split ratio=5-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_f action=stock_split ratio=3-for-1", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("five-for-one split", prompt)
        self.assertNotIn("three-for-one split", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_noisy_prompt_adds_registry_distractors(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_NOISY_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
        )
        self.assertIn("No separate corporate-action notes are provided", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_a action=stock_split ratio=5-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_f action=stock_split ratio=3-for-1", prompt)
        self.assertIn("status=unconfirmed", prompt)
        self.assertIn("status=stale", prompt)
        self.assertIn("issuer=sec_stress_z", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_partial_prompt_marks_missing_coverage(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_PARTIAL_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
        )
        self.assertIn("Registry coverage may be incomplete", prompt)
        self.assertNotIn("issuer=sec_stress_a action=stock_split", prompt)
        self.assertIn("corporate_action issuer=sec_stress_f action=stock_split ratio=3-for-1", prompt)
        self.assertIn("status=unconfirmed", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_conflict_prompt_marks_wrong_confirmed_rows(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_CONFLICT_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
        )
        self.assertIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("corporate_action issuer=sec_stress_a action=stock_split ratio=5-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_f action=stock_split ratio=3-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_unmarked_conflict_prompt_hides_conflict_warning(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_UNMARKED_CONFLICT_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
        )
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_a action=stock_split ratio=5-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_f action=stock_split ratio=3-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_history_conflict_prompt_uses_repeated_rows_without_warning(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("filing_row period=2025q4", prompt)
        self.assertIn("filing_row period=2026q1", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_a action=stock_split ratio=5-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_f action=stock_split ratio=3-for-1", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_validation_process_prompt_adds_ratio_check(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_VALIDATION_PROCESS_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_validation_process=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Validation process:", prompt)
        self.assertIn("compute observed_ratio=next_period_shares/prior_period_shares", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_provenance_prompt_adds_reliability_cue(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_provenance=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Registry provenance:", prompt)
        self.assertIn("issuer_exchange_notice sources are direct", prompt)
        self.assertIn("third_party_backfill_feed sources are lower-reliability", prompt)
        self.assertNotIn("Validation process:", prompt)
        self.assertNotIn("observed_ratio", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertIn("source=third_party_backfill_feed status=confirmed", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_context_prompt_adds_natural_source_packets(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_CONTEXT_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Corporate action source packets:", prompt)
        self.assertIn("source_packet issuer=sec_stress_a provenance=issuer_exchange_notice", prompt)
        self.assertIn("source_packet issuer=sec_stress_d provenance=third_party_backfill_feed", prompt)
        self.assertIn("no issuer notice, exchange bulletin, or transfer-agent attachment is present", prompt)
        self.assertNotIn("Registry provenance:", prompt)
        self.assertNotIn("Validation process:", prompt)
        self.assertNotIn("observed_ratio", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertIn("source=third_party_backfill_feed status=confirmed", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_status_ablation_prompt_removes_false_confirmation(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Corporate action source packets:", prompt)
        self.assertIn("source_packet issuer=sec_stress_a provenance=issuer_exchange_notice", prompt)
        self.assertIn("source_packet issuer=sec_stress_d provenance=third_party_backfill_feed", prompt)
        self.assertIn("no issuer notice, exchange bulletin, or transfer-agent attachment is present", prompt)
        self.assertNotIn("Validation process:", prompt)
        self.assertNotIn("observed_ratio", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertIn("source=third_party_backfill_feed status=unverified", prompt)
        self.assertNotIn("source=third_party_backfill_feed status=confirmed", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_status_neutral_prompt_omits_all_status_labels(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Corporate action source packets:", prompt)
        self.assertIn("source_packet issuer=sec_stress_a provenance=issuer_exchange_notice", prompt)
        self.assertIn("source_packet issuer=sec_stress_d provenance=third_party_backfill_feed", prompt)
        self.assertIn("no issuer notice, exchange bulletin, or transfer-agent attachment is present", prompt)
        self.assertNotIn("Validation process:", prompt)
        self.assertNotIn("observed_ratio", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("status=confirmed", prompt)
        self.assertNotIn("status=unverified", prompt)
        self.assertNotIn("status=", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_status_neutral_intro_prompt_removes_confirmed_wording(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
            include_status_neutral_metadata_intro=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Corporate action source packets:", prompt)
        self.assertIn("source_packet issuer=sec_stress_a provenance=issuer_exchange_notice", prompt)
        self.assertIn("source_packet issuer=sec_stress_d provenance=third_party_backfill_feed", prompt)
        self.assertIn("target-period corporate-action registry records", prompt)
        self.assertNotIn("target-period confirmed corporate-action registry records", prompt)
        self.assertNotIn("confirmed", prompt)
        self.assertNotIn("Validation process:", prompt)
        self.assertNotIn("observed_ratio", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("status=", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_audit_prompt_adds_primary_source_audit(self):
        prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
            include_status_neutral_metadata_intro=True,
            include_source_audit=True,
        )
        self.assertIn("filing_row period=2025q3", prompt)
        self.assertIn("Corporate action source packets:", prompt)
        self.assertIn("source_packet issuer=sec_stress_a provenance=issuer_exchange_notice", prompt)
        self.assertIn("source_packet issuer=sec_stress_d provenance=third_party_backfill_feed", prompt)
        self.assertIn("Source audit protocol:", prompt)
        self.assertIn("issuer_exchange_notice packets with attached", prompt)
        self.assertIn("third_party_backfill_feed rows without issuer notice", prompt)
        self.assertIn("reconcile the claimed split ratio against filing-row share-count ratios", prompt)
        self.assertIn("do not use that row as a mechanical unit change", prompt)
        self.assertIn("target-period corporate-action registry records", prompt)
        self.assertNotIn("target-period confirmed corporate-action registry records", prompt)
        self.assertNotIn("confirmed", prompt)
        self.assertNotIn("Validation process:", prompt)
        self.assertNotIn("observed_ratio", prompt)
        self.assertNotIn("Registry records may conflict with filing rows", prompt)
        self.assertIn("Corporate action registry:", prompt)
        self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
        self.assertNotIn("status=", prompt)
        self.assertNotIn("artifact_note", prompt)
        self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_metadata_source_audit_component_prompts_split_protocol(self):
        primary_prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_PRIMARY_ONLY_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
            include_status_neutral_metadata_intro=True,
            source_audit_protocol="primary_only",
        )
        self.assertIn("Source audit protocol:", primary_prompt)
        self.assertIn("primary corporate-action evidence", primary_prompt)
        self.assertNotIn("third_party_backfill_feed rows without", primary_prompt)
        self.assertNotIn("reconcile the claimed split ratio", primary_prompt)
        self.assertNotIn("compare each claimed stock-split ratio", primary_prompt)

        backfill_prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_BACKFILL_ONLY_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
            include_status_neutral_metadata_intro=True,
            source_audit_protocol="backfill_only",
        )
        self.assertIn("Source audit protocol:", backfill_prompt)
        self.assertIn("third_party_backfill_feed rows without issuer notice", backfill_prompt)
        self.assertIn("lower-reliability corporate-action metadata", backfill_prompt)
        self.assertNotIn("primary corporate-action evidence", backfill_prompt)
        self.assertNotIn("reconcile the claimed split ratio", backfill_prompt)
        self.assertNotIn("compare each claimed stock-split ratio", backfill_prompt)

        ratio_prompt = principal_holding_filing_artifact_prompt(
            PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_RATIO_ONLY_CASES[0],
            include_factor=False,
            include_notes=False,
            include_metadata=True,
            include_conflict_warning=False,
            include_source_context=True,
            include_status_neutral_metadata_intro=True,
            source_audit_protocol="ratio_only",
        )
        self.assertIn("Source audit protocol:", ratio_prompt)
        self.assertIn("compare each claimed stock-split ratio", ratio_prompt)
        self.assertIn("filing-row share-count ratios", ratio_prompt)
        self.assertNotIn("primary corporate-action evidence", ratio_prompt)
        self.assertNotIn("third_party_backfill_feed rows without", ratio_prompt)

        for prompt in (primary_prompt, backfill_prompt, ratio_prompt):
            self.assertIn("Corporate action source packets:", prompt)
            self.assertIn("target-period corporate-action registry records", prompt)
            self.assertNotIn("target-period confirmed corporate-action registry records", prompt)
            self.assertNotIn("confirmed", prompt)
            self.assertNotIn("Validation process:", prompt)
            self.assertNotIn("observed_ratio", prompt)
            self.assertNotIn("Registry records may conflict with filing rows", prompt)
            self.assertIn("corporate_action issuer=sec_stress_d action=stock_split ratio=4-for-1", prompt)
            self.assertNotIn("status=", prompt)
            self.assertNotIn("artifact_note", prompt)
            self.assertNotIn("adjustment_factor=", prompt)

    def test_filing_artifact_oracle_beats_artifact_blind_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.6)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.1)

    def test_filing_artifact_natural_oracle_beats_artifact_blind_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_natural",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.1)

    def test_filing_artifact_stress_oracle_beats_combined_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_stress",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_implicit_oracle_beats_combined_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_implicit",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_implicit_stable_oracle_beats_combined_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_implicit_stable",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_metadata_oracle_beats_combined_shortcuts(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_metadata_noisy_oracle_beats_registry_noise(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_noisy",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_naive",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_naive"]["value"], 0.05)

    def test_filing_artifact_metadata_partial_oracle_beats_metadata_only(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_partial",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_only",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_only"]["value"], 0.9)

    def test_filing_artifact_metadata_conflict_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_conflict",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_trusting",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)

    def test_filing_artifact_metadata_unmarked_conflict_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_unmarked_conflict",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_trusting",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)

    def test_filing_artifact_metadata_history_conflict_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_history_conflict",
                agent_specs=[
                    "offline:oracle",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_trusting",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)

    def test_filing_artifact_metadata_validation_process_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_validation_process",
                agent_specs=[
                    "offline:oracle",
                    "offline:metadata_validator",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_trusting",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:metadata_validator"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)

    def test_filing_artifact_metadata_source_provenance_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_source_provenance",
                agent_specs=[
                    "offline:oracle",
                    "offline:source_reliability",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_trusting",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)

    def test_filing_artifact_metadata_source_context_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_source_context",
                agent_specs=[
                    "offline:oracle",
                    "offline:source_reliability",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                    "offline:metadata_trusting",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)

    def test_filing_artifact_metadata_source_status_ablation_oracle_beats_status_blind(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_source_status_ablation",
                agent_specs=[
                    "offline:oracle",
                    "offline:source_reliability",
                    "offline:metadata_trusting",
                    "offline:metadata_naive",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
        self.assertEqual(by_agent["offline:metadata_trusting"]["value"], 0.0)
        self.assertGreater(by_agent["offline:metadata_naive"]["value"], 0.9)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_metadata_source_status_neutral_oracle_beats_metadata_trusting(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_source_status_neutral",
                agent_specs=[
                    "offline:oracle",
                    "offline:source_reliability",
                    "offline:metadata_source_trusting",
                    "offline:metadata_trusting",
                    "offline:metadata_naive",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
        self.assertEqual(by_agent["offline:metadata_source_trusting"]["value"], 0.0)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)
        self.assertGreater(by_agent["offline:metadata_naive"]["value"], 0.9)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_metadata_source_status_neutral_intro_keeps_offline_geometry(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_source_status_neutral_intro",
                agent_specs=[
                    "offline:oracle",
                    "offline:source_reliability",
                    "offline:metadata_source_trusting",
                    "offline:metadata_trusting",
                    "offline:metadata_naive",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
        self.assertEqual(by_agent["offline:metadata_source_trusting"]["value"], 0.0)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)
        self.assertGreater(by_agent["offline:metadata_naive"]["value"], 0.9)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_metadata_source_audit_keeps_offline_geometry(self):
        rows = comparison_table(
            run_sweep(
                task="principal_holding_filing_artifact_metadata_source_audit",
                agent_specs=[
                    "offline:oracle",
                    "offline:source_reliability",
                    "offline:metadata_source_trusting",
                    "offline:metadata_trusting",
                    "offline:metadata_naive",
                    "offline:artifact_blind",
                    "offline:market_value",
                    "offline:percent_change",
                    "offline:second_best",
                ],
            )
        )
        by_agent = {row["agent"]: row for row in rows}
        self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
        self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
        self.assertEqual(by_agent["offline:metadata_source_trusting"]["value"], 0.0)
        self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)
        self.assertGreater(by_agent["offline:metadata_naive"]["value"], 0.9)
        self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
        self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
        self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
        self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_metadata_source_audit_ablations_keep_offline_geometry(self):
        for task in (
            "principal_holding_filing_artifact_metadata_source_audit_primary_only",
            "principal_holding_filing_artifact_metadata_source_audit_backfill_only",
            "principal_holding_filing_artifact_metadata_source_audit_ratio_only",
        ):
            with self.subTest(task=task):
                rows = comparison_table(
                    run_sweep(
                        task=task,
                        agent_specs=[
                            "offline:oracle",
                            "offline:source_reliability",
                            "offline:metadata_source_trusting",
                            "offline:metadata_trusting",
                            "offline:metadata_naive",
                            "offline:artifact_blind",
                            "offline:market_value",
                            "offline:percent_change",
                            "offline:second_best",
                        ],
                    )
                )
                by_agent = {row["agent"]: row for row in rows}
                self.assertEqual(by_agent["offline:oracle"]["value"], 0.0)
                self.assertEqual(by_agent["offline:source_reliability"]["value"], 0.0)
                self.assertEqual(by_agent["offline:metadata_source_trusting"]["value"], 0.0)
                self.assertGreater(by_agent["offline:metadata_trusting"]["value"], 0.9)
                self.assertGreater(by_agent["offline:metadata_naive"]["value"], 0.9)
                self.assertGreater(by_agent["offline:artifact_blind"]["value"], 0.9)
                self.assertGreater(by_agent["offline:market_value"]["value"], 0.9)
                self.assertGreater(by_agent["offline:percent_change"]["value"], 0.7)
                self.assertGreater(by_agent["offline:second_best"]["value"], 0.05)

    def test_filing_artifact_case_key_targets_adjusted_fixture(self):
        results = run_tasks(
            "principal_holding_filing_artifact",
            OfflineAgent("oracle"),
            case_keys=["split_adjustment_vs_discretionary_reduction"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_artifact_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_artifact_a")
        self.assertEqual(trial["market_value_trade"], "sec_artifact_d")
        self.assertEqual(trial["percent_change_trade"], "sec_artifact_e")
        self.assertEqual(trial["second_best_trade"], "sec_artifact_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_artifact_a"]["value"], 0.0)
        self.assertEqual(trial["chosen_trade"], "sec_artifact_b")

    def test_filing_artifact_stress_case_key_targets_composite_fixture(self):
        results = run_tasks(
            "principal_holding_filing_artifact_stress",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_a"]["value"], 0.0)
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_f"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

    def test_filing_artifact_implicit_case_key_reuses_composite_fixture(self):
        results = run_tasks(
            "principal_holding_filing_artifact_implicit",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

    def test_filing_artifact_implicit_stable_case_key_controls_value_drift(self):
        results = run_tasks(
            "principal_holding_filing_artifact_implicit_stable",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_value_stable_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_d")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_f"]["value"], 0.0)
        self.assertEqual(trial["artifact_changes"]["sec_stress_f"]["next_value"], 315000000)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

    def test_filing_artifact_metadata_case_key_restores_split_factors(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_a"]["value"], 0.0)
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_f"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

    def test_filing_artifact_metadata_noisy_case_key_ignores_bad_registry_rows(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_noisy",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_noisy_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_a"]["value"], 0.0)
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_f"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        naive_results = run_tasks(
            "principal_holding_filing_artifact_metadata_noisy",
            OfflineAgent("metadata_naive"),
            case_keys=["multi_artifact_noisy_registry_close_runner_up"],
        )
        naive_trial = naive_results[0]["trials"][0]
        self.assertEqual(naive_trial["chosen_trade"], "sec_stress_c")

    def test_filing_artifact_metadata_partial_case_key_combines_registry_and_rows(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_partial",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_partial_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_a"]["value"], 0.0)
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_f"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_only_results = run_tasks(
            "principal_holding_filing_artifact_metadata_partial",
            OfflineAgent("metadata_only"),
            case_keys=["multi_artifact_partial_registry_close_runner_up"],
        )
        metadata_only_trial = metadata_only_results[0]["trials"][0]
        self.assertEqual(metadata_only_trial["chosen_trade"], "sec_stress_a")

    def test_filing_artifact_metadata_conflict_case_key_validates_registry_against_rows(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_conflict",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_a"]["value"], 0.0)
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_f"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_conflict",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_unmarked_conflict_case_key_reuses_validation_target(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_unmarked_conflict",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_unmarked_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_unmarked_conflict",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_unmarked_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_history_conflict_case_key_adds_repeated_history(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_history_conflict",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_history_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_history_conflict",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_history_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_validation_process_case_key_keeps_validation_target(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_validation_process",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_validation_process_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_validation_process",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_validation_process_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_provenance_case_key_keeps_validation_target(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_provenance",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_source_provenance_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_provenance",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_source_provenance_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_context_case_key_keeps_validation_target(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_context",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_source_context_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_context",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_source_context_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_status_ablation_case_key_removes_confirmed_false_reference(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_ablation",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_source_status_ablation_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_b")
        self.assertEqual(trial["metadata_status_blind_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_naive_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_ablation",
            OfflineAgent("metadata_naive"),
            case_keys=["multi_artifact_source_status_ablation_conflicting_registry_close_runner_up"],
        )
        metadata_naive_trial = metadata_naive_results[0]["trials"][0]
        self.assertEqual(metadata_naive_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_status_neutral_case_key_removes_status_labels(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_source_status_neutral_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertEqual(trial["metadata_status_blind_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_source_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral",
            OfflineAgent("metadata_source_trusting"),
            case_keys=["multi_artifact_source_status_neutral_conflicting_registry_close_runner_up"],
        )
        metadata_source_trial = metadata_source_results[0]["trials"][0]
        self.assertEqual(metadata_source_trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_source_status_neutral_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_status_neutral_intro_case_key_removes_confirmed_wording(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral_intro",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_source_status_neutral_intro_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertEqual(trial["metadata_status_blind_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_source_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral_intro",
            OfflineAgent("metadata_source_trusting"),
            case_keys=["multi_artifact_source_status_neutral_intro_conflicting_registry_close_runner_up"],
        )
        metadata_source_trial = metadata_source_results[0]["trials"][0]
        self.assertEqual(metadata_source_trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_status_neutral_intro",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_source_status_neutral_intro_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_audit_case_key_adds_audit_scaffold(self):
        results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_audit",
            OfflineAgent("oracle"),
            case_keys=["multi_artifact_source_audit_conflicting_registry_close_runner_up"],
        )
        self.assertEqual(results[0]["n_trials"], 1)
        trial = results[0]["trials"][0]
        self.assertEqual(trial["principal_trade"], "sec_stress_b")
        self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
        self.assertEqual(trial["market_value_trade"], "sec_stress_f")
        self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
        self.assertEqual(trial["second_best_trade"], "sec_stress_c")
        self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
        self.assertEqual(trial["metadata_status_blind_trade"], "sec_stress_d")
        self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
        self.assertLess(trial["oracle_margin"], 0.07)
        self.assertEqual(trial["chosen_trade"], "sec_stress_b")

        metadata_source_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_audit",
            OfflineAgent("metadata_source_trusting"),
            case_keys=["multi_artifact_source_audit_conflicting_registry_close_runner_up"],
        )
        metadata_source_trial = metadata_source_results[0]["trials"][0]
        self.assertEqual(metadata_source_trial["chosen_trade"], "sec_stress_b")

        metadata_trusting_results = run_tasks(
            "principal_holding_filing_artifact_metadata_source_audit",
            OfflineAgent("metadata_trusting"),
            case_keys=["multi_artifact_source_audit_conflicting_registry_close_runner_up"],
        )
        metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
        self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_metadata_source_audit_ablation_case_keys_share_target(self):
        task_cases = {
            "principal_holding_filing_artifact_metadata_source_audit_primary_only": (
                "multi_artifact_source_audit_primary_only_conflicting_registry_close_runner_up"
            ),
            "principal_holding_filing_artifact_metadata_source_audit_backfill_only": (
                "multi_artifact_source_audit_backfill_only_conflicting_registry_close_runner_up"
            ),
            "principal_holding_filing_artifact_metadata_source_audit_ratio_only": (
                "multi_artifact_source_audit_ratio_only_conflicting_registry_close_runner_up"
            ),
        }
        for task, case_key in task_cases.items():
            with self.subTest(task=task):
                results = run_tasks(task, OfflineAgent("oracle"), case_keys=[case_key])
                self.assertEqual(results[0]["n_trials"], 1)
                trial = results[0]["trials"][0]
                self.assertEqual(trial["principal_trade"], "sec_stress_b")
                self.assertEqual(trial["artifact_blind_trade"], "sec_stress_a")
                self.assertEqual(trial["market_value_trade"], "sec_stress_f")
                self.assertEqual(trial["percent_change_trade"], "sec_stress_e")
                self.assertEqual(trial["second_best_trade"], "sec_stress_c")
                self.assertEqual(trial["metadata_trusting_trade"], "sec_stress_d")
                self.assertEqual(trial["metadata_status_blind_trade"], "sec_stress_d")
                self.assertAlmostEqual(trial["artifact_changes"]["sec_stress_d"]["value"], 0.0)
                self.assertLess(trial["oracle_margin"], 0.07)
                self.assertEqual(trial["chosen_trade"], "sec_stress_b")

                metadata_source_results = run_tasks(
                    task,
                    OfflineAgent("metadata_source_trusting"),
                    case_keys=[case_key],
                )
                metadata_source_trial = metadata_source_results[0]["trials"][0]
                self.assertEqual(metadata_source_trial["chosen_trade"], "sec_stress_b")

                metadata_trusting_results = run_tasks(
                    task,
                    OfflineAgent("metadata_trusting"),
                    case_keys=[case_key],
                )
                metadata_trusting_trial = metadata_trusting_results[0]["trials"][0]
                self.assertEqual(metadata_trusting_trial["chosen_trade"], "sec_stress_d")

    def test_filing_artifact_stability_attribution_labels_artifact_blind(self):
        payload = run_stability_sweep(
            task="principal_holding_filing_artifact",
            agent_specs=["offline:oracle", "offline:artifact_blind"],
            repeat_count=2,
            case_keys=["split_adjustment_vs_discretionary_reduction"],
        )
        rows = stability_sweep_case_table(payload)
        artifact_blind_row = next(row for row in rows if row["agent"] == "offline:artifact_blind")
        self.assertEqual(artifact_blind_row["status"], "stable_non_oracle")
        self.assertEqual(artifact_blind_row["modal_choice"], "sec_artifact_a")
        self.assertEqual(artifact_blind_row["modal_reference_matches"], ["artifact_blind"])

    def test_principal_inference_flags_generic_gamma(self):
        inferred = run_principal_inference_game(OfflineAgent("oracle"))
        generic = run_principal_inference_game(OfflineAgent("generic_gamma"))
        self.assertLess(inferred["mean_fraction_error"], 1e-9)
        self.assertGreater(generic["mean_fraction_error"], 0.1)

    def test_principal_holding_prediction_flags_market_and_mechanical_defaults(self):
        configured = run_principal_holding_prediction_game(OfflineAgent("oracle"))
        max_return = run_principal_holding_prediction_game(OfflineAgent("max_return"))
        low_turnover = run_principal_holding_prediction_game(OfflineAgent("low_turnover"))
        generic_style = run_principal_holding_prediction_game(OfflineAgent("generic_style"))
        self.assertEqual(configured["task"], "principal_holding_prediction")
        self.assertEqual(configured["n_trials"], len(PRINCIPAL_HOLDING_CASES))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertGreater(configured["min_oracle_margin"], 0.05)
        self.assertEqual(configured["low_margin_rate_005"], 0.0)
        self.assertGreater(max_return["mean_score_regret"], 0.1)
        self.assertGreater(max_return["market_return_miss_rate"], 0.5)
        self.assertGreater(low_turnover["mean_score_regret"], 0.05)
        self.assertGreater(low_turnover["low_turnover_miss_rate"], 0.5)
        self.assertGreater(generic_style["mean_score_regret"], 0.005)
        self.assertGreater(generic_style["generic_style_miss_rate"], 0.2)

    def test_noisy_principal_holding_prediction_flags_inversion_problem(self):
        configured = run_noisy_principal_holding_prediction_game(OfflineAgent("oracle"))
        max_return = run_noisy_principal_holding_prediction_game(OfflineAgent("max_return"))
        low_turnover = run_noisy_principal_holding_prediction_game(OfflineAgent("low_turnover"))
        generic_style = run_noisy_principal_holding_prediction_game(OfflineAgent("generic_style"))
        mechanical_flow = run_noisy_principal_holding_prediction_game(OfflineAgent("mechanical_flow"))
        self.assertEqual(configured["task"], "principal_holding_prediction_noisy")
        self.assertEqual(configured["n_trials"], len(NOISY_PRINCIPAL_HOLDING_CASES))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertGreater(configured["min_oracle_margin"], 0.05)
        self.assertEqual(configured["low_margin_rate_005"], 0.0)
        self.assertGreater(max_return["mean_score_regret"], 0.1)
        self.assertGreater(max_return["market_return_miss_rate"], 0.5)
        self.assertGreater(low_turnover["mean_score_regret"], 0.05)
        self.assertGreater(low_turnover["low_turnover_miss_rate"], 0.5)
        self.assertGreater(generic_style["mean_score_regret"], 0.005)
        self.assertGreater(generic_style["generic_style_miss_rate"], 0.2)
        self.assertGreater(mechanical_flow["mean_score_regret"], 0.005)
        self.assertGreater(mechanical_flow["mechanical_flow_miss_rate"], 0.2)

    def test_principal_holding_notes_flags_implicit_filing_artifacts(self):
        configured = run_principal_holding_prediction_notes_game(OfflineAgent("oracle"))
        max_return = run_principal_holding_prediction_notes_game(OfflineAgent("max_return"))
        low_turnover = run_principal_holding_prediction_notes_game(OfflineAgent("low_turnover"))
        generic_style = run_principal_holding_prediction_notes_game(OfflineAgent("generic_style"))
        mechanical_flow = run_principal_holding_prediction_notes_game(OfflineAgent("mechanical_flow"))
        self.assertEqual(configured["task"], "principal_holding_prediction_notes")
        self.assertEqual(configured["n_trials"], len(PRINCIPAL_HOLDING_NOTES_CASES))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertGreater(configured["min_oracle_margin"], 0.05)
        self.assertEqual(configured["low_margin_rate_005"], 0.0)
        self.assertGreater(max_return["mean_score_regret"], 0.1)
        self.assertGreater(max_return["market_return_miss_rate"], 0.5)
        self.assertGreater(low_turnover["mean_score_regret"], 0.05)
        self.assertGreater(low_turnover["low_turnover_miss_rate"], 0.5)
        self.assertGreater(generic_style["mean_score_regret"], 0.005)
        self.assertGreater(generic_style["generic_style_miss_rate"], 0.2)
        self.assertGreater(mechanical_flow["mean_score_regret"], 0.005)
        self.assertGreater(mechanical_flow["mechanical_flow_miss_rate"], 0.2)

    def test_principal_holding_blind_notes_flags_label_shortcut_removal(self):
        configured = run_principal_holding_prediction_blind_notes_game(OfflineAgent("oracle"))
        max_return = run_principal_holding_prediction_blind_notes_game(OfflineAgent("max_return"))
        low_turnover = run_principal_holding_prediction_blind_notes_game(OfflineAgent("low_turnover"))
        generic_style = run_principal_holding_prediction_blind_notes_game(OfflineAgent("generic_style"))
        mechanical_flow = run_principal_holding_prediction_blind_notes_game(OfflineAgent("mechanical_flow"))
        self.assertEqual(configured["task"], "principal_holding_prediction_blind_notes")
        self.assertEqual(configured["n_trials"], len(PRINCIPAL_HOLDING_BLIND_NOTES_CASES))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertEqual(configured["accuracy"], 1.0)
        self.assertGreater(configured["min_oracle_margin"], 0.05)
        self.assertEqual(configured["low_margin_rate_005"], 0.0)
        self.assertGreater(max_return["mean_score_regret"], 0.1)
        self.assertGreater(max_return["market_return_miss_rate"], 0.5)
        self.assertGreater(low_turnover["mean_score_regret"], 0.05)
        self.assertGreater(low_turnover["low_turnover_miss_rate"], 0.5)
        self.assertGreater(generic_style["mean_score_regret"], 0.005)
        self.assertGreater(generic_style["generic_style_miss_rate"], 0.2)
        self.assertGreater(mechanical_flow["mean_score_regret"], 0.005)
        self.assertGreater(mechanical_flow["mechanical_flow_miss_rate"], 0.2)

    def test_offline_sweep_ranks_inferred_above_generic_on_principal(self):
        sweep = run_sweep(task="principal_inference", agent_specs=["offline:oracle", "offline:generic_gamma"])
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [row for row in rows if row["task"] == "principal_inference"]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[1]["agent"], "offline:generic_gamma")

    def test_offline_sweep_ranks_principal_prediction_above_market_return(self):
        sweep = run_sweep(
            task="principal_holding_prediction",
            agent_specs=[
                "offline:oracle",
                "offline:generic_style",
                "offline:low_turnover",
                "offline:max_return",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [row for row in rows if row["task"] == "principal_holding_prediction"]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[-1]["agent"], "offline:max_return")

    def test_offline_sweep_ranks_noisy_principal_prediction_above_flow_blind(self):
        sweep = run_sweep(
            task="principal_holding_prediction_noisy",
            agent_specs=[
                "offline:oracle",
                "offline:mechanical_flow",
                "offline:generic_style",
                "offline:max_return",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [row for row in rows if row["task"] == "principal_holding_prediction_noisy"]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[-1]["agent"], "offline:max_return")

    def test_offline_sweep_ranks_note_principal_prediction_above_flow_blind(self):
        sweep = run_sweep(
            task="principal_holding_prediction_notes",
            agent_specs=[
                "offline:oracle",
                "offline:mechanical_flow",
                "offline:generic_style",
                "offline:max_return",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [row for row in rows if row["task"] == "principal_holding_prediction_notes"]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[-1]["agent"], "offline:max_return")

    def test_offline_sweep_ranks_blind_note_principal_prediction_above_flow_blind(self):
        sweep = run_sweep(
            task="principal_holding_prediction_blind_notes",
            agent_specs=[
                "offline:oracle",
                "offline:mechanical_flow",
                "offline:generic_style",
                "offline:max_return",
            ],
        )
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [
            row for row in rows if row["task"] == "principal_holding_prediction_blind_notes"
        ]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[-1]["agent"], "offline:max_return")

