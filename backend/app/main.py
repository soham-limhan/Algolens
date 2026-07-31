"""
app/main.py — FastAPI application assembly.

Startup sequence:
  1. Create all DB tables (Base.metadata.create_all)
  2. Configure rotating-file logging
  3. Mount auth, problems, and submissions routers
  4. Add CORS middleware
  5. Expose /health
"""
from __future__ import annotations

import logging
import logging.handlers
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.config import settings
from app.db.database import Base, engine
from app.models import (  # noqa: F401
    BenchmarkRun,
    ForumLike,
    ForumReply,
    ForumThread,
    InefficiencySignature,
    Problem,
    Submission,
    TestCase,
    User,
)
from app.routers.forum import router as forum_router
from app.routers.problems import router as problems_router
from app.routers.submissions import router as submissions_router


# ── Logging setup ─────────────────────────────────────────────────────────────

def _configure_logging() -> None:
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s — %(message)s")

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    # Rotating file handler — log history survives container restarts if /logs is a volume
    try:
        fh = logging.handlers.RotatingFileHandler(
            settings.log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except Exception as e:
        logging.warning("Could not create log file handler: %s", e)


_configure_logging()
logger = logging.getLogger(__name__)


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AlgoLens API",
    description="Complexity-aware competitive coding platform",
    version="0.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field_name = str(err["loc"][-1]) if err["loc"] else "non_field"
        errors.append({"field": field_name, "message": err["msg"]})
    return JSONResponse(status_code=422, content={"detail": errors})

from sqlalchemy import inspect, text

# Create all tables on startup & ensure new columns are added if missing
def _ensure_schema_up_to_date():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "submissions" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("submissions")]
            if "language" not in columns:
                try:
                    conn.execute(text("ALTER TABLE submissions ADD COLUMN language VARCHAR(20) DEFAULT 'java'"))
                    conn.commit()
                    logger.info("Added missing 'language' column to submissions table.")
                except Exception as e:
                    logger.warning("Could not add language column: %s", e)

_ensure_schema_up_to_date()
logger.info("Database tables verified/created.")

try:
    from app.seed import seed
    seed()
except Exception as e:
    logger.warning("Auto-seeding skipped or failed: %s", e)

# Mount routers
app.include_router(auth_router)
app.include_router(problems_router)
app.include_router(submissions_router)
app.include_router(forum_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
