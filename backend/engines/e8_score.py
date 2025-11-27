"""Essential Eight scoring engine implementing ACSC maturity rules."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from statistics import mean
from typing import Dict, List

logger = logging.getLogger(__name__)


class ControlName(str, Enum):
    """Enumeration of the Essential Eight controls."""

    APPLICATION_CONTROL = "application_control"
    PATCH_APPLICATIONS = "patch_applications"
    CONFIGURE_MACROS = "configure_ms_office_macros"
    USER_APP_HARDENING = "user_application_hardening"
    RESTRICT_ADMIN = "restrict_admin_privileges"
    PATCH_OS = "patch_operating_systems"
    MFA = "multi_factor_authentication"
    REGULAR_BACKUPS = "regular_backups"


@dataclass
class ControlAssessment:
    """Result for an individual Essential Eight control."""

    control: ControlName
    level: int
    heat: str
    risk_implication: str


@dataclass
class E8AssessmentResult:
    """Composite Essential Eight assessment output."""

    overall_level: float
    controls: List[ControlAssessment]
    heatmap: Dict[str, str]
    recommendations: List[str]


class EssentialEightEngine:
    """Rule-based engine to compute Essential Eight maturity and recommendations."""

    CONTROLS: List[ControlName] = list(ControlName)

    def __init__(self, industry: str) -> None:
        self.industry = industry.lower()

    def calculate(self, maturity_map: Dict[str, int]) -> E8AssessmentResult:
        """Compute Essential Eight maturity.

        Args:
            maturity_map: Mapping of control name to maturity level (0-3).

        Returns:
            E8AssessmentResult: Aggregate maturity outcome.
        """

        self._validate(maturity_map)
        controls: List[ControlAssessment] = []
        heatmap: Dict[str, str] = {}
        for control_name, level in maturity_map.items():
            heat = self._heat_for_level(level)
            risk_implication = self._implication(control_name, level)
            controls.append(
                ControlAssessment(
                    control=ControlName(control_name),
                    level=level,
                    heat=heat,
                    risk_implication=risk_implication,
                )
            )
            heatmap[control_name] = heat

        overall_level = round(mean([control.level for control in controls]), 2)
        recommendations = self._recommendations(controls)

        logger.info("Computed Essential Eight maturity level %.2f", overall_level)
        return E8AssessmentResult(
            overall_level=overall_level,
            controls=sorted(controls, key=lambda c: c.control.value),
            heatmap=heatmap,
            recommendations=recommendations,
        )

    def _validate(self, maturity_map: Dict[str, int]) -> None:
        expected = {control.value for control in self.CONTROLS}
        missing = expected - maturity_map.keys()
        extra = maturity_map.keys() - expected
        if missing:
            raise ValueError(f"Missing maturity entries: {', '.join(sorted(missing))}")
        if extra:
            raise ValueError(f"Unsupported controls: {', '.join(sorted(extra))}")
        for name, value in maturity_map.items():
            if not 0 <= value <= 3:
                raise ValueError(f"Invalid level for {name}: {value}; expected 0-3")

    @staticmethod
    def _heat_for_level(level: int) -> str:
        if level == 3:
            return "low"
        if level == 2:
            return "moderate"
        if level == 1:
            return "high"
        return "critical"

    def _implication(self, control_name: str, level: int) -> str:
        base_messages = {
            ControlName.APPLICATION_CONTROL.value: (
                "Application safelisting gaps increase payload execution risk."
            ),
            ControlName.PATCH_APPLICATIONS.value: (
                "Delayed patching leaves public CVEs exploitable."
            ),
            ControlName.CONFIGURE_MACROS.value: (
                "Macro execution may enable malware via documents."
            ),
            ControlName.USER_APP_HARDENING.value: (
                "Browser and PDF weaknesses heighten drive-by risks."
            ),
            ControlName.RESTRICT_ADMIN.value: ("Excessive privileges accelerate lateral movement."),
            ControlName.PATCH_OS.value: (
                "Unpatched OS exposes kernel and privilege escalation flaws."
            ),
            ControlName.MFA.value: "Lack of MFA increases credential stuffing success.",
            ControlName.REGULAR_BACKUPS.value: (
                "Weak backups reduce ransomware recovery confidence."
            ),
        }
        severity_prefix = {
            0: "Severe: ",
            1: "Significant: ",
            2: "Managed: ",
            3: "Optimised: ",
        }
        return severity_prefix[level] + base_messages.get(control_name, "Operational gap detected.")

    def _recommendations(self, controls: List[ControlAssessment]) -> List[str]:
        recommendations: List[str] = []
        for assessment in sorted(controls, key=lambda c: c.level):
            if assessment.level >= 3:
                continue
            recommendations.append(
                f"Elevate {assessment.control.value} to level {assessment.level + 1} "
                "by implementing ACSC hardening patterns and validating through assurance testing."
            )
        recommendations.append(
            (
                "Validate backups with offline copies and recovery drills to satisfy Privacy Act "
                "and SOCI expectations."
            )
        )
        return recommendations
