"""Known-answer tests for the revealed-preference axiom core.

Every assertion here is a hand-derived or independently-validated golden value.
The point is that the gate instrument is *correct*, not just that it runs — a
GARP checker that always returns True would pass a smoke test and silently make
every model look rational. These golden cases were validated against a separate
reference implementation before the constants were baked in (see the session
scratch validation): a strict 2-cycle (CCEI 0.8), a Cobb-Douglas maximizer
(CCEI 1.0), and a pure 3-cycle that passes WARP but fails GARP (CCEI 0.75).
"""

import unittest

from aeread_lab.core.axioms import (
    Observation,
    ccei,
    dominated_choice_violations,
    garp_holds,
    monotonicity_violations,
    transitivity_violations,
    warp_violations,
)


def _obs(prices, bundle):
    return Observation(prices=tuple(float(p) for p in prices), bundle=tuple(float(b) for b in bundle))


class WarpTests(unittest.TestCase):
    def test_strict_two_cycle_is_one_warp_violation(self):
        # Classic price-reversal: each bundle affordable-and-chosen-against the other.
        obs = [_obs((1, 2), (1, 2)), _obs((2, 1), (2, 1))]
        count, pairs = warp_violations(obs)
        self.assertEqual(count, 1)
        self.assertEqual(pairs, [(0, 1)])

    def test_identical_bundles_are_not_a_violation(self):
        # Revealed indifference, not inconsistency.
        obs = [_obs((1, 2), (3, 3)), _obs((2, 1), (3, 3))]
        count, _ = warp_violations(obs)
        self.assertEqual(count, 0)

    def test_cobb_douglas_has_no_warp_violation(self):
        obs = _cobb_douglas_obs()
        count, _ = warp_violations(obs)
        self.assertEqual(count, 0)


class GarpTests(unittest.TestCase):
    def test_cobb_douglas_satisfies_garp(self):
        self.assertTrue(garp_holds(_cobb_douglas_obs()))

    def test_two_cycle_violates_garp(self):
        obs = [_obs((1, 2), (1, 2)), _obs((2, 1), (2, 1))]
        self.assertFalse(garp_holds(obs))

    def test_three_cycle_violates_garp_but_passes_warp(self):
        # THE load-bearing case: a length-3 revealed-preference cycle with no
        # pairwise reversal. WARP sees nothing; GARP (via transitive closure)
        # catches it. This proves the instrument does more than the old E11
        # WARP-only toy.
        obs = _three_cycle_obs()
        warp_count, _ = warp_violations(obs)
        self.assertEqual(warp_count, 0, "3-cycle must have zero WARP violations")
        self.assertFalse(garp_holds(obs), "3-cycle must violate GARP")


class CceiTests(unittest.TestCase):
    def test_cobb_douglas_ccei_is_one(self):
        self.assertAlmostEqual(ccei(_cobb_douglas_obs()), 1.0, places=6)

    def test_two_cycle_ccei_is_point_eight(self):
        obs = [_obs((1, 2), (1, 2)), _obs((2, 1), (2, 1))]
        self.assertAlmostEqual(ccei(obs), 0.8, places=4)

    def test_three_cycle_ccei_is_point_seven_five(self):
        self.assertAlmostEqual(ccei(_three_cycle_obs()), 0.75, places=4)

    def test_ccei_monotone_in_violation_severity(self):
        # A milder reversal should have a higher CCEI than a severe one.
        mild = [_obs((1, 1.2), (1, 1.2)), _obs((1.2, 1), (1.2, 1))]
        severe = [_obs((1, 5), (1, 5)), _obs((5, 1), (5, 1))]
        self.assertGreater(ccei(mild), ccei(severe))

    def test_empty_is_trivially_consistent(self):
        self.assertEqual(ccei([]), 1.0)


class DiscreteAxiomTests(unittest.TestCase):
    def test_transitivity_detects_three_cycle(self):
        # a>b, b>c, c>a (a preference cycle).
        choices = {(0, 1): 0, (1, 2): 1, (0, 2): 2}
        count, cycles = transitivity_violations(choices, 3)
        self.assertEqual(count, 1)
        self.assertIn((0, 1, 2), cycles)

    def test_transitivity_clean_chain(self):
        # a>b, b>c, a>c (transitive).
        choices = {(0, 1): 0, (1, 2): 1, (0, 2): 0}
        count, _ = transitivity_violations(choices, 3)
        self.assertEqual(count, 0)

    def test_dominated_choice_flagged(self):
        # Menu 0: option 1 (2,2) dominates chosen option 0 (1,1).
        menus = [[(1, 1), (2, 2)], [(3, 1), (1, 3)]]
        choices = [0, 1]
        count, idx = dominated_choice_violations(menus, choices)
        self.assertEqual(count, 1)
        self.assertEqual(idx, [0])

    def test_no_dominance_violation_on_pareto_frontier(self):
        menus = [[(3, 1), (1, 3)]]
        choices = [0]
        count, _ = dominated_choice_violations(menus, choices)
        self.assertEqual(count, 0)

    def test_monotonicity_violation(self):
        # Bigger budget (10) achieved less utility (1.0) than smaller budget (5 -> 2.0).
        count, pairs = monotonicity_violations([10.0, 5.0], [1.0, 2.0])
        self.assertEqual(count, 1)
        self.assertEqual(pairs, [(0, 1)])

    def test_monotonicity_clean(self):
        count, _ = monotonicity_violations([10.0, 5.0], [2.0, 1.0])
        self.assertEqual(count, 0)


# ----- golden fixtures -----


def _cobb_douglas_obs():
    """A Cobb-Douglas (alpha=0.5) maximizer across 4 price vectors -> GARP-consistent."""
    prices = [(1, 1), (1, 3), (3, 1), (2, 2)]
    budget = 12.0
    obs = []
    for px, py in prices:
        # x = 0.5*B/px, y = 0.5*B/py
        obs.append(_obs((px, py), (0.5 * budget / px, 0.5 * budget / py)))
    return obs


def _three_cycle_obs():
    """A pure length-3 revealed-preference cycle: WARP-clean, GARP-violating, CCEI 0.75."""
    p3 = [(1, 1, 2), (2, 1, 1), (1, 2, 1)]
    x3 = [(0, 2, 1), (1, 0, 2), (2, 1, 0)]
    return [_obs(p, x) for p, x in zip(p3, x3)]


if __name__ == "__main__":
    unittest.main()
