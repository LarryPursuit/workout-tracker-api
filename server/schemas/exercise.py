from marshmallow import Schema, fields, pre_load, validate

from models import EXERCISE_CATEGORIES
from models.exercise import NAME_MAX_LENGTH


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=NAME_MAX_LENGTH))
    category = fields.Str(required=True, validate=validate.OneOf(EXERCISE_CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)

    @pre_load
    def normalize(self, data, **kwargs):
        # Accept " Strength " as "strength" and reject whitespace-only names.
        if not isinstance(data, dict):
            return data
        cleaned = dict(data)
        if isinstance(cleaned.get("name"), str):
            cleaned["name"] = cleaned["name"].strip()
        if isinstance(cleaned.get("category"), str):
            cleaned["category"] = cleaned["category"].strip().lower()
        return cleaned


class ExerciseDetailSchema(ExerciseSchema):
    """Exercise plus every workout it appears in (GET /exercises/<id>)."""

    workouts = fields.List(
        fields.Nested("WorkoutSchema", only=("id", "date", "duration_minutes", "notes")),
        dump_only=True,
    )
