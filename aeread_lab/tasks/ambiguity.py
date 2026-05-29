from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


AMBIGUITY_SYSTEM = (
    "TASK: ambiguity_action\n"
    "Choose one action under ambiguous probabilities. Return one final line only: "
    "FINAL_ACTION: <action_id>."
)


@dataclass(frozen=True)
class Action:
    action_id: str
    payoffs: tuple[float, ...]


@dataclass(frozen=True)
class Prior:
    prior_id: str
    probabilities: tuple[float, ...]


@dataclass(frozen=True)
class AmbiguityCase:
    key: str
    real_case: str
    state_ids: tuple[str, ...]
    priors: tuple[Prior, ...]
    reference_prior_id: str
    actions: tuple[Action, ...]


@dataclass
class AmbiguityTrial:
    case: AmbiguityCase
    oracle_action: str
    reference_prior_action: str
    chosen_action: str | None
    robust_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    AmbiguityCase(
        key="new_market_entry",
        real_case="market-entry decision where demand probabilities are not identifiable yet",
        state_ids=("weak", "base", "strong"),
        reference_prior_id="analyst_base",
        priors=(
            Prior("analyst_base", (0.20, 0.50, 0.30)),
            Prior("downside", (0.55, 0.35, 0.10)),
            Prior("upside", (0.10, 0.35, 0.55)),
        ),
        actions=(
            Action("safe_pilot", (24.0, 32.0, 38.0)),
            Action("full_launch", (-20.0, 45.0, 90.0)),
            Action("delay", (18.0, 20.0, 22.0)),
        ),
    ),
    AmbiguityCase(
        key="supplier_country_shift",
        real_case="supply-chain shift under ambiguous tariff and disruption probabilities",
        state_ids=("tariff", "normal", "boom"),
        reference_prior_id="consultant_base",
        priors=(
            Prior("consultant_base", (0.15, 0.55, 0.30)),
            Prior("stress", (0.50, 0.40, 0.10)),
            Prior("benign", (0.05, 0.55, 0.40)),
        ),
        actions=(
            Action("dual_source", (28.0, 35.0, 42.0)),
            Action("single_low_cost", (-15.0, 48.0, 82.0)),
            Action("stay_current", (22.0, 28.0, 30.0)),
        ),
    ),
    AmbiguityCase(
        key="capital_project",
        real_case="capital-project choice with deep uncertainty over rate and adoption states",
        state_ids=("tight_credit", "steady", "easy_credit"),
        reference_prior_id="base_case",
        priors=(
            Prior("base_case", (0.20, 0.55, 0.25)),
            Prior("tight", (0.60, 0.30, 0.10)),
            Prior("easy", (0.10, 0.35, 0.55)),
        ),
        actions=(
            Action("modular_build", (35.0, 45.0, 55.0)),
            Action("levered_buildout", (-35.0, 70.0, 130.0)),
            Action("cash_preserve", (30.0, 32.0, 34.0)),
        ),
    ),
]


def expected_value(action: Action, prior: Prior) -> float:
    return sum(payoff * probability for payoff, probability in zip(action.payoffs, prior.probabilities))


def robust_value(case: AmbiguityCase, action: Action) -> float:
    return min(expected_value(action, prior) for prior in case.priors)


def oracle_action(case: AmbiguityCase) -> str:
    return max(case.actions, key=lambda action: robust_value(case, action)).action_id


def reference_prior_action(case: AmbiguityCase) -> str:
    prior = next(prior for prior in case.priors if prior.prior_id == case.reference_prior_id)
    return max(case.actions, key=lambda action: expected_value(action, prior)).action_id


def run_ambiguity_game(agent: Agent, cases: list[AmbiguityCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[AmbiguityTrial] = []
    for case in cases:
        oracle = oracle_action(case)
        reference = reference_prior_action(case)
        response = agent.complete(AMBIGUITY_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_ACTION", response)
        action_by_id = {action.action_id: action for action in case.actions}
        chosen = chosen if chosen in action_by_id else None
        regret = (
            robust_value(case, action_by_id[oracle]) - robust_value(case, action_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            AmbiguityTrial(
                case=case,
                oracle_action=oracle,
                reference_prior_action=reference,
                chosen_action=chosen,
                robust_regret=regret,
                raw_response=response,
            )
        )
    return summarize_ambiguity_trials(agent.name, trials)


def summarize_ambiguity_trials(agent_name: str, trials: list[AmbiguityTrial]) -> dict:
    regrets = [trial.robust_regret for trial in trials if trial.robust_regret is not None]
    missable = [trial for trial in trials if trial.reference_prior_action != trial.oracle_action]
    missed = sum(trial.chosen_action == trial.reference_prior_action for trial in missable)
    return {
        "task": "ambiguity",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_robust_regret": mean(regrets),
        "mean_robust_regret_ci95": bootstrap_mean_ci(regrets),
        "reference_prior_miss_rate": missed / len(missable) if missable else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: AmbiguityCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Probability model is ambiguous: no single prior is authoritative.",
        f"states={','.join(case.state_ids)}",
        f"reference_prior_id={case.reference_prior_id}",
        "Plausible priors:",
    ]
    for prior in case.priors:
        probs = ",".join(f"{state}={probability:.4f}" for state, probability in zip(case.state_ids, prior.probabilities))
        lines.append(f"  prior_id={prior.prior_id} {probs}")
    lines.append("Actions:")
    for action in case.actions:
        payoffs = ",".join(f"{state}={payoff:.2f}" for state, payoff in zip(case.state_ids, action.payoffs))
        lines.append(f"  action_id={action.action_id} {payoffs}")
    lines.extend(
        [
            "Use maxmin expected utility across the plausible priors.",
            "Choose the action with the best worst-case expected value, not the action favored only by the reference prior.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: AmbiguityTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
