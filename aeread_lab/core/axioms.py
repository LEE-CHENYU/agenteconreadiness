"""Revealed-preference axiom core for the AERead rationality-saturation gate.

This module is the load-bearing instrument behind the methodology's **gate**
(Layer 1 / coherence). It computes, from a set of (price vector, chosen bundle)
observations, whether the choices are *rationalizable by some utility* and — if
not — *how far* they are from rationalizable. These are the classical
revealed-preference consistency tests:

- **WARP** (Weak Axiom of Revealed Preference): no *pairwise* preference
  reversal. Cheap, but blind to higher-order cycles.
- **GARP** (Generalized Axiom of Revealed Preference): no cycle of *any* length
  in the revealed-preference relation. Afriat's theorem: choices satisfy GARP
  **iff** a non-satiated, continuous, concave, monotone utility rationalizes
  them. This is the operational meaning of "does *some* utility exist?".
- **CCEI** (Critical Cost Efficiency Index / Afriat efficiency index): the
  largest efficiency level e in [0, 1] at which the choices satisfy GARP. 1.0 =
  perfectly consistent; lower = more wasteful/incoherent. This is the *degree*
  of violation Chen et al. 2023 report (frontier LLMs ≈ 0.998), and the metric
  that makes the gate comparable to the literature.
- **transitivity / dominance / monotonicity**: simpler discrete-choice axioms,
  here as standalone checks for menu-choice tasks that are not budget-allocation.

Design notes (the rigor that matters for a reviewer):
- Pure stdlib (the package declares no dependencies). O(n^3) Warshall closure +
  O(log) bisection for CCEI — fine for the menu counts a gate task uses.
- "Directly revealed preferred at efficiency e": bundle x_i is revealed
  preferred to x_j when the agent could have afforded x_j at menu i's prices
  spending only fraction e of what it actually spent —
      e * (p_i · x_i) >= p_i · x_j.
  At e = 1 this is the standard definition; CCEI relaxes e downward until the
  cyclic-consistency check passes.
- A *strict* direct revealed preference (used for the GARP violation test) holds
  when x_j was affordable with strictly slack budget: e * (p_i · x_i) > p_i · x_j.
- Floating-point tolerances are explicit arguments (`tol`), and the saturation
  task runs a sensitivity sweep over them rather than hard-coding one value —
  the violation count must not be an artifact of an arbitrary epsilon.

Validated against hand-derived golden datasets in tests/test_axioms.py:
a strict 2-cycle (CCEI 0.8), a Cobb-Douglas maximizer (CCEI 1.0), and a pure
3-cycle that satisfies WARP but violates GARP (CCEI 0.75) — the last proves GARP
strictly subsumes WARP.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


Vector = Sequence[float]


def _dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass(frozen=True)
class Observation:
    """One revealed-preference observation: prices faced + bundle chosen.

    `prices[k]` is the unit price of good k; `bundle[k]` is the quantity chosen.
    Expenditure is prices · bundle. The budget is implicitly that expenditure
    (the agent is assumed to spend its budget; partial spend is handled by the
    efficiency relaxation, not modeled separately).
    """

    prices: tuple[float, ...]
    bundle: tuple[float, ...]

    def expenditure(self) -> float:
        return _dot(self.prices, self.bundle)


# ============================================================
# Revealed-preference relation
# ============================================================


def _direct_revealed_matrix(
    obs: Sequence[Observation],
    efficiency: float,
    *,
    strict: bool,
    tol: float,
) -> list[list[bool]]:
    """R0[i][j] = x_i is directly revealed (weakly/strictly) preferred to x_j
    at the given efficiency level.

    weak (strict=False):   efficiency * (p_i·x_i) >= p_i·x_j - tol
    strict (strict=True):  efficiency * (p_i·x_i) >  p_i·x_j + tol
    """
    n = len(obs)
    matrix = [[False] * n for _ in range(n)]
    for i in range(n):
        budget_i = efficiency * obs[i].expenditure()
        for j in range(n):
            if i == j:
                continue
            cost_of_j_at_i = _dot(obs[i].prices, obs[j].bundle)
            if strict:
                matrix[i][j] = budget_i > cost_of_j_at_i + tol
            else:
                matrix[i][j] = budget_i >= cost_of_j_at_i - tol
    return matrix


def _transitive_closure(matrix: list[list[bool]]) -> list[list[bool]]:
    """Warshall transitive closure (O(n^3))."""
    n = len(matrix)
    closure = [row[:] for row in matrix]
    for k in range(n):
        ck = closure[k]
        for i in range(n):
            if closure[i][k]:
                ci = closure[i]
                for j in range(n):
                    if ck[j]:
                        ci[j] = True
    return closure


# ============================================================
# WARP
# ============================================================


def warp_violations(
    obs: Sequence[Observation],
    *,
    tol: float = 1e-9,
    bundle_distance_tol: float = 1e-9,
) -> tuple[int, list[tuple[int, int]]]:
    """Count Weak Axiom of Revealed Preference violations across all menu pairs.

    A pair (i, j) violates WARP when each bundle is (weakly) directly revealed
    preferred to the other AND the bundles meaningfully differ — i.e. a direct
    pairwise preference reversal. WARP is necessary but not sufficient for
    rationalizability (it misses cycles of length >= 3 — see GARP).

    Returns (count, list_of_violating_(i, j)_pairs with i < j).
    """
    n = len(obs)
    weak = _direct_revealed_matrix(obs, 1.0, strict=False, tol=tol)
    violations: list[tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if not (weak[i][j] and weak[j][i]):
                continue
            # Bundles must actually differ (else revealed indifference, not a violation).
            dist = sum(abs(a - b) for a, b in zip(obs[i].bundle, obs[j].bundle))
            if dist <= bundle_distance_tol:
                continue
            violations.append((i, j))
    return len(violations), violations


# ============================================================
# GARP
# ============================================================


def garp_holds(obs: Sequence[Observation], *, efficiency: float = 1.0, tol: float = 1e-9) -> bool:
    """Generalized Axiom of Revealed Preference at the given efficiency level.

    GARP: if x_i is revealed preferred to x_j (directly or transitively), then
    x_j is NOT *strictly* directly revealed preferred to x_i. A failure is a
    cost-inefficient cycle. By Afriat's theorem, GARP at efficiency 1 holds iff
    a well-behaved utility rationalizes the choices.

    The transitive closure captures cycles of arbitrary length — this is what
    makes GARP strictly stronger than WARP (which only sees pairwise reversals).
    """
    n = len(obs)
    weak = _direct_revealed_matrix(obs, efficiency, strict=False, tol=tol)
    strict = _direct_revealed_matrix(obs, efficiency, strict=True, tol=tol)
    reachable = _transitive_closure(weak)
    for i in range(n):
        for j in range(n):
            if i != j and reachable[i][j] and strict[j][i]:
                return False
    return True


def ccei(obs: Sequence[Observation], *, tol: float = 1e-9, iters: int = 60) -> float:
    """Critical Cost Efficiency Index (Afriat efficiency index) in [0, 1].

    The largest efficiency e such that the choices satisfy GARP at e. Computed by
    bisection on e (GARP-at-e is monotone in e: passing at e implies passing at
    any e' < e, because shrinking the revealed budget only removes preference
    edges). 1.0 = perfectly rationalizable; the shortfall 1 - CCEI is the
    fraction of budget the agent "wasted" relative to a coherent optimizer.

    `iters` bisection steps give ~2^-iters resolution (60 → ~1e-18, capped by
    float precision; 30 is plenty in practice).
    """
    if not obs:
        return 1.0
    if garp_holds(obs, efficiency=1.0, tol=tol):
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if garp_holds(obs, efficiency=mid, tol=tol):
            lo = mid
        else:
            hi = mid
    return lo


# ============================================================
# Discrete-choice axioms (for non-budget menu tasks)
# ============================================================


def transitivity_violations(
    pairwise_choice: dict[tuple[int, int], int],
    n_items: int,
) -> tuple[int, list[tuple[int, int, int]]]:
    """Count intransitive triples from a pairwise-choice map.

    `pairwise_choice[(a, b)]` = the item chosen when offered {a, b} (must be a or
    b). A triple (a, b, c) is intransitive when a≻b, b≻c, but not a≻c (i.e. c≻a) —
    a preference cycle. Returns (count, list_of_(a, b, c)_cycles).

    Defined over the strict-preference tournament; pairs with no recorded choice
    are skipped (an incomplete tournament simply yields fewer testable triples).
    """

    def prefers(x: int, y: int) -> bool | None:
        key = (x, y) if (x, y) in pairwise_choice else ((y, x) if (y, x) in pairwise_choice else None)
        if key is None:
            return None
        return pairwise_choice[key] == x

    cycles: list[tuple[int, int, int]] = []
    for a in range(n_items):
        for b in range(n_items):
            for c in range(n_items):
                if len({a, b, c}) != 3:
                    continue
                if a < c:  # canonical-order the (a, c) endpoints to avoid double counting
                    ab, bc, ca = prefers(a, b), prefers(b, c), prefers(c, a)
                    if ab and bc and ca:  # a≻b, b≻c, c≻a → cycle
                        cycles.append((a, b, c))
    return len(cycles), cycles


def dominated_choice_violations(
    menus: Sequence[Sequence[Vector]],
    choices: Sequence[int],
    *,
    tol: float = 1e-9,
) -> tuple[int, list[int]]:
    """Count menus where the agent chose a (weakly) dominated option.

    Each menu is a list of option attribute-vectors (higher is better on every
    attribute). Option u dominates v if u >= v on all attributes and u > v on at
    least one. Choosing a dominated option is a hard rationality failure (no
    monotone utility rationalizes it). Returns (count, list_of_violating_menu_indices).
    """
    violations: list[int] = []
    for idx, (menu, chosen) in enumerate(zip(menus, choices)):
        picked = menu[chosen]
        for other in menu:
            if other is picked:
                continue
            ge_all = all(o >= p - tol for o, p in zip(other, picked))
            gt_some = any(o > p + tol for o, p in zip(other, picked))
            if ge_all and gt_some:
                violations.append(idx)
                break
    return len(violations), violations


def monotonicity_violations(
    budgets: Sequence[float],
    achieved_utility: Sequence[float],
    *,
    tol: float = 1e-9,
) -> tuple[int, list[tuple[int, int]]]:
    """Count budget-monotonicity violations: a larger budget yielding strictly
    less achieved utility. For pairs (i, j) with budget_i > budget_j, a coherent
    agent's achieved utility must satisfy u_i >= u_j. Returns (count, pairs)."""
    n = len(budgets)
    violations: list[tuple[int, int]] = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if budgets[i] > budgets[j] + tol and achieved_utility[i] < achieved_utility[j] - tol:
                violations.append((i, j))
    return len(violations), violations
