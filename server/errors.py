"""Turns exceptions raised anywhere in a request into consistent JSON error responses."""
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from extensions import db


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_schema_error(error):
        # Marshmallow reports problems per field, e.g. {"name": ["Missing data..."]}.
        return jsonify({"errors": error.messages}), 400

    @app.errorhandler(ValueError)
    def handle_model_error(error):
        # @validates hooks on the models raise ValueError for bad attribute values.
        db.session.rollback()
        return jsonify({"errors": [str(error)]}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        return jsonify({"errors": [_describe_integrity_error(error)]}), 409

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"errors": [error.description]}), error.code


def _describe_integrity_error(error):
    message = str(error.orig)
    if "UNIQUE" in message:
        return "A record with these values already exists."
    if "CHECK" in message:
        return "Values violate a database constraint."
    if "FOREIGN KEY" in message:
        return "Referenced record does not exist."
    return "Database constraint violated."
