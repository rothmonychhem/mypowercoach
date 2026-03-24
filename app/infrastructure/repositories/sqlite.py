import json

from app.domain.models.account import Account
from app.domain.models.athlete import AthleteProfile, LiftNumbers
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
