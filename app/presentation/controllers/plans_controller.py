from flask import Blueprint, jsonify, request

from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import PlanCreateSchema
from app.presentation.serializers import serialize, serialize_plan_progress

plans_bp = Blueprint("plans", __name__)


@plans_bp.post("/patients/<int:patient_id>/plans")
def create_plan(patient_id: int):
    data = PlanCreateSchema().load(request.get_json(silent=True) or {})
    plan = get_container().plan_service.create_plan(patient_id=patient_id, **data)
    return jsonify(serialize(plan)), 201


@plans_bp.get("/plans/<int:plan_id>/progress")
def plan_progress(plan_id: int):
    progress = get_container().plan_service.get_progress(plan_id)
    return jsonify(serialize_plan_progress(progress))


@plans_bp.get("/patients/<int:patient_id>/recovery")
def recovery(patient_id: int):
    value = get_container().recovery_service.calculate(patient_id)
    return jsonify(patient_id=patient_id, recovery_percentage=value)