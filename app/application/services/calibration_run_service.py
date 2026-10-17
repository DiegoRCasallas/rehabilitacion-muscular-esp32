from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.calibration_run import CalibrationRun, CalibrationRunStatus
from app.domain.entities.signal_window import SignalWindow
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.calibration_estimator import ICalibrationEstimator
from app.domain.interfaces.calibration_repository import ICalibrationWriter
from app.domain.interfaces.calibration_run_store import (
    ICalibrationRunReader, ICalibrationRunWriter)
from app.domain.interfaces.patient_repository import IPatientReader
from app.domain.interfaces.signal_feature_extractor import ISignalFeatureExtractor


class CalibrationRunService:
    def __init__(self, patients: IPatientReader, run_reader: ICalibrationRunReader,
                 run_writer: ICalibrationRunWriter, extractor: ISignalFeatureExtractor,
                 estimator: ICalibrationEstimator, calibrations: ICalibrationWriter):
        self._patients = patients
        self._reader = run_reader
        self._writer = run_writer
        self._extractor = extractor
        self._estimator = estimator
        self._calibrations = calibrations

    def start(self, patient_id: int) -> CalibrationRunStatus:
        if self._patients.get_by_id(patient_id) is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")
        previous = self._reader.get_active_for_patient(patient_id)
        if previous is not None:                       # una sola calibración activa por paciente
            self._writer.remove(previous.id)
        return self._writer.add(CalibrationRun(patient_id=patient_id)).status()

    def active_for_patient(self, patient_id: int) -> CalibrationRunStatus:
        run = self._reader.get_active_for_patient(patient_id)
        if run is None:
            raise NotFoundError(f"Paciente {patient_id} sin calibración en curso")
        return run.status()

    def status(self, run_id: int) -> CalibrationRunStatus:
        return self._get(run_id).status()

    def set_phase(self, run_id: int, phase: str) -> CalibrationRunStatus:
        run = self._get(run_id)
        run.set_phase(phase)
        return run.status()

    def push_window(self, run_id: int, window: SignalWindow) -> CalibrationRunStatus:
        run = self._get(run_id)
        run.record(self._extractor.extract(window))
        return run.status()

    def finish(self, run_id: int, label: str) -> CalibrationProfile:
        run = self._get(run_id)
        estimate = self._estimator.estimate(run.rest, run.contraction)
        profile = self._calibrations.save(CalibrationProfile(
            patient_id=run.patient_id, label=label,
            rest_amplitude=estimate.rest_amplitude,
            max_amplitude=estimate.max_amplitude,
            base_frequency=estimate.base_frequency))
        self._writer.remove(run_id)                    # si falla la estimación, la corrida sigue viva
        return profile

    def cancel(self, run_id: int) -> None:
        self._get(run_id)
        self._writer.remove(run_id)

    def _get(self, run_id: int) -> CalibrationRun:
        run = self._reader.get(run_id)
        if run is None:
            raise NotFoundError(f"Calibración en curso {run_id} no existe")
        return run