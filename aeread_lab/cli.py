from __future__ import annotations

import argparse
import json
from typing import Any

from aeread_lab.models import OfflineAgent, build_agent
from aeread_lab.tasks import (
    run_pricing_game,
    run_procurement_game,
    run_regime_battery,
    run_scam_arena,
)


TASKS = ("regime", "procurement", "pricing", "scam", "all")


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
    parser.add_argument("--json", action="store_true", help="Print raw JSON only.")
    args = parser.parse_args(argv)

    agent = build_agent(args.agent)
    results: list[dict[str, Any]] = []
    selected = [args.task] if args.task != "all" else ["regime", "procurement", "pricing", "scam"]

    for task in selected:
        if task == "regime":
            results.append(run_regime_battery(agent))
        elif task == "procurement":
            results.append(run_procurement_game(agent))
        elif task == "pricing":
            results.append(run_pricing_game(agent))
        elif task == "scam":
            attacker = build_agent(args.attacker)
            results.append(run_scam_arena(defender=agent, attacker=attacker))

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
