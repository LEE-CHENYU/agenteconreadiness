from __future__ import annotations

from dataclasses import dataclass, asdict

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


def _trial_json(trial: MarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _policy_shift_trial_json(trial: PolicyShiftMarketTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _candidate_prices(case: MarketCase) -> list[float]:
    candidates = {case.marginal_cost, case.p_max, nash_price(case), collusive_price(case)}
    for price in range(int(case.marginal_cost), int(case.p_max) + 1):
        candidates.add(float(price))
    return sorted(candidates)
