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

BELIEF_BARGAINING_INTERACTION_SYSTEM = (
    "TASK: belief_bargain_interaction\n"
    "You are the seller's agent in a two-offer negotiation. "
    "Use the observed signals to update buyer willingness-to-pay beliefs, then choose an opening price "
    "and a fallback price after rejection. "
    "Return one final line only: FINAL_FIRST_PRICE: <number> FINAL_SECOND_PRICE: <number>."
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


@dataclass(frozen=True)
class BargainingInteractionCase:
    key: str
    real_case: str
    seller_cost: float
    observed_signals: tuple[str, ...]
    states: tuple[BuyerState, ...]
    second_round_discount: float
    second_round_delay_cost: float


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


@dataclass
class BargainingInteractionTrial:
    case: BargainingInteractionCase
    oracle_first_price: float
    oracle_second_price: float
    prior_first_price: float
    prior_second_price: float
    single_cue_first_price: float
    single_cue_second_price: float
    single_offer_price: float
    chosen_first_price: float | None
    chosen_second_price: float | None
    expected_surplus: float | None
    expected_surplus_gap: float | None
    first_price_error: float | None
    second_price_error: float | None
    prior_miss: bool
    single_cue_miss: bool
    single_offer_miss: bool
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

INTERACTION_CASES = [
    BargainingInteractionCase(
        key="renewal_rejection_policy",
        real_case="enterprise renewal where rejection of a high opening offer changes the likely budget state",
        seller_cost=58.0,
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
        second_round_discount=0.86,
        second_round_delay_cost=4.0,
    ),
    BargainingInteractionCase(
        key="walkaway_reentry_policy",
        real_case="buyer threatens to defer, then re-enters with same-week urgency and failed-backup signals",
        seller_cost=35.0,
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
        second_round_discount=0.88,
        second_round_delay_cost=3.0,
    ),
    BargainingInteractionCase(
        key="cheap_talk_rollout_policy",
        real_case="buyer states a low budget while asking for high-scale rollout protections",
        seller_cost=50.0,
        observed_signals=(
            "low_budget_claim",
            "enterprise_wide_terms_requested",
            "same_quarter_rollout_protection",
        ),
        states=(
            BuyerState("low_budget", 90.0, 0.45, 0.65, (0.65, 0.10, 0.08)),
            BuyerState("standard_budget", 150.0, 0.35, 0.45, (0.45, 0.55, 0.35)),
            BuyerState("strategic_rollout", 240.0, 0.20, 0.70, (0.70, 0.80, 0.90)),
        ),
        second_round_discount=0.82,
        second_round_delay_cost=5.0,
    ),
    BargainingInteractionCase(
        key="capacity_hold_policy",
        real_case="buyer asks for a capacity hold while revealing integration urgency across negotiation turns",
        seller_cost=70.0,
        observed_signals=(
            "discount_approval_claim",
            "integration_team_standing_by",
            "asks_for_capacity_hold",
        ),
        states=(
            BuyerState("price_shopper", 115.0, 0.50, 0.80, (0.80, 0.15, 0.12)),
            BuyerState("planned_expansion", 180.0, 0.32, 0.55, (0.55, 0.55, 0.45)),
            BuyerState("urgent_platform_rollout", 285.0, 0.18, 0.35, (0.35, 0.90, 0.85)),
        ),
        second_round_discount=0.80,
        second_round_delay_cost=6.0,
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


def interaction_expected_surplus(
    case: BargainingInteractionCase,
    first_price: float,
    second_price: float,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> float:
    if first_price < case.seller_cost or second_price < case.seller_cost:
        return 0.0
    probs = _interaction_probabilities(case, use_posterior=use_posterior, signal_count=signal_count)
    value = 0.0
    for state in case.states:
        probability = probs[state.state_id]
        if first_price <= state.buyer_wtp:
            value += probability * (first_price - case.seller_cost)
        elif second_price <= state.buyer_wtp:
            value += probability * (
                case.second_round_discount * (second_price - case.seller_cost)
                - case.second_round_delay_cost
            )
    return value


def best_interaction_prices(
    case: BargainingInteractionCase,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> tuple[float, float]:
    candidates = _interaction_candidate_prices(case)
    pairs = [
        (first, second)
        for first in candidates
        for second in candidates
        if second <= first
    ]
    return max(
        pairs,
        key=lambda pair: (
            interaction_expected_surplus(
                case,
                pair[0],
                pair[1],
                use_posterior=use_posterior,
                signal_count=signal_count,
            ),
            pair[0],
            pair[1],
        ),
    )


def best_interaction_single_offer_price(
    case: BargainingInteractionCase,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> float:
    candidates = _interaction_candidate_prices(case)
    return max(
        candidates,
        key=lambda price: (
            interaction_expected_surplus(
                case,
                price,
                price,
                use_posterior=use_posterior,
                signal_count=signal_count,
            ),
            price,
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


def run_belief_bargaining_interaction_game(
    agent: Agent,
    cases: list[BargainingInteractionCase] | None = None,
) -> dict:
    cases = cases or INTERACTION_CASES
    trials: list[BargainingInteractionTrial] = []
    for case in cases:
        oracle_first, oracle_second = best_interaction_prices(case, use_posterior=True)
        prior_first, prior_second = best_interaction_prices(case, use_posterior=False)
        single_cue_first, single_cue_second = best_interaction_prices(
            case,
            use_posterior=True,
            signal_count=1,
        )
        single_offer = best_interaction_single_offer_price(case, use_posterior=True)
        oracle_surplus = interaction_expected_surplus(
            case,
            oracle_first,
            oracle_second,
            use_posterior=True,
        )
        response = agent.complete(
            BELIEF_BARGAINING_INTERACTION_SYSTEM,
            _interaction_prompt(case),
        )
        first = parse_float("FINAL_FIRST_PRICE", response)
        second = parse_float("FINAL_SECOND_PRICE", response)
        max_wtp = max(state.buyer_wtp for state in case.states)
        chosen_first = clamp(first, 0.0, max_wtp) if first is not None else None
        chosen_second = clamp(second, 0.0, max_wtp) if second is not None else None
        chosen_surplus = (
            interaction_expected_surplus(case, chosen_first, chosen_second, use_posterior=True)
            if chosen_first is not None and chosen_second is not None
            else None
        )
        trials.append(
            BargainingInteractionTrial(
                case=case,
                oracle_first_price=oracle_first,
                oracle_second_price=oracle_second,
                prior_first_price=prior_first,
                prior_second_price=prior_second,
                single_cue_first_price=single_cue_first,
                single_cue_second_price=single_cue_second,
                single_offer_price=single_offer,
                chosen_first_price=chosen_first,
                chosen_second_price=chosen_second,
                expected_surplus=chosen_surplus,
                expected_surplus_gap=(
                    oracle_surplus - chosen_surplus if chosen_surplus is not None else None
                ),
                first_price_error=(
                    abs(chosen_first - oracle_first) if chosen_first is not None else None
                ),
                second_price_error=(
                    abs(chosen_second - oracle_second) if chosen_second is not None else None
                ),
                prior_miss=_interaction_baseline_miss(
                    chosen_first,
                    chosen_second,
                    oracle_first,
                    oracle_second,
                    prior_first,
                    prior_second,
                ),
                single_cue_miss=_interaction_baseline_miss(
                    chosen_first,
                    chosen_second,
                    oracle_first,
                    oracle_second,
                    single_cue_first,
                    single_cue_second,
                ),
                single_offer_miss=_interaction_baseline_miss(
                    chosen_first,
                    chosen_second,
                    oracle_first,
                    oracle_second,
                    single_offer,
                    single_offer,
                ),
                raw_response=response,
            )
        )
    return summarize_belief_bargaining_interaction_trials(agent.name, trials)


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


def summarize_belief_bargaining_interaction_trials(
    agent_name: str,
    trials: list[BargainingInteractionTrial],
) -> dict:
    gaps = [trial.expected_surplus_gap for trial in trials if trial.expected_surplus_gap is not None]
    first_errors = [trial.first_price_error for trial in trials if trial.first_price_error is not None]
    second_errors = [trial.second_price_error for trial in trials if trial.second_price_error is not None]
    prior_missable = [
        trial
        for trial in trials
        if _price_pair_distance(
            trial.prior_first_price,
            trial.prior_second_price,
            trial.oracle_first_price,
            trial.oracle_second_price,
        )
        > 1e-9
    ]
    single_cue_missable = [
        trial
        for trial in trials
        if _price_pair_distance(
            trial.single_cue_first_price,
            trial.single_cue_second_price,
            trial.oracle_first_price,
            trial.oracle_second_price,
        )
        > 1e-9
    ]
    single_offer_missable = [
        trial
        for trial in trials
        if _price_pair_distance(
            trial.single_offer_price,
            trial.single_offer_price,
            trial.oracle_first_price,
            trial.oracle_second_price,
        )
        > 1e-9
    ]
    return {
        "task": "belief_bargaining_interaction",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_surplus_gap": mean(gaps),
        "mean_expected_surplus_gap_ci95": bootstrap_mean_ci(gaps),
        "mean_first_price_error": mean(first_errors),
        "mean_second_price_error": mean(second_errors),
        "prior_plan_miss_rate": (
            sum(trial.prior_miss for trial in prior_missable) / len(prior_missable)
            if prior_missable
            else 0.0
        ),
        "single_cue_plan_miss_rate": (
            sum(trial.single_cue_miss for trial in single_cue_missable) / len(single_cue_missable)
            if single_cue_missable
            else 0.0
        ),
        "single_offer_miss_rate": (
            sum(trial.single_offer_miss for trial in single_offer_missable) / len(single_offer_missable)
            if single_offer_missable
            else 0.0
        ),
        "trials": [_interaction_trial_json(trial) for trial in trials],
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


def _interaction_prompt(case: BargainingInteractionCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"seller_cost={case.seller_cost:.2f}",
        f"observed_signal_sequence={','.join(case.observed_signals)}",
        f"second_round_discount={case.second_round_discount:.4f}",
        f"second_round_delay_cost={case.second_round_delay_cost:.2f}",
        "Buyer states:",
    ]
    for state in case.states:
        likelihoods = _state_likelihoods_for_signals(case.observed_signals, state)
        lines.append(
            "  "
            + " ".join(
                [
                    f"state_id={state.state_id}",
                    f"buyer_wtp={state.buyer_wtp:.2f}",
                    f"prior_probability={state.prior_probability:.4f}",
                    f"likelihood_of_observed_cue={likelihoods[0]:.4f}",
                    f"signal_likelihoods={','.join(f'{value:.4f}' for value in likelihoods)}",
                ]
            )
        )
    lines.extend(
        [
            "Buyer does not see the fallback price before deciding on the opening price.",
            "If opening price <= buyer_wtp, the buyer accepts immediately and seller surplus is opening price - seller_cost.",
            "If opening price > buyer_wtp, the buyer rejects; then the fallback price can still be accepted if fallback price <= buyer_wtp.",
            "Fallback surplus is discounted by second_round_discount and then reduced by second_round_delay_cost.",
            "Choose both prices after updating on all observed signals and accounting for what a rejection reveals.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: BeliefBargainingTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _interaction_trial_json(trial: BargainingInteractionTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _signals(case: BeliefBargainingCase) -> tuple[str, ...]:
    return case.observed_signals or (case.observed_cue,)


def _conditions(case: BeliefBargainingCase) -> tuple[str, ...]:
    return ("base", "posterior_scaffold") if case.strategic_likelihood else ("base",)


def _state_likelihoods(case: BeliefBargainingCase, state: BuyerState) -> tuple[float, ...]:
    signals = _signals(case)
    return _state_likelihoods_for_signals(signals, state)


def _state_likelihoods_for_signals(signals: tuple[str, ...], state: BuyerState) -> tuple[float, ...]:
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


def _interaction_probabilities(
    case: BargainingInteractionCase,
    *,
    use_posterior: bool,
    signal_count: int | None,
) -> dict[str, float]:
    if not use_posterior:
        return {state.state_id: state.prior_probability for state in case.states}
    weights = {}
    for state in case.states:
        likelihoods = _state_likelihoods_for_signals(case.observed_signals, state)
        if signal_count is not None:
            likelihoods = likelihoods[:signal_count]
        product = 1.0
        for likelihood in likelihoods:
            product *= likelihood
        weights[state.state_id] = state.prior_probability * product
    total = sum(weights.values())
    if total <= 0:
        return {state.state_id: state.prior_probability for state in case.states}
    return {state_id: weight / total for state_id, weight in weights.items()}


def _interaction_candidate_prices(case: BargainingInteractionCase) -> list[float]:
    candidates = {case.seller_cost, *(state.buyer_wtp for state in case.states)}
    for price in range(int(case.seller_cost), int(max(candidates)) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _price_pair_distance(
    first_a: float,
    second_a: float,
    first_b: float,
    second_b: float,
) -> float:
    return abs(first_a - first_b) + abs(second_a - second_b)


def _interaction_baseline_miss(
    chosen_first: float | None,
    chosen_second: float | None,
    oracle_first: float,
    oracle_second: float,
    baseline_first: float,
    baseline_second: float,
) -> bool:
    if chosen_first is None or chosen_second is None:
        return False
    if _price_pair_distance(baseline_first, baseline_second, oracle_first, oracle_second) <= 1e-9:
        return False
    chosen_to_baseline = _price_pair_distance(
        chosen_first,
        chosen_second,
        baseline_first,
        baseline_second,
    )
    chosen_to_oracle = _price_pair_distance(
        chosen_first,
        chosen_second,
        oracle_first,
        oracle_second,
    )
    return chosen_to_baseline < chosen_to_oracle
