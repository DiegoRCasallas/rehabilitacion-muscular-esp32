from datetime import datetime, timedelta, timezone

import pytest

from app import create_app
from app.application.services.stale_session_service import StaleSessionService
from app.config import TestConfig
from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.entities.session import Session
from app.infrastructure.live_state.in_memory_store import InMemoryLiveStateStore
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository


def test_cierra_solo_las_sesiones_antiguas_y_conserva_el_puntaje(session_factory):
    patients = SqlPatientRepository(session_factory)
    activities = SqlActivityRepository(session_factory)
    calibrations = SqlCalibrationRepository(session_factory)
    sessions = SqlSessionRepository(session_factory)

    patient = patients.add(Patient(full_name="Ana"))
    activity = activities.add(Activity(name="Globos"))
    calibration = calibrations.save(CalibrationProfile(
        patient_id=patient.id, label="Bíceps",
        rest_amplitude=1.0, max_amplitude=5.0, base_frequency=80))

    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)

    def open_session(started_at, score):
        return sessions.add(Session(
            patient_id=patient.id, activity_id=activity.id,
            calibration_id=calibration.id, started_at=started_at, score=score))

    old = open_session(now - timedelta(hours=3), score=40)
    recent = open_session(now - timedelta(minutes=10), score=5)

    service = StaleSessionService(sessions, sessions, InMemoryLiveStateStore())
    closed = service.close_stale(max_age_minutes=120, now=now)

    assert [s.id for s in closed] == [old.id]
    assert sessions.get_by_id(old.id).ended_at is not None
    assert sessions.get_by_id(old.id).score == 40
    assert sessions.get_by_id(recent.id).ended_at is None


def test_endpoint_de_mantenimiento_responde_cero_si_no_hay_nada():
    client = create_app(TestConfig).test_client()
    body = client.post("/maintenance/close-stale?max_age_minutes=60").get_json()
    assert body == {"closed": 0, "session_ids": []}