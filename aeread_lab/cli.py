from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from aeread_lab.cache import CachedAgent, DEFAULT_CACHE_DIR
from aeread_lab.models import build_agent
from aeread_lab.reporting import format_sweep
from aeread_lab.runner import run_sweep, run_tasks


TASKS = (
    "regime",
    "principal_inference",
    "ambiguity",
    "bargaining",
    "belief_bargaining",
    "market",
    "auction",
    "mechanism",
    "strategic_drift",
    "exploration",
    "retail",
    "procurement",
    "pricing",
    "scam",
    "all",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AERead build-lab runner")
    parser.add_argument("--task", choices=TASKS, default="all")
    parser.add_argument(
        "--agent",
        default="offline:oracle",
        help="offline:<policy> or openai:{gpt-5.5,mini,nano}. Bare gpt-5.5/mini/nano also works.",
    )
    parser.add_argument(
        "--attacker",
        default="offline:credulous",
        help="Attacker for scam arena. Defaults to offline:credulous for no API spend.",
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Run a multi-agent sweep instead of a single agent report.",
    )
    parser.add_argument(
        "--agents",
        default="openai:gpt-5.5,openai:mini,openai:nano",
        help="Comma-separated agent specs for --sweep.",
    )
    parser.add_argument(
        "--cache-dir",
        default=str(DEFAULT_CACHE_DIR),
        help="Response cache directory for sweeps and OpenAI calls.",
    )
    parser.add_argument("--no-cache", action="store_true", help="Disable response cache.")
    parser.add_argument("--json", action="store_true", help="Print raw JSON only.")
    args = parser.parse_args(argv)

    def _wrap(agent):
        return CachedAgent(agent, cache_dir=Path(args.cache_dir), enabled=not args.no_cache)

    if args.sweep:
        specs = [item.strip() for item in args.agents.split(",") if item.strip()]
        payload = run_sweep(
            task=args.task,
            agent_specs=specs,
            attacker_spec=args.attacker,
            wrap_cache=_wrap,
        )
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(format_sweep(payload))
        return 0

    agent = build_agent(args.agent)
    attacker = build_agent(args.attacker)
    if not args.no_cache:
        agent = _wrap(agent)
        attacker = _wrap(attacker)
    results: list[dict[str, Any]] = run_tasks(args.task, agent, attacker=attacker)
    payload = {"agent": agent.name, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_human(payload)
    return 0


def _print_human(payload: dict[str, Any]) -> None:
    print(f"AERead build-lab report for {payload['agent']}")
    print("=" * 72)
    for result in payload["results"]:
        task = result["task"]
        if task == "regime":
            print(
                f"regime: n={result['n_trials']} mean_abs_error="
                f"{_fmt(result['mean_absolute_error'])} "
                f"ci95={_fmt_ci(result.get('mean_absolute_error_ci95'))} "
                f"destroy={result.get('wealth_destruction_rate', 0.0):.2f}"
            )
            for key, row in result["by_regime"].items():
                print(
                    f"  {key:<6} error={_fmt(row['mean_absolute_error'])} "
                    f"ci95={_fmt_ci(row.get('mean_absolute_error_ci95'))} "
                    f"destroy={row['wealth_destruction_rate']:.2f} "
                    f"destroy_ci={_fmt_ci(row.get('wealth_destruction_ci95'))} "
                    f"case={row['real_case']}"
                )
        elif task == "principal_inference":
            print(
                f"principal_inference: n={result['n_trials']} fraction_error="
                f"{_fmt(result['mean_fraction_error'])} "
                f"ci95={_fmt_ci(result.get('mean_fraction_error_ci95'))} "
                f"generic_gap={_fmt(result['generic_mean_fraction_gap'])}"
            )
        elif task == "ambiguity":
            print(
                f"ambiguity: n={result['n_trials']} robust_regret="
                f"{_fmt(result['mean_robust_regret'])} "
                f"ci95={_fmt_ci(result.get('mean_robust_regret_ci95'))} "
                f"reference_miss={result['reference_prior_miss_rate']:.2f}"
            )
        elif task == "bargaining":
            print(
                f"bargaining: n={result['n_trials']} agreement="
                f"{result['agreement_rate']:.2f} mean_grade_error="
                f"{_fmt(result['mean_grade_error'])} "
                f"ci95={_fmt_ci(result.get('mean_grade_error_ci95'))} "
                f"gate_gap={_fmt(result['mean_gate_surplus_gap'])}"
            )
        elif task == "belief_bargaining":
            print(
                f"belief_bargaining: n={result['n_trials']} surplus_gap="
                f"{_fmt(result['mean_expected_surplus_gap'])} "
                f"ci95={_fmt_ci(result.get('mean_expected_surplus_gap_ci95'))} "
                f"cue_miss={result['cue_switch_miss_rate']:.2f}"
            )
        elif task == "market":
            print(
                f"market: n={result['n_trials']} eq_price_gap="
                f"{_fmt(result['mean_equilibrium_price_gap'])} "
                f"ci95={_fmt_ci(result.get('mean_equilibrium_price_gap_ci95'))} "
                f"collusion_index={_fmt(result['mean_collusion_index'])} "
                f"collusion_rate={result['collusion_rate']:.2f}"
            )
        elif task == "auction":
            print(
                f"auction: n={result['n_trials']} mean_reserve_error="
                f"{_fmt(result['mean_reserve_error'])} "
                f"ci95={_fmt_ci(result.get('mean_reserve_error_ci95'))}"
            )
        elif task == "mechanism":
            print(
                f"mechanism: n={result['n_trials']} score_regret="
                f"{_fmt(result['mean_score_regret'])} "
                f"ci95={_fmt_ci(result.get('mean_score_regret_ci95'))} "
                f"revenue_miss={result['revenue_default_miss_rate']:.2f} "
                f"risk_blind_miss={result['risk_blind_miss_rate']:.2f}"
            )
        elif task == "strategic_drift":
            print(
                f"strategic_drift: n={result['n_trials']} drift_rate="
                f"{_fmt(result['drift_rate'])} "
                f"ci95={_fmt_ci(result.get('drift_rate_ci95'))}"
            )
            for key, row in result["by_case"].items():
                print(
                    f"  {key:<24} drift={row['drift_rate']:.2f} "
                    f"first_drift={row['first_drift_round']} case={row['real_case']}"
                )
        elif task == "exploration":
            print(
                f"exploration: n={result['n_trials']} accuracy={result['accuracy']:.2f} "
                f"ev_gap={_fmt(result['mean_expected_value_gap'])} "
                f"ci95={_fmt_ci(result.get('mean_expected_value_gap_ci95'))} "
                f"miss={result['exploration_miss_rate']:.2f}"
            )
        elif task == "retail":
            print(
                f"retail: n={result['n_trials']} cash_gap="
                f"{_fmt(result['mean_expected_cash_gap'])} "
                f"order_error={_fmt(result['mean_order_error'])} "
                f"ruin_prob={_fmt(result['mean_ruin_probability'])} "
                f"ruin_ci={_fmt_ci(result.get('mean_ruin_probability_ci95'))}"
            )
        elif task == "procurement":
            print(
                f"procurement: n={result['n_trials']} accuracy={result['accuracy']:.2f} "
                f"mean_regret={result['mean_regret']:.3f}"
            )
        elif task == "pricing":
            print(
                f"pricing: n={result['n_trials']} mean_revenue_gap="
                f"{_fmt(result['mean_revenue_gap'])}"
            )
            for key, row in result["by_condition"].items():
                print(f"  {key:<9} gap={_fmt(row['mean_revenue_gap'])}")
        elif task == "adversarial_scam":
            controls = result["controls"]
            print(
                f"scam: n={result['n_trials']} mean_overpay="
                f"{_fmt(result['mean_overpayment'])} susceptibility="
                f"{_fmt(result['mean_susceptibility'])} instrument_fires="
                f"{result['instrument_fires']}"
            )
            print(
                "  controls: credulous_overpay="
                f"{controls['credulous_mean_overpayment']:.2f}, skeptical_oracle=0.00"
            )
    print("=" * 72)
    print("OpenAI-only API path: --agent openai:gpt-5.5, --agent openai:mini, or --agent openai:nano")


def _fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def _fmt_ci(value: object) -> str:
    if not value:
        return "n/a"
    lo, hi = value
    return f"[{lo:.4f},{hi:.4f}]"


if __name__ == "__main__":
    raise SystemExit(main())
