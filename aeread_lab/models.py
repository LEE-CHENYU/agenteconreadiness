from __future__ import annotations

import itertools
import math
import os
import re
from dataclasses import dataclass, field
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
    max_output_tokens: int = field(
        default_factory=lambda: int(os.environ.get("AEREAD_OPENAI_MAX_OUTPUT_TOKENS", "4096"))
    )
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
        if "TASK: regime_law_label" in system:
            return self._regime_law_label(user)
        if "TASK: alignment_tax_action" in system:
            return self._alignment_tax_action(user)
        if "TASK: principal_fraction" in system:
            return self._principal_fraction(user)
        if "TASK: portfolio_choice" in system:
            return self._portfolio_choice(user)
        if "TASK: revealed_allocation" in system:
            return self._revealed_allocation(user)
        if "TASK: principal_holding_filing_artifact" in system:
            return self._principal_holding_filing_artifact(user)
        if "TASK: principal_holding_filing_trace_raw" in system:
            return self._principal_holding_filing_trace_raw(user)
        if "TASK: principal_holding_filing_trace" in system:
            return self._principal_holding_filing_trace(user)
        if "TASK: principal_holding_prediction_blind_notes" in system:
            return self._principal_holding_notes_prediction(user)
        if "TASK: principal_holding_prediction_notes" in system:
            return self._principal_holding_notes_prediction(user)
        if "TASK: principal_holding_prediction_noisy" in system:
            return self._noisy_principal_holding_prediction(user)
        if "TASK: principal_holding_prediction" in system:
            return self._principal_holding_prediction(user)
        if "TASK: ambiguity_action" in system:
            return self._ambiguity_action(user)
        if "TASK: procurement_vendor_update" in system:
            return self._procurement_vendor_update(user)
        if "TASK: procurement_bundle" in system:
            return self._procurement_bundle(user)
        if "TASK: procurement_choice" in system:
            return self._procurement_choice(user)
        if "TASK: pricing_price" in system:
            return self._pricing_price(user)
        if "TASK: pricing_cross_price" in system:
            return self._pricing_cross_price(user)
        if "TASK: pricing_multi_product_prices" in system:
            return self._pricing_multi_product_prices(user)
        if "TASK: pricing_multi_product_natural_prices" in system:
            return self._pricing_multi_product_prices(user)
        if (
            "TASK: pricing_multi_product_capacity_prices" in system
            or "TASK: pricing_multi_product_capacity_noisy_prices" in system
        ):
            return self._pricing_multi_product_capacity_prices(user)
        if "TASK: pricing_inventory_markdown_prices" in system:
            return self._pricing_inventory_markdown_prices(user)
        if "TASK: pricing_inventory_markdown_noisy_prices" in system:
            return self._pricing_inventory_markdown_prices(user)
        if "TASK: pricing_multi_product_markdown_noisy_prices" in system:
            return self._pricing_multi_product_markdown_noisy_prices(user)
        if "TASK: pricing_inventory_replenishment_noisy_plan" in system:
            return self._pricing_inventory_replenishment_noisy_plan(user)
        if "TASK: pricing_hidden_intervention_price" in system:
            return self._pricing_hidden_intervention_price(user)
        if "TASK: pricing_law_label" in system:
            return self._pricing_law_label(user)
        if "TASK: pricing_evidence_law_label" in system:
            return self._pricing_evidence_law_label(user)
        if "TASK: bargaining_offer" in system:
            return self._bargaining_offer(user)
        if "TASK: belief_bargain_price" in system:
            return self._belief_bargain_price(user)
        if "TASK: belief_bargain_interaction" in system:
            return self._belief_bargain_interaction(user)
        if "TASK: market_price" in system:
            return self._market_price(user)
        if "TASK: market_policy_price" in system:
            return self._market_policy_price(user)
        if "TASK: market_policy_inventory_price" in system:
            return self._market_policy_inventory_price(user)
        if "TASK: market_trace_inventory_price" in system:
            return self._market_trace_inventory_price(user)
        if "TASK: market_trace_markdown_prices" in system:
            return self._market_trace_markdown_prices(user)
        if (
            "TASK: market_trace_replenishment_plan" in system
            or "TASK: market_trace_replenishment_natural_plan" in system
            or "TASK: market_trace_replenishment_noisy_plan" in system
        ):
            return self._market_trace_replenishment_plan(user)
        if "TASK: auction_reserve" in system:
            return self._auction_reserve(user)
        if "TASK: common_value_bid" in system:
            return self._common_value_bid(user)
        if "TASK: mechanism_choice" in system:
            return self._mechanism_choice(user)
        if "TASK: mechanism_repeated_choice" in system:
            return self._mechanism_repeated_choice(user)
        if "TASK: mechanism_participant_response" in system:
            return self._mechanism_participant_response_choice(user)
        if "TASK: mechanism_strategic_response" in system:
            return self._mechanism_strategic_response_choice(user)
        if "TASK: mechanism_strategic_equilibrium" in system:
            return self._mechanism_strategic_equilibrium_choice(user)
        if "TASK: mechanism_trace_equilibrium" in system:
            return self._mechanism_trace_equilibrium_choice(user)
        if "TASK: mechanism_interaction_trace" in system:
            return self._mechanism_interaction_trace_choice(user)
        if "TASK: matching_choice" in system:
            return self._matching_choice(user)
        if "TASK: screening_choice" in system:
            return self._screening_choice(user)
        if "TASK: moral_hazard_contract" in system:
            return self._moral_hazard_contract(user)
        if "TASK: strategic_action" in system:
            return self._strategic_action(user)
        if "TASK: forecast_probability" in system:
            return self._forecast_probability(user)
        if "TASK: exploration_action" in system:
            return self._exploration_action(user)
        if "TASK: experiment_action" in system:
            return self._experiment_action(user)
        if "TASK: retail_order" in system:
            return self._retail_order(user)
        if "TASK: supplier_scam_order" in system:
            return self._supplier_scam_order(user)
        if "TASK: supplier_scam_natural_order" in system:
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
        elif self.policy in {"wrong_regime", "inverse_regime"}:
            if regime == "ev":
                value = cvar
            elif regime == "cvar":
                value = ev
            elif regime == "kelly":
                value = kelly
            else:
                value = oracle
        elif self.policy == "half":
            value = 0.5
        else:
            value = oracle
        return f"FINAL_FRACTION: {value:.12f}"

    def _regime_law_label(self, user: str) -> str:
        oracle = _regime_law_label(user)
        if self.policy in {"law_accept", "always_valid"}:
            label = "valid"
        elif self.policy in {"law_reject", "always_invalid"}:
            label = "invalid"
        elif self.policy == "law_invert":
            label = "invalid" if oracle == "valid" else "valid"
        else:
            label = oracle
        return f"FINAL_LABEL: {label}"

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

    def _principal_holding_prediction(self, user: str) -> str:
        target_trades = _extract_principal_holding_trades(user, target_only=True)
        if self.policy in {"max_return", "market_return", "return"}:
            trade_id = max(target_trades, key=lambda item: target_trades[item]["expected_return"])
        elif self.policy in {"low_turnover", "min_turnover"}:
            trade_id = min(target_trades, key=lambda item: target_trades[item]["turnover_cost"])
        elif self.policy in {"generic_style", "balanced_style"}:
            trade_id = _best_principal_holding_trade(
                target_trades,
                _PRINCIPAL_GENERIC_STYLE_WEIGHTS,
            )
        else:
            style_id = _infer_principal_holding_style(user)
            trade_id = _best_principal_holding_trade(
                target_trades,
                _PRINCIPAL_STYLE_WEIGHTS[style_id],
            )
        return f"FINAL_TRADE: {trade_id}"

    def _noisy_principal_holding_prediction(self, user: str) -> str:
        target_trades = _extract_noisy_principal_holding_trades(user, target_only=True)
        if self.policy in {"max_return", "market_return", "return"}:
            trade_id = max(target_trades, key=lambda item: target_trades[item]["expected_return"])
        elif self.policy in {"low_turnover", "min_turnover"}:
            trade_id = min(target_trades, key=lambda item: target_trades[item]["turnover_cost"])
        elif self.policy in {"generic_style", "balanced_style"}:
            trade_id = _best_noisy_principal_holding_trade(
                target_trades,
                _PRINCIPAL_GENERIC_STYLE_WEIGHTS,
            )
        elif self.policy in {"mechanical_flow", "flow_blind", "filing_blind"}:
            style_id = _infer_noisy_principal_holding_style(
                user,
                include_mechanical=True,
            )
            trade_id = _best_noisy_principal_holding_trade(
                target_trades,
                _PRINCIPAL_STYLE_WEIGHTS[style_id],
            )
        else:
            style_id = _infer_noisy_principal_holding_style(user)
            trade_id = _best_noisy_principal_holding_trade(
                target_trades,
                _PRINCIPAL_STYLE_WEIGHTS[style_id],
            )
        return f"FINAL_TRADE: {trade_id}"

    def _principal_holding_notes_prediction(self, user: str) -> str:
        target_trades = _extract_note_principal_holding_trades(user, target_only=True)
        if self.policy in {"max_return", "market_return", "return"}:
            trade_id = max(target_trades, key=lambda item: target_trades[item]["expected_return"])
        elif self.policy in {"low_turnover", "min_turnover"}:
            trade_id = min(target_trades, key=lambda item: target_trades[item]["turnover_cost"])
        elif self.policy in {"generic_style", "balanced_style"}:
            trade_id = _best_noisy_principal_holding_trade(
                target_trades,
                _PRINCIPAL_GENERIC_STYLE_WEIGHTS,
            )
        elif self.policy in {"mechanical_flow", "flow_blind", "filing_blind"}:
            style_id = _infer_note_principal_holding_style(
                user,
                include_mechanical=True,
            )
            trade_id = _best_noisy_principal_holding_trade(
                target_trades,
                _PRINCIPAL_STYLE_WEIGHTS[style_id],
            )
        else:
            style_id = _infer_note_principal_holding_style(user)
            trade_id = _best_noisy_principal_holding_trade(
                target_trades,
                _PRINCIPAL_STYLE_WEIGHTS[style_id],
            )
        return f"FINAL_TRADE: {trade_id}"

    def _principal_holding_filing_trace(self, user: str) -> str:
        target_trades = _extract_filing_trace_trades(user)
        if self.policy in {"market_value", "market_return", "max_return", "value_drift"}:
            trade_id = max(
                target_trades,
                key=lambda item: target_trades[item]["next_value"]
                - target_trades[item]["prior_value"],
            )
        elif self.policy in {"low_turnover", "min_turnover", "hold"}:
            trade_id = min(
                target_trades,
                key=lambda item: abs(
                    target_trades[item]["next_shares"] - target_trades[item]["prior_shares"]
                ),
            )
        elif self.policy in {"max_position", "largest_position"}:
            trade_id = max(target_trades, key=lambda item: target_trades[item]["prior_value"])
        elif self.policy in {"trend", "trend_chase"}:
            trade_id = max(
                target_trades,
                key=lambda item: abs(target_trades[item]["previous_share_delta"]),
            )
        elif self.policy in {"percent_change", "relative_change", "largest_pct_change"}:
            trade_id = max(
                target_trades,
                key=lambda item: _filing_trace_share_change_fraction(target_trades[item]),
            )
        elif self.policy in {"second_best", "runner_up", "near_miss"}:
            trade_id = _second_best_filing_trace_id(target_trades)
        else:
            trade_id = max(
                target_trades,
                key=lambda item: _filing_trace_action_value(target_trades[item]),
            )
        return f"FINAL_TRADE: {trade_id}"

    def _principal_holding_filing_trace_raw(self, user: str) -> str:
        target_issuers = _extract_filing_trace_raw_changes(user)
        if self.policy in {"market_value", "market_return", "max_return", "value_drift"}:
            issuer_id = max(
                target_issuers,
                key=lambda item: target_issuers[item]["next_value"]
                - target_issuers[item]["prior_value"],
            )
        elif self.policy in {"low_turnover", "min_turnover", "hold"}:
            issuer_id = min(
                target_issuers,
                key=lambda item: abs(
                    target_issuers[item]["next_shares"]
                    - target_issuers[item]["prior_shares"]
                ),
            )
        elif self.policy in {"max_position", "largest_position"}:
            issuer_id = max(target_issuers, key=lambda item: target_issuers[item]["prior_value"])
        elif self.policy in {"trend", "trend_chase"}:
            issuer_id = max(
                target_issuers,
                key=lambda item: abs(target_issuers[item]["previous_share_delta"]),
            )
        elif self.policy in {"percent_change", "relative_change", "largest_pct_change"}:
            issuer_id = max(
                target_issuers,
                key=lambda item: _filing_trace_share_change_fraction(target_issuers[item]),
            )
        elif self.policy in {"second_best", "runner_up", "near_miss"}:
            issuer_id = _second_best_filing_trace_id(target_issuers)
        else:
            issuer_id = max(
                target_issuers,
                key=lambda item: _filing_trace_action_value(target_issuers[item]),
            )
        return f"FINAL_ISSUER: {issuer_id}"

    def _principal_holding_filing_artifact(self, user: str) -> str:
        strict_metadata = self.policy not in {"metadata_naive", "registry_noise", "stale_metadata"}
        infer_missing_artifacts = self.policy not in {"metadata_only", "registry_only"}
        validate_metadata = self.policy not in {
            "metadata_naive",
            "metadata_source_trusting",
            "metadata_trusting",
            "registry_noise",
            "registry_trusting",
            "stale_metadata",
        }
        trusted_metadata_sources = (
            {"issuer_exchange_notice"} if self.policy == "metadata_source_trusting" else None
        )
        target_issuers = _extract_filing_artifact_changes(
            user,
            strict_metadata=strict_metadata,
            infer_missing_artifacts=infer_missing_artifacts,
            validate_metadata=validate_metadata,
            trusted_metadata_sources=trusted_metadata_sources,
        )
        if self.policy in {
            "metadata_naive",
            "metadata_only",
            "metadata_source_trusting",
            "metadata_trusting",
            "registry_noise",
            "registry_only",
            "registry_trusting",
            "stale_metadata",
        }:
            issuer_id = max(
                target_issuers,
                key=lambda item: target_issuers[item]["value"],
            )
        elif self.policy in {"artifact_blind", "mechanical_flow", "raw_change"}:
            issuer_id = max(
                target_issuers,
                key=lambda item: target_issuers[item]["observed_value"],
            )
        elif self.policy in {"market_value", "market_return", "max_return", "value_drift"}:
            issuer_id = max(
                target_issuers,
                key=lambda item: target_issuers[item]["next_value"]
                - target_issuers[item]["prior_value"],
            )
        elif self.policy in {"percent_change", "relative_change", "largest_pct_change"}:
            issuer_id = max(
                target_issuers,
                key=lambda item: target_issuers[item]["observed_fraction"],
            )
        elif self.policy in {"second_best", "runner_up", "near_miss"}:
            issuer_id = _second_best_artifact_id(target_issuers)
        else:
            issuer_id = max(
                target_issuers,
                key=lambda item: target_issuers[item]["value"],
            )
        return f"FINAL_ISSUER: {issuer_id}"

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
        products = _extract_procurement_products(user)
        if self.policy in {"cheapest", "price"} and products:
            product_id = min(products, key=lambda item: products[item]["price"])
            return f"FINAL_PRODUCT: {product_id}"
        if self.policy == "comfort" and products:
            product_id = max(products, key=lambda item: products[item]["comfort"])
            return f"FINAL_PRODUCT: {product_id}"
        if self.policy == "style" and products:
            product_id = max(products, key=lambda item: products[item]["style_fit"])
            return f"FINAL_PRODUCT: {product_id}"
        if self.policy == "durability" and products:
            product_id = max(products, key=lambda item: products[item]["durability"])
            return f"FINAL_PRODUCT: {product_id}"
        weights = {
            "price": _extract_float(user, "price_weight"),
            "durability": _extract_float(user, "durability_weight"),
            "comfort": _extract_float(user, "comfort_weight"),
            "style": _extract_float(user, "style_weight"),
            "friction": _extract_float(user, "friction_weight"),
        }
        best_product = ""
        best_utility = -math.inf
        for product_id, product in products.items():
            price = product["price"]
            durability = product["durability"]
            comfort = product["comfort"]
            style = product["style_fit"]
            friction = product["assembly_friction"]
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

    def _procurement_bundle(self, user: str) -> str:
        products = _extract_procurement_bundle_products(user)
        if not products:
            return "FINAL_BUNDLE: ,"
        if self.policy in {"first", "first_pair"}:
            pair = tuple(list(products)[:2])
        elif self.policy in {"cheapest", "price", "cheapest_pair"}:
            pair = tuple(sorted(products, key=lambda item: products[item]["price"])[:2])
        else:
            pair = _best_procurement_bundle(user, products, self.policy)
        left, right = sorted(pair)
        return f"FINAL_BUNDLE: {left},{right}"

    def _procurement_vendor_update(self, user: str) -> str:
        vendors = _extract_procurement_vendor_update_vendors(user)
        rounds = _extract_procurement_vendor_update_rounds(user)
        if not vendors or not rounds:
            return "FINAL_VENDOR_PLAN: ,,"
        if self.policy in {"first", "first_vendor"}:
            plan = tuple([next(iter(vendors))] * len(rounds))
        elif self.policy in {"cheapest", "price", "low_bid"}:
            cheapest = min(vendors, key=lambda item: vendors[item]["invoice"])
            plan = tuple([cheapest] * len(rounds))
        elif self.policy in {"myopic", "single_round"}:
            plan = _myopic_procurement_vendor_update_plan(vendors, rounds)
        elif self.policy in {"reputation_blind", "history_blind", "delivery_blind"}:
            plan = _best_procurement_vendor_update_plan(user, vendors, rounds, reputation_blind=True)
        else:
            plan = _best_procurement_vendor_update_plan(user, vendors, rounds)
        return f"FINAL_VENDOR_PLAN: {','.join(plan)}"

    def _pricing_price(self, user: str) -> str:
        case_key = _extract_word(user, "case")
        p_max = _extract_float(user, "p_max", 1e9)
        if self.policy in {"stale_price", "base_price"}:
            stale_prices = {
                "snack_demand_downshift_base": 15.0,
                "snack_demand_downshift_perturbed": 15.0,
                "premium_demand_upswing_base": 20.0,
                "premium_demand_upswing_perturbed": 20.0,
                "noisy_snack_downshift_base": 20.50,
                "noisy_snack_downshift_perturbed": 20.50,
                "noisy_enterprise_upswing_base": 22.76,
                "noisy_enterprise_upswing_perturbed": 22.76,
            }
            if case_key in stale_prices:
                return f"FINAL_PRICE: {stale_prices[case_key]:.2f}"
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

    def _pricing_cross_price(self, user: str) -> str:
        p_max = _extract_float(user, "p_max", 1e9)
        planned_related = _extract_float(user, "planned_related_price")
        rows = _extract_cross_pricing_rows(user)
        if self.policy in {"own_only", "cross_blind"}:
            fit = _fit_pricing_rows([(own, quantity) for own, _, quantity in rows])
            alpha, beta = fit if fit is not None else (1.0, 1.0)
            price = max(0.0, min(p_max, alpha / (2.0 * max(beta, 1e-9))))
        else:
            alpha, own_beta, related_beta = _fit_cross_pricing_rows(rows)
            effective_alpha = alpha + related_beta * planned_related
            price = max(0.0, min(p_max, effective_alpha / (2.0 * max(own_beta, 1e-9))))
        if self.policy == "round":
            price = round(price / 10.0) * 10.0
        return f"FINAL_PRICE: {price:.2f}"

    def _pricing_multi_product_prices(self, user: str) -> str:
        p_max_a = _extract_float(user, "p_max_a", _extract_float(user, "price_ceiling_a", 1e9))
        p_max_b = _extract_float(user, "p_max_b", _extract_float(user, "price_ceiling_b", 1e9))
        rows = _extract_multi_product_rows(user) or _extract_multi_product_natural_rows(user)
        if self.policy in {"independent", "single_product", "own_only"}:
            fit_a = _fit_pricing_rows([(price_a, quantity_a) for price_a, _, quantity_a, _ in rows])
            fit_b = _fit_pricing_rows([(price_b, quantity_b) for _, price_b, _, quantity_b in rows])
            alpha_a, beta_a = fit_a if fit_a is not None else (1.0, 1.0)
            alpha_b, beta_b = fit_b if fit_b is not None else (1.0, 1.0)
            price_a = max(0.0, min(p_max_a, alpha_a / (2.0 * max(beta_a, 1e-9))))
            price_b = max(0.0, min(p_max_b, alpha_b / (2.0 * max(beta_b, 1e-9))))
        else:
            alpha_a, own_beta_a, cross_ab = _fit_cross_pricing_rows(
                [(price_a, price_b, quantity_a) for price_a, price_b, quantity_a, _ in rows]
            )
            alpha_b, own_beta_b, cross_ba = _fit_cross_pricing_rows(
                [(price_b, price_a, quantity_b) for price_a, price_b, _, quantity_b in rows]
            )
            price_a, price_b = _best_multi_product_prices(
                alpha_a=alpha_a,
                own_beta_a=own_beta_a,
                cross_ab=cross_ab,
                alpha_b=alpha_b,
                own_beta_b=own_beta_b,
                cross_ba=cross_ba,
                p_max_a=p_max_a,
                p_max_b=p_max_b,
            )
        if self.policy == "round":
            price_a = round(price_a / 10.0) * 10.0
            price_b = round(price_b / 10.0) * 10.0
        return f"FINAL_PRICE_A: {price_a:.2f}\nFINAL_PRICE_B: {price_b:.2f}"

    def _pricing_multi_product_capacity_prices(self, user: str) -> str:
        p_max_a = _extract_float(user, "p_max_a", _extract_float(user, "price_ceiling_a", 1e9))
        p_max_b = _extract_float(user, "p_max_b", _extract_float(user, "price_ceiling_b", 1e9))
        inventory_a = _extract_float(user, "available_units_a", math.inf)
        inventory_b = _extract_float(user, "available_units_b", math.inf)
        rows = _extract_multi_product_rows(user) or _extract_multi_product_natural_rows(user)
        if self.policy in {"independent", "single_product", "own_only"}:
            fit_a = _fit_pricing_rows([(price_a, quantity_a) for price_a, _, quantity_a, _ in rows])
            fit_b = _fit_pricing_rows([(price_b, quantity_b) for _, price_b, _, quantity_b in rows])
            alpha_a, beta_a = fit_a if fit_a is not None else (1.0, 1.0)
            alpha_b, beta_b = fit_b if fit_b is not None else (1.0, 1.0)
            price_a = max(0.0, min(p_max_a, alpha_a / (2.0 * max(beta_a, 1e-9))))
            price_b = max(0.0, min(p_max_b, alpha_b / (2.0 * max(beta_b, 1e-9))))
        else:
            alpha_a, own_beta_a, cross_ab = _fit_cross_pricing_rows(
                [(price_a, price_b, quantity_a) for price_a, price_b, quantity_a, _ in rows]
            )
            alpha_b, own_beta_b, cross_ba = _fit_cross_pricing_rows(
                [(price_b, price_a, quantity_b) for price_a, price_b, _, quantity_b in rows]
            )
            if self.policy in {"capacity_blind", "inventory_blind", "unconstrained"}:
                price_a, price_b = _best_multi_product_prices(
                    alpha_a=alpha_a,
                    own_beta_a=own_beta_a,
                    cross_ab=cross_ab,
                    alpha_b=alpha_b,
                    own_beta_b=own_beta_b,
                    cross_ba=cross_ba,
                    p_max_a=p_max_a,
                    p_max_b=p_max_b,
                )
            else:
                price_a, price_b = _best_multi_product_capacity_prices(
                    alpha_a=alpha_a,
                    own_beta_a=own_beta_a,
                    cross_ab=cross_ab,
                    alpha_b=alpha_b,
                    own_beta_b=own_beta_b,
                    cross_ba=cross_ba,
                    p_max_a=p_max_a,
                    p_max_b=p_max_b,
                    inventory_a=inventory_a,
                    inventory_b=inventory_b,
                )
        if self.policy == "round":
            price_a = round(price_a / 10.0) * 10.0
            price_b = round(price_b / 10.0) * 10.0
        return f"FINAL_PRICE_A: {price_a:.2f}\nFINAL_PRICE_B: {price_b:.2f}"

    def _pricing_inventory_markdown_prices(self, user: str) -> str:
        p_max_early = _extract_float(
            user,
            "p_max_early",
            _extract_float(user, "price_ceiling_early", _extract_float(user, "launch_price_ceiling", 1e9)),
        )
        p_max_late = _extract_float(
            user,
            "p_max_late",
            _extract_float(user, "price_ceiling_late", _extract_float(user, "clearance_price_ceiling", 1e9)),
        )
        inventory = _extract_float(user, "starting_inventory", _extract_float(user, "starting_units", math.inf))
        salvage_value = _extract_float(user, "salvage_value", _extract_float(user, "liquidation_value", 0.0))
        rows = _extract_inventory_markdown_rows(user) or _extract_inventory_markdown_natural_rows(user)
        fit_early = _fit_pricing_rows([(price, units) for price, units, _, _ in rows])
        fit_late = _fit_pricing_rows([(price, units) for _, _, price, units in rows])
        early_alpha, early_beta = fit_early if fit_early is not None else (1.0, 1.0)
        late_alpha, late_beta = fit_late if fit_late is not None else (1.0, 1.0)
        if self.policy in {"myopic", "single_period", "inventory_blind"}:
            price_early = max(0.0, min(p_max_early, early_alpha / (2.0 * max(early_beta, 1e-9))))
            price_late = max(0.0, min(p_max_late, late_alpha / (2.0 * max(late_beta, 1e-9))))
        else:
            price_early, price_late = _best_inventory_markdown_prices(
                early_alpha=early_alpha,
                early_beta=early_beta,
                late_alpha=late_alpha,
                late_beta=late_beta,
                p_max_early=p_max_early,
                p_max_late=p_max_late,
                inventory=inventory,
                salvage_value=salvage_value,
            )
        if self.policy == "round":
            price_early = round(price_early / 10.0) * 10.0
            price_late = round(price_late / 10.0) * 10.0
        return f"FINAL_PRICE_EARLY: {price_early:.2f}\nFINAL_PRICE_LATE: {price_late:.2f}"

    def _pricing_multi_product_markdown_noisy_prices(self, user: str) -> str:
        p_max_a = _extract_float(user, "p_max_a", _extract_float(user, "price_ceiling_a", 1e9))
        p_max_b = _extract_float(user, "p_max_b", _extract_float(user, "price_ceiling_b", 1e9))
        inventory_a = _extract_float(user, "available_units_a", math.inf)
        inventory_b = _extract_float(user, "available_units_b", math.inf)
        salvage_value_a = _extract_float(user, "liquidation_value_a", 0.0)
        salvage_value_b = _extract_float(user, "liquidation_value_b", 0.0)
        rows = _extract_multi_product_markdown_rows(user)
        early_alpha_a, early_own_a, early_cross_ab = _fit_cross_pricing_rows(
            [(row[0], row[1], row[2]) for row in rows]
        )
        early_alpha_b, early_own_b, early_cross_ba = _fit_cross_pricing_rows(
            [(row[1], row[0], row[3]) for row in rows]
        )
        late_alpha_a, late_own_a, late_cross_ab = _fit_cross_pricing_rows(
            [(row[4], row[5], row[6]) for row in rows]
        )
        late_alpha_b, late_own_b, late_cross_ba = _fit_cross_pricing_rows(
            [(row[5], row[4], row[7]) for row in rows]
        )
        if self.policy in {"independent", "single_product", "own_only"}:
            early_fit_a = _fit_pricing_rows([(row[0], row[2]) for row in rows]) or (1.0, 1.0)
            early_fit_b = _fit_pricing_rows([(row[1], row[3]) for row in rows]) or (1.0, 1.0)
            late_fit_a = _fit_pricing_rows([(row[4], row[6]) for row in rows]) or (1.0, 1.0)
            late_fit_b = _fit_pricing_rows([(row[5], row[7]) for row in rows]) or (1.0, 1.0)
            price_a_early = max(
                salvage_value_a,
                min(p_max_a, early_fit_a[0] / (2.0 * max(early_fit_a[1], 1e-9))),
            )
            price_b_early = max(
                salvage_value_b,
                min(p_max_b, early_fit_b[0] / (2.0 * max(early_fit_b[1], 1e-9))),
            )
            price_a_late = max(
                salvage_value_a,
                min(p_max_a, late_fit_a[0] / (2.0 * max(late_fit_a[1], 1e-9))),
            )
            price_b_late = max(
                salvage_value_b,
                min(p_max_b, late_fit_b[0] / (2.0 * max(late_fit_b[1], 1e-9))),
            )
        elif self.policy in {"capacity_blind", "inventory_blind", "unconstrained"}:
            price_a_early, price_b_early = _best_multi_product_prices(
                alpha_a=early_alpha_a,
                own_beta_a=early_own_a,
                cross_ab=early_cross_ab,
                alpha_b=early_alpha_b,
                own_beta_b=early_own_b,
                cross_ba=early_cross_ba,
                p_max_a=p_max_a,
                p_max_b=p_max_b,
            )
            price_a_late, price_b_late = _best_multi_product_prices(
                alpha_a=late_alpha_a,
                own_beta_a=late_own_a,
                cross_ab=late_cross_ab,
                alpha_b=late_alpha_b,
                own_beta_b=late_own_b,
                cross_ba=late_cross_ba,
                p_max_a=p_max_a,
                p_max_b=p_max_b,
            )
            price_a_early = max(salvage_value_a, price_a_early)
            price_b_early = max(salvage_value_b, price_b_early)
            price_a_late = max(salvage_value_a, price_a_late)
            price_b_late = max(salvage_value_b, price_b_late)
        elif self.policy in {"myopic", "single_period", "depletion_blind"}:
            price_a_early, price_b_early = _best_multi_product_capacity_prices(
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
            price_a_late, price_b_late = _best_multi_product_capacity_prices(
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
            price_a_early = max(salvage_value_a, price_a_early)
            price_b_early = max(salvage_value_b, price_b_early)
            price_a_late = max(salvage_value_a, price_a_late)
            price_b_late = max(salvage_value_b, price_b_late)
        else:
            price_a_early, price_b_early, price_a_late, price_b_late = _best_multi_product_markdown_prices(
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
                p_max_a=p_max_a,
                p_max_b=p_max_b,
                inventory_a=inventory_a,
                inventory_b=inventory_b,
                salvage_value_a=salvage_value_a,
                salvage_value_b=salvage_value_b,
            )
        if self.policy == "round":
            price_a_early = round(price_a_early / 10.0) * 10.0
            price_b_early = round(price_b_early / 10.0) * 10.0
            price_a_late = round(price_a_late / 10.0) * 10.0
            price_b_late = round(price_b_late / 10.0) * 10.0
        return (
            f"FINAL_PRICE_A_EARLY: {price_a_early:.2f}\n"
            f"FINAL_PRICE_B_EARLY: {price_b_early:.2f}\n"
            f"FINAL_PRICE_A_LATE: {price_a_late:.2f}\n"
            f"FINAL_PRICE_B_LATE: {price_b_late:.2f}"
        )

    def _pricing_inventory_replenishment_noisy_plan(self, user: str) -> str:
        p_max_early = _extract_float(user, "launch_price_ceiling", _extract_float(user, "p_max_early", 1e9))
        p_max_late = _extract_float(user, "clearance_price_ceiling", _extract_float(user, "p_max_late", 1e9))
        starting_inventory = _extract_float(user, "starting_units", _extract_float(user, "starting_inventory", math.inf))
        max_replenishment_units = _extract_float(user, "max_replenishment_units", 0.0)
        storage_capacity = _extract_float(user, "storage_capacity", starting_inventory + max_replenishment_units)
        replenishment_unit_cost = _extract_float(user, "replenishment_unit_cost", 0.0)
        replenishment_setup_cost = _extract_float(user, "replenishment_setup_cost", 0.0)
        salvage_value = _extract_float(user, "liquidation_value", _extract_float(user, "salvage_value", 0.0))
        rows = _extract_inventory_markdown_rows(user) or _extract_inventory_markdown_natural_rows(user)
        fit_early = _fit_pricing_rows([(price, units) for price, units, _, _ in rows])
        fit_late = _fit_pricing_rows([(price, units) for _, _, price, units in rows])
        early_alpha, early_beta = fit_early if fit_early is not None else (1.0, 1.0)
        late_alpha, late_beta = fit_late if fit_late is not None else (1.0, 1.0)
        if self.policy in {"no_restock", "no_replenishment", "replenishment_blind"}:
            price_early, price_late = _best_inventory_markdown_prices(
                early_alpha=early_alpha,
                early_beta=early_beta,
                late_alpha=late_alpha,
                late_beta=late_beta,
                p_max_early=p_max_early,
                p_max_late=p_max_late,
                inventory=starting_inventory,
                salvage_value=salvage_value,
            )
            replenishment_units = 0.0
        elif self.policy in {"myopic", "single_period"}:
            price_early = max(0.0, min(p_max_early, early_alpha / (2.0 * max(early_beta, 1e-9))))
            price_late = max(0.0, min(p_max_late, late_alpha / (2.0 * max(late_beta, 1e-9))))
            early_demand = max(0.0, early_alpha - early_beta * price_early)
            remaining = max(0.0, starting_inventory - min(early_demand, starting_inventory))
            replenishment_units = (
                min(max_replenishment_units, max(0.0, storage_capacity - remaining))
                if price_late - replenishment_unit_cost > salvage_value
                else 0.0
            )
        elif self.policy in {"capacity_fill", "fill_capacity", "order_up"}:
            price_early = max(0.0, min(p_max_early, early_alpha / (2.0 * max(early_beta, 1e-9))))
            price_late = max(0.0, min(p_max_late, late_alpha / (2.0 * max(late_beta, 1e-9))))
            early_demand = max(0.0, early_alpha - early_beta * price_early)
            remaining = max(0.0, starting_inventory - min(early_demand, starting_inventory))
            replenishment_units = min(max_replenishment_units, max(0.0, storage_capacity - remaining))
        else:
            price_early, replenishment_units, price_late = _best_inventory_replenishment_plan(
                early_alpha=early_alpha,
                early_beta=early_beta,
                late_alpha=late_alpha,
                late_beta=late_beta,
                p_max_early=p_max_early,
                p_max_late=p_max_late,
                starting_inventory=starting_inventory,
                max_replenishment_units=max_replenishment_units,
                storage_capacity=storage_capacity,
                replenishment_unit_cost=replenishment_unit_cost,
                replenishment_setup_cost=replenishment_setup_cost,
                salvage_value=salvage_value,
            )
        if self.policy == "round":
            price_early = round(price_early / 10.0) * 10.0
            replenishment_units = round(replenishment_units / 10.0) * 10.0
            price_late = round(price_late / 10.0) * 10.0
        return (
            f"FINAL_PRICE_EARLY: {price_early:.2f}\n"
            f"FINAL_REPLENISHMENT_UNITS: {replenishment_units:.2f}\n"
            f"FINAL_PRICE_LATE: {price_late:.2f}"
        )

    def _pricing_hidden_intervention_price(self, user: str) -> str:
        p_max = _extract_float(user, "price_ceiling", _extract_float(user, "p_max", 1e9))
        rows = _extract_intervention_pricing_rows(user)
        if self.policy in {"intervention_blind", "lift_blind", "observed_only"}:
            fit_rows = [(price, observed_units) for price, observed_units, _, _ in rows]
        else:
            fit_rows = [
                (price, (observed_units - intervention_units) / exposure_multiplier)
                for price, observed_units, intervention_units, exposure_multiplier in rows
            ]
        fit = _fit_pricing_rows(fit_rows)
        alpha, beta = fit if fit is not None else (1.0, 1.0)
        price = max(0.0, min(p_max, alpha / (2.0 * max(beta, 1e-9))))
        if self.policy == "round":
            price = round(price / 10.0) * 10.0
        return f"FINAL_PRICE: {price:.2f}"

    def _pricing_law_label(self, user: str) -> str:
        oracle = _pricing_law_label(user)
        if self.policy in {"law_accept", "pricing_law_accept", "always_valid"}:
            label = "valid"
        elif self.policy in {"law_reject", "pricing_law_reject", "always_invalid"}:
            label = "invalid"
        elif self.policy in {"law_invert", "pricing_law_invert"}:
            label = "invalid" if oracle == "valid" else "valid"
        else:
            label = oracle
        return f"FINAL_LABEL: {label}"

    def _pricing_evidence_law_label(self, user: str) -> str:
        oracle = _pricing_evidence_law_label(user)
        if self.policy in {"law_accept", "pricing_law_accept", "always_valid"}:
            label = "valid"
        elif self.policy in {"law_reject", "pricing_law_reject", "always_invalid"}:
            label = "invalid"
        elif self.policy in {"law_invert", "pricing_law_invert"}:
            label = "invalid" if oracle == "valid" else "valid"
        else:
            label = oracle
        return f"FINAL_LABEL: {label}"

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
        elif self.policy in {"literal_claim", "cheap_talk_literal"}:
            price = min(state["buyer_wtp"] for state in states)
        elif self.policy in {"single_cue", "first_cue"}:
            price = _belief_best_price(seller_cost, states, use_posterior=True, signal_count=1)
        else:
            price = _belief_best_price(seller_cost, states, use_posterior=use_posterior)
        return f"FINAL_PRICE: {price:.2f}"

    def _belief_bargain_interaction(self, user: str) -> str:
        seller_cost = _extract_float(user, "seller_cost")
        states = _extract_buyer_states(user)
        if self.policy in {"prior", "ignore_cue"}:
            first, second = _belief_best_interaction_prices(
                seller_cost,
                states,
                user,
                use_posterior=False,
            )
        elif self.policy in {"single_cue", "first_cue"}:
            first, second = _belief_best_interaction_prices(
                seller_cost,
                states,
                user,
                use_posterior=True,
                signal_count=1,
            )
        elif self.policy in {"single_offer", "no_fallback"}:
            first = second = _belief_best_interaction_single_offer(
                seller_cost,
                states,
                user,
                use_posterior=True,
            )
        elif self.policy in {"high_anchor", "max_wtp", "no_concession"}:
            first = second = max(state["buyer_wtp"] for state in states)
        elif self.policy in {"literal_claim", "cheap_talk_literal"}:
            first = second = min(state["buyer_wtp"] for state in states)
        else:
            first, second = _belief_best_interaction_prices(
                seller_cost,
                states,
                user,
                use_posterior=True,
            )
        return f"FINAL_FIRST_PRICE: {first:.2f} FINAL_SECOND_PRICE: {second:.2f}"

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

    def _market_policy_price(self, user: str) -> str:
        base = _extract_float(user, "base_demand")
        shock = _extract_float(user, "demand_shock")
        own_slope = _extract_float(user, "own_price_slope")
        cross_slope = _extract_float(user, "cross_price_slope")
        cost = _extract_float(user, "marginal_cost")
        p_max = _extract_float(user, "p_max", 1e9)
        history = _extract_float_list(user, "opponent_price_history")
        last_opponent = history[-1] if history else _market_policy_static_nash(user)
        predicted_opponent = _market_policy_opponent_price(user)
        denom = 2.0 * own_slope - cross_slope
        static_nash = cost if denom <= 0 else (base + shock + own_slope * cost) / denom
        net_slope = own_slope - cross_slope
        collusive = p_max if net_slope <= 0 else (base + shock + net_slope * cost) / (2.0 * net_slope)
        if self.policy in {"nash", "competitive"}:
            price = static_nash
        elif self.policy in {"last_price", "sticky", "trend_blind"}:
            price = _market_policy_best_response(user, last_opponent)
        elif self.policy in {"collusive", "monopoly"}:
            price = collusive
        elif self.policy in {"cost", "liquidate", "clearance"}:
            price = cost
        else:
            price = _market_policy_best_response(user, predicted_opponent)
        price = max(cost, min(p_max, price))
        return f"FINAL_PRICE: {price:.4f}"

    def _market_policy_inventory_price(self, user: str) -> str:
        cost = _extract_float(user, "marginal_cost")
        p_max = _extract_float(user, "p_max", 1e9)
        history = _extract_float_list(user, "opponent_price_history")
        last_opponent = history[-1] if history else _market_policy_static_nash(user)
        predicted_opponent = _market_policy_opponent_price(user)
        base = _extract_float(user, "base_demand")
        shock = _extract_float(user, "demand_shock")
        own_slope = _extract_float(user, "own_price_slope")
        cross_slope = _extract_float(user, "cross_price_slope")
        denom = 2.0 * own_slope - cross_slope
        static_nash = cost if denom <= 0 else (base + shock + own_slope * cost) / denom
        net_slope = own_slope - cross_slope
        collusive = p_max if net_slope <= 0 else (base + shock + net_slope * cost) / (2.0 * net_slope)
        if self.policy in {"nash", "competitive"}:
            price = static_nash
        elif self.policy in {"last_price", "sticky", "trend_blind"}:
            price = _market_policy_best_response(user, last_opponent)
        elif self.policy in {"inventory_blind", "policy_only"}:
            price = _market_policy_best_response(user, predicted_opponent)
        elif self.policy in {"collusive", "monopoly"}:
            price = collusive
        elif self.policy in {"cost", "liquidate", "clearance"}:
            price = cost
        else:
            price = _best_market_policy_inventory_price(user, predicted_opponent)
        price = max(cost, min(p_max, price))
        return f"FINAL_PRICE: {price:.4f}"

    def _market_trace_inventory_price(self, user: str) -> str:
        cost = _extract_float(user, "marginal_cost")
        p_max = _extract_float(user, "p_max", 1e9)
        history = _extract_market_trace_prices(user)
        last_opponent = history[-1] if history else _market_policy_static_nash(user)
        predicted_opponent = _market_trace_opponent_price(user)
        base = _extract_float(user, "base_demand")
        shock = _extract_float(user, "demand_shock")
        own_slope = _extract_float(user, "own_price_slope")
        cross_slope = _extract_float(user, "cross_price_slope")
        denom = 2.0 * own_slope - cross_slope
        static_nash = cost if denom <= 0 else (base + shock + own_slope * cost) / denom
        net_slope = own_slope - cross_slope
        collusive = p_max if net_slope <= 0 else (base + shock + net_slope * cost) / (2.0 * net_slope)
        if self.policy in {"nash", "competitive"}:
            price = static_nash
        elif self.policy in {"last_price", "sticky"}:
            price = _market_policy_best_response(user, last_opponent)
        elif self.policy in {"trace_blind", "policy_blind", "trend_blind"}:
            price = _best_market_policy_inventory_price(user, last_opponent)
        elif self.policy in {"inventory_blind", "policy_only"}:
            price = _market_policy_best_response(user, predicted_opponent)
        elif self.policy in {"collusive", "monopoly"}:
            price = collusive
        elif self.policy in {"cost", "liquidate", "clearance"}:
            price = cost
        else:
            price = _best_market_policy_inventory_price(user, predicted_opponent)
        price = max(cost, min(p_max, price))
        return f"FINAL_PRICE: {price:.4f}"

    def _market_trace_markdown_prices(self, user: str) -> str:
        cost = _extract_float(user, "marginal_cost")
        p_max = _extract_float(user, "p_max", 1e9)
        history = _extract_market_trace_prices(user)
        last_opponent = history[-1] if history else _market_policy_static_nash(user)
        predicted_opponent = _market_trace_opponent_price(user)
        base = _extract_float(user, "base_demand")
        shock = _extract_float(user, "demand_shock")
        own_slope = _extract_float(user, "own_price_slope")
        cross_slope = _extract_float(user, "cross_price_slope")
        denom = 2.0 * own_slope - cross_slope
        static_nash = cost if denom <= 0 else (base + shock + own_slope * cost) / denom
        if self.policy in {"nash", "competitive"}:
            prices = (static_nash, static_nash)
        elif self.policy in {"last_price", "sticky"}:
            last_price = _market_policy_best_response(user, last_opponent)
            prices = (last_price, last_price)
        elif self.policy in {"trace_blind", "policy_blind", "trend_blind"}:
            prices = _best_market_trace_markdown_prices(user, last_opponent)
        elif self.policy in {"one_price", "fixed_price"}:
            fixed = _best_market_policy_inventory_price(user, predicted_opponent)
            prices = (fixed, fixed)
        elif self.policy in {"inventory_blind", "policy_only"}:
            blind = _market_policy_best_response(user, predicted_opponent)
            prices = (blind, blind)
        elif self.policy in {"cost", "liquidate", "clearance"}:
            prices = (cost, cost)
        else:
            prices = _best_market_trace_markdown_prices(user, predicted_opponent)
        early = max(cost, min(p_max, prices[0]))
        late = max(cost, min(p_max, prices[1]))
        return f"FINAL_PRICE_EARLY: {early:.8f}\nFINAL_PRICE_LATE: {late:.8f}"

    def _market_trace_replenishment_plan(self, user: str) -> str:
        cost = _extract_float(user, "marginal_cost")
        p_max = _extract_float(user, "p_max", 1e9)
        max_units = _extract_float(user, "max_replenishment_units")
        history = _extract_market_trace_prices(user)
        last_opponent = history[-1] if history else _market_policy_static_nash(user)
        predicted_opponent = _market_trace_opponent_price(user)
        if self.policy in {"nash", "competitive"}:
            static = _market_policy_static_nash(user)
            decision = (static, static, 0.0)
        elif self.policy in {"no_replenishment", "no_restock", "order_blind"}:
            prices = _best_market_trace_markdown_prices(user, predicted_opponent)
            decision = (prices[0], prices[1], 0.0)
        elif self.policy in {"one_price", "fixed_price"}:
            decision = _best_market_trace_replenishment_plan(
                user,
                predicted_opponent,
                fixed_price=True,
            )
        elif self.policy in {"trace_blind", "policy_blind", "trend_blind"}:
            decision = _best_market_trace_replenishment_plan(user, last_opponent)
        elif self.policy in {"replenishment_blind", "restock_blind", "always_restock"}:
            decision = _best_market_trace_replenishment_plan(
                user,
                predicted_opponent,
                forced_replenishment=max_units,
            )
        elif self.policy in {"cost", "liquidate", "clearance"}:
            decision = (cost, cost, 0.0)
        else:
            decision = _best_market_trace_replenishment_plan(user, predicted_opponent)
        early = max(cost, min(p_max, decision[0]))
        late = max(cost, min(p_max, decision[1]))
        units = max(0.0, min(max_units, decision[2]))
        return (
            f"FINAL_PRICE_EARLY: {early:.8f}\n"
            f"FINAL_PRICE_LATE: {late:.8f}\n"
            f"FINAL_REPLENISH_UNITS: {units:.8f}"
        )

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

    def _mechanism_repeated_choice(self, user: str) -> str:
        mechanisms = _extract_repeated_mechanisms(user)
        if self.policy in {"revenue", "max_revenue"}:
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["first_period_revenue"])
        elif self.policy in {"one_period", "myopic", "static"}:
            mechanism_id = _best_repeated_mechanism_choice(user, mechanisms, one_period=True)
        elif self.policy in {"risk_blind", "manipulation_blind"}:
            mechanism_id = _best_repeated_mechanism_choice(user, mechanisms, risk_blind=True)
        else:
            mechanism_id = _best_repeated_mechanism_choice(user, mechanisms)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _mechanism_participant_response_choice(self, user: str) -> str:
        mechanisms = _extract_participant_response_mechanisms(user)
        if self.policy in {"revenue", "max_revenue"}:
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["sponsor_take"])
        elif self.policy in {"one_period", "myopic"}:
            mechanism_id = _best_participant_response_mechanism_choice(
                user,
                mechanisms,
                one_period=True,
            )
        elif self.policy in {"response_blind", "static", "retention_blind"}:
            mechanism_id = _best_participant_response_mechanism_choice(
                user,
                mechanisms,
                response_blind=True,
            )
        else:
            mechanism_id = _best_participant_response_mechanism_choice(user, mechanisms)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _mechanism_strategic_response_choice(self, user: str) -> str:
        mechanisms = _extract_strategic_response_mechanisms(user)
        if self.policy in {"revenue", "max_revenue"}:
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["sponsor_take"])
        elif self.policy in {"one_period", "myopic"}:
            mechanism_id = _best_strategic_response_mechanism_choice(
                user,
                mechanisms,
                one_period=True,
            )
        elif self.policy in {"response_blind", "static", "strategic_blind"}:
            mechanism_id = _best_strategic_response_mechanism_choice(
                user,
                mechanisms,
                response_blind=True,
            )
        else:
            mechanism_id = _best_strategic_response_mechanism_choice(user, mechanisms)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _mechanism_strategic_equilibrium_choice(self, user: str) -> str:
        mechanisms = _extract_strategic_response_mechanisms(user)
        if self.policy in {"revenue", "max_revenue"}:
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["sponsor_take"])
        elif self.policy in {"one_period", "myopic"}:
            mechanism_id = _best_strategic_equilibrium_mechanism_choice(
                user,
                mechanisms,
                one_period=True,
            )
        elif self.policy in {"response_blind", "static", "strategic_blind"}:
            mechanism_id = _best_strategic_equilibrium_mechanism_choice(
                user,
                mechanisms,
                response_blind=True,
            )
        else:
            mechanism_id = _best_strategic_equilibrium_mechanism_choice(user, mechanisms)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _mechanism_interaction_trace_choice(self, user: str) -> str:
        mechanisms = _extract_interaction_trace_mechanisms(user)
        if self.policy in {"revenue", "max_revenue"}:
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["sponsor_take"])
        elif self.policy in {"one_period", "myopic"}:
            mechanism_id = _best_interaction_trace_mechanism_choice(
                user,
                mechanisms,
                one_period=True,
            )
        elif self.policy in {"trace_blind", "response_blind", "static", "history_blind"}:
            mechanism_id = _best_interaction_trace_mechanism_choice(
                user,
                mechanisms,
                trace_blind=True,
            )
        else:
            mechanism_id = _best_interaction_trace_mechanism_choice(user, mechanisms)
        return f"FINAL_MECHANISM: {mechanism_id}"

    def _mechanism_trace_equilibrium_choice(self, user: str) -> str:
        mechanisms = _extract_trace_equilibrium_mechanisms(user)
        if self.policy in {"revenue", "max_revenue"}:
            mechanism_id = max(mechanisms, key=lambda item: mechanisms[item]["sponsor_take"])
        elif self.policy in {"trace_projection", "linear_trace", "projection"}:
            mechanism_id = _best_trace_equilibrium_mechanism_choice(
                user,
                mechanisms,
                trace_projection=True,
            )
        elif self.policy in {"equilibrium_blind", "eq_blind", "initial_share"}:
            mechanism_id = _best_trace_equilibrium_mechanism_choice(
                user,
                mechanisms,
                equilibrium_blind=True,
            )
        elif self.policy in {"trace_blind", "history_blind"}:
            mechanism_id = _best_trace_equilibrium_mechanism_choice(
                user,
                mechanisms,
                trace_blind=True,
            )
        else:
            mechanism_id = _best_trace_equilibrium_mechanism_choice(user, mechanisms)
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
        if self.policy not in {"stress_blind", "one_player", "info_blind"}:
            future_loss += _strategic_fragile_posterior(user) * _extract_float(
                user,
                "fragile_extra_loss_per_future_round",
            )
            n_players = _extract_float(user, "n_players", 1.0)
            future_loss += (
                max(0.0, n_players - 1.0)
                * _extract_float(user, "expected_peer_grab_rate")
                * _extract_float(user, "peer_externality_loss_per_future_round")
            )
        future_rounds = _extract_float(user, "remaining_rounds_after_this")
        grab_net = grab - penalty - future_rounds * future_loss
        action = "GRAB" if grab_net > honor else "HONOR"
        return f"FINAL_ACTION: {action}"

    def _forecast_probability(self, user: str) -> str:
        if _has_forecast_operational_log_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"stale_window", "stale", "oldest_window"}:
                probability = _forecast_operational_log_stale_probability(user)
            elif self.policy in {"pooled_history", "pooled", "all_history"}:
                probability = _forecast_operational_log_pooled_probability(user)
            elif self.policy in {"latest_window", "recent_only", "newest_window"}:
                probability = _forecast_operational_log_latest_probability(user)
            elif self.policy in {"policy_blind", "policy_agnostic"}:
                probability = _forecast_operational_log_policy_blind_probability(user)
            elif self.policy in {"route_blind", "route_agnostic"}:
                probability = _forecast_operational_log_route_blind_probability(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_operational_log_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if _has_forecast_event_log_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"stale_window", "stale", "oldest_window"}:
                probability = _forecast_event_log_stale_probability(user)
            elif self.policy in {"pooled_history", "pooled", "all_history"}:
                probability = _forecast_event_log_pooled_probability(user)
            elif self.policy in {"latest_window", "recent_only", "newest_window"}:
                probability = _forecast_event_log_latest_probability(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_event_log_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if _has_forecast_rolling_noisy_log_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"stale_window", "stale", "oldest_window"}:
                probability = _forecast_rolling_noisy_log_stale_probability(user)
            elif self.policy in {"pooled_history", "pooled", "all_history"}:
                probability = _forecast_rolling_noisy_log_pooled_probability(user)
            elif self.policy in {"latest_window", "recent_only", "newest_window"}:
                probability = _forecast_rolling_noisy_log_latest_probability(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_rolling_noisy_log_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if _has_forecast_rolling_log_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"stale_window", "stale", "oldest_window"}:
                probability = _forecast_rolling_log_stale_probability(user)
            elif self.policy in {"pooled_history", "pooled", "all_history"}:
                probability = _forecast_rolling_log_pooled_probability(user)
            elif self.policy in {"latest_window", "recent_only", "newest_window"}:
                probability = _forecast_rolling_log_latest_probability(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_rolling_log_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if _has_forecast_rolling_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"stale_window", "stale", "oldest_window"}:
                probability = _forecast_rolling_stale_probability(user)
            elif self.policy in {"pooled_history", "pooled", "all_history"}:
                probability = _forecast_rolling_pooled_probability(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_rolling_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if _has_forecast_shift_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"source_curve", "source_only"}:
                probability = _forecast_shift_source_probability(user)
            elif self.policy in {"nearest_bridge", "bridge_nearest"}:
                probability = _forecast_shift_nearest_bridge_probability(user)
            elif self.policy in {"bridge_empirical", "no_shrink_bridge"}:
                probability = _forecast_shift_nearest_bridge_empirical(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "source_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_shift_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if _has_forecast_curve_table(user):
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"nearest_bin", "nearest"}:
                probability = _forecast_nearest_curve_bin_probability(user)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_curve_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        if "raw_model_probability=" in user and "observed_event_count=" in user:
            if self.policy in {"raw_score", "uncalibrated"}:
                probability = _extract_float(user, "raw_model_probability")
            elif self.policy in {"empirical_bin", "no_shrink"}:
                total = _extract_float(user, "observed_total", 1.0)
                probability = _extract_float(user, "observed_event_count") / max(total, 1e-9)
            elif self.policy in {"base_rate", "prior", "unconditional"}:
                probability = _extract_float(user, "global_base_rate", _extract_float(user, "base_rate"))
            else:
                probability = _forecast_aggregate_probability(user)
            probability = max(0.0, min(1.0, probability))
            return f"FINAL_PROBABILITY: {probability:.12f}"
        posterior = _forecast_posterior_probability(user)
        base_rate = _extract_float(user, "base_rate")
        if self.policy in {"base_rate", "prior", "unconditional"}:
            probability = base_rate
        elif self.policy in {"underreact", "shrink"}:
            probability = base_rate + 0.25 * (posterior - base_rate)
        elif self.policy in {"raw_likelihood", "reliability_blind"}:
            probability = _forecast_posterior_probability(user, use_reliability=False)
        elif self.policy in {"overconfident", "extreme"}:
            probability = 0.95 if posterior >= base_rate else 0.05
        else:
            probability = posterior
        probability = max(0.0, min(1.0, probability))
        return f"FINAL_PROBABILITY: {probability:.12f}"

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
        values = _experiment_action_values(user, allow_followup=self.policy not in {"single_step", "one_step"})
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
        cash = _extract_float(user, "current_cash", _extract_float(user, "available_cash"))
        reserve = _extract_float(user, "min_cash_reserve", _extract_float(user, "cash_buffer_required"))
        interim_cash_need = _extract_float(
            user,
            "interim_cash_need",
            _extract_float(user, "near_term_obligations_before_delivery"),
        )
        suppliers = _extract_supplier_options(user) or _extract_supplier_natural_options(user)
        credulous = self.policy in {"credulous", "claimed", "high_anchor"}
        timing_blind = self.policy in {"timing_blind", "delay_blind"}
        reputation_blind = self.policy in {"reputation_blind", "history_blind"}
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
            unit_profit = _supplier_unit_profit(
                supplier,
                credulous=credulous,
                timing_blind=timing_blind,
                reputation_blind=reputation_blind,
            )
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


_FLOAT_ALIASES = {
    "base_demand": ("base_customer_flow",),
    "demand_shock": ("demand_adjustment",),
    "own_price_slope": ("own_price_sensitivity",),
    "cross_price_slope": ("rival_price_lift",),
    "marginal_cost": ("sellable_unit_cost",),
    "p_max": ("posted_price_ceiling",),
    "horizon": ("selling_windows",),
    "starting_inventory": ("starting_units",),
    "starting_cash": ("cash_on_hand",),
    "fixed_obligation": ("cash_commitment",),
    "min_terminal_cash": ("cash_reserve_floor",),
    "carrying_cost_per_unsold": ("shelf_cost_per_unsold",),
    "terminal_inventory_value": ("leftover_unit_credit",),
    "replenishment_unit_cost": ("restock_unit_cost",),
    "replenishment_setup_cost": ("restock_setup_fee",),
    "max_replenishment_units": ("restock_unit_limit",),
    "replenishment_storage_capacity": ("storage_ceiling",),
}

_FLOAT_LIST_ALIASES = {
    "demand_shocks": ("window_demand_adjustments",),
}


def _extract_float(text: str, key: str, default: float = 0.0) -> float:
    for candidate in (key, *_FLOAT_ALIASES.get(key, ())):
        match = re.search(rf"{re.escape(candidate)}=([-+]?\d+(?:\.\d+)?)", text)
        if match:
            return float(match.group(1))
    return default


def _extract_word(text: str, key: str, default: str = "") -> str:
    match = re.search(rf"{re.escape(key)}=([a-zA-Z0-9_-]+)", text)
    return match.group(1) if match else default


def _extract_words(text: str, key: str) -> list[str]:
    match = re.search(rf"{re.escape(key)}=([a-zA-Z0-9_,-]+)", text)
    if not match:
        return []
    return [value for value in match.group(1).split(",") if value]


def _extract_procurement_products(text: str) -> dict[str, dict[str, float]]:
    products: dict[str, dict[str, float]] = {}
    product_pattern = re.compile(
        r"product_id=([a-zA-Z0-9_-]+)\s+"
        r"price=([-+]?\d+(?:\.\d+)?)\s+"
        r"durability=([-+]?\d+(?:\.\d+)?)\s+"
        r"comfort=([-+]?\d+(?:\.\d+)?)\s+"
        r"style_fit=([-+]?\d+(?:\.\d+)?)\s+"
        r"assembly_friction=([-+]?\d+(?:\.\d+)?)"
    )
    for match in product_pattern.finditer(text):
        products[match.group(1)] = {
            "price": float(match.group(2)),
            "durability": float(match.group(3)),
            "comfort": float(match.group(4)),
            "style_fit": float(match.group(5)),
            "assembly_friction": float(match.group(6)),
        }
    return products


def _extract_procurement_bundle_products(text: str) -> dict[str, dict[str, float | str]]:
    products: dict[str, dict[str, float | str]] = {}
    product_pattern = re.compile(
        r"product_id=([a-zA-Z0-9_-]+)\s+"
        r"category=([a-zA-Z0-9_-]+)\s+"
        r"price=([-+]?\d+(?:\.\d+)?)\s+"
        r"durability=([-+]?\d+(?:\.\d+)?)\s+"
        r"comfort=([-+]?\d+(?:\.\d+)?)\s+"
        r"style_fit=([-+]?\d+(?:\.\d+)?)\s+"
        r"assembly_friction=([-+]?\d+(?:\.\d+)?)"
    )
    for match in product_pattern.finditer(text):
        products[match.group(1)] = {
            "category": match.group(2),
            "price": float(match.group(3)),
            "durability": float(match.group(4)),
            "comfort": float(match.group(5)),
            "style_fit": float(match.group(6)),
            "assembly_friction": float(match.group(7)),
        }
    return products or _extract_procurement_bundle_natural_products(text)


def _extract_procurement_bundle_natural_products(text: str) -> dict[str, dict[str, float | str]]:
    products: dict[str, dict[str, float | str]] = {}
    product_pattern = re.compile(
        r"sku=([a-zA-Z0-9_-]+)\s+"
        r"line=([a-zA-Z0-9_-]+)\s+"
        r"invoice=([-+]?\d+(?:\.\d+)?)\s+"
        r"field_reliability=([-+]?\d+(?:\.\d+)?)\s+"
        r"operator_fit=([-+]?\d+(?:\.\d+)?)\s+"
        r"presentation_fit=([-+]?\d+(?:\.\d+)?)\s+"
        r"deployment_drag=([-+]?\d+(?:\.\d+)?)"
    )
    for match in product_pattern.finditer(text):
        products[match.group(1)] = {
            "category": match.group(2),
            "price": float(match.group(3)),
            "durability": float(match.group(4)),
            "comfort": float(match.group(5)),
            "style_fit": float(match.group(6)),
            "assembly_friction": float(match.group(7)),
        }
    return products


def _best_procurement_bundle(
    text: str,
    products: dict[str, dict[str, float | str]],
    policy: str,
) -> tuple[str, str]:
    required = set(
        _extract_words(text, "required_categories")
        or _extract_words(text, "must_cover_lines")
    )
    budget = _extract_float(text, "budget", _extract_float(text, "spend_limit", math.inf))
    candidates = []
    for left, right in itertools.combinations(products, 2):
        pair = tuple(sorted((left, right)))
        if policy not in {"category_blind", "coverage_blind"}:
            categories = {str(products[left]["category"]), str(products[right]["category"])}
            if required and not required.issubset(categories):
                continue
        if float(products[left]["price"]) + float(products[right]["price"]) > budget:
            continue
        candidates.append(pair)
    if not candidates:
        candidates = [tuple(sorted(pair)) for pair in itertools.combinations(products, 2)]

    def score(pair: tuple[str, str]) -> float:
        return sum(_procurement_bundle_item_utility(text, products[item]) for item in pair) + (
            0.0
            if policy in {"compatibility_blind", "individual", "top_individual"}
            else _procurement_bundle_compatibility(text, pair)
        )

    return max(candidates, key=score)


def _procurement_bundle_item_utility(text: str, product: dict[str, float | str]) -> float:
    return (
        _extract_float(text, "durability_weight", _extract_float(text, "reliability_weight"))
        * float(product["durability"])
        + _extract_float(text, "comfort_weight", _extract_float(text, "operator_fit_weight"))
        * float(product["comfort"])
        + _extract_float(text, "style_weight", _extract_float(text, "presentation_weight"))
        * float(product["style_fit"])
        - _extract_float(text, "friction_weight", _extract_float(text, "deployment_drag_weight"))
        * float(product["assembly_friction"])
        - _extract_float(text, "price_weight", _extract_float(text, "invoice_penalty"))
        * float(product["price"])
    )


def _procurement_bundle_compatibility(text: str, pair: tuple[str, str]) -> float:
    normalized = set(pair)
    patterns = (
        re.compile(r"pair=([a-zA-Z0-9_-]+),([a-zA-Z0-9_-]+)\s+bonus=([-+]?\d+(?:\.\d+)?)"),
        re.compile(
            r"bundle_pair=([a-zA-Z0-9_-]+),([a-zA-Z0-9_-]+)\s+"
            r"service_fit_delta=([-+]?\d+(?:\.\d+)?)"
        ),
    )
    for pattern in patterns:
        for match in pattern.finditer(text):
            if normalized == {match.group(1), match.group(2)}:
                return float(match.group(3))
    evidence_pattern = re.compile(
        r"pilot_pair=([a-zA-Z0-9_-]+),([a-zA-Z0-9_-]+)\s+"
        r"rollout_hours_delta=([-+]?\d+(?:\.\d+)?)"
    )
    rollout_deltas = []
    for match in evidence_pattern.finditer(text):
        if normalized == {match.group(1), match.group(2)}:
            rollout_deltas.append(float(match.group(3)))
    if rollout_deltas:
        return -(sum(rollout_deltas) / len(rollout_deltas)) / 8.0
    history_pattern = re.compile(
        r"pilot_pair=([a-zA-Z0-9_-]+),([a-zA-Z0-9_-]+)\s+"
        r"rollout_hours_saved=([-+]?\d+(?:\.\d+)?)\s+"
        r"support_tickets_prevented=([-+]?\d+(?:\.\d+)?)\s+"
        r"training_rework_prevented=([-+]?\d+(?:\.\d+)?)"
    )
    history_scores = []
    for match in history_pattern.finditer(text):
        if normalized == {match.group(1), match.group(2)}:
            history_scores.append(
                0.010 * float(match.group(3))
                + 0.040 * float(match.group(4))
                + 0.080 * float(match.group(5))
            )
    if history_scores:
        return sum(history_scores) / len(history_scores)
    reserve_pattern = re.compile(
        r"reserve_pair=([a-zA-Z0-9_-]+),([a-zA-Z0-9_-]+)\s+"
        r"reserve_after_invoice=([-+]?\d+(?:\.\d+)?)\s+"
        r"rollout_hours_saved=([-+]?\d+(?:\.\d+)?)\s+"
        r"expected_support_tickets=([-+]?\d+(?:\.\d+)?)\s+"
        r"tail_probability=([-+]?\d+(?:\.\d+)?)\s+"
        r"tail_support_cost=([-+]?\d+(?:\.\d+)?)"
    )
    reserve_scores = []
    for match in reserve_pattern.finditer(text):
        if normalized == {match.group(1), match.group(2)}:
            reserve_after_invoice = float(match.group(3))
            tail_support_cost = float(match.group(7))
            reserve_scores.append(
                0.010 * float(match.group(4))
                - 0.030 * float(match.group(5))
                - 0.070
                * float(match.group(6))
                * max(0.0, tail_support_cost - reserve_after_invoice)
            )
    if reserve_scores:
        return sum(reserve_scores) / len(reserve_scores)
    return 0.0


def _extract_procurement_vendor_update_vendors(text: str) -> dict[str, dict[str, float]]:
    vendors: dict[str, dict[str, float]] = {}
    vendor_pattern = re.compile(
        r"vendor_id=([a-zA-Z0-9_-]+)\s+"
        r"invoice=([-+]?\d+(?:\.\d+)?)\s+"
        r"operational_fit=([-+]?\d+(?:\.\d+)?)\s+"
        r"shipments_observed=([-+]?\d+(?:\.\d+)?)\s+"
        r"on_time_shipments=([-+]?\d+(?:\.\d+)?)\s+"
        r"late_shipments=([-+]?\d+(?:\.\d+)?)"
    )
    for match in vendor_pattern.finditer(text):
        vendors[match.group(1)] = {
            "invoice": float(match.group(2)),
            "operational_fit": float(match.group(3)),
            "shipments_observed": float(match.group(4)),
            "on_time_shipments": float(match.group(5)),
        }
    if vendors:
        return vendors

    candidate_pattern = re.compile(
        r"vendor_id=([a-zA-Z0-9_-]+)\s+"
        r"invoice=([-+]?\d+(?:\.\d+)?)\s+"
        r"operational_fit=([-+]?\d+(?:\.\d+)?)"
    )
    for match in candidate_pattern.finditer(text):
        vendors[match.group(1)] = {
            "invoice": float(match.group(2)),
            "operational_fit": float(match.group(3)),
            "shipments_observed": 0.0,
            "on_time_shipments": 0.0,
        }

    receiving_pattern = re.compile(
        r"vendor_id=([a-zA-Z0-9_-]+)\s+"
        r"receiving_area=([a-zA-Z0-9_-]+)\s+"
        r"deliveries=([-+]?\d+(?:\.\d+)?)\s+"
        r"on_window_deliveries=([-+]?\d+(?:\.\d+)?)\s+"
        r"late_or_incomplete=([-+]?\d+(?:\.\d+)?)"
    )
    for match in receiving_pattern.finditer(text):
        vendor_id = match.group(1)
        if vendor_id not in vendors:
            continue
        vendors[vendor_id]["shipments_observed"] += float(match.group(3))
        vendors[vendor_id]["on_time_shipments"] += float(match.group(4))
    vendors = {
        vendor_id: vendor
        for vendor_id, vendor in vendors.items()
        if vendor["shipments_observed"] > 0
    }
    return vendors


def _extract_procurement_vendor_update_rounds(text: str) -> list[dict[str, float]]:
    rounds = []
    round_pattern = re.compile(
        r"round=([a-zA-Z0-9_-]+)\s+"
        r"service_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"late_penalty=([-+]?\d+(?:\.\d+)?)"
    )
    for match in round_pattern.finditer(text):
        rounds.append(
            {
                "service_value": float(match.group(2)),
                "late_penalty": float(match.group(3)),
            }
        )
    return rounds


def _vendor_update_reliability(vendor: dict[str, float], *, reputation_blind: bool = False) -> float:
    if reputation_blind:
        return 0.80
    return (vendor["on_time_shipments"] + 2.0) / (vendor["shipments_observed"] + 4.0)


def _vendor_update_round_score(
    vendor: dict[str, float],
    round_case: dict[str, float],
    *,
    reputation_blind: bool = False,
) -> float:
    reliability = _vendor_update_reliability(vendor, reputation_blind=reputation_blind)
    return (
        round_case["service_value"] * vendor["operational_fit"]
        - vendor["invoice"]
        - (1.0 - reliability) * round_case["late_penalty"]
    )


def _procurement_vendor_update_plan_score(
    text: str,
    vendors: dict[str, dict[str, float]],
    rounds: list[dict[str, float]],
    plan: tuple[str, ...],
    *,
    reputation_blind: bool = False,
    include_switch_and_reserve: bool = True,
) -> float:
    cash = _extract_float(text, "starting_reserve", math.inf)
    reserve_floor = _extract_float(text, "reserve_floor", -math.inf)
    reserve_penalty = _extract_float(text, "reserve_penalty", 0.0)
    switch_cost_config = _extract_float(text, "switch_cost", 0.0)
    previous_vendor = None
    score = 0.0
    for vendor_id, round_case in zip(plan, rounds):
        vendor = vendors[vendor_id]
        switch_cost = (
            switch_cost_config
            if include_switch_and_reserve and previous_vendor is not None and previous_vendor != vendor_id
            else 0.0
        )
        cash -= vendor["invoice"] + switch_cost
        score += _vendor_update_round_score(vendor, round_case, reputation_blind=reputation_blind) - switch_cost
        if include_switch_and_reserve:
            score -= reserve_penalty * max(0.0, reserve_floor - cash)
            score -= 4.0 * max(0.0, -cash)
        previous_vendor = vendor_id
    return score


def _best_procurement_vendor_update_plan(
    text: str,
    vendors: dict[str, dict[str, float]],
    rounds: list[dict[str, float]],
    *,
    reputation_blind: bool = False,
) -> tuple[str, ...]:
    vendor_ids = list(vendors)
    return max(
        itertools.product(vendor_ids, repeat=len(rounds)),
        key=lambda plan: _procurement_vendor_update_plan_score(
            text,
            vendors,
            rounds,
            plan,
            reputation_blind=reputation_blind,
        ),
    )


def _myopic_procurement_vendor_update_plan(
    vendors: dict[str, dict[str, float]],
    rounds: list[dict[str, float]],
) -> tuple[str, ...]:
    return tuple(
        max(vendors, key=lambda vendor_id: _vendor_update_round_score(vendors[vendor_id], round_case))
        for round_case in rounds
    )


def _extract_uniform_bounds(text: str) -> tuple[float, float]:
    match = re.search(
        r"value_distribution=Uniform\[([-+]?\d+(?:\.\d+)?),([-+]?\d+(?:\.\d+)?)\]",
        text,
    )
    if not match:
        return 0.0, 1.0
    return float(match.group(1)), float(match.group(2))


def _forecast_posterior_probability(text: str, *, use_reliability: bool = True) -> float:
    base_rate = max(1e-9, min(1.0 - 1e-9, _extract_float(text, "base_rate", 0.5)))
    odds = base_rate / (1.0 - base_rate)
    for line in text.splitlines():
        if "signal_id=" not in line:
            continue
        likelihood_if_event = _extract_float(line, "likelihood_if_event", 1.0)
        likelihood_if_not_event = _extract_float(line, "likelihood_if_not_event", 1.0)
        likelihood_ratio = likelihood_if_event / max(1e-12, likelihood_if_not_event)
        reliability_weight = _extract_float(line, "reliability_weight", 1.0) if use_reliability else 1.0
        odds *= likelihood_ratio ** reliability_weight
    return odds / (1.0 + odds)


def _forecast_aggregate_probability(text: str) -> float:
    event_count = _extract_float(text, "observed_event_count")
    total = _extract_float(text, "observed_total", 1.0)
    global_base_rate = _extract_float(text, "global_base_rate", _extract_float(text, "base_rate", 0.5))
    prior_strength = _extract_float(text, "prior_strength", 0.0)
    return (event_count + prior_strength * global_base_rate) / max(total + prior_strength, 1e-9)


def _interpolate_forecast_points(points: list[tuple[float, float]], raw: float) -> float:
    if not points:
        return raw
    points = sorted(points, key=lambda item: item[0])
    if raw <= points[0][0]:
        return points[0][1]
    if raw >= points[-1][0]:
        return points[-1][1]
    for (left_raw, left_value), (right_raw, right_value) in zip(points, points[1:]):
        if left_raw <= raw <= right_raw:
            weight = (raw - left_raw) / max(right_raw - left_raw, 1e-12)
            return left_value + weight * (right_value - left_value)
    return points[-1][1]


def _has_forecast_operational_log_table(text: str) -> bool:
    return "operational_log_item=" in text and "policy=" in text and "route=" in text


def _forecast_operational_log_half_life(text: str) -> float:
    return _forecast_event_log_half_life(text)


def _extract_forecast_operational_log_entries(text: str) -> list[dict[str, float | str | bool]]:
    entries: list[dict[str, float | str | bool]] = []
    for line in text.splitlines():
        if "operational_log_item=" not in line:
            continue
        outcome = _extract_word(line, "outcome", "no_event")
        entries.append(
            {
                "score": _extract_float(line, "score"),
                "days": _extract_float(line, "age_days", 0.0),
                "policy": _extract_word(line, "policy"),
                "route": _extract_word(line, "route"),
                "event": outcome in {"event", "yes", "true", "1"},
            }
        )
    return entries


def _forecast_operational_log_entry_weight(
    text: str,
    entry: dict[str, float | str | bool],
    *,
    use_recency: bool = True,
    require_policy: bool = True,
    require_route: bool = True,
) -> float:
    if require_policy and entry["policy"] != _extract_word(text, "current_policy"):
        return 0.0
    if require_route and entry["route"] != _extract_word(text, "current_route"):
        return 0.0
    raw = _extract_float(text, "raw_model_probability", 0.5)
    score = float(entry["score"])
    score_width = 0.11
    score_distance = (score - raw) / max(score_width, 1e-9)
    score_weight = math.exp(-0.5 * score_distance * score_distance)
    if not use_recency:
        return score_weight
    age = max(float(entry["days"]), 0.0)
    return score_weight * (0.5 ** (age / max(_forecast_operational_log_half_life(text), 1e-9)))


def _forecast_operational_log_probability_from_entries(
    text: str,
    entries: list[dict[str, float | str | bool]],
    *,
    use_recency: bool = True,
    require_policy: bool = True,
    require_route: bool = True,
) -> float:
    global_base_rate = _extract_float(text, "global_base_rate", _extract_float(text, "base_rate", 0.5))
    prior_strength = _extract_float(text, "prior_strength", 0.0)
    weighted_events = sum(
        _forecast_operational_log_entry_weight(
            text,
            entry,
            use_recency=use_recency,
            require_policy=require_policy,
            require_route=require_route,
        )
        * float(bool(entry["event"]))
        for entry in entries
    )
    weighted_total = sum(
        _forecast_operational_log_entry_weight(
            text,
            entry,
            use_recency=use_recency,
            require_policy=require_policy,
            require_route=require_route,
        )
        for entry in entries
    )
    return (weighted_events + prior_strength * global_base_rate) / max(
        weighted_total + prior_strength,
        1e-9,
    )


def _forecast_operational_log_probability(text: str) -> float:
    entries = _extract_forecast_operational_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_operational_log_probability_from_entries(text, entries, use_recency=True)


def _forecast_operational_log_pooled_probability(text: str) -> float:
    entries = _extract_forecast_operational_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_operational_log_probability_from_entries(
        text,
        entries,
        use_recency=False,
        require_policy=False,
        require_route=False,
    )


def _forecast_operational_log_policy_blind_probability(text: str) -> float:
    entries = _extract_forecast_operational_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_operational_log_probability_from_entries(
        text,
        entries,
        use_recency=True,
        require_policy=False,
        require_route=True,
    )


def _forecast_operational_log_route_blind_probability(text: str) -> float:
    entries = _extract_forecast_operational_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_operational_log_probability_from_entries(
        text,
        entries,
        use_recency=True,
        require_policy=True,
        require_route=False,
    )


def _forecast_operational_log_context_entries(
    entries: list[dict[str, float | str | bool]],
    text: str,
) -> list[dict[str, float | str | bool]]:
    current_policy = _extract_word(text, "current_policy")
    current_route = _extract_word(text, "current_route")
    return [
        entry
        for entry in entries
        if entry["policy"] == current_policy and entry["route"] == current_route
    ]


def _forecast_operational_log_stale_probability(text: str) -> float:
    entries = _forecast_operational_log_context_entries(
        _extract_forecast_operational_log_entries(text),
        text,
    )
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    half_life = _forecast_operational_log_half_life(text)
    stale_entries = [entry for entry in entries if float(entry["days"]) >= 2.0 * half_life]
    if not stale_entries:
        oldest = max(float(entry["days"]) for entry in entries)
        stale_entries = [entry for entry in entries if float(entry["days"]) == oldest]
    return _forecast_operational_log_probability_from_entries(text, stale_entries, use_recency=False)


def _forecast_operational_log_latest_probability(text: str) -> float:
    entries = _forecast_operational_log_context_entries(
        _extract_forecast_operational_log_entries(text),
        text,
    )
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    half_life = _forecast_operational_log_half_life(text)
    latest_entries = [entry for entry in entries if float(entry["days"]) <= 0.5 * half_life]
    if not latest_entries:
        latest = min(float(entry["days"]) for entry in entries)
        latest_entries = [entry for entry in entries if float(entry["days"]) == latest]
    return _forecast_operational_log_probability_from_entries(text, latest_entries, use_recency=False)


def _has_forecast_event_log_table(text: str) -> bool:
    return "event_log_item=" in text and "outcome=" in text


def _forecast_event_log_half_life(text: str) -> float:
    cadence = _extract_word(text, "review_cadence", "monthly")
    if cadence == "biweekly":
        return 21.0
    if cadence == "six_week":
        return 45.0
    if cadence == "quarterly":
        return 90.0
    return 30.0


def _extract_forecast_event_log_entries(text: str) -> list[dict[str, float | bool]]:
    entries: list[dict[str, float | bool]] = []
    for line in text.splitlines():
        if "event_log_item=" not in line:
            continue
        outcome = _extract_word(line, "outcome", "no_event")
        entries.append(
            {
                "score": _extract_float(line, "score"),
                "days": _extract_float(line, "age_days", 0.0),
                "event": outcome in {"event", "yes", "true", "1"},
            }
        )
    return entries


def _forecast_event_log_entry_weight(
    text: str,
    entry: dict[str, float | bool],
    *,
    use_recency: bool = True,
) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5)
    score = float(entry["score"])
    score_width = 0.12
    score_distance = (score - raw) / max(score_width, 1e-9)
    score_weight = math.exp(-0.5 * score_distance * score_distance)
    if not use_recency:
        return score_weight
    age = max(float(entry["days"]), 0.0)
    return score_weight * (0.5 ** (age / max(_forecast_event_log_half_life(text), 1e-9)))


def _forecast_event_log_probability_from_entries(
    text: str,
    entries: list[dict[str, float | bool]],
    *,
    use_recency: bool = True,
) -> float:
    global_base_rate = _extract_float(text, "global_base_rate", _extract_float(text, "base_rate", 0.5))
    prior_strength = _extract_float(text, "prior_strength", 0.0)
    weighted_events = sum(
        _forecast_event_log_entry_weight(text, entry, use_recency=use_recency)
        * float(bool(entry["event"]))
        for entry in entries
    )
    weighted_total = sum(
        _forecast_event_log_entry_weight(text, entry, use_recency=use_recency)
        for entry in entries
    )
    return (weighted_events + prior_strength * global_base_rate) / max(
        weighted_total + prior_strength,
        1e-9,
    )


def _forecast_event_log_probability(text: str) -> float:
    entries = _extract_forecast_event_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_event_log_probability_from_entries(text, entries, use_recency=True)


def _forecast_event_log_pooled_probability(text: str) -> float:
    entries = _extract_forecast_event_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_event_log_probability_from_entries(text, entries, use_recency=False)


def _forecast_event_log_stale_probability(text: str) -> float:
    entries = _extract_forecast_event_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    half_life = _forecast_event_log_half_life(text)
    stale_entries = [entry for entry in entries if float(entry["days"]) >= 2.0 * half_life]
    if not stale_entries:
        oldest = max(float(entry["days"]) for entry in entries)
        stale_entries = [entry for entry in entries if float(entry["days"]) == oldest]
    return _forecast_event_log_probability_from_entries(text, stale_entries, use_recency=False)


def _forecast_event_log_latest_probability(text: str) -> float:
    entries = _extract_forecast_event_log_entries(text)
    if not entries:
        return _extract_float(text, "raw_model_probability", 0.5)
    half_life = _forecast_event_log_half_life(text)
    latest_entries = [entry for entry in entries if float(entry["days"]) <= 0.5 * half_life]
    if not latest_entries:
        latest = min(float(entry["days"]) for entry in entries)
        latest_entries = [entry for entry in entries if float(entry["days"]) == latest]
    return _forecast_event_log_probability_from_entries(text, latest_entries, use_recency=False)


def _has_forecast_rolling_noisy_log_table(text: str) -> bool:
    return "cohort_review=" in text and "score_band=" in text


def _extract_forecast_rolling_noisy_log_periods(text: str) -> list[dict[str, object]]:
    periods: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in text.splitlines():
        if "cohort_review=" in line:
            current = {
                "days_before_target_midpoint": _extract_float(line, "age_days", 0.0),
                "points": [],
            }
            periods.append(current)
            continue
        if "score_band=" in line and current is not None:
            points = current["points"]
            assert isinstance(points, list)
            points.append(
                (
                    _extract_float(line, "score_center"),
                    _extract_float(line, "events"),
                    _extract_float(line, "reviewed", _extract_float(line, "total", 1.0)),
                )
            )
    return periods


def _forecast_rolling_noisy_log_half_life(text: str) -> float:
    cadence = _extract_word(text, "review_cadence", "monthly")
    if cadence == "biweekly":
        return 21.0
    if cadence == "six_week":
        return 45.0
    if cadence == "quarterly":
        return 90.0
    return 30.0


def _forecast_rolling_noisy_log_period_weight(text: str, period: dict[str, object]) -> float:
    half_life = max(_forecast_rolling_noisy_log_half_life(text), 1e-9)
    age = max(float(period.get("days_before_target_midpoint", 0.0)), 0.0)
    return 0.5 ** (age / half_life)


def _forecast_rolling_noisy_log_bin_probability(text: str, events: float, total: float) -> float:
    global_base_rate = _extract_float(text, "global_base_rate", _extract_float(text, "base_rate", 0.5))
    prior_strength = _extract_float(text, "prior_strength", 0.0)
    return (events + prior_strength * global_base_rate) / max(total + prior_strength, 1e-9)


def _forecast_rolling_noisy_log_period_probability(
    text: str,
    period: dict[str, object],
    *,
    raw: float | None = None,
) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5) if raw is None else raw
    raw_points = period.get("points", [])
    assert isinstance(raw_points, list)
    points = [
        (score, _forecast_rolling_noisy_log_bin_probability(text, events, total))
        for score, events, total in raw_points
    ]
    return _interpolate_forecast_points(points, raw)


def _forecast_rolling_noisy_log_probability(text: str) -> float:
    periods = _extract_forecast_rolling_noisy_log_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    weights = [_forecast_rolling_noisy_log_period_weight(text, period) for period in periods]
    total_weight = sum(weights)
    if total_weight <= 0:
        return _forecast_rolling_noisy_log_pooled_probability(text)
    return sum(
        weight * _forecast_rolling_noisy_log_period_probability(text, period)
        for weight, period in zip(weights, periods)
    ) / total_weight


def _forecast_rolling_noisy_log_stale_probability(text: str) -> float:
    periods = _extract_forecast_rolling_noisy_log_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    stale = max(periods, key=lambda period: float(period.get("days_before_target_midpoint", 0.0)))
    return _forecast_rolling_noisy_log_period_probability(text, stale)


def _forecast_rolling_noisy_log_latest_probability(text: str) -> float:
    periods = _extract_forecast_rolling_noisy_log_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    latest = min(periods, key=lambda period: float(period.get("days_before_target_midpoint", 0.0)))
    return _forecast_rolling_noisy_log_period_probability(text, latest)


def _forecast_rolling_noisy_log_pooled_probability(text: str) -> float:
    pooled: dict[float, list[float]] = {}
    for period in _extract_forecast_rolling_noisy_log_periods(text):
        raw_points = period.get("points", [])
        assert isinstance(raw_points, list)
        for score, events, total in raw_points:
            row = pooled.setdefault(score, [0.0, 0.0])
            row[0] += events
            row[1] += total
    raw = _extract_float(text, "raw_model_probability", 0.5)
    points = [
        (score, _forecast_rolling_noisy_log_bin_probability(text, events, total))
        for score, (events, total) in pooled.items()
    ]
    return _interpolate_forecast_points(points, raw)


def _has_forecast_rolling_log_table(text: str) -> bool:
    return "outcome_batch=" in text and "outcome_slice=" in text


def _extract_forecast_rolling_log_periods(text: str) -> list[dict[str, object]]:
    periods: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in text.splitlines():
        if "outcome_batch=" in line:
            current = {
                "days_before_target_midpoint": _extract_float(
                    line,
                    "days_before_target_midpoint",
                    0.0,
                ),
                "points": [],
            }
            periods.append(current)
            continue
        if "outcome_slice=" in line and current is not None:
            points = current["points"]
            assert isinstance(points, list)
            points.append(
                (
                    _extract_float(line, "score_center"),
                    _extract_float(line, "events"),
                    _extract_float(line, "total", 1.0),
                )
            )
    return periods


def _forecast_rolling_log_period_weight(text: str, period: dict[str, object]) -> float:
    half_life = max(_extract_float(text, "recency_half_life_days", 45.0), 1e-9)
    age = max(float(period.get("days_before_target_midpoint", 0.0)), 0.0)
    return 0.5 ** (age / half_life)


def _forecast_rolling_log_period_probability(
    text: str,
    period: dict[str, object],
    *,
    raw: float | None = None,
) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5) if raw is None else raw
    raw_points = period.get("points", [])
    assert isinstance(raw_points, list)
    points = [
        (score, _forecast_rolling_bin_probability(text, events, total))
        for score, events, total in raw_points
    ]
    return _interpolate_forecast_points(points, raw)


def _forecast_rolling_log_probability(text: str) -> float:
    periods = _extract_forecast_rolling_log_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    weights = [_forecast_rolling_log_period_weight(text, period) for period in periods]
    total_weight = sum(weights)
    if total_weight <= 0:
        return _forecast_rolling_log_pooled_probability(text)
    return sum(
        weight * _forecast_rolling_log_period_probability(text, period)
        for weight, period in zip(weights, periods)
    ) / total_weight


def _forecast_rolling_log_stale_probability(text: str) -> float:
    periods = _extract_forecast_rolling_log_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    stale = max(periods, key=lambda period: float(period.get("days_before_target_midpoint", 0.0)))
    return _forecast_rolling_log_period_probability(text, stale)


def _forecast_rolling_log_latest_probability(text: str) -> float:
    periods = _extract_forecast_rolling_log_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    latest = min(periods, key=lambda period: float(period.get("days_before_target_midpoint", 0.0)))
    return _forecast_rolling_log_period_probability(text, latest)


def _forecast_rolling_log_pooled_probability(text: str) -> float:
    pooled: dict[float, list[float]] = {}
    for period in _extract_forecast_rolling_log_periods(text):
        raw_points = period.get("points", [])
        assert isinstance(raw_points, list)
        for score, events, total in raw_points:
            row = pooled.setdefault(score, [0.0, 0.0])
            row[0] += events
            row[1] += total
    raw = _extract_float(text, "raw_model_probability", 0.5)
    points = [
        (score, _forecast_rolling_bin_probability(text, events, total))
        for score, (events, total) in pooled.items()
    ]
    return _interpolate_forecast_points(points, raw)


def _has_forecast_rolling_table(text: str) -> bool:
    return "rolling_period=" in text and "period_bin=" in text


def _extract_forecast_rolling_periods(text: str) -> list[dict[str, object]]:
    periods: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for line in text.splitlines():
        if "rolling_period=" in line:
            current = {
                "weight": _extract_float(line, "recency_weight", 1.0),
                "points": [],
            }
            periods.append(current)
            continue
        if "period_bin=" in line and current is not None:
            points = current["points"]
            assert isinstance(points, list)
            points.append(
                (
                    _extract_float(line, "score_center"),
                    _extract_float(line, "events"),
                    _extract_float(line, "total", 1.0),
                )
            )
    return periods


def _forecast_rolling_bin_probability(text: str, events: float, total: float) -> float:
    global_base_rate = _extract_float(text, "global_base_rate", _extract_float(text, "base_rate", 0.5))
    prior_strength = _extract_float(text, "prior_strength", 0.0)
    return (events + prior_strength * global_base_rate) / max(total + prior_strength, 1e-9)


def _forecast_rolling_period_probability(
    text: str,
    period: dict[str, object],
    *,
    raw: float | None = None,
) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5) if raw is None else raw
    raw_points = period.get("points", [])
    assert isinstance(raw_points, list)
    points = [
        (score, _forecast_rolling_bin_probability(text, events, total))
        for score, events, total in raw_points
    ]
    return _interpolate_forecast_points(points, raw)


def _forecast_rolling_probability(text: str) -> float:
    periods = _extract_forecast_rolling_periods(text)
    weights = [float(period.get("weight", 1.0)) for period in periods]
    total_weight = sum(weights)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    if total_weight <= 0:
        return _forecast_rolling_pooled_probability(text)
    return sum(
        weight * _forecast_rolling_period_probability(text, period)
        for weight, period in zip(weights, periods)
    ) / total_weight


def _forecast_rolling_stale_probability(text: str) -> float:
    periods = _extract_forecast_rolling_periods(text)
    if not periods:
        return _extract_float(text, "raw_model_probability", 0.5)
    return _forecast_rolling_period_probability(text, periods[0])


def _forecast_rolling_pooled_probability(text: str) -> float:
    pooled: dict[float, list[float]] = {}
    for period in _extract_forecast_rolling_periods(text):
        raw_points = period.get("points", [])
        assert isinstance(raw_points, list)
        for score, events, total in raw_points:
            row = pooled.setdefault(score, [0.0, 0.0])
            row[0] += events
            row[1] += total
    raw = _extract_float(text, "raw_model_probability", 0.5)
    points = [
        (score, _forecast_rolling_bin_probability(text, events, total))
        for score, (events, total) in pooled.items()
    ]
    return _interpolate_forecast_points(points, raw)


def _has_forecast_shift_table(text: str) -> bool:
    return "source_bin=" in text and "target_bridge=" in text


def _extract_forecast_shift_source_points(text: str) -> list[tuple[float, float]]:
    source_base_rate = _extract_float(text, "source_base_rate", _extract_float(text, "base_rate", 0.5))
    source_prior_strength = _extract_float(text, "source_prior_strength", 0.0)
    points: list[tuple[float, float]] = []
    for line in text.splitlines():
        if "source_bin=" not in line:
            continue
        raw = _extract_float(line, "score_center")
        events = _extract_float(line, "events")
        total = _extract_float(line, "total", 1.0)
        probability = (events + source_prior_strength * source_base_rate) / max(
            total + source_prior_strength,
            1e-9,
        )
        points.append((raw, probability))
    points.sort(key=lambda item: item[0])
    return points


def _forecast_shift_source_probability(text: str, raw: float | None = None) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5) if raw is None else raw
    return _interpolate_forecast_points(_extract_forecast_shift_source_points(text), raw)


def _extract_forecast_shift_bridge_points(text: str) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for line in text.splitlines():
        if "target_bridge=" not in line:
            continue
        raw = _extract_float(line, "score_center")
        events = _extract_float(line, "events")
        total = _extract_float(line, "total", 1.0)
        points.append((raw, events, total))
    points.sort(key=lambda item: item[0])
    return points


def _forecast_shift_adjusted_bridge_probability(text: str, raw: float, events: float, total: float) -> float:
    source_probability = _forecast_shift_source_probability(text, raw)
    bridge_prior_strength = _extract_float(text, "bridge_prior_strength", 0.0)
    return (events + bridge_prior_strength * source_probability) / max(
        total + bridge_prior_strength,
        1e-9,
    )


def _forecast_shift_probability(text: str) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5)
    source_at_raw = _forecast_shift_source_probability(text, raw)
    shifts = [
        (
            bridge_raw,
            _forecast_shift_adjusted_bridge_probability(text, bridge_raw, events, total)
            - _forecast_shift_source_probability(text, bridge_raw),
        )
        for bridge_raw, events, total in _extract_forecast_shift_bridge_points(text)
    ]
    shift = _interpolate_forecast_points(shifts, raw) if shifts else 0.0
    return source_at_raw + shift


def _forecast_shift_nearest_bridge_probability(text: str) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5)
    bridge_points = _extract_forecast_shift_bridge_points(text)
    if not bridge_points:
        return _forecast_shift_source_probability(text, raw)
    bridge_raw, events, total = min(bridge_points, key=lambda point: abs(point[0] - raw))
    return _forecast_shift_adjusted_bridge_probability(text, bridge_raw, events, total)


def _forecast_shift_nearest_bridge_empirical(text: str) -> float:
    raw = _extract_float(text, "raw_model_probability", 0.5)
    bridge_points = _extract_forecast_shift_bridge_points(text)
    if not bridge_points:
        return _forecast_shift_source_probability(text, raw)
    _, events, total = min(bridge_points, key=lambda point: abs(point[0] - raw))
    return events / max(total, 1e-9)


def _has_forecast_curve_table(text: str) -> bool:
    has_raw_mean = "raw_mean_probability=" in text or "score_center=" in text
    has_count = "observed_event_count=" in text or "events=" in text
    return has_raw_mean and has_count


def _extract_forecast_curve_bins(text: str) -> list[tuple[float, float]]:
    global_base_rate = _extract_float(text, "global_base_rate", _extract_float(text, "base_rate", 0.5))
    prior_strength = _extract_float(text, "prior_strength", 0.0)
    points: list[tuple[float, float]] = []
    for line in text.splitlines():
        if "raw_mean_probability=" not in line and "score_center=" not in line:
            continue
        raw_mean = _extract_float(line, "raw_mean_probability", _extract_float(line, "score_center"))
        event_count = _extract_float(line, "observed_event_count", _extract_float(line, "events"))
        total = _extract_float(line, "observed_total", _extract_float(line, "total", 1.0))
        probability = (event_count + prior_strength * global_base_rate) / max(total + prior_strength, 1e-9)
        points.append((raw_mean, probability))
    points.sort(key=lambda item: item[0])
    return points


def _forecast_curve_probability(text: str) -> float:
    points = _extract_forecast_curve_bins(text)
    if not points:
        return _extract_float(text, "raw_model_probability", 0.5)
    raw = _extract_float(text, "raw_model_probability", points[0][0])
    if raw <= points[0][0]:
        return points[0][1]
    if raw >= points[-1][0]:
        return points[-1][1]
    for (left_raw, left_prob), (right_raw, right_prob) in zip(points, points[1:]):
        if left_raw <= raw <= right_raw:
            weight = (raw - left_raw) / max(right_raw - left_raw, 1e-12)
            return left_prob + weight * (right_prob - left_prob)
    return points[-1][1]


def _forecast_nearest_curve_bin_probability(text: str) -> float:
    points = _extract_forecast_curve_bins(text)
    if not points:
        return _extract_float(text, "raw_model_probability", 0.5)
    raw = _extract_float(text, "raw_model_probability", points[0][0])
    return min(points, key=lambda item: abs(item[0] - raw))[1]


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


def _market_policy_static_nash(text: str) -> float:
    base = _extract_float(text, "base_demand")
    shock = _extract_float(text, "demand_shock")
    own_slope = _extract_float(text, "own_price_slope")
    cross_slope = _extract_float(text, "cross_price_slope")
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    denom = 2.0 * own_slope - cross_slope
    price = cost if denom <= 0 else (base + shock + own_slope * cost) / denom
    return max(cost, min(p_max, price))


def _market_policy_best_response(text: str, opponent_price: float) -> float:
    base = _extract_float(text, "base_demand")
    shock = _extract_float(text, "demand_shock")
    own_slope = _extract_float(text, "own_price_slope")
    cross_slope = _extract_float(text, "cross_price_slope")
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    price = (base + shock + cross_slope * opponent_price + own_slope * cost) / (
        2.0 * own_slope
    )
    return max(cost, min(p_max, price))


def _market_policy_opponent_price(text: str) -> float:
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    history = _extract_float_list(text, "opponent_price_history")
    if not history:
        return _market_policy_static_nash(text)
    if len(history) == 1:
        return max(cost, min(p_max, history[-1]))
    policy = _extract_word(text, "opponent_policy")
    last = history[-1]
    step = last - history[-2]
    if policy == "liquidation_drop":
        price = last + 1.5 * step
    elif policy == "stockout_jump":
        price = last + 1.5 * max(0.0, step)
    elif policy == "entry_price_war":
        price = last + 1.5 * step
    elif policy == "capacity_exit":
        price = last + 2.0 * max(0.0, step)
    else:
        price = last
    return max(cost, min(p_max, price))


def _extract_market_trace_prices(text: str) -> list[float]:
    prices = []
    for line in text.splitlines():
        if "trace period=" in line and "opponent_price=" in line:
            prices.append(_extract_float(line, "opponent_price"))
        elif "rival_observation" in line and "rival_ticket=" in line:
            prices.append(_extract_float(line, "rival_ticket"))
    return prices


def _extract_market_trace_points(text: str) -> list[tuple[float, float, float]]:
    points = []
    for line in text.splitlines():
        if "trace period=" in line and "opponent_price=" in line:
            points.append(
                (
                    _extract_float(line, "opponent_price"),
                    _extract_float(line, "opponent_fill_rate", 1.0),
                    _extract_float(line, "opponent_remaining_inventory_share", 0.0),
                )
            )
        elif "rival_observation" in line and "rival_ticket=" in line:
            points.append(
                (
                    _extract_float(line, "rival_ticket"),
                    _extract_float(line, "sell_through", 1.0),
                    _extract_float(line, "shelf_left", 0.0),
                )
            )
    return points


def _market_trace_opponent_price(text: str) -> float:
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    points = _extract_market_trace_points(text)
    if not points:
        return _market_policy_static_nash(text)
    if len(points) == 1:
        return max(cost, min(p_max, points[-1][0]))
    last_price, last_fill_rate, last_remaining_share = points[-1]
    previous_price = points[-2][0]
    step = last_price - previous_price
    stockout_pressure = max(0.0, 0.82 - last_fill_rate)
    clearance_pressure = max(0.0, last_remaining_share - 0.65)
    price = (
        last_price
        + 1.35 * step
        + 35.0 * stockout_pressure
        - 30.0 * clearance_pressure
    )
    return max(cost, min(p_max, price))


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


def _market_policy_inventory_terminal_cash(text: str, price: float, other_price: float) -> float:
    base = _extract_float(text, "base_demand")
    shock = _extract_float(text, "demand_shock")
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
        period_shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            base + shock + period_shock - own_slope * price + cross_slope * other_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, price - cost) * sold
        inventory -= sold
        cash -= carrying_cost * inventory
    cash += terminal_value * inventory
    cash -= fixed_obligation
    return cash


def _market_trace_markdown_terminal_cash(
    text: str,
    early_price: float,
    late_price: float,
    other_price: float,
) -> float:
    base = _extract_float(text, "base_demand")
    shock = _extract_float(text, "demand_shock")
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
    switch_period = max(1, horizon // 2)
    for period in range(max(1, horizon)):
        price = early_price if period < switch_period else late_price
        period_shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            base + shock + period_shock - own_slope * price + cross_slope * other_price,
        )
        sold = min(inventory, demand)
        cash += max(0.0, price - cost) * sold
        inventory -= sold
        cash -= carrying_cost * inventory
    cash += terminal_value * inventory
    cash -= fixed_obligation
    return cash


def _market_trace_replenishment_terminal_cash(
    text: str,
    early_price: float,
    late_price: float,
    replenishment_units: float,
    other_price: float,
) -> float:
    base = _extract_float(text, "base_demand")
    shock = _extract_float(text, "demand_shock")
    own_slope = _extract_float(text, "own_price_slope")
    cross_slope = _extract_float(text, "cross_price_slope")
    cost = _extract_float(text, "marginal_cost")
    horizon = int(round(_extract_float(text, "horizon", 1.0)))
    inventory = _extract_float(text, "starting_inventory")
    cash = _extract_float(text, "starting_cash")
    carrying_cost = _extract_float(text, "carrying_cost_per_unsold")
    terminal_value = _extract_float(text, "terminal_inventory_value")
    fixed_obligation = _extract_float(text, "fixed_obligation")
    unit_cost = _extract_float(text, "replenishment_unit_cost")
    setup_cost = _extract_float(text, "replenishment_setup_cost")
    max_units = _extract_float(text, "max_replenishment_units")
    storage_capacity = _extract_float(
        text,
        "replenishment_storage_capacity",
        inventory + max_units,
    )
    shocks = _extract_float_list(text, "demand_shocks")
    switch_period = max(1, horizon // 2)
    for period in range(max(1, horizon)):
        if period == switch_period and replenishment_units > 0:
            received_units = min(
                replenishment_units,
                max(0.0, storage_capacity - inventory),
            )
            if received_units > 0:
                inventory += received_units
                cash -= unit_cost * received_units + setup_cost
        price = early_price if period < switch_period else late_price
        period_shock = shocks[period] if period < len(shocks) else 0.0
        demand = max(
            0.0,
            base + shock + period_shock - own_slope * price + cross_slope * other_price,
        )
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


def _best_market_policy_inventory_price(text: str, other_price: float) -> float:
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    candidates = {
        cost,
        p_max,
        _market_policy_static_nash(text),
        _market_policy_best_response(text, other_price),
    }
    history = _extract_float_list(text, "opponent_price_history")
    if history:
        candidates.add(_market_policy_best_response(text, history[-1]))
    for price in range(int(cost), int(p_max) + 1):
        candidates.add(float(price))
    reference = _market_policy_best_response(text, other_price)
    return max(
        sorted(candidates),
        key=lambda price: (
            _market_policy_inventory_terminal_cash(text, price, other_price),
            -abs(price - reference),
        ),
    )


def _best_market_trace_markdown_prices(text: str, other_price: float) -> tuple[float, float]:
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    candidates = {
        cost,
        p_max,
        _market_policy_static_nash(text),
        _market_policy_best_response(text, other_price),
        _best_market_policy_inventory_price(text, other_price),
    }
    history = _extract_market_trace_prices(text)
    if history:
        candidates.add(_market_policy_best_response(text, history[-1]))
    for price in range(int(cost), int(p_max) + 1):
        candidates.add(float(price))
    reference = _market_policy_best_response(text, other_price)
    pairs = ((early, late) for early in candidates for late in candidates)
    return max(
        pairs,
        key=lambda pair: (
            _market_trace_markdown_terminal_cash(text, pair[0], pair[1], other_price),
            -abs(pair[0] - reference) - abs(pair[1] - reference),
        ),
    )


def _best_market_trace_replenishment_plan(
    text: str,
    other_price: float,
    *,
    forced_replenishment: float | None = None,
    fixed_price: bool = False,
) -> tuple[float, float, float]:
    cost = _extract_float(text, "marginal_cost")
    p_max = _extract_float(text, "p_max", cost)
    max_units = _extract_float(text, "max_replenishment_units")
    candidates = {
        cost,
        p_max,
        _market_policy_static_nash(text),
        _market_policy_best_response(text, other_price),
        _best_market_policy_inventory_price(text, other_price),
    }
    history = _extract_market_trace_prices(text)
    if history:
        candidates.add(_market_policy_best_response(text, history[-1]))
    for price in range(int(cost), int(p_max) + 1):
        candidates.add(float(price))
    replenishment_candidates = (
        [max(0.0, min(max_units, forced_replenishment))]
        if forced_replenishment is not None
        else _market_trace_replenishment_candidate_units(text)
    )
    reference = _best_market_trace_markdown_prices(text, other_price)
    if fixed_price:
        decisions = (
            (price, price, units)
            for price in candidates
            for units in replenishment_candidates
        )
    else:
        decisions = (
            (early, late, units)
            for early in candidates
            for late in candidates
            for units in replenishment_candidates
        )
    return max(
        decisions,
        key=lambda decision: (
            _market_trace_replenishment_terminal_cash(
                text,
                decision[0],
                decision[1],
                decision[2],
                other_price,
            ),
            -abs(decision[0] - reference[0])
            - abs(decision[1] - reference[1])
            - 0.25 * abs(decision[2]),
        ),
    )


def _market_trace_replenishment_candidate_units(text: str) -> list[float]:
    max_units = _extract_float(text, "max_replenishment_units")
    if max_units <= 0:
        return [0.0]
    candidates = {0.0, max_units, max_units / 2.0}
    return sorted(max(0.0, min(max_units, units)) for units in candidates)


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


_PRINCIPAL_STYLE_WEIGHTS = {
    "quality_defensive": {
        "expected_return": 0.70,
        "quality": 1.45,
        "value": 0.35,
        "momentum": 0.10,
        "volatility": -1.15,
        "turnover_cost": -0.95,
        "concentration_delta": -0.75,
        "liquidity": 0.45,
    },
    "growth_momentum": {
        "expected_return": 1.25,
        "quality": 0.45,
        "value": -0.25,
        "momentum": 1.25,
        "volatility": -0.35,
        "turnover_cost": -0.35,
        "concentration_delta": 0.15,
        "liquidity": 0.10,
    },
    "value_discipline": {
        "expected_return": 0.75,
        "quality": 0.40,
        "value": 1.50,
        "momentum": -0.10,
        "volatility": -0.70,
        "turnover_cost": -1.05,
        "concentration_delta": -0.70,
        "liquidity": 0.30,
    },
    "concentrated_quality": {
        "expected_return": 0.95,
        "quality": 1.10,
        "value": 0.10,
        "momentum": 0.55,
        "volatility": -0.50,
        "turnover_cost": -0.25,
        "concentration_delta": 0.80,
        "liquidity": -0.15,
    },
}

_PRINCIPAL_GENERIC_STYLE_WEIGHTS = {
    "expected_return": 0.95,
    "quality": 0.45,
    "value": 0.35,
    "momentum": 0.35,
    "volatility": -0.45,
    "turnover_cost": -0.45,
    "concentration_delta": -0.25,
    "liquidity": 0.20,
}

_PRINCIPAL_HOLDING_FIELDS = tuple(_PRINCIPAL_GENERIC_STYLE_WEIGHTS)
_NOISY_PRINCIPAL_DELIBERATE_EVENTS = {
    "manager_thesis",
    "quality_rotation",
    "growth_thesis",
    "valuation_thesis",
    "engagement_add",
}
_PRINCIPAL_NOTE_MECHANICAL_MARKERS = (
    "awaiting_board_liquidity_vote",
    "cash_raised_after_external",
    "external_benefit_payment",
    "external_liquidity_calendar",
    "benchmark_transition",
    "without_new_thesis",
    "cash_placeholder",
    "passive_index",
    "benchmark_change_ticket",
    "paired_year_end_swap",
    "unallocated_cash",
    "paired_sale_and_replacement",
    "client_distribution",
    "outside_withdrawal",
    "reduced_active_weight",
    "external_withdrawal",
    "external_transfer",
    "risk_committee_ticket",
    "benchmark_weight",
    "cash_operations_entry",
    "external_schedule",
    "client_wire_liquidity",
    "benchmark_model_update",
    "tax_lot_operations",
    "operations_entry",
)


def _extract_principal_holding_trades(
    text: str,
    *,
    target_only: bool = False,
) -> dict[str, dict[str, float | bool | str]]:
    trades: dict[str, dict[str, float | bool | str]] = {}
    prefix = "candidate_trade" if target_only else r"(?:history_decision|candidate_trade)"
    pattern = re.compile(
        rf"{prefix}=([a-zA-Z0-9_-]+)\s+"
        r"(?:menu_id=([a-zA-Z0-9_-]+)\s+)?"
        r"issuer=([a-zA-Z0-9_-]+)\s+"
        r"expected_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"value=([-+]?\d+(?:\.\d+)?)\s+"
        r"momentum=([-+]?\d+(?:\.\d+)?)\s+"
        r"volatility=([-+]?\d+(?:\.\d+)?)\s+"
        r"turnover_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"concentration_delta=([-+]?\d+(?:\.\d+)?)\s+"
        r"liquidity=([-+]?\d+(?:\.\d+)?)\s+"
        r"chosen=([01])"
    )
    for match in pattern.finditer(text):
        trades[match.group(1)] = {
            "menu_id": match.group(2) or "",
            "issuer": match.group(3),
            "expected_return": float(match.group(4)),
            "quality": float(match.group(5)),
            "value": float(match.group(6)),
            "momentum": float(match.group(7)),
            "volatility": float(match.group(8)),
            "turnover_cost": float(match.group(9)),
            "concentration_delta": float(match.group(10)),
            "liquidity": float(match.group(11)),
            "chosen": match.group(12) == "1",
        }
    return trades


def _principal_holding_utility(
    trade: dict[str, float | bool | str],
    weights: dict[str, float],
) -> float:
    return sum(weights[field] * float(trade[field]) for field in _PRINCIPAL_HOLDING_FIELDS)


def _infer_principal_holding_style(text: str) -> str:
    trades = _extract_principal_holding_trades(text)
    menus: dict[str, list[dict[str, float | bool | str]]] = {}
    for trade in trades.values():
        menu_id = str(trade["menu_id"])
        if menu_id:
            menus.setdefault(menu_id, []).append(trade)
    best_style = next(iter(_PRINCIPAL_STYLE_WEIGHTS))
    best_score = (-1, -math.inf)
    for style_id, weights in _PRINCIPAL_STYLE_WEIGHTS.items():
        valid = True
        margin = 0.0
        for options in menus.values():
            chosen = next(option for option in options if bool(option["chosen"]))
            chosen_u = _principal_holding_utility(chosen, weights)
            best_alt = max(
                _principal_holding_utility(option, weights)
                for option in options
                if not bool(option["chosen"])
            )
            valid = valid and chosen_u >= best_alt
            margin += chosen_u - best_alt
        score = (1 if valid else 0, margin)
        if score > best_score:
            best_style = style_id
            best_score = score
    return best_style


def _best_principal_holding_trade(
    target_trades: dict[str, dict[str, float | bool | str]],
    weights: dict[str, float],
) -> str:
    return max(
        target_trades,
        key=lambda trade_id: _principal_holding_utility(target_trades[trade_id], weights),
    )


def _extract_noisy_principal_holding_trades(
    text: str,
    *,
    target_only: bool = False,
) -> dict[str, dict[str, float | bool | str]]:
    trades: dict[str, dict[str, float | bool | str]] = {}
    prefix = "candidate_trade" if target_only else r"(?:history_decision|candidate_trade)"
    pattern = re.compile(
        rf"{prefix}=([a-zA-Z0-9_-]+)\s+"
        r"(?:menu_id=([a-zA-Z0-9_-]+)\s+)?"
        r"issuer=([a-zA-Z0-9_-]+)\s+"
        r"event_type=([a-zA-Z0-9_-]+)\s+"
        r"expected_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"value=([-+]?\d+(?:\.\d+)?)\s+"
        r"momentum=([-+]?\d+(?:\.\d+)?)\s+"
        r"volatility=([-+]?\d+(?:\.\d+)?)\s+"
        r"turnover_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"concentration_delta=([-+]?\d+(?:\.\d+)?)\s+"
        r"liquidity=([-+]?\d+(?:\.\d+)?)\s+"
        r"chosen=([01])"
    )
    for match in pattern.finditer(text):
        menu_id = match.group(2) or ""
        trade_id = match.group(1)
        key = trade_id if target_only or not menu_id else f"{menu_id}:{trade_id}"
        trades[key] = {
            "menu_id": menu_id,
            "issuer": match.group(3),
            "event_type": match.group(4),
            "expected_return": float(match.group(5)),
            "quality": float(match.group(6)),
            "value": float(match.group(7)),
            "momentum": float(match.group(8)),
            "volatility": float(match.group(9)),
            "turnover_cost": float(match.group(10)),
            "concentration_delta": float(match.group(11)),
            "liquidity": float(match.group(12)),
            "chosen": match.group(13) == "1",
        }
    return trades


def _infer_noisy_principal_holding_style(
    text: str,
    *,
    include_mechanical: bool = False,
) -> str:
    trades = _extract_noisy_principal_holding_trades(text)
    menus: dict[str, list[dict[str, float | bool | str]]] = {}
    for trade in trades.values():
        menu_id = str(trade["menu_id"])
        if menu_id:
            menus.setdefault(menu_id, []).append(trade)
    usable_menus = list(menus.values())
    if not include_mechanical:
        usable_menus = [
            options
            for options in usable_menus
            if str(next(option for option in options if bool(option["chosen"]))["event_type"])
            in _NOISY_PRINCIPAL_DELIBERATE_EVENTS
        ] or usable_menus
    best_style = next(iter(_PRINCIPAL_STYLE_WEIGHTS))
    best_score = (-1, -math.inf)
    for style_id, weights in _PRINCIPAL_STYLE_WEIGHTS.items():
        valid = True
        margin = 0.0
        for options in usable_menus:
            chosen = next(option for option in options if bool(option["chosen"]))
            chosen_u = _principal_holding_utility(chosen, weights)
            best_alt = max(
                _principal_holding_utility(option, weights)
                for option in options
                if not bool(option["chosen"])
            )
            valid = valid and chosen_u >= best_alt
            margin += chosen_u - best_alt
        score = (1 if valid else 0, margin)
        if score > best_score:
            best_style = style_id
            best_score = score
    return best_style


def _best_noisy_principal_holding_trade(
    target_trades: dict[str, dict[str, float | bool | str]],
    weights: dict[str, float],
) -> str:
    return max(
        target_trades,
        key=lambda trade_id: _principal_holding_utility(target_trades[trade_id], weights),
    )


def _extract_note_principal_holding_trades(
    text: str,
    *,
    target_only: bool = False,
) -> dict[str, dict[str, float | bool | str]]:
    trades: dict[str, dict[str, float | bool | str]] = {}
    prefix = "candidate_trade" if target_only else r"(?:history_decision|candidate_trade)"
    pattern = re.compile(
        rf"{prefix}=([a-zA-Z0-9_-]+)\s+"
        r"(?:menu_id=([a-zA-Z0-9_-]+)\s+)?"
        r"issuer=([a-zA-Z0-9_-]+)\s+"
        r"filing_note=([a-zA-Z0-9_-]+)\s+"
        r"expected_return=([-+]?\d+(?:\.\d+)?)\s+"
        r"quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"value=([-+]?\d+(?:\.\d+)?)\s+"
        r"momentum=([-+]?\d+(?:\.\d+)?)\s+"
        r"volatility=([-+]?\d+(?:\.\d+)?)\s+"
        r"turnover_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"concentration_delta=([-+]?\d+(?:\.\d+)?)\s+"
        r"liquidity=([-+]?\d+(?:\.\d+)?)\s+"
        r"chosen=([01])"
    )
    for match in pattern.finditer(text):
        menu_id = match.group(2) or ""
        trade_id = match.group(1)
        key = trade_id if target_only or not menu_id else f"{menu_id}:{trade_id}"
        trades[key] = {
            "menu_id": menu_id,
            "issuer": match.group(3),
            "filing_note": match.group(4),
            "expected_return": float(match.group(5)),
            "quality": float(match.group(6)),
            "value": float(match.group(7)),
            "momentum": float(match.group(8)),
            "volatility": float(match.group(9)),
            "turnover_cost": float(match.group(10)),
            "concentration_delta": float(match.group(11)),
            "liquidity": float(match.group(12)),
            "chosen": match.group(13) == "1",
        }
    return trades


def _infer_note_principal_holding_style(
    text: str,
    *,
    include_mechanical: bool = False,
) -> str:
    trades = _extract_note_principal_holding_trades(text)
    menus: dict[str, list[dict[str, float | bool | str]]] = {}
    for trade in trades.values():
        menu_id = str(trade["menu_id"])
        if menu_id:
            menus.setdefault(menu_id, []).append(trade)
    usable_menus = list(menus.values())
    if not include_mechanical:
        usable_menus = [
            options
            for options in usable_menus
            if not _principal_note_is_mechanical(
                str(next(option for option in options if bool(option["chosen"]))["filing_note"])
            )
        ] or usable_menus
    best_style = next(iter(_PRINCIPAL_STYLE_WEIGHTS))
    best_score = (-1, -math.inf)
    for style_id, weights in _PRINCIPAL_STYLE_WEIGHTS.items():
        valid = True
        margin = 0.0
        for options in usable_menus:
            chosen = next(option for option in options if bool(option["chosen"]))
            chosen_u = _principal_holding_utility(chosen, weights)
            best_alt = max(
                _principal_holding_utility(option, weights)
                for option in options
                if not bool(option["chosen"])
            )
            valid = valid and chosen_u >= best_alt
            margin += chosen_u - best_alt
        score = (1 if valid else 0, margin)
        if score > best_score:
            best_style = style_id
            best_score = score
    return best_style


def _principal_note_is_mechanical(note: str) -> bool:
    return any(marker in note for marker in _PRINCIPAL_NOTE_MECHANICAL_MARKERS)


def _extract_filing_trace_trades(text: str) -> dict[str, dict[str, float | str]]:
    pattern = re.compile(
        r"candidate_trade=([a-zA-Z0-9_-]+)\s+"
        r"issuer=([a-zA-Z0-9_-]+)\s+"
        r"prior_period=([a-zA-Z0-9_-]+)\s+"
        r"next_period=([a-zA-Z0-9_-]+)\s+"
        r"prior_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"next_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"prior_shares=([-+]?\d+(?:\.\d+)?)\s+"
        r"next_shares=([-+]?\d+(?:\.\d+)?)\s+"
        r"previous_share_delta=([-+]?\d+(?:\.\d+)?)"
    )
    trades: dict[str, dict[str, float | str]] = {}
    for match in pattern.finditer(text):
        trades[match.group(1)] = {
            "issuer": match.group(2),
            "prior_period": match.group(3),
            "next_period": match.group(4),
            "prior_value": float(match.group(5)),
            "next_value": float(match.group(6)),
            "prior_shares": float(match.group(7)),
            "next_shares": float(match.group(8)),
            "previous_share_delta": float(match.group(9)),
        }
    return trades


def _filing_trace_action_value(trade: dict[str, float | str]) -> float:
    prior_shares = float(trade["prior_shares"])
    if prior_shares <= 0:
        return 0.0
    prior_price = float(trade["prior_value"]) / prior_shares
    return abs(float(trade["next_shares"]) - prior_shares) * prior_price


def _filing_trace_share_change_fraction(trade: dict[str, float | str]) -> float:
    prior_shares = float(trade["prior_shares"])
    if prior_shares <= 0:
        return 0.0
    return abs(float(trade["next_shares"]) - prior_shares) / prior_shares


def _second_best_filing_trace_id(trades: dict[str, dict[str, float | str]]) -> str:
    ranked = sorted(
        trades,
        key=lambda item: _filing_trace_action_value(trades[item]),
        reverse=True,
    )
    if not ranked:
        raise ValueError("filing trace prompt has no candidate trades")
    return ranked[1] if len(ranked) > 1 else ranked[0]


def _second_best_artifact_id(trades: dict[str, dict[str, float | str]]) -> str:
    ranked = sorted(
        trades,
        key=lambda item: float(trades[item]["value"]),
        reverse=True,
    )
    if not ranked:
        raise ValueError("filing artifact prompt has no candidate issuers")
    return ranked[1] if len(ranked) > 1 else ranked[0]


def _extract_filing_trace_raw_changes(text: str) -> dict[str, dict[str, float | str]]:
    pattern = re.compile(
        r"filing_row\s+"
        r"period=([a-zA-Z0-9_-]+)\s+"
        r"accession=([a-zA-Z0-9_-]+)\s+"
        r"issuer=([a-zA-Z0-9_-]+)\s+"
        r"reported_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"shares=([-+]?\d+(?:\.\d+)?)"
    )
    by_issuer: dict[str, dict[str, dict[str, float | str]]] = {}
    periods: set[str] = set()
    for match in pattern.finditer(text):
        period = match.group(1)
        issuer = match.group(3)
        periods.add(period)
        by_issuer.setdefault(issuer, {})[period] = {
            "accession": match.group(2),
            "value": float(match.group(4)),
            "shares": float(match.group(5)),
        }
    ordered_periods = sorted(periods)
    if len(ordered_periods) < 2:
        return {}
    previous_period = ordered_periods[-3] if len(ordered_periods) >= 3 else None
    prior_period = ordered_periods[-2]
    next_period = ordered_periods[-1]
    changes: dict[str, dict[str, float | str]] = {}
    for issuer, rows in by_issuer.items():
        if prior_period not in rows or next_period not in rows:
            continue
        previous_share_delta = 0.0
        if previous_period is not None and previous_period in rows:
            previous_share_delta = (
                float(rows[prior_period]["shares"]) - float(rows[previous_period]["shares"])
            )
        changes[issuer] = {
            "issuer": issuer,
            "prior_period": prior_period,
            "next_period": next_period,
            "prior_value": float(rows[prior_period]["value"]),
            "next_value": float(rows[next_period]["value"]),
            "prior_shares": float(rows[prior_period]["shares"]),
            "next_shares": float(rows[next_period]["shares"]),
            "previous_share_delta": previous_share_delta,
        }
    return changes


def _extract_filing_artifact_changes(
    text: str,
    *,
    strict_metadata: bool = True,
    infer_missing_artifacts: bool = True,
    validate_metadata: bool = True,
    trusted_metadata_sources: set[str] | None = None,
) -> dict[str, dict[str, float | str]]:
    base_changes = _extract_filing_trace_raw_changes(text)
    factor_pattern = re.compile(
        r"artifact_note\s+issuer=([a-zA-Z0-9_-]+)\s+"
        r"adjustment_factor=([-+]?\d+(?:\.\d+)?)"
    )
    factors = {match.group(1): float(match.group(2)) for match in factor_pattern.finditer(text)}
    note_pattern = re.compile(r"artifact_note\s+issuer=([a-zA-Z0-9_-]+)\s+note=(.*)")
    for match in note_pattern.finditer(text):
        factors.setdefault(match.group(1), _filing_artifact_factor_from_note(match.group(2)))
    for issuer, factor in _extract_corporate_action_factors(
        text,
        base_changes,
        strict_metadata=strict_metadata,
        validate_metadata=validate_metadata,
        trusted_metadata_sources=trusted_metadata_sources,
    ).items():
        factors.setdefault(issuer, factor)
    if infer_missing_artifacts:
        if "Registry coverage may be incomplete" in text:
            inferred = _infer_filing_artifact_factors(base_changes)
            for issuer, factor in inferred.items():
                factors.setdefault(issuer, factor)
        elif not factors and "No separate corporate-action notes are provided" in text:
            factors.update(_infer_filing_artifact_factors(base_changes))
    changes: dict[str, dict[str, float | str]] = {}
    for issuer, trade in base_changes.items():
        factor = factors.get(issuer, 1.0)
        prior_shares = float(trade["prior_shares"])
        next_shares = float(trade["next_shares"])
        prior_value = float(trade["prior_value"])
        adjusted_prior_shares = prior_shares * factor
        adjusted_delta = next_shares - adjusted_prior_shares
        observed_delta = next_shares - prior_shares
        adjusted_price = prior_value / adjusted_prior_shares if adjusted_prior_shares else 0.0
        observed_price = prior_value / prior_shares if prior_shares else 0.0
        changes[issuer] = {
            **trade,
            "adjustment_factor": factor,
            "adjusted_prior_shares": adjusted_prior_shares,
            "adjusted_delta": adjusted_delta,
            "observed_delta": observed_delta,
            "value": abs(adjusted_delta) * adjusted_price,
            "observed_value": abs(observed_delta) * observed_price,
            "observed_fraction": abs(observed_delta) / prior_shares if prior_shares else 0.0,
        }
    return changes


def _extract_corporate_action_factors(
    text: str,
    base_changes: dict[str, dict[str, float | str]],
    *,
    strict_metadata: bool,
    validate_metadata: bool,
    trusted_metadata_sources: set[str] | None,
) -> dict[str, float]:
    factors: dict[str, float] = {}
    active_statuses = {"active", "confirmed", "effective"}
    for line in text.splitlines():
        if not line.startswith("corporate_action "):
            continue
        fields = {
            key: value
            for part in line.split()[1:]
            if "=" in part
            for key, value in [part.split("=", 1)]
        }
        issuer = fields.get("issuer")
        if not issuer or issuer not in base_changes:
            continue
        if fields.get("action") != "stock_split":
            continue
        if (
            trusted_metadata_sources is not None
            and fields.get("source") not in trusted_metadata_sources
        ):
            continue
        ratio_match = re.match(r"([-+]?\d+(?:\.\d+)?)[- ]for[- ]1$", fields.get("ratio", ""))
        if not ratio_match:
            continue
        if strict_metadata:
            next_period = str(base_changes[issuer]["next_period"])
            if fields.get("effective_period") != next_period:
                continue
            if fields.get("status", "confirmed") not in active_statuses:
                continue
        ratio = float(ratio_match.group(1))
        if validate_metadata and not _corporate_action_matches_rows(base_changes[issuer], ratio):
            continue
        factors.setdefault(issuer, ratio)
    return factors


def _corporate_action_matches_rows(trade: dict[str, float | str], ratio: float) -> bool:
    prior_shares = float(trade["prior_shares"])
    if prior_shares <= 0:
        return False
    observed_ratio = float(trade["next_shares"]) / prior_shares
    return abs(observed_ratio - ratio) <= 0.02


def _infer_filing_artifact_factors(
    changes: dict[str, dict[str, float | str]]
) -> dict[str, float]:
    factors: dict[str, float] = {}
    common_split_ratios = {2, 3, 4, 5, 10}
    for issuer, trade in changes.items():
        prior_shares = float(trade["prior_shares"])
        next_shares = float(trade["next_shares"])
        if prior_shares <= 0:
            continue
        ratio = next_shares / prior_shares
        rounded = round(ratio)
        if rounded not in common_split_ratios:
            continue
        if abs(ratio - rounded) > 0.02:
            continue
        factors[issuer] = float(rounded)
    return factors


def _filing_artifact_factor_from_note(note: str) -> float:
    lowered = note.lower()
    numeric = re.search(r"(\d+(?:\.\d+)?)\s*[- ]for[- ]\s*1", lowered)
    if numeric:
        return float(numeric.group(1))
    word_factors = {
        "two": 2.0,
        "three": 3.0,
        "four": 4.0,
        "five": 5.0,
        "six": 6.0,
        "seven": 7.0,
        "eight": 8.0,
        "nine": 9.0,
        "ten": 10.0,
    }
    for word, factor in word_factors.items():
        if f"{word}-for-one" in lowered or f"{word} for one" in lowered:
            return factor
        if f"{word}-for-1" in lowered or f"{word} for 1" in lowered:
            return factor
    return 1.0


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


def _regime_law_label(text: str) -> str:
    left_regime = _extract_word(text, "left_regime")
    relation = _extract_word(text, "relation")
    right_regime = _extract_word(text, "right_regime")
    left = _regime_oracle_fraction(text, left_regime)
    right = _regime_oracle_fraction(text, right_regime)
    if relation == "le":
        return "valid" if left <= right + 1e-9 else "invalid"
    return "valid" if left + 1e-9 >= right else "invalid"


def _pricing_prompt_parameters(text: str) -> tuple[float, float]:
    alpha = _extract_float(text, "alpha")
    beta = _extract_float(text, "beta")
    if alpha > 0 and beta > 0:
        return alpha, beta
    alpha_hat = _extract_float(text, "alpha_hat")
    beta_hat = _extract_float(text, "beta_hat")
    if alpha_hat > 0 and beta_hat > 0:
        return alpha_hat, beta_hat
    rows = _extract_pricing_rows(text)
    if len(rows) >= 2:
        fit = _fit_pricing_rows(rows)
        if fit is not None:
            return fit
    return 1.0, 1.0


def _pricing_law_label(text: str) -> str:
    base_alpha = _extract_float(text, "base_alpha")
    base_beta = max(1e-9, _extract_float(text, "base_beta"))
    base_p_max = _extract_float(text, "base_p_max")
    new_alpha = _extract_float(text, "new_alpha")
    new_beta = max(1e-9, _extract_float(text, "new_beta"))
    new_p_max = _extract_float(text, "new_p_max")
    relation = _extract_word(text, "relation")
    base_price = max(0.0, min(base_p_max, base_alpha / (2.0 * base_beta)))
    new_price = max(0.0, min(new_p_max, new_alpha / (2.0 * new_beta)))
    return _pricing_relation_label(base_price, new_price, relation)


def _pricing_evidence_law_label(text: str) -> str:
    relation = _extract_word(text, "relation")
    base_p_max = _extract_float(text, "baseline_price_cap")
    updated_p_max = _extract_float(text, "updated_price_cap")
    base_blob = _extract_between(text, "baseline_evidence:", "updated_price_cap=")
    updated_blob = _extract_between(text, "updated_evidence:", "relation=")
    base_fit = _fit_pricing_rows(_extract_pricing_rows(base_blob))
    updated_fit = _fit_pricing_rows(_extract_pricing_rows(updated_blob))
    if base_fit is None or updated_fit is None:
        return "invalid"
    base_alpha, base_beta = base_fit
    updated_alpha, updated_beta = updated_fit
    base_price = max(0.0, min(base_p_max, base_alpha / (2.0 * max(base_beta, 1e-9))))
    updated_price = max(0.0, min(updated_p_max, updated_alpha / (2.0 * max(updated_beta, 1e-9))))
    return _pricing_relation_label(base_price, updated_price, relation)


def _pricing_relation_label(base_price: float, new_price: float, relation: str) -> str:
    if relation == "new_gt_base":
        return "valid" if new_price > base_price + 1e-9 else "invalid"
    if relation == "new_ge_base":
        return "valid" if new_price + 1e-9 >= base_price else "invalid"
    if relation == "new_lt_base":
        return "valid" if new_price < base_price - 1e-9 else "invalid"
    if relation == "new_le_base":
        return "valid" if new_price <= base_price + 1e-9 else "invalid"
    return "invalid"


def _extract_between(text: str, start: str, end: str) -> str:
    start_idx = text.find(start)
    if start_idx < 0:
        return ""
    start_idx += len(start)
    end_idx = text.find(end, start_idx)
    if end_idx < 0:
        end_idx = len(text)
    return text[start_idx:end_idx]


def _extract_pricing_rows(text: str) -> list[tuple[float, float]]:
    return [
        (float(price), float(quantity))
        for price, quantity in re.findall(
            r"price=([-+]?\d+(?:\.\d+)?),\s+quantity=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_intervention_pricing_rows(text: str) -> list[tuple[float, float, float, float]]:
    return [
        (
            float(price),
            float(observed_units),
            float(intervention_units),
            float(exposure_multiplier),
        )
        for price, observed_units, intervention_units, exposure_multiplier in re.findall(
            r"price=([-+]?\d+(?:\.\d+)?),\s+"
            r"observed_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"intervention_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"exposure_multiplier=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_cross_pricing_rows(text: str) -> list[tuple[float, float, float]]:
    return [
        (float(own_price), float(related_price), float(quantity))
        for own_price, related_price, quantity in re.findall(
            r"own_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"related_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"quantity=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_multi_product_rows(text: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(price_a), float(price_b), float(quantity_a), float(quantity_b))
        for price_a, price_b, quantity_a, quantity_b in re.findall(
            r"price_a=([-+]?\d+(?:\.\d+)?),\s+"
            r"price_b=([-+]?\d+(?:\.\d+)?),\s+"
            r"quantity_a=([-+]?\d+(?:\.\d+)?),\s+"
            r"quantity_b=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_multi_product_natural_rows(text: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(price_a), float(price_b), float(quantity_a), float(quantity_b))
        for price_a, price_b, quantity_a, quantity_b in re.findall(
            r"product_a_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"product_b_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"product_a_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"product_b_units=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_inventory_markdown_rows(text: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(early_price), float(early_units), float(late_price), float(late_units))
        for early_price, early_units, late_price, late_units in re.findall(
            r"early_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"early_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"late_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"late_units=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_inventory_markdown_natural_rows(text: str) -> list[tuple[float, float, float, float]]:
    return [
        (float(launch_price), float(launch_units), float(clearance_price), float(clearance_units))
        for launch_price, launch_units, clearance_price, clearance_units in re.findall(
            r"launch_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"launch_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"clearance_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"clearance_units=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _extract_multi_product_markdown_rows(
    text: str,
) -> list[tuple[float, float, float, float, float, float, float, float]]:
    return [
        (
            float(launch_a_price),
            float(launch_b_price),
            float(launch_a_units),
            float(launch_b_units),
            float(clearance_a_price),
            float(clearance_b_price),
            float(clearance_a_units),
            float(clearance_b_units),
        )
        for (
            launch_a_price,
            launch_b_price,
            launch_a_units,
            launch_b_units,
            clearance_a_price,
            clearance_b_price,
            clearance_a_units,
            clearance_b_units,
        ) in re.findall(
            r"launch_a_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"launch_b_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"launch_a_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"launch_b_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"clearance_a_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"clearance_b_price=([-+]?\d+(?:\.\d+)?),\s+"
            r"clearance_a_units=([-+]?\d+(?:\.\d+)?),\s+"
            r"clearance_b_units=([-+]?\d+(?:\.\d+)?)",
            text,
        )
    ]


def _fit_pricing_rows(rows: list[tuple[float, float]]) -> tuple[float, float] | None:
    if len(rows) < 2:
        return None
    xs = [price for price, _ in rows]
    ys = [quantity for _, quantity in rows]
    x_bar = sum(xs) / len(xs)
    y_bar = sum(ys) / len(ys)
    denom = sum((x - x_bar) ** 2 for x in xs)
    if denom <= 0:
        return None
    slope = sum((x - x_bar) * (y - y_bar) for x, y in rows) / denom
    beta = max(0.001, -slope)
    alpha = y_bar + beta * x_bar
    return alpha, beta


def _fit_cross_pricing_rows(rows: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    if len(rows) < 3:
        return 1.0, 1.0, 0.0
    design = [(1.0, own_price, related_price) for own_price, related_price, _ in rows]
    values = [quantity for _, _, quantity in rows]
    normal = [
        [sum(row[i] * row[j] for row in design) for j in range(3)]
        for i in range(3)
    ]
    rhs = [sum(row[i] * value for row, value in zip(design, values)) for i in range(3)]
    try:
        intercept, own_slope, related_slope = _solve_linear_3(normal, rhs)
    except ValueError:
        return 1.0, 1.0, 0.0
    return intercept, max(0.001, -own_slope), related_slope


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
        price_a = max(0.0, min(p_max_a, pair[0]))
        price_b = max(0.0, min(p_max_b, pair[1]))
        quantity_a = max(0.0, alpha_a - own_beta_a * price_a + cross_ab * price_b)
        quantity_b = max(0.0, alpha_b - own_beta_b * price_b + cross_ba * price_a)
        return price_a * quantity_a + price_b * quantity_b

    best = max(candidates, key=objective)
    return max(0.0, min(p_max_a, best[0])), max(0.0, min(p_max_b, best[1]))


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
    best_pair = (0.0, 0.0)
    best_value = -1.0
    for price_a in _price_grid(p_max_a, step):
        for price_b in _price_grid(p_max_b, step):
            demand_a = max(0.0, alpha_a - own_beta_a * price_a + cross_ab * price_b)
            demand_b = max(0.0, alpha_b - own_beta_b * price_b + cross_ba * price_a)
            value = price_a * min(demand_a, inventory_a) + price_b * min(demand_b, inventory_b)
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
    early_myopic = max(0.0, min(p_max_early, early_alpha / (2.0 * max(early_beta, 1e-9))))
    late_myopic = max(0.0, min(p_max_late, late_alpha / (2.0 * max(late_beta, 1e-9))))
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
    useful_capacity = max(0.0, min(max_replenishment_units, storage_capacity - starting_inventory))
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
            values.add(round(max(price_floor, min(p_max, anchor + offset)), 2))
    return sorted(values)


def _price_grid(p_max: float, step: float) -> list[float]:
    count = int(p_max / step)
    values = [round(idx * step, 2) for idx in range(count + 1)]
    if values[-1] < p_max:
        values.append(round(p_max, 2))
    return values


def _solve_linear_3(matrix: list[list[float]], vector: list[float]) -> tuple[float, float, float]:
    for col in range(3):
        pivot = max(range(col, 3), key=lambda row: abs(matrix[row][col]))
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        vector[col], vector[pivot] = vector[pivot], vector[col]
        divisor = matrix[col][col]
        if abs(divisor) < 1e-12:
            raise ValueError("singular matrix")
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


def _extract_experiments(text: str) -> dict[str, tuple[float, float, float, float]]:
    experiments: dict[str, tuple[float, float, float, float]] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("experiment_id="):
            continue
        experiment_id = _extract_word(line, "experiment_id")
        experiments[experiment_id] = (
            _extract_float(line, "cost"),
            _extract_float(line, "accuracy"),
            _extract_float(line, "followup_cost", 0.0),
            _extract_float(line, "followup_accuracy", 0.0),
        )
    return experiments


def _extract_experiment_cost(text: str, experiment_id: str) -> float:
    experiments = _extract_experiments(text)
    return experiments.get(experiment_id, (math.inf, 0.0, 0.0, 0.0))[0]


def _experiment_action_values(text: str, *, allow_followup: bool = True) -> dict[str, float]:
    units = _extract_float(text, "deployment_units")
    p_high = _extract_float(text, "high_state_probability")
    arms = _extract_experiment_arms(text)
    experiments = _extract_experiments(text)

    def deploy_value(arm_id: str, high_probability: float) -> float:
        low, high = arms[arm_id]
        return units * (high_probability * high + (1.0 - high_probability) * low)

    values = {f"DEPLOY_{arm_id}": deploy_value(arm_id, p_high) for arm_id in arms}
    def posterior_after_signal(prior: float, accuracy: float, signal_high: bool) -> tuple[float, float]:
        p_low = 1.0 - prior
        if signal_high:
            p_signal = prior * accuracy + p_low * (1.0 - accuracy)
            posterior = (prior * accuracy) / p_signal if p_signal > 0 else prior
        else:
            p_signal = prior * (1.0 - accuracy) + p_low * accuracy
            posterior = (prior * (1.0 - accuracy)) / p_signal if p_signal > 0 else prior
        return p_signal, posterior

    def followup_value(prior: float, followup_cost: float, followup_accuracy: float) -> float:
        if followup_accuracy <= 0:
            return -math.inf
        p_signal_high, posterior_high = posterior_after_signal(prior, followup_accuracy, True)
        p_signal_low, posterior_low = posterior_after_signal(prior, followup_accuracy, False)
        return (
            -followup_cost
            + p_signal_high * max(deploy_value(arm_id, posterior_high) for arm_id in arms)
            + p_signal_low * max(deploy_value(arm_id, posterior_low) for arm_id in arms)
        )

    for experiment_id, (cost, accuracy, followup_cost, followup_accuracy) in experiments.items():
        p_signal_high, posterior_high_given_high_signal = posterior_after_signal(p_high, accuracy, True)
        p_signal_low, posterior_high_given_low_signal = posterior_after_signal(p_high, accuracy, False)
        best_after_high_signal = max(deploy_value(arm_id, posterior_high_given_high_signal) for arm_id in arms)
        best_after_low_signal = max(deploy_value(arm_id, posterior_high_given_low_signal) for arm_id in arms)
        if allow_followup:
            best_after_high_signal = max(
                best_after_high_signal,
                followup_value(posterior_high_given_high_signal, followup_cost, followup_accuracy),
            )
            best_after_low_signal = max(
                best_after_low_signal,
                followup_value(posterior_high_given_low_signal, followup_cost, followup_accuracy),
            )
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


def _strategic_fragile_posterior(text: str) -> float:
    prior = max(0.0, min(1.0, _extract_float(text, "fragile_prior")))
    signal = _extract_word(text, "stress_signal", "none")
    if signal == "none":
        return prior
    likelihood_fragile = _extract_float(text, "signal_likelihood_if_fragile")
    likelihood_resilient = _extract_float(text, "signal_likelihood_if_resilient")
    numerator = prior * likelihood_fragile
    denominator = numerator + (1.0 - prior) * likelihood_resilient
    return numerator / denominator if denominator > 0 else prior


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
                "successful_deliveries": int(round(_extract_float(line, "successful_deliveries", 0.0))),
                "failed_deliveries": int(round(_extract_float(line, "failed_deliveries", 0.0))),
                "reputation_strength": _extract_float(line, "reputation_strength", 2.0),
            }
        )
    return suppliers


def _extract_supplier_natural_options(text: str) -> list[dict[str, float | int | str]]:
    suppliers = []
    for line in text.splitlines():
        if not line.startswith("vendor_id="):
            continue
        suppliers.append(
            {
                "supplier_id": _extract_word(line, "vendor_id"),
                "unit_cost": _extract_float(line, "invoice_per_unit"),
                "claimed_resale": _extract_float(line, "advertised_resale_per_unit"),
                "verified_resale_if_legit": _extract_float(line, "audited_resale_if_good"),
                "scam_probability": _extract_float(line, "failure_risk_prior"),
                "salvage_resale_if_scam": _extract_float(line, "recovery_resale_if_bad"),
                "max_units": int(round(_extract_float(line, "order_limit"))),
                "delivery_lag_rounds": int(round(_extract_float(line, "delivery_delay_rounds", 0.0))),
                "sell_through_rate": _extract_float(line, "expected_sell_through_share", 1.0),
                "storage_cost_per_unsold": _extract_float(line, "holding_cost_per_leftover_unit", 0.0),
                "successful_deliveries": int(round(_extract_float(line, "on_time_deliveries", 0.0))),
                "failed_deliveries": int(round(_extract_float(line, "missed_deliveries", 0.0))),
                "reputation_strength": _extract_float(line, "history_weight", 2.0),
            }
        )
    return suppliers


def _supplier_effective_scam_probability(
    supplier: dict[str, float | int | str],
    *,
    reputation_blind: bool,
) -> float:
    scam_probability = float(supplier["scam_probability"])
    if reputation_blind:
        return scam_probability
    successes = int(supplier.get("successful_deliveries", 0))
    failures = int(supplier.get("failed_deliveries", 0))
    history = successes + failures
    if history <= 0:
        return scam_probability
    strength = float(supplier.get("reputation_strength", 2.0))
    return max(0.0, min(1.0, (scam_probability * strength + failures) / (strength + history)))


def _supplier_resale(
    supplier: dict[str, float | int | str],
    *,
    credulous: bool,
    reputation_blind: bool,
) -> float:
    if credulous:
        return float(supplier["claimed_resale"])
    scam_probability = _supplier_effective_scam_probability(
        supplier,
        reputation_blind=reputation_blind,
    )
    return (
        (1.0 - scam_probability) * float(supplier["verified_resale_if_legit"])
        + scam_probability * float(supplier["salvage_resale_if_scam"])
    )


def _supplier_unit_profit(
    supplier: dict[str, float | int | str],
    *,
    credulous: bool,
    timing_blind: bool,
    reputation_blind: bool,
) -> float:
    resale = _supplier_resale(
        supplier,
        credulous=credulous,
        reputation_blind=reputation_blind,
    )
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


def _belief_best_interaction_prices(
    seller_cost: float,
    states: list[dict[str, float]],
    text: str,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> tuple[float, float]:
    candidates = _belief_interaction_candidates(seller_cost, states)
    pairs = [
        (first, second)
        for first in candidates
        for second in candidates
        if second <= first
    ]
    return max(
        pairs,
        key=lambda pair: (
            _belief_interaction_expected_surplus(
                seller_cost,
                states,
                text,
                pair[0],
                pair[1],
                use_posterior=use_posterior,
                signal_count=signal_count,
            ),
            pair[0],
            pair[1],
        ),
    )


def _belief_best_interaction_single_offer(
    seller_cost: float,
    states: list[dict[str, float]],
    text: str,
    *,
    use_posterior: bool,
    signal_count: int | None = None,
) -> float:
    candidates = _belief_interaction_candidates(seller_cost, states)
    return max(
        candidates,
        key=lambda price: (
            _belief_interaction_expected_surplus(
                seller_cost,
                states,
                text,
                price,
                price,
                use_posterior=use_posterior,
                signal_count=signal_count,
            ),
            price,
        ),
    )


def _belief_interaction_expected_surplus(
    seller_cost: float,
    states: list[dict[str, float]],
    text: str,
    first_price: float,
    second_price: float,
    *,
    use_posterior: bool,
    signal_count: int | None,
) -> float:
    if first_price < seller_cost or second_price < seller_cost:
        return 0.0
    probabilities = _belief_probabilities(states, use_posterior=use_posterior, signal_count=signal_count)
    discount = _extract_float(text, "second_round_discount", 1.0)
    delay_cost = _extract_float(text, "second_round_delay_cost")
    value = 0.0
    for probability, state in zip(probabilities, states):
        if first_price <= state["buyer_wtp"]:
            value += probability * (first_price - seller_cost)
        elif second_price <= state["buyer_wtp"]:
            value += probability * (discount * (second_price - seller_cost) - delay_cost)
    return value


def _belief_probabilities(
    states: list[dict[str, float]],
    *,
    use_posterior: bool,
    signal_count: int | None,
) -> list[float]:
    if not states:
        return []
    if not use_posterior:
        return [state["prior"] for state in states]
    weights = [state["prior"] * _belief_likelihood_product(state, signal_count=signal_count) for state in states]
    total = sum(weights)
    return [weight / total for weight in weights] if total > 0 else [state["prior"] for state in states]


def _belief_interaction_candidates(
    seller_cost: float,
    states: list[dict[str, float]],
) -> list[float]:
    if not states:
        return [seller_cost]
    candidates = {seller_cost, *(state["buyer_wtp"] for state in states)}
    for price in range(int(seller_cost), int(max(candidates)) + 1):
        candidates.add(float(price))
    return sorted(candidates)


def _belief_likelihood_product(state: dict[str, float], *, signal_count: int | None) -> float:
    likelihoods = list(state.get("likelihoods") or [state["likelihood"]])
    if signal_count is not None:
        likelihoods = likelihoods[:signal_count]
    product = 1.0
    for likelihood in likelihoods:
        product *= likelihood
    return product


def _extract_float_list(text: str, key: str) -> list[float]:
    for candidate in (key, *_FLOAT_LIST_ALIASES.get(key, ())):
        match = re.search(rf"{re.escape(candidate)}=([-+0-9.,]+)", text)
        if match:
            return [float(value) for value in match.group(1).split(",") if value]
    return []


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


def _extract_repeated_mechanisms(text: str) -> dict[str, dict[str, float]]:
    mechanisms: dict[str, dict[str, float]] = {}
    explicit_pattern = re.compile(
        r"mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"first_period_revenue=([-+]?\d+(?:\.\d+)?)\s+"
        r"welfare=([-+]?\d+(?:\.\d+)?)\s+"
        r"access=([-+]?\d+(?:\.\d+)?)\s+"
        r"strategic_risk=([-+]?\d+(?:\.\d+)?)\s+"
        r"retention_rate=([-+]?\d+(?:\.\d+)?)\s+"
        r"manipulation_load=([-+]?\d+(?:\.\d+)?)\s+"
        r"manipulation_growth=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_cost=([-+]?\d+(?:\.\d+)?)"
    )
    natural_pattern = re.compile(
        r"option_id=([a-zA-Z0-9_-]+)\s+"
        r"initial_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_reach=([-+]?\d+(?:\.\d+)?)\s+"
        r"governance_risk=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_retention=([-+]?\d+(?:\.\d+)?)\s+"
        r"gaming_pressure=([-+]?\d+(?:\.\d+)?)\s+"
        r"gaming_acceleration=([-+]?\d+(?:\.\d+)?)\s+"
        r"oversight_cost=([-+]?\d+(?:\.\d+)?)"
    )
    for match in explicit_pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "first_period_revenue": float(match.group(2)),
            "welfare": float(match.group(3)),
            "access": float(match.group(4)),
            "strategic_risk": float(match.group(5)),
            "retention_rate": float(match.group(6)),
            "manipulation_load": float(match.group(7)),
            "manipulation_growth": float(match.group(8)),
            "review_cost": float(match.group(9)),
        }
    for match in natural_pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "first_period_revenue": float(match.group(2)),
            "welfare": float(match.group(3)),
            "access": float(match.group(4)),
            "strategic_risk": float(match.group(5)),
            "retention_rate": float(match.group(6)),
            "manipulation_load": float(match.group(7)),
            "manipulation_growth": float(match.group(8)),
            "review_cost": float(match.group(9)),
        }
    return mechanisms


def _best_repeated_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, float]],
    *,
    one_period: bool = False,
    risk_blind: bool = False,
) -> str:
    horizon = 1 if one_period else int(round(_extract_float(text, "horizon", 1.0)))
    revenue_weight = _extract_float(text, "revenue_weight")
    welfare_weight = _extract_float(text, "welfare_weight")
    access_weight = _extract_float(text, "access_weight")
    strategic_risk_penalty = 0.0 if risk_blind else _extract_float(text, "strategic_risk_penalty")
    manipulation_penalty = 0.0 if risk_blind else _extract_float(text, "manipulation_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        total = 0.0
        for period in range(max(1, horizon)):
            retention = mechanism["retention_rate"] ** period
            manipulation = mechanism["manipulation_load"] * (
                mechanism["manipulation_growth"] ** period
            )
            total += (
                revenue_weight * mechanism["first_period_revenue"] * retention
                + welfare_weight * mechanism["welfare"] * retention
                + access_weight * mechanism["access"] * retention
                - strategic_risk_penalty * mechanism["strategic_risk"]
                - manipulation_penalty * manipulation
                - mechanism["review_cost"]
            )
        return total

    return max(mechanisms, key=score)


def _extract_participant_response_mechanisms(text: str) -> dict[str, dict[str, float]]:
    mechanisms: dict[str, dict[str, float]] = {}
    explicit_pattern = re.compile(
        r"policy_id=([a-zA-Z0-9_-]+)\s+"
        r"sponsor_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"starting_participants=([-+]?\d+(?:\.\d+)?)\s+"
        r"base_stay_rate=([-+]?\d+(?:\.\d+)?)\s+"
        r"take_exit_sensitivity=([-+]?\d+(?:\.\d+)?)\s+"
        r"gaming_pressure=([-+]?\d+(?:\.\d+)?)\s+"
        r"trust_decay=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_cost=([-+]?\d+(?:\.\d+)?)"
    )
    elasticity_pattern = re.compile(
        r"policy_id=([a-zA-Z0-9_-]+)\s+"
        r"sponsor_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"starting_participants=([-+]?\d+(?:\.\d+)?)\s+"
        r"gaming_pressure=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"pilot_low_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"pilot_low_stay=([-+]?\d+(?:\.\d+)?)\s+"
        r"pilot_high_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"pilot_high_stay=([-+]?\d+(?:\.\d+)?)\s+"
        r"round3_extra_exit=([-+]?\d+(?:\.\d+)?)"
    )
    for match in explicit_pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "sponsor_take": float(match.group(2)),
            "participant_value": float(match.group(3)),
            "access_quality": float(match.group(4)),
            "starting_participants": float(match.group(5)),
            "base_stay_rate": float(match.group(6)),
            "take_exit_sensitivity": float(match.group(7)),
            "gaming_pressure": float(match.group(8)),
            "trust_decay": float(match.group(9)),
            "review_cost": float(match.group(10)),
        }
    for match in elasticity_pattern.finditer(text):
        low_take = float(match.group(8))
        low_stay = float(match.group(9))
        high_take = float(match.group(10))
        high_stay = float(match.group(11))
        gaming_pressure = float(match.group(6))
        take_span = high_take - low_take
        sensitivity = (low_stay - high_stay) / take_span if take_span else 0.0
        round3_extra_exit = float(match.group(12))
        trust_decay = round3_extra_exit / (2.0 * gaming_pressure) if gaming_pressure else 0.0
        mechanisms[match.group(1)] = {
            "sponsor_take": float(match.group(2)),
            "participant_value": float(match.group(3)),
            "access_quality": float(match.group(4)),
            "starting_participants": float(match.group(5)),
            "base_stay_rate": low_stay + sensitivity * low_take,
            "take_exit_sensitivity": sensitivity,
            "gaming_pressure": gaming_pressure,
            "trust_decay": trust_decay,
            "review_cost": float(match.group(7)),
        }
    return mechanisms


def _best_participant_response_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, float]],
    *,
    one_period: bool = False,
    response_blind: bool = False,
) -> str:
    horizon = 1 if one_period else int(round(_extract_float(text, "horizon", 1.0)))
    revenue_weight = _extract_float(text, "revenue_weight")
    participant_value_weight = _extract_float(text, "participant_value_weight")
    access_weight = _extract_float(text, "access_weight")
    gaming_penalty = _extract_float(text, "gaming_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        participants = mechanism["starting_participants"]
        total = 0.0
        for period in range(max(1, horizon)):
            gaming_pressure = mechanism["gaming_pressure"] * (
                1.0 + mechanism["trust_decay"] * period
            )
            total += (
                participants
                * (
                    revenue_weight * mechanism["sponsor_take"]
                    + participant_value_weight * mechanism["participant_value"]
                    + access_weight * mechanism["access_quality"]
                    - gaming_penalty * gaming_pressure
                )
                - mechanism["review_cost"]
            )
            if response_blind:
                participants = mechanism["starting_participants"]
                continue
            stay_rate = min(
                0.99,
                max(
                    0.05,
                    mechanism["base_stay_rate"]
                    - mechanism["take_exit_sensitivity"] * mechanism["sponsor_take"]
                    - mechanism["trust_decay"] * mechanism["gaming_pressure"] * period,
                ),
            )
            participants *= stay_rate
        return total

    return max(mechanisms, key=score)


def _extract_strategic_response_mechanisms(text: str) -> dict[str, dict[str, float]]:
    mechanisms: dict[str, dict[str, float]] = {}
    pattern = re.compile(
        r"mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"participant_count=([-+]?\d+(?:\.\d+)?)\s+"
        r"sponsor_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"base_stay_rate=([-+]?\d+(?:\.\d+)?)\s+"
        r"exit_sensitivity=([-+]?\d+(?:\.\d+)?)\s+"
        r"initial_strategic_share=([-+]?\d+(?:\.\d+)?)\s+"
        r"strategic_gain=([-+]?\d+(?:\.\d+)?)\s+"
        r"peer_contagion=([-+]?\d+(?:\.\d+)?)\s+"
        r"audit_strength=([-+]?\d+(?:\.\d+)?)\s+"
        r"detection_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"manipulation_harm=([-+]?\d+(?:\.\d+)?)\s+"
        r"response_update_rate=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_cost=([-+]?\d+(?:\.\d+)?)"
    )
    for match in pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "participant_count": float(match.group(2)),
            "sponsor_take": float(match.group(3)),
            "participant_value": float(match.group(4)),
            "access_quality": float(match.group(5)),
            "base_stay_rate": float(match.group(6)),
            "exit_sensitivity": float(match.group(7)),
            "initial_strategic_share": float(match.group(8)),
            "strategic_gain": float(match.group(9)),
            "peer_contagion": float(match.group(10)),
            "audit_strength": float(match.group(11)),
            "detection_cost": float(match.group(12)),
            "manipulation_harm": float(match.group(13)),
            "response_update_rate": float(match.group(14)),
            "review_cost": float(match.group(15)),
        }
    return mechanisms


def _best_strategic_response_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, float]],
    *,
    one_period: bool = False,
    response_blind: bool = False,
) -> str:
    horizon = 1 if one_period else int(round(_extract_float(text, "horizon", 1.0)))
    revenue_weight = _extract_float(text, "revenue_weight")
    participant_value_weight = _extract_float(text, "participant_value_weight")
    access_weight = _extract_float(text, "access_weight")
    manipulation_penalty = _extract_float(text, "manipulation_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        participants = mechanism["participant_count"]
        strategic_share = mechanism["initial_strategic_share"]
        total = 0.0
        for _period in range(max(1, horizon)):
            total += (
                participants
                * (
                    revenue_weight * mechanism["sponsor_take"]
                    + participant_value_weight * mechanism["participant_value"]
                    + access_weight * mechanism["access_quality"]
                    - manipulation_penalty * mechanism["manipulation_harm"] * strategic_share
                )
                - mechanism["review_cost"]
            )
            if not response_blind:
                payoff_advantage = (
                    mechanism["strategic_gain"]
                    + mechanism["peer_contagion"] * strategic_share
                    - mechanism["audit_strength"] * mechanism["detection_cost"]
                )
                strategic_share = min(
                    0.95,
                    max(
                        0.0,
                        strategic_share + mechanism["response_update_rate"] * payoff_advantage,
                    ),
                )
            stay_rate = min(
                0.99,
                max(0.05, mechanism["base_stay_rate"] - mechanism["exit_sensitivity"] * strategic_share),
            )
            participants *= stay_rate
        return total

    return max(mechanisms, key=score)


def _strategic_equilibrium_share(mechanism: dict[str, float], *, response_blind: bool = False) -> float:
    if response_blind:
        return mechanism["initial_strategic_share"]
    strategic_share = mechanism["initial_strategic_share"]
    for _iteration in range(25):
        payoff_advantage = (
            mechanism["strategic_gain"]
            + mechanism["peer_contagion"] * strategic_share
            - mechanism["audit_strength"] * mechanism["detection_cost"]
        )
        strategic_share = min(
            0.95,
            max(0.0, strategic_share + mechanism["response_update_rate"] * payoff_advantage),
        )
    return strategic_share


def _best_strategic_equilibrium_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, float]],
    *,
    one_period: bool = False,
    response_blind: bool = False,
) -> str:
    horizon = 1 if one_period else int(round(_extract_float(text, "horizon", 1.0)))
    revenue_weight = _extract_float(text, "revenue_weight")
    participant_value_weight = _extract_float(text, "participant_value_weight")
    access_weight = _extract_float(text, "access_weight")
    manipulation_penalty = _extract_float(text, "manipulation_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        participants = mechanism["participant_count"]
        strategic_share = _strategic_equilibrium_share(mechanism, response_blind=response_blind)
        total = 0.0
        for _period in range(max(1, horizon)):
            total += (
                participants
                * (
                    revenue_weight * mechanism["sponsor_take"]
                    + participant_value_weight * mechanism["participant_value"]
                    + access_weight * mechanism["access_quality"]
                    - manipulation_penalty * mechanism["manipulation_harm"] * strategic_share
                )
                - mechanism["review_cost"]
            )
            stay_rate = min(
                0.99,
                max(0.05, mechanism["base_stay_rate"] - mechanism["exit_sensitivity"] * strategic_share),
            )
            participants *= stay_rate
        return total

    return max(mechanisms, key=score)


def _extract_interaction_trace_mechanisms(text: str) -> dict[str, dict[str, object]]:
    mechanisms: dict[str, dict[str, object]] = {}
    mechanism_pattern = re.compile(
        r"mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"sponsor_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"manipulation_harm=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_cost=([-+]?\d+(?:\.\d+)?)"
    )
    for match in mechanism_pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "sponsor_take": float(match.group(2)),
            "participant_value": float(match.group(3)),
            "access_quality": float(match.group(4)),
            "manipulation_harm": float(match.group(5)),
            "review_cost": float(match.group(6)),
            "trace": [],
        }
    trace_pattern = re.compile(
        r"trace mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"round=\d+\s+"
        r"active_participants=([-+]?\d+(?:\.\d+)?)\s+"
        r"strategic_share=([-+]?\d+(?:\.\d+)?)"
    )
    for match in trace_pattern.finditer(text):
        mechanism_id = match.group(1)
        if mechanism_id in mechanisms:
            trace = mechanisms[mechanism_id]["trace"]
            assert isinstance(trace, list)
            trace.append((float(match.group(2)), float(match.group(3))))
    return mechanisms


def _best_interaction_trace_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, object]],
    *,
    one_period: bool = False,
    trace_blind: bool = False,
) -> str:
    horizon = 1 if one_period else int(round(_extract_float(text, "future_rounds_to_score", 1.0)))
    revenue_weight = _extract_float(text, "revenue_weight")
    participant_value_weight = _extract_float(text, "participant_value_weight")
    access_weight = _extract_float(text, "access_weight")
    manipulation_penalty = _extract_float(text, "manipulation_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        trace = mechanism["trace"]
        assert isinstance(trace, list)
        if trace_blind:
            participants, strategic_share = trace[0]
            participant_ratio = 1.0
            strategic_delta = 0.0
        else:
            participants, strategic_share = trace[-1]
            ratios = [
                later[0] / earlier[0]
                for earlier, later in zip(trace, trace[1:])
                if earlier[0] > 0
            ]
            deltas = [later[1] - earlier[1] for earlier, later in zip(trace, trace[1:])]
            participant_ratio = sum(ratios) / len(ratios) if ratios else 1.0
            strategic_delta = sum(deltas) / len(deltas) if deltas else 0.0
        total = 0.0
        for _period in range(max(1, horizon)):
            total += (
                participants
                * (
                    revenue_weight * float(mechanism["sponsor_take"])
                    + participant_value_weight * float(mechanism["participant_value"])
                    + access_weight * float(mechanism["access_quality"])
                    - manipulation_penalty * float(mechanism["manipulation_harm"]) * strategic_share
                )
                - float(mechanism["review_cost"])
            )
            participants *= participant_ratio
            strategic_share = min(0.95, max(0.0, strategic_share + strategic_delta))
        return total

    return max(mechanisms, key=score)


def _extract_trace_equilibrium_mechanisms(text: str) -> dict[str, dict[str, object]]:
    mechanisms: dict[str, dict[str, object]] = {}
    mechanism_pattern = re.compile(
        r"mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"sponsor_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_value=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_quality=([-+]?\d+(?:\.\d+)?)\s+"
        r"manipulation_harm=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"base_stay_rate=([-+]?\d+(?:\.\d+)?)\s+"
        r"exit_sensitivity=([-+]?\d+(?:\.\d+)?)\s+"
        r"strategic_gain=([-+]?\d+(?:\.\d+)?)\s+"
        r"peer_contagion=([-+]?\d+(?:\.\d+)?)\s+"
        r"audit_strength=([-+]?\d+(?:\.\d+)?)\s+"
        r"detection_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"response_update_rate=([-+]?\d+(?:\.\d+)?)"
    )
    for match in mechanism_pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "sponsor_take": float(match.group(2)),
            "participant_value": float(match.group(3)),
            "access_quality": float(match.group(4)),
            "manipulation_harm": float(match.group(5)),
            "review_cost": float(match.group(6)),
            "base_stay_rate": float(match.group(7)),
            "exit_sensitivity": float(match.group(8)),
            "strategic_gain": float(match.group(9)),
            "peer_contagion": float(match.group(10)),
            "audit_strength": float(match.group(11)),
            "detection_cost": float(match.group(12)),
            "response_update_rate": float(match.group(13)),
            "trace": [],
        }
    natural_pattern = re.compile(
        r"option_id=([a-zA-Z0-9_-]+)\s+"
        r"launch_take=([-+]?\d+(?:\.\d+)?)\s+"
        r"participant_outcome=([-+]?\d+(?:\.\d+)?)\s+"
        r"access_reach=([-+]?\d+(?:\.\d+)?)\s+"
        r"gaming_damage=([-+]?\d+(?:\.\d+)?)\s+"
        r"oversight_cost=([-+]?\d+(?:\.\d+)?)\s+"
        r"ordinary_stay=([-+]?\d+(?:\.\d+)?)\s+"
        r"departure_pressure=([-+]?\d+(?:\.\d+)?)\s+"
        r"private_strategy_pull=([-+]?\d+(?:\.\d+)?)\s+"
        r"copycat_pressure=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_deterrence=([-+]?\d+(?:\.\d+)?)\s+"
        r"review_consequence=([-+]?\d+(?:\.\d+)?)\s+"
        r"adaptation_speed=([-+]?\d+(?:\.\d+)?)"
    )
    for match in natural_pattern.finditer(text):
        mechanisms[match.group(1)] = {
            "sponsor_take": float(match.group(2)),
            "participant_value": float(match.group(3)),
            "access_quality": float(match.group(4)),
            "manipulation_harm": float(match.group(5)),
            "review_cost": float(match.group(6)),
            "base_stay_rate": float(match.group(7)),
            "exit_sensitivity": float(match.group(8)),
            "strategic_gain": float(match.group(9)),
            "peer_contagion": float(match.group(10)),
            "audit_strength": float(match.group(11)),
            "detection_cost": float(match.group(12)),
            "response_update_rate": float(match.group(13)),
            "trace": [],
        }
    trace_pattern = re.compile(
        r"trace mechanism_id=([a-zA-Z0-9_-]+)\s+"
        r"round=\d+\s+"
        r"active_participants=([-+]?\d+(?:\.\d+)?)\s+"
        r"strategic_share=([-+]?\d+(?:\.\d+)?)"
    )
    for match in trace_pattern.finditer(text):
        mechanism_id = match.group(1)
        if mechanism_id in mechanisms:
            trace = mechanisms[mechanism_id]["trace"]
            assert isinstance(trace, list)
            trace.append((float(match.group(2)), float(match.group(3))))
    natural_trace_pattern = re.compile(
        r"pilot option_id=([a-zA-Z0-9_-]+)\s+"
        r"wave=\d+\s+"
        r"active_pool=([-+]?\d+(?:\.\d+)?)\s+"
        r"flagged_share=([-+]?\d+(?:\.\d+)?)"
    )
    for match in natural_trace_pattern.finditer(text):
        mechanism_id = match.group(1)
        if mechanism_id in mechanisms:
            trace = mechanisms[mechanism_id]["trace"]
            assert isinstance(trace, list)
            trace.append((float(match.group(2)), float(match.group(3))))
    return mechanisms


def _best_trace_equilibrium_mechanism_choice(
    text: str,
    mechanisms: dict[str, dict[str, object]],
    *,
    trace_projection: bool = False,
    equilibrium_blind: bool = False,
    trace_blind: bool = False,
) -> str:
    horizon = int(round(_extract_float(text, "future_rounds_to_score", 1.0)))
    revenue_weight = _extract_float(text, "revenue_weight")
    participant_value_weight = _extract_float(text, "participant_value_weight")
    access_weight = _extract_float(text, "access_weight")
    manipulation_penalty = _extract_float(text, "manipulation_penalty")

    def score(mechanism_id: str) -> float:
        mechanism = mechanisms[mechanism_id]
        trace = mechanism["trace"]
        assert isinstance(trace, list)
        if trace_projection:
            participants, strategic_share = trace[-1]
            ratios = [
                later[0] / earlier[0]
                for earlier, later in zip(trace, trace[1:])
                if earlier[0] > 0
            ]
            deltas = [later[1] - earlier[1] for earlier, later in zip(trace, trace[1:])]
            participant_ratio = sum(ratios) / len(ratios) if ratios else 1.0
            strategic_delta = sum(deltas) / len(deltas) if deltas else 0.0
            total = 0.0
            for _period in range(max(1, horizon)):
                total += (
                    participants
                    * (
                        revenue_weight * float(mechanism["sponsor_take"])
                        + participant_value_weight * float(mechanism["participant_value"])
                        + access_weight * float(mechanism["access_quality"])
                        - manipulation_penalty
                        * float(mechanism["manipulation_harm"])
                        * strategic_share
                    )
                    - float(mechanism["review_cost"])
                )
                participants *= participant_ratio
                strategic_share = min(0.95, max(0.0, strategic_share + strategic_delta))
            return total

        if trace_blind:
            participants, strategic_share = trace[0]
            strategic_momentum = 0.0
        else:
            participants, strategic_share = trace[-1]
            deltas = [later[1] - earlier[1] for earlier, later in zip(trace, trace[1:])]
            strategic_momentum = sum(deltas) / len(deltas) if deltas else 0.0
        if not equilibrium_blind:
            for _iteration in range(25):
                payoff_advantage = (
                    float(mechanism["strategic_gain"])
                    + float(mechanism["peer_contagion"]) * strategic_share
                    + strategic_momentum
                    - float(mechanism["audit_strength"]) * float(mechanism["detection_cost"])
                )
                strategic_share = min(
                    0.95,
                    max(
                        0.0,
                        strategic_share
                        + float(mechanism["response_update_rate"]) * payoff_advantage,
                    ),
                )
        total = 0.0
        for _period in range(max(1, horizon)):
            total += (
                participants
                * (
                    revenue_weight * float(mechanism["sponsor_take"])
                    + participant_value_weight * float(mechanism["participant_value"])
                    + access_weight * float(mechanism["access_quality"])
                    - manipulation_penalty
                    * float(mechanism["manipulation_harm"])
                    * strategic_share
                )
                - float(mechanism["review_cost"])
            )
            stay_rate = min(
                0.99,
                max(
                    0.05,
                    float(mechanism["base_stay_rate"])
                    - float(mechanism["exit_sensitivity"]) * strategic_share,
                ),
            )
            participants *= stay_rate
        return total

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
