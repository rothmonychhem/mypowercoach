from app.domain.models.coaching import DailyFeedback


class FeedbackComposer:
    def compose_daily_feedback(self, session_quality: str, fatigue_level: str, notes: str | None) -> DailyFeedback:
        if session_quality == "great" and fatigue_level != "high":
            feedback = DailyFeedback(
                status="Progression supported",
                summary="Training landed well today, so the current progression can keep moving without forced changes.",
                next_adjustment="Keep the next session on plan and look for another clean exposure before increasing stress.",
            )
        elif fatigue_level == "high" or session_quality == "rough":
            feedback = DailyFeedback(
                status="Fatigue watch",
                summary="The day suggests recovery may be getting tight, so the next useful move is to protect momentum rather than add more stress.",
                next_adjustment="Trim the least useful fatigue first, especially from heavy deadlift backoff work.",
            )
        else:
            feedback = DailyFeedback(
                status="Stable",
                summary="The session looks productive enough to stay on course while watching for repeated fatigue patterns.",
                next_adjustment="Hold the plan steady and reassess after the next one or two sessions.",
            )

        if notes:
            feedback.summary = f"{feedback.summary} Athlete note: {notes}"
        return feedback
