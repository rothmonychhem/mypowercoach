from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.coaching import (
    ChatRequest,
    ChatResponse,
    DailyFeedbackRequest,
    DailyFeedbackResponse,
)
from app.api.schemas.video_analysis import (
    BenchVideoAnalysisRequest,
    BenchVideoAnalysisResponse,
    BenchVideoPathAnalysisRequest,
    DeadliftVideoAnalysisRequest,
    DeadliftVideoAnalysisResponse,
    DeadliftVideoPathAnalysisRequest,
    SquatVideoAnalysisRequest,
    SquatVideoAnalysisResponse,
    SquatVideoPathAnalysisRequest,
    VideoPathAnalysisResponse,
)
from app.application.use_cases.coaching import CoachingService
from app.dependencies import get_coaching_service

router = APIRouter()


@router.post("/daily-feedback", response_model=DailyFeedbackResponse)
def create_daily_feedback(
    request: DailyFeedbackRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> DailyFeedbackResponse:
    payload = request.model_dump()
    if payload.get("workout_exercises"):
        payload["exercises"] = payload["workout_exercises"]
    payload.pop("workout_exercises", None)

    try:
        feedback = service.generate_daily_feedback(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return DailyFeedbackResponse(
        status=feedback.status,
        summary=feedback.summary,
        next_adjustment=feedback.next_adjustment,
        cues=feedback.cues,
        improvements=feedback.improvements,
        exercise_feedback=[
            {
                "exercise_name": item.exercise_name,
                "planned_sets": item.planned_sets,
                "planned_reps": item.planned_reps,
                "planned_weight_kg": item.planned_weight_kg,
                "completed_sets": item.completed_sets,
                "completed_reps": item.completed_reps,
                "completed_weight_kg": item.completed_weight_kg,
                "note": item.note,
            }
            for item in feedback.exercise_feedback
        ],
        video_feedback=feedback.video_feedback,
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


@router.post("/bench-video-analysis", response_model=BenchVideoAnalysisResponse)
def analyze_bench_video(
    request: BenchVideoAnalysisRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> BenchVideoAnalysisResponse:
    payload = request.model_dump()

    try:
        analysis = service.analyze_bench_video(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    data = service.bench_video_analysis_to_dict(analysis)
    return BenchVideoAnalysisResponse(**data)


@router.post("/bench-video-from-path", response_model=VideoPathAnalysisResponse)
def analyze_bench_video_from_path(
    request: BenchVideoPathAnalysisRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> VideoPathAnalysisResponse:
    payload = request.model_dump()
    try:
        result = service.analyze_bench_video_path(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return VideoPathAnalysisResponse(**result)


@router.post("/squat-video-analysis", response_model=SquatVideoAnalysisResponse)
def analyze_squat_video(
    request: SquatVideoAnalysisRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> SquatVideoAnalysisResponse:
    payload = request.model_dump()

    try:
        analysis = service.analyze_squat_video(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    data = service.squat_video_analysis_to_dict(analysis)
    return SquatVideoAnalysisResponse(**data)


@router.post("/squat-video-from-path", response_model=VideoPathAnalysisResponse)
def analyze_squat_video_from_path(
    request: SquatVideoPathAnalysisRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> VideoPathAnalysisResponse:
    payload = request.model_dump()
    try:
        result = service.analyze_squat_video_path(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return VideoPathAnalysisResponse(**result)


@router.post("/deadlift-video-analysis", response_model=DeadliftVideoAnalysisResponse)
def analyze_deadlift_video(
    request: DeadliftVideoAnalysisRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> DeadliftVideoAnalysisResponse:
    payload = request.model_dump()

    try:
        analysis = service.analyze_deadlift_video(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    data = service.deadlift_video_analysis_to_dict(analysis)
    return DeadliftVideoAnalysisResponse(**data)


@router.post("/deadlift-video-from-path", response_model=VideoPathAnalysisResponse)
def analyze_deadlift_video_from_path(
    request: DeadliftVideoPathAnalysisRequest,
    service: CoachingService = Depends(get_coaching_service),
) -> VideoPathAnalysisResponse:
    payload = request.model_dump()
    try:
        result = service.analyze_deadlift_video_path(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return VideoPathAnalysisResponse(**result)
