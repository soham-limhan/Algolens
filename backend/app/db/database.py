"""
app/db/database.py — SQLAlchemy engine, session factory, and declarative base.

DATABASE_URL from settings controls SQLite (local dev) vs PostgreSQL (prod).
No code changes are needed to switch — only the env var differs.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite requires connect_args to allow multi-threaded access from FastAPI
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    # Pool settings suitable for the expected scale
    pool_pre_ping=True,
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
