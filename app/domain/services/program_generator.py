from copy import deepcopy
from dataclasses import dataclass

from app.domain.models.athlete import AthleteProfile
from app.domain.models.program import (
    ProgramDay,
    ProgramExercisePrescription,
    ProgramOverview,
    ProgramWeek,
)
from app.domain.services.exercise_selector import (
    ExerciseSelectionContext,
    RuleBasedExerciseSelector,
)


@dataclass(frozen=True, slots=True)
class ProgressionStep:
    sets: int
    reps: int
    rpe: float


@dataclass(frozen=True, slots=True)
class AthleteNeeds:
    lower_back_sensitivity: bool
    bench_priority: bool
    squat_priority: bool
    deadlift_priority: bool
    leg_drive_focus: bool
    knee_stability_focus: bool
    squat_bottom_focus: bool
    deadlift_floor_focus: bool
    deadlift_lockout_focus: bool
    bench_off_chest_focus: bool
    bench_lockout_focus: bool
    target_limiters: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BlockTypeProfile:
    block_type: str
    week_labels: tuple[str, str, str, str]
    week_summaries: tuple[str, str, str, str]
    percentage_shift: tuple[float, float, float, float]
    rpe_shift: tuple[float, float, float, float]
    set_shift: tuple[int, int, int, int]
    rep_shift: tuple[int, int, int, int]
    max_exercises_per_day: int | None
    accessory_cap: int | None


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
    "back_health": (
        ProgressionStep(2, 12, 6.0),
        ProgressionStep(2, 10, 6.5),
        ProgressionStep(3, 10, 7.0),
        ProgressionStep(2, 12, 5.5),
    ),
}

LOAD_LIBRARY: dict[str, tuple[float | None, float | None, float | None, float | None]] = {
    "squat_primary": (0.72, 0.76, 0.80, 0.67),
    "squat_secondary": (0.64, 0.68, 0.72, 0.60),
    "bench_volume": (0.75, 0.78, 0.825, 0.70),
    "bench_intensity": (0.77, 0.80, 0.84, 0.72),
    "bench_technique": (0.68, 0.71, 0.74, 0.65),
    "deadlift_primary": (0.70, 0.74, 0.78, 0.65),
    "deadlift_secondary": (0.62, 0.66, 0.70, 0.58),
    "press_assistance": (0.55, 0.58, 0.60, 0.52),
    "row_support": (0.32, 0.35, 0.37, 0.28),
    "single_leg": (0.26, 0.29, 0.31, 0.24),
    "posterior_chain": (0.38, 0.41, 0.44, 0.34),
    "triceps_upper_back": (0.22, 0.24, 0.26, 0.20),
    "trunk_gpp": (None, None, None, None),
    "bench_hypertrophy": (0.67, 0.70, 0.73, 0.63),
    "squat_hypertrophy": (0.56, 0.60, 0.64, 0.52),
    "arm_isolation": (0.18, 0.20, 0.22, 0.16),
    "back_health": (0.18, 0.20, 0.22, 0.16),
}


BLOCK_TYPE_LIBRARY: dict[str, BlockTypeProfile] = {
    "off_season": BlockTypeProfile(
        block_type="off_season",
        week_labels=("Foundation", "Volume build", "Strength bridge", "Pivot"),
        week_summaries=(
            "Start the block with more variation, more muscle-building work, and lower stress per exposure.",
            "Drive volume higher while keeping technique and recovery under control.",
            "Bridge toward heavier work without abandoning variation and weak-point work.",
            "Drop fatigue, keep quality high, and leave room to push the next block.",
        ),
        percentage_shift=(-0.02, -0.01, 0.0, -0.02),
        rpe_shift=(-0.5, -0.25, 0.0, -0.5),
        set_shift=(1, 1, 0, -1),
        rep_shift=(1, 1, 0, 0),
        max_exercises_per_day=None,
        accessory_cap=None,
    ),
    "general_strength": BlockTypeProfile(
        block_type="general_strength",
        week_labels=("Accumulation", "Build", "Intensification", "Pivot"),
        week_summaries=(
            "Establish technical volume and accumulate useful work with conservative RPE targets.",
            "Push load and specificity upward while keeping total fatigue manageable.",
            "Expose heavier work and sharper top-end effort without letting fatigue run the week.",
            "Reduce fatigue, keep movement quality high, and set up the next block cleanly.",
        ),
        percentage_shift=(0.0, 0.0, 0.0, 0.0),
        rpe_shift=(0.0, 0.0, 0.0, 0.0),
        set_shift=(0, 0, 0, 0),
        rep_shift=(0, 0, 0, 0),
        max_exercises_per_day=None,
        accessory_cap=None,
    ),
    "pivot": BlockTypeProfile(
        block_type="pivot",
        week_labels=("Reset", "Reload", "Rebuild", "Exit"),
        week_summaries=(
            "Cut fatigue early and restore movement quality instead of forcing another hard accumulation wave.",
            "Bring productive work back in carefully with simpler prescriptions and tighter fatigue control.",
            "Rebuild momentum with moderate loading while keeping the weak area exposed at a manageable cost.",
            "Finish the pivot fresher than you started it so the next block can be more aggressive.",
        ),
        percentage_shift=(-0.05, -0.04, -0.02, -0.05),
        rpe_shift=(-1.0, -0.75, -0.5, -1.0),
        set_shift=(-1, -1, -1, -1),
        rep_shift=(0, 0, 0, 0),
        max_exercises_per_day=5,
        accessory_cap=2,
    ),
    "peak": BlockTypeProfile(
        block_type="peak",
        week_labels=("Specificity", "Heavy build", "Realization", "Freshen up"),
        week_summaries=(
            "Shift the block toward competition lifts and reduce fluff so heavy work has room to matter.",
            "Drive heavier specific work while trimming accessory fatigue that could blur performance.",
            "Let the athlete touch the sharpest work of the block with specificity prioritized over volume.",
            "Freshen up without losing the feel of the competition lifts.",
        ),
        percentage_shift=(0.015, 0.025, 0.035, -0.01),
        rpe_shift=(0.25, 0.25, 0.5, -0.5),
        set_shift=(0, -1, -1, -1),
        rep_shift=(-1, -1, -1, 0),
        max_exercises_per_day=5,
        accessory_cap=2,
    ),
    "taper": BlockTypeProfile(
        block_type="taper",
        week_labels=("Volume cut", "Sharpness", "Meet week", "Transition"),
        week_summaries=(
            "Start dropping fatigue fast while keeping enough specific work to hold onto rhythm.",
            "Keep the lifts sharp with small exposures and far less background fatigue.",
            "Do the minimum effective work needed to stay confident and coordinated going into testing or competition.",
            "Use a very easy transition week before the next full block starts.",
        ),
        percentage_shift=(-0.02, 0.0, -0.05, -0.08),
        rpe_shift=(-0.75, -0.5, -1.0, -1.25),
        set_shift=(-2, -2, -3, -3),
        rep_shift=(-1, -2, -2, -1),
        max_exercises_per_day=3,
        accessory_cap=1,
    ),
}


class ProgramGenerator:
    def __init__(self, exercise_selector: RuleBasedExerciseSelector | None = None) -> None:
        self._exercise_selector = exercise_selector or RuleBasedExerciseSelector()

    def generate(self, athlete: AthleteProfile, athlete_level: str, focus_points: list[str]) -> ProgramOverview:
        training_days = self._validated_training_days(athlete.training_days_per_week)
        split = f"{training_days}-day powerlifting split"
        athlete_needs = self._athlete_needs(athlete)
        block_type = self._block_type(athlete, athlete_needs)
        block_profile = BLOCK_TYPE_LIBRARY[block_type]
        weeks = self._build_weeks(athlete, training_days, athlete_needs, block_profile)
        block_focus = self._block_focus_summary(athlete_needs)

        summary = (
            f"A {athlete_level} 4-week block for {athlete.primary_goal.lower()}, built on a {split} "
            f"using a {block_type.replace('_', ' ')} structure with bench frequency prioritized "
            f"and a block emphasis on {block_focus.lower()}."
        )

        progression_notes = [
            f"Block type is {block_type.replace('_', ' ')}, so the structure, exercise density, and loading all reflect that phase rather than repeating the same 4-week shape every time.",
            "Bench appears more often than squat and deadlift because it usually tolerates higher weekly frequency.",
            "Variation slots are chosen by a scoring engine that balances specificity, weak-point match, fatigue cost, and pain constraints instead of reusing the same combo every block.",
            "Main competition lifts start around RPE 6-7 and build toward RPE 8-8.5 before the pivot week.",
            "Suggested loads are anchored to the athlete's current PRs and rounded to realistic gym jumps, usually 2.5 kg for upper-body work and 5 kg for lower-body work.",
            "Weak areas should get enough exposure to improve, but pain-sensitive regions should get support with a lower fatigue cost instead of reckless overload.",
            "Sets, reps, and load should move together: heavier weeks usually come with fewer reps or slightly less total volume rather than mindlessly adding stress everywhere.",
            "Daily load adjustments should use the target RPE as the guardrail rather than forcing percentages on bad days.",
        ]

        return ProgramOverview(
            account_id=athlete.account_id,
            style=f"{athlete_level.capitalize()} rule-based powerlifting block",
            summary=summary,
            split=split,
            block_type=block_type,
            block_focus=block_focus,
            focus_points=focus_points,
            target_limiters=list(athlete_needs.target_limiters),
            progression_notes=progression_notes,
            weeks=weeks,
        )

    def _build_weeks(
        self,
        athlete: AthleteProfile,
        training_days: int,
        athlete_needs: AthleteNeeds,
        block_profile: BlockTypeProfile,
    ) -> list[ProgramWeek]:
        templates = self._day_templates(athlete, training_days, athlete_needs, block_profile)
        weeks: list[ProgramWeek] = []

        for week_index, (label, summary) in enumerate(zip(block_profile.week_labels, block_profile.week_summaries, strict=True)):
            days = [
                ProgramDay(
                    day_label=f"Day {day_number}",
                    focus=template["focus"],
                    objective=template["objective"],
                    exercises=[
                        self._build_exercise(athlete, slot, week_index, athlete_needs, block_profile)
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

    def _day_templates(
        self,
        athlete: AthleteProfile,
        training_days: int,
        athlete_needs: AthleteNeeds,
        block_profile: BlockTypeProfile,
    ) -> list[dict]:
        selection_context = self._selection_context(athlete_needs, block_profile)
        main_deadlift_note = (
            "Primary deadlift exposure with spinal fatigue managed more carefully because low-back stress is a known constraint."
            if athlete_needs.lower_back_sensitivity
            else "Primary conventional deadlift exposure."
        )
        secondary_deadlift_note = (
            "Secondary deadlift slot kept technical and submaximal so the weak area is trained without tipping total fatigue over."
            if athlete_needs.lower_back_sensitivity
            else "Secondary deadlift slot for position and speed."
        )

        day1_primary = self._slot("Competition bench press", "competition", "bench_intensity", "Primary bench exposure for the week.")
        bench_primary_support = self._select_slot(
            "bench_primary_support",
            selection_context,
            primary_day_tags=("horizontal_press", "pec", "triceps"),
            existing_slots=[day1_primary],
        )

        day2_primary = self._slot("Competition deadlift", "competition", "deadlift_primary", main_deadlift_note)
        quad_support_accessory = self._select_slot(
            "quad_support_accessory",
            selection_context,
            primary_day_tags=("hinge", "posterior_chain", "bracing"),
            existing_slots=[day2_primary],
        )
        row_variation = self._select_slot(
            "row_variation",
            selection_context,
            primary_day_tags=("hinge", "posterior_chain", "upper_back"),
            existing_slots=[
                day2_primary,
                quad_support_accessory,
                self._slot("Cable hip abductor", "accessory", "single_leg", "Hip stability and glute-med support.", load_anchor="squat"),
                self._slot("Lat pulldown", "accessory", "row_support", "Lat strength for deadlift positioning.", load_anchor="deadlift"),
            ],
        )

        bench_secondary_variation = self._select_slot(
            "bench_secondary_variation",
            selection_context,
            primary_day_tags=("horizontal_press", "pec", "triceps"),
            existing_slots=[],
        )
        squat_variation = self._select_slot(
            "squat_secondary_variation",
            selection_context,
            primary_day_tags=("squat_pattern", "quads", "bracing"),
            existing_slots=[bench_secondary_variation],
        )
        quad_support_midweek = self._select_slot(
            "quad_support_accessory",
            selection_context,
            primary_day_tags=("squat_pattern", "quads", "bracing"),
            existing_slots=[bench_secondary_variation, squat_variation],
        )
        posterior_chain_accessory = self._select_slot(
            "posterior_chain_accessory",
            selection_context,
            primary_day_tags=("squat_pattern", "posterior_chain"),
            existing_slots=[
                bench_secondary_variation,
                squat_variation,
                quad_support_midweek,
                self._slot("Leg curl", "accessory", "posterior_chain", "Hamstring support.", load_anchor="deadlift"),
            ],
        )

        deadlift_variation = self._select_slot(
            "deadlift_secondary_variation",
            selection_context,
            primary_day_tags=("hinge", "posterior_chain", "bracing"),
            existing_slots=[],
        )
        bench_rep_variation = self._select_slot(
            "bench_rep_variation",
            selection_context,
            primary_day_tags=("horizontal_press", "pec", "triceps"),
            existing_slots=[
                deadlift_variation,
                self._slot("Copenhagen plank", "accessory", "trunk_gpp", "Adductor and trunk support.", load_anchor=None),
            ],
        )

        day5_primary = self._slot("Competition squat", "competition", "squat_primary", "Primary squat exposure for the week.")
        squat_primary_accessory = self._select_slot(
            "squat_primary_accessory",
            selection_context,
            primary_day_tags=("squat_pattern", "quads", "bracing"),
            existing_slots=[day5_primary],
        )
        bench_variation = self._select_slot(
            "bench_closeout_variation",
            selection_context,
            primary_day_tags=("horizontal_press", "pec", "triceps"),
            existing_slots=[
                day5_primary,
                squat_primary_accessory,
                self._slot("Bulgarian split squat", "accessory", "single_leg", "Single-leg control and leg volume.", load_anchor="squat"),
            ],
        )

        five_day_templates = [
            {
                "focus": "Primary bench day",
                "objective": "Open the week with the main bench exposure and upper-body assistance that supports it.",
                "exercise_slots": [
                    day1_primary,
                    bench_primary_support,
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
                    day2_primary,
                    quad_support_accessory,
                    self._slot("Cable hip abductor", "accessory", "single_leg", "Hip stability and glute-med support.", load_anchor="squat"),
                    self._slot("Lat pulldown", "accessory", "row_support", "Lat strength for deadlift positioning.", load_anchor="deadlift"),
                    row_variation,
                    self._slot("Lat pullover", "accessory", "triceps_upper_back", "Lats without adding spinal fatigue.", load_anchor="bench"),
                ],
            },
            {
                "focus": "Bench and squat support",
                "objective": "Use a secondary bench and a secondary squat to build muscle and positional quality mid-week.",
                "exercise_slots": [
                    bench_secondary_variation,
                    squat_variation,
                    quad_support_midweek,
                    self._slot("Leg curl", "accessory", "posterior_chain", "Hamstring support.", load_anchor="deadlift"),
                    posterior_chain_accessory,
                ],
            },
            {
                "focus": "Secondary deadlift and bench repetition",
                "objective": "Add a second hinge touchpoint with lower cost, then a repetition bench and smaller upper-body work.",
                "exercise_slots": [
                    self._with_objective_note(deadlift_variation, secondary_deadlift_note),
                    self._slot("Copenhagen plank", "accessory", "trunk_gpp", "Adductor and trunk support.", load_anchor=None),
                    bench_rep_variation,
                    self._slot("Incline dumbbell curl", "accessory", "arm_isolation", "Biceps support.", load_anchor="bench"),
                    self._slot("Preacher curl", "accessory", "arm_isolation", "Arm isolation that does not tax recovery.", load_anchor="bench"),
                    self._slot("Triceps pushdown", "accessory", "arm_isolation", "Simple triceps volume.", load_anchor="bench"),
                    self._slot("Overhead triceps extension", "accessory", "arm_isolation", "Long-head triceps support.", load_anchor="bench"),
                ],
            },
            {
                "focus": "Competition squat day",
                "objective": "Close the week with the main squat exposure and a final bench support slot.",
                "exercise_slots": [
                    day5_primary,
                    squat_primary_accessory,
                    self._slot("Bulgarian split squat", "accessory", "single_leg", "Single-leg control and leg volume.", load_anchor="squat"),
                    bench_variation,
                    self._slot("Leg extension", "accessory", "arm_isolation", "Quad isolation to push local volume.", load_anchor="squat"),
                    self._slot("Sit-up", "accessory", "trunk_gpp", "Trunk flexion work.", load_anchor=None),
                    self._slot("Leg raise", "accessory", "trunk_gpp", "Anterior core support.", load_anchor=None),
                ],
            },
        ]

        if athlete_needs.knee_stability_focus:
            five_day_templates[1]["exercise_slots"][1] = self._select_slot(
                "quad_support_accessory",
                selection_context,
                primary_day_tags=("hinge", "posterior_chain", "bracing"),
                existing_slots=[day2_primary],
            )

        if athlete_needs.bench_priority:
            five_day_templates[3]["objective"] = (
                "Add a second hinge touchpoint with lower cost while keeping the extra bench slot meaningful because bench is a priority."
            )

        if training_days == 5:
            templates = five_day_templates
        else:
            templates = [
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
                    day5_primary,
                    self._slot("Bulgarian split squat", "accessory", "single_leg", "Single-leg control and leg volume.", load_anchor="squat"),
                    bench_variation,
                    row_variation,
                    self._slot("Leg extension", "accessory", "arm_isolation", "Quad isolation to round out the week.", load_anchor="squat"),
                    self._slot("Weighted plank", "accessory", "trunk_gpp", "Trunk work to finish the week.", load_anchor=None),
                ],
            },
            ]

        return self._apply_block_type_to_templates(templates, block_profile, athlete_needs)

    def _build_exercise(
        self,
        athlete: AthleteProfile,
        slot: dict,
        week_index: int,
        athlete_needs: AthleteNeeds,
        block_profile: BlockTypeProfile,
    ) -> ProgramExercisePrescription:
        progression = PROGRESSION_LIBRARY[slot["progression_key"]][week_index]
        progression = self._progression_for_block_type(progression, slot, week_index, block_profile)
        prescribed_weight, reference_lift, percent_of_reference = self._build_load_prescription(
            athlete=athlete,
            slot=slot,
            week_index=week_index,
            athlete_needs=athlete_needs,
            block_profile=block_profile,
        )
        return ProgramExercisePrescription(
            name=slot["name"],
            category=slot["category"],
            sets=progression.sets,
            reps=progression.reps,
            target_rpe=progression.rpe,
            prescribed_weight_kg=prescribed_weight,
            reference_lift=reference_lift,
            percent_of_reference=percent_of_reference,
            notes=slot["notes"],
            selection_reason=slot.get("selection_reason", ""),
        )

    @staticmethod
    def _slot(
        name: str,
        category: str,
        progression_key: str,
        notes: str,
        load_anchor: str | None = None,
        selection_reason: str = "",
    ) -> dict:
        return {
            "name": name,
            "category": category,
            "progression_key": progression_key,
            "notes": notes,
            "load_anchor": load_anchor,
            "selection_reason": selection_reason,
        }

    @staticmethod
    def _with_objective_note(slot: dict, prefix_note: str) -> dict:
        updated_slot = dict(slot)
        updated_slot["notes"] = f"{prefix_note} {slot['notes']}".strip()
        return updated_slot

    @staticmethod
    def _selection_context(
        athlete_needs: AthleteNeeds,
        block_profile: BlockTypeProfile,
    ) -> ExerciseSelectionContext:
        return ExerciseSelectionContext(
            block_type=block_profile.block_type,
            lower_back_sensitivity=athlete_needs.lower_back_sensitivity,
            bench_priority=athlete_needs.bench_priority,
            squat_priority=athlete_needs.squat_priority,
            deadlift_priority=athlete_needs.deadlift_priority,
            leg_drive_focus=athlete_needs.leg_drive_focus,
            knee_stability_focus=athlete_needs.knee_stability_focus,
            squat_bottom_focus=athlete_needs.squat_bottom_focus,
            deadlift_floor_focus=athlete_needs.deadlift_floor_focus,
            deadlift_lockout_focus=athlete_needs.deadlift_lockout_focus,
            bench_off_chest_focus=athlete_needs.bench_off_chest_focus,
            bench_lockout_focus=athlete_needs.bench_lockout_focus,
        )

    def _select_slot(
        self,
        slot_key: str,
        context: ExerciseSelectionContext,
        primary_day_tags: tuple[str, ...] = (),
        existing_slots: list[dict] | None = None,
    ) -> dict:
        existing_slots = existing_slots or []
        day_context = ExerciseSelectionContext(
            block_type=context.block_type,
            lower_back_sensitivity=context.lower_back_sensitivity,
            bench_priority=context.bench_priority,
            squat_priority=context.squat_priority,
            deadlift_priority=context.deadlift_priority,
            leg_drive_focus=context.leg_drive_focus,
            knee_stability_focus=context.knee_stability_focus,
            squat_bottom_focus=context.squat_bottom_focus,
            deadlift_floor_focus=context.deadlift_floor_focus,
            deadlift_lockout_focus=context.deadlift_lockout_focus,
            bench_off_chest_focus=context.bench_off_chest_focus,
            bench_lockout_focus=context.bench_lockout_focus,
            primary_day_tags=primary_day_tags,
            accumulated_movement_tags=self._accumulated_tags(existing_slots, "movement"),
            accumulated_soreness_tags=self._accumulated_tags(existing_slots, "soreness"),
            accumulated_day_fatigue=self._accumulated_day_fatigue(existing_slots),
        )
        return self._exercise_selector.select_slot(slot_key, day_context)

    def _accumulated_tags(self, slots: list[dict], kind: str) -> tuple[str, ...]:
        values: list[str] = []
        for slot in slots:
            tags = slot.get(f"{kind}_tags")
            if tags:
                values.extend(tags)
                continue
            movement_tags, soreness_tags = self._infer_slot_profiles(slot)
            values.extend(movement_tags if kind == "movement" else soreness_tags)
        return tuple(values)

    def _accumulated_day_fatigue(self, slots: list[dict]) -> float:
        total = 0.0
        for slot in slots:
            if "fatigue_cost" in slot:
                total += float(slot["fatigue_cost"])
            else:
                total += self._infer_slot_fatigue(slot)
        return round(total, 2)

    @staticmethod
    def _infer_slot_profiles(slot: dict) -> tuple[tuple[str, ...], tuple[str, ...]]:
        progression_key = slot.get("progression_key", "")
        name = slot.get("name", "").lower()

        if "bench" in name or "press" in name or "fly" in name:
            return ("horizontal_press", "pec", "triceps"), ("pec", "front_delts", "triceps")
        if "squat" in name or "leg press" in name or "leg extension" in name:
            return ("squat_pattern", "quads", "bracing"), ("quads", "glutes")
        if "deadlift" in name or "back extension" in name or "pull-through" in name:
            return ("hinge", "posterior_chain", "bracing"), ("hamstrings", "glutes", "low_back")
        if "row" in name or "lat" in name:
            return ("upper_back", "lats"), ("lats", "upper_back")
        if progression_key == "single_leg":
            return ("single_leg", "quads"), ("quads", "glutes")
        if progression_key == "posterior_chain":
            return ("posterior_chain", "hinge"), ("hamstrings", "glutes")
        return (), ()

    @staticmethod
    def _infer_slot_fatigue(slot: dict) -> float:
        progression_key = slot.get("progression_key", "")
        category = slot.get("category", "")
        if category == "competition":
            return 4.0
        fatigue_by_progression = {
            "bench_intensity": 4.0,
            "bench_volume": 3.4,
            "bench_technique": 3.0,
            "bench_hypertrophy": 2.9,
            "squat_primary": 4.1,
            "squat_secondary": 3.5,
            "squat_hypertrophy": 3.1,
            "deadlift_primary": 4.2,
            "deadlift_secondary": 3.2,
            "posterior_chain": 2.5,
            "back_health": 1.8,
            "press_assistance": 2.8,
            "row_support": 2.4,
            "single_leg": 2.4,
            "trunk_gpp": 1.2,
            "triceps_upper_back": 1.8,
            "arm_isolation": 1.4,
        }
        return fatigue_by_progression.get(progression_key, 2.2)

    def _build_load_prescription(
        self,
        athlete: AthleteProfile,
        slot: dict,
        week_index: int,
        athlete_needs: AthleteNeeds,
        block_profile: BlockTypeProfile,
    ) -> tuple[float | None, str | None, float | None]:
        load_anchor = slot.get("load_anchor")
        if load_anchor is None:
            load_anchor = self._infer_load_anchor(slot["name"])

        percentage = LOAD_LIBRARY[slot["progression_key"]][week_index]
        if load_anchor is None or percentage is None:
            return None, None, None

        percentage = self._adjust_percentage_for_needs(percentage, slot, athlete_needs)
        percentage += block_profile.percentage_shift[week_index]

        reference_max = self._reference_max(athlete, load_anchor)
        raw_weight = reference_max * percentage
        rounded_weight = self._round_weight(raw_weight, load_anchor, slot["name"])
        return rounded_weight, load_anchor, round(percentage * 100, 1)

    @staticmethod
    def _adjust_percentage_for_needs(
        percentage: float,
        slot: dict,
        athlete_needs: AthleteNeeds,
    ) -> float:
        progression_key = slot["progression_key"]
        category = slot["category"]
        adjusted = percentage

        if athlete_needs.lower_back_sensitivity and progression_key in {"deadlift_primary", "deadlift_secondary", "posterior_chain"}:
            adjusted -= 0.03 if category != "competition" else 0.025
        if athlete_needs.lower_back_sensitivity and progression_key == "row_support":
            adjusted -= 0.02
        if athlete_needs.bench_priority and progression_key in {"bench_intensity", "bench_volume", "bench_hypertrophy", "bench_technique"}:
            adjusted += 0.01
        if athlete_needs.squat_priority and progression_key in {"squat_primary", "squat_secondary", "squat_hypertrophy"}:
            adjusted += 0.01
        if athlete_needs.deadlift_priority and progression_key == "deadlift_primary" and not athlete_needs.lower_back_sensitivity:
            adjusted += 0.01

        return max(0.12, adjusted)

    @staticmethod
    def _progression_for_block_type(
        progression: ProgressionStep,
        slot: dict,
        week_index: int,
        block_profile: BlockTypeProfile,
    ) -> ProgressionStep:
        sets = progression.sets + block_profile.set_shift[week_index]
        reps = progression.reps + block_profile.rep_shift[week_index]
        rpe = progression.rpe + block_profile.rpe_shift[week_index]
        category = slot["category"]

        if category == "accessory" and block_profile.block_type in {"peak", "taper", "pivot"}:
            sets = min(sets, progression.sets if block_profile.block_type == "pivot" else max(2, progression.sets - 1))
        if block_profile.block_type == "peak" and category == "competition":
            reps = min(reps, max(1, progression.reps - 1))
        if block_profile.block_type == "taper":
            rpe = min(rpe, 7.5)

        return ProgressionStep(
            sets=max(1, sets),
            reps=max(1, reps),
            rpe=max(5.0, round(rpe, 1)),
        )

    @staticmethod
    def _reference_max(athlete: AthleteProfile, load_anchor: str) -> float:
        if load_anchor == "squat":
            return athlete.lift_numbers.squat_kg
        if load_anchor == "bench":
            return athlete.lift_numbers.bench_kg
        return athlete.lift_numbers.deadlift_kg

    @staticmethod
    def _infer_load_anchor(exercise_name: str) -> str | None:
        normalized = exercise_name.lower()
        if "bench" in normalized or "press" in normalized or "fly" in normalized or "triceps" in normalized:
            return "bench"
        if "squat" in normalized or "leg" in normalized or "bulgarian" in normalized:
            return "squat"
        if "deadlift" in normalized or "row" in normalized or "lat" in normalized or "back extension" in normalized:
            return "deadlift"
        return None

    @staticmethod
    def _round_weight(raw_weight: float, load_anchor: str, exercise_name: str) -> float:
        normalized = exercise_name.lower()
        if load_anchor == "bench" or any(keyword in normalized for keyword in ("curl", "raise", "fly", "pushdown", "extension")):
            increment = 2.5
        else:
            increment = 5.0

        rounded = round(raw_weight / increment) * increment
        return max(increment, round(rounded, 1))

    @staticmethod
    def _validated_training_days(training_days: int) -> int:
        if training_days not in (4, 5):
            raise ValueError("For now, myPowerCoach only supports 4-day or 5-day training splits.")
        return training_days

    @staticmethod
    def _all_notes(athlete: AthleteProfile) -> str:
        return " ".join([athlete.notes, *athlete.constraints]).lower()

    def _athlete_needs(self, athlete: AthleteProfile) -> AthleteNeeds:
        notes = self._all_notes(athlete)
        squat = athlete.lift_numbers.squat_kg
        bench = athlete.lift_numbers.bench_kg
        deadlift = athlete.lift_numbers.deadlift_kg
        target_limiters: list[str] = []

        lower_back_sensitivity = any(term in notes for term in ("low-back pain", "lower back pain", "back pain", "back fatigue", "low-back fatigue", "lower back"))
        bench_priority = squat > 0 and bench / squat < 0.58
        squat_priority = deadlift > 0 and squat / deadlift < 0.78
        deadlift_priority = squat > 0 and deadlift / squat < 1.08
        leg_drive_focus = "leg drive" in notes
        knee_stability_focus = any(term in notes for term in ("knee cave", "knee collapse", "knee pain", "knee track"))
        squat_bottom_focus = any(term in notes for term in ("out of the hole", "bottom", "hips shoot", "quad"))
        deadlift_floor_focus = any(term in notes for term in ("off the floor", "floor break", "wedge", "bar drifts", "bar drift"))
        deadlift_lockout_focus = any(term in notes for term in ("lockout", "at knee", "near the knee"))
        bench_off_chest_focus = any(term in notes for term in ("off chest", "off the chest", "pause weakness", "start strength")) or leg_drive_focus
        bench_lockout_focus = any(term in notes for term in ("bench lockout", "bench triceps", "soft lockout"))

        if lower_back_sensitivity:
            target_limiters.append("low-back-friendly posterior-chain development")
        if bench_priority:
            target_limiters.append("bench specialization")
        if squat_priority or squat_bottom_focus:
            target_limiters.append("squat drive out of the hole")
        if deadlift_priority or deadlift_floor_focus:
            target_limiters.append("deadlift strength from the floor")
        if leg_drive_focus:
            target_limiters.append("bench leg-drive timing")
        if knee_stability_focus:
            target_limiters.append("knee stability")

        if not target_limiters:
            target_limiters.append("general strength accumulation")

        return AthleteNeeds(
            lower_back_sensitivity=lower_back_sensitivity,
            bench_priority=bench_priority,
            squat_priority=squat_priority,
            deadlift_priority=deadlift_priority,
            leg_drive_focus=leg_drive_focus,
            knee_stability_focus=knee_stability_focus,
            squat_bottom_focus=squat_bottom_focus,
            deadlift_floor_focus=deadlift_floor_focus,
            deadlift_lockout_focus=deadlift_lockout_focus,
            bench_off_chest_focus=bench_off_chest_focus,
            bench_lockout_focus=bench_lockout_focus,
            target_limiters=tuple(target_limiters),
        )

    @staticmethod
    def _block_focus_summary(athlete_needs: AthleteNeeds) -> str:
        if not athlete_needs.target_limiters:
            return "general strength accumulation"
        return ", ".join(athlete_needs.target_limiters[:2])

    def _block_type(self, athlete: AthleteProfile, athlete_needs: AthleteNeeds) -> str:
        preferred = athlete.preferred_block_type.strip().lower().replace(" ", "_")
        if preferred in BLOCK_TYPE_LIBRARY:
            return preferred

        notes = self._all_notes(athlete)
        goal = athlete.primary_goal.lower()

        if any(term in notes for term in ("meet week", "competition next week", "competition in 1 week", "test week", "mock meet", "taper")):
            return "taper"
        if any(term in notes for term in ("peak", "peaking", "competition prep", "meet prep", "meet block", "test max", "1rm")):
            return "peak"
        if any(term in notes for term in ("deload", "pivot", "recover", "recovery block", "fatigued", "burned out")):
            return "pivot"
        if any(term in goal for term in ("hypertrophy", "build muscle", "off season", "off-season", "growth")):
            return "off_season"
        if athlete_needs.lower_back_sensitivity and any(term in notes for term in ("pain flare", "beat up", "recovery")):
            return "pivot"
        return "general_strength"

    def _apply_block_type_to_templates(
        self,
        templates: list[dict],
        block_profile: BlockTypeProfile,
        athlete_needs: AthleteNeeds,
    ) -> list[dict]:
        adjusted_templates = deepcopy(templates)

        for template in adjusted_templates:
            slots = template["exercise_slots"]
            if block_profile.block_type == "off_season":
                template["objective"] += " Variation and targeted support stay higher because this block is building capacity."
            if block_profile.block_type == "pivot":
                template["objective"] += " Exercise count and fatigue are intentionally trimmed so recovery can rebound."
            if block_profile.block_type == "peak":
                template["objective"] += " Exercise selection is tighter so performance can center on the competition lifts."
            if block_profile.block_type == "taper":
                template["objective"] += " Only the minimum useful work stays in so fatigue can fall quickly."

            if block_profile.accessory_cap is not None:
                accessory_seen = 0
                kept_slots: list[dict] = []
                for slot in slots:
                    if slot["category"] == "accessory":
                        accessory_seen += 1
                        if accessory_seen > block_profile.accessory_cap:
                            continue
                    kept_slots.append(slot)
                template["exercise_slots"] = kept_slots
                slots = template["exercise_slots"]

            if block_profile.max_exercises_per_day is not None:
                template["exercise_slots"] = slots[: block_profile.max_exercises_per_day]

        if block_profile.block_type in {"peak", "taper"}:
            for template in adjusted_templates:
                for slot in template["exercise_slots"]:
                    if slot["name"] == "Competition bench press" and athlete_needs.bench_off_chest_focus:
                        slot["notes"] = "Competition bench work stays specific, but the setup and pause should still reflect the off-chest weakness the block is trying to improve."
                    if slot["name"] == "Competition squat" and athlete_needs.squat_bottom_focus:
                        slot["notes"] = "Competition squat stays in place while the lifter practices cleaner balance and drive out of the hole."
                    if slot["name"] == "Competition deadlift" and athlete_needs.deadlift_floor_focus:
                        slot["notes"] = "Competition deadlift stays specific while the setup, wedge, and first push from the floor remain the priority."

        return adjusted_templates

    def _bench_primary_support(self, athlete_needs: AthleteNeeds) -> dict:
        if athlete_needs.bench_off_chest_focus:
            return self._slot(
                "Paused bench press",
                "variation",
                "bench_technique",
                "Use a more controlled bench variation to rehearse tighter touch position and cleaner leg-drive timing.",
            )
        if athlete_needs.bench_lockout_focus:
            return self._slot(
                "Close-grip bench press",
                "variation",
                "press_assistance",
                "Use a lockout-biased press variation when the finish is the limiting factor.",
            )
        return self._slot(
            "Dips",
            "accessory",
            "press_assistance",
            "Heavy pressing assistance for triceps and chest.",
            load_anchor=None,
        )

    def _bench_secondary_variation(self, athlete_needs: AthleteNeeds) -> dict:
        if athlete_needs.bench_off_chest_focus:
            return self._slot(
                "Long-pause bench press",
                "variation",
                "bench_technique",
                "Build start strength, touch control, and pressure transfer off the chest.",
            )
        if athlete_needs.bench_lockout_focus:
            return self._slot(
                "Pin press",
                "variation",
                "bench_technique",
                "Bias the range where the bar usually softens near lockout.",
            )
        return self._slot(
            "Spoto press",
            "variation",
            "bench_technique",
            "Secondary bench exposure focused on control.",
        )

    def _bench_rep_variation(self, athlete_needs: AthleteNeeds) -> dict:
        if athlete_needs.bench_priority:
            return self._slot(
                "Bench press repetition work",
                "variation",
                "bench_volume",
                "Higher-rep bench slot to keep the priority lift driving forward through extra quality volume.",
            )
        return self._slot(
            "Bench press repetition work",
            "variation",
            "bench_volume",
            "Higher-rep bench slot for extra exposure.",
        )

    def _squat_primary_accessory(self, athlete_needs: AthleteNeeds) -> dict:
        if athlete_needs.squat_bottom_focus:
            return self._slot(
                "Front squat",
                "variation",
                "squat_secondary",
                "Use a more upright squat variation when the block is trying to improve drive and position out of the hole.",
                load_anchor="squat",
            )
        return self._slot(
            "Goblet squat",
            "accessory",
            "single_leg",
            "Light patterning and quad work.",
            load_anchor="squat",
        )

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
