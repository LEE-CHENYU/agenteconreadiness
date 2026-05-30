from __future__ import annotations

import random
from dataclasses import dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float


PRICING_SYSTEM = (
    "TASK: pricing_price\n"
    "Choose a price. Return one final line only: FINAL_PRICE: <number>."
)


@dataclass(frozen=True)
class PricingCase:
    key: str
    alpha: float
    beta: float
    sigma: float
    p_max: float
    seed: int


@dataclass(frozen=True)
class PricingEvidenceCase:
    key: str
    p_max: float
    observations: tuple[tuple[float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingCounterfactualSet:
    key: str
    base: PricingEvidenceCase
    perturbed: PricingEvidenceCase


DEFAULT_CASES = [
    PricingCase("snack_box", alpha=180.0, beta=6.0, sigma=4.0, p_max=30.0, seed=11),
    PricingCase("premium_widget", alpha=260.0, beta=4.0, sigma=6.0, p_max=55.0, seed=29),
]

COUNTERFACTUAL_SETS = [
    PricingCounterfactualSet(
        key="snack_demand_downshift",
        base=PricingEvidenceCase(
            key="snack_demand_downshift_base",
            p_max=30.0,
            scenario_note="Base evidence: the product has steady weekday demand.",
            observations=((8.0, 132.0), (12.0, 108.0), (16.0, 84.0), (20.0, 60.0), (24.0, 36.0)),
        ),
        perturbed=PricingEvidenceCase(
            key="snack_demand_downshift_perturbed",
            p_max=30.0,
            scenario_note="Perturbed evidence: a cheaper substitute enters and demand steepens.",
            observations=((8.0, 86.0), (10.0, 70.0), (12.0, 54.0), (14.0, 38.0), (16.0, 22.0)),
        ),
    ),
    PricingCounterfactualSet(
        key="premium_demand_upswing",
        base=PricingEvidenceCase(
            key="premium_demand_upswing_base",
            p_max=55.0,
            scenario_note="Base evidence: premium demand is moderate.",
            observations=((14.0, 130.0), (18.0, 110.0), (22.0, 90.0), (26.0, 70.0), (30.0, 50.0)),
        ),
        perturbed=PricingEvidenceCase(
            key="premium_demand_upswing_perturbed",
            p_max=55.0,
            scenario_note="Perturbed evidence: enterprise buyers arrive and demand becomes less price-sensitive.",
            observations=((20.0, 180.0), (25.0, 160.0), (30.0, 140.0), (35.0, 120.0), (40.0, 100.0)),
        ),
    ),
]


def demand(case: PricingCase, price: float) -> float:
    return max(0.0, case.alpha - case.beta * price)


def expected_revenue(case: PricingCase, price: float) -> float:
    return price * demand(case, price)


def oracle_price(case: PricingCase) -> float:
    return clamp(case.alpha / (2.0 * case.beta), 0.0, case.p_max)


def observations(case: PricingCase, n: int = 10) -> list[tuple[float, float]]:
    rng = random.Random(case.seed)
    rows = []
    for _ in range(n):
        price = rng.uniform(0.25 * case.p_max, 0.90 * case.p_max)
        quantity = max(0.0, case.alpha - case.beta * price + rng.gauss(0.0, case.sigma))
        rows.append((round(price, 2), round(quantity, 2)))
    return rows


def ols_posterior(case: PricingCase) -> tuple[float, float]:
    return _ols_fit(observations(case))


def evidence_posterior(case: PricingEvidenceCase) -> tuple[float, float]:
    return _ols_fit(list(case.observations))


def evidence_oracle_price(case: PricingEvidenceCase) -> float:
    alpha_hat, beta_hat = evidence_posterior(case)
    return clamp(alpha_hat / (2.0 * beta_hat), 0.0, case.p_max)


def evidence_revenue(case: PricingEvidenceCase, price: float) -> float:
    alpha_hat, beta_hat = evidence_posterior(case)
    return price * max(0.0, alpha_hat - beta_hat * price)


def _ols_fit(rows: list[tuple[float, float]]) -> tuple[float, float]:
    xs = [p for p, _ in rows]
    ys = [q for _, q in rows]
    x_bar = sum(xs) / len(xs)
    y_bar = sum(ys) / len(ys)
    denom = sum((x - x_bar) ** 2 for x in xs)
    slope = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denom
    beta_hat = max(0.001, -slope)
    alpha_hat = y_bar + beta_hat * x_bar
    return alpha_hat, beta_hat


def run_pricing_game(agent: Agent, cases: list[PricingCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    rows = []
    for case in cases:
        oracle = oracle_price(case)
        oracle_rev = expected_revenue(case, oracle)
        for condition in ("base", "posterior", "reveal"):
            response = agent.complete(PRICING_SYSTEM, _prompt(case, condition))
            parsed = parse_float("FINAL_PRICE", response)
            chosen = clamp(parsed, 0.0, case.p_max) if parsed is not None else None
            revenue = expected_revenue(case, chosen) if chosen is not None else None
            gap = oracle_rev - revenue if revenue is not None else None
            rows.append(
                {
                    "case": case.key,
                    "condition": condition,
                    "oracle_price": oracle,
                    "chosen_price": chosen,
                    "oracle_revenue": oracle_rev,
                    "chosen_revenue": revenue,
                    "revenue_gap": gap,
                    "raw_response": response,
                }
            )
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    by_condition = {}
    for condition in ("base", "posterior", "reveal"):
        subset = [row for row in rows if row["condition"] == condition and row["revenue_gap"] is not None]
        by_condition[condition] = {
            "mean_revenue_gap": sum(row["revenue_gap"] for row in subset) / len(subset)
            if subset
            else None
        }
    return {
        "task": "pricing",
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "by_condition": by_condition,
        "trials": rows,
    }


def run_pricing_counterfactual_game(
    agent: Agent,
    cases: list[PricingCounterfactualSet] | None = None,
) -> dict:
    cases = cases or COUNTERFACTUAL_SETS
    rows = []
    by_set = {}
    for case_set in cases:
        set_rows = []
        for variant, case in (("base", case_set.base), ("perturbed", case_set.perturbed)):
            oracle = evidence_oracle_price(case)
            oracle_rev = evidence_revenue(case, oracle)
            response = agent.complete(PRICING_SYSTEM, _counterfactual_prompt(case, variant))
            parsed = parse_float("FINAL_PRICE", response)
            chosen = clamp(parsed, 0.0, case.p_max) if parsed is not None else None
            revenue = evidence_revenue(case, chosen) if chosen is not None else None
            gap = oracle_rev - revenue if revenue is not None else None
            row = {
                "set": case_set.key,
                "case": case.key,
                "variant": variant,
                "oracle_price": oracle,
                "chosen_price": chosen,
                "absolute_price_error": abs(chosen - oracle) if chosen is not None else None,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": gap,
                "raw_response": response,
            }
            rows.append(row)
            set_rows.append(row)
        base_row, perturbed_row = set_rows
        oracle_shift = perturbed_row["oracle_price"] - base_row["oracle_price"]
        if base_row["chosen_price"] is None or perturbed_row["chosen_price"] is None:
            chosen_shift = None
            shift_error = None
            shift_miss = True
            sticky = True
        else:
            chosen_shift = perturbed_row["chosen_price"] - base_row["chosen_price"]
            shift_error = abs(chosen_shift - oracle_shift)
            shift_miss = (
                abs(oracle_shift) > 1e-9
                and (
                    chosen_shift * oracle_shift <= 0.0
                    or abs(chosen_shift) < 0.5 * abs(oracle_shift)
                )
            )
            sticky = abs(chosen_shift) < 0.5 and abs(oracle_shift) > 1e-9
        by_set[case_set.key] = {
            "base_oracle_price": base_row["oracle_price"],
            "perturbed_oracle_price": perturbed_row["oracle_price"],
            "base_chosen_price": base_row["chosen_price"],
            "perturbed_chosen_price": perturbed_row["chosen_price"],
            "oracle_price_shift": oracle_shift,
            "chosen_price_shift": chosen_shift,
            "shift_error": shift_error,
            "counterfactual_shift_miss": shift_miss,
            "sticky_base_price": sticky,
        }
    errors = [row["absolute_price_error"] for row in rows if row["absolute_price_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    shift_errors = [row["shift_error"] for row in by_set.values() if row["shift_error"] is not None]
    n_sets = len(cases)
    shift_misses = sum(row["counterfactual_shift_miss"] for row in by_set.values())
    sticky_prices = sum(row["sticky_base_price"] for row in by_set.values())
    return {
        "task": "pricing_counterfactual",
        "agent": agent.name,
        "n_trials": len(rows),
        "n_sets": n_sets,
        "mean_absolute_price_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "mean_shift_error": sum(shift_errors) / len(shift_errors) if shift_errors else None,
        "counterfactual_shift_miss_rate": shift_misses / n_sets if n_sets else 0.0,
        "sticky_base_price_rate": sticky_prices / n_sets if n_sets else 0.0,
        "by_set": by_set,
        "trials": rows,
    }


def _prompt(case: PricingCase, condition: str) -> str:
    alpha_hat, beta_hat = ols_posterior(case)
    lines = [
        f"case={case.key}",
        f"condition={condition}",
        f"p_max={case.p_max:.2f}",
    ]
    if condition == "base":
        lines.append("Prior: alpha in [120, 320], beta in [2, 8].")
        lines.append("Historical sales observations:")
        lines.extend(f"  price={p:.2f}, quantity={q:.2f}" for p, q in observations(case))
    elif condition == "posterior":
        lines.append(f"Bayes/OLS posterior summary: alpha_hat={alpha_hat:.2f}, beta_hat={beta_hat:.2f}.")
    elif condition == "reveal":
        lines.append(f"True demand parameters: alpha={case.alpha:.2f}, beta={case.beta:.2f}, sigma={case.sigma:.2f}.")
    lines.append("Demand is approximately quantity = alpha - beta * price + noise.")
    return "\n".join(lines)


def _counterfactual_prompt(case: PricingEvidenceCase, variant: str) -> str:
    lines = [
        f"case={case.key}",
        f"variant={variant}",
        f"p_max={case.p_max:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Historical sales observations:")
    lines.extend(f"  price={p:.2f}, quantity={q:.2f}" for p, q in case.observations)
    lines.append("Fit a linear demand curve quantity = alpha - beta * price, then choose the revenue-maximizing price.")
    return "\n".join(lines)
