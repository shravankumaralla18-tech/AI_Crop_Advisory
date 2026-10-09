import asyncio
import io

import httpx
from PIL import Image

from app.config import settings
from app.main import app
from app.middleware.auth_middleware import get_current_user


def _png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "green").save(buffer, format="PNG")
    return buffer.getvalue()


def test_disease_api_auth_model_status_and_upload_validation():
    async def exercise_routes():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            app.dependency_overrides.pop(get_current_user, None)
            unauthenticated = await client.get("/api/disease/model-status")
            assert unauthenticated.status_code == 401

            app.dependency_overrides[get_current_user] = authenticated_user
            status = await client.get("/api/disease/model-status")
            assert status.status_code == 200
            assert status.json()["supported_crops"] == ["Apple", "Corn (maize)", "Potato", "Tomato"]

            unsupported = await client.post(
                "/api/disease/detect",
                data={"crop": "Rice"},
                files={"file": ("leaf.png", _png_bytes(), "image/png")},
            )
            assert unsupported.status_code == 422

            oversized = await client.post(
                "/api/disease/detect",
                data={"crop": "Tomato"},
                files={"file": ("large.png", b"x" * (settings.MAX_UPLOAD_MB * 1024 * 1024 + 1), "image/png")},
            )
            assert oversized.status_code == 413

    async def authenticated_user():
        return {"id": "test-user", "name": "Test Farmer"}

    try:
        asyncio.run(exercise_routes())
    finally:
        app.dependency_overrides.pop(get_current_user, None)
