from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import sessionmaker

from app.domain.entities.session import Session
from app.domain.interfaces.session_repository import ISessionReader, ISessionWriter
from app.infrastructure.database.models import SessionModel


def _as_utc(value: Optional[datetime]) -> Optional[datetime]:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _to_entity(m: SessionModel) -> Session:
    return Session(
        id=m.id, patient_id=m.patient_id, activity_id=m.activity_id,
        calibration_id=m.calibration_id, score=m.score,
        started_at=_as_utc(m.started_at), ended_at=_as_utc(m.ended_at),
    )


class SqlSessionRepository(ISessionReader, ISessionWriter):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_by_id(self, session_id: int) -> Optional[Session]:
        with self._session_factory() as db:
            model = db.get(SessionModel, session_id)
            return _to_entity(model) if model else None

    def list_by_patient(self, patient_id: int) -> List[Session]:
        with self._session_factory() as db:
            rows = (db.query(SessionModel)
                      .filter_by(patient_id=patient_id)
                      .order_by(SessionModel.started_at)
                      .all())
            return [_to_entity(m) for m in rows]

    def add(self, session: Session) -> Session:
        with self._session_factory() as db:
            model = SessionModel(
                patient_id=session.patient_id, activity_id=session.activity_id,
                calibration_id=session.calibration_id, score=session.score,
                started_at=session.started_at, ended_at=session.ended_at,
            )
            db.add(model)
            db.commit()
            return _to_entity(model)

    def update(self, session: Session) -> Session:
        with self._session_factory() as db:
            model = db.get(SessionModel, session.id)
            if model is None:
                raise ValueError(f"La sesión {session.id} no existe")
            model.score = session.score
            model.ended_at = session.ended_at
            db.commit()
            return _to_entity(model)