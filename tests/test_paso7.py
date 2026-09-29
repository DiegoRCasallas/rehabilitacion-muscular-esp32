import math
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app import create_app
from app.application.services.goal_policies import GoalPolicyFactory
from app.application.services.plan_service import PlanService
from app.config import TestConfig
from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.entities.session import Session
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.plan_repository import SqlPlanRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository

BOGOTA = ZoneInfo("America/Bogota")


# --- Zona horaria ---

def test_meta_diaria_usa_la_zona_horaria_configurada(session_factory):
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

    # 02:00 UTC del 30 = 21:00 del 29 en Bogotá
    s = sessions.add(Session(patient_id=patient.id, activity_id=activity.id,
                             calibration_id=calibration.id,
                             started_at=datetime(2026, 9, 30, 2, tzinfo=timezone.utc)))
    s.finish(50)
    sessions.update(s)

    service = PlanService(patients, plans, plans, sessions, GoalPolicyFactory(), tz=BOGOTA)
    plan = service.create_plan(patient.id, "Codo", "sessions", 5, 100, date(2026, 9, 1))

    assert service.get_progress(plan.id, today=date(2026, 9, 29)).daily.current == 50
    assert service.get_progress(plan.id, today=date(2026, 9, 30)).daily.current == 0


# --- API ---

def _sine(amplitude, freq=100.0, rate=1000.0, n=200):
    return [amplitude * math.sin(2 * math.pi * freq * i / rate) for i in range(n)]


@pytest.fixture
def client():
    return create_app(TestConfig).test_client()


def _setup_patient(client):
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    activity = client.post("/activities", json={"name": "Globos"}).get_json()
    calibration = client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps", "rest_amplitude": 0.5,
        "max_amplitude": 4.0, "base_frequency": 100}).get_json()
    return patient, activity, calibration


def test_plan_y_progreso_por_api(client):
    patient, activity, calibration = _setup_patient(client)
    yesterday = (datetime.now(BOGOTA).date() - timedelta(days=1)).isoformat()

    plan = client.post(f"/patients/{patient['id']}/plans", json={
        "name": "Codo", "goal_type": "sessions", "goal_target": 2,
        "daily_score_goal": 100, "start_date": yesterday}).get_json()

    session = client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": calibration["id"]}).get_json()
    client.post(f"/sessions/{session['id']}/finish", json={
        "windows": [{"samples": _sine(2.0), "sample_rate_hz": 1000.0}]})

    body = client.get(f"/plans/{plan['id']}/progress").get_json()
    assert body["goal"]["current"] == 1
    assert body["goal"]["percentage"] == 50.0
    assert body["daily"]["current"] == 10
    assert body["daily"]["completed"] is False


def test_recuperacion_es_cero_con_poco_historial(client):
    patient, _, _ = _setup_patient(client)
    body = client.get(f"/patients/{patient['id']}/recovery").get_json()
    assert body["recovery_percentage"] == 0.0


def test_progreso_de_plan_inexistente_devuelve_404(client):
    assert client.get("/plans/999/progress").status_code == 404