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
class MechanismOption:
    mechanism_id: str
    revenue: float
    welfare: float
    access: float
    strategic_risk: float


@dataclass(frozen=True)
class MechanismCase:
    key: str
    real_case: str
    revenue_weight: float
    welfare_weight: float
    access_weight: float
    strategic_risk_penalty: float
    mechanisms: tuple[MechanismOption, ...]


@dataclass
class MechanismTrial:
    case: MechanismCase
    best_mechanism: str
    revenue_mechanism: str
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
]


def mechanism_score(case: MechanismCase, mechanism: MechanismOption, *, risk_blind: bool = False) -> float:
    risk_penalty = 0.0 if risk_blind else case.strategic_risk_penalty
    return (
        case.revenue_weight * mechanism.revenue
        + case.welfare_weight * mechanism.welfare
        + case.access_weight * mechanism.access
        - risk_penalty * mechanism.strategic_risk
    )


def best_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism)).mechanism_id


def revenue_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.revenue).mechanism_id


def risk_blind_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism, risk_blind=True)).mechanism_id


def run_mechanism_game(agent: Agent, cases: list[MechanismCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[MechanismTrial] = []
    for case in cases:
        best = best_mechanism(case)
        revenue = revenue_mechanism(case)
        blind = risk_blind_mechanism(case)
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
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_mechanism_trials(agent.name, trials)


def summarize_mechanism_trials(agent_name: str, trials: list[MechanismTrial]) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    risk_missable = [trial for trial in trials if trial.risk_blind_mechanism != trial.best_mechanism]
    revenue_misses = sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
    risk_misses = sum(trial.chosen_mechanism == trial.risk_blind_mechanism for trial in risk_missable)
    return {
        "task": "mechanism",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": revenue_misses / len(revenue_missable) if revenue_missable else 0.0,
        "risk_blind_miss_rate": risk_misses / len(risk_missable) if risk_missable else 0.0,
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
        "Outcomes below already account for expected strategic response under each mechanism.",
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
    lines.append(
        "Choose the mechanism with the best configured score: "
        "revenue_weight*revenue + welfare_weight*welfare + access_weight*access "
        "- strategic_risk_penalty*strategic_risk."
    )
    return "\n".join(lines)


def _trial_json(trial: MechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
