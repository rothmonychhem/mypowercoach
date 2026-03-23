from dataclasses import dataclass, field


@dataclass(slots=True)
class ExerciseFeedback:
    exercise_name: str
    planned_sets: int
    planned_reps: int
    planned_weight_kg: float
    completed_sets: int
    completed_reps: int
    completed_weight_kg: float
    note: str


@dataclass(slots=True)
class DailyFeedback:
    status: str
    summary: str
    next_adjustment: str
    cues: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    exercise_feedback: list[ExerciseFeedback] = field(default_factory=list)
    video_feedback: str | None = None


@dataclass(slots=True)
class ChatReply:
    answer: str
    suggested_questions: list[str] = field(default_factory=list)
