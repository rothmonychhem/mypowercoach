from pydantic import BaseModel, Field


class JointPointPayload(BaseModel):
    x: float
    y: float
    visibility: float = Field(default=1.0, ge=0.0, le=1.0)


class BenchFramePosePayload(BaseModel):
    frame_index: int = Field(ge=0)
    barbell: JointPointPayload
    shoulder: JointPointPayload
    elbow: JointPointPayload
    wrist: JointPointPayload
    hip: JointPointPayload
    knee: JointPointPayload
    ankle: JointPointPayload


class BenchSignalPayload(BaseModel):
    touch_frame: int = Field(ge=0)
    press_frame: int = Field(ge=0)
    sticking_frame: int = Field(ge=0)
    lockout_frame: int = Field(ge=0)
    pause_duration_ms: int = Field(ge=0, le=5000)
    sticking_height_ratio: float = Field(ge=0.0, le=1.0)
    bar_speed_drop_pct: float = Field(ge=0.0, le=100.0)
    bar_path_deviation_cm: float = Field(ge=0.0, le=50.0)
    elbow_flare_delta_deg: float = Field(ge=0.0, le=90.0)
    wrist_stack_score: float = Field(ge=0.0, le=1.0)
    heel_stability_score: float = Field(ge=0.0, le=1.0)
    leg_drive_score: float = Field(ge=0.0, le=1.0)
    butt_contact_score: float = Field(ge=0.0, le=1.0)
    thoracic_extension_score: float = Field(ge=0.0, le=1.0)
    left_right_lockout_delta_ms: float = Field(ge=0.0, le=2000.0)


class SquatFramePosePayload(BaseModel):
    frame_index: int = Field(ge=0)
    barbell: JointPointPayload
    shoulder: JointPointPayload
    hip: JointPointPayload
    knee: JointPointPayload
    ankle: JointPointPayload
    midfoot: JointPointPayload


class SquatSignalPayload(BaseModel):
    unrack_frame: int = Field(ge=0)
    descent_start_frame: int = Field(ge=0)
    bottom_frame: int = Field(ge=0)
    sticking_frame: int = Field(ge=0)
    lockout_frame: int = Field(ge=0)
    depth_margin_ratio: float = Field(ge=-1.0, le=1.0)
    sticking_height_ratio: float = Field(ge=0.0, le=1.0)
    bar_speed_drop_pct: float = Field(ge=0.0, le=100.0)
    bar_path_deviation_cm: float = Field(ge=0.0, le=50.0)
    torso_angle_change_deg: float = Field(ge=0.0, le=90.0)
    hip_shoot_score: float = Field(ge=0.0, le=1.0)
    knee_collapse_score: float = Field(ge=0.0, le=1.0)
    foot_pressure_shift_score: float = Field(ge=0.0, le=1.0)
    bracing_score: float = Field(ge=0.0, le=1.0)
    depth_confidence: float = Field(ge=0.0, le=1.0)
    left_right_shift_cm: float = Field(ge=0.0, le=20.0)


class DeadliftFramePosePayload(BaseModel):
    frame_index: int = Field(ge=0)
    barbell: JointPointPayload
    shoulder: JointPointPayload
    hip: JointPointPayload
    knee: JointPointPayload
    ankle: JointPointPayload
    midfoot: JointPointPayload


class DeadliftSignalPayload(BaseModel):
    setup_frame: int = Field(ge=0)
    break_from_floor_frame: int = Field(ge=0)
    knee_pass_frame: int = Field(ge=0)
    sticking_frame: int = Field(ge=0)
    lockout_frame: int = Field(ge=0)
    sticking_height_ratio: float = Field(ge=0.0, le=1.0)
    bar_speed_drop_pct: float = Field(ge=0.0, le=100.0)
    bar_path_deviation_cm: float = Field(ge=0.0, le=50.0)
    hip_rise_score: float = Field(ge=0.0, le=1.0)
    shoulder_ahead_bar_score: float = Field(ge=0.0, le=1.0)
    lat_engagement_score: float = Field(ge=0.0, le=1.0)
    lockout_stability_score: float = Field(ge=0.0, le=1.0)
    foot_balance_score: float = Field(ge=0.0, le=1.0)
    knee_track_score: float = Field(ge=0.0, le=1.0)
    bar_to_shin_distance_cm: float = Field(ge=0.0, le=30.0)
    asymmetry_shift_cm: float = Field(ge=0.0, le=20.0)


class BenchVideoAnalysisRequest(BaseModel):
    account_id: str
    video_name: str = Field(min_length=3, max_length=200)
    camera_angle: str = Field(pattern="^(side|front|front_45)$")
    fps: int = Field(ge=24, le=240)
    lift_kg: float = Field(gt=0.0, le=1000.0)
    reps: int = Field(ge=1, le=20)
    completed_rpe: float = Field(ge=5.0, le=10.0)
    grip_width_style: str = Field(pattern="^(narrow|medium|wide|self_selected)$")
    signals: BenchSignalPayload
    landmark_frames: list[BenchFramePosePayload] = Field(default_factory=list, max_length=12)


class BenchVideoAnalysisResponse(BaseModel):
    status: str
    summary: str
    sticking_point: str
    movement_issues: list[dict]
    weak_points: list[dict]
    cues: list[str]
    programming_adjustments: list[str]
    overlay_plan: dict
    reference_notes: list[str]


class SquatVideoAnalysisRequest(BaseModel):
    account_id: str
    video_name: str = Field(min_length=3, max_length=200)
    camera_angle: str = Field(pattern="^(side|front|front_45|rear_45)$")
    fps: int = Field(ge=24, le=240)
    lift_kg: float = Field(gt=0.0, le=1000.0)
    reps: int = Field(ge=1, le=20)
    completed_rpe: float = Field(ge=5.0, le=10.0)
    stance_style: str = Field(pattern="^(narrow|medium|wide|self_selected)$")
    signals: SquatSignalPayload
    landmark_frames: list[SquatFramePosePayload] = Field(default_factory=list, max_length=12)


class SquatVideoAnalysisResponse(BaseModel):
    status: str
    summary: str
    sticking_point: str
    movement_issues: list[dict]
    weak_points: list[dict]
    cues: list[str]
    programming_adjustments: list[str]
    overlay_plan: dict
    reference_notes: list[str]


class DeadliftVideoAnalysisRequest(BaseModel):
    account_id: str
    video_name: str = Field(min_length=3, max_length=200)
    camera_angle: str = Field(pattern="^(side|front_45|rear_45)$")
    fps: int = Field(ge=24, le=240)
    lift_kg: float = Field(gt=0.0, le=1000.0)
    reps: int = Field(ge=1, le=20)
    completed_rpe: float = Field(ge=5.0, le=10.0)
    deadlift_style: str = Field(pattern="^(conventional|sumo)$")
    signals: DeadliftSignalPayload
    landmark_frames: list[DeadliftFramePosePayload] = Field(default_factory=list, max_length=12)


class DeadliftVideoAnalysisResponse(BaseModel):
    status: str
    summary: str
    sticking_point: str
    style: str
    movement_issues: list[dict]
    weak_points: list[dict]
    cues: list[str]
    programming_adjustments: list[str]
    overlay_plan: dict
    reference_notes: list[str]
