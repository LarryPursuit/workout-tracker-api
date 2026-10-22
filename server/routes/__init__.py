from routes.exercises import exercises_bp
from routes.workout_exercises import workout_exercises_bp
from routes.workouts import workouts_bp


def register_blueprints(app):
    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)
    app.register_blueprint(workout_exercises_bp)
