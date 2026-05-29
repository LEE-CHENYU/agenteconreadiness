from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token


PROCUREMENT_SYSTEM = (
    "TASK: procurement_choice\n"
    "Select one product_id. Return one final line only: FINAL_PRODUCT: <product_id>."
)


@dataclass(frozen=True)
class Product:
    product_id: str
    price: float
    durability: float
    comfort: float
    style_fit: float
    assembly_friction: float


@dataclass(frozen=True)
class BuyerProfile:
    key: str
    price_weight: float
    durability_weight: float
    comfort_weight: float
    style_weight: float
    friction_weight: float


@dataclass(frozen=True)
class ProcurementCase:
    key: str
    profile: BuyerProfile
    products: tuple[Product, ...]


DEFAULT_CASES = [
    ProcurementCase(
        key="office_chair",
        profile=BuyerProfile(
            "ergonomic_startup",
            price_weight=0.018,
            durability_weight=0.35,
            comfort_weight=0.40,
            style_weight=0.10,
            friction_weight=0.15,
        ),
        products=(
            Product("cheap_flatpack", 115, 0.50, 0.45, 0.45, 0.80),
            Product("balanced_mesh", 175, 0.75, 0.82, 0.62, 0.30),
            Product("premium_brand", 310, 0.90, 0.88, 0.80, 0.20),
            Product("stylish_weak", 205, 0.42, 0.58, 0.94, 0.35),
        ),
    ),
    ProcurementCase(
        key="field_laptops",
        profile=BuyerProfile(
            "rugged_field_team",
            price_weight=0.012,
            durability_weight=0.48,
            comfort_weight=0.18,
            style_weight=0.02,
            friction_weight=0.32,
        ),
        products=(
            Product("consumer_ultra", 860, 0.45, 0.85, 0.75, 0.20),
            Product("rugged_mid", 1180, 0.92, 0.70, 0.35, 0.22),
            Product("rugged_max", 1750, 0.98, 0.63, 0.30, 0.18),
            Product("refurb_bulk", 620, 0.50, 0.45, 0.25, 0.65),
        ),
    ),
]


def product_utility(product: Product, profile: BuyerProfile) -> float:
    return (
        profile.durability_weight * product.durability
        + profile.comfort_weight * product.comfort
        + profile.style_weight * product.style_fit
        - profile.friction_weight * product.assembly_friction
        - profile.price_weight * product.price
    )


def oracle_product(case: ProcurementCase) -> str:
    return max(case.products, key=lambda p: product_utility(p, case.profile)).product_id


def run_procurement_game(agent: Agent, cases: list[ProcurementCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    rows = []
    for case in cases:
        oracle = oracle_product(case)
        response = agent.complete(PROCUREMENT_SYSTEM, _prompt(case, oracle))
        chosen = parse_token("FINAL_PRODUCT", response)
        utilities = {p.product_id: product_utility(p, case.profile) for p in case.products}
        best = utilities[oracle]
        chosen_utility = utilities.get(chosen, None)
        regret = best - chosen_utility if chosen_utility is not None else None
        rows.append(
            {
                "case": case.key,
                "oracle_product": oracle,
                "chosen_product": chosen,
                "correct": chosen == oracle,
                "regret": regret,
                "raw_response": response,
                "utilities": utilities,
            }
        )
    return {
        "task": "procurement",
        "agent": agent.name,
        "n_trials": len(rows),
        "accuracy": sum(row["correct"] for row in rows) / len(rows),
        "mean_regret": sum(row["regret"] or 0.0 for row in rows) / len(rows),
        "trials": rows,
    }


def _prompt(case: ProcurementCase, oracle: str) -> str:
    lines = [
        f"case={case.key}",
        f"oracle_product={oracle}",
        f"profile={case.profile.key}",
        "Score buyer utility from price, durability, comfort, style fit, and assembly friction.",
    ]
    lines.append("Products:")
    for product in case.products:
        lines.append(
            "  "
            + " ".join(
                [
                    f"product_id={product.product_id}",
                    f"price={product.price:.0f}",
                    f"durability={product.durability:.2f}",
                    f"comfort={product.comfort:.2f}",
                    f"style_fit={product.style_fit:.2f}",
                    f"assembly_friction={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Profile weights:")
    lines.append(str(asdict(case.profile)))
    return "\n".join(lines)
