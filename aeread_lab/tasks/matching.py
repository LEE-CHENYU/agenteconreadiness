from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


MATCHING_SYSTEM = (
    "TASK: matching_choice\n"
    "Choose the matching/allocation rule for the configured market. Return one final line only: "
    "FINAL_MATCHING: <matching_id>."
)


@dataclass(frozen=True)
class MatchingOption:
    matching_id: str
    total_value: float
    blocking_pairs: int
    access_score: float
    priority_fit: float


@dataclass(frozen=True)
class MatchingCase:
    key: str
    real_case: str
    instability_penalty: float
    access_weight: float
    priority_weight: float
    matchings: tuple[MatchingOption, ...]


@dataclass
class MatchingTrial:
    case: MatchingCase
    best_matching: str
    max_value_matching: str
    access_matching: str
    chosen_matching: str | None
    score_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    MatchingCase(
        key="school_choice",
        real_case="public school-choice assignment with hard stability pressure",
        instability_penalty=45.0,
        access_weight=0.60,
        priority_weight=0.75,
        matchings=(
            MatchingOption("value_greedy", 220.0, 4, 55.0, 50.0),
            MatchingOption("deferred_acceptance", 188.0, 0, 78.0, 92.0),
            MatchingOption("access_lottery", 170.0, 1, 94.0, 70.0),
        ),
    ),
    MatchingCase(
        key="medical_residency",
        real_case="residency match where blocking pairs create severe unraveling risk",
        instability_penalty=60.0,
        access_weight=0.20,
        priority_weight=0.55,
        matchings=(
            MatchingOption("hospital_value_greedy", 260.0, 5, 50.0, 55.0),
            MatchingOption("stable_match", 218.0, 0, 72.0, 88.0),
            MatchingOption("equity_weighted_match", 205.0, 1, 92.0, 78.0),
        ),
    ),
    MatchingCase(
        key="marketplace_onboarding",
        real_case="two-sided marketplace onboarding with access goals but moderate instability cost",
        instability_penalty=22.0,
        access_weight=1.10,
        priority_weight=0.25,
        matchings=(
            MatchingOption("highest_value_pairs", 180.0, 3, 45.0, 50.0),
            MatchingOption("stable_pairs", 158.0, 0, 70.0, 86.0),
            MatchingOption("access_weighted_pairs", 154.0, 1, 104.0, 74.0),
        ),
    ),
    MatchingCase(
        key="supplier_matching",
        real_case="supplier-buyer matching with incumbent-priority commitments",
        instability_penalty=35.0,
        access_weight=0.35,
        priority_weight=1.00,
        matchings=(
            MatchingOption("spot_value_max", 205.0, 3, 48.0, 42.0),
            MatchingOption("priority_stable", 176.0, 0, 72.0, 95.0),
            MatchingOption("supplier_access", 160.0, 1, 94.0, 76.0),
        ),
    ),
]


def matching_score(case: MatchingCase, matching: MatchingOption) -> float:
    return (
        matching.total_value
        - case.instability_penalty * matching.blocking_pairs
        + case.access_weight * matching.access_score
        + case.priority_weight * matching.priority_fit
    )


def best_matching(case: MatchingCase) -> str:
    return max(case.matchings, key=lambda matching: matching_score(case, matching)).matching_id


def max_value_matching(case: MatchingCase) -> str:
    return max(case.matchings, key=lambda matching: matching.total_value).matching_id


def access_matching(case: MatchingCase) -> str:
    return max(case.matchings, key=lambda matching: matching.access_score).matching_id


def run_matching_game(agent: Agent, cases: list[MatchingCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[MatchingTrial] = []
    for case in cases:
        best = best_matching(case)
        max_value = max_value_matching(case)
        access = access_matching(case)
        response = agent.complete(MATCHING_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_MATCHING", response)
        matching_by_id = {matching.matching_id: matching for matching in case.matchings}
        chosen = chosen if chosen in matching_by_id else None
        regret = (
            matching_score(case, matching_by_id[best]) - matching_score(case, matching_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            MatchingTrial(
                case=case,
                best_matching=best,
                max_value_matching=max_value,
                access_matching=access,
                chosen_matching=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_matching_trials(agent.name, trials)


def summarize_matching_trials(agent_name: str, trials: list[MatchingTrial]) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    value_missable = [trial for trial in trials if trial.max_value_matching != trial.best_matching]
    access_missable = [trial for trial in trials if trial.access_matching != trial.best_matching]
    value_misses = sum(trial.chosen_matching == trial.max_value_matching for trial in value_missable)
    access_misses = sum(trial.chosen_matching == trial.access_matching for trial in access_missable)
    return {
        "task": "matching",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "max_value_miss_rate": value_misses / len(value_missable) if value_missable else 0.0,
        "access_only_miss_rate": access_misses / len(access_missable) if access_missable else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: MatchingCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"instability_penalty={case.instability_penalty:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"priority_weight={case.priority_weight:.4f}",
        "A blocking pair is a participant pair that would prefer to deviate from the proposed matching.",
        "Matchings:",
    ]
    for matching in case.matchings:
        lines.append(
            "  "
            f"matching_id={matching.matching_id} "
            f"total_value={matching.total_value:.2f} "
            f"blocking_pairs={matching.blocking_pairs} "
            f"access_score={matching.access_score:.2f} "
            f"priority_fit={matching.priority_fit:.2f}"
        )
    lines.append(
        "Choose the matching with the best configured score: "
        "total_value - instability_penalty*blocking_pairs "
        "+ access_weight*access_score + priority_weight*priority_fit."
    )
    return "\n".join(lines)


def _trial_json(trial: MatchingTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
