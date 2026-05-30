from __future__ import annotations

from dataclasses import dataclass, asdict
from itertools import combinations
import re

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token


PROCUREMENT_SYSTEM = (
    "TASK: procurement_choice\n"
    "Select one product_id. Return one final line only: FINAL_PRODUCT: <product_id>."
)

PROCUREMENT_BUNDLE_SYSTEM = (
    "TASK: procurement_bundle\n"
    "Select exactly two product_id values as a procurement bundle. "
    "Respect the budget, required category coverage, and compatibility bonuses. "
    "Return one final line only: FINAL_BUNDLE: <product_id>,<product_id>."
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
class BundleProduct:
    product_id: str
    category: str
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


@dataclass(frozen=True)
class ProcurementBundleCase:
    key: str
    profile: BuyerProfile
    budget: float
    required_categories: tuple[str, str]
    products: tuple[BundleProduct, ...]
    compatibility_bonuses: tuple[tuple[str, str, float], ...]
    scenario_note: str = ""


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

PROCUREMENT_BUNDLE_CASES = [
    ProcurementBundleCase(
        key="hybrid_workstation",
        profile=BuyerProfile(
            "hybrid_ops_bundle",
            price_weight=0.004,
            durability_weight=0.34,
            comfort_weight=0.32,
            style_weight=0.06,
            friction_weight=0.28,
        ),
        budget=520.0,
        required_categories=("display", "dock"),
        scenario_note=(
            "Principal needs one display item and one dock item for hybrid desks; "
            "setup friction and compatibility matter because IT will deploy many kits."
        ),
        products=(
            BundleProduct("budget_panel", "display", 220, 0.58, 0.62, 0.42, 0.26),
            BundleProduct("ergonomic_panel", "display", 320, 0.82, 0.86, 0.58, 0.18),
            BundleProduct("portable_screen", "display", 240, 0.50, 0.72, 0.80, 0.34),
            BundleProduct("basic_dock", "dock", 115, 0.50, 0.45, 0.30, 0.32),
            BundleProduct("fleet_dock", "dock", 185, 0.76, 0.62, 0.42, 0.16),
            BundleProduct("premium_dock", "dock", 260, 0.88, 0.70, 0.50, 0.12),
        ),
        compatibility_bonuses=(
            ("ergonomic_panel", "fleet_dock", 0.70),
            ("budget_panel", "basic_dock", 0.10),
            ("portable_screen", "premium_dock", -0.12),
        ),
    ),
    ProcurementBundleCase(
        key="field_repair_kit",
        profile=BuyerProfile(
            "field_repair_bundle",
            price_weight=0.005,
            durability_weight=0.52,
            comfort_weight=0.10,
            style_weight=0.02,
            friction_weight=0.36,
        ),
        budget=430.0,
        required_categories=("scanner", "case"),
        scenario_note=(
            "Principal needs one scanner and one case for field repair vans; "
            "ruggedness and low setup friction dominate style."
        ),
        products=(
            BundleProduct("cheap_scanner", "scanner", 140, 0.48, 0.55, 0.25, 0.34),
            BundleProduct("rugged_scanner", "scanner", 260, 0.92, 0.58, 0.32, 0.18),
            BundleProduct("fast_scanner", "scanner", 310, 0.78, 0.70, 0.45, 0.22),
            BundleProduct("soft_case", "case", 70, 0.45, 0.60, 0.50, 0.15),
            BundleProduct("sealed_case", "case", 145, 0.90, 0.42, 0.28, 0.10),
            BundleProduct("rolling_case", "case", 190, 0.86, 0.72, 0.34, 0.24),
        ),
        compatibility_bonuses=(
            ("rugged_scanner", "sealed_case", 0.85),
            ("fast_scanner", "rolling_case", 0.10),
            ("cheap_scanner", "soft_case", 0.05),
        ),
    ),
    ProcurementBundleCase(
        key="training_room_av",
        profile=BuyerProfile(
            "training_room_bundle",
            price_weight=0.003,
            durability_weight=0.22,
            comfort_weight=0.20,
            style_weight=0.36,
            friction_weight=0.22,
        ),
        budget=760.0,
        required_categories=("camera", "speaker"),
        scenario_note=(
            "Principal needs one camera and one speaker for client-facing training rooms; "
            "style and user experience matter, but integration friction cannot be ignored."
        ),
        products=(
            BundleProduct("basic_camera", "camera", 210, 0.55, 0.58, 0.38, 0.30),
            BundleProduct("studio_camera", "camera", 420, 0.80, 0.76, 0.88, 0.20),
            BundleProduct("portable_camera", "camera", 300, 0.64, 0.72, 0.70, 0.18),
            BundleProduct("basic_speaker", "speaker", 160, 0.50, 0.58, 0.42, 0.22),
            BundleProduct("studio_bar", "speaker", 335, 0.76, 0.82, 0.86, 0.18),
            BundleProduct("ceiling_array", "speaker", 410, 0.88, 0.78, 0.74, 0.36),
        ),
        compatibility_bonuses=(
            ("studio_camera", "studio_bar", 0.85),
            ("portable_camera", "basic_speaker", 0.08),
            ("studio_camera", "ceiling_array", -0.20),
        ),
    ),
    ProcurementBundleCase(
        key="clinic_checkout",
        profile=BuyerProfile(
            "clinic_checkout_bundle",
            price_weight=0.004,
            durability_weight=0.30,
            comfort_weight=0.24,
            style_weight=0.04,
            friction_weight=0.42,
        ),
        budget=610.0,
        required_categories=("tablet", "stand"),
        scenario_note=(
            "Principal needs one tablet and one stand for clinic checkout stations; "
            "deployment friction and durability carry more weight than visual polish."
        ),
        products=(
            BundleProduct("consumer_tablet", "tablet", 280, 0.52, 0.82, 0.70, 0.20),
            BundleProduct("managed_tablet", "tablet", 390, 0.82, 0.72, 0.55, 0.12),
            BundleProduct("rugged_tablet", "tablet", 460, 0.95, 0.62, 0.40, 0.18),
            BundleProduct("tilt_stand", "stand", 105, 0.58, 0.66, 0.45, 0.16),
            BundleProduct("locking_stand", "stand", 170, 0.88, 0.50, 0.35, 0.08),
            BundleProduct("rolling_stand", "stand", 240, 0.75, 0.78, 0.48, 0.24),
        ),
        compatibility_bonuses=(
            ("managed_tablet", "locking_stand", 0.90),
            ("consumer_tablet", "tilt_stand", 0.08),
            ("rugged_tablet", "rolling_stand", -0.18),
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


def bundle_product_utility(product: BundleProduct, profile: BuyerProfile) -> float:
    return (
        profile.durability_weight * product.durability
        + profile.comfort_weight * product.comfort
        + profile.style_weight * product.style_fit
        - profile.friction_weight * product.assembly_friction
        - profile.price_weight * product.price
    )


def oracle_product(case: ProcurementCase) -> str:
    return max(case.products, key=lambda p: product_utility(p, case.profile)).product_id


def oracle_bundle(case: ProcurementBundleCase) -> tuple[str, str]:
    return max(valid_bundles(case), key=lambda pair: bundle_utility(case, pair))


def valid_bundles(case: ProcurementBundleCase) -> list[tuple[str, str]]:
    pairs = []
    products = {product.product_id: product for product in case.products}
    required = set(case.required_categories)
    for left, right in combinations(products, 2):
        pair = tuple(sorted((left, right)))
        if bundle_price(case, pair) > case.budget:
            continue
        if not required.issubset({products[left].category, products[right].category}):
            continue
        pairs.append(pair)
    return pairs


def bundle_utility(
    case: ProcurementBundleCase,
    pair: tuple[str, str],
    *,
    include_compatibility: bool = True,
) -> float:
    products = {product.product_id: product for product in case.products}
    return (
        sum(bundle_product_utility(products[item], case.profile) for item in pair)
        + (compatibility_bonus(case, pair) if include_compatibility else 0.0)
    )


def bundle_price(case: ProcurementBundleCase, pair: tuple[str, str]) -> float:
    products = {product.product_id: product for product in case.products}
    return sum(products[item].price for item in pair if item in products)


def compatibility_bonus(case: ProcurementBundleCase, pair: tuple[str, str]) -> float:
    normalized = set(pair)
    for left, right, bonus in case.compatibility_bonuses:
        if normalized == {left, right}:
            return bonus
    return 0.0


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


def run_procurement_bundle_game(
    agent: Agent,
    cases: list[ProcurementBundleCase] | None = None,
) -> dict:
    cases = cases or PROCUREMENT_BUNDLE_CASES
    rows = []
    for case in cases:
        oracle = oracle_bundle(case)
        response = agent.complete(PROCUREMENT_BUNDLE_SYSTEM, _bundle_prompt(case))
        chosen = _parse_bundle(response)
        row = _score_bundle_case(case, chosen, response)
        row["oracle_bundle"] = oracle
        row["correct"] = chosen == oracle
        rows.append(row)
    total = len(rows)
    invalid = sum(row["invalid"] for row in rows)
    category_misses = sum(row["category_miss"] for row in rows)
    budget_violations = sum(row["budget_violation"] for row in rows)
    compatibility_missable = [
        row for row in rows if row["compatibility_blind_bundle"] != row["oracle_bundle"]
    ]
    return {
        "task": "procurement_bundle",
        "agent": agent.name,
        "n_trials": total,
        "accuracy": sum(row["correct"] for row in rows) / total if total else 0.0,
        "mean_score_regret": sum(row["score_regret"] for row in rows) / total if total else 0.0,
        "invalid_rate": invalid / total if total else 0.0,
        "category_miss_rate": category_misses / total if total else 0.0,
        "budget_violation_rate": budget_violations / total if total else 0.0,
        "compatibility_blind_miss_rate": (
            sum(row["compatibility_blind_miss"] for row in compatibility_missable)
            / len(compatibility_missable)
            if compatibility_missable
            else 0.0
        ),
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


def _score_bundle_case(
    case: ProcurementBundleCase,
    chosen: tuple[str, str] | None,
    response: str,
) -> dict:
    oracle = oracle_bundle(case)
    valid = valid_bundles(case)
    best_score = bundle_utility(case, oracle)
    worst_valid_score = min(bundle_utility(case, pair) for pair in valid)
    invalid_score = worst_valid_score - 10.0
    products = {product.product_id: product for product in case.products}
    chosen_exists = chosen is not None and all(item in products for item in chosen)
    budget_violation = bool(chosen_exists and bundle_price(case, chosen) > case.budget)
    category_miss = bool(
        chosen_exists
        and not set(case.required_categories).issubset({products[item].category for item in chosen})
    )
    invalid = not chosen_exists or budget_violation or category_miss
    chosen_score = bundle_utility(case, chosen) if chosen is not None and not invalid else invalid_score
    compatibility_blind = _compatibility_blind_bundle(case)
    return {
        "case": case.key,
        "profile": case.profile.key,
        "oracle_bundle": oracle,
        "chosen_bundle": chosen,
        "score": chosen_score,
        "score_regret": best_score - chosen_score,
        "invalid": invalid,
        "category_miss": category_miss or not chosen_exists,
        "budget_violation": budget_violation,
        "compatibility_blind_bundle": compatibility_blind,
        "compatibility_blind_miss": (
            chosen == compatibility_blind and compatibility_blind != oracle
        ),
        "raw_response": response,
        "case_data": asdict(case),
    }


def _compatibility_blind_bundle(case: ProcurementBundleCase) -> tuple[str, str]:
    return max(
        valid_bundles(case),
        key=lambda pair: bundle_utility(case, pair, include_compatibility=False),
    )


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


def _bundle_prompt(case: ProcurementBundleCase) -> str:
    lines = [
        f"case={case.key}",
        f"profile={case.profile.key}",
        f"budget={case.budget:.0f}",
        f"required_categories={','.join(case.required_categories)}",
        "Score bundle utility from item utility plus listed compatibility bonuses.",
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
                    f"category={product.category}",
                    f"price={product.price:.0f}",
                    f"durability={product.durability:.2f}",
                    f"comfort={product.comfort:.2f}",
                    f"style_fit={product.style_fit:.2f}",
                    f"assembly_friction={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Compatibility bonuses:")
    for left, right, bonus in case.compatibility_bonuses:
        lines.append(f"  pair={left},{right} bonus={bonus:.2f}")
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


def _parse_bundle(response: str) -> tuple[str, str] | None:
    match = re.search(
        r"FINAL_BUNDLE\s*:\s*([a-zA-Z0-9_-]+)\s*,\s*([a-zA-Z0-9_-]+)",
        response,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    left, right = match.group(1), match.group(2)
    if left == right:
        return None
    return tuple(sorted((left, right)))
