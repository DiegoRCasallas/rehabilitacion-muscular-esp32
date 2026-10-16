from flask import Blueprint, current_app, render_template

from app.presentation.dependencies import get_container

web_bp = Blueprint("web", __name__, url_prefix="/ui")


@web_bp.get("/")
def index():
    patients = get_container().patient_query.list_all()
    return render_template("index.html", patients=patients)


@web_bp.get("/patients/<int:patient_id>")
def patient_dashboard(patient_id: int):
    dashboard = get_container().dashboard_service.for_patient(patient_id)
    return render_template("patient.html", dashboard=dashboard)


@web_bp.get("/patients/<int:patient_id>/play")
def play(patient_id: int):
    container = get_container()
    return render_template(
        "play.html",
        patient=container.patient_service.get(patient_id),
        calibrations=container.calibration_query.list_for_patient(patient_id),
        activities=container.activity_query.list_all(),
        threshold=current_app.config["ACTIVATION_THRESHOLD"])