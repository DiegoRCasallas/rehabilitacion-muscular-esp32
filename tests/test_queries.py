import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app import create_app
from app.config import TestConfig

BOGOTA = ZoneInfo("America/Bogota")


def _sine(amplitude, freq=100.0, rate=1000.0, n=200):
    return [amplitude * math.sin(2 * math.pi * freq * i / rate) for i in range(n)]


@pytest.fixture
def client():
    return create_app(TestConfig).test_client()


def _setup(client):
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    activity = client.post("/activities", json={"name": "Globos"}).get_json()
    calibration = client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps", "rest_amplitude": 0.5,
        "max_amplitude": 4.0, "base_frequency": 100}).get_json()
    return patient, activity, calibration


def _play(client, patient, activity, calibration):
    session = client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": calibration["id"]}).get_json()
    client.post(f"/sessions/{session['id']}/finish", json={
        "windows": [{"samples": _sine(2.0), "sample_rate_hz": 1000.0}]})
    return session


def _today():
    return datetime.now(BOGOTA).date()


def test_lista_pacientes(client):
    client.post("/patients", json={"full_name": "Ana"})
    client.post("/patients", json={"full_name": "Luis"})
    names = [p["full_name"] for p in client.get("/patients").get_json()]
    assert names == ["Ana", "Luis"]


def test_lista_actividades(client):
    client.post("/activities", json={"name": "Globos"})
    names = [a["name"] for a in client.get("/activities").get_json()]
    assert "Globos" in names

def test_lista_calibraciones_y_planes_del_paciente(client):
    patient, _, _ = _setup(client)
    client.post(f"/patients/{patient['id']}/plans", json={
        "name": "Codo", "goal_type": "score", "goal_target": 500,
        "daily_score_goal": 100, "start_date": _today().isoformat()})

    calibrations = client.get(f"/patients/{patient['id']}/calibrations").get_json()
    plans = client.get(f"/patients/{patient['id']}/plans").get_json()
    assert [c["label"] for c in calibrations] == ["Bíceps"]
    assert [p["name"] for p in plans] == ["Codo"]


def test_lista_y_detalle_de_sesiones(client):
    patient, activity, calibration = _setup(client)
    session = _play(client, patient, activity, calibration)

    listed = client.get(f"/patients/{patient['id']}/sessions").get_json()
    detail = client.get(f"/sessions/{session['id']}").get_json()
    assert len(listed) == 1
    assert listed[0]["id"] == detail["id"]
    assert detail["score"] == 10


def test_sesion_inexistente_devuelve_404(client):
    assert client.get("/sessions/999").status_code == 404


def test_historial_diario_agrupa_por_dia(client):
    patient, activity, calibration = _setup(client)
    _play(client, patient, activity, calibration)
    _play(client, patient, activity, calibration)

    history = client.get(f"/patients/{patient['id']}/history").get_json()
    assert history == [{"day": _today().isoformat(), "sessions": 2, "total_score": 20}]


def test_filtro_por_fecha_excluye_sesiones(client):
    patient, activity, calibration = _setup(client)
    _play(client, patient, activity, calibration)
    base = f"/patients/{patient['id']}/sessions"
    tomorrow = (_today() + timedelta(days=1)).isoformat()

    assert client.get(f"{base}?from={tomorrow}").get_json() == []
    assert len(client.get(f"{base}?from={_today().isoformat()}").get_json()) == 1


def test_rango_invertido_devuelve_400(client):
    patient, _, _ = _setup(client)
    res = client.get(f"/patients/{patient['id']}/sessions?from=2026-10-10&to=2026-10-01")
    assert res.status_code == 400


def test_fecha_invalida_devuelve_422(client):
    patient, _, _ = _setup(client)
    res = client.get(f"/patients/{patient['id']}/sessions?from=ayer")
    assert res.status_code == 422


def test_historial_de_paciente_inexistente_devuelve_404(client):
    assert client.get("/patients/999/history").status_code == 404