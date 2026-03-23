from functools import lru_cache

from app.application.use_cases.account import AccountService
from app.application.use_cases.athlete_onboarding import AthleteOnboardingService
from app.application.use_cases.coaching import CoachingService
from app.core.config import get_settings
from app.domain.services.athlete_profiler import AthleteProfiler
from app.domain.services.bench_video_analyzer import BenchVideoAnalyzer
from app.domain.services.coach_chat import CoachChatService
from app.domain.services.deadlift_video_analyzer import DeadliftVideoAnalyzer
from app.domain.services.feedback_composer import FeedbackComposer
from app.domain.services.program_generator import ProgramGenerator
from app.domain.services.squat_video_analyzer import SquatVideoAnalyzer
from app.infrastructure.db.sqlite import SQLiteDatabase
from app.infrastructure.repositories.sqlite import SQLiteAccountRepository, SQLiteAthleteRepository


@lru_cache
def get_database() -> SQLiteDatabase:
    return SQLiteDatabase(database_path=get_settings().database_path)


@lru_cache
def get_account_repository() -> SQLiteAccountRepository:
    return SQLiteAccountRepository(database=get_database())


@lru_cache
def get_athlete_repository() -> SQLiteAthleteRepository:
    return SQLiteAthleteRepository(database=get_database())


@lru_cache
def get_account_service() -> AccountService:
    return AccountService(
        account_repository=get_account_repository(),
        password_salt=get_settings().password_salt,
    )


@lru_cache
def get_athlete_onboarding_service() -> AthleteOnboardingService:
    return AthleteOnboardingService(
        account_repository=get_account_repository(),
        athlete_repository=get_athlete_repository(),
        athlete_profiler=AthleteProfiler(),
        program_generator=ProgramGenerator(),
    )


@lru_cache
def get_coaching_service() -> CoachingService:
    return CoachingService(
        athlete_repository=get_athlete_repository(),
        feedback_composer=FeedbackComposer(),
        coach_chat_service=CoachChatService(),
        athlete_profiler=AthleteProfiler(),
        program_generator=ProgramGenerator(),
        bench_video_analyzer=BenchVideoAnalyzer(),
        squat_video_analyzer=SquatVideoAnalyzer(),
        deadlift_video_analyzer=DeadliftVideoAnalyzer(),
    )
