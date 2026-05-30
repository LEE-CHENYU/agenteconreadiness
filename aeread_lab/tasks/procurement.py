from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from itertools import combinations, product as cartesian_product

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

PROCUREMENT_BUNDLE_NATURAL_SYSTEM = (
    "TASK: procurement_bundle_natural\n"
    "Select exactly two SKU values for the procurement package. "
    "Respect the spend limit, required product lines, and package fit notes. "
    "Return one final line only: FINAL_BUNDLE: <sku>,<sku>."
)

PROCUREMENT_BUNDLE_EVIDENCE_SYSTEM = (
    "TASK: procurement_bundle_evidence\n"
    "Select exactly two SKU values for the procurement package. "
    "Respect the spend limit, required product lines, and deployment outcome evidence. "
    "Return one final line only: FINAL_BUNDLE: <sku>,<sku>."
)

PROCUREMENT_BUNDLE_NOISY_EVIDENCE_SYSTEM = (
    "TASK: procurement_bundle_noisy_evidence\n"
    "Select exactly two SKU values for the procurement package. "
    "Respect the spend limit, required product lines, and noisy deployment outcome evidence. "
    "Return one final line only: FINAL_BUNDLE: <sku>,<sku>."
)

PROCUREMENT_BUNDLE_HISTORY_SYSTEM = (
    "TASK: procurement_bundle_history\n"
    "Select exactly two SKU values for the procurement package. "
    "Respect the spend limit, required product lines, and multi-period deployment history. "
    "Return one final line only: FINAL_BUNDLE: <sku>,<sku>."
)

PROCUREMENT_BUNDLE_RESERVE_SYSTEM = (
    "TASK: procurement_bundle_reserve\n"
    "Select exactly two SKU values for the procurement package. "
    "Respect the spend limit, required product lines, and support-reserve risk. "
    "Return one final line only: FINAL_BUNDLE: <sku>,<sku>."
)

PROCUREMENT_VENDOR_UPDATE_SYSTEM = (
    "TASK: procurement_vendor_update\n"
    "Choose one vendor for each procurement round after reading delivery history. "
    "Return one final line only: FINAL_VENDOR_PLAN: <vendor_id>,<vendor_id>,<vendor_id>."
)

PROCUREMENT_VENDOR_UPDATE_NOISY_SYSTEM = (
    "TASK: procurement_vendor_update_noisy\n"
    "Choose one vendor for each procurement round after reading noisy receiving history. "
    "Return one final line only: FINAL_VENDOR_PLAN: <vendor_id>,<vendor_id>,<vendor_id>."
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


@dataclass(frozen=True)
class VendorOption:
    vendor_id: str
    invoice: float
    operational_fit: float
    shipments_observed: int
    on_time_shipments: int


@dataclass(frozen=True)
class VendorRound:
    round_id: str
    service_value: float
    late_penalty: float


@dataclass(frozen=True)
class ProcurementVendorUpdateCase:
    key: str
    starting_reserve: float
    reserve_floor: float
    reserve_penalty: float
    switch_cost: float
    vendors: tuple[VendorOption, ...]
    rounds: tuple[VendorRound, ...]
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


def reserve_adjusted_bonus(case: ProcurementBundleCase, pair: tuple[str, str]) -> float:
    reserve_after_invoice = case.budget - bundle_price(case, pair)
    reserve_shortfall_penalty = 0.0010 * max(0.0, 180.0 - reserve_after_invoice)
    return compatibility_bonus(case, pair) - reserve_shortfall_penalty


def reserve_adjusted_case(case: ProcurementBundleCase) -> ProcurementBundleCase:
    return ProcurementBundleCase(
        key=case.key,
        profile=case.profile,
        budget=case.budget,
        required_categories=case.required_categories,
        products=case.products,
        compatibility_bonuses=tuple(
            (left, right, reserve_adjusted_bonus(case, (left, right)))
            for left, right in valid_bundles(case)
        ),
        scenario_note=case.scenario_note,
    )


PROCUREMENT_BUNDLE_RESERVE_CASES = [
    reserve_adjusted_case(case) for case in PROCUREMENT_BUNDLE_CASES
]

PROCUREMENT_VENDOR_UPDATE_CASES = [
    ProcurementVendorUpdateCase(
        key="clinic_kiosk_rollout",
        starting_reserve=410.0,
        reserve_floor=120.0,
        reserve_penalty=0.035,
        switch_cost=12.0,
        scenario_note=(
            "The clinic needs three sequential kiosk batches. A late batch causes rebooking "
            "and temporary staffing cost, so delivery history should update vendor choice."
        ),
        vendors=(
            VendorOption("budget_lane", 76.0, 0.92, 20, 8),
            VendorOption("steady_med", 108.0, 0.88, 24, 21),
            VendorOption("white_glove", 142.0, 0.93, 18, 18),
        ),
        rounds=(
            VendorRound("batch_1", 168.0, 58.0),
            VendorRound("batch_2", 185.0, 135.0),
            VendorRound("batch_3", 174.0, 92.0),
        ),
    ),
    ProcurementVendorUpdateCase(
        key="field_sensor_refresh",
        starting_reserve=455.0,
        reserve_floor=135.0,
        reserve_penalty=0.04,
        switch_cost=16.0,
        scenario_note=(
            "Field sensors are replaced in waves. The middle wave supports a regulatory "
            "inspection, while the first and last waves have more scheduling slack."
        ),
        vendors=(
            VendorOption("low_bid", 82.0, 0.95, 22, 10),
            VendorOption("regional_reliable", 118.0, 0.90, 26, 23),
            VendorOption("expedite_prime", 154.0, 0.92, 20, 20),
        ),
        rounds=(
            VendorRound("wave_1", 176.0, 48.0),
            VendorRound("wave_2", 208.0, 168.0),
            VendorRound("wave_3", 181.0, 70.0),
        ),
    ),
    ProcurementVendorUpdateCase(
        key="training_room_cutover",
        starting_reserve=390.0,
        reserve_floor=115.0,
        reserve_penalty=0.045,
        switch_cost=10.0,
        scenario_note=(
            "Training-room hardware is installed over three weekends. Late delivery in the "
            "final weekend blocks a client launch, but overpaying every weekend strains reserve."
        ),
        vendors=(
            VendorOption("discount_av", 72.0, 0.86, 18, 7),
            VendorOption("campus_supply", 104.0, 0.87, 25, 21),
            VendorOption("launch_ready", 138.0, 0.91, 16, 16),
        ),
        rounds=(
            VendorRound("weekend_1", 150.0, 46.0),
            VendorRound("weekend_2", 161.0, 78.0),
            VendorRound("weekend_3", 190.0, 172.0),
        ),
    ),
    ProcurementVendorUpdateCase(
        key="warehouse_scanner_rollout",
        starting_reserve=430.0,
        reserve_floor=130.0,
        reserve_penalty=0.04,
        switch_cost=14.0,
        scenario_note=(
            "Scanner kits deploy across three warehouses. The first site can absorb delay; "
            "later sites depend on synchronized labor windows and need reliability updates."
        ),
        vendors=(
            VendorOption("auction_liquidator", 68.0, 0.82, 16, 5),
            VendorOption("fleet_supplier", 112.0, 0.90, 28, 25),
            VendorOption("priority_fulfill", 148.0, 0.91, 19, 19),
        ),
        rounds=(
            VendorRound("site_1", 145.0, 38.0),
            VendorRound("site_2", 188.0, 142.0),
            VendorRound("site_3", 202.0, 156.0),
        ),
    ),
]

PROCUREMENT_VENDOR_UPDATE_NOISY_CASES = PROCUREMENT_VENDOR_UPDATE_CASES


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
    return _run_procurement_bundle_game(
        agent,
        cases=cases,
        system=PROCUREMENT_BUNDLE_SYSTEM,
        prompt_builder=_bundle_prompt,
        task_name="procurement_bundle",
    )


def run_procurement_bundle_natural_game(
    agent: Agent,
    cases: list[ProcurementBundleCase] | None = None,
) -> dict:
    return _run_procurement_bundle_game(
        agent,
        cases=cases,
        system=PROCUREMENT_BUNDLE_NATURAL_SYSTEM,
        prompt_builder=_bundle_natural_prompt,
        task_name="procurement_bundle_natural",
    )


def run_procurement_bundle_evidence_game(
    agent: Agent,
    cases: list[ProcurementBundleCase] | None = None,
) -> dict:
    return _run_procurement_bundle_game(
        agent,
        cases=cases,
        system=PROCUREMENT_BUNDLE_EVIDENCE_SYSTEM,
        prompt_builder=_bundle_evidence_prompt,
        task_name="procurement_bundle_evidence",
    )


def run_procurement_bundle_noisy_evidence_game(
    agent: Agent,
    cases: list[ProcurementBundleCase] | None = None,
) -> dict:
    return _run_procurement_bundle_game(
        agent,
        cases=cases,
        system=PROCUREMENT_BUNDLE_NOISY_EVIDENCE_SYSTEM,
        prompt_builder=_bundle_noisy_evidence_prompt,
        task_name="procurement_bundle_noisy_evidence",
    )


def run_procurement_bundle_history_game(
    agent: Agent,
    cases: list[ProcurementBundleCase] | None = None,
) -> dict:
    return _run_procurement_bundle_game(
        agent,
        cases=cases,
        system=PROCUREMENT_BUNDLE_HISTORY_SYSTEM,
        prompt_builder=_bundle_history_prompt,
        task_name="procurement_bundle_history",
    )


def run_procurement_bundle_reserve_game(
    agent: Agent,
    cases: list[ProcurementBundleCase] | None = None,
) -> dict:
    return _run_procurement_bundle_game(
        agent,
        cases=cases or PROCUREMENT_BUNDLE_RESERVE_CASES,
        system=PROCUREMENT_BUNDLE_RESERVE_SYSTEM,
        prompt_builder=_bundle_reserve_prompt,
        task_name="procurement_bundle_reserve",
    )


def run_procurement_vendor_update_game(
    agent: Agent,
    cases: list[ProcurementVendorUpdateCase] | None = None,
) -> dict:
    return _run_procurement_vendor_update_game(
        agent,
        cases=cases or PROCUREMENT_VENDOR_UPDATE_CASES,
        system=PROCUREMENT_VENDOR_UPDATE_SYSTEM,
        prompt_builder=_vendor_update_prompt,
        task_name="procurement_vendor_update",
    )


def run_procurement_vendor_update_noisy_game(
    agent: Agent,
    cases: list[ProcurementVendorUpdateCase] | None = None,
) -> dict:
    return _run_procurement_vendor_update_game(
        agent,
        cases=cases or PROCUREMENT_VENDOR_UPDATE_NOISY_CASES,
        system=PROCUREMENT_VENDOR_UPDATE_NOISY_SYSTEM,
        prompt_builder=_vendor_update_noisy_prompt,
        task_name="procurement_vendor_update_noisy",
    )


def _run_procurement_vendor_update_game(
    agent: Agent,
    *,
    cases: list[ProcurementVendorUpdateCase],
    system: str,
    prompt_builder,
    task_name: str,
) -> dict:
    rows = []
    for case in cases:
        oracle = oracle_vendor_plan(case)
        reputation_blind = reputation_blind_vendor_plan(case)
        myopic = myopic_vendor_plan(case)
        response = agent.complete(system, prompt_builder(case))
        chosen = _parse_vendor_plan(response, len(case.rounds))
        row = _score_vendor_plan_case(case, chosen, response)
        row["oracle_plan"] = oracle
        row["correct"] = chosen == oracle
        row["reputation_blind_plan"] = reputation_blind
        row["myopic_plan"] = myopic
        rows.append(row)
    total = len(rows)
    reputation_blind_missable = [
        row for row in rows if row["reputation_blind_plan"] != row["oracle_plan"]
    ]
    myopic_missable = [row for row in rows if row["myopic_plan"] != row["oracle_plan"]]
    return {
        "task": task_name,
        "agent": agent.name,
        "n_trials": total,
        "accuracy": sum(row["correct"] for row in rows) / total if total else 0.0,
        "mean_score_regret": sum(row["score_regret"] for row in rows) / total if total else 0.0,
        "parse_rate": sum(row["chosen_plan"] is not None for row in rows) / total if total else 0.0,
        "reputation_blind_miss_rate": (
            sum(row["reputation_blind_miss"] for row in reputation_blind_missable)
            / len(reputation_blind_missable)
            if reputation_blind_missable
            else 0.0
        ),
        "myopic_miss_rate": (
            sum(row["myopic_miss"] for row in myopic_missable) / len(myopic_missable)
            if myopic_missable
            else 0.0
        ),
        "trials": rows,
    }


def _run_procurement_bundle_game(
    agent: Agent,
    *,
    cases: list[ProcurementBundleCase] | None,
    system: str,
    prompt_builder,
    task_name: str,
) -> dict:
    cases = cases or PROCUREMENT_BUNDLE_CASES
    rows = []
    for case in cases:
        oracle = oracle_bundle(case)
        response = agent.complete(system, prompt_builder(case))
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
        "task": task_name,
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


def _score_vendor_plan_case(
    case: ProcurementVendorUpdateCase,
    chosen: tuple[str, ...] | None,
    response: str,
) -> dict:
    oracle = oracle_vendor_plan(case)
    best_score = vendor_plan_score(case, oracle)
    valid_ids = {vendor.vendor_id for vendor in case.vendors}
    valid = chosen is not None and len(chosen) == len(case.rounds) and all(item in valid_ids for item in chosen)
    chosen_score = vendor_plan_score(case, chosen) if chosen is not None and valid else best_score - 1000.0
    reputation_blind = reputation_blind_vendor_plan(case)
    myopic = myopic_vendor_plan(case)
    return {
        "case": case.key,
        "oracle_plan": oracle,
        "chosen_plan": chosen,
        "score": chosen_score,
        "score_regret": best_score - chosen_score,
        "invalid": not valid,
        "reputation_blind_plan": reputation_blind,
        "reputation_blind_miss": chosen == reputation_blind and reputation_blind != oracle,
        "myopic_plan": myopic,
        "myopic_miss": chosen == myopic and myopic != oracle,
        "raw_response": response,
        "case_data": asdict(case),
    }


def vendor_reliability(vendor: VendorOption, *, reputation_blind: bool = False) -> float:
    if reputation_blind:
        return 0.80
    return (vendor.on_time_shipments + 2.0) / (vendor.shipments_observed + 4.0)


def vendor_round_score(
    vendor: VendorOption,
    round_case: VendorRound,
    *,
    reputation_blind: bool = False,
) -> float:
    reliability = vendor_reliability(vendor, reputation_blind=reputation_blind)
    return (
        round_case.service_value * vendor.operational_fit
        - vendor.invoice
        - (1.0 - reliability) * round_case.late_penalty
    )


def vendor_plan_score(
    case: ProcurementVendorUpdateCase,
    plan: tuple[str, ...],
    *,
    reputation_blind: bool = False,
    include_switch_and_reserve: bool = True,
) -> float:
    vendors = {vendor.vendor_id: vendor for vendor in case.vendors}
    cash = case.starting_reserve
    previous_vendor = None
    score = 0.0
    for vendor_id, round_case in zip(plan, case.rounds):
        vendor = vendors[vendor_id]
        switch_cost = (
            case.switch_cost
            if include_switch_and_reserve and previous_vendor is not None and previous_vendor != vendor_id
            else 0.0
        )
        cash -= vendor.invoice + switch_cost
        score += vendor_round_score(vendor, round_case, reputation_blind=reputation_blind) - switch_cost
        if include_switch_and_reserve:
            score -= case.reserve_penalty * max(0.0, case.reserve_floor - cash)
            score -= 4.0 * max(0.0, -cash)
        previous_vendor = vendor_id
    return score


def oracle_vendor_plan(case: ProcurementVendorUpdateCase) -> tuple[str, ...]:
    return _best_vendor_plan(case)


def reputation_blind_vendor_plan(case: ProcurementVendorUpdateCase) -> tuple[str, ...]:
    return _best_vendor_plan(case, reputation_blind=True)


def myopic_vendor_plan(case: ProcurementVendorUpdateCase) -> tuple[str, ...]:
    plan = []
    for round_case in case.rounds:
        plan.append(max(case.vendors, key=lambda vendor: vendor_round_score(vendor, round_case)).vendor_id)
    return tuple(plan)


def _best_vendor_plan(
    case: ProcurementVendorUpdateCase,
    *,
    reputation_blind: bool = False,
) -> tuple[str, ...]:
    vendor_ids = [vendor.vendor_id for vendor in case.vendors]
    return max(
        cartesian_product(vendor_ids, repeat=len(case.rounds)),
        key=lambda plan: vendor_plan_score(case, plan, reputation_blind=reputation_blind),
    )


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


def _bundle_natural_prompt(case: ProcurementBundleCase) -> str:
    lines = [
        f"case={case.key}",
        f"buying_team={case.profile.key}",
        f"spend_limit={case.budget:.0f}",
        f"must_cover_lines={','.join(case.required_categories)}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Candidate SKUs:")
    for product in case.products:
        lines.append(
            "  "
            + " ".join(
                [
                    f"sku={product.product_id}",
                    f"line={product.category}",
                    f"invoice={product.price:.0f}",
                    f"field_reliability={product.durability:.2f}",
                    f"operator_fit={product.comfort:.2f}",
                    f"presentation_fit={product.style_fit:.2f}",
                    f"deployment_drag={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Package fit notes:")
    for left, right, bonus in case.compatibility_bonuses:
        lines.append(f"  bundle_pair={left},{right} service_fit_delta={bonus:.2f}")
    lines.append("Buying team priorities:")
    lines.append(
        " ".join(
            [
                f"invoice_penalty={case.profile.price_weight:.4f}",
                f"reliability_weight={case.profile.durability_weight:.4f}",
                f"operator_fit_weight={case.profile.comfort_weight:.4f}",
                f"presentation_weight={case.profile.style_weight:.4f}",
                f"deployment_drag_weight={case.profile.friction_weight:.4f}",
            ]
        )
    )
    lines.append(
        "Pick the two-SKU package with the best total procurement fit after spend, "
        "line coverage, deployment drag, and package-fit notes."
    )
    return "\n".join(lines)


def _bundle_evidence_prompt(case: ProcurementBundleCase) -> str:
    lines = [
        f"case={case.key}",
        f"buying_team={case.profile.key}",
        f"spend_limit={case.budget:.0f}",
        f"must_cover_lines={','.join(case.required_categories)}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note.replace("compatibility", "package performance"))
    lines.append("Candidate SKUs:")
    for product in case.products:
        lines.append(
            "  "
            + " ".join(
                [
                    f"sku={product.product_id}",
                    f"line={product.category}",
                    f"invoice={product.price:.0f}",
                    f"field_reliability={product.durability:.2f}",
                    f"operator_fit={product.comfort:.2f}",
                    f"presentation_fit={product.style_fit:.2f}",
                    f"deployment_drag={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Prior two-SKU deployment outcomes:")
    for left, right, bonus in case.compatibility_bonuses:
        lines.append(
            "  "
            + " ".join(
                [
                    f"pilot_pair={left},{right}",
                    f"rollout_hours_delta={-8.0 * bonus:.2f}",
                    f"support_ticket_delta={-4.0 * bonus:.2f}",
                    f"operator_acceptance_delta={0.12 * bonus:.3f}",
                ]
            )
        )
    lines.append("Buying team priorities:")
    lines.append(
        " ".join(
            [
                f"invoice_penalty={case.profile.price_weight:.4f}",
                f"reliability_weight={case.profile.durability_weight:.4f}",
                f"operator_fit_weight={case.profile.comfort_weight:.4f}",
                f"presentation_weight={case.profile.style_weight:.4f}",
                f"deployment_drag_weight={case.profile.friction_weight:.4f}",
            ]
        )
    )
    lines.append(
        "Use the pilot outcome rows to infer whether a pair reduces or increases "
        "deployment burden, then pick the two-SKU package with the best total "
        "procurement fit."
    )
    return "\n".join(lines)


def _bundle_noisy_evidence_prompt(case: ProcurementBundleCase) -> str:
    lines = [
        f"case={case.key}",
        f"buying_team={case.profile.key}",
        f"spend_limit={case.budget:.0f}",
        f"must_cover_lines={','.join(case.required_categories)}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note.replace("compatibility", "package performance"))
    lines.append("Candidate SKUs:")
    for product in case.products:
        lines.append(
            "  "
            + " ".join(
                [
                    f"sku={product.product_id}",
                    f"line={product.category}",
                    f"invoice={product.price:.0f}",
                    f"field_reliability={product.durability:.2f}",
                    f"operator_fit={product.comfort:.2f}",
                    f"presentation_fit={product.style_fit:.2f}",
                    f"deployment_drag={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Noisy prior two-SKU deployment measurements:")
    noise_rows = ((1.20, 0.45, -0.010), (-0.70, -0.25, 0.004), (-0.50, -0.20, 0.006))
    for left, right, bonus in case.compatibility_bonuses:
        base_hours = -8.0 * bonus
        base_tickets = -4.0 * bonus
        base_acceptance = 0.12 * bonus
        for run_id, (hour_noise, ticket_noise, acceptance_noise) in enumerate(noise_rows, start=1):
            lines.append(
                "  "
                + " ".join(
                    [
                        f"deployment_run={run_id}",
                        f"pilot_pair={left},{right}",
                        f"rollout_hours_delta={base_hours + hour_noise:.2f}",
                        f"support_ticket_delta={base_tickets + ticket_noise:.2f}",
                        f"operator_acceptance_delta={base_acceptance + acceptance_noise:.3f}",
                    ]
                )
            )
    lines.append("Buying team priorities:")
    lines.append(
        " ".join(
            [
                f"invoice_penalty={case.profile.price_weight:.4f}",
                f"reliability_weight={case.profile.durability_weight:.4f}",
                f"operator_fit_weight={case.profile.comfort_weight:.4f}",
                f"presentation_weight={case.profile.style_weight:.4f}",
                f"deployment_drag_weight={case.profile.friction_weight:.4f}",
            ]
        )
    )
    lines.append(
        "Treat individual deployment rows as noisy measurements. Aggregate the field "
        "evidence by SKU pair before deciding which package best serves the buying team."
    )
    return "\n".join(lines)


def _bundle_history_prompt(case: ProcurementBundleCase) -> str:
    lines = [
        f"case={case.key}",
        f"buying_team={case.profile.key}",
        f"spend_limit={case.budget:.0f}",
        f"must_cover_lines={','.join(case.required_categories)}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note.replace("compatibility", "deployment history"))
    lines.append("Candidate SKUs:")
    for product in case.products:
        lines.append(
            "  "
            + " ".join(
                [
                    f"sku={product.product_id}",
                    f"line={product.category}",
                    f"invoice={product.price:.0f}",
                    f"field_reliability={product.durability:.2f}",
                    f"operator_fit={product.comfort:.2f}",
                    f"presentation_fit={product.style_fit:.2f}",
                    f"deployment_drag={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Deployment-history value conversion:")
    lines.append(
        "package_history_delta = 0.010*rollout_hours_saved "
        "+ 0.040*support_tickets_prevented + 0.080*training_rework_prevented"
    )
    lines.append("Negative prevented values mean the package created extra operational burden.")
    lines.append("Multi-period deployment history:")
    periods = ("2025Q1", "2025Q2", "2025Q3")
    noise_rows = ((2.40, -0.40, 0.15), (-1.60, 0.80, -0.05), (-0.80, -0.40, -0.10))
    for left, right, bonus in case.compatibility_bonuses:
        base_hours = 60.0 * bonus
        base_tickets = 6.0 * bonus
        base_rework = 2.0 * bonus
        for period, (hour_noise, ticket_noise, rework_noise) in zip(periods, noise_rows):
            lines.append(
                "  "
                + " ".join(
                    [
                        f"period={period}",
                        f"pilot_pair={left},{right}",
                        f"rollout_hours_saved={base_hours + hour_noise:.2f}",
                        f"support_tickets_prevented={base_tickets + ticket_noise:.2f}",
                        f"training_rework_prevented={base_rework + rework_noise:.2f}",
                    ]
                )
            )
    lines.append("Buying team priorities:")
    lines.append(
        " ".join(
            [
                f"invoice_penalty={case.profile.price_weight:.4f}",
                f"reliability_weight={case.profile.durability_weight:.4f}",
                f"operator_fit_weight={case.profile.comfort_weight:.4f}",
                f"presentation_weight={case.profile.style_weight:.4f}",
                f"deployment_drag_weight={case.profile.friction_weight:.4f}",
            ]
        )
    )
    lines.append(
        "Aggregate the deployment history by SKU pair, convert it into package value, "
        "and combine that with the buying team's item priorities."
    )
    return "\n".join(lines)


def _bundle_reserve_prompt(case: ProcurementBundleCase) -> str:
    lines = [
        f"case={case.key}",
        f"buying_team={case.profile.key}",
        f"spend_limit={case.budget:.0f}",
        f"must_cover_lines={','.join(case.required_categories)}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note.replace("compatibility", "support-reserve risk"))
    lines.append("Candidate SKUs:")
    for product in case.products:
        lines.append(
            "  "
            + " ".join(
                [
                    f"sku={product.product_id}",
                    f"line={product.category}",
                    f"invoice={product.price:.0f}",
                    f"field_reliability={product.durability:.2f}",
                    f"operator_fit={product.comfort:.2f}",
                    f"presentation_fit={product.style_fit:.2f}",
                    f"deployment_drag={product.assembly_friction:.2f}",
                ]
            )
        )
    lines.append("Support-reserve value conversion:")
    lines.append(
        "package_reserve_delta = 0.010*rollout_hours_saved "
        "- 0.030*expected_support_tickets "
        "- 0.070*tail_probability*max(0, tail_support_cost - reserve_after_invoice)"
    )
    lines.append("Support-reserve scenarios:")
    for left, right, delta in case.compatibility_bonuses:
        reserve_after_invoice = case.budget - bundle_price(case, (left, right))
        tail_probability = 0.25
        if delta >= 0:
            rollout_hours_saved = delta / 0.010
            expected_support_tickets = 0.0
            tail_support_cost = reserve_after_invoice
        else:
            rollout_hours_saved = 0.0
            expected_support_tickets = (-delta * 0.40) / 0.030
            shortfall = (-delta * 0.60) / (0.070 * tail_probability)
            tail_support_cost = reserve_after_invoice + shortfall
        lines.append(
            "  "
            + " ".join(
                [
                    f"reserve_pair={left},{right}",
                    f"reserve_after_invoice={reserve_after_invoice:.2f}",
                    f"rollout_hours_saved={rollout_hours_saved:.2f}",
                    f"expected_support_tickets={expected_support_tickets:.2f}",
                    f"tail_probability={tail_probability:.2f}",
                    f"tail_support_cost={tail_support_cost:.2f}",
                ]
            )
        )
    lines.append("Buying team priorities:")
    lines.append(
        " ".join(
            [
                f"invoice_penalty={case.profile.price_weight:.4f}",
                f"reliability_weight={case.profile.durability_weight:.4f}",
                f"operator_fit_weight={case.profile.comfort_weight:.4f}",
                f"presentation_weight={case.profile.style_weight:.4f}",
                f"deployment_drag_weight={case.profile.friction_weight:.4f}",
            ]
        )
    )
    lines.append(
        "For each feasible pair, combine item priorities with the support-reserve "
        "scenario value. Avoid packages whose tail support cost consumes the reserve."
    )
    return "\n".join(lines)


def _vendor_update_prompt(case: ProcurementVendorUpdateCase) -> str:
    lines = [
        f"case={case.key}",
        f"starting_reserve={case.starting_reserve:.2f}",
        f"reserve_floor={case.reserve_floor:.2f}",
        f"reserve_penalty={case.reserve_penalty:.4f}",
        f"switch_cost={case.switch_cost:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Procurement rounds:")
    for round_case in case.rounds:
        lines.append(
            "  "
            + " ".join(
                [
                    f"round={round_case.round_id}",
                    f"service_value={round_case.service_value:.2f}",
                    f"late_penalty={round_case.late_penalty:.2f}",
                ]
            )
        )
    lines.append("Vendor delivery history:")
    for vendor in case.vendors:
        late = vendor.shipments_observed - vendor.on_time_shipments
        lines.append(
            "  "
            + " ".join(
                [
                    f"vendor_id={vendor.vendor_id}",
                    f"invoice={vendor.invoice:.2f}",
                    f"operational_fit={vendor.operational_fit:.2f}",
                    f"shipments_observed={vendor.shipments_observed}",
                    f"on_time_shipments={vendor.on_time_shipments}",
                    f"late_shipments={late}",
                ]
            )
        )
    lines.append(
        "Choose one vendor for each round in order. Use delivery history to estimate "
        "late risk, subtract invoices from reserve as rounds are ordered, pay the switch "
        "cost when changing vendors, and penalize reserve shortfalls below the floor."
    )
    return "\n".join(lines)


def _vendor_update_noisy_prompt(case: ProcurementVendorUpdateCase) -> str:
    lines = [
        f"case={case.key}",
        f"starting_reserve={case.starting_reserve:.2f}",
        f"reserve_floor={case.reserve_floor:.2f}",
        f"reserve_penalty={case.reserve_penalty:.4f}",
        f"switch_cost={case.switch_cost:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note.replace("delivery history", "noisy receiving history"))
    lines.append("Procurement rounds:")
    for round_case in case.rounds:
        lines.append(
            "  "
            + " ".join(
                [
                    f"round={round_case.round_id}",
                    f"service_value={round_case.service_value:.2f}",
                    f"late_penalty={round_case.late_penalty:.2f}",
                ]
            )
        )
    lines.append("Candidate vendors:")
    for vendor in case.vendors:
        lines.append(
            "  "
            + " ".join(
                [
                    f"vendor_id={vendor.vendor_id}",
                    f"invoice={vendor.invoice:.2f}",
                    f"operational_fit={vendor.operational_fit:.2f}",
                ]
            )
        )
    lines.append("Noisy receiving ledger:")
    for vendor in case.vendors:
        for receiving_area, deliveries, on_window in _vendor_receiving_rows(vendor):
            lines.append(
                "  "
                + " ".join(
                    [
                        f"vendor_id={vendor.vendor_id}",
                        f"receiving_area={receiving_area}",
                        f"deliveries={deliveries}",
                        f"on_window_deliveries={on_window}",
                        f"late_or_incomplete={deliveries - on_window}",
                    ]
                )
            )
    lines.append(
        "Treat the receiving ledger as noisy field evidence. Aggregate deliveries by "
        "vendor to estimate late risk, subtract invoices from reserve as rounds are "
        "ordered, pay the switch cost when changing vendors, and penalize reserve "
        "shortfalls below the floor."
    )
    return "\n".join(lines)


def _vendor_receiving_rows(vendor: VendorOption) -> tuple[tuple[str, int, int], ...]:
    deliveries = _split_count(vendor.shipments_observed, weights=(0.45, 0.30, 0.25))
    late = vendor.shipments_observed - vendor.on_time_shipments
    late_parts = _split_capped_count(late, deliveries, weights=(0.20, 0.50, 0.30))
    areas = ("north_dock", "south_dock", "after_hours")
    return tuple(
        (area, delivered, delivered - late_count)
        for area, delivered, late_count in zip(areas, deliveries, late_parts)
    )


def _split_count(total: int, *, weights: tuple[float, ...]) -> tuple[int, ...]:
    parts = [int(total * weight) for weight in weights]
    remainder = total - sum(parts)
    for index in range(remainder):
        parts[index % len(parts)] += 1
    return tuple(parts)


def _split_capped_count(
    total: int,
    caps: tuple[int, ...],
    *,
    weights: tuple[float, ...],
) -> tuple[int, ...]:
    parts = [min(cap, int(total * weight)) for cap, weight in zip(caps, weights)]
    remaining = total - sum(parts)
    order = sorted(range(len(caps)), key=lambda index: weights[index], reverse=True)
    while remaining > 0:
        progressed = False
        for index in order:
            if parts[index] < caps[index]:
                parts[index] += 1
                remaining -= 1
                progressed = True
                if remaining == 0:
                    break
        if not progressed:
            break
    return tuple(parts)


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


def _parse_vendor_plan(response: str, expected_len: int) -> tuple[str, ...] | None:
    match = re.search(
        r"FINAL_VENDOR_PLAN\s*:\s*([a-zA-Z0-9_,-]+)",
        response,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    plan = tuple(item for item in match.group(1).split(",") if item)
    return plan if len(plan) == expected_len else None
