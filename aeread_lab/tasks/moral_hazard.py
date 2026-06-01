from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


MORAL_HAZARD_SYSTEM = (
    "TASK: moral_hazard_contract\n"
    "Choose the compensation contract for the hidden-action setting. Return one final line only: "
    "FINAL_CONTRACT: <contract_id>."
)


@dataclass(frozen=True)
class EffortLevel:
    effort_id: str
    high_output_probability: float
    effort_cost: float


@dataclass(frozen=True)
class CompensationContract:
    contract_id: str
    base_pay: float
    high_output_bonus: float


@dataclass(frozen=True)
class MoralHazardCase:
    key: str
    real_case: str
    high_output_value: float
    low_output_value: float
    worker_outside_option: float
    worker_risk_penalty: float
    nonparticipation_penalty: float
    efforts: tuple[EffortLevel, ...]
    contracts: tuple[CompensationContract, ...]


@dataclass(frozen=True)
class ContractMetrics:
    induced_effort: str
    participates: bool
    expected_principal_profit: float
    worker_utility: float
    expected_wage: float


@dataclass
class MoralHazardTrial:
    case: MoralHazardCase
    best_contract: str
    hidden_action_blind_contract: str
    high_bonus_contract: str
    chosen_contract: str | None
    profit_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    MoralHazardCase(
        key="sales_comp",
        real_case="sales compensation where effort is hidden and output is noisy",
        high_output_value=160.0,
        low_output_value=60.0,
        worker_outside_option=25.0,
        worker_risk_penalty=0.0010,
        nonparticipation_penalty=120.0,
        efforts=(
            EffortLevel("low_effort", 0.35, 0.0),
            EffortLevel("high_effort", 0.75, 14.0),
        ),
        contracts=(
            CompensationContract("cheap_fixed", 40.0, 0.0),
            CompensationContract("balanced_bonus", 15.0, 42.0),
            CompensationContract("aggressive_bonus", 5.0, 80.0),
        ),
    ),
    MoralHazardCase(
        key="enterprise_sales",
        real_case="enterprise sales team where first-best output needs costly prospecting",
        high_output_value=250.0,
        low_output_value=50.0,
        worker_outside_option=25.0,
        worker_risk_penalty=0.0008,
        nonparticipation_penalty=150.0,
        efforts=(
            EffortLevel("low_effort", 0.25, 0.0),
            EffortLevel("high_effort", 0.70, 28.0),
        ),
        contracts=(
            CompensationContract("cheap_fixed", 55.0, 0.0),
            CompensationContract("screened_bonus", 5.0, 75.0),
            CompensationContract("overpowered_bonus", 0.0, 120.0),
        ),
    ),
    MoralHazardCase(
        key="risk_averse_operator",
        real_case="operations bonus plan for a risk-averse worker",
        high_output_value=140.0,
        low_output_value=40.0,
        worker_outside_option=20.0,
        worker_risk_penalty=0.0040,
        nonparticipation_penalty=90.0,
        efforts=(
            EffortLevel("low_effort", 0.40, 0.0),
            EffortLevel("high_effort", 0.80, 18.0),
        ),
        contracts=(
            CompensationContract("cheap_fixed", 45.0, 0.0),
            CompensationContract("risk_adjusted_bonus", 18.0, 58.0),
            CompensationContract("too_much_bonus_risk", 0.0, 95.0),
        ),
    ),
    MoralHazardCase(
        key="startup_ops",
        real_case="startup operations role where effort changes launch success probability",
        high_output_value=300.0,
        low_output_value=80.0,
        worker_outside_option=30.0,
        worker_risk_penalty=0.0007,
        nonparticipation_penalty=160.0,
        efforts=(
            EffortLevel("low_effort", 0.30, 0.0),
            EffortLevel("high_effort", 0.65, 40.0),
        ),
        contracts=(
            CompensationContract("cheap_fixed", 70.0, 0.0),
            CompensationContract("launch_bonus", 10.0, 125.0),
            CompensationContract("huge_bonus", 0.0, 180.0),
        ),
    ),
]


def expected_output_value(case: MoralHazardCase, effort: EffortLevel) -> float:
    return (
        effort.high_output_probability * case.high_output_value
        + (1.0 - effort.high_output_probability) * case.low_output_value
    )


def expected_wage(contract: CompensationContract, effort: EffortLevel) -> float:
    return contract.base_pay + effort.high_output_probability * contract.high_output_bonus


def wage_variance(contract: CompensationContract, effort: EffortLevel) -> float:
    p_high = effort.high_output_probability
    return p_high * (1.0 - p_high) * contract.high_output_bonus**2


def worker_utility(case: MoralHazardCase, contract: CompensationContract, effort: EffortLevel) -> float:
    return (
        expected_wage(contract, effort)
        - effort.effort_cost
        - case.worker_risk_penalty * wage_variance(contract, effort)
    )


def contract_metrics(case: MoralHazardCase, contract: CompensationContract) -> ContractMetrics:
    induced_effort = max(case.efforts, key=lambda effort: worker_utility(case, contract, effort))
    utility = worker_utility(case, contract, induced_effort)
    participates = utility >= case.worker_outside_option
    wage = expected_wage(contract, induced_effort)
    profit = expected_output_value(case, induced_effort) - wage if participates else -case.nonparticipation_penalty
    return ContractMetrics(
        induced_effort=induced_effort.effort_id,
        participates=participates,
        expected_principal_profit=profit,
        worker_utility=utility,
        expected_wage=wage,
    )


def best_contract(case: MoralHazardCase) -> str:
    return max(case.contracts, key=lambda contract: contract_metrics(case, contract).expected_principal_profit).contract_id


def hidden_action_blind_contract(case: MoralHazardCase) -> str:
    high_effort = max(case.efforts, key=lambda effort: effort.high_output_probability)
    return max(
        case.contracts,
        key=lambda contract: expected_output_value(case, high_effort) - expected_wage(contract, high_effort),
    ).contract_id


def high_bonus_contract(case: MoralHazardCase) -> str:
    return max(case.contracts, key=lambda contract: contract.high_output_bonus).contract_id


def run_moral_hazard_game(agent: Agent, cases: list[MoralHazardCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[MoralHazardTrial] = []
    for case in cases:
        best = best_contract(case)
        blind = hidden_action_blind_contract(case)
        high_bonus = high_bonus_contract(case)
        response = agent.complete(MORAL_HAZARD_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_CONTRACT", response)
        contract_by_id = {contract.contract_id: contract for contract in case.contracts}
        chosen = chosen if chosen in contract_by_id else None
        regret = (
            contract_metrics(case, contract_by_id[best]).expected_principal_profit
            - contract_metrics(case, contract_by_id[chosen]).expected_principal_profit
            if chosen is not None
            else None
        )
        trials.append(
            MoralHazardTrial(
                case=case,
                best_contract=best,
                hidden_action_blind_contract=blind,
                high_bonus_contract=high_bonus,
                chosen_contract=chosen,
                profit_regret=regret,
                raw_response=response,
            )
        )
    return summarize_moral_hazard_trials(agent.name, trials)


def summarize_moral_hazard_trials(agent_name: str, trials: list[MoralHazardTrial]) -> dict:
    regrets = [trial.profit_regret for trial in trials if trial.profit_regret is not None]
    blind_missable = [trial for trial in trials if trial.hidden_action_blind_contract != trial.best_contract]
    bonus_missable = [trial for trial in trials if trial.high_bonus_contract != trial.best_contract]
    blind_misses = sum(trial.chosen_contract == trial.hidden_action_blind_contract for trial in blind_missable)
    bonus_misses = sum(trial.chosen_contract == trial.high_bonus_contract for trial in bonus_missable)
    return {
        "task": "moral_hazard",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_profit_regret": mean(regrets),
        "mean_profit_regret_ci95": bootstrap_mean_ci(regrets),
        "hidden_action_blind_miss_rate": blind_misses / len(blind_missable) if blind_missable else 0.0,
        "high_bonus_miss_rate": bonus_misses / len(bonus_missable) if bonus_missable else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: MoralHazardCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"high_output_value={case.high_output_value:.2f}",
        f"low_output_value={case.low_output_value:.2f}",
        f"worker_outside_option={case.worker_outside_option:.2f}",
        f"worker_risk_penalty={case.worker_risk_penalty:.6f}",
        "Effort is hidden. Worker chooses the effort level that maximizes expected wage minus effort cost and wage-risk penalty.",
        "Effort levels:",
    ]
    for effort in case.efforts:
        lines.append(
            "  "
            f"effort_id={effort.effort_id} "
            f"high_output_probability={effort.high_output_probability:.4f} "
            f"effort_cost={effort.effort_cost:.2f}"
        )
    lines.append("Contracts:")
    for contract in case.contracts:
        lines.append(
            "  "
            f"contract_id={contract.contract_id} "
            f"base_pay={contract.base_pay:.2f} "
            f"high_output_bonus={contract.high_output_bonus:.2f}"
        )
    lines.extend(
        [
            "Expected wage = base_pay + P(high_output|effort)*high_output_bonus.",
            "Wage risk penalty = worker_risk_penalty * P(high)*(1-P(high))*high_output_bonus^2.",
            "A contract only works if the worker's best effort utility is at least the outside option.",
            "Choose the contract that maximizes expected principal profit after the worker's hidden effort response.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: MoralHazardTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
