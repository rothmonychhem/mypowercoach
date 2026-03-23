from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.coaching import ProgramResponse
from app.application.use_cases.coaching import CoachingService
from app.dependencies import get_coaching_service

router = APIRouter()


@router.get("/{account_id}/current", response_model=ProgramResponse)
def get_current_program(
    account_id: str,
    service: CoachingService = Depends(get_coaching_service),
) -> ProgramResponse:
    try:
        program = service.get_program(account_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    return ProgramResponse(program=service.program_to_dict(program))
