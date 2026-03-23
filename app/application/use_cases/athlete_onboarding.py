from dataclasses import asdict

from app.domain.models.athlete import AthleteProfile, LiftNumbers
from app.domain.models.program import ProgramOverview
from app.domain.repositories.account_repository import AccountRepository
from app.domain.repositories.athlete_repository import AthleteRepository
from app.domain.services.athlete_profiler import AthleteProfiler
from app.domain.services.program_generator import ProgramGenerator


class AthleteOnboardingService:
    def __init__(
        self,
        account_repository: AccountRepository,
        athlete_repository: AthleteRepository,
        athlete_profiler: AthleteProfiler,
        program_generator: ProgramGenerator,
    ) -> None:
        self._account_repository = account_repository
        self._athlete_repository = athlete_repository
        self._athlete_profiler = athlete_profiler
        self._program_generator = program_generator

    def onboard(
        self,
        account_id: str,
        name: str,
        height_cm: float,
        age: int,
        sex: str,
        bodyweight_kg: float,
        training_age_years: float,
        training_days_per_week: int,
        primary_goal: str,
        equipment: str,
        squat_kg: float,
        bench_kg: float,
        deadlift_kg: float,
        notes: str = "",
        constraints: list[str] | None = None,
    ) -> tuple[AthleteProfile, ProgramOverview]:
        account = self._account_repository.get_by_id(account_id)
        if account is None:
            raise ValueError("The account does not exist.")

        athlete = AthleteProfile(
            account_id=account_id,
            name=name.strip(),
            height_cm=height_cm,
            age=age,
            sex=sex.strip(),
            bodyweight_kg=bodyweight_kg,
            training_age_years=training_age_years,
            training_days_per_week=training_days_per_week,
            primary_goal=primary_goal.strip(),
            equipment=equipment.strip(),
            lift_numbers=LiftNumbers(
                squat_kg=squat_kg,
                bench_kg=bench_kg,
                deadlift_kg=deadlift_kg,
            ),
            notes=notes.strip(),
            constraints=constraints or [],
        )
        self._athlete_repository.save(athlete)
        athlete_level, focus_points = self._athlete_profiler.profile_summary(athlete)
        program = self._program_generator.generate(athlete, athlete_level, focus_points)
        return athlete, program

    def get_profile(self, account_id: str) -> AthleteProfile:
        athlete = self._athlete_repository.get_by_account_id(account_id)
        if athlete is None:
            raise ValueError("No athlete profile exists for that account yet.")
        return athlete

    @staticmethod
    def athlete_to_dict(athlete: AthleteProfile) -> dict:
        data = asdict(athlete)
        data["lift_numbers"] = asdict(athlete.lift_numbers)
        return data

    @staticmethod
    def program_to_dict(program: ProgramOverview) -> dict:
        data = asdict(program)
        data["sessions"] = [asdict(session) for session in program.sessions]
        return data
