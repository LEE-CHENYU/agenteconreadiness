from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


BELIEF_BARGAINING_SYSTEM = (
    "TASK: belief_bargain_price\n"
    "You are the seller's agent in a take-it-or-leave-it negotiation. "
    "Use the observed cue to update beliefs about buyer willingness-to-pay, then choose a price. "
    "Return one final line only: FINAL_PRICE: <number>."
)


@dataclass(frozen=True)
class BuyerState:
    state_id: str
    buyer_wtp: float
    prior_probability: float
    cue_likelihood: float
    signal_likelihoods: tuple[float, ...] = ()


@dataclass(frozen=True)
class BeliefBargainingCase:
    key: str
    real_case: str
    seller_cost: float
    observed_cue: str
    states: tuple[BuyerState, ...]
    observed_signals: tuple[str, ...] = ()


@dataclass
class BeliefBargainingTrial:
    case: BeliefBargainingCase
    oracle_price: float
    prior_price: float
    single_cue_price: float
    chosen_price: float | None
    expected_surplus: float | None
    expected_surplus_gap: float | None
    raw_response: str


DEFAULT_CASES = [
    BeliefBargainingCase(
        key="enterprise_budget_signal",
        real_case="enterprise software negotiation with a procurement-budget cue",
        seller_cost=42.0,
        observed_cue="mentions accelerated enterprise rollout",
        states=(
            BuyerState("low_budget", 75.0, 0.45, 0.15),
            BuyerState("mid_budget", 115.0, 0.35, 0.40),
            BuyerState("high_budget", 180.0, 0.20, 0.85),
        ),
    ),
    BeliefBargainingCase(
        key="used_equipment_rush",
        real_case="used-equipment sale where timing language reveals operational urgency",
        seller_cost=28.0,
        observed_cue="buyer asks whether pickup can happen today",
        states=(
            BuyerState("casual", 55.0, 0.50, 0.10),
            BuyerState("needs_soon", 92.0, 0.30, 0.35),
            BuyerState("urgent", 140.0, 0.20, 0.98),
        ),
    ),
    BeliefBargainingCase(
        key="supplier_capacity_cue",
        real_case="supplier quote where buyer hints at capacity shortage",
        seller_cost=80.0,
        observed_cue="buyer says their backup supplier may miss deadline",
        states=(
            BuyerState("many_options", 118.0, 0.40, 0.08),
            BuyerState("some_pressure", 168.0, 0.42, 0.25),
            BuyerState("shortage", 250.0, 0.18, 0.98),
        ),
    ),
    BeliefBargainingCase(
        key="renewal_counteroffer_sequence",
        real_case="enterprise renewal where multiple counteroffer turns reveal budget pressure",
        seller_cost=58.0,
        observed_cue="first buyer pushback says the renewal is above their approved budget",
        observed_signals=(
            "budget_pushback",
            "usage_growth_disclosed",
            "executive_sponsor_joins_call",
        ),
        states=(
            BuyerState("tight_budget", 92.0, 0.45, 0.75, (0.75, 0.15, 0.10)),
            BuyerState("expansion_budget", 148.0, 0.38, 0.35, (0.35, 0.75, 0.55)),
            BuyerState("strategic_rollout", 230.0, 0.17, 0.18, (0.18, 0.82, 0.90)),
        ),
    ),
    BeliefBargainingCase(
        key="walkaway_then_procurement_reentry",
        real_case="buyer first threatens to walk away, then procurement returns with urgency signals",
        seller_cost=35.0,
        observed_cue="buyer initially says they can defer the purchase",
        observed_signals=(
            "walkaway_threat",
            "asks_for_same_week_delivery",
            "mentions_failed_backup_vendor",
        ),
        states=(
            BuyerState("browsing", 68.0, 0.52, 0.80, (0.80, 0.12, 0.08)),
            BuyerState("planned_need", 116.0, 0.33, 0.42, (0.42, 0.55, 0.35)),
            BuyerState("urgent_replacement", 175.0, 0.15, 0.18, (0.18, 0.82, 0.92)),
        ),
    ),
]


def posterior_probabilities(
    case: BeliefBargainingCase,
    *,
    signal_count: int | None = None,
) -> dict[str, float]:
    weights = {
        state.state_id: state.prior_probability * _combined_likelihood(case, state, signal_count=signal_count)
        for state in case.states
    }
    total = sum(weights.values())
    if total <= 0:
        return {state.state_id: state.prior_probability for state in case.states}
    return {state_id: weight / total for state_id, weight in weights.items()}


def expected_surplus(
    case: BeliefBargainingCase,
    price: float,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> float:
    if price < case.seller_cost:
        return 0.0
    probs = posterior_probabilities(case, signal_count=signal_count) if use_posterior else {
        state.state_id: state.prior_probability for state in case.states
    }
    return sum(
        probs[state.state_id] * (price - case.seller_cost)
        for state in case.states
        if price <= state.buyer_wtp
    )


def best_price(
    case: BeliefBargainingCase,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> float:
    candidates = sorted({case.seller_cost, *(state.buyer_wtp for state in case.states)})
    return max(
        candidates,
        key=lambda price: expected_surplus(
            case,
            price,
            use_posterior=use_posterior,
            signal_count=signal_count,
        ),
    )


def run_belief_bargaining_game(
    agent: Agent,
    cases: list[BeliefBargainingCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[BeliefBargainingTrial] = []
    for case in cases:
        oracle = best_price(case, use_posterior=True)
        prior = best_price(case, use_posterior=False)
        single_cue = best_price(case, use_posterior=True, signal_count=1)
        response = agent.complete(BELIEF_BARGAINING_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_PRICE", response)
        max_wtp = max(state.buyer_wtp for state in case.states)
        chosen = clamp(parsed, 0.0, max_wtp) if parsed is not None else None
        chosen_surplus = (
            expected_surplus(case, chosen, use_posterior=True)
            if chosen is not None
            else None
        )
        gap = (
            expected_surplus(case, oracle, use_posterior=True) - chosen_surplus
            if chosen_surplus is not None
            else None
        )
        trials.append(
            BeliefBargainingTrial(
                case=case,
                oracle_price=oracle,
                prior_price=prior,
                single_cue_price=single_cue,
                chosen_price=chosen,
                expected_surplus=chosen_surplus,
                expected_surplus_gap=gap,
                raw_response=response,
            )
        )
    return summarize_belief_bargaining_trials(agent.name, trials)


def summarize_belief_bargaining_trials(agent_name: str, trials: list[BeliefBargainingTrial]) -> dict:
    gaps = [trial.expected_surplus_gap for trial in trials if trial.expected_surplus_gap is not None]
    cue_switches = sum(abs(trial.oracle_price - trial.prior_price) > 1e-9 for trial in trials)
    missed_switches = sum(
        abs(trial.oracle_price - trial.prior_price) > 1e-9
        and trial.chosen_price is not None
        and abs(trial.chosen_price - trial.oracle_price) > 1e-9
        for trial in trials
    )
    multi_turn_switches = sum(
        len(trial.case.observed_signals) > 1
        and abs(trial.oracle_price - trial.single_cue_price) > 1e-9
        for trial in trials
    )
    missed_multi_turn_switches = sum(
        len(trial.case.observed_signals) > 1
        and abs(trial.oracle_price - trial.single_cue_price) > 1e-9
        and trial.chosen_price is not None
        and abs(trial.chosen_price - trial.oracle_price) > 1e-9
        for trial in trials
    )
    return {
        "task": "belief_bargaining",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_surplus_gap": mean(gaps),
        "mean_expected_surplus_gap_ci95": bootstrap_mean_ci(gaps),
        "cue_switch_miss_rate": missed_switches / cue_switches if cue_switches else 0.0,
        "multi_turn_miss_rate": missed_multi_turn_switches / multi_turn_switches if multi_turn_switches else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: BeliefBargainingCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"seller_cost={case.seller_cost:.2f}",
        f"observed_cue={case.observed_cue}",
        f"observed_signal_sequence={','.join(_signals(case))}",
        "Buyer states:",
    ]
    for state in case.states:
        likelihoods = _state_likelihoods(case, state)
        lines.append(
            "  "
            + " ".join(
                [
                    f"state_id={state.state_id}",
                    f"buyer_wtp={state.buyer_wtp:.2f}",
                    f"prior_probability={state.prior_probability:.4f}",
                    f"likelihood_of_observed_cue={state.cue_likelihood:.4f}",
                    f"signal_likelihoods={','.join(f'{value:.4f}' for value in likelihoods)}",
                ]
            )
        )
    lines.extend(
        [
            "If price <= buyer_wtp, the buyer accepts and seller surplus is price - seller_cost.",
            "If price > buyer_wtp, the buyer rejects and seller surplus is 0.",
            "Choose the price that maximizes expected seller surplus after updating on the observed cue.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: BeliefBargainingTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _signals(case: BeliefBargainingCase) -> tuple[str, ...]:
    return case.observed_signals or (case.observed_cue,)


def _state_likelihoods(case: BeliefBargainingCase, state: BuyerState) -> tuple[float, ...]:
    signals = _signals(case)
    if state.signal_likelihoods:
        return state.signal_likelihoods[: len(signals)]
    return (state.cue_likelihood,)


def _combined_likelihood(
    case: BeliefBargainingCase,
    state: BuyerState,
    *,
    signal_count: int | None,
) -> float:
    likelihoods = _state_likelihoods(case, state)
    if signal_count is not None:
        likelihoods = likelihoods[:signal_count]
    product = 1.0
    for likelihood in likelihoods:
        product *= likelihood
    return product
