import os

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
