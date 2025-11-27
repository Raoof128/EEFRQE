"""Map Essential Eight posture to Australian regulatory signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from backend.engines.e8_score import ControlAssessment, ControlName


@dataclass
class RegulatorySignal:
    """Regulatory emphasis description."""

    regulation: str
    impact: str
    recommendation: str


class RegulationMapper:
    """Generate regulatory insights aligned to Essential Eight posture."""

    REGULATIONS = [
        "Privacy Act (OAIC)",
        "SOCI Act",
        "APRA CPS 234",
    ]

    def build(self, controls: List[ControlAssessment], industry: str) -> List[RegulatorySignal]:
        """Derive regulatory signals based on weak controls and industry context."""

        signals: List[RegulatorySignal] = []
        low_backup = next(
            (c for c in controls if c.control == ControlName.REGULAR_BACKUPS and c.level < 3),
            None,
        )
        if low_backup:
            signals.append(
                RegulatorySignal(
                    regulation="Privacy Act (OAIC)",
                    impact=(
                        "Higher likelihood of Notifiable Data Breach costs if recovery is delayed."
                    ),
                    recommendation=(
                        "Harden backup segregation and test restoration to minimise notification "
                        "penalties."
                    ),
                )
            )
        low_mfa = next(
            (c for c in controls if c.control == ControlName.MFA and c.level < 3),
            None,
        )
        if low_mfa:
            signals.append(
                RegulatorySignal(
                    regulation="SOCI Act",
                    impact=(
                        "Identity weaknesses undermine critical infrastructure trust obligations."
                    ),
                    recommendation=(
                        "Deploy phishing-resistant MFA for privileged and remote access users."
                    ),
                )
            )
        if industry.lower() in {"finance", "banking", "superannuation"}:
            signals.append(
                RegulatorySignal(
                    regulation="APRA CPS 234",
                    impact=(
                        "APRA expects demonstrable control assurance and timely vulnerability "
                        "remediation."
                    ),
                    recommendation=(
                        "Document control assurance and vulnerability SLAs mapped to CPS 234 "
                        "clauses."
                    ),
                )
            )
        return signals
