from typing import Sequence

from app.domain.entities.session import Session
from app.domain.entities.signal_features import SignalFeatures
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.activity_repository import IActivityReader
from app.domain.interfaces.calibration_repository import ICalibrationReader
from app.domain.interfaces.patient_repository import IPatientReader
from app.domain.interfaces.score_calculator import IScoreCalculator
from app.domain.interfaces.session_repository import ISessionReader, ISessionWriter
from app.domain.interfaces.signal_normalizer import ISignalNormalizer


class SessionService:
    def __init__(
        self,
        patients: IPatientReader,
        activities: IActivityReader,
        calibrations: ICalibrationReader,
        session_reader: ISessionReader,
        session_writer: ISessionWriter,
        normalizer: ISignalNormalizer,
        score_calculator: IScoreCalculator,
    ):
        self._patients = patients
        self._activities = activities
        self._calibrations = calibrations
        self._session_reader = session_reader
        self._session_writer = session_writer
        self._normalizer = normalizer
        self._score_calculator = score_calculator

    def start(self, patient_id: int, activity_id: int, calibration_id: int) -> Session:
        if self._patients.get_by_id(patient_id) is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")
        if self._activities.get_by_id(activity_id) is None:
            raise NotFoundError(f"Actividad {activity_id} no existe")
        calibration = self._calibrations.get_by_id(calibration_id)
        if calibration is None or calibration.patient_id != patient_id:
            raise NotFoundError(f"Calibración {calibration_id} no existe para este paciente")

        session = Session(patient_id=patient_id, activity_id=activity_id,
                          calibration_id=calibration_id)
        return self._session_writer.add(session)

    def finish(self, session_id: int, readings: Sequence[SignalFeatures]) -> Session:
        session = self._session_reader.get_by_id(session_id)
        if session is None:
            raise NotFoundError(f"Sesión {session_id} no existe")
        if session.ended_at is not None:
            raise ValueError("La sesión ya fue finalizada")

        profile = self._calibrations.get_by_id(session.calibration_id)
        activations = [self._normalizer.normalize(r, profile) for r in readings]

        session.finish(self._score_calculator.calculate(activations))
        return self._session_writer.update(session)