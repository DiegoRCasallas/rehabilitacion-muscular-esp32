from flask import Flask

from app.config import BaseConfig
from app.container import Container
from app.presentation.controllers.activities_controller import activities_bp
from app.presentation.controllers.health_controller import health_bp
from app.presentation.controllers.history_controller import history_bp
from app.presentation.controllers.maintenance_controller import maintenance_bp
from app.presentation.controllers.patients_controller import patients_bp
from app.presentation.controllers.plans_controller import plans_bp
from app.presentation.controllers.sessions_controller import sessions_bp
from app.presentation.controllers.web_controller import web_bp
from app.presentation.error_handlers import register_error_handlers
from app.presentation.websockets import register_websockets

from app.presentation.controllers.calibration_controller import calibration_bp


def create_app(config_class=BaseConfig) -> Flask:
    app = Flask(__name__,
                template_folder="presentation/templates",
                static_folder="presentation/static")
    app.config.from_object(config_class)
    app.extensions["container"] = Container(app.config["DATABASE_URL"],
                                            app.config["TIMEZONE"],
                                            app.config["ACTIVATION_THRESHOLD"],
                                            app.config["SIGNAL_MODE"])
    
    for blueprint in (health_bp, patients_bp, activities_bp, sessions_bp,
                      plans_bp, history_bp, maintenance_bp, calibration_bp, web_bp):
        app.register_blueprint(blueprint)
    register_error_handlers(app)
    register_websockets(app)

    return app