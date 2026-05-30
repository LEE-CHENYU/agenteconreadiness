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
    strategic_likelihood: bool = False


@dataclass
class BeliefBargainingTrial:
    case: BeliefBargainingCase
    condition: str
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
    BeliefBargainingCase(
        key="strategic_budget_bluff",
        real_case="buyer states a low budget while requesting high-scale rollout protections",
        seller_cost=50.0,
        observed_cue="buyer says their budget cannot exceed 95",
        observed_signals=(
            "low_budget_claim",
            "enterprise_wide_terms_requested",
            "same_quarter_rollout_protection",
        ),
        strategic_likelihood=True,
        states=(
            BuyerState("low_budget", 90.0, 0.45, 0.65, (0.65, 0.10, 0.08)),
            BuyerState("standard_budget", 150.0, 0.35, 0.45, (0.45, 0.55, 0.35)),
            BuyerState("strategic_rollout", 240.0, 0.20, 0.70, (0.70, 0.80, 0.90)),
        ),
    ),
    BeliefBargainingCase(
        key="pooling_discount_request",
        real_case="buyer asks for discount approval while revealing expansion urgency across turns",
        seller_cost=70.0,
        observed_cue="buyer says discount approval is the only blocker",
        observed_signals=(
            "discount_approval_claim",
            "integration_team_standing_by",
            "asks_for_capacity_hold",
        ),
        strategic_likelihood=True,
        states=(
            BuyerState("price_shopper", 115.0, 0.50, 0.80, (0.80, 0.15, 0.12)),
            BuyerState("planned_expansion", 180.0, 0.32, 0.55, (0.55, 0.55, 0.45)),
            BuyerState("urgent_platform_rollout", 285.0, 0.18, 0.35, (0.35, 0.90, 0.85)),
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
        for condition in _conditions(case):
            response = agent.complete(BELIEF_BARGAINING_SYSTEM, _prompt(case, condition=condition))
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
                    condition=condition,
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
        and trial.condition == "base"
        for trial in trials
    )
    missed_multi_turn_switches = sum(
        len(trial.case.observed_signals) > 1
        and abs(trial.oracle_price - trial.single_cue_price) > 1e-9
        and trial.condition == "base"
        and trial.chosen_price is not None
        and abs(trial.chosen_price - trial.oracle_price) > 1e-9
        for trial in trials
    )
    strategic_base = [
        trial
        for trial in trials
        if trial.case.strategic_likelihood
        and trial.condition == "base"
        and trial.expected_surplus_gap is not None
    ]
    strategic_scaffold = [
        trial
        for trial in trials
        if trial.case.strategic_likelihood
        and trial.condition == "posterior_scaffold"
        and trial.expected_surplus_gap is not None
    ]
    return {
        "task": "belief_bargaining",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_surplus_gap": mean(gaps),
        "mean_expected_surplus_gap_ci95": bootstrap_mean_ci(gaps),
        "cue_switch_miss_rate": missed_switches / cue_switches if cue_switches else 0.0,
        "multi_turn_miss_rate": missed_multi_turn_switches / multi_turn_switches if multi_turn_switches else 0.0,
        "mean_strategic_base_gap": mean([trial.expected_surplus_gap for trial in strategic_base]),
        "mean_strategic_scaffold_gap": mean([trial.expected_surplus_gap for trial in strategic_scaffold]),
        "strategic_scaffold_improvement": (
            mean([trial.expected_surplus_gap for trial in strategic_base])
            - mean([trial.expected_surplus_gap for trial in strategic_scaffold])
            if strategic_base and strategic_scaffold
            else None
        ),
        "strategic_base_miss_rate": _price_miss_rate(strategic_base),
        "strategic_scaffold_miss_rate": _price_miss_rate(strategic_scaffold),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: BeliefBargainingCase, condition: str = "base") -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"condition={condition}",
        f"seller_cost={case.seller_cost:.2f}",
        f"observed_cue={case.observed_cue}",
        f"observed_signal_sequence={','.join(_signals(case))}",
        f"strategic_likelihood={1 if case.strategic_likelihood else 0}",
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
    if condition == "posterior_scaffold":
        lines.append("Externalized belief state after each observed signal:")
        for idx, signal in enumerate(_signals(case), start=1):
            posterior = posterior_probabilities(case, signal_count=idx)
            values = ",".join(
                f"{state.state_id}:{posterior[state.state_id]:.4f}" for state in case.states
            )
            lines.append(f"  after_signal={signal} posterior={values}")
        final_posterior = posterior_probabilities(case)
        final_values = ",".join(
            f"{state.state_id}:{final_posterior[state.state_id]:.4f}" for state in case.states
        )
        lines.append(f"final_posterior={final_values}")
    lines.extend(
        [
            "If price <= buyer_wtp, the buyer accepts and seller surplus is price - seller_cost.",
            "If price > buyer_wtp, the buyer rejects and seller surplus is 0.",
            "In strategic-likelihood cases, buyer claims can be cheap talk; use the likelihoods rather than treating statements literally.",
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


def _conditions(case: BeliefBargainingCase) -> tuple[str, ...]:
    return ("base", "posterior_scaffold") if case.strategic_likelihood else ("base",)


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


def _price_miss_rate(trials: list[BeliefBargainingTrial]) -> float:
    if not trials:
        return 0.0
    misses = sum(
        trial.chosen_price is not None
        and abs(trial.chosen_price - trial.oracle_price) > 1e-9
        for trial in trials
    )
    return misses / len(trials)
