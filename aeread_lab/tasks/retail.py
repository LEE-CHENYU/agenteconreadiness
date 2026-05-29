from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


RETAIL_SYSTEM = (
    "TASK: retail_order\n"
    "Choose an integer inventory order quantity for the next cycle. "
    "Return one final line only: FINAL_ORDER: <integer>."
)


@dataclass(frozen=True)
class DemandState:
    units: int
    probability: float


@dataclass(frozen=True)
class RetailCase:
    key: str
    real_case: str
    cash_on_hand: float
    unit_cost: float
    sale_price: float
    fixed_cost_due: float
    min_cash_reserve: float
    max_order: int
    demand_states: tuple[DemandState, ...]


@dataclass
class RetailTrial:
    case: RetailCase
    oracle_order: int
    ev_order: int
    chosen_order: int | None
    expected_cash_gap: float | None
    ruin_probability: float | None
    order_error: float | None
    raw_response: str


DEFAULT_CASES = [
    RetailCase(
        key="vending_snacks",
        real_case="cash-constrained vending route with uncertain weekly demand",
        cash_on_hand=700.0,
        unit_cost=4.0,
        sale_price=8.0,
        fixed_cost_due=320.0,
        min_cash_reserve=450.0,
        max_order=120,
        demand_states=(DemandState(35, 0.35), DemandState(70, 0.45), DemandState(105, 0.20)),
    ),
    RetailCase(
        key="seasonal_merch",
        real_case="seasonal merchandise buy where unsold stock has no salvage value",
        cash_on_hand=1800.0,
        unit_cost=18.0,
        sale_price=35.0,
        fixed_cost_due=900.0,
        min_cash_reserve=900.0,
        max_order=80,
        demand_states=(DemandState(20, 0.30), DemandState(45, 0.50), DemandState(75, 0.20)),
    ),
    RetailCase(
        key="runway_limited_launch",
        real_case="startup launch inventory with a hard payroll/runway reserve",
        cash_on_hand=2600.0,
        unit_cost=32.0,
        sale_price=62.0,
        fixed_cost_due=1200.0,
        min_cash_reserve=1300.0,
        max_order=70,
        demand_states=(DemandState(18, 0.25), DemandState(42, 0.55), DemandState(66, 0.20)),
    ),
]


def terminal_cash(case: RetailCase, order: int, demand: int) -> float:
    sold = min(order, demand)
    return case.cash_on_hand - case.fixed_cost_due - order * case.unit_cost + sold * case.sale_price


def expected_terminal_cash(case: RetailCase, order: int) -> float:
    return sum(state.probability * terminal_cash(case, order, state.units) for state in case.demand_states)


def ruin_probability(case: RetailCase, order: int) -> float:
    return sum(
        state.probability
        for state in case.demand_states
        if terminal_cash(case, order, state.units) < case.min_cash_reserve
    )


def ev_order(case: RetailCase) -> int:
    return max(range(case.max_order + 1), key=lambda q: expected_terminal_cash(case, q))


def oracle_order(case: RetailCase) -> int:
    feasible = [q for q in range(case.max_order + 1) if ruin_probability(case, q) <= 0.0]
    if not feasible:
        return 0
    return max(feasible, key=lambda q: expected_terminal_cash(case, q))


def run_retail_game(agent: Agent, cases: list[RetailCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[RetailTrial] = []
    for case in cases:
        oracle = oracle_order(case)
        ev = ev_order(case)
        response = agent.complete(RETAIL_SYSTEM, _prompt(case))
        parsed = parse_float("FINAL_ORDER", response)
        chosen = int(round(clamp(parsed, 0.0, float(case.max_order)))) if parsed is not None else None
        gap = expected_terminal_cash(case, oracle) - expected_terminal_cash(case, chosen) if chosen is not None else None
        ruin = ruin_probability(case, chosen) if chosen is not None else None
        error = abs(chosen - oracle) / max(1.0, case.max_order) if chosen is not None else None
        trials.append(
            RetailTrial(
                case=case,
                oracle_order=oracle,
                ev_order=ev,
                chosen_order=chosen,
                expected_cash_gap=gap,
                ruin_probability=ruin,
                order_error=error,
                raw_response=response,
            )
        )
    return summarize_retail_trials(agent.name, trials)


def summarize_retail_trials(agent_name: str, trials: list[RetailTrial]) -> dict:
    gaps = [trial.expected_cash_gap for trial in trials if trial.expected_cash_gap is not None]
    errors = [trial.order_error for trial in trials if trial.order_error is not None]
    ruins = [trial.ruin_probability for trial in trials if trial.ruin_probability is not None]
    return {
        "task": "retail",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_cash_gap": mean(gaps),
        "mean_order_error": mean(errors),
        "mean_ruin_probability": mean(ruins),
        "mean_ruin_probability_ci95": bootstrap_mean_ci(ruins),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: RetailCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"cash_on_hand={case.cash_on_hand:.2f}",
        f"unit_cost={case.unit_cost:.2f}",
        f"sale_price={case.sale_price:.2f}",
        f"fixed_cost_due={case.fixed_cost_due:.2f}",
        f"min_cash_reserve={case.min_cash_reserve:.2f}",
        f"max_order={case.max_order}",
        "Demand states:",
    ]
    for state in case.demand_states:
        lines.append(f"  demand_units={state.units} probability={state.probability:.4f}")
    lines.extend(
        [
            "Unsold units have no salvage value this cycle.",
            "Terminal cash = cash_on_hand - fixed_cost_due - order*unit_cost + sold_units*sale_price.",
            "Hard survival constraint: terminal cash must stay at or above min_cash_reserve in every listed demand state.",
            "Choose the order quantity that maximizes expected terminal cash subject to the survival constraint.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: RetailTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
