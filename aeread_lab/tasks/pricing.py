from __future__ import annotations

import random
from dataclasses import dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float, parse_token


PRICING_SYSTEM = (
    "TASK: pricing_price\n"
    "Choose a price. Return one final line only: FINAL_PRICE: <number>."
)

PRICING_CROSS_SYSTEM = (
    "TASK: pricing_cross_price\n"
    "Choose the focal product price. Return one final line only: FINAL_PRICE: <number>."
)

PRICING_MULTI_SYSTEM = (
    "TASK: pricing_multi_product_prices\n"
    "Choose prices for both products. Return two final lines only: "
    "FINAL_PRICE_A: <number> and FINAL_PRICE_B: <number>."
)

PRICING_MULTI_NATURAL_SYSTEM = (
    "TASK: pricing_multi_product_natural_prices\n"
    "Choose prices for both products. Return two final lines only: "
    "FINAL_PRICE_A: <number> and FINAL_PRICE_B: <number>."
)

PRICING_MULTI_CAPACITY_SYSTEM = (
    "TASK: pricing_multi_product_capacity_prices\n"
    "Choose prices for both products with finite stock available. Return two final lines only: "
    "FINAL_PRICE_A: <number> and FINAL_PRICE_B: <number>."
)

PRICING_MULTI_CAPACITY_NOISY_SYSTEM = (
    "TASK: pricing_multi_product_capacity_noisy_prices\n"
    "Choose prices for both products using lumpy sales evidence and finite stock available. "
    "Return two final lines only: FINAL_PRICE_A: <number> and FINAL_PRICE_B: <number>."
)

PRICING_INVENTORY_MARKDOWN_SYSTEM = (
    "TASK: pricing_inventory_markdown_prices\n"
    "Choose early and late campaign prices for one shared inventory pool. Return two final lines only: "
    "FINAL_PRICE_EARLY: <number> and FINAL_PRICE_LATE: <number>."
)

PRICING_INVENTORY_MARKDOWN_NOISY_SYSTEM = (
    "TASK: pricing_inventory_markdown_noisy_prices\n"
    "Choose launch and clearance prices for one shared inventory pool. Return two final lines only: "
    "FINAL_PRICE_EARLY: <number> and FINAL_PRICE_LATE: <number>."
)

PRICING_MULTI_PRODUCT_MARKDOWN_NOISY_SYSTEM = (
    "TASK: pricing_multi_product_markdown_noisy_prices\n"
    "Choose launch and clearance prices for two products using lumpy regional evidence and finite stock. "
    "Return four final lines only: FINAL_PRICE_A_EARLY: <number>, FINAL_PRICE_B_EARLY: <number>, "
    "FINAL_PRICE_A_LATE: <number>, and FINAL_PRICE_B_LATE: <number>."
)

PRICING_INVENTORY_REPLENISHMENT_NOISY_SYSTEM = (
    "TASK: pricing_inventory_replenishment_noisy_plan\n"
    "Choose a launch price, replenishment quantity, and clearance price using lumpy regional evidence. "
    "Return three final lines only: FINAL_PRICE_EARLY: <number>, "
    "FINAL_REPLENISHMENT_UNITS: <number>, and FINAL_PRICE_LATE: <number>."
)

PRICING_HIDDEN_INTERVENTION_SYSTEM = (
    "TASK: pricing_hidden_intervention_price\n"
    "Choose the price for the next normal campaign after accounting for non-price interventions. "
    "Return one final line only: FINAL_PRICE: <number>."
)

PRICING_LAW_SYSTEM = (
    "TASK: pricing_law_label\n"
    "You are verifying a proposed comparative-static claim about the revenue-maximizing price. "
    "Return one final line only: FINAL_LABEL: valid or FINAL_LABEL: invalid."
)

PRICING_EVIDENCE_LAW_SYSTEM = (
    "TASK: pricing_evidence_law_label\n"
    "You are verifying a proposed claim about how the revenue-maximizing price changes after "
    "new sales evidence. Return one final line only: FINAL_LABEL: valid or FINAL_LABEL: invalid."
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
class PricingCrossCase:
    key: str
    p_max: float
    planned_related_price: float
    observations: tuple[tuple[float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingMultiProductCase:
    key: str
    p_max_a: float
    p_max_b: float
    observations: tuple[tuple[float, float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingMultiProductCapacityCase:
    key: str
    p_max_a: float
    p_max_b: float
    inventory_a: float
    inventory_b: float
    observations: tuple[tuple[float, float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingInventoryMarkdownCase:
    key: str
    p_max_early: float
    p_max_late: float
    inventory: float
    salvage_value: float
    observations: tuple[tuple[float, float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingInventoryReplenishmentCase:
    key: str
    p_max_early: float
    p_max_late: float
    starting_inventory: float
    max_replenishment_units: float
    storage_capacity: float
    replenishment_unit_cost: float
    replenishment_setup_cost: float
    salvage_value: float
    observations: tuple[tuple[float, float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingMultiProductMarkdownCase:
    key: str
    p_max_a: float
    p_max_b: float
    inventory_a: float
    inventory_b: float
    salvage_value_a: float
    salvage_value_b: float
    observations: tuple[tuple[float, float, float, float, float, float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingInterventionCase:
    key: str
    p_max: float
    observations: tuple[tuple[float, float, float, float], ...]
    scenario_note: str = ""


@dataclass(frozen=True)
class PricingCounterfactualSet:
    key: str
    base: PricingEvidenceCase
    perturbed: PricingEvidenceCase


@dataclass(frozen=True)
class PricingLawCase:
    key: str
    base_alpha: float
    base_beta: float
    base_p_max: float
    new_alpha: float
    new_beta: float
    new_p_max: float
    relation: str
    law_family: str


@dataclass(frozen=True)
class PricingEvidenceLawCase:
    key: str
    case_set: PricingCounterfactualSet
    relation: str
    law_family: str


@dataclass
class PricingLawTrial:
    case: PricingLawCase
    base_price: float
    new_price: float
    oracle_label: str
    chosen_label: str | None
    correct: bool
    invalid_accept: bool
    valid_reject: bool
    raw_response: str


@dataclass
class PricingEvidenceLawTrial:
    case: PricingEvidenceLawCase
    base_price: float
    new_price: float
    oracle_label: str
    chosen_label: str | None
    correct: bool
    invalid_accept: bool
    valid_reject: bool
    raw_response: str


def _cross_observations(
    alpha: float,
    own_beta: float,
    related_beta: float,
    p_max: float,
) -> tuple[tuple[float, float, float], ...]:
    pairs = ((0.22, 0.25), (0.34, 0.70), (0.46, 0.40), (0.58, 0.86), (0.70, 0.55), (0.82, 0.95))
    return tuple(
        (
            round(own_ratio * p_max, 2),
            round(related_ratio * p_max, 2),
            round(max(0.0, alpha - own_beta * own_ratio * p_max + related_beta * related_ratio * p_max), 2),
        )
        for own_ratio, related_ratio in pairs
    )


def _multi_product_observations(
    alpha_a: float,
    own_beta_a: float,
    cross_ab: float,
    alpha_b: float,
    own_beta_b: float,
    cross_ba: float,
    p_max_a: float,
    p_max_b: float,
) -> tuple[tuple[float, float, float, float], ...]:
    pairs = ((0.24, 0.28), (0.36, 0.72), (0.48, 0.40), (0.60, 0.84), (0.72, 0.55), (0.84, 0.92))
    return tuple(
        (
            round(a_ratio * p_max_a, 2),
            round(b_ratio * p_max_b, 2),
            round(max(0.0, alpha_a - own_beta_a * a_ratio * p_max_a + cross_ab * b_ratio * p_max_b), 2),
            round(max(0.0, alpha_b - own_beta_b * b_ratio * p_max_b + cross_ba * a_ratio * p_max_a), 2),
        )
        for a_ratio, b_ratio in pairs
    )


def _noisy_multi_product_observations(
    alpha_a: float,
    own_beta_a: float,
    cross_ab: float,
    alpha_b: float,
    own_beta_b: float,
    cross_ba: float,
    p_max_a: float,
    p_max_b: float,
    noise_a: tuple[float, ...],
    noise_b: tuple[float, ...],
) -> tuple[tuple[float, float, float, float], ...]:
    base = _multi_product_observations(
        alpha_a,
        own_beta_a,
        cross_ab,
        alpha_b,
        own_beta_b,
        cross_ba,
        p_max_a,
        p_max_b,
    )
    return tuple(
        (
            price_a,
            price_b,
            round(max(0.0, quantity_a + noise_a[idx]), 2),
            round(max(0.0, quantity_b + noise_b[idx]), 2),
        )
        for idx, (price_a, price_b, quantity_a, quantity_b) in enumerate(base)
    )


def _markdown_observations(
    early_alpha: float,
    early_beta: float,
    late_alpha: float,
    late_beta: float,
    p_max_early: float,
    p_max_late: float,
) -> tuple[tuple[float, float, float, float], ...]:
    pairs = ((0.24, 0.30), (0.36, 0.42), (0.48, 0.54), (0.60, 0.66), (0.72, 0.78), (0.84, 0.90))
    return tuple(
        (
            round(early_ratio * p_max_early, 2),
            round(max(0.0, early_alpha - early_beta * early_ratio * p_max_early), 2),
            round(late_ratio * p_max_late, 2),
            round(max(0.0, late_alpha - late_beta * late_ratio * p_max_late), 2),
        )
        for early_ratio, late_ratio in pairs
    )


def _noisy_markdown_observations(
    early_alpha: float,
    early_beta: float,
    late_alpha: float,
    late_beta: float,
    p_max_early: float,
    p_max_late: float,
    early_noise: tuple[float, ...],
    late_noise: tuple[float, ...],
) -> tuple[tuple[float, float, float, float], ...]:
    pairs = ((0.22, 0.28), (0.31, 0.39), (0.43, 0.49), (0.52, 0.61), (0.64, 0.73), (0.76, 0.84), (0.88, 0.94))
    return tuple(
        (
            round(early_ratio * p_max_early, 2),
            round(
                max(0.0, early_alpha - early_beta * early_ratio * p_max_early + early_noise[idx]),
                2,
            ),
            round(late_ratio * p_max_late, 2),
            round(
                max(0.0, late_alpha - late_beta * late_ratio * p_max_late + late_noise[idx]),
                2,
            ),
        )
        for idx, (early_ratio, late_ratio) in enumerate(pairs)
    )


def _noisy_multi_product_markdown_observations(
    early_alpha_a: float,
    early_own_a: float,
    early_cross_ab: float,
    early_alpha_b: float,
    early_own_b: float,
    early_cross_ba: float,
    late_alpha_a: float,
    late_own_a: float,
    late_cross_ab: float,
    late_alpha_b: float,
    late_own_b: float,
    late_cross_ba: float,
    p_max_a: float,
    p_max_b: float,
    early_noise_a: tuple[float, ...],
    early_noise_b: tuple[float, ...],
    late_noise_a: tuple[float, ...],
    late_noise_b: tuple[float, ...],
) -> tuple[tuple[float, float, float, float, float, float, float, float], ...]:
    pairs = (
        (0.22, 0.28, 0.30, 0.34),
        (0.31, 0.39, 0.42, 0.46),
        (0.43, 0.49, 0.52, 0.56),
        (0.52, 0.61, 0.63, 0.67),
        (0.64, 0.73, 0.74, 0.78),
        (0.76, 0.84, 0.82, 0.88),
        (0.88, 0.94, 0.91, 0.96),
    )
    return tuple(
        (
            round(early_a_ratio * p_max_a, 2),
            round(early_b_ratio * p_max_b, 2),
            round(
                max(
                    0.0,
                    early_alpha_a
                    - early_own_a * early_a_ratio * p_max_a
                    + early_cross_ab * early_b_ratio * p_max_b
                    + early_noise_a[idx],
                ),
                2,
            ),
            round(
                max(
                    0.0,
                    early_alpha_b
                    - early_own_b * early_b_ratio * p_max_b
                    + early_cross_ba * early_a_ratio * p_max_a
                    + early_noise_b[idx],
                ),
                2,
            ),
            round(late_a_ratio * p_max_a, 2),
            round(late_b_ratio * p_max_b, 2),
            round(
                max(
                    0.0,
                    late_alpha_a
                    - late_own_a * late_a_ratio * p_max_a
                    + late_cross_ab * late_b_ratio * p_max_b
                    + late_noise_a[idx],
                ),
                2,
            ),
            round(
                max(
                    0.0,
                    late_alpha_b
                    - late_own_b * late_b_ratio * p_max_b
                    + late_cross_ba * late_a_ratio * p_max_a
                    + late_noise_b[idx],
                ),
                2,
            ),
        )
        for idx, (early_a_ratio, early_b_ratio, late_a_ratio, late_b_ratio) in enumerate(pairs)
    )


def _intervention_observations(
    alpha: float,
    beta: float,
    p_max: float,
    intervention_units: tuple[float, ...],
    exposure_multipliers: tuple[float, ...],
    normal_noise: tuple[float, ...],
) -> tuple[tuple[float, float, float, float], ...]:
    ratios = (0.24, 0.36, 0.48, 0.60, 0.72, 0.84)
    return tuple(
        (
            round(ratio * p_max, 2),
            round(
                max(0.0, alpha - beta * ratio * p_max + normal_noise[idx])
                * exposure_multipliers[idx]
                + intervention_units[idx],
                2,
            ),
            intervention_units[idx],
            exposure_multipliers[idx],
        )
        for idx, ratio in enumerate(ratios)
    )


DEFAULT_CASES = [
    PricingCase("snack_box", alpha=180.0, beta=6.0, sigma=4.0, p_max=30.0, seed=11),
    PricingCase("premium_widget", alpha=260.0, beta=4.0, sigma=6.0, p_max=55.0, seed=29),
]

CROSS_ELASTICITY_CASES = [
    PricingCrossCase(
        key="cross_case_01",
        p_max=45.0,
        planned_related_price=28.0,
        scenario_note="Set the focal product price for the next campaign.",
        observations=_cross_observations(alpha=130.0, own_beta=4.0, related_beta=2.0, p_max=45.0),
    ),
    PricingCrossCase(
        key="cross_case_02",
        p_max=45.0,
        planned_related_price=8.0,
        scenario_note="Set the focal product price for a different related-product promotion.",
        observations=_cross_observations(alpha=130.0, own_beta=4.0, related_beta=2.0, p_max=45.0),
    ),
    PricingCrossCase(
        key="cross_case_03",
        p_max=40.0,
        planned_related_price=8.0,
        scenario_note="Set the focal product price for a bundle-adjacent catalog page.",
        observations=_cross_observations(alpha=190.0, own_beta=5.0, related_beta=-2.0, p_max=40.0),
    ),
    PricingCrossCase(
        key="cross_case_04",
        p_max=45.0,
        planned_related_price=24.0,
        scenario_note="Set the focal product price after related-product placement changes.",
        observations=_cross_observations(alpha=190.0, own_beta=4.0, related_beta=-2.0, p_max=45.0),
    ),
    PricingCrossCase(
        key="cross_case_05",
        p_max=50.0,
        planned_related_price=36.0,
        scenario_note="Set the focal product price for a market with strong cross-product movement.",
        observations=_cross_observations(alpha=100.0, own_beta=3.0, related_beta=3.0, p_max=50.0),
    ),
    PricingCrossCase(
        key="cross_case_06",
        p_max=42.0,
        planned_related_price=9.0,
        scenario_note="Set the focal product price using the observed related-product variation.",
        observations=_cross_observations(alpha=220.0, own_beta=6.0, related_beta=-3.0, p_max=42.0),
    ),
]

MULTI_PRODUCT_CASES = [
    PricingMultiProductCase(
        key="multi_case_01",
        p_max_a=50.0,
        p_max_b=48.0,
        scenario_note="Two substitute products are promoted together; choose both prices jointly.",
        observations=_multi_product_observations(110.0, 4.5, 3.0, 105.0, 4.2, 3.0, 50.0, 48.0),
    ),
    PricingMultiProductCase(
        key="multi_case_02",
        p_max_a=65.0,
        p_max_b=60.0,
        scenario_note="The related products substitute asymmetrically; choose the joint campaign prices.",
        observations=_multi_product_observations(120.0, 4.0, 3.6, 125.0, 4.2, 3.6, 65.0, 60.0),
    ),
    PricingMultiProductCase(
        key="multi_case_03",
        p_max_a=55.0,
        p_max_b=55.0,
        scenario_note="The products are complements, so raising one price can reduce demand for the other.",
        observations=_multi_product_observations(330.0, 5.0, -3.2, 310.0, 4.8, -3.0, 55.0, 55.0),
    ),
    PricingMultiProductCase(
        key="multi_case_04",
        p_max_a=70.0,
        p_max_b=68.0,
        scenario_note="A high-demand bundle has asymmetric complement effects across products.",
        observations=_multi_product_observations(500.0, 5.0, -4.0, 480.0, 5.2, -3.8, 70.0, 68.0),
    ),
    PricingMultiProductCase(
        key="multi_case_05",
        p_max_a=45.0,
        p_max_b=44.0,
        scenario_note="Both product prices have tight campaign caps under substitute demand.",
        observations=_multi_product_observations(100.0, 4.0, 3.0, 100.0, 4.2, 3.2, 45.0, 44.0),
    ),
    PricingMultiProductCase(
        key="multi_case_06",
        p_max_a=60.0,
        p_max_b=52.0,
        scenario_note="Both capped products are complements with strong joint-demand effects.",
        observations=_multi_product_observations(360.0, 5.5, -3.5, 300.0, 4.6, -2.6, 60.0, 52.0),
    ),
]

MULTI_PRODUCT_CAPACITY_CASES = [
    PricingMultiProductCapacityCase(
        key="capacity_case_01",
        p_max_a=50.0,
        p_max_b=48.0,
        inventory_a=46.0,
        inventory_b=44.0,
        scenario_note=(
            "Two substitute products are promoted together, but the warehouse has limited "
            "stock for the campaign."
        ),
        observations=MULTI_PRODUCT_CASES[0].observations,
    ),
    PricingMultiProductCapacityCase(
        key="capacity_case_02",
        p_max_a=65.0,
        p_max_b=60.0,
        inventory_a=58.0,
        inventory_b=56.0,
        scenario_note=(
            "Substitute products share a campaign page; choose prices with finite inventory "
            "rather than chasing unconstrained unit demand."
        ),
        observations=MULTI_PRODUCT_CASES[1].observations,
    ),
    PricingMultiProductCapacityCase(
        key="capacity_case_03",
        p_max_a=55.0,
        p_max_b=55.0,
        inventory_a=90.0,
        inventory_b=85.0,
        scenario_note=(
            "Complementary products have large demand, but stock caps bind before the "
            "unconstrained revenue optimum."
        ),
        observations=MULTI_PRODUCT_CASES[2].observations,
    ),
    PricingMultiProductCapacityCase(
        key="capacity_case_04",
        p_max_a=70.0,
        p_max_b=68.0,
        inventory_a=150.0,
        inventory_b=145.0,
        scenario_note=(
            "A high-demand complement bundle has limited sellable units for each product."
        ),
        observations=MULTI_PRODUCT_CASES[3].observations,
    ),
]


MULTI_PRODUCT_CAPACITY_NOISY_CASES = [
    PricingMultiProductCapacityCase(
        key="noisy_capacity_case_01",
        p_max_a=50.0,
        p_max_b=48.0,
        inventory_a=46.0,
        inventory_b=44.0,
        scenario_note=(
            "Regional joint-campaign rows are lumpy, but finite stock still caps sellable "
            "units for the next campaign."
        ),
        observations=_noisy_multi_product_observations(
            110.0,
            4.5,
            3.0,
            105.0,
            4.2,
            3.0,
            50.0,
            48.0,
            (5.0, -4.0, 6.0, -5.0, 4.0, -3.0),
            (-3.0, 5.0, -4.0, 6.0, -5.0, 4.0),
        ),
    ),
    PricingMultiProductCapacityCase(
        key="noisy_capacity_case_02",
        p_max_a=65.0,
        p_max_b=60.0,
        inventory_a=58.0,
        inventory_b=56.0,
        scenario_note=(
            "The two substitute products share traffic, and several observed rows include "
            "local demand noise around the joint price effect."
        ),
        observations=_noisy_multi_product_observations(
            120.0,
            4.0,
            3.6,
            125.0,
            4.2,
            3.6,
            65.0,
            60.0,
            (6.0, -5.0, 7.0, -6.0, 4.0, -4.0),
            (-4.0, 6.0, -5.0, 5.0, -6.0, 4.0),
        ),
    ),
    PricingMultiProductCapacityCase(
        key="noisy_capacity_case_03",
        p_max_a=55.0,
        p_max_b=55.0,
        inventory_a=90.0,
        inventory_b=85.0,
        scenario_note=(
            "Complement-product rows are noisy and stock-constrained; pricing only to the "
            "unconstrained demand curve can waste scarce units."
        ),
        observations=_noisy_multi_product_observations(
            330.0,
            5.0,
            -3.2,
            310.0,
            4.8,
            -3.0,
            55.0,
            55.0,
            (8.0, -7.0, 6.0, -5.0, 7.0, -6.0),
            (-6.0, 7.0, -8.0, 6.0, -5.0, 7.0),
        ),
    ),
    PricingMultiProductCapacityCase(
        key="noisy_capacity_case_04",
        p_max_a=70.0,
        p_max_b=68.0,
        inventory_a=150.0,
        inventory_b=145.0,
        scenario_note=(
            "A high-demand complement bundle has noisy regional measurements and limited "
            "sellable units for each product."
        ),
        observations=_noisy_multi_product_observations(
            500.0,
            5.0,
            -4.0,
            480.0,
            5.2,
            -3.8,
            70.0,
            68.0,
            (9.0, -8.0, 7.0, -9.0, 6.0, -7.0),
            (-8.0, 9.0, -7.0, 8.0, -9.0, 6.0),
        ),
    ),
]


INVENTORY_MARKDOWN_CASES = [
    PricingInventoryMarkdownCase(
        key="markdown_case_01",
        p_max_early=60.0,
        p_max_late=55.0,
        inventory=85.0,
        salvage_value=4.0,
        scenario_note=(
            "The launch window has strong volume, but holding some units for the later "
            "campaign can be valuable because late buyers are less price-sensitive."
        ),
        observations=_markdown_observations(170.0, 3.2, 150.0, 2.0, 60.0, 55.0),
    ),
    PricingInventoryMarkdownCase(
        key="markdown_case_02",
        p_max_early=58.0,
        p_max_late=60.0,
        inventory=70.0,
        salvage_value=5.0,
        scenario_note=(
            "The early list can clear stock quickly, but the follow-up channel has a "
            "higher willingness to pay if inventory remains."
        ),
        observations=_markdown_observations(130.0, 2.4, 200.0, 3.0, 58.0, 60.0),
    ),
    PricingInventoryMarkdownCase(
        key="markdown_case_03",
        p_max_early=65.0,
        p_max_late=62.0,
        inventory=120.0,
        salvage_value=6.0,
        scenario_note=(
            "Early demand is broad, while the late campaign is smaller but more profitable "
            "per unit when stock is preserved."
        ),
        observations=_markdown_observations(260.0, 4.4, 210.0, 3.0, 65.0, 62.0),
    ),
    PricingInventoryMarkdownCase(
        key="markdown_case_04",
        p_max_early=70.0,
        p_max_late=68.0,
        inventory=95.0,
        salvage_value=3.0,
        scenario_note=(
            "A fast early channel competes with a scarce late allocation; unsold units "
            "can be liquidated only at low salvage value."
        ),
        observations=_markdown_observations(180.0, 2.8, 130.0, 1.6, 70.0, 68.0),
    ),
]


INVENTORY_MARKDOWN_NOISY_CASES = [
    PricingInventoryMarkdownCase(
        key="noisy_markdown_01",
        p_max_early=60.0,
        p_max_late=55.0,
        inventory=86.0,
        salvage_value=4.0,
        scenario_note=(
            "Launch-week and clearance-week rows come from different regional tests; "
            "use the pattern rather than one unusually high or low row."
        ),
        observations=_noisy_markdown_observations(
            172.0,
            3.25,
            151.0,
            2.0,
            60.0,
            55.0,
            (4.0, -5.0, 6.5, -3.5, 2.0, -4.5, 3.0),
            (-3.0, 5.5, -4.0, 3.0, -5.0, 4.0, -2.5),
        ),
    ),
    PricingInventoryMarkdownCase(
        key="noisy_markdown_02",
        p_max_early=58.0,
        p_max_late=60.0,
        inventory=72.0,
        salvage_value=5.0,
        scenario_note=(
            "The follow-up channel is valuable, but a few launch rows overstate sell-through "
            "because of local promotion noise."
        ),
        observations=_noisy_markdown_observations(
            132.0,
            2.45,
            202.0,
            3.05,
            58.0,
            60.0,
            (5.0, -4.0, 4.0, -6.0, 3.0, -5.5, 2.5),
            (-4.5, 3.0, -3.5, 5.0, -2.0, 4.5, -3.0),
        ),
    ),
    PricingInventoryMarkdownCase(
        key="noisy_markdown_03",
        p_max_early=65.0,
        p_max_late=62.0,
        inventory=121.0,
        salvage_value=6.0,
        scenario_note=(
            "Broad launch demand and smaller late demand are both noisy; the decision still "
            "needs to preserve stock for the late high-margin window."
        ),
        observations=_noisy_markdown_observations(
            262.0,
            4.45,
            212.0,
            3.05,
            65.0,
            62.0,
            (7.0, -6.0, 4.5, -5.0, 6.0, -4.0, 3.5),
            (-5.0, 4.0, -6.0, 5.5, -3.0, 4.5, -2.5),
        ),
    ),
    PricingInventoryMarkdownCase(
        key="noisy_markdown_04",
        p_max_early=70.0,
        p_max_late=68.0,
        inventory=96.0,
        salvage_value=3.0,
        scenario_note=(
            "Clearance data are lumpy, and the launch channel can drain inventory unless "
            "the launch price is set above the single-period optimum."
        ),
        observations=_noisy_markdown_observations(
            182.0,
            2.85,
            132.0,
            1.62,
            70.0,
            68.0,
            (6.0, -3.5, 5.0, -5.5, 4.0, -4.5, 2.0),
            (-4.0, 5.0, -3.0, 4.5, -5.5, 3.5, -2.0),
        ),
    ),
]


INVENTORY_REPLENISHMENT_NOISY_CASES = [
    PricingInventoryReplenishmentCase(
        key="noisy_replenishment_01",
        p_max_early=60.0,
        p_max_late=55.0,
        starting_inventory=52.0,
        max_replenishment_units=45.0,
        storage_capacity=90.0,
        replenishment_unit_cost=18.0,
        replenishment_setup_cost=120.0,
        salvage_value=4.0,
        scenario_note=(
            "Launch rows are lumpy, and the later channel can absorb extra units if the "
            "mid-campaign buy is worth its unit and setup cost."
        ),
        observations=_noisy_markdown_observations(
            172.0,
            3.25,
            151.0,
            2.0,
            60.0,
            55.0,
            (4.0, -5.0, 6.5, -3.5, 2.0, -4.5, 3.0),
            (-3.0, 5.5, -4.0, 3.0, -5.0, 4.0, -2.5),
        ),
    ),
    PricingInventoryReplenishmentCase(
        key="noisy_replenishment_02",
        p_max_early=58.0,
        p_max_late=60.0,
        starting_inventory=46.0,
        max_replenishment_units=60.0,
        storage_capacity=95.0,
        replenishment_unit_cost=20.0,
        replenishment_setup_cost=140.0,
        salvage_value=5.0,
        scenario_note=(
            "The follow-up channel is price-tolerant, but launch sell-through and restock "
            "cost jointly determine whether buying more units is worthwhile."
        ),
        observations=_noisy_markdown_observations(
            132.0,
            2.45,
            202.0,
            3.05,
            58.0,
            60.0,
            (5.0, -4.0, 4.0, -6.0, 3.0, -5.5, 2.5),
            (-4.5, 3.0, -3.5, 5.0, -2.0, 4.5, -3.0),
        ),
    ),
    PricingInventoryReplenishmentCase(
        key="noisy_replenishment_03",
        p_max_early=65.0,
        p_max_late=62.0,
        starting_inventory=78.0,
        max_replenishment_units=55.0,
        storage_capacity=124.0,
        replenishment_unit_cost=23.0,
        replenishment_setup_cost=165.0,
        salvage_value=6.0,
        scenario_note=(
            "Broad launch demand can stock out the batch, while the late channel is still "
            "valuable enough that a partial replenishment may dominate simply preserving units."
        ),
        observations=_noisy_markdown_observations(
            262.0,
            4.45,
            212.0,
            3.05,
            65.0,
            62.0,
            (7.0, -6.0, 4.5, -5.0, 6.0, -4.0, 3.5),
            (-5.0, 4.0, -6.0, 5.5, -3.0, 4.5, -2.5),
        ),
    ),
    PricingInventoryReplenishmentCase(
        key="noisy_replenishment_04",
        p_max_early=70.0,
        p_max_late=68.0,
        starting_inventory=58.0,
        max_replenishment_units=62.0,
        storage_capacity=108.0,
        replenishment_unit_cost=24.0,
        replenishment_setup_cost=150.0,
        salvage_value=3.0,
        scenario_note=(
            "The launch channel can drain inventory quickly; the clearance channel is smaller "
            "but has enough margin that a restock can be better than a high launch price alone."
        ),
        observations=_noisy_markdown_observations(
            182.0,
            2.85,
            132.0,
            1.62,
            70.0,
            68.0,
            (6.0, -3.5, 5.0, -5.5, 4.0, -4.5, 2.0),
            (-4.0, 5.0, -3.0, 4.5, -5.5, 3.5, -2.0),
        ),
    ),
]


MULTI_PRODUCT_MARKDOWN_NOISY_CASES = [
    PricingMultiProductMarkdownCase(
        key="noisy_multi_markdown_01",
        p_max_a=50.0,
        p_max_b=48.0,
        inventory_a=60.0,
        inventory_b=58.0,
        salvage_value_a=4.0,
        salvage_value_b=4.0,
        scenario_note=(
            "Two substitute products launch together, and the later clearance channel is "
            "more price-tolerant if enough units survive the launch."
        ),
        observations=_noisy_multi_product_markdown_observations(
            122.0,
            4.5,
            3.2,
            118.0,
            4.3,
            3.0,
            150.0,
            2.6,
            1.8,
            143.0,
            2.5,
            1.7,
            50.0,
            48.0,
            (5.0, -4.0, 6.0, -5.0, 4.0, -3.0, 2.0),
            (-3.0, 5.0, -4.0, 6.0, -5.0, 4.0, -2.0),
            (-4.0, 5.0, -3.0, 4.0, -5.0, 3.0, -2.0),
            (4.0, -3.0, 5.0, -4.0, 3.0, -5.0, 2.0),
        ),
    ),
    PricingMultiProductMarkdownCase(
        key="noisy_multi_markdown_02",
        p_max_a=65.0,
        p_max_b=60.0,
        inventory_a=95.0,
        inventory_b=120.0,
        salvage_value_a=5.0,
        salvage_value_b=5.0,
        scenario_note=(
            "The substitute pair shares traffic asymmetrically. Launch rows are noisy, and "
            "draining either product early weakens the paired clearance plan."
        ),
        observations=_noisy_multi_product_markdown_observations(
            138.0,
            4.1,
            3.7,
            135.0,
            4.0,
            3.4,
            178.0,
            2.9,
            2.0,
            166.0,
            2.7,
            1.8,
            65.0,
            60.0,
            (6.0, -5.0, 7.0, -6.0, 5.0, -4.0, 3.0),
            (-4.0, 6.0, -5.0, 5.0, -6.0, 4.0, -3.0),
            (-5.0, 4.0, -4.0, 6.0, -3.0, 5.0, -2.5),
            (5.0, -4.5, 4.0, -5.0, 6.0, -3.0, 2.5),
        ),
    ),
    PricingMultiProductMarkdownCase(
        key="noisy_multi_markdown_03",
        p_max_a=55.0,
        p_max_b=55.0,
        inventory_a=92.0,
        inventory_b=88.0,
        salvage_value_a=6.0,
        salvage_value_b=6.0,
        scenario_note=(
            "Complement products move together in both windows. Clearance demand is durable, "
            "so launch pricing must account for paired late stock rather than each product alone."
        ),
        observations=_noisy_multi_product_markdown_observations(
            340.0,
            5.1,
            -3.1,
            318.0,
            4.9,
            -2.9,
            286.0,
            3.0,
            -1.8,
            272.0,
            2.8,
            -1.7,
            55.0,
            55.0,
            (8.0, -7.0, 6.0, -5.0, 7.0, -6.0, 4.0),
            (-6.0, 7.0, -8.0, 6.0, -5.0, 7.0, -4.0),
            (5.0, -4.0, 6.0, -5.0, 4.0, -6.0, 3.0),
            (-5.0, 6.0, -4.0, 5.0, -6.0, 4.0, -3.0),
        ),
    ),
    PricingMultiProductMarkdownCase(
        key="noisy_multi_markdown_04",
        p_max_a=70.0,
        p_max_b=68.0,
        inventory_a=150.0,
        inventory_b=145.0,
        salvage_value_a=3.0,
        salvage_value_b=3.0,
        scenario_note=(
            "A high-demand complement bundle has lumpy regional launch and clearance rows. "
            "The clearance channel is smaller but more price-tolerant when stock remains."
        ),
        observations=_noisy_multi_product_markdown_observations(
            510.0,
            5.1,
            -4.0,
            486.0,
            5.2,
            -3.7,
            420.0,
            3.2,
            -2.1,
            398.0,
            3.1,
            -2.0,
            70.0,
            68.0,
            (9.0, -8.0, 7.0, -9.0, 6.0, -7.0, 5.0),
            (-8.0, 9.0, -7.0, 8.0, -9.0, 6.0, -5.0),
            (7.0, -6.0, 5.0, -7.0, 6.0, -5.0, 4.0),
            (-6.0, 7.0, -5.0, 6.0, -7.0, 5.0, -4.0),
        ),
    ),
]


HIDDEN_INTERVENTION_CASES = [
    PricingInterventionCase(
        key="intervention_case_01",
        p_max=60.0,
        scenario_note=(
            "Several test rows included a non-price traffic boost. The next campaign is a "
            "normal paid campaign with no boost, and the adjusted rows are noisy regional tests."
        ),
        observations=_intervention_observations(
            170.0,
            3.2,
            60.0,
            (0.0, 8.0, 15.0, 28.0, 45.0, 65.0),
            (1.00, 1.08, 1.18, 1.32, 1.48, 1.70),
            (3.0, -5.0, 4.0, -2.0, 5.0, -4.0),
        ),
    ),
    PricingInterventionCase(
        key="intervention_case_02",
        p_max=58.0,
        scenario_note=(
            "Higher-price rows had extra placement from a partner newsletter. Remove that "
            "increment before setting the normal-list price from noisy test rows."
        ),
        observations=_intervention_observations(
            130.0,
            2.4,
            58.0,
            (4.0, 7.0, 12.0, 24.0, 38.0, 58.0),
            (1.03, 1.06, 1.15, 1.28, 1.45, 1.68),
            (-4.0, 6.0, -5.0, 4.0, -3.0, 5.0),
        ),
    ),
    PricingInterventionCase(
        key="intervention_case_03",
        p_max=65.0,
        scenario_note=(
            "The campaign mixed price tests with row-specific merchandising lifts; the next "
            "rollout does not include those merchandising lifts, and the base rows are noisy."
        ),
        observations=_intervention_observations(
            260.0,
            4.4,
            65.0,
            (0.0, 12.0, 28.0, 50.0, 78.0, 110.0),
            (1.00, 1.10, 1.22, 1.38, 1.55, 1.82),
            (8.0, -7.0, 5.0, -6.0, 7.0, -5.0),
        ),
    ),
    PricingInterventionCase(
        key="intervention_case_04",
        p_max=70.0,
        scenario_note=(
            "Late rows were boosted by retargeting and affiliate placement. Choose the "
            "normal-campaign price after removing the listed incremental units from noisy rows."
        ),
        observations=_intervention_observations(
            180.0,
            2.8,
            70.0,
            (5.0, 10.0, 20.0, 42.0, 65.0, 95.0),
            (1.04, 1.10, 1.20, 1.36, 1.58, 1.90),
            (-6.0, 5.0, -4.0, 6.0, -5.0, 4.0),
        ),
    ),
]


DEFAULT_LAW_CASES = [
    PricingLawCase(
        "intercept_up_unconstrained",
        base_alpha=180.0,
        base_beta=6.0,
        base_p_max=40.0,
        new_alpha=216.0,
        new_beta=6.0,
        new_p_max=40.0,
        relation="new_ge_base",
        law_family="intercept_up",
    ),
    PricingLawCase(
        "intercept_down_unconstrained",
        base_alpha=240.0,
        base_beta=5.0,
        base_p_max=60.0,
        new_alpha=192.0,
        new_beta=5.0,
        new_p_max=60.0,
        relation="new_ge_base",
        law_family="intercept_down",
    ),
    PricingLawCase(
        "slope_up_unconstrained",
        base_alpha=220.0,
        base_beta=4.0,
        base_p_max=70.0,
        new_alpha=220.0,
        new_beta=5.5,
        new_p_max=70.0,
        relation="new_ge_base",
        law_family="slope_up",
    ),
    PricingLawCase(
        "slope_down_unconstrained",
        base_alpha=180.0,
        base_beta=6.0,
        base_p_max=50.0,
        new_alpha=180.0,
        new_beta=4.5,
        new_p_max=50.0,
        relation="new_ge_base",
        law_family="slope_down",
    ),
    PricingLawCase(
        "cap_raise_binding",
        base_alpha=260.0,
        base_beta=4.0,
        base_p_max=26.0,
        new_alpha=260.0,
        new_beta=4.0,
        new_p_max=34.0,
        relation="new_ge_base",
        law_family="cap_raise",
    ),
    PricingLawCase(
        "cap_cut_binding",
        base_alpha=260.0,
        base_beta=4.0,
        base_p_max=34.0,
        new_alpha=260.0,
        new_beta=4.0,
        new_p_max=26.0,
        relation="new_ge_base",
        law_family="cap_cut",
    ),
    PricingLawCase(
        "intercept_up_cap_binding_equal",
        base_alpha=260.0,
        base_beta=4.0,
        base_p_max=24.0,
        new_alpha=300.0,
        new_beta=4.0,
        new_p_max=24.0,
        relation="new_gt_base",
        law_family="cap_binding_equal",
    ),
    PricingLawCase(
        "demand_mix_price_down",
        base_alpha=240.0,
        base_beta=4.0,
        base_p_max=80.0,
        new_alpha=252.0,
        new_beta=5.6,
        new_p_max=80.0,
        relation="new_ge_base",
        law_family="mixed_shift",
    ),
    PricingLawCase(
        "demand_mix_price_up",
        base_alpha=220.0,
        base_beta=6.0,
        base_p_max=70.0,
        new_alpha=250.0,
        new_beta=5.0,
        new_p_max=70.0,
        relation="new_ge_base",
        law_family="mixed_shift",
    ),
    PricingLawCase(
        "small_intercept_up_case",
        base_alpha=150.0,
        base_beta=5.0,
        base_p_max=50.0,
        new_alpha=160.0,
        new_beta=5.0,
        new_p_max=50.0,
        relation="new_gt_base",
        law_family="intercept_up",
    ),
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
    PricingCounterfactualSet(
        key="noisy_snack_downshift",
        base=PricingEvidenceCase(
            key="noisy_snack_downshift_base",
            p_max=35.0,
            scenario_note="Base evidence: sales are noisy but suggest a moderate weekday demand curve.",
            observations=(
                (12.0, 153.0),
                (16.0, 132.0),
                (20.0, 106.0),
                (24.0, 92.0),
                (28.0, 67.0),
                (32.0, 48.0),
            ),
        ),
        perturbed=PricingEvidenceCase(
            key="noisy_snack_downshift_perturbed",
            p_max=35.0,
            scenario_note="Perturbed evidence: the same SKU faces noisier demand after a substitute launch.",
            observations=(
                (10.0, 124.0),
                (14.0, 96.0),
                (18.0, 62.0),
                (22.0, 40.0),
                (26.0, 13.0),
                (30.0, 0.0),
            ),
        ),
    ),
    PricingCounterfactualSet(
        key="noisy_enterprise_upswing",
        base=PricingEvidenceCase(
            key="noisy_enterprise_upswing_base",
            p_max=60.0,
            scenario_note="Base evidence: premium demand is noisy and only moderately price tolerant.",
            observations=(
                (18.0, 122.0),
                (22.0, 105.0),
                (26.0, 84.0),
                (30.0, 70.0),
                (34.0, 50.0),
                (38.0, 34.0),
            ),
        ),
        perturbed=PricingEvidenceCase(
            key="noisy_enterprise_upswing_perturbed",
            p_max=60.0,
            scenario_note="Perturbed evidence: enterprise buyers arrive, with noisy but less price-sensitive demand.",
            observations=(
                (18.0, 190.0),
                (24.0, 166.0),
                (30.0, 141.0),
                (36.0, 121.0),
                (42.0, 91.0),
                (48.0, 77.0),
            ),
        ),
    ),
]

EVIDENCE_LAW_CASES = [
    PricingEvidenceLawCase(
        "evidence_case_01",
        case_set=COUNTERFACTUAL_SETS[0],
        relation="new_lt_base",
        law_family="evidence_downshift",
    ),
    PricingEvidenceLawCase(
        "evidence_case_02",
        case_set=COUNTERFACTUAL_SETS[0],
        relation="new_ge_base",
        law_family="evidence_downshift",
    ),
    PricingEvidenceLawCase(
        "evidence_case_03",
        case_set=COUNTERFACTUAL_SETS[1],
        relation="new_gt_base",
        law_family="evidence_upswing",
    ),
    PricingEvidenceLawCase(
        "evidence_case_04",
        case_set=COUNTERFACTUAL_SETS[1],
        relation="new_le_base",
        law_family="evidence_upswing",
    ),
    PricingEvidenceLawCase(
        "evidence_case_05",
        case_set=COUNTERFACTUAL_SETS[2],
        relation="new_lt_base",
        law_family="noisy_downshift",
    ),
    PricingEvidenceLawCase(
        "evidence_case_06",
        case_set=COUNTERFACTUAL_SETS[2],
        relation="new_gt_base",
        law_family="noisy_downshift",
    ),
    PricingEvidenceLawCase(
        "evidence_case_07",
        case_set=COUNTERFACTUAL_SETS[3],
        relation="new_gt_base",
        law_family="noisy_upswing",
    ),
    PricingEvidenceLawCase(
        "evidence_case_08",
        case_set=COUNTERFACTUAL_SETS[3],
        relation="new_le_base",
        law_family="noisy_upswing",
    ),
]

def _build_holdout_evidence_law_cases() -> list[PricingEvidenceLawCase]:
    specs = [
        ("intercept", 168.0, 4.8, 60.0, 204.0, 4.8, 60.0),
        ("intercept", 220.0, 5.0, 60.0, 180.0, 5.0, 60.0),
        ("slope", 220.0, 4.0, 70.0, 220.0, 5.5, 70.0),
        ("slope", 200.0, 6.0, 60.0, 200.0, 4.8, 60.0),
        ("cap", 260.0, 4.0, 28.0, 260.0, 4.0, 36.0),
        ("cap", 260.0, 4.0, 36.0, 260.0, 4.0, 28.0),
        ("mixed", 210.0, 5.8, 60.0, 240.0, 5.2, 60.0),
        ("mixed", 260.0, 5.0, 70.0, 255.0, 7.0, 70.0),
        ("intervention", 220.0, 4.0, 25.0, 300.0, 5.0, 24.0),
        ("intervention", 260.0, 6.0, 30.0, 210.0, 4.0, 30.0),
        ("intervention", 230.0, 4.0, 20.0, 210.0, 4.0, 26.0),
        ("intervention", 210.0, 5.0, 26.0, 240.0, 5.0, 18.0),
    ]
    cases: list[PricingEvidenceLawCase] = []
    for idx, (family, base_alpha, base_beta, base_cap, new_alpha, new_beta, new_cap) in enumerate(
        specs,
        start=1,
    ):
        case_set = PricingCounterfactualSet(
            key=f"holdout_set_{idx:02d}",
            base=_generated_evidence_case(
                f"holdout_set_{idx:02d}_baseline",
                alpha=base_alpha,
                beta=base_beta,
                p_max=base_cap,
            ),
            perturbed=_generated_evidence_case(
                f"holdout_set_{idx:02d}_updated",
                alpha=new_alpha,
                beta=new_beta,
                p_max=new_cap,
            ),
        )
        base_price = evidence_oracle_price(case_set.base)
        new_price = evidence_oracle_price(case_set.perturbed)
        valid_relation, invalid_relation = _paired_relations(base_price, new_price)
        cases.append(
            PricingEvidenceLawCase(
                key=f"holdout_case_{2 * idx - 1:02d}",
                case_set=case_set,
                relation=valid_relation,
                law_family=f"holdout_{family}",
            )
        )
        cases.append(
            PricingEvidenceLawCase(
                key=f"holdout_case_{2 * idx:02d}",
                case_set=case_set,
                relation=invalid_relation,
                law_family=f"holdout_{family}",
            )
        )
    return cases


def _generated_evidence_case(key: str, alpha: float, beta: float, p_max: float) -> PricingEvidenceCase:
    prices = [0.22 * p_max, 0.34 * p_max, 0.46 * p_max, 0.58 * p_max, 0.70 * p_max, 0.82 * p_max]
    return PricingEvidenceCase(
        key=key,
        p_max=p_max,
        scenario_note="Evidence batch from the same product line; use only the rows and price cap.",
        observations=tuple(
            (round(price, 2), round(max(0.0, alpha - beta * price), 2))
            for price in prices
        ),
    )


def _paired_relations(base_price: float, new_price: float) -> tuple[str, str]:
    if new_price > base_price + 1e-9:
        return "new_gt_base", "new_le_base"
    if new_price < base_price - 1e-9:
        return "new_lt_base", "new_ge_base"
    return "new_ge_base", "new_gt_base"



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


def intervention_posterior(
    case: PricingInterventionCase,
    *,
    intervention_blind: bool = False,
) -> tuple[float, float]:
    rows = [
        (
            price,
            observed_units
            if intervention_blind
            else (observed_units - intervention_units) / exposure_multiplier,
        )
        for price, observed_units, intervention_units, exposure_multiplier in case.observations
    ]
    return _ols_fit(rows)


def intervention_oracle_price(case: PricingInterventionCase) -> float:
    alpha_hat, beta_hat = intervention_posterior(case)
    return clamp(alpha_hat / (2.0 * beta_hat), 0.0, case.p_max)


def intervention_blind_price(case: PricingInterventionCase) -> float:
    alpha_hat, beta_hat = intervention_posterior(case, intervention_blind=True)
    return clamp(alpha_hat / (2.0 * beta_hat), 0.0, case.p_max)


def intervention_revenue(case: PricingInterventionCase, price: float) -> float:
    alpha_hat, beta_hat = intervention_posterior(case)
    return price * max(0.0, alpha_hat - beta_hat * price)


def cross_posterior(case: PricingCrossCase) -> tuple[float, float, float]:
    return _cross_fit(list(case.observations))


def cross_oracle_price(case: PricingCrossCase) -> float:
    alpha_hat, own_beta_hat, related_beta_hat = cross_posterior(case)
    effective_alpha = alpha_hat + related_beta_hat * case.planned_related_price
    return clamp(effective_alpha / (2.0 * own_beta_hat), 0.0, case.p_max)


def cross_own_only_price(case: PricingCrossCase) -> float:
    rows = [(own_price, quantity) for own_price, _, quantity in case.observations]
    alpha_hat, beta_hat = _ols_fit(rows)
    return clamp(alpha_hat / (2.0 * beta_hat), 0.0, case.p_max)


def cross_revenue(case: PricingCrossCase, price: float) -> float:
    alpha_hat, own_beta_hat, related_beta_hat = cross_posterior(case)
    quantity = max(0.0, alpha_hat - own_beta_hat * price + related_beta_hat * case.planned_related_price)
    return price * quantity


def multi_product_posterior(case: PricingMultiProductCase) -> tuple[float, float, float, float, float, float]:
    product_a = _cross_fit([(price_a, price_b, quantity_a) for price_a, price_b, quantity_a, _ in case.observations])
    product_b = _cross_fit([(price_b, price_a, quantity_b) for price_a, price_b, _, quantity_b in case.observations])
    alpha_a, own_beta_a, cross_ab = product_a
    alpha_b, own_beta_b, cross_ba = product_b
    return alpha_a, own_beta_a, cross_ab, alpha_b, own_beta_b, cross_ba


def multi_product_revenue(case: PricingMultiProductCase, price_a: float, price_b: float) -> float:
    alpha_a, own_beta_a, cross_ab, alpha_b, own_beta_b, cross_ba = multi_product_posterior(case)
    quantity_a = max(0.0, alpha_a - own_beta_a * price_a + cross_ab * price_b)
    quantity_b = max(0.0, alpha_b - own_beta_b * price_b + cross_ba * price_a)
    return price_a * quantity_a + price_b * quantity_b


def multi_product_oracle_prices(case: PricingMultiProductCase) -> tuple[float, float]:
    alpha_a, own_beta_a, cross_ab, alpha_b, own_beta_b, cross_ba = multi_product_posterior(case)
    return _best_multi_product_prices(
        alpha_a=alpha_a,
        own_beta_a=own_beta_a,
        cross_ab=cross_ab,
        alpha_b=alpha_b,
        own_beta_b=own_beta_b,
        cross_ba=cross_ba,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
    )


def multi_product_independent_prices(case: PricingMultiProductCase) -> tuple[float, float]:
    alpha_a, beta_a = _ols_fit([(price_a, quantity_a) for price_a, _, quantity_a, _ in case.observations])
    alpha_b, beta_b = _ols_fit([(price_b, quantity_b) for _, price_b, _, quantity_b in case.observations])
    return (
        clamp(alpha_a / (2.0 * beta_a), 0.0, case.p_max_a),
        clamp(alpha_b / (2.0 * beta_b), 0.0, case.p_max_b),
    )


def _capacity_base_case(case: PricingMultiProductCapacityCase) -> PricingMultiProductCase:
    return PricingMultiProductCase(
        key=case.key,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
        observations=case.observations,
        scenario_note=case.scenario_note,
    )


def multi_product_capacity_revenue(
    case: PricingMultiProductCapacityCase,
    price_a: float,
    price_b: float,
) -> float:
    alpha_a, own_beta_a, cross_ab, alpha_b, own_beta_b, cross_ba = multi_product_posterior(
        _capacity_base_case(case)
    )
    demand_a = max(0.0, alpha_a - own_beta_a * price_a + cross_ab * price_b)
    demand_b = max(0.0, alpha_b - own_beta_b * price_b + cross_ba * price_a)
    sold_a = min(demand_a, case.inventory_a)
    sold_b = min(demand_b, case.inventory_b)
    return price_a * sold_a + price_b * sold_b


def multi_product_capacity_oracle_prices(case: PricingMultiProductCapacityCase) -> tuple[float, float]:
    alpha_a, own_beta_a, cross_ab, alpha_b, own_beta_b, cross_ba = multi_product_posterior(
        _capacity_base_case(case)
    )
    return _best_multi_product_capacity_prices(
        alpha_a=alpha_a,
        own_beta_a=own_beta_a,
        cross_ab=cross_ab,
        alpha_b=alpha_b,
        own_beta_b=own_beta_b,
        cross_ba=cross_ba,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
        inventory_a=case.inventory_a,
        inventory_b=case.inventory_b,
    )


def multi_product_capacity_blind_prices(case: PricingMultiProductCapacityCase) -> tuple[float, float]:
    return multi_product_oracle_prices(_capacity_base_case(case))


def multi_product_capacity_independent_prices(case: PricingMultiProductCapacityCase) -> tuple[float, float]:
    return multi_product_independent_prices(_capacity_base_case(case))


def inventory_markdown_posterior(case: PricingInventoryMarkdownCase) -> tuple[float, float, float, float]:
    early_alpha, early_beta = _ols_fit([(price, units) for price, units, _, _ in case.observations])
    late_alpha, late_beta = _ols_fit([(price, units) for _, _, price, units in case.observations])
    return early_alpha, early_beta, late_alpha, late_beta


def inventory_markdown_revenue(
    case: PricingInventoryMarkdownCase,
    price_early: float,
    price_late: float,
) -> float:
    early_alpha, early_beta, late_alpha, late_beta = inventory_markdown_posterior(case)
    early_demand = max(0.0, early_alpha - early_beta * price_early)
    early_sold = min(early_demand, case.inventory)
    remaining = max(0.0, case.inventory - early_sold)
    late_demand = max(0.0, late_alpha - late_beta * price_late)
    late_sold = min(late_demand, remaining)
    unsold = max(0.0, remaining - late_sold)
    return price_early * early_sold + price_late * late_sold + case.salvage_value * unsold


def inventory_markdown_oracle_prices(case: PricingInventoryMarkdownCase) -> tuple[float, float]:
    early_alpha, early_beta, late_alpha, late_beta = inventory_markdown_posterior(case)
    return _best_inventory_markdown_prices(
        early_alpha=early_alpha,
        early_beta=early_beta,
        late_alpha=late_alpha,
        late_beta=late_beta,
        p_max_early=case.p_max_early,
        p_max_late=case.p_max_late,
        inventory=case.inventory,
        salvage_value=case.salvage_value,
    )


def inventory_markdown_myopic_prices(case: PricingInventoryMarkdownCase) -> tuple[float, float]:
    early_alpha, early_beta, late_alpha, late_beta = inventory_markdown_posterior(case)
    return (
        clamp(early_alpha / (2.0 * early_beta), 0.0, case.p_max_early),
        clamp(late_alpha / (2.0 * late_beta), 0.0, case.p_max_late),
    )


def inventory_replenishment_posterior(case: PricingInventoryReplenishmentCase) -> tuple[float, float, float, float]:
    early_alpha, early_beta = _ols_fit([(price, units) for price, units, _, _ in case.observations])
    late_alpha, late_beta = _ols_fit([(price, units) for _, _, price, units in case.observations])
    return early_alpha, early_beta, late_alpha, late_beta


def inventory_replenishment_revenue(
    case: PricingInventoryReplenishmentCase,
    price_early: float,
    replenishment_units: float,
    price_late: float,
) -> float:
    early_alpha, early_beta, late_alpha, late_beta = inventory_replenishment_posterior(case)
    early_demand = max(0.0, early_alpha - early_beta * price_early)
    early_sold = min(early_demand, case.starting_inventory)
    remaining = max(0.0, case.starting_inventory - early_sold)
    ordered = clamp(replenishment_units, 0.0, case.max_replenishment_units)
    received = min(ordered, max(0.0, case.storage_capacity - remaining))
    replenishment_cost = (
        case.replenishment_setup_cost + case.replenishment_unit_cost * received
        if received > 1e-9
        else 0.0
    )
    late_inventory = remaining + received
    late_demand = max(0.0, late_alpha - late_beta * price_late)
    late_sold = min(late_demand, late_inventory)
    unsold = max(0.0, late_inventory - late_sold)
    return price_early * early_sold + price_late * late_sold + case.salvage_value * unsold - replenishment_cost


def inventory_replenishment_oracle_plan(case: PricingInventoryReplenishmentCase) -> tuple[float, float, float]:
    early_alpha, early_beta, late_alpha, late_beta = inventory_replenishment_posterior(case)
    return _best_inventory_replenishment_plan(
        early_alpha=early_alpha,
        early_beta=early_beta,
        late_alpha=late_alpha,
        late_beta=late_beta,
        p_max_early=case.p_max_early,
        p_max_late=case.p_max_late,
        starting_inventory=case.starting_inventory,
        max_replenishment_units=case.max_replenishment_units,
        storage_capacity=case.storage_capacity,
        replenishment_unit_cost=case.replenishment_unit_cost,
        replenishment_setup_cost=case.replenishment_setup_cost,
        salvage_value=case.salvage_value,
    )


def inventory_replenishment_no_restock_plan(case: PricingInventoryReplenishmentCase) -> tuple[float, float, float]:
    early_alpha, early_beta, late_alpha, late_beta = inventory_replenishment_posterior(case)
    price_early, price_late = _best_inventory_markdown_prices(
        early_alpha=early_alpha,
        early_beta=early_beta,
        late_alpha=late_alpha,
        late_beta=late_beta,
        p_max_early=case.p_max_early,
        p_max_late=case.p_max_late,
        inventory=case.starting_inventory,
        salvage_value=case.salvage_value,
    )
    return price_early, 0.0, price_late


def inventory_replenishment_myopic_plan(case: PricingInventoryReplenishmentCase) -> tuple[float, float, float]:
    early_alpha, early_beta, late_alpha, late_beta = inventory_replenishment_posterior(case)
    price_early = clamp(early_alpha / (2.0 * early_beta), 0.0, case.p_max_early)
    price_late = clamp(late_alpha / (2.0 * late_beta), 0.0, case.p_max_late)
    early_demand = max(0.0, early_alpha - early_beta * price_early)
    remaining = max(0.0, case.starting_inventory - min(early_demand, case.starting_inventory))
    late_margin = price_late - case.replenishment_unit_cost
    order_units = (
        min(case.max_replenishment_units, max(0.0, case.storage_capacity - remaining))
        if late_margin > case.salvage_value
        else 0.0
    )
    return price_early, order_units, price_late


def inventory_replenishment_capacity_fill_plan(case: PricingInventoryReplenishmentCase) -> tuple[float, float, float]:
    price_early, _, price_late = inventory_replenishment_myopic_plan(case)
    early_alpha, early_beta, _, _ = inventory_replenishment_posterior(case)
    early_demand = max(0.0, early_alpha - early_beta * price_early)
    remaining = max(0.0, case.starting_inventory - min(early_demand, case.starting_inventory))
    order_units = min(case.max_replenishment_units, max(0.0, case.storage_capacity - remaining))
    return price_early, order_units, price_late


def multi_product_markdown_posterior(
    case: PricingMultiProductMarkdownCase,
) -> tuple[float, float, float, float, float, float, float, float, float, float, float, float]:
    early_a = _cross_fit(
        [
            (early_price_a, early_price_b, early_units_a)
            for (
                early_price_a,
                early_price_b,
                early_units_a,
                _,
                _,
                _,
                _,
                _,
            ) in case.observations
        ]
    )
    early_b = _cross_fit(
        [
            (early_price_b, early_price_a, early_units_b)
            for (
                early_price_a,
                early_price_b,
                _,
                early_units_b,
                _,
                _,
                _,
                _,
            ) in case.observations
        ]
    )
    late_a = _cross_fit(
        [
            (late_price_a, late_price_b, late_units_a)
            for (
                _,
                _,
                _,
                _,
                late_price_a,
                late_price_b,
                late_units_a,
                _,
            ) in case.observations
        ]
    )
    late_b = _cross_fit(
        [
            (late_price_b, late_price_a, late_units_b)
            for (
                _,
                _,
                _,
                _,
                late_price_a,
                late_price_b,
                _,
                late_units_b,
            ) in case.observations
        ]
    )
    return (*early_a, *early_b, *late_a, *late_b)


def multi_product_markdown_revenue(
    case: PricingMultiProductMarkdownCase,
    price_a_early: float,
    price_b_early: float,
    price_a_late: float,
    price_b_late: float,
) -> float:
    (
        early_alpha_a,
        early_own_a,
        early_cross_ab,
        early_alpha_b,
        early_own_b,
        early_cross_ba,
        late_alpha_a,
        late_own_a,
        late_cross_ab,
        late_alpha_b,
        late_own_b,
        late_cross_ba,
    ) = multi_product_markdown_posterior(case)
    early_demand_a = max(0.0, early_alpha_a - early_own_a * price_a_early + early_cross_ab * price_b_early)
    early_demand_b = max(0.0, early_alpha_b - early_own_b * price_b_early + early_cross_ba * price_a_early)
    early_sold_a = min(early_demand_a, case.inventory_a)
    early_sold_b = min(early_demand_b, case.inventory_b)
    remaining_a = max(0.0, case.inventory_a - early_sold_a)
    remaining_b = max(0.0, case.inventory_b - early_sold_b)
    late_demand_a = max(0.0, late_alpha_a - late_own_a * price_a_late + late_cross_ab * price_b_late)
    late_demand_b = max(0.0, late_alpha_b - late_own_b * price_b_late + late_cross_ba * price_a_late)
    late_sold_a = min(late_demand_a, remaining_a)
    late_sold_b = min(late_demand_b, remaining_b)
    unsold_a = max(0.0, remaining_a - late_sold_a)
    unsold_b = max(0.0, remaining_b - late_sold_b)
    return (
        price_a_early * early_sold_a
        + price_b_early * early_sold_b
        + price_a_late * late_sold_a
        + price_b_late * late_sold_b
        + case.salvage_value_a * unsold_a
        + case.salvage_value_b * unsold_b
    )


def multi_product_markdown_oracle_prices(
    case: PricingMultiProductMarkdownCase,
) -> tuple[float, float, float, float]:
    return _best_multi_product_markdown_prices(
        *multi_product_markdown_posterior(case),
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
        inventory_a=case.inventory_a,
        inventory_b=case.inventory_b,
        salvage_value_a=case.salvage_value_a,
        salvage_value_b=case.salvage_value_b,
    )


def multi_product_markdown_myopic_prices(
    case: PricingMultiProductMarkdownCase,
) -> tuple[float, float, float, float]:
    (
        early_alpha_a,
        early_own_a,
        early_cross_ab,
        early_alpha_b,
        early_own_b,
        early_cross_ba,
        late_alpha_a,
        late_own_a,
        late_cross_ab,
        late_alpha_b,
        late_own_b,
        late_cross_ba,
    ) = multi_product_markdown_posterior(case)
    early_a, early_b = _best_multi_product_capacity_prices(
        alpha_a=early_alpha_a,
        own_beta_a=early_own_a,
        cross_ab=early_cross_ab,
        alpha_b=early_alpha_b,
        own_beta_b=early_own_b,
        cross_ba=early_cross_ba,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
        inventory_a=case.inventory_a,
        inventory_b=case.inventory_b,
    )
    late_a, late_b = _best_multi_product_capacity_prices(
        alpha_a=late_alpha_a,
        own_beta_a=late_own_a,
        cross_ab=late_cross_ab,
        alpha_b=late_alpha_b,
        own_beta_b=late_own_b,
        cross_ba=late_cross_ba,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
        inventory_a=case.inventory_a,
        inventory_b=case.inventory_b,
    )
    return (
        clamp(early_a, case.salvage_value_a, case.p_max_a),
        clamp(early_b, case.salvage_value_b, case.p_max_b),
        clamp(late_a, case.salvage_value_a, case.p_max_a),
        clamp(late_b, case.salvage_value_b, case.p_max_b),
    )


def multi_product_markdown_capacity_blind_prices(
    case: PricingMultiProductMarkdownCase,
) -> tuple[float, float, float, float]:
    (
        early_alpha_a,
        early_own_a,
        early_cross_ab,
        early_alpha_b,
        early_own_b,
        early_cross_ba,
        late_alpha_a,
        late_own_a,
        late_cross_ab,
        late_alpha_b,
        late_own_b,
        late_cross_ba,
    ) = multi_product_markdown_posterior(case)
    early_a, early_b = _best_multi_product_prices(
        alpha_a=early_alpha_a,
        own_beta_a=early_own_a,
        cross_ab=early_cross_ab,
        alpha_b=early_alpha_b,
        own_beta_b=early_own_b,
        cross_ba=early_cross_ba,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
    )
    late_a, late_b = _best_multi_product_prices(
        alpha_a=late_alpha_a,
        own_beta_a=late_own_a,
        cross_ab=late_cross_ab,
        alpha_b=late_alpha_b,
        own_beta_b=late_own_b,
        cross_ba=late_cross_ba,
        p_max_a=case.p_max_a,
        p_max_b=case.p_max_b,
    )
    return (
        clamp(early_a, case.salvage_value_a, case.p_max_a),
        clamp(early_b, case.salvage_value_b, case.p_max_b),
        clamp(late_a, case.salvage_value_a, case.p_max_a),
        clamp(late_b, case.salvage_value_b, case.p_max_b),
    )


def multi_product_markdown_independent_prices(
    case: PricingMultiProductMarkdownCase,
) -> tuple[float, float, float, float]:
    early_a_alpha, early_a_beta = _ols_fit(
        [(row[0], row[2]) for row in case.observations]
    )
    early_b_alpha, early_b_beta = _ols_fit(
        [(row[1], row[3]) for row in case.observations]
    )
    late_a_alpha, late_a_beta = _ols_fit(
        [(row[4], row[6]) for row in case.observations]
    )
    late_b_alpha, late_b_beta = _ols_fit(
        [(row[5], row[7]) for row in case.observations]
    )
    return (
        clamp(early_a_alpha / (2.0 * early_a_beta), case.salvage_value_a, case.p_max_a),
        clamp(early_b_alpha / (2.0 * early_b_beta), case.salvage_value_b, case.p_max_b),
        clamp(late_a_alpha / (2.0 * late_a_beta), case.salvage_value_a, case.p_max_a),
        clamp(late_b_alpha / (2.0 * late_b_beta), case.salvage_value_b, case.p_max_b),
    )


def _best_multi_product_prices(
    *,
    alpha_a: float,
    own_beta_a: float,
    cross_ab: float,
    alpha_b: float,
    own_beta_b: float,
    cross_ba: float,
    p_max_a: float,
    p_max_b: float,
) -> tuple[float, float]:
    cross_sum = cross_ab + cross_ba
    candidates: list[tuple[float, float]] = []
    determinant = 4.0 * own_beta_a * own_beta_b - cross_sum * cross_sum
    if abs(determinant) > 1e-12:
        candidates.append(
            (
                (alpha_a * 2.0 * own_beta_b + cross_sum * alpha_b) / determinant,
                (2.0 * own_beta_a * alpha_b + cross_sum * alpha_a) / determinant,
            )
        )
    for price_a in (0.0, p_max_a):
        candidates.append((price_a, (alpha_b + cross_sum * price_a) / (2.0 * own_beta_b)))
    for price_b in (0.0, p_max_b):
        candidates.append(((alpha_a + cross_sum * price_b) / (2.0 * own_beta_a), price_b))
    candidates.extend((price_a, price_b) for price_a in (0.0, p_max_a) for price_b in (0.0, p_max_b))

    def objective(pair: tuple[float, float]) -> float:
        price_a = clamp(pair[0], 0.0, p_max_a)
        price_b = clamp(pair[1], 0.0, p_max_b)
        quantity_a = max(0.0, alpha_a - own_beta_a * price_a + cross_ab * price_b)
        quantity_b = max(0.0, alpha_b - own_beta_b * price_b + cross_ba * price_a)
        return price_a * quantity_a + price_b * quantity_b

    best = max(candidates, key=objective)
    return clamp(best[0], 0.0, p_max_a), clamp(best[1], 0.0, p_max_b)


def _best_multi_product_capacity_prices(
    *,
    alpha_a: float,
    own_beta_a: float,
    cross_ab: float,
    alpha_b: float,
    own_beta_b: float,
    cross_ba: float,
    p_max_a: float,
    p_max_b: float,
    inventory_a: float,
    inventory_b: float,
) -> tuple[float, float]:
    step = 0.25
    grid_a = _price_grid(p_max_a, step)
    grid_b = _price_grid(p_max_b, step)

    def objective(price_a: float, price_b: float) -> float:
        demand_a = max(0.0, alpha_a - own_beta_a * price_a + cross_ab * price_b)
        demand_b = max(0.0, alpha_b - own_beta_b * price_b + cross_ba * price_a)
        sold_a = min(demand_a, inventory_a)
        sold_b = min(demand_b, inventory_b)
        return price_a * sold_a + price_b * sold_b

    best_pair = (0.0, 0.0)
    best_value = -1.0
    for price_a in grid_a:
        for price_b in grid_b:
            value = objective(price_a, price_b)
            if value > best_value:
                best_value = value
                best_pair = (price_a, price_b)
    return best_pair


def _best_inventory_markdown_prices(
    *,
    early_alpha: float,
    early_beta: float,
    late_alpha: float,
    late_beta: float,
    p_max_early: float,
    p_max_late: float,
    inventory: float,
    salvage_value: float,
) -> tuple[float, float]:
    step = 0.25
    best_pair = (0.0, 0.0)
    best_value = -1.0
    for price_early in _price_grid(p_max_early, step):
        for price_late in _price_grid(p_max_late, step):
            early_demand = max(0.0, early_alpha - early_beta * price_early)
            early_sold = min(early_demand, inventory)
            remaining = max(0.0, inventory - early_sold)
            late_demand = max(0.0, late_alpha - late_beta * price_late)
            late_sold = min(late_demand, remaining)
            unsold = max(0.0, remaining - late_sold)
            value = price_early * early_sold + price_late * late_sold + salvage_value * unsold
            if value > best_value:
                best_value = value
                best_pair = (price_early, price_late)
    return best_pair


def _best_inventory_replenishment_plan(
    *,
    early_alpha: float,
    early_beta: float,
    late_alpha: float,
    late_beta: float,
    p_max_early: float,
    p_max_late: float,
    starting_inventory: float,
    max_replenishment_units: float,
    storage_capacity: float,
    replenishment_unit_cost: float,
    replenishment_setup_cost: float,
    salvage_value: float,
) -> tuple[float, float, float]:
    early_myopic = clamp(early_alpha / (2.0 * early_beta), 0.0, p_max_early)
    late_myopic = clamp(late_alpha / (2.0 * late_beta), 0.0, p_max_late)
    no_restock_early, no_restock_late = _best_inventory_markdown_prices(
        early_alpha=early_alpha,
        early_beta=early_beta,
        late_alpha=late_alpha,
        late_beta=late_beta,
        p_max_early=p_max_early,
        p_max_late=p_max_late,
        inventory=starting_inventory,
        salvage_value=salvage_value,
    )
    early_grid = _markdown_price_candidates(
        p_max_early,
        0.0,
        (early_myopic, no_restock_early),
    )
    late_grid = _markdown_price_candidates(
        p_max_late,
        0.0,
        (late_myopic, no_restock_late, replenishment_unit_cost + 5.0),
    )
    quantity_grid = _replenishment_quantity_candidates(
        max_replenishment_units=max_replenishment_units,
        storage_capacity=storage_capacity,
        starting_inventory=starting_inventory,
    )

    def objective(price_early: float, replenishment_units: float, price_late: float) -> float:
        early_demand = max(0.0, early_alpha - early_beta * price_early)
        early_sold = min(early_demand, starting_inventory)
        remaining = max(0.0, starting_inventory - early_sold)
        received = min(replenishment_units, max(0.0, storage_capacity - remaining))
        replenishment_cost = (
            replenishment_setup_cost + replenishment_unit_cost * received
            if received > 1e-9
            else 0.0
        )
        late_inventory = remaining + received
        late_demand = max(0.0, late_alpha - late_beta * price_late)
        late_sold = min(late_demand, late_inventory)
        unsold = max(0.0, late_inventory - late_sold)
        return price_early * early_sold + price_late * late_sold + salvage_value * unsold - replenishment_cost

    best_plan = (0.0, 0.0, 0.0)
    best_value = -1e18
    for price_early in early_grid:
        for replenishment_units in quantity_grid:
            for price_late in late_grid:
                value = objective(price_early, replenishment_units, price_late)
                if value > best_value:
                    best_value = value
                    best_plan = (price_early, replenishment_units, price_late)
    return best_plan


def _replenishment_quantity_candidates(
    *,
    max_replenishment_units: float,
    storage_capacity: float,
    starting_inventory: float,
) -> list[float]:
    values = {0.0, round(max_replenishment_units, 2)}
    useful_capacity = clamp(storage_capacity - starting_inventory, 0.0, max_replenishment_units)
    values.add(round(useful_capacity, 2))
    step = 5.0
    count = int(max_replenishment_units / step)
    values.update(round(idx * step, 2) for idx in range(count + 1))
    if count * step < max_replenishment_units:
        values.add(round(max_replenishment_units, 2))
    return sorted(values)


def _best_multi_product_markdown_prices(
    early_alpha_a: float,
    early_own_a: float,
    early_cross_ab: float,
    early_alpha_b: float,
    early_own_b: float,
    early_cross_ba: float,
    late_alpha_a: float,
    late_own_a: float,
    late_cross_ab: float,
    late_alpha_b: float,
    late_own_b: float,
    late_cross_ba: float,
    *,
    p_max_a: float,
    p_max_b: float,
    inventory_a: float,
    inventory_b: float,
    salvage_value_a: float,
    salvage_value_b: float,
) -> tuple[float, float, float, float]:
    early_blind_a, early_blind_b = _best_multi_product_prices(
        alpha_a=early_alpha_a,
        own_beta_a=early_own_a,
        cross_ab=early_cross_ab,
        alpha_b=early_alpha_b,
        own_beta_b=early_own_b,
        cross_ba=early_cross_ba,
        p_max_a=p_max_a,
        p_max_b=p_max_b,
    )
    late_blind_a, late_blind_b = _best_multi_product_prices(
        alpha_a=late_alpha_a,
        own_beta_a=late_own_a,
        cross_ab=late_cross_ab,
        alpha_b=late_alpha_b,
        own_beta_b=late_own_b,
        cross_ba=late_cross_ba,
        p_max_a=p_max_a,
        p_max_b=p_max_b,
    )
    early_cap_a, early_cap_b = _best_multi_product_capacity_prices(
        alpha_a=early_alpha_a,
        own_beta_a=early_own_a,
        cross_ab=early_cross_ab,
        alpha_b=early_alpha_b,
        own_beta_b=early_own_b,
        cross_ba=early_cross_ba,
        p_max_a=p_max_a,
        p_max_b=p_max_b,
        inventory_a=inventory_a,
        inventory_b=inventory_b,
    )
    late_cap_a, late_cap_b = _best_multi_product_capacity_prices(
        alpha_a=late_alpha_a,
        own_beta_a=late_own_a,
        cross_ab=late_cross_ab,
        alpha_b=late_alpha_b,
        own_beta_b=late_own_b,
        cross_ba=late_cross_ba,
        p_max_a=p_max_a,
        p_max_b=p_max_b,
        inventory_a=inventory_a,
        inventory_b=inventory_b,
    )
    early_a_grid = _markdown_price_candidates(
        p_max_a,
        salvage_value_a,
        (early_blind_a, early_cap_a, late_cap_a),
    )
    early_b_grid = _markdown_price_candidates(
        p_max_b,
        salvage_value_b,
        (early_blind_b, early_cap_b, late_cap_b),
    )
    late_a_grid = _markdown_price_candidates(
        p_max_a,
        salvage_value_a,
        (late_blind_a, late_cap_a, early_cap_a),
    )
    late_b_grid = _markdown_price_candidates(
        p_max_b,
        salvage_value_b,
        (late_blind_b, late_cap_b, early_cap_b),
    )

    def objective(
        price_a_early: float,
        price_b_early: float,
        price_a_late: float,
        price_b_late: float,
    ) -> float:
        early_demand_a = max(0.0, early_alpha_a - early_own_a * price_a_early + early_cross_ab * price_b_early)
        early_demand_b = max(0.0, early_alpha_b - early_own_b * price_b_early + early_cross_ba * price_a_early)
        early_sold_a = min(early_demand_a, inventory_a)
        early_sold_b = min(early_demand_b, inventory_b)
        remaining_a = max(0.0, inventory_a - early_sold_a)
        remaining_b = max(0.0, inventory_b - early_sold_b)
        late_demand_a = max(0.0, late_alpha_a - late_own_a * price_a_late + late_cross_ab * price_b_late)
        late_demand_b = max(0.0, late_alpha_b - late_own_b * price_b_late + late_cross_ba * price_a_late)
        late_sold_a = min(late_demand_a, remaining_a)
        late_sold_b = min(late_demand_b, remaining_b)
        unsold_a = max(0.0, remaining_a - late_sold_a)
        unsold_b = max(0.0, remaining_b - late_sold_b)
        return (
            price_a_early * early_sold_a
            + price_b_early * early_sold_b
            + price_a_late * late_sold_a
            + price_b_late * late_sold_b
            + salvage_value_a * unsold_a
            + salvage_value_b * unsold_b
        )

    best_plan = (0.0, 0.0, 0.0, 0.0)
    best_value = -1.0
    for price_a_early in early_a_grid:
        for price_b_early in early_b_grid:
            for price_a_late in late_a_grid:
                for price_b_late in late_b_grid:
                    value = objective(price_a_early, price_b_early, price_a_late, price_b_late)
                    if value > best_value:
                        best_value = value
                        best_plan = (price_a_early, price_b_early, price_a_late, price_b_late)
    return best_plan


def _markdown_price_candidates(p_max: float, price_floor: float, anchors: tuple[float, ...]) -> list[float]:
    values = {round(price_floor, 2), round(p_max, 2)}
    values.update(value for value in _price_grid(p_max, 5.0) if value >= price_floor)
    for anchor in anchors:
        for offset in (-7.5, -5.0, -2.5, -1.0, -0.5, 0.0, 0.5, 1.0, 2.5, 5.0, 7.5):
            values.add(round(clamp(anchor + offset, price_floor, p_max), 2))
    return sorted(values)


def _price_grid(p_max: float, step: float) -> list[float]:
    count = int(p_max / step)
    values = [round(idx * step, 2) for idx in range(count + 1)]
    if values[-1] < p_max:
        values.append(round(p_max, 2))
    return values


def param_oracle_price(alpha: float, beta: float, p_max: float) -> float:
    return clamp(alpha / (2.0 * beta), 0.0, p_max)


def pricing_law_label(case: PricingLawCase, eps: float = 1e-9) -> str:
    base = param_oracle_price(case.base_alpha, case.base_beta, case.base_p_max)
    new = param_oracle_price(case.new_alpha, case.new_beta, case.new_p_max)
    return _relation_label(base, new, case.relation, eps=eps)


def pricing_evidence_law_label(case: PricingEvidenceLawCase, eps: float = 1e-9) -> str:
    base = evidence_oracle_price(case.case_set.base)
    new = evidence_oracle_price(case.case_set.perturbed)
    return _relation_label(base, new, case.relation, eps=eps)


def _relation_label(base: float, new: float, relation: str, eps: float = 1e-9) -> str:
    if relation == "new_ge_base":
        return "valid" if new + eps >= base else "invalid"
    if relation == "new_gt_base":
        return "valid" if new > base + eps else "invalid"
    if relation == "new_le_base":
        return "valid" if new <= base + eps else "invalid"
    if relation == "new_lt_base":
        return "valid" if new < base - eps else "invalid"
    raise ValueError(f"Unsupported relation: {relation}")


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


def _cross_fit(rows: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    matrix = []
    vector = []
    for own_price, related_price, quantity in rows:
        matrix.append((1.0, own_price, related_price))
        vector.append(quantity)
    normal = [
        [sum(row[i] * row[j] for row in matrix) for j in range(3)]
        for i in range(3)
    ]
    rhs = [sum(row[i] * quantity for row, quantity in zip(matrix, vector)) for i in range(3)]
    intercept, own_slope, related_slope = _solve_3x3(normal, rhs)
    return intercept, max(0.001, -own_slope), related_slope


def _solve_3x3(matrix: list[list[float]], vector: list[float]) -> tuple[float, float, float]:
    for col in range(3):
        pivot = max(range(col, 3), key=lambda row: abs(matrix[row][col]))
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        vector[col], vector[pivot] = vector[pivot], vector[col]
        divisor = matrix[col][col]
        if abs(divisor) < 1e-12:
            raise ValueError("Singular pricing cross-elasticity design matrix")
        for idx in range(col, 3):
            matrix[col][idx] /= divisor
        vector[col] /= divisor
        for row in range(3):
            if row == col:
                continue
            factor = matrix[row][col]
            for idx in range(col, 3):
                matrix[row][idx] -= factor * matrix[col][idx]
            vector[row] -= factor * vector[col]
    return vector[0], vector[1], vector[2]


HOLDOUT_EVIDENCE_LAW_CASES = _build_holdout_evidence_law_cases()


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


def run_pricing_cross_elasticity_game(
    agent: Agent,
    cases: list[PricingCrossCase] | None = None,
) -> dict:
    cases = cases or CROSS_ELASTICITY_CASES
    rows = []
    for case in cases:
        oracle = cross_oracle_price(case)
        own_only = cross_own_only_price(case)
        oracle_rev = cross_revenue(case, oracle)
        response = agent.complete(PRICING_CROSS_SYSTEM, _cross_elasticity_prompt(case))
        parsed = parse_float("FINAL_PRICE", response)
        chosen = clamp(parsed, 0.0, case.p_max) if parsed is not None else None
        revenue = cross_revenue(case, chosen) if chosen is not None else None
        rows.append(
            {
                "case": case.key,
                "oracle_price": oracle,
                "own_only_price": own_only,
                "chosen_price": chosen,
                "absolute_price_error": abs(chosen - oracle) if chosen is not None else None,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "cross_blind_miss": (
                    chosen is not None
                    and abs(chosen - own_only) < 1.0
                    and abs(oracle - own_only) > 2.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["absolute_price_error"] for row in rows if row["absolute_price_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed = [row for row in rows if row["chosen_price"] is not None]
    cross_blind_misses = sum(row["cross_blind_miss"] for row in rows)
    return {
        "task": "pricing_cross_elasticity",
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_absolute_price_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed) / len(rows) if rows else 0.0,
        "cross_blind_miss_rate": cross_blind_misses / len(rows) if rows else 0.0,
        "trials": rows,
    }


def run_pricing_multi_product_game(
    agent: Agent,
    cases: list[PricingMultiProductCase] | None = None,
) -> dict:
    return _run_pricing_multi_product_game(
        agent,
        cases=cases,
        system=PRICING_MULTI_SYSTEM,
        prompt_builder=_multi_product_prompt,
        task_name="pricing_multi_product",
    )


def run_pricing_multi_product_natural_game(
    agent: Agent,
    cases: list[PricingMultiProductCase] | None = None,
) -> dict:
    return _run_pricing_multi_product_game(
        agent,
        cases=cases,
        system=PRICING_MULTI_NATURAL_SYSTEM,
        prompt_builder=_multi_product_natural_prompt,
        task_name="pricing_multi_product_natural",
    )


def run_pricing_multi_product_capacity_game(
    agent: Agent,
    cases: list[PricingMultiProductCapacityCase] | None = None,
) -> dict:
    return _run_pricing_multi_product_capacity_game(
        agent,
        cases=cases or MULTI_PRODUCT_CAPACITY_CASES,
        system=PRICING_MULTI_CAPACITY_SYSTEM,
        prompt_builder=_multi_product_capacity_prompt,
        task_name="pricing_multi_product_capacity",
    )


def run_pricing_multi_product_capacity_noisy_game(
    agent: Agent,
    cases: list[PricingMultiProductCapacityCase] | None = None,
) -> dict:
    return _run_pricing_multi_product_capacity_game(
        agent,
        cases=cases or MULTI_PRODUCT_CAPACITY_NOISY_CASES,
        system=PRICING_MULTI_CAPACITY_NOISY_SYSTEM,
        prompt_builder=_multi_product_capacity_noisy_prompt,
        task_name="pricing_multi_product_capacity_noisy",
    )


def _run_pricing_multi_product_capacity_game(
    agent: Agent,
    *,
    cases: list[PricingMultiProductCapacityCase],
    system: str,
    prompt_builder,
    task_name: str,
) -> dict:
    rows = []
    for case in cases:
        oracle_a, oracle_b = multi_product_capacity_oracle_prices(case)
        capacity_blind_a, capacity_blind_b = multi_product_capacity_blind_prices(case)
        independent_a, independent_b = multi_product_capacity_independent_prices(case)
        oracle_rev = multi_product_capacity_revenue(case, oracle_a, oracle_b)
        response = agent.complete(system, prompt_builder(case))
        parsed_a = parse_float("FINAL_PRICE_A", response)
        parsed_b = parse_float("FINAL_PRICE_B", response)
        chosen_a = clamp(parsed_a, 0.0, case.p_max_a) if parsed_a is not None else None
        chosen_b = clamp(parsed_b, 0.0, case.p_max_b) if parsed_b is not None else None
        revenue = (
            multi_product_capacity_revenue(case, chosen_a, chosen_b)
            if chosen_a is not None and chosen_b is not None
            else None
        )
        price_l1 = (
            abs(chosen_a - oracle_a) + abs(chosen_b - oracle_b)
            if chosen_a is not None and chosen_b is not None
            else None
        )
        capacity_blind_l1 = abs(capacity_blind_a - oracle_a) + abs(capacity_blind_b - oracle_b)
        independent_l1 = abs(independent_a - oracle_a) + abs(independent_b - oracle_b)
        rows.append(
            {
                "case": case.key,
                "oracle_price_a": oracle_a,
                "oracle_price_b": oracle_b,
                "capacity_blind_price_a": capacity_blind_a,
                "capacity_blind_price_b": capacity_blind_b,
                "independent_price_a": independent_a,
                "independent_price_b": independent_b,
                "chosen_price_a": chosen_a,
                "chosen_price_b": chosen_b,
                "price_l1_error": price_l1,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "capacity_blind_miss": (
                    chosen_a is not None
                    and chosen_b is not None
                    and abs(chosen_a - capacity_blind_a) + abs(chosen_b - capacity_blind_b) < 1.5
                    and capacity_blind_l1 > 5.0
                ),
                "independent_miss": (
                    chosen_a is not None
                    and chosen_b is not None
                    and abs(chosen_a - independent_a) + abs(chosen_b - independent_b) < 1.5
                    and independent_l1 > 5.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["price_l1_error"] for row in rows if row["price_l1_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed = [row for row in rows if row["chosen_price_a"] is not None and row["chosen_price_b"] is not None]
    capacity_blind_misses = sum(row["capacity_blind_miss"] for row in rows)
    independent_misses = sum(row["independent_miss"] for row in rows)
    return {
        "task": task_name,
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_price_l1_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed) / len(rows) if rows else 0.0,
        "capacity_blind_miss_rate": capacity_blind_misses / len(rows) if rows else 0.0,
        "independent_miss_rate": independent_misses / len(rows) if rows else 0.0,
        "trials": rows,
    }


def run_pricing_inventory_markdown_game(
    agent: Agent,
    cases: list[PricingInventoryMarkdownCase] | None = None,
) -> dict:
    return _run_pricing_inventory_markdown_game(
        agent,
        cases=cases,
        system=PRICING_INVENTORY_MARKDOWN_SYSTEM,
        prompt_builder=_inventory_markdown_prompt,
        task_name="pricing_inventory_markdown",
        default_cases=INVENTORY_MARKDOWN_CASES,
    )


def run_pricing_inventory_markdown_noisy_game(
    agent: Agent,
    cases: list[PricingInventoryMarkdownCase] | None = None,
) -> dict:
    return _run_pricing_inventory_markdown_game(
        agent,
        cases=cases,
        system=PRICING_INVENTORY_MARKDOWN_NOISY_SYSTEM,
        prompt_builder=_inventory_markdown_noisy_prompt,
        task_name="pricing_inventory_markdown_noisy",
        default_cases=INVENTORY_MARKDOWN_NOISY_CASES,
    )


def run_pricing_inventory_replenishment_noisy_game(
    agent: Agent,
    cases: list[PricingInventoryReplenishmentCase] | None = None,
) -> dict:
    cases = cases or INVENTORY_REPLENISHMENT_NOISY_CASES
    rows = []
    for case in cases:
        oracle = inventory_replenishment_oracle_plan(case)
        no_restock = inventory_replenishment_no_restock_plan(case)
        myopic = inventory_replenishment_myopic_plan(case)
        capacity_fill = inventory_replenishment_capacity_fill_plan(case)
        oracle_rev = inventory_replenishment_revenue(case, *oracle)
        response = agent.complete(
            PRICING_INVENTORY_REPLENISHMENT_NOISY_SYSTEM,
            _inventory_replenishment_noisy_prompt(case),
        )
        parsed = (
            parse_float("FINAL_PRICE_EARLY", response),
            parse_float("FINAL_REPLENISHMENT_UNITS", response),
            parse_float("FINAL_PRICE_LATE", response),
        )
        chosen = (
            clamp(parsed[0], 0.0, case.p_max_early) if parsed[0] is not None else None,
            clamp(parsed[1], 0.0, case.max_replenishment_units) if parsed[1] is not None else None,
            clamp(parsed[2], 0.0, case.p_max_late) if parsed[2] is not None else None,
        )
        parsed_all = all(value is not None for value in chosen)
        revenue = inventory_replenishment_revenue(case, *chosen) if parsed_all else None
        decision_l1 = sum(abs(chosen[idx] - oracle[idx]) for idx in range(3)) if parsed_all else None
        no_restock_l1 = sum(abs(no_restock[idx] - oracle[idx]) for idx in range(3))
        myopic_l1 = sum(abs(myopic[idx] - oracle[idx]) for idx in range(3))
        capacity_fill_l1 = sum(abs(capacity_fill[idx] - oracle[idx]) for idx in range(3))
        rows.append(
            {
                "case": case.key,
                "oracle_price_early": oracle[0],
                "oracle_replenishment_units": oracle[1],
                "oracle_price_late": oracle[2],
                "no_restock_price_early": no_restock[0],
                "no_restock_replenishment_units": no_restock[1],
                "no_restock_price_late": no_restock[2],
                "myopic_price_early": myopic[0],
                "myopic_replenishment_units": myopic[1],
                "myopic_price_late": myopic[2],
                "capacity_fill_price_early": capacity_fill[0],
                "capacity_fill_replenishment_units": capacity_fill[1],
                "capacity_fill_price_late": capacity_fill[2],
                "chosen_price_early": chosen[0],
                "chosen_replenishment_units": chosen[1],
                "chosen_price_late": chosen[2],
                "decision_l1_error": decision_l1,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "no_restock_miss": (
                    parsed_all
                    and sum(abs(chosen[idx] - no_restock[idx]) for idx in range(3)) < 2.0
                    and no_restock_l1 > 5.0
                ),
                "myopic_miss": (
                    parsed_all
                    and sum(abs(chosen[idx] - myopic[idx]) for idx in range(3)) < 2.0
                    and myopic_l1 > 5.0
                ),
                "capacity_fill_miss": (
                    parsed_all
                    and sum(abs(chosen[idx] - capacity_fill[idx]) for idx in range(3)) < 2.0
                    and capacity_fill_l1 > 5.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["decision_l1_error"] for row in rows if row["decision_l1_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed_rows = [
        row
        for row in rows
        if row["chosen_price_early"] is not None
        and row["chosen_replenishment_units"] is not None
        and row["chosen_price_late"] is not None
    ]
    return {
        "task": "pricing_inventory_replenishment_noisy",
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_decision_l1_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed_rows) / len(rows) if rows else 0.0,
        "no_restock_miss_rate": sum(row["no_restock_miss"] for row in rows) / len(rows) if rows else 0.0,
        "myopic_miss_rate": sum(row["myopic_miss"] for row in rows) / len(rows) if rows else 0.0,
        "capacity_fill_miss_rate": sum(row["capacity_fill_miss"] for row in rows) / len(rows) if rows else 0.0,
        "trials": rows,
    }


def run_pricing_multi_product_markdown_noisy_game(
    agent: Agent,
    cases: list[PricingMultiProductMarkdownCase] | None = None,
) -> dict:
    cases = cases or MULTI_PRODUCT_MARKDOWN_NOISY_CASES
    rows = []
    for case in cases:
        oracle = multi_product_markdown_oracle_prices(case)
        myopic = multi_product_markdown_myopic_prices(case)
        capacity_blind = multi_product_markdown_capacity_blind_prices(case)
        independent = multi_product_markdown_independent_prices(case)
        oracle_rev = multi_product_markdown_revenue(case, *oracle)
        response = agent.complete(PRICING_MULTI_PRODUCT_MARKDOWN_NOISY_SYSTEM, _multi_product_markdown_noisy_prompt(case))
        parsed = (
            parse_float("FINAL_PRICE_A_EARLY", response),
            parse_float("FINAL_PRICE_B_EARLY", response),
            parse_float("FINAL_PRICE_A_LATE", response),
            parse_float("FINAL_PRICE_B_LATE", response),
        )
        chosen = (
            clamp(parsed[0], case.salvage_value_a, case.p_max_a) if parsed[0] is not None else None,
            clamp(parsed[1], case.salvage_value_b, case.p_max_b) if parsed[1] is not None else None,
            clamp(parsed[2], case.salvage_value_a, case.p_max_a) if parsed[2] is not None else None,
            clamp(parsed[3], case.salvage_value_b, case.p_max_b) if parsed[3] is not None else None,
        )
        parsed_all = all(value is not None for value in chosen)
        revenue = multi_product_markdown_revenue(case, *chosen) if parsed_all else None
        price_l1 = sum(abs(chosen[idx] - oracle[idx]) for idx in range(4)) if parsed_all else None
        myopic_l1 = sum(abs(myopic[idx] - oracle[idx]) for idx in range(4))
        capacity_blind_l1 = sum(abs(capacity_blind[idx] - oracle[idx]) for idx in range(4))
        independent_l1 = sum(abs(independent[idx] - oracle[idx]) for idx in range(4))
        rows.append(
            {
                "case": case.key,
                "oracle_price_a_early": oracle[0],
                "oracle_price_b_early": oracle[1],
                "oracle_price_a_late": oracle[2],
                "oracle_price_b_late": oracle[3],
                "myopic_price_a_early": myopic[0],
                "myopic_price_b_early": myopic[1],
                "myopic_price_a_late": myopic[2],
                "myopic_price_b_late": myopic[3],
                "capacity_blind_price_a_early": capacity_blind[0],
                "capacity_blind_price_b_early": capacity_blind[1],
                "capacity_blind_price_a_late": capacity_blind[2],
                "capacity_blind_price_b_late": capacity_blind[3],
                "independent_price_a_early": independent[0],
                "independent_price_b_early": independent[1],
                "independent_price_a_late": independent[2],
                "independent_price_b_late": independent[3],
                "chosen_price_a_early": chosen[0],
                "chosen_price_b_early": chosen[1],
                "chosen_price_a_late": chosen[2],
                "chosen_price_b_late": chosen[3],
                "price_l1_error": price_l1,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "myopic_miss": (
                    parsed_all
                    and sum(abs(chosen[idx] - myopic[idx]) for idx in range(4)) < 2.0
                    and myopic_l1 > 5.0
                ),
                "capacity_blind_miss": (
                    parsed_all
                    and sum(abs(chosen[idx] - capacity_blind[idx]) for idx in range(4)) < 2.0
                    and capacity_blind_l1 > 5.0
                ),
                "independent_miss": (
                    parsed_all
                    and sum(abs(chosen[idx] - independent[idx]) for idx in range(4)) < 2.0
                    and independent_l1 > 5.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["price_l1_error"] for row in rows if row["price_l1_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed_rows = [
        row
        for row in rows
        if row["chosen_price_a_early"] is not None
        and row["chosen_price_b_early"] is not None
        and row["chosen_price_a_late"] is not None
        and row["chosen_price_b_late"] is not None
    ]
    return {
        "task": "pricing_multi_product_markdown_noisy",
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_price_l1_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed_rows) / len(rows) if rows else 0.0,
        "myopic_miss_rate": sum(row["myopic_miss"] for row in rows) / len(rows) if rows else 0.0,
        "capacity_blind_miss_rate": sum(row["capacity_blind_miss"] for row in rows) / len(rows) if rows else 0.0,
        "independent_miss_rate": sum(row["independent_miss"] for row in rows) / len(rows) if rows else 0.0,
        "trials": rows,
    }


def run_pricing_hidden_intervention_game(
    agent: Agent,
    cases: list[PricingInterventionCase] | None = None,
) -> dict:
    cases = cases or HIDDEN_INTERVENTION_CASES
    rows = []
    for case in cases:
        oracle = intervention_oracle_price(case)
        blind = intervention_blind_price(case)
        oracle_rev = intervention_revenue(case, oracle)
        response = agent.complete(PRICING_HIDDEN_INTERVENTION_SYSTEM, _hidden_intervention_prompt(case))
        parsed = parse_float("FINAL_PRICE", response)
        chosen = clamp(parsed, 0.0, case.p_max) if parsed is not None else None
        revenue = intervention_revenue(case, chosen) if chosen is not None else None
        blind_error = abs(blind - oracle)
        rows.append(
            {
                "case": case.key,
                "oracle_price": oracle,
                "intervention_blind_price": blind,
                "chosen_price": chosen,
                "absolute_price_error": abs(chosen - oracle) if chosen is not None else None,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "intervention_blind_miss": (
                    chosen is not None
                    and abs(chosen - blind) < 1.5
                    and blind_error > 5.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["absolute_price_error"] for row in rows if row["absolute_price_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed_rows = [row for row in rows if row["chosen_price"] is not None]
    blind_misses = sum(row["intervention_blind_miss"] for row in rows)
    return {
        "task": "pricing_hidden_intervention",
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_absolute_price_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed_rows) / len(rows) if rows else 0.0,
        "intervention_blind_miss_rate": blind_misses / len(rows) if rows else 0.0,
        "trials": rows,
    }


def _run_pricing_inventory_markdown_game(
    agent: Agent,
    *,
    cases: list[PricingInventoryMarkdownCase] | None,
    system: str,
    prompt_builder,
    task_name: str,
    default_cases: list[PricingInventoryMarkdownCase],
) -> dict:
    cases = cases or default_cases
    rows = []
    for case in cases:
        oracle_early, oracle_late = inventory_markdown_oracle_prices(case)
        myopic_early, myopic_late = inventory_markdown_myopic_prices(case)
        oracle_rev = inventory_markdown_revenue(case, oracle_early, oracle_late)
        response = agent.complete(system, prompt_builder(case))
        parsed_early = parse_float("FINAL_PRICE_EARLY", response)
        parsed_late = parse_float("FINAL_PRICE_LATE", response)
        chosen_early = clamp(parsed_early, 0.0, case.p_max_early) if parsed_early is not None else None
        chosen_late = clamp(parsed_late, 0.0, case.p_max_late) if parsed_late is not None else None
        revenue = (
            inventory_markdown_revenue(case, chosen_early, chosen_late)
            if chosen_early is not None and chosen_late is not None
            else None
        )
        price_l1 = (
            abs(chosen_early - oracle_early) + abs(chosen_late - oracle_late)
            if chosen_early is not None and chosen_late is not None
            else None
        )
        myopic_l1 = abs(myopic_early - oracle_early) + abs(myopic_late - oracle_late)
        rows.append(
            {
                "case": case.key,
                "oracle_price_early": oracle_early,
                "oracle_price_late": oracle_late,
                "myopic_price_early": myopic_early,
                "myopic_price_late": myopic_late,
                "chosen_price_early": chosen_early,
                "chosen_price_late": chosen_late,
                "price_l1_error": price_l1,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "myopic_miss": (
                    chosen_early is not None
                    and chosen_late is not None
                    and abs(chosen_early - myopic_early) + abs(chosen_late - myopic_late) < 1.5
                    and myopic_l1 > 5.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["price_l1_error"] for row in rows if row["price_l1_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed = [
        row
        for row in rows
        if row["chosen_price_early"] is not None and row["chosen_price_late"] is not None
    ]
    myopic_misses = sum(row["myopic_miss"] for row in rows)
    return {
        "task": task_name,
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_price_l1_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed) / len(rows) if rows else 0.0,
        "myopic_miss_rate": myopic_misses / len(rows) if rows else 0.0,
        "trials": rows,
    }


def _run_pricing_multi_product_game(
    agent: Agent,
    *,
    cases: list[PricingMultiProductCase] | None,
    system: str,
    prompt_builder,
    task_name: str,
) -> dict:
    cases = cases or MULTI_PRODUCT_CASES
    rows = []
    for case in cases:
        oracle_a, oracle_b = multi_product_oracle_prices(case)
        independent_a, independent_b = multi_product_independent_prices(case)
        oracle_rev = multi_product_revenue(case, oracle_a, oracle_b)
        response = agent.complete(system, prompt_builder(case))
        parsed_a = parse_float("FINAL_PRICE_A", response)
        parsed_b = parse_float("FINAL_PRICE_B", response)
        chosen_a = clamp(parsed_a, 0.0, case.p_max_a) if parsed_a is not None else None
        chosen_b = clamp(parsed_b, 0.0, case.p_max_b) if parsed_b is not None else None
        revenue = (
            multi_product_revenue(case, chosen_a, chosen_b)
            if chosen_a is not None and chosen_b is not None
            else None
        )
        price_l1 = (
            abs(chosen_a - oracle_a) + abs(chosen_b - oracle_b)
            if chosen_a is not None and chosen_b is not None
            else None
        )
        independent_l1 = abs(independent_a - oracle_a) + abs(independent_b - oracle_b)
        rows.append(
            {
                "case": case.key,
                "oracle_price_a": oracle_a,
                "oracle_price_b": oracle_b,
                "independent_price_a": independent_a,
                "independent_price_b": independent_b,
                "chosen_price_a": chosen_a,
                "chosen_price_b": chosen_b,
                "price_l1_error": price_l1,
                "oracle_revenue": oracle_rev,
                "chosen_revenue": revenue,
                "revenue_gap": oracle_rev - revenue if revenue is not None else None,
                "independent_miss": (
                    chosen_a is not None
                    and chosen_b is not None
                    and abs(chosen_a - independent_a) + abs(chosen_b - independent_b) < 1.5
                    and independent_l1 > 5.0
                ),
                "raw_response": response,
            }
        )
    errors = [row["price_l1_error"] for row in rows if row["price_l1_error"] is not None]
    gaps = [row["revenue_gap"] for row in rows if row["revenue_gap"] is not None]
    parsed = [row for row in rows if row["chosen_price_a"] is not None and row["chosen_price_b"] is not None]
    independent_misses = sum(row["independent_miss"] for row in rows)
    return {
        "task": task_name,
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_price_l1_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed) / len(rows) if rows else 0.0,
        "independent_miss_rate": independent_misses / len(rows) if rows else 0.0,
        "trials": rows,
    }


def run_pricing_law_audit_game(agent: Agent, cases: list[PricingLawCase] | None = None) -> dict:
    cases = cases or DEFAULT_LAW_CASES
    rows: list[PricingLawTrial] = []
    for case in cases:
        base_price = param_oracle_price(case.base_alpha, case.base_beta, case.base_p_max)
        new_price = param_oracle_price(case.new_alpha, case.new_beta, case.new_p_max)
        oracle_label = pricing_law_label(case)
        response = agent.complete(PRICING_LAW_SYSTEM, _law_audit_prompt(case))
        parsed = parse_token("FINAL_LABEL", response)
        chosen = parsed.lower() if parsed and parsed.lower() in {"valid", "invalid"} else None
        correct = chosen == oracle_label
        rows.append(
            PricingLawTrial(
                case=case,
                base_price=base_price,
                new_price=new_price,
                oracle_label=oracle_label,
                chosen_label=chosen,
                correct=correct,
                invalid_accept=oracle_label == "invalid" and chosen == "valid",
                valid_reject=oracle_label == "valid" and chosen == "invalid",
                raw_response=response,
            )
        )
    return summarize_pricing_law_trials(agent.name, rows)


def run_pricing_evidence_law_audit_game(
    agent: Agent,
    cases: list[PricingEvidenceLawCase] | None = None,
) -> dict:
    cases = cases or EVIDENCE_LAW_CASES
    return _run_pricing_evidence_law_game(
        agent,
        cases=cases,
        task_name="pricing_evidence_law_audit",
    )


def run_pricing_evidence_law_holdout_game(
    agent: Agent,
    cases: list[PricingEvidenceLawCase] | None = None,
) -> dict:
    cases = cases or HOLDOUT_EVIDENCE_LAW_CASES
    return _run_pricing_evidence_law_game(
        agent,
        cases=cases,
        task_name="pricing_evidence_law_holdout",
    )


def _run_pricing_evidence_law_game(
    agent: Agent,
    cases: list[PricingEvidenceLawCase],
    task_name: str,
) -> dict:
    rows: list[PricingEvidenceLawTrial] = []
    for case in cases:
        base_price = evidence_oracle_price(case.case_set.base)
        new_price = evidence_oracle_price(case.case_set.perturbed)
        oracle_label = pricing_evidence_law_label(case)
        response = agent.complete(PRICING_EVIDENCE_LAW_SYSTEM, _evidence_law_audit_prompt(case))
        parsed = parse_token("FINAL_LABEL", response)
        chosen = parsed.lower() if parsed and parsed.lower() in {"valid", "invalid"} else None
        correct = chosen == oracle_label
        rows.append(
            PricingEvidenceLawTrial(
                case=case,
                base_price=base_price,
                new_price=new_price,
                oracle_label=oracle_label,
                chosen_label=chosen,
                correct=correct,
                invalid_accept=oracle_label == "invalid" and chosen == "valid",
                valid_reject=oracle_label == "valid" and chosen == "invalid",
                raw_response=response,
            )
        )
    return summarize_pricing_evidence_law_trials(agent.name, rows, task_name=task_name)


def summarize_pricing_law_trials(agent_name: str, trials: list[PricingLawTrial]) -> dict:
    parsed = [trial for trial in trials if trial.chosen_label is not None]
    correct = sum(trial.correct for trial in trials)
    invalid_trials = [trial for trial in trials if trial.oracle_label == "invalid"]
    valid_trials = [trial for trial in trials if trial.oracle_label == "valid"]
    invalid_accepts = sum(trial.invalid_accept for trial in invalid_trials)
    valid_rejects = sum(trial.valid_reject for trial in valid_trials)
    by_family: dict[str, dict] = {}
    for family in sorted({trial.case.law_family for trial in trials}):
        subset = [trial for trial in trials if trial.case.law_family == family]
        by_family[family] = {
            "n_trials": len(subset),
            "accuracy": sum(trial.correct for trial in subset) / len(subset) if subset else 0.0,
            "valid_count": sum(trial.oracle_label == "valid" for trial in subset),
            "invalid_count": sum(trial.oracle_label == "invalid" for trial in subset),
        }
    return {
        "task": "pricing_law_audit",
        "agent": agent_name,
        "n_trials": len(trials),
        "accuracy": correct / len(trials) if trials else 0.0,
        "parse_rate": len(parsed) / len(trials) if trials else 0.0,
        "invalid_accept_rate": invalid_accepts / len(invalid_trials) if invalid_trials else 0.0,
        "valid_reject_rate": valid_rejects / len(valid_trials) if valid_trials else 0.0,
        "by_family": by_family,
        "trials": [_pricing_law_trial_json(trial) for trial in trials],
    }


def summarize_pricing_evidence_law_trials(
    agent_name: str,
    trials: list[PricingEvidenceLawTrial],
    task_name: str = "pricing_evidence_law_audit",
) -> dict:
    parsed = [trial for trial in trials if trial.chosen_label is not None]
    correct = sum(trial.correct for trial in trials)
    invalid_trials = [trial for trial in trials if trial.oracle_label == "invalid"]
    valid_trials = [trial for trial in trials if trial.oracle_label == "valid"]
    invalid_accepts = sum(trial.invalid_accept for trial in invalid_trials)
    valid_rejects = sum(trial.valid_reject for trial in valid_trials)
    by_family: dict[str, dict] = {}
    for family in sorted({trial.case.law_family for trial in trials}):
        subset = [trial for trial in trials if trial.case.law_family == family]
        by_family[family] = {
            "n_trials": len(subset),
            "accuracy": sum(trial.correct for trial in subset) / len(subset) if subset else 0.0,
            "valid_count": sum(trial.oracle_label == "valid" for trial in subset),
            "invalid_count": sum(trial.oracle_label == "invalid" for trial in subset),
        }
    return {
        "task": task_name,
        "agent": agent_name,
        "n_trials": len(trials),
        "accuracy": correct / len(trials) if trials else 0.0,
        "parse_rate": len(parsed) / len(trials) if trials else 0.0,
        "invalid_accept_rate": invalid_accepts / len(invalid_trials) if invalid_trials else 0.0,
        "valid_reject_rate": valid_rejects / len(valid_trials) if valid_trials else 0.0,
        "by_family": by_family,
        "trials": [_pricing_evidence_law_trial_json(trial) for trial in trials],
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


def _cross_elasticity_prompt(case: PricingCrossCase) -> str:
    lines = [
        f"case={case.key}",
        f"p_max={case.p_max:.2f}",
        f"planned_related_price={case.planned_related_price:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Historical sales observations:")
    lines.extend(
        f"  own_price={own_price:.2f}, related_price={related_price:.2f}, quantity={quantity:.2f}"
        for own_price, related_price, quantity in case.observations
    )
    lines.append(
        "Fit demand as quantity = alpha - own_beta * own_price + related_beta * related_price, "
        "then choose the focal price that maximizes focal price * quantity under p_max."
    )
    return "\n".join(lines)


def _multi_product_prompt(case: PricingMultiProductCase) -> str:
    lines = [
        f"case={case.key}",
        f"p_max_a={case.p_max_a:.2f}",
        f"p_max_b={case.p_max_b:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Historical sales observations:")
    lines.extend(
        (
            f"  price_a={price_a:.2f}, price_b={price_b:.2f}, "
            f"quantity_a={quantity_a:.2f}, quantity_b={quantity_b:.2f}"
        )
        for price_a, price_b, quantity_a, quantity_b in case.observations
    )
    lines.append(
        "Fit product A demand as quantity_a = alpha_a - own_beta_a * price_a + cross_ab * price_b. "
        "Fit product B demand as quantity_b = alpha_b - own_beta_b * price_b + cross_ba * price_a. "
        "Choose both prices jointly to maximize price_a * quantity_a + price_b * quantity_b under the caps."
    )
    return "\n".join(lines)


def _multi_product_natural_prompt(case: PricingMultiProductCase) -> str:
    lines = [
        f"case={case.key}",
        f"price_ceiling_a={case.p_max_a:.2f}",
        f"price_ceiling_b={case.p_max_b:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Recent joint campaign outcomes:")
    lines.extend(
        (
            f"  campaign_row={idx} product_a_price={price_a:.2f}, "
            f"product_b_price={price_b:.2f}, product_a_units={quantity_a:.2f}, "
            f"product_b_units={quantity_b:.2f}"
        )
        for idx, (price_a, price_b, quantity_a, quantity_b) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Use the joint sales history to set the next campaign prices for both products. "
        "The two products can affect each other's unit sales, so assess the pair together."
    )
    return "\n".join(lines)


def _multi_product_capacity_prompt(case: PricingMultiProductCapacityCase) -> str:
    lines = [
        f"case={case.key}",
        f"price_ceiling_a={case.p_max_a:.2f}",
        f"price_ceiling_b={case.p_max_b:.2f}",
        f"available_units_a={case.inventory_a:.2f}",
        f"available_units_b={case.inventory_b:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Recent joint campaign outcomes:")
    lines.extend(
        (
            f"  campaign_row={idx} product_a_price={price_a:.2f}, "
            f"product_b_price={price_b:.2f}, product_a_units={quantity_a:.2f}, "
            f"product_b_units={quantity_b:.2f}"
        )
        for idx, (price_a, price_b, quantity_a, quantity_b) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Use the joint sales history to set the next campaign prices for both products. "
        "Unit sales can be affected by both prices. Revenue is earned only on units available "
        "for the campaign, so demand above available units is capped by stock."
    )
    return "\n".join(lines)


def _multi_product_capacity_noisy_prompt(case: PricingMultiProductCapacityCase) -> str:
    lines = [
        f"case={case.key}",
        f"price_ceiling_a={case.p_max_a:.2f}",
        f"price_ceiling_b={case.p_max_b:.2f}",
        f"available_units_a={case.inventory_a:.2f}",
        f"available_units_b={case.inventory_b:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Lumpy regional joint-campaign outcomes:")
    lines.extend(
        (
            f"  campaign_row={idx} product_a_price={price_a:.2f}, "
            f"product_b_price={price_b:.2f}, product_a_units={quantity_a:.2f}, "
            f"product_b_units={quantity_b:.2f}"
        )
        for idx, (price_a, price_b, quantity_a, quantity_b) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Use the regional sales pattern rather than one unusually high or low row. "
        "Set both campaign prices jointly because each product can move the other's sales. "
        "Revenue is earned only on units available for the campaign."
    )
    return "\n".join(lines)


def _inventory_markdown_prompt(case: PricingInventoryMarkdownCase) -> str:
    lines = [
        f"case={case.key}",
        f"price_ceiling_early={case.p_max_early:.2f}",
        f"price_ceiling_late={case.p_max_late:.2f}",
        f"starting_inventory={case.inventory:.2f}",
        f"salvage_value={case.salvage_value:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Prior campaign outcome rows:")
    lines.extend(
        (
            f"  row={idx} early_price={early_price:.2f}, early_units={early_units:.2f}, "
            f"late_price={late_price:.2f}, late_units={late_units:.2f}"
        )
        for idx, (early_price, early_units, late_price, late_units) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Set one launch-window price and one later markdown-window price for the same starting inventory. "
        "Units sold early reduce the units available later; unsold units after the late window receive only "
        "the salvage value."
    )
    return "\n".join(lines)


def _inventory_markdown_noisy_prompt(case: PricingInventoryMarkdownCase) -> str:
    lines = [
        f"case={case.key}",
        f"launch_price_ceiling={case.p_max_early:.2f}",
        f"clearance_price_ceiling={case.p_max_late:.2f}",
        f"starting_units={case.inventory:.2f}",
        f"liquidation_value={case.salvage_value:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Regional campaign evidence:")
    lines.extend(
        (
            f"  region_row={idx} launch_price={early_price:.2f}, launch_units={early_units:.2f}, "
            f"clearance_price={late_price:.2f}, clearance_units={late_units:.2f}"
        )
        for idx, (early_price, early_units, late_price, late_units) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Recommend a launch price and later clearance price for the same batch of units. "
        "Launch sales happen first and reduce units available for clearance; leftover units "
        "after clearance recover only the liquidation value."
    )
    return "\n".join(lines)


def _inventory_replenishment_noisy_prompt(case: PricingInventoryReplenishmentCase) -> str:
    lines = [
        f"case={case.key}",
        f"launch_price_ceiling={case.p_max_early:.2f}",
        f"clearance_price_ceiling={case.p_max_late:.2f}",
        f"starting_units={case.starting_inventory:.2f}",
        f"max_replenishment_units={case.max_replenishment_units:.2f}",
        f"storage_capacity={case.storage_capacity:.2f}",
        f"replenishment_unit_cost={case.replenishment_unit_cost:.2f}",
        f"replenishment_setup_cost={case.replenishment_setup_cost:.2f}",
        f"liquidation_value={case.salvage_value:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Regional campaign evidence:")
    lines.extend(
        (
            f"  region_row={idx} launch_price={early_price:.2f}, launch_units={early_units:.2f}, "
            f"clearance_price={late_price:.2f}, clearance_units={late_units:.2f}"
        )
        for idx, (early_price, early_units, late_price, late_units) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Recommend a launch price, the units to buy after the launch window, and a later "
        "clearance price. Launch sales happen before the replenishment decision; received "
        "replenishment cannot exceed the max units or the storage space left after launch. "
        "A positive replenishment pays both the unit cost for received units and the setup cost. "
        "Leftover units after clearance recover only the liquidation value."
    )
    return "\n".join(lines)


def _multi_product_markdown_noisy_prompt(case: PricingMultiProductMarkdownCase) -> str:
    lines = [
        f"case={case.key}",
        f"price_ceiling_a={case.p_max_a:.2f}",
        f"price_ceiling_b={case.p_max_b:.2f}",
        f"available_units_a={case.inventory_a:.2f}",
        f"available_units_b={case.inventory_b:.2f}",
        f"liquidation_value_a={case.salvage_value_a:.2f}",
        f"liquidation_value_b={case.salvage_value_b:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Regional launch and clearance evidence:")
    lines.extend(
        (
            f"  region_row={idx} launch_a_price={early_price_a:.2f}, "
            f"launch_b_price={early_price_b:.2f}, launch_a_units={early_units_a:.2f}, "
            f"launch_b_units={early_units_b:.2f}, clearance_a_price={late_price_a:.2f}, "
            f"clearance_b_price={late_price_b:.2f}, clearance_a_units={late_units_a:.2f}, "
            f"clearance_b_units={late_units_b:.2f}"
        )
        for idx, (
            early_price_a,
            early_price_b,
            early_units_a,
            early_units_b,
            late_price_a,
            late_price_b,
            late_units_a,
            late_units_b,
        ) in enumerate(case.observations, start=1)
    )
    lines.append(
        "Recommend launch prices and later clearance prices for both products. "
        "Launch sales happen first and reduce each product's units available for clearance. "
        "The two products can affect each other's unit sales in either window, and leftover "
        "units after clearance recover only their product-specific liquidation value. "
        "Do not price either product below its liquidation value."
    )
    return "\n".join(lines)


def _hidden_intervention_prompt(case: PricingInterventionCase) -> str:
    lines = [
        f"case={case.key}",
        f"price_ceiling={case.p_max:.2f}",
    ]
    if case.scenario_note:
        lines.append(case.scenario_note)
    lines.append("Observed price-test rows:")
    lines.extend(
        (
            f"  row={idx} price={price:.2f}, observed_units={observed_units:.2f}, "
            f"intervention_units={intervention_units:.2f}, "
            f"exposure_multiplier={exposure_multiplier:.4f}"
        )
        for idx, (price, observed_units, intervention_units, exposure_multiplier) in enumerate(
            case.observations,
            start=1,
        )
    )
    lines.append(
        "Set the next normal-campaign price. The next campaign has no non-price intervention. "
        "For each row, first remove intervention_units from observed_units, then divide by "
        "exposure_multiplier before fitting the normal demand curve; then maximize price "
        "times normal demand under the price ceiling."
    )
    return "\n".join(lines)


def _law_audit_prompt(case: PricingLawCase) -> str:
    relation_text = {
        "new_ge_base": "new optimal price >= base optimal price",
        "new_gt_base": "new optimal price > base optimal price",
        "new_le_base": "new optimal price <= base optimal price",
    }[case.relation]
    lines = [
        f"case={case.key}",
        "Demand is quantity = alpha - beta * price.",
        "Choose the price that maximizes price * quantity, capped by p_max.",
        f"base_alpha={case.base_alpha:.4f}",
        f"base_beta={case.base_beta:.4f}",
        f"base_p_max={case.base_p_max:.4f}",
        f"new_alpha={case.new_alpha:.4f}",
        f"new_beta={case.new_beta:.4f}",
        f"new_p_max={case.new_p_max:.4f}",
        f"relation={case.relation}",
        f"Claim: {relation_text}.",
        "Decide whether the claim is valid or invalid for this generated pricing case.",
    ]
    return "\n".join(lines)


def _evidence_law_audit_prompt(case: PricingEvidenceLawCase) -> str:
    relation_text = {
        "new_ge_base": "updated optimal price >= baseline optimal price",
        "new_gt_base": "updated optimal price > baseline optimal price",
        "new_le_base": "updated optimal price <= baseline optimal price",
        "new_lt_base": "updated optimal price < baseline optimal price",
    }[case.relation]
    base = case.case_set.base
    updated = case.case_set.perturbed
    lines = [
        f"case={case.key}",
        "A seller sets a price to maximize price * quantity under the listed price cap.",
        "Fit a linear demand curve quantity = alpha - beta * price from each evidence block.",
        "Use the baseline evidence for the baseline curve and the updated evidence for the updated curve.",
        "Respect each price cap when comparing the two optimal prices.",
        f"baseline_price_cap={base.p_max:.4f}",
    ]
    if base.scenario_note:
        lines.append(f"baseline_context={base.scenario_note}")
    lines.append("baseline_evidence:")
    lines.extend(f"  price={p:.2f}, quantity={q:.2f}" for p, q in base.observations)
    lines.append(f"updated_price_cap={updated.p_max:.4f}")
    if updated.scenario_note:
        lines.append(f"updated_context={updated.scenario_note}")
    lines.append("updated_evidence:")
    lines.extend(f"  price={p:.2f}, quantity={q:.2f}" for p, q in updated.observations)
    lines.extend(
        [
            f"relation={case.relation}",
            f"Claim: {relation_text}.",
            "Decide whether the claim is valid or invalid for this evidence update.",
        ]
    )
    return "\n".join(lines)


def _pricing_law_trial_json(trial: PricingLawTrial) -> dict:
    return {
        "case": trial.case.key,
        "law_family": trial.case.law_family,
        "base_alpha": trial.case.base_alpha,
        "base_beta": trial.case.base_beta,
        "base_p_max": trial.case.base_p_max,
        "new_alpha": trial.case.new_alpha,
        "new_beta": trial.case.new_beta,
        "new_p_max": trial.case.new_p_max,
        "relation": trial.case.relation,
        "base_price": trial.base_price,
        "new_price": trial.new_price,
        "oracle_label": trial.oracle_label,
        "chosen_label": trial.chosen_label,
        "correct": trial.correct,
        "invalid_accept": trial.invalid_accept,
        "valid_reject": trial.valid_reject,
        "raw_response": trial.raw_response,
    }


def _pricing_evidence_law_trial_json(trial: PricingEvidenceLawTrial) -> dict:
    return {
        "case": trial.case.key,
        "counterfactual_set": trial.case.case_set.key,
        "law_family": trial.case.law_family,
        "relation": trial.case.relation,
        "base_price": trial.base_price,
        "new_price": trial.new_price,
        "oracle_label": trial.oracle_label,
        "chosen_label": trial.chosen_label,
        "correct": trial.correct,
        "invalid_accept": trial.invalid_accept,
        "valid_reject": trial.valid_reject,
        "raw_response": trial.raw_response,
    }
