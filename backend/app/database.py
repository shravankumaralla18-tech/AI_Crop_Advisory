import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

logger = logging.getLogger("uvicorn.error")

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect() -> None:
    global _client, _db
    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        _db = _client[settings.MONGODB_DB]
        # Verify connectivity
        await _client.admin.command("ping")
        logger.info("MongoDB connected successfully to database: %s", settings.MONGODB_DB)

        await _db.users.create_index("email", unique=True)
        await _db.disease_history.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("MongoDB indexes verified.")
    except Exception as exc:
        logger.error(
            "MongoDB connection failed: %s. "
            "Please check MONGODB_URI and verify MongoDB Atlas Network Access whitelist (allow 0.0.0.0/0 for Render).",
            exc,
        )
        raise exc


async def close() -> None:
    if _client is not None:
        _client.close()


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database is not connected")
    return _db

