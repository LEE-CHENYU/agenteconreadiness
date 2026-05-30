from __future__ import annotations

from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float
from aeread_lab.stats import bootstrap_mean_ci, mean


REVEALED_ALLOCATION_SYSTEM = (
    "TASK: revealed_allocation\n"
    "Infer the principal's risk preference from historical portfolio choices, then allocate "
    "across the target assets. Return three final lines only: "
    "FINAL_GROWTH_WEIGHT: <number>, FINAL_INCOME_WEIGHT: <number>, "
    "FINAL_HEDGE_WEIGHT: <number>."
)


@dataclass(frozen=True)
class PortfolioOption:
    option_id: str
    expected_return: float
    variance: float
    chosen: bool = False


@dataclass(frozen=True)
class HistoryMenu:
    menu_id: str
    options: tuple[PortfolioOption, ...]


@dataclass(frozen=True)
class AllocationAsset:
    asset_id: str
    expected_return: float
    variance: float


@dataclass(frozen=True)
class RevealedAllocationCase:
    key: str
    real_case: str
    principal_profile: str
    history: tuple[HistoryMenu, ...]
    assets: tuple[AllocationAsset, ...]


@dataclass
class RevealedAllocationTrial:
    case: RevealedAllocationCase
    inferred_gamma: float
    oracle_weights: dict[str, float]
    chosen_weights: dict[str, float] | None
    oracle_utility: float
    chosen_utility: float | None
    utility_regret: float | None
    weight_l1_error: float | None
    raw_response: str


DEFAULT_CASES = [
    RevealedAllocationCase(
        key="pension_defensive",
        real_case="13F-style pension mandate with a history of preferring smoother portfolios",
        principal_profile="capital-preservation pension board",
        history=(
            HistoryMenu(
                "rate_shock",
                (
                    PortfolioOption("growth_tilt", 0.118, 0.032, False),
                    PortfolioOption("balanced_income", 0.082, 0.010, True),
                    PortfolioOption("cash_heavy", 0.042, 0.002, False),
                ),
            ),
            HistoryMenu(
                "credit_spread",
                (
                    PortfolioOption("equity_credit", 0.126, 0.039, False),
                    PortfolioOption("quality_income", 0.074, 0.007, True),
                    PortfolioOption("cash_heavy", 0.039, 0.0015, False),
                ),
            ),
            HistoryMenu(
                "inflation",
                (
                    PortfolioOption("real_asset_barbell", 0.096, 0.019, True),
                    PortfolioOption("growth_tilt", 0.122, 0.034, False),
                    PortfolioOption("cash_heavy", 0.040, 0.002, False),
                ),
            ),
        ),
        assets=(
            AllocationAsset("growth", 0.130, 0.090),
            AllocationAsset("income", 0.070, 0.020),
            AllocationAsset("hedge", 0.035, 0.004),
        ),
    ),
    RevealedAllocationCase(
        key="endowment_growth",
        real_case="13F-style endowment mandate with tolerance for growth volatility",
        principal_profile="long-horizon endowment committee",
        history=(
            HistoryMenu(
                "tech_pullback",
                (
                    PortfolioOption("growth_tilt", 0.135, 0.050, True),
                    PortfolioOption("balanced_income", 0.087, 0.015, False),
                    PortfolioOption("cash_heavy", 0.044, 0.002, False),
                ),
            ),
            HistoryMenu(
                "credit_cycle",
                (
                    PortfolioOption("equity_credit", 0.128, 0.044, True),
                    PortfolioOption("quality_income", 0.083, 0.012, False),
                    PortfolioOption("cash_heavy", 0.041, 0.002, False),
                ),
            ),
            HistoryMenu(
                "inflation",
                (
                    PortfolioOption("real_asset_barbell", 0.104, 0.026, True),
                    PortfolioOption("cash_heavy", 0.045, 0.003, False),
                    PortfolioOption("defensive_income", 0.078, 0.010, False),
                ),
            ),
        ),
        assets=(
            AllocationAsset("growth", 0.145, 0.095),
            AllocationAsset("income", 0.076, 0.018),
            AllocationAsset("hedge", 0.045, 0.006),
        ),
    ),
    RevealedAllocationCase(
        key="family_office_balanced",
        real_case="13F-style family-office mandate balancing compounding and drawdown aversion",
        principal_profile="multi-generation family office",
        history=(
            HistoryMenu(
                "liquidity_event",
                (
                    PortfolioOption("growth_tilt", 0.126, 0.043, False),
                    PortfolioOption("balanced_income", 0.090, 0.017, True),
                    PortfolioOption("cash_heavy", 0.044, 0.002, False),
                ),
            ),
            HistoryMenu(
                "private_equity_call",
                (
                    PortfolioOption("equity_credit", 0.119, 0.036, True),
                    PortfolioOption("quality_income", 0.079, 0.010, False),
                    PortfolioOption("cash_heavy", 0.041, 0.002, False),
                ),
            ),
            HistoryMenu(
                "recession",
                (
                    PortfolioOption("growth_tilt", 0.120, 0.046, False),
                    PortfolioOption("defensive_income", 0.073, 0.008, True),
                    PortfolioOption("cash_heavy", 0.040, 0.002, False),
                ),
            ),
        ),
        assets=(
            AllocationAsset("growth", 0.132, 0.080),
            AllocationAsset("income", 0.074, 0.017),
            AllocationAsset("hedge", 0.040, 0.005),
        ),
    ),
]


def portfolio_utility(expected_return: float, variance: float, gamma: float) -> float:
    return expected_return - gamma * variance


def infer_gamma(case: RevealedAllocationCase) -> float:
    best_gamma = 1.0
    best_margin = -float("inf")
    for idx in range(10, 801):
        gamma = idx / 100.0
        margin = 0.0
        valid = True
        for menu in case.history:
            chosen = next(option for option in menu.options if option.chosen)
            chosen_u = portfolio_utility(chosen.expected_return, chosen.variance, gamma)
            alternatives = [option for option in menu.options if not option.chosen]
            best_alt = max(
                portfolio_utility(option.expected_return, option.variance, gamma)
                for option in alternatives
            )
            margin += chosen_u - best_alt
            valid = valid and chosen_u >= best_alt
        if (valid, margin) > (best_margin >= 0.0, best_margin):
            best_gamma = gamma
            best_margin = margin
    return best_gamma


def allocation_utility(weights: dict[str, float], assets: tuple[AllocationAsset, ...], gamma: float) -> float:
    asset_map = {asset.asset_id: asset for asset in assets}
    expected_return = sum(weights[asset_id] * asset_map[asset_id].expected_return for asset_id in weights)
    variance = sum((weights[asset_id] ** 2) * asset_map[asset_id].variance for asset_id in weights)
    return portfolio_utility(expected_return, variance, gamma)


def oracle_allocation(case: RevealedAllocationCase) -> tuple[float, dict[str, float]]:
    gamma = infer_gamma(case)
    return gamma, _best_allocation(case.assets, gamma)


def run_revealed_allocation_game(
    agent: Agent,
    cases: list[RevealedAllocationCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[RevealedAllocationTrial] = []
    for case in cases:
        gamma, oracle_weights = oracle_allocation(case)
        oracle_u = allocation_utility(oracle_weights, case.assets, gamma)
        response = agent.complete(REVEALED_ALLOCATION_SYSTEM, _prompt(case))
        chosen_weights = _parse_weights(response)
        chosen_u = (
            allocation_utility(chosen_weights, case.assets, gamma)
            if chosen_weights is not None
            else None
        )
        regret = oracle_u - chosen_u if chosen_u is not None else None
        l1_error = (
            sum(abs(chosen_weights[asset.asset_id] - oracle_weights[asset.asset_id]) for asset in case.assets)
            if chosen_weights is not None
            else None
        )
        trials.append(
            RevealedAllocationTrial(
                case=case,
                inferred_gamma=gamma,
                oracle_weights=oracle_weights,
                chosen_weights=chosen_weights,
                oracle_utility=oracle_u,
                chosen_utility=chosen_u,
                utility_regret=regret,
                weight_l1_error=l1_error,
                raw_response=response,
            )
        )
    regrets = [trial.utility_regret for trial in trials if trial.utility_regret is not None]
    errors = [trial.weight_l1_error for trial in trials if trial.weight_l1_error is not None]
    return {
        "task": "revealed_allocation",
        "agent": agent.name,
        "n_trials": len(trials),
        "parse_rate": len(regrets) / len(trials) if trials else 0.0,
        "mean_utility_regret": mean(regrets),
        "mean_utility_regret_ci95": bootstrap_mean_ci(regrets),
        "mean_weight_l1_error": mean(errors),
        "mean_weight_l1_error_ci95": bootstrap_mean_ci(errors),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _best_allocation(assets: tuple[AllocationAsset, ...], gamma: float) -> dict[str, float]:
    ids = [asset.asset_id for asset in assets]
    best_weights = {ids[0]: 1.0, ids[1]: 0.0, ids[2]: 0.0}
    best_u = -float("inf")
    for first in range(21):
        for second in range(21 - first):
            third = 20 - first - second
            weights = {
                ids[0]: first / 20.0,
                ids[1]: second / 20.0,
                ids[2]: third / 20.0,
            }
            utility = allocation_utility(weights, assets, gamma)
            if utility > best_u:
                best_u = utility
                best_weights = weights
    return best_weights


def _parse_weights(response: str) -> dict[str, float] | None:
    growth = parse_float("FINAL_GROWTH_WEIGHT", response)
    income = parse_float("FINAL_INCOME_WEIGHT", response)
    hedge = parse_float("FINAL_HEDGE_WEIGHT", response)
    if growth is None or income is None or hedge is None:
        return None
    weights = {
        "growth": clamp(growth, 0.0, 1.0),
        "income": clamp(income, 0.0, 1.0),
        "hedge": clamp(hedge, 0.0, 1.0),
    }
    total = sum(weights.values())
    if total <= 0.0:
        return None
    return {key: value / total for key, value in weights.items()}


def _prompt(case: RevealedAllocationCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"principal_profile={case.principal_profile}",
        "Historical choices reveal the principal's risk preference; chosen=1 marks the historical selection.",
    ]
    for menu in case.history:
        for option in menu.options:
            lines.append(
                "history_id={menu_id} option_id={option_id} expected_return={expected_return:.4f} "
                "variance={variance:.4f} chosen={chosen}".format(
                    menu_id=menu.menu_id,
                    option_id=option.option_id,
                    expected_return=option.expected_return,
                    variance=option.variance,
                    chosen=1 if option.chosen else 0,
                )
            )
    lines.append("Target allocation assets:")
    for asset in case.assets:
        lines.append(
            "asset_id={asset_id} expected_return={expected_return:.4f} variance={variance:.4f}".format(
                **asdict(asset)
            )
        )
    return "\n".join(lines)


def _trial_json(trial: RevealedAllocationTrial) -> dict:
    data = asdict(trial)
    data["case"] = {
        "key": trial.case.key,
        "real_case": trial.case.real_case,
        "principal_profile": trial.case.principal_profile,
    }
    return data
