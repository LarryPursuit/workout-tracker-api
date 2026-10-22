# Workout Tracker API

A Flask REST API that personal trainers use to track workouts and the exercises in them.
Exercises are reusable: one "Back Squat" can be added to many workouts, and each time it
is added the trainer records the sets, reps, and/or duration for that workout.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow on SQLite.

## Data model

```
Workout 1 ──< WorkoutExercise >── 1 Exercise
```

| Model | Fields |
|-------|--------|
| `Exercise` | `id`, `name` (unique), `category`, `equipment_needed` |
| `Workout` | `id`, `date`, `duration_minutes`, `notes` |
| `WorkoutExercise` | `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds` |

`Workout.exercises` and `Exercise.workouts` are association proxies through
`WorkoutExercise`. Deleting a workout or an exercise also deletes its `WorkoutExercise` rows.

Valid categories: `strength`, `cardio`, `flexibility`, `balance`, `mobility`.

## Installation

Requires Python 3.8.13 or newer and [Pipenv](https://pipenv.pypa.io/).

> The pinned Werkzeug 2.2.2 does not run on Python 3.14 or newer. Use Python 3.8–3.13.

```bash
pipenv install --dev
pipenv shell
cd server
flask db upgrade      # create server/instance/app.db from the migrations
python seed.py        # load sample exercises, workouts, and workout exercises
```

`seed.py` clears existing rows first, so it can be re-run any time to reset the data.

## Running

From the `server/` directory:

```bash
flask run --port 5555
```

or `python app.py`. The API is served at http://localhost:5555.

## Running the tests

From the project root:

```bash
pytest
```

Tests use an in-memory SQLite database and never touch `app.db`.

## Endpoints

All request and response bodies are JSON. Errors come back as `{"errors": ...}`.

### Workouts

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/workouts` | List all workouts, newest first. |
| `GET` | `/workouts/<id>` | One workout with its exercises and each entry's sets/reps/duration. `404` if missing. |
| `POST` | `/workouts` | Create a workout. Body: `date` (`YYYY-MM-DD`, required), `duration_minutes` (1–600, required), `notes` (optional, ≤500 chars). Returns `201`. |
| `DELETE` | `/workouts/<id>` | Delete a workout and its exercise entries. Returns `204`. |

### Exercises

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/exercises` | List all exercises alphabetically. |
| `GET` | `/exercises/<id>` | One exercise with the workouts it appears in. `404` if missing. |
| `POST` | `/exercises` | Create an exercise. Body: `name` (required, unique, ≤100 chars), `category` (required), `equipment_needed` (bool, default `false`). Returns `201`, or `409` if the name exists. |
| `DELETE` | `/exercises/<id>` | Delete an exercise and remove it from every workout. Returns `204`. |

### Adding an exercise to a workout

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add the exercise to the workout. Body: any of `reps` (1–1000), `sets` (1–100), `duration_seconds` (1–14400); at least one is required. Returns `201`, `404` if either id is missing, or `409` if the exercise is already in that workout. |

Example:

```bash
curl -X POST http://localhost:5555/workouts/1/exercises/4/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"sets": 3, "duration_seconds": 45}'
```

## Validations

Each rule is enforced at the layer best suited to it, so bad data is stopped as early as possible.

**Table constraints** (`server/models/*.py`, `__table_args__`)
- `NOT NULL` on required columns and foreign keys
- `UNIQUE` exercise name, and `UNIQUE (workout_id, exercise_id)` so an exercise appears once per workout
- `CHECK` exercise name not blank and category in the allowed list
- `CHECK` `duration_minutes`, `reps`, `sets`, `duration_seconds` are positive
- `CHECK` every workout exercise has at least one of reps, sets, or duration
- Foreign keys enforced in SQLite via `PRAGMA foreign_keys=ON` (`server/extensions.py`)

**Model validations** (`@validates`)
- Exercise name required, trimmed, ≤100 chars
- Exercise category normalized to lowercase and checked against the allowed list
- `equipment_needed` must be a boolean
- Workout `date` must be a date; `duration_minutes` a whole number from 1 to 600
- `reps`, `sets`, `duration_seconds` whole numbers within their limits when given

**Schema validations** (Marshmallow, `server/schemas/`)
- Required fields, `Length`, `OneOf`, and `Range` validators
- Strict integers (`"40"` or `12.5` are rejected)
- ISO date parsing for workout `date`
- `@validates_schema` requiring at least one measurement on a workout exercise
- `@pre_load` trims names and lowercases categories
- Unknown fields (including ids) are rejected

## Project structure

```
server/
├── app.py              # create_app() factory and app instance
├── config.py           # Config and TestConfig
├── extensions.py       # db, migrate, naming convention, SQLite FK pragma
├── errors.py           # JSON error handlers
├── seed.py             # sample data
├── models/             # Exercise, Workout, WorkoutExercise (+ shared validators)
├── schemas/            # Marshmallow schemas
├── routes/             # one blueprint per resource
└── migrations/         # Alembic migrations
tests/                  # model, schema, and route tests
```
# workout-tracker-api
