from datetime import date

import pytest
from marshmallow import ValidationError

from schemas import ExerciseSchema, WorkoutExerciseSchema, WorkoutSchema


class TestExerciseSchema:
    def test_loads_and_normalizes(self):
        data = ExerciseSchema().load({"name": " Row ", "category": "CARDIO"})
        assert data == {"name": "Row", "category": "cardio", "equipment_needed": False}

    def test_requires_name_and_category(self):
        with pytest.raises(ValidationError) as error:
            ExerciseSchema().load({})
        assert set(error.value.messages) == {"name", "category"}

    def test_rejects_unknown_category(self):
        with pytest.raises(ValidationError) as error:
            ExerciseSchema().load({"name": "Row", "category": "dance"})
        assert "category" in error.value.messages

    def test_rejects_unknown_fields(self):
        with pytest.raises(ValidationError) as error:
            ExerciseSchema().load({"name": "Row", "category": "cardio", "id": 4})
        assert "id" in error.value.messages


class TestWorkoutSchema:
    def test_parses_iso_date(self):
        data = WorkoutSchema().load({"date": "2026-10-01", "duration_minutes": 40})
        assert data["date"] == date(2026, 10, 1)

    @pytest.mark.parametrize("minutes", [0, 601, "40", 12.5])
    def test_rejects_out_of_range_or_non_integer_duration(self, minutes):
        with pytest.raises(ValidationError) as error:
            WorkoutSchema().load({"date": "2026-10-01", "duration_minutes": minutes})
        assert "duration_minutes" in error.value.messages

    def test_rejects_bad_date(self):
        with pytest.raises(ValidationError) as error:
            WorkoutSchema().load({"date": "October 1st", "duration_minutes": 40})
        assert "date" in error.value.messages

    def test_rejects_long_notes(self):
        with pytest.raises(ValidationError):
            WorkoutSchema().load(
                {"date": "2026-10-01", "duration_minutes": 40, "notes": "x" * 501}
            )


class TestWorkoutExerciseSchema:
    def test_requires_at_least_one_measurement(self):
        with pytest.raises(ValidationError) as error:
            WorkoutExerciseSchema().load({})
        assert "_schema" in error.value.messages

    def test_accepts_duration_only(self):
        assert WorkoutExerciseSchema().load({"duration_seconds": 60}) == {"duration_seconds": 60}

    def test_rejects_zero_sets(self):
        with pytest.raises(ValidationError) as error:
            WorkoutExerciseSchema().load({"sets": 0, "reps": 5})
        assert "sets" in error.value.messages

    def test_ids_cannot_be_set_from_body(self):
        with pytest.raises(ValidationError) as error:
            WorkoutExerciseSchema().load({"reps": 5, "workout_id": 2})
        assert "workout_id" in error.value.messages
