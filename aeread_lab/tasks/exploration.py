from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


EXPLORATION_SYSTEM = (
    "TASK: exploration_action\n"
    "Choose the first action for this unknown environment. Return one final line only: "
    "FINAL_ACTION: <SAMPLE_arm_id or DEPLOY_arm_id>."
)


@dataclass(frozen=True)
class ArmState:
    payoff: float
    probability: float


@dataclass(frozen=True)
class Arm:
    arm_id: str
    states: tuple[ArmState, ...]


@dataclass(frozen=True)
class ExplorationCase:
    key: str
    real_case: str
    sample_cost: float
    deployment_units: int
    arms: tuple[Arm, ...]


@dataclass
class ExplorationTrial:
    case: ExplorationCase
    oracle_action: str
    exploit_action: str
    chosen_action: str | None
    expected_value_gap: float | None
    correct: bool
    raw_response: str


DEFAULT_CASES = [
    ExplorationCase(
        key="new_supplier_pilot",
        real_case="unknown supplier quality before a large procurement rollout",
        sample_cost=8.0,
        deployment_units=10,
        arms=(
            Arm("safe_incumbent", (ArmState(58.0, 1.0),)),
            Arm("new_supplier", (ArmState(95.0, 0.42), ArmState(25.0, 0.58))),
        ),
    ),
    ExplorationCase(
        key="pricing_channel_test",
        real_case="whether to pilot an uncertain acquisition channel before scaling",
        sample_cost=6.0,
        deployment_units=12,
        arms=(
            Arm("known_search", (ArmState(44.0, 1.0),)),
            Arm("creator_channel", (ArmState(88.0, 0.35), ArmState(18.0, 0.65))),
        ),
    ),
    ExplorationCase(
        key="low_value_info",
        real_case="small rollout where exploration cost dominates value of information",
        sample_cost=20.0,
        deployment_units=2,
        arms=(
            Arm("known_vendor", (ArmState(50.0, 1.0),)),
            Arm("uncertain_vendor", (ArmState(80.0, 0.45), ArmState(10.0, 0.55))),
        ),
    ),
    ExplorationCase(
        key="risky_breakthrough",
        real_case="high-scale product launch where a noisy pilot can reveal a breakthrough segment",
        sample_cost=10.0,
        deployment_units=25,
        arms=(
            Arm("standard_segment", (ArmState(38.0, 1.0),)),
            Arm("breakthrough_segment", (ArmState(110.0, 0.25), ArmState(5.0, 0.75))),
        ),
    ),
]


def arm_expected_payoff(arm: Arm) -> float:
    return sum(state.payoff * state.probability for state in arm.states)


def deploy_value(case: ExplorationCase, arm: Arm) -> float:
    return case.deployment_units * arm_expected_payoff(arm)


def sample_value(case: ExplorationCase, arm: Arm) -> float:
    other_arms = [candidate for candidate in case.arms if candidate.arm_id != arm.arm_id]
    value = -case.sample_cost
    for state in arm.states:
        best_after_sample = max(
            [case.deployment_units * state.payoff]
            + [deploy_value(case, other) for other in other_arms]
        )
        value += state.probability * best_after_sample
    return value


def action_values(case: ExplorationCase) -> dict[str, float]:
    values: dict[str, float] = {}
    for arm in case.arms:
        values[f"DEPLOY_{arm.arm_id}"] = deploy_value(case, arm)
        if len(arm.states) > 1:
            values[f"SAMPLE_{arm.arm_id}"] = sample_value(case, arm)
    return values


def oracle_action(case: ExplorationCase) -> str:
    values = action_values(case)
    return max(values, key=values.get)


def exploit_action(case: ExplorationCase) -> str:
    return max((f"DEPLOY_{arm.arm_id}" for arm in case.arms), key=lambda action: action_values(case)[action])


def run_exploration_game(agent: Agent, cases: list[ExplorationCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[ExplorationTrial] = []
    for case in cases:
        values = action_values(case)
        oracle = oracle_action(case)
        exploit = exploit_action(case)
        response = agent.complete(EXPLORATION_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_ACTION", response)
        chosen = chosen if chosen in values else None
        gap = values[oracle] - values[chosen] if chosen is not None else None
        trials.append(
            ExplorationTrial(
                case=case,
                oracle_action=oracle,
                exploit_action=exploit,
                chosen_action=chosen,
                expected_value_gap=gap,
                correct=chosen == oracle,
                raw_response=response,
            )
        )
    return summarize_exploration_trials(agent.name, trials)


def summarize_exploration_trials(agent_name: str, trials: list[ExplorationTrial]) -> dict:
    gaps = [trial.expected_value_gap for trial in trials if trial.expected_value_gap is not None]
    exploration_required = [trial for trial in trials if trial.oracle_action.startswith("SAMPLE_")]
    missed = sum(
        trial.chosen_action is not None and not trial.chosen_action.startswith("SAMPLE_")
        for trial in exploration_required
    )
    return {
        "task": "exploration",
        "agent": agent_name,
        "n_trials": len(trials),
        "accuracy": sum(trial.correct for trial in trials) / len(trials) if trials else 0.0,
        "mean_expected_value_gap": mean(gaps),
        "mean_expected_value_gap_ci95": bootstrap_mean_ci(gaps),
        "exploration_miss_rate": missed / len(exploration_required) if exploration_required else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: ExplorationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"sample_cost={case.sample_cost:.2f}",
        f"deployment_units={case.deployment_units}",
        "You may either DEPLOY an arm immediately for all units, or SAMPLE one uncertain arm first.",
        "A sample reveals that arm's true payoff state before deployment; after sampling, deploy the best known arm.",
        "Arms:",
    ]
    for arm in case.arms:
        states = ",".join(f"{state.payoff:.2f}@{state.probability:.4f}" for state in arm.states)
        lines.append(f"  arm_id={arm.arm_id} states={states}")
    lines.append("Choose the first action that maximizes expected total payoff net of sample cost.")
    return "\n".join(lines)


def _trial_json(trial: ExplorationTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
