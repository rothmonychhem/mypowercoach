from app.domain.models.athlete import AthleteProfile


class AthleteProfiler:
    def profile_summary(self, athlete: AthleteProfile) -> tuple[str, list[str]]:
        level = self._classify_level(athlete.training_age_years)
        recoverability = self._recoverability_label(athlete.training_days_per_week)
        lift_balance = self._lift_balance_focus(athlete)
        split_guidance = self._split_guidance(athlete.training_days_per_week)
        focus_points = [
            f"{level.capitalize()} athlete profile with {recoverability} recoverability.",
            f"Primary goal: {athlete.primary_goal}.",
            split_guidance,
            f"Equipment setup: {athlete.equipment}.",
            lift_balance,
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
        if training_days_per_week == 4:
            return "moderate"
        if training_days_per_week == 5:
            return "carefully managed"
        return "unsupported"

    @staticmethod
    def _split_guidance(training_days_per_week: int) -> str:
        if training_days_per_week == 4:
            return "Training split targets 4 sessions each week with 3 bench touches, 2 squat exposures, and 1 main deadlift day."
        if training_days_per_week == 5:
            return "Training split targets 5 sessions each week with extra bench frequency and a dedicated weak-point support day."
        return "Training split is outside the current product scope and should be normalized to 4 or 5 days."

    @staticmethod
    def _lift_balance_focus(athlete: AthleteProfile) -> str:
        squat = athlete.lift_numbers.squat_kg
        bench = athlete.lift_numbers.bench_kg
        deadlift = athlete.lift_numbers.deadlift_kg

        if squat > 0 and bench / squat < 0.58:
            return "Bench is comparatively underdeveloped, so the block should use extra bench frequency and triceps support."
        if deadlift > 0 and squat / deadlift < 0.78:
            return "Squat is comparatively behind the deadlift, so the block should keep quad and positional squat work in place."
        return "Lift balance is serviceable, so the block can progress from a general strength base rather than a single-lift rescue approach."
