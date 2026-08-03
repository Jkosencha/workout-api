
from datetime import date, timedelta

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    print("Seeding exercises...")
    squat = Exercise(name="Back Squat", category="strength", equipment_needed=True)
    pushup = Exercise(name="Push-Up", category="strength", equipment_needed=False)
    plank = Exercise(name="Plank", category="endurance", equipment_needed=False)
    run = Exercise(name="Treadmill Run", category="cardio", equipment_needed=True)
    stretch = Exercise(
        name="Hamstring Stretch", category="flexibility", equipment_needed=False
    )
    db.session.add_all([squat, pushup, plank, run, stretch])
    db.session.commit()

    print("Seeding workouts...")
    leg_day = Workout(
        date=date.today() - timedelta(days=2),
        duration_minutes=60,
        notes="Heavy lower-body session.",
    )
    conditioning = Workout(
        date=date.today() - timedelta(days=1),
        duration_minutes=45,
        notes="Cardio and core conditioning.",
    )
    mobility = Workout(
        date=date.today(),
        duration_minutes=30,
        notes="Recovery and mobility work.",
    )
    db.session.add_all([leg_day, conditioning, mobility])
    db.session.commit()

    print("Linking exercises to workouts...")
    db.session.add_all(
        [
            WorkoutExercise(workout=leg_day, exercise=squat, reps=8, sets=5),
            WorkoutExercise(workout=leg_day, exercise=pushup, reps=15, sets=3),
            WorkoutExercise(workout=conditioning, exercise=run, duration_seconds=1200),
            WorkoutExercise(workout=conditioning, exercise=plank, duration_seconds=90, sets=3),
            WorkoutExercise(workout=mobility, exercise=stretch, duration_seconds=300),
        ]
    )
    db.session.commit()

    print("Done seeding!")
