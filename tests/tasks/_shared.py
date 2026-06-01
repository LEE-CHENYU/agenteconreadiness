"""Shared fixtures for the split task tests (was the monolithic test_tasks.py).

Imports + helper agent classes used across the per-cluster task test modules.
"""

import unittest
from types import SimpleNamespace

from aeread_lab.models import (
    OfflineAgent,
    OpenAIResponsesAgent,
    _extract_openai_response_text,
    resolve_openai_model,
)
from aeread_lab.reporting import (
    comparison_table,
    format_stability,
    format_stability_sweep,
    parse_rate,
    rank_rows,
    stability_sweep_case_table,
)
from aeread_lab.runner import run_stability_probe, run_stability_sweep, run_sweep, run_tasks
from aeread_lab.tasks.adversarial import run_scam_arena
from aeread_lab.tasks.alignment_tax import DEFAULT_CASES as ALIGNMENT_CASES
from aeread_lab.tasks.alignment_tax import _prompt as alignment_tax_prompt
from aeread_lab.tasks.alignment_tax import run_alignment_tax_game
from aeread_lab.tasks.ambiguity import DEFAULT_CASES as AMBIGUITY_CASES
from aeread_lab.tasks.ambiguity import _prompt as ambiguity_prompt
from aeread_lab.tasks.ambiguity import run_ambiguity_game
from aeread_lab.tasks.auction import run_auction_game
from aeread_lab.tasks.bargaining import run_bargaining_game
from aeread_lab.tasks.belief_bargaining import DEFAULT_CASES as BELIEF_BARGAINING_CASES
from aeread_lab.tasks.belief_bargaining import INTERACTION_CASES as BELIEF_INTERACTION_CASES
from aeread_lab.tasks.belief_bargaining import _interaction_prompt as belief_interaction_prompt
from aeread_lab.tasks.belief_bargaining import _prompt as belief_bargaining_prompt
from aeread_lab.tasks.belief_bargaining import run_belief_bargaining_game
from aeread_lab.tasks.belief_bargaining import run_belief_bargaining_interaction_game
from aeread_lab.tasks.common_value import DEFAULT_CASES as COMMON_VALUE_CASES
from aeread_lab.tasks.common_value import _prompt as common_value_prompt
from aeread_lab.tasks.common_value import run_common_value_game
from aeread_lab.tasks.experiment_design import DEFAULT_CASES as EXPERIMENT_CASES
from aeread_lab.tasks.experiment_design import _prompt as experiment_prompt
from aeread_lab.tasks.experiment_design import run_experiment_design_game
from aeread_lab.tasks.exploration import DEFAULT_CASES as EXPLORATION_CASES
from aeread_lab.tasks.exploration import _prompt as exploration_prompt
from aeread_lab.tasks.exploration import run_exploration_game
from aeread_lab.tasks.forecast_calibration import AGGREGATE_CASES as FORECAST_AGGREGATE_CASES
from aeread_lab.tasks.forecast_calibration import CURVE_CASES as FORECAST_CURVE_CASES
from aeread_lab.tasks.forecast_calibration import DEFAULT_CASES as FORECAST_CASES
from aeread_lab.tasks.forecast_calibration import (
    NOISY_ROLLING_LOG_CALIBRATION_CASES as FORECAST_ROLLING_NOISY_LOG_CASES,
)
from aeread_lab.tasks.forecast_calibration import EVENT_LOG_CALIBRATION_CASES as FORECAST_EVENT_LOG_CASES
from aeread_lab.tasks.forecast_calibration import (
    OPERATIONAL_LOG_CALIBRATION_CASES as FORECAST_OPERATIONAL_LOG_CASES,
)
from aeread_lab.tasks.forecast_calibration import NOISY_CURVE_CASES as FORECAST_NOISY_CURVE_CASES
from aeread_lab.tasks.forecast_calibration import ROLLING_CALIBRATION_CASES as FORECAST_ROLLING_CASES
from aeread_lab.tasks.forecast_calibration import ROLLING_LOG_CALIBRATION_CASES as FORECAST_ROLLING_LOG_CASES
from aeread_lab.tasks.forecast_calibration import SHIFT_CALIBRATION_CASES as FORECAST_SHIFT_CASES
from aeread_lab.tasks.forecast_calibration import _aggregate_prompt as forecast_aggregate_prompt
from aeread_lab.tasks.forecast_calibration import (
    _curve_implicit_prompt as forecast_curve_implicit_prompt,
)
from aeread_lab.tasks.forecast_calibration import _curve_natural_prompt as forecast_curve_natural_prompt
from aeread_lab.tasks.forecast_calibration import _curve_noisy_prompt as forecast_curve_noisy_prompt
from aeread_lab.tasks.forecast_calibration import _curve_prompt as forecast_curve_prompt
from aeread_lab.tasks.forecast_calibration import _event_log_prompt as forecast_event_log_prompt
from aeread_lab.tasks.forecast_calibration import _operational_log_prompt as forecast_operational_log_prompt
from aeread_lab.tasks.forecast_calibration import _prompt as forecast_prompt
from aeread_lab.tasks.forecast_calibration import _rolling_log_noisy_prompt as forecast_rolling_noisy_log_prompt
from aeread_lab.tasks.forecast_calibration import _rolling_log_prompt as forecast_rolling_log_prompt
from aeread_lab.tasks.forecast_calibration import _rolling_prompt as forecast_rolling_prompt
from aeread_lab.tasks.forecast_calibration import _shift_prompt as forecast_shift_prompt
from aeread_lab.tasks.forecast_calibration import run_forecast_aggregate_game
from aeread_lab.tasks.forecast_calibration import run_forecast_calibration_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_implicit_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_natural_game
from aeread_lab.tasks.forecast_calibration import run_forecast_curve_noisy_game
from aeread_lab.tasks.forecast_calibration import run_forecast_event_log_calibration_game
from aeread_lab.tasks.forecast_calibration import run_forecast_operational_log_calibration_game
from aeread_lab.tasks.forecast_calibration import run_forecast_rolling_log_calibration_game
from aeread_lab.tasks.forecast_calibration import run_forecast_rolling_log_noisy_game
from aeread_lab.tasks.forecast_calibration import run_forecast_rolling_calibration_game
from aeread_lab.tasks.forecast_calibration import run_forecast_shift_calibration_game
from aeread_lab.tasks.market import INVENTORY_POLICY_CASES as MARKET_INVENTORY_POLICY_CASES
from aeread_lab.tasks.market import POLICY_SHIFT_CASES as MARKET_POLICY_CASES
from aeread_lab.tasks.market import TRACE_INVENTORY_CASES as MARKET_TRACE_INVENTORY_CASES
from aeread_lab.tasks.market import TRACE_REPLENISHMENT_CASES as MARKET_TRACE_REPLENISHMENT_CASES
from aeread_lab.tasks.market import (
    TRACE_REPLENISHMENT_NOISY_CASES as MARKET_TRACE_REPLENISHMENT_NOISY_CASES,
)
from aeread_lab.tasks.market import _policy_inventory_prompt as market_policy_inventory_prompt
from aeread_lab.tasks.market import _policy_shift_prompt as market_policy_prompt
from aeread_lab.tasks.market import _trace_inventory_prompt as market_trace_inventory_prompt
from aeread_lab.tasks.market import _trace_markdown_prompt as market_trace_markdown_prompt
from aeread_lab.tasks.market import (
    _trace_replenishment_natural_prompt as market_trace_replenishment_natural_prompt,
)
from aeread_lab.tasks.market import (
    _trace_replenishment_noisy_prompt as market_trace_replenishment_noisy_prompt,
)
from aeread_lab.tasks.market import _trace_replenishment_prompt as market_trace_replenishment_prompt
from aeread_lab.tasks.market import (
    run_market_game,
    run_market_policy_inventory_game,
    run_market_policy_shift_game,
    run_market_trace_inventory_game,
    run_market_trace_markdown_game,
    run_market_trace_replenishment_natural_game,
    run_market_trace_replenishment_noisy_game,
    run_market_trace_replenishment_game,
)
from aeread_lab.tasks.matching import DEFAULT_CASES as MATCHING_CASES
from aeread_lab.tasks.matching import _prompt as matching_prompt
from aeread_lab.tasks.matching import run_matching_game
from aeread_lab.tasks.mechanism import DEFAULT_CASES as MECHANISM_CASES
from aeread_lab.tasks.mechanism import INTERACTION_TRACE_CASES as MECHANISM_TRACE_CASES
from aeread_lab.tasks.mechanism import PARTICIPANT_RESPONSE_CASES as MECHANISM_RESPONSE_CASES
from aeread_lab.tasks.mechanism import REPEATED_CASES as MECHANISM_REPEATED_CASES
from aeread_lab.tasks.mechanism import STRATEGIC_RESPONSE_CASES as MECHANISM_STRATEGIC_CASES
from aeread_lab.tasks.mechanism import TRACE_EQUILIBRIUM_CASES as MECHANISM_TRACE_EQUILIBRIUM_CASES
from aeread_lab.tasks.mechanism import (
    TRACE_EQUILIBRIUM_NOISY_CASES as MECHANISM_TRACE_EQUILIBRIUM_NOISY_CASES,
)
from aeread_lab.tasks.mechanism import _participant_elasticity_prompt as mechanism_elasticity_prompt
from aeread_lab.tasks.mechanism import _participant_response_prompt as mechanism_response_prompt
from aeread_lab.tasks.mechanism import _prompt as mechanism_prompt
from aeread_lab.tasks.mechanism import _repeated_natural_prompt as mechanism_repeated_natural_prompt
from aeread_lab.tasks.mechanism import _repeated_prompt as mechanism_repeated_prompt
from aeread_lab.tasks.mechanism import _strategic_equilibrium_prompt as mechanism_strategic_equilibrium_prompt
from aeread_lab.tasks.mechanism import _strategic_response_prompt as mechanism_strategic_response_prompt
from aeread_lab.tasks.mechanism import _interaction_trace_prompt as mechanism_interaction_trace_prompt
from aeread_lab.tasks.mechanism import _trace_equilibrium_prompt as mechanism_trace_equilibrium_prompt
from aeread_lab.tasks.mechanism import (
    _trace_equilibrium_natural_prompt as mechanism_trace_equilibrium_natural_prompt,
)
from aeread_lab.tasks.mechanism import (
    _trace_equilibrium_noisy_prompt as mechanism_trace_equilibrium_noisy_prompt,
)
from aeread_lab.tasks.mechanism import (
    run_mechanism_elasticity_inference_game,
    run_mechanism_game,
    run_mechanism_interaction_trace_game,
    run_mechanism_participant_response_game,
    run_mechanism_repeated_game,
    run_mechanism_repeated_natural_game,
    run_mechanism_strategic_equilibrium_game,
    run_mechanism_strategic_response_game,
    run_mechanism_trace_equilibrium_game,
    run_mechanism_trace_equilibrium_natural_game,
    run_mechanism_trace_equilibrium_noisy_game,
)
from aeread_lab.tasks.moral_hazard import DEFAULT_CASES as MORAL_HAZARD_CASES
from aeread_lab.tasks.moral_hazard import _prompt as moral_hazard_prompt
from aeread_lab.tasks.moral_hazard import run_moral_hazard_game
from aeread_lab.tasks.portfolio import DEFAULT_CASES as PORTFOLIO_CASES
from aeread_lab.tasks.portfolio import _prompt as portfolio_prompt
from aeread_lab.tasks.portfolio import run_portfolio_game
from aeread_lab.tasks.principal_holding_prediction import (
    DEFAULT_CASES as PRINCIPAL_HOLDING_CASES,
)
from aeread_lab.tasks.principal_holding_prediction import _prompt as principal_holding_prompt
from aeread_lab.tasks.principal_holding_prediction import run_principal_holding_prediction_game
from aeread_lab.tasks.principal_holding_prediction_blind_notes import (
    DEFAULT_CASES as PRINCIPAL_HOLDING_BLIND_NOTES_CASES,
)
from aeread_lab.tasks.principal_holding_prediction_blind_notes import (
    _prompt as principal_holding_blind_notes_prompt,
)
from aeread_lab.tasks.principal_holding_prediction_blind_notes import (
    run_principal_holding_prediction_blind_notes_game,
)
from aeread_lab.tasks.principal_holding_prediction_notes import (
    DEFAULT_CASES as PRINCIPAL_HOLDING_NOTES_CASES,
)
from aeread_lab.tasks.principal_holding_prediction_notes import _prompt as principal_holding_notes_prompt
from aeread_lab.tasks.principal_holding_prediction_notes import run_principal_holding_prediction_notes_game
from aeread_lab.tasks.principal_holding_prediction_noisy import (
    DEFAULT_CASES as NOISY_PRINCIPAL_HOLDING_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_STRESS_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_STRESS_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_IMPLICIT_STABLE_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_IMPLICIT_STABLE_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_NOISY_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_NOISY_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_PARTIAL_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_PARTIAL_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_CONFLICT_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_CONFLICT_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_UNMARKED_CONFLICT_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_UNMARKED_CONFLICT_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_HISTORY_CONFLICT_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_HISTORY_CONFLICT_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_VALIDATION_PROCESS_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_VALIDATION_PROCESS_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_PROVENANCE_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_CONTEXT_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_CONTEXT_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_ABLATION_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_STATUS_NEUTRAL_INTRO_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_AUDIT_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_AUDIT_BACKFILL_ONLY_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_BACKFILL_ONLY_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_AUDIT_PRIMARY_ONLY_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_PRIMARY_ONLY_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    ARTIFACT_METADATA_SOURCE_AUDIT_RATIO_ONLY_CASES as PRINCIPAL_HOLDING_FILING_ARTIFACT_METADATA_SOURCE_AUDIT_RATIO_ONLY_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    DEFAULT_CASES as PRINCIPAL_HOLDING_FILING_TRACE_CASES,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    _artifact_prompt as principal_holding_filing_artifact_prompt,
)
from aeread_lab.tasks.principal_holding_filing_trace import (
    _raw_prompt as principal_holding_filing_trace_raw_prompt,
)
from aeread_lab.tasks.principal_holding_prediction_noisy import _prompt as noisy_principal_holding_prompt
from aeread_lab.tasks.principal_holding_prediction_noisy import run_noisy_principal_holding_prediction_game
from aeread_lab.tasks.pricing import COUNTERFACTUAL_SETS as PRICING_COUNTERFACTUAL_SETS
from aeread_lab.tasks.pricing import CROSS_ELASTICITY_CASES as PRICING_CROSS_CASES
from aeread_lab.tasks.pricing import DEFAULT_CASES as PRICING_CASES
from aeread_lab.tasks.pricing import DEFAULT_LAW_CASES as PRICING_LAW_CASES
from aeread_lab.tasks.pricing import EVIDENCE_LAW_CASES as PRICING_EVIDENCE_LAW_CASES
from aeread_lab.tasks.pricing import HOLDOUT_EVIDENCE_LAW_CASES as PRICING_EVIDENCE_HOLDOUT_CASES
from aeread_lab.tasks.pricing import HIDDEN_INTERVENTION_CASES as PRICING_HIDDEN_INTERVENTION_CASES
from aeread_lab.tasks.pricing import INVENTORY_MARKDOWN_CASES as PRICING_INVENTORY_MARKDOWN_CASES
from aeread_lab.tasks.pricing import INVENTORY_MARKDOWN_NOISY_CASES as PRICING_INVENTORY_MARKDOWN_NOISY_CASES
from aeread_lab.tasks.pricing import (
    INVENTORY_REPLENISHMENT_NOISY_CASES as PRICING_INVENTORY_REPLENISHMENT_NOISY_CASES,
)
from aeread_lab.tasks.pricing import (
    MULTI_PRODUCT_MARKDOWN_NOISY_CASES as PRICING_MULTI_MARKDOWN_NOISY_CASES,
)
from aeread_lab.tasks.pricing import (
    MULTI_PRODUCT_CAPACITY_NOISY_CASES as PRICING_MULTI_CAPACITY_NOISY_CASES,
)
from aeread_lab.tasks.pricing import MULTI_PRODUCT_CAPACITY_CASES as PRICING_MULTI_CAPACITY_CASES
from aeread_lab.tasks.pricing import MULTI_PRODUCT_CASES as PRICING_MULTI_CASES
from aeread_lab.tasks.pricing import _counterfactual_prompt as pricing_counterfactual_prompt
from aeread_lab.tasks.pricing import _cross_elasticity_prompt as pricing_cross_prompt
from aeread_lab.tasks.pricing import _evidence_law_audit_prompt as pricing_evidence_law_prompt
from aeread_lab.tasks.pricing import _inventory_markdown_noisy_prompt as pricing_inventory_markdown_noisy_prompt
from aeread_lab.tasks.pricing import _inventory_markdown_prompt as pricing_inventory_markdown_prompt
from aeread_lab.tasks.pricing import (
    _inventory_replenishment_noisy_prompt as pricing_inventory_replenishment_noisy_prompt,
)
from aeread_lab.tasks.pricing import _hidden_intervention_prompt as pricing_hidden_intervention_prompt
from aeread_lab.tasks.pricing import _law_audit_prompt as pricing_law_audit_prompt
from aeread_lab.tasks.pricing import (
    _multi_product_markdown_noisy_prompt as pricing_multi_markdown_noisy_prompt,
)
from aeread_lab.tasks.pricing import (
    _multi_product_capacity_noisy_prompt as pricing_multi_capacity_noisy_prompt,
)
from aeread_lab.tasks.pricing import _multi_product_capacity_prompt as pricing_multi_capacity_prompt
from aeread_lab.tasks.pricing import _multi_product_natural_prompt as pricing_multi_natural_prompt
from aeread_lab.tasks.pricing import _multi_product_prompt as pricing_multi_prompt
from aeread_lab.tasks.pricing import _prompt as pricing_prompt
from aeread_lab.tasks.pricing import run_pricing_counterfactual_game
from aeread_lab.tasks.pricing import run_pricing_cross_elasticity_game
from aeread_lab.tasks.pricing import run_pricing_evidence_law_audit_game
from aeread_lab.tasks.pricing import run_pricing_evidence_law_holdout_game
from aeread_lab.tasks.pricing import run_pricing_game
from aeread_lab.tasks.pricing import run_pricing_hidden_intervention_game
from aeread_lab.tasks.pricing import run_pricing_inventory_markdown_game
from aeread_lab.tasks.pricing import run_pricing_inventory_markdown_noisy_game
from aeread_lab.tasks.pricing import run_pricing_inventory_replenishment_noisy_game
from aeread_lab.tasks.pricing import run_pricing_law_audit_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_markdown_noisy_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_capacity_noisy_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_capacity_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_game
from aeread_lab.tasks.pricing import run_pricing_multi_product_natural_game
from aeread_lab.tasks.principal_inference import DEFAULT_CASES as PRINCIPAL_CASES
from aeread_lab.tasks.principal_inference import _prompt as principal_prompt
from aeread_lab.tasks.principal_inference import run_principal_inference_game
from aeread_lab.tasks.procurement import COUNTERFACTUAL_SETS
from aeread_lab.tasks.procurement import DEFAULT_CASES as PROCUREMENT_CASES
from aeread_lab.tasks.procurement import PROCUREMENT_BUNDLE_CASES
from aeread_lab.tasks.procurement import PROCUREMENT_VENDOR_UPDATE_CASES
from aeread_lab.tasks.procurement import (
    PROCUREMENT_VENDOR_UPDATE_NOISY_CASES,
)
from aeread_lab.tasks.procurement import _bundle_evidence_prompt as procurement_bundle_evidence_prompt
from aeread_lab.tasks.procurement import _bundle_history_prompt as procurement_bundle_history_prompt
from aeread_lab.tasks.procurement import _bundle_natural_prompt as procurement_bundle_natural_prompt
from aeread_lab.tasks.procurement import _bundle_noisy_evidence_prompt as procurement_bundle_noisy_evidence_prompt
from aeread_lab.tasks.procurement import _bundle_prompt as procurement_bundle_prompt
from aeread_lab.tasks.procurement import _bundle_reserve_prompt as procurement_bundle_reserve_prompt
from aeread_lab.tasks.procurement import _prompt as procurement_prompt
from aeread_lab.tasks.procurement import _vendor_update_prompt as procurement_vendor_update_prompt
from aeread_lab.tasks.procurement import (
    _vendor_update_noisy_prompt as procurement_vendor_update_noisy_prompt,
)
from aeread_lab.tasks.procurement import run_procurement_bundle_evidence_game
from aeread_lab.tasks.procurement import run_procurement_bundle_game
from aeread_lab.tasks.procurement import run_procurement_bundle_history_game
from aeread_lab.tasks.procurement import run_procurement_bundle_natural_game
from aeread_lab.tasks.procurement import run_procurement_bundle_noisy_evidence_game
from aeread_lab.tasks.procurement import run_procurement_bundle_reserve_game
from aeread_lab.tasks.procurement import run_procurement_counterfactual_game
from aeread_lab.tasks.procurement import run_procurement_game
from aeread_lab.tasks.procurement import run_procurement_vendor_update_game
from aeread_lab.tasks.procurement import run_procurement_vendor_update_noisy_game
from aeread_lab.tasks.regime import (
    DEFAULT_GAMBLES,
    DEFAULT_HOLDOUT_GAMBLES,
    DEFAULT_LAW_AUDIT_CASES,
    DEFAULT_RELATIONSHIP_GAMBLES,
    _holdout_prompt as regime_holdout_prompt,
    _law_audit_prompt as regime_law_audit_prompt,
    _prompt as regime_prompt,
    _relationship_prompt as regime_relationship_prompt,
    run_regime_holdout_verifier,
    run_regime_law_audit_game,
    run_regime_relationship_verifier,
)
from aeread_lab.tasks.revealed_allocation import DEFAULT_CASES as REVEALED_ALLOCATION_CASES
from aeread_lab.tasks.revealed_allocation import _prompt as revealed_allocation_prompt
from aeread_lab.tasks.revealed_allocation import run_revealed_allocation_game
from aeread_lab.tasks.retail import DEFAULT_CASES as RETAIL_CASES
from aeread_lab.tasks.retail import _prompt as retail_prompt
from aeread_lab.tasks.retail import run_retail_game
from aeread_lab.tasks.screening import DEFAULT_CASES as SCREENING_CASES
from aeread_lab.tasks.screening import _prompt as screening_prompt
from aeread_lab.tasks.screening import run_screening_game
from aeread_lab.tasks.strategic_drift import DEFAULT_CASES as DRIFT_CASES
from aeread_lab.tasks.strategic_drift import _prompt as strategic_prompt
from aeread_lab.tasks.strategic_drift import run_strategic_drift_game
from aeread_lab.tasks.supplier_scam import DEFAULT_CASES as SUPPLIER_SCAM_CASES
from aeread_lab.tasks.supplier_scam import _natural_prompt as supplier_scam_natural_prompt
from aeread_lab.tasks.supplier_scam import _prompt as supplier_scam_prompt
from aeread_lab.tasks.supplier_scam import run_supplier_scam_game
from aeread_lab.tasks.supplier_scam import run_supplier_scam_natural_game


class _AlternatingTradeAgent:
    name = "offline:alternating_trade"

    def __init__(self):
        self.calls = 0

    def complete(self, system: str, user: str) -> str:
        self.calls += 1
        trade_id = "t1" if self.calls % 2 else "t2"
        return f"FINAL_TRADE: {trade_id}"


class _WrongTradeAgent:
    name = "offline:wrong_trade"

    def complete(self, system: str, user: str) -> str:
        return "FINAL_TRADE: t2"


class _ArtifactStressMixtureAgent:
    name = "offline:artifact_stress_mixture"

    def __init__(self):
        self.calls = 0

    def complete(self, system: str, user: str) -> str:
        sequence = ("sec_stress_b", "sec_stress_a", "sec_stress_f")
        trade_id = sequence[self.calls % len(sequence)]
        self.calls += 1
        return f"FINAL_ISSUER: {trade_id}"
