from flask import Blueprint, jsonify, request

from app.domain.entities.signal_window import SignalWindow
from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import SessionFinishSchema, SessionStartSchema
from app.presentation.serializers import serialize

sessions_bp = Blueprint("sessions", __name__, url_prefix="/sessions")


@sessions_bp.post("")
def start_session():
    data = SessionStartSchema().load(request.get_json(silent=True) or {})
    session = get_container().session_service.start(**data)
    return jsonify(serialize(session)), 201


@sessions_bp.post("/<int:session_id>/finish")
def finish_session(session_id: int):
    data = SessionFinishSchema().load(request.get_json(silent=True) or {})
    windows = [SignalWindow(samples=tuple(w["samples"]),
                            sample_rate_hz=w["sample_rate_hz"])
               for w in data["windows"]]
    session = get_container().reading_service.finish_with_windows(session_id, windows)
    return jsonify(serialize(session))
