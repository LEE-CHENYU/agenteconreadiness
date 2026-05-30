from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


MECHANISM_SYSTEM = (
    "TASK: mechanism_choice\n"
    "Choose the mechanism for the configured principal. Return one final line only: "
    "FINAL_MECHANISM: <mechanism_id>."
)

MECHANISM_REPEATED_SYSTEM = (
    "TASK: mechanism_repeated_choice\n"
    "Choose the mechanism for a repeated market setting. Return one final line only: "
    "FINAL_MECHANISM: <mechanism_id>."
)


@dataclass(frozen=True)
class IncentiveCheck:
    type_id: str
    probability: float
    truthful_utility: float
    best_deviation_utility: float


@dataclass(frozen=True)
class MechanismOption:
    mechanism_id: str
    revenue: float
    welfare: float
    access: float
    strategic_risk: float
    incentive_checks: tuple[IncentiveCheck, ...] = ()


@dataclass(frozen=True)
class MechanismCase:
    key: str
    real_case: str
    revenue_weight: float
    welfare_weight: float
    access_weight: float
    strategic_risk_penalty: float
    mechanisms: tuple[MechanismOption, ...]
    incentive_violation_penalty: float = 0.0


@dataclass
class MechanismTrial:
    case: MechanismCase
    best_mechanism: str
    revenue_mechanism: str
    risk_blind_mechanism: str
    ic_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    incentive_violation: float | None
    raw_response: str


@dataclass(frozen=True)
class RepeatedMechanismOption:
    mechanism_id: str
    first_period_revenue: float
    welfare: float
    access: float
    strategic_risk: float
    retention_rate: float
    manipulation_load: float
    manipulation_growth: float
    review_cost: float


@dataclass(frozen=True)
class RepeatedMechanismCase:
    key: str
    real_case: str
    horizon: int
    revenue_weight: float
    welfare_weight: float
    access_weight: float
    strategic_risk_penalty: float
    manipulation_penalty: float
    mechanisms: tuple[RepeatedMechanismOption, ...]


@dataclass
class RepeatedMechanismTrial:
    case: RepeatedMechanismCase
    best_mechanism: str
    revenue_mechanism: str
    one_period_mechanism: str
    risk_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    MechanismCase(
        key="ad_slot_revenue",
        real_case="ad-slot allocation for a revenue-weighted platform seller",
        revenue_weight=1.0,
        welfare_weight=0.10,
        access_weight=0.0,
        strategic_risk_penalty=0.20,
        mechanisms=(
            MechanismOption("first_price_high_reserve", 118.0, 88.0, 40.0, 22.0),
            MechanismOption("second_price_truthful", 96.0, 120.0, 75.0, 3.0),
            MechanismOption("access_lottery", 50.0, 82.0, 95.0, 10.0),
        ),
    ),
    MechanismCase(
        key="public_grants_access",
        real_case="public grant allocation where access and participation dominate fee revenue",
        revenue_weight=0.0,
        welfare_weight=0.35,
        access_weight=1.20,
        strategic_risk_penalty=0.50,
        mechanisms=(
            MechanismOption("pay_to_rank", 120.0, 88.0, 40.0, 22.0),
            MechanismOption("scored_auction", 74.0, 120.0, 75.0, 3.0),
            MechanismOption("access_lottery", 35.0, 90.0, 94.0, 8.0),
        ),
    ),
    MechanismCase(
        key="platform_truthfulness",
        real_case="marketplace rule where long-run participation depends on truthful bidding",
        revenue_weight=0.80,
        welfare_weight=0.50,
        access_weight=0.20,
        strategic_risk_penalty=2.00,
        mechanisms=(
            MechanismOption("first_price_high_reserve", 130.0, 110.0, 50.0, 60.0),
            MechanismOption("second_price_truthful", 105.0, 124.0, 75.0, 3.0),
            MechanismOption("posted_price_menu", 92.0, 116.0, 86.0, 12.0),
        ),
    ),
    MechanismCase(
        key="small_supplier_procurement",
        real_case="procurement design where supplier diversity matters alongside cost savings",
        revenue_weight=0.40,
        welfare_weight=0.50,
        access_weight=1.00,
        strategic_risk_penalty=0.80,
        mechanisms=(
            MechanismOption("reverse_auction_low_bid", 110.0, 78.0, 32.0, 40.0),
            MechanismOption("quality_scoring_rule", 82.0, 125.0, 82.0, 8.0),
            MechanismOption("set_aside_lottery", 50.0, 90.0, 96.0, 12.0),
        ),
    ),
    MechanismCase(
        key="truthful_creator_market",
        real_case="creator marketplace allocation where strategic quality misreports degrade long-run fit",
        revenue_weight=0.80,
        welfare_weight=0.45,
        access_weight=0.15,
        strategic_risk_penalty=0.40,
        incentive_violation_penalty=6.00,
        mechanisms=(
            MechanismOption(
                "first_price_quality_bid",
                150.0,
                102.0,
                48.0,
                18.0,
                (
                    IncentiveCheck("low_quality", 0.45, 8.0, 20.0),
                    IncentiveCheck("mid_quality", 0.35, 13.0, 24.0),
                    IncentiveCheck("high_quality", 0.20, 19.0, 27.0),
                ),
            ),
            MechanismOption(
                "vcg_quality_score",
                116.0,
                135.0,
                72.0,
                4.0,
                (
                    IncentiveCheck("low_quality", 0.45, 15.0, 15.4),
                    IncentiveCheck("mid_quality", 0.35, 22.0, 22.3),
                    IncentiveCheck("high_quality", 0.20, 31.0, 31.2),
                ),
            ),
            MechanismOption(
                "manual_review_queue",
                88.0,
                126.0,
                90.0,
                6.0,
                (
                    IncentiveCheck("low_quality", 0.45, 13.0, 15.0),
                    IncentiveCheck("mid_quality", 0.35, 19.0, 21.0),
                    IncentiveCheck("high_quality", 0.20, 25.0, 27.5),
                ),
            ),
        ),
    ),
    MechanismCase(
        key="procurement_scoring_truthfulness",
        real_case="procurement scoring rule where vendors can exaggerate delivery reliability",
        revenue_weight=0.50,
        welfare_weight=0.65,
        access_weight=0.35,
        strategic_risk_penalty=0.70,
        incentive_violation_penalty=5.50,
        mechanisms=(
            MechanismOption(
                "lowest_bid_with_self_certification",
                240.0,
                94.0,
                45.0,
                36.0,
                (
                    IncentiveCheck("fragile_vendor", 0.30, 6.0, 21.0),
                    IncentiveCheck("standard_vendor", 0.50, 14.0, 26.0),
                    IncentiveCheck("reliable_vendor", 0.20, 22.0, 29.0),
                ),
            ),
            MechanismOption(
                "audited_score_auction",
                102.0,
                137.0,
                70.0,
                8.0,
                (
                    IncentiveCheck("fragile_vendor", 0.30, 11.0, 11.5),
                    IncentiveCheck("standard_vendor", 0.50, 20.0, 20.4),
                    IncentiveCheck("reliable_vendor", 0.20, 30.0, 30.2),
                ),
            ),
            MechanismOption(
                "access_weighted_lottery",
                76.0,
                120.0,
                94.0,
                10.0,
                (
                    IncentiveCheck("fragile_vendor", 0.30, 10.0, 13.0),
                    IncentiveCheck("standard_vendor", 0.50, 16.0, 18.0),
                    IncentiveCheck("reliable_vendor", 0.20, 24.0, 25.5),
                ),
            ),
        ),
    ),
]


REPEATED_CASES = [
    RepeatedMechanismCase(
        key="creator_market_retention",
        real_case="creator marketplace where aggressive ranking raises first-period revenue but drives creator exit",
        horizon=4,
        revenue_weight=0.90,
        welfare_weight=0.35,
        access_weight=0.20,
        strategic_risk_penalty=0.60,
        manipulation_penalty=8.00,
        mechanisms=(
            RepeatedMechanismOption("extractive_first_price", 160.0, 98.0, 45.0, 18.0, 0.72, 2.0, 2.20, 2.0),
            RepeatedMechanismOption("truthful_score_clock", 118.0, 132.0, 78.0, 4.0, 0.94, 0.6, 1.10, 4.0),
            RepeatedMechanismOption("manual_review_queue", 82.0, 126.0, 92.0, 7.0, 0.90, 0.8, 1.25, 9.0),
        ),
    ),
    RepeatedMechanismCase(
        key="procurement_reliability_repeated",
        real_case="repeated procurement where self-certification attracts low bids but vendor exaggeration compounds",
        horizon=5,
        revenue_weight=0.65,
        welfare_weight=0.60,
        access_weight=0.45,
        strategic_risk_penalty=0.70,
        manipulation_penalty=7.00,
        mechanisms=(
            RepeatedMechanismOption("self_certified_low_bid", 230.0, 90.0, 42.0, 32.0, 0.68, 3.0, 2.00, 1.0),
            RepeatedMechanismOption("audited_dynamic_score", 108.0, 140.0, 72.0, 7.0, 0.95, 0.7, 1.08, 5.0),
            RepeatedMechanismOption("supplier_rotation_lottery", 74.0, 118.0, 96.0, 10.0, 0.93, 0.8, 1.15, 6.0),
        ),
    ),
    RepeatedMechanismCase(
        key="public_grants_repeated_access",
        real_case="public grants platform where repeated participation and access matter more than immediate fees",
        horizon=4,
        revenue_weight=0.15,
        welfare_weight=0.55,
        access_weight=1.10,
        strategic_risk_penalty=0.50,
        manipulation_penalty=5.00,
        mechanisms=(
            RepeatedMechanismOption("pay_to_rank_fast", 150.0, 84.0, 38.0, 24.0, 0.70, 2.5, 1.80, 1.0),
            RepeatedMechanismOption("deliberative_score_rule", 70.0, 128.0, 82.0, 5.0, 0.96, 0.5, 1.10, 6.0),
            RepeatedMechanismOption("rotating_access_lottery", 42.0, 92.0, 98.0, 8.0, 0.97, 0.6, 1.05, 4.0),
        ),
    ),
    RepeatedMechanismCase(
        key="creator_feed_manipulation_growth",
        real_case="creator feed mechanism where engagement manipulation compounds over repeated allocation rounds",
        horizon=5,
        revenue_weight=0.75,
        welfare_weight=0.55,
        access_weight=0.35,
        strategic_risk_penalty=0.40,
        manipulation_penalty=10.00,
        mechanisms=(
            RepeatedMechanismOption("viral_rank_auction", 155.0, 120.0, 62.0, 10.0, 0.93, 1.8, 2.40, 2.0),
            RepeatedMechanismOption("audited_pacing_rule", 112.0, 132.0, 78.0, 5.0, 0.94, 0.5, 1.10, 5.0),
            RepeatedMechanismOption("community_lottery", 72.0, 112.0, 95.0, 6.0, 0.95, 0.4, 1.15, 5.0),
        ),
    ),
]


def incentive_violation(mechanism: MechanismOption) -> float:
    return sum(
        max(0.0, check.best_deviation_utility - check.truthful_utility) * max(0.0, check.probability)
        for check in mechanism.incentive_checks
    )


def mechanism_score(
    case: MechanismCase,
    mechanism: MechanismOption,
    *,
    risk_blind: bool = False,
    ic_blind: bool = False,
) -> float:
    risk_penalty = 0.0 if risk_blind else case.strategic_risk_penalty
    ic_penalty = 0.0 if ic_blind else case.incentive_violation_penalty
    return (
        case.revenue_weight * mechanism.revenue
        + case.welfare_weight * mechanism.welfare
        + case.access_weight * mechanism.access
        - risk_penalty * mechanism.strategic_risk
        - ic_penalty * incentive_violation(mechanism)
    )


def best_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism)).mechanism_id


def revenue_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.revenue).mechanism_id


def risk_blind_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism, risk_blind=True)).mechanism_id


def ic_blind_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism, ic_blind=True)).mechanism_id


def run_mechanism_game(agent: Agent, cases: list[MechanismCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[MechanismTrial] = []
    for case in cases:
        best = best_mechanism(case)
        revenue = revenue_mechanism(case)
        blind = risk_blind_mechanism(case)
        ic_blind = ic_blind_mechanism(case)
        response = agent.complete(MECHANISM_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            mechanism_score(case, mechanism_by_id[best]) - mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            MechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                risk_blind_mechanism=blind,
                ic_blind_mechanism=ic_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                incentive_violation=incentive_violation(mechanism_by_id[chosen]) if chosen is not None else None,
                raw_response=response,
            )
        )
    return summarize_mechanism_trials(agent.name, trials)


def repeated_mechanism_score(
    case: RepeatedMechanismCase,
    mechanism: RepeatedMechanismOption,
    *,
    one_period: bool = False,
    risk_blind: bool = False,
) -> float:
    horizon = 1 if one_period else case.horizon
    total = 0.0
    manipulation_penalty = 0.0 if risk_blind else case.manipulation_penalty
    strategic_risk_penalty = 0.0 if risk_blind else case.strategic_risk_penalty
    for period in range(horizon):
        retention = mechanism.retention_rate**period
        manipulation = mechanism.manipulation_load * (mechanism.manipulation_growth**period)
        total += (
            case.revenue_weight * mechanism.first_period_revenue * retention
            + case.welfare_weight * mechanism.welfare * retention
            + case.access_weight * mechanism.access * retention
            - strategic_risk_penalty * mechanism.strategic_risk
            - manipulation_penalty * manipulation
            - mechanism.review_cost
        )
    return total


def best_repeated_mechanism(case: RepeatedMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: repeated_mechanism_score(case, mechanism),
    ).mechanism_id


def revenue_repeated_mechanism(case: RepeatedMechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.first_period_revenue).mechanism_id


def one_period_mechanism(case: RepeatedMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: repeated_mechanism_score(case, mechanism, one_period=True),
    ).mechanism_id


def risk_blind_repeated_mechanism(case: RepeatedMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: repeated_mechanism_score(case, mechanism, risk_blind=True),
    ).mechanism_id


def run_mechanism_repeated_game(
    agent: Agent,
    cases: list[RepeatedMechanismCase] | None = None,
) -> dict:
    return _run_repeated_mechanism_game(
        agent,
        cases,
        prompt_fn=_repeated_prompt,
        task_name="mechanism_repeated",
    )


def run_mechanism_repeated_natural_game(
    agent: Agent,
    cases: list[RepeatedMechanismCase] | None = None,
) -> dict:
    return _run_repeated_mechanism_game(
        agent,
        cases,
        prompt_fn=_repeated_natural_prompt,
        task_name="mechanism_repeated_natural",
    )


def _run_repeated_mechanism_game(
    agent: Agent,
    cases: list[RepeatedMechanismCase] | None,
    *,
    prompt_fn: Callable[[RepeatedMechanismCase], str],
    task_name: str,
) -> dict:
    cases = cases or REPEATED_CASES
    trials: list[RepeatedMechanismTrial] = []
    for case in cases:
        best = best_repeated_mechanism(case)
        revenue = revenue_repeated_mechanism(case)
        one_period = one_period_mechanism(case)
        risk_blind = risk_blind_repeated_mechanism(case)
        response = agent.complete(MECHANISM_REPEATED_SYSTEM, prompt_fn(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            repeated_mechanism_score(case, mechanism_by_id[best])
            - repeated_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            RepeatedMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                risk_blind_mechanism=risk_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_repeated_mechanism_trials(agent.name, trials, task_name=task_name)


def summarize_mechanism_trials(agent_name: str, trials: list[MechanismTrial]) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    risk_missable = [trial for trial in trials if trial.risk_blind_mechanism != trial.best_mechanism]
    ic_missable = [trial for trial in trials if trial.ic_blind_mechanism != trial.best_mechanism]
    revenue_misses = sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
    risk_misses = sum(trial.chosen_mechanism == trial.risk_blind_mechanism for trial in risk_missable)
    ic_misses = sum(trial.chosen_mechanism == trial.ic_blind_mechanism for trial in ic_missable)
    violations = [trial.incentive_violation for trial in trials if trial.incentive_violation is not None]
    return {
        "task": "mechanism",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": revenue_misses / len(revenue_missable) if revenue_missable else 0.0,
        "risk_blind_miss_rate": risk_misses / len(risk_missable) if risk_missable else 0.0,
        "ic_blind_miss_rate": ic_misses / len(ic_missable) if ic_missable else 0.0,
        "mean_incentive_violation": mean(violations),
        "trials": [_trial_json(trial) for trial in trials],
    }


def summarize_repeated_mechanism_trials(
    agent_name: str,
    trials: list[RepeatedMechanismTrial],
    *,
    task_name: str = "mechanism_repeated",
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    one_period_missable = [
        trial for trial in trials if trial.one_period_mechanism != trial.best_mechanism
    ]
    risk_missable = [trial for trial in trials if trial.risk_blind_mechanism != trial.best_mechanism]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": (
            sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
            / len(revenue_missable)
            if revenue_missable
            else 0.0
        ),
        "one_period_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.one_period_mechanism
                for trial in one_period_missable
            )
            / len(one_period_missable)
            if one_period_missable
            else 0.0
        ),
        "risk_blind_miss_rate": (
            sum(trial.chosen_mechanism == trial.risk_blind_mechanism for trial in risk_missable)
            / len(risk_missable)
            if risk_missable
            else 0.0
        ),
        "trials": [_repeated_trial_json(trial) for trial in trials],
    }


def _prompt(case: MechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"welfare_weight={case.welfare_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"strategic_risk_penalty={case.strategic_risk_penalty:.4f}",
        f"incentive_violation_penalty={case.incentive_violation_penalty:.4f}",
        "Outcomes below account for expected strategic response; incentive checks expose residual misreport gains.",
        "Mechanisms:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"revenue={mechanism.revenue:.2f} "
            f"welfare={mechanism.welfare:.2f} "
            f"access={mechanism.access:.2f} "
            f"strategic_risk={mechanism.strategic_risk:.2f}"
        )
        for check in mechanism.incentive_checks:
            lines.append(
                "    "
                f"ic_check mechanism_id={mechanism.mechanism_id} "
                f"type_id={check.type_id} "
                f"probability={check.probability:.4f} "
                f"truthful_utility={check.truthful_utility:.2f} "
                f"best_deviation_utility={check.best_deviation_utility:.2f}"
            )
    lines.append(
        "Choose the mechanism with the best configured score: "
        "revenue_weight*revenue + welfare_weight*welfare + access_weight*access "
        "- strategic_risk_penalty*strategic_risk "
        "- incentive_violation_penalty*expected_positive_misreport_gain."
    )
    return "\n".join(lines)


def _repeated_prompt(case: RepeatedMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"welfare_weight={case.welfare_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"strategic_risk_penalty={case.strategic_risk_penalty:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Mechanisms:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"first_period_revenue={mechanism.first_period_revenue:.2f} "
            f"welfare={mechanism.welfare:.2f} "
            f"access={mechanism.access:.2f} "
            f"strategic_risk={mechanism.strategic_risk:.2f} "
            f"retention_rate={mechanism.retention_rate:.4f} "
            f"manipulation_load={mechanism.manipulation_load:.2f} "
            f"manipulation_growth={mechanism.manipulation_growth:.4f} "
            f"review_cost={mechanism.review_cost:.2f}"
        )
    lines.append(
        "For each period, retained revenue/welfare/access scale by retention_rate^(period-1), "
        "while manipulation load scales by manipulation_growth^(period-1)."
    )
    lines.append(
        "Choose the mechanism with the highest total configured score across the full horizon, "
        "not just the highest first-period revenue."
    )
    return "\n".join(lines)


def _repeated_natural_prompt(case: RepeatedMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"welfare_weight={case.welfare_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"strategic_risk_penalty={case.strategic_risk_penalty:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Pilot outcomes from candidate rules:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"option_id={mechanism.mechanism_id} "
            f"initial_take={mechanism.first_period_revenue:.2f} "
            f"participant_value={mechanism.welfare:.2f} "
            f"access_reach={mechanism.access:.2f} "
            f"governance_risk={mechanism.strategic_risk:.2f} "
            f"participant_retention={mechanism.retention_rate:.4f} "
            f"gaming_pressure={mechanism.manipulation_load:.2f} "
            f"gaming_acceleration={mechanism.manipulation_growth:.4f} "
            f"oversight_cost={mechanism.review_cost:.2f}"
        )
    lines.extend(
        [
            "Higher participant retention keeps later-round value available.",
            "Gaming pressure that accelerates over repeated use erodes the principal's value.",
            "Pick the rule that should govern the whole repeated program, not the rule "
            "with the largest launch-period take.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: MechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _repeated_trial_json(trial: RepeatedMechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
