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


PRINCIPAL_HOLDING_NOTES_SYSTEM = (
    "TASK: principal_holding_prediction_notes\n"
    "Predict the next discretionary holding change for the named principal from "
    "13F-style filing notes. Return one final line only: FINAL_TRADE: <trade_id>."
)


FILING_NOTES = {
    "add_quality_insurer": "manager_memo_named_balance_sheet_resilience_after_rate_shock",
    "buy_ai_beta": "sector_team_watchlist_with_high_beta_revenue_revision",
    "hold_short_bills": "temporary_cash_sleeve_awaiting_board_liquidity_vote",
    "redeem_to_cash": "cash_raised_after_external_benefit_payment_schedule_changed",
    "add_rail_compounder": "portfolio_manager_wrote_moat_and_pricing_power_note",
    "chase_cloud_breakout": "growth_team_flagged_breakout_but_risk_group_objected",
    "add_healthcare_quality": "manager_memo_named_recession_resilience_and_margin_stability",
    "buy_cyclical_rebound": "sector_rebound_note_after_inventory_correction",
    "raise_cash_only": "cash_bucket_lifted_for_external_liquidity_calendar",
    "match_index_weight": "benchmark_transition_memo_moved_weight_without_new_thesis",
    "add_quality_utility": "manager_note_prefers_regulated_cashflows_and_balance_sheet_quality",
    "buy_ai_momentum": "street_revision_note_with_high_multiple_momentum",
    "move_to_cash": "liquidity_sleeve_option_for_uncertain_client_cash_needs",
    "add_discount_bank": "valuation_team_note_on_discount_to_book_value",
    "add_platform_winner": "investment_committee_note_on_durable_platform_momentum",
    "buy_deep_value_bank": "valuation_screen_candidate_after_spread_widening",
    "trim_to_cash": "cash_placeholder_pending_capital_call_timing",
    "passive_index_topup": "benchmark_change_ticket_added_weight_without_manager_memo",
    "add_software_compounder": "manager_note_on_retention_and_expansion_momentum",
    "buy_energy_value": "valuation_screen_note_on_discounted_cashflow_gap",
    "add_semicap_leader": "manager_note_on_order_backlog_and_momentum_continuation",
    "rebalance_quality": "quality_watchlist_raised_after_credit_review",
    "buy_cheap_retail": "valuation_screen_after_multiple_compression",
    "harvest_loss_peer": "paired_year_end_swap_preserved_exposure_while_realizing_loss",
    "add_ai_platform": "manager_note_reaffirmed_platform_compounding_thesis",
    "buy_max_return_biotech": "optional_return_candidate_with_binary_trial_readout",
    "buy_deep_value_energy": "valuation_committee_note_on_underpriced_reserves",
    "hold_cash": "cash_bucket_candidate_pending_next_committee_window",
    "add_discount_industrial": "family_office_note_on_discounted_asset_base",
    "buy_high_beta_growth": "growth_watchlist_note_with_large_upside_but_volatility",
    "do_nothing_cash": "unallocated_cash_from_external_subscription_timing",
    "tax_loss_swap": "paired_sale_and_replacement_preserved_exposure_near_year_end",
    "add_healthcare_value": "family_office_note_on_cashflow_yield_and_margin_safety",
    "add_cloud_leader": "growth_team_note_on_high_revenue_multiple",
    "swap_to_cheaper_peer": "manager_note_on_cheaper_peer_with_same_exposure",
    "add_momentum_winner": "momentum_screen_after_revenue_revision",
    "raise_cash": "client_distribution_calendar_required_cash_lift",
    "meet_redemption": "outside_withdrawal_ticket_required_liquid_sleeve",
    "add_cheap_quality": "family_office_note_on_quality_at_discount",
    "buy_max_return_saas": "highest_upside_watchlist_name_with_high_multiple",
    "minimize_turnover_hold": "do_little_candidate_reduces_trading_friction",
    "buy_safe_utility": "safe_income_candidate_after_rate_review",
    "add_board_campaign": "campaign_team_note_on_board_seat_and_quality_asset",
    "buy_high_return_smallcap": "optionality_watchlist_with_small_float",
    "diversify_index": "risk_committee_ticket_reduced_active_weight",
    "client_redemption_trim": "external_withdrawal_notice_forced_liquidity_sale",
    "add_quality_target": "engagement_note_on_quality_target_and_operational_plan",
    "buy_deep_value_spread": "valuation_screen_note_on_sum_of_parts_discount",
    "add_follow_on_block": "campaign_team_note_on_follow_on_block_after_engagement",
    "buy_fast_growth": "growth_watchlist_after_accelerating_bookings",
    "reduce_to_cash": "temporary_cash_bucket_for_external_transfer",
    "risk_committee_index_trim": "risk_committee_ticket_moved_toward_benchmark_weight",
    "add_campaign_block": "campaign_team_note_on_concentrated_block_and_board_plan",
    "buy_max_return_option": "highest_upside_optionality_name_with_volatile_float",
    "buy_value_peer": "valuation_screen_peer_with_discounted_assets",
}


def run_principal_holding_prediction_notes_game(
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
        response = agent.complete(PRINCIPAL_HOLDING_NOTES_SYSTEM, _prompt(case))
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
    result["task"] = "principal_holding_prediction_notes"
    return result


def _prompt(case: NoisyPrincipalHoldingCase) -> str:
    lines = [
        "case=principal_holding_notes_case",
        "real_case=13F-style filing with noisy non-manager rows mixed into the trade pattern",
        f"principal_profile={case.principal_profile}",
        "Historical 13F-style rows include the disclosed choice plus filing notes from memos, tickets, and committee logs.",
        "The target is predict-the-principal: infer the next discretionary choice this principal would disclose, not the best market-return candidate or a filing artifact.",
    ]
    for menu_index, menu in enumerate(case.history, start=1):
        for trade_index, trade in enumerate(menu.trades, start=1):
            visible_trade_id = f"h{menu_index}_{trade_index}"
            lines.append(
                _trade_line(
                    "history_decision",
                    visible_trade_id,
                    _visible_menu_id(menu.menu_id),
                    trade,
                )
            )
    lines.append("Next-quarter candidate discretionary holding changes:")
    for trade_index, trade in enumerate(case.target_trades, start=1):
        visible_trade_id = f"t{trade_index}"
        lines.append(_trade_line("candidate_trade", visible_trade_id, "", trade))
    lines.append(
        "Use the history notes to separate manager-initiated thesis choices "
        "from outside cash, benchmark, risk-ticket, or year-end bookkeeping artifacts. "
        "Do not simply choose highest expected_return, lowest turnover_cost, "
        "or a generic balanced style."
    )
    return "\n".join(lines)


def _trade_line(prefix: str, visible_trade_id: str, menu_id: str, trade: NoisyHoldingTrade) -> str:
    menu_part = f"menu_id={menu_id} " if menu_id else ""
    note = FILING_NOTES.get(trade.trade_id, "candidate_under_review")
    return (
        f"{prefix}={visible_trade_id} "
        f"{menu_part}"
        f"issuer={trade.issuer} "
        f"filing_note={note} "
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


def _visible_menu_id(menu_id: str) -> str:
    return (
        menu_id.replace("redemption", "liquidity")
        .replace("index", "policy")
        .replace("tax", "yearend")
        .replace("flow", "cash")
    )
