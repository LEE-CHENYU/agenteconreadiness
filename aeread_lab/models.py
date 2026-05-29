from __future__ import annotations

import os
import re
from dataclasses import dataclass
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
        if "TASK: procurement_choice" in system:
            return self._procurement_choice(user)
        if "TASK: pricing_price" in system:
            return self._pricing_price(user)
        if "TASK: scam_estimate" in system:
            return self._scam_estimate(user)
        if "TASK: scam_pitch" in system:
            return self._scam_pitch(user)
        return "FINAL_ANSWER: offline baseline has no handler"

    def _regime_fraction(self, user: str) -> str:
        oracle = _extract_float(user, "oracle_fraction")
        ev = _extract_float(user, "ev_fraction")
        kelly = _extract_float(user, "kelly_fraction")
        cvar = _extract_float(user, "cvar_fraction")
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

    def _procurement_choice(self, user: str) -> str:
        oracle = _extract_word(user, "oracle_product")
        if self.policy == "first":
            first = re.search(r"product_id=([a-zA-Z0-9_-]+)", user)
            oracle = first.group(1) if first else oracle
        return f"FINAL_PRODUCT: {oracle}"

    def _pricing_price(self, user: str) -> str:
        oracle = _extract_float(user, "oracle_price")
        if self.policy == "round":
            oracle = round(oracle / 10.0) * 10.0
        return f"FINAL_PRICE: {oracle:.2f}"

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
