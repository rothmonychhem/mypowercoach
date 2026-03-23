from pydantic import BaseModel, EmailStr, Field


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    account_id: str
    email: EmailStr
    message: str
