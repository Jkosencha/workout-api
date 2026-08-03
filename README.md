# Workout Tracker API

A Flask + SQLAlchemy + Marshmallow backend for a workout tracking application used by personal trainers. Trainers can create workouts and reusable exercises, then attach exercises to workouts along with the reps, sets, or duration performed.

## Tech Stack

- Python 3.8
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Marshmallow
- SQLite

## Setup

Install dependencies with Pipenv:

```
pipenv install
pipenv shell
```

Move into the server directory, run migrations, and seed the database:

```
cd server
flask db upgrade
python seed.py
```

Start the server:

```
python app.py
```

The API runs at `http://localhost:5555`.

## Data Model

- **Exercise**: a reusable exercise with a name, category (strength, cardio, flexibility, balance, or endurance), and whether equipment is needed.
- **Workout**: a training session with a date, duration in minutes, and optional notes.
- **WorkoutExercise**: a join between a workout and an exercise, recording reps, sets, and/or duration in seconds for that exercise within that workout.

A workout can have many exercises, and an exercise can belong to many workouts, connected through WorkoutExercise records.

## API Routes

### Workouts

| Method | Route | Description |
| --- | --- | --- |
| GET | `/workouts` | List all workouts |
| GET | `/workouts/:id` | Get one workout, including its exercises |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/:id` | Delete a workout and its linked exercise records |

### Exercises

| Method | Route | Description |
| --- | --- | --- |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/:id` | Get one exercise, including the workouts it appears in |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/:id` | Delete an exercise and its linked workout records |

### Workout Exercises

| Method | Route | Description |
| --- | --- | --- |
| POST | `/workouts/:workout_id/exercises/:exercise_id/workout_exercises` | Attach an exercise to a workout with reps, sets, and/or duration |

## Validation

- Exercise names must be unique and non-empty.
- Exercise category must be one of strength, cardio, flexibility, balance, or endurance.
- Workout duration must be a positive number of minutes.
- Workout date cannot be in the future.
- Reps, sets, and duration on a workout exercise cannot be negative.

Validation errors return a 422 status with a message describing the problem.

## Tests

Run the test suite from the `server` directory:

```
pytest
```
