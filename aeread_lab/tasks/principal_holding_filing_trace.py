from __future__ import annotations

from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


PRINCIPAL_HOLDING_FILING_TRACE_SYSTEM = (
    "TASK: principal_holding_filing_trace\n"
    "Infer the material next holding action from real-derived 13F filing rows. "
    "Return one final line only: FINAL_TRADE: <trade_id>."
)

PRINCIPAL_HOLDING_FILING_TRACE_RAW_SYSTEM = (
    "TASK: principal_holding_filing_trace_raw\n"
    "Infer the material next holding action from raw real-derived 13F filing rows. "
    "Return one final line only: FINAL_ISSUER: <issuer_id>."
)


@dataclass(frozen=True)
class FilingTraceRow:
    period: str
    accession: str
    issuer: str
    value: float
    shares: float


@dataclass(frozen=True)
class FilingTraceTrade:
    trade_id: str
    issuer: str
    prior_period: str
    next_period: str
    prior_value: float
    next_value: float
    prior_shares: float
    next_shares: float
    previous_share_delta: float


@dataclass(frozen=True)
class FilingTraceCase:
    key: str
    real_case: str
    manager_cik: str
    manager_name: str
    source_url: str
    target_accession: str
    history: tuple[FilingTraceRow, ...]
    target_trades: tuple[FilingTraceTrade, ...]


@dataclass
class FilingTraceTrial:
    case: FilingTraceCase
    principal_trade: str
    market_value_trade: str
    low_turnover_trade: str
    max_position_trade: str
    trend_trade: str
    chosen_trade: str | None
    principal_score: float
    chosen_score: float | None
    score_regret: float | None
    oracle_margin: float
    raw_response: str


# Real-derived public SEC 13F-HR rows for Berkshire Hathaway Inc. The rows were
# inspected from SEC EDGAR information tables for accessions:
# 2025Q3 0001193125-25-282901, 2025Q4 0001193125-26-054580,
# 2026Q1 0001193125-26-226661.
DEFAULT_CASES = [
    FilingTraceCase(
        key="brk_2026q1_energy_rebalance",
        real_case=(
            "Berkshire Hathaway 13F-HR trace where a share-driven energy "
            "rebalance must be separated from market-value drift"
        ),
        manager_cik="0001067983",
        manager_name="BERKSHIRE HATHAWAY INC",
        source_url="https://www.sec.gov/Archives/edgar/data/1067983/",
        target_accession="0001193125-26-226661",
        history=(
            FilingTraceRow("2025q3", "0001193125-25-282901", "sec_apple", 60656116097, 238212764),
            FilingTraceRow("2025q4", "0001193125-26-054580", "sec_apple", 61961735283, 227917808),
            FilingTraceRow("2025q3", "0001193125-25-282901", "sec_amex", 50359010112, 151610700),
            FilingTraceRow("2025q4", "0001193125-26-054580", "sec_amex", 56088378465, 151610700),
            FilingTraceRow("2025q3", "0001193125-25-282901", "sec_coke", 26528000000, 400000000),
            FilingTraceRow("2025q4", "0001193125-26-054580", "sec_coke", 27964000000, 400000000),
            FilingTraceRow("2025q3", "0001193125-25-282901", "sec_oxy", 12518482615, 264941431),
            FilingTraceRow("2025q4", "0001193125-26-054580", "sec_oxy", 10894391643, 264941431),
            FilingTraceRow("2025q3", "0001193125-25-282901", "sec_chevron", 18955441549, 122064792),
            FilingTraceRow("2025q4", "0001193125-26-054580", "sec_chevron", 19837131131, 130156362),
            FilingTraceRow(
                "2025q3",
                "0001193125-25-282901",
                "sec_constellation",
                1804578000,
                13400000,
            ),
            FilingTraceRow(
                "2025q4",
                "0001193125-26-054580",
                "sec_constellation",
                1793480000,
                13000000,
            ),
        ),
        target_trades=(
            FilingTraceTrade(
                "price_drift_apple",
                "sec_apple",
                "2025q4",
                "2026q1",
                61961735283,
                57843260493,
                227917808,
                227917808,
                -10294956,
            ),
            FilingTraceTrade(
                "price_drift_amex",
                "sec_amex",
                "2025q4",
                "2026q1",
                56088378465,
                45859204536,
                151610700,
                151610700,
                0,
            ),
            FilingTraceTrade(
                "price_drift_coke",
                "sec_coke",
                "2025q4",
                "2026q1",
                27964000000,
                30420000000,
                400000000,
                400000000,
                0,
            ),
            FilingTraceTrade(
                "price_drift_oxy",
                "sec_oxy",
                "2025q4",
                "2026q1",
                10894391643,
                17221193015,
                264941431,
                264941431,
                0,
            ),
            FilingTraceTrade(
                "reduce_chevron",
                "sec_chevron",
                "2025q4",
                "2026q1",
                19837131131,
                17457364606,
                130156362,
                84375856,
                8091570,
            ),
            FilingTraceTrade(
                "reduce_constellation",
                "sec_constellation",
                "2025q4",
                "2026q1",
                1793480000,
                94933500,
                13000000,
                632890,
                -400000,
            ),
        ),
    ),
]


def run_principal_holding_filing_trace_game(
    agent: Agent,
    cases: list[FilingTraceCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[FilingTraceTrial] = []
    for case in cases:
        principal = material_action_trade(case)
        market_value = market_value_trade(case)
        low_turnover = low_turnover_trade(case)
        max_position = max_position_trade(case)
        trend = trend_trade(case)
        score_by_id = _normalized_action_scores(case)
        oracle_margin = _oracle_margin(score_by_id, principal)
        response = agent.complete(PRINCIPAL_HOLDING_FILING_TRACE_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_TRADE", response)
        chosen = chosen if chosen in score_by_id else None
        chosen_score = score_by_id[chosen] if chosen else None
        trials.append(
            FilingTraceTrial(
                case=case,
                principal_trade=principal,
                market_value_trade=market_value,
                low_turnover_trade=low_turnover,
                max_position_trade=max_position,
                trend_trade=trend,
                chosen_trade=chosen,
                principal_score=score_by_id[principal],
                chosen_score=chosen_score,
                score_regret=score_by_id[principal] - chosen_score
                if chosen_score is not None
                else None,
                oracle_margin=oracle_margin,
                raw_response=response,
            )
        )
    return summarize_filing_trace_trials(agent.name, trials)


def run_principal_holding_filing_trace_raw_game(
    agent: Agent,
    cases: list[FilingTraceCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[FilingTraceTrial] = []
    for case in cases:
        principal = _issuer_for_trade(case, material_action_trade(case))
        market_value = _issuer_for_trade(case, market_value_trade(case))
        low_turnover = _issuer_for_trade(case, low_turnover_trade(case))
        max_position = _issuer_for_trade(case, max_position_trade(case))
        trend = _issuer_for_trade(case, trend_trade(case))
        score_by_id = _normalized_issuer_action_scores(case)
        oracle_margin = _oracle_margin(score_by_id, principal)
        response = agent.complete(
            PRINCIPAL_HOLDING_FILING_TRACE_RAW_SYSTEM,
            _raw_prompt(case),
        )
        chosen = parse_token("FINAL_ISSUER", response)
        chosen = chosen if chosen in score_by_id else None
        chosen_score = score_by_id[chosen] if chosen else None
        trials.append(
            FilingTraceTrial(
                case=case,
                principal_trade=principal,
                market_value_trade=market_value,
                low_turnover_trade=low_turnover,
                max_position_trade=max_position,
                trend_trade=trend,
                chosen_trade=chosen,
                principal_score=score_by_id[principal],
                chosen_score=chosen_score,
                score_regret=score_by_id[principal] - chosen_score
                if chosen_score is not None
                else None,
                oracle_margin=oracle_margin,
                raw_response=response,
            )
        )
    return summarize_filing_trace_trials(
        agent.name,
        trials,
        task="principal_holding_filing_trace_raw",
    )


def material_action_trade(case: FilingTraceCase) -> str:
    return max(case.target_trades, key=_action_value).trade_id


def market_value_trade(case: FilingTraceCase) -> str:
    return max(case.target_trades, key=lambda trade: trade.next_value - trade.prior_value).trade_id


def low_turnover_trade(case: FilingTraceCase) -> str:
    return min(case.target_trades, key=lambda trade: abs(trade.next_shares - trade.prior_shares)).trade_id


def max_position_trade(case: FilingTraceCase) -> str:
    return max(case.target_trades, key=lambda trade: trade.prior_value).trade_id


def trend_trade(case: FilingTraceCase) -> str:
    return max(case.target_trades, key=lambda trade: abs(trade.previous_share_delta)).trade_id


def summarize_filing_trace_trials(
    agent_name: str,
    trials: list[FilingTraceTrial],
    *,
    task: str = "principal_holding_filing_trace",
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    parsed = [trial for trial in trials if trial.chosen_trade is not None]
    margins = [trial.oracle_margin for trial in trials]
    market_missable = [
        trial for trial in trials if trial.market_value_trade != trial.principal_trade
    ]
    low_turnover_missable = [
        trial for trial in trials if trial.low_turnover_trade != trial.principal_trade
    ]
    max_position_missable = [
        trial for trial in trials if trial.max_position_trade != trial.principal_trade
    ]
    trend_missable = [trial for trial in trials if trial.trend_trade != trial.principal_trade]
    return {
        "task": task,
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
        "mean_oracle_margin": mean(margins),
        "min_oracle_margin": min(margins) if margins else None,
        "market_value_miss_rate": _reference_miss_rate(market_missable, "market_value_trade"),
        "low_turnover_miss_rate": _reference_miss_rate(low_turnover_missable, "low_turnover_trade"),
        "max_position_miss_rate": _reference_miss_rate(max_position_missable, "max_position_trade"),
        "trend_miss_rate": _reference_miss_rate(trend_missable, "trend_trade"),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _reference_miss_rate(trials: list[FilingTraceTrial], attr: str) -> float:
    if not trials:
        return 0.0
    return sum(trial.chosen_trade == getattr(trial, attr) for trial in trials) / len(trials)


def _prompt(case: FilingTraceCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Rows are neutralized but derived from public SEC 13F-HR information tables.",
        "The task is to identify the material share-driven holding action, not the largest market-value drift and not the lowest-turnover hold.",
        "Historical filing rows:",
    ]
    for row in case.history:
        lines.append(
            f"history_filing period={row.period} accession={row.accession} "
            f"issuer={row.issuer} reported_value={row.value:.0f} shares={row.shares:.0f}"
        )
    lines.append("Candidate next-quarter filing changes:")
    for trade in case.target_trades:
        lines.append(
            f"candidate_trade={trade.trade_id} issuer={trade.issuer} "
            f"prior_period={trade.prior_period} next_period={trade.next_period} "
            f"prior_value={trade.prior_value:.0f} next_value={trade.next_value:.0f} "
            f"prior_shares={trade.prior_shares:.0f} next_shares={trade.next_shares:.0f} "
            f"previous_share_delta={trade.previous_share_delta:.0f}"
        )
    lines.append(
        "Choose the candidate with the strongest share-driven action implied by the filings. "
        "Do not choose only by value increase, prior position size, previous-quarter trend, or no-change turnover."
    )
    return "\n".join(lines)


def _raw_prompt(case: FilingTraceCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Rows are neutralized but derived from public SEC 13F-HR information tables.",
        "The final period is the next disclosed filing; infer the issuer with the material share-driven action from the raw rows.",
        "Do not choose only by reported value movement, prior position size, previous-period trend, or no-change turnover.",
        "Raw filing rows:",
    ]
    for row in _raw_filing_rows(case):
        lines.append(
            f"filing_row period={row.period} accession={row.accession} "
            f"issuer={row.issuer} reported_value={row.value:.0f} shares={row.shares:.0f}"
        )
    issuers = ", ".join(sorted({trade.issuer for trade in case.target_trades}))
    lines.append(f"issuer_choices={issuers}")
    lines.append("Return the issuer id with the strongest material share-driven action.")
    return "\n".join(lines)


def _action_value(trade: FilingTraceTrade) -> float:
    prior_price = trade.prior_value / trade.prior_shares if trade.prior_shares else 0.0
    return abs(trade.next_shares - trade.prior_shares) * prior_price


def _normalized_action_scores(case: FilingTraceCase) -> dict[str, float]:
    values = {trade.trade_id: _action_value(trade) for trade in case.target_trades}
    max_value = max(values.values()) if values else 0.0
    if max_value <= 0:
        return {trade_id: 0.0 for trade_id in values}
    return {trade_id: value / max_value for trade_id, value in values.items()}


def _normalized_issuer_action_scores(case: FilingTraceCase) -> dict[str, float]:
    values = {trade.issuer: _action_value(trade) for trade in case.target_trades}
    max_value = max(values.values()) if values else 0.0
    if max_value <= 0:
        return {issuer: 0.0 for issuer in values}
    return {issuer: value / max_value for issuer, value in values.items()}


def _oracle_margin(score_by_id: dict[str, float], oracle: str) -> float:
    oracle_score = score_by_id[oracle]
    alternatives = [score for trade_id, score in score_by_id.items() if trade_id != oracle]
    return oracle_score - max(alternatives) if alternatives else oracle_score


def _issuer_for_trade(case: FilingTraceCase, trade_id: str) -> str:
    for trade in case.target_trades:
        if trade.trade_id == trade_id:
            return trade.issuer
    raise ValueError(f"unknown trade id: {trade_id}")


def _raw_filing_rows(case: FilingTraceCase) -> tuple[FilingTraceRow, ...]:
    rows: dict[tuple[str, str], FilingTraceRow] = {}
    for row in case.history:
        rows[(row.period, row.issuer)] = row
    for trade in case.target_trades:
        rows[(trade.next_period, trade.issuer)] = FilingTraceRow(
            period=trade.next_period,
            accession=case.target_accession,
            issuer=trade.issuer,
            value=trade.next_value,
            shares=trade.next_shares,
        )
    return tuple(sorted(rows.values(), key=lambda row: (row.issuer, row.period)))


def _trial_json(trial: FilingTraceTrial) -> dict:
    data = asdict(trial)
    data["case"] = {
        "key": trial.case.key,
        "real_case": trial.case.real_case,
        "manager_cik": trial.case.manager_cik,
        "source_url": trial.case.source_url,
        "target_accession": trial.case.target_accession,
    }
    return data
