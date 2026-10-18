import json
from queue import Empty

from flask_sock import Sock
from marshmallow import ValidationError

from app.domain.entities.signal_window import SignalWindow
from app.domain.exceptions import NotFoundError
from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import ReadingSchema
from app.presentation.serializers import serialize

HEARTBEAT_SECONDS = 15


def _send(ws, payload: dict) -> None:
    ws.send(json.dumps(payload))


def _serve_windows(ws, handle) -> None:
    """Recibe ventanas JSON; responde con lo que devuelva handle(window)."""
    while True:
        raw = ws.receive()
        try:
            data = ReadingSchema().load(json.loads(raw))
            window = SignalWindow(samples=tuple(data["samples"]),
                                  sample_rate_hz=data["sample_rate_hz"])
            _send(ws, serialize(handle(window)))
        except ValidationError as e:
            _send(ws, {"error": e.messages})
        except (ValueError, NotFoundError) as e:   # JSON inválido incluido
            _send(ws, {"error": str(e)})


def register_websockets(app) -> None:
    sock = Sock(app)

    @sock.route("/ws/sessions/<int:session_id>/device")
    def device_stream(ws, session_id: int):
        """El ESP32 envía ventanas de juego y recibe el feedback."""
        service = get_container().streaming_service
        _serve_windows(ws, lambda window: service.push_window(session_id, window))

    @sock.route("/ws/calibration-runs/<int:run_id>/device")
    def calibration_stream(ws, run_id: int):
        """El ESP32 envía ventanas de calibración y recibe el estado de la corrida."""
        service = get_container().calibration_run_service
        _serve_windows(ws, lambda window: service.push_window(run_id, window))

    @sock.route("/ws/sessions/<int:session_id>/watch")
    def watch_stream(ws, session_id: int):
        """El navegador recibe cada feedback apenas se publica."""
        hub = get_container().feedback_hub
        queue = hub.subscribe(session_id)
        try:
            while True:
                try:
                    _send(ws, serialize(queue.get(timeout=HEARTBEAT_SECONDS)))
                except Empty:
                    _send(ws, {"type": "ping"})
        finally:
            hub.unsubscribe(session_id, queue)