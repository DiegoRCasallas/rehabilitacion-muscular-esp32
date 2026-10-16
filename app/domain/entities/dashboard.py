from dataclasses import dataclass
from typing import List

from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.daily_history import DailyHistory
from app.domain.entities.patient import Patient
from app.domain.entities.progress import PlanProgress
from app.domain.entities.rehabilitation_plan import RehabilitationPlan


@dataclass(frozen=True)
class PlanSummary:
    plan: RehabilitationPlan
    progress: PlanProgress


@dataclass(frozen=True)
class PatientDashboard:
    patient: Patient
    calibrations: List[CalibrationProfile]
    plans: List[PlanSummary]
    history: List[DailyHistory]
    recovery_percentage: float