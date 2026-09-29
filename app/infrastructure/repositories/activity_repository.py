from typing import List, Optional

from sqlalchemy.orm import sessionmaker

from app.domain.entities.activity import Activity
from app.domain.interfaces.activity_repository import IActivityReader, IActivityWriter
from app.infrastructure.database.models import ActivityModel


def _to_entity(m: ActivityModel) -> Activity:
    return Activity(id=m.id, name=m.name)


class SqlActivityRepository(IActivityReader, IActivityWriter):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_by_id(self, activity_id: int) -> Optional[Activity]:
        with self._session_factory() as db:
            model = db.get(ActivityModel, activity_id)
            return _to_entity(model) if model else None

    def list_all(self) -> List[Activity]:
        with self._session_factory() as db:
            return [_to_entity(m) for m in db.query(ActivityModel).all()]

    def add(self, activity: Activity) -> Activity:
        with self._session_factory() as db:
            model = ActivityModel(name=activity.name)
            db.add(model)
            db.commit()
            return _to_entity(model)