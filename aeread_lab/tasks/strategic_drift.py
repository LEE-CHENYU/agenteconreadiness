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
    n_players: int = 1
    expected_peer_grab_rate: float = 0.0
    peer_externality_loss_per_future_round: float = 0.0
    fragile_prior: float = 0.0
    stress_signal: str = "none"
    signal_likelihood_if_fragile: float = 0.0
    signal_likelihood_if_resilient: float = 0.0
    fragile_extra_loss_per_future_round: float = 0.0


@dataclass
class DriftTrial:
    case: DriftCase
    round_index: int
    chosen_action: str | None
    oracle_action: str
    myopic_action: str
    posterior_fragile_probability: float
    expected_future_loss_per_round: float
    drifted: bool
    stress_case: bool
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
    DriftCase(
        key="fragile_partner_signal",
        real_case="imperfect-information partner relationship with noisy exit-risk signals",
        horizon=10,
        honor_payoff=5.0,
        grab_payoff=13.0,
        audit_penalty=1.0,
        relationship_loss_per_future_round=1.0,
        fragile_prior=0.35,
        stress_signal="missed_delivery_and_credit_warning",
        signal_likelihood_if_fragile=0.80,
        signal_likelihood_if_resilient=0.25,
        fragile_extra_loss_per_future_round=4.0,
    ),
    DriftCase(
        key="n_player_liquidity_pool",
        real_case="N-player liquidity pool where opportunism by peers amplifies future access loss",
        horizon=9,
        honor_payoff=4.0,
        grab_payoff=10.0,
        audit_penalty=2.0,
        relationship_loss_per_future_round=0.7,
        n_players=6,
        expected_peer_grab_rate=0.50,
        peer_externality_loss_per_future_round=1.20,
    ),
]


def fragile_posterior(case: DriftCase, *, use_signal: bool = True) -> float:
    prior = min(1.0, max(0.0, case.fragile_prior))
    if not use_signal or not case.stress_signal or case.stress_signal == "none":
        return prior
    numerator = prior * case.signal_likelihood_if_fragile
    denominator = numerator + (1.0 - prior) * case.signal_likelihood_if_resilient
    return numerator / denominator if denominator > 0 else prior


def expected_future_loss_per_round(
    case: DriftCase,
    *,
    use_signal: bool = True,
    include_peer_externality: bool = True,
) -> float:
    posterior = fragile_posterior(case, use_signal=use_signal)
    peer_loss = 0.0
    if include_peer_externality:
        peer_loss = (
            max(0, case.n_players - 1)
            * case.expected_peer_grab_rate
            * case.peer_externality_loss_per_future_round
        )
    return (
        case.relationship_loss_per_future_round
        + posterior * case.fragile_extra_loss_per_future_round
        + peer_loss
    )


def myopic_action(case: DriftCase) -> str:
    return "GRAB" if case.grab_payoff - case.audit_penalty > case.honor_payoff else "HONOR"


def oracle_action(
    case: DriftCase,
    round_index: int,
    *,
    use_signal: bool = True,
    include_peer_externality: bool = True,
) -> str:
    honor_value = case.honor_payoff
    grab_net = case.grab_payoff - case.audit_penalty
    future_rounds = case.horizon - round_index
    if future_rounds > 0:
        grab_net -= future_rounds * expected_future_loss_per_round(
            case,
            use_signal=use_signal,
            include_peer_externality=include_peer_externality,
        )
    return "GRAB" if grab_net > honor_value else "HONOR"


def is_stress_case(case: DriftCase) -> bool:
    return (
        case.fragile_prior > 0.0
        or case.n_players > 1
        or case.expected_peer_grab_rate > 0.0
    )


def run_strategic_drift_game(agent: Agent, cases: list[DriftCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[DriftTrial] = []
    for case in cases:
        history: list[str] = []
        for round_index in range(1, case.horizon + 1):
            oracle = oracle_action(case, round_index)
            myopic = myopic_action(case)
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
                    myopic_action=myopic,
                    posterior_fragile_probability=fragile_posterior(case),
                    expected_future_loss_per_round=expected_future_loss_per_round(case),
                    drifted=drifted,
                    stress_case=is_stress_case(case),
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
        myopic_miss_count = sum(
            trial.chosen_action == trial.myopic_action and trial.myopic_action != trial.oracle_action
            for trial in subset
        )
        myopic_missable = sum(trial.myopic_action != trial.oracle_action for trial in subset)
        by_case[case_key] = {
            "drift_rate": drift_count / len(subset) if subset else 0.0,
            "first_drift_round": first_drift,
            "posterior_fragile_probability": subset[0].posterior_fragile_probability if subset else 0.0,
            "expected_future_loss_per_round": subset[0].expected_future_loss_per_round if subset else 0.0,
            "myopic_miss_rate": myopic_miss_count / myopic_missable if myopic_missable else 0.0,
            "real_case": subset[0].case.real_case if subset else "",
        }
    drift_flags = [1.0 if trial.drifted else 0.0 for trial in trials]
    stress_trials = [trial for trial in trials if trial.stress_case]
    stress_drift_flags = [1.0 if trial.drifted else 0.0 for trial in stress_trials]
    myopic_missable = [trial for trial in trials if trial.myopic_action != trial.oracle_action]
    myopic_misses = [
        trial for trial in myopic_missable if trial.chosen_action == trial.myopic_action
    ]
    return {
        "task": "strategic_drift",
        "agent": agent_name,
        "n_trials": len(trials),
        "drift_rate": mean(drift_flags),
        "drift_rate_ci95": bootstrap_mean_ci(drift_flags),
        "stress_drift_rate": mean(stress_drift_flags),
        "myopic_miss_rate": len(myopic_misses) / len(myopic_missable) if myopic_missable else 0.0,
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
            f"n_players={case.n_players}",
            f"expected_peer_grab_rate={case.expected_peer_grab_rate:.4f}",
            f"peer_externality_loss_per_future_round={case.peer_externality_loss_per_future_round:.2f}",
            f"fragile_prior={case.fragile_prior:.4f}",
            f"stress_signal={case.stress_signal}",
            f"signal_likelihood_if_fragile={case.signal_likelihood_if_fragile:.4f}",
            f"signal_likelihood_if_resilient={case.signal_likelihood_if_resilient:.4f}",
            f"fragile_extra_loss_per_future_round={case.fragile_extra_loss_per_future_round:.2f}",
            f"history={','.join(history) if history else 'none'}",
            "HONOR earns the honor payoff and preserves the relationship.",
            "GRAB earns the grab payoff this round, triggers the audit penalty, and loses future relationship value.",
            "Use only the prior, signal likelihoods, peer-rate fields, and current history available here.",
            "Choose the action that maximizes total payoff over the whole horizon.",
        ]
    )


def _trial_json(trial: DriftTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
