from __future__ import annotations

from typing import Any


PRIMARY_METRICS = {
    "regime": ("mean_absolute_error", "lower"),
    "principal_inference": ("mean_fraction_error", "lower"),
    "portfolio": ("mean_utility_regret", "lower"),
    "ambiguity": ("mean_robust_regret", "lower"),
    "bargaining": ("mean_grade_error", "lower"),
    "belief_bargaining": ("mean_expected_surplus_gap", "lower"),
    "market": ("mean_equilibrium_price_gap", "lower"),
    "auction": ("mean_reserve_error", "lower"),
    "mechanism": ("mean_score_regret", "lower"),
    "strategic_drift": ("drift_rate", "lower"),
    "exploration": ("mean_expected_value_gap", "lower"),
    "experiment_design": ("mean_expected_value_gap", "lower"),
    "retail": ("mean_ruin_probability", "lower"),
    "procurement": ("accuracy", "higher"),
    "pricing": ("mean_revenue_gap", "lower"),
    "adversarial_scam": ("mean_overpayment", "lower"),
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
                }
            )
    return rows


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
    lines = [
        f"AERead model sweep: task={sweep['task']} agents={', '.join(sweep['agents'])}",
        "=" * 88,
        f"{'task':<18} {'rank':>4} {'agent':<18} {'metric':<24} {'value':>12} {'direction':<7}",
        "-" * 88,
    ]
    for row in rows:
        value = "n/a" if row["value"] is None else f"{row['value']:.6g}"
        lines.append(
            f"{row['task']:<18} {row['rank']:>4} {row['agent']:<18} "
            f"{row['metric']:<24} {value:>12} {row['direction']:<7}"
        )
    lines.append("=" * 88)
    return "\n".join(lines)
