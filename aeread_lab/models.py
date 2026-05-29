from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from statistics import median
from typing import Protocol


ALLOWED_OPENAI_ALIASES = {
    "gpt-5.5": "gpt-5.5",
    "mini": os.environ.get("AEREAD_OPENAI_MODEL_MINI", "gpt-5.5-mini"),
    "nano": os.environ.get("AEREAD_OPENAI_MODEL_NANO", "gpt-5.5-nano"),
}


class Agent(Protocol):
    name: str

    def complete(self, system: str, user: str) -> str:
        ...


def resolve_openai_model(name: str) -> str:
    if name in ALLOWED_OPENAI_ALIASES:
        return ALLOWED_OPENAI_ALIASES[name]
    allowed = ", ".join(sorted(ALLOWED_OPENAI_ALIASES))
    raise ValueError(f"Unsupported model '{name}'. Allowed OpenAI aliases: {allowed}")


@dataclass
class OpenAIResponsesAgent:
    """Minimal OpenAI Responses API adapter.

    The build lab deliberately exposes only the user-approved aliases:
    `gpt-5.5`, `mini`, and `nano`.
    """

    model: str = "nano"
    max_output_tokens: int = 400
    name: str = "openai"

    def __post_init__(self) -> None:
        resolved = resolve_openai_model(self.model)
        self.name = f"openai:{self.model}"
        self._resolved_model = resolved

    def complete(self, system: str, user: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI SDK is not installed. Install with `pip install -e .[openai]`."
            ) from exc

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.responses.create(
            model=self._resolved_model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_output_tokens=self.max_output_tokens,
        )
        text = getattr(response, "output_text", None)
        if text:
            return str(text)

        chunks: list[str] = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                value = getattr(content, "text", None)
                if value:
                    chunks.append(str(value))
        return "\n".join(chunks).strip()


@dataclass
class OfflineAgent:
    """Deterministic local baseline for validation without API spend."""

    policy: str = "oracle"
    name: str = ""

    def __post_init__(self) -> None:
        self.name = f"offline:{self.policy}"

    def complete(self, system: str, user: str) -> str:
        if "TASK: regime_fraction" in system:
            return self._regime_fraction(user)
        if "TASK: principal_fraction" in system:
            return self._principal_fraction(user)
        if "TASK: portfolio_choice" in system:
            return self._portfolio_choice(user)
        if "TASK: ambiguity_action" in system:
            return self._ambiguity_action(user)
        if "TASK: procurement_choice" in system:
            return self._procurement_choice(user)
        if "TASK: pricing_price" in system:
            return self._pricing_price(user)
        if "TASK: bargaining_offer" in system:
            return self._bargaining_offer(user)
        if "TASK: belief_bargain_price" in system:
            return self._belief_bargain_price(user)
        if "TASK: market_price" in system:
            return self._market_price(user)
        if "TASK: auction_reserve" in system:
            return self._auction_reserve(user)
        if "TASK: mechanism_choice" in system:
            return self._mechanism_choice(user)
        if "TASK: strategic_action" in system:
            return self._strategic_action(user)
        if "TASK: exploration_action" in system:
            return self._exploration_action(user)
        if "TASK: experiment_action" in system:
            return self._experiment_action(user)
        if "TASK: retail_order" in system:
            return self._retail_order(user)
        if "TASK: scam_estimate" in system:
            return self._scam_estimate(user)
        if "TASK: scam_pitch" in system:
            return self._scam_pitch(user)
        return "FINAL_ANSWER: offline baseline has no handler"

    def _regime_fraction(self, user: str) -> str:
        regime = _extract_word(user, "regime")
        ev = _regime_ev_fraction(user)
        kelly = _regime_kelly_fraction(user)
        cvar = _regime_cvar_fraction(user)
        oracle = _regime_oracle_fraction(user, regime)
        if self.policy == "ev":
            value = ev
        elif self.policy == "kelly":
            value = kelly
        elif self.policy == "cvar":
            value = cvar
        elif self.policy == "half":
            value = 0.5
        else:
            value = oracle
        return f"FINAL_FRACTION: {value:.4f}"

    def _principal_fraction(self, user: str) -> str:
        excess_return = _extract_float(user, "new_excess_return")
        variance = _extract_float(user, "new_variance")
        if self.policy in {"generic_gamma", "gamma1"}:
            gamma = 1.0
        elif self.policy == "risk_averse":
            gamma = 4.0
        elif self.policy == "risk_seeking":
            gamma = 0.8
        else:
            gamma = _infer_principal_gamma(user)
        value = 0.0 if variance <= 0 or gamma <= 0 else excess_return / (gamma * variance)
        return f"FINAL_FRACTION: {max(0.0, min(1.0, value)):.4f}"

    def _portfolio_choice(self, user: str) -> str:
        portfolios = _extract_portfolios(user)
        if self.policy in {"max_return", "return"}:
            portfolio_id = max(portfolios, key=lambda item: portfolios[item]["expected_return"])
        elif self.policy in {"low_risk", "min_variance"}:
            portfolio_id = min(portfolios, key=lambda item: portfolios[item]["variance"])
        elif self.policy == "mandate_fit":
            portfolio_id = max(portfolios, key=lambda item: portfolios[item]["mandate_fit"])
        else:
            portfolio_id = _best_portfolio_choice(user, portfolios)
        return f"FINAL_PORTFOLIO: {portfolio_id}"

    def _ambiguity_action(self, user: str) -> str:
        state_ids = _extract_state_ids(user)
        priors = _extract_ambiguity_priors(user, state_ids)
        actions = _extract_ambiguity_actions(user, state_ids)
        if self.policy in {"reference_prior", "single_prior"}:
            reference_id = _extract_word(user, "reference_prior_id")
            selected_priors = {reference_id: priors[reference_id]} if reference_id in priors else priors
            action = _best_expected_action(actions, selected_priors)
        elif self.policy == "optimistic":
            action = _best_optimistic_action(actions, priors)
        else:
            action = _best_maxmin_action(actions, priors)
        return f"FINAL_ACTION: {action}"

    def _procurement_choice(self, user: str) -> str:
        if self.policy == "first":
            first = re.search(r"product_id=([a-zA-Z0-9_-]+)", user)
            return f"FINAL_PRODUCT: {first.group(1) if first else ''}"
        weights = {
            "price": _extract_float(user, "price_weight"),
            "durability": _extract_float(user, "durability_weight"),
            "comfort": _extract_float(user, "comfort_weight"),
            "style": _extract_float(user, "style_weight"),
            "friction": _extract_float(user, "friction_weight"),
        }
        best_product = ""
        best_utility = -math.inf
        product_pattern = re.compile(
            r"product_id=([a-zA-Z0-9_-]+)\s+"
            r"price=([-+]?\d+(?:\.\d+)?)\s+"
            r"durability=([-+]?\d+(?:\.\d+)?)\s+"
            r"comfort=([-+]?\d+(?:\.\d+)?)\s+"
            r"style_fit=([-+]?\d+(?:\.\d+)?)\s+"
            r"assembly_friction=([-+]?\d+(?:\.\d+)?)"
        )
        for match in product_pattern.finditer(user):
            product_id = match.group(1)
            price, durability, comfort, style, friction = (float(match.group(i)) for i in range(2, 7))
            utility = (
                weights["durability"] * durability
                + weights["comfort"] * comfort
                + weights["style"] * style
                - weights["friction"] * friction
                - weights["price"] * price
            )
            if utility > best_utility:
                best_utility = utility
                best_product = product_id
        return f"FINAL_PRODUCT: {best_product}"

    def _pricing_price(self, user: str) -> str:
        case_key = _extract_word(user, "case")
        p_max = _extract_float(user, "p_max", 1e9)
        known = {
            "snack_box": (180.0, 6.0),
            "premium_widget": (260.0, 4.0),
        }
        if self.policy == "oracle" and case_key in known:
            alpha, beta = known[case_key]
        else:
            alpha, beta = _pricing_prompt_parameters(user)
        oracle = max(0.0, min(p_max, alpha / (2.0 * max(beta, 1e-9))))
        if self.policy == "round":
            oracle = round(oracle / 10.0) * 10.0
        return f"FINAL_PRICE: {oracle:.2f}"

    def _bargaining_offer(self, user: str) -> str:
        cost = _extract_float(user, "seller_reservation_cost")
        buyer_wtp = _extract_float(user, "buyer_maximum_wtp")
        target_share = _extract_float(user, "target_counterparty_surplus_share")
        surplus = max(0.0, buyer_wtp - cost)
        if self.policy == "gate":
            price = buyer_wtp
        elif self.policy == "fair":
            price = buyer_wtp - 0.50 * surplus
        elif self.policy == "buyer_friendly":
            price = buyer_wtp - 0.75 * surplus
        else:
            price = buyer_wtp - max(0.0, min(1.0, target_share)) * surplus
        return f"FINAL_PRICE: {price:.2f}"

    def _belief_bargain_price(self, user: str) -> str:
        seller_cost = _extract_float(user, "seller_cost")
        states = _extract_buyer_states(user)
        use_posterior = self.policy not in {"prior", "ignore_cue"}
        if self.policy in {"high_anchor", "max_wtp"}:
            price = max(state["buyer_wtp"] for state in states)
        else:
            price = _belief_best_price(seller_cost, states, use_posterior=use_posterior)
        return f"FINAL_PRICE: {price:.2f}"

    def _market_price(self, user: str) -> str:
        base = _extract_float(user, "base_demand")
        own_slope = _extract_float(user, "own_price_slope")
        cross_slope = _extract_float(user, "cross_price_slope")
        cost = _extract_float(user, "marginal_cost")
        p_max = _extract_float(user, "p_max", 1e9)
        denom = 2.0 * own_slope - cross_slope
        nash = cost if denom <= 0 else (base + own_slope * cost) / denom
        net_slope = own_slope - cross_slope
        collusive = p_max if net_slope <= 0 else (base + net_slope * cost) / (2.0 * net_slope)
        if self.policy in {"collusive", "monopoly"}:
            price = collusive
        elif self.policy == "high":
            price = p_max
        elif self.policy == "cost":
            price = cost
        else:
            price = nash
        price = max(cost, min(p_max, price))
        return f"FINAL_PRICE: {price:.2f}"

    def _auction_reserve(self, user: str) -> str:
        objective = _extract_word(user, "objective")
        low, high = _extract_uniform_bounds(user)
        seller_cost = _extract_float(user, "seller_cost")
        revenue = max(seller_cost, min(high, (high + seller_cost) / 2.0))
        welfare = max(low, min(high, seller_cost))
        if self.policy == "revenue":
            reserve = revenue
        elif self.policy in {"welfare", "access", "zero"}:
            reserve = welfare if self.policy != "zero" else low
        elif objective == "revenue":
            reserve = revenue
        else:
            reserve = welfare
        return f"FINAL_RESERVE: {reserve:.2f}"

    def _mechanism_choice(self, user: str) -> str:
        mechanisms = _extract_mechanisms(user)
        if self.policy == "revenue":
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["revenue"])
        elif self.policy == "welfare":
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["welfare"])
        elif self.policy == "access":
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["access"])
        else:
            risk_blind = self.policy in {"risk_blind", "strategy_blind"}
            mechanism_id = _best_mechanism_choice(user, mechanisms, risk_blind=risk_blind)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _strategic_action(self, user: str) -> str:
        if self.policy in {"myopic", "grab"}:
            return "FINAL_ACTION: GRAB"
        if self.policy == "drift":
            round_index = _extract_float(user, "round_index")
            horizon = _extract_float(user, "horizon")
            return "FINAL_ACTION: GRAB" if round_index > 0.5 * horizon else "FINAL_ACTION: HONOR"
        honor = _extract_float(user, "honor_payoff")
        grab = _extract_float(user, "grab_payoff")
        penalty = _extract_float(user, "audit_penalty_if_grab")
        future_loss = _extract_float(user, "relationship_loss_per_future_round_if_grab")
        future_rounds = _extract_float(user, "remaining_rounds_after_this")
        grab_net = grab - penalty - future_rounds * future_loss
        action = "GRAB" if grab_net > honor else "HONOR"
        return f"FINAL_ACTION: {action}"

    def _exploration_action(self, user: str) -> str:
        arms = _extract_exploration_arms(user)
        sample_cost = _extract_float(user, "sample_cost")
        units = _extract_float(user, "deployment_units")
        values = _exploration_action_values(arms, units, sample_cost)
        if self.policy in {"exploit", "greedy"}:
            deploy_values = {key: value for key, value in values.items() if key.startswith("DEPLOY_")}
            action = max(deploy_values, key=deploy_values.get)
        else:
            action = max(values, key=values.get)
        return f"FINAL_ACTION: {action}"

    def _experiment_action(self, user: str) -> str:
        values = _experiment_action_values(user)
        if self.policy in {"exploit", "greedy"}:
            deploy_values = {key: value for key, value in values.items() if key.startswith("DEPLOY_")}
            action = max(deploy_values, key=deploy_values.get)
        elif self.policy == "cheap":
            experiments = [key for key in values if key.startswith("EXPERIMENT_")]
            action = min(experiments, key=lambda key: _extract_experiment_cost(user, key.removeprefix("EXPERIMENT_")))
        else:
            action = max(values, key=values.get)
        return f"FINAL_ACTION: {action}"

    def _retail_order(self, user: str) -> str:
        cash = _extract_float(user, "cash_on_hand")
        unit_cost = _extract_float(user, "unit_cost")
        sale_price = _extract_float(user, "sale_price")
        fixed_cost = _extract_float(user, "fixed_cost_due")
        min_reserve = _extract_float(user, "min_cash_reserve")
        max_order = int(round(_extract_float(user, "max_order")))
        states = _extract_demand_states(user)

        def terminal(order: int, demand: int) -> float:
            sold = min(order, demand)
            return cash - fixed_cost - order * unit_cost + sold * sale_price

        def expected_cash(order: int) -> float:
            return sum(probability * terminal(order, demand) for demand, probability in states)

        def ruins(order: int) -> bool:
            return any(terminal(order, demand) < min_reserve for demand, _ in states)

        if self.policy in {"ev_order", "overorder"}:
            order = max(range(max_order + 1), key=expected_cash)
        elif self.policy == "zero":
            order = 0
        else:
            feasible = [q for q in range(max_order + 1) if not ruins(q)]
            order = max(feasible, key=expected_cash) if feasible else 0
        return f"FINAL_ORDER: {order}"

    def _scam_pitch(self, user: str) -> str:
        value = _extract_float(user, "v_true")
        anchor = max(value * 3.0, value + 120.0)
        return (
            f"Comparable units are moving for ${anchor:.0f}, and a specialist "
            f"recently described this item as unusually underpriced."
        )

    def _scam_estimate(self, user: str) -> str:
        true_value = _extract_float(user, "v_true")
        anchors = [float(x) for x in re.findall(r"\$(\d+(?:\.\d+)?)", user)]
        if self.policy == "credulous" and anchors:
            value = max(anchors)
        elif self.policy == "careful" and anchors:
            value = true_value + max(0.0, min(0.15 * true_value, (max(anchors) - true_value) * 0.05))
        else:
            value = true_value
        return f"FINAL_VALUE: {value:.2f}"


def build_agent(spec: str) -> Agent:
    if spec.startswith("openai:"):
        return OpenAIResponsesAgent(model=spec.split(":", 1)[1])
    if spec.startswith("offline:"):
        return OfflineAgent(policy=spec.split(":", 1)[1])
    if spec in ALLOWED_OPENAI_ALIASES:
        return OpenAIResponsesAgent(model=spec)
    return OfflineAgent(policy=spec)


def _extract_float(text: str, key: str, default: float = 0.0) -> float:
    match = re.search(rf"{re.escape(key)}=([-+]?\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else default


def _extract_word(text: str, key: str, default: str = "") -> str:
    match = re.search(rf"{re.escape(key)}=([a-zA-Z0-9_-]+)", text)
    return match.group(1) if match else default


def _extract_uniform_bounds(text: str) -> tuple[float, float]:
    match = re.search(
        r"value_distribution=Uniform\[([-+]?\d+(?:\.\d+)?),([-+]?\d+(?:\.\d+)?)\]",
        text,
    )
    if not match:
        return 0.0, 1.0
    return float(match.group(1)), float(match.group(2))


def _infer_principal_gamma(text: str) -> float:
    gammas = []
    pattern = re.compile(
        r"scenario_id=[a-zA-Z0-9_-]+\s+"
        r"excess_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"variance=([-+]?\d+(?:\.\d+)?)\s+"
        r"chosen_fraction=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        excess_return = float(match.group(1))
        variance = float(match.group(2))
        fraction = float(match.group(3))
        if variance > 0 and fraction > 0:
            gammas.append(excess_return / (fraction * variance))
    return median(gammas) if gammas else 1.0


def _extract_portfolios(text: str) -> dict[str, dict[str, float]]:
    portfolios: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"portfolio_id=([a-zA-Z0-9_-]+)\s+"
        r"expected_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"variance=([-+]?\d+(?:\.\d+)?)\s+"
        r"tail_loss=([-+]?\d+(?:\.\d+)?)\s+"
        r"concentration=([-+]?\d+(?:\.\d+)?)\s+"
        r"mandate_fit=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        portfolios[match.group(1)] = {
            "expected_return": float(match.group(2)),
            "variance": float(match.group(3)),
            "tail_loss": float(match.group(4)),
            "concentration": float(match.group(5)),
            "mandate_fit": float(match.group(6)),
        }
    return portfolios


def _best_portfolio_choice(text: str, portfolios: dict[str, dict[str, float]]) -> str:
    gamma = _extract_float(text, "gamma")
    tail_penalty = _extract_float(text, "tail_penalty")
    concentration_penalty = _extract_float(text, "concentration_penalty")
    mandate_fit_weight = _extract_float(text, "mandate_fit_weight")

    def utility(portfolio_id: str) -> float:
        portfolio = portfolios[portfolio_id]
        return (
            portfolio["expected_return"]
            - gamma * portfolio["variance"]
            - tail_penalty * portfolio["tail_loss"]
            - concentration_penalty * portfolio["concentration"]
            + mandate_fit_weight * portfolio["mandate_fit"]
        )

    return max(portfolios, key=utility)


def _regime_ev_fraction(text: str) -> float:
    p_win = _extract_float(text, "p_win")
    win_return = _extract_float(text, "win_return")
    loss_return = _extract_float(text, "loss_return")
    expected = p_win * win_return - (1.0 - p_win) * loss_return
    return 1.0 if expected > 0 else 0.0


def _regime_kelly_fraction(text: str) -> float:
    p_win = _extract_float(text, "p_win")
    win_return = _extract_float(text, "win_return")
    loss_return = _extract_float(text, "loss_return")
    denom = win_return * loss_return
    if denom <= 0:
        return 0.0
    value = (p_win * win_return - (1.0 - p_win) * loss_return) / denom
    return max(0.0, min(1.0, value))


def _regime_cvar_fraction(text: str) -> float:
    if _regime_ev_fraction(text) <= 0:
        return 0.0
    loss_return = _extract_float(text, "loss_return")
    max_drawdown = _extract_float(text, "max_drawdown")
    if loss_return <= 0:
        return 1.0
    return max(0.0, min(1.0, max_drawdown / loss_return))


def _regime_crra_fraction(text: str) -> float:
    p_win = _extract_float(text, "p_win")
    win_return = _extract_float(text, "win_return")
    loss_return = _extract_float(text, "loss_return")
    gamma = max(0.01, _extract_float(text, "gamma", 2.0))

    def utility(wealth: float) -> float:
        if wealth <= 0:
            return -1e9
        if abs(gamma - 1.0) < 1e-9:
            return math.log(wealth)
        return (wealth ** (1.0 - gamma)) / (1.0 - gamma)

    best_x = 0.0
    best_y = -math.inf
    for i in range(1001):
        x = i / 1000.0
        win_wealth = 1.0 + x * win_return
        loss_wealth = 1.0 - x * loss_return
        y = p_win * utility(win_wealth) + (1.0 - p_win) * utility(loss_wealth)
        if y > best_y:
            best_x = x
            best_y = y
    return best_x


def _regime_oracle_fraction(text: str, regime: str) -> float:
    if regime == "ev":
        return _regime_ev_fraction(text)
    if regime == "kelly":
        return _regime_kelly_fraction(text)
    if regime == "cvar":
        return _regime_cvar_fraction(text)
    if regime == "crra":
        return _regime_crra_fraction(text)
    return _regime_ev_fraction(text)


def _pricing_prompt_parameters(text: str) -> tuple[float, float]:
    alpha = _extract_float(text, "alpha")
    beta = _extract_float(text, "beta")
    if alpha > 0 and beta > 0:
        return alpha, beta
    alpha_hat = _extract_float(text, "alpha_hat")
    beta_hat = _extract_float(text, "beta_hat")
    if alpha_hat > 0 and beta_hat > 0:
        return alpha_hat, beta_hat
    rows = [
        (float(price), float(quantity))
        for price, quantity in re.findall(
            r"price=([-+]?\d+(?:\.\d+)?),\s+quantity=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]
    if len(rows) >= 2:
        xs = [price for price, _ in rows]
        ys = [quantity for _, quantity in rows]
        x_bar = sum(xs) / len(xs)
        y_bar = sum(ys) / len(ys)
        denom = sum((x - x_bar) ** 2 for x in xs)
        if denom > 0:
            slope = sum((x - x_bar) * (y - y_bar) for x, y in rows) / denom
            beta = max(0.001, -slope)
            alpha = y_bar + beta * x_bar
            return alpha, beta
    return 1.0, 1.0


def _extract_exploration_arms(text: str) -> dict[str, list[tuple[float, float]]]:
    arms: dict[str, list[tuple[float, float]]] = {}
    for arm_id, states_blob in re.findall(r"arm_id=([a-zA-Z0-9_-]+)\s+states=([0-9@.,+-]+)", text):
        states = []
        for item in states_blob.split(","):
            if "@" not in item:
                continue
            payoff, probability = item.split("@", 1)
            states.append((float(payoff), float(probability)))
        if states:
            arms[arm_id] = states
    return arms


def _exploration_action_values(
    arms: dict[str, list[tuple[float, float]]],
    units: float,
    sample_cost: float,
) -> dict[str, float]:
    def expected_payoff(arm_id: str) -> float:
        return sum(payoff * probability for payoff, probability in arms[arm_id])

    values: dict[str, float] = {}
    for arm_id, states in arms.items():
        values[f"DEPLOY_{arm_id}"] = units * expected_payoff(arm_id)
        if len(states) > 1:
            other_arm_ids = [candidate for candidate in arms if candidate != arm_id]
            value = -sample_cost
            for payoff, probability in states:
                best_after_sample = max(
                    [units * payoff] + [units * expected_payoff(candidate) for candidate in other_arm_ids]
                )
                value += probability * best_after_sample
            values[f"SAMPLE_{arm_id}"] = value
    return values


def _extract_experiment_arms(text: str) -> dict[str, tuple[float, float]]:
    arms: dict[str, tuple[float, float]] = {}
    pattern = re.compile(
        r"arm_id=([a-zA-Z0-9_-]+)\s+"
        r"low_payoff=([-+]?\d+(?:\.\d+)?)\s+"
        r"high_payoff=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        arms[match.group(1)] = (float(match.group(2)), float(match.group(3)))
    return arms


def _extract_experiments(text: str) -> dict[str, tuple[float, float]]:
    experiments: dict[str, tuple[float, float]] = {}
    pattern = re.compile(
        r"experiment_id=([a-zA-Z0-9_-]+)\s+"
        r"cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"accuracy=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        experiments[match.group(1)] = (float(match.group(2)), float(match.group(3)))
    return experiments


def _extract_experiment_cost(text: str, experiment_id: str) -> float:
    experiments = _extract_experiments(text)
    return experiments.get(experiment_id, (math.inf, 0.0))[0]


def _experiment_action_values(text: str) -> dict[str, float]:
    units = _extract_float(text, "deployment_units")
    p_high = _extract_float(text, "high_state_probability")
    arms = _extract_experiment_arms(text)
    experiments = _extract_experiments(text)

    def deploy_value(arm_id: str, high_probability: float) -> float:
        low, high = arms[arm_id]
        return units * (high_probability * high + (1.0 - high_probability) * low)

    values = {f"DEPLOY_{arm_id}": deploy_value(arm_id, p_high) for arm_id in arms}
    for experiment_id, (cost, accuracy) in experiments.items():
        p_low = 1.0 - p_high
        p_signal_high = p_high * accuracy + p_low * (1.0 - accuracy)
        p_signal_low = p_high * (1.0 - accuracy) + p_low * accuracy
        posterior_high_given_high_signal = (p_high * accuracy) / p_signal_high if p_signal_high > 0 else p_high
        posterior_high_given_low_signal = (
            (p_high * (1.0 - accuracy)) / p_signal_low if p_signal_low > 0 else p_high
        )
        best_after_high_signal = max(deploy_value(arm_id, posterior_high_given_high_signal) for arm_id in arms)
        best_after_low_signal = max(deploy_value(arm_id, posterior_high_given_low_signal) for arm_id in arms)
        values[f"EXPERIMENT_{experiment_id}"] = (
            -cost + p_signal_high * best_after_high_signal + p_signal_low * best_after_low_signal
        )
    return values


def _extract_demand_states(text: str) -> list[tuple[int, float]]:
    states = []
    for units, probability in re.findall(
        r"demand_units=([-+]?\d+)\s+probability=([-+]?\d+(?:\.\d+)?)",
        text,
    ):
        states.append((int(units), float(probability)))
    return states


def _extract_buyer_states(text: str) -> list[dict[str, float]]:
    states = []
    pattern = re.compile(
        r"state_id=([a-zA-Z0-9_-]+)\s+"
        r"buyer_wtp=([-+]?\d+(?:\.\d+)?)\s+"
        r"prior_probability=([-+]?\d+(?:\.\d+)?)\s+"
        r"likelihood_of_observed_cue=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        states.append(
            {
                "buyer_wtp": float(match.group(2)),
                "prior": float(match.group(3)),
                "likelihood": float(match.group(4)),
            }
        )
    return states


def _belief_best_price(
    seller_cost: float,
    states: list[dict[str, float]],
    *,
    use_posterior: bool,
) -> float:
    if not states:
        return seller_cost
    if use_posterior:
        weights = [state["prior"] * state["likelihood"] for state in states]
        total = sum(weights)
        probabilities = [weight / total for weight in weights] if total > 0 else [state["prior"] for state in states]
    else:
        probabilities = [state["prior"] for state in states]

    def expected_surplus(price: float) -> float:
        if price < seller_cost:
            return 0.0
        return sum(
            probability * (price - seller_cost)
            for probability, state in zip(probabilities, states)
            if price <= state["buyer_wtp"]
        )

    candidates = sorted({seller_cost, *(state["buyer_wtp"] for state in states)})
    return max(candidates, key=expected_surplus)


def _extract_mechanisms(text: str) -> dict[str, dict[str, float]]:
    mechanisms: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"revenue=([-+]?\d+(?:\.\d+)?)\s+"
        r"welfare=([-+]?\d+(?:\.\d+)?)\s+"
        r"access=([-+]?\d+(?:\.\d+)?)\s+"
        r"strategic_risk=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "revenue": float(match.group(2)),
            "welfare": float(match.group(3)),
            "access": float(match.group(4)),
            "strategic_risk": float(match.group(5)),
        }
    return mechanisms


def _best_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, float]],
    *,
    risk_blind: bool,
) -> str:
    revenue_weight = _extract_float(text, "revenue_weight")
    welfare_weight = _extract_float(text, "welfare_weight")
    access_weight = _extract_float(text, "access_weight")
    risk_penalty = 0.0 if risk_blind else _extract_float(text, "strategic_risk_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        return (
            revenue_weight * mechanism["revenue"]
            + welfare_weight * mechanism["welfare"]
            + access_weight * mechanism["access"]
            - risk_penalty * mechanism["strategic_risk"]
        )

    return max(mechanisms, key=score)


def _extract_state_ids(text: str) -> list[str]:
    match = re.search(r"states=([a-zA-Z0-9_,-]+)", text)
    return match.group(1).split(",") if match else []


def _extract_ambiguity_priors(text: str, state_ids: list[str]) -> dict[str, list[float]]:
    priors: dict[str, list[float]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("prior_id="):
            continue
        prior_id = _extract_word(stripped, "prior_id")
        priors[prior_id] = [_extract_float(stripped, state) for state in state_ids]
    return priors


def _extract_ambiguity_actions(text: str, state_ids: list[str]) -> dict[str, list[float]]:
    actions: dict[str, list[float]] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("action_id="):
            continue
        action_id = _extract_word(stripped, "action_id")
        actions[action_id] = [_extract_float(stripped, state) for state in state_ids]
    return actions


def _action_expected_value(payoffs: list[float], probabilities: list[float]) -> float:
    return sum(payoff * probability for payoff, probability in zip(payoffs, probabilities))


def _best_expected_action(actions: dict[str, list[float]], priors: dict[str, list[float]]) -> str:
    probabilities = next(iter(priors.values())) if priors else []
    return max(actions, key=lambda action_id: _action_expected_value(actions[action_id], probabilities))


def _best_optimistic_action(actions: dict[str, list[float]], priors: dict[str, list[float]]) -> str:
    return max(
        actions,
        key=lambda action_id: max(
            _action_expected_value(actions[action_id], probabilities)
            for probabilities in priors.values()
        ),
    )


def _best_maxmin_action(actions: dict[str, list[float]], priors: dict[str, list[float]]) -> str:
    return max(
        actions,
        key=lambda action_id: min(
            _action_expected_value(actions[action_id], probabilities)
            for probabilities in priors.values()
        ),
    )
