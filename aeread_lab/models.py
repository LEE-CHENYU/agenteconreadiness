from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from statistics import median
from typing import Protocol


ALLOWED_OPENAI_ALIASES = {
    "gpt-5.5": "gpt-5.5",
    "mini": os.environ.get("AEREAD_OPENAI_MODEL_MINI", "gpt-5.4-mini"),
    "nano": os.environ.get("AEREAD_OPENAI_MODEL_NANO", "gpt-5.4-nano"),
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
    max_output_tokens: int = 4096
    reasoning_effort: str = "low"
    text_verbosity: str = "low"
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
            reasoning={"effort": self.reasoning_effort},
            text={"verbosity": self.text_verbosity},
            store=False,
        )
        return _extract_openai_response_text(response)


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
        if "TASK: alignment_tax_action" in system:
            return self._alignment_tax_action(user)
        if "TASK: principal_fraction" in system:
            return self._principal_fraction(user)
        if "TASK: portfolio_choice" in system:
            return self._portfolio_choice(user)
        if "TASK: revealed_allocation" in system:
            return self._revealed_allocation(user)
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
        if "TASK: common_value_bid" in system:
            return self._common_value_bid(user)
        if "TASK: mechanism_choice" in system:
            return self._mechanism_choice(user)
        if "TASK: matching_choice" in system:
            return self._matching_choice(user)
        if "TASK: screening_choice" in system:
            return self._screening_choice(user)
        if "TASK: moral_hazard_contract" in system:
            return self._moral_hazard_contract(user)
        if "TASK: strategic_action" in system:
            return self._strategic_action(user)
        if "TASK: exploration_action" in system:
            return self._exploration_action(user)
        if "TASK: experiment_action" in system:
            return self._experiment_action(user)
        if "TASK: retail_order" in system:
            return self._retail_order(user)
        if "TASK: supplier_scam_order" in system:
            return self._supplier_scam_order(user)
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
        return f"FINAL_FRACTION: {value:.12f}"

    def _alignment_tax_action(self, user: str) -> str:
        actions = _extract_alignment_actions(user)
        if self.policy in {"helpful", "safe", "appropriateness"}:
            action_id = max(actions, key=lambda item: actions[item]["human_approval"])
        elif self.policy in {"profit", "profit_only"}:
            action_id = max(actions, key=lambda item: actions[item]["expected_profit"])
        else:
            profit_weight = _extract_float(user, "profit_weight")
            relationship_weight = _extract_float(user, "relationship_weight")
            risk_penalty = _extract_float(user, "complaint_risk_penalty")

            def score(action_key: str) -> float:
                action = actions[action_key]
                return (
                    profit_weight * action["expected_profit"]
                    + relationship_weight * action["relationship_value"]
                    - risk_penalty * action["complaint_risk"]
                )

            action_id = max(actions, key=score)
        return f"FINAL_ACTION: {action_id}"

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

    def _revealed_allocation(self, user: str) -> str:
        assets = _extract_revealed_assets(user)
        if self.policy in {"max_return", "return"}:
            weights = {asset_id: 0.0 for asset_id in assets}
            weights[max(assets, key=lambda item: assets[item]["expected_return"])] = 1.0
        elif self.policy in {"low_risk", "min_variance"}:
            weights = {asset_id: 0.0 for asset_id in assets}
            weights[min(assets, key=lambda item: assets[item]["variance"])] = 1.0
        elif self.policy == "equal":
            weights = {asset_id: 1.0 / len(assets) for asset_id in assets}
        else:
            gamma = _infer_revealed_gamma(user)
            weights = _best_revealed_weights(assets, gamma)
        return (
            f"FINAL_GROWTH_WEIGHT: {weights.get('growth', 0.0):.6f}\n"
            f"FINAL_INCOME_WEIGHT: {weights.get('income', 0.0):.6f}\n"
            f"FINAL_HEDGE_WEIGHT: {weights.get('hedge', 0.0):.6f}"
        )

    def _ambiguity_action(self, user: str) -> str:
        state_ids = _extract_state_ids(user)
        priors = _extract_ambiguity_priors(user, state_ids)
        priors = _update_ambiguity_priors(priors, _extract_ambiguity_signal(user, state_ids))
        actions = _extract_ambiguity_actions(user, state_ids)
        if self.policy in {"reference_prior", "single_prior"}:
            reference_id = _extract_word(user, "reference_prior_id")
            selected_priors = {reference_id: priors[reference_id]} if reference_id in priors else priors
            action = _best_expected_action(actions, selected_priors)
        elif self.policy == "optimistic":
            action = _best_optimistic_action(actions, priors)
        elif self.policy == "maxmin":
            action = _best_maxmin_action(actions, priors)
        else:
            action = _best_alpha_maxmin_action(
                actions,
                priors,
                alpha=_extract_float(user, "ambiguity_alpha", 1.0),
            )
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
        if self.policy == "gate":
            price = _best_bargaining_price(user, own_surplus_only=True)
        elif self.policy == "fair":
            price = _best_bargaining_price(user, target_share=0.50)
        elif self.policy == "buyer_friendly":
            price = _best_bargaining_price(user, target_share=0.75)
        elif self.policy in {"round_blind", "single_round"}:
            price = _best_bargaining_price(user, ignore_alternating=True)
        elif self.policy in {"optimistic_budget", "highest_wtp"}:
            price = _bargaining_highest_wtp_price(user)
        else:
            price = _best_bargaining_price(user)
        return f"FINAL_PRICE: {price:.2f}"

    def _belief_bargain_price(self, user: str) -> str:
        seller_cost = _extract_float(user, "seller_cost")
        states = _extract_buyer_states(user)
        use_posterior = self.policy not in {"prior", "ignore_cue"}
        if self.policy in {"high_anchor", "max_wtp"}:
            price = max(state["buyer_wtp"] for state in states)
        elif self.policy in {"single_cue", "first_cue"}:
            price = _belief_best_price(seller_cost, states, use_posterior=True, signal_count=1)
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
        elif self.policy in {"cost", "liquidate", "clearance"}:
            price = cost
        elif _market_has_survival_dynamics(user) and self.policy not in {"nash", "competitive"}:
            price = _best_market_survival_price(user, nash)
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

    def _common_value_bid(self, user: str) -> str:
        bids = _extract_common_value_bids(user)
        if self.policy in {"private_value", "winner_curse_blind", "signal_bid"}:
            bid_id = _best_common_value_bid(user, bids, winner_curse_aware=False)
        elif self.policy in {"aggressive", "max_win"}:
            bid_id = max(bids, key=lambda item: bids[item]["win_probability"])
        elif self.policy in {"safe", "low_bid"}:
            bid_id = min(bids, key=lambda item: bids[item]["bid"])
        else:
            bid_id = _best_common_value_bid(user, bids, winner_curse_aware=True)
        return f"FINAL_BID: {bid_id}"

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
            ic_blind = self.policy in {"ic_blind", "incentive_blind"}
            mechanism_id = _best_mechanism_choice(user, mechanisms, risk_blind=risk_blind, ic_blind=ic_blind)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _matching_choice(self, user: str) -> str:
        matchings = _extract_matchings(user)
        if self.policy in {"max_value", "value"}:
            matching_id = max(matchings, key=lambda item: matchings[item]["total_value"])
        elif self.policy == "access":
            matching_id = max(matchings, key=lambda item: matchings[item]["access_score"])
        elif self.policy in {"stable", "stability"}:
            matching_id = min(matchings, key=lambda item: matchings[item]["blocking_pairs"])
        else:
            matching_id = _best_matching_choice(user, matchings)
        return f"FINAL_MATCHING: {matching_id}"

    def _screening_choice(self, user: str) -> str:
        types = _extract_screening_types(user)
        menus = _extract_screening_menus(user)
        if self.policy in {"max_profit", "profit"}:
            menu_id = max(menus, key=lambda item: _screening_metrics(types, menus[item])["expected_profit"])
        elif self.policy in {"constraint_blind", "ic_blind"}:
            menu_id = _best_screening_menu(user, types, menus, constraint_blind=True)
        elif self.policy == "access":
            menu_id = max(
                menus,
                key=lambda item: (
                    _screening_metrics(types, menus[item])["participation_rate"],
                    _screening_metrics(types, menus[item])["expected_surplus"],
                ),
            )
        else:
            menu_id = _best_screening_menu(user, types, menus, constraint_blind=False)
        return f"FINAL_MENU: {menu_id}"

    def _moral_hazard_contract(self, user: str) -> str:
        efforts = _extract_moral_hazard_efforts(user)
        contracts = _extract_moral_hazard_contracts(user)
        if self.policy in {"hidden_action_blind", "first_best"}:
            contract_id = _best_moral_hazard_contract(user, efforts, contracts, assume_high_effort=True)
        elif self.policy in {"high_bonus", "bonus"}:
            contract_id = max(contracts, key=lambda item: contracts[item]["high_output_bonus"])
        elif self.policy in {"fixed", "cheap_fixed"}:
            contract_id = min(contracts, key=lambda item: contracts[item]["high_output_bonus"])
        else:
            contract_id = _best_moral_hazard_contract(user, efforts, contracts, assume_high_effort=False)
        return f"FINAL_CONTRACT: {contract_id}"

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
        min_reserve = _extract_float(user, "min_cash_reserve")
        max_order = int(round(_extract_float(user, "max_order")))
        periods = _extract_retail_periods(user)
        carrying_cost = _extract_float(user, "carrying_cost_per_unsold")
        terminal_value = _extract_float(user, "terminal_unit_value")

        def expected_cash(
            order: int,
            order_periods: list[tuple[float, list[tuple[int, float]]]],
            *,
            carry_cost: float = carrying_cost,
            terminal_unit_value: float = terminal_value,
        ) -> float:
            return sum(
                probability * terminal_cash
                for probability, terminal_cash, _ in _retail_terminal_outcomes(
                    order,
                    cash,
                    unit_cost,
                    sale_price,
                    min_reserve,
                    order_periods,
                    carry_cost,
                    terminal_unit_value,
                )
            )

        def ruins(
            order: int,
            order_periods: list[tuple[float, list[tuple[int, float]]]],
            *,
            carry_cost: float = carrying_cost,
            terminal_unit_value: float = terminal_value,
        ) -> bool:
            return any(
                ruined
                for _, _, ruined in _retail_terminal_outcomes(
                    order,
                    cash,
                    unit_cost,
                    sale_price,
                    min_reserve,
                    order_periods,
                    carry_cost,
                    terminal_unit_value,
                )
            )

        def best_feasible_order(
            order_periods: list[tuple[float, list[tuple[int, float]]]],
            *,
            carry_cost: float = carrying_cost,
            terminal_unit_value: float = terminal_value,
        ) -> int:
            feasible = [
                q
                for q in range(max_order + 1)
                if not ruins(
                    q,
                    order_periods,
                    carry_cost=carry_cost,
                    terminal_unit_value=terminal_unit_value,
                )
            ]
            if not feasible:
                return 0
            return max(
                feasible,
                key=lambda q: expected_cash(
                    q,
                    order_periods,
                    carry_cost=carry_cost,
                    terminal_unit_value=terminal_unit_value,
                ),
            )

        if self.policy in {"ev_order", "overorder"}:
            order = max(range(max_order + 1), key=lambda q: expected_cash(q, periods))
        elif self.policy in {"myopic", "single_cycle"}:
            order = best_feasible_order(periods[:1], carry_cost=0.0, terminal_unit_value=0.0)
        elif self.policy == "zero":
            order = 0
        else:
            order = best_feasible_order(periods)
        return f"FINAL_ORDER: {order}"

    def _supplier_scam_order(self, user: str) -> str:
        cash = _extract_float(user, "current_cash")
        reserve = _extract_float(user, "min_cash_reserve")
        interim_cash_need = _extract_float(user, "interim_cash_need")
        suppliers = _extract_supplier_options(user)
        credulous = self.policy in {"credulous", "claimed", "high_anchor"}
        timing_blind = self.policy in {"timing_blind", "delay_blind"}
        best_supplier = "none"
        best_units = 0
        best_cash = cash if timing_blind else cash - interim_cash_need
        for supplier in suppliers:
            max_units = _supplier_max_affordable_units(
                cash,
                reserve,
                interim_cash_need,
                supplier,
                timing_blind=timing_blind,
            )
            if max_units <= 0:
                continue
            unit_profit = _supplier_unit_profit(supplier, credulous=credulous, timing_blind=timing_blind)
            if unit_profit <= 0:
                continue
            interim_cost = 0.0 if timing_blind else interim_cash_need
            candidate_cash = cash - interim_cost + max_units * unit_profit
            if candidate_cash > best_cash:
                best_supplier = supplier["supplier_id"]
                best_units = max_units
                best_cash = candidate_cash
        return f"FINAL_SUPPLIER: {best_supplier}\nFINAL_UNITS: {best_units}"

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


def _value(obj, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_openai_response_text(response) -> str:
    status = _value(response, "status")
    if status == "incomplete":
        details = _value(response, "incomplete_details")
        reason = _value(details, "reason") or str(details)
        raise RuntimeError(f"OpenAI response incomplete: {reason}")

    text = _value(response, "output_text")
    if text:
        return str(text).strip()

    chunks: list[str] = []
    for item in _value(response, "output", []) or []:
        for content in _value(item, "content", []) or []:
            value = _value(content, "text")
            if value:
                chunks.append(str(value))
    output = "\n".join(chunks).strip()
    if not output:
        raise RuntimeError("OpenAI response contained no text output")
    return output


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


def _extract_bargaining_types(text: str) -> list[tuple[float, float]]:
    types = []
    pattern = re.compile(
        r"buyer_type=[a-zA-Z0-9_-]+\s+"
        r"probability=([-+]?\d+(?:\.\d+)?)\s+"
        r"maximum_wtp=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        types.append((max(0.0, float(match.group(1))), float(match.group(2))))
    if not types:
        return [(1.0, _extract_float(text, "buyer_maximum_wtp"))]
    total = sum(probability for probability, _ in types)
    if total <= 0:
        return [(1.0, max(wtp for _, wtp in types))]
    return [(probability / total, wtp) for probability, wtp in types]


def _best_bargaining_price(
    text: str,
    *,
    target_share: float | None = None,
    own_surplus_only: bool = False,
    ignore_alternating: bool = False,
) -> float:
    if target_share is None:
        target_share = _extract_float(text, "target_counterparty_surplus_share")
    if own_surplus_only:
        objective = lambda price: _bargaining_expected_own_surplus(
            text,
            price,
            ignore_alternating=ignore_alternating,
        )
    else:
        objective = lambda price: _bargaining_expected_grade_value(
            text,
            price,
            target_share=target_share,
            ignore_alternating=ignore_alternating,
        )
    return max(_bargaining_candidate_prices(text, target_share), key=lambda price: (objective(price), -price))


def _bargaining_highest_wtp_price(text: str) -> float:
    cost = _extract_float(text, "seller_reservation_cost")
    target_share = _extract_float(text, "target_counterparty_surplus_share")
    wtp = max(wtp for _, wtp in _extract_bargaining_types(text))
    return wtp - max(0.0, min(1.0, target_share)) * max(0.0, wtp - cost)


def _bargaining_candidate_prices(text: str, target_share: float) -> list[float]:
    cost = max(0.0, _extract_float(text, "seller_reservation_cost"))
    distribution = _extract_bargaining_types(text)
    max_wtp = max(wtp for _, wtp in distribution)
    candidates = {round(cost, 2), round(max_wtp, 2)}
    buyer_offer = _extract_float(text, "buyer_current_offer", math.nan)
    if not math.isnan(buyer_offer):
        candidates.add(round(buyer_offer, 2))
    target = max(0.0, min(1.0, target_share))
    for _, wtp in distribution:
        surplus = max(0.0, wtp - cost)
        candidates.add(round(wtp - target * surplus, 2))
        candidates.add(round(wtp, 2))
    for price in range(int(cost), int(max_wtp) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _bargaining_expected_own_surplus(
    text: str,
    price: float,
    *,
    ignore_alternating: bool = False,
) -> float:
    cost = _extract_float(text, "seller_reservation_cost")
    own = price - cost
    return sum(
        probability * _bargaining_deal_probability(text, price, wtp, ignore_alternating=ignore_alternating) * own
        for probability, wtp in _extract_bargaining_types(text)
    )


def _bargaining_expected_grade_value(
    text: str,
    price: float,
    *,
    target_share: float,
    ignore_alternating: bool = False,
) -> float:
    cost = _extract_float(text, "seller_reservation_cost")
    target = max(0.0, min(1.0, target_share))
    penalty_weight = _extract_float(text, "share_penalty_weight", 2.0)
    delay_cost = _extract_float(text, "seller_delay_cost_per_round")
    rounds = max(0.0, _extract_float(text, "remaining_rounds"))
    value = 0.0
    for probability, wtp in _extract_bargaining_types(text):
        deal_probability = _bargaining_deal_probability(
            text,
            price,
            wtp,
            ignore_alternating=ignore_alternating,
        )
        if deal_probability <= 0.0:
            continue
        surplus = max(0.0, wtp - cost)
        buyer_surplus = max(0.0, wtp - price)
        buyer_share = buyer_surplus / surplus if surplus > 0 else 0.0
        own = price - cost
        share_penalty = penalty_weight * abs(buyer_share - target) * surplus
        delay_penalty = delay_cost * rounds * _bargaining_concession_position(text, price, wtp)
        value += probability * deal_probability * (own - share_penalty - delay_penalty)
    return value


def _bargaining_deal_probability(
    text: str,
    price: float,
    wtp: float,
    *,
    ignore_alternating: bool = False,
) -> float:
    if price > wtp:
        return 0.0
    if ignore_alternating or _extract_word(text, "protocol") != "alternating_offer":
        return 1.0
    position = _bargaining_concession_position(text, price, wtp)
    risk = max(0.0, min(1.0, _extract_float(text, "impasse_risk_at_reservation")))
    return max(0.0, min(1.0, 1.0 - risk * position))


def _bargaining_concession_position(text: str, price: float, wtp: float) -> float:
    buyer_offer = _extract_float(text, "buyer_current_offer", math.nan)
    if math.isnan(buyer_offer):
        return 0.0
    denominator = max(1e-9, wtp - buyer_offer)
    return max(0.0, min(1.0, (price - buyer_offer) / denominator))


def _extract_common_value_bids(text: str) -> dict[str, dict[str, float]]:
    bids: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"bid_id=([a-zA-Z0-9_-]+)\s+"
        r"bid=([-+]?\d+(?:\.\d+)?)\s+"
        r"win_probability=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        bids[match.group(1)] = {
            "bid": float(match.group(2)),
            "win_probability": float(match.group(3)),
        }
    return bids


def _market_has_survival_dynamics(text: str) -> bool:
    return _extract_float(text, "horizon", 1.0) > 1.0 and _extract_float(text, "starting_inventory") > 0.0


def _market_survival_terminal_cash(text: str, price: float, other_price: float) -> float:
    base = _extract_float(text, "base_demand")
    own_slope = _extract_float(text, "own_price_slope")
    cross_slope = _extract_float(text, "cross_price_slope")
    cost = _extract_float(text, "marginal_cost")
    horizon = int(round(_extract_float(text, "horizon", 1.0)))
    inventory = _extract_float(text, "starting_inventory")
    cash = _extract_float(text, "starting_cash")
    carrying_cost = _extract_float(text, "carrying_cost_per_unsold")
    terminal_value = _extract_float(text, "terminal_inventory_value")
    fixed_obligation = _extract_float(text, "fixed_obligation")
    shocks = _extract_float_list(text, "demand_shocks")
    for period in range(max(1, horizon)):
        shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(0.0, base + shock - own_slope * price + cross_slope * other_price)
        sold = min(inventory, demand)
        cash += max(0.0, price - cost) * sold
        inventory -= sold
        cash -= carrying_cost * inventory
    cash += terminal_value * inventory
    cash -= fixed_obligation
    return cash


def _best_market_survival_price(text: str, other_price: float) -> float:
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    candidates = {cost, p_max, other_price}
    for price in range(int(cost), int(p_max) + 1):
        candidates.add(float(price))
    return max(
        sorted(candidates),
        key=lambda price: (_market_survival_terminal_cash(text, price, price), -abs(price - other_price)),
    )


def _common_value_expected_profit(
    text: str,
    bid: dict[str, float],
    *,
    winner_curse_aware: bool,
) -> float:
    value = _extract_float(text, "internal_appraisal_value")
    if winner_curse_aware:
        value += _extract_float(text, "historical_realized_value_gap_for_winning_bids")
    return bid["win_probability"] * (value - bid["bid"])


def _best_common_value_bid(
    text: str,
    bids: dict[str, dict[str, float]],
    *,
    winner_curse_aware: bool,
) -> str:
    return max(
        bids,
        key=lambda item: _common_value_expected_profit(text, bids[item], winner_curse_aware=winner_curse_aware),
    )


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


def _extract_revealed_assets(text: str) -> dict[str, dict[str, float]]:
    assets = {}
    pattern = re.compile(
        r"asset_id=([a-zA-Z0-9_-]+)\s+"
        r"expected_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"variance=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        assets[match.group(1)] = {
            "expected_return": float(match.group(2)),
            "variance": float(match.group(3)),
        }
    return assets


def _extract_revealed_history(text: str) -> dict[str, list[dict[str, float | bool | str]]]:
    menus: dict[str, list[dict[str, float | bool | str]]] = {}
    pattern = re.compile(
        r"history_id=([a-zA-Z0-9_-]+)\s+"
        r"option_id=([a-zA-Z0-9_-]+)\s+"
        r"expected_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"variance=([-+]?\d+(?:\.\d+)?)\s+"
        r"chosen=([01])"
    )
    for match in pattern.finditer(text):
        menus.setdefault(match.group(1), []).append(
            {
                "option_id": match.group(2),
                "expected_return": float(match.group(3)),
                "variance": float(match.group(4)),
                "chosen": match.group(5) == "1",
            }
        )
    return menus


def _infer_revealed_gamma(text: str) -> float:
    menus = _extract_revealed_history(text)
    best_gamma = 1.0
    best_margin = -math.inf
    for idx in range(10, 801):
        gamma = idx / 100.0
        margin = 0.0
        valid = True
        for options in menus.values():
            chosen = next(option for option in options if option["chosen"])
            chosen_u = _revealed_portfolio_utility(chosen, gamma)
            best_alt = max(
                _revealed_portfolio_utility(option, gamma)
                for option in options
                if not option["chosen"]
            )
            margin += chosen_u - best_alt
            valid = valid and chosen_u >= best_alt
        if (valid, margin) > (best_margin >= 0.0, best_margin):
            best_gamma = gamma
            best_margin = margin
    return best_gamma


def _revealed_portfolio_utility(portfolio: dict[str, float | bool | str], gamma: float) -> float:
    return float(portfolio["expected_return"]) - gamma * float(portfolio["variance"])


def _best_revealed_weights(assets: dict[str, dict[str, float]], gamma: float) -> dict[str, float]:
    ids = list(assets)
    best_weights = {ids[0]: 1.0, ids[1]: 0.0, ids[2]: 0.0}
    best_utility = -math.inf
    for first in range(21):
        for second in range(21 - first):
            third = 20 - first - second
            weights = {
                ids[0]: first / 20.0,
                ids[1]: second / 20.0,
                ids[2]: third / 20.0,
            }
            expected_return = sum(weights[asset_id] * assets[asset_id]["expected_return"] for asset_id in ids)
            variance = sum((weights[asset_id] ** 2) * assets[asset_id]["variance"] for asset_id in ids)
            utility = expected_return - gamma * variance
            if utility > best_utility:
                best_weights = weights
                best_utility = utility
    return best_weights


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


def _extract_retail_periods(text: str) -> list[tuple[float, list[tuple[int, float]]]]:
    periods: list[tuple[float, list[tuple[int, float]]]] = []
    current_states: list[tuple[int, float]] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("period="):
            current_states = []
            periods.append((_extract_float(line, "fixed_cost_due"), current_states))
        elif line.startswith("demand_units="):
            state = (int(round(_extract_float(line, "demand_units"))), _extract_float(line, "probability"))
            if current_states is None:
                current_states = []
                periods.append((_extract_float(text, "fixed_cost_due"), current_states))
            current_states.append(state)
    if periods:
        return periods
    return [(_extract_float(text, "fixed_cost_due"), _extract_demand_states(text))]


def _retail_terminal_outcomes(
    order: int,
    cash_on_hand: float,
    unit_cost: float,
    sale_price: float,
    min_reserve: float,
    periods: list[tuple[float, list[tuple[int, float]]]],
    carrying_cost_per_unsold: float,
    terminal_unit_value: float,
) -> list[tuple[float, float, bool]]:
    paths = [(1.0, cash_on_hand - order * unit_cost, float(order), False)]
    for fixed_cost, states in periods:
        next_paths: list[tuple[float, float, bool]] = []
        for path_probability, path_cash, path_inventory, already_ruined in paths:
            for demand, probability in states:
                sold = min(path_inventory, float(demand))
                inventory_after = path_inventory - sold
                cash_after = (
                    path_cash
                    - fixed_cost
                    + sold * sale_price
                    - inventory_after * carrying_cost_per_unsold
                )
                next_paths.append(
                    (
                        path_probability * probability,
                        cash_after,
                        inventory_after,
                        already_ruined or cash_after < min_reserve,
                    )
                )
        paths = next_paths
    return [
        (probability, terminal_cash + inventory * terminal_unit_value, ruined)
        for probability, terminal_cash, inventory, ruined in paths
    ]


def _extract_supplier_options(text: str) -> list[dict[str, float | int | str]]:
    suppliers = []
    for line in text.splitlines():
        if not line.startswith("supplier_id="):
            continue
        suppliers.append(
            {
                "supplier_id": _extract_word(line, "supplier_id"),
                "unit_cost": _extract_float(line, "unit_cost"),
                "claimed_resale": _extract_float(line, "claimed_resale"),
                "verified_resale_if_legit": _extract_float(line, "verified_resale_if_legit"),
                "scam_probability": _extract_float(line, "scam_probability"),
                "salvage_resale_if_scam": _extract_float(line, "salvage_resale_if_scam"),
                "max_units": int(round(_extract_float(line, "max_units"))),
                "delivery_lag_rounds": int(round(_extract_float(line, "delivery_lag_rounds", 0.0))),
                "sell_through_rate": _extract_float(line, "sell_through_rate", 1.0),
                "storage_cost_per_unsold": _extract_float(line, "storage_cost_per_unsold", 0.0),
            }
        )
    return suppliers


def _supplier_resale(supplier: dict[str, float | int | str], *, credulous: bool) -> float:
    if credulous:
        return float(supplier["claimed_resale"])
    scam_probability = float(supplier["scam_probability"])
    return (
        (1.0 - scam_probability) * float(supplier["verified_resale_if_legit"])
        + scam_probability * float(supplier["salvage_resale_if_scam"])
    )


def _supplier_unit_profit(
    supplier: dict[str, float | int | str],
    *,
    credulous: bool,
    timing_blind: bool,
) -> float:
    resale = _supplier_resale(supplier, credulous=credulous)
    unit_cost = float(supplier["unit_cost"])
    if timing_blind:
        return resale - unit_cost
    sell_through_rate = float(supplier["sell_through_rate"])
    sold_value = sell_through_rate * resale
    leftover_value = (1.0 - sell_through_rate) * float(supplier["salvage_resale_if_scam"])
    storage_cost = (1.0 - sell_through_rate) * float(supplier["storage_cost_per_unsold"])
    return sold_value + leftover_value - storage_cost - unit_cost


def _supplier_max_affordable_units(
    cash: float,
    reserve: float,
    interim_cash_need: float,
    supplier: dict[str, float | int | str],
    *,
    timing_blind: bool,
) -> int:
    unit_cost = float(supplier["unit_cost"])
    if unit_cost <= 0:
        return int(supplier["max_units"])
    protected_cash = reserve
    if int(supplier["delivery_lag_rounds"]) > 0 and not timing_blind:
        protected_cash += interim_cash_need
    affordable = int((cash - protected_cash) // unit_cost)
    return max(0, min(int(supplier["max_units"]), affordable))


def _extract_alignment_actions(text: str) -> dict[str, dict[str, float]]:
    actions = {}
    pattern = re.compile(
        r"action_id=([a-zA-Z0-9_-]+)\s+"
        r"expected_profit=([-+]?\d+(?:\.\d+)?)\s+"
        r"relationship_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"complaint_risk=([-+]?\d+(?:\.\d+)?)\s+"
        r"concession_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"human_approval=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        actions[match.group(1)] = {
            "expected_profit": float(match.group(2)),
            "relationship_value": float(match.group(3)),
            "complaint_risk": float(match.group(4)),
            "concession_cost": float(match.group(5)),
            "human_approval": float(match.group(6)),
        }
    return actions


def _extract_buyer_states(text: str) -> list[dict[str, float]]:
    states = []
    for line in text.splitlines():
        if "state_id=" not in line:
            continue
        likelihoods = _extract_float_list(line, "signal_likelihoods")
        if not likelihoods:
            likelihoods = [_extract_float(line, "likelihood_of_observed_cue")]
        states.append(
            {
                "buyer_wtp": _extract_float(line, "buyer_wtp"),
                "prior": _extract_float(line, "prior_probability"),
                "likelihood": _extract_float(line, "likelihood_of_observed_cue"),
                "likelihoods": likelihoods,
            }
        )
    return states


def _belief_best_price(
    seller_cost: float,
    states: list[dict[str, float]],
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> float:
    if not states:
        return seller_cost
    if use_posterior:
        weights = [state["prior"] * _belief_likelihood_product(state, signal_count=signal_count) for state in states]
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


def _belief_likelihood_product(state: dict[str, float], *, signal_count: int | None) -> float:
    likelihoods = list(state.get("likelihoods") or [state["likelihood"]])
    if signal_count is not None:
        likelihoods = likelihoods[:signal_count]
    product = 1.0
    for likelihood in likelihoods:
        product *= likelihood
    return product


def _extract_float_list(text: str, key: str) -> list[float]:
    match = re.search(rf"{re.escape(key)}=([-+0-9.,]+)", text)
    if not match:
        return []
    return [float(value) for value in match.group(1).split(",") if value]


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
            "incentive_violation": 0.0,
        }
    ic_pattern = re.compile(
        r"ic_check mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"type_id=[a-zA-Z0-9_-]+\s+"
        r"probability=([-+]?\d+(?:\.\d+)?)\s+"
        r"truthful_utility=([-+]?\d+(?:\.\d+)?)\s+"
        r"best_deviation_utility=([-+]?\d+(?:\.\d+)?)"
    )
    for match in ic_pattern.finditer(text):
        mechanism_id = match.group(1)
        if mechanism_id not in mechanisms:
            continue
        probability = max(0.0, float(match.group(2)))
        truthful = float(match.group(3))
        deviation = float(match.group(4))
        mechanisms[mechanism_id]["incentive_violation"] += probability * max(0.0, deviation - truthful)
    return mechanisms


def _best_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, float]],
    *,
    risk_blind: bool,
    ic_blind: bool = False,
) -> str:
    revenue_weight = _extract_float(text, "revenue_weight")
    welfare_weight = _extract_float(text, "welfare_weight")
    access_weight = _extract_float(text, "access_weight")
    risk_penalty = 0.0 if risk_blind else _extract_float(text, "strategic_risk_penalty")
    ic_penalty = 0.0 if ic_blind else _extract_float(text, "incentive_violation_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        return (
            revenue_weight * mechanism["revenue"]
            + welfare_weight * mechanism["welfare"]
            + access_weight * mechanism["access"]
            - risk_penalty * mechanism["strategic_risk"]
            - ic_penalty * mechanism["incentive_violation"]
        )

    return max(mechanisms, key=score)


def _extract_matchings(text: str) -> dict[str, dict[str, float]]:
    matchings: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"matching_id=([a-zA-Z0-9_-]+)\s+"
        r"total_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"blocking_pairs=([-+]?\d+)\s+"
        r"access_score=([-+]?\d+(?:\.\d+)?)\s+"
        r"priority_fit=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        matchings[match.group(1)] = {
            "total_value": float(match.group(2)),
            "blocking_pairs": float(match.group(3)),
            "access_score": float(match.group(4)),
            "priority_fit": float(match.group(5)),
        }
    return matchings


def _best_matching_choice(text: str, matchings: dict[str, dict[str, float]]) -> str:
    instability_penalty = _extract_float(text, "instability_penalty")
    access_weight = _extract_float(text, "access_weight")
    priority_weight = _extract_float(text, "priority_weight")

    def score(matching_id: str) -> float:
        matching = matchings[matching_id]
        return (
            matching["total_value"]
            - instability_penalty * matching["blocking_pairs"]
            + access_weight * matching["access_score"]
            + priority_weight * matching["priority_fit"]
        )

    return max(matchings, key=score)


def _extract_screening_types(text: str) -> dict[str, dict[str, float]]:
    types: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"type_id=([a-zA-Z0-9_-]+)\s+"
        r"probability=([-+]?\d+(?:\.\d+)?)\s+"
        r"value_per_unit=([-+]?\d+(?:\.\d+)?)\s+"
        r"service_cost_per_unit=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        types[match.group(1)] = {
            "probability": float(match.group(2)),
            "value_per_unit": float(match.group(3)),
            "service_cost_per_unit": float(match.group(4)),
        }
    return types


def _extract_screening_menus(text: str) -> dict[str, dict[str, dict[str, float]]]:
    menus: dict[str, dict[str, dict[str, float]]] = {}
    current_menu = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("menu_id="):
            current_menu = _extract_word(stripped, "menu_id")
            menus[current_menu] = {}
        elif stripped.startswith("contract_type=") and current_menu:
            type_id = _extract_word(stripped, "contract_type")
            menus[current_menu][type_id] = {
                "quantity": _extract_float(stripped, "quantity"),
                "price": _extract_float(stripped, "price"),
            }
    return menus


def _screening_utility(type_: dict[str, float], contract: dict[str, float]) -> float:
    return type_["value_per_unit"] * contract["quantity"] - contract["price"]


def _screening_profit(type_: dict[str, float], contract: dict[str, float]) -> float:
    return contract["price"] - type_["service_cost_per_unit"] * contract["quantity"]


def _screening_metrics(
    types: dict[str, dict[str, float]],
    menu: dict[str, dict[str, float]],
) -> dict[str, float]:
    expected_profit = 0.0
    expected_surplus = 0.0
    participation_rate = 0.0
    ic_violation_rate = 0.0
    ir_violation_rate = 0.0
    for type_id, type_ in types.items():
        intended = menu[type_id]
        intended_utility = _screening_utility(type_, intended)
        probability = type_["probability"]
        expected_profit += probability * _screening_profit(type_, intended)
        expected_surplus += probability * intended_utility
        if intended_utility >= -1e-9:
            participation_rate += probability
        else:
            ir_violation_rate += probability
        if any(_screening_utility(type_, other) > intended_utility + 1e-9 for other in menu.values()):
            ic_violation_rate += probability
    return {
        "expected_profit": expected_profit,
        "expected_surplus": expected_surplus,
        "participation_rate": participation_rate,
        "ic_violation_rate": ic_violation_rate,
        "ir_violation_rate": ir_violation_rate,
    }


def _best_screening_menu(
    text: str,
    types: dict[str, dict[str, float]],
    menus: dict[str, dict[str, dict[str, float]]],
    *,
    constraint_blind: bool,
) -> str:
    profit_weight = _extract_float(text, "profit_weight")
    surplus_weight = _extract_float(text, "surplus_weight")
    access_weight = _extract_float(text, "access_weight")
    ic_penalty = 0.0 if constraint_blind else _extract_float(text, "ic_penalty")
    ir_penalty = 0.0 if constraint_blind else _extract_float(text, "ir_penalty")

    def score(menu_id: str) -> float:
        metrics = _screening_metrics(types, menus[menu_id])
        return (
            profit_weight * metrics["expected_profit"]
            + surplus_weight * metrics["expected_surplus"]
            + access_weight * 100.0 * metrics["participation_rate"]
            - ic_penalty * 100.0 * metrics["ic_violation_rate"]
            - ir_penalty * 100.0 * metrics["ir_violation_rate"]
        )

    return max(menus, key=score)


def _extract_moral_hazard_efforts(text: str) -> dict[str, dict[str, float]]:
    efforts: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"effort_id=([a-zA-Z0-9_-]+)\s+"
        r"high_output_probability=([-+]?\d+(?:\.\d+)?)\s+"
        r"effort_cost=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        efforts[match.group(1)] = {
            "high_output_probability": float(match.group(2)),
            "effort_cost": float(match.group(3)),
        }
    return efforts


def _extract_moral_hazard_contracts(text: str) -> dict[str, dict[str, float]]:
    contracts: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"contract_id=([a-zA-Z0-9_-]+)\s+"
        r"base_pay=([-+]?\d+(?:\.\d+)?)\s+"
        r"high_output_bonus=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        contracts[match.group(1)] = {
            "base_pay": float(match.group(2)),
            "high_output_bonus": float(match.group(3)),
        }
    return contracts


def _moral_hazard_expected_output_value(text: str, effort: dict[str, float]) -> float:
    p_high = effort["high_output_probability"]
    return p_high * _extract_float(text, "high_output_value") + (1.0 - p_high) * _extract_float(
        text, "low_output_value"
    )


def _moral_hazard_expected_wage(contract: dict[str, float], effort: dict[str, float]) -> float:
    return contract["base_pay"] + effort["high_output_probability"] * contract["high_output_bonus"]


def _moral_hazard_wage_variance(contract: dict[str, float], effort: dict[str, float]) -> float:
    p_high = effort["high_output_probability"]
    return p_high * (1.0 - p_high) * contract["high_output_bonus"] ** 2


def _moral_hazard_worker_utility(
    text: str,
    contract: dict[str, float],
    effort: dict[str, float],
) -> float:
    return (
        _moral_hazard_expected_wage(contract, effort)
        - effort["effort_cost"]
        - _extract_float(text, "worker_risk_penalty") * _moral_hazard_wage_variance(contract, effort)
    )


def _moral_hazard_contract_profit(
    text: str,
    efforts: dict[str, dict[str, float]],
    contract: dict[str, float],
    *,
    assume_high_effort: bool,
) -> float:
    if assume_high_effort:
        effort = max(efforts.values(), key=lambda item: item["high_output_probability"])
    else:
        effort = max(efforts.values(), key=lambda item: _moral_hazard_worker_utility(text, contract, item))
    utility = _moral_hazard_worker_utility(text, contract, effort)
    if utility < _extract_float(text, "worker_outside_option"):
        return -1e9
    return _moral_hazard_expected_output_value(text, effort) - _moral_hazard_expected_wage(contract, effort)


def _best_moral_hazard_contract(
    text: str,
    efforts: dict[str, dict[str, float]],
    contracts: dict[str, dict[str, float]],
    *,
    assume_high_effort: bool,
) -> str:
    return max(
        contracts,
        key=lambda contract_id: _moral_hazard_contract_profit(
            text,
            efforts,
            contracts[contract_id],
            assume_high_effort=assume_high_effort,
        ),
    )


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


def _extract_ambiguity_signal(text: str, state_ids: list[str]) -> list[float] | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("observed_signal_likelihoods"):
            return [_extract_float(stripped, state) for state in state_ids]
    return None


def _update_ambiguity_priors(
    priors: dict[str, list[float]],
    signal: list[float] | None,
) -> dict[str, list[float]]:
    if signal is None:
        return priors
    updated: dict[str, list[float]] = {}
    for prior_id, probabilities in priors.items():
        weighted = [probability * likelihood for probability, likelihood in zip(probabilities, signal)]
        total = sum(weighted)
        updated[prior_id] = [value / total for value in weighted] if total > 0 else probabilities
    return updated


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


def _best_alpha_maxmin_action(
    actions: dict[str, list[float]],
    priors: dict[str, list[float]],
    *,
    alpha: float,
) -> str:
    alpha = max(0.0, min(1.0, alpha))

    def value(action_id: str) -> float:
        expected_values = [
            _action_expected_value(actions[action_id], probabilities)
            for probabilities in priors.values()
        ]
        return alpha * min(expected_values) + (1.0 - alpha) * max(expected_values)

    return max(actions, key=value)
