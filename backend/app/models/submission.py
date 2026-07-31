"""app/models/submission.py — Submission and BenchmarkRun ORM models."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey("problems.id"), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="java", nullable=False)

    # Status lifecycle: pending → running_correctness → failed | benchmarking → complete
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    # Populated after benchmarking + classification
    empirical_complexity: Mapped[str | None] = mapped_column(String(30), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Populated only when a complexity gap exists
    structural_hint: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Populated on failure (compiler output / failing test case detail)
    failure_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="submissions")
    problem: Mapped["Problem"] = relationship("Problem", back_populates="submissions")
    benchmark_runs: Mapped[list["BenchmarkRun"]] = relationship(
        "BenchmarkRun", back_populates="submission", cascade="all, delete-orphan"
    )


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("submissions.id"), nullable=False
    )
    input_size: Mapped[int] = mapped_column(Integer, nullable=False)
    runtime_ms: Mapped[float] = mapped_column(Float, nullable=False)
    timed_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="benchmark_runs")
