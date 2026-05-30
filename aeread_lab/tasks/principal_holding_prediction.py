from __future__ import annotations

from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


PRINCIPAL_HOLDING_SYSTEM = (
    "TASK: principal_holding_prediction\n"
    "Predict the next disclosed holding change for the named principal from "
    "their prior 13F-style choices. Return one final line only: "
    "FINAL_TRADE: <trade_id>."
)


STYLE_WEIGHTS = {
    "quality_defensive": {
        "expected_return": 0.70,
        "quality": 1.45,
        "value": 0.35,
        "momentum": 0.10,
        "volatility": -1.15,
        "turnover_cost": -0.95,
        "concentration_delta": -0.75,
        "liquidity": 0.45,
    },
    "growth_momentum": {
        "expected_return": 1.25,
        "quality": 0.45,
        "value": -0.25,
        "momentum": 1.25,
        "volatility": -0.35,
        "turnover_cost": -0.35,
        "concentration_delta": 0.15,
        "liquidity": 0.10,
    },
    "value_discipline": {
        "expected_return": 0.75,
        "quality": 0.40,
        "value": 1.50,
        "momentum": -0.10,
        "volatility": -0.70,
        "turnover_cost": -1.05,
        "concentration_delta": -0.70,
        "liquidity": 0.30,
    },
    "concentrated_quality": {
        "expected_return": 0.95,
        "quality": 1.10,
        "value": 0.10,
        "momentum": 0.55,
        "volatility": -0.50,
        "turnover_cost": -0.25,
        "concentration_delta": 0.80,
        "liquidity": -0.15,
    },
}

GENERIC_STYLE_WEIGHTS = {
    "expected_return": 0.95,
    "quality": 0.45,
    "value": 0.35,
    "momentum": 0.35,
    "volatility": -0.45,
    "turnover_cost": -0.45,
    "concentration_delta": -0.25,
    "liquidity": 0.20,
}

FEATURE_FIELDS = tuple(GENERIC_STYLE_WEIGHTS)


@dataclass(frozen=True)
class HoldingTrade:
    trade_id: str
    issuer: str
    expected_return: float
    quality: float
    value: float
    momentum: float
    volatility: float
    turnover_cost: float
    concentration_delta: float
    liquidity: float
    chosen: bool = False


@dataclass(frozen=True)
class HoldingHistoryMenu:
    menu_id: str
    trades: tuple[HoldingTrade, ...]


@dataclass(frozen=True)
class PrincipalHoldingCase:
    key: str
    real_case: str
    principal_profile: str
    history: tuple[HoldingHistoryMenu, ...]
    target_trades: tuple[HoldingTrade, ...]


@dataclass
class PrincipalHoldingTrial:
    case: PrincipalHoldingCase
    inferred_style: str
    principal_trade: str
    max_return_trade: str
    low_turnover_trade: str
    generic_style_trade: str
    chosen_trade: str | None
    principal_score: float
    chosen_score: float | None
    score_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    PrincipalHoldingCase(
        key="pension_quality_rotation",
        real_case="13F-style pension manager rotating after a rate shock",
        principal_profile="capital-preservation pension board",
        history=(
            HoldingHistoryMenu(
                "rate_shock_q1",
                (
                    HoldingTrade("add_quality_insurer", "QUALITY_INS", 0.090, 0.88, 0.62, 0.42, 0.22, 0.12, 0.05, 0.72, True),
                    HoldingTrade("buy_ai_beta", "AI_BETA", 0.170, 0.48, 0.28, 0.86, 0.74, 0.30, 0.36, 0.62),
                    HoldingTrade("hold_short_bills", "T_BILLS", 0.045, 0.70, 0.55, 0.10, 0.05, 0.02, -0.18, 0.95),
                ),
            ),
            HoldingHistoryMenu(
                "credit_spread_q2",
                (
                    HoldingTrade("add_rail_compounder", "RAIL_CORE", 0.086, 0.91, 0.58, 0.38, 0.20, 0.10, 0.03, 0.69, True),
                    HoldingTrade("chase_cloud_breakout", "CLOUD_HIGH", 0.162, 0.52, 0.25, 0.90, 0.79, 0.31, 0.33, 0.61),
                    HoldingTrade("cut_equity_risk", "CASH_PROXY", 0.038, 0.66, 0.60, 0.04, 0.04, 0.03, -0.22, 0.96),
                ),
            ),
            HoldingHistoryMenu(
                "recession_q3",
                (
                    HoldingTrade("add_healthcare_quality", "HEALTH_STEADY", 0.082, 0.93, 0.52, 0.34, 0.18, 0.11, 0.04, 0.73, True),
                    HoldingTrade("buy_cyclical_rebound", "CYCLIC_REBOUND", 0.155, 0.45, 0.42, 0.79, 0.70, 0.28, 0.31, 0.58),
                    HoldingTrade("raise_cash_only", "CASH_PROXY", 0.040, 0.65, 0.60, 0.06, 0.04, 0.02, -0.20, 0.97),
                ),
            ),
        ),
        target_trades=(
            HoldingTrade("add_quality_utility", "UTILITY_CORE", 0.084, 0.92, 0.57, 0.36, 0.19, 0.10, 0.04, 0.76),
            HoldingTrade("buy_ai_momentum", "AI_MOMENTUM", 0.178, 0.50, 0.23, 0.92, 0.78, 0.32, 0.35, 0.60),
            HoldingTrade("move_to_cash", "CASH_PROXY", 0.041, 0.66, 0.58, 0.05, 0.04, 0.02, -0.21, 0.96),
            HoldingTrade("add_discount_bank", "BANK_VALUE", 0.104, 0.64, 0.78, 0.31, 0.40, 0.18, 0.12, 0.70),
        ),
    ),
    PrincipalHoldingCase(
        key="endowment_growth_continuation",
        real_case="13F-style endowment manager adding after durable momentum",
        principal_profile="long-horizon growth endowment",
        history=(
            HoldingHistoryMenu(
                "tech_pullback_q1",
                (
                    HoldingTrade("add_platform_winner", "PLATFORM_WIN", 0.154, 0.73, 0.30, 0.91, 0.58, 0.20, 0.18, 0.64, True),
                    HoldingTrade("buy_deep_value_bank", "BANK_VALUE", 0.104, 0.64, 0.82, 0.28, 0.39, 0.16, 0.06, 0.70),
                    HoldingTrade("trim_to_cash", "CASH_PROXY", 0.042, 0.65, 0.57, 0.05, 0.04, 0.03, -0.20, 0.96),
                ),
            ),
            HoldingHistoryMenu(
                "software_q2",
                (
                    HoldingTrade("add_software_compounder", "SOFT_COMP", 0.148, 0.77, 0.35, 0.88, 0.55, 0.19, 0.19, 0.62, True),
                    HoldingTrade("add_low_vol_consumer", "CONSUMER_LOW", 0.078, 0.89, 0.60, 0.32, 0.18, 0.11, 0.04, 0.74),
                    HoldingTrade("buy_energy_value", "ENERGY_VALUE", 0.118, 0.51, 0.86, 0.35, 0.50, 0.24, 0.12, 0.67),
                ),
            ),
            HoldingHistoryMenu(
                "ai_supply_q3",
                (
                    HoldingTrade("add_semicap_leader", "SEMICAP_LEAD", 0.166, 0.70, 0.26, 0.94, 0.62, 0.23, 0.22, 0.59, True),
                    HoldingTrade("rebalance_quality", "QUALITY_INS", 0.086, 0.90, 0.61, 0.38, 0.20, 0.10, 0.04, 0.72),
                    HoldingTrade("buy_cheap_retail", "RETAIL_VALUE", 0.112, 0.47, 0.88, 0.30, 0.45, 0.22, 0.10, 0.65),
                ),
            ),
        ),
        target_trades=(
            HoldingTrade("add_ai_platform", "AI_PLATFORM", 0.158, 0.75, 0.32, 0.90, 0.56, 0.20, 0.18, 0.63),
            HoldingTrade("buy_max_return_biotech", "BIOTECH_OPTION", 0.190, 0.40, 0.20, 0.78, 0.92, 0.37, 0.40, 0.48),
            HoldingTrade("buy_deep_value_energy", "ENERGY_VALUE", 0.120, 0.52, 0.87, 0.34, 0.49, 0.24, 0.12, 0.66),
            HoldingTrade("hold_cash", "CASH_PROXY", 0.042, 0.65, 0.57, 0.05, 0.04, 0.03, -0.20, 0.96),
        ),
    ),
    PrincipalHoldingCase(
        key="family_office_value_trim",
        real_case="13F-style family office avoiding crowded momentum after inflows",
        principal_profile="multi-generation value-disciplined family office",
        history=(
            HoldingHistoryMenu(
                "liquidity_event_q1",
                (
                    HoldingTrade("add_discount_industrial", "INDUSTRIAL_VALUE", 0.102, 0.63, 0.88, 0.30, 0.34, 0.12, 0.02, 0.70, True),
                    HoldingTrade("buy_high_beta_growth", "GROWTH_BETA", 0.168, 0.46, 0.22, 0.84, 0.77, 0.30, 0.36, 0.57),
                    HoldingTrade("do_nothing_cash", "CASH_PROXY", 0.041, 0.66, 0.58, 0.05, 0.04, 0.02, -0.20, 0.96),
                ),
            ),
            HoldingHistoryMenu(
                "valuation_spread_q2",
                (
                    HoldingTrade("add_healthcare_value", "HEALTH_VALUE", 0.098, 0.70, 0.84, 0.34, 0.31, 0.13, 0.04, 0.72, True),
                    HoldingTrade("add_cloud_leader", "CLOUD_HIGH", 0.160, 0.55, 0.28, 0.88, 0.72, 0.29, 0.32, 0.60),
                    HoldingTrade("buy_low_vol_bond_proxy", "BOND_PROXY", 0.052, 0.72, 0.61, 0.12, 0.09, 0.06, -0.08, 0.91),
                ),
            ),
            HoldingHistoryMenu(
                "tax_loss_q3",
                (
                    HoldingTrade("swap_to_cheaper_peer", "CHEAP_PEER", 0.094, 0.62, 0.90, 0.24, 0.30, 0.10, -0.02, 0.69, True),
                    HoldingTrade("add_momentum_winner", "MOMENTUM_WIN", 0.150, 0.48, 0.26, 0.91, 0.70, 0.27, 0.34, 0.58),
                    HoldingTrade("raise_cash", "CASH_PROXY", 0.040, 0.66, 0.60, 0.05, 0.04, 0.02, -0.18, 0.97),
                ),
            ),
        ),
        target_trades=(
            HoldingTrade("add_cheap_quality", "CHEAP_QUALITY", 0.096, 0.73, 0.86, 0.32, 0.30, 0.12, 0.03, 0.73),
            HoldingTrade("buy_max_return_saas", "SAAS_HIGH", 0.172, 0.54, 0.24, 0.89, 0.76, 0.30, 0.35, 0.59),
            HoldingTrade("minimize_turnover_hold", "CURRENT_HOLD", 0.060, 0.70, 0.58, 0.18, 0.18, 0.01, 0.00, 0.90),
            HoldingTrade("buy_safe_utility", "UTILITY_CORE", 0.078, 0.88, 0.58, 0.30, 0.20, 0.10, 0.02, 0.77),
        ),
    ),
    PrincipalHoldingCase(
        key="activist_concentrated_add",
        real_case="13F-style activist manager building a concentrated campaign position",
        principal_profile="concentrated quality activist",
        history=(
            HoldingHistoryMenu(
                "campaign_q1",
                (
                    HoldingTrade("add_board_campaign", "BOARD_CAMPAIGN", 0.126, 0.82, 0.42, 0.66, 0.42, 0.18, 0.32, 0.50, True),
                    HoldingTrade("buy_high_return_smallcap", "SMALLCAP_OPTION", 0.180, 0.38, 0.36, 0.70, 0.88, 0.35, 0.20, 0.38),
                    HoldingTrade("diversify_index", "INDEX_PROXY", 0.072, 0.68, 0.58, 0.28, 0.18, 0.05, -0.22, 0.94),
                ),
            ),
            HoldingHistoryMenu(
                "engagement_q2",
                (
                    HoldingTrade("add_quality_target", "QUALITY_TARGET", 0.118, 0.86, 0.48, 0.62, 0.38, 0.16, 0.30, 0.52, True),
                    HoldingTrade("buy_deep_value_spread", "CHEAP_SPREAD", 0.108, 0.56, 0.88, 0.22, 0.41, 0.20, 0.06, 0.63),
                    HoldingTrade("trim_concentration", "INDEX_PROXY", 0.070, 0.68, 0.58, 0.28, 0.18, 0.05, -0.24, 0.95),
                ),
            ),
            HoldingHistoryMenu(
                "settlement_q3",
                (
                    HoldingTrade("add_follow_on_block", "FOLLOW_BLOCK", 0.121, 0.84, 0.44, 0.64, 0.40, 0.17, 0.34, 0.49, True),
                    HoldingTrade("buy_fast_growth", "FAST_GROWTH", 0.162, 0.48, 0.24, 0.84, 0.76, 0.31, 0.24, 0.56),
                    HoldingTrade("reduce_to_cash", "CASH_PROXY", 0.041, 0.66, 0.58, 0.05, 0.04, 0.02, -0.20, 0.96),
                ),
            ),
        ),
        target_trades=(
            HoldingTrade("add_campaign_block", "CAMPAIGN_BLOCK", 0.120, 0.85, 0.46, 0.65, 0.40, 0.17, 0.33, 0.50),
            HoldingTrade("buy_max_return_option", "OPTIONALITY", 0.184, 0.42, 0.22, 0.78, 0.90, 0.36, 0.22, 0.42),
            HoldingTrade("diversify_low_turnover", "INDEX_PROXY", 0.073, 0.68, 0.58, 0.30, 0.18, 0.04, -0.25, 0.94),
            HoldingTrade("buy_value_peer", "VALUE_PEER", 0.105, 0.58, 0.86, 0.27, 0.42, 0.20, 0.06, 0.64),
        ),
    ),
]


def trade_utility(
    trade: HoldingTrade,
    weights: dict[str, float],
) -> float:
    values = asdict(trade)
    return sum(weights[field] * float(values[field]) for field in FEATURE_FIELDS)


def infer_principal_style(case: PrincipalHoldingCase) -> str:
    best_style = next(iter(STYLE_WEIGHTS))
    best_score = (-1, -float("inf"))
    for style_id, weights in STYLE_WEIGHTS.items():
        valid = True
        margin = 0.0
        for menu in case.history:
            chosen = next(trade for trade in menu.trades if trade.chosen)
            chosen_u = trade_utility(chosen, weights)
            best_alt = max(
                trade_utility(trade, weights)
                for trade in menu.trades
                if not trade.chosen
            )
            valid = valid and chosen_u >= best_alt
            margin += chosen_u - best_alt
        score = (1 if valid else 0, margin)
        if score > best_score:
            best_style = style_id
            best_score = score
    return best_style


def principal_trade(case: PrincipalHoldingCase) -> tuple[str, str]:
    style_id = infer_principal_style(case)
    weights = STYLE_WEIGHTS[style_id]
    trade = max(case.target_trades, key=lambda candidate: trade_utility(candidate, weights))
    return style_id, trade.trade_id


def max_return_trade(case: PrincipalHoldingCase) -> str:
    return max(case.target_trades, key=lambda trade: trade.expected_return).trade_id


def low_turnover_trade(case: PrincipalHoldingCase) -> str:
    return min(case.target_trades, key=lambda trade: trade.turnover_cost).trade_id


def generic_style_trade(case: PrincipalHoldingCase) -> str:
    return max(
        case.target_trades,
        key=lambda candidate: trade_utility(candidate, GENERIC_STYLE_WEIGHTS),
    ).trade_id


def run_principal_holding_prediction_game(
    agent: Agent,
    cases: list[PrincipalHoldingCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[PrincipalHoldingTrial] = []
    for case in cases:
        style_id, expected_trade = principal_trade(case)
        weights = STYLE_WEIGHTS[style_id]
        target_by_id = {trade.trade_id: trade for trade in case.target_trades}
        principal_score = trade_utility(target_by_id[expected_trade], weights)
        response = agent.complete(PRINCIPAL_HOLDING_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_TRADE", response)
        chosen = chosen if chosen in target_by_id else None
        chosen_score = trade_utility(target_by_id[chosen], weights) if chosen else None
        trials.append(
            PrincipalHoldingTrial(
                case=case,
                inferred_style=style_id,
                principal_trade=expected_trade,
                max_return_trade=max_return_trade(case),
                low_turnover_trade=low_turnover_trade(case),
                generic_style_trade=generic_style_trade(case),
                chosen_trade=chosen,
                principal_score=principal_score,
                chosen_score=chosen_score,
                score_regret=principal_score - chosen_score if chosen_score is not None else None,
                raw_response=response,
            )
        )
    return summarize_principal_holding_trials(agent.name, trials)


def summarize_principal_holding_trials(
    agent_name: str,
    trials: list[PrincipalHoldingTrial],
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    parsed = [trial for trial in trials if trial.chosen_trade is not None]
    max_return_missable = [
        trial for trial in trials if trial.max_return_trade != trial.principal_trade
    ]
    low_turnover_missable = [
        trial for trial in trials if trial.low_turnover_trade != trial.principal_trade
    ]
    generic_missable = [
        trial for trial in trials if trial.generic_style_trade != trial.principal_trade
    ]
    return {
        "task": "principal_holding_prediction",
        "agent": agent_name,
        "n_trials": len(trials),
        "parse_rate": len(parsed) / len(trials) if trials else 0.0,
        "accuracy": (
            sum(trial.chosen_trade == trial.principal_trade for trial in parsed) / len(trials)
            if trials
            else 0.0
        ),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "market_return_miss_rate": (
            sum(trial.chosen_trade == trial.max_return_trade for trial in max_return_missable)
            / len(max_return_missable)
            if max_return_missable
            else 0.0
        ),
        "low_turnover_miss_rate": (
            sum(trial.chosen_trade == trial.low_turnover_trade for trial in low_turnover_missable)
            / len(low_turnover_missable)
            if low_turnover_missable
            else 0.0
        ),
        "generic_style_miss_rate": (
            sum(trial.chosen_trade == trial.generic_style_trade for trial in generic_missable)
            / len(generic_missable)
            if generic_missable
            else 0.0
        ),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: PrincipalHoldingCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"principal_profile={case.principal_profile}",
        "Historical 13F-style choices reveal this principal's trade pattern; chosen=1 marks the disclosed choice.",
        "The target is predict-the-principal: predict what this principal will disclose next, not which trade will beat the market.",
    ]
    for menu in case.history:
        for trade in menu.trades:
            lines.append(_trade_line("history_decision", menu.menu_id, trade))
    lines.append("Next-quarter candidate holding changes:")
    for trade in case.target_trades:
        lines.append(_trade_line("candidate_trade", "", trade))
    lines.append(
        "Use the historical revealed choices to infer the principal's style. "
        "Do not simply choose the highest expected_return, the lowest turnover_cost, "
        "or a generic balanced style unless that is what the principal's past choices imply."
    )
    return "\n".join(lines)


def _trade_line(prefix: str, menu_id: str, trade: HoldingTrade) -> str:
    menu_part = f"menu_id={menu_id} " if menu_id else ""
    return (
        f"{prefix}={trade.trade_id} "
        f"{menu_part}"
        f"issuer={trade.issuer} "
        f"expected_return={trade.expected_return:.4f} "
        f"quality={trade.quality:.4f} "
        f"value={trade.value:.4f} "
        f"momentum={trade.momentum:.4f} "
        f"volatility={trade.volatility:.4f} "
        f"turnover_cost={trade.turnover_cost:.4f} "
        f"concentration_delta={trade.concentration_delta:.4f} "
        f"liquidity={trade.liquidity:.4f} "
        f"chosen={1 if trade.chosen else 0}"
    )


def _trial_json(trial: PrincipalHoldingTrial) -> dict:
    data = asdict(trial)
    data["case"] = {
        "key": trial.case.key,
        "real_case": trial.case.real_case,
        "principal_profile": trial.case.principal_profile,
    }
    return data
