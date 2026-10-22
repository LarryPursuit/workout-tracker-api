from marshmallow import Schema, fields, validate

from models.workout import MAX_WORKOUT_MINUTES

NOTES_MAX_LENGTH = 500


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True, strict=True, validate=validate.Range(min=1, max=MAX_WORKOUT_MINUTES)
    )
    notes = fields.Str(allow_none=True, validate=validate.Length(max=NOTES_MAX_LENGTH))


class WorkoutDetailSchema(WorkoutSchema):
    """Workout plus each exercise entry with its sets/reps/duration (GET /workouts/<id>)."""

    workout_exercises = fields.List(
        fields.Nested("WorkoutExerciseSchema", exclude=("workout_id",)),
        dump_only=True,
    )
