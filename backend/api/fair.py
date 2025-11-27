"""FAIR calculation API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

from backend.config import AppSettings, get_settings
from backend.engines.fair_calc import FAIRCalculator, FAIRParameters, FAIRResult
from backend.schemas import FAIRResultModel

router = APIRouter()


class FAIRPayload(BaseModel):
    """Input schema for FAIR calculations."""

    threat_event_frequency: tuple[float, float, float] = Field(..., description="(min, mode, max)")
    vulnerability: tuple[float, float, float] = Field(..., description="(min, mode, max)")
    primary_loss: tuple[float, float, float] = Field(..., description="(min, mode, max)")
    secondary_loss: tuple[float, float, float] = Field(..., description="(min, mode, max)")
    secondary_event_frequency: tuple[float, float, float] = Field(
        ..., description="(min, mode, max)"
    )

    @field_validator(
        "threat_event_frequency",
        "vulnerability",
        "primary_loss",
        "secondary_loss",
        "secondary_event_frequency",
    )
    @classmethod
    def validate_tuple(cls, value: tuple[float, float, float]) -> tuple[float, float, float]:
        if len(value) != 3:
            raise ValueError("Each FAIR parameter must provide (min, mode, max)")
        return value

    def to_params(self) -> FAIRParameters:
        return FAIRParameters(
            threat_event_frequency=self.threat_event_frequency,
            vulnerability=self.vulnerability,
            primary_loss=self.primary_loss,
            secondary_loss=self.secondary_loss,
            secondary_event_frequency=self.secondary_event_frequency,
        )


@router.post("/calc", response_model=FAIRResultModel)
async def calculate_fair(
    payload: FAIRPayload, settings: Annotated[AppSettings, Depends(get_settings)]
) -> FAIRResultModel:
    """Run FAIR Monte Carlo simulation."""

    calculator = FAIRCalculator(iterations=settings.monte_carlo_iterations)
    try:
        result: FAIRResult = calculator.run(payload.to_params())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return FAIRResultModel.from_dataclass(result)
