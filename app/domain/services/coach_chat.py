from app.domain.models.athlete import AthleteProfile
from app.domain.models.coaching import ChatReply


class CoachChatService:
    def reply(self, athlete: AthleteProfile | None, message: str) -> ChatReply:
        text = message.lower()
        athlete_name = athlete.name if athlete else "your training"

        if "bench" in text:
            answer = (
                f"For {athlete_name}, bench should usually be the easiest lift to push when recovery is good. "
                "The system would prefer adding touchpoints before forcing a big intensity jump."
            )
        elif "squat" in text:
            answer = (
                "Squat feedback should connect technique and programming. "
                "If bottom-end force production looks weak, the fix is usually positional squat work plus quad volume."
            )
        elif "deadlift" in text or "pull" in text:
            answer = (
                "Deadlift is often the biggest fatigue lever. "
                "A strong coaching response keeps meaningful heavy exposure while trimming fatigue that is not producing progress."
            )
        elif "today" in text or "day" in text or "fatigue" in text:
            answer = (
                "Daily feedback should translate how the session felt into a next action, "
                "not just show a score with no coaching meaning."
            )
        else:
            answer = (
                "The coach chatbot should explain what your training means, why the program changed, "
                "and what to focus on next in plain language."
            )

        return ChatReply(
            answer=answer,
            suggested_questions=[
                "How is my bench progressing?",
                "Why did the next week change?",
                "What should I focus on in squat today?",
            ],
        )
