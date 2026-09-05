"""app/schemas/problem.py — Pydantic models for problem endpoints."""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class ProblemSummary(BaseModel):
    id: str
    title: str
    difficulty: str

    model_config = {"from_attributes": True}


class TestCaseSummary(BaseModel):
    id: Optional[str] = None
    input: str
    expected_output: str

    model_config = {"from_attributes": True}


class ProblemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    difficulty: str = "easy"  # easy | medium | hard
    optimal_time_complexity: Optional[str] = "O(n)"
    optimal_space_complexity: Optional[str] = "O(1)"
    optimal_solution: Optional[str] = None
    generator_key: Optional[str] = "two_sum"
    test_cases: List[TestCaseSummary] = []


class ProblemDetail(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    optimal_time_complexity: str
    optimal_space_complexity: str
    optimal_solution: Optional[str] = None
    test_cases: List[TestCaseSummary] = []

    model_config = {"from_attributes": True}
