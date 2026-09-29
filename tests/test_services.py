import pytest

from app.application.services.linear_signal_normalizer import LinearSignalNormalizer
from app.application.services.score_progress_metric import ScoreProgressMetric
from app.application.services.session_service import SessionService
from app.application.services.threshold_score_calculator import ThresholdScoreCalculator
from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.patient import Patient
from app.domain.entities.session import Session
from app.domain.entities.signal_features import SignalFeatures
from app.domain.exceptions import NotFoundError
from app.infrastructure.repositories.activity_repository import SqlActivityRepository
from app.infrastructure.repositories.calibration_repository import SqlCalibrationRepository
from app.infrastructure.repositories.patient_repository import SqlPatientRepository
from app.infrastructure.repositories.session_repository import SqlSessionRepository


def _profile(rest=1.0, maximum=5.0):
    return CalibrationProfile(patient_id=1, label="Bíceps", rest_amplitude=rest,
                              max_amplitude=maximum, base_frequency=80)


# --- Normalizador ---

def test_normalizador_escala_entre_cero_y_uno():
    n = LinearSignalNormalizer()
    assert n.normalize(SignalFeatures(3.0, 80), _profile()) == 0.5


def test_normalizador_limita_los_extremos():
    n = LinearSignalNormalizer()
    assert n.normalize(SignalFeatures(0.2, 80), _profile()) == 0.0
    assert n.normalize(SignalFeatures(9.0, 80), _profile()) == 1.0


def test_misma_senal_da_activacion_distinta_segun_calibracion():
    n = LinearSignalNormalizer()
    signal = SignalFeatures(3.0, 80)
    debil = n.normalize(signal, _profile(rest=1.0, maximum=3.0))
    fuerte = n.normalize(signal, _profile(rest=1.0, maximum=9.0))
    assert debil > fuerte


# --- Puntaje ---

def test_puntaje_cuenta_muestras_sobre_el_umbral():
    calc = ThresholdScoreCalculator(threshold=0.5, points_per_sample=10)
    assert calc.calculate([0.1, 0.5, 0.9, 0.4]) == 20


# --- Métrica de recuperación ---

def _finished(score, day):
    from datetime import datetime, timezone
    s = Session(patient_id=1, activity_id=1, calibration_id=1,
                started_at=datetime(2026, 1, day, tzinfo=timezone.utc))
    s.finish(score)
    return s


def test_recuperacion_mide_mejora_porcentual():
    sessions = [_finished(100, 1), _finished(100, 2), _finished(150, 3), _finished(150, 4)]
    assert ScoreProgressMetric(window=2).calculate(sessions) == 50.0


def test_recuperacion_es_cero_con_historial_insuficiente():
    assert ScoreProgressMetric(window=2).calculate([_finished(100, 1)]) == 0.0


# --- SessionService ---

@pytest.fixture
def service_setup(session_factory):
    patients = SqlPatientRepository(session_factory)
    activities = SqlActivityRepository(session_factory)
    calibrations = SqlCalibrationRepository(session_factory)
    sessions = SqlSessionRepository(session_factory)

    patient = patients.add(Patient(full_name="Ana"))
    activity = activities.add(Activity(name="Globos"))
    calibration = calibrations.save(CalibrationProfile(
        patient_id=patient.id, label="Bíceps",
        rest_amplitude=1.0, max_amplitude=5.0, base_frequency=80))

    service = SessionService(patients, activities, calibrations, sessions, sessions,
                             LinearSignalNormalizer(),
                             ThresholdScoreCalculator(threshold=0.5, points_per_sample=10))
    return service, patient, activity, calibration


def test_flujo_completo_de_sesion(service_setup):
    service, patient, activity, calibration = service_setup
    session = service.start(patient.id, activity.id, calibration.id)

    readings = [SignalFeatures(4.0, 80), SignalFeatures(1.0, 80), SignalFeatures(5.0, 80)]
    finished = service.finish(session.id, readings)

    assert finished.score == 20   # solo 2 de 3 muestras superan el umbral
    assert finished.ended_at is not None


def test_no_permite_finalizar_dos_veces(service_setup):
    service, patient, activity, calibration = service_setup
    session = service.start(patient.id, activity.id, calibration.id)
    service.finish(session.id, [])
    with pytest.raises(ValueError):
        service.finish(session.id, [])


def test_rechaza_calibracion_de_otro_paciente(service_setup):
    service, patient, activity, calibration = service_setup
    with pytest.raises(NotFoundError):
        service.start(patient_id=999, activity_id=activity.id,
                      calibration_id=calibration.id)