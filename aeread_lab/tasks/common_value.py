from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean, wilson_ci


COMMON_VALUE_SYSTEM = (
    "TASK: common_value_bid\n"
    "You bid in a common-value auction. The asset has one true resale value for all bidders, "
    "and bidders receive noisy appraisals before bidding. Choose one listed bid option. "
    "Return one final line only: FINAL_BID: <bid_id>."
)


@dataclass(frozen=True)
class BidOption:
    bid_id: str
    bid: float
    win_probability: float


@dataclass(frozen=True)
class CommonValueCase:
    key: str
    real_case: str
    n_bidders: int
    private_signal_value: float
    expected_selection_discount_if_win: float
    bid_options: tuple[BidOption, ...]


@dataclass
class CommonValueTrial:
    case: CommonValueCase
    oracle_bid_id: str
    private_value_bid_id: str
    chosen_bid_id: str | None
    oracle_expected_profit: float
    chosen_expected_profit: float | None
    profit_regret: float | None
    winner_curse_miss: bool | None
    negative_expected_profit: bool | None
    raw_response: str


DEFAULT_CASES = [
    CommonValueCase(
        key="mineral_rights",
        real_case="mineral-rights auction where your survey is a noisy high signal",
        n_bidders=6,
        private_signal_value=100.0,
        expected_selection_discount_if_win=25.0,
        bid_options=(
            BidOption("cautious", 55.0, 0.20),
            BidOption("discounted", 65.0, 0.45),
            BidOption("signal_bid", 80.0, 0.90),
            BidOption("aggressive", 100.0, 0.98),
        ),
    ),
    CommonValueCase(
        key="spectrum_block",
        real_case="common-value spectrum block with rival engineers seeing correlated signals",
        n_bidders=8,
        private_signal_value=150.0,
        expected_selection_discount_if_win=45.0,
        bid_options=(
            BidOption("low_entry", 85.0, 0.25),
            BidOption("discounted", 92.0, 0.45),
            BidOption("signal_bid", 120.0, 0.98),
            BidOption("aggressive", 150.0, 0.99),
        ),
    ),
    CommonValueCase(
        key="salvage_lot",
        real_case="industrial salvage lot where inspection estimates share common hidden defects",
        n_bidders=5,
        private_signal_value=80.0,
        expected_selection_discount_if_win=20.0,
        bid_options=(
            BidOption("low_entry", 45.0, 0.15),
            BidOption("discounted", 52.0, 0.40),
            BidOption("signal_bid", 67.0, 0.90),
            BidOption("aggressive", 84.0, 0.97),
        ),
    ),
    CommonValueCase(
        key="oil_lease",
        real_case="oil-lease auction with many competitors and a highly optimistic internal estimate",
        n_bidders=10,
        private_signal_value=220.0,
        expected_selection_discount_if_win=70.0,
        bid_options=(
            BidOption("low_entry", 120.0, 0.18),
            BidOption("discounted", 135.0, 0.45),
            BidOption("signal_bid", 175.0, 0.95),
            BidOption("aggressive", 225.0, 0.99),
        ),
    ),
]


def expected_value_if_win(case: CommonValueCase) -> float:
    return case.private_signal_value - case.expected_selection_discount_if_win


def expected_profit(case: CommonValueCase, bid: BidOption, *, winner_curse_aware: bool = True) -> float:
    value = expected_value_if_win(case) if winner_curse_aware else case.private_signal_value
    return bid.win_probability * (value - bid.bid)


def best_bid(case: CommonValueCase, *, winner_curse_aware: bool = True) -> BidOption:
    return max(case.bid_options, key=lambda bid: expected_profit(case, bid, winner_curse_aware=winner_curse_aware))


def run_common_value_game(agent: Agent, cases: list[CommonValueCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[CommonValueTrial] = []
    for case in cases:
        oracle_bid = best_bid(case, winner_curse_aware=True)
        private_value_bid = best_bid(case, winner_curse_aware=False)
        response = agent.complete(COMMON_VALUE_SYSTEM, _prompt(case))
        chosen_id = parse_token("FINAL_BID", response)
        chosen_bid = next((bid for bid in case.bid_options if bid.bid_id == chosen_id), None)
        chosen_profit = expected_profit(case, chosen_bid) if chosen_bid is not None else None
        oracle_profit = expected_profit(case, oracle_bid)
        regret = oracle_profit - chosen_profit if chosen_profit is not None else None
        trials.append(
            CommonValueTrial(
                case=case,
                oracle_bid_id=oracle_bid.bid_id,
                private_value_bid_id=private_value_bid.bid_id,
                chosen_bid_id=chosen_bid.bid_id if chosen_bid is not None else None,
                oracle_expected_profit=oracle_profit,
                chosen_expected_profit=chosen_profit,
                profit_regret=regret,
                winner_curse_miss=(
                    chosen_bid.bid_id == private_value_bid.bid_id and private_value_bid.bid_id != oracle_bid.bid_id
                    if chosen_bid is not None
                    else None
                ),
                negative_expected_profit=chosen_profit < 0 if chosen_profit is not None else None,
                raw_response=response,
            )
        )
    return summarize_common_value_trials(agent.name, trials)


def summarize_common_value_trials(agent_name: str, trials: list[CommonValueTrial]) -> dict:
    regrets = [trial.profit_regret for trial in trials if trial.profit_regret is not None]
    misses = [trial.winner_curse_miss for trial in trials if trial.winner_curse_miss is not None]
    negative = [trial.negative_expected_profit for trial in trials if trial.negative_expected_profit is not None]
    return {
        "task": "common_value",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_profit_regret": mean(regrets),
        "mean_profit_regret_ci95": bootstrap_mean_ci(regrets),
        "winner_curse_miss_rate": mean([1.0 if item else 0.0 for item in misses]),
        "winner_curse_miss_rate_ci95": wilson_ci(sum(1 for item in misses if item), len(misses)),
        "negative_expected_profit_rate": mean([1.0 if item else 0.0 for item in negative]),
        "negative_expected_profit_rate_ci95": wilson_ci(sum(1 for item in negative if item), len(negative)),
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: CommonValueCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        f"n_bidders={case.n_bidders}",
        f"internal_appraisal_value={case.private_signal_value:.2f}",
        f"historical_realized_value_gap_for_winning_bids={-case.expected_selection_discount_if_win:.2f}",
        "Objective: maximize expected dollar profit from the auction.",
        "Bid options:",
    ]
    for bid in case.bid_options:
        lines.append(
            f"bid_id={bid.bid_id} bid={bid.bid:.2f} win_probability={bid.win_probability:.2f}"
        )
    return "\n".join(lines)


def _trial_json(trial: CommonValueTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
