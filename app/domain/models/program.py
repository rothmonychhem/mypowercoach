from dataclasses import dataclass, field


@dataclass(slots=True)
class ProgramSession:
    day_label: str
    focus: str
    prescription: str


@dataclass(slots=True)
class ProgramOverview:
    account_id: str
    style: str
    summary: str
    focus_points: list[str]
    sessions: list[ProgramSession] = field(default_factory=list)
