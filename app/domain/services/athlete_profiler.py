from app.domain.models.athlete import AthleteProfile


class AthleteProfiler:
    def profile_summary(self, athlete: AthleteProfile) -> tuple[str, list[str]]:
        level = self._classify_level(athlete.training_age_years)
        recoverability = self._recoverability_label(athlete.training_days_per_week)
        lift_balance = self._lift_balance_focus(athlete)
        split_guidance = self._split_guidance(athlete.training_days_per_week)
        constraint_guidance = self._constraint_guidance(athlete)
        focus_points = [
            f"{level.capitalize()} athlete profile with {recoverability} recoverability.",
            f"Primary goal: {athlete.primary_goal}.",
            self._block_type_guidance(athlete),
            split_guidance,
            f"Equipment setup: {athlete.equipment}.",
            lift_balance,
            constraint_guidance,
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

    @staticmethod
    def _constraint_guidance(athlete: AthleteProfile) -> str:
        notes = " ".join([athlete.notes, *athlete.constraints]).lower()
        if any(term in notes for term in ("low-back pain", "lower back pain", "back pain", "back fatigue", "low-back fatigue", "lower back")):
            return "Low-back sensitivity is present, so the block should build posterior-chain capacity with a lower spinal cost instead of solving the problem by piling on more hinge fatigue."
        if "leg drive" in notes:
            return "Leg-drive timing is a noted issue, so the block should keep technical exposures that let force transfer improve without forcing max-load work."
        if any(term in notes for term in ("knee cave", "knee collapse", "knee pain", "knee track")):
            return "Knee stability is a noted issue, so the block should keep unilateral and controlled accessory work that cleans up tracking without chasing fatigue."
        return "No dominant pain or movement constraint is overriding the current block design."

    @staticmethod
    def _block_type_guidance(athlete: AthleteProfile) -> str:
        if athlete.preferred_block_type:
            normalized = athlete.preferred_block_type.replace("_", " ").strip().lower()
            return f"Preferred block type: {normalized}."
        return "Block type should be inferred from the athlete goal and current readiness rather than forced blindly."
