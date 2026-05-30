from __future__ import annotations

import random
from dataclasses import dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float, parse_token


PRICING_SYSTEM = (
    "TASK: pricing_price\n"
    "Choose a price. Return one final line only: FINAL_PRICE: <number>."
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


DEFAULT_CASES = [
    PricingCase("snack_box", alpha=180.0, beta=6.0, sigma=4.0, p_max=30.0, seed=11),
    PricingCase("premium_widget", alpha=260.0, beta=4.0, sigma=6.0, p_max=55.0, seed=29),
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
        "small_intercept_up_valid",
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
        "snack_downshift_new_lt_base_valid",
        case_set=COUNTERFACTUAL_SETS[0],
        relation="new_lt_base",
        law_family="evidence_downshift",
    ),
    PricingEvidenceLawCase(
        "snack_downshift_new_ge_base_invalid",
        case_set=COUNTERFACTUAL_SETS[0],
        relation="new_ge_base",
        law_family="evidence_downshift",
    ),
    PricingEvidenceLawCase(
        "premium_upswing_new_gt_base_valid",
        case_set=COUNTERFACTUAL_SETS[1],
        relation="new_gt_base",
        law_family="evidence_upswing",
    ),
    PricingEvidenceLawCase(
        "premium_upswing_new_le_base_invalid",
        case_set=COUNTERFACTUAL_SETS[1],
        relation="new_le_base",
        law_family="evidence_upswing",
    ),
    PricingEvidenceLawCase(
        "noisy_snack_new_lt_base_valid",
        case_set=COUNTERFACTUAL_SETS[2],
        relation="new_lt_base",
        law_family="noisy_downshift",
    ),
    PricingEvidenceLawCase(
        "noisy_snack_new_gt_base_invalid",
        case_set=COUNTERFACTUAL_SETS[2],
        relation="new_gt_base",
        law_family="noisy_downshift",
    ),
    PricingEvidenceLawCase(
        "noisy_enterprise_new_gt_base_valid",
        case_set=COUNTERFACTUAL_SETS[3],
        relation="new_gt_base",
        law_family="noisy_upswing",
    ),
    PricingEvidenceLawCase(
        "noisy_enterprise_new_le_base_invalid",
        case_set=COUNTERFACTUAL_SETS[3],
        relation="new_le_base",
        law_family="noisy_upswing",
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
    return summarize_pricing_evidence_law_trials(agent.name, rows)


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
        "task": "pricing_evidence_law_audit",
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
