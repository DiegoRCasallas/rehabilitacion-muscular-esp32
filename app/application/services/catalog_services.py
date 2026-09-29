from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.activity_repository import IActivityWriter
from app.domain.interfaces.calibration_repository import ICalibrationWriter
from app.domain.interfaces.patient_repository import IPatientReader, IPatientWriter


class PatientService:
    def __init__(self, reader: IPatientReader, writer: IPatientWriter):
        self._reader = reader
        self._writer = writer

    def create(self, full_name: str) -> Patient:
        return self._writer.add(Patient(full_name=full_name))

    def get(self, patient_id: int) -> Patient:
        patient = self._reader.get_by_id(patient_id)
        if patient is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")
        return patient


class ActivityService:
    def __init__(self, writer: IActivityWriter):
        self._writer = writer

    def create(self, name: str) -> Activity:
        return self._writer.add(Activity(name=name))


class CalibrationService:
    def __init__(self, patients: IPatientReader, writer: ICalibrationWriter):
        self._patients = patients
        self._writer = writer

    def create(self, patient_id: int, label: str, rest_amplitude: float,
               max_amplitude: float, base_frequency: float) -> CalibrationProfile:
        if self._patients.get_by_id(patient_id) is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")
        return self._writer.save(CalibrationProfile(
            patient_id=patient_id, label=label, rest_amplitude=rest_amplitude,
            max_amplitude=max_amplitude, base_frequency=base_frequency))