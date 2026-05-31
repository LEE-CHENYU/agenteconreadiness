from __future__ import annotations

from typing import Any


PRIMARY_METRICS = {
    "regime": ("mean_absolute_error", "lower"),
    "regime_relationship": ("mean_absolute_error", "lower"),
    "regime_holdout": ("mean_absolute_error", "lower"),
    "regime_law_audit": ("accuracy", "higher"),
    "alignment_tax": ("mean_objective_regret", "lower"),
    "principal_inference": ("mean_fraction_error", "lower"),
    "portfolio": ("mean_utility_regret", "lower"),
    "revealed_allocation": ("mean_utility_regret", "lower"),
    "principal_holding_prediction": ("mean_score_regret", "lower"),
    "principal_holding_prediction_noisy": ("mean_score_regret", "lower"),
    "principal_holding_prediction_notes": ("mean_score_regret", "lower"),
    "principal_holding_prediction_blind_notes": ("mean_score_regret", "lower"),
    "principal_holding_filing_trace": ("mean_score_regret", "lower"),
    "principal_holding_filing_trace_raw": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_natural": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_stress": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_implicit": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_implicit_stable": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_metadata": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_metadata_noisy": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_metadata_partial": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_metadata_conflict": ("mean_score_regret", "lower"),
    "principal_holding_filing_artifact_metadata_unmarked_conflict": (
        "mean_score_regret",
        "lower",
    ),
    "principal_holding_filing_artifact_metadata_history_conflict": (
        "mean_score_regret",
        "lower",
    ),
    "principal_holding_filing_artifact_metadata_validation_process": (
        "mean_score_regret",
        "lower",
    ),
    "principal_holding_filing_artifact_metadata_source_provenance": (
        "mean_score_regret",
        "lower",
    ),
    "principal_holding_filing_artifact_metadata_source_context": (
        "mean_score_regret",
        "lower",
    ),
    "principal_holding_filing_artifact_metadata_source_status_ablation": (
        "mean_score_regret",
        "lower",
    ),
    "ambiguity": ("mean_robust_regret", "lower"),
    "bargaining": ("mean_grade_error", "lower"),
    "belief_bargaining": ("mean_expected_surplus_gap", "lower"),
    "belief_bargaining_interaction": ("mean_expected_surplus_gap", "lower"),
    "market": ("mean_equilibrium_price_gap", "lower"),
    "market_policy_shift": ("mean_profit_regret", "lower"),
    "market_policy_inventory": ("mean_constrained_terminal_cash_regret", "lower"),
    "market_trace_inventory": ("mean_constrained_terminal_cash_regret", "lower"),
    "market_trace_markdown": ("mean_constrained_terminal_cash_regret", "lower"),
    "market_trace_replenishment": ("mean_constrained_terminal_cash_regret", "lower"),
    "market_trace_replenishment_natural": ("mean_constrained_terminal_cash_regret", "lower"),
    "market_trace_replenishment_noisy": ("mean_constrained_terminal_cash_regret", "lower"),
    "matching": ("mean_score_regret", "lower"),
    "screening": ("mean_score_regret", "lower"),
    "moral_hazard": ("mean_profit_regret", "lower"),
    "auction": ("mean_reserve_error", "lower"),
    "common_value": ("mean_profit_regret", "lower"),
    "mechanism": ("mean_score_regret", "lower"),
    "mechanism_repeated": ("mean_score_regret", "lower"),
    "mechanism_repeated_natural": ("mean_score_regret", "lower"),
    "mechanism_participant_response": ("mean_score_regret", "lower"),
    "mechanism_elasticity_inference": ("mean_score_regret", "lower"),
    "mechanism_strategic_response": ("mean_score_regret", "lower"),
    "mechanism_strategic_equilibrium": ("mean_score_regret", "lower"),
    "mechanism_interaction_trace": ("mean_score_regret", "lower"),
    "mechanism_trace_equilibrium": ("mean_score_regret", "lower"),
    "mechanism_trace_equilibrium_natural": ("mean_score_regret", "lower"),
    "mechanism_trace_equilibrium_noisy": ("mean_score_regret", "lower"),
    "strategic_drift": ("drift_rate", "lower"),
    "forecast_calibration": ("mean_expected_brier_regret", "lower"),
    "forecast_aggregate": ("mean_expected_brier_regret", "lower"),
    "forecast_curve": ("mean_expected_brier_regret", "lower"),
    "forecast_curve_implicit": ("mean_expected_brier_regret", "lower"),
    "forecast_curve_noisy": ("mean_expected_brier_regret", "lower"),
    "forecast_curve_natural": ("mean_expected_brier_regret", "lower"),
    "forecast_shift_calibration": ("mean_expected_brier_regret", "lower"),
    "forecast_rolling_calibration": ("mean_expected_brier_regret", "lower"),
    "forecast_rolling_log_calibration": ("mean_expected_brier_regret", "lower"),
    "forecast_rolling_log_noisy": ("mean_expected_brier_regret", "lower"),
    "forecast_event_log_calibration": ("mean_expected_brier_regret", "lower"),
    "forecast_operational_log_calibration": ("mean_expected_brier_regret", "lower"),
    "exploration": ("mean_expected_value_gap", "lower"),
    "experiment_design": ("mean_expected_value_gap", "lower"),
    "retail": ("mean_order_error", "lower"),
    "procurement": ("accuracy", "higher"),
    "procurement_counterfactual": ("accuracy", "higher"),
    "procurement_bundle": ("mean_score_regret", "lower"),
    "procurement_bundle_natural": ("mean_score_regret", "lower"),
    "procurement_bundle_evidence": ("mean_score_regret", "lower"),
    "procurement_bundle_noisy_evidence": ("mean_score_regret", "lower"),
    "procurement_bundle_history": ("mean_score_regret", "lower"),
    "procurement_bundle_reserve": ("mean_score_regret", "lower"),
    "procurement_vendor_update": ("mean_score_regret", "lower"),
    "procurement_vendor_update_noisy": ("mean_score_regret", "lower"),
    "pricing": ("mean_revenue_gap", "lower"),
    "pricing_counterfactual": ("mean_absolute_price_error", "lower"),
    "pricing_cross_elasticity": ("mean_absolute_price_error", "lower"),
    "pricing_multi_product": ("mean_price_l1_error", "lower"),
    "pricing_multi_product_natural": ("mean_price_l1_error", "lower"),
    "pricing_multi_product_capacity": ("mean_price_l1_error", "lower"),
    "pricing_multi_product_capacity_noisy": ("mean_price_l1_error", "lower"),
    "pricing_inventory_markdown": ("mean_price_l1_error", "lower"),
    "pricing_inventory_markdown_noisy": ("mean_price_l1_error", "lower"),
    "pricing_multi_product_markdown_noisy": ("mean_price_l1_error", "lower"),
    "pricing_inventory_replenishment_noisy": ("mean_decision_l1_error", "lower"),
    "pricing_hidden_intervention": ("mean_absolute_price_error", "lower"),
    "pricing_law_audit": ("accuracy", "higher"),
    "pricing_evidence_law_audit": ("accuracy", "higher"),
    "pricing_evidence_law_holdout": ("accuracy", "higher"),
    "adversarial_scam": ("mean_overpayment", "lower"),
    "supplier_scam": ("mean_constrained_final_cash_regret", "lower"),
    "supplier_scam_natural": ("mean_constrained_final_cash_regret", "lower"),
}


def extract_metric(result: dict[str, Any]) -> tuple[str, float | None, str]:
    metric, direction = PRIMARY_METRICS[result["task"]]
    value = result.get(metric)
    return metric, value, direction


def comparison_table(sweep: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for run in sweep["runs"]:
        agent = run["agent"]
        for result in run["results"]:
            metric, value, direction = extract_metric(result)
            rows.append(
                {
                    "agent": agent,
                    "task": result["task"],
                    "metric": metric,
                    "direction": direction,
                    "value": value,
                    "n_trials": result.get("n_trials"),
                    "parse_rate": parse_rate(result),
                }
            )
    return rows


def parse_rate(result: dict[str, Any]) -> float | None:
    if "parse_rate" in result:
        return result["parse_rate"]
    trials = result.get("trials")
    if not isinstance(trials, list) or not trials:
        return None
    total = 0
    parsed = 0
    for trial in trials:
        if not isinstance(trial, dict):
            continue
        chosen_keys = [
            key
            for key in trial
            if key.startswith("chosen_")
            and key not in {"chosen_revenue", "chosen_expected_profit", "chosen_surplus"}
        ]
        if not chosen_keys:
            continue
        total += 1
        if any(trial.get(key) is not None for key in chosen_keys):
            parsed += 1
    return parsed / total if total else None


def rank_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for task in sorted({row["task"] for row in rows}):
        subset = [row for row in rows if row["task"] == task]
        if not subset:
            continue
        direction = subset[0]["direction"]
        present = [row for row in subset if row["value"] is not None]
        missing = [row for row in subset if row["value"] is None]
        present.sort(key=lambda row: row["value"], reverse=direction == "higher")
        ordered = present + missing
        for idx, row in enumerate(ordered, start=1):
            ranked.append({**row, "rank": idx})
    return ranked


def format_sweep(sweep: dict[str, Any]) -> str:
    rows = rank_rows(comparison_table(sweep))
    limit = sweep.get("sample_limit")
    limit_text = "" if limit is None else f" sample_limit={limit}"
    case_text = _case_text(sweep.get("case_keys"))
    lines = [
        (
            f"AERead model sweep: task={sweep['task']} agents={', '.join(sweep['agents'])}"
            f"{limit_text}{case_text}"
        ),
        "=" * 88,
        f"{'task':<18} {'rank':>4} {'agent':<18} {'metric':<24} "
        f"{'value':>12} {'parse':>6} {'direction':<7}",
        "-" * 88,
    ]
    for row in rows:
        value = "n/a" if row["value"] is None else f"{row['value']:.6g}"
        parse = "n/a" if row["parse_rate"] is None else f"{row['parse_rate']:.2f}"
        lines.append(
            f"{row['task']:<18} {row['rank']:>4} {row['agent']:<18} "
            f"{row['metric']:<24} {value:>12} {parse:>6} {row['direction']:<7}"
        )
    lines.append("=" * 88)
    return "\n".join(lines)


def stability_sweep_table(sweep: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for run in sweep["runs"]:
        rows.append(
            {
                "agent": run["agent"],
                "primary_metric": run["primary_metric"],
                "direction": run["direction"],
                "primary_mean": run.get("primary_mean"),
                "primary_range": run.get("primary_range"),
                "parse_rate_min": run.get("parse_rate_min"),
                "accuracy_mean": run.get("accuracy_mean"),
                "unstable_case_rate": run.get("unstable_case_rate"),
                "stable_oracle_case_rate": run.get("stable_oracle_case_rate"),
                "non_oracle_modal_case_rate": _sum_optional_rates(
                    run.get("stable_non_oracle_case_rate"),
                    run.get("unstable_non_oracle_modal_case_rate"),
                ),
                "unstable_non_oracle_modal_case_rate": run.get(
                    "unstable_non_oracle_modal_case_rate"
                ),
                "modal_reference_counts": run.get("non_oracle_modal_reference_counts") or {},
                "choice_reference_hit_counts": run.get("choice_reference_hit_counts") or {},
                "non_oracle_choice_rate": run.get("non_oracle_choice_rate"),
                "attributed_non_oracle_choice_rate": run.get(
                    "attributed_non_oracle_choice_rate"
                ),
                "multi_reference_case_rate": run.get("multi_reference_case_rate"),
            }
        )
    if not rows:
        return rows
    direction = rows[0]["direction"]
    present = [row for row in rows if row["primary_mean"] is not None]
    missing = [row for row in rows if row["primary_mean"] is None]
    present.sort(key=lambda row: row["primary_mean"], reverse=direction == "higher")
    ordered = present + missing
    return [{**row, "rank": idx} for idx, row in enumerate(ordered, start=1)]


def stability_sweep_case_table(sweep: dict[str, Any]) -> list[dict[str, Any]]:
    agents = [run["agent"] for run in sweep["runs"]]
    cases_by_agent: dict[str, dict[str, dict[str, Any]]] = {}
    case_keys: set[str] = set()
    for run in sweep["runs"]:
        agent = run["agent"]
        cases_by_agent[agent] = {}
        for case_row in run.get("case_stability") or []:
            case_key = case_row["case_key"]
            case_keys.add(case_key)
            cases_by_agent[agent][case_key] = case_row

    rows: list[dict[str, Any]] = []
    for case_key in sorted(case_keys):
        for agent in agents:
            case_row = cases_by_agent.get(agent, {}).get(case_key)
            if case_row is None:
                rows.append(
                    {
                        "case_key": case_key,
                        "agent": agent,
                        "status": "missing",
                        "unique_choice_count": None,
                        "oracle_margin": None,
                        "modal_choice": None,
                        "modal_reference_matches": [],
                        "oracle_hit_rate": None,
                    }
                )
                continue
            rows.append(
                {
                    "case_key": case_key,
                    "agent": agent,
                    "status": case_row.get("status"),
                    "unique_choice_count": case_row.get("unique_choice_count"),
                    "oracle_margin": case_row.get("oracle_margin"),
                    "modal_choice": case_row.get("modal_choice"),
                    "modal_reference_matches": case_row.get("modal_reference_matches") or [],
                    "oracle_hit_rate": case_row.get("oracle_hit_rate"),
                }
            )
    return rows


def format_stability_sweep(sweep: dict[str, Any]) -> str:
    limit = sweep.get("sample_limit")
    limit_text = "" if limit is None else f" sample_limit={limit}"
    case_text = _case_text(sweep.get("case_keys"))
    rows = stability_sweep_table(sweep)
    lines = [
        (
            f"AERead stability sweep: task={sweep['task']} "
            f"agents={', '.join(sweep['agents'])} repeats={sweep['repeat_count']}"
            f"{limit_text}{case_text}"
        ),
        "=" * 112,
        (
            f"{'rank':>4} {'agent':<18} {'metric':<24} {'mean':>10} {'range':>10} "
            f"{'parse_min':>9} {'acc_mean':>9} {'unstable':>9} {'stable_oracle':>13} "
            f"{'non_oracle':>11} {'refs':<18}"
        ),
        "-" * 112,
    ]
    for row in rows:
        refs = ", ".join(
            f"{reference}:{count}"
            for reference, count in sorted(row["modal_reference_counts"].items())
        )
        lines.append(
            f"{row['rank']:>4} {row['agent']:<18.18} {row['primary_metric']:<24.24} "
            f"{_fmt(row['primary_mean']):>10} {_fmt(row['primary_range']):>10} "
            f"{_fmt(row['parse_rate_min']):>9} {_fmt(row['accuracy_mean']):>9} "
            f"{_fmt(row['unstable_case_rate']):>9} "
            f"{_fmt(row['stable_oracle_case_rate']):>13} "
            f"{_fmt(row['non_oracle_modal_case_rate']):>11} "
            f"{refs:<18.18}"
        )
    case_rows = stability_sweep_case_table(sweep)
    if case_rows:
        lines.append("-" * 112)
        mix_rows = [
            row for row in rows if row.get("choice_reference_hit_counts")
        ]
        if mix_rows:
            lines.append("Choice reference mix")
            lines.append(
                f"{'agent':<18} {'non_oracle':>10} {'attributed':>10} "
                f"{'multi_ref':>10} {'choice_refs':<48}"
            )
            for row in mix_rows:
                refs = _format_counts(row.get("choice_reference_hit_counts") or {})
                lines.append(
                    f"{row['agent']:<18.18} "
                    f"{_fmt(row.get('non_oracle_choice_rate')):>10} "
                    f"{_fmt(row.get('attributed_non_oracle_choice_rate')):>10} "
                    f"{_fmt(row.get('multi_reference_case_rate')):>10} "
                    f"{refs:<48.48}"
                )
            lines.append("-" * 112)
        lines.append("Per-case stability drilldown")
        lines.append(
            f"{'case':<28} {'agent':<18} {'status':<26} {'unique':>6} {'margin':>8} "
            f"{'modal':<16} {'refs':<18} {'oracle_hit':>10}"
        )
        for row in case_rows:
            refs = ",".join(row.get("modal_reference_matches") or [])
            lines.append(
                f"{row['case_key']:<28.28} {row['agent']:<18.18} "
                f"{row.get('status', 'n/a'):<26.26} "
                f"{_fmt(row.get('unique_choice_count')):>6} "
                f"{_fmt(row.get('oracle_margin')):>8} "
                f"{_fmt(row.get('modal_choice')):<16.16} "
                f"{refs:<18.18} {_fmt(row.get('oracle_hit_rate')):>10}"
            )
    lines.append("=" * 112)
    return "\n".join(lines)


def format_stability(stability: dict[str, Any]) -> str:
    limit = stability.get("sample_limit")
    limit_text = "" if limit is None else f" sample_limit={limit}"
    case_text = _case_text(stability.get("case_keys"))
    lines = [
        (
            f"AERead stability probe: task={stability['task']} "
            f"agent={stability['agent']} repeats={stability['repeat_count']}"
            f"{limit_text}{case_text}"
        ),
        "=" * 88,
        (
            f"primary={stability['primary_metric']} direction={stability['direction']} "
            f"mean={_fmt(stability.get('primary_mean'))} "
            f"min={_fmt(stability.get('primary_min'))} "
            f"max={_fmt(stability.get('primary_max'))} "
            f"range={_fmt(stability.get('primary_range'))}"
        ),
        (
            f"parse_rate mean={_fmt(stability.get('parse_rate_mean'))} "
            f"min={_fmt(stability.get('parse_rate_min'))} "
            f"max={_fmt(stability.get('parse_rate_max'))}"
        ),
    ]
    if stability.get("accuracy_values"):
        lines.append(
            f"accuracy mean={_fmt(stability.get('accuracy_mean'))} "
            f"min={_fmt(stability.get('accuracy_min'))} "
            f"max={_fmt(stability.get('accuracy_max'))} "
            f"range={_fmt(stability.get('accuracy_range'))}"
        )
    if stability.get("unstable_case_rate") is not None:
        lines.append(f"unstable_case_rate={_fmt(stability.get('unstable_case_rate'))}")
    if stability.get("case_status_counts"):
        lines.append(
            "case_status_counts="
            + ", ".join(
                f"{status}:{count}"
                for status, count in sorted(stability["case_status_counts"].items())
            )
        )
        lines.append(
            "case_outcomes "
            f"stable_oracle={_fmt(stability.get('stable_oracle_case_rate'))} "
            f"stable_non_oracle={_fmt(stability.get('stable_non_oracle_case_rate'))} "
            f"unstable_oracle_modal={_fmt(stability.get('unstable_oracle_modal_case_rate'))} "
            f"unstable_non_oracle_modal={_fmt(stability.get('unstable_non_oracle_modal_case_rate'))} "
            f"parse_modal={_fmt(stability.get('parse_modal_case_rate'))} "
            f"mean_oracle_hit={_fmt(stability.get('mean_case_oracle_hit_rate'))}"
        )
    if stability.get("modal_reference_counts"):
        lines.append(
            "modal_reference_counts="
            + ", ".join(
                f"{reference}:{count}"
                for reference, count in sorted(stability["modal_reference_counts"].items())
            )
        )
        if stability.get("non_oracle_modal_reference_counts"):
            lines.append(
                "non_oracle_modal_reference_counts="
                + ", ".join(
                    f"{reference}:{count}"
                    for reference, count in sorted(
                        stability["non_oracle_modal_reference_counts"].items()
                    )
                )
            )
        if stability.get("attributed_non_oracle_modal_case_rate") is not None:
            lines.append(
                "attributed_non_oracle_modal_case_rate="
                f"{_fmt(stability.get('attributed_non_oracle_modal_case_rate'))}"
            )
    if stability.get("choice_reference_hit_counts"):
        lines.append(
            "choice_reference_hit_counts="
            + _format_counts(stability["choice_reference_hit_counts"])
        )
        lines.append(
            "choice_mix "
            f"non_oracle={_fmt(stability.get('non_oracle_choice_rate'))} "
            f"attributed_non_oracle={_fmt(stability.get('attributed_non_oracle_choice_rate'))} "
            f"multi_reference_cases={_fmt(stability.get('multi_reference_case_rate'))}"
        )
    case_rows = stability.get("case_stability") or []
    if case_rows:
        lines.append("-" * 88)
        lines.append(
            f"{'case':<24} {'status':<26} {'unique':>6} {'margin':>8} "
            f"{'modal':<16} {'refs':<16} {'oracle_hit':>10}"
        )
        for row in case_rows:
            oracle_hit = row.get("oracle_hit_rate")
            refs = ",".join(row.get("modal_reference_matches") or [])
            lines.append(
                f"{row['case_key']:<24.24} {row.get('status', 'n/a'):<26.26} "
                f"{row['unique_choice_count']:>6} {_fmt(row.get('oracle_margin')):>8} "
                f"{row['modal_choice']:<16.16} {refs:<16.16} {_fmt(oracle_hit):>10}"
            )
    lines.append("=" * 88)
    return "\n".join(lines)


def _fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, (int, float)):
        return f"{value:.6g}"
    return str(value)


def _sum_optional_rates(*values: Any) -> float | None:
    present = [value for value in values if isinstance(value, (int, float))]
    if not present:
        return None
    return sum(present)


def _format_counts(counts: dict[str, Any]) -> str:
    return ", ".join(
        f"{key}:{value}"
        for key, value in sorted(counts.items())
    )


def _case_text(case_keys: Any) -> str:
    if not case_keys:
        return ""
    return " cases=" + ",".join(str(case_key) for case_key in case_keys)
