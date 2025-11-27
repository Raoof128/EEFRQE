"""Monte Carlo sampling utilities for FAIR simulations."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Iterable, List

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MonteCarloResult:
    """Summary statistics from Monte Carlo simulations."""

    mean: float
    p90: float
    p95: float
    worst_case: float
    samples: List[float]


class MonteCarloEngine:
    """Simple Monte Carlo engine for FAIR simulations."""

    def __init__(self, iterations: int = 10000) -> None:
        self.iterations = max(iterations, 1000)

    def run(self, generator: Callable[[int], Iterable[float]]) -> MonteCarloResult:
        """Execute the simulation.

        Args:
            generator: Function receiving iteration count and returning iterable of samples.

        Returns:
            MonteCarloResult: Statistical summary of samples.
        """

        logger.debug("Starting Monte Carlo with %s iterations", self.iterations)
        samples_array = np.array(list(generator(self.iterations)), dtype=float)
        if samples_array.size == 0:
            raise ValueError("No samples produced by generator")
        mean_val = float(np.mean(samples_array))
        p90 = float(np.percentile(samples_array, 90))
        p95 = float(np.percentile(samples_array, 95))
        worst_case = float(np.max(samples_array))
        logger.debug(
            "Monte Carlo results mean=%s p90=%s p95=%s worst=%s", mean_val, p90, p95, worst_case
        )
        return MonteCarloResult(
            mean=mean_val,
            p90=p90,
            p95=p95,
            worst_case=worst_case,
            samples=list(samples_array),
        )
