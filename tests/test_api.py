import math

import pytest

from app import create_app
from app.application.services.fft_feature_extractor import FftFeatureExtractor
from app.config import TestConfig
from app.domain.entities.signal_window import SignalWindow


def _sine(amplitude, freq=100.0, rate=1000.0, n=200):
    return [amplitude * math.sin(2 * math.pi * freq * i / rate) for i in range(n)]


# --- Extractor ---

# def test_extractor_recupera_amplitud_y_frecuencia():
#     window = SignalWindow(samples=tuple(_sine(2.0, n=1000)), sample_rate_hz=1000.0)
#     features = FftFeatureExtractor().extract(window)
#     assert features.amplitude == pytest.approx(4.0, abs=0.01)
#     assert features.frequency == pytest.approx(100.0, abs=1.0)

def test_extractor_recupera_amplitud_y_frecuencia():
    rate = 10000.0
    window = SignalWindow(samples=tuple(_sine(2.0, freq=100.0, rate=rate, n=1000)),
                          sample_rate_hz=rate)
    features = FftFeatureExtractor().extract(window)
    assert features.amplitude == pytest.approx(4.0, abs=0.01)
    assert features.frequency == pytest.approx(100.0, abs=1.0)


def test_ventana_rechaza_una_sola_muestra():
    with pytest.raises(ValueError):
        SignalWindow(samples=(1.0,), sample_rate_hz=1000.0)


# --- API ---

@pytest.fixture
def client():
    return create_app(TestConfig).test_client()


def test_flujo_completo_desde_el_esp32(client):
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    activity = client.post("/activities", json={"name": "Globos"}).get_json()
    calibration = client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps derecho", "rest_amplitude": 0.5,
        "max_amplitude": 4.0, "base_frequency": 100}).get_json()

    session = client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": calibration["id"]}).get_json()

    def window(amplitude):
        return {"samples": _sine(amplitude), "sample_rate_hz": 1000.0}

    res = client.post(f"/sessions/{session['id']}/finish", json={
        "windows": [window(2.0), window(0.5), window(2.0)]})

    assert res.status_code == 200
    assert res.get_json()["score"] == 20   # 2 de 3 ventanas superan el umbral


def test_sesion_con_paciente_inexistente_devuelve_404(client):
    res = client.post("/sessions", json={
        "patient_id": 999, "activity_id": 1, "calibration_id": 1})
    assert res.status_code == 404


def test_cuerpo_invalido_devuelve_422(client):
    res = client.post("/patients", json={})
    assert res.status_code == 422