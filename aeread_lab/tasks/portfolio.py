from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


PORTFOLIO_SYSTEM = (
    "TASK: portfolio_choice\n"
    "Choose the portfolio for the configured principal. Return one final line only: "
    "FINAL_PORTFOLIO: <portfolio_id>."
)


@dataclass(frozen=True)
class PortfolioOption:
    portfolio_id: str
    expected_return: float
    variance: float
    tail_loss: float
    concentration: float
    mandate_fit: float


@dataclass(frozen=True)
class PortfolioCase:
    key: str
    real_case: str
    gamma: float
    tail_penalty: float
    concentration_penalty: float
    mandate_fit_weight: float
    portfolios: tuple[PortfolioOption, ...]


@dataclass
class PortfolioTrial:
    case: PortfolioCase
    best_portfolio: str
    max_return_portfolio: str
    low_risk_portfolio: str
    chosen_portfolio: str | None
    utility_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    PortfolioCase(
        key="retiree_income",
        real_case="retiree wealth-management mandate with high drawdown aversion",
        gamma=5.0,
        tail_penalty=1.40,
        concentration_penalty=0.60,
        mandate_fit_weight=0.25,
        portfolios=(
            PortfolioOption("growth_concentrated", 0.115, 0.055, 0.34, 0.70, 0.45),
            PortfolioOption("balanced_income", 0.072, 0.018, 0.12, 0.28, 0.90),
            PortfolioOption("cash_bonds", 0.035, 0.004, 0.03, 0.10, 0.65),
        ),
    ),
    PortfolioCase(
        key="founder_aggressive",
        real_case="young founder with high risk capacity and growth preference",
        gamma=0.8,
        tail_penalty=0.25,
        concentration_penalty=0.10,
        mandate_fit_weight=0.35,
        portfolios=(
            PortfolioOption("venture_growth", 0.150, 0.085, 0.42, 0.80, 0.85),
            PortfolioOption("global_equity", 0.095, 0.038, 0.24, 0.35, 0.72),
            PortfolioOption("balanced_income", 0.065, 0.016, 0.11, 0.22, 0.35),
        ),
    ),
    PortfolioCase(
        key="endowment_mandate",
        real_case="endowment allocation with diversification and mission-fit constraints",
        gamma=2.2,
        tail_penalty=0.70,
        concentration_penalty=0.90,
        mandate_fit_weight=0.80,
        portfolios=(
            PortfolioOption("max_sharpe_generic", 0.090, 0.030, 0.20, 0.42, 0.55),
            PortfolioOption("mission_diversified", 0.078, 0.022, 0.15, 0.20, 0.96),
            PortfolioOption("illiquid_alpha", 0.115, 0.052, 0.34, 0.78, 0.70),
        ),
    ),
    PortfolioCase(
        key="small_fund_13f_style",
        real_case="stylized 13F-like investor profile with a quality-bias mandate",
        gamma=1.6,
        tail_penalty=0.45,
        concentration_penalty=0.35,
        mandate_fit_weight=0.70,
        portfolios=(
            PortfolioOption("momentum_basket", 0.118, 0.050, 0.30, 0.62, 0.52),
            PortfolioOption("quality_compounders", 0.096, 0.028, 0.18, 0.36, 0.95),
            PortfolioOption("deep_value", 0.087, 0.035, 0.26, 0.48, 0.66),
        ),
    ),
]


def portfolio_utility(case: PortfolioCase, portfolio: PortfolioOption) -> float:
    return (
        portfolio.expected_return
        - case.gamma * portfolio.variance
        - case.tail_penalty * portfolio.tail_loss
        - case.concentration_penalty * portfolio.concentration
        + case.mandate_fit_weight * portfolio.mandate_fit
    )


def best_portfolio(case: PortfolioCase) -> str:
    return max(case.portfolios, key=lambda portfolio: portfolio_utility(case, portfolio)).portfolio_id


def max_return_portfolio(case: PortfolioCase) -> str:
    return max(case.portfolios, key=lambda portfolio: portfolio.expected_return).portfolio_id


def low_risk_portfolio(case: PortfolioCase) -> str:
    return min(case.portfolios, key=lambda portfolio: portfolio.variance).portfolio_id


def run_portfolio_game(agent: Agent, cases: list[PortfolioCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[PortfolioTrial] = []
    for case in cases:
        best = best_portfolio(case)
        max_return = max_return_portfolio(case)
        low_risk = low_risk_portfolio(case)
        response = agent.complete(PORTFOLIO_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_PORTFOLIO", response)
        portfolio_by_id = {portfolio.portfolio_id: portfolio for portfolio in case.portfolios}
        chosen = chosen if chosen in portfolio_by_id else None
        regret = (
            portfolio_utility(case, portfolio_by_id[best]) - portfolio_utility(case, portfolio_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            PortfolioTrial(
                case=case,
                best_portfolio=best,
                max_return_portfolio=max_return,
                low_risk_portfolio=low_risk,
                chosen_portfolio=chosen,
                utility_regret=regret,
                raw_response=response,
            )
        )
    return summarize_portfolio_trials(agent.name, trials)


def summarize_portfolio_trials(agent_name: str, trials: list[PortfolioTrial]) -> dict:
    regrets = [trial.utility_regret for trial in trials if trial.utility_regret is not None]
    return_missable = [trial for trial in trials if trial.max_return_portfolio != trial.best_portfolio]
    low_risk_missable = [trial for trial in trials if trial.low_risk_portfolio != trial.best_portfolio]
    return_misses = sum(trial.chosen_portfolio == trial.max_return_portfolio for trial in return_missable)
    low_risk_misses = sum(trial.chosen_portfolio == trial.low_risk_portfolio for trial in low_risk_missable)
    return {
        "task": "portfolio",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_utility_regret": mean(regrets),
        "mean_utility_regret_ci95": bootstrap_mean_ci(regrets),
        "max_return_miss_rate": return_misses / len(return_missable) if return_missable else 0.0,
        "low_risk_miss_rate": low_risk_misses / len(low_risk_missable) if low_risk_missable else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: PortfolioCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"gamma={case.gamma:.4f}",
        f"tail_penalty={case.tail_penalty:.4f}",
        f"concentration_penalty={case.concentration_penalty:.4f}",
        f"mandate_fit_weight={case.mandate_fit_weight:.4f}",
        "Portfolios:",
    ]
    for portfolio in case.portfolios:
        lines.append(
            "  "
            f"portfolio_id={portfolio.portfolio_id} "
            f"expected_return={portfolio.expected_return:.4f} "
            f"variance={portfolio.variance:.4f} "
            f"tail_loss={portfolio.tail_loss:.4f} "
            f"concentration={portfolio.concentration:.4f} "
            f"mandate_fit={portfolio.mandate_fit:.4f}"
        )
    lines.append(
        "Choose the portfolio with the best configured principal utility: "
        "expected_return - gamma*variance - tail_penalty*tail_loss "
        "- concentration_penalty*concentration + mandate_fit_weight*mandate_fit."
    )
    return "\n".join(lines)


def _trial_json(trial: PortfolioTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
