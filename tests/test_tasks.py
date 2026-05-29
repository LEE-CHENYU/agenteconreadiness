import unittest

from aeread_lab.models import OfflineAgent, resolve_openai_model
from aeread_lab.reporting import comparison_table, rank_rows
from aeread_lab.runner import run_sweep
from aeread_lab.tasks.adversarial import run_scam_arena
from aeread_lab.tasks.ambiguity import DEFAULT_CASES as AMBIGUITY_CASES
from aeread_lab.tasks.ambiguity import _prompt as ambiguity_prompt
from aeread_lab.tasks.ambiguity import run_ambiguity_game
from aeread_lab.tasks.auction import run_auction_game
from aeread_lab.tasks.bargaining import run_bargaining_game
from aeread_lab.tasks.belief_bargaining import DEFAULT_CASES as BELIEF_BARGAINING_CASES
from aeread_lab.tasks.belief_bargaining import _prompt as belief_bargaining_prompt
from aeread_lab.tasks.belief_bargaining import run_belief_bargaining_game
from aeread_lab.tasks.experiment_design import DEFAULT_CASES as EXPERIMENT_CASES
from aeread_lab.tasks.experiment_design import _prompt as experiment_prompt
from aeread_lab.tasks.experiment_design import run_experiment_design_game
from aeread_lab.tasks.exploration import DEFAULT_CASES as EXPLORATION_CASES
from aeread_lab.tasks.exploration import _prompt as exploration_prompt
from aeread_lab.tasks.exploration import run_exploration_game
from aeread_lab.tasks.market import run_market_game
from aeread_lab.tasks.matching import DEFAULT_CASES as MATCHING_CASES
from aeread_lab.tasks.matching import _prompt as matching_prompt
from aeread_lab.tasks.matching import run_matching_game
from aeread_lab.tasks.mechanism import DEFAULT_CASES as MECHANISM_CASES
from aeread_lab.tasks.mechanism import _prompt as mechanism_prompt
from aeread_lab.tasks.mechanism import run_mechanism_game
from aeread_lab.tasks.portfolio import DEFAULT_CASES as PORTFOLIO_CASES
from aeread_lab.tasks.portfolio import _prompt as portfolio_prompt
from aeread_lab.tasks.portfolio import run_portfolio_game
from aeread_lab.tasks.pricing import DEFAULT_CASES as PRICING_CASES
from aeread_lab.tasks.pricing import _prompt as pricing_prompt
from aeread_lab.tasks.pricing import run_pricing_game
from aeread_lab.tasks.principal_inference import DEFAULT_CASES as PRINCIPAL_CASES
from aeread_lab.tasks.principal_inference import _prompt as principal_prompt
from aeread_lab.tasks.principal_inference import run_principal_inference_game
from aeread_lab.tasks.procurement import DEFAULT_CASES as PROCUREMENT_CASES
from aeread_lab.tasks.procurement import _prompt as procurement_prompt
from aeread_lab.tasks.procurement import run_procurement_game
from aeread_lab.tasks.regime import DEFAULT_GAMBLES, _prompt as regime_prompt
from aeread_lab.tasks.retail import run_retail_game
from aeread_lab.tasks.screening import DEFAULT_CASES as SCREENING_CASES
from aeread_lab.tasks.screening import _prompt as screening_prompt
from aeread_lab.tasks.screening import run_screening_game
from aeread_lab.tasks.strategic_drift import DEFAULT_CASES as DRIFT_CASES
from aeread_lab.tasks.strategic_drift import _prompt as strategic_prompt
from aeread_lab.tasks.strategic_drift import run_strategic_drift_game


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
        strategic = strategic_prompt(DRIFT_CASES[0], 1, [])
        exploration = exploration_prompt(EXPLORATION_CASES[0])
        belief_bargaining = belief_bargaining_prompt(BELIEF_BARGAINING_CASES[0])
        principal = principal_prompt(PRINCIPAL_CASES[0])
        portfolio = portfolio_prompt(PORTFOLIO_CASES[0])
        ambiguity = ambiguity_prompt(AMBIGUITY_CASES[0])
        matching = matching_prompt(MATCHING_CASES[0])
        screening = screening_prompt(SCREENING_CASES[0])
        mechanism = mechanism_prompt(MECHANISM_CASES[0])
        experiment = experiment_prompt(EXPERIMENT_CASES[0])
        self.assertNotIn("oracle", regime)
        self.assertNotIn("oracle", procurement)
        self.assertNotIn("oracle", pricing)
        self.assertNotIn("oracle", strategic)
        self.assertNotIn("oracle", exploration)
        self.assertNotIn("oracle", belief_bargaining)
        self.assertNotIn("oracle", principal)
        self.assertNotIn("oracle", portfolio)
        self.assertNotIn("oracle", ambiguity)
        self.assertNotIn("oracle", matching)
        self.assertNotIn("oracle", screening)
        self.assertNotIn("oracle", mechanism)
        self.assertNotIn("oracle", experiment)
        self.assertNotIn("kelly_fraction", regime)
        self.assertNotIn("oracle_price", pricing)

    def test_principal_inference_flags_generic_gamma(self):
        inferred = run_principal_inference_game(OfflineAgent("oracle"))
        generic = run_principal_inference_game(OfflineAgent("generic_gamma"))
        self.assertLess(inferred["mean_fraction_error"], 1e-9)
        self.assertGreater(generic["mean_fraction_error"], 0.1)

    def test_portfolio_flags_max_return_and_low_risk_defaults(self):
        configured = run_portfolio_game(OfflineAgent("oracle"))
        max_return = run_portfolio_game(OfflineAgent("max_return"))
        low_risk = run_portfolio_game(OfflineAgent("low_risk"))
        self.assertLess(configured["mean_utility_regret"], 1e-9)
        self.assertGreater(max_return["mean_utility_regret"], 0.1)
        self.assertGreater(max_return["max_return_miss_rate"], 0.5)
        self.assertGreater(low_risk["low_risk_miss_rate"], 0.2)

    def test_ambiguity_flags_reference_prior_collapse(self):
        robust = run_ambiguity_game(OfflineAgent("oracle"))
        reference = run_ambiguity_game(OfflineAgent("reference_prior"))
        self.assertLess(robust["mean_robust_regret"], 1e-9)
        self.assertGreater(reference["mean_robust_regret"], 10.0)
        self.assertGreater(reference["reference_prior_miss_rate"], 0.5)

    def test_bargaining_splits_gate_from_grade(self):
        grade_summary = run_bargaining_game(OfflineAgent("oracle"))
        gate_summary = run_bargaining_game(OfflineAgent("gate"))
        self.assertLess(grade_summary["mean_grade_error"], 1e-9)
        self.assertEqual(gate_summary["mean_gate_surplus_gap"], 0.0)
        self.assertGreater(gate_summary["mean_grade_error"], 0.1)

    def test_belief_bargaining_flags_ignored_cues(self):
        calibrated = run_belief_bargaining_game(OfflineAgent("oracle"))
        prior = run_belief_bargaining_game(OfflineAgent("prior"))
        self.assertLess(calibrated["mean_expected_surplus_gap"], 1e-9)
        self.assertGreater(prior["mean_expected_surplus_gap"], 1.0)
        self.assertGreater(prior["cue_switch_miss_rate"], 0.5)

    def test_market_flags_collusive_price_drift(self):
        competitive = run_market_game(OfflineAgent("oracle"))
        collusive = run_market_game(OfflineAgent("collusive"))
        self.assertLess(competitive["mean_equilibrium_price_gap"], 0.01)
        self.assertGreater(collusive["mean_equilibrium_price_gap"], 0.9)
        self.assertGreaterEqual(collusive["collusion_rate"], 0.9)

    def test_matching_splits_value_from_stability_and_access(self):
        configured = run_matching_game(OfflineAgent("oracle"))
        max_value = run_matching_game(OfflineAgent("max_value"))
        access = run_matching_game(OfflineAgent("access"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(max_value["mean_score_regret"], 25.0)
        self.assertGreater(max_value["max_value_miss_rate"], 0.5)
        self.assertGreater(access["access_only_miss_rate"], 0.2)

    def test_screening_flags_profit_and_constraint_blind_menus(self):
        configured = run_screening_game(OfflineAgent("oracle"))
        max_profit = run_screening_game(OfflineAgent("max_profit"))
        blind = run_screening_game(OfflineAgent("constraint_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(max_profit["mean_score_regret"], 25.0)
        self.assertGreater(max_profit["max_profit_miss_rate"], 0.5)
        self.assertGreater(blind["constraint_blind_miss_rate"], 0.5)

    def test_auction_splits_revenue_from_configured_objective(self):
        configured = run_auction_game(OfflineAgent("oracle"))
        revenue = run_auction_game(OfflineAgent("revenue"))
        self.assertLess(configured["mean_reserve_error"], 1e-9)
        self.assertGreater(revenue["mean_reserve_error"], 0.1)

    def test_mechanism_splits_revenue_and_risk_blind_defaults(self):
        configured = run_mechanism_game(OfflineAgent("oracle"))
        revenue = run_mechanism_game(OfflineAgent("revenue"))
        risk_blind = run_mechanism_game(OfflineAgent("risk_blind"))
        self.assertLess(configured["mean_score_regret"], 1e-9)
        self.assertGreater(revenue["mean_score_regret"], 25.0)
        self.assertGreater(revenue["revenue_default_miss_rate"], 0.5)
        self.assertGreater(risk_blind["risk_blind_miss_rate"], 0.2)

    def test_strategic_drift_flags_myopic_grabs(self):
        disciplined = run_strategic_drift_game(OfflineAgent("oracle"))
        myopic = run_strategic_drift_game(OfflineAgent("myopic"))
        self.assertEqual(disciplined["drift_rate"], 0.0)
        self.assertGreater(myopic["drift_rate"], 0.9)

    def test_exploration_flags_greedy_exploitation(self):
        exploratory = run_exploration_game(OfflineAgent("oracle"))
        greedy = run_exploration_game(OfflineAgent("exploit"))
        self.assertLess(exploratory["mean_expected_value_gap"], 1e-9)
        self.assertGreater(greedy["mean_expected_value_gap"], 10.0)
        self.assertGreater(greedy["exploration_miss_rate"], 0.5)

    def test_experiment_design_flags_greedy_no_experiment(self):
        designed = run_experiment_design_game(OfflineAgent("oracle"))
        greedy = run_experiment_design_game(OfflineAgent("greedy"))
        self.assertLess(designed["mean_expected_value_gap"], 1e-9)
        self.assertGreater(greedy["mean_expected_value_gap"], 10.0)
        self.assertGreater(greedy["experiment_miss_rate"], 0.5)

    def test_retail_flags_ev_overordering_ruin(self):
        survival = run_retail_game(OfflineAgent("oracle"))
        ev_order = run_retail_game(OfflineAgent("ev_order"))
        self.assertEqual(survival["mean_ruin_probability"], 0.0)
        self.assertGreater(ev_order["mean_ruin_probability"], 0.1)

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

    def test_offline_sweep_ranks_inferred_above_generic_on_principal(self):
        sweep = run_sweep(task="principal_inference", agent_specs=["offline:oracle", "offline:generic_gamma"])
        rows = rank_rows(comparison_table(sweep))
        principal_rows = [row for row in rows if row["task"] == "principal_inference"]
        self.assertEqual(principal_rows[0]["agent"], "offline:oracle")
        self.assertEqual(principal_rows[1]["agent"], "offline:generic_gamma")

    def test_offline_sweep_ranks_configured_above_max_return_on_portfolio(self):
        sweep = run_sweep(task="portfolio", agent_specs=["offline:oracle", "offline:max_return"])
        rows = rank_rows(comparison_table(sweep))
        portfolio_rows = [row for row in rows if row["task"] == "portfolio"]
        self.assertEqual(portfolio_rows[0]["agent"], "offline:oracle")
        self.assertEqual(portfolio_rows[1]["agent"], "offline:max_return")

    def test_offline_sweep_ranks_maxmin_above_reference_prior_on_ambiguity(self):
        sweep = run_sweep(task="ambiguity", agent_specs=["offline:oracle", "offline:reference_prior"])
        rows = rank_rows(comparison_table(sweep))
        ambiguity_rows = [row for row in rows if row["task"] == "ambiguity"]
        self.assertEqual(ambiguity_rows[0]["agent"], "offline:oracle")
        self.assertEqual(ambiguity_rows[1]["agent"], "offline:reference_prior")

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

    def test_offline_sweep_ranks_competitive_above_collusive_on_market(self):
        sweep = run_sweep(task="market", agent_specs=["offline:oracle", "offline:collusive"])
        rows = rank_rows(comparison_table(sweep))
        market_rows = [row for row in rows if row["task"] == "market"]
        self.assertEqual(market_rows[0]["agent"], "offline:oracle")
        self.assertEqual(market_rows[1]["agent"], "offline:collusive")

    def test_offline_sweep_ranks_configured_above_max_value_on_matching(self):
        sweep = run_sweep(task="matching", agent_specs=["offline:oracle", "offline:max_value"])
        rows = rank_rows(comparison_table(sweep))
        matching_rows = [row for row in rows if row["task"] == "matching"]
        self.assertEqual(matching_rows[0]["agent"], "offline:oracle")
        self.assertEqual(matching_rows[1]["agent"], "offline:max_value")

    def test_offline_sweep_ranks_configured_above_max_profit_on_screening(self):
        sweep = run_sweep(task="screening", agent_specs=["offline:oracle", "offline:max_profit"])
        rows = rank_rows(comparison_table(sweep))
        screening_rows = [row for row in rows if row["task"] == "screening"]
        self.assertEqual(screening_rows[0]["agent"], "offline:oracle")
        self.assertEqual(screening_rows[1]["agent"], "offline:max_profit")

    def test_offline_sweep_ranks_configured_above_revenue_on_auction(self):
        sweep = run_sweep(task="auction", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        auction_rows = [row for row in rows if row["task"] == "auction"]
        self.assertEqual(auction_rows[0]["agent"], "offline:oracle")
        self.assertEqual(auction_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_configured_above_revenue_on_mechanism(self):
        sweep = run_sweep(task="mechanism", agent_specs=["offline:oracle", "offline:revenue"])
        rows = rank_rows(comparison_table(sweep))
        mechanism_rows = [row for row in rows if row["task"] == "mechanism"]
        self.assertEqual(mechanism_rows[0]["agent"], "offline:oracle")
        self.assertEqual(mechanism_rows[1]["agent"], "offline:revenue")

    def test_offline_sweep_ranks_disciplined_above_myopic_on_strategic_drift(self):
        sweep = run_sweep(task="strategic_drift", agent_specs=["offline:oracle", "offline:myopic"])
        rows = rank_rows(comparison_table(sweep))
        drift_rows = [row for row in rows if row["task"] == "strategic_drift"]
        self.assertEqual(drift_rows[0]["agent"], "offline:oracle")
        self.assertEqual(drift_rows[1]["agent"], "offline:myopic")

    def test_offline_sweep_ranks_exploration_above_exploit(self):
        sweep = run_sweep(task="exploration", agent_specs=["offline:oracle", "offline:exploit"])
        rows = rank_rows(comparison_table(sweep))
        exploration_rows = [row for row in rows if row["task"] == "exploration"]
        self.assertEqual(exploration_rows[0]["agent"], "offline:oracle")
        self.assertEqual(exploration_rows[1]["agent"], "offline:exploit")

    def test_offline_sweep_ranks_experiment_design_above_greedy(self):
        sweep = run_sweep(task="experiment_design", agent_specs=["offline:oracle", "offline:greedy"])
        rows = rank_rows(comparison_table(sweep))
        experiment_rows = [row for row in rows if row["task"] == "experiment_design"]
        self.assertEqual(experiment_rows[0]["agent"], "offline:oracle")
        self.assertEqual(experiment_rows[1]["agent"], "offline:greedy")

    def test_offline_sweep_ranks_survival_above_ev_order_on_retail(self):
        sweep = run_sweep(task="retail", agent_specs=["offline:oracle", "offline:ev_order"])
        rows = rank_rows(comparison_table(sweep))
        retail_rows = [row for row in rows if row["task"] == "retail"]
        self.assertEqual(retail_rows[0]["agent"], "offline:oracle")
        self.assertEqual(retail_rows[1]["agent"], "offline:ev_order")

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
