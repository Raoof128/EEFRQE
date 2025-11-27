"""Scenario engine validation tests."""

from backend.engines.e8_score import ControlAssessment, ControlName
from backend.engines.scenario_engine import ScenarioEngine


def build_controls(level: int = 2) -> list[ControlAssessment]:
    return [
        ControlAssessment(control=control, level=level, heat="moderate", risk_implication="")
        for control in ControlName
    ]


def test_scenario_runs_with_controls() -> None:
    engine = ScenarioEngine()
    controls = build_controls()
    result = engine.run("ransomware", controls)
    assert result.monte_carlo.mean > 0


def test_scenario_missing_control_raises() -> None:
    engine = ScenarioEngine()
    controls = build_controls()
    controls.pop()  # remove one to trigger validation
    try:
        engine.run("ransomware", controls)
    except ValueError as exc:
        assert "Controls missing" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError when controls are incomplete")
