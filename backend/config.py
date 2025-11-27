"""Application configuration using Pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Central application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="E8_FAIR_", case_sensitive=False)

    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://127.0.0.1:3000", "http://localhost:3000"],
        description="Allowed CORS origins for the API.",
    )
    monte_carlo_iterations: int = Field(
        10000, description="Default Monte Carlo iterations for FAIR simulations."
    )
    pdf_output_dir: str = Field(
        "reports", description="Directory where generated PDF reports are stored."
    )
    log_level: str = Field("INFO", description="Application log level")

    @field_validator("monte_carlo_iterations")
    @classmethod
    def validate_iterations(cls, value: int) -> int:
        if value < 1000:
            raise ValueError("monte_carlo_iterations must be at least 1000 for stability")
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            value = [origin.strip() for origin in value.split(",") if origin.strip()]
        if not value:
            raise ValueError("cors_origins cannot be empty")
        return value

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = value.upper()
        if level not in allowed:
            raise ValueError(f"log_level must be one of {', '.join(sorted(allowed))}")
        return level


@lru_cache()
def get_settings() -> AppSettings:
    """Return cached settings instance."""

    return AppSettings()  # type: ignore[call-arg]
