from flask import Blueprint, current_app, redirect, render_template, request, url_for

from app.presentation.dependencies import get_container

web_bp = Blueprint("web", __name__, url_prefix="/ui")


@web_bp.get("/")
def index():
    return render_template("index.html",
                           patients=get_container().patient_query.list_all())


@web_bp.get("/patients/<int:patient_id>")
def patient_home(patient_id: int):
    home = get_container().home_service.for_patient(patient_id)
    return render_template("patient_home.html", home=home)


@web_bp.get("/patients/<int:patient_id>/calibrate")
def calibrate(patient_id: int):
    home = get_container().home_service.for_patient(patient_id)
    return render_template("calibrate.html", home=home,
                           needed=request.args.get("needed") is not None)


@web_bp.get("/patients/<int:patient_id>/play")
def choose_game(patient_id: int):
    container = get_container()
    home = container.home_service.for_patient(patient_id)
    if not home.can_play:
        return redirect(url_for("web.calibrate", patient_id=patient_id, needed=1))
    return render_template("games.html", home=home, games=container.game_catalog.list())


@web_bp.get("/patients/<int:patient_id>/play/<game_key>")
def play(patient_id: int, game_key: str):
    container = get_container()
    home = container.home_service.for_patient(patient_id)
    if not home.can_play:
        return redirect(url_for("web.calibrate", patient_id=patient_id, needed=1))
    return render_template("play.html", home=home,
                           game=container.game_catalog.get(game_key),
                           threshold=current_app.config["ACTIVATION_THRESHOLD"])


@web_bp.get("/patients/<int:patient_id>/recovery")
def patient_dashboard(patient_id: int):
    dashboard = get_container().dashboard_service.for_patient(patient_id)
    return render_template("patient.html", dashboard=dashboard)