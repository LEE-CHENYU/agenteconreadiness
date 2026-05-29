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
    raw_response: str


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
    Gamble("g01", p_win=0.58, win_return=1.0, loss_return=1.0, horizon=1, gamma=2.0),
    Gamble("g02", p_win=0.60, win_return=1.0, loss_return=1.0, horizon=2, gamma=3.0),
    Gamble("g03", p_win=0.64, win_return=0.8, loss_return=1.0, horizon=5, gamma=1.7),
    Gamble("g04", p_win=0.70, win_return=0.5, loss_return=1.0, horizon=20, gamma=4.0),
]


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
            destruction = chosen is not None and regime == "kelly" and log_growth(gamble, chosen) <= 0.0
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
                    raw_response=response,
                )
            )
    return summarize_regime_trials(agent.name, trials)


def summarize_regime_trials(agent_name: str, trials: list[RegimeTrial]) -> dict:
    by_regime: dict[str, dict] = {}
    for regime in sorted({trial.regime for trial in trials}):
        subset = [trial for trial in trials if trial.regime == regime]
        errors = [trial.absolute_error for trial in subset if trial.absolute_error is not None]
        destroyed = sum(t.wealth_destruction for t in subset)
        by_regime[regime] = {
            "mean_absolute_error": mean(errors),
            "mean_absolute_error_ci95": bootstrap_mean_ci(errors),
            "parse_rate": len(errors) / len(subset) if subset else 0.0,
            "wealth_destruction_rate": destroyed / len(subset),
            "wealth_destruction_ci95": wilson_ci(destroyed, len(subset)),
            "real_case": REGIMES[regime].real_case,
        }
    all_errors = [trial.absolute_error for trial in trials if trial.absolute_error is not None]
    total_destroyed = sum(t.wealth_destruction for t in trials)
    return {
        "task": "regime",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_absolute_error": mean(all_errors),
        "mean_absolute_error_ci95": bootstrap_mean_ci(all_errors),
        "wealth_destruction_rate": total_destroyed / len(trials) if trials else 0.0,
        "wealth_destruction_ci95": wilson_ci(total_destroyed, len(trials)),
        "by_regime": by_regime,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(gamble: Gamble, regime: str) -> str:
    spec = REGIMES[regime]
    return (
        f"regime={regime}\n"
        f"case={spec.real_case}\n"
        f"objective={spec.objective}\n"
        f"p_win={gamble.p_win:.4f}\n"
        f"win_return={gamble.win_return:.4f}\n"
        f"loss_return={gamble.loss_return:.4f}\n"
        f"horizon={gamble.horizon}\n"
        f"gamma={gamble.gamma:.4f}\n"
        f"max_drawdown={gamble.max_drawdown:.4f}\n"
        "Choose the fraction f in [0,1] for this deployment regime."
    )


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


def dumps_summary(summary: dict) -> str:
    return json.dumps(summary, indent=2, sort_keys=True)
