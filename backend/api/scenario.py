"""Scenario execution API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

from backend.config import AppSettings, get_settings
from backend.engines.e8_score import ControlAssessment, ControlName
from backend.engines.scenario_engine import ScenarioEngine
from backend.schemas import MonteCarloModel

router = APIRouter()


class ControlAssessmentInput(BaseModel):
    """Minimal schema for control assessments passed into scenarios."""

    control: ControlName
    level: int = Field(..., ge=0, le=3)
    heat: str | None = None
    risk_implication: str | None = None

    def to_dataclass(self) -> ControlAssessment:
        return ControlAssessment(
            control=self.control,
            level=self.level,
            heat=self.heat or "unknown",
            risk_implication=self.risk_implication or "",
        )


class ScenarioRequest(BaseModel):
    """Request schema for running a scenario."""

    scenario_key: str = Field(..., description="Scenario identifier e.g., ransomware")
    controls: list[ControlAssessmentInput]

    @field_validator("controls")
    @classmethod
    def validate_controls(
        cls, values: list[ControlAssessmentInput]
    ) -> list[ControlAssessmentInput]:
        if len(values) != len(ControlName):
            raise ValueError("All Essential Eight controls must be provided for scenario mapping")
        return values

    @model_validator(mode="after")
    def ensure_unique_controls(self) -> "ScenarioRequest":
        controls = self.controls or []
        names = [control.control for control in controls]
        if len(set(names)) != len(names):
            raise ValueError(
                "Duplicate controls provided; ensure each Essential Eight control is unique"
            )
        return self


class ScenarioResponse(BaseModel):
    """Scenario output payload."""

    scenario: str
    monte_carlo: MonteCarloModel
    base_stats: dict[str, float]


@router.post("/run", response_model=ScenarioResponse)
async def run_scenario(
    request: ScenarioRequest, settings: Annotated[AppSettings, Depends(get_settings)]
) -> ScenarioResponse:
    """Execute a scenario with adjusted FAIR parameters based on E8 maturity."""

    engine = ScenarioEngine(iterations=settings.monte_carlo_iterations)
    try:
        controls = [control.to_dataclass() for control in request.controls]
        result = engine.run(request.scenario_key, controls)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    base_stats = {
        "loss_event_frequency": result.loss_event_frequency,
        "secondary_event_frequency": result.secondary_event_frequency,
        "primary_loss": result.loss_magnitude.primary,
        "secondary_loss": result.loss_magnitude.secondary,
    }

    return ScenarioResponse(
        scenario=request.scenario_key,
        monte_carlo=MonteCarloModel.from_dataclass(result.monte_carlo),
        base_stats=base_stats,
    )
