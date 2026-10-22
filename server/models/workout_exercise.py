from sqlalchemy.orm import validates

from extensions import db
from models.validators import optional_positive_int

MAX_REPS = 1000
MAX_SETS = 100
MAX_DURATION_SECONDS = 4 * 60 * 60


class WorkoutExercise(db.Model):
    """Join model: one exercise as performed in one workout, with its volume."""

    __tablename__ = "workout_exercises"
    # A CHECK on a NULL column passes, so reps/sets/duration stay optional individually.
    __table_args__ = (
        db.UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise_pair"),
        db.CheckConstraint("reps > 0", name="reps_positive"),
        db.CheckConstraint("sets > 0", name="sets_positive"),
        db.CheckConstraint("duration_seconds > 0", name="duration_seconds_positive"),
        db.CheckConstraint(
            "reps IS NOT NULL OR sets IS NOT NULL OR duration_seconds IS NOT NULL",
            name="has_measurement",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps")
    def validate_reps(self, key, value):
        return optional_positive_int(key, value, MAX_REPS)

    @validates("sets")
    def validate_sets(self, key, value):
        return optional_positive_int(key, value, MAX_SETS)

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        return optional_positive_int(key, value, MAX_DURATION_SECONDS)

    def __repr__(self):
        return (
            f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id} "
            f"sets={self.sets} reps={self.reps} seconds={self.duration_seconds}>"
        )
