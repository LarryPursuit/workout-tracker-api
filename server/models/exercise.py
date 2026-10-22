from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

from extensions import db

EXERCISE_CATEGORIES = ("strength", "cardio", "flexibility", "balance", "mobility")
NAME_MAX_LENGTH = 100


class Exercise(db.Model):
    """A reusable movement (e.g. "Back Squat") that trainers add to many workouts."""

    __tablename__ = "exercises"
    __table_args__ = (
        db.CheckConstraint("length(trim(name)) > 0", name="name_not_blank"),
        db.CheckConstraint(
            "category IN ({})".format(", ".join(f"'{c}'" for c in EXERCISE_CATEGORIES)),
            name="category_allowed",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(NAME_MAX_LENGTH), nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.id",
    )
    workouts = association_proxy("workout_exercises", "workout")

    @validates("name")
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise name is required.")
        value = value.strip()
        if len(value) > NAME_MAX_LENGTH:
            raise ValueError(f"Exercise name must be at most {NAME_MAX_LENGTH} characters.")
        return value

    @validates("category")
    def validate_category(self, key, value):
        normalized = value.strip().lower() if isinstance(value, str) else value
        if normalized not in EXERCISE_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(EXERCISE_CATEGORIES)}.")
        return normalized

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be true or false.")
        return value

    def __repr__(self):
        return f"<Exercise {self.id} {self.name!r} ({self.category})>"
