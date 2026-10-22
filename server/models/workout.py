import datetime

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

from extensions import db
from models.validators import require_positive_int

MAX_WORKOUT_MINUTES = 600


class Workout(db.Model):
    """A single training session on a given date."""

    __tablename__ = "workouts"
    __table_args__ = (
        db.CheckConstraint("duration_minutes > 0", name="duration_minutes_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # delete-orphan: deleting a workout also deletes its exercise entries.
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.id",
    )
    exercises = association_proxy("workout_exercises", "exercise")

    @validates("date")
    def validate_date(self, key, value):
        if not isinstance(value, datetime.date):
            raise ValueError("Workout date must be a valid date.")
        return value

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        return require_positive_int("duration_minutes", value, MAX_WORKOUT_MINUTES)

    def __repr__(self):
        return f"<Workout {self.id} {self.date} {self.duration_minutes}min>"
