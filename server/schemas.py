from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    validates_schema,
    ValidationError,
)

from models import VALID_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(load_default=False)

    @validates("category")
    def validate_category(self, value, **kwargs):
        if value.strip().lower() not in VALID_CATEGORIES:
            allowed = ", ".join(sorted(VALID_CATEGORIES))
            raise ValidationError(f"Category must be one of: {allowed}.")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date() 
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

    @validates("duration_minutes")
    def validate_duration(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("duration_minutes must be a positive integer.")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    @validates("reps")
    def validate_reps(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("reps cannot be negative.")

    @validates("sets")
    def validate_sets(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("sets cannot be negative.")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("duration_seconds cannot be negative.")

    @validates_schema
    def validate_effort_provided(self, data, **kwargs):
        reps = data.get("reps")
        sets = data.get("sets")
        duration = data.get("duration_seconds")
        has_strength = reps is not None and sets is not None
        has_duration = duration is not None
        if not has_strength and not has_duration:
            raise ValidationError(
                "Provide either both reps and sets, or duration_seconds."
            )


class ExerciseSummarySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()


class WorkoutSummarySchema(Schema):
    id = fields.Int()
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Str()


class WorkoutExerciseDetailSchema(Schema):
    id = fields.Int()
    reps = fields.Int()
    sets = fields.Int()
    duration_seconds = fields.Int()
    exercise = fields.Nested(ExerciseSummarySchema)


class WorkoutDetailSchema(Schema):
    """A single workout plus each linked exercise and its reps/sets/duration."""

    id = fields.Int()
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Str()
    workout_exercises = fields.Nested(WorkoutExerciseDetailSchema, many=True)


class ExerciseDetailSchema(Schema):
    """A single exercise plus the workouts it appears in."""

    id = fields.Int()
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()
    workouts = fields.Nested(WorkoutSummarySchema, many=True)
