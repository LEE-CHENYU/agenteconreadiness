from __future__ import annotations

import math
import random
from collections.abc import Sequence


def mean(values: Sequence[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bootstrap_mean_ci(
    values: Sequence[float],
    *,
    confidence: float = 0.95,
    samples: int = 1000,
    seed: int = 20260529,
) -> tuple[float, float] | None:
    if not values:
        return None
    if len(values) == 1:
        return (values[0], values[0])
    rng = random.Random(seed)
    means = []
    n = len(values)
    for _ in range(samples):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    alpha = (1.0 - confidence) / 2.0
    lo = means[int(alpha * (samples - 1))]
    hi = means[int((1.0 - alpha) * (samples - 1))]
    return (lo, hi)


def wilson_ci(successes: int, total: int, *, z: float = 1.959963984540054) -> tuple[float, float] | None:
    if total <= 0:
        return None
    p = successes / total
    denom = 1.0 + z * z / total
    center = (p + z * z / (2.0 * total)) / denom
    margin = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * total)) / total) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))
