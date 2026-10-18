import pytest

from app import create_app
from app.application.services.level_feature_extractor import LevelFeatureExtractor
from app.config import TestConfig
from app.domain.entities.signal_window import SignalWindow


class LevelConfig(TestConfig):
    SIGNAL_MODE = "level"


def test_extractor_promedia_la_ventana():
    window = SignalWindow(samples=(100.0, 200.0, 300.0), sample_rate_hz=1000.0)
    features = LevelFeatureExtractor().extract(window)
    assert features.amplitude == 200.0
    assert features.frequency == 0.0


@pytest.fixture
def client():
    return create_app(LevelConfig).test_client()


def _level(value, n=100):
    return {"samples": [value] * n, "sample_rate_hz": 1000.0}


def test_calibracion_y_sesion_con_niveles(client):
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    run_id = client.post(f"/patients/{patient['id']}/calibration-runs").get_json()["run_id"]

    for phase, level in (("rest", 100), ("contraction", 900)):
        client.post(f"/calibration-runs/{run_id}/phase", json={"phase": phase})
        for _ in range(12):
            client.post(f"/calibration-runs/{run_id}/readings", json=_level(level))

    res = client.post(f"/calibration-runs/{run_id}/finish", json={"label": "Pot"})
    profile = res.get_json()
    assert res.status_code == 201
    assert profile["rest_amplitude"] == 100
    assert profile["max_amplitude"] == 900
    assert profile["base_frequency"] == 0

    activity = client.get("/activities").get_json()[0]
    session = client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": profile["id"]}).get_json()

    medio = client.post(f"/sessions/{session['id']}/readings", json=_level(500)).get_json()
    assert medio["activation"] == pytest.approx(0.5)
    fuerte = client.post(f"/sessions/{session['id']}/readings", json=_level(900)).get_json()
    assert fuerte["activation"] == 1.0