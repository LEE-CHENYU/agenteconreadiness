from __future__ import annotations

from typing import Any


PRIMARY_METRICS = {
    "regime": ("mean_absolute_error", "lower"),
    "alignment_tax": ("mean_objective_regret", "lower"),
    "principal_inference": ("mean_fraction_error", "lower"),
    "portfolio": ("mean_utility_regret", "lower"),
    "revealed_allocation": ("mean_utility_regret", "lower"),
    "ambiguity": ("mean_robust_regret", "lower"),
    "bargaining": ("mean_grade_error", "lower"),
    "belief_bargaining": ("mean_expected_surplus_gap", "lower"),
    "market": ("mean_equilibrium_price_gap", "lower"),
    "matching": ("mean_score_regret", "lower"),
    "screening": ("mean_score_regret", "lower"),
    "moral_hazard": ("mean_profit_regret", "lower"),
    "auction": ("mean_reserve_error", "lower"),
    "common_value": ("mean_profit_regret", "lower"),
    "mechanism": ("mean_score_regret", "lower"),
    "strategic_drift": ("drift_rate", "lower"),
    "exploration": ("mean_expected_value_gap", "lower"),
    "experiment_design": ("mean_expected_value_gap", "lower"),
    "retail": ("mean_order_error", "lower"),
    "procurement": ("accuracy", "higher"),
    "pricing": ("mean_revenue_gap", "lower"),
    "adversarial_scam": ("mean_overpayment", "lower"),
    "supplier_scam": ("mean_constrained_final_cash_regret", "lower"),
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
    lines = [
        f"AERead model sweep: task={sweep['task']} agents={', '.join(sweep['agents'])}{limit_text}",
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
