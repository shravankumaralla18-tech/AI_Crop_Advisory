import asyncio
import httpx
import pytest
from app.config import Settings
from app.main import app
from app.routes import auth
from app.schemas.user_schema import UserCreate, UserLogin
from app.services import auth_service


def test_health_endpoints():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            r1 = await client.get("/api/health")
            assert r1.status_code == 200
            assert r1.json() == {"status": "ok"}

            r2 = await client.get("/health")
            assert r2.status_code == 200
            assert r2.json() == {"status": "ok"}

            r3 = await client.get("/")
            assert r3.status_code == 200
            assert r3.json()["status"] == "ok"

    asyncio.run(run())


def test_cors_preflight_and_headers():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Production Vercel origin
            res_prod = await client.options(
                "/api/auth/register",
                headers={
                    "Origin": "https://ai-crop-advisory-ochre.vercel.app",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "content-type",
                },
            )
            assert res_prod.status_code == 200
            assert res_prod.headers.get("access-control-allow-origin") == "https://ai-crop-advisory-ochre.vercel.app"
            assert res_prod.headers.get("access-control-allow-credentials") == "true"

            # 2. Localhost origin
            res_local = await client.options(
                "/api/health",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert res_local.status_code == 200
            assert res_local.headers.get("access-control-allow-origin") == "http://localhost:5173"

            # 3. Vercel preview branch origin matching regex
            res_preview = await client.options(
                "/api/health",
                headers={
                    "Origin": "https://ai-crop-advisory-preview-123.vercel.app",
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert res_preview.status_code == 200
            assert res_preview.headers.get("access-control-allow-origin") == "https://ai-crop-advisory-preview-123.vercel.app"

    asyncio.run(run())


def test_cors_origins_parsing():
    # Comma-separated with whitespace and trailing slash
    s1 = Settings(CORS_ORIGINS="http://localhost:5173/ , https://custom-domain.com/ ")
    origins = s1.cors_origins_list
    assert "http://localhost:5173" in origins
    assert "https://custom-domain.com" in origins
    assert "https://ai-crop-advisory-ochre.vercel.app" in origins

    # JSON array format
    s2 = Settings(CORS_ORIGINS='["http://localhost:3000/", "https://preview.vercel.app"]')
    origins2 = s2.cors_origins_list
    assert "http://localhost:3000" in origins2
    assert "https://preview.vercel.app" in origins2
    assert "https://ai-crop-advisory-ochre.vercel.app" in origins2


def test_registration_validation_rules():
    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Short password (<8 chars)
            r_short = await client.post(
                "/api/auth/register",
                json={"name": "Farmer Joe", "email": "joe@example.com", "password": "short"},
            )
            assert r_short.status_code == 422

            # Oversized password (>72 bytes)
            r_long = await client.post(
                "/api/auth/register",
                json={"name": "Farmer Joe", "email": "joe@example.com", "password": "a" * 73},
            )
            assert r_long.status_code == 422

            # Bad email
            r_email = await client.post(
                "/api/auth/register",
                json={"name": "Farmer Joe", "email": "not-an-email", "password": "validpassword123"},
            )
            assert r_email.status_code == 422

            # Short name (<2 chars)
            r_name = await client.post(
                "/api/auth/register",
                json={"name": "J", "email": "joe@example.com", "password": "validpassword123"},
            )
            assert r_name.status_code == 422

    asyncio.run(run())


def test_auth_registration_and_login_flow(monkeypatch):
    from bson import ObjectId
    from pymongo.errors import DuplicateKeyError
    import app.database as db_mod

    stored_users = {}

    class MockInsertResult:
        def __init__(self, inserted_id):
            self.inserted_id = inserted_id

    class MockUsersCollection:
        async def insert_one(self, doc):
            email = doc["email"]
            if email in stored_users:
                raise DuplicateKeyError("Duplicate email")
            oid = ObjectId()
            doc["_id"] = oid
            stored_users[email] = dict(doc)
            return MockInsertResult(oid)

        async def find_one(self, filter_dict):
            email = filter_dict.get("email")
            return stored_users.get(email)

    class MockDB:
        def __init__(self):
            self.users = MockUsersCollection()

    mock_db = MockDB()
    monkeypatch.setattr(db_mod, "get_db", lambda: mock_db)

    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Successful registration
            payload = {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "password": "Password123!",
                "location": "Springfield",
            }
            reg_res = await client.post("/api/auth/register", json=payload)
            assert reg_res.status_code == 201
            reg_data = reg_res.json()
            assert reg_data["email"] == "jane@example.com"
            assert reg_data["name"] == "Jane Doe"
            assert "id" in reg_data
            assert "password" not in reg_data
            assert "hashed_password" not in reg_data

            # 2. Duplicate registration triggers 409 Conflict
            dup_res = await client.post("/api/auth/register", json=payload)
            assert dup_res.status_code == 409
            assert "already exists" in dup_res.json()["detail"]

            # 3. Successful login
            login_res = await client.post(
                "/api/auth/login",
                json={"email": "jane@example.com", "password": "Password123!"},
            )
            assert login_res.status_code == 200
            login_data = login_res.json()
            assert "access_token" in login_data
            assert login_data["token_type"] == "bearer"
            assert login_data["user"]["email"] == "jane@example.com"

            # 4. Failed login - wrong password
            bad_pw_res = await client.post(
                "/api/auth/login",
                json={"email": "jane@example.com", "password": "WrongPassword99!"},
            )
            assert bad_pw_res.status_code == 401

            # 5. Failed login - unknown email
            unknown_res = await client.post(
                "/api/auth/login",
                json={"email": "unknown@example.com", "password": "Password123!"},
            )
            assert unknown_res.status_code == 401

    asyncio.run(run())

