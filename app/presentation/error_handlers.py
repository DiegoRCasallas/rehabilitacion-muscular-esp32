from flask import Flask, jsonify
from marshmallow import ValidationError

from app.domain.exceptions import NotFoundError


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def validation_error(e):
        return jsonify(errors=e.messages), 422

    @app.errorhandler(NotFoundError)
    def not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(ValueError)
    def bad_request(e):
        return jsonify(error=str(e)), 400