from dataclasses import dataclass, field


@dataclass(slots=True)
class LiftNumbers:
    squat_kg: float
    bench_kg: float
    deadlift_kg: float


@dataclass(slots=True)
class AthleteProfile:
    account_id: str
    name: str
    height_cm: float
    age: int
    sex: str
    bodyweight_kg: float
    training_age_years: float
    training_days_per_week: int
    primary_goal: str
    equipment: str
    lift_numbers: LiftNumbers
    notes: str = ""
    constraints: list[str] = field(default_factory=list)
