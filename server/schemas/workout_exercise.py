from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from models.workout_exercise import MAX_DURATION_SECONDS, MAX_REPS, MAX_SETS

MEASUREMENT_FIELDS = ("reps", "sets", "duration_seconds")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    # Both ids come from the URL, so clients can't set them in the body.
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(strict=True, allow_none=True, validate=validate.Range(min=1, max=MAX_REPS))
    sets = fields.Int(strict=True, allow_none=True, validate=validate.Range(min=1, max=MAX_SETS))
    duration_seconds = fields.Int(
        strict=True, allow_none=True, validate=validate.Range(min=1, max=MAX_DURATION_SECONDS)
    )
    exercise = fields.Nested("ExerciseSchema", dump_only=True)

    @validates_schema
    def require_measurement(self, data, **kwargs):
        if all(data.get(field) is None for field in MEASUREMENT_FIELDS):
            raise ValidationError(
                "Provide at least one of reps, sets, or duration_seconds.",
                field_name="_schema",
            )
