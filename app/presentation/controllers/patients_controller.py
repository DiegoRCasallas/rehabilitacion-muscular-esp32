from flask import Blueprint, jsonify, request

from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import CalibrationCreateSchema, PatientCreateSchema
from app.presentation.serializers import serialize

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


@patients_bp.post("")
def create_patient():
    data = PatientCreateSchema().load(request.get_json(silent=True) or {})
    patient = get_container().patient_service.create(**data)
    return jsonify(serialize(patient)), 201


@patients_bp.get("/<int:patient_id>")
def get_patient(patient_id: int):
    return jsonify(serialize(get_container().patient_service.get(patient_id)))


@patients_bp.post("/<int:patient_id>/calibrations")
def create_calibration(patient_id: int):
    data = CalibrationCreateSchema().load(request.get_json(silent=True) or {})
    profile = get_container().calibration_service.create(patient_id=patient_id, **data)
    return jsonify(serialize(profile)), 201