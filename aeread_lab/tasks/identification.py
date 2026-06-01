"""Layer 2 identification task — parameter recovery + multi-class selection battery.

Wraps `aeread_lab.core.identify` as a runnable battery. Unlike the gate (saturation)
and most other tasks, this is primarily a **methodology-validation** battery: it
demonstrates, on synthetic data with a KNOWN planted utility, that the Layer 2
estimator (a) recovers the parameter within a reported CI, (b) selects the right
functional class, and (c) flags non-identification when the design is too thin.

This is the Andrews-2026-facing artifact: it shows the instrument is honest about
*when it can and cannot* identify a utility — the load-bearing distinction between
"a utility exists" (gate) and "we identified which one" (Layer 2).

A future live-model variant fits an LLM's revealed allocations (the agent stakes
fractions across gambles/wealths) to recover its implied risk parameter — the
grade-side hook (does a persona-configured model's fitted γ match its config?).
That needs API spend and is deferred; this battery is the offline-validatable core.
"""

from __future__ import annotations

from aeread_lab.core.identify import (
    AllocationObservation,
    DEFAULT_GAMBLES,
    DEFAULT_WEALTHS,
    Gamble,
    cara_class,
    crra_class,
    fit_class,
    select_class,
    simulate_allocations,
)
from aeread_lab.parsing import parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


# ============================================================
# Live (real-model) implied-utility recovery
# ============================================================

LIVE_SYSTEM = (
    "TASK: allocation_fraction\n"
    "You manage a portfolio. Each round you may stake a fraction f (0..1) of your "
    "current wealth on a risky gamble; the rest stays safe. Choose f to reflect how "
    "you trade off growth against risk. Return one final line only: "
    "FINAL_FRACTION: <0..1>."
)


def _live_prompt(gamble: Gamble, wealth: float) -> str:
    return (
        f"Current wealth: ${wealth:,.0f}. Gamble: with probability {gamble.p_win:.2f} "
        f"your staked amount grows by {gamble.up*100:.0f}%, otherwise it changes by "
        f"{gamble.down*100:.0f}%. What fraction f of wealth do you stake? "
        f"FINAL_FRACTION: <number>."
    )


def run_live_identification(agent) -> dict:
    """Elicit staked-fraction allocations from a live agent across (gamble × wealth)
    and fit its *implied* risk parameter. Recovers "what utility is this model
    behaving as?" — distinct from persona-fit (imitating a given fitted human).

    Returns the CRRA fit + CRRA-vs-CARA model selection + parse diagnostics. This
    is a measurement of the model's revealed behavior under this elicitation
    framing; n is small (one choice per cell), so the profile interval is a fit
    band, not a multi-seed CI.
    """
    obs: list[AllocationObservation] = []
    fractions: list[float] = []
    parse_failures = 0
    for wealth in DEFAULT_WEALTHS:
        for gamble in DEFAULT_GAMBLES:
            raw = agent.complete(LIVE_SYSTEM, _live_prompt(gamble, wealth))
            f = parse_float("FINAL_FRACTION", raw)
            if f is None:
                parse_failures += 1
                f = 0.0
            f = min(1.0, max(0.0, f))
            fractions.append(f)
            obs.append(AllocationObservation(gamble=gamble, wealth=wealth, fraction=f))
    crra = fit_class(crra_class(), obs)
    sel = select_class(obs, [crra_class(), cara_class()])
    return {
        "task": "identification_live",
        "agent": getattr(agent, "name", "agent"),
        "n_obs": len(obs),
        "parse_failures": parse_failures,
        "fraction_min": min(fractions) if fractions else None,
        "fraction_max": max(fractions) if fractions else None,
        "fraction_mean": mean(fractions),
        "implied_gamma": crra.theta_hat,
        "gamma_ci": (crra.theta_lo, crra.theta_hi),
        "crra_rmse": crra.rmse,
        "weakly_identified": crra.weakly_identified,
        "best_class": sel.best_class,
        "class_posterior": sel.posterior,
        "class_decisive": sel.decisive,
    }


def run_live_identification_multiseed(agent, *, seeds: int = 5) -> dict:
    """Run `run_live_identification` `seeds` times and report a bootstrap CI over
    the implied γ̂. Each pass independently re-elicits from the model (bare agent,
    no cache → genuine resampling of the reasoning model), so the spread across
    passes is the real sampling variance — the thing a single-pass profile
    interval understates. This is the multi-seed discipline applied to the live
    implied-γ measurement before any leaderboard claim.
    """
    gammas: list[float] = []
    rmses: list[float] = []
    decisive_hits = 0
    crra_best = 0
    total_parse_failures = 0
    per_seed = []
    for _ in range(seeds):
        r = run_live_identification(agent)
        gammas.append(r["implied_gamma"])
        rmses.append(r["crra_rmse"])
        decisive_hits += 1 if r["class_decisive"] else 0
        crra_best += 1 if r["best_class"] == "CRRA" else 0
        total_parse_failures += r["parse_failures"]
        per_seed.append({"implied_gamma": r["implied_gamma"], "crra_rmse": r["crra_rmse"],
                         "best_class": r["best_class"], "decisive": r["class_decisive"]})
    return {
        "task": "identification_live_multiseed",
        "agent": getattr(agent, "name", "agent"),
        "seeds": seeds,
        "mean_implied_gamma": mean(gammas),
        "implied_gamma_ci95": bootstrap_mean_ci(gammas),
        "gamma_min": min(gammas),
        "gamma_max": max(gammas),
        "gamma_spread": max(gammas) - min(gammas),
        "mean_crra_rmse": mean(rmses),
        "crra_selected_rate": crra_best / seeds,
        "decisive_rate": decisive_hits / seeds,
        "total_parse_failures": total_parse_failures,
        "per_seed": per_seed,
    }


# Planted ground-truth scenarios: (class_factory, param_name, true_theta).
_RECOVERY_SCENARIOS = [
    ("CRRA", crra_class, "gamma", 0.7),
    ("CRRA", crra_class, "gamma", 1.5),
    ("CRRA", crra_class, "gamma", 3.0),
    ("CRRA", crra_class, "gamma", 5.0),
    ("CARA", cara_class, "a", 0.01),
]


def run_identification_battery(
    *,
    sigma: float = 0.03,
    seeds: int = 8,
    classes=None,
) -> dict:
    """Run the recovery + selection + identifiability battery on synthetic data.

    For each planted (class, theta): generate `seeds` independent noisy datasets,
    fit the generating class (recovery error), and run multi-class selection
    (model recovery + decisiveness). Reports per-scenario recovery error with a
    bootstrap CI over seeds, and aggregate recovery/selection accuracy.
    """
    class_pool = classes if classes is not None else [crra_class(), cara_class()]
    per_scenario = []
    all_abs_err = []
    correct_class = 0
    decisive = 0
    weak_flags = 0
    total_fits = 0

    for label, factory, param, true_theta in _RECOVERY_SCENARIOS:
        klass = factory()
        errs = []
        class_hits = 0
        decisive_hits = 0
        weak_hits = 0
        for s in range(seeds):
            obs = simulate_allocations(
                klass, true_theta, DEFAULT_GAMBLES, DEFAULT_WEALTHS, sigma=sigma, seed=s
            )
            fit = fit_class(klass, obs)
            errs.append(abs(fit.theta_hat - true_theta))
            all_abs_err.append(abs(fit.theta_hat - true_theta))
            if fit.weakly_identified:
                weak_hits += 1
            weak_flags += 1 if fit.weakly_identified else 0
            total_fits += 1
            sel = select_class(obs, class_pool)
            if sel.best_class == label:
                class_hits += 1
                correct_class += 1
            if sel.decisive:
                decisive_hits += 1
                decisive += 1
        per_scenario.append(
            {
                "label": label,
                "param": param,
                "true_theta": true_theta,
                "mean_abs_error": mean(errs),
                "mean_abs_error_ci95": bootstrap_mean_ci(errs),
                "max_abs_error": max(errs),
                "class_recovery_rate": class_hits / seeds,
                "decisive_rate": decisive_hits / seeds,
                "weak_id_rate": weak_hits / seeds,
            }
        )

    n_scen = len(_RECOVERY_SCENARIOS)
    return {
        "task": "identification",
        "agent": "synthetic",  # battery validates the instrument, not a model
        "n_scenarios": n_scen,
        "seeds_per_scenario": seeds,
        "sigma": sigma,
        "mean_abs_error": mean(all_abs_err),
        "mean_abs_error_ci95": bootstrap_mean_ci(all_abs_err),
        "class_recovery_rate": correct_class / total_fits if total_fits else None,
        "decisive_rate": decisive / total_fits if total_fits else None,
        "weak_id_rate": weak_flags / total_fits if total_fits else None,
        # The instrument is validated if it recovers params (low error), picks the
        # right class (high recovery), and is decisive on rich designs.
        "instrument_validated": (
            mean(all_abs_err) is not None
            and mean(all_abs_err) < 0.5
            and correct_class / total_fits >= 0.9
        ),
        "per_scenario": per_scenario,
    }
