import math

import pytest

from app import create_app
from app.config import TestConfig
from app.domain.entities.session import Session


def _sine(amplitude, freq=100.0, rate=1000.0, n=200):
    return [amplitude * math.sin(2 * math.pi * freq * i / rate) for i in range(n)]


def _window(amplitude):
    return {"samples": _sine(amplitude), "sample_rate_hz": 1000.0}


@pytest.fixture
def client():
    return create_app(TestConfig).test_client()


@pytest.fixture
def session_id(client):
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    activity = client.post("/activities", json={"name": "Globos"}).get_json()
    calibration = client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps", "rest_amplitude": 0.5,
        "max_amplitude": 4.0, "base_frequency": 100}).get_json()
    return client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": calibration["id"]}).get_json()["id"]


def test_entidad_no_acepta_puntos_tras_finalizar():
    session = Session(patient_id=1, activity_id=1, calibration_id=1)
    session.finish(10)
    with pytest.raises(ValueError):
        session.add_points(5)


def test_flujo_en_vivo_acumula_puntaje(client, session_id):
    fuerte = client.post(f"/sessions/{session_id}/readings", json=_window(2.0)).get_json()
    assert fuerte["activation"] > 0.5
    assert fuerte["score"] == 10
    assert fuerte["windows_received"] == 1

    debil = client.post(f"/sessions/{session_id}/readings", json=_window(0.5)).get_json()
    assert debil["activation"] < 0.5
    assert debil["score"] == 10          # una contracción débil no suma
    assert debil["windows_received"] == 2

    client.post(f"/sessions/{session_id}/readings", json=_window(2.0))

    live = client.get(f"/sessions/{session_id}/live").get_json()
    assert live["score"] == 20
    assert live["windows_received"] == 3

    closed = client.post(f"/sessions/{session_id}/close").get_json()
    assert closed["score"] == 20
    assert closed["ended_at"] is not None


def test_no_acepta_lecturas_tras_cerrar(client, session_id):
    client.post(f"/sessions/{session_id}/close")
    res = client.post(f"/sessions/{session_id}/readings", json=_window(2.0))
    assert res.status_code == 400


def test_estado_en_vivo_sin_lecturas_devuelve_404(client, session_id):
    assert client.get(f"/sessions/{session_id}/live").status_code == 404


def test_lectura_para_sesion_inexistente_devuelve_404(client):
    assert client.post("/sessions/999/readings", json=_window(2.0)).status_code == 404


def test_lectura_invalida_devuelve_422(client, session_id):
    res = client.post(f"/sessions/{session_id}/readings", json={"samples": [1.0]})
    assert res.status_code == 422