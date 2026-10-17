from flask import Blueprint, jsonify, request

from app.domain.entities.signal_window import SignalWindow
from app.presentation.dependencies import get_container
from app.presentation.schemas.schemas import (
    CalibrationFinishSchema, CalibrationPhaseSchema, ReadingSchema)
from app.presentation.serializers import serialize

calibration_bp = Blueprint("calibration", __name__)


def _service():
    return get_container().calibration_run_service


@calibration_bp.post("/patients/<int:patient_id>/calibration-runs")
def start_run(patient_id: int):
    return jsonify(serialize(_service().start(patient_id))), 201


@calibration_bp.get("/patients/<int:patient_id>/calibration-runs/active")
def active_run(patient_id: int):
    return jsonify(serialize(_service().active_for_patient(patient_id)))


@calibration_bp.get("/calibration-runs/<int:run_id>")
def run_status(run_id: int):
    return jsonify(serialize(_service().status(run_id)))


@calibration_bp.post("/calibration-runs/<int:run_id>/phase")
def set_phase(run_id: int):
    data = CalibrationPhaseSchema().load(request.get_json(silent=True) or {})
    return jsonify(serialize(_service().set_phase(run_id, data["phase"])))


@calibration_bp.post("/calibration-runs/<int:run_id>/readings")
def push_reading(run_id: int):
    data = ReadingSchema().load(request.get_json(silent=True) or {})
    window = SignalWindow(samples=tuple(data["samples"]),
                          sample_rate_hz=data["sample_rate_hz"])
    return jsonify(serialize(_service().push_window(run_id, window)))


@calibration_bp.post("/calibration-runs/<int:run_id>/finish")
def finish_run(run_id: int):
    data = CalibrationFinishSchema().load(request.get_json(silent=True) or {})
    return jsonify(serialize(_service().finish(run_id, data["label"]))), 201


@calibration_bp.delete("/calibration-runs/<int:run_id>")
def cancel_run(run_id: int):
    _service().cancel(run_id)
    return "", 204