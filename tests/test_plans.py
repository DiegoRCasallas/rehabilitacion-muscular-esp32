from datetime import date, datetime, timezone

import pytest

from app.application.services.goal_policies import (
    GoalPolicyFactory, SessionCountGoal, TotalScoreGoal)
from app.application.services.plan_service import PlanService
from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.entities.progress import Progress
from app.domain.entities.rehabilitation_plan import RehabilitationPlan
from app.domain.entities.session import Session
from app.domain.exceptions import NotFoundError
from app.domain.interfaces.goal_policy import IGoalPolicy
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.plan_repository import SqlPlanRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository


def _finished(score, day):
    s = Session(patient_id=1, activity_id=1, calibration_id=1,
                started_at=datetime(2026, 9, day, 10, tzinfo=timezone.utc))
    s.finish(score)
    return s


# --- Metas ---

def test_meta_por_sesiones_cuenta_las_sesiones():
    progress = SessionCountGoal(target=4).evaluate([_finished(10, 1), _finished(20, 2)])
    assert progress == Progress(current=2, target=4)
    assert progress.percentage == 50.0


def test_meta_por_score_suma_puntajes_y_se_completa():
    progress = TotalScoreGoal(target=100).evaluate([_finished(60, 1), _finished(50, 2)])
    assert progress.current == 110
    assert progress.completed
    assert progress.percentage == 100.0


def test_fabrica_rechaza_tipo_desconocido():
    with pytest.raises(ValueError):
        GoalPolicyFactory().create("inexistente", 5)


def test_fabrica_permite_registrar_un_tipo_nuevo_sin_modificarla():
    class SiempreCumplida(IGoalPolicy):
        def evaluate(self, sessions):
            return Progress(current=1, target=1)

    factory = GoalPolicyFactory()
    factory.register("siempre", lambda target: SiempreCumplida())
    assert factory.create("siempre", 1).evaluate([]).completed


# --- Entidad ---

def test_plan_rechaza_metas_no_positivas():
    with pytest.raises(ValueError):
        RehabilitationPlan(patient_id=1, name="Codo", goal_type="score",
                           goal_target=0, daily_score_goal=50,
                           start_date=date(2026, 9, 1))


# --- PlanService ---

@pytest.fixture
def plan_setup(session_factory):
    patients = SqlPatientRepository(session_factory)
    activities = SqlActivityRepository(session_factory)
    calibrations = SqlCalibrationRepository(session_factory)
    sessions = SqlSessionRepository(session_factory)
    plans = SqlPlanRepository(session_factory)

    patient = patients.add(Patient(full_name="Ana"))
    activity = activities.add(Activity(name="Globos"))
    calibration = calibrations.save(CalibrationProfile(
        patient_id=patient.id, label="Bíceps",
        rest_amplitude=1.0, max_amplitude=5.0, base_frequency=80))

    service = PlanService(patients, plans, plans, sessions, GoalPolicyFactory())

    def play(day, score):
        s = sessions.add(Session(
            patient_id=patient.id, activity_id=activity.id,
            calibration_id=calibration.id,
            started_at=datetime(2026, 9, day, 10, tzinfo=timezone.utc)))
        s.finish(score)
        sessions.update(s)

    return service, patient, play


def test_plan_se_guarda_y_calcula_progreso_con_meta_diaria(plan_setup):
    service, patient, play = plan_setup
    plan = service.create_plan(patient.id, "Codo", "sessions", goal_target=5,
                               daily_score_goal=100, start_date=date(2026, 9, 1))
    play(28, 60)
    play(29, 70)
    play(29, 50)

    progress = service.get_progress(plan.id, today=date(2026, 9, 29))

    assert progress.goal.current == 3
    assert progress.goal.percentage == 60.0
    assert not progress.goal.completed
    assert progress.daily.current == 120
    assert progress.daily.completed


def test_plan_rechaza_paciente_inexistente(plan_setup):
    service, _, _ = plan_setup
    with pytest.raises(NotFoundError):
        service.create_plan(999, "Codo", "score", 100, 50, date(2026, 9, 1))