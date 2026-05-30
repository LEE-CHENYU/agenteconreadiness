from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


MECHANISM_SYSTEM = (
    "TASK: mechanism_choice\n"
    "Choose the mechanism for the configured principal. Return one final line only: "
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


def _trial_json(trial: MechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
