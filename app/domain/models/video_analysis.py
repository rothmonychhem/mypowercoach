from dataclasses import dataclass, field


@dataclass(slots=True)
class JointPoint:
    x: float
    y: float
    visibility: float = 1.0


@dataclass(slots=True)
class BenchFramePose:
    frame_index: int
    barbell: JointPoint
    shoulder: JointPoint
    elbow: JointPoint
    wrist: JointPoint
    hip: JointPoint
    knee: JointPoint
    ankle: JointPoint


@dataclass(slots=True)
class SquatFramePose:
    frame_index: int
    barbell: JointPoint
    shoulder: JointPoint
    hip: JointPoint
    knee: JointPoint
    ankle: JointPoint
    midfoot: JointPoint


@dataclass(slots=True)
class DeadliftFramePose:
    frame_index: int
    barbell: JointPoint
    shoulder: JointPoint
    hip: JointPoint
    knee: JointPoint
    ankle: JointPoint
    midfoot: JointPoint


@dataclass(slots=True)
class VideoSubmission:
    account_id: str
    lift_type: str
    video_name: str
    camera_angle: str
    fps: int
    lift_kg: float
    reps: int
    completed_rpe: float
    grip_width_style: str
    style_variant: str = ""


@dataclass(slots=True)
class BenchSignalProfile:
    touch_frame: int
    press_frame: int
    sticking_frame: int
    lockout_frame: int
    pause_duration_ms: int
    sticking_height_ratio: float
    bar_speed_drop_pct: float
    bar_path_deviation_cm: float
    elbow_flare_delta_deg: float
    wrist_stack_score: float
    heel_stability_score: float
    leg_drive_score: float
    butt_contact_score: float
    thoracic_extension_score: float
    left_right_lockout_delta_ms: float


@dataclass(slots=True)
class SquatSignalProfile:
    unrack_frame: int
    descent_start_frame: int
    bottom_frame: int
    sticking_frame: int
    lockout_frame: int
    depth_margin_ratio: float
    sticking_height_ratio: float
    bar_speed_drop_pct: float
    bar_path_deviation_cm: float
    torso_angle_change_deg: float
    hip_shoot_score: float
    knee_collapse_score: float
    foot_pressure_shift_score: float
    bracing_score: float
    depth_confidence: float
    left_right_shift_cm: float


@dataclass(slots=True)
class DeadliftSignalProfile:
    setup_frame: int
    break_from_floor_frame: int
    knee_pass_frame: int
    sticking_frame: int
    lockout_frame: int
    sticking_height_ratio: float
    bar_speed_drop_pct: float
    bar_path_deviation_cm: float
    hip_rise_score: float
    shoulder_ahead_bar_score: float
    lat_engagement_score: float
    lockout_stability_score: float
    foot_balance_score: float
    knee_track_score: float
    bar_to_shin_distance_cm: float
    asymmetry_shift_cm: float


@dataclass(slots=True)
class MovementIssue:
    code: str
    label: str
    severity: str
    evidence: str


@dataclass(slots=True)
class WeakPointInference:
    label: str
    confidence: float
    rationale: str


@dataclass(slots=True)
class OverlayPlan:
    joints_to_draw: list[str] = field(default_factory=list)
    highlight_frames: list[int] = field(default_factory=list)
    draw_bar_path: bool = True
    reference_profile: str = "legal-self-selected-powerlifting-bench"


@dataclass(slots=True)
class BenchVideoAnalysis:
    status: str
    summary: str
    sticking_point: str
    movement_issues: list[MovementIssue] = field(default_factory=list)
    weak_points: list[WeakPointInference] = field(default_factory=list)
    cues: list[str] = field(default_factory=list)
    programming_adjustments: list[str] = field(default_factory=list)
    overlay_plan: OverlayPlan = field(default_factory=OverlayPlan)
    reference_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SquatVideoAnalysis:
    status: str
    summary: str
    sticking_point: str
    movement_issues: list[MovementIssue] = field(default_factory=list)
    weak_points: list[WeakPointInference] = field(default_factory=list)
    cues: list[str] = field(default_factory=list)
    programming_adjustments: list[str] = field(default_factory=list)
    overlay_plan: OverlayPlan = field(default_factory=OverlayPlan)
    reference_notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DeadliftVideoAnalysis:
    status: str
    summary: str
    sticking_point: str
    style: str
    movement_issues: list[MovementIssue] = field(default_factory=list)
    weak_points: list[WeakPointInference] = field(default_factory=list)
    cues: list[str] = field(default_factory=list)
    programming_adjustments: list[str] = field(default_factory=list)
    overlay_plan: OverlayPlan = field(default_factory=OverlayPlan)
    reference_notes: list[str] = field(default_factory=list)
