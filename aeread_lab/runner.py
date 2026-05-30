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
    "alignment_tax",
    "principal_inference",
    "portfolio",
    "revealed_allocation",
    "ambiguity",
    "bargaining",
    "belief_bargaining",
    "market",
    "market_policy_shift",
    "matching",
    "screening",
    "moral_hazard",
    "auction",
    "common_value",
    "mechanism",
    "mechanism_repeated",
    "mechanism_repeated_natural",
    "mechanism_participant_response",
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
    "pricing",
    "pricing_counterfactual",
    "scam",
    "supplier_scam",
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
    "market": (market_task.run_market_game, market_task.DEFAULT_CASES),
    "market_policy_shift": (
        market_task.run_market_policy_shift_game,
        market_task.POLICY_SHIFT_CASES,
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
    "pricing": (pricing_task.run_pricing_game, pricing_task.DEFAULT_CASES),
    "pricing_counterfactual": (
        pricing_task.run_pricing_counterfactual_game,
        pricing_task.COUNTERFACTUAL_SETS,
    ),
    "supplier_scam": (supplier_scam_task.run_supplier_scam_game, supplier_scam_task.DEFAULT_CASES),
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
