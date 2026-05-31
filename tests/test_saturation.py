"""Harness tests for the rationality-saturation gate task.

These prove the instrument has DYNAMIC RANGE (the validity-control discipline):
- the oracle (Cobb-Douglas maximizer) saturates: CCEI ≈ 1.0, GARP passes, 0 WARP
  violations, on every menu set;
- the violation controls (random, cycler) produce CCEI < 1.0 and GARP failures —
  so the harness demonstrably FIRES when consistency is absent;
- the multi-seed battery reports CIs (mandatory-CI rule);
- the tolerance sweep shows the verdict is stable across epsilons (not an
  artifact).

A gate that only ever returns "saturated" is not a gate. These tests are the
proof it isn't.
"""

import unittest

from aeread_lab.models import OfflineAgent
from aeread_lab.tasks.saturation import (
    Menu,
    cobb_douglas_allocation,
    default_alphas,
    default_menu_sets,
    generate_menu_set,
    run_saturation_battery,
    run_saturation_trial,
    score_trial,
    tolerance_sweep,
)


class OracleSaturationTests(unittest.TestCase):
    def test_oracle_saturates_every_menu_set(self):
        summary = run_saturation_battery(OfflineAgent("oracle"))
        self.assertTrue(summary["saturated"])
        self.assertGreaterEqual(summary["mean_ccei"], 0.999)
        self.assertEqual(summary["garp_pass_rate"], 1.0)
        self.assertEqual(summary["total_warp_violations"], 0)
        self.assertEqual(summary["min_ccei"], 1.0)

    def test_oracle_battery_reports_cis(self):
        summary = run_saturation_battery(OfflineAgent("oracle"))
        self.assertEqual(summary["n_menu_sets"], 8)
        lo, hi = summary["mean_ccei_ci95"]
        self.assertAlmostEqual(lo, 1.0, places=6)
        self.assertAlmostEqual(hi, 1.0, places=6)
        # Wilson CI on a perfect pass rate is defined and upper-bounded at 1.
        wlo, whi = summary["garp_pass_rate_ci95"]
        self.assertLessEqual(whi, 1.0)
        self.assertGreater(whi, 0.5)

    def test_oracle_verdict_is_tolerance_stable(self):
        summary = run_saturation_battery(OfflineAgent("oracle"))
        self.assertTrue(summary["tolerance_verdict_stable"])
        self.assertLess(summary["tolerance_max_ccei_spread"], 1e-6)


class ViolationControlTests(unittest.TestCase):
    """Dynamic-range proof: the harness must catch incoherence when it's there."""

    def test_cycler_fails_the_gate(self):
        summary = run_saturation_battery(OfflineAgent("cycler"))
        self.assertFalse(summary["saturated"])
        self.assertLess(summary["mean_ccei"], 0.99)
        self.assertLess(summary["garp_pass_rate"], 1.0)

    def test_random_policy_produces_inconsistency(self):
        summary = run_saturation_battery(OfflineAgent("random"))
        self.assertFalse(summary["saturated"])
        # random should violate on at least some sets (GARP pass rate < 1).
        self.assertLess(summary["garp_pass_rate"], 1.0)

    def test_oracle_and_cycler_are_separated(self):
        oracle = run_saturation_battery(OfflineAgent("oracle"))
        cycler = run_saturation_battery(OfflineAgent("cycler"))
        self.assertGreater(oracle["mean_ccei"], cycler["mean_ccei"])


class MenuConstructionTests(unittest.TestCase):
    def test_default_battery_shape(self):
        sets = default_menu_sets()
        self.assertEqual(len(sets), 8)
        self.assertEqual(sum(1 for s in sets if s.n_goods == 2), 4)
        self.assertEqual(sum(1 for s in sets if s.n_goods == 3), 4)
        for s in sets:
            self.assertEqual(len(s.menus), 8)

    def test_menu_generation_is_deterministic(self):
        a = generate_menu_set("x", seed=7)
        b = generate_menu_set("x", seed=7)
        self.assertEqual([m.prices for m in a.menus], [m.prices for m in b.menus])

    def test_cobb_douglas_allocation_exhausts_budget(self):
        menu = Menu(key="t", prices=(2.0, 3.0), budget=60.0)
        alphas = default_alphas(2)
        bundle = cobb_douglas_allocation(menu, alphas)
        spend = sum(q * p for q, p in zip(bundle, menu.prices))
        self.assertAlmostEqual(spend, 60.0, places=6)


class TrialScoringTests(unittest.TestCase):
    def test_oracle_trial_scores_clean(self):
        sets = default_menu_sets()
        trial = run_saturation_trial(OfflineAgent("oracle"), sets[0])
        score = score_trial(sets[0], trial)
        self.assertTrue(score["garp_pass"])
        self.assertEqual(score["warp_violations"], 0)
        self.assertAlmostEqual(score["ccei"], 1.0, places=6)
        self.assertEqual(score["parse_failures"], 0)

    def test_tolerance_sweep_reports_grid(self):
        sets = default_menu_sets()
        trial = run_saturation_trial(OfflineAgent("oracle"), sets[0])
        sweep = tolerance_sweep(sets[0], trial)
        self.assertEqual(len(sweep["ccei_by_tol"]), len(sweep["grid"]))
        self.assertTrue(sweep["garp_verdict_stable"])

    def test_parse_failure_is_counted_not_crashed(self):
        # An agent with no saturation handler returns a non-bundle string.
        trial = run_saturation_trial(OfflineAgent("nonexistent_policy_xyz"), default_menu_sets()[0])
        # Either it parsed (default->oracle path) or it counted a parse failure;
        # crucially it must not raise and must yield well-defined observations.
        self.assertEqual(len(trial.bundles), 8)


if __name__ == "__main__":
    unittest.main()
