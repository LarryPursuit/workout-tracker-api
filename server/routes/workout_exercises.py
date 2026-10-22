from flask import Blueprint

from extensions import db
from models import Exercise, Workout, WorkoutExercise
from routes.request_body import json_body
from schemas import WorkoutExerciseSchema

workout_exercises_bp = Blueprint("workout_exercises", __name__)

workout_exercise_schema = WorkoutExerciseSchema()


@workout_exercises_bp.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.get_or_404(Workout, workout_id, description="Workout not found.")
    exercise = db.get_or_404(Exercise, exercise_id, description="Exercise not found.")
    data = workout_exercise_schema.load(json_body())

    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return workout_exercise_schema.dump(workout_exercise), 201
