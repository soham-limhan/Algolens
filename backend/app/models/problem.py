"""app/models/problem.py — Problem, TestCase, and InefficiencySignature ORM models."""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy | medium | hard
    optimal_time_complexity: Mapped[str] = mapped_column(String(30), nullable=False)
    optimal_space_complexity: Mapped[str] = mapped_column(String(30), nullable=False)
    optimal_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Key into app/problems_data/registry.py — NOT the generator code itself
    generator_key: Mapped[str] = mapped_column(String(80), nullable=False)

    # Relationships
    test_cases: Mapped[list["TestCase"]] = relationship(
        "TestCase", back_populates="problem", cascade="all, delete-orphan"
    )
    inefficiency_signatures: Mapped[list["InefficiencySignature"]] = relationship(
        "InefficiencySignature", back_populates="problem", cascade="all, delete-orphan"
    )
    submissions: Mapped[list["Submission"]] = relationship("Submission", back_populates="problem")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey("problems.id"), nullable=False)
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    # exact | numeric_tolerance | sorted | custom
    comparator_type: Mapped[str] = mapped_column(String(30), nullable=False, default="exact")

    problem: Mapped["Problem"] = relationship("Problem", back_populates="test_cases")


class InefficiencySignature(Base):
    __tablename__ = "inefficiency_signatures"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    problem_id: Mapped[str] = mapped_column(String(36), ForeignKey("problems.id"), nullable=False)
    # e.g. "nested_loop_lookup", "unmemoized_recursion"
    pattern_type: Mapped[str] = mapped_column(String(60), nullable=False)
    # Shown to the learner when pattern matches AND a complexity gap exists
    hint_text: Mapped[str] = mapped_column(Text, nullable=False)

    problem: Mapped["Problem"] = relationship("Problem", back_populates="inefficiency_signatures")
