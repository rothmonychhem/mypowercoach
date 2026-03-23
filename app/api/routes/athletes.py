from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.athlete import (
    AthleteOnboardingRequest,
    AthleteOnboardingResponse,
    AthleteProfilePayload,
    AthleteProfileResponse,
)
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
        program=service.program_to_dict(program),
    )


@router.get("/{account_id}", response_model=AthleteProfileResponse)
def get_athlete_profile(
    account_id: str,
    service: AthleteOnboardingService = Depends(get_athlete_onboarding_service),
) -> AthleteProfileResponse:
    try:
        athlete = service.get_profile(account_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return AthleteProfileResponse(athlete=service.athlete_to_dict(athlete))


@router.put("/{account_id}", response_model=AthleteOnboardingResponse)
def update_athlete_profile(
    account_id: str,
    request: AthleteProfilePayload,
    service: AthleteOnboardingService = Depends(get_athlete_onboarding_service),
) -> AthleteOnboardingResponse:
    payload = request.model_dump()
    payload["account_id"] = account_id

    try:
        athlete, program = service.onboard(**payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return AthleteOnboardingResponse(
        athlete=service.athlete_to_dict(athlete),
        program=service.program_to_dict(program),
    )
