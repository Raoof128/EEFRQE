"""Reporting endpoints for generating PDF exports."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from backend.config import AppSettings, get_settings
from backend.schemas import ReportRequestModel
from backend.utils.pdf_export import export_pdf

router = APIRouter()


@router.post("/pdf")
async def build_pdf(
    request: ReportRequestModel,
    settings: Annotated[AppSettings, Depends(get_settings)],
) -> FileResponse:
    """Generate a PDF and stream it back to the caller."""

    output_dir = Path(settings.pdf_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf", dir=output_dir) as tmp:
            output = export_pdf(
                organisation=request.organisation,
                e8=request.e8_result.to_dataclass(),
                fair=request.fair_result.to_dataclass(),
                recommendations=request.recommendations,
                output_path=Path(tmp.name),
            )
    except Exception as exc:  # pragma: no cover - passthrough response
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return FileResponse(output, media_type="application/pdf", filename="risk-report.pdf")
