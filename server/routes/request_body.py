from flask import abort, request


def json_body() -> dict:
    """Return the request's JSON object, or 400 if the body is missing or not an object."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="Request body must be a JSON object.")
    return data
