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
    cases = cases or MULTI_PRODUCT_CAPACITY_CASES
    rows = []
    for case in cases:
        oracle_a, oracle_b = multi_product_capacity_oracle_prices(case)
        capacity_blind_a, capacity_blind_b = multi_product_capacity_blind_prices(case)
        independent_a, independent_b = multi_product_capacity_independent_prices(case)
        oracle_rev = multi_product_capacity_revenue(case, oracle_a, oracle_b)
        response = agent.complete(PRICING_MULTI_CAPACITY_SYSTEM, _multi_product_capacity_prompt(case))
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
        "task": "pricing_multi_product_capacity",
        "agent": agent.name,
        "n_trials": len(rows),
        "mean_price_l1_error": sum(errors) / len(errors) if errors else None,
        "mean_revenue_gap": sum(gaps) / len(gaps) if gaps else None,
        "parse_rate": len(parsed) / len(rows) if rows else 0.0,
        "capacity_blind_miss_rate": capacity_blind_misses / len(rows) if rows else 0.0,
        "independent_miss_rate": independent_misses / len(rows) if rows else 0.0,
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
