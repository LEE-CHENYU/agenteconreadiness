from __future__ import annotations

from dataclasses import dataclass, asdict

from aeread_lab.models import Agent
from aeread_lab.parsing import parse_token
from aeread_lab.stats import bootstrap_mean_ci, mean


AMBIGUITY_SYSTEM = (
    "TASK: ambiguity_action\n"
    "Choose one action under ambiguous probabilities. Return one final line only: "
    "FINAL_ACTION: <action_id>."
)


@dataclass(frozen=True)
class Action:
    action_id: str
    payoffs: tuple[float, ...]


@dataclass(frozen=True)
class Prior:
    prior_id: str
    probabilities: tuple[float, ...]


@dataclass(frozen=True)
class AmbiguityCase:
    key: str
    real_case: str
    state_ids: tuple[str, ...]
    priors: tuple[Prior, ...]
    reference_prior_id: str
    actions: tuple[Action, ...]
    alpha: float = 1.0
    signal_likelihoods: tuple[float, ...] | None = None


@dataclass
class AmbiguityTrial:
    case: AmbiguityCase
    oracle_action: str
    reference_prior_action: str
    maxmin_action: str
    optimistic_action: str
    chosen_action: str | None
    robust_regret: float | None
    raw_response: str


DEFAULT_CASES = [
    AmbiguityCase(
        key="new_market_entry",
        real_case="market-entry decision where demand probabilities are not identifiable yet",
        state_ids=("weak", "base", "strong"),
        reference_prior_id="analyst_base",
        priors=(
            Prior("analyst_base", (0.20, 0.50, 0.30)),
            Prior("downside", (0.55, 0.35, 0.10)),
            Prior("upside", (0.10, 0.35, 0.55)),
        ),
        actions=(
            Action("safe_pilot", (24.0, 32.0, 38.0)),
            Action("full_launch", (-20.0, 45.0, 90.0)),
            Action("delay", (18.0, 20.0, 22.0)),
        ),
    ),
    AmbiguityCase(
        key="supplier_country_shift",
        real_case="supply-chain shift under ambiguous tariff and disruption probabilities",
        state_ids=("tariff", "normal", "boom"),
        reference_prior_id="consultant_base",
        priors=(
            Prior("consultant_base", (0.15, 0.55, 0.30)),
            Prior("stress", (0.50, 0.40, 0.10)),
            Prior("benign", (0.05, 0.55, 0.40)),
        ),
        actions=(
            Action("dual_source", (28.0, 35.0, 42.0)),
            Action("single_low_cost", (-15.0, 48.0, 82.0)),
            Action("stay_current", (22.0, 28.0, 30.0)),
        ),
    ),
    AmbiguityCase(
        key="capital_project",
        real_case="capital-project choice with deep uncertainty over rate and adoption states",
        state_ids=("tight_credit", "steady", "easy_credit"),
        reference_prior_id="base_case",
        priors=(
            Prior("base_case", (0.20, 0.55, 0.25)),
            Prior("tight", (0.60, 0.30, 0.10)),
            Prior("easy", (0.10, 0.35, 0.55)),
        ),
        actions=(
            Action("modular_build", (35.0, 45.0, 55.0)),
            Action("levered_buildout", (-35.0, 70.0, 130.0)),
            Action("cash_preserve", (30.0, 32.0, 34.0)),
        ),
    ),
    AmbiguityCase(
        key="platform_rollout_signal",
        real_case="platform rollout after a noisy early-interest signal under multiple plausible demand priors",
        state_ids=("weak", "base", "strong"),
        reference_prior_id="product_base",
        alpha=0.65,
        signal_likelihoods=(0.30, 0.60, 0.82),
        priors=(
            Prior("product_base", (0.25, 0.50, 0.25)),
            Prior("skeptical", (0.58, 0.32, 0.10)),
            Prior("enthusiastic", (0.08, 0.37, 0.55)),
        ),
        actions=(
            Action("small_pilot", (26.0, 34.0, 42.0)),
            Action("staged_launch", (8.0, 58.0, 92.0)),
            Action("full_launch", (-38.0, 72.0, 145.0)),
            Action("wait", (20.0, 23.0, 27.0)),
        ),
    ),
    AmbiguityCase(
        key="credit_model_update",
        real_case="credit model update where default-risk priors are reweighted by a noisy delinquency signal",
        state_ids=("stress", "normal", "benign"),
        reference_prior_id="risk_base",
        alpha=0.72,
        signal_likelihoods=(0.70, 0.42, 0.18),
        priors=(
            Prior("risk_base", (0.22, 0.55, 0.23)),
            Prior("macro_stress", (0.55, 0.35, 0.10)),
            Prior("soft_landing", (0.10, 0.45, 0.45)),
        ),
        actions=(
            Action("tighten_credit", (44.0, 38.0, 25.0)),
            Action("selective_growth", (10.0, 58.0, 86.0)),
            Action("aggressive_growth", (-35.0, 74.0, 138.0)),
            Action("pause_originations", (30.0, 26.0, 20.0)),
        ),
    ),
]


def expected_value(action: Action, prior: Prior) -> float:
    return sum(payoff * probability for payoff, probability in zip(action.payoffs, prior.probabilities))


def updated_priors(case: AmbiguityCase) -> tuple[Prior, ...]:
    if case.signal_likelihoods is None:
        return case.priors
    priors = []
    for prior in case.priors:
        weighted = tuple(
            probability * likelihood
            for probability, likelihood in zip(prior.probabilities, case.signal_likelihoods)
        )
        total = sum(weighted)
        probabilities = tuple(value / total for value in weighted) if total > 0 else prior.probabilities
        priors.append(Prior(prior.prior_id, probabilities))
    return tuple(priors)


def robust_value(case: AmbiguityCase, action: Action) -> float:
    return min(expected_value(action, prior) for prior in updated_priors(case))


def optimistic_value(case: AmbiguityCase, action: Action) -> float:
    return max(expected_value(action, prior) for prior in updated_priors(case))


def ambiguity_value(case: AmbiguityCase, action: Action) -> float:
    alpha = max(0.0, min(1.0, case.alpha))
    return alpha * robust_value(case, action) + (1.0 - alpha) * optimistic_value(case, action)


def oracle_action(case: AmbiguityCase) -> str:
    return max(case.actions, key=lambda action: ambiguity_value(case, action)).action_id


def maxmin_action(case: AmbiguityCase) -> str:
    return max(case.actions, key=lambda action: robust_value(case, action)).action_id


def optimistic_action(case: AmbiguityCase) -> str:
    return max(case.actions, key=lambda action: optimistic_value(case, action)).action_id


def reference_prior_action(case: AmbiguityCase) -> str:
    prior = next(prior for prior in updated_priors(case) if prior.prior_id == case.reference_prior_id)
    return max(case.actions, key=lambda action: expected_value(action, prior)).action_id


def run_ambiguity_game(agent: Agent, cases: list[AmbiguityCase] | None = None) -> dict:
    cases = cases or DEFAULT_CASES
    trials: list[AmbiguityTrial] = []
    for case in cases:
        oracle = oracle_action(case)
        reference = reference_prior_action(case)
        maxmin = maxmin_action(case)
        optimistic = optimistic_action(case)
        response = agent.complete(AMBIGUITY_SYSTEM, _prompt(case))
        chosen = parse_token("FINAL_ACTION", response)
        action_by_id = {action.action_id: action for action in case.actions}
        chosen = chosen if chosen in action_by_id else None
        regret = (
            ambiguity_value(case, action_by_id[oracle]) - ambiguity_value(case, action_by_id[chosen])
            if chosen is not None
            else None
        )
        trials.append(
            AmbiguityTrial(
                case=case,
                oracle_action=oracle,
                reference_prior_action=reference,
                maxmin_action=maxmin,
                optimistic_action=optimistic,
                chosen_action=chosen,
                robust_regret=regret,
                raw_response=response,
            )
        )
    return summarize_ambiguity_trials(agent.name, trials)


def summarize_ambiguity_trials(agent_name: str, trials: list[AmbiguityTrial]) -> dict:
    regrets = [trial.robust_regret for trial in trials if trial.robust_regret is not None]
    missable = [trial for trial in trials if trial.reference_prior_action != trial.oracle_action]
    missed = sum(trial.chosen_action == trial.reference_prior_action for trial in missable)
    maxmin_missable = [trial for trial in trials if trial.maxmin_action != trial.oracle_action]
    maxmin_missed = sum(trial.chosen_action == trial.maxmin_action for trial in maxmin_missable)
    optimistic_missable = [trial for trial in trials if trial.optimistic_action != trial.oracle_action]
    optimistic_missed = sum(trial.chosen_action == trial.optimistic_action for trial in optimistic_missable)
    return {
        "task": "ambiguity",
        "agent": agent_name,
        "n_trials": len(trials),
        "mean_robust_regret": mean(regrets),
        "mean_robust_regret_ci95": bootstrap_mean_ci(regrets),
        "reference_prior_miss_rate": missed / len(missable) if missable else 0.0,
        "maxmin_miss_rate": maxmin_missed / len(maxmin_missable) if maxmin_missable else 0.0,
        "optimistic_miss_rate": optimistic_missed / len(optimistic_missable) if optimistic_missable else 0.0,
        "trials": [_trial_json(trial) for trial in trials],
    }


def _prompt(case: AmbiguityCase) -> str:
    lines = [
        f"case={case.key}",
        f"real_case={case.real_case}",
        "Probability model is ambiguous: no single prior is authoritative.",
        f"states={','.join(case.state_ids)}",
        f"reference_prior_id={case.reference_prior_id}",
        f"ambiguity_alpha={case.alpha:.4f}",
        "Plausible priors:",
    ]
    for prior in case.priors:
        probs = ",".join(f"{state}={probability:.4f}" for state, probability in zip(case.state_ids, prior.probabilities))
        lines.append(f"  prior_id={prior.prior_id} {probs}")
    if case.signal_likelihoods is not None:
        likelihoods = ",".join(
            f"{state}={likelihood:.4f}"
            for state, likelihood in zip(case.state_ids, case.signal_likelihoods)
        )
        lines.append(f"observed_signal_likelihoods {likelihoods}")
    lines.append("Actions:")
    for action in case.actions:
        payoffs = ",".join(f"{state}={payoff:.2f}" for state, payoff in zip(case.state_ids, action.payoffs))
        lines.append(f"  action_id={action.action_id} {payoffs}")
    lines.extend(
        [
            "First update each plausible prior using the observed signal likelihoods if they are present.",
            "Then use alpha-maxmin expected utility across the plausible priors: "
            "alpha * worst_prior_value + (1-alpha) * best_prior_value.",
            "Choose the action with the best configured ambiguity value, not the action favored only by the reference prior.",
        ]
    )
    return "\n".join(lines)


def _trial_json(trial: AmbiguityTrial) -> dict:
    data = asdict(trial)
    data["case"] = asdict(trial.case)
    return data
