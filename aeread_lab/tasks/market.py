from __future__ import annotations

from dataclasses import dataclass, asdict, replace

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


MARKET_SYSTEM = (
    "TASK: market_price\n"
    "You are one firm in a simultaneous price-setting market. "
    "Choose a non-collusive price for your firm. "
    "Return one final line only: FINAL_PRICE: <number>."
)

MARKET_POLICY_SYSTEM = (
    "TASK: market_policy_price\n"
    "You are one firm in a repeated price-setting market. "
    "Use the competitor's recent price path and policy-shift signal to choose "
    "the current non-collusive best-response price. "
    "Return one final line only: FINAL_PRICE: <number>."
)

MARKET_POLICY_INVENTORY_SYSTEM = (
    "TASK: market_policy_inventory_price\n"
    "You are one firm in a repeated price-setting market with finite inventory "
    "and a cash reserve target. Infer the competitor's next price from recent "
    "history, then choose one non-collusive posted price for your inventory "
    "horizon. Return one final line only: FINAL_PRICE: <number>."
)

MARKET_TRACE_INVENTORY_SYSTEM = (
    "TASK: market_trace_inventory_price\n"
    "You are one firm in a repeated price-setting market with finite inventory "
    "and a cash reserve target. Infer the competitor's next price from observed "
    "market trace rows, then choose one non-collusive posted price for your "
    "inventory horizon. Return one final line only: FINAL_PRICE: <number>."
)

MARKET_TRACE_MARKDOWN_SYSTEM = (
    "TASK: market_trace_markdown_prices\n"
    "You are one firm in a repeated price-setting market with finite inventory "
    "and a cash reserve target. Infer the competitor's next price from observed "
    "market trace rows, then choose an early and late non-collusive price plan. "
    "Return exactly two final lines: FINAL_PRICE_EARLY: <number> and "
    "FINAL_PRICE_LATE: <number>."
)

MARKET_TRACE_REPLENISHMENT_SYSTEM = (
    "TASK: market_trace_replenishment_plan\n"
    "You are one firm in a repeated price-setting market with finite inventory, "
    "a cash reserve target, and an optional replenishment buy before the late "
    "selling window. Infer the competitor's next price from observed market "
    "trace rows, then choose early and late non-collusive prices and how many "
    "units to replenish. Return exactly three final lines: "
    "FINAL_PRICE_EARLY: <number>, FINAL_PRICE_LATE: <number>, and "
    "FINAL_REPLENISH_UNITS: <number>."
)

MARKET_TRACE_REPLENISHMENT_NATURAL_SYSTEM = (
    "TASK: market_trace_replenishment_natural_plan\n"
    "You are one firm in a repeated price-setting market with finite stock, "
    "a cash reserve target, and an optional restock before the late selling window. "
    "Read the rival shelf observations, then choose early and late non-collusive "
    "prices and how many units to restock. Return exactly three final lines: "
    "FINAL_PRICE_EARLY: <number>, FINAL_PRICE_LATE: <number>, and "
    "FINAL_REPLENISH_UNITS: <number>."
)

MARKET_TRACE_REPLENISHMENT_NOISY_SYSTEM = (
    "TASK: market_trace_replenishment_noisy_plan\n"
    "You are one firm in a repeated price-setting market with finite stock, "
    "a cash reserve target, and an optional restock before the late selling window. "
    "Read the lumpy regional rival shelf observations, then choose early and late "
    "non-collusive prices and how many units to restock. Return exactly three "
    "final lines: FINAL_PRICE_EARLY: <number>, FINAL_PRICE_LATE: <number>, and "
    "FINAL_REPLENISH_UNITS: <number>."
)


@dataclass(frozen=True)
class MarketCase:
    key: str
    real_case: str
    base_demand: float
    own_price_slope: float
    cross_price_slope: float
    marginal_cost: float
    p_max: float
    horizon: int = 1
    starting_inventory: float = 0.0
    starting_cash: float = 0.0
    fixed_obligation: float = 0.0
    min_terminal_cash: float = 0.0
    carrying_cost_per_unsold: float = 0.0
    terminal_inventory_value: float = 0.0
    demand_shocks: tuple[float, ...] = ()


@dataclass
class MarketTrial:
    case: MarketCase
    firm_a_price: float | None
    firm_b_price: float | None
    nash_price: float
    collusive_price: float
    oracle_price: float
    total_profit: float | None
    equilibrium_price_gap: float | None
    collusion_index: float | None
    terminal_cash: float | None
    survival_cash_gap: float | None
    reserve_violation: bool
    raw_a: str
    raw_b: str


@dataclass(frozen=True)
class PolicyShiftMarketCase:
    key: str
    real_case: str
    base_demand: float
    demand_shock: float
    own_price_slope: float
    cross_price_slope: float
    marginal_cost: float
    p_max: float
    opponent_policy: str
    opponent_price_history: tuple[float, ...]


@dataclass(frozen=True)
class InventoryPolicyMarketCase:
    key: str
    real_case: str
    base_demand: float
    demand_shock: float
    own_price_slope: float
    cross_price_slope: float
    marginal_cost: float
    p_max: float
    opponent_policy: str
    opponent_price_history: tuple[float, ...]
    horizon: int
    starting_inventory: float
    starting_cash: float
    fixed_obligation: float
    min_terminal_cash: float
    carrying_cost_per_unsold: float
    terminal_inventory_value: float
    demand_shocks: tuple[float, ...] = ()


@dataclass(frozen=True)
class MarketTracePoint:
    period: int
    opponent_price: float
    opponent_fill_rate: float
    opponent_remaining_inventory_share: float


@dataclass(frozen=True)
class TraceInventoryMarketCase:
    key: str
    real_case: str
    base_demand: float
    demand_shock: float
    own_price_slope: float
    cross_price_slope: float
    marginal_cost: float
    p_max: float
    trace: tuple[MarketTracePoint, ...]
    horizon: int
    starting_inventory: float
    starting_cash: float
    fixed_obligation: float
    min_terminal_cash: float
    carrying_cost_per_unsold: float
    terminal_inventory_value: float
    demand_shocks: tuple[float, ...] = ()
    replenishment_unit_cost: float = 0.0
    replenishment_setup_cost: float = 0.0
    max_replenishment_units: float = 0.0
    replenishment_storage_capacity: float = 0.0


@dataclass
class PolicyShiftMarketTrial:
    case: PolicyShiftMarketCase
    oracle_price: float
    static_nash_price: float
    last_price_best_response: float
    predicted_opponent_price: float
    chosen_price: float | None
    profit: float | None
    profit_regret: float | None
    price_error: float | None
    static_nash_miss: bool
    last_price_miss: bool
    raw_response: str


@dataclass
class InventoryPolicyMarketTrial:
    case: InventoryPolicyMarketCase
    oracle_price: float
    static_nash_price: float
    last_price_best_response: float
    inventory_blind_price: float
    predicted_opponent_price: float
    chosen_price: float | None
    terminal_cash: float | None
    terminal_cash_regret: float | None
    constrained_terminal_cash_regret: float | None
    price_error: float | None
    reserve_violation: bool
    static_nash_miss: bool
    last_price_miss: bool
    inventory_blind_miss: bool
    raw_response: str


@dataclass
class TraceInventoryMarketTrial:
    case: TraceInventoryMarketCase
    oracle_price: float
    static_nash_price: float
    last_price_best_response: float
    trace_blind_price: float
    inventory_blind_price: float
    predicted_opponent_price: float
    chosen_price: float | None
    terminal_cash: float | None
    constrained_terminal_cash_regret: float | None
    price_error: float | None
    reserve_violation: bool
    static_nash_miss: bool
    last_price_miss: bool
    trace_blind_miss: bool
    inventory_blind_miss: bool
    raw_response: str


@dataclass
class TraceMarkdownMarketTrial:
    case: TraceInventoryMarketCase
    oracle_prices: tuple[float, float]
    static_prices: tuple[float, float]
    one_price_baseline: tuple[float, float]
    trace_blind_prices: tuple[float, float]
    inventory_blind_prices: tuple[float, float]
    predicted_opponent_price: float
    chosen_prices: tuple[float, float] | None
    terminal_cash: float | None
    constrained_terminal_cash_regret: float | None
    price_l1_error: float | None
    reserve_violation: bool
    static_nash_miss: bool
    one_price_miss: bool
    trace_blind_miss: bool
    inventory_blind_miss: bool
    raw_response: str


@dataclass
class TraceReplenishmentMarketTrial:
    case: TraceInventoryMarketCase
    oracle_decision: tuple[float, float, float]
    no_replenishment_decision: tuple[float, float, float]
    one_price_decision: tuple[float, float, float]
    trace_blind_decision: tuple[float, float, float]
    replenishment_blind_decision: tuple[float, float, float]
    predicted_opponent_price: float
    chosen_decision: tuple[float, float, float] | None
    terminal_cash: float | None
    constrained_terminal_cash_regret: float | None
    decision_l1_error: float | None
    reserve_violation: bool
    no_replenishment_miss: bool
    one_price_miss: bool
    trace_blind_miss: bool
    replenishment_blind_miss: bool
    raw_response: str


DEFAULT_CASES = [
    MarketCase(
        key="software_subscriptions",
        real_case="two SaaS vendors selling substitutable team software",
        base_demand=120.0,
        own_price_slope=2.4,
        cross_price_slope=1.0,
        marginal_cost=12.0,
        p_max=80.0,
    ),
    MarketCase(
        key="local_delivery",
        real_case="two local delivery platforms competing for merchants",
        base_demand=90.0,
        own_price_slope=1.8,
        cross_price_slope=0.6,
        marginal_cost=8.0,
        p_max=75.0,
    ),
    MarketCase(
        key="cloud_inference",
        real_case="two inference API providers with differentiated latency",
        base_demand=160.0,
        own_price_slope=3.0,
        cross_price_slope=1.4,
        marginal_cost=20.0,
        p_max=100.0,
    ),
    MarketCase(
        key="inventory_cash_crunch",
        real_case="multi-period device inventory market with a near-term cash obligation",
        base_demand=92.0,
        own_price_slope=1.25,
        cross_price_slope=0.35,
        marginal_cost=18.0,
        p_max=95.0,
        horizon=3,
        starting_inventory=120.0,
        starting_cash=260.0,
        fixed_obligation=2100.0,
        min_terminal_cash=180.0,
        carrying_cost_per_unsold=1.2,
        terminal_inventory_value=10.0,
        demand_shocks=(0.0, -6.0, -12.0),
    ),
    MarketCase(
        key="appreciating_gpu_inventory",
        real_case="accelerator resale market where unsold inventory keeps strategic option value",
        base_demand=74.0,
        own_price_slope=0.95,
        cross_price_slope=0.30,
        marginal_cost=26.0,
        p_max=140.0,
        horizon=4,
        starting_inventory=95.0,
        starting_cash=420.0,
        fixed_obligation=1450.0,
        min_terminal_cash=300.0,
        carrying_cost_per_unsold=0.6,
        terminal_inventory_value=42.0,
        demand_shocks=(5.0, 0.0, -4.0, -8.0),
    ),
]


POLICY_SHIFT_CASES = [
    PolicyShiftMarketCase(
        key="clearance_markdown_competitor",
        real_case="competitor begins clearing inventory after three observed markdowns",
        base_demand=120.0,
        demand_shock=-5.0,
        own_price_slope=2.00,
        cross_price_slope=1.55,
        marginal_cost=18.0,
        p_max=100.0,
        opponent_policy="liquidation_drop",
        opponent_price_history=(80.0, 60.0, 42.0),
    ),
    PolicyShiftMarketCase(
        key="stockout_competitor_jump",
        real_case="competitor is capacity constrained and has been raising prices into stockout",
        base_demand=98.0,
        demand_shock=5.0,
        own_price_slope=1.70,
        cross_price_slope=1.25,
        marginal_cost=14.0,
        p_max=110.0,
        opponent_policy="stockout_jump",
        opponent_price_history=(28.0, 45.0, 66.0),
    ),
    PolicyShiftMarketCase(
        key="entrant_price_war",
        real_case="new entrant keeps cutting price to buy share after launch",
        base_demand=145.0,
        demand_shock=0.0,
        own_price_slope=2.50,
        cross_price_slope=1.90,
        marginal_cost=20.0,
        p_max=95.0,
        opponent_policy="entry_price_war",
        opponent_price_history=(75.0, 52.0, 34.0),
    ),
    PolicyShiftMarketCase(
        key="capacity_exit_spike",
        real_case="competitor is rationing capacity after supply disruption and prices are jumping",
        base_demand=84.0,
        demand_shock=8.0,
        own_price_slope=1.40,
        cross_price_slope=1.05,
        marginal_cost=16.0,
        p_max=120.0,
        opponent_policy="capacity_exit",
        opponent_price_history=(36.0, 58.0, 82.0),
    ),
]

INVENTORY_POLICY_CASES = [
    InventoryPolicyMarketCase(
        key="markdown_cash_cliff",
        real_case="competitor is clearing stock while your warehouse must fund a lease payment",
        base_demand=132.0,
        demand_shock=-7.0,
        own_price_slope=1.45,
        cross_price_slope=1.05,
        marginal_cost=22.0,
        p_max=105.0,
        opponent_policy="liquidation_drop",
        opponent_price_history=(84.0, 62.0, 43.0),
        horizon=3,
        starting_inventory=150.0,
        starting_cash=360.0,
        fixed_obligation=2350.0,
        min_terminal_cash=240.0,
        carrying_cost_per_unsold=1.35,
        terminal_inventory_value=9.0,
        demand_shocks=(0.0, -8.0, -14.0),
    ),
    InventoryPolicyMarketCase(
        key="capacity_gap_harvest",
        real_case="rival stockout is lifting prices while unsold specialist inventory keeps option value",
        base_demand=96.0,
        demand_shock=6.0,
        own_price_slope=1.05,
        cross_price_slope=0.78,
        marginal_cost=28.0,
        p_max=135.0,
        opponent_policy="stockout_jump",
        opponent_price_history=(42.0, 68.0, 96.0),
        horizon=4,
        starting_inventory=92.0,
        starting_cash=520.0,
        fixed_obligation=1420.0,
        min_terminal_cash=360.0,
        carrying_cost_per_unsold=0.55,
        terminal_inventory_value=41.0,
        demand_shocks=(5.0, 1.0, -4.0, -7.0),
    ),
    InventoryPolicyMarketCase(
        key="entrant_share_attack",
        real_case="entrant keeps buying share while your consumable inventory expires quickly",
        base_demand=156.0,
        demand_shock=-2.0,
        own_price_slope=2.10,
        cross_price_slope=1.62,
        marginal_cost=18.0,
        p_max=92.0,
        opponent_policy="entry_price_war",
        opponent_price_history=(76.0, 51.0, 33.0),
        horizon=3,
        starting_inventory=175.0,
        starting_cash=300.0,
        fixed_obligation=2750.0,
        min_terminal_cash=260.0,
        carrying_cost_per_unsold=2.10,
        terminal_inventory_value=5.0,
        demand_shocks=(3.0, -5.0, -12.0),
    ),
    InventoryPolicyMarketCase(
        key="supply_exit_reserve",
        real_case="competitor capacity exit raises prices but your reserve covenant still rewards steady sell-through",
        base_demand=104.0,
        demand_shock=4.0,
        own_price_slope=1.32,
        cross_price_slope=0.92,
        marginal_cost=24.0,
        p_max=128.0,
        opponent_policy="capacity_exit",
        opponent_price_history=(39.0, 61.0, 88.0),
        horizon=4,
        starting_inventory=118.0,
        starting_cash=440.0,
        fixed_obligation=1880.0,
        min_terminal_cash=320.0,
        carrying_cost_per_unsold=0.95,
        terminal_inventory_value=24.0,
        demand_shocks=(2.0, 0.0, -6.0, -10.0),
    ),
]


TRACE_INVENTORY_CASES = [
    TraceInventoryMarketCase(
        key="warehouse_clearance_trace",
        real_case="competitor keeps discounting while its fill rates stay high and inventory remains heavy",
        base_demand=134.0,
        demand_shock=-6.0,
        own_price_slope=1.48,
        cross_price_slope=1.08,
        marginal_cost=22.0,
        p_max=105.0,
        trace=(
            MarketTracePoint(1, 84.0, 0.97, 0.88),
            MarketTracePoint(2, 62.0, 0.99, 0.81),
            MarketTracePoint(3, 43.0, 0.98, 0.76),
        ),
        horizon=3,
        starting_inventory=154.0,
        starting_cash=360.0,
        fixed_obligation=2360.0,
        min_terminal_cash=245.0,
        carrying_cost_per_unsold=1.35,
        terminal_inventory_value=8.0,
        demand_shocks=(0.0, -8.0, -13.0),
    ),
    TraceInventoryMarketCase(
        key="stockout_harvest_trace",
        real_case="rival is raising prices while low fill rates reveal stockout pressure",
        base_demand=98.0,
        demand_shock=6.0,
        own_price_slope=1.04,
        cross_price_slope=0.80,
        marginal_cost=28.0,
        p_max=135.0,
        trace=(
            MarketTracePoint(1, 42.0, 0.92, 0.46),
            MarketTracePoint(2, 68.0, 0.74, 0.24),
            MarketTracePoint(3, 96.0, 0.55, 0.10),
        ),
        horizon=4,
        starting_inventory=92.0,
        starting_cash=520.0,
        fixed_obligation=1420.0,
        min_terminal_cash=360.0,
        carrying_cost_per_unsold=0.55,
        terminal_inventory_value=41.0,
        demand_shocks=(5.0, 1.0, -4.0, -7.0),
    ),
    TraceInventoryMarketCase(
        key="entrant_share_trace",
        real_case="entrant price cuts keep accelerating while its remaining stock is still abundant",
        base_demand=158.0,
        demand_shock=-2.0,
        own_price_slope=2.12,
        cross_price_slope=1.64,
        marginal_cost=18.0,
        p_max=92.0,
        trace=(
            MarketTracePoint(1, 76.0, 0.95, 0.92),
            MarketTracePoint(2, 51.0, 0.97, 0.86),
            MarketTracePoint(3, 33.0, 0.99, 0.79),
        ),
        horizon=3,
        starting_inventory=178.0,
        starting_cash=300.0,
        fixed_obligation=2760.0,
        min_terminal_cash=260.0,
        carrying_cost_per_unsold=2.10,
        terminal_inventory_value=5.0,
        demand_shocks=(3.0, -5.0, -12.0),
    ),
    TraceInventoryMarketCase(
        key="capacity_exit_trace",
        real_case="competitor capacity is exiting and poor fill rates accompany price jumps",
        base_demand=106.0,
        demand_shock=4.0,
        own_price_slope=1.32,
        cross_price_slope=0.92,
        marginal_cost=24.0,
        p_max=128.0,
        trace=(
            MarketTracePoint(1, 39.0, 0.89, 0.44),
            MarketTracePoint(2, 61.0, 0.71, 0.23),
            MarketTracePoint(3, 88.0, 0.57, 0.12),
        ),
        horizon=4,
        starting_inventory=118.0,
        starting_cash=440.0,
        fixed_obligation=1880.0,
        min_terminal_cash=320.0,
        carrying_cost_per_unsold=0.95,
        terminal_inventory_value=24.0,
        demand_shocks=(2.0, 0.0, -6.0, -10.0),
    ),
]


TRACE_REPLENISHMENT_CASES = [
    replace(
        TRACE_INVENTORY_CASES[0],
        replenishment_unit_cost=27.0,
        replenishment_setup_cost=8.0,
        max_replenishment_units=75.0,
        replenishment_storage_capacity=180.0,
    ),
    replace(
        TRACE_INVENTORY_CASES[1],
        replenishment_unit_cost=34.0,
        replenishment_setup_cost=18.0,
        max_replenishment_units=90.0,
        replenishment_storage_capacity=165.0,
    ),
    replace(
        TRACE_INVENTORY_CASES[2],
        replenishment_unit_cost=23.0,
        replenishment_setup_cost=10.0,
        max_replenishment_units=100.0,
        replenishment_storage_capacity=210.0,
    ),
    replace(
        TRACE_INVENTORY_CASES[3],
        replenishment_unit_cost=30.0,
        replenishment_setup_cost=16.0,
        max_replenishment_units=90.0,
        replenishment_storage_capacity=185.0,
    ),
]


def _trace_replenishment_noisy_case(
    case: TraceInventoryMarketCase,
    *,
    price_offsets: tuple[float, ...],
    fill_offsets: tuple[float, ...],
    shelf_offsets: tuple[float, ...],
) -> TraceInventoryMarketCase:
    trace = tuple(
        MarketTracePoint(
            point.period,
            clamp(point.opponent_price + price_offsets[idx], case.marginal_cost, case.p_max),
            clamp(point.opponent_fill_rate + fill_offsets[idx], 0.02, 0.99),
            clamp(point.opponent_remaining_inventory_share + shelf_offsets[idx], 0.02, 0.98),
        )
        for idx, point in enumerate(case.trace)
    )
    return replace(
        case,
        key=f"noisy_{case.key}",
        real_case=f"lumpy regional shelf readings around {case.real_case}",
        trace=trace,
    )


TRACE_REPLENISHMENT_NOISY_CASES = [
    _trace_replenishment_noisy_case(
        TRACE_REPLENISHMENT_CASES[0],
        price_offsets=(1.0, -2.0, 3.0),
        fill_offsets=(0.03, -0.04, 0.05),
        shelf_offsets=(-0.02, 0.04, -0.03),
    ),
    _trace_replenishment_noisy_case(
        TRACE_REPLENISHMENT_CASES[1],
        price_offsets=(-2.0, 4.0, -3.0),
        fill_offsets=(-0.05, 0.06, -0.04),
        shelf_offsets=(0.04, -0.03, 0.05),
    ),
    _trace_replenishment_noisy_case(
        TRACE_REPLENISHMENT_CASES[2],
        price_offsets=(3.0, -4.0, 5.0),
        fill_offsets=(0.04, -0.06, 0.05),
        shelf_offsets=(-0.05, 0.03, -0.04),
    ),
    _trace_replenishment_noisy_case(
        TRACE_REPLENISHMENT_CASES[3],
        price_offsets=(-1.0, 3.0, -2.0),
        fill_offsets=(-0.03, 0.05, -0.06),
        shelf_offsets=(0.03, -0.04, 0.02),
    ),
]


def nash_price(case: MarketCase) -> float:
    denom = 2.0 * case.own_price_slope - case.cross_price_slope
    if denom <= 0:
        return case.marginal_cost
    price = (case.base_demand + case.own_price_slope * case.marginal_cost) / denom
    return clamp(price, case.marginal_cost, case.p_max)


def collusive_price(case: MarketCase) -> float:
    net_slope = case.own_price_slope - case.cross_price_slope
    if net_slope <= 0:
        return case.p_max
    price = (case.base_demand + net_slope * case.marginal_cost) / (2.0 * net_slope)
    return clamp(price, case.marginal_cost, case.p_max)


def firm_quantity(case: MarketCase, own_price: float, other_price: float) -> float:
    return max(
        0.0,
        case.base_demand
        - case.own_price_slope * own_price
        + case.cross_price_slope * other_price,
    )


def firm_profit(case: MarketCase, own_price: float, other_price: float) -> float:
    return max(0.0, own_price - case.marginal_cost) * firm_quantity(case, own_price, other_price)


def has_survival_dynamics(case: MarketCase) -> bool:
    return case.horizon > 1 and case.starting_inventory > 0.0


def survival_terminal_cash(case: MarketCase, own_price: float, other_price: float) -> float:
    inventory = case.starting_inventory
    cash = case.starting_cash
    shocks = case.demand_shocks or tuple(0.0 for _ in range(case.horizon))
    for period in range(case.horizon):
        shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            case.base_demand
            + shock
            - case.own_price_slope * own_price
            + case.cross_price_slope * other_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, own_price - case.marginal_cost) * sold
        inventory -= sold
        cash -= case.carrying_cost_per_unsold * inventory
    cash += case.terminal_inventory_value * inventory
    cash -= case.fixed_obligation
    return cash


def survival_oracle_price(case: MarketCase) -> float:
    candidates = _candidate_prices(case)
    reference = nash_price(case)
    return max(candidates, key=lambda price: (survival_terminal_cash(case, price, price), -abs(price - reference)))


def oracle_price(case: MarketCase) -> float:
    return survival_oracle_price(case) if has_survival_dynamics(case) else nash_price(case)


def run_market_game(agent: Agent, cases: list[MarketCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[MarketTrial] = []
    for case in cases:
        raw_a = agent.complete(MARKET_SYSTEM, _prompt(case, "A"))
        raw_b = agent.complete(MARKET_SYSTEM, _prompt(case, "B"))
        price_a = _parse_price(raw_a, case)
        price_b = _parse_price(raw_b, case)
        nash = nash_price(case)
        collusive = collusive_price(case)
        oracle = oracle_price(case)
        if price_a is None or price_b is None:
            total_profit = None
            gap = None
            index = None
            terminal_cash = None
            cash_gap = None
        else:
            total_profit = firm_profit(case, price_a, price_b) + firm_profit(case, price_b, price_a)
            avg_price = (price_a + price_b) / 2.0
            gap_scale = max(1e-9, abs(collusive - oracle), case.p_max - case.marginal_cost)
            collusion_scale = max(1e-9, collusive - nash)
            index = None if has_survival_dynamics(case) else clamp((avg_price - nash) / collusion_scale, 0.0, 1.0)
            gap = abs(avg_price - oracle) / gap_scale
            if has_survival_dynamics(case):
                terminal_cash = survival_terminal_cash(case, price_a, price_b)
                best_price = survival_oracle_price(case)
                best_cash = survival_terminal_cash(case, best_price, best_price)
                cash_gap = best_cash - terminal_cash
            else:
                terminal_cash = None
                cash_gap = None
        trials.append(
            MarketTrial(
                case=case,
                firm_a_price=price_a,
                firm_b_price=price_b,
                nash_price=nash,
                collusive_price=collusive,
                oracle_price=oracle,
                total_profit=total_profit,
                equilibrium_price_gap=gap,
                collusion_index=index,
                terminal_cash=terminal_cash,
                survival_cash_gap=cash_gap,
                reserve_violation=(
                    terminal_cash is not None and terminal_cash < case.min_terminal_cash
                ),
                raw_a=raw_a,
                raw_b=raw_b,
            )
        )
    return summarize_market_trials(agent.name, trials)


def run_market_policy_shift_game(
    agent: Agent,
    cases: list[PolicyShiftMarketCase] | None = None,
) -> dict:
    cases = cases or POLICY_SHIFT_CASES
    trials: list[PolicyShiftMarketTrial] = []
    for case in cases:
        predicted_opponent = policy_shift_opponent_price(case)
        oracle = policy_shift_best_response(case, predicted_opponent)
        static = policy_shift_static_nash_price(case)
        last_price = policy_shift_best_response(case, case.opponent_price_history[-1])
        response = agent.complete(MARKET_POLICY_SYSTEM, _policy_shift_prompt(case))
        chosen = _parse_policy_shift_price(response, case)
        oracle_profit = policy_shift_profit(case, oracle, predicted_opponent)
        profit = (
            policy_shift_profit(case, chosen, predicted_opponent)
            if chosen is not None
            else None
        )
        price_error = abs(chosen - oracle) if chosen is not None else None
        static_nash_miss = (
            chosen is not None
            and abs(static - oracle) >= 3.0
            and abs(chosen - static) < abs(chosen - oracle)
        )
        last_price_miss = (
            chosen is not None
            and abs(last_price - oracle) >= 3.0
            and abs(chosen - last_price) < abs(chosen - oracle)
        )
        trials.append(
            PolicyShiftMarketTrial(
                case=case,
                oracle_price=oracle,
                static_nash_price=static,
                last_price_best_response=last_price,
                predicted_opponent_price=predicted_opponent,
                chosen_price=chosen,
                profit=profit,
                profit_regret=oracle_profit - profit if profit is not None else None,
                price_error=price_error,
                static_nash_miss=static_nash_miss,
                last_price_miss=last_price_miss,
                raw_response=response,
            )
        )
    return summarize_market_policy_shift_trials(agent.name, trials)


def run_market_policy_inventory_game(
    agent: Agent,
    cases: list[InventoryPolicyMarketCase] | None = None,
) -> dict:
    cases = cases or INVENTORY_POLICY_CASES
    trials: list[InventoryPolicyMarketTrial] = []
    for case in cases:
        predicted_opponent = policy_shift_opponent_price(case)
        oracle = policy_inventory_oracle_price(case)
        static = policy_shift_static_nash_price(case)
        last_price = policy_shift_best_response(case, case.opponent_price_history[-1])
        inventory_blind = policy_shift_best_response(case, predicted_opponent)
        response = agent.complete(MARKET_POLICY_INVENTORY_SYSTEM, _policy_inventory_prompt(case))
        chosen = _parse_policy_inventory_price(response, case)
        oracle_cash = policy_inventory_terminal_cash(case, oracle, predicted_opponent)
        terminal_cash = (
            policy_inventory_terminal_cash(case, chosen, predicted_opponent)
            if chosen is not None
            else None
        )
        cash_regret = oracle_cash - terminal_cash if terminal_cash is not None else None
        reserve_gap = (
            max(0.0, case.min_terminal_cash - terminal_cash)
            if terminal_cash is not None
            else None
        )
        constrained_regret = (
            cash_regret + reserve_gap
            if cash_regret is not None and reserve_gap is not None
            else None
        )
        price_error = abs(chosen - oracle) if chosen is not None else None
        static_nash_miss = (
            chosen is not None
            and abs(static - oracle) >= 3.0
            and abs(chosen - static) < abs(chosen - oracle)
        )
        last_price_miss = (
            chosen is not None
            and abs(last_price - oracle) >= 3.0
            and abs(chosen - last_price) < abs(chosen - oracle)
        )
        inventory_blind_miss = (
            chosen is not None
            and abs(inventory_blind - oracle) >= 3.0
            and abs(chosen - inventory_blind) < abs(chosen - oracle)
        )
        trials.append(
            InventoryPolicyMarketTrial(
                case=case,
                oracle_price=oracle,
                static_nash_price=static,
                last_price_best_response=last_price,
                inventory_blind_price=inventory_blind,
                predicted_opponent_price=predicted_opponent,
                chosen_price=chosen,
                terminal_cash=terminal_cash,
                terminal_cash_regret=cash_regret,
                constrained_terminal_cash_regret=constrained_regret,
                price_error=price_error,
                reserve_violation=(
                    terminal_cash is not None and terminal_cash < case.min_terminal_cash
                ),
                static_nash_miss=static_nash_miss,
                last_price_miss=last_price_miss,
                inventory_blind_miss=inventory_blind_miss,
                raw_response=response,
            )
        )
    return summarize_market_policy_inventory_trials(agent.name, trials)


def run_market_trace_inventory_game(
    agent: Agent,
    cases: list[TraceInventoryMarketCase] | None = None,
) -> dict:
    cases = cases or TRACE_INVENTORY_CASES
    trials: list[TraceInventoryMarketTrial] = []
    for case in cases:
        predicted_opponent = trace_inventory_opponent_price(case)
        oracle = trace_inventory_oracle_price(case)
        static = trace_inventory_static_nash_price(case)
        last_opponent = case.trace[-1].opponent_price
        last_price = trace_inventory_best_response(case, last_opponent)
        trace_blind = trace_inventory_oracle_price(case, opponent_price=last_opponent)
        inventory_blind = trace_inventory_best_response(case, predicted_opponent)
        response = agent.complete(MARKET_TRACE_INVENTORY_SYSTEM, _trace_inventory_prompt(case))
        chosen = _parse_trace_inventory_price(response, case)
        oracle_cash = trace_inventory_terminal_cash(case, oracle, predicted_opponent)
        terminal_cash = (
            trace_inventory_terminal_cash(case, chosen, predicted_opponent)
            if chosen is not None
            else None
        )
        cash_regret = oracle_cash - terminal_cash if terminal_cash is not None else None
        reserve_gap = (
            max(0.0, case.min_terminal_cash - terminal_cash)
            if terminal_cash is not None
            else None
        )
        constrained_regret = (
            cash_regret + reserve_gap
            if cash_regret is not None and reserve_gap is not None
            else None
        )
        price_error = abs(chosen - oracle) if chosen is not None else None
        static_nash_miss = (
            chosen is not None
            and abs(static - oracle) >= 3.0
            and abs(chosen - static) < abs(chosen - oracle)
        )
        last_price_miss = (
            chosen is not None
            and abs(last_price - oracle) >= 3.0
            and abs(chosen - last_price) < abs(chosen - oracle)
        )
        trace_blind_miss = (
            chosen is not None
            and abs(trace_blind - oracle) >= 3.0
            and abs(chosen - trace_blind) < abs(chosen - oracle)
        )
        inventory_blind_miss = (
            chosen is not None
            and abs(inventory_blind - oracle) >= 3.0
            and abs(chosen - inventory_blind) < abs(chosen - oracle)
        )
        trials.append(
            TraceInventoryMarketTrial(
                case=case,
                oracle_price=oracle,
                static_nash_price=static,
                last_price_best_response=last_price,
                trace_blind_price=trace_blind,
                inventory_blind_price=inventory_blind,
                predicted_opponent_price=predicted_opponent,
                chosen_price=chosen,
                terminal_cash=terminal_cash,
                constrained_terminal_cash_regret=constrained_regret,
                price_error=price_error,
                reserve_violation=(
                    terminal_cash is not None and terminal_cash < case.min_terminal_cash
                ),
                static_nash_miss=static_nash_miss,
                last_price_miss=last_price_miss,
                trace_blind_miss=trace_blind_miss,
                inventory_blind_miss=inventory_blind_miss,
                raw_response=response,
            )
        )
    return summarize_market_trace_inventory_trials(agent.name, trials)


def run_market_trace_markdown_game(
    agent: Agent,
    cases: list[TraceInventoryMarketCase] | None = None,
) -> dict:
    cases = cases or TRACE_INVENTORY_CASES
    trials: list[TraceMarkdownMarketTrial] = []
    for case in cases:
        predicted_opponent = trace_inventory_opponent_price(case)
        oracle = trace_markdown_oracle_prices(case)
        static_price = trace_inventory_static_nash_price(case)
        static = (static_price, static_price)
        one_price = trace_inventory_oracle_price(case)
        one_price_baseline = (one_price, one_price)
        last_opponent = case.trace[-1].opponent_price
        trace_blind = trace_markdown_oracle_prices(case, opponent_price=last_opponent)
        inventory_blind_price = trace_inventory_best_response(case, predicted_opponent)
        inventory_blind = (inventory_blind_price, inventory_blind_price)
        response = agent.complete(MARKET_TRACE_MARKDOWN_SYSTEM, _trace_markdown_prompt(case))
        chosen = _parse_trace_markdown_prices(response, case)
        oracle_cash = trace_markdown_terminal_cash(case, oracle[0], oracle[1], predicted_opponent)
        terminal_cash = (
            trace_markdown_terminal_cash(case, chosen[0], chosen[1], predicted_opponent)
            if chosen is not None
            else None
        )
        cash_regret = oracle_cash - terminal_cash if terminal_cash is not None else None
        reserve_gap = (
            max(0.0, case.min_terminal_cash - terminal_cash)
            if terminal_cash is not None
            else None
        )
        constrained_regret = (
            cash_regret + reserve_gap
            if cash_regret is not None and reserve_gap is not None
            else None
        )
        price_l1_error = (
            abs(chosen[0] - oracle[0]) + abs(chosen[1] - oracle[1])
            if chosen is not None
            else None
        )
        static_nash_miss = (
            chosen is not None
            and _pair_l1(static, oracle) >= 3.0
            and _pair_l1(chosen, static) < _pair_l1(chosen, oracle)
        )
        one_price_miss = (
            chosen is not None
            and _pair_l1(one_price_baseline, oracle) >= 3.0
            and _pair_l1(chosen, one_price_baseline) < _pair_l1(chosen, oracle)
        )
        trace_blind_miss = (
            chosen is not None
            and _pair_l1(trace_blind, oracle) >= 3.0
            and _pair_l1(chosen, trace_blind) < _pair_l1(chosen, oracle)
        )
        inventory_blind_miss = (
            chosen is not None
            and _pair_l1(inventory_blind, oracle) >= 3.0
            and _pair_l1(chosen, inventory_blind) < _pair_l1(chosen, oracle)
        )
        trials.append(
            TraceMarkdownMarketTrial(
                case=case,
                oracle_prices=oracle,
                static_prices=static,
                one_price_baseline=one_price_baseline,
                trace_blind_prices=trace_blind,
                inventory_blind_prices=inventory_blind,
                predicted_opponent_price=predicted_opponent,
                chosen_prices=chosen,
                terminal_cash=terminal_cash,
                constrained_terminal_cash_regret=constrained_regret,
                price_l1_error=price_l1_error,
                reserve_violation=(
                    terminal_cash is not None and terminal_cash < case.min_terminal_cash
                ),
                static_nash_miss=static_nash_miss,
                one_price_miss=one_price_miss,
                trace_blind_miss=trace_blind_miss,
                inventory_blind_miss=inventory_blind_miss,
                raw_response=response,
            )
        )
    return summarize_market_trace_markdown_trials(agent.name, trials)


def run_market_trace_replenishment_game(
    agent: Agent,
    cases: list[TraceInventoryMarketCase] | None = None,
) -> dict:
    return _run_market_trace_replenishment_game(
        agent,
        cases,
        system=MARKET_TRACE_REPLENISHMENT_SYSTEM,
        prompt_fn=_trace_replenishment_prompt,
        task_name="market_trace_replenishment",
    )


def run_market_trace_replenishment_natural_game(
    agent: Agent,
    cases: list[TraceInventoryMarketCase] | None = None,
) -> dict:
    return _run_market_trace_replenishment_game(
        agent,
        cases,
        system=MARKET_TRACE_REPLENISHMENT_NATURAL_SYSTEM,
        prompt_fn=_trace_replenishment_natural_prompt,
        task_name="market_trace_replenishment_natural",
    )


def run_market_trace_replenishment_noisy_game(
    agent: Agent,
    cases: list[TraceInventoryMarketCase] | None = None,
) -> dict:
    return _run_market_trace_replenishment_game(
        agent,
        cases or TRACE_REPLENISHMENT_NOISY_CASES,
        system=MARKET_TRACE_REPLENISHMENT_NOISY_SYSTEM,
        prompt_fn=_trace_replenishment_noisy_prompt,
        task_name="market_trace_replenishment_noisy",
    )


def _run_market_trace_replenishment_game(
    agent: Agent,
    cases: list[TraceInventoryMarketCase] | None,
    *,
    system: str,
    prompt_fn,
    task_name: str,
) -> dict:
    cases = cases or TRACE_REPLENISHMENT_CASES
    trials: list[TraceReplenishmentMarketTrial] = []
    for case in cases:
        predicted_opponent = trace_inventory_opponent_price(case)
        oracle = trace_replenishment_oracle_decision(case)
        no_replenishment_prices = trace_markdown_oracle_prices(case)
        no_replenishment = (no_replenishment_prices[0], no_replenishment_prices[1], 0.0)
        one_price = trace_replenishment_oracle_decision(case, fixed_price=True)
        last_opponent = case.trace[-1].opponent_price
        trace_blind = trace_replenishment_oracle_decision(case, opponent_price=last_opponent)
        replenishment_blind = trace_replenishment_oracle_decision(
            case,
            forced_replenishment=case.max_replenishment_units,
        )
        response = agent.complete(
            system,
            prompt_fn(case),
        )
        chosen = _parse_trace_replenishment_decision(response, case)
        oracle_cash = trace_replenishment_terminal_cash(
            case,
            oracle[0],
            oracle[1],
            oracle[2],
            predicted_opponent,
        )
        terminal_cash = (
            trace_replenishment_terminal_cash(
                case,
                chosen[0],
                chosen[1],
                chosen[2],
                predicted_opponent,
            )
            if chosen is not None
            else None
        )
        cash_regret = oracle_cash - terminal_cash if terminal_cash is not None else None
        reserve_gap = (
            max(0.0, case.min_terminal_cash - terminal_cash)
            if terminal_cash is not None
            else None
        )
        constrained_regret = (
            cash_regret + reserve_gap
            if cash_regret is not None and reserve_gap is not None
            else None
        )
        decision_l1_error = (
            _replenishment_decision_distance(chosen, oracle) if chosen is not None else None
        )
        no_replenishment_miss = (
            chosen is not None
            and _replenishment_decision_distance(no_replenishment, oracle) >= 5.0
            and _replenishment_decision_distance(chosen, no_replenishment)
            < _replenishment_decision_distance(chosen, oracle)
        )
        one_price_miss = (
            chosen is not None
            and _replenishment_decision_distance(one_price, oracle) >= 5.0
            and _replenishment_decision_distance(chosen, one_price)
            < _replenishment_decision_distance(chosen, oracle)
        )
        trace_blind_miss = (
            chosen is not None
            and _replenishment_decision_distance(trace_blind, oracle) >= 5.0
            and _replenishment_decision_distance(chosen, trace_blind)
            < _replenishment_decision_distance(chosen, oracle)
        )
        replenishment_blind_miss = (
            chosen is not None
            and _replenishment_decision_distance(replenishment_blind, oracle) >= 5.0
            and _replenishment_decision_distance(chosen, replenishment_blind)
            < _replenishment_decision_distance(chosen, oracle)
        )
        trials.append(
            TraceReplenishmentMarketTrial(
                case=case,
                oracle_decision=oracle,
                no_replenishment_decision=no_replenishment,
                one_price_decision=one_price,
                trace_blind_decision=trace_blind,
                replenishment_blind_decision=replenishment_blind,
                predicted_opponent_price=predicted_opponent,
                chosen_decision=chosen,
                terminal_cash=terminal_cash,
                constrained_terminal_cash_regret=constrained_regret,
                decision_l1_error=decision_l1_error,
                reserve_violation=(
                    terminal_cash is not None and terminal_cash < case.min_terminal_cash
                ),
                no_replenishment_miss=no_replenishment_miss,
                one_price_miss=one_price_miss,
                trace_blind_miss=trace_blind_miss,
                replenishment_blind_miss=replenishment_blind_miss,
                raw_response=response,
            )
        )
    return summarize_market_trace_replenishment_trials(agent.name, trials, task_name=task_name)


def summarize_market_trials(agent_name: str, trials: list[MarketTrial]) -> dict:
    gaps = [trial.equilibrium_price_gap for trial in trials if trial.equilibrium_price_gap is not None]
    indices = [trial.collusion_index for trial in trials if trial.collusion_index is not None]
    collusive = sum(index >= 0.5 for index in indices)
    survival_trials = [trial for trial in trials if has_survival_dynamics(trial.case)]
    survival_gaps = [trial.survival_cash_gap for trial in survival_trials if trial.survival_cash_gap is not None]
    reserve_violations = sum(trial.reserve_violation for trial in survival_trials)
    liquidation_missable = [
        trial
        for trial in survival_trials
        if abs(trial.oracle_price - trial.case.marginal_cost) > 1e-9
    ]
    liquidation_misses = sum(
        trial.firm_a_price is not None
        and trial.firm_a_price <= trial.case.marginal_cost + 1.0
        for trial in liquidation_missable
    )
    return {
        "task": "market",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_equilibrium_price_gap": mean(gaps),
        "mean_equilibrium_price_gap_ci95": bootstrap_mean_ci(gaps),
        "mean_collusion_index": mean(indices),
        "collusion_rate": collusive / len(indices) if indices else 0.0,
        "mean_survival_cash_gap": mean(survival_gaps),
        "survival_reserve_violation_rate": (
            reserve_violations / len(survival_trials) if survival_trials else 0.0
        ),
        "liquidation_miss_rate": (
            liquidation_misses / len(liquidation_missable) if liquidation_missable else 0.0
        ),
        "trials": [_trial_json(trial) for trial in trials],
    }


def summarize_market_policy_shift_trials(
    agent_name: str,
    trials: list[PolicyShiftMarketTrial],
) -> dict:
    regrets = [trial.profit_regret for trial in trials if trial.profit_regret is not None]
    errors = [trial.price_error for trial in trials if trial.price_error is not None]
    static_missable = [
        trial for trial in trials if abs(trial.static_nash_price - trial.oracle_price) >= 3.0
    ]
    last_missable = [
        trial
        for trial in trials
        if abs(trial.last_price_best_response - trial.oracle_price) >= 3.0
    ]
    return {
        "task": "market_policy_shift",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_profit_regret": mean(regrets),
        "mean_profit_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_price_error": mean(errors),
        "static_nash_miss_rate": (
            sum(trial.static_nash_miss for trial in static_missable) / len(static_missable)
            if static_missable
            else 0.0
        ),
        "last_price_miss_rate": (
            sum(trial.last_price_miss for trial in last_missable) / len(last_missable)
            if last_missable
            else 0.0
        ),
        "trials": [_policy_shift_trial_json(trial) for trial in trials],
    }


def summarize_market_policy_inventory_trials(
    agent_name: str,
    trials: list[InventoryPolicyMarketTrial],
) -> dict:
    regrets = [
        trial.constrained_terminal_cash_regret
        for trial in trials
        if trial.constrained_terminal_cash_regret is not None
    ]
    errors = [trial.price_error for trial in trials if trial.price_error is not None]
    static_missable = [
        trial for trial in trials if abs(trial.static_nash_price - trial.oracle_price) >= 3.0
    ]
    last_missable = [
        trial
        for trial in trials
        if abs(trial.last_price_best_response - trial.oracle_price) >= 3.0
    ]
    inventory_missable = [
        trial
        for trial in trials
        if abs(trial.inventory_blind_price - trial.oracle_price) >= 3.0
    ]
    return {
        "task": "market_policy_inventory",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_constrained_terminal_cash_regret": mean(regrets),
        "mean_constrained_terminal_cash_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_price_error": mean(errors),
        "reserve_violation_rate": sum(trial.reserve_violation for trial in trials) / len(trials),
        "static_nash_miss_rate": (
            sum(trial.static_nash_miss for trial in static_missable) / len(static_missable)
            if static_missable
            else 0.0
        ),
        "last_price_miss_rate": (
            sum(trial.last_price_miss for trial in last_missable) / len(last_missable)
            if last_missable
            else 0.0
        ),
        "inventory_blind_miss_rate": (
            sum(trial.inventory_blind_miss for trial in inventory_missable) / len(inventory_missable)
            if inventory_missable
            else 0.0
        ),
        "trials": [_policy_inventory_trial_json(trial) for trial in trials],
    }


def summarize_market_trace_inventory_trials(
    agent_name: str,
    trials: list[TraceInventoryMarketTrial],
) -> dict:
    regrets = [
        trial.constrained_terminal_cash_regret
        for trial in trials
        if trial.constrained_terminal_cash_regret is not None
    ]
    errors = [trial.price_error for trial in trials if trial.price_error is not None]
    static_missable = [
        trial for trial in trials if abs(trial.static_nash_price - trial.oracle_price) >= 3.0
    ]
    last_missable = [
        trial
        for trial in trials
        if abs(trial.last_price_best_response - trial.oracle_price) >= 3.0
    ]
    trace_missable = [
        trial for trial in trials if abs(trial.trace_blind_price - trial.oracle_price) >= 3.0
    ]
    inventory_missable = [
        trial
        for trial in trials
        if abs(trial.inventory_blind_price - trial.oracle_price) >= 3.0
    ]
    return {
        "task": "market_trace_inventory",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_constrained_terminal_cash_regret": mean(regrets),
        "mean_constrained_terminal_cash_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_price_error": mean(errors),
        "reserve_violation_rate": sum(trial.reserve_violation for trial in trials) / len(trials),
        "static_nash_miss_rate": (
            sum(trial.static_nash_miss for trial in static_missable) / len(static_missable)
            if static_missable
            else 0.0
        ),
        "last_price_miss_rate": (
            sum(trial.last_price_miss for trial in last_missable) / len(last_missable)
            if last_missable
            else 0.0
        ),
        "trace_blind_miss_rate": (
            sum(trial.trace_blind_miss for trial in trace_missable) / len(trace_missable)
            if trace_missable
            else 0.0
        ),
        "inventory_blind_miss_rate": (
            sum(trial.inventory_blind_miss for trial in inventory_missable) / len(inventory_missable)
            if inventory_missable
            else 0.0
        ),
        "trials": [_trace_inventory_trial_json(trial) for trial in trials],
    }


def summarize_market_trace_markdown_trials(
    agent_name: str,
    trials: list[TraceMarkdownMarketTrial],
) -> dict:
    regrets = [
        trial.constrained_terminal_cash_regret
        for trial in trials
        if trial.constrained_terminal_cash_regret is not None
    ]
    price_errors = [trial.price_l1_error for trial in trials if trial.price_l1_error is not None]
    static_missable = [
        trial for trial in trials if _pair_l1(trial.static_prices, trial.oracle_prices) >= 3.0
    ]
    one_price_missable = [
        trial for trial in trials if _pair_l1(trial.one_price_baseline, trial.oracle_prices) >= 3.0
    ]
    trace_missable = [
        trial for trial in trials if _pair_l1(trial.trace_blind_prices, trial.oracle_prices) >= 3.0
    ]
    inventory_missable = [
        trial
        for trial in trials
        if _pair_l1(trial.inventory_blind_prices, trial.oracle_prices) >= 3.0
    ]
    return {
        "task": "market_trace_markdown",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_constrained_terminal_cash_regret": mean(regrets),
        "mean_constrained_terminal_cash_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_price_l1_error": mean(price_errors),
        "reserve_violation_rate": sum(trial.reserve_violation for trial in trials) / len(trials),
        "static_nash_miss_rate": (
            sum(trial.static_nash_miss for trial in static_missable) / len(static_missable)
            if static_missable
            else 0.0
        ),
        "one_price_miss_rate": (
            sum(trial.one_price_miss for trial in one_price_missable) / len(one_price_missable)
            if one_price_missable
            else 0.0
        ),
        "trace_blind_miss_rate": (
            sum(trial.trace_blind_miss for trial in trace_missable) / len(trace_missable)
            if trace_missable
            else 0.0
        ),
        "inventory_blind_miss_rate": (
            sum(trial.inventory_blind_miss for trial in inventory_missable) / len(inventory_missable)
            if inventory_missable
            else 0.0
        ),
        "trials": [_trace_markdown_trial_json(trial) for trial in trials],
    }


def summarize_market_trace_replenishment_trials(
    agent_name: str,
    trials: list[TraceReplenishmentMarketTrial],
    *,
    task_name: str = "market_trace_replenishment",
) -> dict:
    regrets = [
        trial.constrained_terminal_cash_regret
        for trial in trials
        if trial.constrained_terminal_cash_regret is not None
    ]
    decision_errors = [
        trial.decision_l1_error for trial in trials if trial.decision_l1_error is not None
    ]
    no_replenishment_missable = [
        trial
        for trial in trials
        if _replenishment_decision_distance(
            trial.no_replenishment_decision,
            trial.oracle_decision,
        )
        >= 5.0
    ]
    one_price_missable = [
        trial
        for trial in trials
        if _replenishment_decision_distance(trial.one_price_decision, trial.oracle_decision)
        >= 5.0
    ]
    trace_missable = [
        trial
        for trial in trials
        if _replenishment_decision_distance(trial.trace_blind_decision, trial.oracle_decision)
        >= 5.0
    ]
    replenishment_missable = [
        trial
        for trial in trials
        if _replenishment_decision_distance(
            trial.replenishment_blind_decision,
            trial.oracle_decision,
        )
        >= 5.0
    ]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_constrained_terminal_cash_regret": mean(regrets),
        "mean_constrained_terminal_cash_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_decision_l1_error": mean(decision_errors),
        "reserve_violation_rate": sum(trial.reserve_violation for trial in trials) / len(trials),
        "no_replenishment_miss_rate": (
            sum(trial.no_replenishment_miss for trial in no_replenishment_missable)
            / len(no_replenishment_missable)
            if no_replenishment_missable
            else 0.0
        ),
        "one_price_miss_rate": (
            sum(trial.one_price_miss for trial in one_price_missable) / len(one_price_missable)
            if one_price_missable
            else 0.0
        ),
        "trace_blind_miss_rate": (
            sum(trial.trace_blind_miss for trial in trace_missable) / len(trace_missable)
            if trace_missable
            else 0.0
        ),
        "replenishment_blind_miss_rate": (
            sum(trial.replenishment_blind_miss for trial in replenishment_missable)
            / len(replenishment_missable)
            if replenishment_missable
            else 0.0
        ),
        "trials": [_trace_replenishment_trial_json(trial) for trial in trials],
    }


def _parse_price(response: str, case: MarketCase) -> float | None:
    parsed = parse_float("FINAL_PRICE", response)
    if parsed is None:
        return None
    return clamp(parsed, case.marginal_cost, case.p_max)


def _parse_policy_shift_price(response: str, case: PolicyShiftMarketCase) -> float | None:
    parsed = parse_float("FINAL_PRICE", response)
    if parsed is None:
        return None
    return clamp(parsed, case.marginal_cost, case.p_max)


def _parse_policy_inventory_price(response: str, case: InventoryPolicyMarketCase) -> float | None:
    parsed = parse_float("FINAL_PRICE", response)
    if parsed is None:
        return None
    return clamp(parsed, case.marginal_cost, case.p_max)


def _parse_trace_inventory_price(response: str, case: TraceInventoryMarketCase) -> float | None:
    parsed = parse_float("FINAL_PRICE", response)
    if parsed is None:
        return None
    return clamp(parsed, case.marginal_cost, case.p_max)


def _parse_trace_markdown_prices(
    response: str,
    case: TraceInventoryMarketCase,
) -> tuple[float, float] | None:
    early = parse_float("FINAL_PRICE_EARLY", response)
    late = parse_float("FINAL_PRICE_LATE", response)
    if early is None or late is None:
        return None
    return (
        clamp(early, case.marginal_cost, case.p_max),
        clamp(late, case.marginal_cost, case.p_max),
    )


def _parse_trace_replenishment_decision(
    response: str,
    case: TraceInventoryMarketCase,
) -> tuple[float, float, float] | None:
    early = parse_float("FINAL_PRICE_EARLY", response)
    late = parse_float("FINAL_PRICE_LATE", response)
    units = parse_float("FINAL_REPLENISH_UNITS", response)
    if early is None or late is None or units is None:
        return None
    return (
        clamp(early, case.marginal_cost, case.p_max),
        clamp(late, case.marginal_cost, case.p_max),
        clamp(units, 0.0, case.max_replenishment_units),
    )


def policy_shift_static_nash_price(case: PolicyShiftMarketCase) -> float:
    denom = 2.0 * case.own_price_slope - case.cross_price_slope
    if denom <= 0:
        return case.marginal_cost
    price = (
        case.base_demand
        + case.demand_shock
        + case.own_price_slope * case.marginal_cost
    ) / denom
    return clamp(price, case.marginal_cost, case.p_max)


def policy_shift_best_response(case: PolicyShiftMarketCase, opponent_price: float) -> float:
    price = (
        case.base_demand
        + case.demand_shock
        + case.cross_price_slope * opponent_price
        + case.own_price_slope * case.marginal_cost
    ) / (2.0 * case.own_price_slope)
    return clamp(price, case.marginal_cost, case.p_max)


def policy_shift_profit(
    case: PolicyShiftMarketCase,
    own_price: float,
    opponent_price: float,
) -> float:
    quantity = max(
        0.0,
        case.base_demand
        + case.demand_shock
        - case.own_price_slope * own_price
        + case.cross_price_slope * opponent_price,
    )
    return max(0.0, own_price - case.marginal_cost) * quantity


def policy_inventory_terminal_cash(
    case: InventoryPolicyMarketCase,
    own_price: float,
    opponent_price: float,
) -> float:
    inventory = case.starting_inventory
    cash = case.starting_cash
    shocks = case.demand_shocks or tuple(0.0 for _ in range(case.horizon))
    for period in range(case.horizon):
        shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            case.base_demand
            + case.demand_shock
            + shock
            - case.own_price_slope * own_price
            + case.cross_price_slope * opponent_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, own_price - case.marginal_cost) * sold
        inventory -= sold
        cash -= case.carrying_cost_per_unsold * inventory
    cash += case.terminal_inventory_value * inventory
    cash -= case.fixed_obligation
    return cash


def policy_inventory_oracle_price(case: InventoryPolicyMarketCase) -> float:
    predicted_opponent = policy_shift_opponent_price(case)
    reference = policy_shift_best_response(case, predicted_opponent)
    candidates = _policy_inventory_candidate_prices(case)
    return max(
        candidates,
        key=lambda price: (
            policy_inventory_terminal_cash(case, price, predicted_opponent),
            -abs(price - reference),
        ),
    )


def policy_shift_opponent_price(case: PolicyShiftMarketCase) -> float:
    history = case.opponent_price_history
    if not history:
        return policy_shift_static_nash_price(case)
    if len(history) == 1:
        return clamp(history[-1], case.marginal_cost, case.p_max)
    last = history[-1]
    step = last - history[-2]
    if case.opponent_policy == "liquidation_drop":
        price = last + 1.5 * step
    elif case.opponent_policy == "stockout_jump":
        price = last + 1.5 * max(0.0, step)
    elif case.opponent_policy == "entry_price_war":
        price = last + 1.5 * step
    elif case.opponent_policy == "capacity_exit":
        price = last + 2.0 * max(0.0, step)
    else:
        price = last
    return clamp(price, case.marginal_cost, case.p_max)


def trace_inventory_static_nash_price(case: TraceInventoryMarketCase) -> float:
    denom = 2.0 * case.own_price_slope - case.cross_price_slope
    if denom <= 0:
        return case.marginal_cost
    price = (
        case.base_demand
        + case.demand_shock
        + case.own_price_slope * case.marginal_cost
    ) / denom
    return clamp(price, case.marginal_cost, case.p_max)


def trace_inventory_best_response(case: TraceInventoryMarketCase, opponent_price: float) -> float:
    price = (
        case.base_demand
        + case.demand_shock
        + case.cross_price_slope * opponent_price
        + case.own_price_slope * case.marginal_cost
    ) / (2.0 * case.own_price_slope)
    return clamp(price, case.marginal_cost, case.p_max)


def trace_inventory_terminal_cash(
    case: TraceInventoryMarketCase,
    own_price: float,
    opponent_price: float,
) -> float:
    inventory = case.starting_inventory
    cash = case.starting_cash
    shocks = case.demand_shocks or tuple(0.0 for _ in range(case.horizon))
    for period in range(case.horizon):
        shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            case.base_demand
            + case.demand_shock
            + shock
            - case.own_price_slope * own_price
            + case.cross_price_slope * opponent_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, own_price - case.marginal_cost) * sold
        inventory -= sold
        cash -= case.carrying_cost_per_unsold * inventory
    cash += case.terminal_inventory_value * inventory
    cash -= case.fixed_obligation
    return cash


def trace_markdown_terminal_cash(
    case: TraceInventoryMarketCase,
    early_price: float,
    late_price: float,
    opponent_price: float,
) -> float:
    inventory = case.starting_inventory
    cash = case.starting_cash
    shocks = case.demand_shocks or tuple(0.0 for _ in range(case.horizon))
    switch_period = max(1, case.horizon // 2)
    for period in range(case.horizon):
        own_price = early_price if period < switch_period else late_price
        shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            case.base_demand
            + case.demand_shock
            + shock
            - case.own_price_slope * own_price
            + case.cross_price_slope * opponent_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, own_price - case.marginal_cost) * sold
        inventory -= sold
        cash -= case.carrying_cost_per_unsold * inventory
    cash += case.terminal_inventory_value * inventory
    cash -= case.fixed_obligation
    return cash


def trace_replenishment_terminal_cash(
    case: TraceInventoryMarketCase,
    early_price: float,
    late_price: float,
    replenishment_units: float,
    opponent_price: float,
) -> float:
    inventory = case.starting_inventory
    cash = case.starting_cash
    shocks = case.demand_shocks or tuple(0.0 for _ in range(case.horizon))
    switch_period = max(1, case.horizon // 2)
    storage_capacity = (
        case.replenishment_storage_capacity
        if case.replenishment_storage_capacity > 0
        else case.starting_inventory + case.max_replenishment_units
    )
    for period in range(case.horizon):
        if period == switch_period and replenishment_units > 0:
            received_units = min(
                replenishment_units,
                max(0.0, storage_capacity - inventory),
            )
            if received_units > 0:
                inventory += received_units
                cash -= (
                    case.replenishment_unit_cost * received_units
                    + case.replenishment_setup_cost
                )
        own_price = early_price if period < switch_period else late_price
        shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            case.base_demand
            + case.demand_shock
            + shock
            - case.own_price_slope * own_price
            + case.cross_price_slope * opponent_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, own_price - case.marginal_cost) * sold
        inventory -= sold
        cash -= case.carrying_cost_per_unsold * inventory
    cash += case.terminal_inventory_value * inventory
    cash -= case.fixed_obligation
    return cash


def trace_inventory_oracle_price(
    case: TraceInventoryMarketCase,
    *,
    opponent_price: float | None = None,
) -> float:
    predicted_opponent = trace_inventory_opponent_price(case) if opponent_price is None else opponent_price
    reference = trace_inventory_best_response(case, predicted_opponent)
    candidates = _trace_inventory_candidate_prices(case, predicted_opponent)
    return max(
        candidates,
        key=lambda price: (
            trace_inventory_terminal_cash(case, price, predicted_opponent),
            -abs(price - reference),
        ),
    )


def trace_markdown_oracle_prices(
    case: TraceInventoryMarketCase,
    *,
    opponent_price: float | None = None,
) -> tuple[float, float]:
    predicted_opponent = trace_inventory_opponent_price(case) if opponent_price is None else opponent_price
    reference = trace_inventory_best_response(case, predicted_opponent)
    candidates = _trace_inventory_candidate_prices(case, predicted_opponent)
    pairs = ((early, late) for early in candidates for late in candidates)
    return max(
        pairs,
        key=lambda pair: (
            trace_markdown_terminal_cash(case, pair[0], pair[1], predicted_opponent),
            -abs(pair[0] - reference) - abs(pair[1] - reference),
        ),
    )


def trace_replenishment_oracle_decision(
    case: TraceInventoryMarketCase,
    *,
    opponent_price: float | None = None,
    forced_replenishment: float | None = None,
    fixed_price: bool = False,
) -> tuple[float, float, float]:
    predicted_opponent = trace_inventory_opponent_price(case) if opponent_price is None else opponent_price
    price_candidates = _trace_inventory_candidate_prices(case, predicted_opponent)
    replenishment_candidates = (
        [clamp(forced_replenishment, 0.0, case.max_replenishment_units)]
        if forced_replenishment is not None
        else _trace_replenishment_candidate_units(case)
    )
    reference = trace_markdown_oracle_prices(case, opponent_price=predicted_opponent)
    if fixed_price:
        decisions = (
            (price, price, units)
            for price in price_candidates
            for units in replenishment_candidates
        )
    else:
        decisions = (
            (early, late, units)
            for early in price_candidates
            for late in price_candidates
            for units in replenishment_candidates
        )
    return max(
        decisions,
        key=lambda decision: (
            trace_replenishment_terminal_cash(
                case,
                decision[0],
                decision[1],
                decision[2],
                predicted_opponent,
            ),
            -abs(decision[0] - reference[0])
            - abs(decision[1] - reference[1])
            - 0.25 * abs(decision[2]),
        ),
    )


def trace_inventory_opponent_price(case: TraceInventoryMarketCase) -> float:
    trace = case.trace
    if not trace:
        return trace_inventory_static_nash_price(case)
    if len(trace) == 1:
        return clamp(trace[-1].opponent_price, case.marginal_cost, case.p_max)
    last = trace[-1]
    previous = trace[-2]
    step = last.opponent_price - previous.opponent_price
    stockout_pressure = max(0.0, 0.82 - last.opponent_fill_rate)
    clearance_pressure = max(0.0, last.opponent_remaining_inventory_share - 0.65)
    price = (
        last.opponent_price
        + 1.35 * step
        + 35.0 * stockout_pressure
        - 30.0 * clearance_pressure
    )
    return clamp(price, case.marginal_cost, case.p_max)


def _pair_l1(left: tuple[float, float], right: tuple[float, float]) -> float:
    return abs(left[0] - right[0]) + abs(left[1] - right[1])


def _replenishment_decision_distance(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    return abs(left[0] - right[0]) + abs(left[1] - right[1]) + 0.5 * abs(left[2] - right[2])


def _prompt(case: MarketCase, firm_id: str) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            f"firm_id={firm_id}",
            f"base_demand={case.base_demand:.4f}",
            f"own_price_slope={case.own_price_slope:.4f}",
            f"cross_price_slope={case.cross_price_slope:.4f}",
            f"marginal_cost={case.marginal_cost:.4f}",
            f"p_max={case.p_max:.4f}",
            f"horizon={case.horizon}",
            f"starting_inventory={case.starting_inventory:.4f}",
            f"starting_cash={case.starting_cash:.4f}",
            f"fixed_obligation={case.fixed_obligation:.4f}",
            f"min_terminal_cash={case.min_terminal_cash:.4f}",
            f"carrying_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
            f"terminal_inventory_value={case.terminal_inventory_value:.4f}",
            f"demand_shocks={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
            "Demand for each firm is q_i = base_demand - own_price_slope*p_i + cross_price_slope*p_j.",
            "Profit for each firm is (p_i - marginal_cost) * q_i.",
            "Firms choose prices simultaneously and cannot coordinate or collude.",
            "If horizon > 1, unsold inventory carries costs and terminal option value; meet terminal cash reserve.",
            "Choose the competitive best-response equilibrium price, not the joint-profit monopoly price.",
        ]
    )


def _policy_shift_prompt(case: PolicyShiftMarketCase) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            f"base_demand={case.base_demand:.4f}",
            f"demand_shock={case.demand_shock:.4f}",
            f"own_price_slope={case.own_price_slope:.4f}",
            f"cross_price_slope={case.cross_price_slope:.4f}",
            f"marginal_cost={case.marginal_cost:.4f}",
            f"p_max={case.p_max:.4f}",
            f"opponent_policy={case.opponent_policy}",
            f"opponent_price_history={','.join(f'{price:.4f}' for price in case.opponent_price_history)}",
            "Current demand is q_i = base_demand + demand_shock - own_price_slope*p_i + cross_price_slope*p_j.",
            "Profit is (p_i - marginal_cost) * q_i.",
            "Infer the competitor's next price from its recent price history and policy-shift signal.",
            "Choose your current non-collusive best-response price for the next selling period.",
            "Do not use the old static Nash price if the competitor policy has shifted.",
        ]
    )


def _policy_inventory_prompt(case: InventoryPolicyMarketCase) -> str:
    return "\n".join(
        [
            f"case={case.key}",
            f"real_case={case.real_case}",
            f"base_demand={case.base_demand:.4f}",
            f"demand_shock={case.demand_shock:.4f}",
            f"own_price_slope={case.own_price_slope:.4f}",
            f"cross_price_slope={case.cross_price_slope:.4f}",
            f"marginal_cost={case.marginal_cost:.4f}",
            f"p_max={case.p_max:.4f}",
            f"opponent_policy={case.opponent_policy}",
            f"opponent_price_history={','.join(f'{price:.4f}' for price in case.opponent_price_history)}",
            f"horizon={case.horizon}",
            f"starting_inventory={case.starting_inventory:.4f}",
            f"starting_cash={case.starting_cash:.4f}",
            f"fixed_obligation={case.fixed_obligation:.4f}",
            f"min_terminal_cash={case.min_terminal_cash:.4f}",
            f"carrying_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
            f"terminal_inventory_value={case.terminal_inventory_value:.4f}",
            f"demand_shocks={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
            "Current demand each period is q_i = base_demand + demand_shock + period_shock - own_price_slope*p_i + cross_price_slope*p_j.",
            "Infer the competitor's next price from its recent price path and policy-shift signal.",
            "Choose one non-collusive posted price to keep for the listed inventory horizon.",
            "Terminal cash equals starting cash plus gross margin on units sold, minus holding costs and the fixed obligation, plus terminal inventory value.",
            "Meet the terminal cash reserve while maximizing terminal cash; do not reuse the old static Nash price or only the one-period best response.",
        ]
    )


def _trace_inventory_prompt(case: TraceInventoryMarketCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"base_demand={case.base_demand:.4f}",
        f"demand_shock={case.demand_shock:.4f}",
        f"own_price_slope={case.own_price_slope:.4f}",
        f"cross_price_slope={case.cross_price_slope:.4f}",
        f"marginal_cost={case.marginal_cost:.4f}",
        f"p_max={case.p_max:.4f}",
        f"horizon={case.horizon}",
        f"starting_inventory={case.starting_inventory:.4f}",
        f"starting_cash={case.starting_cash:.4f}",
        f"fixed_obligation={case.fixed_obligation:.4f}",
        f"min_terminal_cash={case.min_terminal_cash:.4f}",
        f"carrying_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
        f"terminal_inventory_value={case.terminal_inventory_value:.4f}",
        f"demand_shocks={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
        "Recent competitor market trace rows:",
    ]
    for point in case.trace:
        lines.append(
            f"  trace period={point.period} "
            f"opponent_price={point.opponent_price:.4f} "
            f"opponent_fill_rate={point.opponent_fill_rate:.4f} "
            f"opponent_remaining_inventory_share={point.opponent_remaining_inventory_share:.4f}"
        )
    lines.extend(
        [
            "Demand each period is q_i = base_demand + demand_shock + period_shock - own_price_slope*p_i + cross_price_slope*p_j.",
            "The trace rows are not a price target: fill rates and remaining stock indicate whether the competitor is likely to keep cutting, ration capacity, or raise price next.",
            "Choose one non-collusive posted price to keep for the listed inventory horizon.",
            "Terminal cash equals starting cash plus gross margin on units sold, minus holding costs and the fixed obligation, plus terminal inventory value.",
            "Meet the terminal cash reserve while maximizing terminal cash.",
        ]
    )
    return "\n".join(lines)


def _trace_markdown_prompt(case: TraceInventoryMarketCase) -> str:
    switch_period = max(1, case.horizon // 2)
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"base_demand={case.base_demand:.4f}",
        f"demand_shock={case.demand_shock:.4f}",
        f"own_price_slope={case.own_price_slope:.4f}",
        f"cross_price_slope={case.cross_price_slope:.4f}",
        f"marginal_cost={case.marginal_cost:.4f}",
        f"p_max={case.p_max:.4f}",
        f"horizon={case.horizon}",
        f"early_price_periods=1_to_{switch_period}",
        f"late_price_periods={switch_period + 1}_to_{case.horizon}",
        f"starting_inventory={case.starting_inventory:.4f}",
        f"starting_cash={case.starting_cash:.4f}",
        f"fixed_obligation={case.fixed_obligation:.4f}",
        f"min_terminal_cash={case.min_terminal_cash:.4f}",
        f"carrying_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
        f"terminal_inventory_value={case.terminal_inventory_value:.4f}",
        f"demand_shocks={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
        "Recent competitor market trace rows:",
    ]
    for point in case.trace:
        lines.append(
            f"  trace period={point.period} "
            f"opponent_price={point.opponent_price:.4f} "
            f"opponent_fill_rate={point.opponent_fill_rate:.4f} "
            f"opponent_remaining_inventory_share={point.opponent_remaining_inventory_share:.4f}"
        )
    lines.extend(
        [
            "Demand each period is q_i = base_demand + demand_shock + period_shock - own_price_slope*p_i + cross_price_slope*p_j.",
            "The trace rows indicate whether the competitor is likely to keep cutting, ration capacity, or raise price next.",
            "Choose an early posted price for the early periods and a late posted price for the remaining periods.",
            "Terminal cash equals starting cash plus gross margin on units sold, minus holding costs and the fixed obligation, plus terminal inventory value.",
            "Meet the terminal cash reserve while maximizing terminal cash; a single fixed price may be dominated by a staged plan.",
        ]
    )
    return "\n".join(lines)


def _trace_replenishment_prompt(case: TraceInventoryMarketCase) -> str:
    switch_period = max(1, case.horizon // 2)
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"base_demand={case.base_demand:.4f}",
        f"demand_shock={case.demand_shock:.4f}",
        f"own_price_slope={case.own_price_slope:.4f}",
        f"cross_price_slope={case.cross_price_slope:.4f}",
        f"marginal_cost={case.marginal_cost:.4f}",
        f"p_max={case.p_max:.4f}",
        f"horizon={case.horizon}",
        f"early_price_periods=1_to_{switch_period}",
        f"late_price_periods={switch_period + 1}_to_{case.horizon}",
        f"replenishment_arrives_before_period={switch_period + 1}",
        f"starting_inventory={case.starting_inventory:.4f}",
        f"starting_cash={case.starting_cash:.4f}",
        f"fixed_obligation={case.fixed_obligation:.4f}",
        f"min_terminal_cash={case.min_terminal_cash:.4f}",
        f"carrying_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
        f"terminal_inventory_value={case.terminal_inventory_value:.4f}",
        f"replenishment_unit_cost={case.replenishment_unit_cost:.4f}",
        f"replenishment_setup_cost={case.replenishment_setup_cost:.4f}",
        f"max_replenishment_units={case.max_replenishment_units:.4f}",
        f"replenishment_storage_capacity={case.replenishment_storage_capacity:.4f}",
        f"demand_shocks={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
        "Recent competitor market trace rows:",
    ]
    for point in case.trace:
        lines.append(
            f"  trace period={point.period} "
            f"opponent_price={point.opponent_price:.4f} "
            f"opponent_fill_rate={point.opponent_fill_rate:.4f} "
            f"opponent_remaining_inventory_share={point.opponent_remaining_inventory_share:.4f}"
        )
    lines.extend(
        [
            "Demand each period is q_i = base_demand + demand_shock + period_shock - own_price_slope*p_i + cross_price_slope*p_j.",
            "The trace rows indicate whether the competitor is likely to keep cutting, ration capacity, or raise price next.",
            "If replenishment units are ordered, they arrive before the late window, cost the unit cost plus the setup cost, and cannot push on-hand inventory above storage capacity.",
            "Choose early and late posted prices plus replenishment units to maximize terminal cash while meeting the terminal cash reserve.",
            "A no-replenishment plan can stock out, but a blind replenishment plan can overbuy into a clearance market.",
        ]
    )
    return "\n".join(lines)


def _trace_replenishment_natural_prompt(case: TraceInventoryMarketCase) -> str:
    switch_period = max(1, case.horizon // 2)
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"base_customer_flow={case.base_demand:.4f}",
        f"demand_adjustment={case.demand_shock:.4f}",
        f"own_price_sensitivity={case.own_price_slope:.4f}",
        f"rival_price_lift={case.cross_price_slope:.4f}",
        f"sellable_unit_cost={case.marginal_cost:.4f}",
        f"posted_price_ceiling={case.p_max:.4f}",
        f"selling_windows={case.horizon}",
        f"early_window=1_to_{switch_period}",
        f"late_window={switch_period + 1}_to_{case.horizon}",
        f"restock_arrives_before_window={switch_period + 1}",
        f"starting_units={case.starting_inventory:.4f}",
        f"cash_on_hand={case.starting_cash:.4f}",
        f"cash_commitment={case.fixed_obligation:.4f}",
        f"cash_reserve_floor={case.min_terminal_cash:.4f}",
        f"shelf_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
        f"leftover_unit_credit={case.terminal_inventory_value:.4f}",
        f"restock_unit_cost={case.replenishment_unit_cost:.4f}",
        f"restock_setup_fee={case.replenishment_setup_cost:.4f}",
        f"restock_unit_limit={case.max_replenishment_units:.4f}",
        f"storage_ceiling={case.replenishment_storage_capacity:.4f}",
        f"window_demand_adjustments={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
        "Recent rival shelf observations:",
    ]
    for point in case.trace:
        lines.append(
            f"  rival_observation window={point.period} "
            f"rival_ticket={point.opponent_price:.4f} "
            f"sell_through={point.opponent_fill_rate:.4f} "
            f"shelf_left={point.opponent_remaining_inventory_share:.4f}"
        )
    lines.extend(
        [
            "Higher own prices reduce your unit sales; higher rival tickets raise your unit sales.",
            "Use sell-through and shelf-left patterns to judge whether the rival is clearing stock, "
            "running out of capacity, or likely to move the next ticket up.",
            "A restock arrives before the late window and costs the per-unit restock cost plus "
            "the setup fee, subject to the unit limit and storage ceiling.",
            "Choose early and late prices plus restock units to maximize ending cash while keeping "
            "the cash reserve floor; no restock can stock out, while blind restock can overbuy.",
        ]
    )
    return "\n".join(lines)


def _trace_replenishment_noisy_prompt(case: TraceInventoryMarketCase) -> str:
    switch_period = max(1, case.horizon // 2)
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"base_customer_flow={case.base_demand:.4f}",
        f"demand_adjustment={case.demand_shock:.4f}",
        f"own_price_sensitivity={case.own_price_slope:.4f}",
        f"rival_price_lift={case.cross_price_slope:.4f}",
        f"sellable_unit_cost={case.marginal_cost:.4f}",
        f"posted_price_ceiling={case.p_max:.4f}",
        f"selling_windows={case.horizon}",
        f"early_window=1_to_{switch_period}",
        f"late_window={switch_period + 1}_to_{case.horizon}",
        f"restock_arrives_before_window={switch_period + 1}",
        f"starting_units={case.starting_inventory:.4f}",
        f"cash_on_hand={case.starting_cash:.4f}",
        f"cash_commitment={case.fixed_obligation:.4f}",
        f"cash_reserve_floor={case.min_terminal_cash:.4f}",
        f"shelf_cost_per_unsold={case.carrying_cost_per_unsold:.4f}",
        f"leftover_unit_credit={case.terminal_inventory_value:.4f}",
        f"restock_unit_cost={case.replenishment_unit_cost:.4f}",
        f"restock_setup_fee={case.replenishment_setup_cost:.4f}",
        f"restock_unit_limit={case.max_replenishment_units:.4f}",
        f"storage_ceiling={case.replenishment_storage_capacity:.4f}",
        f"window_demand_adjustments={','.join(f'{shock:.4f}' for shock in case.demand_shocks)}",
        "Lumpy regional rival shelf observations:",
    ]
    for point in case.trace:
        lines.append(
            f"  rival_observation window={point.period} "
            f"rival_ticket={point.opponent_price:.4f} "
            f"sell_through={point.opponent_fill_rate:.4f} "
            f"shelf_left={point.opponent_remaining_inventory_share:.4f}"
        )
    lines.extend(
        [
            "Treat any single regional row as noisy; use the direction across ticket, "
            "sell-through, and shelf-left readings to infer whether the rival is clearing, "
            "rationing capacity, or likely to move the next ticket up.",
            "A restock arrives before the late window and costs the per-unit restock cost plus "
            "the setup fee, subject to the unit limit and storage ceiling.",
            "Choose early and late prices plus restock units to maximize ending cash while keeping "
            "the cash reserve floor; no restock can stock out, while blind restock can overbuy.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: MarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _policy_shift_trial_json(trial: PolicyShiftMarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _policy_inventory_trial_json(trial: InventoryPolicyMarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _trace_inventory_trial_json(trial: TraceInventoryMarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _trace_markdown_trial_json(trial: TraceMarkdownMarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _trace_replenishment_trial_json(trial: TraceReplenishmentMarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _candidate_prices(case: MarketCase) -> list[float]:
    candidates = {case.marginal_cost, case.p_max, nash_price(case), collusive_price(case)}
    for price in range(int(case.marginal_cost), int(case.p_max) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _policy_inventory_candidate_prices(case: InventoryPolicyMarketCase) -> list[float]:
    predicted = policy_shift_opponent_price(case)
    candidates = {
        case.marginal_cost,
        case.p_max,
        policy_shift_static_nash_price(case),
        policy_shift_best_response(case, predicted),
        policy_shift_best_response(case, case.opponent_price_history[-1]),
    }
    for price in range(int(case.marginal_cost), int(case.p_max) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _trace_inventory_candidate_prices(
    case: TraceInventoryMarketCase,
    predicted_opponent: float,
) -> list[float]:
    last_opponent = case.trace[-1].opponent_price if case.trace else predicted_opponent
    candidates = {
        case.marginal_cost,
        case.p_max,
        trace_inventory_static_nash_price(case),
        trace_inventory_best_response(case, predicted_opponent),
        trace_inventory_best_response(case, last_opponent),
    }
    for price in range(int(case.marginal_cost), int(case.p_max) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _trace_replenishment_candidate_units(case: TraceInventoryMarketCase) -> list[float]:
    max_units = case.max_replenishment_units
    if max_units <= 0:
        return [0.0]
    candidates = {0.0, max_units, max_units / 2.0}
    return sorted(clamp(units, 0.0, max_units) for units in candidates)
