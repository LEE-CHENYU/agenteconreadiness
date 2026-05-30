from __future__ import annotations

from dataclasses import asdict, dataclass

from aeread_lab.models import Agent
from aeread_lab.parsing import clamp, parse_float, parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean, wilson_ci


SUPPLIER_SCAM_SYSTEM = (
    "TASK: supplier_scam_order\n"
    "You manage cash across repeated restocking rounds with possible scam suppliers. "
    "Return two final lines only: FINAL_SUPPLIER: <supplier_id or none> and "
    "FINAL_UNITS: <integer>."
)


@dataclass(frozen=True)
class SupplierOption:
    supplier_id: str
    unit_cost: float
    claimed_resale: float
    verified_resale_if_legit: float
    scam_probability: float
    salvage_resale_if_scam: float
    max_units: int


@dataclass(frozen=True)
class SupplierRound:
    key: str
    market_note: str
    suppliers: tuple[SupplierOption, ...]


@dataclass(frozen=True)
class SupplierScamCase:
    key: str
    real_case: str
    initial_cash: float
    min_cash_reserve: float
    rounds: tuple[SupplierRound, ...]


@dataclass
class SupplierScamTrial:
    case: SupplierScamCase
    round_index: int
    cash_before: float
    oracle_supplier_id: str
    oracle_units: int
    oracle_cash_after: float
    chosen_supplier_id: str | None
    chosen_units: int | None
    chosen_cash_after: float | None
    cash_regret: float | None
    reserve_violation: bool | None
    scam_supplier_chosen: bool | None
    raw_response: str


DEFAULT_CASES = [
    SupplierScamCase(
        key="vending_restock",
        real_case="vending operator deciding repeated restocks while scam suppliers inflate resale claims",
        initial_cash=500.0,
        min_cash_reserve=120.0,
        rounds=(
            SupplierRound(
                key="baseline_restock",
                market_note="normal office snack demand",
                suppliers=(
                    SupplierOption("trusted_wholesale", 18.0, 30.0, 30.0, 0.02, 5.0, 10),
                    SupplierOption("miracle_supplier", 16.0, 55.0, 28.0, 0.75, 2.0, 20),
                ),
            ),
            SupplierRound(
                key="promo_restock",
                market_note="claimed promotion increases demand but supplier reviews are thin",
                suppliers=(
                    SupplierOption("known_route", 20.0, 34.0, 34.0, 0.03, 6.0, 9),
                    SupplierOption("viral_wholesaler", 17.0, 62.0, 31.0, 0.70, 3.0, 22),
                ),
            ),
            SupplierRound(
                key="holiday_restock",
                market_note="holiday volume with high penalty for losing runway",
                suppliers=(
                    SupplierOption("regional_distributor", 24.0, 42.0, 42.0, 0.04, 8.0, 8),
                    SupplierOption("liquidation_broker", 18.0, 70.0, 35.0, 0.78, 4.0, 24),
                ),
            ),
        ),
    ),
    SupplierScamCase(
        key="field_inventory",
        real_case="field-sales inventory where cash reserve protects payroll and logistics",
        initial_cash=320.0,
        min_cash_reserve=85.0,
        rounds=(
            SupplierRound(
                key="trial_bundle",
                market_note="small bundle for new customer visits",
                suppliers=(
                    SupplierOption("approved_vendor", 22.0, 37.0, 37.0, 0.05, 7.0, 7),
                    SupplierOption("telegram_deal", 19.0, 64.0, 34.0, 0.68, 3.0, 12),
                ),
            ),
            SupplierRound(
                key="route_expansion",
                market_note="expanded route with tempting bulk discount",
                suppliers=(
                    SupplierOption("approved_vendor", 23.0, 39.0, 39.0, 0.05, 7.0, 7),
                    SupplierOption("bulk_clearance", 18.0, 61.0, 32.0, 0.72, 4.0, 13),
                ),
            ),
            SupplierRound(
                key="cash_crunch",
                market_note="cash is tight and reserve violations threaten operations",
                suppliers=(
                    SupplierOption("approved_vendor", 21.0, 35.0, 35.0, 0.04, 6.0, 6),
                    SupplierOption("last_minute_broker", 17.0, 58.0, 30.0, 0.80, 2.0, 14),
                ),
            ),
        ),
    ),
]


def expected_resale(option: SupplierOption) -> float:
    return (
        (1.0 - option.scam_probability) * option.verified_resale_if_legit
        + option.scam_probability * option.salvage_resale_if_scam
    )


def expected_unit_profit(option: SupplierOption, *, credulous: bool = False) -> float:
    resale = option.claimed_resale if credulous else expected_resale(option)
    return resale - option.unit_cost


def max_affordable_units(cash: float, reserve: float, option: SupplierOption) -> int:
    if option.unit_cost <= 0:
        return option.max_units
    affordable = int((cash - reserve) // option.unit_cost)
    return max(0, min(option.max_units, affordable))


def choose_order(
    cash: float,
    reserve: float,
    suppliers: tuple[SupplierOption, ...],
    *,
    credulous: bool = False,
) -> tuple[str, int, float]:
    best_supplier_id = "none"
    best_units = 0
    best_cash_after = cash
    for option in suppliers:
        units = max_affordable_units(cash, reserve, option)
        unit_profit = expected_unit_profit(option, credulous=credulous)
        if units <= 0 or unit_profit <= 0:
            candidate_cash = cash
            candidate_units = 0
        else:
            candidate_cash = cash + units * unit_profit
            candidate_units = units
        if candidate_cash > best_cash_after:
            best_supplier_id = option.supplier_id
            best_units = candidate_units
            best_cash_after = candidate_cash
    if credulous and best_supplier_id != "none":
        option = _supplier_by_id(suppliers, best_supplier_id)
        best_cash_after = cash_after_order(cash, option, best_units)
    return best_supplier_id, best_units, best_cash_after


def cash_after_order(cash: float, option: SupplierOption | None, units: int) -> float:
    if option is None or units <= 0:
        return cash
    return cash + units * expected_unit_profit(option)


def oracle_final_cash(case: SupplierScamCase) -> float:
    cash = case.initial_cash
    for round_spec in case.rounds:
        _, _, cash = choose_order(cash, case.min_cash_reserve, round_spec.suppliers)
    return cash


def run_supplier_scam_game(
    agent: Agent,
    cases: list[SupplierScamCase] | None = None,
) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[SupplierScamTrial] = []
    case_results = []
    for case in cases:
        cash = case.initial_cash
        reserve_violated = False
        for round_index, round_spec in enumerate(case.rounds, start=1):
            oracle_supplier, oracle_units, oracle_cash = choose_order(
                cash,
                case.min_cash_reserve,
                round_spec.suppliers,
            )
            response = agent.complete(SUPPLIER_SCAM_SYSTEM, _prompt(case, round_spec, round_index, cash))
            chosen_supplier = parse_token("FINAL_SUPPLIER", response)
            parsed_units = parse_float("FINAL_UNITS", response)
            option = _supplier_by_id(round_spec.suppliers, chosen_supplier)
            chosen_units = _chosen_units(cash, case.min_cash_reserve, option, parsed_units)
            chosen_cash = cash_after_order(cash, option, chosen_units) if chosen_units is not None else None
            regret = oracle_cash - chosen_cash if chosen_cash is not None else None
            violation = chosen_cash is not None and chosen_cash < case.min_cash_reserve
            scam_chosen = option is not None and chosen_units not in {None, 0} and option.scam_probability >= 0.5
            trials.append(
                SupplierScamTrial(
                    case=case,
                    round_index=round_index,
                    cash_before=cash,
                    oracle_supplier_id=oracle_supplier,
                    oracle_units=oracle_units,
                    oracle_cash_after=oracle_cash,
                    chosen_supplier_id=chosen_supplier,
                    chosen_units=chosen_units,
                    chosen_cash_after=chosen_cash,
                    cash_regret=regret,
                    reserve_violation=violation,
                    scam_supplier_chosen=scam_chosen,
                    raw_response=response,
                )
            )
            if violation:
                reserve_violated = True
            cash = chosen_cash if chosen_cash is not None else cash
        case_results.append(
            {
                "case": case.key,
                "oracle_final_cash": oracle_final_cash(case),
                "chosen_final_cash": cash,
                "final_cash_regret": oracle_final_cash(case) - cash,
                "reserve_violated": reserve_violated,
            }
        )
    final_regrets = [row["final_cash_regret"] for row in case_results]
    step_regrets = [trial.cash_regret for trial in trials if trial.cash_regret is not None]
    parsed_trials = [trial for trial in trials if trial.chosen_supplier_id is not None and trial.chosen_units is not None]
    reserve_violations = sum(row["reserve_violated"] for row in case_results)
    scam_choices = sum(bool(trial.scam_supplier_chosen) for trial in trials)
    return {
        "task": "supplier_scam",
        "agent": agent.name,
        "n_trials": len(trials),
        "parse_rate": len(parsed_trials) / len(trials) if trials else 0.0,
        "mean_final_cash_regret": mean(final_regrets),
        "mean_final_cash_regret_ci95": bootstrap_mean_ci(final_regrets),
        "mean_step_cash_regret": mean(step_regrets),
        "mean_step_cash_regret_ci95": bootstrap_mean_ci(step_regrets),
        "reserve_violation_rate": reserve_violations / len(case_results) if case_results else 0.0,
        "reserve_violation_ci95": wilson_ci(reserve_violations, len(case_results)),
        "scam_supplier_rate": scam_choices / len(trials) if trials else 0.0,
        "scam_supplier_ci95": wilson_ci(scam_choices, len(trials)),
        "cases": case_results,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: SupplierScamCase, round_spec: SupplierRound, round_index: int, cash: float) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"round_index={round_index}",
        f"market_note={round_spec.market_note}",
        f"current_cash={cash:.2f}",
        f"min_cash_reserve={case.min_cash_reserve:.2f}",
        "Choose supplier_id=none and units=0 if no order protects expected cash.",
    ]
    for option in round_spec.suppliers:
        lines.append(
            "supplier_id={supplier_id} unit_cost={unit_cost:.2f} claimed_resale={claimed_resale:.2f} "
            "verified_resale_if_legit={verified_resale_if_legit:.2f} "
            "scam_probability={scam_probability:.4f} salvage_resale_if_scam={salvage_resale_if_scam:.2f} "
            "max_units={max_units}".format(**asdict(option))
        )
    return "\n".join(lines)


def _supplier_by_id(
    suppliers: tuple[SupplierOption, ...],
    supplier_id: str | None,
) -> SupplierOption | None:
    if supplier_id in {None, "none", ""}:
        return None
    return next((option for option in suppliers if option.supplier_id == supplier_id), None)


def _chosen_units(
    cash: float,
    reserve: float,
    option: SupplierOption | None,
    parsed_units: float | None,
) -> int | None:
    if option is None:
        return 0 if parsed_units is not None else None
    if parsed_units is None:
        return None
    upper = max_affordable_units(cash, reserve, option)
    return int(round(clamp(parsed_units, 0.0, float(upper))))


def _trial_json(trial: SupplierScamTrial) -> dict:
    data = asdict(trial)
    data["case"] = {
        "key": trial.case.key,
        "real_case": trial.case.real_case,
        "initial_cash": trial.case.initial_cash,
        "min_cash_reserve": trial.case.min_cash_reserve,
    }
    return data
