from flask import Blueprint, jsonify, request

from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import ActivityCreateSchema
from app.presentation.serializers import serialize

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")


@activities_bp.post("")
def create_activity():
    data = ActivityCreateSchema().load(request.get_json(silent=True) or {})
    activity = get_container().activity_service.create(**data)
    return jsonify(serialize(activity)), 201