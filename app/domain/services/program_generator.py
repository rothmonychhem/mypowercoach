from app.domain.models.athlete import AthleteProfile
from app.domain.models.program import ProgramOverview, ProgramSession


class ProgramGenerator:
    def generate(self, athlete: AthleteProfile, athlete_level: str, focus_points: list[str]) -> ProgramOverview:
        sessions = self._build_sessions(athlete)
        summary = (
            f"A {athlete_level} block built around {athlete.primary_goal.lower()}, "
            f"with lift exposure matched to {athlete.training_days_per_week} training days."
        )
        return ProgramOverview(
            account_id=athlete.account_id,
            style=f"{athlete_level.capitalize()} adaptive powerlifting block",
            summary=summary,
            focus_points=focus_points
            + [
                "Bench receives the easiest extra exposure when recovery is strong.",
                "Deadlift fatigue is monitored so it does not drain the entire week.",
                "Squat exercise choice should reflect the athlete's current force-production needs.",
            ],
            sessions=sessions,
        )

    @staticmethod
    def _build_sessions(athlete: AthleteProfile) -> list[ProgramSession]:
        base_sessions = [
            ProgramSession(
                day_label="Day 1",
                focus="Squat development",
                prescription="Competition squat, paused squat, and quad-biased accessories.",
            ),
            ProgramSession(
                day_label="Day 2",
                focus="Bench volume",
                prescription="Primary bench work, close-grip bench, and upper-back support.",
            ),
            ProgramSession(
                day_label="Day 3",
                focus="Deadlift control",
                prescription="Heavy pull exposure with capped fatigue and front squat support.",
            ),
        ]
        if athlete.training_days_per_week >= 4:
            base_sessions.append(
                ProgramSession(
                    day_label="Day 4",
                    focus="Bench technique",
                    prescription="Extra bench touchpoint, triceps work, and recovery-friendly upper assistance.",
                )
            )
        if athlete.training_days_per_week >= 5:
            base_sessions.append(
                ProgramSession(
                    day_label="Day 5",
                    focus="GPP and weak-point support",
                    prescription="Low-fatigue accessories, trunk stability, and targeted weak-point volume.",
                )
            )
        return base_sessions
