from app.domain.models.video_analysis import (
    MovementIssue,
    OverlayPlan,
    SquatSignalProfile,
    SquatVideoAnalysis,
    VideoSubmission,
    WeakPointInference,
)


class SquatVideoAnalyzer:
    def analyze(
        self,
        submission: VideoSubmission,
        signals: SquatSignalProfile,
    ) -> SquatVideoAnalysis:
        sticking_point = self._classify_sticking_point(signals.sticking_height_ratio)
        movement_issues = self._build_movement_issues(signals)
        weak_points = self._infer_weak_points(signals, sticking_point, movement_issues)
        cues = self._build_cues(movement_issues, sticking_point)
        programming_adjustments = self._build_programming_adjustments(movement_issues, sticking_point)
        summary = self._build_summary(submission, sticking_point, movement_issues, weak_points)

        return SquatVideoAnalysis(
            status="Squat analysis ready",
            summary=summary,
            sticking_point=sticking_point,
            movement_issues=movement_issues,
            weak_points=weak_points,
            cues=cues,
            programming_adjustments=programming_adjustments,
            overlay_plan=OverlayPlan(
                joints_to_draw=["shoulder", "hip", "knee", "ankle", "midfoot", "barbell"],
                highlight_frames=[
                    signals.descent_start_frame,
                    signals.bottom_frame,
                    signals.sticking_frame,
                    signals.lockout_frame,
                ],
                draw_bar_path=True,
                reference_profile="legal-powerlifting-squat-self-selected-stance",
            ),
            reference_notes=[
                "Judge squat technique against legal depth and stable bar-over-midfoot mechanics, not one forced stance width.",
                "Use hip, knee, ankle, shoulder, and bar path overlays to see whether the ascent preserves torso position and balance.",
                "Treat the sticking point as the hardest part of the ascent after the bottom where bar speed drops and the rep risks folding or stalling.",
            ],
        )

    @staticmethod
    def _classify_sticking_point(sticking_height_ratio: float) -> str:
        if sticking_height_ratio <= 0.18:
            return "out of the hole"
        if sticking_height_ratio <= 0.45:
            return "just above parallel"
        return "high grind"

    def _build_movement_issues(self, signals: SquatSignalProfile) -> list[MovementIssue]:
        issues: list[MovementIssue] = []

        if signals.depth_margin_ratio < 0:
            issues.append(
                MovementIssue(
                    code="depth_short",
                    label="Depth is likely high",
                    severity="high",
                    evidence=(
                        f"Depth margin ratio {signals.depth_margin_ratio:.2f} suggests the hip crease may not pass below "
                        "the top of the knee cleanly."
                    ),
                )
            )

        if signals.hip_shoot_score < 0.48:
            issues.append(
                MovementIssue(
                    code="hips_shoot",
                    label="Hips shoot up early",
                    severity=self._severity_from_score(signals.hip_shoot_score),
                    evidence=(
                        f"Hip-shoot score {signals.hip_shoot_score:.2f} suggests the hips rise faster than the shoulders "
                        "as the rep leaves the bottom."
                    ),
                )
            )

        if signals.torso_angle_change_deg > 14 or signals.bracing_score < 0.55:
            issues.append(
                MovementIssue(
                    code="torso_collapse",
                    label="Torso angle collapses in the ascent",
                    severity="moderate" if signals.torso_angle_change_deg <= 20 else "high",
                    evidence=(
                        f"Torso angle change {signals.torso_angle_change_deg:.1f} degrees and bracing score "
                        f"{signals.bracing_score:.2f} suggest you lose the stacked torso coming out of the hole."
                    ),
                )
            )

        if signals.knee_collapse_score < 0.55:
            issues.append(
                MovementIssue(
                    code="knee_collapse",
                    label="Knees collapse inward",
                    severity=self._severity_from_score(signals.knee_collapse_score),
                    evidence=(
                        f"Knee-collapse score {signals.knee_collapse_score:.2f} suggests valgus or loss of knee tracking "
                        "under load."
                    ),
                )
            )

        if signals.bar_path_deviation_cm > 8.0 or signals.foot_pressure_shift_score < 0.55:
            issues.append(
                MovementIssue(
                    code="forward_shift",
                    label="Bar and pressure shift forward",
                    severity="moderate" if signals.bar_path_deviation_cm <= 11 else "high",
                    evidence=(
                        f"Bar-path deviation {signals.bar_path_deviation_cm:.1f} cm and pressure-shift score "
                        f"{signals.foot_pressure_shift_score:.2f} suggest the bar drifts away from the strongest line over midfoot."
                    ),
                )
            )

        if signals.left_right_shift_cm > 3.5:
            issues.append(
                MovementIssue(
                    code="asymmetry",
                    label="Left-right shift is noticeable",
                    severity="moderate" if signals.left_right_shift_cm <= 5.5 else "high",
                    evidence=(
                        f"Left-right shift of {signals.left_right_shift_cm:.1f} cm suggests the ascent is not symmetrical."
                    ),
                )
            )

        return issues

    def _infer_weak_points(
        self,
        signals: SquatSignalProfile,
        sticking_point: str,
        movement_issues: list[MovementIssue],
    ) -> list[WeakPointInference]:
        issue_codes = {issue.code for issue in movement_issues}
        weak_points: list[WeakPointInference] = []

        if sticking_point == "out of the hole":
            if "hips_shoot" in issue_codes or "torso_collapse" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Quad drive and bracing out of the hole",
                        confidence=0.84,
                        rationale="The rep slows immediately from the bottom and the hip-torso relationship suggests you lose posture instead of driving straight up.",
                    )
                )
            if "forward_shift" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Bottom-position balance and bar-over-midfoot control",
                        confidence=0.76,
                        rationale="The rep slows early while pressure and bar path drift forward, which usually makes the hole much harder to escape.",
                    )
                )

        if sticking_point == "just above parallel":
            weak_points.append(
                WeakPointInference(
                    label="Mid-range squat strength and position retention",
                    confidence=0.74,
                    rationale="The rep survives the hole but loses speed before the torso and hips are fully organized for the finish.",
                )
            )
            if "knee_collapse" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Hip stability and knee tracking under load",
                        confidence=0.71,
                        rationale="Knee position is leaking as the rep enters the hardest middle range, which costs force transfer.",
                    )
                )

        if sticking_point == "high grind":
            weak_points.append(
                WeakPointInference(
                    label="Top-end grind tolerance and lockout posture",
                    confidence=0.61,
                    rationale="The rep is mostly won from the bottom but still loses speed high in the ascent, which points more toward finish strength or fatigue tolerance.",
                )
            )

        if not weak_points:
            weak_points.append(
                WeakPointInference(
                    label="General squat coordination",
                    confidence=0.5,
                    rationale="The current signals show leakage, but not one dominant squat weak point cleanly enough yet.",
                )
            )

        return weak_points

    @staticmethod
    def _build_cues(
        movement_issues: list[MovementIssue],
        sticking_point: str,
    ) -> list[str]:
        issue_codes = {issue.code for issue in movement_issues}
        cues = [
            "Stay stacked over midfoot and drive the floor away instead of letting the chest and hips separate.",
            "Own the bottom position before the ascent so the first inches out of the hole stay organized.",
        ]

        if "hips_shoot" in issue_codes:
            cues.append("Push the shoulders and hips up together out of the hole instead of letting the hips win the race.")
        if "torso_collapse" in issue_codes:
            cues.append("Brace harder into the belt and keep the chest tall so the torso angle does not fold forward.")
        if "knee_collapse" in issue_codes:
            cues.append("Keep the knees tracking over the feet and keep pressure through the whole foot.")
        if "forward_shift" in issue_codes:
            cues.append("Keep the bar over midfoot and do not let pressure dump onto the toes at the bottom.")
        if "depth_short" in issue_codes:
            cues.append("Sit into a position that reaches clear depth without giving away your brace or balance.")
        if sticking_point == "out of the hole":
            cues.append("Treat the first third of the ascent as the money zone: brace hard, stay over midfoot, and drive straight up.")

        return cues[:5]

    @staticmethod
    def _build_programming_adjustments(
        movement_issues: list[MovementIssue],
        sticking_point: str,
    ) -> list[str]:
        issue_codes = {issue.code for issue in movement_issues}
        adjustments: list[str] = []

        if sticking_point == "out of the hole":
            adjustments.append("Bias one squat slot toward paused squat or pin squat work in the RPE 6.5-8 range to build force from the bottom.")
        if sticking_point == "just above parallel":
            adjustments.append("Keep a secondary squat variation that reinforces the mid-range, such as tempo squat or controlled high-bar work.")
        if sticking_point == "high grind":
            adjustments.append("Keep the main squat slot but trim fatigue if top-end grind is mostly a recovery problem rather than a technical one.")

        if "hips_shoot" in issue_codes or "torso_collapse" in issue_codes:
            adjustments.append("Add more bracing-sensitive squat work and keep some front-loaded or paused squat exposure in the block.")
        if "knee_collapse" in issue_codes:
            adjustments.append("Use single-leg work and controlled squat accessories that reinforce knee tracking and hip stability.")
        if "forward_shift" in issue_codes:
            adjustments.append("Reduce load jumps on squat until bar-over-midfoot consistency improves, then build intensity again.")
        if "depth_short" in issue_codes:
            adjustments.append("Use tempo or paused squats to rehearse legal depth without chasing load.")

        if not adjustments:
            adjustments.append("Hold the current squat structure steady and collect more reps before changing the block.")

        return adjustments[:4]

    @staticmethod
    def _build_summary(
        submission: VideoSubmission,
        sticking_point: str,
        movement_issues: list[MovementIssue],
        weak_points: list[WeakPointInference],
    ) -> str:
        top_issue = movement_issues[0].label if movement_issues else "no dominant movement fault"
        top_weak_point = weak_points[0].label if weak_points else "general squat coordination"
        return (
            f"This {submission.lift_kg:.1f} kg squat at RPE {submission.completed_rpe:.1f} shows the main sticking point "
            f"{sticking_point}. The strongest current signal is {top_issue.lower()}, and the likely improvement target is "
            f"{top_weak_point.lower()}."
        )

    @staticmethod
    def _severity_from_score(score: float) -> str:
        if score < 0.35:
            return "high"
        if score < 0.6:
            return "moderate"
        return "low"
