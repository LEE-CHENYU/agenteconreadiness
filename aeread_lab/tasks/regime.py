from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean, wilson_ci


REGIME_SYSTEM = (
    "TASK: regime_fraction\n"
    "You are choosing a fraction f in [0,1]. Return one final line only: "
    "FINAL_FRACTION: <number>."
)


@dataclass(frozen=True)
class Gamble:
    key: str
    p_win: float
    win_return: float
    loss_return: float
    horizon: int
    gamma: float = 2.0
    max_drawdown: float = 0.2
    family: str = "even_money"


@dataclass(frozen=True)
class RegimeSpec:
    key: str
    label: str
    real_case: str
    objective: str


@dataclass
class RegimeTrial:
    gamble: Gamble
    regime: str
    oracle_fraction: float
    ev_fraction: float
    kelly_fraction: float
    cvar_fraction: float
    chosen_fraction: float | None
    absolute_error: float | None
    wealth_destruction: bool
    drawdown_violation: bool
    raw_response: str


@dataclass
class RegimeRelationshipGroup:
    gamble: Gamble
    trials: list[RegimeTrial]
    mean_absolute_error: float | None
    relationship_violation: bool
    fit_fail: bool


REGIMES = {
    "ev": RegimeSpec(
        "ev",
        "single-shot EV",
        "one-off procurement, diversified ad auctions, one-shot bidding",
        "maximize expected additive payoff",
    ),
    "kelly": RegimeSpec(
        "kelly",
        "Kelly compounding",
        "reinvested bankroll trading, cash-compounding retail agents",
        "maximize expected log growth over repeated multiplicative wealth",
    ),
    "cvar": RegimeSpec(
        "cvar",
        "CVaR / drawdown bounded",
        "insurance, regulatory capital, startup runway, hard bankruptcy barriers",
        "maximize return subject to worst-tail or drawdown survival constraint",
    ),
    "crra": RegimeSpec(
        "crra",
        "principal CRRA",
        "wealth management, pension/endowment mandate, investor persona fit",
        "maximize configured principal utility with CRRA gamma",
    ),
}


DEFAULT_GAMBLES = [
    Gamble(
        "g01_even_mild",
        p_win=0.58,
        win_return=1.0,
        loss_return=1.0,
        horizon=1,
        gamma=2.0,
        max_drawdown=0.20,
        family="even_money",
    ),
    Gamble(
        "g02_even_compound",
        p_win=0.60,
        win_return=1.0,
        loss_return=1.0,
        horizon=12,
        gamma=3.0,
        max_drawdown=0.12,
        family="even_money",
    ),
    Gamble(
        "g03_upside_skew",
        p_win=0.36,
        win_return=3.0,
        loss_return=1.0,
        horizon=6,
        gamma=1.4,
        max_drawdown=0.25,
        family="upside_skew",
    ),
    Gamble(
        "g04_downside_skew",
        p_win=0.82,
        win_return=0.35,
        loss_return=1.3,
        horizon=18,
        gamma=4.5,
        max_drawdown=0.14,
        family="downside_skew",
    ),
    Gamble(
        "g05_thin_edge",
        p_win=0.515,
        win_return=1.0,
        loss_return=1.0,
        horizon=40,
        gamma=2.5,
        max_drawdown=0.08,
        family="thin_edge",
    ),
    Gamble(
        "g06_hard_barrier",
        p_win=0.82,
        win_return=0.55,
        loss_return=1.9,
        horizon=24,
        gamma=5.0,
        max_drawdown=0.095,
        family="barrier",
    ),
    Gamble(
        "g07_negative_lottery",
        p_win=0.16,
        win_return=4.0,
        loss_return=0.9,
        horizon=1,
        gamma=0.8,
        max_drawdown=0.18,
        family="negative_ev",
    ),
    Gamble(
        "g08_high_frequency_small_edge",
        p_win=0.88,
        win_return=0.18,
        loss_return=0.95,
        horizon=120,
        gamma=6.0,
        max_drawdown=0.06,
        family="small_edge",
    ),
]


RELATIONSHIP_REGIMES = ("ev", "kelly", "cvar", "crra")
RELATIONSHIP_FIT_TOLERANCE = 0.05

DEFAULT_RELATIONSHIP_GAMBLES = [
    Gamble(
        "rel_even",
        p_win=0.60,
        win_return=1.0,
        loss_return=1.0,
        horizon=10,
        gamma=2.0,
        max_drawdown=0.08,
        family="generated_relationship",
    ),
    Gamble(
        "rel_upside",
        p_win=0.38,
        win_return=3.0,
        loss_return=1.0,
        horizon=8,
        gamma=2.2,
        max_drawdown=0.06,
        family="generated_relationship",
    ),
    Gamble(
        "rel_downside",
        p_win=0.82,
        win_return=0.45,
        loss_return=1.2,
        horizon=18,
        gamma=4.0,
        max_drawdown=0.05,
        family="generated_relationship",
    ),
    Gamble(
        "rel_thin",
        p_win=0.54,
        win_return=1.0,
        loss_return=1.0,
        horizon=30,
        gamma=3.0,
        max_drawdown=0.04,
        family="generated_relationship",
    ),
]


def generate_regime_holdout_gambles() -> list[Gamble]:
    candidates = [
        Gamble(
            "hold_even_compound_low_barrier",
            p_win=0.57,
            win_return=1.1,
            loss_return=1.0,
            horizon=20,
            gamma=2.8,
            max_drawdown=0.055,
            family="holdout_even",
        ),
        Gamble(
            "hold_upside_sparse",
            p_win=0.31,
            win_return=4.1,
            loss_return=1.0,
            horizon=9,
            gamma=1.8,
            max_drawdown=0.075,
            family="holdout_upside",
        ),
        Gamble(
            "hold_downside_frequent_loss",
            p_win=0.86,
            win_return=0.32,
            loss_return=1.55,
            horizon=30,
            gamma=5.5,
            max_drawdown=0.05,
            family="holdout_downside",
        ),
        Gamble(
            "hold_micro_edge_high_frequency",
            p_win=0.91,
            win_return=0.14,
            loss_return=1.05,
            horizon=180,
            gamma=7.0,
            max_drawdown=0.035,
            family="holdout_micro_edge",
        ),
        Gamble(
            "hold_negative_skew_one_shot",
            p_win=0.22,
            win_return=3.0,
            loss_return=1.05,
            horizon=1,
            gamma=1.1,
            max_drawdown=0.12,
            family="holdout_negative",
        ),
        Gamble(
            "hold_barrier_positive_ev",
            p_win=0.78,
            win_return=0.62,
            loss_return=1.75,
            horizon=36,
            gamma=4.2,
            max_drawdown=0.045,
            family="holdout_barrier",
        ),
        Gamble(
            "hold_asymmetric_moderate",
            p_win=0.49,
            win_return=1.8,
            loss_return=0.7,
            horizon=14,
            gamma=2.4,
            max_drawdown=0.065,
            family="holdout_asymmetric",
        ),
        Gamble(
            "hold_tail_heavy_repeat",
            p_win=0.68,
            win_return=0.8,
            loss_return=1.35,
            horizon=48,
            gamma=6.0,
            max_drawdown=0.04,
            family="holdout_tail",
        ),
    ]
    holdouts = [
        gamble
        for gamble in candidates
        if relationship_laws_hold(relationship_oracle_fractions(gamble))
    ]
    if len(holdouts) != len(candidates):
        raise ValueError("All regime holdout candidates must satisfy relationship laws")
    return holdouts

def ev_fraction(gamble: Gamble) -> float:
    expected = gamble.p_win * gamble.win_return - (1.0 - gamble.p_win) * gamble.loss_return
    return 1.0 if expected > 0 else 0.0


def kelly_fraction(gamble: Gamble) -> float:
    numerator = gamble.p_win * gamble.win_return - (1.0 - gamble.p_win) * gamble.loss_return
    denominator = gamble.win_return * gamble.loss_return
    if denominator <= 0:
        return 0.0
    return clamp(numerator / denominator, 0.0, 1.0)


def cvar_fraction(gamble: Gamble) -> float:
    if ev_fraction(gamble) <= 0:
        return 0.0
    if gamble.loss_return <= 0:
        return 1.0
    return clamp(gamble.max_drawdown / gamble.loss_return, 0.0, 1.0)


def drawdown_violation(gamble: Gamble, fraction: float) -> bool:
    return fraction * gamble.loss_return > gamble.max_drawdown + 1e-9


def crra_fraction(gamble: Gamble) -> float:
    gamma = max(0.01, gamble.gamma)

    def utility(wealth: float) -> float:
        if wealth <= 0:
            return -1e9
        if abs(gamma - 1.0) < 1e-9:
            return math.log(wealth)
        return (wealth ** (1.0 - gamma)) / (1.0 - gamma)

    def expected_utility(fraction: float) -> float:
        win_wealth = 1.0 + fraction * gamble.win_return
        loss_wealth = 1.0 - fraction * gamble.loss_return
        return gamble.p_win * utility(win_wealth) + (1.0 - gamble.p_win) * utility(loss_wealth)

    return _grid_argmax(expected_utility)


def log_growth(gamble: Gamble, fraction: float) -> float:
    win_wealth = 1.0 + fraction * gamble.win_return
    loss_wealth = 1.0 - fraction * gamble.loss_return
    if win_wealth <= 0 or loss_wealth <= 0:
        return -math.inf
    return gamble.p_win * math.log(win_wealth) + (1.0 - gamble.p_win) * math.log(loss_wealth)


def oracle_fraction(gamble: Gamble, regime: str) -> float:
    if regime == "ev":
        return ev_fraction(gamble)
    if regime == "kelly":
        return kelly_fraction(gamble)
    if regime == "cvar":
        return cvar_fraction(gamble)
    if regime == "crra":
        return crra_fraction(gamble)
    raise ValueError(f"Unknown regime: {regime}")


def run_regime_battery(
    agent: Agent,
    gambles: list[Gamble] | None = None,
    regimes: list[str] | None = None,
) -> dict:
    gambles = gambles or DEFAULT_GAMBLES
    regimes = regimes or list(REGIMES)
    trials: list[RegimeTrial] = []
    for gamble in gambles:
        ev_f = ev_fraction(gamble)
        kelly_f = kelly_fraction(gamble)
        cvar_f = cvar_fraction(gamble)
        for regime in regimes:
            oracle_f = oracle_fraction(gamble, regime)
            prompt = _prompt(gamble, regime)
            response = agent.complete(REGIME_SYSTEM, prompt)
            parsed = parse_float("FINAL_FRACTION", response)
            chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
            error = abs(chosen - oracle_f) if chosen is not None else None
            destruction = chosen is not None and regime == "kelly" and log_growth(gamble, chosen) < 0.0
            violation = chosen is not None and regime == "cvar" and drawdown_violation(gamble, chosen)
            trials.append(
                RegimeTrial(
                    gamble=gamble,
                    regime=regime,
                    oracle_fraction=oracle_f,
                    ev_fraction=ev_f,
                    kelly_fraction=kelly_f,
                    cvar_fraction=cvar_f,
                    chosen_fraction=chosen,
                    absolute_error=error,
                    wealth_destruction=destruction,
                    drawdown_violation=violation,
                    raw_response=response,
                )
            )
    return summarize_regime_trials(agent.name, trials)


def run_regime_relationship_verifier(
    agent: Agent,
    gambles: list[Gamble] | None = None,
) -> dict:
    gambles = gambles or DEFAULT_RELATIONSHIP_GAMBLES
    return _run_regime_group_verifier(
        agent=agent,
        gambles=gambles,
        task="regime_relationship",
        prompt_fn=_relationship_prompt,
    )


def run_regime_holdout_verifier(
    agent: Agent,
    gambles: list[Gamble] | None = None,
) -> dict:
    gambles = gambles or DEFAULT_HOLDOUT_GAMBLES
    return _run_regime_group_verifier(
        agent=agent,
        gambles=gambles,
        task="regime_holdout",
        prompt_fn=_holdout_prompt,
    )


def _run_regime_group_verifier(
    *,
    agent: Agent,
    gambles: list[Gamble],
    task: str,
    prompt_fn,
) -> dict:
    groups: list[RegimeRelationshipGroup] = []
    for gamble in gambles:
        trials: list[RegimeTrial] = []
        ev_f = ev_fraction(gamble)
        kelly_f = kelly_fraction(gamble)
        cvar_f = cvar_fraction(gamble)
        for regime in RELATIONSHIP_REGIMES:
            oracle_f = oracle_fraction(gamble, regime)
            prompt = prompt_fn(gamble, regime)
            response = agent.complete(REGIME_SYSTEM, prompt)
            parsed = parse_float("FINAL_FRACTION", response)
            chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
            error = abs(chosen - oracle_f) if chosen is not None else None
            destruction = chosen is not None and regime == "kelly" and log_growth(gamble, chosen) < 0.0
            violation = chosen is not None and regime == "cvar" and drawdown_violation(gamble, chosen)
            trials.append(
                RegimeTrial(
                    gamble=gamble,
                    regime=regime,
                    oracle_fraction=oracle_f,
                    ev_fraction=ev_f,
                    kelly_fraction=kelly_f,
                    cvar_fraction=cvar_f,
                    chosen_fraction=chosen,
                    absolute_error=error,
                    wealth_destruction=destruction,
                    drawdown_violation=violation,
                    raw_response=response,
                )
            )
        errors = [trial.absolute_error for trial in trials if trial.absolute_error is not None]
        group_error = mean(errors) if errors else None
        chosen = {trial.regime: trial.chosen_fraction for trial in trials}
        groups.append(
            RegimeRelationshipGroup(
                gamble=gamble,
                trials=trials,
                mean_absolute_error=group_error,
                relationship_violation=not relationship_laws_hold(chosen),
                fit_fail=len(errors) != len(trials)
                or group_error is None
                or group_error > RELATIONSHIP_FIT_TOLERANCE,
            )
        )
    return summarize_regime_relationship_groups(agent.name, groups, task=task)


def summarize_regime_trials(agent_name: str, trials: list[RegimeTrial]) -> dict:
    by_regime: dict[str, dict] = {}
    for regime in sorted({trial.regime for trial in trials}):
        subset = [trial for trial in trials if trial.regime == regime]
        errors = [trial.absolute_error for trial in subset if trial.absolute_error is not None]
        destroyed = sum(t.wealth_destruction for t in subset)
        violations = sum(t.drawdown_violation for t in subset)
        by_regime[regime] = {
            "mean_absolute_error": mean(errors),
            "mean_absolute_error_ci95": bootstrap_mean_ci(errors),
            "parse_rate": len(errors) / len(subset) if subset else 0.0,
            "wealth_destruction_rate": destroyed / len(subset),
            "wealth_destruction_ci95": wilson_ci(destroyed, len(subset)),
            "drawdown_violation_rate": violations / len(subset),
            "drawdown_violation_ci95": wilson_ci(violations, len(subset)),
            "real_case": REGIMES[regime].real_case,
        }
    by_family: dict[str, dict] = {}
    for family in sorted({trial.gamble.family for trial in trials}):
        subset = [trial for trial in trials if trial.gamble.family == family]
        errors = [trial.absolute_error for trial in subset if trial.absolute_error is not None]
        destroyed = sum(t.wealth_destruction for t in subset)
        violations = sum(t.drawdown_violation for t in subset)
        by_family[family] = {
            "n_trials": len(subset),
            "mean_absolute_error": mean(errors),
            "parse_rate": len(errors) / len(subset) if subset else 0.0,
            "wealth_destruction_rate": destroyed / len(subset) if subset else 0.0,
            "drawdown_violation_rate": violations / len(subset) if subset else 0.0,
        }
    all_errors = [trial.absolute_error for trial in trials if trial.absolute_error is not None]
    total_destroyed = sum(t.wealth_destruction for t in trials)
    cvar_trials = [trial for trial in trials if trial.regime == "cvar"]
    cvar_violations = sum(t.drawdown_violation for t in cvar_trials)
    return {
        "task": "regime",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_absolute_error": mean(all_errors),
        "mean_absolute_error_ci95": bootstrap_mean_ci(all_errors),
        "wealth_destruction_rate": total_destroyed / len(trials) if trials else 0.0,
        "wealth_destruction_ci95": wilson_ci(total_destroyed, len(trials)),
        "cvar_drawdown_violation_rate": cvar_violations / len(cvar_trials) if cvar_trials else 0.0,
        "cvar_drawdown_violation_ci95": wilson_ci(cvar_violations, len(cvar_trials)),
        "by_regime": by_regime,
        "by_family": by_family,
        "trials": [_trial_json(trial) for trial in trials],
    }


def summarize_regime_relationship_groups(
    agent_name: str,
    groups: list[RegimeRelationshipGroup],
    task: str = "regime_relationship",
) -> dict:
    trials = [trial for group in groups for trial in group.trials]
    all_errors = [trial.absolute_error for trial in trials if trial.absolute_error is not None]
    violations = sum(group.relationship_violation for group in groups)
    fit_fails = sum(group.fit_fail for group in groups)
    combined_fails = sum(group.relationship_violation or group.fit_fail for group in groups)
    return {
        "task": task,
        "agent": agent_name,
        "n_groups": len(groups),
        "n_trials": len(trials),
        "mean_absolute_error": mean(all_errors),
        "mean_absolute_error_ci95": bootstrap_mean_ci(all_errors),
        "parse_rate": len(all_errors) / len(trials) if trials else 0.0,
        "relationship_violation_rate": violations / len(groups) if groups else 0.0,
        "relationship_violation_ci95": wilson_ci(violations, len(groups)),
        "fit_fail_rate": fit_fails / len(groups) if groups else 0.0,
        "fit_fail_ci95": wilson_ci(fit_fails, len(groups)),
        "relationship_or_fit_fail_rate": combined_fails / len(groups) if groups else 0.0,
        "relationship_or_fit_fail_ci95": wilson_ci(combined_fails, len(groups)),
        "fit_tolerance": RELATIONSHIP_FIT_TOLERANCE,
        "by_group": {group.gamble.key: _relationship_group_json(group) for group in groups},
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(gamble: Gamble, regime: str) -> str:
    spec = REGIMES[regime]
    return (
        f"regime={regime}\n"
        f"case={spec.real_case}\n"
        f"objective={spec.objective}\n"
        f"gamble_family={gamble.family}\n"
        f"p_win={gamble.p_win:.4f}\n"
        f"win_return={gamble.win_return:.4f}\n"
        f"loss_return={gamble.loss_return:.4f}\n"
        f"horizon={gamble.horizon}\n"
        f"gamma={gamble.gamma:.4f}\n"
        f"max_drawdown={gamble.max_drawdown:.4f}\n"
        "Choose the fraction f in [0,1] for this deployment regime."
    )


def _relationship_prompt(gamble: Gamble, regime: str) -> str:
    return (
        _prompt(gamble, regime)
        + "\nThis case is part of a generated relationship-law verifier. "
        "Return the deployment fraction for this regime only."
    )


def _holdout_prompt(gamble: Gamble, regime: str) -> str:
    return (
        _prompt(gamble, regime)
        + "\nThis is a held-out generated case from a broader regime-law family. "
        "Use the deployment objective and gamble parameters; do not reuse a memorized case pattern."
    )


def relationship_laws_hold(fractions: dict[str, float | None], eps: float = 1e-9) -> bool:
    required = RELATIONSHIP_REGIMES
    if any(fractions.get(regime) is None for regime in required):
        return False
    return (
        fractions["ev"] + eps >= fractions["kelly"]
        and fractions["kelly"] + eps >= fractions["cvar"]
        and fractions["kelly"] + eps >= fractions["crra"]
    )


def relationship_oracle_fractions(gamble: Gamble) -> dict[str, float]:
    return {regime: oracle_fraction(gamble, regime) for regime in RELATIONSHIP_REGIMES}


def _relationship_group_json(group: RegimeRelationshipGroup) -> dict:
    chosen = {trial.regime: trial.chosen_fraction for trial in group.trials}
    oracle = {trial.regime: trial.oracle_fraction for trial in group.trials}
    errors = [trial.absolute_error for trial in group.trials if trial.absolute_error is not None]
    return {
        "gamble": asdict(group.gamble),
        "mean_absolute_error": group.mean_absolute_error,
        "parse_rate": len(errors) / len(group.trials) if group.trials else 0.0,
        "relationship_violation": group.relationship_violation,
        "fit_fail": group.fit_fail,
        "oracle_fractions": oracle,
        "chosen_fractions": chosen,
        "laws": _relationship_law_report(chosen),
    }


def _relationship_law_report(fractions: dict[str, float | None]) -> dict[str, bool]:
    if any(fractions.get(regime) is None for regime in RELATIONSHIP_REGIMES):
        return {
            "ev_ge_kelly": False,
            "kelly_ge_cvar": False,
            "kelly_ge_crra": False,
        }
    return {
        "ev_ge_kelly": fractions["ev"] >= fractions["kelly"],
        "kelly_ge_cvar": fractions["kelly"] >= fractions["cvar"],
        "kelly_ge_crra": fractions["kelly"] >= fractions["crra"],
    }


def _trial_json(trial: RegimeTrial) -> dict:
    data = asdict(trial)
    data["gamble"] = asdict(trial.gamble)
    return data


def _grid_argmax(fn) -> float:
    best_x = 0.0
    best_y = -math.inf
    for i in range(1001):
        x = i / 1000.0
        y = fn(x)
        if y > best_y:
            best_x = x
            best_y = y
    return best_x


DEFAULT_HOLDOUT_GAMBLES = generate_regime_holdout_gambles()


def dumps_summary(summary: dict) -> str:
    return json.dumps(summary, indent=2, sort_keys=True)
