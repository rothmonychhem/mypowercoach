from pydantic import BaseModel, Field


class AthleteOnboardingRequest(BaseModel):
    account_id: str
    name: str = Field(min_length=2, max_length=80)
    age: int = Field(ge=13, le=100)
    bodyweight_kg: float = Field(gt=20, lt=400)
    training_age_years: float = Field(ge=0, le=40)
    training_days_per_week: int = Field(ge=2, le=7)
    primary_goal: str = Field(min_length=4, max_length=140)
    squat_kg: float = Field(gt=20, lt=600)
    bench_kg: float = Field(gt=20, lt=400)
    deadlift_kg: float = Field(gt=20, lt=600)
    constraints: list[str] = Field(default_factory=list)


class AthleteOnboardingResponse(BaseModel):
    athlete: dict
    program: dict
