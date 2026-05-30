from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


EXPERIMENT_SYSTEM = (
    "TASK: experiment_action\n"
    "Choose the first action in an unknown environment with imperfect signals. "
    "Return one final line only: FINAL_ACTION: <DEPLOY_arm_id or EXPERIMENT_experiment_id>."
)


@dataclass(frozen=True)
class ExperimentArm:
    arm_id: str
    low_payoff: float
    high_payoff: float


@dataclass(frozen=True)
class Experiment:
    experiment_id: str
    cost: float
    accuracy: float
    followup_cost: float = 0.0
    followup_accuracy: float = 0.0


@dataclass(frozen=True)
class ExperimentCase:
    key: str
    real_case: str
    deployment_units: int
    high_state_probability: float
    arms: tuple[ExperimentArm, ...]
    experiments: tuple[Experiment, ...]


@dataclass
class ExperimentTrial:
    case: ExperimentCase
    best_action: str
    greedy_action: str
    single_step_action: str
    chosen_action: str | None
    expected_value_gap: float | None
    raw_response: str


DEFAULT_CASES = [
    ExperimentCase(
        key="supplier_certification",
        real_case="choose whether to audit an uncertain supplier before a large rollout",
        deployment_units=12,
        high_state_probability=0.35,
        arms=(
            ExperimentArm("incumbent", 55.0, 55.0),
            ExperimentArm("new_supplier", 20.0, 110.0),
        ),
        experiments=(
            Experiment("cheap_reference_check", 5.0, 0.60),
            Experiment("expert_factory_audit", 35.0, 0.85),
        ),
    ),
    ExperimentCase(
        key="acquisition_channel",
        real_case="decide whether to run a noisy channel test before committing budget",
        deployment_units=10,
        high_state_probability=0.55,
        arms=(
            ExperimentArm("known_search", 45.0, 45.0),
            ExperimentArm("creator_channel", 15.0, 85.0),
        ),
        experiments=(
            Experiment("fast_small_probe", 7.0, 0.62),
            Experiment("controlled_geo_test", 28.0, 0.82),
        ),
    ),
    ExperimentCase(
        key="low_scale_rollout",
        real_case="small rollout where experiment cost can exceed information value",
        deployment_units=2,
        high_state_probability=0.50,
        arms=(
            ExperimentArm("known_vendor", 50.0, 50.0),
            ExperimentArm("uncertain_vendor", 10.0, 90.0),
        ),
        experiments=(
            Experiment("reference_call", 8.0, 0.65),
            Experiment("paid_pilot", 35.0, 0.90),
        ),
    ),
    ExperimentCase(
        key="breakthrough_segment",
        real_case="high-scale launch where a signal can reveal a breakthrough segment",
        deployment_units=30,
        high_state_probability=0.20,
        arms=(
            ExperimentArm("standard_segment", 38.0, 38.0),
            ExperimentArm("breakthrough_segment", 5.0, 140.0),
        ),
        experiments=(
            Experiment("survey_panel", 12.0, 0.58),
            Experiment("live_market_test", 45.0, 0.88),
        ),
    ),
    ExperimentCase(
        key="adaptive_segment_screen",
        real_case="adaptive two-stage market test where a cheap screen can justify a confirmatory pilot",
        deployment_units=20,
        high_state_probability=0.25,
        arms=(
            ExperimentArm("known_segment", 50.0, 50.0),
            ExperimentArm("new_segment", 0.0, 140.0),
        ),
        experiments=(
            Experiment("cheap_screen", 10.0, 0.62, followup_cost=45.0, followup_accuracy=0.90),
            Experiment("direct_pilot", 80.0, 0.86),
        ),
    ),
]


def deploy_value(case: ExperimentCase, arm: ExperimentArm, high_probability: float | None = None) -> float:
    probability = case.high_state_probability if high_probability is None else high_probability
    expected_payoff = probability * arm.high_payoff + (1.0 - probability) * arm.low_payoff
    return case.deployment_units * expected_payoff


def posterior_after_signal(prior_high: float, accuracy: float, *, signal_high: bool) -> tuple[float, float]:
    p_low = 1.0 - prior_high
    if signal_high:
        p_signal = prior_high * accuracy + p_low * (1.0 - accuracy)
        posterior = (prior_high * accuracy) / p_signal if p_signal > 0 else prior_high
    else:
        p_signal = prior_high * (1.0 - accuracy) + p_low * accuracy
        posterior = (prior_high * (1.0 - accuracy)) / p_signal if p_signal > 0 else prior_high
    return p_signal, posterior


def best_deploy_value(case: ExperimentCase, high_probability: float) -> float:
    return max(deploy_value(case, arm, high_probability) for arm in case.arms)


def followup_value(case: ExperimentCase, experiment: Experiment, high_probability: float) -> float:
    if experiment.followup_accuracy <= 0.0:
        return float("-inf")
    p_signal_high, posterior_high = posterior_after_signal(
        high_probability,
        experiment.followup_accuracy,
        signal_high=True,
    )
    p_signal_low, posterior_low = posterior_after_signal(
        high_probability,
        experiment.followup_accuracy,
        signal_high=False,
    )
    return (
        -experiment.followup_cost
        + p_signal_high * best_deploy_value(case, posterior_high)
        + p_signal_low * best_deploy_value(case, posterior_low)
    )


def experiment_value(case: ExperimentCase, experiment: Experiment, *, allow_followup: bool = True) -> float:
    p_high = case.high_state_probability
    p_low = 1.0 - p_high
    accuracy = experiment.accuracy

    p_signal_high, posterior_high_given_high_signal = posterior_after_signal(
        p_high,
        accuracy,
        signal_high=True,
    )
    p_signal_low, posterior_high_given_low_signal = posterior_after_signal(
        p_high,
        accuracy,
        signal_high=False,
    )

    best_after_high_signal = best_deploy_value(case, posterior_high_given_high_signal)
    best_after_low_signal = best_deploy_value(case, posterior_high_given_low_signal)
    if allow_followup:
        best_after_high_signal = max(
            best_after_high_signal,
            followup_value(case, experiment, posterior_high_given_high_signal),
        )
        best_after_low_signal = max(
            best_after_low_signal,
            followup_value(case, experiment, posterior_high_given_low_signal),
        )
    return -experiment.cost + p_signal_high * best_after_high_signal + p_signal_low * best_after_low_signal


def action_values(case: ExperimentCase, *, allow_followup: bool = True) -> dict[str, float]:
    values = {f"DEPLOY_{arm.arm_id}": deploy_value(case, arm) for arm in case.arms}
    for experiment in case.experiments:
        values[f"EXPERIMENT_{experiment.experiment_id}"] = experiment_value(
            case,
            experiment,
            allow_followup=allow_followup,
        )
    return values


def best_action(case: ExperimentCase) -> str:
    values = action_values(case)
    return max(values, key=values.get)


def greedy_action(case: ExperimentCase) -> str:
    values = action_values(case)
    deploy_values = {action: value for action, value in values.items() if action.startswith("DEPLOY_")}
    return max(deploy_values, key=deploy_values.get)


def single_step_action(case: ExperimentCase) -> str:
    values = action_values(case, allow_followup=False)
    return max(values, key=values.get)


def run_experiment_design_game(agent: Agent, cases: list[ExperimentCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[ExperimentTrial] = []
    for case in cases:
        values = action_values(case)
        best = best_action(case)
        greedy = greedy_action(case)
        single_step = single_step_action(case)
        response = agent.complete(EXPERIMENT_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_ACTION", response)
        chosen = chosen if chosen in values else None
        gap = values[best] - values[chosen] if chosen is not None else None
        trials.append(
            ExperimentTrial(
                case=case,
                best_action=best,
                greedy_action=greedy,
                single_step_action=single_step,
                chosen_action=chosen,
                expected_value_gap=gap,
                raw_response=response,
            )
        )
    return summarize_experiment_trials(agent.name, trials)


def summarize_experiment_trials(agent_name: str, trials: list[ExperimentTrial]) -> dict:
    gaps = [trial.expected_value_gap for trial in trials if trial.expected_value_gap is not None]
    experiment_required = [trial for trial in trials if trial.best_action.startswith("EXPERIMENT_")]
    missed = sum(
        trial.chosen_action is not None and not trial.chosen_action.startswith("EXPERIMENT_")
        for trial in experiment_required
    )
    multi_step_required = [
        trial for trial in trials if trial.best_action != trial.single_step_action
    ]
    multi_step_misses = sum(
        trial.chosen_action is not None and trial.chosen_action != trial.best_action
        for trial in multi_step_required
    )
    return {
        "task": "experiment_design",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_value_gap": mean(gaps),
        "mean_expected_value_gap_ci95": bootstrap_mean_ci(gaps),
        "experiment_miss_rate": missed / len(experiment_required) if experiment_required else 0.0,
        "multi_step_miss_rate": (
            multi_step_misses / len(multi_step_required) if multi_step_required else 0.0
        ),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: ExperimentCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"deployment_units={case.deployment_units}",
        f"high_state_probability={case.high_state_probability:.4f}",
        "State is binary: LOW or HIGH. Experiments return a HIGH or LOW signal.",
        "If the true state is HIGH, signal accuracy is P(signal=HIGH). "
        "If the true state is LOW, signal accuracy is P(signal=LOW).",
        "After an experiment, update beliefs by Bayes rule and deploy the arm with highest posterior expected payoff.",
        "Arms:",
    ]
    for arm in case.arms:
        lines.append(
            "  "
            f"arm_id={arm.arm_id} "
            f"low_payoff={arm.low_payoff:.2f} "
            f"high_payoff={arm.high_payoff:.2f}"
        )
    lines.append("Experiments:")
    for experiment in case.experiments:
        lines.append(
            "  "
            f"experiment_id={experiment.experiment_id} "
            f"cost={experiment.cost:.2f} "
            f"accuracy={experiment.accuracy:.4f} "
            f"followup_cost={experiment.followup_cost:.2f} "
            f"followup_accuracy={experiment.followup_accuracy:.4f}"
        )
    lines.append(
        "If followup_accuracy > 0, the first experiment can be followed by that second test before deployment when the posterior makes it worthwhile."
    )
    lines.append("Choose the first action with the highest expected total payoff net of experiment costs.")
    return "\n".join(lines)


def _trial_json(trial: ExperimentTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
