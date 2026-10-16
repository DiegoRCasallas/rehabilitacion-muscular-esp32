from datetime import date
from typing import Optional

from app.application.services.catalog_services import PatientService
from app.application.services.history_service import HistoryService
from app.application.services.plan_service import PlanService
from app.application.services.query_services import (
    CalibrationQueryService, PlanQueryService)
from app.application.services.recovery_service import RecoveryService
from app.domain.entities.dashboard import PatientDashboard, PlanSummary


class DashboardService:
    def __init__(self, patients: PatientService, calibrations: CalibrationQueryService,
                 plan_query: PlanQueryService, plans: PlanService,
                 history: HistoryService, recovery: RecoveryService):
        self._patients = patients
        self._calibrations = calibrations
        self._plan_query = plan_query
        self._plans = plans
        self._history = history
        self._recovery = recovery

    def for_patient(self, patient_id: int, today: Optional[date] = None) -> PatientDashboard:
        patient = self._patients.get(patient_id)      # lanza NotFoundError si no existe
        summaries = [
            PlanSummary(plan=p, progress=self._plans.get_progress(p.id, today))
            for p in self._plan_query.list_for_patient(patient_id)]
        return PatientDashboard(
            patient=patient,
            calibrations=self._calibrations.list_for_patient(patient_id),
            plans=summaries,
            history=self._history.daily(patient_id),
            recovery_percentage=self._recovery.calculate(patient_id))