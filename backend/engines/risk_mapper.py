"""Translate Essential Eight maturity into FAIR parameter adjustments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, cast

from backend.engines.e8_score import ControlAssessment, ControlName
from backend.engines.fair_calc import FAIRParameters


@dataclass
class RiskAdjustment:
    """Adjustment factors applied to FAIR parameters."""

    tef_multiplier: float
    vulnerability_multiplier: float
    primary_loss_multiplier: float
    secondary_loss_multiplier: float
    secondary_event_multiplier: float


class RiskMapper:
    """Map E8 maturity levels to FAIR adjustments for contextual risk scenarios."""

    def __init__(self, base_params: FAIRParameters) -> None:
        self.base_params = base_params

    def adjust(self, controls: Dict[str, ControlAssessment]) -> FAIRParameters:
        """Return new FAIRParameters scaled according to control maturity."""

        self._validate_controls(controls)
        modifiers = self._control_modifiers(controls)
        return FAIRParameters(
            threat_event_frequency=self._scale(
                self.base_params.threat_event_frequency, modifiers.tef_multiplier
            ),
            vulnerability=self._scale_probability(
                self.base_params.vulnerability, modifiers.vulnerability_multiplier
            ),
            primary_loss=self._scale(
                self.base_params.primary_loss, modifiers.primary_loss_multiplier
            ),
            secondary_loss=self._scale(
                self.base_params.secondary_loss, modifiers.secondary_loss_multiplier
            ),
            secondary_event_frequency=self._scale(
                self.base_params.secondary_event_frequency, modifiers.secondary_event_multiplier
            ),
        )

    @staticmethod
    def _validate_controls(controls: Dict[str, ControlAssessment]) -> None:
        expected = {control.value for control in ControlName}
        missing = expected - set(controls.keys())
        if missing:
            raise ValueError(f"Controls missing for risk mapping: {', '.join(sorted(missing))}")

    def _control_modifiers(self, controls: Dict[str, ControlAssessment]) -> RiskAdjustment:
        worst_level = min(assessment.level for assessment in controls.values())
        tef_multiplier = 1.0 + (0.25 * (3 - worst_level))
        vulnerability_multiplier = 1.0 + (0.3 * (3 - worst_level))

        backup_level = controls[ControlName.REGULAR_BACKUPS.value].level
        secondary_loss_multiplier = 1.0 + (0.2 * (3 - backup_level))

        mfa_level = controls[ControlName.MFA.value].level
        primary_loss_multiplier = 1.0 + (0.15 * (3 - mfa_level))

        patch_level = min(
            controls[ControlName.PATCH_APPLICATIONS.value].level,
            controls[ControlName.PATCH_OS.value].level,
        )
        secondary_event_multiplier = 1.0 + (0.1 * (3 - patch_level))

        return RiskAdjustment(
            tef_multiplier=tef_multiplier,
            vulnerability_multiplier=vulnerability_multiplier,
            primary_loss_multiplier=primary_loss_multiplier,
            secondary_loss_multiplier=secondary_loss_multiplier,
            secondary_event_multiplier=secondary_event_multiplier,
        )

    @staticmethod
    def _scale(values: tuple[float, float, float], multiplier: float) -> tuple[float, float, float]:
        return cast(tuple[float, float, float], tuple(round(v * multiplier, 2) for v in values))

    @staticmethod
    def _scale_probability(
        values: tuple[float, float, float], multiplier: float
    ) -> tuple[float, float, float]:
        """Scale probability triplets while respecting an upper bound of 1."""

        return cast(
            tuple[float, float, float],
            tuple(min(round(v * multiplier, 2), 1.0) for v in values),
        )
