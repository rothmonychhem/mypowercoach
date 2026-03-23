from dataclasses import asdict

from app.domain.models.coaching import ChatReply, DailyFeedback
from app.domain.models.video_analysis import (
    BenchSignalProfile,
    BenchVideoAnalysis,
    DeadliftSignalProfile,
    DeadliftVideoAnalysis,
    SquatSignalProfile,
    SquatVideoAnalysis,
    VideoSubmission,
)
from app.domain.models.program import ProgramOverview
from app.domain.repositories.athlete_repository import AthleteRepository
from app.domain.services.athlete_profiler import AthleteProfiler
from app.domain.services.bench_video_analyzer import BenchVideoAnalyzer
from app.domain.services.coach_chat import CoachChatService
from app.domain.services.deadlift_video_analyzer import DeadliftVideoAnalyzer
from app.domain.services.feedback_composer import FeedbackComposer
from app.domain.services.program_generator import ProgramGenerator
from app.domain.services.squat_video_analyzer import SquatVideoAnalyzer


class CoachingService:
    def __init__(
        self,
        athlete_repository: AthleteRepository,
        feedback_composer: FeedbackComposer,
        coach_chat_service: CoachChatService,
        athlete_profiler: AthleteProfiler,
        program_generator: ProgramGenerator,
        bench_video_analyzer: BenchVideoAnalyzer,
        squat_video_analyzer: SquatVideoAnalyzer,
        deadlift_video_analyzer: DeadliftVideoAnalyzer,
    ) -> None:
        self._athlete_repository = athlete_repository
        self._feedback_composer = feedback_composer
        self._coach_chat_service = coach_chat_service
        self._athlete_profiler = athlete_profiler
        self._program_generator = program_generator
        self._bench_video_analyzer = bench_video_analyzer
        self._squat_video_analyzer = squat_video_analyzer
        self._deadlift_video_analyzer = deadlift_video_analyzer

    def generate_daily_feedback(
        self,
        account_id: str,
        session_quality: str,
        fatigue_level: str,
        notes: str | None,
        exercises: list[dict] | None = None,
        video_name: str | None = None,
    ) -> DailyFeedback:
        self._require_athlete(account_id)
        return self._feedback_composer.compose_daily_feedback(
            session_quality=session_quality,
            fatigue_level=fatigue_level,
            notes=notes,
            exercises=exercises,
            video_name=video_name,
        )

    def chat(self, account_id: str, message: str) -> ChatReply:
        athlete = self._require_athlete(account_id)
        return self._coach_chat_service.reply(athlete=athlete, message=message)

    def get_program(self, account_id: str) -> ProgramOverview:
        athlete = self._require_athlete(account_id)
        athlete_level, focus_points = self._athlete_profiler.profile_summary(athlete)
        return self._program_generator.generate(athlete, athlete_level, focus_points)

    def analyze_bench_video(
        self,
        account_id: str,
        video_name: str,
        camera_angle: str,
        fps: int,
        lift_kg: float,
        reps: int,
        completed_rpe: float,
        grip_width_style: str,
        signals: dict,
        landmark_frames: list[dict] | None = None,
    ) -> BenchVideoAnalysis:
        self._require_athlete(account_id)
        submission = VideoSubmission(
            account_id=account_id,
            lift_type="bench_press",
            video_name=video_name,
            camera_angle=camera_angle,
            fps=fps,
            lift_kg=lift_kg,
            reps=reps,
            completed_rpe=completed_rpe,
            grip_width_style=grip_width_style,
        )
        signal_profile = BenchSignalProfile(**signals)
        return self._bench_video_analyzer.analyze(
            submission=submission,
            signals=signal_profile,
        )

    def analyze_squat_video(
        self,
        account_id: str,
        video_name: str,
        camera_angle: str,
        fps: int,
        lift_kg: float,
        reps: int,
        completed_rpe: float,
        stance_style: str,
        signals: dict,
        landmark_frames: list[dict] | None = None,
    ) -> SquatVideoAnalysis:
        self._require_athlete(account_id)
        submission = VideoSubmission(
            account_id=account_id,
            lift_type="squat",
            video_name=video_name,
            camera_angle=camera_angle,
            fps=fps,
            lift_kg=lift_kg,
            reps=reps,
            completed_rpe=completed_rpe,
            grip_width_style=stance_style,
        )
        signal_profile = SquatSignalProfile(**signals)
        return self._squat_video_analyzer.analyze(
            submission=submission,
            signals=signal_profile,
        )

    def analyze_deadlift_video(
        self,
        account_id: str,
        video_name: str,
        camera_angle: str,
        fps: int,
        lift_kg: float,
        reps: int,
        completed_rpe: float,
        deadlift_style: str,
        signals: dict,
        landmark_frames: list[dict] | None = None,
    ) -> DeadliftVideoAnalysis:
        self._require_athlete(account_id)
        submission = VideoSubmission(
            account_id=account_id,
            lift_type="deadlift",
            video_name=video_name,
            camera_angle=camera_angle,
            fps=fps,
            lift_kg=lift_kg,
            reps=reps,
            completed_rpe=completed_rpe,
            grip_width_style="",
            style_variant=deadlift_style,
        )
        signal_profile = DeadliftSignalProfile(**signals)
        return self._deadlift_video_analyzer.analyze(
            submission=submission,
            signals=signal_profile,
        )

    def _require_athlete(self, account_id: str):
        athlete = self._athlete_repository.get_by_account_id(account_id)
        if athlete is None:
            raise ValueError("No athlete profile exists for that account yet.")
        return athlete

    @staticmethod
    def program_to_dict(program: ProgramOverview) -> dict:
        return asdict(program)

    @staticmethod
    def bench_video_analysis_to_dict(analysis: BenchVideoAnalysis) -> dict:
        return asdict(analysis)

    @staticmethod
    def squat_video_analysis_to_dict(analysis: SquatVideoAnalysis) -> dict:
        return asdict(analysis)

    @staticmethod
    def deadlift_video_analysis_to_dict(analysis: DeadliftVideoAnalysis) -> dict:
        return asdict(analysis)
