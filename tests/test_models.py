from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Exercise, Workout, WorkoutExercise


def make_exercise(**overrides):
    data = {"name": "Lunge", "category": "strength", "equipment_needed": False}
    return Exercise(**{**data, **overrides})


def make_workout(**overrides):
    data = {"date": date(2026, 10, 1), "duration_minutes": 45}
    return Workout(**{**data, **overrides})


class TestModelValidations:
    def test_exercise_name_is_stripped_and_category_lowercased(self, app):
        exercise = make_exercise(name="  Lunge ", category=" Strength")
        assert exercise.name == "Lunge"
        assert exercise.category == "strength"

    @pytest.mark.parametrize("name", ["", "   ", None, "x" * 101])
    def test_exercise_rejects_bad_name(self, app, name):
        with pytest.raises(ValueError):
            make_exercise(name=name)

    def test_exercise_rejects_unknown_category(self, app):
        with pytest.raises(ValueError, match="Category must be one of"):
            make_exercise(category="yoga-ish")

    def test_exercise_rejects_non_bool_equipment(self, app):
        with pytest.raises(ValueError):
            make_exercise(equipment_needed="yes")

    @pytest.mark.parametrize("minutes", [0, -5, 601, 12.5, True, "30"])
    def test_workout_rejects_bad_duration(self, app, minutes):
        with pytest.raises(ValueError):
            make_workout(duration_minutes=minutes)

    def test_workout_rejects_non_date(self, app):
        with pytest.raises(ValueError, match="valid date"):
            make_workout(date="2026-10-01")

    @pytest.mark.parametrize("field", ["reps", "sets", "duration_seconds"])
    def test_workout_exercise_rejects_non_positive_values(self, app, field):
        with pytest.raises(ValueError, match="greater than 0"):
            WorkoutExercise(**{field: 0})

    def test_workout_exercise_allows_missing_individual_values(self, app):
        entry = WorkoutExercise(sets=3, reps=None)
        assert entry.reps is None


class TestRelationships:
    def test_workout_and_exercise_link_through_join_model(self, app):
        workout, exercise = make_workout(), make_exercise()
        db.session.add(WorkoutExercise(workout=workout, exercise=exercise, sets=3, reps=8))
        db.session.commit()

        assert workout.exercises == [exercise]
        assert exercise.workouts == [workout]

    def test_deleting_workout_deletes_its_entries_but_keeps_exercise(self, app):
        workout, exercise = make_workout(), make_exercise()
        db.session.add(WorkoutExercise(workout=workout, exercise=exercise, reps=10))
        db.session.commit()

        db.session.delete(workout)
        db.session.commit()

        assert WorkoutExercise.query.count() == 0
        assert db.session.get(Exercise, exercise.id) is not None


class TestTableConstraints:
    """Raw SQL bypasses @validates so these exercise the database itself."""

    def insert(self, sql, **params):
        db.session.execute(text(sql), params)
        db.session.commit()

    def test_exercise_name_must_be_unique(self, app):
        db.session.add(make_exercise())
        db.session.commit()
        with pytest.raises(IntegrityError):
            db.session.add(make_exercise())
            db.session.commit()

    def test_exercise_category_check(self, app):
        with pytest.raises(IntegrityError):
            self.insert(
                "INSERT INTO exercises (name, category, equipment_needed) VALUES ('A', 'bad', 0)"
            )

    def test_workout_duration_check(self, app):
        with pytest.raises(IntegrityError):
            self.insert(
                "INSERT INTO workouts (date, duration_minutes) VALUES ('2026-10-01', 0)"
            )

    def test_workout_exercise_requires_a_measurement(self, app, seeded):
        with pytest.raises(IntegrityError):
            self.insert(
                "INSERT INTO workout_exercises (workout_id, exercise_id) VALUES (1, 8)"
            )

    def test_workout_exercise_foreign_keys_enforced(self, app):
        with pytest.raises(IntegrityError):
            self.insert(
                "INSERT INTO workout_exercises (workout_id, exercise_id, reps) VALUES (99, 99, 5)"
            )

    def test_exercise_added_to_workout_only_once(self, app):
        workout, exercise = make_workout(), make_exercise()
        db.session.add(WorkoutExercise(workout=workout, exercise=exercise, reps=5))
        db.session.commit()
        with pytest.raises(IntegrityError):
            db.session.add(WorkoutExercise(workout=workout, exercise=exercise, reps=8))
            db.session.commit()
