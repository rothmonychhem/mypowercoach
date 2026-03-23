from dataclasses import dataclass, field


@dataclass(slots=True)
class DailyFeedback:
    status: str
    summary: str
    next_adjustment: str


@dataclass(slots=True)
class ChatReply:
    answer: str
    suggested_questions: list[str] = field(default_factory=list)
