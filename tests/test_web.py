from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app import create_app
from app.config import TestConfig


@pytest.fixture
def app():
    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def patient(client):
    return client.post("/patients", json={"full_name": "Ana"}).get_json()


@pytest.fixture
def calibrated(client, patient):
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
    assert f"/ui/patients/{patient['id']}" in html


def test_panel_bloquea_el_juego_sin_calibracion(client, patient):
    html = client.get(f"/ui/patients/{patient['id']}").get_data(as_text=True)
    assert "Empezar calibración" in html
    assert "Primero calibra" in html
    assert "Elegir juego" not in html


def test_panel_habilita_el_juego_con_calibracion(client, calibrated):
    html = client.get(f"/ui/patients/{calibrated['id']}").get_data(as_text=True)
    assert "Elegir juego" in html
    assert "Bíceps" in html


def test_jugar_sin_calibracion_redirige_a_calibrar(client, patient):
    for path in ("play", "play/dino"):
        res = client.get(f"/ui/patients/{patient['id']}/{path}")
        assert res.status_code == 302
        assert "/calibrate" in res.headers["Location"]


def test_pantalla_de_calibracion(client, patient):
    res = client.get(f"/ui/patients/{patient['id']}/calibrate?needed=1")
    html = res.get_data(as_text=True)
    assert res.status_code == 200
    assert "antes de jugar" in html
    assert 'id="start"' in html


def test_seleccion_de_juegos_muestra_el_catalogo(client, calibrated):
    html = client.get(f"/ui/patients/{calibrated['id']}/play").get_data(as_text=True)
    assert "Dino EMG" in html
    assert "Sigue la línea" in html


def test_pantalla_de_juego_incluye_umbral_y_juego(client, calibrated):
    html = client.get(f"/ui/patients/{calibrated['id']}/play/dino").get_data(as_text=True)
    assert 'data-game="dino"' in html
    assert 'data-threshold="0.5"' in html
    assert "Bíceps" in html


def test_juego_inexistente_devuelve_404(client, calibrated):
    assert client.get(f"/ui/patients/{calibrated['id']}/play/inexistente").status_code == 404


def test_panel_de_recuperacion_muestra_el_plan(client, calibrated):
    res = client.get(f"/ui/patients/{calibrated['id']}/recovery")
    assert res.status_code == 200
    assert "Codo" in res.get_data(as_text=True)


def test_paciente_inexistente_devuelve_404(client):
    assert client.get("/ui/patients/999").status_code == 404


def test_catalogo_no_duplica_actividades(app, client):
    catalog = app.extensions["container"].game_catalog
    catalog.ensure_seeded()
    assert [g.name for g in catalog.list()] == ["Dino EMG", "Sigue la línea"]
    assert len(client.get("/activities").get_json()) == 2


def test_los_modulos_js_se_sirven_como_estaticos(client):
    for path in ("game/main.js", "game/registry.js", "game/tracker.js",
                 "calibration/main.js"):
        assert client.get(f"/static/js/{path}").status_code == 200