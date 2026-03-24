from __future__ import annotations

from dataclasses import asdict, dataclass
from math import acos, degrees, sqrt
from pathlib import Path
from statistics import mean, pstdev

from app.domain.models.video_analysis import (
    BenchFramePose,
    BenchSignalProfile,
    DeadliftFramePose,
    DeadliftSignalProfile,
    JointPoint,
    SquatFramePose,
    SquatSignalProfile,
)

try:
    import cv2  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    cv2 = None

try:
    import mediapipe as mp  # type: ignore
except ImportError:  # pragma: no cover - optional runtime dependency
    mp = None


@dataclass(slots=True)
class BenchExtractionResult:
    sampled_frame_count: int
    landmark_frames: list[BenchFramePose]
    derived_signals: BenchSignalProfile


@dataclass(slots=True)
class SquatExtractionResult:
    sampled_frame_count: int
    landmark_frames: list[SquatFramePose]
    derived_signals: SquatSignalProfile


@dataclass(slots=True)
class DeadliftExtractionResult:
    sampled_frame_count: int
    landmark_frames: list[DeadliftFramePose]
    derived_signals: DeadliftSignalProfile


class VideoDependencyError(RuntimeError):
    pass


class VideoExtractionError(RuntimeError):
    pass


class MediaPipeVideoAnalysisPipeline:
    def __init__(self, max_sampled_frames: int = 48, preview_frames: int = 12) -> None:
        self._max_sampled_frames = max_sampled_frames
        self._preview_frames = preview_frames

    def extract_bench(self, video_path: str) -> BenchExtractionResult:
        frames, fps = self._extract_video_frames(video_path)
        poses = self._extract_bench_poses(frames)
        return BenchExtractionResult(
            sampled_frame_count=len(poses),
            landmark_frames=self._preview_pose_frames(poses),
            derived_signals=self._derive_bench_signals(poses, fps),
        )

    def extract_squat(self, video_path: str) -> SquatExtractionResult:
        frames, fps = self._extract_video_frames(video_path)
        poses = self._extract_squat_poses(frames)
        return SquatExtractionResult(
            sampled_frame_count=len(poses),
            landmark_frames=self._preview_pose_frames(poses),
            derived_signals=self._derive_squat_signals(poses, fps),
        )

    def extract_deadlift(self, video_path: str) -> DeadliftExtractionResult:
        frames, fps = self._extract_video_frames(video_path)
        poses = self._extract_deadlift_poses(frames)
        return DeadliftExtractionResult(
            sampled_frame_count=len(poses),
            landmark_frames=self._preview_pose_frames(poses),
            derived_signals=self._derive_deadlift_signals(poses, fps),
        )

    @staticmethod
    def bench_result_to_dict(result: BenchExtractionResult) -> dict:
        return {
            "sampled_frame_count": result.sampled_frame_count,
            "landmark_frames": [asdict(frame) for frame in result.landmark_frames],
            "derived_signals": asdict(result.derived_signals),
        }

    @staticmethod
    def squat_result_to_dict(result: SquatExtractionResult) -> dict:
        return {
            "sampled_frame_count": result.sampled_frame_count,
            "landmark_frames": [asdict(frame) for frame in result.landmark_frames],
            "derived_signals": asdict(result.derived_signals),
        }

    @staticmethod
    def deadlift_result_to_dict(result: DeadliftExtractionResult) -> dict:
        return {
            "sampled_frame_count": result.sampled_frame_count,
            "landmark_frames": [asdict(frame) for frame in result.landmark_frames],
            "derived_signals": asdict(result.derived_signals),
        }

    def _extract_video_frames(self, video_path: str) -> tuple[list[tuple[int, object]], float]:
        if cv2 is None or mp is None:
            raise VideoDependencyError(
                "Video extraction requires OpenCV and MediaPipe. Install the video dependencies first."
            )

        path = Path(video_path)
        if not path.exists():
            raise VideoExtractionError(f"Video file does not exist: {video_path}")

        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            raise VideoExtractionError(f"Could not open video file: {video_path}")

        fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total_frames <= 0:
            capture.release()
            raise VideoExtractionError("Video appears to have no readable frames.")

        sampled_indices = self._sample_indices(total_frames, self._max_sampled_frames)
        extracted_frames: list[tuple[int, object]] = []

        for frame_index in sampled_indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = capture.read()
            if ok and frame is not None:
                extracted_frames.append((frame_index, frame))

        capture.release()

        if len(extracted_frames) < 6:
            raise VideoExtractionError(
                "Not enough frames were extracted from the video to derive lift signals."
            )

        return extracted_frames, float(fps)

    @staticmethod
    def _sample_indices(total_frames: int, max_frames: int) -> list[int]:
        if total_frames <= max_frames:
            return list(range(total_frames))

        if max_frames <= 1:
            return [0]

        step = (total_frames - 1) / (max_frames - 1)
        return sorted({round(index * step) for index in range(max_frames)})

    def _extract_bench_poses(self, frames: list[tuple[int, object]]) -> list[BenchFramePose]:
        with mp.solutions.pose.Pose(  # type: ignore[union-attr]
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
        ) as pose:
            poses: list[BenchFramePose] = []
            for frame_index, frame in frames:
                landmarks = self._detect_landmarks(pose, frame)
                poses.append(
                    BenchFramePose(
                        frame_index=frame_index,
                        barbell=self._midpoint(landmarks, "left_wrist", "right_wrist"),
                        shoulder=self._midpoint(landmarks, "left_shoulder", "right_shoulder"),
                        elbow=self._midpoint(landmarks, "left_elbow", "right_elbow"),
                        wrist=self._midpoint(landmarks, "left_wrist", "right_wrist"),
                        hip=self._midpoint(landmarks, "left_hip", "right_hip"),
                        knee=self._midpoint(landmarks, "left_knee", "right_knee"),
                        ankle=self._midpoint(landmarks, "left_ankle", "right_ankle"),
                    )
                )
            return poses

    def _extract_squat_poses(self, frames: list[tuple[int, object]]) -> list[SquatFramePose]:
        with mp.solutions.pose.Pose(  # type: ignore[union-attr]
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
        ) as pose:
            poses: list[SquatFramePose] = []
            for frame_index, frame in frames:
                landmarks = self._detect_landmarks(pose, frame)
                midfoot = self._midpoint(landmarks, "left_foot_index", "right_foot_index")
                poses.append(
                    SquatFramePose(
                        frame_index=frame_index,
                        barbell=self._midpoint(landmarks, "left_wrist", "right_wrist"),
                        shoulder=self._midpoint(landmarks, "left_shoulder", "right_shoulder"),
                        hip=self._midpoint(landmarks, "left_hip", "right_hip"),
                        knee=self._midpoint(landmarks, "left_knee", "right_knee"),
                        ankle=self._midpoint(landmarks, "left_ankle", "right_ankle"),
                        midfoot=JointPoint(x=midfoot.x, y=self._midpoint(landmarks, "left_ankle", "right_ankle").y),
                    )
                )
            return poses

    def _extract_deadlift_poses(self, frames: list[tuple[int, object]]) -> list[DeadliftFramePose]:
        with mp.solutions.pose.Pose(  # type: ignore[union-attr]
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
        ) as pose:
            poses: list[DeadliftFramePose] = []
            for frame_index, frame in frames:
                landmarks = self._detect_landmarks(pose, frame)
                midfoot = self._midpoint(landmarks, "left_foot_index", "right_foot_index")
                poses.append(
                    DeadliftFramePose(
                        frame_index=frame_index,
                        barbell=self._midpoint(landmarks, "left_wrist", "right_wrist"),
                        shoulder=self._midpoint(landmarks, "left_shoulder", "right_shoulder"),
                        hip=self._midpoint(landmarks, "left_hip", "right_hip"),
                        knee=self._midpoint(landmarks, "left_knee", "right_knee"),
                        ankle=self._midpoint(landmarks, "left_ankle", "right_ankle"),
                        midfoot=JointPoint(x=midfoot.x, y=self._midpoint(landmarks, "left_ankle", "right_ankle").y),
                    )
                )
            return poses

    @staticmethod
    def _detect_landmarks(pose: object, frame: object) -> dict[str, JointPoint]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # type: ignore[union-attr]
        result = pose.process(rgb_frame)
        if result.pose_landmarks is None:
            raise VideoExtractionError("Pose landmarks could not be detected on one or more video frames.")

        landmark_list = result.pose_landmarks.landmark
        names = mp.solutions.pose.PoseLandmark  # type: ignore[union-attr]

        def point(name: str) -> JointPoint:
            landmark = landmark_list[getattr(names, name.upper()).value]
            return JointPoint(x=float(landmark.x), y=float(landmark.y), visibility=float(landmark.visibility))

        return {
            "left_shoulder": point("left_shoulder"),
            "right_shoulder": point("right_shoulder"),
            "left_elbow": point("left_elbow"),
            "right_elbow": point("right_elbow"),
            "left_wrist": point("left_wrist"),
            "right_wrist": point("right_wrist"),
            "left_hip": point("left_hip"),
            "right_hip": point("right_hip"),
            "left_knee": point("left_knee"),
            "right_knee": point("right_knee"),
            "left_ankle": point("left_ankle"),
            "right_ankle": point("right_ankle"),
            "left_foot_index": point("left_foot_index"),
            "right_foot_index": point("right_foot_index"),
        }

    @staticmethod
    def _midpoint(points: dict[str, JointPoint], left_key: str, right_key: str) -> JointPoint:
        left = points[left_key]
        right = points[right_key]
        return JointPoint(
            x=(left.x + right.x) / 2,
            y=(left.y + right.y) / 2,
            visibility=(left.visibility + right.visibility) / 2,
        )

    def _preview_pose_frames(self, frames: list[object]) -> list[object]:
        if len(frames) <= self._preview_frames:
            return frames
        indices = self._sample_indices(len(frames), self._preview_frames)
        return [frames[index] for index in indices]

    def _derive_bench_signals(self, poses: list[BenchFramePose], fps: float) -> BenchSignalProfile:
        bar_y = [pose.barbell.y for pose in poses]
        touch_index = bar_y.index(max(bar_y))
        press_index = min(touch_index + 1, len(poses) - 1)
        lockout_index = touch_index + self._argmin(bar_y[touch_index:])
        upward_speeds = self._upward_speed_series(bar_y, touch_index)
        sticking_relative_index = self._argmin(upward_speeds)
        sticking_index = min(touch_index + sticking_relative_index + 1, len(poses) - 1)
        shoulder_to_hip = [abs(pose.shoulder.y - pose.hip.y) for pose in poses]
        hip_y = [pose.hip.y for pose in poses]
        ankle_x = [pose.ankle.x for pose in poses]
        wrist_stack_offsets = [abs(pose.wrist.x - pose.elbow.x) for pose in poses]

        return BenchSignalProfile(
            touch_frame=poses[touch_index].frame_index,
            press_frame=poses[press_index].frame_index,
            sticking_frame=poses[sticking_index].frame_index,
            lockout_frame=poses[lockout_index].frame_index,
            pause_duration_ms=int(self._pause_duration_ms(bar_y, touch_index, fps)),
            sticking_height_ratio=self._travel_ratio(bar_y[touch_index], bar_y[sticking_index], bar_y[lockout_index]),
            bar_speed_drop_pct=self._speed_drop_pct(upward_speeds),
            bar_path_deviation_cm=self._path_deviation_cm([pose.barbell for pose in poses]),
            elbow_flare_delta_deg=abs(
                self._joint_angle(poses[press_index].shoulder, poses[press_index].elbow, poses[press_index].wrist)
                - self._joint_angle(poses[lockout_index].shoulder, poses[lockout_index].elbow, poses[lockout_index].wrist)
            ),
            wrist_stack_score=self._score_from_offsets(wrist_stack_offsets, 0.08),
            heel_stability_score=self._score_from_spread(ankle_x, 0.025),
            leg_drive_score=self._score_from_spread(hip_y[touch_index:lockout_index + 1], 0.05),
            butt_contact_score=self._score_from_spread(hip_y, 0.035),
            thoracic_extension_score=self._score_from_spread(shoulder_to_hip, 0.05),
            left_right_lockout_delta_ms=0.0,
        )

    def _derive_squat_signals(self, poses: list[SquatFramePose], fps: float) -> SquatSignalProfile:
        bar_y = [pose.barbell.y for pose in poses]
        descent_start_index = self._first_index_above_threshold(
            [bar_y[index + 1] - bar_y[index] for index in range(len(bar_y) - 1)],
            0.0015,
        )
        bottom_index = bar_y.index(max(bar_y))
        lockout_index = bottom_index + self._argmin(bar_y[bottom_index:])
        upward_speeds = self._upward_speed_series(bar_y, bottom_index)
        sticking_relative_index = self._argmin(upward_speeds)
        sticking_index = min(bottom_index + sticking_relative_index + 1, len(poses) - 1)
        torso_angles = [self._vertical_angle(pose.shoulder, pose.hip) for pose in poses]
        hip_y = [pose.hip.y for pose in poses]
        shoulder_y = [pose.shoulder.y for pose in poses]
        knee_to_midfoot = [abs(pose.knee.x - pose.midfoot.x) for pose in poses]
        bar_to_midfoot = [abs(pose.barbell.x - pose.midfoot.x) for pose in poses]
        depth_margin = [
            (pose.hip.y - pose.knee.y) / max(abs(pose.ankle.y - pose.hip.y), 0.001)
            for pose in poses
        ]

        hip_delta = hip_y[bottom_index] - hip_y[min(bottom_index + 1, len(poses) - 1)]
        shoulder_delta = shoulder_y[bottom_index] - shoulder_y[min(bottom_index + 1, len(poses) - 1)]
        hip_shoot_score = self._ratio_score(shoulder_delta, hip_delta)

        return SquatSignalProfile(
            unrack_frame=poses[0].frame_index,
            descent_start_frame=poses[descent_start_index].frame_index,
            bottom_frame=poses[bottom_index].frame_index,
            sticking_frame=poses[sticking_index].frame_index,
            lockout_frame=poses[lockout_index].frame_index,
            depth_margin_ratio=min(depth_margin),
            sticking_height_ratio=self._travel_ratio(bar_y[bottom_index], bar_y[sticking_index], bar_y[lockout_index]),
            bar_speed_drop_pct=self._speed_drop_pct(upward_speeds),
            bar_path_deviation_cm=self._path_deviation_cm([pose.barbell for pose in poses]),
            torso_angle_change_deg=abs(torso_angles[sticking_index] - torso_angles[bottom_index]),
            hip_shoot_score=hip_shoot_score,
            knee_collapse_score=self._score_from_offsets(knee_to_midfoot, 0.09),
            foot_pressure_shift_score=self._score_from_offsets(bar_to_midfoot, 0.07),
            bracing_score=self._score_from_spread(torso_angles[bottom_index:lockout_index + 1], 10.0),
            depth_confidence=self._visibility_score([pose.hip.visibility for pose in poses]),
            left_right_shift_cm=0.0,
        )

    def _derive_deadlift_signals(self, poses: list[DeadliftFramePose], fps: float) -> DeadliftSignalProfile:
        bar_y = [pose.barbell.y for pose in poses]
        start_deltas = [bar_y[index] - bar_y[index + 1] for index in range(len(bar_y) - 1)]
        break_index = self._first_index_above_threshold(start_deltas, 0.001)
        knee_pass_index = self._first_matching_index(
            poses,
            lambda pose: pose.barbell.y <= pose.knee.y,
            default=max(break_index + 1, len(poses) // 2),
        )
        lockout_index = self._argmin(bar_y)
        upward_speeds = self._upward_speed_series(bar_y, break_index)
        sticking_relative_index = self._argmin(upward_speeds)
        sticking_index = min(break_index + sticking_relative_index + 1, len(poses) - 1)
        hip_y = [pose.hip.y for pose in poses]
        bar_to_midfoot = [abs(pose.barbell.x - pose.midfoot.x) for pose in poses]
        bar_to_shin = [abs(pose.barbell.x - pose.ankle.x) for pose in poses]
        lockout_distances = [abs(pose.shoulder.y - pose.hip.y) for pose in poses[max(lockout_index - 2, 0):lockout_index + 1]]

        hip_delta = hip_y[break_index] - hip_y[min(break_index + 1, len(poses) - 1)]
        bar_delta = bar_y[break_index] - bar_y[min(break_index + 1, len(poses) - 1)]

        return DeadliftSignalProfile(
            setup_frame=poses[0].frame_index,
            break_from_floor_frame=poses[break_index].frame_index,
            knee_pass_frame=poses[knee_pass_index].frame_index,
            sticking_frame=poses[sticking_index].frame_index,
            lockout_frame=poses[lockout_index].frame_index,
            sticking_height_ratio=self._travel_ratio(bar_y[break_index], bar_y[sticking_index], bar_y[lockout_index]),
            bar_speed_drop_pct=self._speed_drop_pct(upward_speeds),
            bar_path_deviation_cm=self._path_deviation_cm([pose.barbell for pose in poses]),
            hip_rise_score=self._ratio_score(bar_delta, hip_delta),
            shoulder_ahead_bar_score=self._score_from_offsets([abs(pose.shoulder.x - pose.barbell.x) for pose in poses], 0.1),
            lat_engagement_score=self._score_from_spread(bar_to_shin, 0.05),
            lockout_stability_score=self._score_from_spread(lockout_distances, 0.04),
            foot_balance_score=self._score_from_offsets(bar_to_midfoot, 0.075),
            knee_track_score=self._score_from_offsets([abs(pose.knee.x - pose.midfoot.x) for pose in poses], 0.1),
            bar_to_shin_distance_cm=round(mean(bar_to_shin) * 100, 2),
            asymmetry_shift_cm=0.0,
        )

    @staticmethod
    def _upward_speed_series(y_values: list[float], start_index: int) -> list[float]:
        if start_index >= len(y_values) - 1:
            return [0.0]
        return [
            max(0.0, y_values[index] - y_values[index + 1])
            for index in range(start_index, len(y_values) - 1)
        ]

    @staticmethod
    def _pause_duration_ms(y_values: list[float], touch_index: int, fps: float) -> float:
        threshold = 0.0012
        frames = 0
        index = touch_index
        while index > 0 and abs(y_values[index] - y_values[index - 1]) < threshold:
            frames += 1
            index -= 1
        index = touch_index
        while index < len(y_values) - 1 and abs(y_values[index + 1] - y_values[index]) < threshold:
            frames += 1
            index += 1
        return (frames / max(fps, 1.0)) * 1000

    @staticmethod
    def _travel_ratio(start_y: float, sticking_y: float, lockout_y: float) -> float:
        travel = max(start_y - lockout_y, 0.001)
        progressed = max(start_y - sticking_y, 0.0)
        return max(0.0, min(1.0, progressed / travel))

    @staticmethod
    def _speed_drop_pct(speeds: list[float]) -> float:
        positive_speeds = [speed for speed in speeds if speed > 0]
        if len(positive_speeds) < 2:
            return 0.0
        fastest = max(positive_speeds)
        slowest = min(positive_speeds)
        return round((1 - (slowest / max(fastest, 0.001))) * 100, 2)

    @staticmethod
    def _path_deviation_cm(points: list[JointPoint]) -> float:
        x_values = [point.x for point in points]
        return round((max(x_values) - min(x_values)) * 100, 2)

    @staticmethod
    def _joint_angle(a: JointPoint, b: JointPoint, c: JointPoint) -> float:
        ab = (a.x - b.x, a.y - b.y)
        cb = (c.x - b.x, c.y - b.y)
        return MediaPipeVideoAnalysisPipeline._angle_between(ab, cb)

    @staticmethod
    def _vertical_angle(upper: JointPoint, lower: JointPoint) -> float:
        vector = (upper.x - lower.x, upper.y - lower.y)
        return MediaPipeVideoAnalysisPipeline._angle_between(vector, (0.0, -1.0))

    @staticmethod
    def _angle_between(vector_a: tuple[float, float], vector_b: tuple[float, float]) -> float:
        dot = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
        mag_a = sqrt(vector_a[0] ** 2 + vector_a[1] ** 2)
        mag_b = sqrt(vector_b[0] ** 2 + vector_b[1] ** 2)
        if mag_a == 0 or mag_b == 0:
            return 0.0
        cosine = max(-1.0, min(1.0, dot / (mag_a * mag_b)))
        return degrees(acos(cosine))

    @staticmethod
    def _score_from_offsets(values: list[float], threshold: float) -> float:
        return max(0.0, min(1.0, 1 - (mean(values) / max(threshold, 0.001))))

    @staticmethod
    def _score_from_spread(values: list[float], threshold: float) -> float:
        if len(values) < 2:
            return 1.0
        return max(0.0, min(1.0, 1 - (pstdev(values) / max(threshold, 0.001))))

    @staticmethod
    def _ratio_score(expected_delta: float, observed_delta: float) -> float:
        if observed_delta <= 0:
            return 0.0
        ratio = expected_delta / observed_delta
        return max(0.0, min(1.0, ratio))

    @staticmethod
    def _visibility_score(values: list[float]) -> float:
        return max(0.0, min(1.0, mean(values)))

    @staticmethod
    def _argmin(values: list[float]) -> int:
        return min(range(len(values)), key=lambda index: values[index])

    @staticmethod
    def _first_index_above_threshold(values: list[float], threshold: float) -> int:
        for index, value in enumerate(values):
            if value > threshold:
                return index
        return 0

    @staticmethod
    def _first_matching_index(items: list[object], matcher: object, default: int) -> int:
        for index, item in enumerate(items):
            if matcher(item):
                return index
        return default
