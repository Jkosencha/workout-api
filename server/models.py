from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()

VALID_CATEGORIES = {"strength", "cardio", "flexibility", "balance", "endurance"}


class Exercise(db.Model):
    __tablename__ = "exercises"

    __table_args__ = (
        UniqueConstraint("name", name="uq_exercise_name"),
        CheckConstraint("length(trim(name)) > 0", name="ck_exercise_name_not_empty"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        viewonly=True,
    )

    @validates("name")
    def validate_name(self, key, value):
        if not value or not value.strip():
            raise ValueError("Exercise name cannot be empty.")
        return value.strip()

    @validates("category")
    def validate_category(self, key, value):
        if not value or value.strip().lower() not in VALID_CATEGORIES:
            allowed = ", ".join(sorted(VALID_CATEGORIES))
            raise ValueError(f"Category must be one of: {allowed}.")
        return value.strip().lower()

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        viewonly=True,
    )

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is None or value <= 0:
            raise ValueError("duration_minutes must be a positive integer.")
        return value

    @validates("date")
    def validate_date(self, key, value):
        if value is not None and value > date.today():
            raise ValueError("Workout date cannot be in the future.")
        return value

    def __repr__(self):
        return f"<Workout {self.id}: {self.date} ({self.duration_minutes} min)>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    __table_args__ = (
        CheckConstraint("reps IS NULL OR reps >= 0", name="ck_we_reps_non_negative"),
        CheckConstraint("sets IS NULL OR sets >= 0", name="ck_we_sets_non_negative"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="ck_we_duration_non_negative",
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

    @validates("reps", "sets", "duration_seconds")
    def validate_non_negative(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative.")
        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout={self.workout_id} "
            f"exercise={self.exercise_id}>"
        )
