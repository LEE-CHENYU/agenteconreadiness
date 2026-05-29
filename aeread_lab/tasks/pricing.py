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


DEFAULT_CASES = [
    PricingCase("snack_box", alpha=180.0, beta=6.0, sigma=4.0, p_max=30.0, seed=11),
    PricingCase("premium_widget", alpha=260.0, beta=4.0, sigma=6.0, p_max=55.0, seed=29),
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
    rows = observations(case)
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
            response = agent.complete(PRICING_SYSTEM, _prompt(case, condition, oracle))
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


def _prompt(case: PricingCase, condition: str, oracle: float) -> str:
    alpha_hat, beta_hat = ols_posterior(case)
    lines = [
        f"case={case.key}",
        f"condition={condition}",
        f"p_max={case.p_max:.2f}",
        f"oracle_price={oracle:.2f}",
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
