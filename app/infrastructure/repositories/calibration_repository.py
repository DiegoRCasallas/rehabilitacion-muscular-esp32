from typing import List, Optional

from sqlalchemy.orm import sessionmaker

from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.interfaces.calibration_repository import ICalibrationReader, ICalibrationWriter
from app.infrastructure.database.models import CalibrationModel


def _to_entity(m: CalibrationModel) -> CalibrationProfile:
    return CalibrationProfile(
        id=m.id, patient_id=m.patient_id, label=m.label,
        rest_amplitude=m.rest_amplitude, max_amplitude=m.max_amplitude,
        base_frequency=m.base_frequency,
    )


class SqlCalibrationRepository(ICalibrationReader, ICalibrationWriter):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_by_id(self, calibration_id: int) -> Optional[CalibrationProfile]:
        with self._session_factory() as db:
            model = db.get(CalibrationModel, calibration_id)
            return _to_entity(model) if model else None

    def list_by_patient(self, patient_id: int) -> List[CalibrationProfile]:
        with self._session_factory() as db:
            rows = db.query(CalibrationModel).filter_by(patient_id=patient_id).all()
            return [_to_entity(m) for m in rows]

    def save(self, profile: CalibrationProfile) -> CalibrationProfile:
        with self._session_factory() as db:
            model = CalibrationModel(
                patient_id=profile.patient_id, label=profile.label,
                rest_amplitude=profile.rest_amplitude,
                max_amplitude=profile.max_amplitude,
                base_frequency=profile.base_frequency,
            )
            db.add(model)
            db.commit()
            return _to_entity(model)