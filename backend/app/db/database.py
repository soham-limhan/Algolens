"""
app/db/database.py — SQLAlchemy engine, session factory, and declarative base.

DATABASE_URL from settings controls SQLite (local dev) vs PostgreSQL (prod).
No code changes are needed to switch — only the env var differs.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# Database-specific engine configuration
is_sqlite = settings.database_url.startswith("sqlite")
is_mysql = settings.database_url.startswith("mysql") or settings.database_url.startswith("mariadb")

connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_kwargs = {
    "connect_args": connect_args,
    "pool_pre_ping": True,
}

if is_mysql:
    # Avoid "MySQL server has gone away" timeouts and set pool parameters
    engine_kwargs["pool_recycle"] = 3600
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine = create_engine(
    settings.database_url,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session and ensures it is closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
