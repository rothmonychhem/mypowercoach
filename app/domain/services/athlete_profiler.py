from app.domain.models.athlete import AthleteProfile


class AthleteProfiler:
    def profile_summary(self, athlete: AthleteProfile) -> tuple[str, list[str]]:
        level = self._classify_level(athlete.training_age_years)
        recoverability = self._recoverability_label(athlete.training_days_per_week)
        focus_points = [
            f"{level.capitalize()} athlete profile with {recoverability} recoverability.",
            f"Primary goal: {athlete.primary_goal}.",
            f"Training split targets {athlete.training_days_per_week} sessions each week.",
        ]
        return level, focus_points

    @staticmethod
    def _classify_level(training_age_years: float) -> str:
        if training_age_years < 1.5:
            return "novice"
        if training_age_years < 4:
            return "intermediate"
        return "advanced"

    @staticmethod
    def _recoverability_label(training_days_per_week: int) -> str:
        if training_days_per_week <= 3:
            return "high"
        if training_days_per_week == 4:
            return "moderate"
        return "carefully managed"
