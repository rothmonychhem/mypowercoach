from functools import lru_cache

from app.application.use_cases.account import AccountService
from app.application.use_cases.athlete_onboarding import AthleteOnboardingService
from app.application.use_cases.coaching import CoachingService
from app.core.config import get_settings
from app.domain.services.athlete_profiler import AthleteProfiler
from app.domain.services.coach_chat import CoachChatService
from app.domain.services.feedback_composer import FeedbackComposer
from app.domain.services.program_generator import ProgramGenerator
from app.infrastructure.repositories.in_memory import (
    InMemoryAccountRepository,
    InMemoryAthleteRepository,
)


@lru_cache
def get_account_repository() -> InMemoryAccountRepository:
    return InMemoryAccountRepository()


@lru_cache
def get_athlete_repository() -> InMemoryAthleteRepository:
    return InMemoryAthleteRepository()


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
    )
