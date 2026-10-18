import math

import pytest

from app import create_app
from app.application.services.calibration_estimator import PercentileCalibrationEstimator
from app.config import TestConfig
from app.domain.entities.signal_features import SignalFeatures


def _f(amplitude, frequency=50.0):
    return SignalFeatures(amplitude, frequency)


def _window(peak_to_peak, freq=50.0, rate=1000.0, n=200):
    amplitude = peak_to_peak / 2
    samples = [amplitude * math.sin(2 * math.pi * freq * i / rate) for i in range(n)]
    return {"samples": samples, "sample_rate_hz": rate}


# --- Estimador ---

def test_estimador_ignora_artefactos():
    rest = [_f(60)] * 10 + [_f(500)]
    contraction = [_f(800, 70)] * 29 + [_f(9000, 300)]
    estimate = PercentileCalibrationEstimator().estimate(rest, contraction)
    assert estimate.rest_amplitude == 60
    assert estimate.max_amplitude == 800
    assert estimate.base_frequency == 70


def test_estimador_rechaza_contraccion_debil():
    with pytest.raises(ValueError):
        PercentileCalibrationEstimator().estimate([_f(60)] * 10, [_f(90)] * 10)


def test_estimador_rechaza_pocas_ventanas():
    with pytest.raises(ValueError):
        PercentileCalibrationEstimator().estimate([_f(60)] * 3, [_f(800)] * 10)


# --- API ---

@pytest.fixture
def client():
    return create_app(TestConfig).test_client()


@pytest.fixture
def patient(client):
    return client.post("/patients", json={"full_name": "Ana"}).get_json()


def _start(client, patient):
    return client.post(f"/patients/{patient['id']}/calibration-runs").get_json()["run_id"]


def _protocol(client, run_id, rest_pp=60, contraction_pp=800, windows=12):
    for phase, peak_to_peak in (("rest", rest_pp), ("contraction", contraction_pp)):
        client.post(f"/calibration-runs/{run_id}/phase", json={"phase": phase})
        for _ in range(windows):
            client.post(f"/calibration-runs/{run_id}/readings", json=_window(peak_to_peak))


def test_calibracion_guiada_crea_el_perfil(client, patient):
    run_id = _start(client, patient)
    _protocol(client, run_id)

    res = client.post(f"/calibration-runs/{run_id}/finish", json={"label": "Bíceps derecho"})
    body = res.get_json()
    assert res.status_code == 201
    assert body["rest_amplitude"] == pytest.approx(60, abs=1)
    assert body["max_amplitude"] == pytest.approx(800, abs=1)

    listed = client.get(f"/patients/{patient['id']}/calibrations").get_json()
    assert [c["label"] for c in listed] == ["Bíceps derecho"]
    assert client.get(f"/calibration-runs/{run_id}").status_code == 404   # la corrida se cerró


def test_contraccion_debil_devuelve_400_y_no_crea_perfil(client, patient):
    run_id = _start(client, patient)
    _protocol(client, run_id, contraction_pp=80)

    res = client.post(f"/calibration-runs/{run_id}/finish", json={"label": "Bíceps"})
    assert res.status_code == 400
    assert client.get(f"/patients/{patient['id']}/calibrations").get_json() == []


def test_la_fase_idle_descarta_las_ventanas(client, patient):
    run_id = _start(client, patient)
    client.post(f"/calibration-runs/{run_id}/readings", json=_window(60))

    status = client.get(f"/calibration-runs/{run_id}").get_json()
    assert status["total_windows"] == 1
    assert status["rest_windows"] == 0
    assert status["contraction_windows"] == 0
    assert status["last_amplitude"] == pytest.approx(60, abs=1)


def test_fase_invalida_devuelve_422(client, patient):
    run_id = _start(client, patient)
    res = client.post(f"/calibration-runs/{run_id}/phase", json={"phase": "salto"})
    assert res.status_code == 422


def test_el_dispositivo_encuentra_la_calibracion_activa(client, patient):
    active = f"/patients/{patient['id']}/calibration-runs/active"
    assert client.get(active).status_code == 404
    run_id = _start(client, patient)
    assert client.get(active).get_json()["run_id"] == run_id


def test_iniciar_otra_calibracion_reemplaza_la_anterior(client, patient):
    first = _start(client, patient)
    second = _start(client, patient)
    assert first != second
    assert client.get(f"/calibration-runs/{first}").status_code == 404
    assert client.get(f"/calibration-runs/{second}").status_code == 200


def test_cancelar_elimina_la_corrida(client, patient):
    run_id = _start(client, patient)
    assert client.delete(f"/calibration-runs/{run_id}").status_code == 204
    assert client.get(f"/calibration-runs/{run_id}").status_code == 404


def test_calibracion_de_paciente_inexistente_devuelve_404(client):
    assert client.post("/patients/999/calibration-runs").status_code == 404


def test_el_dispositivo_encuentra_la_sesion_abierta(client, patient):
    open_url = f"/patients/{patient['id']}/sessions/open"
    assert client.get(open_url).status_code == 404

    activity = client.get("/activities").get_json()[0]
    calibration = client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps", "rest_amplitude": 60,
        "max_amplitude": 900, "base_frequency": 80}).get_json()
    session = client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": calibration["id"]}).get_json()

    assert client.get(open_url).get_json()["id"] == session["id"]
    client.post(f"/sessions/{session['id']}/close")
    assert client.get(open_url).status_code == 404