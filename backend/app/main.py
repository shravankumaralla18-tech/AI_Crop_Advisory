from contextlib import asynccontextmanager
from pathlib import Path
import sys

# Ensure both backend directory and repo root are on sys.path
_app_dir = Path(__file__).resolve().parent
_backend_dir = _app_dir.parent
_repo_dir = _backend_dir.parent
for p in (_backend_dir, _repo_dir):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import database
from app.config import settings
from app.middleware.error_handler import register_exception_handlers
from app.routes import advisory, auth, crop, disease, market, user


@asynccontextmanager
async def lifespan(_: FastAPI):
    await database.connect()
    yield
    await database.close()


Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI Crop Disease & Market Advisory API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

for module in (auth, user, crop, disease, market, advisory):
    app.include_router(module.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.get("/health", tags=["Health"])
async def root_health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Crop Advisory API is running"}