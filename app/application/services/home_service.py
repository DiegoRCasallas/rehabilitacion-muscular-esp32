from app.application.services.catalog_services import PatientService
from app.application.services.query_services import CalibrationQueryService
from app.domain.entities.home import PatientHome


class PatientHomeService:
    def __init__(self, patients: PatientService, calibrations: CalibrationQueryService):
        self._patients = patients
        self._calibrations = calibrations

    def for_patient(self, patient_id: int) -> PatientHome:
        patient = self._patients.get(patient_id)
        return PatientHome(patient=patient,
                           calibrations=self._calibrations.list_for_patient(patient_id))