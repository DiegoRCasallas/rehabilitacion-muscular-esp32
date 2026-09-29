from datetime import date, datetime, timezone, tzinfo
from typing import List, Optional

from app.application.services.goal_policies import GoalPolicyFactory
from app.domain.entities.progress import PlanProgress, Progress
from app.domain.entities.rehabilitation_plan import RehabilitationPlan
from app.domain.entities.session import Session
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.patient_repository import IPatientReader
from app.domain.interfaces.plan_repository import IPlanReader, IPlanWriter
from app.domain.interfaces.session_repository import ISessionReader


class PlanService:
    def __init__(
        self,
        patients: IPatientReader,
        plan_reader: IPlanReader,
        plan_writer: IPlanWriter,
        sessions: ISessionReader,
        goal_factory: GoalPolicyFactory,
        tz: tzinfo = timezone.utc,
    ):
        self._patients = patients
        self._plan_reader = plan_reader
        self._plan_writer = plan_writer
        self._sessions = sessions
        self._goal_factory = goal_factory
        self._tz = tz

    def create_plan(self, patient_id: int, name: str, goal_type: str,
                    goal_target: int, daily_score_goal: int,
                    start_date: date) -> RehabilitationPlan:
        if self._patients.get_by_id(patient_id) is None:
            raise NotFoundError(f"Paciente {patient_id} no existe")
        self._goal_factory.create(goal_type, goal_target)  # valida el tipo de meta

        plan = RehabilitationPlan(
            patient_id=patient_id, name=name, goal_type=goal_type,
            goal_target=goal_target, daily_score_goal=daily_score_goal,
            start_date=start_date)
        return self._plan_writer.add(plan)

    def get_progress(self, plan_id: int, today: Optional[date] = None) -> PlanProgress:
        plan = self._plan_reader.get_by_id(plan_id)
        if plan is None:
            raise NotFoundError(f"Plan {plan_id} no existe")

        today = today or datetime.now(self._tz).date()
        sessions = self._plan_sessions(plan)
        goal = self._goal_factory.create(plan.goal_type, plan.goal_target).evaluate(sessions)

        today_score = sum(s.score for s in sessions if self._local_date(s) == today)
        daily = Progress(current=today_score, target=plan.daily_score_goal)
        return PlanProgress(goal=goal, daily=daily)

    def _local_date(self, session: Session) -> date:
        return session.started_at.astimezone(self._tz).date()

    def _plan_sessions(self, plan: RehabilitationPlan) -> List[Session]:
        return [s for s in self._sessions.list_by_patient(plan.patient_id)
                if s.ended_at is not None and self._local_date(s) >= plan.start_date]