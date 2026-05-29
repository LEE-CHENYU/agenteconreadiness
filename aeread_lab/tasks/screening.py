from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


SCREENING_SYSTEM = (
    "TASK: screening_choice\n"
    "Choose the contract menu for the configured principal. Return one final line only: "
    "FINAL_MENU: <menu_id>."
)


@dataclass(frozen=True)
class PrivateType:
    type_id: str
    probability: float
    value_per_unit: float
    service_cost_per_unit: float


@dataclass(frozen=True)
class Contract:
    type_id: str
    quantity: float
    price: float


@dataclass(frozen=True)
class MenuOption:
    menu_id: str
    contracts: tuple[Contract, ...]


@dataclass(frozen=True)
class ScreeningCase:
    key: str
    real_case: str
    profit_weight: float
    surplus_weight: float
    access_weight: float
    ic_penalty: float
    ir_penalty: float
    types: tuple[PrivateType, ...]
    menus: tuple[MenuOption, ...]


@dataclass(frozen=True)
class MenuMetrics:
    expected_profit: float
    expected_surplus: float
    participation_rate: float
    ic_violation_rate: float
    ir_violation_rate: float


@dataclass
class ScreeningTrial:
    case: ScreeningCase
    best_menu: str
    max_profit_menu: str
    ic_blind_menu: str
    chosen_menu: str | None
    score_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    ScreeningCase(
        key="insurance_pool",
        real_case="insurance menu for low-risk and high-risk customers under adverse selection",
        profit_weight=1.0,
        surplus_weight=0.25,
        access_weight=0.35,
        ic_penalty=2.0,
        ir_penalty=2.2,
        types=(
            PrivateType("low_risk", 0.60, 0.90, 0.25),
            PrivateType("high_risk", 0.40, 1.60, 0.85),
        ),
        menus=(
            MenuOption(
                "pooled_high_price",
                (
                    Contract("low_risk", 80.0, 85.0),
                    Contract("high_risk", 80.0, 85.0),
                ),
            ),
            MenuOption(
                "ic_screening_menu",
                (
                    Contract("low_risk", 35.0, 22.0),
                    Contract("high_risk", 80.0, 72.0),
                ),
            ),
            MenuOption(
                "access_subsidy",
                (
                    Contract("low_risk", 50.0, 20.0),
                    Contract("high_risk", 80.0, 50.0),
                ),
            ),
        ),
    ),
    ScreeningCase(
        key="saas_tiers",
        real_case="SaaS tier menu where enterprise users can mimic small-business plans",
        profit_weight=1.0,
        surplus_weight=0.15,
        access_weight=0.20,
        ic_penalty=3.0,
        ir_penalty=2.0,
        types=(
            PrivateType("small_business", 0.70, 1.00, 0.10),
            PrivateType("enterprise", 0.30, 3.00, 0.10),
        ),
        menus=(
            MenuOption(
                "greedy_full_access",
                (
                    Contract("small_business", 100.0, 95.0),
                    Contract("enterprise", 100.0, 260.0),
                ),
            ),
            MenuOption(
                "self_selection_tiers",
                (
                    Contract("small_business", 45.0, 35.0),
                    Contract("enterprise", 100.0, 170.0),
                ),
            ),
            MenuOption(
                "enterprise_only",
                (
                    Contract("small_business", 0.0, 0.0),
                    Contract("enterprise", 100.0, 230.0),
                ),
            ),
        ),
    ),
    ScreeningCase(
        key="credit_lines",
        real_case="credit-line contracts where risky borrowers prefer safer borrowers' rates",
        profit_weight=1.0,
        surplus_weight=0.10,
        access_weight=0.30,
        ic_penalty=2.6,
        ir_penalty=2.5,
        types=(
            PrivateType("safe_borrower", 0.55, 1.05, 0.45),
            PrivateType("risky_borrower", 0.45, 1.45, 0.95),
        ),
        menus=(
            MenuOption(
                "cheap_credit_for_all",
                (
                    Contract("safe_borrower", 90.0, 72.0),
                    Contract("risky_borrower", 90.0, 112.0),
                ),
            ),
            MenuOption(
                "collateral_screening",
                (
                    Contract("safe_borrower", 75.0, 64.0),
                    Contract("risky_borrower", 55.0, 70.0),
                ),
            ),
            MenuOption(
                "tight_underwriting",
                (
                    Contract("safe_borrower", 80.0, 72.0),
                    Contract("risky_borrower", 20.0, 32.0),
                ),
            ),
        ),
    ),
    ScreeningCase(
        key="vendor_service_levels",
        real_case="supplier service-level menu with hidden supplier capability",
        profit_weight=0.85,
        surplus_weight=0.30,
        access_weight=0.45,
        ic_penalty=2.4,
        ir_penalty=2.0,
        types=(
            PrivateType("basic_supplier", 0.65, 0.95, 0.35),
            PrivateType("premium_supplier", 0.35, 1.75, 0.65),
        ),
        menus=(
            MenuOption(
                "one_size_premium",
                (
                    Contract("basic_supplier", 90.0, 88.0),
                    Contract("premium_supplier", 90.0, 128.0),
                ),
            ),
            MenuOption(
                "screened_service_levels",
                (
                    Contract("basic_supplier", 40.0, 28.0),
                    Contract("premium_supplier", 85.0, 112.0),
                ),
            ),
            MenuOption(
                "broad_access_menu",
                (
                    Contract("basic_supplier", 55.0, 25.0),
                    Contract("premium_supplier", 75.0, 75.0),
                ),
            ),
        ),
    ),
]


def utility(type_: PrivateType, contract: Contract) -> float:
    return type_.value_per_unit * contract.quantity - contract.price


def profit(type_: PrivateType, contract: Contract) -> float:
    return contract.price - type_.service_cost_per_unit * contract.quantity


def menu_metrics(case: ScreeningCase, menu: MenuOption) -> MenuMetrics:
    contract_by_type = {contract.type_id: contract for contract in menu.contracts}
    expected_profit = 0.0
    expected_surplus = 0.0
    participation = 0.0
    ic_violation = 0.0
    ir_violation = 0.0
    for type_ in case.types:
        intended = contract_by_type[type_.type_id]
        intended_utility = utility(type_, intended)
        expected_profit += type_.probability * profit(type_, intended)
        expected_surplus += type_.probability * intended_utility
        if intended_utility >= -1e-9:
            participation += type_.probability
        else:
            ir_violation += type_.probability
        if any(utility(type_, other) > intended_utility + 1e-9 for other in menu.contracts):
            ic_violation += type_.probability
    return MenuMetrics(
        expected_profit=expected_profit,
        expected_surplus=expected_surplus,
        participation_rate=participation,
        ic_violation_rate=ic_violation,
        ir_violation_rate=ir_violation,
    )


def screening_score(case: ScreeningCase, menu: MenuOption, *, constraint_blind: bool = False) -> float:
    metrics = menu_metrics(case, menu)
    ic_penalty = 0.0 if constraint_blind else case.ic_penalty
    ir_penalty = 0.0 if constraint_blind else case.ir_penalty
    return (
        case.profit_weight * metrics.expected_profit
        + case.surplus_weight * metrics.expected_surplus
        + case.access_weight * 100.0 * metrics.participation_rate
        - ic_penalty * 100.0 * metrics.ic_violation_rate
        - ir_penalty * 100.0 * metrics.ir_violation_rate
    )


def best_menu(case: ScreeningCase) -> str:
    return max(case.menus, key=lambda menu: screening_score(case, menu)).menu_id


def max_profit_menu(case: ScreeningCase) -> str:
    return max(case.menus, key=lambda menu: menu_metrics(case, menu).expected_profit).menu_id


def ic_blind_menu(case: ScreeningCase) -> str:
    return max(case.menus, key=lambda menu: screening_score(case, menu, constraint_blind=True)).menu_id


def run_screening_game(agent: Agent, cases: list[ScreeningCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[ScreeningTrial] = []
    for case in cases:
        best = best_menu(case)
        max_profit = max_profit_menu(case)
        blind = ic_blind_menu(case)
        response = agent.complete(SCREENING_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_MENU", response)
        menu_by_id = {menu.menu_id: menu for menu in case.menus}
        chosen = chosen if chosen in menu_by_id else None
        regret = (
            screening_score(case, menu_by_id[best]) - screening_score(case, menu_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            ScreeningTrial(
                case=case,
                best_menu=best,
                max_profit_menu=max_profit,
                ic_blind_menu=blind,
                chosen_menu=chosen,
                score_regret=regret,
                raw_response=response,
            )
        )
    return summarize_screening_trials(agent.name, trials)


def summarize_screening_trials(agent_name: str, trials: list[ScreeningTrial]) -> dict:
    regrets = [trial.score_regret for trial in trials if trial.score_regret is not None]
    profit_missable = [trial for trial in trials if trial.max_profit_menu != trial.best_menu]
    blind_missable = [trial for trial in trials if trial.ic_blind_menu != trial.best_menu]
    profit_misses = sum(trial.chosen_menu == trial.max_profit_menu for trial in profit_missable)
    blind_misses = sum(trial.chosen_menu == trial.ic_blind_menu for trial in blind_missable)
    return {
        "task": "screening",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_score_regret": mean(regrets),
        "mean_score_regret_ci95": bootstrap_mean_ci(regrets),
        "max_profit_miss_rate": profit_misses / len(profit_missable) if profit_missable else 0.0,
        "constraint_blind_miss_rate": blind_misses / len(blind_missable) if blind_missable else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: ScreeningCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"profit_weight={case.profit_weight:.4f}",
        f"surplus_weight={case.surplus_weight:.4f}",
        f"access_weight={case.access_weight:.4f}",
        f"ic_penalty={case.ic_penalty:.4f}",
        f"ir_penalty={case.ir_penalty:.4f}",
        "Private types:",
    ]
    for type_ in case.types:
        lines.append(
            "  "
            f"type_id={type_.type_id} "
            f"probability={type_.probability:.4f} "
            f"value_per_unit={type_.value_per_unit:.4f} "
            f"service_cost_per_unit={type_.service_cost_per_unit:.4f}"
        )
    lines.append("Candidate menus:")
    for menu in case.menus:
        lines.append(f"  menu_id={menu.menu_id}")
        for contract in menu.contracts:
            lines.append(
                "    "
                f"contract_type={contract.type_id} "
                f"quantity={contract.quantity:.2f} "
                f"price={contract.price:.2f}"
            )
    lines.extend(
        [
            "For each private type, intended utility = value_per_unit*quantity - price.",
            "A menu violates participation if a type's intended utility is negative.",
            "A menu violates incentive compatibility if a type prefers another type's contract.",
            "Choose the menu with the best configured score: profit + surplus/access terms minus IC and participation penalties.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: ScreeningTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
