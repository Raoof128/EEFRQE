"""Tests for AppSettings configuration."""

import pytest

from backend.config import AppSettings, get_settings


def test_settings_defaults() -> None:
    settings = get_settings()
    assert settings.monte_carlo_iterations >= 1000
    assert settings.cors_origins


def test_settings_validation_error() -> None:
    with pytest.raises(ValueError):
        AppSettings(
            monte_carlo_iterations=10,
            cors_origins=["http://localhost"],
            pdf_output_dir="reports",
            log_level="INFO",
        )

    with pytest.raises(ValueError):
        AppSettings(
            monte_carlo_iterations=1000,
            cors_origins=[],
            pdf_output_dir="reports",
            log_level="INFO",
        )

    with pytest.raises(ValueError):
        AppSettings(
            monte_carlo_iterations=1000,
            cors_origins=["http://localhost"],
            pdf_output_dir="reports",
            log_level="verbose",
        )


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("E8_FAIR_MONTE_CARLO_ITERATIONS", "12000")
    monkeypatch.setenv("E8_FAIR_CORS_ORIGINS", '["http://example.com"]')
    monkeypatch.setenv("E8_FAIR_LOG_LEVEL", "DEBUG")
    settings = AppSettings()  # type: ignore[call-arg]
    assert settings.monte_carlo_iterations == 12000
    assert settings.cors_origins == ["http://example.com"]
    assert settings.log_level == "DEBUG"
