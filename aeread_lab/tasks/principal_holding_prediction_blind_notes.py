from __future__ import annotations

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.tasks.principal_holding_prediction_noisy import (
    DEFAULT_CASES,
    NoisyHoldingTrade,
    NoisyPrincipalHoldingCase,
    NoisyPrincipalHoldingTrial,
    generic_style_trade,
    low_turnover_trade,
    max_return_trade,
    mechanical_flow_trade,
    principal_trade,
    summarize_noisy_principal_holding_trials,
    target_margin,
    trade_utility,
)
from aeread_lab.tasks.principal_holding_prediction_noisy import STYLE_WEIGHTS


PRINCIPAL_HOLDING_BLIND_NOTES_SYSTEM = (
    "TASK: principal_holding_prediction_blind_notes\n"
    "Predict the next discretionary holding change for a neutralized principal "
    "from 13F-style raw notes. Return one final line only: FINAL_TRADE: <trade_id>."
)


RAW_NOTE_BY_EVENT = {
    "manager_thesis": "pm_packet_followup_from_research_meeting",
    "quality_rotation": "pm_packet_followup_from_research_meeting",
    "growth_thesis": "pm_packet_followup_from_research_meeting",
    "valuation_thesis": "pm_packet_followup_from_research_meeting",
    "engagement_add": "pm_packet_followup_from_research_meeting",
    "fund_flow": "cash_operations_entry_from_external_schedule",
    "redemption": "client_wire_liquidity_entry_from_operations",
    "index_rebalance": "benchmark_model_update_from_policy_desk",
    "tax_loss": "tax_lot_operations_entry_near_year_end",
    "candidate": "candidate_packet_under_review",
}


def run_principal_holding_prediction_blind_notes_game(
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
        visible_targets = {
            f"t{i}": trade.trade_id for i, trade in enumerate(case.target_trades, start=1)
        }
        principal_score = trade_utility(target_by_id[expected_trade], weights)
        second_trade, second_score, oracle_margin = target_margin(
            case.target_trades,
            weights,
            expected_trade,
        )
        response = agent.complete(PRINCIPAL_HOLDING_BLIND_NOTES_SYSTEM, _prompt(case))
        chosen_visible = parse_token("FINAL_TRADE", response)
        chosen = visible_targets.get(chosen_visible, chosen_visible)
        chosen = chosen if chosen in target_by_id else None
        chosen_score = trade_utility(target_by_id[chosen], weights) if chosen else None
        trials.append(
            NoisyPrincipalHoldingTrial(
                case=case,
                inferred_style=style_id,
                flow_blind_style=flow_blind_style,
                principal_trade=expected_trade,
                second_best_trade=second_trade,
                max_return_trade=max_return_trade(case),
                low_turnover_trade=low_turnover_trade(case),
                generic_style_trade=generic_style_trade(case),
                mechanical_flow_trade=flow_trade,
                chosen_trade=chosen,
                principal_score=principal_score,
                second_best_score=second_score,
                oracle_margin=oracle_margin,
                chosen_score=chosen_score,
                score_regret=principal_score - chosen_score if chosen_score is not None else None,
                raw_response=response,
            )
        )
    result = summarize_noisy_principal_holding_trials(agent.name, trials)
    result["task"] = "principal_holding_prediction_blind_notes"
    return result


def _prompt(case: NoisyPrincipalHoldingCase) -> str:
    issuer_map = _issuer_map(case)
    lines = [
        "case=principal_holding_blind_notes_case",
        "real_case=13F-style ledger with neutralized account and security labels",
        "account_id=acct_hidden",
        "Historical rows use neutral security IDs and raw filing notes. Some chosen rows reflect manager discretion; other chosen rows reflect filing artifacts.",
        "Infer the principal's discretionary pattern from the manager-initiated rows, then choose the next candidate disclosed change.",
    ]
    for menu_index, menu in enumerate(case.history, start=1):
        for trade_index, trade in enumerate(menu.trades, start=1):
            visible_trade_id = f"h{menu_index}_{trade_index}"
            lines.append(
                _trade_line(
                    "history_decision",
                    visible_trade_id,
                    f"m{menu_index}",
                    trade,
                    issuer_map,
                )
            )
    lines.append("Next-quarter candidate disclosed changes:")
    for trade_index, trade in enumerate(case.target_trades, start=1):
        visible_trade_id = f"t{trade_index}"
        lines.append(_trade_line("candidate_trade", visible_trade_id, "", trade, issuer_map))
    lines.append(
        "Use only the neutralized ledger pattern. Do not choose only by highest expected_return, "
        "lowest turnover_cost, or a generic balanced style."
    )
    return "\n".join(lines)


def _trade_line(
    prefix: str,
    visible_trade_id: str,
    menu_id: str,
    trade: NoisyHoldingTrade,
    issuer_map: dict[str, str],
) -> str:
    menu_part = f"menu_id={menu_id} " if menu_id else ""
    return (
        f"{prefix}={visible_trade_id} "
        f"{menu_part}"
        f"issuer={issuer_map[trade.issuer]} "
        f"filing_note={RAW_NOTE_BY_EVENT.get(trade.event_type, 'candidate_packet_under_review')} "
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


def _issuer_map(case: NoisyPrincipalHoldingCase) -> dict[str, str]:
    issuers = []
    for menu in case.history:
        issuers.extend(trade.issuer for trade in menu.trades)
    issuers.extend(trade.issuer for trade in case.target_trades)
    return {issuer: f"sec{i:02d}" for i, issuer in enumerate(dict.fromkeys(issuers), start=1)}
