from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.athlete import AthleteOnboardingRequest, AthleteOnboardingResponse
from app.application.use_cases.athlete_onboarding import AthleteOnboardingService
from app.dependencies import get_athlete_onboarding_service

router = APIRouter()


@router.post("/onboard", response_model=AthleteOnboardingResponse, status_code=status.HTTP_201_CREATED)
def onboard_athlete(
    request: AthleteOnboardingRequest,
    service: AthleteOnboardingService = Depends(get_athlete_onboarding_service),
) -> AthleteOnboardingResponse:
    try:
        athlete, program = service.onboard(**request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return AthleteOnboardingResponse(
        athlete=service.athlete_to_dict(athlete),
        program=AthleteOnboardingService.athlete_to_dict(athlete) | {"program_preview": program.summary},
    )
