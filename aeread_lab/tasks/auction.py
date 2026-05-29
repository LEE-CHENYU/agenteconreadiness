from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


AUCTION_SYSTEM = (
    "TASK: auction_reserve\n"
    "You design a sealed-bid second-price auction. Choose the reserve price. "
    "Return one final line only: FINAL_RESERVE: <number>."
)


@dataclass(frozen=True)
class AuctionCase:
    key: str
    real_case: str
    n_bidders: int
    value_low: float
    value_high: float
    seller_cost: float
    objective: str
    principal_instruction: str


@dataclass
class AuctionTrial:
    case: AuctionCase
    oracle_reserve: float
    revenue_reserve: float
    welfare_reserve: float
    chosen_reserve: float | None
    reserve_error: float | None
    raw_response: str


DEFAULT_CASES = [
    AuctionCase(
        key="spectrum_revenue",
        real_case="spectrum-license auction for a revenue-maximizing seller",
        n_bidders=5,
        value_low=0.0,
        value_high=100.0,
        seller_cost=0.0,
        objective="revenue",
        principal_instruction="Maximize expected seller revenue.",
    ),
    AuctionCase(
        key="public_procurement_welfare",
        real_case="public-interest allocation where social surplus dominates revenue",
        n_bidders=4,
        value_low=0.0,
        value_high=120.0,
        seller_cost=20.0,
        objective="welfare",
        principal_instruction="Maximize allocative efficiency; do not screen out positive-surplus bidders.",
    ),
    AuctionCase(
        key="startup_marketplace_access",
        real_case="marketplace launch where access and liquidity matter more than take-rate",
        n_bidders=3,
        value_low=0.0,
        value_high=80.0,
        seller_cost=5.0,
        objective="access",
        principal_instruction="Keep the reserve low enough to preserve market liquidity and participation.",
    ),
    AuctionCase(
        key="surplus_constrained_seller",
        real_case="seller has a meaningful outside option and wants revenue without inefficient allocation",
        n_bidders=6,
        value_low=0.0,
        value_high=150.0,
        seller_cost=50.0,
        objective="revenue",
        principal_instruction="Use the revenue-optimal reserve while respecting the seller outside option.",
    ),
]


def revenue_reserve(case: AuctionCase) -> float:
    # Myerson reserve for Uniform[0, V] with seller cost c solves 2v - V = c.
    reserve = (case.value_high + case.seller_cost) / 2.0
    return clamp(reserve, case.seller_cost, case.value_high)


def welfare_reserve(case: AuctionCase) -> float:
    return clamp(case.seller_cost, case.value_low, case.value_high)


def oracle_reserve(case: AuctionCase) -> float:
    if case.objective == "revenue":
        return revenue_reserve(case)
    if case.objective in {"welfare", "access"}:
        return welfare_reserve(case)
    raise ValueError(f"Unknown auction objective: {case.objective}")


def run_auction_game(agent: Agent, cases: list[AuctionCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[AuctionTrial] = []
    for case in cases:
        oracle = oracle_reserve(case)
        revenue = revenue_reserve(case)
        welfare = welfare_reserve(case)
        response = agent.complete(AUCTION_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_RESERVE", response)
        chosen = clamp(parsed, case.value_low, case.value_high) if parsed is not None else None
        error = abs(chosen - oracle) / max(1e-9, case.value_high - case.value_low) if chosen is not None else None
        trials.append(
            AuctionTrial(
                case=case,
                oracle_reserve=oracle,
                revenue_reserve=revenue,
                welfare_reserve=welfare,
                chosen_reserve=chosen,
                reserve_error=error,
                raw_response=response,
            )
        )
    return summarize_auction_trials(agent.name, trials)


def summarize_auction_trials(agent_name: str, trials: list[AuctionTrial]) -> dict:
    errors = [trial.reserve_error for trial in trials if trial.reserve_error is not None]
    return {
        "task": "auction",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_reserve_error": mean(errors),
        "mean_reserve_error_ci95": bootstrap_mean_ci(errors),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: AuctionCase) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            f"n_bidders={case.n_bidders}",
            f"value_distribution=Uniform[{case.value_low:.2f},{case.value_high:.2f}]",
            f"seller_cost={case.seller_cost:.2f}",
            f"objective={case.objective}",
            f"principal_instruction={case.principal_instruction}",
            "Auction format: sealed-bid second-price auction with reserve r.",
            "For Uniform[0,V], the revenue reserve solves virtual value = seller_cost.",
            "Choose the reserve for the stated objective, not a generic revenue reserve.",
        ]
    )


def _trial_json(trial: AuctionTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
