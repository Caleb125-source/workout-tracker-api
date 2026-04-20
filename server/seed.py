from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():
    # Always clear first so re-runs don't duplicate
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()
    db.session.commit()

    # Exercises (one per valid category)
    bench  = Exercise(name="Bench Press",     category="Strength",    equipment_needed=True)
    squat  = Exercise(name="Barbell Squat",   category="Strength",    equipment_needed=True)
    run    = Exercise(name="Treadmill Run",   category="Cardio",      equipment_needed=True)
    jacks  = Exercise(name="Jumping Jacks",   category="Cardio",      equipment_needed=False)
    plank  = Exercise(name="Plank",           category="Endurance",   equipment_needed=False)
    yoga   = Exercise(name="Yoga Stretch",    category="Flexibility", equipment_needed=False)
    stand  = Exercise(name="Single Leg Stand",category="Balance",     equipment_needed=False)
    db.session.add_all([bench,squat,run,jacks,plank,yoga,stand])
    db.session.commit()

    # Workouts
    w1 = Workout(date=date(2025,4,14), duration_minutes=60, notes="Upper body day")
    w2 = Workout(date=date(2025,4,15), duration_minutes=45, notes="Cardio session")
    w3 = Workout(date=date(2025,4,16), duration_minutes=90, notes="Full body")
    db.session.add_all([w1, w2, w3])
    db.session.commit()

    # WorkoutExercises (join records with performance data)
    db.session.add_all([
        WorkoutExercise(workout_id=w1.id, exercise_id=bench.id, reps=10, sets=4),
        WorkoutExercise(workout_id=w1.id, exercise_id=plank.id, sets=3,  duration_seconds=60),
        WorkoutExercise(workout_id=w2.id, exercise_id=run.id,             duration_seconds=1200),
        WorkoutExercise(workout_id=w2.id, exercise_id=jacks.id, reps=50, sets=3),
        WorkoutExercise(workout_id=w3.id, exercise_id=squat.id, reps=8,  sets=5),
        WorkoutExercise(workout_id=w3.id, exercise_id=yoga.id,            duration_seconds=600),
    ])
    db.session.commit()

    print(f"Seeded: {Exercise.query.count()} exercises, {Workout.query.count()} workouts")