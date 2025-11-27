"""PDF export utilities for executive reporting."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from backend.engines.e8_score import E8AssessmentResult
from backend.engines.fair_calc import FAIRResult

logger = logging.getLogger(__name__)


class ReportPDF(FPDF):
    """Simple PDF report generator."""

    def header(self) -> None:  # pragma: no cover - rendering
        self.set_font("Helvetica", "B", 14)
        self.cell(
            0,
            10,
            "Essential Eight + FAIR Executive Report",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
            align="C",
        )
        self.ln(4)

    def footer(self) -> None:  # pragma: no cover - rendering
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(
            0,
            10,
            f"Generated {datetime.now(timezone.utc).isoformat()}",
            align="C",
        )


def export_pdf(
    organisation: str,
    e8: E8AssessmentResult,
    fair: FAIRResult,
    recommendations: List[str],
    output_path: Path,
) -> Path:
    """Create a PDF summary report."""

    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Organisation: {organisation}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(
        0,
        10,
        f"Overall E8 maturity: {e8.overall_level}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Control Heatmap", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=11)
    for control in e8.controls:
        pdf.cell(
            0,
            8,
            f"{control.control.value}: level {control.level} ({control.heat})",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "FAIR Simulation", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(
        0,
        8,
        f"Mean loss: ${fair.monte_carlo.mean:,.0f}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.cell(
        0,
        8,
        f"P95 loss: ${fair.monte_carlo.p95:,.0f}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.cell(
        0,
        8,
        f"Worst case: ${fair.monte_carlo.worst_case:,.0f}",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Recommendations", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", size=11)
    for rec in recommendations:
        pdf.multi_cell(0, 8, f"- {rec}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        pdf.output(str(output_path))
    except OSError as exc:  # pragma: no cover - triggered only on filesystem errors
        logger.exception("Failed to write PDF report: %s", exc)
        raise

    logger.info("PDF report written to %s", output_path)
    return output_path
