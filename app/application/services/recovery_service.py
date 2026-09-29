from app.domain.exceptions import NotFoundError
from app.domain.interfaces.patient_repository import IPatientReader
from app.domain.interfaces.recovery_metric import IRecoveryMetric
from app.domain.interfaces.session_repository import ISessionReader


class RecoveryService:
    def __init__(self, patients: IPatientReader, sessions: ISessionReader,
                 metric: IRecoveryMetric):
        self._patients = patients
        self._sessions = sessions
        self._metric = metric

    def calculate(self, patient_id: int) -> float:
        if self._patients.get_by_id(patient_id) is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")
        return self._metric.calculate(self._sessions.list_by_patient(patient_id))