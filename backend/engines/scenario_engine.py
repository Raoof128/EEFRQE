"""Risk scenario builder leveraging E8 posture and FAIR modelling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from backend.engines.e8_score import ControlAssessment
from backend.engines.fair_calc import FAIRCalculator, FAIRParameters, FAIRResult
from backend.engines.risk_mapper import RiskMapper


@dataclass
class ScenarioConfig:
    """Base FAIR parameters and descriptive metadata for a scenario."""

    name: str
    description: str
    fair: FAIRParameters


SCENARIO_LIBRARY: Dict[str, ScenarioConfig] = {
    "ransomware": ScenarioConfig(
        name="Ransomware",
        description="Encryption of file shares leading to downtime and extortion risk.",
        fair=FAIRParameters(
            threat_event_frequency=(2, 6, 12),
            vulnerability=(0.3, 0.5, 0.8),
            primary_loss=(200000, 400000, 800000),
            secondary_loss=(50000, 150000, 300000),
            secondary_event_frequency=(0.5, 1, 3),
        ),
    ),
    "bec": ScenarioConfig(
        name="Business Email Compromise",
        description="Mailbox takeover leading to fraudulent payments or data theft.",
        fair=FAIRParameters(
            threat_event_frequency=(5, 12, 24),
            vulnerability=(0.4, 0.6, 0.9),
            primary_loss=(50000, 120000, 350000),
            secondary_loss=(20000, 80000, 200000),
            secondary_event_frequency=(0.2, 0.8, 1.5),
        ),
    ),
    "data_breach": ScenarioConfig(
        name="Data Breach",
        description="Exposure of regulated personal or health information.",
        fair=FAIRParameters(
            threat_event_frequency=(1, 4, 8),
            vulnerability=(0.2, 0.4, 0.7),
            primary_loss=(300000, 700000, 1500000),
            secondary_loss=(100000, 400000, 1200000),
            secondary_event_frequency=(0.5, 1.5, 3),
        ),
    ),
}


class ScenarioEngine:
    """Build and run scenarios integrating Essential Eight and FAIR outputs."""

    def __init__(self, iterations: int = 10000, calculator: FAIRCalculator | None = None) -> None:
        # iterations parameter allows external configuration while keeping backwards compatibility
        self.calculator = calculator or FAIRCalculator(iterations=iterations)

    def run(self, scenario_key: str, controls: List[ControlAssessment]) -> FAIRResult:
        if scenario_key not in SCENARIO_LIBRARY:
            raise KeyError(f"Unknown scenario: {scenario_key}")
        config = SCENARIO_LIBRARY[scenario_key]
        mapper = RiskMapper(config.fair)
        adjusted_params = mapper.adjust({c.control.value: c for c in controls})
        return self.calculator.run(adjusted_params)

    def describe(self) -> List[ScenarioConfig]:
        """Return available scenarios."""

        return list(SCENARIO_LIBRARY.values())
