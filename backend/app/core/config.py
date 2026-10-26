from pathlib import Path
import os

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(BACKEND_ROOT / ".env")

DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)


def get_allowed_origins() -> list[str]:
    configured_origins = os.environ.get("LEARNINGSPHERE_CORS_ORIGINS")
    if configured_origins is None:
        return list(DEFAULT_CORS_ORIGINS)
    return [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]


def get_teaching_provider_settings() -> tuple[str, str, str, str | None]:
    return (
        os.environ.get("TEACHING_PROVIDER", "mock").strip().casefold(),
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip(),
        os.environ.get("OPENAI_API_KEY"),
    )
