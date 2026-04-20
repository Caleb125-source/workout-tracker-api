from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)

    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        viewonly=True,
    )

    # Model Validations
    @validates("name")
    def validate_name(self, _key, name):
        if not name or not name.strip():
            raise ValueError("Exercise name cannot be empty.")
        return name.strip()

    @validates("category")
    def validate_category(self, _key, category):
        valid_categories = [
            "Strength",
            "Cardio",
            "Flexibility",
            "Balance",
            "Endurance",
        ]
        if category not in valid_categories:
            raise ValueError(
                f"Category must be one of: {', '.join(valid_categories)}."
            )
        return category

    def __repr__(self):
        return f"<Exercise {self.id}: {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Table constraint: duration must be positive
    __table_args__ = (
        db.CheckConstraint("duration_minutes > 0", name="ck_positive_duration"),
    )

    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        viewonly=True,
    )

    # Model Validations
    @validates("duration_minutes")
    def validate_duration(self, _key, duration_minutes):
        if duration_minutes is None or duration_minutes <= 0:
            raise ValueError("Duration must be a positive integer.")
        return duration_minutes

    @validates("date")
    def validate_date(self, _key, date):
        if date is None:
            raise ValueError("Workout date is required.")
        return date

    def __repr__(self):
        return f"<Workout {self.id}: {self.date}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer, db.ForeignKey("workouts.id"), nullable=False
    )
    exercise_id = db.Column(
        db.Integer, db.ForeignKey("exercises.id"), nullable=False
    )
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # Table constraints: reps, sets, duration_seconds must be positive when provided
    __table_args__ = (
        db.CheckConstraint(
            "reps IS NULL OR reps > 0", name="ck_positive_reps"
        ),
        db.CheckConstraint(
            "sets IS NULL OR sets > 0", name="ck_positive_sets"
        ),
        db.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_positive_duration_seconds",
        ),
    )

    # Relationships
    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    # Model Validation
    @validates("reps")
    def validate_reps(self, _key, reps):
        if reps is not None and reps <= 0:
            raise ValueError("Reps must be a positive integer.")
        return reps

    @validates("sets")
    def validate_sets(self, _key, sets):
        if sets is not None and sets <= 0:
            raise ValueError("Sets must be a positive integer.")
        return sets

    def __repr__(self):
        return f"<WorkoutExercise {self.id}: W{self.workout_id}-E{self.exercise_id}>"