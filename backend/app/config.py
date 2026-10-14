from pathlib import Path
import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/config.py -> project root is two folders above app/
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "crop_advisory"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    MAX_UPLOAD_MB: int = 8
    UPLOAD_DIR: str = str(BASE_DIR / "backend" / "uploads")
    DATA_DIR: str = str(BASE_DIR / "data")
    AI_MODEL_DIR: str = str(BASE_DIR / "ai-model")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "backend" / ".env"),
        extra="ignore"
    )


settings = Settings()
