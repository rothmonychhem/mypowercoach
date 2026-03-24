from pathlib import Path
import sqlite3


class SQLiteDatabase:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    @property
    def database_path(self) -> Path:
        return self._database_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    account_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS athlete_profiles (
                    account_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    height_cm REAL NOT NULL DEFAULT 170,
                    age INTEGER NOT NULL,
                    sex TEXT NOT NULL DEFAULT '',
                    bodyweight_kg REAL NOT NULL,
                    training_age_years REAL NOT NULL,
                    training_days_per_week INTEGER NOT NULL,
                    primary_goal TEXT NOT NULL,
                    equipment TEXT NOT NULL DEFAULT 'Raw',
                    preferred_block_type TEXT NOT NULL DEFAULT '',
                    squat_kg REAL NOT NULL,
                    bench_kg REAL NOT NULL,
                    deadlift_kg REAL NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    constraints_json TEXT NOT NULL,
                    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
                );

                CREATE TABLE IF NOT EXISTS exercises (
                    exercise_id TEXT PRIMARY KEY,
                    slot_key TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    progression_key TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    load_anchor TEXT,
                    specificity REAL NOT NULL,
                    fatigue_cost REAL NOT NULL,
                    emphasis_tags_json TEXT NOT NULL,
                    movement_tags_json TEXT NOT NULL DEFAULT '[]',
                    soreness_tags_json TEXT NOT NULL DEFAULT '[]',
                    phase_tags_json TEXT NOT NULL,
                    helpful_tags_json TEXT NOT NULL,
                    costly_tags_json TEXT NOT NULL,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(slot_key, name)
                );
                """
            )
            self._ensure_column(connection, "athlete_profiles", "height_cm", "REAL NOT NULL DEFAULT 170")
            self._ensure_column(connection, "athlete_profiles", "sex", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(connection, "athlete_profiles", "equipment", "TEXT NOT NULL DEFAULT 'Raw'")
            self._ensure_column(connection, "athlete_profiles", "preferred_block_type", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(connection, "athlete_profiles", "notes", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(connection, "exercises", "sort_order", "INTEGER NOT NULL DEFAULT 0")
            self._ensure_column(connection, "exercises", "movement_tags_json", "TEXT NOT NULL DEFAULT '[]'")
            self._ensure_column(connection, "exercises", "soreness_tags_json", "TEXT NOT NULL DEFAULT '[]'")

    @staticmethod
    def _ensure_column(
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_definition: str,
    ) -> None:
        rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        existing_columns = {row["name"] for row in rows}
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            )
