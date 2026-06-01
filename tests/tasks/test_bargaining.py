# Split from the former monolithic tests/test_tasks.py — bargaining cluster (9 tests).
# Shared imports + helper agents live in tests/tasks/_shared.py.
from tests.tasks._shared import *  # noqa: F401,F403
from tests.tasks._shared import unittest  # explicit


class BargainingTests(unittest.TestCase):

    def test_sample_limit_slices_belief_bargaining_interaction_cases(self):
        results = run_tasks("belief_bargaining_interaction", OfflineAgent("oracle"), sample_limit=1)
        self.assertEqual(results[0]["n_trials"], 1)
        self.assertLess(results[0]["mean_expected_surplus_gap"], 1e-9)

    def test_bargaining_splits_gate_from_grade(self):
        grade_summary = run_bargaining_game(OfflineAgent("oracle"))
        gate_summary = run_bargaining_game(OfflineAgent("gate"))
        self.assertLess(grade_summary["mean_grade_error"], 1e-9)
        self.assertEqual(gate_summary["mean_gate_surplus_gap"], 0.0)
        self.assertGreater(gate_summary["mean_grade_error"], 0.1)

    def test_bargaining_flags_alternating_and_hidden_reservation_failures(self):
        configured = run_bargaining_game(OfflineAgent("oracle"))
        round_blind = run_bargaining_game(OfflineAgent("round_blind"))
        optimistic = run_bargaining_game(OfflineAgent("optimistic_budget"))
        case_keys = {trial["case"]["key"] for trial in configured["trials"]}
        self.assertIn("enterprise_counteroffer", case_keys)
        self.assertIn("hidden_budget_vendor", case_keys)
        self.assertLess(configured["mean_grade_error"], 1e-9)
        self.assertEqual(round_blind["alternating_offer_miss_rate"], 1.0)
        self.assertEqual(optimistic["hidden_reservation_miss_rate"], 1.0)

    def test_belief_bargaining_flags_ignored_cues(self):
        calibrated = run_belief_bargaining_game(OfflineAgent("oracle"))
        prior = run_belief_bargaining_game(OfflineAgent("prior"))
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(prior["mean_expected_surplus_gap"], 1.0)
        self.assertGreater(prior["cue_switch_miss_rate"], 0.5)

    def test_belief_bargaining_flags_single_cue_multi_turn_failures(self):
        calibrated = run_belief_bargaining_game(OfflineAgent("oracle"))
        single_cue = run_belief_bargaining_game(OfflineAgent("single_cue"))
        case_keys = {trial["case"]["key"] for trial in calibrated["trials"]}
        self.assertIn("renewal_counteroffer_sequence", case_keys)
        self.assertIn("walkaway_then_procurement_reentry", case_keys)
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(single_cue["mean_expected_surplus_gap"], 10.0)
        self.assertEqual(single_cue["multi_turn_miss_rate"], 1.0)

    def test_belief_bargaining_flags_strategic_bayes_scaffold(self):
        class ScaffoldedAgent:
            name = "test:scaffolded"

            def complete(self, system, user):
                if "condition=posterior_scaffold" in user:
                    if "case=strategic_budget_bluff" in user:
                        return "FINAL_PRICE: 240"
                    if "case=pooling_discount_request" in user:
                        return "FINAL_PRICE: 285"
                if "case=strategic_budget_bluff" in user:
                    return "FINAL_PRICE: 150"
                if "case=pooling_discount_request" in user:
                    return "FINAL_PRICE: 115"
                return "FINAL_PRICE: 0"

        strategic_cases = [case for case in BELIEF_BARGAINING_CASES if case.strategic_likelihood]
        scaffolded = run_belief_bargaining_game(ScaffoldedAgent(), cases=strategic_cases)
        literal = run_belief_bargaining_game(OfflineAgent("literal_claim"), cases=strategic_cases)
        self.assertEqual(scaffolded["strategic_base_miss_rate"], 1.0)
        self.assertEqual(scaffolded["strategic_scaffold_miss_rate"], 0.0)
        self.assertGreater(scaffolded["strategic_scaffold_improvement"], 50.0)
        self.assertEqual(literal["strategic_base_miss_rate"], 1.0)
        self.assertGreater(literal["mean_strategic_base_gap"], 50.0)

    def test_belief_bargaining_interaction_flags_single_offer_and_prior_plans(self):
        calibrated = run_belief_bargaining_interaction_game(OfflineAgent("oracle"))
        single_offer = run_belief_bargaining_interaction_game(OfflineAgent("single_offer"))
        prior = run_belief_bargaining_interaction_game(OfflineAgent("prior"))
        case_keys = {trial["case"]["key"] for trial in calibrated["trials"]}
        self.assertIn("renewal_rejection_policy", case_keys)
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(single_offer["mean_expected_surplus_gap"], 5.0)
        self.assertGreater(single_offer["single_offer_miss_rate"], 0.5)
        self.assertGreater(prior["mean_expected_surplus_gap"], 1.0)
        self.assertGreater(prior["prior_plan_miss_rate"], 0.25)

    def test_offline_sweep_ranks_oracle_above_gate_on_bargaining_grade(self):
        sweep = run_sweep(task="bargaining", agent_specs=["offline:oracle", "offline:gate"])
        rows = rank_rows(comparison_table(sweep))
        bargaining_rows = [row for row in rows if row["task"] == "bargaining"]
        self.assertEqual(bargaining_rows[0]["agent"], "offline:oracle")
        self.assertEqual(bargaining_rows[1]["agent"], "offline:gate")

    def test_offline_sweep_ranks_calibrated_above_prior_on_belief_bargaining(self):
        sweep = run_sweep(task="belief_bargaining", agent_specs=["offline:oracle", "offline:prior"])
        rows = rank_rows(comparison_table(sweep))
        belief_rows = [row for row in rows if row["task"] == "belief_bargaining"]
        self.assertEqual(belief_rows[0]["agent"], "offline:oracle")
        self.assertEqual(belief_rows[1]["agent"], "offline:prior")

