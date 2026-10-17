import math

from app import create_app
from app.config import TestConfig
from app.domain.entities.live_feedback import LiveFeedback
from app.infrastructure.live_state.feedback_hub import LiveFeedbackHub


def _fb(session_id, score=0, windows=1):
    return LiveFeedback(session_id=session_id, activation=0.5, amplitude=1.0,
                        frequency=50.0, score=score, windows_received=windows)


def test_hub_conserva_solo_lo_ultimo():
    hub = LiveFeedbackHub()
    queue = hub.subscribe(1)
    hub.publish(_fb(1, score=10))
    hub.publish(_fb(1, score=20))
    assert queue.get_nowait().score == 20
    assert queue.empty()


def test_hub_aisla_las_sesiones():
    hub = LiveFeedbackHub()
    queue = hub.subscribe(1)
    hub.publish(_fb(2))
    assert queue.empty()


def test_hub_no_entrega_tras_cancelar_la_suscripcion():
    hub = LiveFeedbackHub()
    queue = hub.subscribe(1)
    hub.unsubscribe(1, queue)
    hub.publish(_fb(1))
    assert queue.empty()


def test_lectura_http_se_publica_a_los_suscriptores():
    app = create_app(TestConfig)
    client = app.test_client()
    patient = client.post("/patients", json={"full_name": "Ana"}).get_json()
    activity = client.post("/activities", json={"name": "Dino"}).get_json()
    calibration = client.post(f"/patients/{patient['id']}/calibrations", json={
        "label": "Bíceps", "rest_amplitude": 0.5,
        "max_amplitude": 4.0, "base_frequency": 100}).get_json()
    session = client.post("/sessions", json={
        "patient_id": patient["id"], "activity_id": activity["id"],
        "calibration_id": calibration["id"]}).get_json()

    queue = app.extensions["container"].feedback_hub.subscribe(session["id"])
    samples = [2.0 * math.sin(2 * math.pi * 100 * i / 1000) for i in range(200)]
    client.post(f"/sessions/{session['id']}/readings",
                json={"samples": samples, "sample_rate_hz": 1000.0})

    assert queue.get_nowait().windows_received == 1