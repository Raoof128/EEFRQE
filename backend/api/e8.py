"""API router exposing Essential Eight maturity scoring functionality."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from backend.engines.e8_score import E8AssessmentResult, EssentialEightEngine
from backend.engines.regulation_mapping import RegulationMapper
from backend.schemas import ControlAssessmentModel, E8AssessmentModel, RegulatorySignalModel

router = APIRouter()


class ControlInput(BaseModel):
    """Input schema for a single control's maturity score."""

    level: int = Field(..., ge=0, le=3, description="Maturity level 0-3 as defined by ACSC")
    notes: str | None = Field(None, description="Optional context or evidence")


class E8Request(BaseModel):
    """Payload for Essential Eight scoring."""

    organisation: str = Field(..., description="Synthetic organisation name for labelling")
    industry: str = Field(..., description="Industry sector (finance, health, telco, etc.)")
    assessments: dict[str, ControlInput]

    @field_validator("assessments")
    @classmethod
    def validate_controls(cls, value: dict[str, ControlInput]) -> dict[str, ControlInput]:
        expected_controls = {control.value for control in EssentialEightEngine.CONTROLS}
        provided_controls = set(value.keys())
        missing = expected_controls - provided_controls
        if missing:
            raise ValueError(f"Missing control assessments: {', '.join(sorted(missing))}")
        extra = provided_controls - expected_controls
        if extra:
            raise ValueError(f"Unsupported controls provided: {', '.join(sorted(extra))}")
        return value


class E8Response(BaseModel):
    """Response shape for maturity calculation including regulatory context."""

    organisation: str
    overall_level: float
    control_results: list[ControlAssessmentModel]
    heatmap: dict[str, str]
    recommendations: list[str]
    regulatory_signals: list[RegulatorySignalModel]


@router.post("/score", response_model=E8Response)
async def score_e8(request: E8Request) -> E8Response:
    """Calculate Essential Eight maturity results."""

    engine = EssentialEightEngine(industry=request.industry)
    try:
        assessment_input = {k: v.level for k, v in request.assessments.items()}
        assessment: E8AssessmentResult = engine.calculate(assessment_input)
    except ValueError as exc:  # pragma: no cover - validated above but defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    regulation_mapper = RegulationMapper()
    regulatory_signals = regulation_mapper.build(assessment.controls, industry=request.industry)

    assessment_model = E8AssessmentModel.from_dataclass(assessment)
    return E8Response(
        organisation=request.organisation,
        overall_level=assessment_model.overall_level,
        control_results=assessment_model.controls,
        heatmap=assessment_model.heatmap,
        recommendations=assessment_model.recommendations,
        regulatory_signals=[
            RegulatorySignalModel.from_dataclass(sig) for sig in regulatory_signals
        ],
    )
