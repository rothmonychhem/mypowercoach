from pydantic import BaseModel, Field


class ExerciseFeedbackEntry(BaseModel):
    exercise_name: str = Field(min_length=2, max_length=120)
    planned_sets: int = Field(ge=1, le=20)
    planned_reps: int = Field(ge=1, le=20)
    planned_weight_kg: float = Field(ge=0, le=1000)
    completed_sets: int = Field(ge=0, le=20)
    completed_reps: int = Field(ge=0, le=30)
    completed_weight_kg: float = Field(ge=0, le=1000)


class WorkoutSetEntry(BaseModel):
    set_number: int = Field(ge=1, le=30)
    planned_reps: int = Field(ge=1, le=30)
    planned_weight_kg: float = Field(ge=0, le=1000)
    completed_reps: int = Field(ge=0, le=30)
    completed_weight_kg: float = Field(ge=0, le=1000)


class WorkoutExerciseEntry(BaseModel):
    exercise_name: str = Field(min_length=2, max_length=120)
    sets: list[WorkoutSetEntry] = Field(min_length=1, max_length=20)


class DailyFeedbackRequest(BaseModel):
    account_id: str
    session_quality: str = Field(pattern="^(great|solid|rough)$")
    fatigue_level: str = Field(pattern="^(low|moderate|high)$")
    notes: str | None = Field(default=None, max_length=500)
    video_name: str | None = Field(default=None, max_length=200)
    exercises: list[ExerciseFeedbackEntry] = Field(default_factory=list)
    workout_exercises: list[WorkoutExerciseEntry] = Field(default_factory=list)


class DailyFeedbackResponse(BaseModel):
    status: str
    summary: str
    next_adjustment: str
    cues: list[str]
    improvements: list[str]
    exercise_feedback: list[dict]
    video_feedback: str | None = None


class ChatRequest(BaseModel):
    account_id: str
    message: str = Field(min_length=2, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    suggested_questions: list[str]


class ProgramResponse(BaseModel):
    program: dict
