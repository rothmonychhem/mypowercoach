from dataclasses import asdict

from app.domain.models.coaching import ChatReply, DailyFeedback
from app.domain.models.program import ProgramOverview
from app.domain.repositories.athlete_repository import AthleteRepository
from app.domain.services.athlete_profiler import AthleteProfiler
from app.domain.services.coach_chat import CoachChatService
from app.domain.services.feedback_composer import FeedbackComposer
from app.domain.services.program_generator import ProgramGenerator


class CoachingService:
    def __init__(
        self,
        athlete_repository: AthleteRepository,
        feedback_composer: FeedbackComposer,
        coach_chat_service: CoachChatService,
        athlete_profiler: AthleteProfiler,
        program_generator: ProgramGenerator,
    ) -> None:
        self._athlete_repository = athlete_repository
        self._feedback_composer = feedback_composer
        self._coach_chat_service = coach_chat_service
        self._athlete_profiler = athlete_profiler
        self._program_generator = program_generator

    def generate_daily_feedback(
        self,
        account_id: str,
        session_quality: str,
        fatigue_level: str,
        notes: str | None,
    ) -> DailyFeedback:
        self._require_athlete(account_id)
        return self._feedback_composer.compose_daily_feedback(
            session_quality=session_quality,
            fatigue_level=fatigue_level,
            notes=notes,
        )

    def chat(self, account_id: str, message: str) -> ChatReply:
        athlete = self._require_athlete(account_id)
        return self._coach_chat_service.reply(athlete=athlete, message=message)

    def get_program(self, account_id: str) -> ProgramOverview:
        athlete = self._require_athlete(account_id)
        athlete_level, focus_points = self._athlete_profiler.profile_summary(athlete)
        return self._program_generator.generate(athlete, athlete_level, focus_points)

    def _require_athlete(self, account_id: str):
        athlete = self._athlete_repository.get_by_account_id(account_id)
        if athlete is None:
            raise ValueError("No athlete profile exists for that account yet.")
        return athlete

    @staticmethod
    def program_to_dict(program: ProgramOverview) -> dict:
        data = asdict(program)
        data["sessions"] = [asdict(session) for session in program.sessions]
        return data
