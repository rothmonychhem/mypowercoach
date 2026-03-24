import json
import sqlite3
import uuid

from app.domain.models.account import Account
from app.domain.models.athlete import AthleteProfile, LiftNumbers
from app.domain.models.exercise import ExerciseDefinition
from app.infrastructure.db.sqlite import SQLiteDatabase


class SQLiteAccountRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, account: Account) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO accounts (account_id, email, password_hash)
                VALUES (?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    email = excluded.email,
                    password_hash = excluded.password_hash
                """,
                (account.account_id, account.email, account.password_hash),
            )

    def get_by_email(self, email: str) -> Account | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT account_id, email, password_hash FROM accounts WHERE email = ?",
                (email.lower(),),
            ).fetchone()
        if row is None:
            return None
        return Account(
            account_id=row["account_id"],
            email=row["email"],
            password_hash=row["password_hash"],
        )

    def get_by_id(self, account_id: str) -> Account | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT account_id, email, password_hash FROM accounts WHERE account_id = ?",
                (account_id,),
            ).fetchone()
        if row is None:
            return None
        return Account(
            account_id=row["account_id"],
            email=row["email"],
            password_hash=row["password_hash"],
        )


class SQLiteAthleteRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save(self, athlete: AthleteProfile) -> None:
        with self._database.connect() as connection:
            connection.execute(
                """
                INSERT INTO athlete_profiles (
                    account_id,
                    name,
                    height_cm,
                    age,
                    sex,
                    bodyweight_kg,
                    training_age_years,
                    training_days_per_week,
                    primary_goal,
                    equipment,
                    preferred_block_type,
                    squat_kg,
                    bench_kg,
                    deadlift_kg,
                    notes,
                    constraints_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    name = excluded.name,
                    height_cm = excluded.height_cm,
                    age = excluded.age,
                    sex = excluded.sex,
                    bodyweight_kg = excluded.bodyweight_kg,
                    training_age_years = excluded.training_age_years,
                    training_days_per_week = excluded.training_days_per_week,
                    primary_goal = excluded.primary_goal,
                    equipment = excluded.equipment,
                    preferred_block_type = excluded.preferred_block_type,
                    squat_kg = excluded.squat_kg,
                    bench_kg = excluded.bench_kg,
                    deadlift_kg = excluded.deadlift_kg,
                    notes = excluded.notes,
                    constraints_json = excluded.constraints_json
                """,
                (
                    athlete.account_id,
                    athlete.name,
                    athlete.height_cm,
                    athlete.age,
                    athlete.sex,
                    athlete.bodyweight_kg,
                    athlete.training_age_years,
                    athlete.training_days_per_week,
                    athlete.primary_goal,
                    athlete.equipment,
                    athlete.preferred_block_type,
                    athlete.lift_numbers.squat_kg,
                    athlete.lift_numbers.bench_kg,
                    athlete.lift_numbers.deadlift_kg,
                    athlete.notes,
                    json.dumps(athlete.constraints),
                ),
            )

    def get_by_account_id(self, account_id: str) -> AthleteProfile | None:
        with self._database.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    account_id,
                    name,
                    height_cm,
                    age,
                    sex,
                    bodyweight_kg,
                    training_age_years,
                    training_days_per_week,
                    primary_goal,
                    equipment,
                    preferred_block_type,
                    squat_kg,
                    bench_kg,
                    deadlift_kg,
                    notes,
                    constraints_json
                FROM athlete_profiles
                WHERE account_id = ?
                """,
                (account_id,),
            ).fetchone()
        if row is None:
            return None
        return AthleteProfile(
            account_id=row["account_id"],
            name=row["name"],
            height_cm=row["height_cm"],
            age=row["age"],
            sex=row["sex"],
            bodyweight_kg=row["bodyweight_kg"],
            training_age_years=row["training_age_years"],
            training_days_per_week=row["training_days_per_week"],
            primary_goal=row["primary_goal"],
            equipment=row["equipment"],
            preferred_block_type=row["preferred_block_type"],
            lift_numbers=LiftNumbers(
                squat_kg=row["squat_kg"],
                bench_kg=row["bench_kg"],
                deadlift_kg=row["deadlift_kg"],
            ),
            notes=row["notes"],
            constraints=json.loads(row["constraints_json"]),
        )


class SQLiteExerciseRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def save_many(self, exercises: list[ExerciseDefinition]) -> None:
        with self._database.connect() as connection:
            for exercise in exercises:
                existing = connection.execute(
                    "SELECT exercise_id FROM exercises WHERE slot_key = ? AND name = ?",
                    (exercise.slot_key, exercise.name),
                ).fetchone()
                exercise_id = existing["exercise_id"] if existing is not None else str(uuid.uuid4())
                connection.execute(
                    """
                    INSERT INTO exercises (
                        exercise_id,
                        slot_key,
                        name,
                        category,
                        progression_key,
                        notes,
                        load_anchor,
                        specificity,
                        fatigue_cost,
                        emphasis_tags_json,
                        movement_tags_json,
                        soreness_tags_json,
                        phase_tags_json,
                        helpful_tags_json,
                        costly_tags_json,
                        sort_order
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(exercise_id) DO UPDATE SET
                        slot_key = excluded.slot_key,
                        name = excluded.name,
                        category = excluded.category,
                        progression_key = excluded.progression_key,
                        notes = excluded.notes,
                        load_anchor = excluded.load_anchor,
                        specificity = excluded.specificity,
                        fatigue_cost = excluded.fatigue_cost,
                        emphasis_tags_json = excluded.emphasis_tags_json,
                        movement_tags_json = excluded.movement_tags_json,
                        soreness_tags_json = excluded.soreness_tags_json,
                        phase_tags_json = excluded.phase_tags_json,
                        helpful_tags_json = excluded.helpful_tags_json,
                        costly_tags_json = excluded.costly_tags_json,
                        sort_order = excluded.sort_order
                    """,
                    (
                        exercise_id,
                        exercise.slot_key,
                        exercise.name,
                        exercise.category,
                        exercise.progression_key,
                        exercise.notes,
                        exercise.load_anchor,
                        exercise.specificity,
                        exercise.fatigue_cost,
                        json.dumps(exercise.emphasis_tags),
                        json.dumps(exercise.movement_tags),
                        json.dumps(exercise.soreness_tags),
                        json.dumps(exercise.phase_tags),
                        json.dumps(exercise.helpful_tags),
                        json.dumps(exercise.costly_tags),
                        exercise.sort_order,
                    ),
                )

    def list_by_slot(self, slot_key: str) -> list[ExerciseDefinition]:
        try:
            with self._database.connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        slot_key,
                        name,
                        category,
                        progression_key,
                        notes,
                        load_anchor,
                        specificity,
                        fatigue_cost,
                        emphasis_tags_json,
                        movement_tags_json,
                        soreness_tags_json,
                        phase_tags_json,
                        helpful_tags_json,
                        costly_tags_json,
                        sort_order
                    FROM exercises
                    WHERE slot_key = ?
                    ORDER BY sort_order ASC, name ASC
                    """,
                    (slot_key,),
                ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [
            ExerciseDefinition(
                slot_key=row["slot_key"],
                name=row["name"],
                category=row["category"],
                progression_key=row["progression_key"],
                notes=row["notes"],
                load_anchor=row["load_anchor"],
                specificity=row["specificity"],
                fatigue_cost=row["fatigue_cost"],
                emphasis_tags=tuple(json.loads(row["emphasis_tags_json"])),
                movement_tags=tuple(json.loads(row["movement_tags_json"])),
                soreness_tags=tuple(json.loads(row["soreness_tags_json"])),
                phase_tags=tuple(json.loads(row["phase_tags_json"])),
                helpful_tags=tuple(json.loads(row["helpful_tags_json"])),
                costly_tags=tuple(json.loads(row["costly_tags_json"])),
                sort_order=row["sort_order"],
            )
            for row in rows
        ]

    def list_slot_keys(self) -> list[str]:
        try:
            with self._database.connect() as connection:
                rows = connection.execute(
                    "SELECT DISTINCT slot_key FROM exercises ORDER BY slot_key ASC"
                ).fetchall()
        except sqlite3.OperationalError:
            return []
        return [row["slot_key"] for row in rows]
