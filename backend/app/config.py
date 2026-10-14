import json
from pathlib import Path
import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> project root is two folders above app/
BASE_DIR = Path(__file__).resolve().parents[2]


def _resolve_dir(name: str, fallback_parent: Path = BASE_DIR) -> str:
    """Find directory either at project root or in backend subfolder."""
    for candidate in [
        BASE_DIR / name,
        BASE_DIR / "backend" / name,
        Path.cwd() / name,
        Path(__file__).resolve().parents[1] / name,
    ]:
        if candidate.exists() and candidate.is_dir():
            return str(candidate)
    return str(fallback_parent / name)


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "crop_advisory"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "https://ai-crop-advisory-ochre.vercel.app"
    )
    MAX_UPLOAD_MB: int = 8
    UPLOAD_DIR: str = Field(default_factory=lambda: _resolve_dir("uploads", BASE_DIR / "backend"))
    DATA_DIR: str = Field(default_factory=lambda: _resolve_dir("data", BASE_DIR))
    AI_MODEL_DIR: str = Field(default_factory=lambda: _resolve_dir("ai-model", BASE_DIR))

    model_config = SettingsConfigDict(
        env_file=(
            str(BASE_DIR / "backend" / ".env"),
            str(BASE_DIR / ".env"),
            ".env",
        ),
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        default_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "https://ai-crop-advisory-ochre.vercel.app",
        ]
        raw = self.CORS_ORIGINS.strip() if self.CORS_ORIGINS else ""
        if not raw:
            return default_origins

        origins: list[str] = []
        if raw.startswith("[") and raw.endswith("]"):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    origins = [str(o).strip().rstrip("/") for o in parsed if str(o).strip()]
            except Exception:
                pass

        if not origins:
            origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]

        # Ensure the production Vercel frontend is always permitted
        prod_origin = "https://ai-crop-advisory-ochre.vercel.app"
        if prod_origin not in origins:
            origins.append(prod_origin)

        return origins


settings = Settings()

