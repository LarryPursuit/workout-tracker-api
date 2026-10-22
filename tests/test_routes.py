from extensions import db
from models import Exercise, Workout, WorkoutExercise

ADD_PATH = "/workouts/{}/exercises/{}/workout_exercises"


class TestWorkoutRoutes:
    def test_list_workouts(self, client, seeded):
        response = client.get("/workouts")
        assert response.status_code == 200
        body = response.get_json()
        assert len(body) == 3
        assert set(body[0]) == {"id", "date", "duration_minutes", "notes"}

    def test_get_workout_includes_exercises_with_volume(self, client, seeded):
        body = client.get("/workouts/1").get_json()
        entry = body["workout_exercises"][1]
        assert entry["sets"] == 5 and entry["reps"] == 5
        assert entry["exercise"]["name"] == "Back Squat"
        assert "workout_id" not in entry

    def test_get_missing_workout_returns_json_404(self, client):
        response = client.get("/workouts/999")
        assert response.status_code == 404
        assert response.get_json() == {"errors": ["Workout not found."]}

    def test_create_workout(self, client):
        response = client.post(
            "/workouts", json={"date": "2026-10-20", "duration_minutes": 50, "notes": "Push day"}
        )
        assert response.status_code == 201
        assert response.get_json()["workout_exercises"] == []
        assert Workout.query.count() == 1

    def test_create_workout_with_invalid_body(self, client):
        response = client.post("/workouts", json={"duration_minutes": -1})
        assert response.status_code == 400
        assert set(response.get_json()["errors"]) == {"date", "duration_minutes"}

    def test_create_workout_requires_json_object(self, client):
        response = client.post("/workouts", data="not json")
        assert response.status_code == 400

    def test_delete_workout_removes_its_entries(self, client, seeded):
        response = client.delete("/workouts/1")
        assert response.status_code == 204
        assert db.session.get(Workout, 1) is None
        assert WorkoutExercise.query.filter_by(workout_id=1).count() == 0
        assert Exercise.query.count() == 8

    def test_delete_missing_workout(self, client):
        assert client.delete("/workouts/999").status_code == 404


class TestExerciseRoutes:
    def test_list_exercises(self, client, seeded):
        body = client.get("/exercises").get_json()
        assert len(body) == 8
        assert "workouts" not in body[0]

    def test_get_exercise_includes_workouts(self, client, seeded):
        squat = Exercise.query.filter_by(name="Back Squat").one()
        body = client.get(f"/exercises/{squat.id}").get_json()
        assert sorted(w["id"] for w in body["workouts"]) == [1, 3]

    def test_create_exercise(self, client):
        response = client.post(
            "/exercises", json={"name": "Burpee", "category": "Cardio", "equipment_needed": False}
        )
        assert response.status_code == 201
        assert response.get_json()["category"] == "cardio"

    def test_create_duplicate_exercise_conflicts(self, client, seeded):
        response = client.post("/exercises", json={"name": "Plank", "category": "balance"})
        assert response.status_code == 409

    def test_create_exercise_with_invalid_body(self, client):
        response = client.post("/exercises", json={"name": "", "category": "nope"})
        assert response.status_code == 400

    def test_delete_exercise_removes_its_entries(self, client, seeded):
        squat = Exercise.query.filter_by(name="Back Squat").one()
        assert client.delete(f"/exercises/{squat.id}").status_code == 204
        assert WorkoutExercise.query.filter_by(exercise_id=squat.id).count() == 0
        assert Workout.query.count() == 3

    def test_get_missing_exercise(self, client):
        assert client.get("/exercises/999").status_code == 404


class TestAddExerciseToWorkout:
    def test_adds_exercise_with_volume(self, client, seeded):
        plank = Exercise.query.filter_by(name="Plank").one()
        response = client.post(ADD_PATH.format(1, plank.id), json={"sets": 3, "duration_seconds": 45})
        assert response.status_code == 201
        body = response.get_json()
        assert body["workout_id"] == 1 and body["exercise"]["name"] == "Plank"
        assert plank in db.session.get(Workout, 1).exercises

    def test_requires_a_measurement(self, client, seeded):
        response = client.post(ADD_PATH.format(1, 4), json={})
        assert response.status_code == 400

    def test_duplicate_pair_conflicts(self, client, seeded):
        squat = Exercise.query.filter_by(name="Back Squat").one()
        response = client.post(ADD_PATH.format(1, squat.id), json={"sets": 1, "reps": 1})
        assert response.status_code == 409

    def test_missing_workout_or_exercise(self, client, seeded):
        assert client.post(ADD_PATH.format(999, 1), json={"reps": 5}).status_code == 404
        assert client.post(ADD_PATH.format(1, 999), json={"reps": 5}).status_code == 404

    def test_unsupported_method_returns_json(self, client):
        response = client.put("/workouts/1", json={})
        assert response.status_code == 405
        assert "errors" in response.get_json()
