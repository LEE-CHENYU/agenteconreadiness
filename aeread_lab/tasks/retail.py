from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


RETAIL_SYSTEM = (
    "TASK: retail_order\n"
    "Choose an integer initial inventory order quantity. "
    "Return one final line only: FINAL_ORDER: <integer>. Do not explain or show calculations."
)


@dataclass(frozen=True)
class DemandState:
    units: int
    probability: float


@dataclass(frozen=True)
class RetailPeriod:
    label: str
    fixed_cost_due: float
    demand_states: tuple[DemandState, ...]


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
    periods: tuple[RetailPeriod, ...] = ()
    carrying_cost_per_unsold: float = 0.0
    terminal_unit_value: float = 0.0


@dataclass
class RetailTrial:
    case: RetailCase
    oracle_order: int
    ev_order: int
    myopic_order: int
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
    RetailCase(
        key="route_expansion_restock_lag",
        real_case="route expansion where a large opening buy must survive a later demand drought",
        cash_on_hand=3100.0,
        unit_cost=21.0,
        sale_price=39.0,
        fixed_cost_due=650.0,
        min_cash_reserve=1200.0,
        max_order=95,
        demand_states=(DemandState(32, 0.30), DemandState(58, 0.50), DemandState(82, 0.20)),
        periods=(
            RetailPeriod(
                "launch",
                650.0,
                (DemandState(32, 0.30), DemandState(58, 0.50), DemandState(82, 0.20)),
            ),
            RetailPeriod(
                "post_promo",
                720.0,
                (DemandState(8, 0.35), DemandState(24, 0.45), DemandState(46, 0.20)),
            ),
            RetailPeriod(
                "renewal",
                830.0,
                (DemandState(12, 0.25), DemandState(34, 0.50), DemandState(60, 0.25)),
            ),
        ),
        carrying_cost_per_unsold=2.25,
        terminal_unit_value=4.0,
    ),
    RetailCase(
        key="holiday_bundle_cash_buffer",
        real_case="holiday bundle inventory with payroll and storage costs before final liquidation",
        cash_on_hand=5200.0,
        unit_cost=46.0,
        sale_price=88.0,
        fixed_cost_due=1050.0,
        min_cash_reserve=2100.0,
        max_order=85,
        demand_states=(DemandState(18, 0.25), DemandState(42, 0.45), DemandState(70, 0.30)),
        periods=(
            RetailPeriod(
                "black_friday",
                1050.0,
                (DemandState(18, 0.25), DemandState(42, 0.45), DemandState(70, 0.30)),
            ),
            RetailPeriod(
                "december",
                980.0,
                (DemandState(14, 0.25), DemandState(38, 0.50), DemandState(64, 0.25)),
            ),
            RetailPeriod(
                "january_returns",
                1250.0,
                (DemandState(6, 0.40), DemandState(22, 0.40), DemandState(44, 0.20)),
            ),
        ),
        carrying_cost_per_unsold=3.80,
        terminal_unit_value=12.0,
    ),
]


def terminal_cash(case: RetailCase, order: int, demand: int) -> float:
    sold = min(order, demand)
    return case.cash_on_hand - case.fixed_cost_due - order * case.unit_cost + sold * case.sale_price


def expected_terminal_cash(case: RetailCase, order: int) -> float:
    return sum(probability * cash for probability, cash, _ in terminal_outcomes(case, order))


def ruin_probability(case: RetailCase, order: int) -> float:
    return sum(probability for probability, _, ruined in terminal_outcomes(case, order) if ruined)


def case_periods(case: RetailCase) -> tuple[RetailPeriod, ...]:
    if case.periods:
        return case.periods
    return (RetailPeriod("cycle_1", case.fixed_cost_due, case.demand_states),)


def terminal_outcomes(case: RetailCase, order: int) -> list[tuple[float, float, bool]]:
    paths = [(1.0, case.cash_on_hand - order * case.unit_cost, float(order), False)]
    for period in case_periods(case):
        next_paths: list[tuple[float, float, bool]] = []
        for path_probability, path_cash, path_inventory, already_ruined in paths:
            for state in period.demand_states:
                sold = min(path_inventory, float(state.units))
                inventory_after = path_inventory - sold
                cash_after = (
                    path_cash
                    - period.fixed_cost_due
                    + sold * case.sale_price
                    - inventory_after * case.carrying_cost_per_unsold
                )
                ruined = already_ruined or cash_after < case.min_cash_reserve
                next_paths.append((path_probability * state.probability, cash_after, inventory_after, ruined))
        paths = next_paths
    return [
        (probability, cash + inventory * case.terminal_unit_value, ruined)
        for probability, cash, inventory, ruined in paths
    ]


def ev_order(case: RetailCase) -> int:
    return max(range(case.max_order + 1), key=lambda q: expected_terminal_cash(case, q))


def oracle_order(case: RetailCase) -> int:
    feasible = [q for q in range(case.max_order + 1) if ruin_probability(case, q) <= 0.0]
    if not feasible:
        return 0
    return max(feasible, key=lambda q: expected_terminal_cash(case, q))


def myopic_order(case: RetailCase) -> int:
    first_period = case_periods(case)[0]
    one_cycle_case = RetailCase(
        key=case.key,
        real_case=case.real_case,
        cash_on_hand=case.cash_on_hand,
        unit_cost=case.unit_cost,
        sale_price=case.sale_price,
        fixed_cost_due=first_period.fixed_cost_due,
        min_cash_reserve=case.min_cash_reserve,
        max_order=case.max_order,
        demand_states=first_period.demand_states,
    )
    return oracle_order(one_cycle_case)


def run_retail_game(agent: Agent, cases: list[RetailCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[RetailTrial] = []
    for case in cases:
        oracle = oracle_order(case)
        ev = ev_order(case)
        myopic = myopic_order(case)
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
                myopic_order=myopic,
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
    multi_period_trials = [trial for trial in trials if len(case_periods(trial.case)) > 1]
    multi_period_gaps = [
        trial.expected_cash_gap
        for trial in multi_period_trials
        if trial.expected_cash_gap is not None
    ]
    multi_period_missable = [
        trial for trial in multi_period_trials if trial.myopic_order != trial.oracle_order
    ]
    multi_period_misses = sum(
        trial.chosen_order is not None and trial.chosen_order != trial.oracle_order
        for trial in multi_period_missable
    )
    myopic_gaps = [
        abs(trial.myopic_order - trial.oracle_order) / max(1.0, trial.case.max_order)
        for trial in multi_period_trials
    ]
    return {
        "task": "retail",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_expected_cash_gap": mean(gaps),
        "mean_order_error": mean(errors),
        "mean_ruin_probability": mean(ruins),
        "mean_ruin_probability_ci95": bootstrap_mean_ci(ruins),
        "mean_myopic_order_gap": mean(myopic_gaps),
        "mean_multi_period_cash_gap": mean(multi_period_gaps),
        "multi_period_miss_rate": (
            multi_period_misses / len(multi_period_missable) if multi_period_missable else 0.0
        ),
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
        f"planning_horizon={len(case_periods(case))}",
        f"carrying_cost_per_unsold={case.carrying_cost_per_unsold:.2f}",
        f"terminal_unit_value={case.terminal_unit_value:.2f}",
        "Demand states by period:",
    ]
    for index, period in enumerate(case_periods(case), start=1):
        lines.append(f"period={index} label={period.label} fixed_cost_due={period.fixed_cost_due:.2f}")
        for state in period.demand_states:
            lines.append(f"  demand_units={state.units} probability={state.probability:.4f}")
    lines.extend(
        [
            "Unsold units carry into the next period.",
            "At the start, cash is reduced by order*unit_cost. In each period, pay that period's fixed_cost_due, sell min(inventory, demand_units), carry unsold units, and pay carrying_cost_per_unsold for each unsold unit.",
            "After the final period, unsold units receive terminal_unit_value each.",
            "Hard survival constraint: cash after every period must stay at or above min_cash_reserve in every listed demand path.",
            "Choose the initial order quantity that maximizes expected final cash subject to the survival constraint.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: RetailTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
