from flask import Blueprint

from extensions import db
from models import Workout
from routes.request_body import json_body
from schemas import WorkoutDetailSchema, WorkoutSchema

workouts_bp = Blueprint("workouts", __name__, url_prefix="/workouts")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()


@workouts_bp.get("")
def list_workouts():
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.id).all()
    return workouts_schema.dump(workouts), 200


@workouts_bp.get("/<int:workout_id>")
def get_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id, description="Workout not found.")
    return workout_detail_schema.dump(workout), 200


@workouts_bp.post("")
def create_workout():
    data = workout_schema.load(json_body())
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return workout_detail_schema.dump(workout), 201


@workouts_bp.delete("/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id, description="Workout not found.")
    db.session.delete(workout)
    db.session.commit()
    return "", 204
