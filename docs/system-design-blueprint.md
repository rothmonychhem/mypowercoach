# myPowerCoach System Design Blueprint

## 1. Purpose

`myPowerCoach` is a powerlifting coaching platform designed as a professional software product, not a single opaque AI feature. The system should:

- generate personalized training plans
- track workout execution and adherence
- analyze performance trends
- infer likely weak points
- adapt future programming
- later incorporate video-based technique analysis

The core design decision is to model the coaching intelligence as a composed expert system. Instead of one `AICoach` class or one generic chatbot workflow, the platform uses specialized engines with narrow responsibilities and explicit contracts.

## 2. Product Goals

### Functional goals

- Create and manage athlete profiles
- Generate an initial 4-week powerlifting training block
- Log workouts against prescriptions
- Analyze execution, fatigue, and progress
- Adapt upcoming programming based on performance and readiness
- Produce clear athlete-facing coaching feedback
- Add video movement analysis in a later phase without reworking the core architecture

### Quality goals

- professional architecture
- clean OOP and separation of concerns
- explainable and extensible AI structure
- zero-cost friendly initial implementation
- easy migration from SQLite to PostgreSQL
- easy replacement of rule-based components with ML or LLM components later

## 3. Architectural Style

The system should use a layered architecture with domain-driven boundaries.

### Layers

1. Presentation
   Handles HTTP endpoints, request validation, auth hooks later, and response formatting.
2. Application
   Handles use cases, orchestration, transactions, and workflow sequencing.
3. Domain
   Holds business entities, value objects, domain services, rule engines, and policy logic.
4. Infrastructure
   Handles persistence, local storage, video tooling, and third-party adapters.

### Dependency direction

Dependencies point inward:

- `api -> application -> domain`
- `infrastructure -> domain`

The domain layer must not depend on FastAPI, SQLAlchemy models, OpenCV, or storage frameworks.

## 4. System Context

### External actors

- Athlete
- Coach or admin user later
- Local file system
- Database
- Video processing libraries

### High-level modules

- Athlete Management
- Programming Engine
- Logging and Progress Tracking
- Performance Analysis
- Adaptation Engine
- Feedback Engine
- Video Analysis Engine

## 5. Core Design Principles

- Follow SRP, OCP, and Dependency Inversion
- Prefer composition over inheritance
- Avoid god services and fat controllers
- Keep business rules in the domain layer
- Use repositories to isolate persistence
- Use explicit DTOs at layer boundaries
- Favor deterministic, explainable rules in v1
- Make each intelligence component independently replaceable

## 6. Bounded Contexts

The initial product can be organized around five bounded contexts.

### Athlete Context

Owns athlete identity, demographics, training background, constraints, and lift baselines.

### Programming Context

Owns training programs, blocks, weeks, sessions, exercise prescriptions, progression models, and lift priorities.

### Training Execution Context

Owns workout logs, completion status, actual performance, adherence, RPE, and recovery check-ins.

### Coaching Intelligence Context

Owns profiling, performance analysis, weak-point inference, adaptation, and feedback composition.

### Movement Analysis Context

Owns video submissions, extracted kinematics, technique issue detection, and movement-analysis outputs.

## 7. Domain Model

### Entities

#### Athlete

Represents a lifter and their stable coaching profile.

Key responsibilities:

- own athlete identity and profile state
- maintain training constraints and preferences
- expose domain-safe update methods

Suggested fields:

- `athlete_id`
- `name`
- `birth_date`
- `sex`
- `bodyweight_kg`
- `training_age_years`
- `goal`
- `equipment_profile`
- `availability`
- `injury_constraints`
- `created_at`

#### LiftProfile

Represents the athlete’s current state for a specific lift.

Suggested fields:

- `athlete_id`
- `lift_type`
- `best_single_kg`
- `estimated_one_rm_kg`
- `technique_notes`
- `priority`
- `frequency_tolerance`

#### TrainingProgram

Aggregate root for a generated program.

Responsibilities:

- own block lifecycle
- protect consistency of weeks and sessions
- track current status and adaptation history

Suggested fields:

- `program_id`
- `athlete_id`
- `status`
- `start_date`
- `end_date`
- `goal`
- `program_style`
- `weeks`

#### TrainingBlock

Optional intermediate concept if programs contain multiple blocks.

Suggested use:

- accumulation
- intensification
- taper
- test

#### TrainingWeek

Represents a weekly unit of prescriptions and adaptation scope.

Suggested fields:

- `week_number`
- `theme`
- `planned_volume`
- `planned_intensity`
- `sessions`

#### TrainingSession

Represents one training day.

Suggested fields:

- `session_id`
- `week_number`
- `day_index`
- `focus`
- `exercise_prescriptions`

#### ExercisePrescription

Represents an assigned exercise with set, rep, and intensity instructions.

Suggested fields:

- `exercise_name`
- `category`
- `sets`
- `reps`
- `target_rpe`
- `percentage_of_e1rm`
- `tempo`
- `rest_seconds`
- `notes`

#### WorkoutLog

Represents what the athlete actually completed.

Suggested fields:

- `workout_log_id`
- `athlete_id`
- `session_id`
- `completed_at`
- `exercise_results`
- `adherence_score`
- `session_notes`

#### RecoveryLog

Represents recovery and readiness inputs used for analysis.

Suggested fields:

- `sleep_hours`
- `fatigue_score`
- `soreness_score`
- `stress_score`
- `motivation_score`
- `bodyweight_kg`

#### VideoSubmission

Represents a submitted lift video and metadata.

Suggested fields:

- `video_submission_id`
- `athlete_id`
- `lift_type`
- `camera_angle`
- `file_path`
- `captured_at`
- `status`

#### MovementAnalysis

Represents extracted motion metrics and detected issues from a video.

Suggested fields:

- `analysis_id`
- `video_submission_id`
- `rep_count`
- `depth_score`
- `bar_path_proxy`
- `joint_trajectory_metrics`
- `timing_metrics`
- `technique_issues`
- `confidence`

#### WeakPointProfile

Represents current inferred weaknesses for an athlete.

Suggested fields:

- `athlete_id`
- `inferred_weak_points`
- `confidence_scores`
- `updated_at`

#### CoachingFeedback

Represents athlete-facing guidance produced from internal analyses.

Suggested fields:

- `feedback_id`
- `athlete_id`
- `context_type`
- `summary`
- `cues`
- `rationale`
- `recommendations`
- `created_at`

### Value Objects

Value objects should be immutable where practical and validate their own invariants.

- `RPE`
- `Percentage`
- `Volume`
- `Intensity`
- `ReadinessScore`
- `EstimatedOneRepMax`
- `ExerciseSelection`
- `TechniqueIssue`
- `WeakPoint`
- `ProgramAdjustment`

## 8. Domain Services and Intelligence Engines

The coaching intelligence should be composed of narrow domain services.

### AthleteProfiler

Purpose:

- classify athlete level
- estimate recoverability
- identify constraints and lift priorities

Inputs:

- athlete profile
- lift profiles
- schedule constraints
- injury constraints

Outputs:

- `AthleteAssessment`

Primary decisions:

- beginner, intermediate, advanced
- suggested frequency by lift
- recoverability score
- programming style recommendation

### ProgramGenerator

Purpose:

- generate an initial training block from athlete assessment and goals

Inputs:

- athlete assessment
- goal context
- weak-point profile if present

Outputs:

- `TrainingProgram`

Primary decisions:

- split selection
- frequency assignment
- main lift variants
- progression model
- weekly set and intensity targets

### PerformanceAnalyzer

Purpose:

- evaluate training execution against prescription

Inputs:

- prescribed session
- workout logs
- recovery logs
- previous performance baseline

Outputs:

- `PerformanceAnalysis`

Primary decisions:

- e1RM trend
- adherence quality
- underperformance flags
- overreaching indicators
- progress classification

### RecoveryAnalyzer

Purpose:

- interpret readiness and fatigue data independent of raw performance

Outputs:

- `RecoveryAssessment`

Primary decisions:

- low, moderate, high fatigue
- deload pressure
- readiness trend

### MovementAnalyzer

Purpose:

- convert raw lift video into structured movement metrics

Outputs:

- `MovementAnalysis`

Responsibilities:

- frame extraction
- pose estimation
- rep segmentation
- angle and timing calculation
- technique issue candidate generation

### WeakPointInferer

Purpose:

- infer likely limiting factors by combining multiple signals

Inputs:

- movement analysis
- missed rep patterns
- plateau trends
- exercise responses

Outputs:

- `WeakPointProfile`

Responsibilities:

- map observed patterns to likely causes
- assign confidence levels
- distinguish technique issues from strength deficits where possible

### ProgramAdapter

Purpose:

- modify future programming without mutating analysis concerns

Inputs:

- performance analysis
- recovery assessment
- weak-point profile
- current program

Outputs:

- `ProgramAdaptationResult`

Responsibilities:

- adjust volume
- adjust intensity targets
- change lift emphasis
- recommend deload
- swap exercise variations

### FeedbackComposer

Purpose:

- produce clear athlete-facing communication from structured outputs

Outputs:

- `CoachingFeedback`

Responsibilities:

- summarize what changed
- explain why it changed
- generate cues and next steps

V1 should use templates and deterministic phrasing rather than an LLM.

## 9. Domain Service Contracts

These are logical interfaces, not final syntax.

```python
from typing import Protocol


class AthleteProfiler(Protocol):
    def assess(self, athlete: Athlete, lifts: list[LiftProfile]) -> AthleteAssessment: ...


class ProgramGenerator(Protocol):
    def generate_initial_block(
        self,
        athlete: Athlete,
        assessment: AthleteAssessment,
        weak_points: WeakPointProfile | None = None,
    ) -> TrainingProgram: ...


class PerformanceAnalyzer(Protocol):
    def analyze(
        self,
        prescription: TrainingSession,
        workout_log: WorkoutLog,
        recovery_log: RecoveryLog | None,
    ) -> PerformanceAnalysis: ...


class MovementAnalyzer(Protocol):
    def analyze(
        self,
        submission: VideoSubmission,
    ) -> MovementAnalysis: ...


class WeakPointInferer(Protocol):
    def infer(
        self,
        performance: PerformanceAnalysis | None,
        movement: MovementAnalysis | None,
        history: list[WorkoutLog],
    ) -> WeakPointProfile: ...


class ProgramAdapter(Protocol):
    def adapt(
        self,
        program: TrainingProgram,
        performance: PerformanceAnalysis,
        recovery: RecoveryAssessment | None,
        weak_points: WeakPointProfile | None,
    ) -> ProgramAdaptationResult: ...


class FeedbackComposer(Protocol):
    def compose(self, context: CoachingContext) -> CoachingFeedback: ...
```

## 10. Rule Engine Design

The intelligence layer should be powered by explicit rule sets before any ML work.

### Why rules first

- zero-cost friendly
- explainable
- deterministic
- easy to test
- easy to debug
- easy to replace later behind interfaces

### Rule categories

#### Profiling rules

- athlete level classification
- recoverability scoring
- frequency recommendation

#### Programming rules

- split selection
- weekly volume landmarks
- intensity ceilings and floors
- progression schemes by athlete level

#### Performance rules

- e1RM estimation
- fatigue flagging
- missed-target classification
- stall detection

#### Technique rules

- squat depth detection
- hip shoot detection
- torso collapse detection
- bench touch consistency
- deadlift lockout timing

#### Weak-point inference rules

- map symptoms to likely causes
- score confidence by supporting evidence

#### Adaptation rules

- deload recommendation
- volume increase or decrease
- intensity adjustment
- variation swaps
- frequency shifts

### Rule object pattern

```python
from typing import Protocol


class TechniqueRule(Protocol):
    def evaluate(self, analysis: MovementAnalysis) -> list[TechniqueIssue]: ...


class AdaptationRule(Protocol):
    def apply(self, context: AdaptationContext) -> list[ProgramAdjustment]: ...
```

### Example concrete rule types

- `BeginnerFrequencyRule`
- `IntermediateVolumeLandmarkRule`
- `EstimatedOneRmTrendRule`
- `HighFatigueDeloadRule`
- `SquatDepthRule`
- `HipShootRule`
- `BenchBarPathDeviationRule`
- `LowBenchExposureRule`
- `QuadWeaknessInferenceRule`
- `BracingDeficitInferenceRule`
- `ReduceSquatIntensityRule`
- `IncreaseBenchFrequencyRule`
- `SwapPausedSquatRule`

### Rule execution strategy

Rules should be grouped into ordered pipelines. Each pipeline can:

- collect evidence
- assign scores
- emit decisions
- include rationale strings for explainability

Avoid embedding rule thresholds directly inside API or application handlers.

## 11. Application Layer Use Cases

Each use case should orchestrate repositories and domain services but avoid domain logic of its own.

### CreateAthleteUseCase

Flow:

1. validate command
2. create athlete aggregate
3. persist athlete
4. optionally create initial lift profiles

### GenerateInitialProgramUseCase

Flow:

1. load athlete and lift profiles
2. call `AthleteProfiler`
3. call `WeakPointInferer` if prior evidence exists
4. call `ProgramGenerator`
5. persist program
6. call `FeedbackComposer`
7. return program and explanation

### LogWorkoutUseCase

Flow:

1. load prescription
2. store workout log
3. optionally store recovery log
4. analyze performance
5. update athlete metrics snapshots if needed
6. compose feedback

### AdaptProgramUseCase

Flow:

1. load current program and recent logs
2. analyze performance and recovery
3. infer weak points
4. apply adaptation
5. persist modified future prescriptions
6. create feedback record

### AnalyzeVideoUseCase

Flow:

1. store submission metadata
2. call movement analyzer
3. infer weak points
4. persist movement analysis and weak-point profile
5. optionally trigger adaptation workflow
6. compose technique feedback

## 12. Repository Contracts

Repositories should expose domain-oriented methods, not generic ORM abstractions.

```python
from typing import Protocol


class AthleteRepository(Protocol):
    def add(self, athlete: Athlete) -> None: ...
    def get(self, athlete_id: str) -> Athlete | None: ...
    def save(self, athlete: Athlete) -> None: ...


class LiftProfileRepository(Protocol):
    def list_for_athlete(self, athlete_id: str) -> list[LiftProfile]: ...
    def save_many(self, profiles: list[LiftProfile]) -> None: ...


class ProgramRepository(Protocol):
    def add(self, program: TrainingProgram) -> None: ...
    def get_active_for_athlete(self, athlete_id: str) -> TrainingProgram | None: ...
    def save(self, program: TrainingProgram) -> None: ...


class WorkoutLogRepository(Protocol):
    def add(self, log: WorkoutLog) -> None: ...
    def list_recent_for_athlete(self, athlete_id: str, limit: int = 12) -> list[WorkoutLog]: ...


class RecoveryLogRepository(Protocol):
    def add(self, log: RecoveryLog) -> None: ...
    def list_recent_for_athlete(self, athlete_id: str, limit: int = 12) -> list[RecoveryLog]: ...


class VideoSubmissionRepository(Protocol):
    def add(self, submission: VideoSubmission) -> None: ...
    def get(self, submission_id: str) -> VideoSubmission | None: ...


class MovementAnalysisRepository(Protocol):
    def add(self, analysis: MovementAnalysis) -> None: ...
    def list_for_athlete(self, athlete_id: str) -> list[MovementAnalysis]: ...
```

## 13. Persistence Model

The persistence model can be flatter than the domain model while preserving traceability.

### Initial tables

- `athletes`
- `lift_profiles`
- `training_programs`
- `training_blocks`
- `training_weeks`
- `training_sessions`
- `exercise_prescriptions`
- `workout_logs`
- `exercise_results`
- `recovery_logs`
- `video_submissions`
- `movement_analyses`
- `weak_point_profiles`
- `coaching_feedback`

### Persistence guidance

- Start with SQLite and SQLAlchemy 2.0
- Use Alembic from the start
- Store domain IDs as UUID strings
- Keep JSON columns for structured evidence where relational modeling would slow iteration
- Avoid exposing ORM models outside the infrastructure layer

### Migration path

The design should allow:

- SQLite in local development
- PostgreSQL later with minimal application or domain changes

## 14. Package Structure

Recommended backend layout:

```text
app/
├── api/
│   ├── routes/
│   │   ├── athletes.py
│   │   ├── programs.py
│   │   ├── workouts.py
│   │   ├── videos.py
│   │   └── feedback.py
│   ├── schemas/
│   │   ├── athlete.py
│   │   ├── program.py
│   │   ├── workout.py
│   │   ├── recovery.py
│   │   └── video.py
│   └── dependencies.py
│
├── application/
│   ├── dto/
│   ├── commands/
│   ├── queries/
│   └── use_cases/
│       ├── create_athlete.py
│       ├── generate_initial_program.py
│       ├── log_workout.py
│       ├── adapt_program.py
│       └── analyze_video.py
│
├── domain/
│   ├── models/
│   │   ├── athlete.py
│   │   ├── lift_profile.py
│   │   ├── training_program.py
│   │   ├── training_block.py
│   │   ├── training_week.py
│   │   ├── training_session.py
│   │   ├── exercise_prescription.py
│   │   ├── workout_log.py
│   │   ├── recovery_log.py
│   │   ├── video_submission.py
│   │   ├── movement_analysis.py
│   │   ├── weak_point_profile.py
│   │   └── coaching_feedback.py
│   ├── value_objects/
│   │   ├── rpe.py
│   │   ├── percentage.py
│   │   ├── intensity.py
│   │   ├── volume.py
│   │   ├── readiness_score.py
│   │   ├── estimated_one_rep_max.py
│   │   └── technique_issue.py
│   ├── services/
│   │   ├── athlete_profiler.py
│   │   ├── program_generator.py
│   │   ├── performance_analyzer.py
│   │   ├── recovery_analyzer.py
│   │   ├── movement_analyzer.py
│   │   ├── weak_point_inferer.py
│   │   ├── program_adapter.py
│   │   └── feedback_composer.py
│   ├── rules/
│   │   ├── profiling/
│   │   ├── programming/
│   │   ├── performance/
│   │   ├── technique/
│   │   ├── weak_points/
│   │   └── adaptation/
│   └── repositories/
│       ├── athlete_repository.py
│       ├── lift_profile_repository.py
│       ├── program_repository.py
│       ├── workout_log_repository.py
│       ├── recovery_log_repository.py
│       ├── video_submission_repository.py
│       └── movement_analysis_repository.py
│
├── infrastructure/
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   ├── models/
│   │   ├── mappers/
│   │   └── repositories/
│   ├── storage/
│   │   └── local_file_storage.py
│   ├── video/
│   │   ├── frame_extractor.py
│   │   ├── mediapipe_pose_estimator.py
│   │   ├── rep_detector.py
│   │   ├── angle_calculator.py
│   │   └── motion_metrics.py
│   └── feedback/
│       └── template_feedback_composer.py
│
├── core/
│   ├── config.py
│   ├── exceptions.py
│   └── logging.py
│
└── main.py
```

## 15. Workflow Blueprints

### Workflow A: Generate Initial Program

1. create athlete
2. create or load lift profiles
3. profile athlete
4. infer initial priorities
5. generate first 4-week block
6. persist program
7. compose athlete-facing plan explanation

### Workflow B: Log Workout and Reassess

1. athlete submits completed session
2. store workout log and recovery data
3. analyze performance against prescription
4. update short-term fatigue and progress assessments
5. compose immediate feedback

### Workflow C: Weekly Adaptation

1. load recent performance and recovery history
2. infer weak points and fatigue status
3. apply adaptation rules to upcoming sessions
4. persist program changes
5. compose summary of what changed and why

### Workflow D: Upload Video and Get Technique Feedback

1. receive video metadata and file
2. extract movement metrics
3. run technique rules
4. infer likely weak points from technique plus history
5. optionally modify future exercise selection
6. compose cues and rationale

## 16. Explainability Model

Every intelligence component should be capable of returning structured rationale. This makes the system feel more like a real coaching engine and less like hidden magic.

### Example rationale payloads

- why a frequency was chosen
- which fatigue signals triggered a reduction
- which movement evidence supported a weak-point inference
- why a lift variation was swapped

This can be implemented with:

- rule identifiers
- supporting evidence list
- confidence values
- human-readable rationale strings

## 17. Zero-Cost-Friendly Strategy

V1 should avoid external paid services.

### Use these defaults

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- OpenCV
- MediaPipe
- NumPy
- Pandas
- local file storage
- synchronous background processing unless async or queueing becomes necessary

### Defer these until justified

- Celery or RQ
- PostgreSQL
- Redis
- cloud object storage
- LLM-based feedback generation
- custom ML models

## 18. Non-Functional Requirements

### Maintainability

- domain logic must remain testable without HTTP or DB setup
- rule thresholds should live in dedicated rule modules or config objects
- new engines should be pluggable behind protocols

### Performance

- initial workout and plan flows should be request-response
- video analysis can start synchronous for small clips, then move to background jobs later

### Observability

- log use case boundaries
- log rule outcomes and adaptation decisions
- preserve analysis artifacts for debugging

### Safety

- version adaptation rules and programming logic over time
- keep an audit trail of generated and adapted prescriptions
- store derived metrics separately from raw logs when helpful

## 19. Testing Strategy

### Domain tests

- entity invariants
- value object validation
- rule behavior
- adaptation decision logic

### Application tests

- use case orchestration
- repository interaction through fakes
- workflow success and failure paths

### Infrastructure tests

- SQLAlchemy repository behavior
- file storage behavior
- video analysis adapter integration

### End-to-end tests

- create athlete -> generate program
- log workout -> adapt program
- upload video -> receive analysis

The testing pyramid should emphasize domain and rule tests first.

## 20. Implementation Roadmap

### Milestone 1: Domain Foundation

Deliverables:

- domain entities
- value objects
- service protocols
- domain result models
- initial rule definitions

Success criteria:

- core coaching logic can be tested without FastAPI or SQLAlchemy

### Milestone 2: Initial Programming Engine

Deliverables:

- athlete profiling engine
- program generator
- feedback composer
- initial 4-week block generation

Success criteria:

- generate a reasonable program for a novice or intermediate athlete from profile data

### Milestone 3: Training Execution and Analysis

Deliverables:

- workout log model
- recovery log model
- performance analyzer
- weekly adaptation engine

Success criteria:

- system can modify upcoming training based on recent execution and recovery data

### Milestone 4: Persistence

Deliverables:

- SQLAlchemy models
- repository implementations
- Alembic setup
- SQLite database wiring

Success criteria:

- athlete, program, and workout flows persist and reload correctly

### Milestone 5: API Surface

Deliverables:

- FastAPI routes
- request and response schemas
- dependency wiring

Success criteria:

- external clients can create athletes, generate programs, log workouts, and request feedback

### Milestone 6: Video Analysis

Deliverables:

- video submission flow
- MediaPipe-backed movement analyzer
- technique rule set
- weak-point inference integration

Success criteria:

- system can return structured technique findings and integrate them into programming adaptation

## 21. Risks and Mitigations

### Risk: domain model becomes anemic

Mitigation:

- keep invariants and state transitions inside entities and value objects
- avoid pushing all behavior into use cases

### Risk: AI logic becomes scattered

Mitigation:

- centralize intelligence inside domain services and rule pipelines
- require explicit contracts between engines

### Risk: rule count becomes unmanageable

Mitigation:

- organize rules by context
- use small rule objects
- include metadata and rationale

### Risk: video analysis dominates architecture too early

Mitigation:

- make video a later bounded context
- keep the coaching engine valuable without it

### Risk: infrastructure leaks into domain

Mitigation:

- isolate ORM models and adapters in infrastructure
- keep domain models framework-agnostic

## 22. Recommended First Build Scope

The first production-worthy backend slice should include:

- athlete creation
- lift profile management
- athlete profiling
- initial 4-week program generation
- workout logging
- performance analysis
- weekly adaptation
- feedback composition

Video analysis should be added after the programming engine proves strong.

## 23. Resume-Quality Product Description

`myPowerCoach` is a Python-based powerlifting coaching platform designed with layered architecture and domain-driven principles. It implements a modular intelligent coaching pipeline for athlete profiling, training plan generation, performance analysis, weak-point inference, and program adaptation, using OOP service boundaries, repository abstractions, and extensible rule engines with a migration path toward video-based technique analysis and future ML enhancements.

## 24. Immediate Next Deliverables

The best follow-up artifacts to create from this blueprint are:

1. a domain model map
2. a service responsibility map
3. a rule catalog for v1 programming and adaptation
4. class skeletons for the domain and application layers

Those four artifacts will let implementation start with clean boundaries and very little architectural churn.
