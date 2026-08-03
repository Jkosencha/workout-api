import os

from flask import Flask, request, make_response
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    ExerciseSchema,
    ExerciseDetailSchema,
    WorkoutSchema,
    WorkoutDetailSchema,
    WorkoutExerciseSchema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", "sqlite:///app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)

# Reusable schema instances
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()
workout_exercise_schema = WorkoutExerciseSchema()


@app.route("/")
def index():
    return {"message": "Workout Tracker API"}, 200


@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return workouts_schema.dump(workouts), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return {"error": "Workout not found"}, 404
    return workout_detail_schema.dump(workout), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    try:
        data = workout_schema.load(request.get_json() or {})
    except ValidationError as err:
        return {"errors": err.messages}, 422

    try:
        workout = Workout(**data)
        db.session.add(workout)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return {"error": str(err.orig) if isinstance(err, IntegrityError) else str(err)}, 422

    return workout_schema.dump(workout), 201


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if workout is None:
        return {"error": "Workout not found"}, 404
    db.session.delete(workout)  # cascade removes linked WorkoutExercises
    db.session.commit()
    return make_response("", 204)


@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return exercises_schema.dump(exercises), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return {"error": "Exercise not found"}, 404
    return exercise_detail_schema.dump(exercise), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json() or {})
    except ValidationError as err:
        return {"errors": err.messages}, 422

    try:
        exercise = Exercise(**data)
        db.session.add(exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return {"error": str(err.orig) if isinstance(err, IntegrityError) else str(err)}, 422

    return exercise_schema.dump(exercise), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if exercise is None:
        return {"error": "Exercise not found"}, 404
    db.session.delete(exercise) 
    db.session.commit()
    return make_response("", 204)


@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if workout is None:
        return {"error": "Workout not found"}, 404
    if exercise is None:
        return {"error": "Exercise not found"}, 404

    try:
        data = workout_exercise_schema.load(request.get_json() or {})
    except ValidationError as err:
        return {"errors": err.messages}, 422

    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            **data,
        )
        db.session.add(workout_exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as err:
        db.session.rollback()
        return {"error": str(err.orig) if isinstance(err, IntegrityError) else str(err)}, 422

    return workout_exercise_schema.dump(workout_exercise), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
