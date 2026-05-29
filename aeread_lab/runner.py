from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from aeread_lab.models import Agent, build_agent
from aeread_lab.tasks import (
    run_auction_game,
    run_bargaining_game,
    run_market_game,
    run_pricing_game,
    run_procurement_game,
    run_regime_battery,
    run_scam_arena,
)


TASK_ORDER = ("regime", "bargaining", "market", "auction", "procurement", "pricing", "scam")


def run_task(task: str, agent: Agent, attacker: Agent | None = None) -> dict[str, Any]:
    if task == "regime":
        return run_regime_battery(agent)
    if task == "bargaining":
        return run_bargaining_game(agent)
    if task == "market":
        return run_market_game(agent)
    if task == "auction":
        return run_auction_game(agent)
    if task == "procurement":
        return run_procurement_game(agent)
    if task == "pricing":
        return run_pricing_game(agent)
    if task == "scam":
        return run_scam_arena(defender=agent, attacker=attacker or build_agent("offline:credulous"))
    raise ValueError(f"Unknown task: {task}")


def expand_tasks(task: str) -> list[str]:
    return list(TASK_ORDER) if task == "all" else [task]


def run_tasks(task: str, agent: Agent, attacker: Agent | None = None) -> list[dict[str, Any]]:
    return [run_task(t, agent, attacker=attacker) for t in expand_tasks(task)]


def run_sweep(
    *,
    task: str,
    agent_specs: Iterable[str],
    attacker_spec: str = "offline:credulous",
    wrap_cache=None,
) -> dict[str, Any]:
    attacker = build_agent(attacker_spec)
    if wrap_cache is not None:
        attacker = wrap_cache(attacker)
    specs = list(agent_specs)
    runs = []
    for spec in specs:
        agent = build_agent(spec)
        if wrap_cache is not None:
            agent = wrap_cache(agent)
        runs.append({"agent": agent.name, "results": run_tasks(task, agent, attacker=attacker)})
    return {"task": task, "agents": specs, "runs": runs}
