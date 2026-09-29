from typing import List, Optional

from sqlalchemy.orm import sessionmaker

from app.domain.entities.patient import Patient
from app.domain.interfaces.patient_repository import IPatientReader, IPatientWriter
from app.infrastructure.database.models import PatientModel


def _to_entity(m: PatientModel) -> Patient:
    return Patient(id=m.id, full_name=m.full_name)


class SqlPatientRepository(IPatientReader, IPatientWriter):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        with self._session_factory() as db:
            model = db.get(PatientModel, patient_id)
            return _to_entity(model) if model else None

    def list_all(self) -> List[Patient]:
        with self._session_factory() as db:
            return [_to_entity(m) for m in db.query(PatientModel).all()]

    def add(self, patient: Patient) -> Patient:
        with self._session_factory() as db:
            model = PatientModel(full_name=patient.full_name)
            db.add(model)
            db.commit()
            return _to_entity(model)