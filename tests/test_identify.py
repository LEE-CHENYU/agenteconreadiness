"""Layer 2 identification tests — parameter recovery, model selection, and the
identifiability audit.

The rigor bar mirrors the gate's golden-answer tests: every assertion is a
ground-truth recovery (plant a known utility, fit it back) or a known
non-identification case. An estimator that runs but doesn't recover the planted
value would silently mislabel every model; these tests prove it recovers.

Validated empirically before constants were fixed (session scratch): CRRA γ
recovered to median≈true with 5-95% spread ≈ ±0.1 at σ=0.03 across
γ ∈ {0.7,1.5,3,5}; CRRA-vs-CARA fractions separate by wealth (CRRA flat 0.20,
CARA declining 0.998→0.028). Tolerances below carry margin over that.
"""

import unittest

from aeread_lab.core.identify import (
    AllocationObservation,
    Gamble,
    DEFAULT_GAMBLES,
    DEFAULT_WEALTHS,
    cara_class,
    crra_class,
    crra_optimal_fraction,
    fit_class,
    select_class,
    simulate_allocations,
)


# ---------- #1 parameter recovery ----------


class ParameterRecoveryTests(unittest.TestCase):
    def _recover_crra(self, true_gamma, sigma=0.03, seed=0):
        klass = crra_class()
        obs = simulate_allocations(
            klass, true_gamma, DEFAULT_GAMBLES, DEFAULT_WEALTHS, sigma=sigma, seed=seed
        )
        return fit_class(klass, obs)

    def test_recovers_moderate_risk_aversion(self):
        fit = self._recover_crra(3.0)
        self.assertAlmostEqual(fit.theta_hat, 3.0, delta=0.4)
        self.assertFalse(fit.weakly_identified)

    def test_recovers_low_risk_aversion(self):
        fit = self._recover_crra(1.5)
        self.assertAlmostEqual(fit.theta_hat, 1.5, delta=0.4)

    def test_recovers_high_risk_aversion(self):
        fit = self._recover_crra(5.0)
        self.assertAlmostEqual(fit.theta_hat, 5.0, delta=0.5)

    def test_recovers_near_log_utility(self):
        fit = self._recover_crra(0.7)
        self.assertAlmostEqual(fit.theta_hat, 0.7, delta=0.4)

    def test_recovery_stable_across_seeds(self):
        gammas = [self._recover_crra(3.0, seed=s).theta_hat for s in range(8)]
        # every seed within delta; spread tight (the multi-seed discipline)
        self.assertTrue(all(abs(g - 3.0) < 0.6 for g in gammas), gammas)
        self.assertLess(max(gammas) - min(gammas), 0.8)

    def test_higher_noise_widens_ci(self):
        clean = self._recover_crra(3.0, sigma=0.02)
        noisy = self._recover_crra(3.0, sigma=0.12)
        self.assertGreaterEqual(noisy.ci_width, clean.ci_width)


# ---------- #2 multi-class model selection ----------


class ModelSelectionTests(unittest.TestCase):
    def test_recovers_crra_when_data_is_crra(self):
        klass = crra_class()
        obs = simulate_allocations(klass, 3.0, DEFAULT_GAMBLES, DEFAULT_WEALTHS, sigma=0.02, seed=1)
        sel = select_class(obs, [crra_class(), cara_class()])
        self.assertEqual(sel.best_class, "CRRA")
        self.assertGreater(sel.posterior["CRRA"], sel.posterior["CARA"])

    def test_recovers_cara_when_data_is_cara(self):
        klass = cara_class()
        obs = simulate_allocations(klass, 0.01, DEFAULT_GAMBLES, DEFAULT_WEALTHS, sigma=0.02, seed=2)
        sel = select_class(obs, [crra_class(), cara_class()])
        self.assertEqual(sel.best_class, "CARA")
        self.assertGreater(sel.posterior["CARA"], sel.posterior["CRRA"])

    def test_posterior_is_a_distribution(self):
        obs = simulate_allocations(crra_class(), 3.0, DEFAULT_GAMBLES, DEFAULT_WEALTHS, seed=3)
        sel = select_class(obs, [crra_class(), cara_class()])
        self.assertAlmostEqual(sum(sel.posterior.values()), 1.0, places=9)
        self.assertEqual(len(sel.fits), 2)


# ---------- #3 identifiability audit ----------


class IdentifiabilityAuditTests(unittest.TestCase):
    def test_rich_wealth_range_is_decisive(self):
        # CRRA vs CARA separate cleanly only when wealth varies widely.
        obs = simulate_allocations(
            crra_class(), 3.0, DEFAULT_GAMBLES, DEFAULT_WEALTHS, sigma=0.02, seed=4
        )
        sel = select_class(obs, [crra_class(), cara_class()])
        self.assertTrue(sel.decisive)

    def test_single_wealth_under_identifies_class(self):
        # At ONE wealth level, CRRA and CARA can mimic each other (both just pick a
        # fraction) -> the class is NOT identified. The audit must say so.
        obs = simulate_allocations(
            crra_class(), 3.0, DEFAULT_GAMBLES, wealths=(200.0,), sigma=0.02, seed=5
        )
        sel = select_class(obs, [crra_class(), cara_class()])
        self.assertFalse(sel.decisive, f"single-wealth should be non-decisive; posterior={sel.posterior}")

    def test_too_few_observations_flag_weak_identification(self):
        # One uninformative observation -> parameter not pinned down.
        obs = [AllocationObservation(gamble=Gamble(0.5, 0.8, -0.4), wealth=100.0, fraction=0.2)]
        fit = fit_class(crra_class(), obs)
        self.assertTrue(fit.weakly_identified)

    def test_boundary_estimate_flagged_weak(self):
        # A risk-neutral-ish agent that bets the max on every gamble pins gamma at
        # the grid floor -> boundary estimate, flagged weak (ran out of range).
        gambles = DEFAULT_GAMBLES
        obs = [
            AllocationObservation(gamble=gm, wealth=w, fraction=1.0)
            for w in DEFAULT_WEALTHS
            for gm in gambles
        ]
        fit = fit_class(crra_class(), obs)
        self.assertTrue(fit.weakly_identified)


# ---------- class-signature sanity (the separability the selection relies on) ----------


class ClassSignatureTests(unittest.TestCase):
    def test_crra_fraction_is_wealth_invariant(self):
        gm = Gamble(0.5, 0.8, -0.4)
        fractions = [crra_optimal_fraction(gm, w, 3.0) for w in (20, 200, 2000)]
        self.assertLess(max(fractions) - min(fractions), 1e-6)

    def test_cara_fraction_declines_with_wealth(self):
        from aeread_lab.core.identify import cara_optimal_fraction

        gm = Gamble(0.5, 0.8, -0.4)
        low = cara_optimal_fraction(gm, 20.0, 0.01)
        high = cara_optimal_fraction(gm, 2000.0, 0.01)
        self.assertGreater(low, high)


if __name__ == "__main__":
    unittest.main()
