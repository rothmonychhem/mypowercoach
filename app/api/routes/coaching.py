from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.coaching import (
    ChatRequest,
    ChatResponse,
    DailyFeedbackRequest,
    DailyFeedbackResponse,
)
from app.application.use_cases.coaching import CoachingService
from app.dependencies import get_coaching_service

router = APIRouter()


@router.post("/daily-feedback", response_model=DailyFeedbackResponse)
def create_daily_feedback(
    request: DailyFeedbackRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> DailyFeedbackResponse:
    try:
        feedback = service.generate_daily_feedback(**request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return DailyFeedbackResponse(
        status=feedback.status,
        summary=feedback.summary,
        next_adjustment=feedback.next_adjustment,
    )


@router.post("/chat", response_model=ChatResponse)
def coach_chat(
    request: ChatRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> ChatResponse:
    try:
        reply = service.chat(account_id=request.account_id, message=request.message)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return ChatResponse(
        answer=reply.answer,
        suggested_questions=reply.suggested_questions,
    )
