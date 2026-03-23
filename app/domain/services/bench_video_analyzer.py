from app.domain.models.video_analysis import (
    BenchSignalProfile,
    BenchVideoAnalysis,
    MovementIssue,
    OverlayPlan,
    VideoSubmission,
    WeakPointInference,
)


class BenchVideoAnalyzer:
    def analyze(
        self,
        submission: VideoSubmission,
        signals: BenchSignalProfile,
    ) -> BenchVideoAnalysis:
        sticking_point = self._classify_sticking_point(signals.sticking_height_ratio)
        movement_issues = self._build_movement_issues(signals)
        weak_points = self._infer_weak_points(signals, sticking_point, movement_issues)
        cues = self._build_cues(sticking_point, movement_issues, submission)
        programming_adjustments = self._build_programming_adjustments(sticking_point, movement_issues)
        summary = self._build_summary(submission, sticking_point, movement_issues, weak_points)

        return BenchVideoAnalysis(
            status="Bench analysis ready",
            summary=summary,
            sticking_point=sticking_point,
            movement_issues=movement_issues,
            weak_points=weak_points,
            cues=cues,
            programming_adjustments=programming_adjustments,
            overlay_plan=OverlayPlan(
                joints_to_draw=["shoulder", "elbow", "wrist", "hip", "knee", "ankle", "barbell"],
                highlight_frames=[
                    signals.touch_frame,
                    signals.press_frame,
                    signals.sticking_frame,
                    signals.lockout_frame,
                ],
                draw_bar_path=True,
                reference_profile="legal-self-selected-powerlifting-bench",
            ),
            reference_notes=[
                "Compare the lift to legal and repeatable powerlifting positions rather than a forced wide-grip template.",
                "Use shoulder, elbow, wrist, hip, knee, ankle, and bar path overlays to judge timing and stacked positions.",
                "Treat the sticking point as the hardest region after the press where bar speed drops and the rep risks stalling.",
            ],
        )

    @staticmethod
    def _classify_sticking_point(sticking_height_ratio: float) -> str:
        if sticking_height_ratio <= 0.22:
            return "off chest"
        if sticking_height_ratio <= 0.58:
            return "mid-range"
        return "lockout"

    def _build_movement_issues(self, signals: BenchSignalProfile) -> list[MovementIssue]:
        issues: list[MovementIssue] = []

        if signals.leg_drive_score < 0.48 or signals.heel_stability_score < 0.55:
            issues.append(
                MovementIssue(
                    code="leg_drive_timing",
                    label="Leg drive is not transferring cleanly",
                    severity=self._severity_from_score(min(signals.leg_drive_score, signals.heel_stability_score)),
                    evidence=(
                        f"Leg-drive score {signals.leg_drive_score:.2f} and heel-stability score "
                        f"{signals.heel_stability_score:.2f} suggest poor force transfer from the floor."
                    ),
                )
            )

        if signals.butt_contact_score < 0.55:
            issues.append(
                MovementIssue(
                    code="hip_stability",
                    label="Hip contact is getting unstable",
                    severity=self._severity_from_score(signals.butt_contact_score),
                    evidence=(
                        f"Butt-contact score {signals.butt_contact_score:.2f} suggests the press is trying to find "
                        "leg drive by shifting the pelvis instead of staying stacked."
                    ),
                )
            )

        if signals.bar_path_deviation_cm > 7.5 or signals.wrist_stack_score < 0.58:
            issues.append(
                MovementIssue(
                    code="bar_path_stack",
                    label="Bar path and forearm stack drift",
                    severity="moderate" if signals.bar_path_deviation_cm <= 10 else "high",
                    evidence=(
                        f"Bar-path deviation {signals.bar_path_deviation_cm:.1f} cm and wrist-stack score "
                        f"{signals.wrist_stack_score:.2f} suggest the bar is not staying in its strongest line."
                    ),
                )
            )

        if signals.elbow_flare_delta_deg > 16:
            issues.append(
                MovementIssue(
                    code="early_elbow_flare",
                    label="Elbows flare too early",
                    severity="moderate" if signals.elbow_flare_delta_deg <= 24 else "high",
                    evidence=(
                        f"Elbow flare change of {signals.elbow_flare_delta_deg:.1f} degrees suggests the transition "
                        "from chest drive to lockout is leaking position."
                    ),
                )
            )

        if signals.left_right_lockout_delta_ms > 140:
            issues.append(
                MovementIssue(
                    code="uneven_lockout",
                    label="Lockout is uneven",
                    severity="moderate" if signals.left_right_lockout_delta_ms <= 220 else "high",
                    evidence=(
                        f"Left-right lockout gap of {signals.left_right_lockout_delta_ms:.0f} ms suggests asymmetry "
                        "through the finish."
                    ),
                )
            )

        if signals.thoracic_extension_score < 0.55:
            issues.append(
                MovementIssue(
                    code="upper_back_stability",
                    label="Upper-back position softens during the press",
                    severity=self._severity_from_score(signals.thoracic_extension_score),
                    evidence=(
                        f"Thoracic-extension score {signals.thoracic_extension_score:.2f} suggests you lose the chest-up "
                        "platform that keeps the touch and press consistent."
                    ),
                )
            )

        return issues

    def _infer_weak_points(
        self,
        signals: BenchSignalProfile,
        sticking_point: str,
        movement_issues: list[MovementIssue],
    ) -> list[WeakPointInference]:
        issue_codes = {issue.code for issue in movement_issues}
        weak_points: list[WeakPointInference] = []

        if sticking_point == "off chest":
            if "leg_drive_timing" in issue_codes or "hip_stability" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Start strength and leg-drive timing",
                        confidence=0.82,
                        rationale="The bar is slowing early and the lower-body timing markers suggest you are not transferring force into the press off the chest.",
                    )
                )
            if "upper_back_stability" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Chest-up stability off the chest",
                        confidence=0.74,
                        rationale="The bar is hardest near the chest while the upper-back platform softens, which can blunt the initial drive.",
                    )
                )

        if sticking_point == "mid-range":
            if "bar_path_stack" in issue_codes or "early_elbow_flare" in issue_codes:
                weak_points.append(
                    WeakPointInference(
                        label="Mid-range transition strength and bar path",
                        confidence=0.79,
                        rationale="The bar slows through the transition zone and the path or elbow timing suggests you are losing leverage as the press leaves the chest.",
                    )
                )
            else:
                weak_points.append(
                    WeakPointInference(
                        label="Mid-range pressing strength",
                        confidence=0.62,
                        rationale="The hardest point lands in the middle of the press without a clearer setup fault dominating the rep.",
                    )
                )

        if sticking_point == "lockout":
            weak_points.append(
                WeakPointInference(
                    label="Lockout finish and triceps expression",
                    confidence=0.68,
                    rationale="The bar survives the chest and transition but still loses speed near the top, which points more toward finishing strength or asymmetry than start strength.",
                )
            )

        if not weak_points:
            weak_points.append(
                WeakPointInference(
                    label="General bench coordination",
                    confidence=0.5,
                    rationale="The rep shows some leakage, but the current signals do not isolate one dominant weak point cleanly yet.",
                )
            )

        return weak_points

    def _build_cues(
        self,
        sticking_point: str,
        movement_issues: list[MovementIssue],
        submission: VideoSubmission,
    ) -> list[str]:
        issue_codes = {issue.code for issue in movement_issues}
        cues = [
            "Drive yourself back into the bench as the press command starts instead of kicking late with the legs.",
            "Keep wrist, elbow, and bar stacked so the bar travels through the strongest line.",
        ]

        if "leg_drive_timing" in issue_codes:
            cues.append("Set the feet early, create floor pressure before the descent, and keep that pressure through the touch.")
        if "bar_path_stack" in issue_codes:
            cues.append("Touch lower and press back slightly so the bar does not drift into the slowest path.")
        if "early_elbow_flare" in issue_codes:
            cues.append("Stay tucked long enough to finish the initial drive before letting the elbows open fully.")
        if "upper_back_stability" in issue_codes:
            cues.append("Keep the sternum high and squeeze the bench with the upper back so the chest does not collapse at the bottom.")

        if submission.grip_width_style in {"self_selected", "medium"}:
            cues.append("Stay with your self-selected grip if it keeps you strong and legal; do not force a wide grip just because it looks more typical.")

        if sticking_point == "off chest":
            cues.append("Treat the first inches off the chest as the priority: tight touch, instant leg drive, and no soft sink at the bottom.")

        return cues[:5]

    @staticmethod
    def _build_programming_adjustments(
        sticking_point: str,
        movement_issues: list[MovementIssue],
    ) -> list[str]:
        issue_codes = {issue.code for issue in movement_issues}
        adjustments: list[str] = []

        if sticking_point == "off chest":
            adjustments.append("Add paused bench or Spoto press work in the RPE 6.5-8 range to build control and force off the chest.")
        if sticking_point == "mid-range":
            adjustments.append("Keep bench variation work that reinforces the chest-to-mid-range transition, such as Spoto press or longer pauses.")
        if sticking_point == "lockout":
            adjustments.append("Bias one accessory slot toward close-grip or pin press work to reinforce the finish.")

        if "leg_drive_timing" in issue_codes:
            adjustments.append("Use more submaximal competition bench exposures with a deliberate pause so leg-drive timing is practiced under repeatable conditions.")
        if "bar_path_stack" in issue_codes:
            adjustments.append("Keep technical bench sets earlier in the week and avoid pushing load if bar drift keeps showing up.")
        if "uneven_lockout" in issue_codes:
            adjustments.append("Add unilateral upper-back and dumbbell pressing work to clean up left-right finish asymmetry.")

        if not adjustments:
            adjustments.append("Hold the current pressing structure steady and gather more clips before changing the block.")

        return adjustments[:4]

    @staticmethod
    def _build_summary(
        submission: VideoSubmission,
        sticking_point: str,
        movement_issues: list[MovementIssue],
        weak_points: list[WeakPointInference],
    ) -> str:
        top_issue = movement_issues[0].label if movement_issues else "no dominant movement fault"
        top_weak_point = weak_points[0].label if weak_points else "general pressing coordination"
        return (
            f"This {submission.lift_kg:.1f} kg bench at RPE {submission.completed_rpe:.1f} shows the main sticking point "
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
