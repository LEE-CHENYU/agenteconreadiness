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


def parse_floats(label: str, text: str) -> list[float] | None:
    """Parse a comma/space-separated float vector after `label:` (e.g.
    `FINAL_BUNDLE: 6.0, 3.0` -> [6.0, 3.0]). Returns None if the label is absent."""
    pattern = rf"{re.escape(label)}\s*:\s*([-+0-9.,\s]+)"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    raw = match.group(1)
    out: list[float] = []
    for tok in re.split(r"[,\s]+", raw.strip()):
        if not tok:
            continue
        try:
            out.append(float(tok))
        except ValueError:
            break  # stop at first non-numeric token (end of the vector)
    return out or None


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
