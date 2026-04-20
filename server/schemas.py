from marshmallow import Schema, fields, validate, validates, ValidationError

# Flat schemas (used inside nested contexts to avoid circularity)
class ExerciseBriefSchema(Schema):
    id               = fields.Int(dump_only=True)
    name             = fields.Str()
    category         = fields.Str()
    equipment_needed = fields.Bool()

class WorkoutBriefSchema(Schema):
    id               = fields.Int(dump_only=True)
    date             = fields.Date()
    duration_minutes = fields.Int()
    notes            = fields.Str()

# WorkoutExercise 
class WorkoutExerciseSchema(Schema):
    id               = fields.Int(dump_only=True)
    workout_id       = fields.Int(required=True)
    exercise_id      = fields.Int(required=True)
    reps             = fields.Int(allow_none=True, load_default=None)
    sets             = fields.Int(allow_none=True, load_default=None)
    duration_seconds = fields.Int(allow_none=True, load_default=None)
    exercise         = fields.Nested(ExerciseBriefSchema, dump_only=True)
    workout          = fields.Nested(WorkoutBriefSchema,  dump_only=True)

    # Schema validations
    @validates("reps")
    def validate_reps(self, v):
        if v is not None and v <= 0:
            raise ValidationError("Reps must be a positive integer.")

    @validates("sets")
    def validate_sets(self, v):
        if v is not None and v <= 0:
            raise ValidationError("Sets must be a positive integer.")

    @validates("duration_seconds")
    def validate_dur_sec(self, v):
        if v is not None and v <= 0:
            raise ValidationError("Duration seconds must be positive.")

# Exercise
class WEForExerciseSchema(Schema):  # WorkoutExercise nested inside Exercise
    id               = fields.Int(dump_only=True)
    workout_id       = fields.Int()
    reps             = fields.Int()
    sets             = fields.Int()
    duration_seconds = fields.Int()
    workout          = fields.Nested(WorkoutBriefSchema, dump_only=True)

class ExerciseSchema(Schema):
    id               = fields.Int(dump_only=True)
    name             = fields.Str(required=True,
        validate=validate.Length(min=1, max=100))
    category         = fields.Str(required=True,
        validate=validate.OneOf(["Strength","Cardio","Flexibility","Balance","Endurance"]))
    equipment_needed = fields.Bool(load_default=False)
    workout_exercises = fields.Nested(WEForExerciseSchema, many=True, dump_only=True)

# Workout 
class WEForWorkoutSchema(Schema):   # WorkoutExercise nested inside Workout
    id               = fields.Int(dump_only=True)
    exercise_id      = fields.Int()
    reps             = fields.Int()
    sets             = fields.Int()
    duration_seconds = fields.Int()
    exercise         = fields.Nested(ExerciseBriefSchema, dump_only=True)

class WorkoutSchema(Schema):
    id               = fields.Int(dump_only=True)
    date             = fields.Date(required=True)
    duration_minutes = fields.Int(required=True,
        validate=validate.Range(min=1, error="Duration must be at least 1 minute."))
    notes            = fields.Str(allow_none=True, load_default=None)
    workout_exercises = fields.Nested(WEForWorkoutSchema, many=True, dump_only=True)

    @validates("notes")
    def validate_notes(self, v):
        if v is not None and len(v) > 500:
            raise ValidationError("Notes must be 500 characters or fewer.")

# Instances for import in app.py 
exercise_schema       = ExerciseSchema()
exercises_schema      = ExerciseSchema(many=True, exclude=("workout_exercises",))
workout_schema        = WorkoutSchema()
workouts_schema       = WorkoutSchema(many=True,  exclude=("workout_exercises",))
workout_exercise_schema = WorkoutExerciseSchema()