from dataclasses import dataclass

from app.domain.models.athlete import AthleteProfile
from app.domain.models.program import (
    ProgramDay,
    ProgramExercisePrescription,
    ProgramOverview,
    ProgramWeek,
)


@dataclass(frozen=True, slots=True)
class ProgressionStep:
    sets: int
    reps: int
    rpe: float


PROGRESSION_LIBRARY: dict[str, tuple[ProgressionStep, ProgressionStep, ProgressionStep, ProgressionStep]] = {
    "squat_primary": (
        ProgressionStep(4, 5, 6.5),
        ProgressionStep(5, 4, 7.0),
        ProgressionStep(5, 3, 8.0),
        ProgressionStep(3, 4, 6.0),
    ),
    "squat_secondary": (
        ProgressionStep(3, 5, 6.0),
        ProgressionStep(3, 4, 6.5),
        ProgressionStep(4, 3, 7.0),
        ProgressionStep(2, 4, 6.0),
    ),
    "bench_volume": (
        ProgressionStep(5, 5, 6.5),
        ProgressionStep(5, 4, 7.0),
        ProgressionStep(6, 3, 8.0),
        ProgressionStep(4, 4, 6.0),
    ),
    "bench_intensity": (
        ProgressionStep(4, 4, 7.0),
        ProgressionStep(5, 3, 7.5),
        ProgressionStep(5, 2, 8.5),
        ProgressionStep(3, 3, 6.0),
    ),
    "bench_technique": (
        ProgressionStep(4, 6, 6.0),
        ProgressionStep(4, 5, 6.5),
        ProgressionStep(5, 4, 7.0),
        ProgressionStep(3, 5, 6.0),
    ),
    "deadlift_primary": (
        ProgressionStep(4, 4, 6.5),
        ProgressionStep(4, 3, 7.0),
        ProgressionStep(5, 2, 8.0),
        ProgressionStep(3, 3, 6.0),
    ),
    "deadlift_secondary": (
        ProgressionStep(3, 5, 6.0),
        ProgressionStep(3, 4, 6.5),
        ProgressionStep(4, 3, 7.0),
        ProgressionStep(2, 3, 6.0),
    ),
    "press_assistance": (
        ProgressionStep(3, 8, 7.0),
        ProgressionStep(3, 6, 7.5),
        ProgressionStep(4, 5, 8.0),
        ProgressionStep(2, 8, 6.5),
    ),
    "row_support": (
        ProgressionStep(4, 10, 7.0),
        ProgressionStep(4, 8, 7.5),
        ProgressionStep(4, 8, 8.0),
        ProgressionStep(3, 10, 6.5),
    ),
    "single_leg": (
        ProgressionStep(3, 10, 7.0),
        ProgressionStep(3, 8, 7.5),
        ProgressionStep(3, 8, 8.0),
        ProgressionStep(2, 10, 6.5),
    ),
    "posterior_chain": (
        ProgressionStep(3, 8, 7.0),
        ProgressionStep(3, 6, 7.5),
        ProgressionStep(3, 6, 8.0),
        ProgressionStep(2, 8, 6.5),
    ),
    "triceps_upper_back": (
        ProgressionStep(3, 12, 7.0),
        ProgressionStep(3, 10, 7.5),
        ProgressionStep(4, 10, 8.0),
        ProgressionStep(2, 12, 6.5),
    ),
    "trunk_gpp": (
        ProgressionStep(3, 12, 6.5),
        ProgressionStep(3, 10, 7.0),
        ProgressionStep(3, 10, 7.5),
        ProgressionStep(2, 12, 6.0),
    ),
    "bench_hypertrophy": (
        ProgressionStep(3, 10, 6.5),
        ProgressionStep(3, 9, 7.0),
        ProgressionStep(4, 8, 7.5),
        ProgressionStep(2, 8, 6.0),
    ),
    "squat_hypertrophy": (
        ProgressionStep(3, 10, 6.5),
        ProgressionStep(3, 8, 7.0),
        ProgressionStep(4, 8, 7.5),
        ProgressionStep(2, 8, 6.0),
    ),
    "arm_isolation": (
        ProgressionStep(2, 12, 7.0),
        ProgressionStep(2, 10, 7.5),
        ProgressionStep(3, 10, 8.0),
        ProgressionStep(2, 12, 6.5),
    ),
}


WEEK_LABELS = (
    "Accumulation",
    "Build",
    "Intensification",
    "Pivot",
)

WEEK_SUMMARIES = (
    "Establish technical volume and accumulate useful work with conservative RPE targets.",
    "Push load and specificity upward while keeping total fatigue manageable.",
    "Expose heavier work and sharper top-end effort without letting fatigue run the week.",
    "Reduce fatigue, keep movement quality high, and set up the next block cleanly.",
)


class ProgramGenerator:
    def generate(self, athlete: AthleteProfile, athlete_level: str, focus_points: list[str]) -> ProgramOverview:
        training_days = self._validated_training_days(athlete.training_days_per_week)
        split = f"{training_days}-day powerlifting split"
        weeks = self._build_weeks(athlete, training_days)

        summary = (
            f"A {athlete_level} 4-week block for {athlete.primary_goal.lower()}, built on a {split} "
            "with bench frequency prioritized and fatigue-controlled squat and deadlift exposures."
        )

        progression_notes = [
            "Bench appears more often than squat and deadlift because it usually tolerates higher weekly frequency.",
            "Main competition lifts start around RPE 6-7 and build toward RPE 8-8.5 before the pivot week.",
            "Week 4 is a pivot week: volume comes down, technique stays in place, and the next block can build from cleaner readiness.",
            "Daily load adjustments should use the target RPE as the guardrail rather than forcing percentages on bad days.",
        ]

        return ProgramOverview(
            account_id=athlete.account_id,
            style=f"{athlete_level.capitalize()} rule-based powerlifting block",
            summary=summary,
            split=split,
            focus_points=focus_points,
            progression_notes=progression_notes,
            weeks=weeks,
        )

    def _build_weeks(self, athlete: AthleteProfile, training_days: int) -> list[ProgramWeek]:
        templates = self._day_templates(athlete, training_days)
        weeks: list[ProgramWeek] = []

        for week_index, (label, summary) in enumerate(zip(WEEK_LABELS, WEEK_SUMMARIES, strict=True)):
            days = [
                ProgramDay(
                    day_label=f"Day {day_number}",
                    focus=template["focus"],
                    objective=template["objective"],
                    exercises=[
                        self._build_exercise(slot, week_index)
                        for slot in template["exercise_slots"]
                    ],
                )
                for day_number, template in enumerate(templates, start=1)
            ]
            weeks.append(
                ProgramWeek(
                    week_number=week_index + 1,
                    label=label,
                    summary=summary,
                    days=days,
                )
            )

        return weeks

    def _day_templates(self, athlete: AthleteProfile, training_days: int) -> list[dict]:
        squat_variation = self._squat_variation(athlete)
        deadlift_variation = self._deadlift_variation(athlete)
        row_variation = self._row_variation(athlete)
        bench_variation = self._bench_variation(athlete)

        five_day_templates = [
            {
                "focus": "Primary bench day",
                "objective": "Open the week with the main bench exposure and upper-body assistance that supports it.",
                "exercise_slots": [
                    self._slot("Competition bench press", "competition", "bench_intensity", "Primary bench exposure for the week."),
                    self._slot("Dips", "accessory", "press_assistance", "Heavy pressing assistance for triceps and chest."),
                    self._slot("Overhead press", "accessory", "press_assistance", "Secondary press for shoulder strength."),
                    self._slot("Lateral raise", "accessory", "arm_isolation", "Shoulder hypertrophy support."),
                    self._slot("Rear delt fly", "accessory", "arm_isolation", "Upper-back and shoulder balance work."),
                    self._slot("JM press", "accessory", "arm_isolation", "Direct triceps volume with pressing carryover."),
                    self._slot("Cable fly", "accessory", "arm_isolation", "Low-cost pec volume."),
                ],
            },
            {
                "focus": "Competition deadlift day",
                "objective": "Place the main conventional deadlift exposure early in the week and keep lower-body accessories controlled.",
                "exercise_slots": [
                    self._slot("Competition deadlift", "competition", "deadlift_primary", "Primary conventional deadlift exposure."),
                    self._slot("Leg press", "accessory", "single_leg", "Lower-body volume without high technical cost."),
                    self._slot("Cable hip abductor", "accessory", "single_leg", "Hip stability and glute-med support."),
                    self._slot("Lat pulldown", "accessory", "row_support", "Lat strength for deadlift positioning."),
                    self._slot(row_variation, "accessory", "row_support", "Extra pulling support for the hinge days."),
                    self._slot("Lat pullover", "accessory", "triceps_upper_back", "Lats without adding spinal fatigue."),
                ],
            },
            {
                "focus": "Bench and squat support",
                "objective": "Use a secondary bench and a secondary squat to build muscle and positional quality mid-week.",
                "exercise_slots": [
                    self._slot("Spoto press", "variation", "bench_technique", "Secondary bench exposure focused on control."),
                    self._slot(squat_variation, "variation", "squat_hypertrophy", "High-rep squat support and positional work."),
                    self._slot("Hack squat", "accessory", "single_leg", "Quad work without another barbell squat cost."),
                    self._slot("Leg curl", "accessory", "posterior_chain", "Hamstring support."),
                    self._slot("Back extension", "accessory", "posterior_chain", "Posterior-chain endurance with low skill demand."),
                ],
            },
            {
                "focus": "Secondary deadlift and bench repetition",
                "objective": "Add a second hinge touchpoint with lower cost, then a repetition bench and smaller upper-body work.",
                "exercise_slots": [
                    self._slot(deadlift_variation, "variation", "deadlift_secondary", "Secondary deadlift slot for position and speed."),
                    self._slot("Copenhagen plank", "accessory", "trunk_gpp", "Adductor and trunk support."),
                    self._slot("Bench press repetition work", "variation", "bench_volume", "Higher-rep bench slot for extra exposure."),
                    self._slot("Incline dumbbell curl", "accessory", "arm_isolation", "Biceps support."),
                    self._slot("Preacher curl", "accessory", "arm_isolation", "Arm isolation that does not tax recovery."),
                    self._slot("Triceps pushdown", "accessory", "arm_isolation", "Simple triceps volume."),
                    self._slot("Overhead triceps extension", "accessory", "arm_isolation", "Long-head triceps support."),
                ],
            },
            {
                "focus": "Competition squat day",
                "objective": "Close the week with the main squat exposure and a final paused bench slot.",
                "exercise_slots": [
                    self._slot("Competition squat", "competition", "squat_primary", "Primary squat exposure for the week."),
                    self._slot("Goblet squat", "accessory", "single_leg", "Light patterning and quad work."),
                    self._slot("Bulgarian split squat", "accessory", "single_leg", "Single-leg control and leg volume."),
                    self._slot(bench_variation, "variation", "bench_hypertrophy", "Final bench exposure of the week with longer time under tension."),
                    self._slot("Leg extension", "accessory", "arm_isolation", "Quad isolation to push local volume."),
                    self._slot("Sit-up", "accessory", "trunk_gpp", "Trunk flexion work."),
                    self._slot("Leg raise", "accessory", "trunk_gpp", "Anterior core support."),
                ],
            },
        ]

        if training_days == 5:
            return five_day_templates

        return [
            {
                "focus": "Primary bench day",
                "objective": "Open the week with the main bench exposure and upper-body assistance that supports it.",
                "exercise_slots": five_day_templates[0]["exercise_slots"],
            },
            {
                "focus": "Competition deadlift day",
                "objective": "Place the main conventional deadlift exposure early in the week and keep lower-body accessories controlled.",
                "exercise_slots": five_day_templates[1]["exercise_slots"],
            },
            {
                "focus": "Bench and squat support",
                "objective": "Use a secondary bench and a secondary squat to build muscle and positional quality mid-week.",
                "exercise_slots": five_day_templates[2]["exercise_slots"],
            },
            {
                "focus": "Competition squat and bench closeout",
                "objective": "Finish the week with the main squat slot and a final bench touchpoint.",
                "exercise_slots": [
                    self._slot("Competition squat", "competition", "squat_primary", "Primary squat exposure for the week."),
                    self._slot("Bulgarian split squat", "accessory", "single_leg", "Single-leg control and leg volume."),
                    self._slot(bench_variation, "variation", "bench_hypertrophy", "Final bench exposure of the week with controlled fatigue."),
                    self._slot(row_variation, "accessory", "row_support", "Upper-back support for stable pressing."),
                    self._slot("Leg extension", "accessory", "arm_isolation", "Quad isolation to round out the week."),
                    self._slot("Weighted plank", "accessory", "trunk_gpp", "Trunk work to finish the week."),
                ],
            },
        ]

    @staticmethod
    def _build_exercise(slot: dict, week_index: int) -> ProgramExercisePrescription:
        progression = PROGRESSION_LIBRARY[slot["progression_key"]][week_index]
        return ProgramExercisePrescription(
            name=slot["name"],
            category=slot["category"],
            sets=progression.sets,
            reps=progression.reps,
            target_rpe=progression.rpe,
            notes=slot["notes"],
        )

    @staticmethod
    def _slot(name: str, category: str, progression_key: str, notes: str) -> dict:
        return {
            "name": name,
            "category": category,
            "progression_key": progression_key,
            "notes": notes,
        }

    @staticmethod
    def _validated_training_days(training_days: int) -> int:
        if training_days not in (4, 5):
            raise ValueError("For now, myPowerCoach only supports 4-day or 5-day training splits.")
        return training_days

    @staticmethod
    def _all_notes(athlete: AthleteProfile) -> str:
        return " ".join([athlete.notes, *athlete.constraints]).lower()

    def _squat_variation(self, athlete: AthleteProfile) -> str:
        notes = self._all_notes(athlete)
        if "hip" in notes or "bottom" in notes:
            return "Paused squat"
        if "brace" in notes or "position" in notes:
            return "Tempo squat"
        return "Paused squat"

    def _deadlift_variation(self, athlete: AthleteProfile) -> str:
        notes = self._all_notes(athlete)
        if "back" in notes or "fatigue" in notes:
            return "Romanian deadlift"
        return "Paused deadlift"

    def _row_variation(self, athlete: AthleteProfile) -> str:
        notes = self._all_notes(athlete)
        if "back" in notes:
            return "Chest-supported row"
        return "Barbell row"

    def _bench_variation(self, athlete: AthleteProfile) -> str:
        notes = self._all_notes(athlete)
        if "pause" in notes or "chest" in notes:
            return "Paused bench press"
        return "Competition bench press"
