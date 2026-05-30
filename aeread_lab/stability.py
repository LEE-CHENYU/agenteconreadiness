from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from aeread_lab.reporting import extract_metric, parse_rate
from aeread_lab.stats import mean


def summarize_stability_runs(
    *,
    task: str,
    agent_name: str,
    results: list[dict[str, Any]],
    sample_limit: int | None = None,
) -> dict[str, Any]:
    if not results:
        raise ValueError("stability runs require at least one result")

    metric_name, _, direction = extract_metric(results[0])
    metric_values = [_metric_value(result, metric_name) for result in results]
    present_metrics = [value for value in metric_values if value is not None]
    parse_values = [parse_rate(result) for result in results]
    present_parse = [value for value in parse_values if value is not None]
    accuracy_values = [
        result.get("accuracy")
        for result in results
        if isinstance(result.get("accuracy"), (int, float))
    ]
    case_stability = _case_stability(results)
    case_status_counts = Counter(row["status"] for row in case_stability)
    case_count = len(case_stability)
    oracle_hit_rates = [
        row["oracle_hit_rate"]
        for row in case_stability
        if isinstance(row.get("oracle_hit_rate"), (int, float))
    ]

    return {
        "task": task,
        "agent": agent_name,
        "sample_limit": sample_limit,
        "repeat_count": len(results),
        "primary_metric": metric_name,
        "direction": direction,
        "primary_values": metric_values,
        "primary_mean": mean(present_metrics),
        "primary_min": min(present_metrics) if present_metrics else None,
        "primary_max": max(present_metrics) if present_metrics else None,
        "primary_range": (
            max(present_metrics) - min(present_metrics) if len(present_metrics) >= 2 else 0.0
        ),
        "parse_rate_values": parse_values,
        "parse_rate_mean": mean(present_parse),
        "parse_rate_min": min(present_parse) if present_parse else None,
        "parse_rate_max": max(present_parse) if present_parse else None,
        "accuracy_values": accuracy_values,
        "accuracy_mean": mean(accuracy_values),
        "accuracy_min": min(accuracy_values) if accuracy_values else None,
        "accuracy_max": max(accuracy_values) if accuracy_values else None,
        "accuracy_range": (
            max(accuracy_values) - min(accuracy_values) if len(accuracy_values) >= 2 else 0.0
        ),
        "unstable_case_rate": _unstable_case_rate(case_stability),
        "case_status_counts": dict(sorted(case_status_counts.items())),
        "stable_oracle_case_rate": _case_status_rate(
            case_status_counts, case_count, "stable_oracle"
        ),
        "stable_non_oracle_case_rate": _case_status_rate(
            case_status_counts, case_count, "stable_non_oracle"
        ),
        "unstable_oracle_modal_case_rate": _case_status_rate(
            case_status_counts, case_count, "unstable_oracle_modal"
        ),
        "unstable_non_oracle_modal_case_rate": _case_status_rate(
            case_status_counts, case_count, "unstable_non_oracle_modal"
        ),
        "parse_modal_case_rate": _case_status_rate(case_status_counts, case_count, "parse_modal"),
        "mean_case_oracle_hit_rate": mean(oracle_hit_rates),
        "case_stability": case_stability,
        "runs": results,
    }


def _metric_value(result: dict[str, Any], metric_name: str) -> float | None:
    value = result.get(metric_name)
    return value if isinstance(value, (int, float)) else None


def _case_stability(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    choices_by_case: dict[str, list[str]] = defaultdict(list)
    oracle_by_case: dict[str, str | None] = {}
    margin_by_case: dict[str, float] = {}
    for result in results:
        trials = result.get("trials")
        if not isinstance(trials, list):
            continue
        for idx, trial in enumerate(trials):
            if not isinstance(trial, dict):
                continue
            case_key = _trial_case_key(trial, idx)
            choice = _choice_label(_trial_choice(trial))
            choices_by_case[case_key].append(choice)
            oracle = _trial_oracle(trial)
            if oracle is not None and case_key not in oracle_by_case:
                oracle_by_case[case_key] = _choice_label(oracle)
            margin = trial.get("oracle_margin")
            if isinstance(margin, (int, float)) and case_key not in margin_by_case:
                margin_by_case[case_key] = float(margin)

    rows: list[dict[str, Any]] = []
    for case_key in sorted(choices_by_case):
        choices = choices_by_case[case_key]
        counts = Counter(choices)
        modal_choice, modal_count = counts.most_common(1)[0]
        oracle_choice = oracle_by_case.get(case_key)
        parse_fail_rate = counts.get("PARSE_FAIL", 0) / len(choices)
        oracle_hit_rate = (
            sum(choice == oracle_choice for choice in choices) / len(choices)
            if oracle_choice is not None
            else None
        )
        rows.append(
            {
                "case_key": case_key,
                "choice_counts": dict(sorted(counts.items())),
                "unique_choice_count": len(counts),
                "modal_choice": modal_choice,
                "modal_choice_rate": modal_count / len(choices),
                "oracle_choice": oracle_choice,
                "oracle_margin": margin_by_case.get(case_key),
                "oracle_hit_rate": oracle_hit_rate,
                "parse_fail_rate": parse_fail_rate,
                "status": _case_status(
                    unique_choice_count=len(counts),
                    modal_choice=modal_choice,
                    oracle_choice=oracle_choice,
                    parse_fail_rate=parse_fail_rate,
                ),
            }
        )
    return rows


def _case_status(
    *,
    unique_choice_count: int,
    modal_choice: str,
    oracle_choice: str | None,
    parse_fail_rate: float,
) -> str:
    if modal_choice == "PARSE_FAIL" and parse_fail_rate >= 0.5:
        return "parse_modal"
    if oracle_choice is None:
        return "unstable_unscored" if unique_choice_count > 1 else "stable_unscored"
    if unique_choice_count == 1:
        return "stable_oracle" if modal_choice == oracle_choice else "stable_non_oracle"
    return "unstable_oracle_modal" if modal_choice == oracle_choice else "unstable_non_oracle_modal"


def _trial_case_key(trial: dict[str, Any], idx: int) -> str:
    case = trial.get("case")
    if isinstance(case, dict):
        for key in ("key", "case_key", "id", "real_case"):
            value = case.get(key)
            if value is not None:
                return str(value)
    for key in ("case_key", "key", "real_case"):
        value = trial.get(key)
        if value is not None:
            return str(value)
    return f"trial_{idx + 1}"


def _trial_choice(trial: dict[str, Any]) -> Any:
    preferred = (
        "chosen_trade",
        "chosen_action",
        "chosen_option",
        "chosen_choice",
        "chosen_supplier_id",
        "chosen_mechanism_id",
        "chosen_contract_id",
        "chosen_bundle",
        "chosen_label",
    )
    for key in preferred:
        if key in trial:
            return trial.get(key)

    ignored = {"chosen_revenue", "chosen_expected_profit", "chosen_surplus", "chosen_score"}
    for key in sorted(trial):
        if key.startswith("chosen_") and key not in ignored:
            return trial.get(key)
    return None


def _trial_oracle(trial: dict[str, Any]) -> Any:
    preferred = (
        "principal_trade",
        "oracle_trade",
        "oracle_action",
        "oracle_choice",
        "oracle_supplier_id",
        "oracle_mechanism_id",
        "oracle_contract_id",
        "oracle_bundle",
        "expected_trade",
        "expected_action",
    )
    for key in preferred:
        if key in trial:
            return trial.get(key)
    return None


def _choice_label(value: Any) -> str:
    if value is None:
        return "PARSE_FAIL"
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (list, tuple)):
        return ",".join(_choice_label(item) for item in value)
    return str(value)


def _unstable_case_rate(case_stability: list[dict[str, Any]]) -> float | None:
    if not case_stability:
        return None
    unstable = sum(row["unique_choice_count"] > 1 for row in case_stability)
    return unstable / len(case_stability)


def _case_status_rate(status_counts: Counter, case_count: int, status: str) -> float | None:
    if case_count == 0:
        return None
    return status_counts.get(status, 0) / case_count
