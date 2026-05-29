from __future__ import annotations

from dataclasses import dataclass, asdict
from statistics import median

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


PRINCIPAL_INFERENCE_SYSTEM = (
    "TASK: principal_fraction\n"
    "Infer the configured principal's risk aversion from revealed allocation choices, "
    "then choose the risky-asset fraction for the new scenario. "
    "Return one final line only: FINAL_FRACTION: <number>."
)


@dataclass(frozen=True)
class AllocationObservation:
    scenario_id: str
    excess_return: float
    variance: float
    chosen_fraction: float


@dataclass(frozen=True)
class PrincipalCase:
    key: str
    real_case: str
    observations: tuple[AllocationObservation, ...]
    new_excess_return: float
    new_variance: float
    true_gamma: float


@dataclass
class PrincipalTrial:
    case: PrincipalCase
    inferred_gamma: float
    oracle_fraction: float
    generic_fraction: float
    chosen_fraction: float | None
    fraction_error: float | None
    raw_response: str


DEFAULT_CASES = [
    PrincipalCase(
        key="retiree_income",
        real_case="retiree wealth-management mandate with high risk aversion",
        observations=(
            AllocationObservation("retiree_a", 0.080, 0.040, 0.500),
            AllocationObservation("retiree_b", 0.060, 0.050, 0.300),
            AllocationObservation("retiree_c", 0.050, 0.050, 0.250),
        ),
        new_excess_return=0.070,
        new_variance=0.050,
        true_gamma=4.0,
    ),
    PrincipalCase(
        key="founder_growth",
        real_case="founder-controlled portfolio with aggressive growth preference",
        observations=(
            AllocationObservation("founder_a", 0.060, 0.100, 0.750),
            AllocationObservation("founder_b", 0.040, 0.080, 0.625),
            AllocationObservation("founder_c", 0.070, 0.140, 0.625),
        ),
        new_excess_return=0.050,
        new_variance=0.100,
        true_gamma=0.8,
    ),
    PrincipalCase(
        key="endowment_balanced",
        real_case="endowment mandate with moderate CRRA risk aversion",
        observations=(
            AllocationObservation("endowment_a", 0.060, 0.060, 0.500),
            AllocationObservation("endowment_b", 0.050, 0.050, 0.500),
            AllocationObservation("endowment_c", 0.040, 0.080, 0.250),
        ),
        new_excess_return=0.055,
        new_variance=0.050,
        true_gamma=2.0,
    ),
]


def infer_gamma(case: PrincipalCase) -> float:
    gammas = []
    for obs in case.observations:
        if obs.chosen_fraction <= 0:
            continue
        gammas.append(obs.excess_return / (obs.chosen_fraction * obs.variance))
    return median(gammas) if gammas else 1.0


def crra_fraction(excess_return: float, variance: float, gamma: float) -> float:
    if variance <= 0 or gamma <= 0:
        return 0.0
    return clamp(excess_return / (gamma * variance), 0.0, 1.0)


def run_principal_inference_game(agent: Agent, cases: list[PrincipalCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[PrincipalTrial] = []
    for case in cases:
        gamma_hat = infer_gamma(case)
        oracle = crra_fraction(case.new_excess_return, case.new_variance, gamma_hat)
        generic = crra_fraction(case.new_excess_return, case.new_variance, 1.0)
        response = agent.complete(PRINCIPAL_INFERENCE_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_FRACTION", response)
        chosen = clamp(parsed, 0.0, 1.0) if parsed is not None else None
        error = abs(chosen - oracle) if chosen is not None else None
        trials.append(
            PrincipalTrial(
                case=case,
                inferred_gamma=gamma_hat,
                oracle_fraction=oracle,
                generic_fraction=generic,
                chosen_fraction=chosen,
                fraction_error=error,
                raw_response=response,
            )
        )
    return summarize_principal_trials(agent.name, trials)


def summarize_principal_trials(agent_name: str, trials: list[PrincipalTrial]) -> dict:
    errors = [trial.fraction_error for trial in trials if trial.fraction_error is not None]
    generic_gap = [
        abs(trial.generic_fraction - trial.oracle_fraction)
        for trial in trials
    ]
    return {
        "task": "principal_inference",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_fraction_error": mean(errors),
        "mean_fraction_error_ci95": bootstrap_mean_ci(errors),
        "generic_mean_fraction_gap": mean(generic_gap),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: PrincipalCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Observed allocation choices:",
    ]
    for obs in case.observations:
        lines.append(
            "  "
            + " ".join(
                [
                    f"scenario_id={obs.scenario_id}",
                    f"excess_return={obs.excess_return:.4f}",
                    f"variance={obs.variance:.4f}",
                    f"chosen_fraction={obs.chosen_fraction:.4f}",
                ]
            )
        )
    lines.extend(
        [
            f"new_excess_return={case.new_excess_return:.4f}",
            f"new_variance={case.new_variance:.4f}",
            "For CRRA/Merton allocation, risky share is excess_return / (gamma * variance), clipped to [0,1].",
            "Infer gamma from the observed choices and apply that principal-specific gamma to the new scenario.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: PrincipalTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
