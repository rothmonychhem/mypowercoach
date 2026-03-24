from dataclasses import dataclass

from app.domain.models.exercise import ExerciseDefinition


@dataclass(frozen=True, slots=True)
class ExerciseSelectionContext:
    block_type: str
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
    primary_day_tags: tuple[str, ...] = ()
    accumulated_movement_tags: tuple[str, ...] = ()
    accumulated_soreness_tags: tuple[str, ...] = ()
    accumulated_day_fatigue: float = 0.0


class RuleBasedExerciseSelector:
    def __init__(self, exercise_repository: object | None = None) -> None:
        self._exercise_repository = exercise_repository
        self._library = EXERCISE_LIBRARY

    def select_slot(self, slot_key: str, context: ExerciseSelectionContext) -> dict:
        candidates = self._candidates_for_slot(slot_key)
        scored = [(self._score_candidate(candidate, context), candidate) for candidate in candidates]
        scored.sort(key=lambda item: item[0], reverse=True)
        score, candidate = scored[0]
        return {
            "name": candidate.name,
            "category": candidate.category,
            "progression_key": candidate.progression_key,
            "notes": candidate.notes,
            "load_anchor": candidate.load_anchor,
            "movement_tags": candidate.movement_tags,
            "soreness_tags": candidate.soreness_tags,
            "fatigue_cost": candidate.fatigue_cost,
            "selection_reason": self._selection_reason(candidate, context, score),
        }

    def _candidates_for_slot(self, slot_key: str) -> tuple[ExerciseDefinition, ...]:
        if self._exercise_repository is not None:
            load_method = getattr(self._exercise_repository, "list_by_slot", None)
            if callable(load_method):
                loaded = tuple(candidate for candidate in load_method(slot_key) if self._is_complete_candidate(candidate))
                if loaded:
                    return loaded
        return self._library[slot_key]

    @staticmethod
    def _is_complete_candidate(candidate: ExerciseDefinition) -> bool:
        return bool(
            candidate.slot_key
            and candidate.name
            and candidate.category
            and candidate.progression_key
            and candidate.notes
        )

    def _score_candidate(self, candidate: ExerciseDefinition, context: ExerciseSelectionContext) -> float:
        specificity_weight = 0.55
        fatigue_weight = 0.35
        score = candidate.specificity * specificity_weight + (6.0 - candidate.fatigue_cost) * fatigue_weight

        if context.block_type == "off_season":
            if "volume" in candidate.phase_tags or "variation" in candidate.phase_tags:
                score += 1.2
            if "specificity" in candidate.phase_tags:
                score -= 0.2
        elif context.block_type == "general_strength":
            if "bridge" in candidate.phase_tags or "specificity" in candidate.phase_tags:
                score += 0.75
        elif context.block_type == "pivot":
            score += (6.0 - candidate.fatigue_cost) * 0.6
            if "recovery" in candidate.phase_tags:
                score += 1.2
            if "high_stress" in candidate.costly_tags:
                score -= 0.8
        elif context.block_type == "peak":
            score += candidate.specificity * 0.65
            if "specificity" in candidate.phase_tags:
                score += 1.25
            if "volume" in candidate.phase_tags:
                score -= 0.4
        elif context.block_type == "taper":
            score += candidate.specificity * 0.85
            score += (6.0 - candidate.fatigue_cost) * 0.75
            if "recovery" in candidate.phase_tags or "specificity" in candidate.phase_tags:
                score += 1.0
            if "volume" in candidate.phase_tags:
                score -= 0.75

        score += self._needs_score(candidate, context)
        score += self._day_balance_score(candidate, context)
        return round(score, 3)

    @staticmethod
    def _needs_score(candidate: ExerciseDefinition, context: ExerciseSelectionContext) -> float:
        score = 0.0

        if context.lower_back_sensitivity:
            if "low_back_friendly" in candidate.helpful_tags:
                score += 1.9
            if "high_spinal_cost" in candidate.costly_tags:
                score -= 2.1
        if context.bench_priority and "bench_bias" in candidate.helpful_tags:
            score += 0.8
        if context.squat_priority and "squat_bias" in candidate.helpful_tags:
            score += 0.8
        if context.deadlift_priority and "deadlift_bias" in candidate.helpful_tags:
            score += 0.8
        if context.leg_drive_focus and "leg_drive" in candidate.emphasis_tags:
            score += 1.6
        if context.knee_stability_focus and "knee_stability" in candidate.emphasis_tags:
            score += 1.7
        if context.squat_bottom_focus and "squat_bottom" in candidate.emphasis_tags:
            score += 2.0
        if context.deadlift_floor_focus and "deadlift_floor" in candidate.emphasis_tags:
            score += 2.0
        if context.deadlift_lockout_focus and "deadlift_lockout" in candidate.emphasis_tags:
            score += 1.9
        if context.bench_off_chest_focus and "bench_off_chest" in candidate.emphasis_tags:
            score += 2.0
        if context.bench_lockout_focus and "bench_lockout" in candidate.emphasis_tags:
            score += 2.0

        return score

    @staticmethod
    def _day_balance_score(candidate: ExerciseDefinition, context: ExerciseSelectionContext) -> float:
        score = 0.0
        movement_overlap = len(set(candidate.movement_tags) & set(context.accumulated_movement_tags))
        soreness_overlap = len(set(candidate.soreness_tags) & set(context.accumulated_soreness_tags))
        primary_overlap = len(set(candidate.movement_tags) & set(context.primary_day_tags))

        if primary_overlap and candidate.fatigue_cost >= 3.4 and "same_day_primary_ok" not in candidate.helpful_tags:
            score -= 0.9 * primary_overlap
        elif primary_overlap and "direct_support" in candidate.helpful_tags:
            score += 0.35

        if movement_overlap:
            score -= movement_overlap * (0.45 if candidate.fatigue_cost >= 3.0 else 0.2)
        if soreness_overlap:
            score -= soreness_overlap * (0.3 if candidate.fatigue_cost >= 2.5 else 0.15)

        if context.accumulated_day_fatigue >= 6.0:
            if candidate.fatigue_cost >= 3.2:
                score -= 0.7
            elif candidate.fatigue_cost <= 2.4:
                score += 0.35
        if context.accumulated_day_fatigue >= 8.5:
            if "low_local_soreness" in candidate.helpful_tags or "low_back_friendly" in candidate.helpful_tags:
                score += 0.35
            elif candidate.fatigue_cost >= 3.0:
                score -= 0.5

        return score

    @staticmethod
    def _selection_reason(candidate: ExerciseDefinition, context: ExerciseSelectionContext, score: float) -> str:
        reasons: list[str] = []

        if context.block_type in candidate.phase_tags:
            reasons.append(f"fits the {context.block_type.replace('_', ' ')} phase")
        elif context.block_type == "peak" and "specificity" in candidate.phase_tags:
            reasons.append("keeps specificity high for heavier work")
        elif context.block_type in {"pivot", "taper"} and "recovery" in candidate.phase_tags:
            reasons.append("keeps fatigue under tighter control")
        elif context.block_type == "off_season" and "variation" in candidate.phase_tags:
            reasons.append("adds variation while capacity is being built")

        if context.lower_back_sensitivity and "low_back_friendly" in candidate.helpful_tags:
            reasons.append("reduces spinal cost while still training the target pattern")
        if context.bench_off_chest_focus and "bench_off_chest" in candidate.emphasis_tags:
            reasons.append("targets strength and control off the chest")
        if context.bench_lockout_focus and "bench_lockout" in candidate.emphasis_tags:
            reasons.append("biases the bench lockout range")
        if context.leg_drive_focus and "leg_drive" in candidate.emphasis_tags:
            reasons.append("helps clean up leg-drive timing")
        if context.squat_bottom_focus and "squat_bottom" in candidate.emphasis_tags:
            reasons.append("targets drive out of the hole")
        if context.knee_stability_focus and "knee_stability" in candidate.emphasis_tags:
            reasons.append("supports steadier knee tracking")
        if context.deadlift_floor_focus and "deadlift_floor" in candidate.emphasis_tags:
            reasons.append("helps improve the break from the floor")
        if context.deadlift_lockout_focus and "deadlift_lockout" in candidate.emphasis_tags:
            reasons.append("builds the top-end pull and lockout")
        if context.accumulated_day_fatigue >= 6.0 and candidate.fatigue_cost <= 2.4:
            reasons.append("keeps same-day fatigue and soreness more manageable")

        if not reasons:
            reasons.append("was the best overall fit for specificity, fatigue cost, and current focus")

        joined = "; ".join(reasons[:2])
        return f"Selected by the exercise scorer because it {joined}. Score {score:.1f}."


EXERCISE_LIBRARY: dict[str, tuple[ExerciseDefinition, ...]] = {
    "bench_primary_support": (
        ExerciseDefinition(
            slot_key="bench_primary_support",
            name="Paused bench press",
            category="variation",
            progression_key="bench_technique",
            notes="Use a more controlled bench variation to rehearse tighter touch position and cleaner leg-drive timing.",
            load_anchor="bench",
            specificity=4.6,
            fatigue_cost=3.0,
            emphasis_tags=("bench_off_chest", "leg_drive"),
            movement_tags=("horizontal_press", "pec", "triceps"),
            soreness_tags=("pec", "front_delts", "triceps"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("bench_bias", "direct_support", "same_day_primary_ok"),
        ),
        ExerciseDefinition(
            slot_key="bench_primary_support",
            name="Close-grip bench press",
            category="variation",
            progression_key="press_assistance",
            notes="Use a lockout-biased press variation when the finish is the limiting factor.",
            load_anchor="bench",
            specificity=4.0,
            fatigue_cost=3.2,
            emphasis_tags=("bench_lockout",),
            movement_tags=("horizontal_press", "triceps"),
            soreness_tags=("triceps", "front_delts"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("bench_bias", "direct_support"),
        ),
        ExerciseDefinition(
            slot_key="bench_primary_support",
            name="Larsen press",
            category="variation",
            progression_key="bench_technique",
            notes="Remove some leg assistance so upper-back tension and touch control have to stay honest.",
            load_anchor="bench",
            specificity=3.6,
            fatigue_cost=2.4,
            emphasis_tags=("bench_off_chest",),
            movement_tags=("horizontal_press", "upper_back"),
            soreness_tags=("pec", "front_delts"),
            phase_tags=("off_season", "variation", "volume"),
            helpful_tags=("bench_bias", "low_local_soreness"),
        ),
        ExerciseDefinition(
            slot_key="bench_primary_support",
            name="Dips",
            category="accessory",
            progression_key="press_assistance",
            notes="Heavy pressing assistance for triceps and chest.",
            specificity=2.7,
            fatigue_cost=3.0,
            emphasis_tags=("bench_lockout",),
            movement_tags=("vertical_press", "triceps"),
            soreness_tags=("triceps", "pec"),
            phase_tags=("off_season", "volume"),
            helpful_tags=("bench_bias",),
        ),
    ),
    "bench_secondary_variation": (
        ExerciseDefinition(
            slot_key="bench_secondary_variation",
            name="Long-pause bench press",
            category="variation",
            progression_key="bench_technique",
            notes="Build start strength, touch control, and pressure transfer off the chest.",
            load_anchor="bench",
            specificity=4.7,
            fatigue_cost=3.0,
            emphasis_tags=("bench_off_chest", "leg_drive"),
            movement_tags=("horizontal_press", "pec", "triceps"),
            soreness_tags=("pec", "front_delts", "triceps"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("bench_bias", "direct_support", "same_day_primary_ok"),
        ),
        ExerciseDefinition(
            slot_key="bench_secondary_variation",
            name="Pin press",
            category="variation",
            progression_key="bench_technique",
            notes="Bias the range where the bar usually softens near lockout.",
            load_anchor="bench",
            specificity=4.1,
            fatigue_cost=3.1,
            emphasis_tags=("bench_lockout",),
            movement_tags=("horizontal_press", "triceps"),
            soreness_tags=("triceps", "front_delts"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("bench_bias", "direct_support"),
        ),
        ExerciseDefinition(
            slot_key="bench_secondary_variation",
            name="Spoto press",
            category="variation",
            progression_key="bench_technique",
            notes="Secondary bench exposure focused on control and a stable touch position.",
            load_anchor="bench",
            specificity=4.2,
            fatigue_cost=2.8,
            emphasis_tags=("bench_off_chest",),
            movement_tags=("horizontal_press", "pec"),
            soreness_tags=("pec", "front_delts"),
            phase_tags=("off_season", "general_strength", "variation"),
            helpful_tags=("bench_bias", "direct_support"),
        ),
        ExerciseDefinition(
            slot_key="bench_secondary_variation",
            name="Feet-up bench press",
            category="variation",
            progression_key="bench_technique",
            notes="Strip away lower-body help to sharpen bar control and torso positioning.",
            load_anchor="bench",
            specificity=3.5,
            fatigue_cost=2.3,
            emphasis_tags=("bench_off_chest",),
            movement_tags=("horizontal_press", "upper_back"),
            soreness_tags=("pec", "front_delts"),
            phase_tags=("off_season", "variation", "volume"),
            helpful_tags=("bench_bias", "low_local_soreness"),
        ),
    ),
    "bench_rep_variation": (
        ExerciseDefinition(
            slot_key="bench_rep_variation",
            name="Bench press repetition work",
            category="variation",
            progression_key="bench_volume",
            notes="Higher-rep bench slot to keep quality volume in the week without drifting away from the main lift.",
            load_anchor="bench",
            specificity=4.3,
            fatigue_cost=3.4,
            movement_tags=("horizontal_press", "pec", "triceps"),
            soreness_tags=("pec", "front_delts", "triceps"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("bench_bias", "same_day_primary_ok"),
        ),
        ExerciseDefinition(
            slot_key="bench_rep_variation",
            name="Close-grip bench repetition work",
            category="variation",
            progression_key="bench_volume",
            notes="Use more repetition work through a narrower press when triceps or lockout need more dedicated volume.",
            load_anchor="bench",
            specificity=4.0,
            fatigue_cost=3.2,
            emphasis_tags=("bench_lockout",),
            movement_tags=("horizontal_press", "triceps"),
            soreness_tags=("triceps", "front_delts"),
            phase_tags=("general_strength", "off_season", "variation"),
            helpful_tags=("bench_bias",),
        ),
        ExerciseDefinition(
            slot_key="bench_rep_variation",
            name="Larsen press repetition work",
            category="variation",
            progression_key="bench_volume",
            notes="Extra bench volume with less total loading so bar path and upper-back discipline can stay crisp.",
            load_anchor="bench",
            specificity=3.4,
            fatigue_cost=2.5,
            emphasis_tags=("bench_off_chest",),
            movement_tags=("horizontal_press", "upper_back"),
            soreness_tags=("pec", "front_delts"),
            phase_tags=("off_season", "pivot", "variation", "recovery"),
            helpful_tags=("bench_bias", "low_local_soreness"),
        ),
    ),
    "bench_closeout_variation": (
        ExerciseDefinition(
            slot_key="bench_closeout_variation",
            name="Paused bench press",
            category="variation",
            progression_key="bench_hypertrophy",
            notes="Final bench exposure of the week with a controlled pause and cleaner pressure transfer.",
            load_anchor="bench",
            specificity=4.5,
            fatigue_cost=2.9,
            emphasis_tags=("bench_off_chest", "leg_drive"),
            movement_tags=("horizontal_press", "pec", "triceps"),
            soreness_tags=("pec", "front_delts", "triceps"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("bench_bias", "same_day_primary_ok"),
        ),
        ExerciseDefinition(
            slot_key="bench_closeout_variation",
            name="Competition bench press",
            category="variation",
            progression_key="bench_hypertrophy",
            notes="Final bench exposure of the week with controlled fatigue and direct carryover to the comp lift.",
            load_anchor="bench",
            specificity=5.0,
            fatigue_cost=3.2,
            movement_tags=("horizontal_press", "pec", "triceps"),
            soreness_tags=("pec", "front_delts", "triceps"),
            phase_tags=("peak", "taper", "specificity"),
            helpful_tags=("bench_bias", "same_day_primary_ok"),
        ),
        ExerciseDefinition(
            slot_key="bench_closeout_variation",
            name="Larsen press",
            category="variation",
            progression_key="bench_hypertrophy",
            notes="A lower-fatigue bench touch that keeps tension honest even when the week is already busy.",
            load_anchor="bench",
            specificity=3.6,
            fatigue_cost=2.2,
            emphasis_tags=("bench_off_chest",),
            movement_tags=("horizontal_press", "upper_back"),
            soreness_tags=("pec", "front_delts"),
            phase_tags=("off_season", "pivot", "variation", "recovery"),
            helpful_tags=("bench_bias", "low_local_soreness"),
        ),
    ),
    "squat_secondary_variation": (
        ExerciseDefinition(
            slot_key="squat_secondary_variation",
            name="Paused squat",
            category="variation",
            progression_key="squat_hypertrophy",
            notes="High-rep squat support that reinforces balance and force out of the bottom.",
            load_anchor="squat",
            specificity=4.3,
            fatigue_cost=3.2,
            emphasis_tags=("squat_bottom",),
            movement_tags=("squat_pattern", "quads", "bracing"),
            soreness_tags=("quads", "adductors", "glutes"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("squat_bias", "direct_support", "same_day_primary_ok"),
        ),
        ExerciseDefinition(
            slot_key="squat_secondary_variation",
            name="Tempo squat",
            category="variation",
            progression_key="squat_hypertrophy",
            notes="Use tempo to improve bracing, mid-foot control, and positional awareness on the way down.",
            load_anchor="squat",
            specificity=4.0,
            fatigue_cost=2.9,
            emphasis_tags=("squat_bottom", "knee_stability"),
            movement_tags=("squat_pattern", "quads", "bracing"),
            soreness_tags=("quads", "adductors"),
            phase_tags=("off_season", "pivot", "variation", "recovery"),
            helpful_tags=("squat_bias", "direct_support", "low_local_soreness"),
        ),
        ExerciseDefinition(
            slot_key="squat_secondary_variation",
            name="Front squat",
            category="variation",
            progression_key="squat_hypertrophy",
            notes="Use a more upright squat variation when the block is trying to improve drive and position out of the hole.",
            load_anchor="squat",
            specificity=3.8,
            fatigue_cost=3.4,
            emphasis_tags=("squat_bottom",),
            movement_tags=("squat_pattern", "quads", "upper_back"),
            soreness_tags=("quads", "upper_back"),
            phase_tags=("off_season", "general_strength", "variation"),
            helpful_tags=("squat_bias",),
        ),
    ),
    "squat_primary_accessory": (
        ExerciseDefinition(
            slot_key="squat_primary_accessory",
            name="Front squat",
            category="variation",
            progression_key="squat_secondary",
            notes="Use a more upright squat variation when the block is trying to improve drive and position out of the hole.",
            load_anchor="squat",
            specificity=4.0,
            fatigue_cost=3.6,
            emphasis_tags=("squat_bottom",),
            movement_tags=("squat_pattern", "quads", "upper_back"),
            soreness_tags=("quads", "upper_back"),
            phase_tags=("general_strength", "off_season", "variation"),
            helpful_tags=("squat_bias", "direct_support"),
        ),
        ExerciseDefinition(
            slot_key="squat_primary_accessory",
            name="Tempo goblet squat",
            category="accessory",
            progression_key="single_leg",
            notes="Patterning and knee-control work to reinforce stable tracking without another heavy spinal demand.",
            load_anchor="squat",
            specificity=2.5,
            fatigue_cost=1.9,
            emphasis_tags=("knee_stability", "squat_bottom"),
            movement_tags=("squat_pattern", "quads"),
            soreness_tags=("quads",),
            phase_tags=("pivot", "taper", "recovery"),
            helpful_tags=("squat_bias", "low_back_friendly", "low_local_soreness"),
        ),
        ExerciseDefinition(
            slot_key="squat_primary_accessory",
            name="Goblet squat",
            category="accessory",
            progression_key="single_leg",
            notes="Light patterning and quad work.",
            load_anchor="squat",
            specificity=2.3,
            fatigue_cost=1.8,
            movement_tags=("squat_pattern", "quads"),
            soreness_tags=("quads",),
            phase_tags=("off_season", "pivot", "recovery"),
            helpful_tags=("squat_bias", "low_back_friendly", "low_local_soreness"),
        ),
    ),
    "quad_support_accessory": (
        ExerciseDefinition(
            slot_key="quad_support_accessory",
            name="Hack squat",
            category="accessory",
            progression_key="single_leg",
            notes="Quad work without another barbell squat cost.",
            load_anchor="squat",
            specificity=2.8,
            fatigue_cost=2.8,
            emphasis_tags=("squat_bottom",),
            movement_tags=("squat_pattern", "quads"),
            soreness_tags=("quads",),
            phase_tags=("off_season", "general_strength", "volume"),
            helpful_tags=("squat_bias", "low_back_friendly"),
        ),
        ExerciseDefinition(
            slot_key="quad_support_accessory",
            name="Front-foot elevated split squat",
            category="accessory",
            progression_key="single_leg",
            notes="Quad-biased unilateral work to help squat drive without another heavy barbell cost.",
            load_anchor="squat",
            specificity=2.6,
            fatigue_cost=2.4,
            emphasis_tags=("squat_bottom", "knee_stability"),
            movement_tags=("single_leg", "quads", "adductors"),
            soreness_tags=("quads", "glutes"),
            phase_tags=("general_strength", "pivot", "recovery"),
            helpful_tags=("squat_bias", "low_back_friendly", "low_local_soreness"),
        ),
        ExerciseDefinition(
            slot_key="quad_support_accessory",
            name="Leg press",
            category="accessory",
            progression_key="single_leg",
            notes="Lower-body volume without high technical cost.",
            load_anchor="squat",
            specificity=2.1,
            fatigue_cost=2.5,
            movement_tags=("single_leg", "quads"),
            soreness_tags=("quads",),
            phase_tags=("off_season", "volume"),
            helpful_tags=("squat_bias", "low_back_friendly"),
        ),
    ),
    "deadlift_secondary_variation": (
        ExerciseDefinition(
            slot_key="deadlift_secondary_variation",
            name="Paused deadlift",
            category="variation",
            progression_key="deadlift_secondary",
            notes="Secondary deadlift slot for position and speed through the hardest early range.",
            load_anchor="deadlift",
            specificity=4.4,
            fatigue_cost=3.2,
            emphasis_tags=("deadlift_floor",),
            movement_tags=("hinge", "posterior_chain", "bracing"),
            soreness_tags=("hamstrings", "glutes", "low_back"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("deadlift_bias", "direct_support"),
        ),
        ExerciseDefinition(
            slot_key="deadlift_secondary_variation",
            name="Block pull",
            category="variation",
            progression_key="deadlift_secondary",
            notes="Use a top-half deadlift variation when the bar keeps dying near the knee or at lockout.",
            load_anchor="deadlift",
            specificity=3.9,
            fatigue_cost=3.1,
            emphasis_tags=("deadlift_lockout",),
            movement_tags=("hinge", "posterior_chain", "upper_back"),
            soreness_tags=("glutes", "hamstrings", "upper_back"),
            phase_tags=("general_strength", "peak", "specificity"),
            helpful_tags=("deadlift_bias",),
        ),
        ExerciseDefinition(
            slot_key="deadlift_secondary_variation",
            name="Deficit deadlift",
            category="variation",
            progression_key="deadlift_secondary",
            notes="Use more range when the block needs force from the floor and the athlete can tolerate the extra stress.",
            load_anchor="deadlift",
            specificity=4.0,
            fatigue_cost=4.1,
            emphasis_tags=("deadlift_floor",),
            movement_tags=("hinge", "posterior_chain", "bracing"),
            soreness_tags=("hamstrings", "glutes", "low_back"),
            phase_tags=("off_season", "variation", "volume"),
            helpful_tags=("deadlift_bias",),
            costly_tags=("high_spinal_cost",),
        ),
        ExerciseDefinition(
            slot_key="deadlift_secondary_variation",
            name="Tempo deadlift",
            category="variation",
            progression_key="deadlift_secondary",
            notes="A lower-load hinge slot that still teaches position and patience without pushing fatigue too hard.",
            load_anchor="deadlift",
            specificity=3.7,
            fatigue_cost=2.4,
            emphasis_tags=("deadlift_floor",),
            movement_tags=("hinge", "posterior_chain", "bracing"),
            soreness_tags=("hamstrings", "glutes"),
            phase_tags=("pivot", "taper", "recovery"),
            helpful_tags=("deadlift_bias", "low_back_friendly", "low_local_soreness"),
        ),
    ),
    "row_variation": (
        ExerciseDefinition(
            slot_key="row_variation",
            name="Chest-supported row",
            category="accessory",
            progression_key="row_support",
            notes="Extra pulling support for the hinge and bench days without adding much spinal fatigue.",
            load_anchor="deadlift",
            specificity=2.1,
            fatigue_cost=1.9,
            movement_tags=("upper_back", "lats"),
            soreness_tags=("lats", "upper_back"),
            phase_tags=("pivot", "taper", "recovery"),
            helpful_tags=("low_back_friendly", "low_local_soreness"),
        ),
        ExerciseDefinition(
            slot_key="row_variation",
            name="Barbell row",
            category="accessory",
            progression_key="row_support",
            notes="Extra pulling support for the hinge days with more total loading through the trunk.",
            load_anchor="deadlift",
            specificity=2.5,
            fatigue_cost=3.6,
            movement_tags=("upper_back", "hinge", "bracing"),
            soreness_tags=("lats", "upper_back", "low_back"),
            phase_tags=("off_season", "volume"),
            costly_tags=("high_spinal_cost",),
        ),
        ExerciseDefinition(
            slot_key="row_variation",
            name="Cable row",
            category="accessory",
            progression_key="row_support",
            notes="Simple upper-back volume when the block wants pulling work without extra setup fatigue.",
            load_anchor="deadlift",
            specificity=1.8,
            fatigue_cost=1.7,
            movement_tags=("upper_back", "lats"),
            soreness_tags=("lats", "upper_back"),
            phase_tags=("pivot", "taper", "recovery"),
            helpful_tags=("low_back_friendly", "low_local_soreness"),
        ),
    ),
    "posterior_chain_accessory": (
        ExerciseDefinition(
            slot_key="posterior_chain_accessory",
            name="Reverse hyper",
            category="accessory",
            progression_key="back_health",
            notes="Low-cost lower-back and posterior-chain support with fatigue capped.",
            load_anchor="deadlift",
            specificity=1.7,
            fatigue_cost=1.6,
            movement_tags=("posterior_chain", "low_back"),
            soreness_tags=("glutes", "low_back"),
            phase_tags=("pivot", "taper", "recovery"),
            helpful_tags=("low_back_friendly", "low_local_soreness"),
        ),
        ExerciseDefinition(
            slot_key="posterior_chain_accessory",
            name="Back extension",
            category="accessory",
            progression_key="posterior_chain",
            notes="Posterior-chain endurance with low skill demand.",
            load_anchor="deadlift",
            specificity=2.0,
            fatigue_cost=2.4,
            movement_tags=("posterior_chain", "low_back"),
            soreness_tags=("glutes", "hamstrings", "low_back"),
            phase_tags=("general_strength", "off_season", "volume"),
            helpful_tags=("deadlift_bias",),
        ),
        ExerciseDefinition(
            slot_key="posterior_chain_accessory",
            name="Cable pull-through",
            category="accessory",
            progression_key="back_health",
            notes="A hinge-pattern accessory that keeps glute and hamstring work in without adding much recovery debt.",
            load_anchor="deadlift",
            specificity=1.8,
            fatigue_cost=1.9,
            movement_tags=("posterior_chain", "glutes"),
            soreness_tags=("glutes", "hamstrings"),
            phase_tags=("pivot", "off_season", "recovery"),
            helpful_tags=("low_back_friendly", "low_local_soreness"),
        ),
    ),
}

REQUIRED_SELECTOR_SLOTS: tuple[str, ...] = tuple(EXERCISE_LIBRARY.keys())


def catalog_exercises() -> list[ExerciseDefinition]:
    catalog: list[ExerciseDefinition] = []
    for slot_key, exercises in EXERCISE_LIBRARY.items():
        for sort_order, exercise in enumerate(exercises):
            catalog.append(
                ExerciseDefinition(
                    slot_key=slot_key,
                    name=exercise.name,
                    category=exercise.category,
                    progression_key=exercise.progression_key,
                    notes=exercise.notes,
                    load_anchor=exercise.load_anchor,
                    specificity=exercise.specificity,
                    fatigue_cost=exercise.fatigue_cost,
                    emphasis_tags=exercise.emphasis_tags,
                    movement_tags=exercise.movement_tags,
                    soreness_tags=exercise.soreness_tags,
                    phase_tags=exercise.phase_tags,
                    helpful_tags=exercise.helpful_tags,
                    costly_tags=exercise.costly_tags,
                    sort_order=sort_order,
                )
            )
    return catalog


def validate_catalog() -> dict[str, list[str]]:
    issues: dict[str, list[str]] = {}
    for slot_key, exercises in EXERCISE_LIBRARY.items():
        slot_issues: list[str] = []
        if not exercises:
            slot_issues.append("Slot has no exercise candidates.")
        for exercise in exercises:
            if not exercise.name:
                slot_issues.append("Candidate is missing a name.")
            if not exercise.category:
                slot_issues.append(f"{exercise.name or 'Candidate'} is missing a category.")
            if not exercise.progression_key:
                slot_issues.append(f"{exercise.name or 'Candidate'} is missing a progression key.")
            if not exercise.notes:
                slot_issues.append(f"{exercise.name or 'Candidate'} is missing coaching notes.")
            if not exercise.movement_tags:
                slot_issues.append(f"{exercise.name or 'Candidate'} is missing movement tags.")
            if not exercise.soreness_tags:
                slot_issues.append(f"{exercise.name or 'Candidate'} is missing soreness tags.")
        if slot_issues:
            issues[slot_key] = slot_issues
    return issues
