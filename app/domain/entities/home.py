from dataclasses import dataclass
from typing import List, Optional

from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient


@dataclass(frozen=True)
class PatientHome:
    patient: Patient
    calibrations: List[CalibrationProfile]

    @property
    def latest_calibration(self) -> Optional[CalibrationProfile]:
        return max(self.calibrations, key=lambda c: c.id) if self.calibrations else None

    @property
    def can_play(self) -> bool:
        return self.latest_calibration is not None