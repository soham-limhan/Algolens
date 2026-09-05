"""app/schemas/submission.py — Pydantic models for submission endpoints."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import uuid

from pydantic import BaseModel, Field, field_validator

from app.config import settings


SUPPORTED_LANGUAGES = {"java", "python", "cpp", "c", "javascript"}


class SubmissionCreate(BaseModel):
    problem_id: str
    source_code: str = Field(..., min_length=1)
    language: str = Field("java")

    @field_validator("problem_id")
    @classmethod
    def validate_problem_id_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("problem_id must be a valid UUID")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        lang = v.strip().lower()
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{v}'. Must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}")
        return lang

    @field_validator("source_code")
    @classmethod
    def check_size(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("source_code cannot be empty or whitespace only")
        if len(v.encode()) > settings.max_source_code_bytes or len(v) > 20000:
            raise ValueError("source code exceeds maximum length")
        return v


class TestCaseResult(BaseModel):
    test_case_id: str
    passed: bool
    input: str
    expected: str
    actual: str


class BenchmarkPoint(BaseModel):
    input_size: int
    runtime_ms: float
    timed_out: bool


class SubmissionResponse(BaseModel):
    id: str
    status: str
    problem_id: Optional[str] = None
    source_code: Optional[str] = None
    language: Optional[str] = "java"
    empirical_complexity: Optional[str] = None
    confidence_score: Optional[float] = None
    structural_hint: Optional[str] = None
    failure_detail: Optional[str] = None
    test_results: Optional[List[TestCaseResult]] = None
    benchmark_curve: Optional[List[BenchmarkPoint]] = None
    optimal_solution: Optional[str] = None
    optimal_time_complexity: Optional[str] = None
    optimal_space_complexity: Optional[str] = None

    model_config = {"from_attributes": True}


class SubmissionHistoryItem(BaseModel):
    id: str
    problem_id: Optional[str] = None
    problem_title: str
    status: str
    language: Optional[str] = "java"
    empirical_complexity: Optional[str] = None
    confidence_score: Optional[float] = None
    submitted_at: datetime
    source_code: Optional[str] = None

    model_config = {"from_attributes": True}


class RunCodeRequest(BaseModel):
    problem_id: str
    source_code: str = Field(..., min_length=1)
    language: str = Field("python")

    @field_validator("problem_id")
    @classmethod
    def validate_problem_id_uuid(cls, v: str) -> str:
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("problem_id must be a valid UUID")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        lang = v.strip().lower()
        if lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language '{v}'. Must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}")
        return lang


class TestCaseRunOutcome(BaseModel):
    test_case_id: Optional[str] = None
    passed: bool
    input: str
    expected_output: str
    actual_output: str
    verdict: str


class RunCodeResponse(BaseModel):
    verdict: str  # Accepted | Wrong Answer | Compilation Error | Runtime Error | Time Limit Exceeded
    failure_detail: Optional[str] = None
    test_cases: List[TestCaseRunOutcome] = []


