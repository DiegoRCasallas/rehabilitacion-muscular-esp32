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


def register_websockets(app) -> None:
    sock = Sock(app)

    @sock.route("/ws/sessions/<int:session_id>/device")
    def device_stream(ws, session_id: int):
        """El ESP32 envía ventanas y recibe el feedback de cada una."""
        service = get_container().streaming_service
        while True:
            raw = ws.receive()
            try:
                data = ReadingSchema().load(json.loads(raw))
                window = SignalWindow(samples=tuple(data["samples"]),
                                      sample_rate_hz=data["sample_rate_hz"])
                _send(ws, serialize(service.push_window(session_id, window)))
            except ValidationError as e:
                _send(ws, {"error": e.messages})
            except (ValueError, NotFoundError) as e:   # JSON inválido incluido
                _send(ws, {"error": str(e)})

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
                    _send(ws, {"type": "ping"})   # detecta clientes desconectados
        finally:
            hub.unsubscribe(session_id, queue)