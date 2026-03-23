from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.auth import AuthRequest, AuthResponse
from app.application.use_cases.account import AccountService
from app.dependencies import get_account_service

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: AuthRequest,
    service: AccountService = Depends(get_account_service),
) -> AuthResponse:
    try:
        account = service.register(email=request.email, password=request.password)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    return AuthResponse(
        account_id=account.account_id,
        email=account.email,
        message="Account created successfully.",
    )


@router.post("/sign-in", response_model=AuthResponse)
def sign_in(
    request: AuthRequest,
    service: AccountService = Depends(get_account_service),
) -> AuthResponse:
    try:
        account = service.sign_in(email=request.email, password=request.password)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error

    return AuthResponse(
        account_id=account.account_id,
        email=account.email,
        message="Signed in successfully.",
    )
