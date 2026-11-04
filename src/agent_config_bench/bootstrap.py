"""Paired bootstrap utilities shared by analysis and tests."""

from __future__ import annotations

import random
import statistics


def bootstrap_mean(
    values: list[float],
    n: int = 4000,
    seed: int = 11,
) -> tuple[float, float, float]:
    """Return (mean, ci_lo, ci_hi) with a percentile bootstrap over the task means."""
    if not values:
        raise ValueError("values must be non-empty")
    rng = random.Random(seed)
    means = sorted(
        statistics.fmean(rng.choices(values, k=len(values))) for _ in range(n)
    )
    return statistics.fmean(values), means[int(0.025 * n)], means[int(0.975 * n) - 1]
