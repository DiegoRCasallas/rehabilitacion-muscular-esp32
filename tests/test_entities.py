import pytest

from app.domain.entities.activity import Activity
from app.domain.entities.calibration_profile import CalibrationProfile
from app.domain.entities.session import Session
from app.domain.entities.signal_features import SignalFeatures


def test_calibration_rechaza_max_menor_que_reposo():
    with pytest.raises(ValueError):
        CalibrationProfile(patient_id=1, label="Bíceps derecho",
                           rest_amplitude=5.0, max_amplitude=2.0, base_frequency=80)


def test_calibration_rechaza_etiqueta_vacia():
    with pytest.raises(ValueError):
        CalibrationProfile(patient_id=1, label="  ",
                           rest_amplitude=1.0, max_amplitude=5.0, base_frequency=80)


def test_signal_features_rechaza_negativos():
    with pytest.raises(ValueError):
        SignalFeatures(amplitude=-1, frequency=50)


def test_activity_requiere_nombre():
    with pytest.raises(ValueError):
        Activity(name="")


def test_session_finish_guarda_puntaje_y_fecha_fin():
    session = Session(patient_id=1, activity_id=1, calibration_id=1)
    session.finish(120)
    assert session.score == 120
    assert session.ended_at is not None