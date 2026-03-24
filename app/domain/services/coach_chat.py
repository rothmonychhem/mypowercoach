import re

from app.domain.models.athlete import AthleteProfile
from app.domain.models.coaching import ChatReply
from app.domain.models.program import ProgramOverview


class CoachChatService:
    def reply(self, athlete: AthleteProfile, program: ProgramOverview, message: str) -> ChatReply:
        text = self._normalize(message)

        if self._matches(text, "why", "change", "next week", "next workout", "adjust"):
            answer = self._change_answer(program)
        elif self._matches(text, "today", "focus", "session"):
            answer = self._today_answer(athlete, program)
        elif self._matches(text, "bench", "pause", "leg drive", "touch point"):
            answer = self._lift_answer(athlete, program, "bench")
        elif self._matches(text, "squat", "hole", "brace", "quad"):
            answer = self._lift_answer(athlete, program, "squat")
        elif self._matches(text, "deadlift", "pull", "hinge", "back fatigue"):
            answer = self._lift_answer(athlete, program, "deadlift")
        elif self._matches(text, "fatigue", "recovery", "tired", "beat up"):
            answer = self._fatigue_answer(athlete, program)
        elif self._matches(text, "weak", "weakness", "sticking point", "limiter"):
            answer = self._weakness_answer(program)
        elif self._matches(text, "week", "block", "recap", "phase", "peak", "pivot", "taper"):
            answer = self._block_answer(program)
        elif self._matches(text, "progress", "progressing", "going"):
            answer = self._progress_answer(athlete, program)
        else:
            answer = self._general_answer(athlete, program)

        return ChatReply(
            answer=answer,
            suggested_questions=self._suggested_questions(program),
        )

    @staticmethod
    def _normalize(message: str) -> str:
        lowered = message.lower().strip()
        return re.sub(r"\s+", " ", lowered)

    @staticmethod
    def _matches(text: str, *keywords: str) -> bool:
        return any(keyword in text for keyword in keywords)

    def _today_answer(self, athlete: AthleteProfile, program: ProgramOverview) -> str:
        first_week = program.weeks[0]
        first_day = first_week.days[0]
        top_exercises = ", ".join(exercise.name for exercise in first_day.exercises[:3])
        return (
            f"Right now the block is organized as a {program.block_type.replace('_', ' ')} phase with a main focus on "
            f"{program.block_focus.lower()}. The first published day is {first_week.label} {first_day.day_label}, which centers on "
            f"{first_day.focus.lower()} and starts with {top_exercises}. The main coaching goal today is to keep the work clean enough "
            f"that the next exposure still fits the block instead of forcing progress from one session."
        )

    def _lift_answer(self, athlete: AthleteProfile, program: ProgramOverview, lift_name: str) -> str:
        weaker_lift = self._weakest_lift(athlete)
        limiter = self._best_limiter(program, lift_name)

        if lift_name == "bench":
            emphasis = (
                "Bench should usually move best through repeated quality exposures, cleaner pauses, and enough triceps or chest support "
                "to match the actual sticking point."
            )
        elif lift_name == "squat":
            emphasis = (
                "Squat should be judged by whether positions stay clean out of the hole and whether the block is building the exact weak range, "
                "not by chasing another random hard top set."
            )
        else:
            emphasis = (
                "Deadlift is often the biggest fatigue lever, so good coaching usually means keeping the productive heavy work while trimming the "
                "hinge stress that is not paying you back."
            )

        if weaker_lift == lift_name:
            emphasis += f" For this athlete, {lift_name} is comparatively the lift that needs the most attention right now."

        if limiter:
            emphasis += f" The current block is already aiming at {limiter.lower()}."

        return emphasis

    def _change_answer(self, program: ProgramOverview) -> str:
        first_note = program.progression_notes[0] if program.progression_notes else ""
        return (
            f"The next workouts change because the block is not just repeating weeks blindly. This block is a "
            f"{program.block_type.replace('_', ' ')} block with a focus on {program.block_focus.lower()}, so exercise choice, volume, and intensity "
            f"should move in service of that goal. {first_note}"
        )

    def _fatigue_answer(self, athlete: AthleteProfile, program: ProgramOverview) -> str:
        notes = " ".join([athlete.notes, *athlete.constraints]).lower()
        if "back" in notes or "fatigue" in notes:
            return (
                "Recovery should be managed by cutting the fatigue that is least useful first, not by panicking and changing the whole plan. "
                "Because lower-back or fatigue sensitivity is already present in the athlete notes, the block should keep productive work for the weak area "
                "while avoiding extra hinge stress that does not carry over."
            )
        return (
            "Recovery should be judged over the whole week and block, not from one hard day. The coaching move is usually to keep the main lift exposure in place "
            "and reduce the fatigue that is least connected to the current block focus."
        )

    def _weakness_answer(self, program: ProgramOverview) -> str:
        limiter = ", ".join(program.target_limiters[:2]) if program.target_limiters else "general strength accumulation"
        return (
            f"The current block is built around {limiter.lower()}. That means the useful question is not only 'what is weak?' but also "
            f"'which variations and loading patterns give that weak point enough exposure without burying recovery?'."
        )

    def _block_answer(self, program: ProgramOverview) -> str:
        week_labels = ", ".join(week.label for week in program.weeks)
        return (
            f"This block is a {program.block_type.replace('_', ' ')} phase with the sequence {week_labels}. The structure matters because "
            "the block should balance phase-specific organization with the actual weak point it is trying to improve."
        )

    def _progress_answer(self, athlete: AthleteProfile, program: ProgramOverview) -> str:
        weaker_lift = self._weakest_lift(athlete)
        return (
            f"Progress should be read against the purpose of the block, not just against whether one session felt hard. Right now the block is trying to move "
            f"{program.block_focus.lower()}, and the lift most likely to need extra attention is {weaker_lift}. If the work stays specific to that goal, the next block can push harder from a better base."
        )

    def _general_answer(self, athlete: AthleteProfile, program: ProgramOverview) -> str:
        return (
            f"This athlete is on a {program.split} built as a {program.block_type.replace('_', ' ')} block with a focus on {program.block_focus.lower()}. "
            "The useful coaching job is to explain what the block is trying to improve, why the week is organized that way, and what to focus on next without treating the whole plan like a black box."
        )

    @staticmethod
    def _weakest_lift(athlete: AthleteProfile) -> str:
        squat = max(athlete.lift_numbers.squat_kg, 1.0)
        bench = max(athlete.lift_numbers.bench_kg, 1.0)
        deadlift = max(athlete.lift_numbers.deadlift_kg, 1.0)

        bench_ratio = bench / squat
        squat_ratio = squat / deadlift
        deadlift_ratio = deadlift / squat

        if bench_ratio < 0.58:
            return "bench"
        if squat_ratio < 0.78:
            return "squat"
        if deadlift_ratio < 1.08:
            return "deadlift"
        return "bench"

    @staticmethod
    def _best_limiter(program: ProgramOverview, lift_name: str) -> str | None:
        lift_aliases = {
            "bench": ("bench", "off chest", "lockout", "leg-drive"),
            "squat": ("squat", "hole", "quad", "knee"),
            "deadlift": ("deadlift", "floor", "lockout", "posterior-chain"),
        }
        aliases = lift_aliases[lift_name]
        for limiter in program.target_limiters:
            lowered = limiter.lower()
            if any(alias in lowered for alias in aliases):
                return limiter
        return None

    def _suggested_questions(self, program: ProgramOverview) -> list[str]:
        lift_question = "How is my bench progressing?"
        if any("squat" in limiter.lower() for limiter in program.target_limiters):
            lift_question = "How is my squat progressing?"
        elif any("deadlift" in limiter.lower() for limiter in program.target_limiters):
            lift_question = "How is my deadlift progressing?"

        return [
            "What should I focus on today?",
            "Why did the next workout change?",
            "What weakness is this block trying to improve?",
            lift_question,
        ]
