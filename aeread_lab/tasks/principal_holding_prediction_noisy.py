from __future__ import annotations

from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean
from aeread_lab.tasks.principal_holding_prediction import (
    GENERIC_STYLE_WEIGHTS,
    STYLE_WEIGHTS,
)


NOISY_PRINCIPAL_HOLDING_SYSTEM = (
    "TASK: principal_holding_prediction_noisy\n"
    "Predict the next discretionary holding change for the named principal from "
    "noisy 13F-style disclosures. Return one final line only: "
    "FINAL_TRADE: <trade_id>."
)

FEATURE_FIELDS = tuple(GENERIC_STYLE_WEIGHTS)
DELIBERATE_EVENTS = {
    "manager_thesis",
    "quality_rotation",
    "growth_thesis",
    "valuation_thesis",
    "engagement_add",
}


@dataclass(frozen=True)
class NoisyHoldingTrade:
    trade_id: str
    issuer: str
    event_type: str
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
class NoisyHoldingHistoryMenu:
    menu_id: str
    trades: tuple[NoisyHoldingTrade, ...]


@dataclass(frozen=True)
class NoisyPrincipalHoldingCase:
    key: str
    real_case: str
    principal_profile: str
    history: tuple[NoisyHoldingHistoryMenu, ...]
    target_trades: tuple[NoisyHoldingTrade, ...]


@dataclass
class NoisyPrincipalHoldingTrial:
    case: NoisyPrincipalHoldingCase
    inferred_style: str
    flow_blind_style: str
    principal_trade: str
    max_return_trade: str
    low_turnover_trade: str
    generic_style_trade: str
    mechanical_flow_trade: str
    chosen_trade: str | None
    principal_score: float
    chosen_score: float | None
    score_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    NoisyPrincipalHoldingCase(
        key="pension_outflow_quality_signal",
        real_case="13F-style pension filing with redemptions mixed into quality rotation",
        principal_profile="capital-preservation pension board",
        history=(
            NoisyHoldingHistoryMenu(
                "q1_discretionary",
                (
                    NoisyHoldingTrade("add_quality_insurer", "QUALITY_INS", "quality_rotation", 0.090, 0.88, 0.62, 0.42, 0.22, 0.12, 0.05, 0.72, True),
                    NoisyHoldingTrade("buy_ai_beta", "AI_BETA", "growth_thesis", 0.170, 0.48, 0.28, 0.86, 0.74, 0.30, 0.36, 0.62),
                    NoisyHoldingTrade("hold_short_bills", "T_BILLS", "fund_flow", 0.045, 0.70, 0.55, 0.10, 0.05, 0.02, -0.18, 0.95),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q2_redemption",
                (
                    NoisyHoldingTrade("redeem_to_cash", "CASH_PROXY", "redemption", 0.040, 0.66, 0.58, 0.05, 0.04, 0.02, -0.28, 0.97, True),
                    NoisyHoldingTrade("add_rail_compounder", "RAIL_CORE", "quality_rotation", 0.086, 0.91, 0.58, 0.38, 0.20, 0.10, 0.03, 0.69),
                    NoisyHoldingTrade("chase_cloud_breakout", "CLOUD_HIGH", "growth_thesis", 0.162, 0.52, 0.25, 0.90, 0.79, 0.31, 0.33, 0.61),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q3_discretionary",
                (
                    NoisyHoldingTrade("add_healthcare_quality", "HEALTH_STEADY", "quality_rotation", 0.082, 0.93, 0.52, 0.34, 0.18, 0.11, 0.04, 0.73, True),
                    NoisyHoldingTrade("buy_cyclical_rebound", "CYCLIC_REBOUND", "valuation_thesis", 0.155, 0.45, 0.42, 0.79, 0.70, 0.28, 0.31, 0.58),
                    NoisyHoldingTrade("raise_cash_only", "CASH_PROXY", "fund_flow", 0.040, 0.65, 0.60, 0.06, 0.04, 0.02, -0.20, 0.97),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q4_index",
                (
                    NoisyHoldingTrade("match_index_weight", "INDEX_PROXY", "index_rebalance", 0.070, 0.68, 0.58, 0.28, 0.18, 0.04, -0.24, 0.94, True),
                    NoisyHoldingTrade("add_quality_utility", "UTILITY_CORE", "quality_rotation", 0.084, 0.92, 0.57, 0.36, 0.19, 0.10, 0.04, 0.76),
                    NoisyHoldingTrade("buy_ai_momentum", "AI_MOMENTUM", "growth_thesis", 0.178, 0.50, 0.23, 0.92, 0.78, 0.32, 0.35, 0.60),
                ),
            ),
        ),
        target_trades=(
            NoisyHoldingTrade("add_quality_utility", "UTILITY_CORE", "candidate", 0.084, 0.92, 0.57, 0.36, 0.19, 0.10, 0.04, 0.76),
            NoisyHoldingTrade("buy_ai_momentum", "AI_MOMENTUM", "candidate", 0.178, 0.50, 0.23, 0.92, 0.78, 0.32, 0.35, 0.60),
            NoisyHoldingTrade("move_to_cash", "CASH_PROXY", "candidate", 0.041, 0.66, 0.58, 0.05, 0.04, 0.02, -0.21, 0.96),
            NoisyHoldingTrade("add_discount_bank", "BANK_VALUE", "candidate", 0.104, 0.64, 0.78, 0.31, 0.40, 0.18, 0.12, 0.70),
        ),
    ),
    NoisyPrincipalHoldingCase(
        key="endowment_index_noise_growth_signal",
        real_case="13F-style endowment filing with passive index adds hiding growth continuation",
        principal_profile="long-horizon growth endowment",
        history=(
            NoisyHoldingHistoryMenu(
                "q1_discretionary",
                (
                    NoisyHoldingTrade("add_platform_winner", "PLATFORM_WIN", "growth_thesis", 0.154, 0.73, 0.30, 0.91, 0.58, 0.20, 0.18, 0.64, True),
                    NoisyHoldingTrade("buy_deep_value_bank", "BANK_VALUE", "valuation_thesis", 0.104, 0.64, 0.82, 0.28, 0.39, 0.16, 0.06, 0.70),
                    NoisyHoldingTrade("trim_to_cash", "CASH_PROXY", "fund_flow", 0.042, 0.65, 0.57, 0.05, 0.04, 0.03, -0.20, 0.96),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q2_index",
                (
                    NoisyHoldingTrade("passive_index_topup", "INDEX_PROXY", "index_rebalance", 0.072, 0.69, 0.58, 0.29, 0.18, 0.04, -0.18, 0.94, True),
                    NoisyHoldingTrade("add_software_compounder", "SOFT_COMP", "growth_thesis", 0.148, 0.77, 0.35, 0.88, 0.55, 0.19, 0.19, 0.62),
                    NoisyHoldingTrade("buy_energy_value", "ENERGY_VALUE", "valuation_thesis", 0.118, 0.51, 0.86, 0.35, 0.50, 0.24, 0.12, 0.67),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q3_discretionary",
                (
                    NoisyHoldingTrade("add_semicap_leader", "SEMICAP_LEAD", "growth_thesis", 0.166, 0.70, 0.26, 0.94, 0.62, 0.23, 0.22, 0.59, True),
                    NoisyHoldingTrade("rebalance_quality", "QUALITY_INS", "quality_rotation", 0.086, 0.90, 0.61, 0.38, 0.20, 0.10, 0.04, 0.72),
                    NoisyHoldingTrade("buy_cheap_retail", "RETAIL_VALUE", "valuation_thesis", 0.112, 0.47, 0.88, 0.30, 0.45, 0.22, 0.10, 0.65),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q4_tax",
                (
                    NoisyHoldingTrade("harvest_loss_peer", "CHEAP_PEER", "tax_loss", 0.094, 0.62, 0.90, 0.24, 0.30, 0.10, -0.02, 0.69, True),
                    NoisyHoldingTrade("add_ai_platform", "AI_PLATFORM", "growth_thesis", 0.158, 0.75, 0.32, 0.90, 0.56, 0.20, 0.18, 0.63),
                    NoisyHoldingTrade("hold_cash", "CASH_PROXY", "fund_flow", 0.042, 0.65, 0.57, 0.05, 0.04, 0.03, -0.20, 0.96),
                ),
            ),
        ),
        target_trades=(
            NoisyHoldingTrade("add_ai_platform", "AI_PLATFORM", "candidate", 0.158, 0.75, 0.32, 0.90, 0.56, 0.20, 0.18, 0.63),
            NoisyHoldingTrade("buy_max_return_biotech", "BIOTECH_OPTION", "candidate", 0.190, 0.40, 0.20, 0.78, 0.92, 0.37, 0.40, 0.48),
            NoisyHoldingTrade("buy_deep_value_energy", "ENERGY_VALUE", "candidate", 0.120, 0.52, 0.87, 0.34, 0.49, 0.24, 0.12, 0.66),
            NoisyHoldingTrade("hold_cash", "CASH_PROXY", "candidate", 0.042, 0.65, 0.57, 0.05, 0.04, 0.03, -0.20, 0.96),
        ),
    ),
    NoisyPrincipalHoldingCase(
        key="family_office_tax_noise_value_signal",
        real_case="13F-style family office filing with tax-loss swaps mixed into value discipline",
        principal_profile="multi-generation value-disciplined family office",
        history=(
            NoisyHoldingHistoryMenu(
                "q1_discretionary",
                (
                    NoisyHoldingTrade("add_discount_industrial", "INDUSTRIAL_VALUE", "valuation_thesis", 0.102, 0.63, 0.88, 0.30, 0.34, 0.12, 0.02, 0.70, True),
                    NoisyHoldingTrade("buy_high_beta_growth", "GROWTH_BETA", "growth_thesis", 0.168, 0.46, 0.22, 0.84, 0.77, 0.30, 0.36, 0.57),
                    NoisyHoldingTrade("do_nothing_cash", "CASH_PROXY", "fund_flow", 0.041, 0.66, 0.58, 0.05, 0.04, 0.02, -0.20, 0.96),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q2_tax",
                (
                    NoisyHoldingTrade("tax_loss_swap", "LOSS_SWAP", "tax_loss", 0.060, 0.55, 0.48, 0.12, 0.20, 0.08, -0.08, 0.80, True),
                    NoisyHoldingTrade("add_healthcare_value", "HEALTH_VALUE", "valuation_thesis", 0.098, 0.70, 0.84, 0.34, 0.31, 0.13, 0.04, 0.72),
                    NoisyHoldingTrade("add_cloud_leader", "CLOUD_HIGH", "growth_thesis", 0.160, 0.55, 0.28, 0.88, 0.72, 0.29, 0.32, 0.60),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q3_discretionary",
                (
                    NoisyHoldingTrade("swap_to_cheaper_peer", "CHEAP_PEER", "valuation_thesis", 0.094, 0.62, 0.90, 0.24, 0.30, 0.10, -0.02, 0.69, True),
                    NoisyHoldingTrade("add_momentum_winner", "MOMENTUM_WIN", "growth_thesis", 0.150, 0.48, 0.26, 0.91, 0.70, 0.27, 0.34, 0.58),
                    NoisyHoldingTrade("raise_cash", "CASH_PROXY", "redemption", 0.040, 0.66, 0.60, 0.05, 0.04, 0.02, -0.18, 0.97),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q4_flow",
                (
                    NoisyHoldingTrade("meet_redemption", "CASH_PROXY", "redemption", 0.040, 0.66, 0.60, 0.05, 0.04, 0.02, -0.22, 0.97, True),
                    NoisyHoldingTrade("add_cheap_quality", "CHEAP_QUALITY", "valuation_thesis", 0.096, 0.73, 0.86, 0.32, 0.30, 0.12, 0.03, 0.73),
                    NoisyHoldingTrade("buy_max_return_saas", "SAAS_HIGH", "growth_thesis", 0.172, 0.54, 0.24, 0.89, 0.76, 0.30, 0.35, 0.59),
                ),
            ),
        ),
        target_trades=(
            NoisyHoldingTrade("add_cheap_quality", "CHEAP_QUALITY", "candidate", 0.096, 0.73, 0.86, 0.32, 0.30, 0.12, 0.03, 0.73),
            NoisyHoldingTrade("buy_max_return_saas", "SAAS_HIGH", "candidate", 0.172, 0.54, 0.24, 0.89, 0.76, 0.30, 0.35, 0.59),
            NoisyHoldingTrade("minimize_turnover_hold", "CURRENT_HOLD", "candidate", 0.060, 0.70, 0.58, 0.18, 0.18, 0.01, 0.00, 0.90),
            NoisyHoldingTrade("buy_safe_utility", "UTILITY_CORE", "candidate", 0.078, 0.88, 0.58, 0.30, 0.20, 0.10, 0.02, 0.77),
        ),
    ),
    NoisyPrincipalHoldingCase(
        key="activist_redemption_noise_concentration_signal",
        real_case="13F-style activist filing with client redemption rows hiding a campaign add",
        principal_profile="concentrated quality activist",
        history=(
            NoisyHoldingHistoryMenu(
                "q1_discretionary",
                (
                    NoisyHoldingTrade("add_board_campaign", "BOARD_CAMPAIGN", "engagement_add", 0.126, 0.82, 0.42, 0.66, 0.42, 0.18, 0.32, 0.50, True),
                    NoisyHoldingTrade("buy_high_return_smallcap", "SMALLCAP_OPTION", "growth_thesis", 0.180, 0.38, 0.36, 0.70, 0.88, 0.35, 0.20, 0.38),
                    NoisyHoldingTrade("diversify_index", "INDEX_PROXY", "index_rebalance", 0.072, 0.68, 0.58, 0.28, 0.18, 0.05, -0.22, 0.94),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q2_redemption",
                (
                    NoisyHoldingTrade("client_redemption_trim", "INDEX_PROXY", "redemption", 0.070, 0.68, 0.58, 0.28, 0.18, 0.05, -0.26, 0.95, True),
                    NoisyHoldingTrade("add_quality_target", "QUALITY_TARGET", "engagement_add", 0.118, 0.86, 0.48, 0.62, 0.38, 0.16, 0.30, 0.52),
                    NoisyHoldingTrade("buy_deep_value_spread", "CHEAP_SPREAD", "valuation_thesis", 0.108, 0.56, 0.88, 0.22, 0.41, 0.20, 0.06, 0.63),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q3_discretionary",
                (
                    NoisyHoldingTrade("add_follow_on_block", "FOLLOW_BLOCK", "engagement_add", 0.121, 0.84, 0.44, 0.64, 0.40, 0.17, 0.34, 0.49, True),
                    NoisyHoldingTrade("buy_fast_growth", "FAST_GROWTH", "growth_thesis", 0.162, 0.48, 0.24, 0.84, 0.76, 0.31, 0.24, 0.56),
                    NoisyHoldingTrade("reduce_to_cash", "CASH_PROXY", "fund_flow", 0.041, 0.66, 0.58, 0.05, 0.04, 0.02, -0.20, 0.96),
                ),
            ),
            NoisyHoldingHistoryMenu(
                "q4_index",
                (
                    NoisyHoldingTrade("risk_committee_index_trim", "INDEX_PROXY", "index_rebalance", 0.073, 0.68, 0.58, 0.30, 0.18, 0.04, -0.25, 0.94, True),
                    NoisyHoldingTrade("add_campaign_block", "CAMPAIGN_BLOCK", "engagement_add", 0.120, 0.85, 0.46, 0.65, 0.40, 0.17, 0.33, 0.50),
                    NoisyHoldingTrade("buy_value_peer", "VALUE_PEER", "valuation_thesis", 0.105, 0.58, 0.86, 0.27, 0.42, 0.20, 0.06, 0.64),
                ),
            ),
        ),
        target_trades=(
            NoisyHoldingTrade("add_campaign_block", "CAMPAIGN_BLOCK", "candidate", 0.120, 0.85, 0.46, 0.65, 0.40, 0.17, 0.33, 0.50),
            NoisyHoldingTrade("buy_max_return_option", "OPTIONALITY", "candidate", 0.184, 0.42, 0.22, 0.78, 0.90, 0.36, 0.22, 0.42),
            NoisyHoldingTrade("diversify_low_turnover", "INDEX_PROXY", "candidate", 0.073, 0.68, 0.58, 0.30, 0.18, 0.04, -0.25, 0.94),
            NoisyHoldingTrade("buy_value_peer", "VALUE_PEER", "candidate", 0.105, 0.58, 0.86, 0.27, 0.42, 0.20, 0.06, 0.64),
        ),
    ),
]


def trade_utility(
    trade: NoisyHoldingTrade,
    weights: dict[str, float],
) -> float:
    values = asdict(trade)
    return sum(weights[field] * float(values[field]) for field in FEATURE_FIELDS)


def infer_principal_style(
    case: NoisyPrincipalHoldingCase,
    *,
    include_mechanical: bool = False,
) -> str:
    best_style = next(iter(STYLE_WEIGHTS))
    best_score = (-1, -float("inf"))
    menus = _usable_menus(case, include_mechanical=include_mechanical)
    for style_id, weights in STYLE_WEIGHTS.items():
        valid = True
        margin = 0.0
        for menu in menus:
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


def principal_trade(case: NoisyPrincipalHoldingCase) -> tuple[str, str]:
    style_id = infer_principal_style(case)
    weights = STYLE_WEIGHTS[style_id]
    trade = max(case.target_trades, key=lambda candidate: trade_utility(candidate, weights))
    return style_id, trade.trade_id


def max_return_trade(case: NoisyPrincipalHoldingCase) -> str:
    return max(case.target_trades, key=lambda trade: trade.expected_return).trade_id


def low_turnover_trade(case: NoisyPrincipalHoldingCase) -> str:
    return min(case.target_trades, key=lambda trade: trade.turnover_cost).trade_id


def generic_style_trade(case: NoisyPrincipalHoldingCase) -> str:
    return max(
        case.target_trades,
        key=lambda candidate: trade_utility(candidate, GENERIC_STYLE_WEIGHTS),
    ).trade_id


def mechanical_flow_trade(case: NoisyPrincipalHoldingCase) -> tuple[str, str]:
    style_id = infer_principal_style(case, include_mechanical=True)
    weights = STYLE_WEIGHTS[style_id]
    trade = max(case.target_trades, key=lambda candidate: trade_utility(candidate, weights))
    return style_id, trade.trade_id


def run_noisy_principal_holding_prediction_game(
    agent: Agent,
    cases: list[NoisyPrincipalHoldingCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[NoisyPrincipalHoldingTrial] = []
    for case in cases:
        style_id, expected_trade = principal_trade(case)
        flow_blind_style, flow_trade = mechanical_flow_trade(case)
        weights = STYLE_WEIGHTS[style_id]
        target_by_id = {trade.trade_id: trade for trade in case.target_trades}
        principal_score = trade_utility(target_by_id[expected_trade], weights)
        response = agent.complete(NOISY_PRINCIPAL_HOLDING_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_TRADE", response)
        chosen = chosen if chosen in target_by_id else None
        chosen_score = trade_utility(target_by_id[chosen], weights) if chosen else None
        trials.append(
            NoisyPrincipalHoldingTrial(
                case=case,
                inferred_style=style_id,
                flow_blind_style=flow_blind_style,
                principal_trade=expected_trade,
                max_return_trade=max_return_trade(case),
                low_turnover_trade=low_turnover_trade(case),
                generic_style_trade=generic_style_trade(case),
                mechanical_flow_trade=flow_trade,
                chosen_trade=chosen,
                principal_score=principal_score,
                chosen_score=chosen_score,
                score_regret=principal_score - chosen_score if chosen_score is not None else None,
                raw_response=response,
            )
        )
    return summarize_noisy_principal_holding_trials(agent.name, trials)


def summarize_noisy_principal_holding_trials(
    agent_name: str,
    trials: list[NoisyPrincipalHoldingTrial],
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
    mechanical_missable = [
        trial for trial in trials if trial.mechanical_flow_trade != trial.principal_trade
    ]
    return {
        "task": "principal_holding_prediction_noisy",
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
        "mechanical_flow_miss_rate": (
            sum(trial.chosen_trade == trial.mechanical_flow_trade for trial in mechanical_missable)
            / len(mechanical_missable)
            if mechanical_missable
            else 0.0
        ),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _usable_menus(
    case: NoisyPrincipalHoldingCase,
    *,
    include_mechanical: bool,
) -> list[NoisyHoldingHistoryMenu]:
    menus: list[NoisyHoldingHistoryMenu] = []
    for menu in case.history:
        chosen = next(trade for trade in menu.trades if trade.chosen)
        if include_mechanical or chosen.event_type in DELIBERATE_EVENTS:
            menus.append(menu)
    return menus or list(case.history)


def _prompt(case: NoisyPrincipalHoldingCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"principal_profile={case.principal_profile}",
        "Historical 13F-style rows are noisy: some chosen rows are discretionary; others are mechanical fund-flow, redemption, index-rebalance, or tax-loss activity.",
        "The target is predict-the-principal: predict the next discretionary choice this principal would disclose, not market return and not a mechanical filing artifact.",
    ]
    for menu in case.history:
        for trade in menu.trades:
            lines.append(_trade_line("history_decision", menu.menu_id, trade))
    lines.append("Next-quarter candidate discretionary holding changes:")
    for trade in case.target_trades:
        lines.append(_trade_line("candidate_trade", "", trade))
    lines.append(
        "Infer the principal's style from discretionary evidence. "
        "Downweight rows whose event_type is fund_flow, redemption, index_rebalance, or tax_loss. "
        "Do not simply choose highest expected_return, lowest turnover_cost, "
        "generic balanced style, or the style implied by mechanical-flow rows."
    )
    return "\n".join(lines)


def _trade_line(prefix: str, menu_id: str, trade: NoisyHoldingTrade) -> str:
    menu_part = f"menu_id={menu_id} " if menu_id else ""
    return (
        f"{prefix}={trade.trade_id} "
        f"{menu_part}"
        f"issuer={trade.issuer} "
        f"event_type={trade.event_type} "
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


def _trial_json(trial: NoisyPrincipalHoldingTrial) -> dict:
    data = asdict(trial)
    data["case"] = {
        "key": trial.case.key,
        "real_case": trial.case.real_case,
        "principal_profile": trial.case.principal_profile,
    }
    return data
