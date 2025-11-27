"""Pydantic schemas shared across API endpoints."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator

from backend.engines.e8_score import ControlAssessment, ControlName, E8AssessmentResult
from backend.engines.fair_calc import FAIRResult, LossMagnitude
from backend.engines.monte_carlo import MonteCarloResult
from backend.engines.regulation_mapping import RegulatorySignal


class ControlAssessmentModel(BaseModel):
    """Serializable representation of a control assessment."""

    control: ControlName
    level: int = Field(..., ge=0, le=3)
    heat: str
    risk_implication: str

    @classmethod
    def from_dataclass(cls, assessment: ControlAssessment) -> "ControlAssessmentModel":
        return cls(
            control=assessment.control,
            level=assessment.level,
            heat=assessment.heat,
            risk_implication=assessment.risk_implication,
        )

    def to_dataclass(self) -> ControlAssessment:
        """Convert schema to dataclass for downstream engines."""

        return ControlAssessment(
            control=self.control,
            level=self.level,
            heat=self.heat,
            risk_implication=self.risk_implication,
        )


class E8AssessmentModel(BaseModel):
    """Aggregated Essential Eight maturity output."""

    overall_level: float
    controls: List[ControlAssessmentModel]
    heatmap: dict[str, str]
    recommendations: List[str]

    @classmethod
    def from_dataclass(cls, assessment: E8AssessmentResult) -> "E8AssessmentModel":
        return cls(
            overall_level=assessment.overall_level,
            controls=[ControlAssessmentModel.from_dataclass(c) for c in assessment.controls],
            heatmap=assessment.heatmap,
            recommendations=assessment.recommendations,
        )

    def to_dataclass(self) -> E8AssessmentResult:
        """Convert schema to dataclass."""

        return E8AssessmentResult(
            overall_level=self.overall_level,
            controls=[control.to_dataclass() for control in self.controls],
            heatmap=self.heatmap,
            recommendations=self.recommendations,
        )


class LossMagnitudeModel(BaseModel):
    """Loss magnitude wrapper for API responses."""

    primary: float
    secondary: float
    total: float

    @classmethod
    def from_dataclass(cls, lm: LossMagnitude) -> "LossMagnitudeModel":
        return cls(primary=lm.primary, secondary=lm.secondary, total=lm.total)


class MonteCarloModel(BaseModel):
    """Monte Carlo summary statistics."""

    mean: float
    p90: float
    p95: float
    worst_case: float

    @classmethod
    def from_dataclass(cls, mc: MonteCarloResult) -> "MonteCarloModel":
        return cls(mean=mc.mean, p90=mc.p90, p95=mc.p95, worst_case=mc.worst_case)


class FAIRResultModel(BaseModel):
    """Serializable FAIR result."""

    loss_event_frequency: float
    loss_magnitude: LossMagnitudeModel
    secondary_event_frequency: float
    monte_carlo: MonteCarloModel

    @classmethod
    def from_dataclass(cls, result: FAIRResult) -> "FAIRResultModel":
        return cls(
            loss_event_frequency=result.loss_event_frequency,
            loss_magnitude=LossMagnitudeModel.from_dataclass(result.loss_magnitude),
            secondary_event_frequency=result.secondary_event_frequency,
            monte_carlo=MonteCarloModel.from_dataclass(result.monte_carlo),
        )

    def to_dataclass(self) -> FAIRResult:
        """Convert schema to FAIRResult dataclass."""

        return FAIRResult(
            loss_event_frequency=self.loss_event_frequency,
            loss_magnitude=LossMagnitude(
                primary=self.loss_magnitude.primary, secondary=self.loss_magnitude.secondary
            ),
            secondary_event_frequency=self.secondary_event_frequency,
            monte_carlo=MonteCarloResult(
                mean=self.monte_carlo.mean,
                p90=self.monte_carlo.p90,
                p95=self.monte_carlo.p95,
                worst_case=self.monte_carlo.worst_case,
                samples=[],
            ),
        )


class RegulatorySignalModel(BaseModel):
    """Australian regulatory context signal."""

    regulation: str
    impact: str
    recommendation: str

    @classmethod
    def from_dataclass(cls, signal: RegulatorySignal) -> "RegulatorySignalModel":
        return cls(
            regulation=signal.regulation,
            impact=signal.impact,
            recommendation=signal.recommendation,
        )


class ReportRequestModel(BaseModel):
    """Payload for PDF export endpoint."""

    organisation: str = Field(..., description="Synthetic organisation name")
    e8_result: E8AssessmentModel
    fair_result: FAIRResultModel
    recommendations: List[str]

    @field_validator("recommendations")
    @classmethod
    def _non_empty_recommendations(cls, values: List[str]) -> List[str]:
        if not values:
            raise ValueError("At least one recommendation is required for reporting")
        return values
