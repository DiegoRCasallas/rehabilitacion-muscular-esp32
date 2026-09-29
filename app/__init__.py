from flask import Flask

from app.config import BaseConfig
from app.container import Container
from app.presentation.controllers.activities_controller import activities_bp
from app.presentation.controllers.health_controller import health_bp
from app.presentation.controllers.patients_controller import patients_bp
from app.presentation.controllers.sessions_controller import sessions_bp
from app.presentation.error_handlers import register_error_handlers


def create_app(config_class=BaseConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.extensions["container"] = Container(app.config["DATABASE_URL"])

    for blueprint in (health_bp, patients_bp, activities_bp, sessions_bp):
        app.register_blueprint(blueprint)
    register_error_handlers(app)

    return app