"""Tests for FAIR calculator."""

from backend.engines.fair_calc import FAIRCalculator, FAIRParameters


def test_fair_simulation_runs() -> None:
    params = FAIRParameters(
        threat_event_frequency=(1, 2, 3),
        vulnerability=(0.2, 0.5, 0.8),
        primary_loss=(1000, 2000, 3000),
        secondary_loss=(500, 1000, 2000),
        secondary_event_frequency=(0.1, 0.5, 1.0),
    )
    calculator = FAIRCalculator(iterations=2000)
    result = calculator.run(params)
    assert result.monte_carlo.mean > 0
    assert result.monte_carlo.worst_case >= result.monte_carlo.mean


def test_fair_parameter_validation() -> None:
    try:
        FAIRParameters(
            threat_event_frequency=(-1, 0, 1),
            vulnerability=(0.2, 0.1, 0.3),
            primary_loss=(100, 200, 300),
            secondary_loss=(50, 75, 100),
            secondary_event_frequency=(0.1, 0.2, 0.3),
        )
    except ValueError as exc:
        assert "must be non-negative" in str(exc) or "must satisfy" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for invalid FAIR parameters")
