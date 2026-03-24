from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExerciseDefinition:
    slot_key: str
    name: str
    category: str
    progression_key: str
    notes: str
    load_anchor: str | None = None
    specificity: float = 2.0
    fatigue_cost: float = 3.0
    emphasis_tags: tuple[str, ...] = ()
    movement_tags: tuple[str, ...] = ()
    soreness_tags: tuple[str, ...] = ()
    phase_tags: tuple[str, ...] = ()
    helpful_tags: tuple[str, ...] = ()
    costly_tags: tuple[str, ...] = ()
    sort_order: int = 0
