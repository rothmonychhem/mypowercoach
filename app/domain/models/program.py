from dataclasses import dataclass, field


@dataclass(slots=True)
class ProgramExercisePrescription:
    name: str
    category: str
    sets: int
    reps: int
    target_rpe: float
    notes: str = ""


@dataclass(slots=True)
class ProgramDay:
    day_label: str
    focus: str
    objective: str
    exercises: list[ProgramExercisePrescription] = field(default_factory=list)


@dataclass(slots=True)
class ProgramWeek:
    week_number: int
    label: str
    summary: str
    days: list[ProgramDay] = field(default_factory=list)


@dataclass(slots=True)
class ProgramOverview:
    account_id: str
    style: str
    summary: str
    split: str
    focus_points: list[str]
    progression_notes: list[str]
    weeks: list[ProgramWeek] = field(default_factory=list)
