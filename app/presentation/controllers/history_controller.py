from flask import Blueprint, jsonify, request

from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import SessionQuerySchema
from app.presentation.serializers import serialize

history_bp = Blueprint("history", __name__)


@history_bp.get("/patients/<int:patient_id>/sessions")
def patient_sessions(patient_id: int):
    filters = SessionQuerySchema().load(request.args.to_dict())
    sessions = get_container().session_query.list_for_patient(patient_id, **filters)
    return jsonify([serialize(s) for s in sessions])


@history_bp.get("/patients/<int:patient_id>/history")
def patient_history(patient_id: int):
    days = get_container().history_service.daily(patient_id)
    return jsonify([serialize(d) for d in days])