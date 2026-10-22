#!/usr/bin/env python3
"""Reset the database and fill it with sample exercises, workouts, and workout entries."""
from datetime import date

from app import app
from extensions import db
from models import Exercise, Workout, WorkoutExercise

EXERCISES = [
    {"name": "Back Squat", "category": "strength", "equipment_needed": True},
    {"name": "Push-Up", "category": "strength", "equipment_needed": False},
    {"name": "Deadlift", "category": "strength", "equipment_needed": True},
    {"name": "Plank", "category": "balance", "equipment_needed": False},
    {"name": "Rowing Machine", "category": "cardio", "equipment_needed": True},
    {"name": "Jump Rope", "category": "cardio", "equipment_needed": True},
    {"name": "Hamstring Stretch", "category": "flexibility", "equipment_needed": False},
    {"name": "Hip Circles", "category": "mobility", "equipment_needed": False},
]

WORKOUTS = [
    {"date": date(2026, 10, 1), "duration_minutes": 60, "notes": "Lower-body strength day."},
    {"date": date(2026, 10, 3), "duration_minutes": 30, "notes": "Conditioning circuit."},
    {"date": date(2026, 10, 5), "duration_minutes": 45, "notes": "Full body + mobility."},
]

# (workout index, exercise name, entry volume)
WORKOUT_EXERCISES = [
    (0, "Hip Circles", {"duration_seconds": 120}),
    (0, "Back Squat", {"sets": 5, "reps": 5}),
    (0, "Deadlift", {"sets": 3, "reps": 5}),
    (0, "Hamstring Stretch", {"sets": 2, "duration_seconds": 45}),
    (1, "Jump Rope", {"sets": 4, "duration_seconds": 60}),
    (1, "Rowing Machine", {"duration_seconds": 600}),
    (1, "Push-Up", {"sets": 3, "reps": 15}),
    (2, "Push-Up", {"sets": 4, "reps": 12}),
    (2, "Plank", {"sets": 3, "duration_seconds": 60}),
    (2, "Back Squat", {"sets": 3, "reps": 10}),
]


def seed():
    # Delete the join table first so no foreign keys point at removed rows.
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    exercises = {data["name"]: Exercise(**data) for data in EXERCISES}
    workouts = [Workout(**data) for data in WORKOUTS]
    # Flush before linking: relationship cascades would otherwise insert rows out of
    # list order, and the README examples rely on the ids matching these lists.
    db.session.add_all([*exercises.values(), *workouts])
    db.session.flush()

    entries = [
        WorkoutExercise(workout=workouts[index], exercise=exercises[name], **volume)
        for index, name, volume in WORKOUT_EXERCISES
    ]
    db.session.add_all(entries)
    db.session.commit()
    return len(exercises), len(workouts), len(entries)


if __name__ == "__main__":
    with app.app_context():
        counts = seed()
        print("Seeded {} exercises, {} workouts, {} workout exercises.".format(*counts))
