from __future__ import annotations

import re


def parse_float(label: str, text: str) -> float | None:
    pattern = rf"{re.escape(label)}\s*:\s*\$?\s*([-+]?\d+(?:\.\d+)?)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def parse_token(label: str, text: str) -> str | None:
    pattern = rf"{re.escape(label)}\s*:\s*([a-zA-Z0-9_-]+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(1) if match else None


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
