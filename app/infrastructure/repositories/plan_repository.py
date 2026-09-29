from typing import List, Optional

from sqlalchemy.orm import sessionmaker

from app.domain.entities.rehabilitation_plan import RehabilitationPlan
from app.domain.interfaces.plan_repository import IPlanReader, IPlanWriter
from app.infrastructure.database.models import PlanModel


def _to_entity(m: PlanModel) -> RehabilitationPlan:
    return RehabilitationPlan(
        id=m.id, patient_id=m.patient_id, name=m.name, goal_type=m.goal_type,
        goal_target=m.goal_target, daily_score_goal=m.daily_score_goal,
        start_date=m.start_date, active=m.active)


class SqlPlanRepository(IPlanReader, IPlanWriter):
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def get_by_id(self, plan_id: int) -> Optional[RehabilitationPlan]:
        with self._session_factory() as db:
            model = db.get(PlanModel, plan_id)
            return _to_entity(model) if model else None

    def list_by_patient(self, patient_id: int) -> List[RehabilitationPlan]:
        with self._session_factory() as db:
            rows = db.query(PlanModel).filter_by(patient_id=patient_id).all()
            return [_to_entity(m) for m in rows]

    def add(self, plan: RehabilitationPlan) -> RehabilitationPlan:
        with self._session_factory() as db:
            model = PlanModel(
                patient_id=plan.patient_id, name=plan.name,
                goal_type=plan.goal_type, goal_target=plan.goal_target,
                daily_score_goal=plan.daily_score_goal,
                start_date=plan.start_date, active=plan.active)
            db.add(model)
            db.commit()
            return _to_entity(model)