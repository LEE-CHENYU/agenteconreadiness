from __future__ import annotations

import math
from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


FORECAST_SYSTEM = (
    "TASK: forecast_probability\n"
    "Estimate the probability of the target event from the available base rate "
    "and signal likelihoods. Return one final line only: FINAL_PROBABILITY: <0 to 1>."
)


@dataclass(frozen=True)
class Signal:
    signal_id: str
    likelihood_if_event: float
    likelihood_if_not_event: float


@dataclass(frozen=True)
class ForecastCase:
    key: str
    real_case: str
    target_event: str
    base_rate: float
    signals: tuple[Signal, ...]
    realized_event_count: int
    total_count: int


@dataclass
class ForecastTrial:
    case: ForecastCase
    posterior_probability: float
    base_rate_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    realized_brier_score: float | None
    posterior_realized_brier_score: float
    realized_log_loss: float | None
    posterior_l1_error: float | None
    raw_response: str


DEFAULT_CASES = [
    ForecastCase(
        key="enterprise_churn_warning",
        real_case="renewal risk forecast after usage and invoice warning signals",
        target_event="account churns before renewal",
        base_rate=0.18,
        signals=(
            Signal("usage_drop", likelihood_if_event=0.62, likelihood_if_not_event=0.18),
            Signal("invoice_delay", likelihood_if_event=0.48, likelihood_if_not_event=0.16),
        ),
        realized_event_count=42,
        total_count=60,
    ),
    ForecastCase(
        key="supplier_default_watch",
        real_case="supplier default probability after diligence warning signals",
        target_event="supplier misses the delivery window",
        base_rate=0.12,
        signals=(
            Signal("paperwork_delay", likelihood_if_event=0.55, likelihood_if_not_event=0.20),
            Signal("weak_bank_reference", likelihood_if_event=0.38, likelihood_if_not_event=0.08),
        ),
        realized_event_count=38,
        total_count=60,
    ),
    ForecastCase(
        key="chargeback_velocity_shift",
        real_case="payment-risk forecast after device and velocity signals",
        target_event="transaction later becomes a chargeback",
        base_rate=0.08,
        signals=(
            Signal("new_device", likelihood_if_event=0.35, likelihood_if_not_event=0.10),
            Signal("velocity_spike", likelihood_if_event=0.45, likelihood_if_not_event=0.05),
        ),
        realized_event_count=44,
        total_count=60,
    ),
    ForecastCase(
        key="renewal_health_green",
        real_case="healthy enterprise renewal with signals that lower churn risk",
        target_event="account churns before renewal",
        base_rate=0.35,
        signals=(
            Signal("executive_reply", likelihood_if_event=0.16, likelihood_if_not_event=0.58),
            Signal("stable_usage", likelihood_if_event=0.22, likelihood_if_not_event=0.62),
        ),
        realized_event_count=3,
        total_count=60,
    ),
    ForecastCase(
        key="mixed_credit_recovery",
        real_case="credit-risk forecast with one adverse and one reassuring signal",
        target_event="borrower becomes 60 days delinquent",
        base_rate=0.28,
        signals=(
            Signal("cash_balance_drop", likelihood_if_event=0.52, likelihood_if_not_event=0.24),
            Signal("payroll_recovered", likelihood_if_event=0.30, likelihood_if_not_event=0.55),
        ),
        realized_event_count=19,
        total_count=60,
    ),
    ForecastCase(
        key="launch_defect_signal",
        real_case="product launch defect forecast after QA and support signals",
        target_event="batch exceeds the defect escalation threshold",
        base_rate=0.15,
        signals=(
            Signal("qa_failure_cluster", likelihood_if_event=0.70, likelihood_if_not_event=0.22),
            Signal("early_ticket_spike", likelihood_if_event=0.40, likelihood_if_not_event=0.12),
        ),
        realized_event_count=39,
        total_count=60,
    ),
]


def posterior_probability(case: ForecastCase) -> float:
    odds = case.base_rate / max(1e-12, 1.0 - case.base_rate)
    for signal in case.signals:
        odds *= signal.likelihood_if_event / max(1e-12, signal.likelihood_if_not_event)
    return odds / (1.0 + odds)


def expected_brier_regret(posterior: float, forecast: float) -> float:
    return (forecast - posterior) ** 2


def realized_brier_score(realized_rate: float, forecast: float) -> float:
    return realized_rate * ((1.0 - forecast) ** 2) + (1.0 - realized_rate) * (forecast**2)


def realized_log_loss(realized_rate: float, forecast: float) -> float:
    clipped = clamp(forecast, 1e-6, 1.0 - 1e-6)
    return -(realized_rate * math.log(clipped) + (1.0 - realized_rate) * math.log(1.0 - clipped))


def run_forecast_calibration_game(agent: Agent, cases: list[ForecastCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[ForecastTrial] = []
    for case in cases:
        posterior = posterior_probability(case)
        realized_rate = case.realized_event_count / case.total_count
        posterior_brier = realized_brier_score(realized_rate, posterior)
        response = agent.complete(FORECAST_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        trials.append(
            ForecastTrial(
                case=case,
                posterior_probability=posterior,
                base_rate_probability=case.base_rate,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(posterior, chosen)
                if chosen is not None
                else None,
                realized_brier_score=realized_brier_score(realized_rate, chosen)
                if chosen is not None
                else None,
                posterior_realized_brier_score=posterior_brier,
                realized_log_loss=realized_log_loss(realized_rate, chosen)
                if chosen is not None
                else None,
                posterior_l1_error=abs(chosen - posterior) if chosen is not None else None,
                raw_response=response,
            )
        )
    return summarize_forecast_trials(agent.name, trials)


def summarize_forecast_trials(agent_name: str, trials: list[ForecastTrial]) -> dict:
    expected_regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    realized_scores = [
        trial.realized_brier_score for trial in trials if trial.realized_brier_score is not None
    ]
    log_losses = [trial.realized_log_loss for trial in trials if trial.realized_log_loss is not None]
    posterior_l1 = [trial.posterior_l1_error for trial in trials if trial.posterior_l1_error is not None]
    shifted = [
        trial
        for trial in trials
        if abs(trial.posterior_probability - trial.base_rate_probability) >= 0.15
    ]
    base_rate_misses = [
        trial
        for trial in shifted
        if trial.chosen_probability is not None
        and abs(trial.chosen_probability - trial.base_rate_probability)
        < abs(trial.chosen_probability - trial.posterior_probability)
    ]
    confidence_eligible = [
        trial
        for trial in trials
        if trial.chosen_probability is not None
        and 0.10 <= trial.posterior_probability <= 0.90
    ]
    overconfident = [
        trial
        for trial in confidence_eligible
        if trial.chosen_probability <= 0.05 or trial.chosen_probability >= 0.95
    ]
    return {
        "task": "forecast_calibration",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(expected_regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(expected_regrets),
        "mean_realized_brier_score": mean(realized_scores),
        "mean_realized_log_loss": mean(log_losses),
        "mean_posterior_l1_error": mean(posterior_l1),
        "base_rate_miss_rate": len(base_rate_misses) / len(shifted) if shifted else 0.0,
        "overconfidence_rate": len(overconfident) / len(confidence_eligible)
        if confidence_eligible
        else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: ForecastCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"base_rate={case.base_rate:.4f}",
        f"calibration_sample_size={case.total_count}",
        "Signal likelihoods are estimated from historical calibration data:",
    ]
    for signal in case.signals:
        lines.append(
            f"  signal_id={signal.signal_id} "
            f"likelihood_if_event={signal.likelihood_if_event:.4f} "
            f"likelihood_if_not_event={signal.likelihood_if_not_event:.4f}"
        )
    lines.append("Estimate the calibrated probability of the target event before outcomes are known.")
    return "\n".join(lines)


def _trial_json(trial: ForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
