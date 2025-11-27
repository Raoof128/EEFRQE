"""Unit tests for Essential Eight engine."""

from backend.engines.e8_score import EssentialEightEngine


def test_e8_average_and_heatmap() -> None:
    engine = EssentialEightEngine(industry="finance")
    maturity = {control.value: 2 for control in engine.CONTROLS}
    result = engine.calculate(maturity)
    assert result.overall_level == 2
    assert all(assessment.heat == "moderate" for assessment in result.controls)


def test_e8_validation_missing_control() -> None:
    engine = EssentialEightEngine(industry="finance")
    maturity = {control.value: 2 for control in engine.CONTROLS[:-1]}
    try:
        engine.calculate(maturity)
    except ValueError as exc:
        assert "Missing maturity entries" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError")
