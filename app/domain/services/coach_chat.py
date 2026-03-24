import re

from app.domain.models.athlete import AthleteProfile
from app.domain.models.coaching import ChatReply
from app.domain.models.program import ProgramOverview


class CoachChatService:
    def __init__(self, llm_chat_client: object | None = None) -> None:
        self._llm_chat_client = llm_chat_client

    def reply(self, athlete: AthleteProfile, program: ProgramOverview, message: str) -> ChatReply:
        text = self._normalize(message)
        intent = self._infer_intent(text)

        if intent == "cues":
            answer = self._cue_answer(athlete, program, self._infer_lift(text, athlete))
        elif intent == "change":
            answer = self._change_answer(program)
        elif intent == "today":
            answer = self._today_answer(athlete, program)
        elif intent == "bench":
            answer = self._lift_answer(athlete, program, "bench")
        elif intent == "squat":
            answer = self._lift_answer(athlete, program, "squat")
        elif intent == "deadlift":
            answer = self._lift_answer(athlete, program, "deadlift")
        elif intent == "fatigue":
            answer = self._fatigue_answer(athlete, program)
        elif intent == "weakness":
            answer = self._weakness_answer(program)
        elif intent == "block":
            answer = self._block_answer(program)
        elif intent == "progress":
            answer = self._progress_answer(athlete, program)
        else:
            answer = self._general_answer(athlete, program)

        llm_answer = self._llm_answer(
            athlete=athlete,
            program=program,
            message=message,
            fallback_answer=answer,
            intent=intent,
        )
        if llm_answer:
            answer = llm_answer

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

    def _infer_intent(self, text: str) -> str:
        if self._matches(text, "cue", "cues", "pointer", "pointers", "technique"):
            return "cues"
        if self._matches(text, "why", "change", "next week", "next workout", "adjust"):
            return "change"
        if self._matches(text, "today", "focus", "session"):
            return "today"
        if self._matches(text, "bench", "pause", "leg drive", "touch point"):
            return "bench"
        if self._matches(text, "squat", "hole", "brace", "quad", "knee"):
            return "squat"
        if self._matches(text, "deadlift", "pull", "hinge", "back fatigue", "wedge", "lockout"):
            return "deadlift"
        if self._matches(text, "fatigue", "recovery", "tired", "beat up"):
            return "fatigue"
        if self._matches(text, "weak", "weakness", "sticking point", "limiter"):
            return "weakness"
        if self._matches(text, "week", "block", "recap", "phase", "peak", "pivot", "taper"):
            return "block"
        if self._matches(text, "progress", "progressing", "going"):
            return "progress"
        return "general"

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

    def _cue_answer(self, athlete: AthleteProfile, program: ProgramOverview, lift_name: str) -> str:
        notes = " ".join([athlete.notes, *athlete.constraints]).lower()
        limiter = self._best_limiter(program, lift_name)
        if lift_name == "bench":
            cues = [
                "Set the upper back before the handoff so the chest stays high and the touch point stays repeatable.",
                "Start leg drive before the press so force transfers into the bar instead of arriving late.",
                "Keep the forearms stacked under the bar so the press stays efficient through the sticking point.",
            ]
            if "off chest" in notes or "off the chest" in notes:
                cues[2] = "Stay patient at the touch and keep the bar path tight so the first inches off the chest do not leak force."
            why = "Bench cues matter because cleaner setup, touch position, and pressure transfer usually improve carryover more than just forcing harder reps."
        elif lift_name == "squat":
            cues = [
                "Brace before the descent and keep pressure through the full foot so the bar stays over the mid-foot.",
                "Let the knees and hips break together so you do not dump forward out of the bottom.",
                "Drive the upper back into the bar as you stand so the torso and hips rise together.",
            ]
            if "knee" in notes:
                cues[1] = "Keep the knees tracking over the foot on the way down and out of the hole so position does not collapse under load."
            if "hips shoot" in notes or "out of the hole" in notes:
                cues[2] = "Push evenly through the floor so the chest and hips rise together instead of the hips shooting up first."
            why = "Squat cues matter because the lift usually improves when balance and position stay clean through the hard range, not when you just grind harder."
        else:
            cues = [
                "Set the lats before the pull so the bar stays close instead of drifting away.",
                "Build the wedge first and then push the floor away instead of yanking the bar loose.",
                "Stay over the bar long enough that the lockout finishes from position, not from a chase forward.",
            ]
            if "lockout" in notes or "at knee" in notes:
                cues[2] = "Keep the bar pinned to you past the knee so the finish is a strong lockout, not a drift away from the body."
            why = "Deadlift cues matter because the pull is usually best when the start is patient, the bar stays close, and the hardest range is attacked from a stable setup."

        limiter_text = f" The current block is trying to improve {limiter.lower()}." if limiter else ""
        return f"{lift_name.capitalize()} cues should stay specific to the lift you asked about.{limiter_text} Focus on these cues: {' '.join(cues)} Why: {why}"

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

    def _llm_answer(
        self,
        athlete: AthleteProfile,
        program: ProgramOverview,
        message: str,
        fallback_answer: str,
        intent: str,
    ) -> str | None:
        if self._llm_chat_client is None:
            return None

        generate = getattr(self._llm_chat_client, "generate", None)
        if not callable(generate):
            return None

        if intent == "cues":
            return None

        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(athlete, program, message, fallback_answer, intent)
        response = generate(system_prompt, user_prompt)
        if not isinstance(response, str):
            return None
        cleaned = response.strip()
        return cleaned or None

    @staticmethod
    def _build_system_prompt() -> str:
        return (
            "You are myPowerCoach, a powerlifting coach chatbot. "
            "Answer like a good coach: specific, practical, and grounded in the athlete context provided. "
            "Do not invent data that is not in the context. "
            "Keep the answer under 140 words, avoid generic motivational filler, and explain the training logic clearly. "
            "Directly answer the user request instead of drifting into a general overview of the lift. "
            "If the athlete asks for cues, give concrete execution pointers with a short why, not general lift commentary. "
            "If the athlete asks about today's work, focus on the current block and first upcoming session. "
            "If the context is incomplete, say what is known and give the most reasonable coaching answer from that context."
        )

    def _build_user_prompt(
        self,
        athlete: AthleteProfile,
        program: ProgramOverview,
        message: str,
        fallback_answer: str,
        intent: str,
    ) -> str:
        first_week = program.weeks[0]
        first_day = first_week.days[0]
        day_summary = ", ".join(
            f"{exercise.name} {exercise.sets}x{exercise.reps} @ RPE {exercise.target_rpe}"
            for exercise in first_day.exercises[:4]
        )
        limiter_summary = ", ".join(program.target_limiters[:3]) if program.target_limiters else "general strength accumulation"
        progression_notes = " ".join(program.progression_notes[:3])

        return (
            f"Athlete: {athlete.name}, {athlete.age} years old, {athlete.bodyweight_kg} kg, "
            f"{athlete.training_days_per_week} training days per week, goal: {athlete.primary_goal}, equipment: {athlete.equipment}.\n"
            f"PRs: squat {athlete.lift_numbers.squat_kg} kg, bench {athlete.lift_numbers.bench_kg} kg, deadlift {athlete.lift_numbers.deadlift_kg} kg.\n"
            f"Notes/constraints: {athlete.notes or 'none'}. Extra constraints: {', '.join(athlete.constraints) if athlete.constraints else 'none'}.\n"
            f"Program: {program.block_type.replace('_', ' ')} block, focus {program.block_focus}, target limiters {limiter_summary}.\n"
            f"Current week flow: {', '.join(week.label for week in program.weeks)}.\n"
            f"First upcoming session: {first_week.label} {first_day.day_label}, focus {first_day.focus}. Exercises: {day_summary}.\n"
            f"Programming notes: {progression_notes}\n"
            f"Detected intent: {intent}\n"
            f"Rule-based coaching baseline answer: {fallback_answer}\n"
            f"User question: {message}\n"
            "Write the final answer for the athlete."
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

    def _infer_lift(self, text: str, athlete: AthleteProfile) -> str:
        if self._matches(text, "bench", "press", "leg drive", "touch point"):
            return "bench"
        if self._matches(text, "squat", "hole", "brace", "quad", "knee"):
            return "squat"
        if self._matches(text, "deadlift", "pull", "hinge", "wedge", "lockout"):
            return "deadlift"
        return self._weakest_lift(athlete)

    def _suggested_questions(self, program: ProgramOverview) -> list[str]:
        lift_question = "How is my bench progressing?"
        if any("squat" in limiter.lower() for limiter in program.target_limiters):
            lift_question = "How is my squat progressing?"
        elif any("deadlift" in limiter.lower() for limiter in program.target_limiters):
            lift_question = "How is my deadlift progressing?"

        return [
            "What should I focus on today?",
            f"What are my {lift_question.split()[2].lower()} cues today?" if lift_question.startswith("How is my") else "What are my main lift cues today?",
            "Why did the next workout change?",
            "What weakness is this block trying to improve?",
            lift_question,
        ]
