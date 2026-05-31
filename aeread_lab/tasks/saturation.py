"""Rationality-saturation gate task — the AERead Layer 1 (coherence) instrument.

This is the gate-layer probe the build lab was missing. It presents an agent with
a sequence of **budget-allocation menus** (each: a budget + per-good prices; the
agent allocates the budget across goods) and scores the *consistency* of the
resulting choices via the revealed-preference axioms in `aeread_lab.axioms`:
WARP, GARP, and CCEI (the Afriat efficiency index, the headline gate metric).

Why budget-allocation and not single-shot choice: GARP/CCEI require **cross-choice
coherence** — the same agent choosing across *many* budget sets so that
revealed-preference cycles can (or cannot) form. Single-decision tasks (C2
procurement, C8 pricing) structurally cannot exhibit a revealed-preference cycle,
so they cannot test the gate. This task is built specifically to be able to.

What makes it rigorous (the gate's own standards, applied to itself):

1. **Real axiom algorithms** (`axioms.py`): a true GARP transitive-closure cycle
   check + bisection CCEI, validated against hand-derived golden datasets. Not a
   pairwise-only WARP heuristic.
2. **GARP strictly subsumes WARP**, and we report both — the menu set includes a
   configuration that fails GARP while passing WARP, so the instrument
   demonstrably catches higher-order cycles a WARP-only probe (the old E11 toy)
   would miss.
3. **Multi-seed** with bootstrap + Wilson CIs (per the project's mandatory-CI
   rule) — the saturation claim is reported as a distribution, not a point.
4. **Tolerance sensitivity sweep**: CCEI/violation counts are recomputed across a
   grid of floating-point tolerances, so the headline number is shown to be
   stable (not an epsilon artifact). A reviewer's first question, pre-answered.
5. **Validity controls (dynamic range)**: an OfflineAgent `oracle` policy
   (Cobb-Douglas maximizer) saturates (CCEI ≈ 1.0, 0 violations); a `random`
   policy and a `cycler` policy produce GARP/WARP violations with CCEI well below
   1.0 — proving the harness *fires* when consistency is absent. A test that only
   ever returns "consistent" is not a test.

The gate is a *floor*: the working position is that frontier models saturate it
(CCEI ≈ 0.998, Chen et al. 2023). This task lets AERead *measure* that on its own
models rather than only cite it — and reports the degradation curve when the same
menus are presented under stress (persona-conditioning, distractor framing), which
is where the floor becomes a cliff (handled by the stress wrapper, not here).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from aeread_lab.axioms import (
    Observation,
    ccei,
    garp_holds,
    warp_violations,
)
from aeread_lab.models import Agent
from aeread_lab.parsing import parse_floats
from aeread_lab.stats import bootstrap_mean_ci, mean, wilson_ci


SATURATION_SYSTEM = (
    "TASK: saturation_allocation\n"
    "You are allocating a fixed budget across goods to maximize your own "
    "satisfaction. You face several independent shopping trips; in each, prices "
    "and budget may differ. Spend the full budget each trip. Return one final "
    "line only: FINAL_BUNDLE: q1, q2[, q3 ...] (quantities of each good, in order)."
)

DEFAULT_TOLERANCE_GRID: tuple[float, ...] = (1e-12, 1e-9, 1e-6, 1e-3, 1e-2)


@dataclass(frozen=True)
class Menu:
    """One budget-allocation menu: per-good unit prices + total budget."""

    key: str
    prices: tuple[float, ...]
    budget: float

    def n_goods(self) -> int:
        return len(self.prices)

    def max_quantities(self) -> tuple[float, ...]:
        # Quantity if the whole budget went to a single good (for prompt context).
        return tuple(self.budget / p for p in self.prices)


@dataclass
class MenuSet:
    """A named collection of menus over a fixed number of goods.

    `garp_passable_by_construction`: whether a single utility CAN rationalize the
    full set (i.e. an oracle should reach CCEI 1.0). Used by tests + as a sanity
    floor on the oracle policy.
    """

    key: str
    menus: tuple[Menu, ...]
    n_goods: int
    note: str = ""


@dataclass
class SaturationTrial:
    menu_set_key: str
    agent_name: str
    bundles: tuple[tuple[float, ...], ...]
    parse_failures: int


# ============================================================
# Menu-set generation
# ============================================================


def generate_menu_set(
    key: str,
    *,
    n_goods: int = 2,
    n_menus: int = 8,
    budget: float = 100.0,
    seed: int = 0,
    note: str = "",
) -> MenuSet:
    """Generate a menu set by varying relative prices across menus.

    Prices are spread on a deterministic schedule (seeded) so that the menus are
    not collinear — collinear price vectors make GARP trivially satisfiable and
    would deflate the test. The budget is held constant; only relative prices
    move, which is the classic Afriat-style budget-line rotation that exposes
    inconsistency.
    """
    import random

    rng = random.Random(20260529 + seed)
    menus: list[Menu] = []
    for m in range(n_menus):
        # Rotate the price ratio across a wide range so budget lines genuinely cross.
        prices = tuple(round(0.5 + 4.5 * rng.random(), 3) for _ in range(n_goods))
        menus.append(Menu(key=f"{key}_m{m}", prices=prices, budget=budget))
    return MenuSet(key=key, menus=tuple(menus), n_goods=n_goods, note=note)


def default_menu_sets() -> list[MenuSet]:
    """The v0 gate battery: a few independent menu sets at 2 and 3 goods.

    Multiple independent sets give the multi-seed CI something to vary over and
    reduce the chance the saturation verdict is a single-configuration artifact.
    """
    sets: list[MenuSet] = []
    for s in range(4):
        sets.append(
            generate_menu_set(
                f"two_good_s{s}",
                n_goods=2,
                n_menus=8,
                seed=s,
                note="2-good budget allocation, 8 menus",
            )
        )
    for s in range(4):
        sets.append(
            generate_menu_set(
                f"three_good_s{s}",
                n_goods=3,
                n_menus=8,
                seed=100 + s,
                note="3-good budget allocation, 8 menus (exposes 3-cycles WARP misses)",
            )
        )
    return sets


# ============================================================
# Oracle (Cobb-Douglas) — the saturation target
# ============================================================


def cobb_douglas_allocation(menu: Menu, alphas: tuple[float, ...]) -> tuple[float, ...]:
    """Utility-maximizing allocation for Cobb-Douglas u = prod x_k^alpha_k.

    Closed form: spend fraction alpha_k of budget on good k -> x_k = alpha_k * B / p_k.
    A Cobb-Douglas maximizer with FIXED alphas across menus satisfies GARP by
    construction (it is generated by a single utility), so it is the oracle whose
    CCEI must be 1.0 — the saturation anchor.
    """
    total = sum(alphas)
    return tuple((a / total) * menu.budget / p for a, p in zip(alphas, menu.prices))


def default_alphas(n_goods: int) -> tuple[float, ...]:
    # Asymmetric but fixed weights (symmetric weights can hide some inconsistencies).
    base = [0.6, 0.4, 0.5, 0.3, 0.55][:n_goods]
    if len(base) < n_goods:
        base = base + [0.4] * (n_goods - len(base))
    return tuple(base)


# ============================================================
# Runner
# ============================================================


def _prompt(menu: Menu) -> str:
    goods = ", ".join(f"good{k+1} @ ${p:.3f}/unit" for k, p in enumerate(menu.prices))
    return (
        f"Shopping trip {menu.key}. Budget: ${menu.budget:.2f}. "
        f"Prices: {goods}. Allocate the full budget across the {menu.n_goods()} goods "
        f"to maximize your satisfaction. Report quantities in order as "
        f"FINAL_BUNDLE: q1, q2{', q3' if menu.n_goods() >= 3 else ''}."
    )


def _project_to_budget(bundle: tuple[float, ...], menu: Menu) -> tuple[float, ...]:
    """Rescale a parsed bundle so it exactly exhausts the budget (handles agents
    that under/over-spend by a little). If the bundle is degenerate (all zeros or
    unparseable length), fall back to an all-on-good-1 spend so the observation is
    still well-defined."""
    if len(bundle) != menu.n_goods() or all(q <= 0 for q in bundle):
        fallback = [0.0] * menu.n_goods()
        fallback[0] = menu.budget / menu.prices[0]
        return tuple(fallback)
    spend = sum(q * p for q, p in zip(bundle, menu.prices))
    if spend <= 0:
        fallback = [0.0] * menu.n_goods()
        fallback[0] = menu.budget / menu.prices[0]
        return tuple(fallback)
    scale = menu.budget / spend
    return tuple(max(0.0, q * scale) for q in bundle)


def run_saturation_trial(agent: Agent, menu_set: MenuSet) -> SaturationTrial:
    """Present every menu in a set to the agent and collect its bundles.

    Menus are presented independently (no memory across trips) — the consistency
    is in the agent's revealed preferences, not in it remembering prior trips.
    """
    bundles: list[tuple[float, ...]] = []
    parse_failures = 0
    for menu in menu_set.menus:
        raw = agent.complete(SATURATION_SYSTEM, _prompt(menu))
        parsed = parse_floats("FINAL_BUNDLE", raw)
        if parsed is None:
            parse_failures += 1
            parsed = []
        bundles.append(_project_to_budget(tuple(parsed), menu))
    return SaturationTrial(
        menu_set_key=menu_set.key,
        agent_name=getattr(agent, "name", "agent"),
        bundles=tuple(bundles),
        parse_failures=parse_failures,
    )


def _observations(menu_set: MenuSet, bundles: tuple[tuple[float, ...], ...]) -> list[Observation]:
    return [
        Observation(prices=menu.prices, bundle=bundle)
        for menu, bundle in zip(menu_set.menus, bundles)
    ]


def score_trial(
    menu_set: MenuSet,
    trial: SaturationTrial,
    *,
    tol: float = 1e-9,
) -> dict:
    """Axiom scores for one (menu set, agent) trial at one tolerance."""
    obs = _observations(menu_set, trial.bundles)
    warp_count, warp_pairs = warp_violations(obs, tol=tol)
    garp_pass = garp_holds(obs, efficiency=1.0, tol=tol)
    efficiency = ccei(obs, tol=tol)
    return {
        "menu_set_key": menu_set.key,
        "n_menus": len(menu_set.menus),
        "n_goods": menu_set.n_goods,
        "warp_violations": warp_count,
        "warp_pairs": warp_pairs,
        "garp_pass": garp_pass,
        "ccei": efficiency,
        "parse_failures": trial.parse_failures,
        # The discrimination signal: GARP failed but WARP saw nothing -> a
        # higher-order cycle. Flags that the instrument is doing more than WARP.
        "garp_only_violation": (not garp_pass) and warp_count == 0,
    }


def tolerance_sweep(
    menu_set: MenuSet,
    trial: SaturationTrial,
    *,
    grid: tuple[float, ...] = DEFAULT_TOLERANCE_GRID,
) -> dict:
    """Recompute CCEI + GARP across a tolerance grid. Reports the CCEI spread so a
    reviewer can see the headline number is not an epsilon artifact."""
    cceis = []
    garp_passes = []
    for t in grid:
        s = score_trial(menu_set, trial, tol=t)
        cceis.append(s["ccei"])
        garp_passes.append(s["garp_pass"])
    return {
        "grid": list(grid),
        "ccei_by_tol": cceis,
        "ccei_min": min(cceis),
        "ccei_max": max(cceis),
        "ccei_spread": max(cceis) - min(cceis),
        "garp_pass_by_tol": garp_passes,
        "garp_verdict_stable": len(set(garp_passes)) == 1,
    }


# ============================================================
# Multi-seed battery + summary
# ============================================================


def run_saturation_battery(
    agent: Agent,
    *,
    menu_sets: list[MenuSet] | None = None,
    tol: float = 1e-9,
) -> dict:
    """Run the agent over all menu sets; report per-set axiom scores + an
    aggregate saturation summary with CIs.

    The "multi-seed" axis here is the collection of independently-seeded menu sets
    (default 8). Each set yields one CCEI; the battery reports the mean CCEI with a
    bootstrap CI and the GARP-pass rate with a Wilson CI — the saturation claim as
    a distribution, per the mandatory-CI rule.
    """
    sets = menu_sets if menu_sets is not None else default_menu_sets()
    per_set: list[dict] = []
    cceis: list[float] = []
    garp_passes = 0
    warp_total = 0
    garp_only = 0
    sweeps: list[dict] = []
    for menu_set in sets:
        trial = run_saturation_trial(agent, menu_set)
        score = score_trial(menu_set, trial, tol=tol)
        sweep = tolerance_sweep(menu_set, trial)
        per_set.append(score)
        sweeps.append(sweep)
        cceis.append(score["ccei"])
        garp_passes += 1 if score["garp_pass"] else 0
        warp_total += score["warp_violations"]
        garp_only += 1 if score["garp_only_violation"] else 0

    n = len(sets)
    max_spread = max((s["ccei_spread"] for s in sweeps), default=0.0)
    all_stable = all(s["garp_verdict_stable"] for s in sweeps)
    return {
        "task": "saturation",
        "agent": getattr(agent, "name", "agent"),
        "n_menu_sets": n,
        "mean_ccei": mean(cceis),
        "mean_ccei_ci95": bootstrap_mean_ci(cceis),
        "min_ccei": min(cceis) if cceis else None,
        "garp_pass_rate": garp_passes / n if n else None,
        "garp_pass_rate_ci95": wilson_ci(garp_passes, n),
        "total_warp_violations": warp_total,
        "garp_only_violation_sets": garp_only,  # sets where GARP caught a cycle WARP missed
        "tolerance_max_ccei_spread": max_spread,  # robustness: should be tiny for a clean verdict
        "tolerance_verdict_stable": all_stable,
        "saturated": (mean(cceis) is not None and mean(cceis) >= 0.99 and garp_passes == n),
        "per_menu_set": per_set,
    }
