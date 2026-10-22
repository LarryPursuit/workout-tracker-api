from flask import Blueprint

from extensions import db
from models import Exercise
from routes.request_body import json_body
from schemas import ExerciseDetailSchema, ExerciseSchema

exercises_bp = Blueprint("exercises", __name__, url_prefix="/exercises")

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()


@exercises_bp.get("")
def list_exercises():
    exercises = Exercise.query.order_by(Exercise.name).all()
    return exercises_schema.dump(exercises), 200


@exercises_bp.get("/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id, description="Exercise not found.")
    return exercise_detail_schema.dump(exercise), 200


@exercises_bp.post("")
def create_exercise():
    data = exercise_schema.load(json_body())
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return exercise_detail_schema.dump(exercise), 201


@exercises_bp.delete("/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id, description="Exercise not found.")
    db.session.delete(exercise)
    db.session.commit()
    return "", 204
