"""FAIR quantitative risk calculation utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

import numpy as np

from backend.engines.monte_carlo import MonteCarloEngine, MonteCarloResult

logger = logging.getLogger(__name__)

RangeTriplet = Tuple[float, float, float]


def _validate_range(name: str, values: RangeTriplet, *, allow_one: bool = False) -> None:
    """Ensure ranges follow (min <= mode <= max) and are non-negative."""

    if len(values) != 3:
        raise ValueError(f"{name} must contain three values (min, mode, max)")
    low, mode, high = values
    if low < 0 or mode < 0 or high < 0:
        raise ValueError(f"{name} values must be non-negative")
    if not low <= mode <= high:
        raise ValueError(f"{name} must satisfy min <= mode <= max")
    if allow_one and high > 1:
        raise ValueError(f"{name} values representing probabilities must be <= 1")


@dataclass
class LossMagnitude:
    """Loss magnitude details for primary and secondary components."""

    primary: float
    secondary: float

    @property
    def total(self) -> float:
        """Total loss magnitude."""

        return self.primary + self.secondary


@dataclass
class FAIRParameters:
    """Collection of FAIR input ranges."""

    threat_event_frequency: RangeTriplet
    vulnerability: RangeTriplet
    primary_loss: RangeTriplet
    secondary_loss: RangeTriplet
    secondary_event_frequency: RangeTriplet

    def __post_init__(self) -> None:
        _validate_range("threat_event_frequency", self.threat_event_frequency)
        _validate_range("vulnerability", self.vulnerability, allow_one=True)
        _validate_range("primary_loss", self.primary_loss)
        _validate_range("secondary_loss", self.secondary_loss)
        _validate_range("secondary_event_frequency", self.secondary_event_frequency)

    def triangular(self, values: RangeTriplet) -> float:
        """Sample triangular distribution given (min, mode, max) and return a scalar."""

        low, mode, high = values
        sample = float(np.random.triangular(left=low, mode=mode, right=high, size=1)[0])
        return max(sample, 0.0)

    def sample_loss_event_frequency(self) -> float:
        """Sample Loss Event Frequency."""

        tef = self.triangular(self.threat_event_frequency)
        vuln = min(self.triangular(self.vulnerability), 1.0)
        return tef * vuln

    def sample_loss_magnitude(self) -> LossMagnitude:
        """Sample Loss Magnitude for primary and secondary losses."""

        primary = self.triangular(self.primary_loss)
        secondary = self.triangular(self.secondary_loss)
        return LossMagnitude(primary=primary, secondary=secondary)

    def sample_secondary_event_frequency(self) -> float:
        """Sample secondary event frequency."""

        return min(self.triangular(self.secondary_event_frequency), 1.0)


@dataclass
class FAIRResult:
    """FAIR calculation output."""

    loss_event_frequency: float
    loss_magnitude: LossMagnitude
    secondary_event_frequency: float
    monte_carlo: MonteCarloResult


class FAIRCalculator:
    """Perform FAIR calculations and Monte Carlo simulations."""

    def __init__(self, iterations: int = 10000) -> None:
        self.engine = MonteCarloEngine(iterations=iterations)

    def run(self, params: FAIRParameters) -> FAIRResult:
        """Run a FAIR Monte Carlo simulation.

        Args:
            params: FAIRParameters configuration.

        Returns:
            FAIRResult: Aggregated FAIR metrics with simulation statistics.
        """

        base_lef = params.sample_loss_event_frequency()
        base_lm = params.sample_loss_magnitude()
        base_secondary_freq = params.sample_secondary_event_frequency()

        def generator(iterations: int) -> Iterable[float]:
            for _ in range(iterations):
                lef = params.sample_loss_event_frequency()
                lm = params.sample_loss_magnitude()
                secondary_events = params.sample_secondary_event_frequency()
                total_loss = lef * lm.total * max(1.0, secondary_events)
                yield max(total_loss, 0.0)

        mc_result = self.engine.run(generator)
        logger.info(
            "FAIR simulation completed: mean=%s, p95=%s, worst=%s",
            mc_result.mean,
            mc_result.p95,
            mc_result.worst_case,
        )
        return FAIRResult(
            loss_event_frequency=base_lef,
            loss_magnitude=base_lm,
            secondary_event_frequency=base_secondary_freq,
            monte_carlo=mc_result,
        )

    @staticmethod
    def annualised_loss_exposure(mc_result: MonteCarloResult) -> Dict[str, float]:
        """Derive annualised loss exposure metrics from simulation."""

        return {
            "mean": mc_result.mean,
            "p90": mc_result.p90,
            "p95": mc_result.p95,
            "worst_case": mc_result.worst_case,
        }
