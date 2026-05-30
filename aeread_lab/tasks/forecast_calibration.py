from __future__ import annotations

import math
from collections.abc import Callable
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
    reliability_weight: float = 1.0


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
    raw_signal_probability: float
    base_rate_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    realized_brier_score: float | None
    posterior_realized_brier_score: float
    realized_log_loss: float | None
    posterior_l1_error: float | None
    raw_response: str


@dataclass(frozen=True)
class AggregateForecastCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    global_base_rate: float
    prior_strength: float
    observed_event_count: int
    observed_total: int
    bin_label: str


@dataclass
class AggregateForecastTrial:
    case: AggregateForecastCase
    calibrated_probability: float
    raw_model_probability: float
    empirical_bin_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    realized_brier_score: float | None
    calibrated_realized_brier_score: float
    probability_error: float | None
    raw_score_miss: bool
    shrinkage_miss: bool
    raw_response: str


@dataclass(frozen=True)
class CalibrationBin:
    bin_id: str
    raw_mean_probability: float
    observed_event_count: int
    observed_total: int


@dataclass(frozen=True)
class ForecastCurveCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    global_base_rate: float
    prior_strength: float
    bins: tuple[CalibrationBin, ...]


@dataclass
class ForecastCurveTrial:
    case: ForecastCurveCase
    calibrated_probability: float
    raw_model_probability: float
    nearest_bin_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    probability_error: float | None
    raw_score_miss: bool
    nearest_bin_miss: bool
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
    ForecastCase(
        key="thin_slice_fraud_spike",
        real_case="fraud alert from a small shifted merchant slice with noisy warning signals",
        target_event="merchant account has a confirmed fraud escalation",
        base_rate=0.06,
        signals=(
            Signal(
                "tiny_sample_velocity",
                likelihood_if_event=0.80,
                likelihood_if_not_event=0.05,
                reliability_weight=0.25,
            ),
            Signal(
                "unverified_device_cluster",
                likelihood_if_event=0.65,
                likelihood_if_not_event=0.12,
                reliability_weight=0.35,
            ),
        ),
        realized_event_count=11,
        total_count=60,
    ),
    ForecastCase(
        key="regional_renewal_shift",
        real_case="renewal forecast from a new region where historical signals transfer weakly",
        target_event="account churns before renewal",
        base_rate=0.30,
        signals=(
            Signal(
                "legacy_success_signal",
                likelihood_if_event=0.10,
                likelihood_if_not_event=0.70,
                reliability_weight=0.30,
            ),
            Signal(
                "old_segment_usage_pattern",
                likelihood_if_event=0.18,
                likelihood_if_not_event=0.55,
                reliability_weight=0.40,
            ),
        ),
        realized_event_count=8,
        total_count=60,
    ),
    ForecastCase(
        key="thin_qa_cluster",
        real_case="launch defect forecast from a small beta sample with high-variance QA warnings",
        target_event="batch exceeds the defect escalation threshold",
        base_rate=0.12,
        signals=(
            Signal(
                "beta_failure_cluster",
                likelihood_if_event=0.70,
                likelihood_if_not_event=0.08,
                reliability_weight=0.20,
            ),
            Signal(
                "support_spike",
                likelihood_if_event=0.50,
                likelihood_if_not_event=0.10,
                reliability_weight=0.25,
            ),
        ),
        realized_event_count=14,
        total_count=60,
    ),
]

AGGREGATE_CASES = [
    AggregateForecastCase(
        key="checkout_low_score_hidden_risk",
        real_case="payment fraud calibration bin after a new merchant cohort shift",
        target_event="transaction later becomes a chargeback",
        raw_model_probability=0.18,
        global_base_rate=0.22,
        prior_strength=40.0,
        observed_event_count=26,
        observed_total=50,
        bin_label="raw_score_0.15_to_0.25",
    ),
    AggregateForecastCase(
        key="renewal_high_score_regression",
        real_case="enterprise churn model high-risk bin after sales-led retention changes",
        target_event="account churns before renewal",
        raw_model_probability=0.78,
        global_base_rate=0.22,
        prior_strength=40.0,
        observed_event_count=7,
        observed_total=20,
        bin_label="raw_score_0.70_to_0.85",
    ),
    AggregateForecastCase(
        key="support_defect_stable_mid",
        real_case="support-defect forecast bin with enough history to trust the calibration table",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.42,
        global_base_rate=0.40,
        prior_strength=30.0,
        observed_event_count=35,
        observed_total=80,
        bin_label="raw_score_0.35_to_0.50",
    ),
    AggregateForecastCase(
        key="small_sample_spike",
        real_case="small regional default bin with a high but very noisy observed spike",
        target_event="supplier misses the delivery window",
        raw_model_probability=0.62,
        global_base_rate=0.25,
        prior_strength=60.0,
        observed_event_count=8,
        observed_total=9,
        bin_label="raw_score_0.55_to_0.70",
    ),
    AggregateForecastCase(
        key="large_bin_persistent_low",
        real_case="large mature credit bin where realized risk is persistently below the model score",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.52,
        global_base_rate=0.35,
        prior_strength=30.0,
        observed_event_count=70,
        observed_total=240,
        bin_label="raw_score_0.45_to_0.60",
    ),
]

CURVE_CASES = [
    ForecastCurveCase(
        key="churn_curve_mid_high",
        real_case="held-out enterprise churn forecast from a shifted renewal segment",
        target_event="account churns before renewal",
        raw_model_probability=0.68,
        global_base_rate=0.22,
        prior_strength=30.0,
        bins=(
            CalibrationBin("b10", 0.10, 9, 60),
            CalibrationBin("b30", 0.30, 31, 80),
            CalibrationBin("b55", 0.55, 49, 110),
            CalibrationBin("b80", 0.80, 46, 90),
        ),
    ),
    ForecastCurveCase(
        key="fraud_curve_underconfident",
        real_case="held-out fraud score from a new merchant cohort",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.46,
        global_base_rate=0.18,
        prior_strength=25.0,
        bins=(
            CalibrationBin("b12", 0.12, 5, 90),
            CalibrationBin("b28", 0.28, 18, 75),
            CalibrationBin("b52", 0.52, 59, 95),
            CalibrationBin("b78", 0.78, 76, 95),
        ),
    ),
    ForecastCurveCase(
        key="defect_curve_small_high_bin",
        real_case="held-out launch defect forecast with sparse high-risk calibration bins",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.74,
        global_base_rate=0.16,
        prior_strength=50.0,
        bins=(
            CalibrationBin("b20", 0.20, 12, 80),
            CalibrationBin("b45", 0.45, 29, 70),
            CalibrationBin("b70", 0.70, 11, 14),
            CalibrationBin("b90", 0.90, 8, 9),
        ),
    ),
]


def posterior_probability(case: ForecastCase) -> float:
    odds = case.base_rate / max(1e-12, 1.0 - case.base_rate)
    for signal in case.signals:
        likelihood_ratio = signal.likelihood_if_event / max(1e-12, signal.likelihood_if_not_event)
        odds *= likelihood_ratio ** signal.reliability_weight
    return odds / (1.0 + odds)


def raw_signal_probability(case: ForecastCase) -> float:
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


def aggregate_calibrated_probability(case: AggregateForecastCase) -> float:
    prior_events = case.prior_strength * case.global_base_rate
    return (case.observed_event_count + prior_events) / (case.observed_total + case.prior_strength)


def curve_bin_probability(case: ForecastCurveCase, bin_: CalibrationBin) -> float:
    prior_events = case.prior_strength * case.global_base_rate
    return (bin_.observed_event_count + prior_events) / (bin_.observed_total + case.prior_strength)


def curve_calibrated_probability(case: ForecastCurveCase) -> float:
    points = sorted(
        (bin_.raw_mean_probability, curve_bin_probability(case, bin_))
        for bin_ in case.bins
    )
    raw = case.raw_model_probability
    if raw <= points[0][0]:
        return points[0][1]
    if raw >= points[-1][0]:
        return points[-1][1]
    for (left_raw, left_prob), (right_raw, right_prob) in zip(points, points[1:]):
        if left_raw <= raw <= right_raw:
            weight = (raw - left_raw) / max(right_raw - left_raw, 1e-12)
            return left_prob + weight * (right_prob - left_prob)
    return points[-1][1]


def nearest_curve_bin_probability(case: ForecastCurveCase) -> float:
    nearest = min(case.bins, key=lambda bin_: abs(bin_.raw_mean_probability - case.raw_model_probability))
    return curve_bin_probability(case, nearest)


def run_forecast_calibration_game(agent: Agent, cases: list[ForecastCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[ForecastTrial] = []
    for case in cases:
        posterior = posterior_probability(case)
        raw_signal = raw_signal_probability(case)
        realized_rate = case.realized_event_count / case.total_count
        posterior_brier = realized_brier_score(realized_rate, posterior)
        response = agent.complete(FORECAST_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        trials.append(
            ForecastTrial(
                case=case,
                posterior_probability=posterior,
                raw_signal_probability=raw_signal,
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


def run_forecast_aggregate_game(
    agent: Agent,
    cases: list[AggregateForecastCase] | None = None,
) -> dict:
    cases = cases or AGGREGATE_CASES
    trials: list[AggregateForecastTrial] = []
    for case in cases:
        calibrated = aggregate_calibrated_probability(case)
        empirical = case.observed_event_count / case.observed_total
        response = agent.complete(FORECAST_SYSTEM, _aggregate_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        realized_brier = realized_brier_score(empirical, chosen) if chosen is not None else None
        calibrated_brier = realized_brier_score(empirical, calibrated)
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.10
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        shrinkage_miss = (
            chosen is not None
            and case.observed_total < case.prior_strength
            and abs(empirical - calibrated) >= 0.10
            and abs(chosen - empirical) < abs(chosen - calibrated)
        )
        trials.append(
            AggregateForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                empirical_bin_probability=empirical,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                realized_brier_score=realized_brier,
                calibrated_realized_brier_score=calibrated_brier,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                shrinkage_miss=shrinkage_miss,
                raw_response=response,
            )
        )
    return summarize_aggregate_forecast_trials(agent.name, trials)


def run_forecast_curve_game(
    agent: Agent,
    cases: list[ForecastCurveCase] | None = None,
) -> dict:
    return _run_forecast_curve_game(
        agent,
        cases,
        prompt_fn=_curve_prompt,
        task_name="forecast_curve",
    )


def run_forecast_curve_implicit_game(
    agent: Agent,
    cases: list[ForecastCurveCase] | None = None,
) -> dict:
    return _run_forecast_curve_game(
        agent,
        cases,
        prompt_fn=_curve_implicit_prompt,
        task_name="forecast_curve_implicit",
    )


def _run_forecast_curve_game(
    agent: Agent,
    cases: list[ForecastCurveCase] | None,
    *,
    prompt_fn: Callable[[ForecastCurveCase], str],
    task_name: str,
) -> dict:
    cases = cases or CURVE_CASES
    trials: list[ForecastCurveTrial] = []
    for case in cases:
        calibrated = curve_calibrated_probability(case)
        nearest = nearest_curve_bin_probability(case)
        response = agent.complete(FORECAST_SYSTEM, prompt_fn(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.10
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        nearest_bin_miss = (
            chosen is not None
            and abs(nearest - calibrated) >= 0.03
            and abs(chosen - nearest) < abs(chosen - calibrated)
        )
        trials.append(
            ForecastCurveTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                nearest_bin_probability=nearest,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                nearest_bin_miss=nearest_bin_miss,
                raw_response=response,
            )
        )
    return summarize_curve_forecast_trials(agent.name, trials, task_name=task_name)


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
    reliability_adjusted = [
        trial
        for trial in trials
        if trial.chosen_probability is not None
        and any(signal.reliability_weight < 0.75 for signal in trial.case.signals)
    ]
    reliability_blind = [
        trial
        for trial in reliability_adjusted
        if abs(trial.chosen_probability - trial.raw_signal_probability)
        < abs(trial.chosen_probability - trial.posterior_probability)
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
        "reliability_miss_rate": len(reliability_blind) / len(reliability_adjusted)
        if reliability_adjusted
        else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def summarize_curve_forecast_trials(
    agent_name: str,
    trials: list[ForecastCurveTrial],
    *,
    task_name: str = "forecast_curve",
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.10
    ]
    nearest_shifted = [
        trial
        for trial in trials
        if abs(trial.nearest_bin_probability - trial.calibrated_probability) >= 0.03
    ]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in shifted) / len(shifted) if shifted else 0.0
        ),
        "nearest_bin_miss_rate": (
            sum(trial.nearest_bin_miss for trial in nearest_shifted) / len(nearest_shifted)
            if nearest_shifted
            else 0.0
        ),
        "trials": [_curve_trial_json(trial) for trial in trials],
    }


def summarize_aggregate_forecast_trials(
    agent_name: str,
    trials: list[AggregateForecastTrial],
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    realized_scores = [
        trial.realized_brier_score for trial in trials if trial.realized_brier_score is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.10
    ]
    shrinkage_cases = [
        trial
        for trial in trials
        if trial.case.observed_total < trial.case.prior_strength
        and abs(trial.empirical_bin_probability - trial.calibrated_probability) >= 0.10
    ]
    return {
        "task": "forecast_aggregate",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_realized_brier_score": mean(realized_scores),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in shifted) / len(shifted) if shifted else 0.0
        ),
        "shrinkage_miss_rate": (
            sum(trial.shrinkage_miss for trial in shrinkage_cases) / len(shrinkage_cases)
            if shrinkage_cases
            else 0.0
        ),
        "trials": [_aggregate_trial_json(trial) for trial in trials],
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
            f"likelihood_if_not_event={signal.likelihood_if_not_event:.4f} "
            f"reliability_weight={signal.reliability_weight:.4f}"
        )
    lines.append(
        "Use reliability_weight as the fraction of each signal's log likelihood ratio "
        "that should count for this setting."
    )
    lines.append("Estimate the calibrated probability of the target event before outcomes are known.")
    return "\n".join(lines)


def _aggregate_prompt(case: AggregateForecastCase) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            f"target_event={case.target_event}",
            f"bin_label={case.bin_label}",
            f"raw_model_probability={case.raw_model_probability:.4f}",
            f"base_rate={case.global_base_rate:.4f}",
            f"global_base_rate={case.global_base_rate:.4f}",
            f"prior_strength={case.prior_strength:.1f}",
            f"observed_event_count={case.observed_event_count}",
            f"observed_total={case.observed_total}",
            "Use aggregate calibration for this raw-score bin. Treat prior_strength as "
            "the equivalent sample size at the global base rate, then combine it with "
            "the observed calibration-bin event count before forecasting.",
            "Estimate the calibrated probability of the target event for the next item in this bin.",
        ]
    )


def _curve_prompt(case: ForecastCurveCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"base_rate={case.global_base_rate:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        "Historical calibration bins for this shifted segment:",
    ]
    for bin_ in case.bins:
        lines.append(
            f"  bin_id={bin_.bin_id} "
            f"raw_mean_probability={bin_.raw_mean_probability:.4f} "
            f"observed_event_count={bin_.observed_event_count} "
            f"observed_total={bin_.observed_total}"
        )
    lines.append(
        "Use the calibration curve, shrinking each bin toward the global base rate "
        "according to prior_strength, then interpolate between nearby raw-score bins."
    )
    lines.append("Estimate the calibrated probability for the next held-out item.")
    return "\n".join(lines)


def _curve_implicit_prompt(case: ForecastCurveCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"base_rate={case.global_base_rate:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        "Historical holdout table for the same shifted segment:",
    ]
    for bin_ in case.bins:
        lines.append(
            f"  bin_id={bin_.bin_id} "
            f"raw_mean_probability={bin_.raw_mean_probability:.4f} "
            f"observed_event_count={bin_.observed_event_count} "
            f"observed_total={bin_.observed_total}"
        )
    lines.extend(
        [
            "The global baseline contributes roughly the listed prior-equivalent "
            "observations for this sparse slice.",
            "Use the historical table to adjust the raw probability for the next "
            "held-out item. Small bins are noisy, larger bins carry more evidence, "
            "and a raw score between table rows should follow the local calibration "
            "trend rather than snapping blindly to one row.",
            "Do not assume the raw score is already calibrated.",
            "Estimate the event probability for the next held-out item.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: ForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _aggregate_trial_json(trial: AggregateForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _curve_trial_json(trial: ForecastCurveTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
