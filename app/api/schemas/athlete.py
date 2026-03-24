from pydantic import BaseModel, Field


class AthleteProfilePayload(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    height_cm: float = Field(gt=100, lt=260)
    age: int = Field(ge=13, le=100)
    sex: str = Field(min_length=1, max_length=24)
    bodyweight_kg: float = Field(gt=20, lt=400)
    training_age_years: float = Field(ge=0, le=40)
    training_days_per_week: int = Field(ge=4, le=5)
    primary_goal: str = Field(min_length=4, max_length=140)
    equipment: str = Field(min_length=2, max_length=40)
    preferred_block_type: str = Field(default="", max_length=40)
    squat_kg: float = Field(gt=20, lt=600)
    bench_kg: float = Field(gt=20, lt=400)
    deadlift_kg: float = Field(gt=20, lt=600)
    notes: str = Field(default="", max_length=500)
    constraints: list[str] = Field(default_factory=list)


class AthleteOnboardingRequest(AthleteProfilePayload):
    account_id: str


class AthleteOnboardingResponse(BaseModel):
    athlete: dict
    program: dict


class AthleteProfileResponse(BaseModel):
    athlete: dict
