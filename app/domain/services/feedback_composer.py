from app.domain.models.coaching import DailyFeedback, ExerciseFeedback


class FeedbackComposer:
    def compose_daily_feedback(
        self,
        session_quality: str,
        fatigue_level: str,
        notes: str | None,
        exercises: list[dict] | None = None,
        video_name: str | None = None,
    ) -> DailyFeedback:
        if session_quality == "great" and fatigue_level != "high":
            feedback = DailyFeedback(
                status="Progression supported",
                summary="Training landed well today, so the current progression can keep moving without forced changes.",
                next_adjustment="Keep the next session on plan and look for another clean exposure before increasing stress.",
                cues=[
                    "Keep technique consistent while the load is moving well.",
                    "Let bench volume rise before making an aggressive intensity jump.",
                ],
                improvements=[
                    "Stay honest with top-set RPE so the next progression stays accurate.",
                ],
            )
        elif fatigue_level == "high" or session_quality == "rough":
            feedback = DailyFeedback(
                status="Fatigue watch",
                summary="The day suggests recovery may be getting tight, so the next useful move is to protect momentum rather than add more stress.",
                next_adjustment="Trim the least useful fatigue first, especially from heavy deadlift backoff work.",
                cues=[
                    "Stay braced and reduce technical slop as fatigue rises.",
                    "Do not chase load if bar speed and positions are degrading.",
                ],
                improvements=[
                    "Backoff work may need to come down before main-lift exposure changes.",
                ],
            )
        else:
            feedback = DailyFeedback(
                status="Stable",
                summary="The session looks productive enough to stay on course while watching for repeated fatigue patterns.",
                next_adjustment="Hold the plan steady and reassess after the next one or two sessions.",
                cues=[
                    "Keep today's execution clean and repeatable.",
                    "Use the logged data to confirm whether the current block is still calibrated well.",
                ],
                improvements=[
                    "Look for one or two small technique wins instead of overhauling the whole session.",
                ],
            )

        if notes:
            feedback.summary = f"{feedback.summary} Athlete note: {notes}"
        feedback.exercise_feedback = self._build_exercise_feedback(exercises or [])
        if video_name:
            feedback.video_feedback = (
                f"Video '{video_name}' was attached for review. "
                "Use it to check positions, sticking points, and whether the next cue should be technical or programming-based."
            )
        return feedback

    @staticmethod
    def _build_exercise_feedback(exercises: list[dict]) -> list[ExerciseFeedback]:
        feedback_items: list[ExerciseFeedback] = []
        for exercise in exercises:
            sets = exercise.get("sets", [])
            below_plan = False
            above_plan = False
            if sets:
                planned_sets = len(sets)
                planned_reps = int(sets[0].get("planned_reps", 0))
                planned_weight = float(sets[0].get("planned_weight_kg", 0))
                completed_sets = sum(1 for set_entry in sets if int(set_entry.get("completed_reps", 0)) > 0)
                completed_reps = sum(int(set_entry.get("completed_reps", 0)) for set_entry in sets)
                completed_weight = sum(float(set_entry.get("completed_weight_kg", 0)) for set_entry in sets) / max(len(sets), 1)
                below_plan = any(
                    int(set_entry.get("completed_reps", 0)) < int(set_entry.get("planned_reps", 0))
                    or float(set_entry.get("completed_weight_kg", 0)) < float(set_entry.get("planned_weight_kg", 0))
                    for set_entry in sets
                )
                above_plan = any(
                    float(set_entry.get("completed_weight_kg", 0)) > float(set_entry.get("planned_weight_kg", 0))
                    for set_entry in sets
                )
            else:
                planned_sets = int(exercise.get("planned_sets", 0))
                planned_reps = int(exercise.get("planned_reps", 0))
                planned_weight = float(exercise.get("planned_weight_kg", 0))
                completed_sets = int(exercise.get("completed_sets", 0))
                completed_reps = int(exercise.get("completed_reps", 0))
                completed_weight = float(exercise.get("completed_weight_kg", 0))
                below_plan = completed_reps < planned_reps or completed_sets < planned_sets
                above_plan = completed_weight > planned_weight

            if above_plan:
                note = "You exceeded the planned load. Good sign if technique stayed tight."
            elif below_plan:
                note = "You fell short of plan. Check fatigue, setup quality, and whether the prescription ran too hot."
            else:
                note = "Execution matched the plan closely. This is useful calibration data."

            feedback_items.append(
                ExerciseFeedback(
                    exercise_name=str(exercise.get("exercise_name", "Exercise")),
                    planned_sets=planned_sets,
                    planned_reps=planned_reps,
                    planned_weight_kg=planned_weight,
                    completed_sets=completed_sets,
                    completed_reps=completed_reps,
                    completed_weight_kg=completed_weight,
                    note=note,
                )
            )
        return feedback_items
