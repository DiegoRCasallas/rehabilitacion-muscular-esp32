from flask import Blueprint, jsonify, request

from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import CloseStaleSchema

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


@maintenance_bp.post("/close-stale")
def close_stale():
    params = CloseStaleSchema().load(request.args.to_dict())
    closed = get_container().stale_session_service.close_stale(**params)
    return jsonify(closed=len(closed), session_ids=[s.id for s in closed])