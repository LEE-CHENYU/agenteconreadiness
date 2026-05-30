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


@dataclass(frozen=True)
class ShiftCalibrationCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    source_base_rate: float
    source_prior_strength: float
    bridge_prior_strength: float
    source_bins: tuple[CalibrationBin, ...]
    bridge_bins: tuple[CalibrationBin, ...]


@dataclass
class ShiftForecastTrial:
    case: ShiftCalibrationCase
    calibrated_probability: float
    raw_model_probability: float
    source_curve_probability: float
    nearest_bridge_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    probability_error: float | None
    raw_score_miss: bool
    source_curve_miss: bool
    nearest_bridge_miss: bool
    raw_response: str


@dataclass(frozen=True)
class RollingCalibrationPeriod:
    period_id: str
    recency_weight: float
    bins: tuple[CalibrationBin, ...]


@dataclass(frozen=True)
class RollingCalibrationCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    global_base_rate: float
    prior_strength: float
    periods: tuple[RollingCalibrationPeriod, ...]


@dataclass
class RollingForecastTrial:
    case: RollingCalibrationCase
    calibrated_probability: float
    raw_model_probability: float
    stale_window_probability: float
    pooled_history_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    probability_error: float | None
    raw_score_miss: bool
    stale_window_miss: bool
    pooled_history_miss: bool
    raw_response: str


@dataclass(frozen=True)
class RollingLogCalibrationPeriod:
    period_id: str
    days_before_target_midpoint: float
    bins: tuple[CalibrationBin, ...]


@dataclass(frozen=True)
class RollingLogCalibrationCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    global_base_rate: float
    prior_strength: float
    recency_half_life_days: float
    periods: tuple[RollingLogCalibrationPeriod, ...]


@dataclass
class RollingLogForecastTrial:
    case: RollingLogCalibrationCase
    calibrated_probability: float
    raw_model_probability: float
    stale_window_probability: float
    pooled_history_probability: float
    latest_window_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    probability_error: float | None
    raw_score_miss: bool
    stale_window_miss: bool
    pooled_history_miss: bool
    latest_window_miss: bool
    raw_response: str


@dataclass(frozen=True)
class EventLogCalibrationEntry:
    entry_id: str
    raw_model_probability: float
    days_before_target: float
    event_observed: bool


@dataclass(frozen=True)
class EventLogCalibrationCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    global_base_rate: float
    prior_strength: float
    recency_half_life_days: float
    score_kernel_width: float
    entries: tuple[EventLogCalibrationEntry, ...]


@dataclass
class EventLogForecastTrial:
    case: EventLogCalibrationCase
    calibrated_probability: float
    raw_model_probability: float
    stale_window_probability: float
    pooled_history_probability: float
    latest_window_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    probability_error: float | None
    raw_score_miss: bool
    stale_window_miss: bool
    pooled_history_miss: bool
    latest_window_miss: bool
    raw_response: str


@dataclass(frozen=True)
class OperationalLogCalibrationEntry:
    entry_id: str
    raw_model_probability: float
    days_before_target: float
    policy: str
    route: str
    event_observed: bool


@dataclass(frozen=True)
class OperationalLogCalibrationCase:
    key: str
    real_case: str
    target_event: str
    raw_model_probability: float
    global_base_rate: float
    prior_strength: float
    recency_half_life_days: float
    score_kernel_width: float
    current_policy: str
    current_route: str
    entries: tuple[OperationalLogCalibrationEntry, ...]


@dataclass
class OperationalLogForecastTrial:
    case: OperationalLogCalibrationCase
    calibrated_probability: float
    raw_model_probability: float
    stale_window_probability: float
    pooled_history_probability: float
    latest_window_probability: float
    policy_blind_probability: float
    route_blind_probability: float
    chosen_probability: float | None
    expected_brier_regret: float | None
    probability_error: float | None
    raw_score_miss: bool
    stale_window_miss: bool
    pooled_history_miss: bool
    latest_window_miss: bool
    policy_blind_miss: bool
    route_blind_miss: bool
    raw_response: str


def _event_log_entries(
    prefix: str,
    rows: tuple[tuple[str, float, float, int, int], ...],
) -> tuple[EventLogCalibrationEntry, ...]:
    entries: list[EventLogCalibrationEntry] = []
    for row_id, score, days, events, total in rows:
        for index in range(total):
            score_jitter = ((index % 5) - 2) * 0.008
            day_jitter = (index % 3) - 1
            entries.append(
                EventLogCalibrationEntry(
                    entry_id=f"{prefix}_{row_id}_{index + 1:02d}",
                    raw_model_probability=clamp(score + score_jitter, 0.01, 0.99),
                    days_before_target=max(0.0, days + day_jitter),
                    event_observed=index < events,
                )
            )
    return tuple(entries)


def _operational_log_entries(
    prefix: str,
    rows: tuple[tuple[str, float, float, str, str, int, int], ...],
) -> tuple[OperationalLogCalibrationEntry, ...]:
    entries: list[OperationalLogCalibrationEntry] = []
    for row_id, score, days, policy, route, events, total in rows:
        for index in range(total):
            score_jitter = ((index % 5) - 2) * 0.007
            day_jitter = (index % 3) - 1
            entries.append(
                OperationalLogCalibrationEntry(
                    entry_id=f"{prefix}_{row_id}_{index + 1:02d}",
                    raw_model_probability=clamp(score + score_jitter, 0.01, 0.99),
                    days_before_target=max(0.0, days + day_jitter),
                    policy=policy,
                    route=route,
                    event_observed=index < events,
                )
            )
    return tuple(entries)


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


NOISY_CURVE_CASES = [
    ForecastCurveCase(
        key="churn_noisy_slope_reversal",
        real_case="held-out renewal score from a segment with non-monotone historical calibration bins",
        target_event="account churns before renewal",
        raw_model_probability=0.64,
        global_base_rate=0.20,
        prior_strength=35.0,
        bins=(
            CalibrationBin("b08_large", 0.08, 26, 200),
            CalibrationBin("b18_sparse", 0.18, 4, 44),
            CalibrationBin("b31_large", 0.31, 55, 150),
            CalibrationBin("b44_sparse_high", 0.44, 22, 38),
            CalibrationBin("b59_large", 0.59, 44, 120),
            CalibrationBin("b72_sparse_low", 0.72, 8, 28),
            CalibrationBin("b87_large", 0.87, 52, 90),
        ),
    ),
    ForecastCurveCase(
        key="fraud_noisy_underconfident",
        real_case="held-out fraud score from a merchant cohort with noisy middle bins",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.49,
        global_base_rate=0.16,
        prior_strength=45.0,
        bins=(
            CalibrationBin("b06_large", 0.06, 4, 180),
            CalibrationBin("b16_mid", 0.16, 12, 65),
            CalibrationBin("b29_sparse_low", 0.29, 9, 42),
            CalibrationBin("b41_large", 0.41, 38, 110),
            CalibrationBin("b55_sparse_high", 0.55, 29, 35),
            CalibrationBin("b69_large", 0.69, 71, 130),
            CalibrationBin("b83_sparse", 0.83, 20, 29),
            CalibrationBin("b94_large", 0.94, 54, 80),
        ),
    ),
    ForecastCurveCase(
        key="credit_noisy_middle_shift",
        real_case="held-out credit score where the middle calibration bands are shifted upward",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.53,
        global_base_rate=0.28,
        prior_strength=30.0,
        bins=(
            CalibrationBin("b09_large", 0.09, 31, 220),
            CalibrationBin("b21_mid", 0.21, 16, 55),
            CalibrationBin("b34_large", 0.34, 50, 140),
            CalibrationBin("b47_sparse", 0.47, 13, 26),
            CalibrationBin("b58_large", 0.58, 82, 160),
            CalibrationBin("b71_sparse", 0.71, 21, 32),
            CalibrationBin("b86_large", 0.86, 61, 100),
        ),
    ),
    ForecastCurveCase(
        key="defect_noisy_sparse_high",
        real_case="held-out defect score where sparse high bins are noisy around a low baseline",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.58,
        global_base_rate=0.12,
        prior_strength=60.0,
        bins=(
            CalibrationBin("b05_large", 0.05, 7, 260),
            CalibrationBin("b14_mid", 0.14, 11, 90),
            CalibrationBin("b26_sparse", 0.26, 4, 22),
            CalibrationBin("b38_large", 0.38, 34, 130),
            CalibrationBin("b51_sparse_high", 0.51, 13, 25),
            CalibrationBin("b63_large", 0.63, 57, 140),
            CalibrationBin("b77_sparse", 0.77, 11, 18),
            CalibrationBin("b91_large", 0.91, 39, 70),
        ),
    ),
]


SHIFT_CALIBRATION_CASES = [
    ShiftCalibrationCase(
        key="fraud_target_lift",
        real_case="merchant-risk model moved from a mature source cohort to a newer acquisition channel",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.44,
        source_base_rate=0.16,
        source_prior_strength=40.0,
        bridge_prior_strength=18.0,
        source_bins=(
            CalibrationBin("src_12", 0.12, 8, 120),
            CalibrationBin("src_28", 0.28, 22, 110),
            CalibrationBin("src_46", 0.46, 42, 100),
            CalibrationBin("src_68", 0.68, 67, 115),
            CalibrationBin("src_86", 0.86, 79, 95),
        ),
        bridge_bins=(
            CalibrationBin("bridge_30", 0.30, 16, 34),
            CalibrationBin("bridge_52", 0.52, 27, 40),
            CalibrationBin("bridge_76", 0.76, 23, 28),
        ),
    ),
    ShiftCalibrationCase(
        key="renewal_target_relief",
        real_case="enterprise churn model applied after a retention playbook changed the target cohort",
        target_event="account churns before renewal",
        raw_model_probability=0.72,
        source_base_rate=0.26,
        source_prior_strength=45.0,
        bridge_prior_strength=16.0,
        source_bins=(
            CalibrationBin("src_18", 0.18, 19, 120),
            CalibrationBin("src_38", 0.38, 46, 130),
            CalibrationBin("src_58", 0.58, 71, 125),
            CalibrationBin("src_78", 0.78, 82, 105),
            CalibrationBin("src_91", 0.91, 62, 70),
        ),
        bridge_bins=(
            CalibrationBin("bridge_44", 0.44, 9, 46),
            CalibrationBin("bridge_66", 0.66, 15, 48),
            CalibrationBin("bridge_84", 0.84, 15, 38),
        ),
    ),
    ShiftCalibrationCase(
        key="credit_bridge_steeper",
        real_case="small-business delinquency model moved into a cash-flow stressed target cohort",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.37,
        source_base_rate=0.24,
        source_prior_strength=35.0,
        bridge_prior_strength=14.0,
        source_bins=(
            CalibrationBin("src_10", 0.10, 18, 140),
            CalibrationBin("src_26", 0.26, 33, 135),
            CalibrationBin("src_44", 0.44, 54, 130),
            CalibrationBin("src_64", 0.64, 79, 125),
            CalibrationBin("src_82", 0.82, 78, 95),
        ),
        bridge_bins=(
            CalibrationBin("bridge_24", 0.24, 18, 42),
            CalibrationBin("bridge_40", 0.40, 28, 45),
            CalibrationBin("bridge_58", 0.58, 38, 46),
        ),
    ),
    ShiftCalibrationCase(
        key="defect_bridge_cooldown",
        real_case="launch-defect model reused after manufacturing controls improved the target cohort",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.58,
        source_base_rate=0.18,
        source_prior_strength=55.0,
        bridge_prior_strength=20.0,
        source_bins=(
            CalibrationBin("src_08", 0.08, 10, 160),
            CalibrationBin("src_24", 0.24, 31, 145),
            CalibrationBin("src_42", 0.42, 59, 140),
            CalibrationBin("src_62", 0.62, 81, 130),
            CalibrationBin("src_84", 0.84, 76, 92),
        ),
        bridge_bins=(
            CalibrationBin("bridge_32", 0.32, 8, 44),
            CalibrationBin("bridge_54", 0.54, 13, 46),
            CalibrationBin("bridge_74", 0.74, 15, 38),
        ),
    ),
]

ROLLING_CALIBRATION_CASES = [
    RollingCalibrationCase(
        key="renewal_playbook_cooldown",
        real_case="enterprise churn model after a retention playbook improved recent outcomes",
        target_event="account churns before renewal",
        raw_model_probability=0.72,
        global_base_rate=0.26,
        prior_strength=20.0,
        periods=(
            RollingCalibrationPeriod(
                "window_1_older",
                0.20,
                (
                    CalibrationBin("old_low", 0.44, 33, 90),
                    CalibrationBin("old_target", 0.72, 53, 80),
                    CalibrationBin("old_high", 0.88, 67, 90),
                ),
            ),
            RollingCalibrationPeriod(
                "window_2_mid",
                0.30,
                (
                    CalibrationBin("mid_low", 0.44, 24, 90),
                    CalibrationBin("mid_target", 0.72, 31, 80),
                    CalibrationBin("mid_high", 0.88, 47, 90),
                ),
            ),
            RollingCalibrationPeriod(
                "window_3_recent",
                0.50,
                (
                    CalibrationBin("recent_low", 0.44, 13, 90),
                    CalibrationBin("recent_target", 0.72, 17, 80),
                    CalibrationBin("recent_high", 0.88, 29, 90),
                ),
            ),
        ),
    ),
    RollingCalibrationCase(
        key="fraud_channel_surge",
        real_case="merchant-risk model after a new acquisition channel began producing fraudier traffic",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.34,
        global_base_rate=0.16,
        prior_strength=24.0,
        periods=(
            RollingCalibrationPeriod(
                "window_1_older",
                0.20,
                (
                    CalibrationBin("old_low", 0.18, 8, 100),
                    CalibrationBin("old_target", 0.34, 10, 90),
                    CalibrationBin("old_high", 0.58, 24, 100),
                ),
            ),
            RollingCalibrationPeriod(
                "window_2_mid",
                0.30,
                (
                    CalibrationBin("mid_low", 0.18, 16, 100),
                    CalibrationBin("mid_target", 0.34, 29, 90),
                    CalibrationBin("mid_high", 0.58, 49, 100),
                ),
            ),
            RollingCalibrationPeriod(
                "window_3_recent",
                0.50,
                (
                    CalibrationBin("recent_low", 0.18, 33, 100),
                    CalibrationBin("recent_target", 0.34, 63, 90),
                    CalibrationBin("recent_high", 0.58, 75, 100),
                ),
            ),
        ),
    ),
    RollingCalibrationCase(
        key="credit_policy_relief",
        real_case="small-business delinquency model after underwriting controls tightened over time",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.58,
        global_base_rate=0.28,
        prior_strength=30.0,
        periods=(
            RollingCalibrationPeriod(
                "window_1_older",
                0.20,
                (
                    CalibrationBin("old_low", 0.30, 35, 110),
                    CalibrationBin("old_target", 0.58, 58, 100),
                    CalibrationBin("old_high", 0.78, 78, 110),
                ),
            ),
            RollingCalibrationPeriod(
                "window_2_mid",
                0.30,
                (
                    CalibrationBin("mid_low", 0.30, 25, 110),
                    CalibrationBin("mid_target", 0.58, 34, 100),
                    CalibrationBin("mid_high", 0.78, 55, 110),
                ),
            ),
            RollingCalibrationPeriod(
                "window_3_recent",
                0.50,
                (
                    CalibrationBin("recent_low", 0.30, 15, 110),
                    CalibrationBin("recent_target", 0.58, 15, 100),
                    CalibrationBin("recent_high", 0.78, 28, 110),
                ),
            ),
        ),
    ),
    RollingCalibrationCase(
        key="defect_supplier_regression",
        real_case="launch-defect model after a component supplier change worsened recent outcomes",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.46,
        global_base_rate=0.12,
        prior_strength=36.0,
        periods=(
            RollingCalibrationPeriod(
                "window_1_older",
                0.20,
                (
                    CalibrationBin("old_low", 0.22, 7, 100),
                    CalibrationBin("old_target", 0.46, 13, 95),
                    CalibrationBin("old_high", 0.70, 27, 100),
                ),
            ),
            RollingCalibrationPeriod(
                "window_2_mid",
                0.30,
                (
                    CalibrationBin("mid_low", 0.22, 11, 100),
                    CalibrationBin("mid_target", 0.46, 23, 95),
                    CalibrationBin("mid_high", 0.70, 41, 100),
                ),
            ),
            RollingCalibrationPeriod(
                "window_3_recent",
                0.50,
                (
                    CalibrationBin("recent_low", 0.22, 22, 100),
                    CalibrationBin("recent_target", 0.46, 51, 95),
                    CalibrationBin("recent_high", 0.70, 69, 100),
                ),
            ),
        ),
    ),
]

ROLLING_LOG_CALIBRATION_CASES = [
    RollingLogCalibrationCase(
        key="retention_log_cooldown",
        real_case="enterprise churn scorecard after a retention playbook changed the recent renewal mix",
        target_event="account churns before renewal",
        raw_model_probability=0.72,
        global_base_rate=0.26,
        prior_strength=20.0,
        recency_half_life_days=45.0,
        periods=(
            RollingLogCalibrationPeriod(
                "jan_review",
                105.0,
                (
                    CalibrationBin("jan_low", 0.44, 33, 90),
                    CalibrationBin("jan_target", 0.72, 53, 80),
                    CalibrationBin("jan_high", 0.88, 67, 90),
                ),
            ),
            RollingLogCalibrationPeriod(
                "mar_review",
                45.0,
                (
                    CalibrationBin("mar_low", 0.44, 24, 90),
                    CalibrationBin("mar_target", 0.72, 31, 80),
                    CalibrationBin("mar_high", 0.88, 47, 90),
                ),
            ),
            RollingLogCalibrationPeriod(
                "apr_review",
                12.0,
                (
                    CalibrationBin("apr_low", 0.44, 13, 90),
                    CalibrationBin("apr_target", 0.72, 17, 80),
                    CalibrationBin("apr_high", 0.88, 29, 90),
                ),
            ),
        ),
    ),
    RollingLogCalibrationCase(
        key="merchant_log_surge",
        real_case="merchant fraud screen after a new acquisition channel began shifting traffic quality",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.34,
        global_base_rate=0.16,
        prior_strength=24.0,
        recency_half_life_days=40.0,
        periods=(
            RollingLogCalibrationPeriod(
                "nov_review",
                120.0,
                (
                    CalibrationBin("nov_low", 0.18, 8, 100),
                    CalibrationBin("nov_target", 0.34, 10, 90),
                    CalibrationBin("nov_high", 0.58, 24, 100),
                ),
            ),
            RollingLogCalibrationPeriod(
                "feb_review",
                58.0,
                (
                    CalibrationBin("feb_low", 0.18, 16, 100),
                    CalibrationBin("feb_target", 0.34, 29, 90),
                    CalibrationBin("feb_high", 0.58, 49, 100),
                ),
            ),
            RollingLogCalibrationPeriod(
                "may_review",
                10.0,
                (
                    CalibrationBin("may_low", 0.18, 33, 100),
                    CalibrationBin("may_target", 0.34, 63, 90),
                    CalibrationBin("may_high", 0.58, 75, 100),
                ),
            ),
        ),
    ),
    RollingLogCalibrationCase(
        key="credit_log_relief",
        real_case="small-business delinquency score after underwriting controls tightened gradually",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.58,
        global_base_rate=0.28,
        prior_strength=30.0,
        recency_half_life_days=50.0,
        periods=(
            RollingLogCalibrationPeriod(
                "q4_review",
                150.0,
                (
                    CalibrationBin("q4_low", 0.30, 35, 110),
                    CalibrationBin("q4_target", 0.58, 58, 100),
                    CalibrationBin("q4_high", 0.78, 78, 110),
                ),
            ),
            RollingLogCalibrationPeriod(
                "q1_review",
                75.0,
                (
                    CalibrationBin("q1_low", 0.30, 25, 110),
                    CalibrationBin("q1_target", 0.58, 34, 100),
                    CalibrationBin("q1_high", 0.78, 55, 110),
                ),
            ),
            RollingLogCalibrationPeriod(
                "q2_review",
                14.0,
                (
                    CalibrationBin("q2_low", 0.30, 15, 110),
                    CalibrationBin("q2_target", 0.58, 15, 100),
                    CalibrationBin("q2_high", 0.78, 28, 110),
                ),
            ),
        ),
    ),
    RollingLogCalibrationCase(
        key="defect_log_regression",
        real_case="launch-defect model after a supplier change worsened the most recent cohorts",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.46,
        global_base_rate=0.12,
        prior_strength=36.0,
        recency_half_life_days=35.0,
        periods=(
            RollingLogCalibrationPeriod(
                "baseline_audit",
                100.0,
                (
                    CalibrationBin("base_low", 0.22, 7, 100),
                    CalibrationBin("base_target", 0.46, 13, 95),
                    CalibrationBin("base_high", 0.70, 27, 100),
                ),
            ),
            RollingLogCalibrationPeriod(
                "transition_audit",
                45.0,
                (
                    CalibrationBin("transition_low", 0.22, 11, 100),
                    CalibrationBin("transition_target", 0.46, 23, 95),
                    CalibrationBin("transition_high", 0.70, 41, 100),
                ),
            ),
            RollingLogCalibrationPeriod(
                "current_audit",
                8.0,
                (
                    CalibrationBin("current_low", 0.22, 22, 100),
                    CalibrationBin("current_target", 0.46, 51, 95),
                    CalibrationBin("current_high", 0.70, 69, 100),
                ),
            ),
        ),
    ),
]

NOISY_ROLLING_LOG_CALIBRATION_CASES = [
    RollingLogCalibrationCase(
        key="retention_noisy_cooldown",
        real_case="enterprise churn scorecard after a retention playbook changed the renewal mix",
        target_event="account churns before renewal",
        raw_model_probability=0.72,
        global_base_rate=0.26,
        prior_strength=20.0,
        recency_half_life_days=30.0,
        periods=(
            RollingLogCalibrationPeriod(
                "january_audit",
                110.0,
                (
                    CalibrationBin("jan_low", 0.44, 32, 92),
                    CalibrationBin("jan_target", 0.72, 54, 80),
                    CalibrationBin("jan_high", 0.88, 69, 91),
                ),
            ),
            RollingLogCalibrationPeriod(
                "march_audit",
                72.0,
                (
                    CalibrationBin("mar_low", 0.44, 27, 89),
                    CalibrationBin("mar_target", 0.72, 40, 80),
                    CalibrationBin("mar_high", 0.88, 49, 83),
                ),
            ),
            RollingLogCalibrationPeriod(
                "april_audit",
                35.0,
                (
                    CalibrationBin("apr_low", 0.44, 18, 76),
                    CalibrationBin("apr_target", 0.72, 25, 78),
                    CalibrationBin("apr_high", 0.88, 35, 74),
                ),
            ),
            RollingLogCalibrationPeriod(
                "current_audit",
                8.0,
                (
                    CalibrationBin("current_low", 0.44, 8, 41),
                    CalibrationBin("current_target", 0.72, 13, 42),
                    CalibrationBin("current_high", 0.88, 19, 39),
                ),
            ),
        ),
    ),
    RollingLogCalibrationCase(
        key="merchant_noisy_surge",
        real_case="merchant fraud screen after a new acquisition channel shifted traffic quality",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.34,
        global_base_rate=0.16,
        prior_strength=24.0,
        recency_half_life_days=21.0,
        periods=(
            RollingLogCalibrationPeriod(
                "old_queue",
                84.0,
                (
                    CalibrationBin("old_low", 0.18, 7, 96),
                    CalibrationBin("old_target", 0.34, 10, 90),
                    CalibrationBin("old_high", 0.58, 26, 103),
                ),
            ),
            RollingLogCalibrationPeriod(
                "mid_queue",
                49.0,
                (
                    CalibrationBin("mid_low", 0.18, 13, 86),
                    CalibrationBin("mid_target", 0.34, 24, 88),
                    CalibrationBin("mid_high", 0.58, 45, 94),
                ),
            ),
            RollingLogCalibrationPeriod(
                "recent_queue",
                21.0,
                (
                    CalibrationBin("recent_low", 0.18, 21, 74),
                    CalibrationBin("recent_target", 0.34, 44, 84),
                    CalibrationBin("recent_high", 0.58, 65, 91),
                ),
            ),
            RollingLogCalibrationPeriod(
                "live_queue",
                5.0,
                (
                    CalibrationBin("live_low", 0.18, 15, 38),
                    CalibrationBin("live_target", 0.34, 35, 40),
                    CalibrationBin("live_high", 0.58, 37, 41),
                ),
            ),
        ),
    ),
    RollingLogCalibrationCase(
        key="credit_noisy_relief",
        real_case="small-business delinquency score after underwriting controls tightened gradually",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.58,
        global_base_rate=0.28,
        prior_strength=30.0,
        recency_half_life_days=45.0,
        periods=(
            RollingLogCalibrationPeriod(
                "legacy_book",
                160.0,
                (
                    CalibrationBin("legacy_low", 0.30, 36, 112),
                    CalibrationBin("legacy_target", 0.58, 58, 100),
                    CalibrationBin("legacy_high", 0.78, 79, 109),
                ),
            ),
            RollingLogCalibrationPeriod(
                "transition_book",
                95.0,
                (
                    CalibrationBin("transition_low", 0.30, 27, 106),
                    CalibrationBin("transition_target", 0.58, 43, 102),
                    CalibrationBin("transition_high", 0.78, 57, 105),
                ),
            ),
            RollingLogCalibrationPeriod(
                "recent_book",
                40.0,
                (
                    CalibrationBin("recent_low", 0.30, 13, 88),
                    CalibrationBin("recent_target", 0.58, 20, 92),
                    CalibrationBin("recent_high", 0.78, 29, 86),
                ),
            ),
            RollingLogCalibrationPeriod(
                "thin_current_book",
                9.0,
                (
                    CalibrationBin("thin_low", 0.30, 5, 36),
                    CalibrationBin("thin_target", 0.58, 8, 35),
                    CalibrationBin("thin_high", 0.78, 13, 34),
                ),
            ),
        ),
    ),
    RollingLogCalibrationCase(
        key="defect_noisy_regression",
        real_case="launch-defect model after a supplier change worsened the most recent cohorts",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.46,
        global_base_rate=0.12,
        prior_strength=36.0,
        recency_half_life_days=21.0,
        periods=(
            RollingLogCalibrationPeriod(
                "baseline_audit",
                90.0,
                (
                    CalibrationBin("baseline_low", 0.22, 6, 94),
                    CalibrationBin("baseline_target", 0.46, 13, 95),
                    CalibrationBin("baseline_high", 0.70, 28, 101),
                ),
            ),
            RollingLogCalibrationPeriod(
                "changeover_audit",
                48.0,
                (
                    CalibrationBin("change_low", 0.22, 10, 87),
                    CalibrationBin("change_target", 0.46, 20, 88),
                    CalibrationBin("change_high", 0.70, 39, 92),
                ),
            ),
            RollingLogCalibrationPeriod(
                "new_supplier_audit",
                19.0,
                (
                    CalibrationBin("new_low", 0.22, 17, 77),
                    CalibrationBin("new_target", 0.46, 39, 82),
                    CalibrationBin("new_high", 0.70, 61, 86),
                ),
            ),
            RollingLogCalibrationPeriod(
                "thin_current_audit",
                4.0,
                (
                    CalibrationBin("thin_low", 0.22, 10, 35),
                    CalibrationBin("thin_target", 0.46, 30, 36),
                    CalibrationBin("thin_high", 0.70, 34, 37),
                ),
            ),
        ),
    ),
]

EVENT_LOG_CALIBRATION_CASES = [
    EventLogCalibrationCase(
        key="retention_item_log_cooldown",
        real_case="enterprise churn scorecard after a retention playbook shifted recent renewals",
        target_event="account churns before renewal",
        raw_model_probability=0.72,
        global_base_rate=0.26,
        prior_strength=20.0,
        recency_half_life_days=30.0,
        score_kernel_width=0.12,
        entries=_event_log_entries(
            "retention",
            (
                ("old_low", 0.50, 126.0, 5, 14),
                ("old_target", 0.72, 124.0, 11, 16),
                ("old_high", 0.88, 122.0, 13, 16),
                ("mid_target", 0.72, 54.0, 7, 14),
                ("recent_target", 0.72, 19.0, 4, 14),
                ("live_target", 0.72, 5.0, 2, 8),
            ),
        ),
    ),
    EventLogCalibrationCase(
        key="merchant_item_log_surge",
        real_case="merchant fraud screen after acquisition traffic changed quickly",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.34,
        global_base_rate=0.16,
        prior_strength=24.0,
        recency_half_life_days=21.0,
        score_kernel_width=0.12,
        entries=_event_log_entries(
            "merchant",
            (
                ("old_low", 0.18, 88.0, 1, 14),
                ("old_target", 0.34, 86.0, 2, 16),
                ("old_high", 0.58, 84.0, 4, 14),
                ("mid_target", 0.34, 48.0, 5, 16),
                ("recent_target", 0.34, 20.0, 11, 16),
                ("live_target", 0.34, 4.0, 7, 8),
            ),
        ),
    ),
    EventLogCalibrationCase(
        key="credit_item_log_relief",
        real_case="small-business delinquency score after tighter underwriting controls",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.58,
        global_base_rate=0.28,
        prior_strength=30.0,
        recency_half_life_days=45.0,
        score_kernel_width=0.12,
        entries=_event_log_entries(
            "credit",
            (
                ("old_low", 0.30, 158.0, 5, 14),
                ("old_target", 0.58, 156.0, 12, 18),
                ("old_high", 0.78, 154.0, 14, 18),
                ("mid_target", 0.58, 92.0, 7, 16),
                ("recent_target", 0.58, 38.0, 3, 14),
                ("live_target", 0.58, 8.0, 1, 8),
            ),
        ),
    ),
    EventLogCalibrationCase(
        key="defect_item_log_regression",
        real_case="launch-defect model after a supplier change worsened recent cohorts",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.46,
        global_base_rate=0.12,
        prior_strength=36.0,
        recency_half_life_days=21.0,
        score_kernel_width=0.12,
        entries=_event_log_entries(
            "defect",
            (
                ("old_low", 0.22, 92.0, 1, 14),
                ("old_target", 0.46, 88.0, 2, 16),
                ("old_high", 0.70, 86.0, 5, 14),
                ("mid_target", 0.46, 48.0, 5, 16),
                ("recent_target", 0.46, 19.0, 11, 16),
                ("live_target", 0.46, 4.0, 7, 8),
            ),
        ),
    ),
]


OPERATIONAL_LOG_CALIBRATION_CASES = [
    OperationalLogCalibrationCase(
        key="retention_policy_route_cooldown",
        real_case="enterprise churn scorecard after a retention policy changed high-touch accounts",
        target_event="account churns before renewal",
        raw_model_probability=0.68,
        global_base_rate=0.24,
        prior_strength=18.0,
        recency_half_life_days=30.0,
        score_kernel_width=0.11,
        current_policy="retention_playbook_v2",
        current_route="enterprise_high_touch",
        entries=_operational_log_entries(
            "retention_ops",
            (
                ("old_current", 0.68, 116.0, "retention_playbook_v2", "enterprise_high_touch", 9, 14),
                ("mid_current", 0.68, 49.0, "retention_playbook_v2", "enterprise_high_touch", 5, 14),
                ("recent_current", 0.68, 17.0, "retention_playbook_v2", "enterprise_high_touch", 2, 14),
                ("live_current", 0.68, 4.0, "retention_playbook_v2", "enterprise_high_touch", 1, 8),
                ("policy_old", 0.68, 53.0, "legacy_discount_default", "enterprise_high_touch", 10, 14),
                ("policy_recent", 0.68, 12.0, "legacy_discount_default", "enterprise_high_touch", 8, 10),
                ("route_old", 0.68, 46.0, "retention_playbook_v2", "self_serve_queue", 9, 14),
                ("route_recent", 0.68, 10.0, "retention_playbook_v2", "self_serve_queue", 7, 10),
                ("far_score_recent", 0.36, 9.0, "retention_playbook_v2", "enterprise_high_touch", 6, 10),
            ),
        ),
    ),
    OperationalLogCalibrationCase(
        key="merchant_route_policy_surge",
        real_case="merchant fraud screen after a traffic gate changed affiliate onboarding",
        target_event="merchant account has a confirmed fraud escalation",
        raw_model_probability=0.30,
        global_base_rate=0.15,
        prior_strength=22.0,
        recency_half_life_days=21.0,
        score_kernel_width=0.11,
        current_policy="traffic_quality_gate",
        current_route="affiliate_onboarding",
        entries=_operational_log_entries(
            "merchant_ops",
            (
                ("old_current", 0.30, 84.0, "traffic_quality_gate", "affiliate_onboarding", 2, 14),
                ("mid_current", 0.30, 39.0, "traffic_quality_gate", "affiliate_onboarding", 6, 14),
                ("recent_current", 0.30, 14.0, "traffic_quality_gate", "affiliate_onboarding", 10, 14),
                ("live_current", 0.30, 3.0, "traffic_quality_gate", "affiliate_onboarding", 6, 8),
                ("policy_old", 0.30, 41.0, "legacy_fast_approve", "affiliate_onboarding", 2, 14),
                ("policy_recent", 0.30, 9.0, "legacy_fast_approve", "affiliate_onboarding", 1, 10),
                ("route_old", 0.30, 37.0, "traffic_quality_gate", "direct_referral", 2, 14),
                ("route_recent", 0.30, 8.0, "traffic_quality_gate", "direct_referral", 1, 10),
                ("far_score_recent", 0.60, 7.0, "traffic_quality_gate", "affiliate_onboarding", 1, 10),
            ),
        ),
    ),
    OperationalLogCalibrationCase(
        key="credit_policy_route_relief",
        real_case="small-business delinquency model after tighter underwriting on documented cashflow loans",
        target_event="borrower becomes 60 days delinquent",
        raw_model_probability=0.62,
        global_base_rate=0.27,
        prior_strength=26.0,
        recency_half_life_days=45.0,
        score_kernel_width=0.11,
        current_policy="tightened_underwriting",
        current_route="cashflow_docs",
        entries=_operational_log_entries(
            "credit_ops",
            (
                ("old_current", 0.62, 150.0, "tightened_underwriting", "cashflow_docs", 10, 16),
                ("mid_current", 0.62, 78.0, "tightened_underwriting", "cashflow_docs", 6, 16),
                ("recent_current", 0.62, 31.0, "tightened_underwriting", "cashflow_docs", 3, 14),
                ("live_current", 0.62, 6.0, "tightened_underwriting", "cashflow_docs", 1, 8),
                ("policy_old", 0.62, 74.0, "legacy_underwriting", "cashflow_docs", 11, 16),
                ("policy_recent", 0.62, 24.0, "legacy_underwriting", "cashflow_docs", 8, 10),
                ("route_old", 0.62, 70.0, "tightened_underwriting", "bank_statement_only", 10, 16),
                ("route_recent", 0.62, 20.0, "tightened_underwriting", "bank_statement_only", 7, 10),
                ("far_score_recent", 0.34, 18.0, "tightened_underwriting", "cashflow_docs", 7, 10),
            ),
        ),
    ),
    OperationalLogCalibrationCase(
        key="defect_policy_route_regression",
        real_case="launch-defect model after supplier-policy and rush-route operations diverged",
        target_event="batch exceeds the defect escalation threshold",
        raw_model_probability=0.40,
        global_base_rate=0.13,
        prior_strength=24.0,
        recency_half_life_days=21.0,
        score_kernel_width=0.11,
        current_policy="supplier_b_expedite",
        current_route="rush_launch_batch",
        entries=_operational_log_entries(
            "defect_ops",
            (
                ("old_current", 0.40, 88.0, "supplier_b_expedite", "rush_launch_batch", 2, 14),
                ("mid_current", 0.40, 42.0, "supplier_b_expedite", "rush_launch_batch", 6, 14),
                ("recent_current", 0.40, 15.0, "supplier_b_expedite", "rush_launch_batch", 11, 14),
                ("live_current", 0.40, 3.0, "supplier_b_expedite", "rush_launch_batch", 7, 8),
                ("policy_old", 0.40, 39.0, "supplier_a_standard", "rush_launch_batch", 1, 14),
                ("policy_recent", 0.40, 9.0, "supplier_a_standard", "rush_launch_batch", 1, 10),
                ("route_old", 0.40, 37.0, "supplier_b_expedite", "scheduled_batch", 1, 14),
                ("route_recent", 0.40, 8.0, "supplier_b_expedite", "scheduled_batch", 1, 10),
                ("far_score_recent", 0.72, 7.0, "supplier_b_expedite", "rush_launch_batch", 1, 10),
            ),
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


def _interpolate_points(points: list[tuple[float, float]], raw: float) -> float:
    if raw <= points[0][0]:
        return points[0][1]
    if raw >= points[-1][0]:
        return points[-1][1]
    for (left_raw, left_value), (right_raw, right_value) in zip(points, points[1:]):
        if left_raw <= raw <= right_raw:
            weight = (raw - left_raw) / max(right_raw - left_raw, 1e-12)
            return left_value + weight * (right_value - left_value)
    return points[-1][1]


def source_bin_probability(case: ShiftCalibrationCase, bin_: CalibrationBin) -> float:
    prior_events = case.source_prior_strength * case.source_base_rate
    return (bin_.observed_event_count + prior_events) / (
        bin_.observed_total + case.source_prior_strength
    )


def source_curve_probability(case: ShiftCalibrationCase, raw: float | None = None) -> float:
    points = sorted(
        (bin_.raw_mean_probability, source_bin_probability(case, bin_))
        for bin_ in case.source_bins
    )
    return _interpolate_points(points, case.raw_model_probability if raw is None else raw)


def bridge_adjusted_probability(case: ShiftCalibrationCase, bin_: CalibrationBin) -> float:
    source_probability = source_curve_probability(case, bin_.raw_mean_probability)
    prior_events = case.bridge_prior_strength * source_probability
    return (bin_.observed_event_count + prior_events) / (
        bin_.observed_total + case.bridge_prior_strength
    )


def shift_calibrated_probability(case: ShiftCalibrationCase) -> float:
    source_at_target = source_curve_probability(case)
    shift_points = sorted(
        (
            bin_.raw_mean_probability,
            bridge_adjusted_probability(case, bin_)
            - source_curve_probability(case, bin_.raw_mean_probability),
        )
        for bin_ in case.bridge_bins
    )
    shift = _interpolate_points(shift_points, case.raw_model_probability)
    return clamp(source_at_target + shift, 0.0, 1.0)


def nearest_bridge_probability(case: ShiftCalibrationCase) -> float:
    nearest = min(
        case.bridge_bins,
        key=lambda bin_: abs(bin_.raw_mean_probability - case.raw_model_probability),
    )
    return bridge_adjusted_probability(case, nearest)


def rolling_period_probability(
    case: RollingCalibrationCase,
    period: RollingCalibrationPeriod,
) -> float:
    points = sorted(
        (
            bin_.raw_mean_probability,
            rolling_bin_probability(case, bin_),
        )
        for bin_ in period.bins
    )
    return _interpolate_points(points, case.raw_model_probability)


def rolling_bin_probability(case: RollingCalibrationCase, bin_: CalibrationBin) -> float:
    prior_events = case.prior_strength * case.global_base_rate
    return (bin_.observed_event_count + prior_events) / (
        bin_.observed_total + case.prior_strength
    )


def rolling_calibrated_probability(case: RollingCalibrationCase) -> float:
    weight_total = sum(period.recency_weight for period in case.periods)
    if weight_total <= 0:
        return pooled_rolling_probability(case)
    return sum(
        period.recency_weight * rolling_period_probability(case, period)
        for period in case.periods
    ) / weight_total


def stale_rolling_probability(case: RollingCalibrationCase) -> float:
    return rolling_period_probability(case, case.periods[0])


def pooled_rolling_probability(case: RollingCalibrationCase) -> float:
    by_center: dict[float, list[float]] = {}
    for period in case.periods:
        for bin_ in period.bins:
            events, total = by_center.setdefault(bin_.raw_mean_probability, [0.0, 0.0])
            by_center[bin_.raw_mean_probability] = [
                events + bin_.observed_event_count,
                total + bin_.observed_total,
            ]
    points = sorted(
        (
            raw,
            (events + case.prior_strength * case.global_base_rate)
            / max(total + case.prior_strength, 1e-12),
        )
        for raw, (events, total) in by_center.items()
    )
    return _interpolate_points(points, case.raw_model_probability)


def rolling_log_period_weight(
    case: RollingLogCalibrationCase,
    period: RollingLogCalibrationPeriod,
) -> float:
    half_life = max(case.recency_half_life_days, 1e-12)
    return 0.5 ** (max(period.days_before_target_midpoint, 0.0) / half_life)


def rolling_log_bin_probability(case: RollingLogCalibrationCase, bin_: CalibrationBin) -> float:
    prior_events = case.prior_strength * case.global_base_rate
    return (bin_.observed_event_count + prior_events) / (
        bin_.observed_total + case.prior_strength
    )


def rolling_log_period_probability(
    case: RollingLogCalibrationCase,
    period: RollingLogCalibrationPeriod,
) -> float:
    points = sorted(
        (
            bin_.raw_mean_probability,
            rolling_log_bin_probability(case, bin_),
        )
        for bin_ in period.bins
    )
    return _interpolate_points(points, case.raw_model_probability)


def rolling_log_calibrated_probability(case: RollingLogCalibrationCase) -> float:
    weights = [rolling_log_period_weight(case, period) for period in case.periods]
    weight_total = sum(weights)
    if weight_total <= 0:
        return pooled_rolling_log_probability(case)
    return sum(
        weight * rolling_log_period_probability(case, period)
        for weight, period in zip(weights, case.periods)
    ) / weight_total


def stale_rolling_log_probability(case: RollingLogCalibrationCase) -> float:
    period = max(case.periods, key=lambda candidate: candidate.days_before_target_midpoint)
    return rolling_log_period_probability(case, period)


def latest_rolling_log_probability(case: RollingLogCalibrationCase) -> float:
    period = min(case.periods, key=lambda candidate: candidate.days_before_target_midpoint)
    return rolling_log_period_probability(case, period)


def pooled_rolling_log_probability(case: RollingLogCalibrationCase) -> float:
    by_center: dict[float, list[float]] = {}
    for period in case.periods:
        for bin_ in period.bins:
            events, total = by_center.setdefault(bin_.raw_mean_probability, [0.0, 0.0])
            by_center[bin_.raw_mean_probability] = [
                events + bin_.observed_event_count,
                total + bin_.observed_total,
            ]
    points = sorted(
        (
            raw,
            (events + case.prior_strength * case.global_base_rate)
            / max(total + case.prior_strength, 1e-12),
        )
        for raw, (events, total) in by_center.items()
    )
    return _interpolate_points(points, case.raw_model_probability)


def event_log_entry_weight(
    case: EventLogCalibrationCase,
    entry: EventLogCalibrationEntry,
    *,
    use_recency: bool = True,
) -> float:
    score_distance = (entry.raw_model_probability - case.raw_model_probability) / max(
        case.score_kernel_width,
        1e-12,
    )
    score_weight = math.exp(-0.5 * score_distance * score_distance)
    if not use_recency:
        return score_weight
    recency_weight = 0.5 ** (
        max(entry.days_before_target, 0.0) / max(case.recency_half_life_days, 1e-12)
    )
    return score_weight * recency_weight


def event_log_probability(
    case: EventLogCalibrationCase,
    entries: tuple[EventLogCalibrationEntry, ...],
    *,
    use_recency: bool = True,
) -> float:
    weighted_events = sum(
        event_log_entry_weight(case, entry, use_recency=use_recency)
        * float(entry.event_observed)
        for entry in entries
    )
    weighted_total = sum(
        event_log_entry_weight(case, entry, use_recency=use_recency) for entry in entries
    )
    prior_events = case.prior_strength * case.global_base_rate
    return (weighted_events + prior_events) / max(weighted_total + case.prior_strength, 1e-12)


def event_log_calibrated_probability(case: EventLogCalibrationCase) -> float:
    return event_log_probability(case, case.entries, use_recency=True)


def pooled_event_log_probability(case: EventLogCalibrationCase) -> float:
    return event_log_probability(case, case.entries, use_recency=False)


def stale_event_log_probability(case: EventLogCalibrationCase) -> float:
    stale_entries = tuple(
        entry
        for entry in case.entries
        if entry.days_before_target >= 2.0 * case.recency_half_life_days
    )
    if not stale_entries:
        oldest_age = max(entry.days_before_target for entry in case.entries)
        stale_entries = tuple(entry for entry in case.entries if entry.days_before_target == oldest_age)
    return event_log_probability(case, stale_entries, use_recency=False)


def latest_event_log_probability(case: EventLogCalibrationCase) -> float:
    latest_entries = tuple(
        entry
        for entry in case.entries
        if entry.days_before_target <= 0.5 * case.recency_half_life_days
    )
    if not latest_entries:
        latest_age = min(entry.days_before_target for entry in case.entries)
        latest_entries = tuple(entry for entry in case.entries if entry.days_before_target == latest_age)
    return event_log_probability(case, latest_entries, use_recency=False)


def operational_log_entry_weight(
    case: OperationalLogCalibrationCase,
    entry: OperationalLogCalibrationEntry,
    *,
    use_recency: bool = True,
    require_policy: bool = True,
    require_route: bool = True,
) -> float:
    if require_policy and entry.policy != case.current_policy:
        return 0.0
    if require_route and entry.route != case.current_route:
        return 0.0
    score_distance = (
        (entry.raw_model_probability - case.raw_model_probability)
        / max(case.score_kernel_width, 1e-12)
    )
    score_weight = math.exp(-0.5 * score_distance * score_distance)
    if not use_recency:
        return score_weight
    recency_weight = 0.5 ** (
        max(entry.days_before_target, 0.0) / max(case.recency_half_life_days, 1e-12)
    )
    return score_weight * recency_weight


def operational_log_probability(
    case: OperationalLogCalibrationCase,
    entries: tuple[OperationalLogCalibrationEntry, ...],
    *,
    use_recency: bool = True,
    require_policy: bool = True,
    require_route: bool = True,
) -> float:
    weighted_events = sum(
        operational_log_entry_weight(
            case,
            entry,
            use_recency=use_recency,
            require_policy=require_policy,
            require_route=require_route,
        )
        * float(entry.event_observed)
        for entry in entries
    )
    weighted_total = sum(
        operational_log_entry_weight(
            case,
            entry,
            use_recency=use_recency,
            require_policy=require_policy,
            require_route=require_route,
        )
        for entry in entries
    )
    prior_events = case.prior_strength * case.global_base_rate
    return (weighted_events + prior_events) / max(weighted_total + case.prior_strength, 1e-12)


def operational_log_calibrated_probability(case: OperationalLogCalibrationCase) -> float:
    return operational_log_probability(case, case.entries, use_recency=True)


def pooled_operational_log_probability(case: OperationalLogCalibrationCase) -> float:
    return operational_log_probability(
        case,
        case.entries,
        use_recency=False,
        require_policy=False,
        require_route=False,
    )


def policy_blind_operational_log_probability(case: OperationalLogCalibrationCase) -> float:
    return operational_log_probability(
        case,
        case.entries,
        use_recency=True,
        require_policy=False,
        require_route=True,
    )


def route_blind_operational_log_probability(case: OperationalLogCalibrationCase) -> float:
    return operational_log_probability(
        case,
        case.entries,
        use_recency=True,
        require_policy=True,
        require_route=False,
    )


def _operational_context_entries(
    case: OperationalLogCalibrationCase,
) -> tuple[OperationalLogCalibrationEntry, ...]:
    return tuple(
        entry
        for entry in case.entries
        if entry.policy == case.current_policy and entry.route == case.current_route
    )


def stale_operational_log_probability(case: OperationalLogCalibrationCase) -> float:
    context_entries = _operational_context_entries(case)
    stale_entries = tuple(
        entry
        for entry in context_entries
        if entry.days_before_target >= 2.0 * case.recency_half_life_days
    )
    if not stale_entries:
        oldest_age = max(entry.days_before_target for entry in context_entries)
        stale_entries = tuple(entry for entry in context_entries if entry.days_before_target == oldest_age)
    return operational_log_probability(case, stale_entries, use_recency=False)


def latest_operational_log_probability(case: OperationalLogCalibrationCase) -> float:
    context_entries = _operational_context_entries(case)
    latest_entries = tuple(
        entry
        for entry in context_entries
        if entry.days_before_target <= 0.5 * case.recency_half_life_days
    )
    if not latest_entries:
        latest_age = min(entry.days_before_target for entry in context_entries)
        latest_entries = tuple(entry for entry in context_entries if entry.days_before_target == latest_age)
    return operational_log_probability(case, latest_entries, use_recency=False)


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


def run_forecast_curve_noisy_game(
    agent: Agent,
    cases: list[ForecastCurveCase] | None = None,
) -> dict:
    return _run_forecast_curve_game(
        agent,
        cases or NOISY_CURVE_CASES,
        prompt_fn=_curve_noisy_prompt,
        task_name="forecast_curve_noisy",
    )


def run_forecast_curve_natural_game(
    agent: Agent,
    cases: list[ForecastCurveCase] | None = None,
) -> dict:
    return _run_forecast_curve_game(
        agent,
        cases or NOISY_CURVE_CASES,
        prompt_fn=_curve_natural_prompt,
        task_name="forecast_curve_natural",
    )


def run_forecast_shift_calibration_game(
    agent: Agent,
    cases: list[ShiftCalibrationCase] | None = None,
) -> dict:
    cases = cases or SHIFT_CALIBRATION_CASES
    trials: list[ShiftForecastTrial] = []
    for case in cases:
        calibrated = shift_calibrated_probability(case)
        source_only = source_curve_probability(case)
        nearest_bridge = nearest_bridge_probability(case)
        response = agent.complete(FORECAST_SYSTEM, _shift_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.08
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        source_curve_miss = (
            chosen is not None
            and abs(source_only - calibrated) >= 0.05
            and abs(chosen - source_only) < abs(chosen - calibrated)
        )
        nearest_bridge_miss = (
            chosen is not None
            and abs(nearest_bridge - calibrated) >= 0.03
            and abs(chosen - nearest_bridge) < abs(chosen - calibrated)
        )
        trials.append(
            ShiftForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                source_curve_probability=source_only,
                nearest_bridge_probability=nearest_bridge,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                source_curve_miss=source_curve_miss,
                nearest_bridge_miss=nearest_bridge_miss,
                raw_response=response,
            )
        )
    return summarize_shift_forecast_trials(agent.name, trials)


def run_forecast_rolling_calibration_game(
    agent: Agent,
    cases: list[RollingCalibrationCase] | None = None,
) -> dict:
    cases = cases or ROLLING_CALIBRATION_CASES
    trials: list[RollingForecastTrial] = []
    for case in cases:
        calibrated = rolling_calibrated_probability(case)
        stale = stale_rolling_probability(case)
        pooled = pooled_rolling_probability(case)
        response = agent.complete(FORECAST_SYSTEM, _rolling_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.08
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        stale_window_miss = (
            chosen is not None
            and abs(stale - calibrated) >= 0.05
            and abs(chosen - stale) < abs(chosen - calibrated)
        )
        pooled_history_miss = (
            chosen is not None
            and abs(pooled - calibrated) >= 0.03
            and abs(chosen - pooled) < abs(chosen - calibrated)
        )
        trials.append(
            RollingForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                stale_window_probability=stale,
                pooled_history_probability=pooled,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                stale_window_miss=stale_window_miss,
                pooled_history_miss=pooled_history_miss,
                raw_response=response,
            )
        )
    return summarize_rolling_forecast_trials(agent.name, trials)


def run_forecast_rolling_log_calibration_game(
    agent: Agent,
    cases: list[RollingLogCalibrationCase] | None = None,
) -> dict:
    cases = cases or ROLLING_LOG_CALIBRATION_CASES
    trials: list[RollingLogForecastTrial] = []
    for case in cases:
        calibrated = rolling_log_calibrated_probability(case)
        stale = stale_rolling_log_probability(case)
        pooled = pooled_rolling_log_probability(case)
        latest = latest_rolling_log_probability(case)
        response = agent.complete(FORECAST_SYSTEM, _rolling_log_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.08
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        stale_window_miss = (
            chosen is not None
            and abs(stale - calibrated) >= 0.05
            and abs(chosen - stale) < abs(chosen - calibrated)
        )
        pooled_history_miss = (
            chosen is not None
            and abs(pooled - calibrated) >= 0.03
            and abs(chosen - pooled) < abs(chosen - calibrated)
        )
        latest_window_miss = (
            chosen is not None
            and abs(latest - calibrated) >= 0.02
            and abs(chosen - latest) < abs(chosen - calibrated)
        )
        trials.append(
            RollingLogForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                stale_window_probability=stale,
                pooled_history_probability=pooled,
                latest_window_probability=latest,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                stale_window_miss=stale_window_miss,
                pooled_history_miss=pooled_history_miss,
                latest_window_miss=latest_window_miss,
                raw_response=response,
            )
        )
    return summarize_rolling_log_forecast_trials(agent.name, trials)


def run_forecast_rolling_log_noisy_game(
    agent: Agent,
    cases: list[RollingLogCalibrationCase] | None = None,
) -> dict:
    cases = cases or NOISY_ROLLING_LOG_CALIBRATION_CASES
    trials: list[RollingLogForecastTrial] = []
    for case in cases:
        calibrated = rolling_log_calibrated_probability(case)
        stale = stale_rolling_log_probability(case)
        pooled = pooled_rolling_log_probability(case)
        latest = latest_rolling_log_probability(case)
        response = agent.complete(FORECAST_SYSTEM, _rolling_log_noisy_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.08
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        stale_window_miss = (
            chosen is not None
            and abs(stale - calibrated) >= 0.05
            and abs(chosen - stale) < abs(chosen - calibrated)
        )
        pooled_history_miss = (
            chosen is not None
            and abs(pooled - calibrated) >= 0.03
            and abs(chosen - pooled) < abs(chosen - calibrated)
        )
        latest_window_miss = (
            chosen is not None
            and abs(latest - calibrated) >= 0.02
            and abs(chosen - latest) < abs(chosen - calibrated)
        )
        trials.append(
            RollingLogForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                stale_window_probability=stale,
                pooled_history_probability=pooled,
                latest_window_probability=latest,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                stale_window_miss=stale_window_miss,
                pooled_history_miss=pooled_history_miss,
                latest_window_miss=latest_window_miss,
                raw_response=response,
            )
        )
    return summarize_rolling_log_forecast_trials(
        agent.name,
        trials,
        task_name="forecast_rolling_log_noisy",
    )


def run_forecast_event_log_calibration_game(
    agent: Agent,
    cases: list[EventLogCalibrationCase] | None = None,
) -> dict:
    cases = cases or EVENT_LOG_CALIBRATION_CASES
    trials: list[EventLogForecastTrial] = []
    for case in cases:
        calibrated = event_log_calibrated_probability(case)
        stale = stale_event_log_probability(case)
        pooled = pooled_event_log_probability(case)
        latest = latest_event_log_probability(case)
        response = agent.complete(FORECAST_SYSTEM, _event_log_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.08
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        stale_window_miss = (
            chosen is not None
            and abs(stale - calibrated) >= 0.05
            and abs(chosen - stale) < abs(chosen - calibrated)
        )
        pooled_history_miss = (
            chosen is not None
            and abs(pooled - calibrated) >= 0.03
            and abs(chosen - pooled) < abs(chosen - calibrated)
        )
        latest_window_miss = (
            chosen is not None
            and abs(latest - calibrated) >= 0.02
            and abs(chosen - latest) < abs(chosen - calibrated)
        )
        trials.append(
            EventLogForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                stale_window_probability=stale,
                pooled_history_probability=pooled,
                latest_window_probability=latest,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                stale_window_miss=stale_window_miss,
                pooled_history_miss=pooled_history_miss,
                latest_window_miss=latest_window_miss,
                raw_response=response,
            )
        )
    return summarize_event_log_forecast_trials(agent.name, trials)


def run_forecast_operational_log_calibration_game(
    agent: Agent,
    cases: list[OperationalLogCalibrationCase] | None = None,
) -> dict:
    cases = cases or OPERATIONAL_LOG_CALIBRATION_CASES
    trials: list[OperationalLogForecastTrial] = []
    for case in cases:
        calibrated = operational_log_calibrated_probability(case)
        stale = stale_operational_log_probability(case)
        pooled = pooled_operational_log_probability(case)
        latest = latest_operational_log_probability(case)
        policy_blind = policy_blind_operational_log_probability(case)
        route_blind = route_blind_operational_log_probability(case)
        response = agent.complete(FORECAST_SYSTEM, _operational_log_prompt(case))
        parsed = parse_float("FINAL_PROBABILITY", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        raw_score_miss = (
            chosen is not None
            and abs(case.raw_model_probability - calibrated) >= 0.08
            and abs(chosen - case.raw_model_probability) < abs(chosen - calibrated)
        )
        stale_window_miss = (
            chosen is not None
            and abs(stale - calibrated) >= 0.04
            and abs(chosen - stale) < abs(chosen - calibrated)
        )
        pooled_history_miss = (
            chosen is not None
            and abs(pooled - calibrated) >= 0.03
            and abs(chosen - pooled) < abs(chosen - calibrated)
        )
        latest_window_miss = (
            chosen is not None
            and abs(latest - calibrated) >= 0.02
            and abs(chosen - latest) < abs(chosen - calibrated)
        )
        policy_blind_miss = (
            chosen is not None
            and abs(policy_blind - calibrated) >= 0.03
            and abs(chosen - policy_blind) < abs(chosen - calibrated)
        )
        route_blind_miss = (
            chosen is not None
            and abs(route_blind - calibrated) >= 0.03
            and abs(chosen - route_blind) < abs(chosen - calibrated)
        )
        trials.append(
            OperationalLogForecastTrial(
                case=case,
                calibrated_probability=calibrated,
                raw_model_probability=case.raw_model_probability,
                stale_window_probability=stale,
                pooled_history_probability=pooled,
                latest_window_probability=latest,
                policy_blind_probability=policy_blind,
                route_blind_probability=route_blind,
                chosen_probability=chosen,
                expected_brier_regret=expected_brier_regret(calibrated, chosen)
                if chosen is not None
                else None,
                probability_error=abs(chosen - calibrated) if chosen is not None else None,
                raw_score_miss=raw_score_miss,
                stale_window_miss=stale_window_miss,
                pooled_history_miss=pooled_history_miss,
                latest_window_miss=latest_window_miss,
                policy_blind_miss=policy_blind_miss,
                route_blind_miss=route_blind_miss,
                raw_response=response,
            )
        )
    return summarize_operational_log_forecast_trials(agent.name, trials)


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


def summarize_shift_forecast_trials(
    agent_name: str,
    trials: list[ShiftForecastTrial],
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    raw_shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.08
    ]
    source_shifted = [
        trial
        for trial in trials
        if abs(trial.source_curve_probability - trial.calibrated_probability) >= 0.05
    ]
    bridge_shifted = [
        trial
        for trial in trials
        if abs(trial.nearest_bridge_probability - trial.calibrated_probability) >= 0.03
    ]
    return {
        "task": "forecast_shift_calibration",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in raw_shifted) / len(raw_shifted)
            if raw_shifted
            else 0.0
        ),
        "source_curve_miss_rate": (
            sum(trial.source_curve_miss for trial in source_shifted) / len(source_shifted)
            if source_shifted
            else 0.0
        ),
        "nearest_bridge_miss_rate": (
            sum(trial.nearest_bridge_miss for trial in bridge_shifted) / len(bridge_shifted)
            if bridge_shifted
            else 0.0
        ),
        "trials": [_shift_trial_json(trial) for trial in trials],
    }


def summarize_rolling_forecast_trials(
    agent_name: str,
    trials: list[RollingForecastTrial],
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    raw_shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.08
    ]
    stale_shifted = [
        trial
        for trial in trials
        if abs(trial.stale_window_probability - trial.calibrated_probability) >= 0.05
    ]
    pooled_shifted = [
        trial
        for trial in trials
        if abs(trial.pooled_history_probability - trial.calibrated_probability) >= 0.03
    ]
    return {
        "task": "forecast_rolling_calibration",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in raw_shifted) / len(raw_shifted)
            if raw_shifted
            else 0.0
        ),
        "stale_window_miss_rate": (
            sum(trial.stale_window_miss for trial in stale_shifted) / len(stale_shifted)
            if stale_shifted
            else 0.0
        ),
        "pooled_history_miss_rate": (
            sum(trial.pooled_history_miss for trial in pooled_shifted) / len(pooled_shifted)
            if pooled_shifted
            else 0.0
        ),
        "trials": [_rolling_trial_json(trial) for trial in trials],
    }


def summarize_rolling_log_forecast_trials(
    agent_name: str,
    trials: list[RollingLogForecastTrial],
    *,
    task_name: str = "forecast_rolling_log_calibration",
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    raw_shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.08
    ]
    stale_shifted = [
        trial
        for trial in trials
        if abs(trial.stale_window_probability - trial.calibrated_probability) >= 0.05
    ]
    pooled_shifted = [
        trial
        for trial in trials
        if abs(trial.pooled_history_probability - trial.calibrated_probability) >= 0.03
    ]
    latest_shifted = [
        trial
        for trial in trials
        if abs(trial.latest_window_probability - trial.calibrated_probability) >= 0.02
    ]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in raw_shifted) / len(raw_shifted)
            if raw_shifted
            else 0.0
        ),
        "stale_window_miss_rate": (
            sum(trial.stale_window_miss for trial in stale_shifted) / len(stale_shifted)
            if stale_shifted
            else 0.0
        ),
        "pooled_history_miss_rate": (
            sum(trial.pooled_history_miss for trial in pooled_shifted) / len(pooled_shifted)
            if pooled_shifted
            else 0.0
        ),
        "latest_window_miss_rate": (
            sum(trial.latest_window_miss for trial in latest_shifted) / len(latest_shifted)
            if latest_shifted
            else 0.0
        ),
        "trials": [_rolling_log_trial_json(trial) for trial in trials],
    }


def summarize_event_log_forecast_trials(
    agent_name: str,
    trials: list[EventLogForecastTrial],
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    raw_shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.08
    ]
    stale_shifted = [
        trial
        for trial in trials
        if abs(trial.stale_window_probability - trial.calibrated_probability) >= 0.05
    ]
    pooled_shifted = [
        trial
        for trial in trials
        if abs(trial.pooled_history_probability - trial.calibrated_probability) >= 0.03
    ]
    latest_shifted = [
        trial
        for trial in trials
        if abs(trial.latest_window_probability - trial.calibrated_probability) >= 0.02
    ]
    return {
        "task": "forecast_event_log_calibration",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in raw_shifted) / len(raw_shifted)
            if raw_shifted
            else 0.0
        ),
        "stale_window_miss_rate": (
            sum(trial.stale_window_miss for trial in stale_shifted) / len(stale_shifted)
            if stale_shifted
            else 0.0
        ),
        "pooled_history_miss_rate": (
            sum(trial.pooled_history_miss for trial in pooled_shifted) / len(pooled_shifted)
            if pooled_shifted
            else 0.0
        ),
        "latest_window_miss_rate": (
            sum(trial.latest_window_miss for trial in latest_shifted) / len(latest_shifted)
            if latest_shifted
            else 0.0
        ),
        "trials": [_event_log_trial_json(trial) for trial in trials],
    }


def summarize_operational_log_forecast_trials(
    agent_name: str,
    trials: list[OperationalLogForecastTrial],
) -> dict:
    regrets = [
        trial.expected_brier_regret
        for trial in trials
        if trial.expected_brier_regret is not None
    ]
    errors = [trial.probability_error for trial in trials if trial.probability_error is not None]
    raw_shifted = [
        trial
        for trial in trials
        if abs(trial.raw_model_probability - trial.calibrated_probability) >= 0.08
    ]
    stale_shifted = [
        trial
        for trial in trials
        if abs(trial.stale_window_probability - trial.calibrated_probability) >= 0.04
    ]
    pooled_shifted = [
        trial
        for trial in trials
        if abs(trial.pooled_history_probability - trial.calibrated_probability) >= 0.03
    ]
    latest_shifted = [
        trial
        for trial in trials
        if abs(trial.latest_window_probability - trial.calibrated_probability) >= 0.02
    ]
    policy_shifted = [
        trial
        for trial in trials
        if abs(trial.policy_blind_probability - trial.calibrated_probability) >= 0.03
    ]
    route_shifted = [
        trial
        for trial in trials
        if abs(trial.route_blind_probability - trial.calibrated_probability) >= 0.03
    ]
    return {
        "task": "forecast_operational_log_calibration",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_brier_regret": mean(regrets),
        "mean_expected_brier_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_probability_error": mean(errors),
        "raw_score_miss_rate": (
            sum(trial.raw_score_miss for trial in raw_shifted) / len(raw_shifted)
            if raw_shifted
            else 0.0
        ),
        "stale_window_miss_rate": (
            sum(trial.stale_window_miss for trial in stale_shifted) / len(stale_shifted)
            if stale_shifted
            else 0.0
        ),
        "pooled_history_miss_rate": (
            sum(trial.pooled_history_miss for trial in pooled_shifted) / len(pooled_shifted)
            if pooled_shifted
            else 0.0
        ),
        "latest_window_miss_rate": (
            sum(trial.latest_window_miss for trial in latest_shifted) / len(latest_shifted)
            if latest_shifted
            else 0.0
        ),
        "policy_blind_miss_rate": (
            sum(trial.policy_blind_miss for trial in policy_shifted) / len(policy_shifted)
            if policy_shifted
            else 0.0
        ),
        "route_blind_miss_rate": (
            sum(trial.route_blind_miss for trial in route_shifted) / len(route_shifted)
            if route_shifted
            else 0.0
        ),
        "trials": [_operational_log_trial_json(trial) for trial in trials],
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


def _curve_noisy_prompt(case: ForecastCurveCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"base_rate={case.global_base_rate:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        "Historical holdout calibration slices from the shifted segment:",
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
            "Some slices are sparse and visibly noisy. The global baseline is a "
            "stabilizing reference with the listed prior-equivalent strength, not "
            "a replacement for the shifted-segment evidence.",
            "Estimate the held-out event probability for the next item at the raw "
            "score above. Use the neighboring calibration pattern while accounting "
            "for sample size; avoid treating one noisy nearby row or the raw score "
            "itself as decisive.",
        ]
    )
    return "\n".join(lines)


def _curve_natural_prompt(case: ForecastCurveCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"base_rate={case.global_base_rate:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        "Recent calibration review for comparable held-out items:",
    ]
    for bin_ in case.bins:
        lines.append(
            f"  slice={bin_.bin_id} "
            f"score_center={bin_.raw_mean_probability:.4f} "
            f"events={bin_.observed_event_count} "
            f"total={bin_.observed_total}"
        )
    lines.extend(
        [
            "Rows summarize historical outcomes near each score center. Some rows "
            "are based on many items and some are thin slices.",
            "Give the best probability for the target event on the next comparable "
            "held-out item at the raw model probability above. Treat the raw score "
            "as a signal to calibrate, not as the final answer.",
        ]
    )
    return "\n".join(lines)


def _shift_prompt(case: ShiftCalibrationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"source_base_rate={case.source_base_rate:.4f}",
        f"source_prior_strength={case.source_prior_strength:.1f}",
        f"bridge_prior_strength={case.bridge_prior_strength:.1f}",
        "Source-cohort review rows from the model's original deployment setting:",
    ]
    for bin_ in case.source_bins:
        lines.append(
            f"  source_bin={bin_.bin_id} "
            f"score_center={bin_.raw_mean_probability:.4f} "
            f"events={bin_.observed_event_count} "
            f"total={bin_.observed_total}"
        )
    lines.append(
        "Small target-cohort bridge sample scored by the same model after deployment moved:"
    )
    for bin_ in case.bridge_bins:
        lines.append(
            f"  target_bridge={bin_.bin_id} "
            f"score_center={bin_.raw_mean_probability:.4f} "
            f"events={bin_.observed_event_count} "
            f"total={bin_.observed_total}"
        )
    lines.extend(
        [
            "The source rows show the original score-to-outcome pattern. The bridge rows "
            "show how the target cohort is locally above or below that source pattern.",
            "Use the bridge sample as a local cohort adjustment around the target raw "
            "score, while stabilizing thin bridge rows against the source pattern.",
            "Give the best event probability for the next target-cohort item at the "
            "raw model probability above.",
        ]
    )
    return "\n".join(lines)


def _rolling_prompt(case: RollingCalibrationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        "Rolling calibration windows for the current deployment slice:",
    ]
    for period in case.periods:
        lines.append(
            f"rolling_period={period.period_id} recency_weight={period.recency_weight:.4f}"
        )
        for bin_ in period.bins:
            lines.append(
                f"  period_bin={bin_.bin_id} "
                f"score_center={bin_.raw_mean_probability:.4f} "
                f"events={bin_.observed_event_count} "
                f"total={bin_.observed_total}"
            )
    lines.extend(
        [
            "Rows summarize outcomes near each score center in successive windows. "
            "Recent windows carry more local evidence, but each row should still be "
            "stabilized toward the global base rate according to prior_strength.",
            "Estimate the event probability for the next item at the raw model "
            "probability above. Do not assume the raw score is already calibrated, "
            "and do not ignore the time-local direction of the calibration windows.",
        ]
    )
    return "\n".join(lines)


def _rolling_log_prompt(case: RollingLogCalibrationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        f"recency_half_life_days={case.recency_half_life_days:.1f}",
        "Outcome-log excerpts from scored cohorts before the target deployment day:",
    ]
    for period in case.periods:
        lines.append(
            f"outcome_batch={period.period_id} "
            f"days_before_target_midpoint={period.days_before_target_midpoint:.1f}"
        )
        for bin_ in period.bins:
            lines.append(
                f"  outcome_slice={bin_.bin_id} "
                f"score_center={bin_.raw_mean_probability:.4f} "
                f"events={bin_.observed_event_count} "
                f"total={bin_.observed_total}"
            )
    lines.extend(
        [
            "Each batch summarizes outcomes near the listed score centers. The "
            "operating environment has been drifting, so cohorts closer to the "
            "target day are more representative, while older cohorts still "
            "stabilize noisy recent rows.",
            "The global base rate is a stabilizing prior with the listed equivalent "
            "sample strength. Estimate the event probability for the next item at "
            "the raw score above; do not treat all dated batches as exchangeable, "
            "and do not use only the newest or oldest batch.",
        ]
    )
    return "\n".join(lines)


def _review_cadence_label(case: RollingLogCalibrationCase) -> str:
    half_life = case.recency_half_life_days
    if half_life <= 22:
        return "biweekly"
    if half_life <= 38:
        return "monthly"
    if half_life <= 55:
        return "six_week"
    return "quarterly"


def _rolling_log_noisy_prompt(case: RollingLogCalibrationCase) -> str:
    cadence = _review_cadence_label(case)
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        f"review_cadence={cadence}",
        "Uneven outcome-log excerpts from prior scored cohorts:",
    ]
    for period in case.periods:
        lines.append(
            f"cohort_review={period.period_id} "
            f"age_days={period.days_before_target_midpoint:.1f}"
        )
        for bin_ in period.bins:
            lines.append(
                f"  score_band={bin_.bin_id} "
                f"score_center={bin_.raw_mean_probability:.4f} "
                f"events={bin_.observed_event_count} "
                f"reviewed={bin_.observed_total}"
            )
    lines.extend(
        [
            "The operating environment has been moving across review cycles. "
            "Older cohorts should not be discarded, but they are less "
            "representative than closer cohorts once the process has shifted.",
            "Some recent score bands are thin and lumpy. Stabilize them against "
            "the global reference and nearby dated evidence instead of blindly "
            "using only the newest row.",
            "Estimate the event probability for the next item at the raw score "
            "above. Do not treat all dated cohorts as exchangeable, and do not "
            "assume the raw score is already calibrated.",
        ]
    )
    return "\n".join(lines)


def _event_log_prompt(case: EventLogCalibrationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        f"review_cadence={_review_cadence_label_for_half_life(case.recency_half_life_days)}",
        "Dated scored-record log for nearby historical items:",
    ]
    for entry in case.entries:
        outcome = "event" if entry.event_observed else "no_event"
        lines.append(
            f"event_log_item={entry.entry_id} "
            f"age_days={entry.days_before_target:.1f} "
            f"score={entry.raw_model_probability:.4f} "
            f"outcome={outcome}"
        )
    lines.extend(
        [
            "Use records with scores near the target raw probability as more "
            "comparable than far-away scores. The process has drifted over time, "
            "so more recent comparable records are more informative, but thin "
            "recent logs should be stabilized against the global reference and "
            "older nearby records.",
            "Estimate the event probability for the next item at the raw score "
            "above. Do not simply count all records equally, use only the newest "
            "records, or reuse the raw model score as the final probability.",
        ]
    )
    return "\n".join(lines)


def _operational_log_prompt(case: OperationalLogCalibrationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"target_event={case.target_event}",
        f"raw_model_probability={case.raw_model_probability:.4f}",
        f"global_base_rate={case.global_base_rate:.4f}",
        f"prior_strength={case.prior_strength:.1f}",
        f"review_cadence={_review_cadence_label_for_half_life(case.recency_half_life_days)}",
        f"current_policy={case.current_policy}",
        f"current_route={case.current_route}",
        "Dated scored operational record log:",
    ]
    for entry in case.entries:
        outcome = "event" if entry.event_observed else "no_event"
        lines.append(
            f"operational_log_item={entry.entry_id} "
            f"age_days={entry.days_before_target:.1f} "
            f"score={entry.raw_model_probability:.4f} "
            f"policy={entry.policy} "
            f"route={entry.route} "
            f"outcome={outcome}"
        )
    lines.extend(
        [
            "Use records with scores near the target raw probability as more "
            "comparable than far-away scores. The process has drifted over time, "
            "so more recent comparable records are more informative, but thin "
            "recent logs should be stabilized against the global reference and "
            "older nearby records.",
            "Operational comparability also matters: records from the current "
            "policy and current route are the closest reference class. Same-score "
            "records from a different policy or route can be misleading even when "
            "they are recent.",
            "Estimate the event probability for the next item at the raw score, "
            "current policy, and current route above. Do not simply pool all "
            "history, use only the newest records, ignore policy/route context, "
            "or reuse the raw model score as the final probability.",
        ]
    )
    return "\n".join(lines)


def _review_cadence_label_for_half_life(half_life: float) -> str:
    if half_life <= 22:
        return "biweekly"
    if half_life <= 38:
        return "monthly"
    if half_life <= 55:
        return "six_week"
    return "quarterly"


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


def _shift_trial_json(trial: ShiftForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _rolling_trial_json(trial: RollingForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _rolling_log_trial_json(trial: RollingLogForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _event_log_trial_json(trial: EventLogForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _operational_log_trial_json(trial: OperationalLogForecastTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
