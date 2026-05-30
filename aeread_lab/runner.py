from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from aeread_lab.models import Agent, build_agent
from aeread_lab.tasks import (
    adversarial as adversarial_task,
    alignment_tax as alignment_tax_task,
    ambiguity as ambiguity_task,
    auction as auction_task,
    bargaining as bargaining_task,
    belief_bargaining as belief_bargaining_task,
    common_value as common_value_task,
    experiment_design as experiment_design_task,
    exploration as exploration_task,
    forecast_calibration as forecast_calibration_task,
    market as market_task,
    matching as matching_task,
    mechanism as mechanism_task,
    moral_hazard as moral_hazard_task,
    portfolio as portfolio_task,
    pricing as pricing_task,
    principal_inference as principal_inference_task,
    procurement as procurement_task,
    regime as regime_task,
    revealed_allocation as revealed_allocation_task,
    retail as retail_task,
    screening as screening_task,
    strategic_drift as strategic_drift_task,
    supplier_scam as supplier_scam_task,
)


TASK_ORDER = (
    "regime",
    "regime_relationship",
    "regime_holdout",
    "regime_law_audit",
    "alignment_tax",
    "principal_inference",
    "portfolio",
    "revealed_allocation",
    "ambiguity",
    "bargaining",
    "belief_bargaining",
    "belief_bargaining_interaction",
    "market",
    "market_policy_shift",
    "market_policy_inventory",
    "matching",
    "screening",
    "moral_hazard",
    "auction",
    "common_value",
    "mechanism",
    "mechanism_repeated",
    "mechanism_repeated_natural",
    "mechanism_participant_response",
    "mechanism_elasticity_inference",
    "mechanism_strategic_response",
    "mechanism_strategic_equilibrium",
    "mechanism_interaction_trace",
    "strategic_drift",
    "forecast_calibration",
    "forecast_aggregate",
    "forecast_curve",
    "forecast_curve_implicit",
    "forecast_curve_noisy",
    "forecast_curve_natural",
    "exploration",
    "experiment_design",
    "retail",
    "procurement",
    "procurement_counterfactual",
    "procurement_bundle",
    "procurement_bundle_natural",
    "procurement_bundle_evidence",
    "procurement_bundle_noisy_evidence",
    "procurement_bundle_history",
    "procurement_bundle_reserve",
    "procurement_vendor_update",
    "pricing",
    "pricing_counterfactual",
    "pricing_cross_elasticity",
    "pricing_multi_product",
    "pricing_multi_product_natural",
    "pricing_multi_product_capacity",
    "pricing_inventory_markdown",
    "pricing_inventory_markdown_noisy",
    "pricing_law_audit",
    "pricing_evidence_law_audit",
    "pricing_evidence_law_holdout",
    "scam",
    "supplier_scam",
    "supplier_scam_natural",
)


_CASE_TASKS = {
    "alignment_tax": (alignment_tax_task.run_alignment_tax_game, alignment_tax_task.DEFAULT_CASES),
    "principal_inference": (
        principal_inference_task.run_principal_inference_game,
        principal_inference_task.DEFAULT_CASES,
    ),
    "portfolio": (portfolio_task.run_portfolio_game, portfolio_task.DEFAULT_CASES),
    "revealed_allocation": (
        revealed_allocation_task.run_revealed_allocation_game,
        revealed_allocation_task.DEFAULT_CASES,
    ),
    "ambiguity": (ambiguity_task.run_ambiguity_game, ambiguity_task.DEFAULT_CASES),
    "bargaining": (bargaining_task.run_bargaining_game, bargaining_task.DEFAULT_CASES),
    "belief_bargaining": (
        belief_bargaining_task.run_belief_bargaining_game,
        belief_bargaining_task.DEFAULT_CASES,
    ),
    "belief_bargaining_interaction": (
        belief_bargaining_task.run_belief_bargaining_interaction_game,
        belief_bargaining_task.INTERACTION_CASES,
    ),
    "market": (market_task.run_market_game, market_task.DEFAULT_CASES),
    "market_policy_shift": (
        market_task.run_market_policy_shift_game,
        market_task.POLICY_SHIFT_CASES,
    ),
    "market_policy_inventory": (
        market_task.run_market_policy_inventory_game,
        market_task.INVENTORY_POLICY_CASES,
    ),
    "matching": (matching_task.run_matching_game, matching_task.DEFAULT_CASES),
    "screening": (screening_task.run_screening_game, screening_task.DEFAULT_CASES),
    "moral_hazard": (moral_hazard_task.run_moral_hazard_game, moral_hazard_task.DEFAULT_CASES),
    "auction": (auction_task.run_auction_game, auction_task.DEFAULT_CASES),
    "common_value": (common_value_task.run_common_value_game, common_value_task.DEFAULT_CASES),
    "mechanism": (mechanism_task.run_mechanism_game, mechanism_task.DEFAULT_CASES),
    "mechanism_repeated": (
        mechanism_task.run_mechanism_repeated_game,
        mechanism_task.REPEATED_CASES,
    ),
    "mechanism_repeated_natural": (
        mechanism_task.run_mechanism_repeated_natural_game,
        mechanism_task.REPEATED_CASES,
    ),
    "mechanism_participant_response": (
        mechanism_task.run_mechanism_participant_response_game,
        mechanism_task.PARTICIPANT_RESPONSE_CASES,
    ),
    "mechanism_elasticity_inference": (
        mechanism_task.run_mechanism_elasticity_inference_game,
        mechanism_task.PARTICIPANT_RESPONSE_CASES,
    ),
    "mechanism_strategic_response": (
        mechanism_task.run_mechanism_strategic_response_game,
        mechanism_task.STRATEGIC_RESPONSE_CASES,
    ),
    "mechanism_strategic_equilibrium": (
        mechanism_task.run_mechanism_strategic_equilibrium_game,
        mechanism_task.STRATEGIC_RESPONSE_CASES,
    ),
    "mechanism_interaction_trace": (
        mechanism_task.run_mechanism_interaction_trace_game,
        mechanism_task.INTERACTION_TRACE_CASES,
    ),
    "strategic_drift": (
        strategic_drift_task.run_strategic_drift_game,
        strategic_drift_task.DEFAULT_CASES,
    ),
    "forecast_calibration": (
        forecast_calibration_task.run_forecast_calibration_game,
        forecast_calibration_task.DEFAULT_CASES,
    ),
    "forecast_aggregate": (
        forecast_calibration_task.run_forecast_aggregate_game,
        forecast_calibration_task.AGGREGATE_CASES,
    ),
    "forecast_curve": (
        forecast_calibration_task.run_forecast_curve_game,
        forecast_calibration_task.CURVE_CASES,
    ),
    "forecast_curve_implicit": (
        forecast_calibration_task.run_forecast_curve_implicit_game,
        forecast_calibration_task.CURVE_CASES,
    ),
    "forecast_curve_noisy": (
        forecast_calibration_task.run_forecast_curve_noisy_game,
        forecast_calibration_task.NOISY_CURVE_CASES,
    ),
    "forecast_curve_natural": (
        forecast_calibration_task.run_forecast_curve_natural_game,
        forecast_calibration_task.NOISY_CURVE_CASES,
    ),
    "exploration": (exploration_task.run_exploration_game, exploration_task.DEFAULT_CASES),
    "experiment_design": (
        experiment_design_task.run_experiment_design_game,
        experiment_design_task.DEFAULT_CASES,
    ),
    "retail": (retail_task.run_retail_game, retail_task.DEFAULT_CASES),
    "procurement": (procurement_task.run_procurement_game, procurement_task.DEFAULT_CASES),
    "procurement_counterfactual": (
        procurement_task.run_procurement_counterfactual_game,
        procurement_task.COUNTERFACTUAL_SETS,
    ),
    "procurement_bundle": (
        procurement_task.run_procurement_bundle_game,
        procurement_task.PROCUREMENT_BUNDLE_CASES,
    ),
    "procurement_bundle_natural": (
        procurement_task.run_procurement_bundle_natural_game,
        procurement_task.PROCUREMENT_BUNDLE_CASES,
    ),
    "procurement_bundle_evidence": (
        procurement_task.run_procurement_bundle_evidence_game,
        procurement_task.PROCUREMENT_BUNDLE_CASES,
    ),
    "procurement_bundle_noisy_evidence": (
        procurement_task.run_procurement_bundle_noisy_evidence_game,
        procurement_task.PROCUREMENT_BUNDLE_CASES,
    ),
    "procurement_bundle_history": (
        procurement_task.run_procurement_bundle_history_game,
        procurement_task.PROCUREMENT_BUNDLE_CASES,
    ),
    "procurement_bundle_reserve": (
        procurement_task.run_procurement_bundle_reserve_game,
        procurement_task.PROCUREMENT_BUNDLE_RESERVE_CASES,
    ),
    "procurement_vendor_update": (
        procurement_task.run_procurement_vendor_update_game,
        procurement_task.PROCUREMENT_VENDOR_UPDATE_CASES,
    ),
    "pricing": (pricing_task.run_pricing_game, pricing_task.DEFAULT_CASES),
    "pricing_counterfactual": (
        pricing_task.run_pricing_counterfactual_game,
        pricing_task.COUNTERFACTUAL_SETS,
    ),
    "pricing_cross_elasticity": (
        pricing_task.run_pricing_cross_elasticity_game,
        pricing_task.CROSS_ELASTICITY_CASES,
    ),
    "pricing_multi_product": (
        pricing_task.run_pricing_multi_product_game,
        pricing_task.MULTI_PRODUCT_CASES,
    ),
    "pricing_multi_product_natural": (
        pricing_task.run_pricing_multi_product_natural_game,
        pricing_task.MULTI_PRODUCT_CASES,
    ),
    "pricing_multi_product_capacity": (
        pricing_task.run_pricing_multi_product_capacity_game,
        pricing_task.MULTI_PRODUCT_CAPACITY_CASES,
    ),
    "pricing_inventory_markdown": (
        pricing_task.run_pricing_inventory_markdown_game,
        pricing_task.INVENTORY_MARKDOWN_CASES,
    ),
    "pricing_inventory_markdown_noisy": (
        pricing_task.run_pricing_inventory_markdown_noisy_game,
        pricing_task.INVENTORY_MARKDOWN_NOISY_CASES,
    ),
    "pricing_law_audit": (
        pricing_task.run_pricing_law_audit_game,
        pricing_task.DEFAULT_LAW_CASES,
    ),
    "pricing_evidence_law_audit": (
        pricing_task.run_pricing_evidence_law_audit_game,
        pricing_task.EVIDENCE_LAW_CASES,
    ),
    "pricing_evidence_law_holdout": (
        pricing_task.run_pricing_evidence_law_holdout_game,
        pricing_task.HOLDOUT_EVIDENCE_LAW_CASES,
    ),
    "supplier_scam": (supplier_scam_task.run_supplier_scam_game, supplier_scam_task.DEFAULT_CASES),
    "supplier_scam_natural": (
        supplier_scam_task.run_supplier_scam_natural_game,
        supplier_scam_task.DEFAULT_CASES,
    ),
}


def run_task(
    task: str,
    agent: Agent,
    attacker: Agent | None = None,
    sample_limit: int | None = None,
) -> dict[str, Any]:
    limit = _normalize_sample_limit(sample_limit)
    if task == "regime":
        return regime_task.run_regime_battery(
            agent,
            gambles=_sample(regime_task.DEFAULT_GAMBLES, limit),
        )
    if task == "regime_relationship":
        return regime_task.run_regime_relationship_verifier(
            agent,
            gambles=_sample(regime_task.DEFAULT_RELATIONSHIP_GAMBLES, limit),
        )
    if task == "regime_holdout":
        return regime_task.run_regime_holdout_verifier(
            agent,
            gambles=_sample(regime_task.DEFAULT_HOLDOUT_GAMBLES, limit),
        )
    if task == "regime_law_audit":
        return regime_task.run_regime_law_audit_game(
            agent,
            cases=_sample(regime_task.DEFAULT_LAW_AUDIT_CASES, limit),
        )
    if task == "scam":
        return adversarial_task.run_scam_arena(
            defender=agent,
            attacker=attacker or build_agent("offline:credulous"),
            items=_sample(adversarial_task.DEFAULT_ITEMS, limit),
        )
    if task in _CASE_TASKS:
        runner, cases = _CASE_TASKS[task]
        return runner(agent, cases=_sample(cases, limit))
    raise ValueError(f"Unknown task: {task}")


def expand_tasks(task: str) -> list[str]:
    return list(TASK_ORDER) if task == "all" else [task]


def run_tasks(
    task: str,
    agent: Agent,
    attacker: Agent | None = None,
    sample_limit: int | None = None,
) -> list[dict[str, Any]]:
    return [run_task(t, agent, attacker=attacker, sample_limit=sample_limit) for t in expand_tasks(task)]


def run_sweep(
    *,
    task: str,
    agent_specs: Iterable[str],
    attacker_spec: str = "offline:credulous",
    wrap_cache=None,
    sample_limit: int | None = None,
) -> dict[str, Any]:
    limit = _normalize_sample_limit(sample_limit)
    attacker = build_agent(attacker_spec)
    if wrap_cache is not None:
        attacker = wrap_cache(attacker)
    specs = list(agent_specs)
    runs = []
    for spec in specs:
        agent = build_agent(spec)
        if wrap_cache is not None:
            agent = wrap_cache(agent)
        runs.append({"agent": agent.name, "results": run_tasks(task, agent, attacker=attacker, sample_limit=limit)})
    return {"task": task, "agents": specs, "sample_limit": limit, "runs": runs}


def _normalize_sample_limit(sample_limit: int | None) -> int | None:
    if sample_limit is None:
        return None
    if sample_limit < 1:
        raise ValueError("sample_limit must be positive")
    return sample_limit


def _sample(items, sample_limit: int | None):
    if sample_limit is None:
        return None
    return list(items)[:sample_limit]
