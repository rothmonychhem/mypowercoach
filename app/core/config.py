from functools import lru_cache
import os
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str
    app_version: str
    api_prefix: str
    password_salt: str
    database_path: Path
    database_url: str | None


@lru_cache
def get_settings() -> Settings:
    load_dotenv(Path(".env"))
    database_path = Path(os.getenv("MYPOWERCOACH_DATABASE_PATH", "data/mypowercoach.db"))
    return Settings(
        app_name=os.getenv("MYPOWERCOACH_APP_NAME", "myPowerCoach API"),
        app_version=os.getenv("MYPOWERCOACH_APP_VERSION", "0.1.0"),
        api_prefix=os.getenv("MYPOWERCOACH_API_PREFIX", "/api"),
        password_salt=os.getenv("MYPOWERCOACH_PASSWORD_SALT", "myPowerCoach-dev-salt"),
        database_path=database_path,
        database_url=os.getenv("DATABASE_URL"),
    )


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if key and key not in os.environ:
            os.environ[key] = value
