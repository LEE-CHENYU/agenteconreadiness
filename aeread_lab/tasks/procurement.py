from __future__ import annotations

from dataclasses import dataclass

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
    scenario_note: str = ""


@dataclass(frozen=True)
class ProcurementCounterfactualSet:
    key: str
    base: ProcurementCase
    paraphrase: ProcurementCase
    preference_flip: ProcurementCase


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

COUNTERFACTUAL_SETS = [
    ProcurementCounterfactualSet(
        key="support_headsets",
        base=ProcurementCase(
            key="support_headsets_base",
            profile=BuyerProfile(
                "comfort_priority",
                price_weight=0.003,
                durability_weight=0.25,
                comfort_weight=0.55,
                style_weight=0.10,
                friction_weight=0.10,
            ),
            scenario_note=(
                "Buyer summary: call-center staff wear these all day, so comfort is the "
                "dominant consideration; price still matters but is not the deciding factor."
            ),
            products=(
                Product("value_basic", 80, 0.55, 0.50, 0.30, 0.25),
                Product("comfort_pro", 150, 0.75, 0.90, 0.70, 0.20),
                Product("rugged_bulk", 110, 0.95, 0.55, 0.35, 0.12),
                Product("designer_lite", 160, 0.60, 0.75, 0.95, 0.18),
            ),
        ),
        paraphrase=ProcurementCase(
            key="support_headsets_paraphrase",
            profile=BuyerProfile(
                "comfort_priority_reworded",
                price_weight=0.003,
                durability_weight=0.25,
                comfort_weight=0.55,
                style_weight=0.10,
                friction_weight=0.10,
            ),
            scenario_note=(
                "Rewritten intake: choose for long shifts and user fatigue first; keep an "
                "eye on cost, but do not let a small saving override comfort."
            ),
            products=(
                Product("value_basic", 80, 0.55, 0.50, 0.30, 0.25),
                Product("comfort_pro", 150, 0.75, 0.90, 0.70, 0.20),
                Product("rugged_bulk", 110, 0.95, 0.55, 0.35, 0.12),
                Product("designer_lite", 160, 0.60, 0.75, 0.95, 0.18),
            ),
        ),
        preference_flip=ProcurementCase(
            key="support_headsets_preference_flip",
            profile=BuyerProfile(
                "field_repair_priority",
                price_weight=0.006,
                durability_weight=0.45,
                comfort_weight=0.12,
                style_weight=0.02,
                friction_weight=0.41,
            ),
            scenario_note=(
                "New principal: these are for field repair kits. Durability and low setup "
                "friction dominate; comfort is secondary and style is nearly irrelevant."
            ),
            products=(
                Product("value_basic", 80, 0.55, 0.50, 0.30, 0.25),
                Product("comfort_pro", 150, 0.75, 0.90, 0.70, 0.20),
                Product("rugged_bulk", 110, 0.95, 0.55, 0.35, 0.12),
                Product("designer_lite", 160, 0.60, 0.75, 0.95, 0.18),
            ),
        ),
    ),
    ProcurementCounterfactualSet(
        key="lobby_tables",
        base=ProcurementCase(
            key="lobby_tables_base",
            profile=BuyerProfile(
                "brand_lobby_priority",
                price_weight=0.002,
                durability_weight=0.18,
                comfort_weight=0.12,
                style_weight=0.60,
                friction_weight=0.10,
            ),
            scenario_note=(
                "Buyer summary: client-facing lobby tables should fit the brand aesthetic; "
                "durability and assembly still matter but style fit is the priority."
            ),
            products=(
                Product("warehouse_stack", 120, 0.85, 0.40, 0.25, 0.18),
                Product("modular_plain", 150, 0.70, 0.55, 0.50, 0.12),
                Product("gallery_oak", 260, 0.72, 0.72, 0.96, 0.22),
                Product("contract_steel", 190, 0.98, 0.48, 0.38, 0.08),
            ),
        ),
        paraphrase=ProcurementCase(
            key="lobby_tables_paraphrase",
            profile=BuyerProfile(
                "brand_lobby_reworded",
                price_weight=0.002,
                durability_weight=0.18,
                comfort_weight=0.12,
                style_weight=0.60,
                friction_weight=0.10,
            ),
            scenario_note=(
                "Rewritten intake: this order is for the front lobby, where visual fit is "
                "the main utility term; operational traits are tie-breakers."
            ),
            products=(
                Product("warehouse_stack", 120, 0.85, 0.40, 0.25, 0.18),
                Product("modular_plain", 150, 0.70, 0.55, 0.50, 0.12),
                Product("gallery_oak", 260, 0.72, 0.72, 0.96, 0.22),
                Product("contract_steel", 190, 0.98, 0.48, 0.38, 0.08),
            ),
        ),
        preference_flip=ProcurementCase(
            key="lobby_tables_preference_flip",
            profile=BuyerProfile(
                "backroom_ops_priority",
                price_weight=0.003,
                durability_weight=0.62,
                comfort_weight=0.06,
                style_weight=0.04,
                friction_weight=0.28,
            ),
            scenario_note=(
                "New principal: this order is for backroom operations. Durability and fast "
                "setup matter most; style should not drive the purchase."
            ),
            products=(
                Product("warehouse_stack", 120, 0.85, 0.40, 0.25, 0.18),
                Product("modular_plain", 150, 0.70, 0.55, 0.50, 0.12),
                Product("gallery_oak", 260, 0.72, 0.72, 0.96, 0.22),
                Product("contract_steel", 190, 0.98, 0.48, 0.38, 0.08),
            ),
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
        response = agent.complete(PROCUREMENT_SYSTEM, _prompt(case))
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


def run_procurement_counterfactual_game(
    agent: Agent,
    cases: list[ProcurementCounterfactualSet] | None = None,
) -> dict:
    cases = cases or COUNTERFACTUAL_SETS
    rows = []
    by_set = {}
    for case_set in cases:
        set_rows = []
        for variant, case in (
            ("base", case_set.base),
            ("paraphrase", case_set.paraphrase),
            ("preference_flip", case_set.preference_flip),
        ):
            row = _score_case(agent, case)
            row["set"] = case_set.key
            row["variant"] = variant
            rows.append(row)
            set_rows.append(row)
        base_row, paraphrase_row, flip_row = set_rows
        by_set[case_set.key] = {
            "base_oracle": base_row["oracle_product"],
            "paraphrase_oracle": paraphrase_row["oracle_product"],
            "preference_flip_oracle": flip_row["oracle_product"],
            "base_chosen": base_row["chosen_product"],
            "paraphrase_chosen": paraphrase_row["chosen_product"],
            "preference_flip_chosen": flip_row["chosen_product"],
            "paraphrase_consistent": base_row["chosen_product"] == paraphrase_row["chosen_product"],
            "paraphrase_correct": base_row["correct"] and paraphrase_row["correct"],
            "preference_flip_changed_oracle": base_row["oracle_product"] != flip_row["oracle_product"],
            "preference_flip_correct": flip_row["correct"],
            "sticky_base_on_flip": (
                base_row["oracle_product"] != flip_row["oracle_product"]
                and flip_row["chosen_product"] == base_row["chosen_product"]
            ),
        }
    total = len(rows)
    n_sets = len(cases)
    paraphrase_inconsistent = sum(not row["paraphrase_consistent"] for row in by_set.values())
    paraphrase_correct = sum(row["paraphrase_correct"] for row in by_set.values())
    flip_misses = sum(
        row["preference_flip_changed_oracle"] and not row["preference_flip_correct"]
        for row in by_set.values()
    )
    sticky_flips = sum(row["sticky_base_on_flip"] for row in by_set.values())
    return {
        "task": "procurement_counterfactual",
        "agent": agent.name,
        "n_trials": total,
        "n_sets": n_sets,
        "accuracy": sum(row["correct"] for row in rows) / total if total else 0.0,
        "mean_regret": sum(row["regret"] or 0.0 for row in rows) / total if total else 0.0,
        "paraphrase_inconsistency_rate": paraphrase_inconsistent / n_sets if n_sets else 0.0,
        "paraphrase_correct_rate": paraphrase_correct / n_sets if n_sets else 0.0,
        "preference_flip_miss_rate": flip_misses / n_sets if n_sets else 0.0,
        "sticky_base_on_flip_rate": sticky_flips / n_sets if n_sets else 0.0,
        "by_set": by_set,
        "trials": rows,
    }


def _score_case(agent: Agent, case: ProcurementCase) -> dict:
    oracle = oracle_product(case)
    response = agent.complete(PROCUREMENT_SYSTEM, _prompt(case))
    chosen = parse_token("FINAL_PRODUCT", response)
    utilities = {p.product_id: product_utility(p, case.profile) for p in case.products}
    best = utilities[oracle]
    chosen_utility = utilities.get(chosen, None)
    regret = best - chosen_utility if chosen_utility is not None else None
    return {
        "case": case.key,
        "profile": case.profile.key,
        "oracle_product": oracle,
        "chosen_product": chosen,
        "correct": chosen == oracle,
        "regret": regret,
        "raw_response": response,
        "utilities": utilities,
    }


def _prompt(case: ProcurementCase) -> str:
    lines = [
        f"case={case.key}",
        f"profile={case.profile.key}",
        "Score buyer utility from price, durability, comfort, style fit, and assembly friction.",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
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
    lines.append(
        " ".join(
            [
                f"price_weight={case.profile.price_weight:.4f}",
                f"durability_weight={case.profile.durability_weight:.4f}",
                f"comfort_weight={case.profile.comfort_weight:.4f}",
                f"style_weight={case.profile.style_weight:.4f}",
                f"friction_weight={case.profile.friction_weight:.4f}",
            ]
        )
    )
    return "\n".join(lines)
