from __future__ import annotations

from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


PRINCIPAL_HOLDING_FILING_TRACE_SYSTEM = (
    "TASK: principal_holding_filing_trace\n"
    "Infer the dollar-material next holding action from real-derived 13F filing rows. "
    "Return one final line only: FINAL_TRADE: <trade_id>."
)

PRINCIPAL_HOLDING_FILING_TRACE_RAW_SYSTEM = (
    "TASK: principal_holding_filing_trace_raw\n"
    "Infer the dollar-material next holding action from raw real-derived 13F filing rows. "
    "Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_SYSTEM = (
    "TASK: principal_holding_filing_artifact\n"
    "Infer the dollar-material discretionary holding action after adjusting public-filing "
    "rows for mechanical corporate-action artifacts. Return one final line only: "
    "FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_NATURAL_SYSTEM = (
    "TASK: principal_holding_filing_artifact_natural\n"
    "Infer the dollar-material discretionary holding action from public-filing rows and "
    "natural corporate-action notes. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_STRESS_SYSTEM = (
    "TASK: principal_holding_filing_artifact_stress\n"
    "Infer the dollar-material discretionary holding action from public-filing rows with "
    "multiple corporate-action artifacts and close runner-up actions. Return one final "
    "line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_IMPLICIT_SYSTEM = (
    "TASK: principal_holding_filing_artifact_implicit\n"
    "Infer the dollar-material discretionary holding action from public-filing rows where "
    "corporate-action artifacts must be inferred from row patterns rather than explicit "
    "artifact notes. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_IMPLICIT_STABLE_SYSTEM = (
    "TASK: principal_holding_filing_artifact_implicit_stable\n"
    "Infer the dollar-material discretionary holding action from public-filing rows where "
    "split-like corporate-action artifacts must be inferred from internally consistent "
    "row-ratio and value-stability evidence. Return one final line only: "
    "FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata\n"
    "Infer the dollar-material discretionary holding action from public-filing rows by "
    "joining raw filing rows to a separate corporate-action registry. Return one final "
    "line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_NOISY_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_noisy\n"
    "Infer the dollar-material discretionary holding action from public-filing rows by "
    "joining raw filing rows to a separate corporate-action registry that may contain "
    "stale, unmatched, or unconfirmed records. Return one final line only: "
    "FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_PARTIAL_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_partial\n"
    "Infer the dollar-material discretionary holding action from public-filing rows by "
    "combining a partial corporate-action registry with row-pattern evidence for "
    "missing split records. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_CONFLICT_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_conflict\n"
    "Infer the dollar-material discretionary holding action from public-filing rows by "
    "validating confirmed corporate-action registry records against filing-row evidence "
    "before applying them. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_UNMARKED_CONFLICT_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_unmarked_conflict\n"
    "Infer the dollar-material discretionary holding action from public-filing rows by "
    "joining raw filing rows to a separate corporate-action registry. Return one final "
    "line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_HISTORY_CONFLICT_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_history_conflict\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows and a separate corporate-action registry. Return one final line only: "
    "FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_VALIDATION_PROCESS_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_validation_process\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows and a separate corporate-action registry after checking registry ratios "
    "against filing rows. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_PROVENANCE_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_source_provenance\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows and a provenance-labeled corporate-action registry. Return one final line only: "
    "FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_CONTEXT_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_source_context\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows, corporate-action source packets, and a separate registry. Return one final "
    "line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_source_status_ablation\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows, corporate-action source packets, and a registry where some rows are not "
    "issuer-confirmed. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_source_status_neutral\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows, corporate-action source packets, and a registry whose split rows do not "
    "carry status labels. Return one final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_source_status_neutral_intro\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows, corporate-action source packets, and a status-neutral registry. Return one "
    "final line only: FINAL_ISSUER: <issuer_id>."
)

PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_SYSTEM = (
    "TASK: principal_holding_filing_artifact_metadata_source_audit\n"
    "Infer the dollar-material discretionary holding action from repeated public-filing "
    "rows, corporate-action source packets, and a status-neutral registry using a "
    "corporate-action source audit. Return one final line only: FINAL_ISSUER: <issuer_id>."
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
    percent_change_trade: str
    second_best_trade: str
    chosen_trade: str | None
    principal_score: float
    chosen_score: float | None
    score_regret: float | None
    oracle_margin: float
    raw_response: str


@dataclass(frozen=True)
class CorporateActionRegistryEntry:
    issuer: str
    action: str
    ratio: float
    effective_period: str
    source: str
    status: str = "confirmed"


@dataclass(frozen=True)
class FilingArtifactCase:
    key: str
    real_case: str
    manager_cik: str
    manager_name: str
    source_url: str
    target_accession: str
    rows: tuple[FilingTraceRow, ...]
    adjustment_factors: dict[str, float]
    artifact_notes: dict[str, str]
    corporate_actions: tuple[CorporateActionRegistryEntry, ...] = ()


@dataclass
class FilingArtifactTrial:
    case: FilingArtifactCase
    principal_trade: str
    artifact_blind_trade: str
    market_value_trade: str
    percent_change_trade: str
    second_best_trade: str
    metadata_trusting_trade: str | None
    metadata_status_blind_trade: str | None
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
    FilingTraceCase(
        key="tiger_2026q1_megacap_rotation",
        real_case=(
            "Tiger Global 13F-HR trace where the dollar-material reduction "
            "must be separated from a runner-up reduction and value drift"
        ),
        manager_cik="0001167483",
        manager_name="TIGER GLOBAL MANAGEMENT LLC",
        source_url="https://www.sec.gov/Archives/edgar/data/1167483/",
        target_accession="0000919574-26-003362",
        history=(
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_a", 2584493826000, 10631402),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_a", 3327628826000, 10631402),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_b", 827539532000, 6209496),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_b", 898886641000, 6209496),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_c", 183283248000, 895200),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_c", 230057448000, 895200),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_d", 509970044000, 15837579),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_d", 619644640000, 26267259),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_e", 3393281056000, 6551368),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_e", 2649148004000, 5477747),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_f", 1074631725000, 4672515),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_f", 883600741000, 3843915),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_g", 1278694074000, 4578374),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_g", 1132134294000, 3725474),
            FilingTraceRow("2025q3", "0000919574-25-006931", "sec_tiger_h", 1508630180000, 5839256),
            FilingTraceRow("2025q4", "0000919574-26-001143", "sec_tiger_h", 1495024714000, 5839256),
        ),
        target_trades=(
            FilingTraceTrade(
                "hold_tiger_a",
                "sec_tiger_a",
                "2025q4",
                "2026q1",
                3327628826000,
                3057165959000,
                10631402,
                10631402,
                0,
            ),
            FilingTraceTrade(
                "reduce_tiger_b",
                "sec_tiger_b",
                "2025q4",
                "2026q1",
                898886641000,
                366943274000,
                6209496,
                3293334,
                0,
            ),
            FilingTraceTrade(
                "add_tiger_c",
                "sec_tiger_c",
                "2025q4",
                "2026q1",
                230057448000,
                566311851000,
                895200,
                1656900,
                0,
            ),
            FilingTraceTrade(
                "add_tiger_d",
                "sec_tiger_d",
                "2025q4",
                "2026q1",
                619644640000,
                653161284000,
                26267259,
                34595407,
                10429680,
            ),
            FilingTraceTrade(
                "reduce_tiger_e",
                "sec_tiger_e",
                "2025q4",
                "2026q1",
                2649148004000,
                925425000000,
                5477747,
                2500000,
                -1073621,
            ),
            FilingTraceTrade(
                "reduce_tiger_f",
                "sec_tiger_f",
                "2025q4",
                "2026q1",
                883600741000,
                336625000000,
                3843915,
                2500000,
                -828600,
            ),
            FilingTraceTrade(
                "add_tiger_g",
                "sec_tiger_g",
                "2025q4",
                "2026q1",
                1132134294000,
                1880716758000,
                3725474,
                5565074,
                -852900,
            ),
            FilingTraceTrade(
                "reduce_tiger_h",
                "sec_tiger_h",
                "2025q4",
                "2026q1",
                1495024714000,
                395000000000,
                5839256,
                2000000,
                0,
            ),
        ),
    ),
]


ARTIFACT_CASES = [
    FilingArtifactCase(
        key="split_adjustment_vs_discretionary_reduction",
        real_case=(
            "13F-style filing trace where an apparent large share-count change is "
            "a corporate-action split artifact, not the principal's discretionary action"
        ),
        manager_cik="0000000000",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT TRACE",
        source_url="public SEC-style 13F information table rows plus neutralized corporate-action note",
        target_accession="neutralized-2026q1-artifact",
        rows=(
            FilingTraceRow("2025q4", "artifact-2025q4", "sec_artifact_a", 480000000, 1000000),
            FilingTraceRow("2026q1", "artifact-2026q1", "sec_artifact_a", 505000000, 4000000),
            FilingTraceRow("2025q4", "artifact-2025q4", "sec_artifact_b", 620000000, 2000000),
            FilingTraceRow("2026q1", "artifact-2026q1", "sec_artifact_b", 270000000, 850000),
            FilingTraceRow("2025q4", "artifact-2025q4", "sec_artifact_c", 590000000, 5000000),
            FilingTraceRow("2026q1", "artifact-2026q1", "sec_artifact_c", 310000000, 2600000),
            FilingTraceRow("2025q4", "artifact-2025q4", "sec_artifact_d", 900000000, 3000000),
            FilingTraceRow("2026q1", "artifact-2026q1", "sec_artifact_d", 1400000000, 3000000),
            FilingTraceRow("2025q4", "artifact-2025q4", "sec_artifact_e", 10000000, 100000),
            FilingTraceRow("2026q1", "artifact-2026q1", "sec_artifact_e", 125000000, 1200000),
        ),
        adjustment_factors={
            "sec_artifact_a": 4.0,
            "sec_artifact_b": 1.0,
            "sec_artifact_c": 1.0,
            "sec_artifact_d": 1.0,
            "sec_artifact_e": 1.0,
        },
        artifact_notes={
            "sec_artifact_a": (
                "quarter included a 4-for-1 share split; compare prior shares after "
                "multiplying by 4 before treating share-count movement as discretionary"
            ),
            "sec_artifact_b": "no corporate-action adjustment noted",
            "sec_artifact_c": "no corporate-action adjustment noted",
            "sec_artifact_d": "reported value drifted with no share-count change",
            "sec_artifact_e": "small position with large relative reduction",
        },
    ),
]


ARTIFACT_STRESS_CASES = [
    FilingArtifactCase(
        key="multi_artifact_close_runner_up",
        real_case=(
            "13F-style filing trace where multiple split artifacts and a close "
            "runner-up discretionary action compete with the adjusted oracle"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT STRESS TRACE",
        source_url="public SEC-style 13F information table rows plus neutralized natural corporate-action notes",
        target_accession="neutralized-2026q1-artifact-stress",
        rows=(
            FilingTraceRow("2025q4", "artifact-stress-2025q4", "sec_stress_a", 750000000, 1500000),
            FilingTraceRow("2026q1", "artifact-stress-2026q1", "sec_stress_a", 780000000, 7500000),
            FilingTraceRow("2025q4", "artifact-stress-2025q4", "sec_stress_b", 1200000000, 3000000),
            FilingTraceRow("2026q1", "artifact-stress-2026q1", "sec_stress_b", 620000000, 1450000),
            FilingTraceRow("2025q4", "artifact-stress-2025q4", "sec_stress_c", 840000000, 2100000),
            FilingTraceRow("2026q1", "artifact-stress-2026q1", "sec_stress_c", 280000000, 650000),
            FilingTraceRow("2025q4", "artifact-stress-2025q4", "sec_stress_d", 900000000, 1800000),
            FilingTraceRow("2026q1", "artifact-stress-2026q1", "sec_stress_d", 1500000000, 1800000),
            FilingTraceRow("2025q4", "artifact-stress-2025q4", "sec_stress_e", 20000000, 100000),
            FilingTraceRow("2026q1", "artifact-stress-2026q1", "sec_stress_e", 120000000, 800000),
            FilingTraceRow("2025q4", "artifact-stress-2025q4", "sec_stress_f", 300000000, 1000000),
            FilingTraceRow("2026q1", "artifact-stress-2026q1", "sec_stress_f", 930000000, 3000000),
        ),
        adjustment_factors={
            "sec_stress_a": 5.0,
            "sec_stress_b": 1.0,
            "sec_stress_c": 1.0,
            "sec_stress_d": 1.0,
            "sec_stress_e": 1.0,
            "sec_stress_f": 3.0,
        },
        artifact_notes={
            "sec_stress_a": (
                "quarter included a five-for-one split; Q1 reports post-event units, "
                "so compare Q4 shares in the same post-event unit basis"
            ),
            "sec_stress_b": "no corporate-action adjustment noted",
            "sec_stress_c": "no corporate-action adjustment noted; reduction is close to the largest adjusted action",
            "sec_stress_d": "reported value moved sharply, but share count did not change",
            "sec_stress_e": "small position with large relative share-count movement",
            "sec_stress_f": (
                "quarter included a three-for-one split; Q1 reports post-event units, "
                "so compare Q4 shares in the same post-event unit basis"
            ),
        },
    ),
]


ARTIFACT_IMPLICIT_STABLE_CASES = [
    FilingArtifactCase(
        key="multi_artifact_value_stable_close_runner_up",
        real_case=(
            "13F-style filing trace where split-like row ratios are paired with "
            "stable reported value, isolating implicit artifact inference from "
            "reported-value drift"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT VALUE-STABILITY TRACE",
        source_url=(
            "public SEC-style 13F information table rows with no artifact notes; "
            "value-stability control for implicit split-like artifacts"
        ),
        target_accession="neutralized-2026q1-artifact-implicit-stable",
        rows=tuple(
            FilingTraceRow(row.period, row.accession, row.issuer, 315000000, row.shares)
            if row.period == "2026q1" and row.issuer == "sec_stress_f"
            else row
            for row in ARTIFACT_STRESS_CASES[0].rows
        ),
        adjustment_factors=dict(ARTIFACT_STRESS_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_STRESS_CASES[0].artifact_notes),
    ),
]


ARTIFACT_METADATA_NOISY_CASES = [
    FilingArtifactCase(
        key="multi_artifact_noisy_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where the corporate-action registry has the "
            "right target-period split records but also stale, unconfirmed, "
            "non-split, and unmatched distractors"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT NOISY-REGISTRY TRACE",
        source_url=(
            "public SEC-style 13F information table rows plus a neutralized noisy "
            "corporate-action registry"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-noisy",
        rows=ARTIFACT_STRESS_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_STRESS_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_STRESS_CASES[0].artifact_notes),
        corporate_actions=(
            CorporateActionRegistryEntry(
                "sec_stress_a",
                "stock_split",
                5.0,
                "2026q1",
                "neutralized_corporate_action_registry",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_c",
                "stock_split",
                2.0,
                "2026q1",
                "third_party_preliminary_feed",
                status="unconfirmed",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_d",
                "spin_off",
                1.0,
                "2026q1",
                "issuer_news_feed",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_f",
                "stock_split",
                3.0,
                "2026q1",
                "neutralized_corporate_action_registry",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_c",
                "stock_split",
                3.0,
                "2025q3",
                "archived_vendor_feed",
                status="stale",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_z",
                "stock_split",
                4.0,
                "2026q1",
                "unmatched_vendor_feed",
            ),
        ),
    ),
]


ARTIFACT_METADATA_PARTIAL_CASES = [
    FilingArtifactCase(
        key="multi_artifact_partial_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where the registry confirms one split artifact "
            "but omits another target-period split-like artifact that must be "
            "inferred from row-ratio evidence"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT PARTIAL-REGISTRY TRACE",
        source_url=(
            "public SEC-style 13F information table rows plus a neutralized partial "
            "corporate-action registry"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-partial",
        rows=ARTIFACT_STRESS_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_STRESS_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_STRESS_CASES[0].artifact_notes),
        corporate_actions=(
            CorporateActionRegistryEntry(
                "sec_stress_f",
                "stock_split",
                3.0,
                "2026q1",
                "neutralized_corporate_action_registry",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_c",
                "stock_split",
                2.0,
                "2026q1",
                "third_party_preliminary_feed",
                status="unconfirmed",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_z",
                "stock_split",
                4.0,
                "2026q1",
                "unmatched_vendor_feed",
            ),
        ),
    ),
]


ARTIFACT_METADATA_CONFLICT_CASES = [
    FilingArtifactCase(
        key="multi_artifact_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where the registry contains the right split "
            "records plus a wrong-but-confirmed target-period split record that "
            "conflicts with the filing-row ratios"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT CONFLICTING-REGISTRY TRACE",
        source_url=(
            "public SEC-style 13F information table rows plus a neutralized "
            "corporate-action registry with a confirmed conflicting record"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-conflict",
        rows=ARTIFACT_STRESS_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_STRESS_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_STRESS_CASES[0].artifact_notes),
        corporate_actions=(
            CorporateActionRegistryEntry(
                "sec_stress_a",
                "stock_split",
                5.0,
                "2026q1",
                "neutralized_corporate_action_registry",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_d",
                "stock_split",
                4.0,
                "2026q1",
                "neutralized_corporate_action_registry",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_f",
                "stock_split",
                3.0,
                "2026q1",
                "neutralized_corporate_action_registry",
            ),
        ),
    ),
]


ARTIFACT_METADATA_UNMARKED_CONFLICT_CASES = [
    FilingArtifactCase(
        key="multi_artifact_unmarked_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where the registry contains the right split "
            "records plus a wrong-but-confirmed target-period split record, but "
            "the prompt does not explicitly warn that registry rows may conflict "
            "with filing-row ratios"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT UNMARKED-CONFLICT REGISTRY TRACE",
        source_url=(
            "public SEC-style 13F information table rows plus a neutralized "
            "corporate-action registry with an unmarked confirmed conflicting record"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-unmarked-conflict",
        rows=ARTIFACT_METADATA_CONFLICT_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_CONFLICT_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_CONFLICT_CASES[0].artifact_notes),
        corporate_actions=ARTIFACT_METADATA_CONFLICT_CASES[0].corporate_actions,
    ),
]


ARTIFACT_METADATA_HISTORY_CONFLICT_CASES = [
    FilingArtifactCase(
        key="multi_artifact_history_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where issuer-level history repeats across filings "
            "and the registry contains a wrong confirmed target-period split record"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT HISTORY-CONFLICT REGISTRY TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus a neutralized "
            "corporate-action registry with an unmarked confirmed conflicting record"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-history-conflict",
        rows=(
            FilingTraceRow("2025q3", "artifact-history-2025q3", "sec_stress_a", 735000000, 1500000),
            FilingTraceRow("2025q3", "artifact-history-2025q3", "sec_stress_b", 1180000000, 3000000),
            FilingTraceRow("2025q3", "artifact-history-2025q3", "sec_stress_c", 850000000, 2100000),
            FilingTraceRow("2025q3", "artifact-history-2025q3", "sec_stress_d", 880000000, 1800000),
            FilingTraceRow("2025q3", "artifact-history-2025q3", "sec_stress_e", 19000000, 100000),
            FilingTraceRow("2025q3", "artifact-history-2025q3", "sec_stress_f", 295000000, 1000000),
            *ARTIFACT_METADATA_CONFLICT_CASES[0].rows,
        ),
        adjustment_factors=dict(ARTIFACT_METADATA_CONFLICT_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_CONFLICT_CASES[0].artifact_notes),
        corporate_actions=ARTIFACT_METADATA_CONFLICT_CASES[0].corporate_actions,
    ),
]


ARTIFACT_METADATA_VALIDATION_PROCESS_CASES = [
    FilingArtifactCase(
        key="multi_artifact_validation_process_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with a "
            "generic registry-validation process for target-period stock splits"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT VALIDATION-PROCESS TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus a neutralized "
            "corporate-action registry and a generic row-ratio validation process"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-validation-process",
        rows=ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].artifact_notes),
        corporate_actions=ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].corporate_actions,
    ),
]


ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES = [
    FilingArtifactCase(
        key="multi_artifact_source_provenance_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with "
            "source-provenance labels for target-period stock-split registry rows"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT SOURCE-PROVENANCE TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus a neutralized "
            "corporate-action registry with source-provenance labels"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-source-provenance",
        rows=ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_HISTORY_CONFLICT_CASES[0].artifact_notes),
        corporate_actions=(
            CorporateActionRegistryEntry(
                "sec_stress_a",
                "stock_split",
                5.0,
                "2026q1",
                "issuer_exchange_notice",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_d",
                "stock_split",
                4.0,
                "2026q1",
                "third_party_backfill_feed",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_f",
                "stock_split",
                3.0,
                "2026q1",
                "issuer_exchange_notice",
            ),
        ),
    ),
]


ARTIFACT_METADATA_SOURCE_CONTEXT_CASES = [
    FilingArtifactCase(
        key="multi_artifact_source_context_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with "
            "natural source packets for target-period stock-split registry rows"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT SOURCE-CONTEXT TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus neutralized corporate-action "
            "registry rows and natural source packets"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-source-context",
        rows=ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].artifact_notes),
        corporate_actions=ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].corporate_actions,
    ),
]


ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_CASES = [
    FilingArtifactCase(
        key="multi_artifact_source_status_ablation_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with "
            "natural source packets and a third-party split row that is not "
            "issuer-confirmed"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT SOURCE-STATUS ABLATION TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus neutralized corporate-action "
            "registry rows, natural source packets, and a non-confirmed third-party row"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-source-status-ablation",
        rows=ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].artifact_notes),
        corporate_actions=(
            CorporateActionRegistryEntry(
                "sec_stress_a",
                "stock_split",
                5.0,
                "2026q1",
                "issuer_exchange_notice",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_d",
                "stock_split",
                4.0,
                "2026q1",
                "third_party_backfill_feed",
                status="unverified",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_f",
                "stock_split",
                3.0,
                "2026q1",
                "issuer_exchange_notice",
            ),
        ),
    ),
]


ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES = [
    FilingArtifactCase(
        key="multi_artifact_source_status_neutral_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with "
            "natural source packets and status-neutral target-period split rows"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT SOURCE-STATUS NEUTRAL TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus neutralized corporate-action "
            "registry rows with natural source packets and no status labels"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-source-status-neutral",
        rows=ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES[0].artifact_notes),
        corporate_actions=(
            CorporateActionRegistryEntry(
                "sec_stress_a",
                "stock_split",
                5.0,
                "2026q1",
                "issuer_exchange_notice",
                status="",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_d",
                "stock_split",
                4.0,
                "2026q1",
                "third_party_backfill_feed",
                status="",
            ),
            CorporateActionRegistryEntry(
                "sec_stress_f",
                "stock_split",
                3.0,
                "2026q1",
                "issuer_exchange_notice",
                status="",
            ),
        ),
    ),
]


ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_CASES = [
    FilingArtifactCase(
        key="multi_artifact_source_status_neutral_intro_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with "
            "natural source packets, status-neutral split rows, and a metadata "
            "intro that does not imply confirmation"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT SOURCE-STATUS NEUTRAL INTRO TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus neutralized corporate-action "
            "registry rows with natural source packets, no status labels, and no "
            "confirmation wording in the metadata intro"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-source-status-neutral-intro",
        rows=ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].artifact_notes),
        corporate_actions=ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].corporate_actions,
    ),
]


ARTIFACT_METADATA_SOURCE_AUDIT_CASES = [
    FilingArtifactCase(
        key="multi_artifact_source_audit_conflicting_registry_close_runner_up",
        real_case=(
            "13F-style filing trace where repeated issuer history is paired with "
            "natural source packets, status-neutral split rows, and a "
            "corporate-action source-audit instruction"
        ),
        manager_cik="0000000001",
        manager_name="NEUTRALIZED PUBLIC-FILING ARTIFACT SOURCE-AUDIT TRACE",
        source_url=(
            "public SEC-style repeated issuer filing rows plus neutralized corporate-action "
            "registry rows with natural source packets, no status labels, and a "
            "source-audit protocol for non-primary rows"
        ),
        target_accession="neutralized-2026q1-artifact-metadata-source-audit",
        rows=ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].rows,
        adjustment_factors=dict(ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].adjustment_factors),
        artifact_notes=dict(ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].artifact_notes),
        corporate_actions=ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES[0].corporate_actions,
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
        percent_change = percent_change_trade(case)
        second_best = second_best_action_trade(case)
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
                percent_change_trade=percent_change,
                second_best_trade=second_best,
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
        percent_change = _issuer_for_trade(case, percent_change_trade(case))
        second_best = _issuer_for_trade(case, second_best_action_trade(case))
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
                percent_change_trade=percent_change,
                second_best_trade=second_best,
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


def run_principal_holding_filing_artifact_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases,
        task="principal_holding_filing_artifact",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_SYSTEM,
        include_factor=True,
        include_notes=True,
        include_metadata=False,
    )


def run_principal_holding_filing_artifact_natural_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases,
        task="principal_holding_filing_artifact_natural",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_NATURAL_SYSTEM,
        include_factor=False,
        include_notes=True,
        include_metadata=False,
    )


def run_principal_holding_filing_artifact_stress_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_STRESS_CASES,
        task="principal_holding_filing_artifact_stress",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_STRESS_SYSTEM,
        include_factor=False,
        include_notes=True,
        include_metadata=False,
    )


def run_principal_holding_filing_artifact_implicit_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_STRESS_CASES,
        task="principal_holding_filing_artifact_implicit",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_IMPLICIT_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=False,
    )


def run_principal_holding_filing_artifact_implicit_stable_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_IMPLICIT_STABLE_CASES,
        task="principal_holding_filing_artifact_implicit_stable",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_IMPLICIT_STABLE_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=False,
    )


def run_principal_holding_filing_artifact_metadata_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_STRESS_CASES,
        task="principal_holding_filing_artifact_metadata",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
    )


def run_principal_holding_filing_artifact_metadata_noisy_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_NOISY_CASES,
        task="principal_holding_filing_artifact_metadata_noisy",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_NOISY_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
    )


def run_principal_holding_filing_artifact_metadata_partial_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_PARTIAL_CASES,
        task="principal_holding_filing_artifact_metadata_partial",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_PARTIAL_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
    )


def run_principal_holding_filing_artifact_metadata_conflict_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_CONFLICT_CASES,
        task="principal_holding_filing_artifact_metadata_conflict",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_CONFLICT_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=True,
    )


def run_principal_holding_filing_artifact_metadata_unmarked_conflict_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_UNMARKED_CONFLICT_CASES,
        task="principal_holding_filing_artifact_metadata_unmarked_conflict",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_UNMARKED_CONFLICT_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
    )


def run_principal_holding_filing_artifact_metadata_history_conflict_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_HISTORY_CONFLICT_CASES,
        task="principal_holding_filing_artifact_metadata_history_conflict",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_HISTORY_CONFLICT_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
    )


def run_principal_holding_filing_artifact_metadata_validation_process_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_VALIDATION_PROCESS_CASES,
        task="principal_holding_filing_artifact_metadata_validation_process",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_VALIDATION_PROCESS_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_validation_process=True,
    )


def run_principal_holding_filing_artifact_metadata_source_provenance_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES,
        task="principal_holding_filing_artifact_metadata_source_provenance",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_PROVENANCE_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_source_provenance=True,
    )


def run_principal_holding_filing_artifact_metadata_source_context_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_SOURCE_CONTEXT_CASES,
        task="principal_holding_filing_artifact_metadata_source_context",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_CONTEXT_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_source_context=True,
    )


def run_principal_holding_filing_artifact_metadata_source_status_ablation_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_CASES,
        task="principal_holding_filing_artifact_metadata_source_status_ablation",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_source_context=True,
    )


def run_principal_holding_filing_artifact_metadata_source_status_neutral_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES,
        task="principal_holding_filing_artifact_metadata_source_status_neutral",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_source_context=True,
    )


def run_principal_holding_filing_artifact_metadata_source_status_neutral_intro_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_CASES,
        task="principal_holding_filing_artifact_metadata_source_status_neutral_intro",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_source_context=True,
        include_status_neutral_metadata_intro=True,
    )


def run_principal_holding_filing_artifact_metadata_source_audit_game(
    agent: Agent,
    cases: list[FilingArtifactCase] | None = None,
) -> dict:
    return _run_principal_holding_filing_artifact_game(
        agent,
        cases=cases or ARTIFACT_METADATA_SOURCE_AUDIT_CASES,
        task="principal_holding_filing_artifact_metadata_source_audit",
        system=PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_SYSTEM,
        include_factor=False,
        include_notes=False,
        include_metadata=True,
        include_conflict_warning=False,
        include_source_context=True,
        include_status_neutral_metadata_intro=True,
        include_source_audit=True,
    )


def _run_principal_holding_filing_artifact_game(
    agent: Agent,
    *,
    cases: list[FilingArtifactCase] | None,
    task: str,
    system: str,
    include_factor: bool,
    include_notes: bool,
    include_metadata: bool,
    include_conflict_warning: bool = True,
    include_validation_process: bool = False,
    include_source_provenance: bool = False,
    include_source_context: bool = False,
    include_status_neutral_metadata_intro: bool = False,
    include_source_audit: bool = False,
) -> dict:
    cases = cases or ARTIFACT_CASES
    trials: list[FilingArtifactTrial] = []
    for case in cases:
        principal = artifact_material_action_issuer(case)
        artifact_blind = artifact_blind_issuer(case)
        market_value = artifact_market_value_issuer(case)
        percent_change = artifact_percent_change_issuer(case)
        second_best = artifact_second_best_issuer(case)
        metadata_trusting = (
            artifact_metadata_trusting_issuer(case) if include_metadata else None
        )
        metadata_status_blind = (
            artifact_metadata_status_blind_issuer(case) if include_metadata else None
        )
        score_by_id = _normalized_artifact_scores(case)
        oracle_margin = _oracle_margin(score_by_id, principal)
        response = agent.complete(
            system,
            _artifact_prompt(
                case,
                include_factor=include_factor,
                include_notes=include_notes,
                include_metadata=include_metadata,
                include_conflict_warning=include_conflict_warning,
                include_validation_process=include_validation_process,
                include_source_provenance=include_source_provenance,
                include_source_context=include_source_context,
                include_status_neutral_metadata_intro=include_status_neutral_metadata_intro,
                include_source_audit=include_source_audit,
            ),
        )
        chosen = parse_token("FINAL_ISSUER", response)
        chosen = chosen if chosen in score_by_id else None
        chosen_score = score_by_id[chosen] if chosen else None
        trials.append(
            FilingArtifactTrial(
                case=case,
                principal_trade=principal,
                artifact_blind_trade=artifact_blind,
                market_value_trade=market_value,
                percent_change_trade=percent_change,
                second_best_trade=second_best,
                metadata_trusting_trade=metadata_trusting,
                metadata_status_blind_trade=metadata_status_blind,
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
    return summarize_filing_artifact_trials(agent.name, trials, task=task)


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


def percent_change_trade(case: FilingTraceCase) -> str:
    return max(case.target_trades, key=_share_change_fraction).trade_id


def second_best_action_trade(case: FilingTraceCase) -> str:
    ranked = sorted(case.target_trades, key=_action_value, reverse=True)
    if not ranked:
        raise ValueError("filing trace case has no target trades")
    return ranked[1].trade_id if len(ranked) > 1 else ranked[0].trade_id


def artifact_material_action_issuer(case: FilingArtifactCase) -> str:
    changes = _artifact_changes(case)
    return max(changes, key=lambda issuer: changes[issuer]["value"])


def artifact_blind_issuer(case: FilingArtifactCase) -> str:
    changes = _artifact_changes(case)
    return max(changes, key=lambda issuer: changes[issuer]["observed_value"])


def artifact_market_value_issuer(case: FilingArtifactCase) -> str:
    changes = _artifact_changes(case)
    return max(
        changes,
        key=lambda issuer: changes[issuer]["next_value"] - changes[issuer]["prior_value"],
    )


def artifact_percent_change_issuer(case: FilingArtifactCase) -> str:
    changes = _artifact_changes(case)
    return max(changes, key=lambda issuer: changes[issuer]["observed_fraction"])


def artifact_second_best_issuer(case: FilingArtifactCase) -> str:
    changes = _artifact_changes(case)
    ranked = sorted(changes, key=lambda issuer: changes[issuer]["value"], reverse=True)
    if not ranked:
        raise ValueError("filing artifact case has no issuer changes")
    return ranked[1] if len(ranked) > 1 else ranked[0]


def artifact_metadata_trusting_issuer(case: FilingArtifactCase) -> str | None:
    factors: dict[str, float] = {}
    target_period = _artifact_target_period(case)
    active_statuses = {"", "active", "confirmed", "effective"}
    for entry in _corporate_action_registry_entries(case):
        if entry.action != "stock_split":
            continue
        if entry.effective_period != target_period:
            continue
        if entry.status not in active_statuses:
            continue
        factors.setdefault(entry.issuer, entry.ratio)
    if not factors:
        return None
    changes = _artifact_changes_with_factors(case, factors)
    return max(changes, key=lambda issuer: changes[issuer]["value"])


def artifact_metadata_status_blind_issuer(case: FilingArtifactCase) -> str | None:
    factors: dict[str, float] = {}
    target_period = _artifact_target_period(case)
    for entry in _corporate_action_registry_entries(case):
        if entry.action != "stock_split":
            continue
        if entry.effective_period != target_period:
            continue
        factors.setdefault(entry.issuer, entry.ratio)
    if not factors:
        return None
    changes = _artifact_changes_with_factors(case, factors)
    return max(changes, key=lambda issuer: changes[issuer]["value"])


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
    percent_change_missable = [
        trial for trial in trials if trial.percent_change_trade != trial.principal_trade
    ]
    second_best_missable = [
        trial for trial in trials if trial.second_best_trade != trial.principal_trade
    ]
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
        "percent_change_miss_rate": _reference_miss_rate(
            percent_change_missable,
            "percent_change_trade",
        ),
        "second_best_miss_rate": _reference_miss_rate(
            second_best_missable,
            "second_best_trade",
        ),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _reference_miss_rate(trials: list[FilingTraceTrial], attr: str) -> float:
    if not trials:
        return 0.0
    return sum(trial.chosen_trade == getattr(trial, attr) for trial in trials) / len(trials)


def summarize_filing_artifact_trials(
    agent_name: str,
    trials: list[FilingArtifactTrial],
    *,
    task: str = "principal_holding_filing_artifact",
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    parsed = [trial for trial in trials if trial.chosen_trade is not None]
    margins = [trial.oracle_margin for trial in trials]
    artifact_missable = [
        trial for trial in trials if trial.artifact_blind_trade != trial.principal_trade
    ]
    market_missable = [
        trial for trial in trials if trial.market_value_trade != trial.principal_trade
    ]
    percent_missable = [
        trial for trial in trials if trial.percent_change_trade != trial.principal_trade
    ]
    second_best_missable = [
        trial for trial in trials if trial.second_best_trade != trial.principal_trade
    ]
    metadata_trusting_missable = [
        trial
        for trial in trials
        if trial.metadata_trusting_trade is not None
        and trial.metadata_trusting_trade != trial.principal_trade
    ]
    metadata_status_blind_missable = [
        trial
        for trial in trials
        if trial.metadata_status_blind_trade is not None
        and trial.metadata_status_blind_trade != trial.principal_trade
    ]
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
        "artifact_blind_miss_rate": _artifact_reference_miss_rate(
            artifact_missable,
            "artifact_blind_trade",
        ),
        "market_value_miss_rate": _artifact_reference_miss_rate(
            market_missable,
            "market_value_trade",
        ),
        "percent_change_miss_rate": _artifact_reference_miss_rate(
            percent_missable,
            "percent_change_trade",
        ),
        "second_best_miss_rate": _artifact_reference_miss_rate(
            second_best_missable,
            "second_best_trade",
        ),
        "metadata_trusting_miss_rate": _artifact_reference_miss_rate(
            metadata_trusting_missable,
            "metadata_trusting_trade",
        ),
        "metadata_status_blind_miss_rate": _artifact_reference_miss_rate(
            metadata_status_blind_missable,
            "metadata_status_blind_trade",
        ),
        "trials": [_artifact_trial_json(trial) for trial in trials],
    }


def _artifact_reference_miss_rate(trials: list[FilingArtifactTrial], attr: str) -> float:
    if not trials:
        return 0.0
    return sum(trial.chosen_trade == getattr(trial, attr) for trial in trials) / len(trials)


def _prompt(case: FilingTraceCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Rows are neutralized but derived from public SEC 13F-HR information tables.",
        "The task is to identify the dollar-material share-driven holding action: approximate prior reported value per share times absolute share-count change.",
        "Do not choose only by market-value drift, prior position size, previous-period trend, no-change turnover, or largest percentage reduction.",
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
        "Choose the candidate with the largest approximate dollar value of share-count change implied by the filings."
    )
    return "\n".join(lines)


def _raw_prompt(case: FilingTraceCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Rows are neutralized but derived from public SEC 13F-HR information tables.",
        "The final period is the next disclosed filing; infer the issuer with the dollar-material share-driven action from the raw rows.",
        "Dollar materiality means approximate prior reported value per share times absolute share-count change.",
        "Do not choose only by reported value movement, prior position size, previous-period trend, no-change turnover, or largest percentage reduction.",
        "Raw filing rows:",
    ]
    for row in _raw_filing_rows(case):
        lines.append(
            f"filing_row period={row.period} accession={row.accession} "
            f"issuer={row.issuer} reported_value={row.value:.0f} shares={row.shares:.0f}"
        )
    issuers = ", ".join(sorted({trade.issuer for trade in case.target_trades}))
    lines.append(f"issuer_choices={issuers}")
    lines.append("Return the issuer id with the largest approximate dollar value of share-count change.")
    return "\n".join(lines)


def _artifact_prompt(
    case: FilingArtifactCase,
    *,
    include_factor: bool = True,
    include_notes: bool = True,
    include_metadata: bool = False,
    include_conflict_warning: bool = True,
    include_validation_process: bool = False,
    include_source_provenance: bool = False,
    include_source_context: bool = False,
    include_status_neutral_metadata_intro: bool = False,
    include_source_audit: bool = False,
) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Rows are neutralized 13F-style filing rows. Some observed share-count changes are mechanical corporate-action artifacts.",
        "The final period is the next disclosed filing. Infer the issuer with the largest dollar-material discretionary share action after applying any artifact adjustment.",
        "Dollar materiality means adjusted prior reported value per comparable share times absolute adjusted share-count change.",
        "Do not choose only by raw unadjusted share-count movement, reported value movement, largest percentage change, or runner-up adjusted action.",
        "Raw filing rows:",
    ]
    for row in sorted(case.rows, key=lambda item: (item.issuer, item.period)):
        lines.append(
            f"filing_row period={row.period} accession={row.accession} "
            f"issuer={row.issuer} reported_value={row.value:.0f} shares={row.shares:.0f}"
        )
    if include_notes:
        lines.append("Artifact notes:")
        for issuer in sorted(case.adjustment_factors):
            if include_factor:
                lines.append(
                    f"artifact_note issuer={issuer} adjustment_factor={case.adjustment_factors[issuer]:.6g} "
                    f"note={case.artifact_notes.get(issuer, 'no note')}"
                )
            else:
                lines.append(
                    f"artifact_note issuer={issuer} note={case.artifact_notes.get(issuer, 'no note')}"
                )
    else:
        metadata_record_phrase = (
            "target-period corporate-action registry records"
            if include_status_neutral_metadata_intro
            else "target-period confirmed corporate-action registry records"
        )
        lines.append(
            "No separate corporate-action notes are provided. Use filing rows and any "
            f"{metadata_record_phrase} to identify mechanical "
            "unit changes before scoring discretionary share actions."
            if include_metadata
            else (
                "No separate corporate-action notes are provided. Infer split-like artifacts from "
                "filing-row patterns: clean integer-multiple share changes paired with roughly "
                "stable economic exposure should be treated as mechanical unit changes before "
                "scoring discretionary share actions."
            )
        )
    if include_metadata:
        if _registry_has_missing_split_entries(
            case,
            include_statusless=include_status_neutral_metadata_intro,
        ):
            missing_record_phrase = (
                "target-period split record"
                if include_status_neutral_metadata_intro
                else "confirmed target-period split record"
            )
            lines.append(
                "Registry coverage may be incomplete. If a "
                f"{missing_record_phrase} is missing, use clean integer row-ratio "
                "evidence paired with comparable economic exposure to identify "
                "mechanical unit changes."
            )
        if include_conflict_warning and _registry_has_conflicting_split_entries(case):
            lines.append(
                "Registry records may conflict with filing rows. Validate confirmed "
                "stock-split records against target-period row-ratio evidence before "
                "applying them."
            )
        if include_validation_process:
            lines.append(
                "Validation process: for each target-period stock-split registry row, "
                "compute observed_ratio=next_period_shares/prior_period_shares from "
                "the filing rows. Apply the split only when observed_ratio approximately "
                "matches the registry ratio before scoring discretionary share actions."
            )
        if include_source_provenance:
            lines.append(
                "Registry provenance: issuer_exchange_notice sources are direct "
                "corporate-action records; third_party_backfill_feed sources are "
                "lower-reliability registry metadata."
            )
        if include_source_context:
            lines.append("Corporate action source packets:")
            lines.extend(_corporate_action_source_packets(case))
        if include_source_audit:
            lines.append(
                "Source audit protocol: issuer_exchange_notice packets with attached "
                "transfer-agent and exchange records are primary corporate-action "
                "evidence. For third_party_backfill_feed rows without issuer notice, "
                "exchange bulletin, or transfer-agent attachment, reconcile the claimed "
                "split ratio against filing-row share-count ratios before applying the "
                "registry adjustment; if filing rows do not support the claimed ratio, "
                "do not use that row as a mechanical unit change."
            )
        lines.append("Corporate action registry:")
        for entry in _corporate_action_registry_entries(case):
            line = (
                f"corporate_action issuer={entry.issuer} action={entry.action} "
                f"ratio={_split_ratio_label(entry.ratio)} "
                f"effective_period={entry.effective_period} source={entry.source}"
            )
            if entry.status:
                line = f"{line} status={entry.status}"
            lines.append(line)
    issuers = ", ".join(sorted({row.issuer for row in case.rows}))
    lines.append(f"issuer_choices={issuers}")
    lines.append(
        "Return the issuer id with the largest adjusted dollar-material discretionary share action."
    )
    return "\n".join(lines)


def _corporate_action_registry_entries(
    case: FilingArtifactCase,
) -> tuple[CorporateActionRegistryEntry, ...]:
    if case.corporate_actions:
        return case.corporate_actions
    return tuple(
        CorporateActionRegistryEntry(
            issuer,
            "stock_split",
            factor,
            _artifact_target_period(case),
            "neutralized_corporate_action_registry",
            status="",
        )
        for issuer, factor in sorted(case.adjustment_factors.items())
        if factor != 1
    )


def _corporate_action_source_packets(case: FilingArtifactCase) -> list[str]:
    packets: list[str] = []
    for entry in _corporate_action_registry_entries(case):
        if entry.source == "issuer_exchange_notice":
            packets.append(
                f"source_packet issuer={entry.issuer} provenance=issuer_exchange_notice "
                f"text=Issuer/exchange notice reports a {_split_ratio_label(entry.ratio)} "
                f"stock split effective {entry.effective_period}; transfer-agent notice "
                "and exchange action bulletin are attached."
            )
        elif entry.source == "third_party_backfill_feed":
            packets.append(
                f"source_packet issuer={entry.issuer} provenance=third_party_backfill_feed "
                f"text=Third-party security-master backfill lists a {_split_ratio_label(entry.ratio)} "
                f"stock split effective {entry.effective_period}; no issuer notice, exchange "
                "bulletin, or transfer-agent attachment is present."
            )
    return packets


def _registry_has_missing_split_entries(
    case: FilingArtifactCase,
    *,
    include_statusless: bool = False,
) -> bool:
    if not case.corporate_actions:
        return False
    target_period = _artifact_target_period(case)
    expected = {
        issuer
        for issuer, factor in case.adjustment_factors.items()
        if factor != 1
    }
    active_statuses = {"active", "confirmed", "effective"}
    if include_statusless:
        active_statuses.add("")
    confirmed = {
        entry.issuer
        for entry in case.corporate_actions
        if entry.action == "stock_split"
        and entry.effective_period == target_period
        and entry.status in active_statuses
    }
    return bool(expected - confirmed)


def _registry_has_conflicting_split_entries(case: FilingArtifactCase) -> bool:
    if not case.corporate_actions:
        return False
    target_period = _artifact_target_period(case)
    rows_by_issuer = _artifact_rows_by_issuer(case)
    for entry in case.corporate_actions:
        if (
            entry.action != "stock_split"
            or entry.effective_period != target_period
            or entry.status not in {"active", "confirmed", "effective"}
        ):
            continue
        row_pair = rows_by_issuer.get(entry.issuer)
        if not row_pair:
            continue
        prior, next_row = row_pair
        if prior.shares <= 0:
            continue
        observed_ratio = next_row.shares / prior.shares
        if abs(observed_ratio - entry.ratio) > 0.02:
            return True
    return False


def _artifact_rows_by_issuer(
    case: FilingArtifactCase,
) -> dict[str, tuple[FilingTraceRow, FilingTraceRow]]:
    periods = sorted({row.period for row in case.rows})
    if len(periods) < 2:
        return {}
    prior_period, next_period = periods[-2], periods[-1]
    rows: dict[str, dict[str, FilingTraceRow]] = {}
    for row in case.rows:
        rows.setdefault(row.issuer, {})[row.period] = row
    return {
        issuer: (period_rows[prior_period], period_rows[next_period])
        for issuer, period_rows in rows.items()
        if prior_period in period_rows and next_period in period_rows
    }


def _artifact_target_period(case: FilingArtifactCase) -> str:
    return sorted({row.period for row in case.rows})[-1]


def _split_ratio_label(factor: float) -> str:
    rounded = round(factor)
    if abs(factor - rounded) < 1e-9:
        return f"{rounded}-for-1"
    return f"{factor:.6g}-for-1"


def _action_value(trade: FilingTraceTrade) -> float:
    prior_price = trade.prior_value / trade.prior_shares if trade.prior_shares else 0.0
    return abs(trade.next_shares - trade.prior_shares) * prior_price


def _share_change_fraction(trade: FilingTraceTrade) -> float:
    if trade.prior_shares <= 0:
        return 0.0
    return abs(trade.next_shares - trade.prior_shares) / trade.prior_shares


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


def _normalized_artifact_scores(case: FilingArtifactCase) -> dict[str, float]:
    values = {issuer: data["value"] for issuer, data in _artifact_changes(case).items()}
    max_value = max(values.values()) if values else 0.0
    if max_value <= 0:
        return {issuer: 0.0 for issuer in values}
    return {issuer: value / max_value for issuer, value in values.items()}


def _artifact_changes(case: FilingArtifactCase) -> dict[str, dict[str, float]]:
    return _artifact_changes_with_factors(case, case.adjustment_factors)


def _artifact_changes_with_factors(
    case: FilingArtifactCase,
    factors: dict[str, float],
) -> dict[str, dict[str, float]]:
    rows_by_issuer: dict[str, list[FilingTraceRow]] = {}
    for row in case.rows:
        rows_by_issuer.setdefault(row.issuer, []).append(row)
    changes: dict[str, dict[str, float]] = {}
    for issuer, rows in rows_by_issuer.items():
        ordered = sorted(rows, key=lambda row: row.period)
        if len(ordered) < 2:
            continue
        prior = ordered[-2]
        next_ = ordered[-1]
        factor = factors.get(issuer, 1.0)
        adjusted_prior_shares = prior.shares * factor
        adjusted_delta = next_.shares - adjusted_prior_shares
        observed_delta = next_.shares - prior.shares
        adjusted_price = prior.value / adjusted_prior_shares if adjusted_prior_shares else 0.0
        observed_price = prior.value / prior.shares if prior.shares else 0.0
        changes[issuer] = {
            "prior_value": prior.value,
            "next_value": next_.value,
            "prior_shares": prior.shares,
            "next_shares": next_.shares,
            "adjustment_factor": factor,
            "adjusted_prior_shares": adjusted_prior_shares,
            "adjusted_delta": adjusted_delta,
            "observed_delta": observed_delta,
            "value": abs(adjusted_delta) * adjusted_price,
            "observed_value": abs(observed_delta) * observed_price,
            "observed_fraction": abs(observed_delta) / prior.shares if prior.shares else 0.0,
        }
    return changes


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


def _artifact_trial_json(trial: FilingArtifactTrial) -> dict:
    data = asdict(trial)
    data["case"] = {
        "key": trial.case.key,
        "real_case": trial.case.real_case,
        "manager_cik": trial.case.manager_cik,
        "source_url": trial.case.source_url,
        "target_accession": trial.case.target_accession,
    }
    data["artifact_changes"] = _artifact_changes(trial.case)
    return data
