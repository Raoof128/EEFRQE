from pathlib import Path

from backend.engines.e8_score import ControlAssessment, ControlName, E8AssessmentResult
from backend.engines.fair_calc import FAIRResult, LossMagnitude
from backend.engines.monte_carlo import MonteCarloResult
from backend.utils.pdf_export import export_pdf


def test_export_pdf_writes_file(tmp_path: Path) -> None:
    control = ControlAssessment(
        control=ControlName.APPLICATION_CONTROL,
        level=2,
        heat="moderate",
        risk_implication="test",
    )
    e8_result = E8AssessmentResult(
        overall_level=2.0,
        controls=[control],
        heatmap={control.control.value: control.heat},
        recommendations=["Remediate"],
    )

    fair_result = FAIRResult(
        loss_event_frequency=1.0,
        loss_magnitude=LossMagnitude(primary=1000.0, secondary=500.0),
        secondary_event_frequency=0.5,
        monte_carlo=MonteCarloResult(
            mean=100.0,
            p90=120.0,
            p95=140.0,
            worst_case=200.0,
            samples=[1.0, 2.0],
        ),
    )

    output_file = tmp_path / "report.pdf"
    result_path = export_pdf(
        organisation="Synthetic Org",
        e8=e8_result,
        fair=fair_result,
        recommendations=["Test"],
        output_path=output_file,
    )

    assert result_path.exists()
    assert result_path.stat().st_size > 0
