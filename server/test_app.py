"""Basic test suite for the Workout Tracker API.

Run from the server/ directory with an in-memory database:
    pytest
"""

import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URI"] = f"sqlite:///{_db_path}"

import pytest

from app import app as flask_app
from models import db, Exercise, Workout


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(Exercise(name="Push-Up", category="strength"))
        db.session.add(Workout(duration_minutes=30))
        db.session.commit()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


def test_list_workouts(client):
    res = client.get("/workouts")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_create_exercise(client):
    res = client.post(
        "/exercises", json={"name": "Deadlift", "category": "strength"}
    )
    assert res.status_code == 201
    assert res.get_json()["name"] == "Deadlift"


def test_schema_rejects_bad_category(client):
    res = client.post("/exercises", json={"name": "X", "category": "dancing"})
    assert res.status_code == 422


def test_missing_required_duration(client):
    res = client.post("/workouts", json={"notes": "no duration"})
    assert res.status_code == 422


def test_workout_exercise_requires_effort(client):
    res = client.post("/workouts/1/exercises/1/workout_exercises", json={})
    assert res.status_code == 422


def test_add_exercise_to_workout(client):
    res = client.post(
        "/workouts/1/exercises/1/workout_exercises",
        json={"reps": 10, "sets": 3},
    )
    assert res.status_code == 201


def test_delete_workout(client):
    assert client.delete("/workouts/1").status_code == 204
    assert client.get("/workouts/1").status_code == 404


def test_404_on_missing_exercise(client):
    assert client.get("/exercises/9999").status_code == 404
