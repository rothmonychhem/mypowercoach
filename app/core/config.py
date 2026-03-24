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
    llm_provider: str
    llm_timeout_seconds: float
    llm_max_output_tokens: int
    ollama_base_url: str
    ollama_model: str
    ollama_api_key: str
    gemini_api_key: str
    gemini_model: str
    groq_api_key: str
    groq_model: str


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
        llm_provider=os.getenv("MYPOWERCOACH_LLM_PROVIDER", "none").strip().lower(),
        llm_timeout_seconds=float(os.getenv("MYPOWERCOACH_LLM_TIMEOUT_SECONDS", "20")),
        llm_max_output_tokens=int(os.getenv("MYPOWERCOACH_LLM_MAX_OUTPUT_TOKENS", "220")),
        ollama_base_url=os.getenv("MYPOWERCOACH_OLLAMA_BASE_URL", "http://localhost:11434/api").strip(),
        ollama_model=os.getenv("MYPOWERCOACH_OLLAMA_MODEL", "gemma3").strip(),
        ollama_api_key=(os.getenv("MYPOWERCOACH_OLLAMA_API_KEY") or os.getenv("OLLAMA_API_KEY") or "").strip(),
        gemini_api_key=(os.getenv("MYPOWERCOACH_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip(),
        gemini_model=os.getenv("MYPOWERCOACH_GEMINI_MODEL", "gemini-2.5-flash").strip(),
        groq_api_key=(os.getenv("MYPOWERCOACH_GROQ_API_KEY") or os.getenv("GROQ_API_KEY") or "").strip(),
        groq_model=os.getenv("MYPOWERCOACH_GROQ_MODEL", "llama-3.1-8b-instant").strip(),
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
