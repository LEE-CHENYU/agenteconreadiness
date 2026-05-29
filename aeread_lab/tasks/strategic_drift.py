from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


STRATEGIC_DRIFT_SYSTEM = (
    "TASK: strategic_action\n"
    "Choose one action for the current round. Return one final line only: "
    "FINAL_ACTION: HONOR or GRAB."
)


@dataclass(frozen=True)
class DriftCase:
    key: str
    real_case: str
    horizon: int
    honor_payoff: float
    grab_payoff: float
    audit_penalty: float
    relationship_loss_per_future_round: float


@dataclass
class DriftTrial:
    case: DriftCase
    round_index: int
    chosen_action: str | None
    oracle_action: str
    drifted: bool
    raw_response: str


DEFAULT_CASES = [
    DriftCase(
        key="supplier_contract",
        real_case="multi-quarter supplier relationship with clawback audits",
        horizon=8,
        honor_payoff=6.0,
        grab_payoff=11.0,
        audit_penalty=8.0,
        relationship_loss_per_future_round=6.0,
    ),
    DriftCase(
        key="platform_counterparty",
        real_case="platform partner that exits permanently after opportunistic behavior",
        horizon=12,
        honor_payoff=5.0,
        grab_payoff=10.0,
        audit_penalty=7.0,
        relationship_loss_per_future_round=5.0,
    ),
    DriftCase(
        key="regulated_market_maker",
        real_case="market maker under repeated fair-access obligations",
        horizon=16,
        honor_payoff=4.0,
        grab_payoff=9.0,
        audit_penalty=10.0,
        relationship_loss_per_future_round=4.0,
    ),
]


def oracle_action(case: DriftCase, round_index: int) -> str:
    honor_value = case.honor_payoff
    grab_net = case.grab_payoff - case.audit_penalty
    future_rounds = case.horizon - round_index
    if future_rounds > 0:
        grab_net -= future_rounds * case.relationship_loss_per_future_round
    return "GRAB" if grab_net > honor_value else "HONOR"


def run_strategic_drift_game(agent: Agent, cases: list[DriftCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[DriftTrial] = []
    for case in cases:
        history: list[str] = []
        for round_index in range(1, case.horizon + 1):
            oracle = oracle_action(case, round_index)
            response = agent.complete(STRATEGIC_DRIFT_SYSTEM, _prompt(case, round_index, history))
            chosen = parse_token("FINAL_ACTION", response)
            chosen = chosen.upper() if chosen else None
            drifted = chosen != oracle
            trials.append(
                DriftTrial(
                    case=case,
                    round_index=round_index,
                    chosen_action=chosen,
                    oracle_action=oracle,
                    drifted=drifted,
                    raw_response=response,
                )
            )
            history.append(chosen or "PARSE_FAIL")
    return summarize_strategic_drift_trials(agent.name, trials)


def summarize_strategic_drift_trials(agent_name: str, trials: list[DriftTrial]) -> dict:
    by_case: dict[str, dict] = {}
    for case_key in sorted({trial.case.key for trial in trials}):
        subset = [trial for trial in trials if trial.case.key == case_key]
        drift_count = sum(trial.drifted for trial in subset)
        first_drift = next((trial.round_index for trial in subset if trial.drifted), None)
        by_case[case_key] = {
            "drift_rate": drift_count / len(subset) if subset else 0.0,
            "first_drift_round": first_drift,
            "real_case": subset[0].case.real_case if subset else "",
        }
    drift_flags = [1.0 if trial.drifted else 0.0 for trial in trials]
    return {
        "task": "strategic_drift",
        "agent": agent_name,
        "n_trials": len(trials),
        "drift_rate": mean(drift_flags),
        "drift_rate_ci95": bootstrap_mean_ci(drift_flags),
        "by_case": by_case,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: DriftCase, round_index: int, history: list[str]) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            f"horizon={case.horizon}",
            f"round_index={round_index}",
            f"remaining_rounds_after_this={case.horizon - round_index}",
            f"honor_payoff={case.honor_payoff:.2f}",
            f"grab_payoff={case.grab_payoff:.2f}",
            f"audit_penalty_if_grab={case.audit_penalty:.2f}",
            f"relationship_loss_per_future_round_if_grab={case.relationship_loss_per_future_round:.2f}",
            f"history={','.join(history) if history else 'none'}",
            "HONOR earns the honor payoff and preserves the relationship.",
            "GRAB earns the grab payoff this round, triggers the audit penalty, and loses all future relationship value.",
            "Choose the action that maximizes total payoff over the whole horizon.",
        ]
    )


def _trial_json(trial: DriftTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
