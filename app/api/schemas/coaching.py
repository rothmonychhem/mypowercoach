from pydantic import BaseModel, Field


class DailyFeedbackRequest(BaseModel):
    account_id: str
    session_quality: str = Field(pattern="^(great|solid|rough)$")
    fatigue_level: str = Field(pattern="^(low|moderate|high)$")
    notes: str | None = Field(default=None, max_length=500)


class DailyFeedbackResponse(BaseModel):
    status: str
    summary: str
    next_adjustment: str


class ChatRequest(BaseModel):
    account_id: str
    message: str = Field(min_length=2, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    suggested_questions: list[str]


class ProgramResponse(BaseModel):
    program: dict
