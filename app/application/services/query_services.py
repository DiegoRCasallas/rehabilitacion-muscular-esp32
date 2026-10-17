from datetime import date, timezone, tzinfo
from typing import List, Optional

from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.entities.rehabilitation_plan import RehabilitationPlan
from app.domain.entities.session import Session
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.activity_repository import IActivityReader
from app.domain.interfaces.calibration_repository import ICalibrationReader
from app.domain.interfaces.patient_repository import IPatientReader
from app.domain.interfaces.plan_repository import IPlanReader
from app.domain.interfaces.session_repository import ISessionReader


def _require_patient(patients: IPatientReader, patient_id: int) -> None:
    if patients.get_by_id(patient_id) is None:
        raise NotFoundError(f"Paciente {patient_id} no existe")


class PatientQueryService:
    def __init__(self, patients: IPatientReader):
        self._patients = patients

    def list_all(self) -> List[Patient]:
        return self._patients.list_all()


class ActivityQueryService:
    def __init__(self, activities: IActivityReader):
        self._activities = activities

    def list_all(self) -> List[Activity]:
        return self._activities.list_all()


class CalibrationQueryService:
    def __init__(self, patients: IPatientReader, calibrations: ICalibrationReader):
        self._patients = patients
        self._calibrations = calibrations

    def list_for_patient(self, patient_id: int) -> List[CalibrationProfile]:
        _require_patient(self._patients, patient_id)
        return self._calibrations.list_by_patient(patient_id)


class PlanQueryService:
    def __init__(self, patients: IPatientReader, plans: IPlanReader):
        self._patients = patients
        self._plans = plans

    def list_for_patient(self, patient_id: int) -> List[RehabilitationPlan]:
        _require_patient(self._patients, patient_id)
        return self._plans.list_by_patient(patient_id)


class SessionQueryService:
    def __init__(self, patients: IPatientReader, sessions: ISessionReader,
                 tz: tzinfo = timezone.utc):
        self._patients = patients
        self._sessions = sessions
        self._tz = tz

    def get(self, session_id: int) -> Session:
        session = self._sessions.get_by_id(session_id)
        if session is None:
            raise NotFoundError(f"Sesión {session_id} no existe")
        return session

    def list_for_patient(self, patient_id: int, start: Optional[date] = None,
                         end: Optional[date] = None) -> List[Session]:
        _require_patient(self._patients, patient_id)
        if start and end and start > end:
            raise ValueError("'from' no puede ser posterior a 'to'")

        result = []
        for s in self._sessions.list_by_patient(patient_id):
            local_day = s.started_at.astimezone(self._tz).date()
            if (start is None or local_day >= start) and (end is None or local_day <= end):
                result.append(s)
        return result
    def latest_open(self, patient_id: int) -> Session:
        _require_patient(self._patients, patient_id)
        open_sessions = [s for s in self._sessions.list_by_patient(patient_id)
                            if s.ended_at is None]
        if not open_sessions:
            raise NotFoundError(f"Paciente {patient_id} sin sesión abierta")
        return open_sessions[-1]