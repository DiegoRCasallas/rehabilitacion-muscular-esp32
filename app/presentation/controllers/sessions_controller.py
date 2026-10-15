from flask import Blueprint, jsonify, request

from app.domain.entities.signal_window import SignalWindow
from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import (
    ReadingSchema, SessionFinishSchema, SessionStartSchema)
from app.presentation.serializers import serialize

sessions_bp = Blueprint("sessions", __name__, url_prefix="/sessions")


def _to_window(data: dict) -> SignalWindow:
    return SignalWindow(samples=tuple(data["samples"]),
                        sample_rate_hz=data["sample_rate_hz"])


@sessions_bp.post("")
def start_session():
    data = SessionStartSchema().load(request.get_json(silent=True) or {})
    session = get_container().session_service.start(**data)
    return jsonify(serialize(session)), 201


# --- Modo por lotes: todas las lecturas al final ---
@sessions_bp.post("/<int:session_id>/finish")
def finish_session(session_id: int):
    data = SessionFinishSchema().load(request.get_json(silent=True) or {})
    windows = [_to_window(w) for w in data["windows"]]
    session = get_container().reading_service.finish_with_windows(session_id, windows)
    return jsonify(serialize(session))


# --- Modo en vivo ---
@sessions_bp.post("/<int:session_id>/readings")
def push_reading(session_id: int):
    data = ReadingSchema().load(request.get_json(silent=True) or {})
    feedback = get_container().live_session_service.push_window(
        session_id, _to_window(data))
    return jsonify(serialize(feedback))


@sessions_bp.get("/<int:session_id>/live")
def live_state(session_id: int):
    return jsonify(serialize(get_container().live_session_service.get_live(session_id)))


@sessions_bp.post("/<int:session_id>/close")
def close_session(session_id: int):
    return jsonify(serialize(get_container().live_session_service.close(session_id)))

@sessions_bp.get("/<int:session_id>")
def get_session(session_id: int):
    return jsonify(serialize(get_container().session_query.get(session_id)))
