from app.domain.models.video_analysis import (
    DeadliftSignalProfile,
    DeadliftVideoAnalysis,
    MovementIssue,
    OverlayPlan,
    VideoSubmission,
    WeakPointInference,
)


class DeadliftVideoAnalyzer:
    def analyze(
        self,
        submission: VideoSubmission,
        signals: DeadliftSignalProfile,
    ) -> DeadliftVideoAnalysis:
        style = submission.style_variant or "conventional"
        sticking_point = self._classify_sticking_point(signals.sticking_height_ratio)
        movement_issues = self._build_movement_issues(signals, style)
        weak_points = self._infer_weak_points(signals, style, sticking_point, movement_issues)
        cues = self._build_cues(style, sticking_point, movement_issues)
        programming_adjustments = self._build_programming_adjustments(style, sticking_point, movement_issues)
        summary = self._build_summary(submission, style, sticking_point, movement_issues, weak_points)

        return DeadliftVideoAnalysis(
            status="Deadlift analysis ready",
            summary=summary,
            sticking_point=sticking_point,
            style=style,
            movement_issues=movement_issues,
            weak_points=weak_points,
            cues=cues,
            programming_adjustments=programming_adjustments,
            overlay_plan=OverlayPlan(
                joints_to_draw=["shoulder", "hip", "knee", "ankle", "midfoot", "barbell"],
                highlight_frames=[
                    signals.setup_frame,
                    signals.break_from_floor_frame,
                    signals.sticking_frame,
                    signals.lockout_frame,
                ],
                draw_bar_path=True,
                reference_profile=f"legal-powerlifting-deadlift-{style}",
            ),
            reference_notes=[
                "Judge the pull against the chosen style, because conventional and sumo use different hip, knee, and torso strategies.",
                "Use bar, shoulder, hip, knee, ankle, and midfoot overlays to see whether the bar stays close and the torso stays organized.",
                "Treat the sticking point as the hardest region from the floor to lockout where bar speed drops and the lift risks stalling.",
            ],
        )

    @staticmethod
    def _classify_sticking_point(sticking_height_ratio: float) -> str:
        if sticking_height_ratio <= 0.2:
            return "off the floor"
        if sticking_height_ratio <= 0.58:
            return "at the knee"
        return "lockout"

    def _build_movement_issues(
        self,
        signals: DeadliftSignalProfile,
        style: str,
    ) -> list[MovementIssue]:
        issues: list[MovementIssue] = []

        if signals.bar_path_deviation_cm > 7.5 or signals.bar_to_shin_distance_cm > 4.5:
            issues.append(
                MovementIssue(
                    code="bar_drift",
                    label="Bar drifts away from the body",
                    severity="moderate" if signals.bar_path_deviation_cm <= 10 else "high",
                    evidence=(
                        f"Bar-path deviation {signals.bar_path_deviation_cm:.1f} cm and bar-to-shin distance "
                        f"{signals.bar_to_shin_distance_cm:.1f} cm suggest the pull is losing proximity."
                    ),
                )
            )

        if signals.lat_engagement_score < 0.55:
            issues.append(
                MovementIssue(
                    code="lat_slack",
                    label="Lats are not holding the bar path tight",
                    severity=self._severity_from_score(signals.lat_engagement_score),
                    evidence=(
                        f"Lat-engagement score {signals.lat_engagement_score:.2f} suggests the bar is not being pulled back into the body cleanly."
                    ),
                )
            )

        if signals.foot_balance_score < 0.55:
            issues.append(
                MovementIssue(
                    code="balance_shift",
                    label="Pressure shifts away from a stable midfoot pull",
                    severity=self._severity_from_score(signals.foot_balance_score),
                    evidence=(
                        f"Foot-balance score {signals.foot_balance_score:.2f} suggests the pull starts or finishes without stable floor pressure."
                    ),
                )
            )

        if signals.asymmetry_shift_cm > 3.0:
            issues.append(
                MovementIssue(
                    code="asymmetry",
                    label="Left-right shift is noticeable",
                    severity="moderate" if signals.asymmetry_shift_cm <= 5 else "high",
                    evidence=(
                        f"Asymmetry shift of {signals.asymmetry_shift_cm:.1f} cm suggests one side is taking more of the pull."
                    ),
                )
            )

        if style == "conventional":
            if signals.hip_rise_score < 0.5 or signals.shoulder_ahead_bar_score < 0.52:
                issues.append(
                    MovementIssue(
                        code="hips_rise_fast",
                        label="Hips rise too fast before the bar breaks cleanly",
                        severity=self._severity_from_score(min(signals.hip_rise_score, signals.shoulder_ahead_bar_score)),
                        evidence=(
                            f"Hip-rise score {signals.hip_rise_score:.2f} and shoulder-over-bar score "
                            f"{signals.shoulder_ahead_bar_score:.2f} suggest you are turning the start into a stiff-leg position."
                        ),
                    )
                )
        else:
            if signals.knee_track_score < 0.55:
                issues.append(
                    MovementIssue(
                        code="knees_close",
                        label="Knees lose their line in the sumo start",
                        severity=self._severity_from_score(signals.knee_track_score),
                        evidence=(
                            f"Knee-track score {signals.knee_track_score:.2f} suggests the knees are not staying out and letting the torso stay organized."
                        ),
                    )
                )
            if signals.hip_rise_score < 0.52:
                issues.append(
                    MovementIssue(
                        code="hips_pop_up",
                        label="Hips pop up and steal the sumo wedge",
                        severity=self._severity_from_score(signals.hip_rise_score),
                        evidence=(
                            f"Hip-rise score {signals.hip_rise_score:.2f} suggests you lose the wedged start position and end up chasing the pull."
                        ),
                    )
                )

        if signals.lockout_stability_score < 0.55:
            issues.append(
                MovementIssue(
                    code="lockout_soft",
                    label="Lockout position softens near the top",
                    severity=self._severity_from_score(signals.lockout_stability_score),
                    evidence=(
                        f"Lockout-stability score {signals.lockout_stability_score:.2f} suggests the hips and shoulders are not finishing together cleanly."
                    ),
                )
            )

        return issues

    def _infer_weak_points(
        self,
        signals: DeadliftSignalProfile,
        style: str,
        sticking_point: str,
        movement_issues: list[MovementIssue],
    ) -> list[WeakPointInference]:
        issue_codes = {issue.code for issue in movement_issues}
        weak_points: list[WeakPointInference] = []

        if sticking_point == "off the floor":
            if style == "conventional" and "hips_rise_fast" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Start position strength and wedge discipline",
                        confidence=0.83,
                        rationale="The conventional pull is losing position before the bar clears the floor, which points to a weak or rushed wedge rather than only a pure strength limit.",
                    )
                )
            if style == "sumo" and ("knees_close" in issue_codes or "hips_pop_up" in issue_codes):
                weak_points.append(
                    WeakPointInference(
                        label="Sumo wedge and leg drive off the floor",
                        confidence=0.84,
                        rationale="The sumo start is losing knee position or hip height early, so the bar has to fight the floor without the intended leg-driven wedge.",
                    )
                )
            if "bar_drift" in issue_codes or "lat_slack" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Bar proximity and lat tension from the floor",
                        confidence=0.76,
                        rationale="The bar is not staying close enough at the hardest early range, which makes the floor break much more expensive.",
                    )
                )

        if sticking_point == "at the knee":
            weak_points.append(
                WeakPointInference(
                    label="Mid-pull position retention",
                    confidence=0.74,
                    rationale="The pull gets moving but loses speed at the knee, which usually means the torso-bar relationship is not being held through transition.",
                )
            )

        if sticking_point == "lockout":
            weak_points.append(
                WeakPointInference(
                    label="Lockout finish and hip extension timing",
                    confidence=0.68,
                    rationale="The bar survives the floor and knee but still softens high in the pull, which points more toward finishing posture and lockout timing.",
                )
            )

        if not weak_points:
            weak_points.append(
                WeakPointInference(
                    label="General deadlift coordination",
                    confidence=0.5,
                    rationale="The current signals show leakage, but not one dominant deadlift weak point clearly enough yet.",
                )
            )

        return weak_points

    def _build_cues(
        self,
        style: str,
        sticking_point: str,
        movement_issues: list[MovementIssue],
    ) -> list[str]:
        issue_codes = {issue.code for issue in movement_issues}

        if style == "sumo":
            cues = [
                "Wedge into the floor first, then push the floor apart instead of yanking the bar with the hips high.",
                "Keep the bar close and let the chest and hips rise together out of the floor.",
            ]
            if "knees_close" in issue_codes:
                cues.append("Keep the knees out so the torso has space and the bar can travel straight up.")
            if "hips_pop_up" in issue_codes:
                cues.append("Do not let the hips pop up before the plates leave the floor or you lose the sumo wedge.")
        else:
            cues = [
                "Pull the slack out, stay over the bar, and push the floor away before the hips jump.",
                "Keep the bar pinned to the body so the pull does not drift forward.",
            ]
            if "hips_rise_fast" in issue_codes:
                cues.append("Let the chest and hips move together so the start does not turn into a stiff-leg pull.")

        if "lat_slack" in issue_codes:
            cues.append("Squeeze the lats hard before the break so the bar stays back into you from the floor.")
        if "lockout_soft" in issue_codes:
            cues.append("Finish by bringing the hips through into a stacked lockout, not by leaning back late.")
        if sticking_point == "off the floor":
            cues.append("Treat the floor break as the key moment: brace, wedge, and make the first inches clean.")

        return cues[:5]

    @staticmethod
    def _build_programming_adjustments(
        style: str,
        sticking_point: str,
        movement_issues: list[MovementIssue],
    ) -> list[str]:
        issue_codes = {issue.code for issue in movement_issues}
        adjustments: list[str] = []

        if sticking_point == "off the floor":
            if style == "sumo":
                adjustments.append("Bias one deadlift slot toward paused sumo or wedge-focused sumo singles in the RPE 6.5-8 range.")
            else:
                adjustments.append("Bias one deadlift slot toward paused conventional or deficit pulls in the RPE 6.5-8 range.")
        if sticking_point == "at the knee":
            adjustments.append("Use a variation that reinforces mid-pull position, such as paused pulls below the knee.")
        if sticking_point == "lockout":
            adjustments.append("Keep one accessory slot for Romanian deadlifts or rack/pin work to reinforce the finish.")

        if "bar_drift" in issue_codes or "lat_slack" in issue_codes:
            adjustments.append("Keep more submaximal technique pulls where the bar path can stay tight before pushing load up.")
        if style == "sumo" and ("knees_close" in issue_codes or "hips_pop_up" in issue_codes):
            adjustments.append("Use sumo-specific setup practice and adductor-aware work so the start position holds under load.")
        if style == "conventional" and "hips_rise_fast" in issue_codes:
            adjustments.append("Add conventional start-position work and keep fatigue low enough that the wedge does not disappear.")
        if "lockout_soft" in issue_codes:
            adjustments.append("Add upper-back and hip-extension support work if the bar keeps softening near lockout.")

        if not adjustments:
            adjustments.append("Hold the current deadlift structure steady and collect more pulls before changing the block.")

        return adjustments[:4]

    @staticmethod
    def _build_summary(
        submission: VideoSubmission,
        style: str,
        sticking_point: str,
        movement_issues: list[MovementIssue],
        weak_points: list[WeakPointInference],
    ) -> str:
        top_issue = movement_issues[0].label if movement_issues else "no dominant movement fault"
        top_weak_point = weak_points[0].label if weak_points else "general deadlift coordination"
        return (
            f"This {submission.lift_kg:.1f} kg {style} deadlift at RPE {submission.completed_rpe:.1f} shows the main sticking point "
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
