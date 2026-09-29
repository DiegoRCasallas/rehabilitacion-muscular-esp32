from flask import Flask
from app.config import BaseConfig


def create_app(config_class=BaseConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.presentation.controllers.health_controller import health_bp
    app.register_blueprint(health_bp)

    return app