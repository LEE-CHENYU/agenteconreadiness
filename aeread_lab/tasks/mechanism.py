from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


MECHANISM_SYSTEM = (
    "TASK: mechanism_choice\n"
    "Choose the mechanism for the configured principal. Return one final line only: "
    "FINAL_MECHANISM: <mechanism_id>."
)

MECHANISM_REPEATED_SYSTEM = (
    "TASK: mechanism_repeated_choice\n"
    "Choose the mechanism for a repeated market setting. Return one final line only: "
    "FINAL_MECHANISM: <mechanism_id>."
)

MECHANISM_PARTICIPANT_RESPONSE_SYSTEM = (
    "TASK: mechanism_participant_response\n"
    "Choose the mechanism for a repeated program with participant response. "
    "Return one final line only: FINAL_MECHANISM: <mechanism_id>."
)

MECHANISM_STRATEGIC_RESPONSE_SYSTEM = (
    "TASK: mechanism_strategic_response\n"
    "Choose the mechanism for a repeated program with strategic multi-participant response. "
    "Return one final line only: FINAL_MECHANISM: <mechanism_id>."
)

MECHANISM_STRATEGIC_EQUILIBRIUM_SYSTEM = (
    "TASK: mechanism_strategic_equilibrium\n"
    "Choose the mechanism for a repeated program after solving strategic response equilibrium. "
    "Return one final line only: FINAL_MECHANISM: <mechanism_id>."
)

MECHANISM_INTERACTION_TRACE_SYSTEM = (
    "TASK: mechanism_interaction_trace\n"
    "Choose the mechanism for the remaining program rounds after reading prior interaction traces. "
    "Return one final line only: FINAL_MECHANISM: <mechanism_id>."
)


@dataclass(frozen=True)
class IncentiveCheck:
    type_id: str
    probability: float
    truthful_utility: float
    best_deviation_utility: float


@dataclass(frozen=True)
class MechanismOption:
    mechanism_id: str
    revenue: float
    welfare: float
    access: float
    strategic_risk: float
    incentive_checks: tuple[IncentiveCheck, ...] = ()


@dataclass(frozen=True)
class MechanismCase:
    key: str
    real_case: str
    revenue_weight: float
    welfare_weight: float
    access_weight: float
    strategic_risk_penalty: float
    mechanisms: tuple[MechanismOption, ...]
    incentive_violation_penalty: float = 0.0


@dataclass
class MechanismTrial:
    case: MechanismCase
    best_mechanism: str
    revenue_mechanism: str
    risk_blind_mechanism: str
    ic_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    incentive_violation: float | None
    raw_response: str


@dataclass(frozen=True)
class RepeatedMechanismOption:
    mechanism_id: str
    first_period_revenue: float
    welfare: float
    access: float
    strategic_risk: float
    retention_rate: float
    manipulation_load: float
    manipulation_growth: float
    review_cost: float


@dataclass(frozen=True)
class RepeatedMechanismCase:
    key: str
    real_case: str
    horizon: int
    revenue_weight: float
    welfare_weight: float
    access_weight: float
    strategic_risk_penalty: float
    manipulation_penalty: float
    mechanisms: tuple[RepeatedMechanismOption, ...]


@dataclass
class RepeatedMechanismTrial:
    case: RepeatedMechanismCase
    best_mechanism: str
    revenue_mechanism: str
    one_period_mechanism: str
    risk_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    raw_response: str


@dataclass(frozen=True)
class ParticipantResponseMechanismOption:
    mechanism_id: str
    sponsor_take: float
    participant_value: float
    access_quality: float
    starting_participants: float
    base_stay_rate: float
    take_exit_sensitivity: float
    gaming_pressure: float
    trust_decay: float
    review_cost: float


@dataclass(frozen=True)
class ParticipantResponseMechanismCase:
    key: str
    real_case: str
    horizon: int
    revenue_weight: float
    participant_value_weight: float
    access_weight: float
    gaming_penalty: float
    mechanisms: tuple[ParticipantResponseMechanismOption, ...]


@dataclass
class ParticipantResponseMechanismTrial:
    case: ParticipantResponseMechanismCase
    best_mechanism: str
    revenue_mechanism: str
    one_period_mechanism: str
    response_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    raw_response: str


@dataclass(frozen=True)
class StrategicResponseMechanismOption:
    mechanism_id: str
    participant_count: float
    sponsor_take: float
    participant_value: float
    access_quality: float
    base_stay_rate: float
    exit_sensitivity: float
    initial_strategic_share: float
    strategic_gain: float
    peer_contagion: float
    audit_strength: float
    detection_cost: float
    manipulation_harm: float
    response_update_rate: float
    review_cost: float


@dataclass(frozen=True)
class StrategicResponseMechanismCase:
    key: str
    real_case: str
    horizon: int
    revenue_weight: float
    participant_value_weight: float
    access_weight: float
    manipulation_penalty: float
    mechanisms: tuple[StrategicResponseMechanismOption, ...]


@dataclass
class StrategicResponseMechanismTrial:
    case: StrategicResponseMechanismCase
    best_mechanism: str
    revenue_mechanism: str
    one_period_mechanism: str
    response_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    raw_response: str


@dataclass(frozen=True)
class InteractionTracePoint:
    round_id: int
    active_participants: float
    strategic_share: float


@dataclass(frozen=True)
class InteractionTraceMechanismOption:
    mechanism_id: str
    sponsor_take: float
    participant_value: float
    access_quality: float
    manipulation_harm: float
    review_cost: float
    trace: tuple[InteractionTracePoint, ...]


@dataclass(frozen=True)
class InteractionTraceMechanismCase:
    key: str
    real_case: str
    forecast_horizon: int
    revenue_weight: float
    participant_value_weight: float
    access_weight: float
    manipulation_penalty: float
    mechanisms: tuple[InteractionTraceMechanismOption, ...]


@dataclass
class InteractionTraceMechanismTrial:
    case: InteractionTraceMechanismCase
    best_mechanism: str
    revenue_mechanism: str
    one_period_mechanism: str
    trace_blind_mechanism: str
    chosen_mechanism: str | None
    score_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    MechanismCase(
        key="ad_slot_revenue",
        real_case="ad-slot allocation for a revenue-weighted platform seller",
        revenue_weight=1.0,
        welfare_weight=0.10,
        access_weight=0.0,
        strategic_risk_penalty=0.20,
        mechanisms=(
            MechanismOption("first_price_high_reserve", 118.0, 88.0, 40.0, 22.0),
            MechanismOption("second_price_truthful", 96.0, 120.0, 75.0, 3.0),
            MechanismOption("access_lottery", 50.0, 82.0, 95.0, 10.0),
        ),
    ),
    MechanismCase(
        key="public_grants_access",
        real_case="public grant allocation where access and participation dominate fee revenue",
        revenue_weight=0.0,
        welfare_weight=0.35,
        access_weight=1.20,
        strategic_risk_penalty=0.50,
        mechanisms=(
            MechanismOption("pay_to_rank", 120.0, 88.0, 40.0, 22.0),
            MechanismOption("scored_auction", 74.0, 120.0, 75.0, 3.0),
            MechanismOption("access_lottery", 35.0, 90.0, 94.0, 8.0),
        ),
    ),
    MechanismCase(
        key="platform_truthfulness",
        real_case="marketplace rule where long-run participation depends on truthful bidding",
        revenue_weight=0.80,
        welfare_weight=0.50,
        access_weight=0.20,
        strategic_risk_penalty=2.00,
        mechanisms=(
            MechanismOption("first_price_high_reserve", 130.0, 110.0, 50.0, 60.0),
            MechanismOption("second_price_truthful", 105.0, 124.0, 75.0, 3.0),
            MechanismOption("posted_price_menu", 92.0, 116.0, 86.0, 12.0),
        ),
    ),
    MechanismCase(
        key="small_supplier_procurement",
        real_case="procurement design where supplier diversity matters alongside cost savings",
        revenue_weight=0.40,
        welfare_weight=0.50,
        access_weight=1.00,
        strategic_risk_penalty=0.80,
        mechanisms=(
            MechanismOption("reverse_auction_low_bid", 110.0, 78.0, 32.0, 40.0),
            MechanismOption("quality_scoring_rule", 82.0, 125.0, 82.0, 8.0),
            MechanismOption("set_aside_lottery", 50.0, 90.0, 96.0, 12.0),
        ),
    ),
    MechanismCase(
        key="truthful_creator_market",
        real_case="creator marketplace allocation where strategic quality misreports degrade long-run fit",
        revenue_weight=0.80,
        welfare_weight=0.45,
        access_weight=0.15,
        strategic_risk_penalty=0.40,
        incentive_violation_penalty=6.00,
        mechanisms=(
            MechanismOption(
                "first_price_quality_bid",
                150.0,
                102.0,
                48.0,
                18.0,
                (
                    IncentiveCheck("low_quality", 0.45, 8.0, 20.0),
                    IncentiveCheck("mid_quality", 0.35, 13.0, 24.0),
                    IncentiveCheck("high_quality", 0.20, 19.0, 27.0),
                ),
            ),
            MechanismOption(
                "vcg_quality_score",
                116.0,
                135.0,
                72.0,
                4.0,
                (
                    IncentiveCheck("low_quality", 0.45, 15.0, 15.4),
                    IncentiveCheck("mid_quality", 0.35, 22.0, 22.3),
                    IncentiveCheck("high_quality", 0.20, 31.0, 31.2),
                ),
            ),
            MechanismOption(
                "manual_review_queue",
                88.0,
                126.0,
                90.0,
                6.0,
                (
                    IncentiveCheck("low_quality", 0.45, 13.0, 15.0),
                    IncentiveCheck("mid_quality", 0.35, 19.0, 21.0),
                    IncentiveCheck("high_quality", 0.20, 25.0, 27.5),
                ),
            ),
        ),
    ),
    MechanismCase(
        key="procurement_scoring_truthfulness",
        real_case="procurement scoring rule where vendors can exaggerate delivery reliability",
        revenue_weight=0.50,
        welfare_weight=0.65,
        access_weight=0.35,
        strategic_risk_penalty=0.70,
        incentive_violation_penalty=5.50,
        mechanisms=(
            MechanismOption(
                "lowest_bid_with_self_certification",
                240.0,
                94.0,
                45.0,
                36.0,
                (
                    IncentiveCheck("fragile_vendor", 0.30, 6.0, 21.0),
                    IncentiveCheck("standard_vendor", 0.50, 14.0, 26.0),
                    IncentiveCheck("reliable_vendor", 0.20, 22.0, 29.0),
                ),
            ),
            MechanismOption(
                "audited_score_auction",
                102.0,
                137.0,
                70.0,
                8.0,
                (
                    IncentiveCheck("fragile_vendor", 0.30, 11.0, 11.5),
                    IncentiveCheck("standard_vendor", 0.50, 20.0, 20.4),
                    IncentiveCheck("reliable_vendor", 0.20, 30.0, 30.2),
                ),
            ),
            MechanismOption(
                "access_weighted_lottery",
                76.0,
                120.0,
                94.0,
                10.0,
                (
                    IncentiveCheck("fragile_vendor", 0.30, 10.0, 13.0),
                    IncentiveCheck("standard_vendor", 0.50, 16.0, 18.0),
                    IncentiveCheck("reliable_vendor", 0.20, 24.0, 25.5),
                ),
            ),
        ),
    ),
]


REPEATED_CASES = [
    RepeatedMechanismCase(
        key="creator_market_retention",
        real_case="creator marketplace where aggressive ranking raises first-period revenue but drives creator exit",
        horizon=4,
        revenue_weight=0.90,
        welfare_weight=0.35,
        access_weight=0.20,
        strategic_risk_penalty=0.60,
        manipulation_penalty=8.00,
        mechanisms=(
            RepeatedMechanismOption("extractive_first_price", 160.0, 98.0, 45.0, 18.0, 0.72, 2.0, 2.20, 2.0),
            RepeatedMechanismOption("truthful_score_clock", 118.0, 132.0, 78.0, 4.0, 0.94, 0.6, 1.10, 4.0),
            RepeatedMechanismOption("manual_review_queue", 82.0, 126.0, 92.0, 7.0, 0.90, 0.8, 1.25, 9.0),
        ),
    ),
    RepeatedMechanismCase(
        key="procurement_reliability_repeated",
        real_case="repeated procurement where self-certification attracts low bids but vendor exaggeration compounds",
        horizon=5,
        revenue_weight=0.65,
        welfare_weight=0.60,
        access_weight=0.45,
        strategic_risk_penalty=0.70,
        manipulation_penalty=7.00,
        mechanisms=(
            RepeatedMechanismOption("self_certified_low_bid", 230.0, 90.0, 42.0, 32.0, 0.68, 3.0, 2.00, 1.0),
            RepeatedMechanismOption("audited_dynamic_score", 108.0, 140.0, 72.0, 7.0, 0.95, 0.7, 1.08, 5.0),
            RepeatedMechanismOption("supplier_rotation_lottery", 74.0, 118.0, 96.0, 10.0, 0.93, 0.8, 1.15, 6.0),
        ),
    ),
    RepeatedMechanismCase(
        key="public_grants_repeated_access",
        real_case="public grants platform where repeated participation and access matter more than immediate fees",
        horizon=4,
        revenue_weight=0.15,
        welfare_weight=0.55,
        access_weight=1.10,
        strategic_risk_penalty=0.50,
        manipulation_penalty=5.00,
        mechanisms=(
            RepeatedMechanismOption("pay_to_rank_fast", 150.0, 84.0, 38.0, 24.0, 0.70, 2.5, 1.80, 1.0),
            RepeatedMechanismOption("deliberative_score_rule", 70.0, 128.0, 82.0, 5.0, 0.96, 0.5, 1.10, 6.0),
            RepeatedMechanismOption("rotating_access_lottery", 42.0, 92.0, 98.0, 8.0, 0.97, 0.6, 1.05, 4.0),
        ),
    ),
    RepeatedMechanismCase(
        key="creator_feed_manipulation_growth",
        real_case="creator feed mechanism where engagement manipulation compounds over repeated allocation rounds",
        horizon=5,
        revenue_weight=0.75,
        welfare_weight=0.55,
        access_weight=0.35,
        strategic_risk_penalty=0.40,
        manipulation_penalty=10.00,
        mechanisms=(
            RepeatedMechanismOption("viral_rank_auction", 155.0, 120.0, 62.0, 10.0, 0.93, 1.8, 2.40, 2.0),
            RepeatedMechanismOption("audited_pacing_rule", 112.0, 132.0, 78.0, 5.0, 0.94, 0.5, 1.10, 5.0),
            RepeatedMechanismOption("community_lottery", 72.0, 112.0, 95.0, 6.0, 0.95, 0.4, 1.15, 5.0),
        ),
    ),
]


PARTICIPANT_RESPONSE_CASES = [
    ParticipantResponseMechanismCase(
        key="creator_subscription_exit",
        real_case="creator marketplace where high sponsor take causes creators to exit over repeated allocation rounds",
        horizon=5,
        revenue_weight=1.00,
        participant_value_weight=0.35,
        access_weight=25.00,
        gaming_penalty=6.00,
        mechanisms=(
            ParticipantResponseMechanismOption(
                "extractive_rank",
                42.0,
                55.0,
                0.45,
                10.0,
                0.920,
                0.0100,
                5.0,
                0.0250,
                2.0,
            ),
            ParticipantResponseMechanismOption(
                "balanced_pacing",
                24.0,
                75.0,
                0.78,
                9.4,
                0.960,
                0.0040,
                1.4,
                0.0080,
                3.5,
            ),
            ParticipantResponseMechanismOption(
                "community_pool",
                14.0,
                68.0,
                0.94,
                9.0,
                0.980,
                0.0020,
                0.8,
                0.0050,
                4.2,
            ),
        ),
    ),
    ParticipantResponseMechanismCase(
        key="public_grants_applicant_retention",
        real_case="public grants portal where extractive ranking rules discourage later applicant participation",
        horizon=4,
        revenue_weight=0.20,
        participant_value_weight=0.55,
        access_weight=45.00,
        gaming_penalty=5.00,
        mechanisms=(
            ParticipantResponseMechanismOption(
                "pay_to_rank",
                38.0,
                52.0,
                0.40,
                8.5,
                0.900,
                0.0110,
                4.5,
                0.0200,
                1.5,
            ),
            ParticipantResponseMechanismOption(
                "deliberative_score",
                18.0,
                78.0,
                0.82,
                8.2,
                0.970,
                0.0030,
                1.0,
                0.0060,
                3.8,
            ),
            ParticipantResponseMechanismOption(
                "rotating_lottery",
                8.0,
                64.0,
                0.97,
                8.0,
                0.985,
                0.0010,
                0.7,
                0.0040,
                3.3,
            ),
        ),
    ),
    ParticipantResponseMechanismCase(
        key="procurement_vendor_exit",
        real_case="repeat procurement market where self-certification extracts margin but pushes reliable vendors out",
        horizon=5,
        revenue_weight=0.70,
        participant_value_weight=0.50,
        access_weight=30.00,
        gaming_penalty=7.00,
        mechanisms=(
            ParticipantResponseMechanismOption(
                "self_certified_low_bid",
                50.0,
                50.0,
                0.42,
                7.0,
                0.880,
                0.0090,
                5.2,
                0.0300,
                1.0,
            ),
            ParticipantResponseMechanismOption(
                "audited_score",
                25.0,
                82.0,
                0.72,
                6.8,
                0.955,
                0.0030,
                1.2,
                0.0060,
                4.2,
            ),
            ParticipantResponseMechanismOption(
                "supplier_rotation",
                16.0,
                74.0,
                0.92,
                6.4,
                0.965,
                0.0020,
                1.0,
                0.0050,
                3.6,
            ),
        ),
    ),
    ParticipantResponseMechanismCase(
        key="creator_feed_trust_decay",
        real_case="creator feed rule where gaming pressure erodes participant trust over a longer program",
        horizon=6,
        revenue_weight=0.85,
        participant_value_weight=0.40,
        access_weight=20.00,
        gaming_penalty=8.00,
        mechanisms=(
            ParticipantResponseMechanismOption(
                "viral_auction",
                44.0,
                70.0,
                0.58,
                12.0,
                0.940,
                0.0060,
                4.8,
                0.0350,
                2.2,
            ),
            ParticipantResponseMechanismOption(
                "audited_pacing",
                28.0,
                86.0,
                0.76,
                11.2,
                0.960,
                0.0030,
                1.1,
                0.0070,
                5.0,
            ),
            ParticipantResponseMechanismOption(
                "community_lottery",
                15.0,
                72.0,
                0.95,
                10.8,
                0.975,
                0.0015,
                0.9,
                0.0050,
                4.5,
            ),
        ),
    ),
]


STRATEGIC_RESPONSE_CASES = [
    StrategicResponseMechanismCase(
        key="creator_market_peer_gaming",
        real_case="creator marketplace where open ranking makes strategic gaming contagious across creators",
        horizon=5,
        revenue_weight=1.00,
        participant_value_weight=0.40,
        access_weight=25.00,
        manipulation_penalty=8.00,
        mechanisms=(
            StrategicResponseMechanismOption(
                "open_rank_auction",
                1000.0,
                70.0,
                55.0,
                0.45,
                0.930,
                0.450,
                0.120,
                0.90,
                1.40,
                0.15,
                2.00,
                18.0,
                0.080,
                220.0,
            ),
            StrategicResponseMechanismOption(
                "audited_score_market",
                950.0,
                28.0,
                78.0,
                0.75,
                0.960,
                0.180,
                0.050,
                0.45,
                0.45,
                0.75,
                2.20,
                8.0,
                0.060,
                520.0,
            ),
            StrategicResponseMechanismOption(
                "community_rotation",
                900.0,
                16.0,
                72.0,
                0.95,
                0.975,
                0.100,
                0.040,
                0.25,
                0.25,
                0.55,
                2.00,
                5.0,
                0.050,
                430.0,
            ),
        ),
    ),
    StrategicResponseMechanismCase(
        key="procurement_bidder_contagion",
        real_case="repeat procurement where self-certification makes bid shading spread among vendors",
        horizon=5,
        revenue_weight=0.70,
        participant_value_weight=0.50,
        access_weight=30.00,
        manipulation_penalty=7.00,
        mechanisms=(
            StrategicResponseMechanismOption(
                "self_certified_low_bid",
                720.0,
                85.0,
                50.0,
                0.42,
                0.900,
                0.480,
                0.150,
                0.85,
                1.50,
                0.12,
                2.00,
                20.0,
                0.080,
                120.0,
            ),
            StrategicResponseMechanismOption(
                "audited_score_auction",
                690.0,
                28.0,
                84.0,
                0.72,
                0.955,
                0.160,
                0.060,
                0.40,
                0.40,
                0.80,
                2.40,
                7.0,
                0.060,
                470.0,
            ),
            StrategicResponseMechanismOption(
                "supplier_rotation_pool",
                650.0,
                17.0,
                76.0,
                0.92,
                0.965,
                0.100,
                0.040,
                0.22,
                0.20,
                0.55,
                2.10,
                5.0,
                0.050,
                390.0,
            ),
        ),
    ),
    StrategicResponseMechanismCase(
        key="grant_applicant_peer_effects",
        real_case="public grants portal where pay-to-rank induces copycat strategic applications",
        horizon=4,
        revenue_weight=0.20,
        participant_value_weight=0.55,
        access_weight=45.00,
        manipulation_penalty=5.00,
        mechanisms=(
            StrategicResponseMechanismOption(
                "pay_to_rank_fast",
                850.0,
                90.0,
                52.0,
                0.40,
                0.900,
                0.420,
                0.140,
                0.75,
                1.20,
                0.10,
                1.80,
                16.0,
                0.080,
                130.0,
            ),
            StrategicResponseMechanismOption(
                "audited_deliberation",
                820.0,
                18.0,
                80.0,
                0.82,
                0.970,
                0.140,
                0.050,
                0.32,
                0.30,
                0.70,
                2.00,
                6.0,
                0.060,
                420.0,
            ),
            StrategicResponseMechanismOption(
                "rotating_access_pool",
                790.0,
                8.0,
                66.0,
                0.97,
                0.980,
                0.080,
                0.040,
                0.20,
                0.15,
                0.45,
                1.80,
                4.0,
                0.050,
                350.0,
            ),
        ),
    ),
    StrategicResponseMechanismCase(
        key="creator_feed_copycat_manipulation",
        real_case="creator feed mechanism where visible gaming success causes copycat manipulation",
        horizon=6,
        revenue_weight=0.85,
        participant_value_weight=0.40,
        access_weight=20.00,
        manipulation_penalty=8.00,
        mechanisms=(
            StrategicResponseMechanismOption(
                "viral_rank_auction",
                1200.0,
                75.0,
                70.0,
                0.58,
                0.940,
                0.400,
                0.100,
                0.80,
                1.60,
                0.12,
                1.80,
                18.0,
                0.080,
                230.0,
            ),
            StrategicResponseMechanismOption(
                "audited_pacing_rule",
                1120.0,
                30.0,
                88.0,
                0.76,
                0.960,
                0.150,
                0.040,
                0.35,
                0.35,
                0.80,
                2.10,
                6.0,
                0.060,
                560.0,
            ),
            StrategicResponseMechanismOption(
                "community_lottery",
                1080.0,
                16.0,
                74.0,
                0.95,
                0.975,
                0.080,
                0.030,
                0.18,
                0.20,
                0.50,
                1.80,
                4.0,
                0.050,
                480.0,
            ),
        ),
    ),
]


INTERACTION_TRACE_CASES = [
    InteractionTraceMechanismCase(
        key="creator_market_trace",
        real_case="creator marketplace where visible ranking changes participation and strategic posting",
        forecast_horizon=5,
        revenue_weight=1.00,
        participant_value_weight=0.35,
        access_weight=30.00,
        manipulation_penalty=8.00,
        mechanisms=(
            InteractionTraceMechanismOption(
                "open_rank_auction",
                95.0,
                55.0,
                0.42,
                20.0,
                180.0,
                (
                    InteractionTracePoint(1, 1100.0, 0.08),
                    InteractionTracePoint(2, 1030.0, 0.17),
                    InteractionTracePoint(3, 930.0, 0.29),
                ),
            ),
            InteractionTraceMechanismOption(
                "audited_score_market",
                32.0,
                78.0,
                0.76,
                8.0,
                520.0,
                (
                    InteractionTracePoint(1, 1050.0, 0.06),
                    InteractionTracePoint(2, 1000.0, 0.08),
                    InteractionTracePoint(3, 940.0, 0.10),
                ),
            ),
            InteractionTraceMechanismOption(
                "community_rotation",
                18.0,
                72.0,
                0.94,
                5.0,
                430.0,
                (
                    InteractionTracePoint(1, 980.0, 0.05),
                    InteractionTracePoint(2, 960.0, 0.06),
                    InteractionTracePoint(3, 930.0, 0.07),
                ),
            ),
        ),
    ),
    InteractionTraceMechanismCase(
        key="procurement_bidder_trace",
        real_case="repeat procurement where self-certification causes bid shading to spread",
        forecast_horizon=5,
        revenue_weight=0.75,
        participant_value_weight=0.50,
        access_weight=30.00,
        manipulation_penalty=7.00,
        mechanisms=(
            InteractionTraceMechanismOption(
                "self_certified_low_bid",
                140.0,
                50.0,
                0.40,
                22.0,
                120.0,
                (
                    InteractionTracePoint(1, 740.0, 0.08),
                    InteractionTracePoint(2, 700.0, 0.16),
                    InteractionTracePoint(3, 650.0, 0.27),
                ),
            ),
            InteractionTraceMechanismOption(
                "audited_score_auction",
                34.0,
                84.0,
                0.72,
                7.0,
                470.0,
                (
                    InteractionTracePoint(1, 720.0, 0.05),
                    InteractionTracePoint(2, 695.0, 0.07),
                    InteractionTracePoint(3, 665.0, 0.09),
                ),
            ),
            InteractionTraceMechanismOption(
                "supplier_rotation_pool",
                20.0,
                76.0,
                0.92,
                5.0,
                390.0,
                (
                    InteractionTracePoint(1, 690.0, 0.04),
                    InteractionTracePoint(2, 675.0, 0.05),
                    InteractionTracePoint(3, 650.0, 0.06),
                ),
            ),
        ),
    ),
    InteractionTraceMechanismCase(
        key="grant_applicant_trace",
        real_case="public grants portal where observed pay-to-rank use changes later applicant quality",
        forecast_horizon=4,
        revenue_weight=0.20,
        participant_value_weight=0.55,
        access_weight=45.00,
        manipulation_penalty=5.00,
        mechanisms=(
            InteractionTraceMechanismOption(
                "pay_to_rank_fast",
                260.0,
                52.0,
                0.40,
                16.0,
                130.0,
                (
                    InteractionTracePoint(1, 850.0, 0.06),
                    InteractionTracePoint(2, 835.0, 0.13),
                    InteractionTracePoint(3, 805.0, 0.22),
                ),
            ),
            InteractionTraceMechanismOption(
                "audited_deliberation",
                22.0,
                80.0,
                0.82,
                6.0,
                420.0,
                (
                    InteractionTracePoint(1, 820.0, 0.05),
                    InteractionTracePoint(2, 795.0, 0.07),
                    InteractionTracePoint(3, 765.0, 0.09),
                ),
            ),
            InteractionTraceMechanismOption(
                "rotating_access_pool",
                9.0,
                66.0,
                0.97,
                4.0,
                350.0,
                (
                    InteractionTracePoint(1, 790.0, 0.04),
                    InteractionTracePoint(2, 775.0, 0.05),
                    InteractionTracePoint(3, 755.0, 0.06),
                ),
            ),
        ),
    ),
    InteractionTraceMechanismCase(
        key="creator_feed_trace",
        real_case="creator feed mechanism where observed gaming success induces copycat behavior",
        forecast_horizon=6,
        revenue_weight=0.85,
        participant_value_weight=0.40,
        access_weight=20.00,
        manipulation_penalty=8.00,
        mechanisms=(
            InteractionTraceMechanismOption(
                "viral_rank_auction",
                100.0,
                70.0,
                0.58,
                18.0,
                230.0,
                (
                    InteractionTracePoint(1, 1200.0, 0.07),
                    InteractionTracePoint(2, 1170.0, 0.15),
                    InteractionTracePoint(3, 1110.0, 0.26),
                ),
            ),
            InteractionTraceMechanismOption(
                "audited_pacing_rule",
                34.0,
                88.0,
                0.76,
                6.0,
                560.0,
                (
                    InteractionTracePoint(1, 1120.0, 0.04),
                    InteractionTracePoint(2, 1085.0, 0.06),
                    InteractionTracePoint(3, 1040.0, 0.08),
                ),
            ),
            InteractionTraceMechanismOption(
                "community_lottery",
                18.0,
                74.0,
                0.95,
                4.0,
                480.0,
                (
                    InteractionTracePoint(1, 1080.0, 0.03),
                    InteractionTracePoint(2, 1060.0, 0.04),
                    InteractionTracePoint(3, 1030.0, 0.05),
                ),
            ),
        ),
    ),
]


def incentive_violation(mechanism: MechanismOption) -> float:
    return sum(
        max(0.0, check.best_deviation_utility - check.truthful_utility) * max(0.0, check.probability)
        for check in mechanism.incentive_checks
    )


def mechanism_score(
    case: MechanismCase,
    mechanism: MechanismOption,
    *,
    risk_blind: bool = False,
    ic_blind: bool = False,
) -> float:
    risk_penalty = 0.0 if risk_blind else case.strategic_risk_penalty
    ic_penalty = 0.0 if ic_blind else case.incentive_violation_penalty
    return (
        case.revenue_weight * mechanism.revenue
        + case.welfare_weight * mechanism.welfare
        + case.access_weight * mechanism.access
        - risk_penalty * mechanism.strategic_risk
        - ic_penalty * incentive_violation(mechanism)
    )


def best_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism)).mechanism_id


def revenue_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.revenue).mechanism_id


def risk_blind_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism, risk_blind=True)).mechanism_id


def ic_blind_mechanism(case: MechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism_score(case, mechanism, ic_blind=True)).mechanism_id


def run_mechanism_game(agent: Agent, cases: list[MechanismCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[MechanismTrial] = []
    for case in cases:
        best = best_mechanism(case)
        revenue = revenue_mechanism(case)
        blind = risk_blind_mechanism(case)
        ic_blind = ic_blind_mechanism(case)
        response = agent.complete(MECHANISM_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            mechanism_score(case, mechanism_by_id[best]) - mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            MechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                risk_blind_mechanism=blind,
                ic_blind_mechanism=ic_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                incentive_violation=incentive_violation(mechanism_by_id[chosen]) if chosen is not None else None,
                raw_response=response,
            )
        )
    return summarize_mechanism_trials(agent.name, trials)


def repeated_mechanism_score(
    case: RepeatedMechanismCase,
    mechanism: RepeatedMechanismOption,
    *,
    one_period: bool = False,
    risk_blind: bool = False,
) -> float:
    horizon = 1 if one_period else case.horizon
    total = 0.0
    manipulation_penalty = 0.0 if risk_blind else case.manipulation_penalty
    strategic_risk_penalty = 0.0 if risk_blind else case.strategic_risk_penalty
    for period in range(horizon):
        retention = mechanism.retention_rate**period
        manipulation = mechanism.manipulation_load * (mechanism.manipulation_growth**period)
        total += (
            case.revenue_weight * mechanism.first_period_revenue * retention
            + case.welfare_weight * mechanism.welfare * retention
            + case.access_weight * mechanism.access * retention
            - strategic_risk_penalty * mechanism.strategic_risk
            - manipulation_penalty * manipulation
            - mechanism.review_cost
        )
    return total


def best_repeated_mechanism(case: RepeatedMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: repeated_mechanism_score(case, mechanism),
    ).mechanism_id


def revenue_repeated_mechanism(case: RepeatedMechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.first_period_revenue).mechanism_id


def one_period_mechanism(case: RepeatedMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: repeated_mechanism_score(case, mechanism, one_period=True),
    ).mechanism_id


def risk_blind_repeated_mechanism(case: RepeatedMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: repeated_mechanism_score(case, mechanism, risk_blind=True),
    ).mechanism_id


def participant_response_mechanism_score(
    case: ParticipantResponseMechanismCase,
    mechanism: ParticipantResponseMechanismOption,
    *,
    one_period: bool = False,
    response_blind: bool = False,
) -> float:
    participants = mechanism.starting_participants
    total = 0.0
    horizon = 1 if one_period else case.horizon
    for period in range(horizon):
        gaming_pressure = mechanism.gaming_pressure * (1.0 + mechanism.trust_decay * period)
        total += (
            participants
            * (
                case.revenue_weight * mechanism.sponsor_take
                + case.participant_value_weight * mechanism.participant_value
                + case.access_weight * mechanism.access_quality
                - case.gaming_penalty * gaming_pressure
            )
            - mechanism.review_cost
        )
        if response_blind:
            participants = mechanism.starting_participants
            continue
        stay_rate = _clamp_participant_stay(
            mechanism.base_stay_rate
            - mechanism.take_exit_sensitivity * mechanism.sponsor_take
            - mechanism.trust_decay * mechanism.gaming_pressure * period
        )
        participants *= stay_rate
    return total


def best_participant_response_mechanism(case: ParticipantResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: participant_response_mechanism_score(case, mechanism),
    ).mechanism_id


def revenue_participant_response_mechanism(case: ParticipantResponseMechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.sponsor_take).mechanism_id


def one_period_participant_response_mechanism(case: ParticipantResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: participant_response_mechanism_score(case, mechanism, one_period=True),
    ).mechanism_id


def response_blind_participant_response_mechanism(case: ParticipantResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: participant_response_mechanism_score(case, mechanism, response_blind=True),
    ).mechanism_id


def _clamp_participant_stay(value: float) -> float:
    return min(0.99, max(0.05, value))


def strategic_response_mechanism_score(
    case: StrategicResponseMechanismCase,
    mechanism: StrategicResponseMechanismOption,
    *,
    one_period: bool = False,
    response_blind: bool = False,
) -> float:
    participants = mechanism.participant_count
    strategic_share = mechanism.initial_strategic_share
    total = 0.0
    horizon = 1 if one_period else case.horizon
    for _period in range(horizon):
        total += (
            participants
            * (
                case.revenue_weight * mechanism.sponsor_take
                + case.participant_value_weight * mechanism.participant_value
                + case.access_weight * mechanism.access_quality
                - case.manipulation_penalty * mechanism.manipulation_harm * strategic_share
            )
            - mechanism.review_cost
        )
        if not response_blind:
            payoff_advantage = (
                mechanism.strategic_gain
                + mechanism.peer_contagion * strategic_share
                - mechanism.audit_strength * mechanism.detection_cost
            )
            strategic_share = _clamp_strategic_share(
                strategic_share + mechanism.response_update_rate * payoff_advantage
            )
        stay_rate = _clamp_participant_stay(
            mechanism.base_stay_rate - mechanism.exit_sensitivity * strategic_share
        )
        participants *= stay_rate
    return total


def best_strategic_response_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: strategic_response_mechanism_score(case, mechanism),
    ).mechanism_id


def revenue_strategic_response_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.sponsor_take).mechanism_id


def one_period_strategic_response_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: strategic_response_mechanism_score(case, mechanism, one_period=True),
    ).mechanism_id


def response_blind_strategic_response_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: strategic_response_mechanism_score(case, mechanism, response_blind=True),
    ).mechanism_id


def _clamp_strategic_share(value: float) -> float:
    return min(0.95, max(0.0, value))


def strategic_equilibrium_share(
    mechanism: StrategicResponseMechanismOption,
    *,
    response_blind: bool = False,
) -> float:
    if response_blind:
        return mechanism.initial_strategic_share
    strategic_share = mechanism.initial_strategic_share
    for _iteration in range(25):
        payoff_advantage = (
            mechanism.strategic_gain
            + mechanism.peer_contagion * strategic_share
            - mechanism.audit_strength * mechanism.detection_cost
        )
        strategic_share = _clamp_strategic_share(
            strategic_share + mechanism.response_update_rate * payoff_advantage
        )
    return strategic_share


def strategic_equilibrium_mechanism_score(
    case: StrategicResponseMechanismCase,
    mechanism: StrategicResponseMechanismOption,
    *,
    one_period: bool = False,
    response_blind: bool = False,
) -> float:
    strategic_share = strategic_equilibrium_share(mechanism, response_blind=response_blind)
    participants = mechanism.participant_count
    total = 0.0
    horizon = 1 if one_period else case.horizon
    for _period in range(horizon):
        total += (
            participants
            * (
                case.revenue_weight * mechanism.sponsor_take
                + case.participant_value_weight * mechanism.participant_value
                + case.access_weight * mechanism.access_quality
                - case.manipulation_penalty * mechanism.manipulation_harm * strategic_share
            )
            - mechanism.review_cost
        )
        stay_rate = _clamp_participant_stay(
            mechanism.base_stay_rate - mechanism.exit_sensitivity * strategic_share
        )
        participants *= stay_rate
    return total


def best_strategic_equilibrium_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: strategic_equilibrium_mechanism_score(case, mechanism),
    ).mechanism_id


def one_period_strategic_equilibrium_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: strategic_equilibrium_mechanism_score(case, mechanism, one_period=True),
    ).mechanism_id


def response_blind_strategic_equilibrium_mechanism(case: StrategicResponseMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: strategic_equilibrium_mechanism_score(case, mechanism, response_blind=True),
    ).mechanism_id


def interaction_trace_mechanism_score(
    case: InteractionTraceMechanismCase,
    mechanism: InteractionTraceMechanismOption,
    *,
    one_period: bool = False,
    trace_blind: bool = False,
) -> float:
    horizon = 1 if one_period else case.forecast_horizon
    if trace_blind:
        participants = mechanism.trace[0].active_participants
        strategic_share = mechanism.trace[0].strategic_share
        participant_ratio = 1.0
        strategic_delta = 0.0
    else:
        participants = mechanism.trace[-1].active_participants
        strategic_share = mechanism.trace[-1].strategic_share
        participant_ratio = _mean_trace_participant_ratio(mechanism.trace)
        strategic_delta = _mean_trace_strategic_delta(mechanism.trace)
    total = 0.0
    for _period in range(horizon):
        total += (
            participants
            * (
                case.revenue_weight * mechanism.sponsor_take
                + case.participant_value_weight * mechanism.participant_value
                + case.access_weight * mechanism.access_quality
                - case.manipulation_penalty * mechanism.manipulation_harm * strategic_share
            )
            - mechanism.review_cost
        )
        participants *= participant_ratio
        strategic_share = _clamp_strategic_share(strategic_share + strategic_delta)
    return total


def _mean_trace_participant_ratio(trace: tuple[InteractionTracePoint, ...]) -> float:
    ratios = [
        later.active_participants / earlier.active_participants
        for earlier, later in zip(trace, trace[1:])
        if earlier.active_participants > 0
    ]
    return mean(ratios) if ratios else 1.0


def _mean_trace_strategic_delta(trace: tuple[InteractionTracePoint, ...]) -> float:
    deltas = [
        later.strategic_share - earlier.strategic_share
        for earlier, later in zip(trace, trace[1:])
    ]
    return mean(deltas) if deltas else 0.0


def best_interaction_trace_mechanism(case: InteractionTraceMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: interaction_trace_mechanism_score(case, mechanism),
    ).mechanism_id


def revenue_interaction_trace_mechanism(case: InteractionTraceMechanismCase) -> str:
    return max(case.mechanisms, key=lambda mechanism: mechanism.sponsor_take).mechanism_id


def one_period_interaction_trace_mechanism(case: InteractionTraceMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: interaction_trace_mechanism_score(case, mechanism, one_period=True),
    ).mechanism_id


def trace_blind_interaction_trace_mechanism(case: InteractionTraceMechanismCase) -> str:
    return max(
        case.mechanisms,
        key=lambda mechanism: interaction_trace_mechanism_score(case, mechanism, trace_blind=True),
    ).mechanism_id


def run_mechanism_repeated_game(
    agent: Agent,
    cases: list[RepeatedMechanismCase] | None = None,
) -> dict:
    return _run_repeated_mechanism_game(
        agent,
        cases,
        prompt_fn=_repeated_prompt,
        task_name="mechanism_repeated",
    )


def run_mechanism_repeated_natural_game(
    agent: Agent,
    cases: list[RepeatedMechanismCase] | None = None,
) -> dict:
    return _run_repeated_mechanism_game(
        agent,
        cases,
        prompt_fn=_repeated_natural_prompt,
        task_name="mechanism_repeated_natural",
    )


def _run_repeated_mechanism_game(
    agent: Agent,
    cases: list[RepeatedMechanismCase] | None,
    *,
    prompt_fn: Callable[[RepeatedMechanismCase], str],
    task_name: str,
) -> dict:
    cases = cases or REPEATED_CASES
    trials: list[RepeatedMechanismTrial] = []
    for case in cases:
        best = best_repeated_mechanism(case)
        revenue = revenue_repeated_mechanism(case)
        one_period = one_period_mechanism(case)
        risk_blind = risk_blind_repeated_mechanism(case)
        response = agent.complete(MECHANISM_REPEATED_SYSTEM, prompt_fn(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            repeated_mechanism_score(case, mechanism_by_id[best])
            - repeated_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            RepeatedMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                risk_blind_mechanism=risk_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_repeated_mechanism_trials(agent.name, trials, task_name=task_name)


def run_mechanism_participant_response_game(
    agent: Agent,
    cases: list[ParticipantResponseMechanismCase] | None = None,
) -> dict:
    cases = cases or PARTICIPANT_RESPONSE_CASES
    trials: list[ParticipantResponseMechanismTrial] = []
    for case in cases:
        best = best_participant_response_mechanism(case)
        revenue = revenue_participant_response_mechanism(case)
        one_period = one_period_participant_response_mechanism(case)
        response_blind = response_blind_participant_response_mechanism(case)
        response = agent.complete(MECHANISM_PARTICIPANT_RESPONSE_SYSTEM, _participant_response_prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            participant_response_mechanism_score(case, mechanism_by_id[best])
            - participant_response_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            ParticipantResponseMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                response_blind_mechanism=response_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_participant_response_mechanism_trials(agent.name, trials)


def run_mechanism_elasticity_inference_game(
    agent: Agent,
    cases: list[ParticipantResponseMechanismCase] | None = None,
) -> dict:
    cases = cases or PARTICIPANT_RESPONSE_CASES
    trials: list[ParticipantResponseMechanismTrial] = []
    for case in cases:
        best = best_participant_response_mechanism(case)
        revenue = revenue_participant_response_mechanism(case)
        one_period = one_period_participant_response_mechanism(case)
        response_blind = response_blind_participant_response_mechanism(case)
        response = agent.complete(MECHANISM_PARTICIPANT_RESPONSE_SYSTEM, _participant_elasticity_prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            participant_response_mechanism_score(case, mechanism_by_id[best])
            - participant_response_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            ParticipantResponseMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                response_blind_mechanism=response_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_participant_response_mechanism_trials(
        agent.name,
        trials,
        task_name="mechanism_elasticity_inference",
    )


def run_mechanism_strategic_response_game(
    agent: Agent,
    cases: list[StrategicResponseMechanismCase] | None = None,
) -> dict:
    cases = cases or STRATEGIC_RESPONSE_CASES
    trials: list[StrategicResponseMechanismTrial] = []
    for case in cases:
        best = best_strategic_response_mechanism(case)
        revenue = revenue_strategic_response_mechanism(case)
        one_period = one_period_strategic_response_mechanism(case)
        response_blind = response_blind_strategic_response_mechanism(case)
        response = agent.complete(MECHANISM_STRATEGIC_RESPONSE_SYSTEM, _strategic_response_prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            strategic_response_mechanism_score(case, mechanism_by_id[best])
            - strategic_response_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            StrategicResponseMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                response_blind_mechanism=response_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_strategic_response_mechanism_trials(agent.name, trials)


def run_mechanism_strategic_equilibrium_game(
    agent: Agent,
    cases: list[StrategicResponseMechanismCase] | None = None,
) -> dict:
    cases = cases or STRATEGIC_RESPONSE_CASES
    trials: list[StrategicResponseMechanismTrial] = []
    for case in cases:
        best = best_strategic_equilibrium_mechanism(case)
        revenue = revenue_strategic_response_mechanism(case)
        one_period = one_period_strategic_equilibrium_mechanism(case)
        response_blind = response_blind_strategic_equilibrium_mechanism(case)
        response = agent.complete(MECHANISM_STRATEGIC_EQUILIBRIUM_SYSTEM, _strategic_equilibrium_prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            strategic_equilibrium_mechanism_score(case, mechanism_by_id[best])
            - strategic_equilibrium_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            StrategicResponseMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                response_blind_mechanism=response_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_strategic_response_mechanism_trials(
        agent.name,
        trials,
        task_name="mechanism_strategic_equilibrium",
    )


def run_mechanism_interaction_trace_game(
    agent: Agent,
    cases: list[InteractionTraceMechanismCase] | None = None,
) -> dict:
    cases = cases or INTERACTION_TRACE_CASES
    trials: list[InteractionTraceMechanismTrial] = []
    for case in cases:
        best = best_interaction_trace_mechanism(case)
        revenue = revenue_interaction_trace_mechanism(case)
        one_period = one_period_interaction_trace_mechanism(case)
        trace_blind = trace_blind_interaction_trace_mechanism(case)
        response = agent.complete(MECHANISM_INTERACTION_TRACE_SYSTEM, _interaction_trace_prompt(case))
        chosen = parse_token("FINAL_MECHANISM", response)
        mechanism_by_id = {mechanism.mechanism_id: mechanism for mechanism in case.mechanisms}
        chosen = chosen if chosen in mechanism_by_id else None
        regret = (
            interaction_trace_mechanism_score(case, mechanism_by_id[best])
            - interaction_trace_mechanism_score(case, mechanism_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            InteractionTraceMechanismTrial(
                case=case,
                best_mechanism=best,
                revenue_mechanism=revenue,
                one_period_mechanism=one_period,
                trace_blind_mechanism=trace_blind,
                chosen_mechanism=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_interaction_trace_mechanism_trials(agent.name, trials)


def summarize_mechanism_trials(agent_name: str, trials: list[MechanismTrial]) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    risk_missable = [trial for trial in trials if trial.risk_blind_mechanism != trial.best_mechanism]
    ic_missable = [trial for trial in trials if trial.ic_blind_mechanism != trial.best_mechanism]
    revenue_misses = sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
    risk_misses = sum(trial.chosen_mechanism == trial.risk_blind_mechanism for trial in risk_missable)
    ic_misses = sum(trial.chosen_mechanism == trial.ic_blind_mechanism for trial in ic_missable)
    violations = [trial.incentive_violation for trial in trials if trial.incentive_violation is not None]
    return {
        "task": "mechanism",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": revenue_misses / len(revenue_missable) if revenue_missable else 0.0,
        "risk_blind_miss_rate": risk_misses / len(risk_missable) if risk_missable else 0.0,
        "ic_blind_miss_rate": ic_misses / len(ic_missable) if ic_missable else 0.0,
        "mean_incentive_violation": mean(violations),
        "trials": [_trial_json(trial) for trial in trials],
    }


def summarize_repeated_mechanism_trials(
    agent_name: str,
    trials: list[RepeatedMechanismTrial],
    *,
    task_name: str = "mechanism_repeated",
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    one_period_missable = [
        trial for trial in trials if trial.one_period_mechanism != trial.best_mechanism
    ]
    risk_missable = [trial for trial in trials if trial.risk_blind_mechanism != trial.best_mechanism]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": (
            sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
            / len(revenue_missable)
            if revenue_missable
            else 0.0
        ),
        "one_period_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.one_period_mechanism
                for trial in one_period_missable
            )
            / len(one_period_missable)
            if one_period_missable
            else 0.0
        ),
        "risk_blind_miss_rate": (
            sum(trial.chosen_mechanism == trial.risk_blind_mechanism for trial in risk_missable)
            / len(risk_missable)
            if risk_missable
            else 0.0
        ),
        "trials": [_repeated_trial_json(trial) for trial in trials],
    }


def summarize_participant_response_mechanism_trials(
    agent_name: str,
    trials: list[ParticipantResponseMechanismTrial],
    *,
    task_name: str = "mechanism_participant_response",
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    one_period_missable = [
        trial for trial in trials if trial.one_period_mechanism != trial.best_mechanism
    ]
    response_blind_missable = [
        trial for trial in trials if trial.response_blind_mechanism != trial.best_mechanism
    ]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": (
            sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
            / len(revenue_missable)
            if revenue_missable
            else 0.0
        ),
        "one_period_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.one_period_mechanism
                for trial in one_period_missable
            )
            / len(one_period_missable)
            if one_period_missable
            else 0.0
        ),
        "response_blind_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.response_blind_mechanism
                for trial in response_blind_missable
            )
            / len(response_blind_missable)
            if response_blind_missable
            else 0.0
        ),
        "trials": [_participant_response_trial_json(trial) for trial in trials],
    }


def summarize_strategic_response_mechanism_trials(
    agent_name: str,
    trials: list[StrategicResponseMechanismTrial],
    *,
    task_name: str = "mechanism_strategic_response",
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    one_period_missable = [
        trial for trial in trials if trial.one_period_mechanism != trial.best_mechanism
    ]
    response_blind_missable = [
        trial for trial in trials if trial.response_blind_mechanism != trial.best_mechanism
    ]
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": (
            sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
            / len(revenue_missable)
            if revenue_missable
            else 0.0
        ),
        "one_period_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.one_period_mechanism
                for trial in one_period_missable
            )
            / len(one_period_missable)
            if one_period_missable
            else 0.0
        ),
        "response_blind_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.response_blind_mechanism
                for trial in response_blind_missable
            )
            / len(response_blind_missable)
            if response_blind_missable
            else 0.0
        ),
        "trials": [_strategic_response_trial_json(trial) for trial in trials],
    }


def summarize_interaction_trace_mechanism_trials(
    agent_name: str,
    trials: list[InteractionTraceMechanismTrial],
) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    revenue_missable = [trial for trial in trials if trial.revenue_mechanism != trial.best_mechanism]
    one_period_missable = [
        trial for trial in trials if trial.one_period_mechanism != trial.best_mechanism
    ]
    trace_blind_missable = [
        trial for trial in trials if trial.trace_blind_mechanism != trial.best_mechanism
    ]
    return {
        "task": "mechanism_interaction_trace",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "revenue_default_miss_rate": (
            sum(trial.chosen_mechanism == trial.revenue_mechanism for trial in revenue_missable)
            / len(revenue_missable)
            if revenue_missable
            else 0.0
        ),
        "one_period_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.one_period_mechanism
                for trial in one_period_missable
            )
            / len(one_period_missable)
            if one_period_missable
            else 0.0
        ),
        "trace_blind_miss_rate": (
            sum(
                trial.chosen_mechanism == trial.trace_blind_mechanism
                for trial in trace_blind_missable
            )
            / len(trace_blind_missable)
            if trace_blind_missable
            else 0.0
        ),
        "trials": [_interaction_trace_trial_json(trial) for trial in trials],
    }


def _prompt(case: MechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"welfare_weight={case.welfare_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"strategic_risk_penalty={case.strategic_risk_penalty:.4f}",
        f"incentive_violation_penalty={case.incentive_violation_penalty:.4f}",
        "Outcomes below account for expected strategic response; incentive checks expose residual misreport gains.",
        "Mechanisms:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"revenue={mechanism.revenue:.2f} "
            f"welfare={mechanism.welfare:.2f} "
            f"access={mechanism.access:.2f} "
            f"strategic_risk={mechanism.strategic_risk:.2f}"
        )
        for check in mechanism.incentive_checks:
            lines.append(
                "    "
                f"ic_check mechanism_id={mechanism.mechanism_id} "
                f"type_id={check.type_id} "
                f"probability={check.probability:.4f} "
                f"truthful_utility={check.truthful_utility:.2f} "
                f"best_deviation_utility={check.best_deviation_utility:.2f}"
            )
    lines.append(
        "Choose the mechanism with the best configured score: "
        "revenue_weight*revenue + welfare_weight*welfare + access_weight*access "
        "- strategic_risk_penalty*strategic_risk "
        "- incentive_violation_penalty*expected_positive_misreport_gain."
    )
    return "\n".join(lines)


def _repeated_prompt(case: RepeatedMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"welfare_weight={case.welfare_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"strategic_risk_penalty={case.strategic_risk_penalty:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Mechanisms:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"first_period_revenue={mechanism.first_period_revenue:.2f} "
            f"welfare={mechanism.welfare:.2f} "
            f"access={mechanism.access:.2f} "
            f"strategic_risk={mechanism.strategic_risk:.2f} "
            f"retention_rate={mechanism.retention_rate:.4f} "
            f"manipulation_load={mechanism.manipulation_load:.2f} "
            f"manipulation_growth={mechanism.manipulation_growth:.4f} "
            f"review_cost={mechanism.review_cost:.2f}"
        )
    lines.append(
        "For each period, retained revenue/welfare/access scale by retention_rate^(period-1), "
        "while manipulation load scales by manipulation_growth^(period-1)."
    )
    lines.append(
        "Choose the mechanism with the highest total configured score across the full horizon, "
        "not just the highest first-period revenue."
    )
    return "\n".join(lines)


def _repeated_natural_prompt(case: RepeatedMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"welfare_weight={case.welfare_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"strategic_risk_penalty={case.strategic_risk_penalty:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Pilot outcomes from candidate rules:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"option_id={mechanism.mechanism_id} "
            f"initial_take={mechanism.first_period_revenue:.2f} "
            f"participant_value={mechanism.welfare:.2f} "
            f"access_reach={mechanism.access:.2f} "
            f"governance_risk={mechanism.strategic_risk:.2f} "
            f"participant_retention={mechanism.retention_rate:.4f} "
            f"gaming_pressure={mechanism.manipulation_load:.2f} "
            f"gaming_acceleration={mechanism.manipulation_growth:.4f} "
            f"oversight_cost={mechanism.review_cost:.2f}"
        )
    lines.extend(
        [
            "Higher participant retention keeps later-round value available.",
            "Gaming pressure that accelerates over repeated use erodes the principal's value.",
            "Pick the rule that should govern the whole repeated program, not the rule "
            "with the largest launch-period take.",
        ]
    )
    return "\n".join(lines)


def _participant_response_prompt(case: ParticipantResponseMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"participant_value_weight={case.participant_value_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"gaming_penalty={case.gaming_penalty:.4f}",
        "Candidate program rules:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"policy_id={mechanism.mechanism_id} "
            f"sponsor_take={mechanism.sponsor_take:.2f} "
            f"participant_value={mechanism.participant_value:.2f} "
            f"access_quality={mechanism.access_quality:.4f} "
            f"starting_participants={mechanism.starting_participants:.2f} "
            f"base_stay_rate={mechanism.base_stay_rate:.4f} "
            f"take_exit_sensitivity={mechanism.take_exit_sensitivity:.4f} "
            f"gaming_pressure={mechanism.gaming_pressure:.2f} "
            f"trust_decay={mechanism.trust_decay:.4f} "
            f"review_cost={mechanism.review_cost:.2f}"
        )
    lines.extend(
        [
            "Simulate the participant pool over the full program.",
            "Each period earns weighted sponsor take, participant value, and access quality "
            "from the currently active participants.",
            "Participant stay rate falls when sponsor take is high and when gaming pressure "
            "accumulates over time.",
            "Pick the rule with the best total program value, not the rule with the highest "
            "launch-period take or the rule that assumes participants never leave.",
        ]
    )
    return "\n".join(lines)


def _participant_elasticity_prompt(case: ParticipantResponseMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"participant_value_weight={case.participant_value_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"gaming_penalty={case.gaming_penalty:.4f}",
        "Pilot observations from candidate program rules:",
    ]
    for mechanism in case.mechanisms:
        low_take = 10.0
        high_take = 30.0
        low_stay = _clamp_participant_stay(
            mechanism.base_stay_rate - mechanism.take_exit_sensitivity * low_take
        )
        high_stay = _clamp_participant_stay(
            mechanism.base_stay_rate - mechanism.take_exit_sensitivity * high_take
        )
        round3_extra_exit = 2.0 * mechanism.trust_decay * mechanism.gaming_pressure
        lines.append(
            "  "
            f"policy_id={mechanism.mechanism_id} "
            f"sponsor_take={mechanism.sponsor_take:.2f} "
            f"participant_value={mechanism.participant_value:.2f} "
            f"access_quality={mechanism.access_quality:.4f} "
            f"starting_participants={mechanism.starting_participants:.2f} "
            f"gaming_pressure={mechanism.gaming_pressure:.2f} "
            f"review_cost={mechanism.review_cost:.2f} "
            f"pilot_low_take={low_take:.2f} "
            f"pilot_low_stay={low_stay:.4f} "
            f"pilot_high_take={high_take:.2f} "
            f"pilot_high_stay={high_stay:.4f} "
            f"round3_extra_exit={round3_extra_exit:.4f}"
        )
    lines.extend(
        [
            "Infer each rule's fee-response from the two pilot stay shares.",
            "Use the round-3 extra-exit observation as the two-period accumulated "
            "gaming-pressure effect.",
            "Simulate active participants over the full horizon before comparing rules.",
            "Pick the rule with the best total program value, not the rule with the highest "
            "launch-period take or the rule that assumes the initial pool stays fixed.",
        ]
    )
    return "\n".join(lines)


def _strategic_response_prompt(case: StrategicResponseMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"participant_value_weight={case.participant_value_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Candidate mechanisms with strategic participant response:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"participant_count={mechanism.participant_count:.2f} "
            f"sponsor_take={mechanism.sponsor_take:.2f} "
            f"participant_value={mechanism.participant_value:.2f} "
            f"access_quality={mechanism.access_quality:.4f} "
            f"base_stay_rate={mechanism.base_stay_rate:.4f} "
            f"exit_sensitivity={mechanism.exit_sensitivity:.4f} "
            f"initial_strategic_share={mechanism.initial_strategic_share:.4f} "
            f"strategic_gain={mechanism.strategic_gain:.4f} "
            f"peer_contagion={mechanism.peer_contagion:.4f} "
            f"audit_strength={mechanism.audit_strength:.4f} "
            f"detection_cost={mechanism.detection_cost:.4f} "
            f"manipulation_harm={mechanism.manipulation_harm:.2f} "
            f"response_update_rate={mechanism.response_update_rate:.4f} "
            f"review_cost={mechanism.review_cost:.2f}"
        )
    lines.extend(
        [
            "Simulate the strategic participant share over the full horizon.",
            "Strategic behavior becomes more attractive when private gain and peer contagion "
            "exceed expected audit deterrence.",
            "Higher strategic share creates manipulation harm and lowers later participant retention.",
            "Pick the mechanism with the best total program value, not the mechanism with the "
            "largest launch-period take or a fixed initial strategic-share assumption.",
        ]
    )
    return "\n".join(lines)


def _strategic_equilibrium_prompt(case: StrategicResponseMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"horizon={case.horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"participant_value_weight={case.participant_value_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Candidate mechanisms with self-consistent strategic response:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"participant_count={mechanism.participant_count:.2f} "
            f"sponsor_take={mechanism.sponsor_take:.2f} "
            f"participant_value={mechanism.participant_value:.2f} "
            f"access_quality={mechanism.access_quality:.4f} "
            f"base_stay_rate={mechanism.base_stay_rate:.4f} "
            f"exit_sensitivity={mechanism.exit_sensitivity:.4f} "
            f"initial_strategic_share={mechanism.initial_strategic_share:.4f} "
            f"strategic_gain={mechanism.strategic_gain:.4f} "
            f"peer_contagion={mechanism.peer_contagion:.4f} "
            f"audit_strength={mechanism.audit_strength:.4f} "
            f"detection_cost={mechanism.detection_cost:.4f} "
            f"manipulation_harm={mechanism.manipulation_harm:.2f} "
            f"response_update_rate={mechanism.response_update_rate:.4f} "
            f"review_cost={mechanism.review_cost:.2f}"
        )
    lines.extend(
        [
            "First find the stable strategic-participant share implied by private gain, "
            "peer contagion, audit strength, detection cost, and response update rate.",
            "Then value the repeated program using that self-consistent strategic share.",
            "Higher equilibrium strategic share creates manipulation harm and lower participant retention.",
            "Pick the mechanism with the best total program value, not the mechanism that looks best "
            "at the initial strategic share.",
        ]
    )
    return "\n".join(lines)


def _interaction_trace_prompt(case: InteractionTraceMechanismCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"future_rounds_to_score={case.forecast_horizon}",
        f"revenue_weight={case.revenue_weight:.4f}",
        f"participant_value_weight={case.participant_value_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"manipulation_penalty={case.manipulation_penalty:.4f}",
        "Candidate mechanisms with observed pilot interaction traces:",
    ]
    for mechanism in case.mechanisms:
        lines.append(
            "  "
            f"mechanism_id={mechanism.mechanism_id} "
            f"sponsor_take={mechanism.sponsor_take:.2f} "
            f"participant_value={mechanism.participant_value:.2f} "
            f"access_quality={mechanism.access_quality:.4f} "
            f"manipulation_harm={mechanism.manipulation_harm:.2f} "
            f"review_cost={mechanism.review_cost:.2f}"
        )
        for point in mechanism.trace:
            lines.append(
                "    "
                f"trace mechanism_id={mechanism.mechanism_id} "
                f"round={point.round_id} "
                f"active_participants={point.active_participants:.2f} "
                f"strategic_share={point.strategic_share:.4f}"
            )
    lines.extend(
        [
            "Use the observed round-to-round interaction trace to project active participants "
            "and strategic share over the future scored rounds.",
            "Each future round earns weighted sponsor take, participant value, and access quality "
            "from active participants, then subtracts manipulation harm and review cost.",
            "Pick the mechanism with the best future program value, not the largest current take "
            "or the rule that ignores the trace trend.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: MechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _repeated_trial_json(trial: RepeatedMechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _participant_response_trial_json(trial: ParticipantResponseMechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _strategic_response_trial_json(trial: StrategicResponseMechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data


def _interaction_trace_trial_json(trial: InteractionTraceMechanismTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
