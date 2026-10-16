from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app import create_app
from app.config import TestConfig


@pytest.fixture
def client():
    return create_app(TestConfig).test_client()


@pytest.fixture
def patient(client):
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    client.post("/activities", json={"name": "Dino EMG"})
    client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps", "rest_amplitude": 60,
        "max_amplitude": 900, "base_frequency": 80})
    today = datetime.now(ZoneInfo("America/Bogota")).date().isoformat()
    client.post(f"/patients/{patient['id']}/plans", json={
        "name": "Codo", "goal_type": "sessions", "goal_target": 10,
        "daily_score_goal": 100, "start_date": today})
    return patient


def test_indice_lista_pacientes(client, patient):
    html = client.get("/ui/").get_data(as_text=True)
    assert "Ana" in html
    assert f"/ui/patients/{patient['id']}/play" in html


def test_panel_muestra_plan_y_calibracion(client, patient):
    res = client.get(f"/ui/patients/{patient['id']}")
    html = res.get_data(as_text=True)
    assert res.status_code == 200
    assert "Codo" in html
    assert "Bíceps" in html


def test_panel_de_paciente_inexistente_devuelve_404(client):
    assert client.get("/ui/patients/999").status_code == 404


def test_pantalla_de_juego_incluye_opciones_y_umbral(client, patient):
    html = client.get(f"/ui/patients/{patient['id']}/play").get_data(as_text=True)
    assert "Dino EMG" in html
    assert "Bíceps" in html
    assert 'data-threshold="0.5"' in html


def test_los_modulos_js_se_sirven_como_estaticos(client):
    assert client.get("/static/js/game/main.js").status_code == 200