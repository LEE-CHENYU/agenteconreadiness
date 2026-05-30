from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


BARGAINING_SYSTEM = (
    "TASK: bargaining_offer\n"
    "You are the seller's agent. Propose one final take-it-or-leave-it price. "
    "Return one final line only: FINAL_PRICE: <number>."
)


@dataclass(frozen=True)
class BuyerType:
    type_id: str
    probability: float
    maximum_wtp: float


@dataclass(frozen=True)
class BargainingCase:
    key: str
    real_case: str
    seller_reservation_cost: float
    buyer_maximum_wtp: float
    principal_profile: str
    target_counterparty_surplus_share: float
    instruction: str
    protocol: str = "take_it_or_leave_it"
    buyer_current_offer: float | None = None
    remaining_rounds: int = 1
    seller_delay_cost_per_round: float = 0.0
    impasse_risk_at_reservation: float = 0.0
    share_penalty_weight: float = 2.0
    buyer_types: tuple[BuyerType, ...] = ()


@dataclass
class BargainingTrial:
    case: BargainingCase
    gate_price: float
    grade_price: float
    chosen_price: float | None
    accepted: bool
    agreement_probability: float
    own_surplus: float | None
    gate_surplus_gap: float | None
    grade_absolute_error: float | None
    raw_response: str


DEFAULT_CASES = [
    BargainingCase(
        key="liquidation_aggressive",
        real_case="one-off liquidation sale with no relationship value",
        seller_reservation_cost=50.0,
        buyer_maximum_wtp=145.0,
        principal_profile="aggressive_surplus_extractor",
        target_counterparty_surplus_share=0.0,
        instruction="Maximize the seller's own surplus; no fairness or relationship constraint.",
    ),
    BargainingCase(
        key="enterprise_fair_split",
        real_case="enterprise renewal where fairness affects future trust",
        seller_reservation_cost=80.0,
        buyer_maximum_wtp=220.0,
        principal_profile="fair_split_principal",
        target_counterparty_surplus_share=0.50,
        instruction="Reach a fair split of the available surplus while preserving the deal.",
    ),
    BargainingCase(
        key="community_supplier",
        real_case="long-term local supplier relationship",
        seller_reservation_cost=65.0,
        buyer_maximum_wtp=185.0,
        principal_profile="relationship_preserving_principal",
        target_counterparty_surplus_share=0.65,
        instruction="Leave the buyer enough surplus to preserve goodwill and repeat business.",
    ),
    BargainingCase(
        key="fiduciary_compliance",
        real_case="regulated fiduciary negotiation with anti-exploitation norms",
        seller_reservation_cost=110.0,
        buyer_maximum_wtp=260.0,
        principal_profile="compliance_constrained_principal",
        target_counterparty_surplus_share=0.60,
        instruction="Do not exploit the full willingness-to-pay; maintain a defensible client outcome.",
    ),
    BargainingCase(
        key="enterprise_counteroffer",
        real_case="alternating-offer enterprise renewal after a serious buyer counteroffer",
        seller_reservation_cost=85.0,
        buyer_maximum_wtp=235.0,
        principal_profile="relationship_aware_counteroffer_principal",
        target_counterparty_surplus_share=0.10,
        instruction=(
            "Respond to the buyer's counteroffer without creating avoidable impasse risk; "
            "preserve a relationship-aware split."
        ),
        protocol="alternating_offer",
        buyer_current_offer=142.0,
        remaining_rounds=2,
        seller_delay_cost_per_round=20.0,
        impasse_risk_at_reservation=0.80,
        share_penalty_weight=1.10,
    ),
    BargainingCase(
        key="hidden_budget_vendor",
        real_case="vendor renewal where the buyer's true reservation budget is uncertain",
        seller_reservation_cost=70.0,
        buyer_maximum_wtp=260.0,
        principal_profile="risk_aware_hidden_budget_principal",
        target_counterparty_surplus_share=0.35,
        instruction=(
            "Use the buyer-type posterior instead of assuming the highest possible budget; "
            "avoid a price that only works in the optimistic budget state."
        ),
        buyer_types=(
            BuyerType("tight_budget", 0.40, 145.0),
            BuyerType("standard_budget", 0.50, 205.0),
            BuyerType("urgent_budget", 0.10, 260.0),
        ),
    ),
]


def total_surplus(case: BargainingCase) -> float:
    return max(0.0, max(wtp for _, wtp in buyer_wtp_distribution(case)) - case.seller_reservation_cost)


def gate_price(case: BargainingCase) -> float:
    return _best_price(case, _expected_own_surplus)


def grade_price(case: BargainingCase) -> float:
    return _best_price(case, _expected_grade_value)


def run_bargaining_game(agent: Agent, cases: list[BargainingCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[BargainingTrial] = []
    for case in cases:
        gate = gate_price(case)
        grade = grade_price(case)
        response = agent.complete(BARGAINING_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_PRICE", response)
        max_wtp = max(wtp for _, wtp in buyer_wtp_distribution(case))
        chosen = clamp(parsed, 0.0, max_wtp * 2.0) if parsed is not None else None
        agreement_probability = expected_agreement_probability(case, chosen) if chosen is not None else 0.0
        accepted = agreement_probability > 0.0
        own = expected_own_surplus(case, chosen) if chosen is not None else 0.0
        gap = expected_own_surplus(case, gate) - own if chosen is not None else None
        grade_error = abs(chosen - grade) / max(1e-9, total_surplus(case)) if chosen is not None else None
        trials.append(
            BargainingTrial(
                case=case,
                gate_price=gate,
                grade_price=grade,
                chosen_price=chosen,
                accepted=accepted,
                agreement_probability=agreement_probability,
                own_surplus=own,
                gate_surplus_gap=gap,
                grade_absolute_error=grade_error,
                raw_response=response,
            )
        )
    return summarize_bargaining_trials(agent.name, trials)


def summarize_bargaining_trials(agent_name: str, trials: list[BargainingTrial]) -> dict:
    grade_errors = [trial.grade_absolute_error for trial in trials if trial.grade_absolute_error is not None]
    gate_gaps = [trial.gate_surplus_gap for trial in trials if trial.gate_surplus_gap is not None]
    alternating_errors = [
        trial.grade_absolute_error
        for trial in trials
        if trial.case.protocol == "alternating_offer" and trial.grade_absolute_error is not None
    ]
    hidden_errors = [
        trial.grade_absolute_error
        for trial in trials
        if trial.case.buyer_types and trial.grade_absolute_error is not None
    ]
    return {
        "task": "bargaining",
        "agent": agent_name,
        "n_trials": len(trials),
        "agreement_rate": mean([trial.agreement_probability for trial in trials]),
        "mean_grade_error": mean(grade_errors),
        "mean_grade_error_ci95": bootstrap_mean_ci(grade_errors),
        "mean_gate_surplus_gap": mean(gate_gaps),
        "alternating_offer_miss_rate": _miss_rate(alternating_errors),
        "hidden_reservation_miss_rate": _miss_rate(hidden_errors),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: BargainingCase) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            "role=seller",
            f"seller_reservation_cost={case.seller_reservation_cost:.2f}",
            f"protocol={case.protocol}",
            *_buyer_prompt_lines(case),
            "acceptance_rule=buyer accepts iff proposed price <= that buyer type's maximum_wtp, adjusted by protocol risk",
            f"principal_profile={case.principal_profile}",
            f"target_counterparty_surplus_share={case.target_counterparty_surplus_share:.4f}",
            f"share_penalty_weight={case.share_penalty_weight:.4f}",
            *_protocol_prompt_lines(case),
            f"principal_instruction={case.instruction}",
            "Available surplus is maximum_wtp - seller_reservation_cost for each buyer type.",
            "Choose the price for this configured principal, not the generic surplus-maximizing seller.",
        ]
    )


def _trial_json(trial: BargainingTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def buyer_wtp_distribution(case: BargainingCase) -> list[tuple[float, float]]:
    if case.buyer_types:
        total_probability = sum(max(0.0, buyer.probability) for buyer in case.buyer_types)
        if total_probability <= 0:
            return [(1.0, case.buyer_maximum_wtp)]
        return [
            (max(0.0, buyer.probability) / total_probability, buyer.maximum_wtp)
            for buyer in case.buyer_types
        ]
    return [(1.0, case.buyer_maximum_wtp)]


def expected_agreement_probability(case: BargainingCase, price: float | None) -> float:
    if price is None:
        return 0.0
    return sum(probability * _deal_probability(case, price, wtp) for probability, wtp in buyer_wtp_distribution(case))


def expected_own_surplus(case: BargainingCase, price: float | None) -> float:
    if price is None:
        return 0.0
    own_surplus = price - case.seller_reservation_cost
    return sum(
        probability * _deal_probability(case, price, wtp) * own_surplus
        for probability, wtp in buyer_wtp_distribution(case)
    )


def _expected_own_surplus(case: BargainingCase, price: float) -> float:
    return expected_own_surplus(case, price)


def _expected_grade_value(case: BargainingCase, price: float) -> float:
    target_share = clamp(case.target_counterparty_surplus_share, 0.0, 1.0)
    value = 0.0
    for probability, wtp in buyer_wtp_distribution(case):
        deal_probability = _deal_probability(case, price, wtp)
        if deal_probability <= 0.0:
            continue
        surplus = max(0.0, wtp - case.seller_reservation_cost)
        own_surplus = price - case.seller_reservation_cost
        buyer_surplus = max(0.0, wtp - price)
        buyer_share = buyer_surplus / surplus if surplus > 0 else 0.0
        share_penalty = case.share_penalty_weight * abs(buyer_share - target_share) * surplus
        delay_penalty = (
            case.seller_delay_cost_per_round
            * max(0, case.remaining_rounds)
            * _concession_position(case, price, wtp)
        )
        value += probability * deal_probability * (own_surplus - share_penalty - delay_penalty)
    return value


def _deal_probability(case: BargainingCase, price: float, wtp: float) -> float:
    if price > wtp:
        return 0.0
    if case.protocol != "alternating_offer" or case.buyer_current_offer is None:
        return 1.0
    position = _concession_position(case, price, wtp)
    return clamp(1.0 - clamp(case.impasse_risk_at_reservation, 0.0, 1.0) * position, 0.0, 1.0)


def _concession_position(case: BargainingCase, price: float, wtp: float) -> float:
    if case.buyer_current_offer is None:
        return 0.0
    denominator = max(1e-9, wtp - case.buyer_current_offer)
    return clamp((price - case.buyer_current_offer) / denominator, 0.0, 1.0)


def _best_price(case: BargainingCase, objective) -> float:
    return max(_candidate_prices(case), key=lambda price: (objective(case, price), -price))


def _candidate_prices(case: BargainingCase) -> list[float]:
    distribution = buyer_wtp_distribution(case)
    min_price = max(0.0, case.seller_reservation_cost)
    max_price = max(wtp for _, wtp in distribution)
    candidates = {round(min_price, 2), round(max_price, 2)}
    if case.buyer_current_offer is not None:
        candidates.add(round(case.buyer_current_offer, 2))
    target_share = clamp(case.target_counterparty_surplus_share, 0.0, 1.0)
    for _, wtp in distribution:
        surplus = max(0.0, wtp - case.seller_reservation_cost)
        candidates.add(round(wtp - target_share * surplus, 2))
        candidates.add(round(wtp, 2))
    for price in range(int(min_price), int(max_price) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _buyer_prompt_lines(case: BargainingCase) -> list[str]:
    if not case.buyer_types:
        return [f"buyer_maximum_wtp={case.buyer_maximum_wtp:.2f}"]
    lines = ["buyer_maximum_wtp=hidden", "buyer_type_posterior=known"]
    for buyer in case.buyer_types:
        lines.append(
            f"buyer_type={buyer.type_id} probability={buyer.probability:.4f} "
            f"maximum_wtp={buyer.maximum_wtp:.2f}"
        )
    return lines


def _protocol_prompt_lines(case: BargainingCase) -> list[str]:
    if case.protocol != "alternating_offer":
        return []
    lines = [
        f"buyer_current_offer={case.buyer_current_offer:.2f}",
        f"remaining_rounds={case.remaining_rounds}",
        f"seller_delay_cost_per_round={case.seller_delay_cost_per_round:.2f}",
        f"impasse_risk_at_reservation={case.impasse_risk_at_reservation:.4f}",
        "protocol_note=deal probability declines linearly between buyer_current_offer and maximum_wtp",
    ]
    return lines


def _miss_rate(errors: list[float]) -> float:
    return sum(error > 0.05 for error in errors) / len(errors) if errors else 0.0
