"""app/routers/problems.py — Problem list, creation, and detail endpoints."""
from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.models.problem import Problem, TestCase
from app.schemas.problem import ProblemCreate, ProblemDetail, ProblemSummary
from app.services.cache import cache_service

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=List[ProblemSummary])
def list_problems(db: Session = Depends(get_db)) -> List[ProblemSummary]:
    """List all problems with Redis caching."""
    cache_key = "problems:list"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return [ProblemSummary.model_validate(p) for p in cached]

    problems = db.query(Problem).order_by(Problem.title).all()
    summaries = [ProblemSummary.model_validate(p) for p in problems]
    cache_service.set(
        cache_key,
        [s.model_dump() for s in summaries],
        ttl=settings.cache_ttl_problems,
    )
    return summaries


@router.post("", response_model=ProblemDetail, status_code=status.HTTP_201_CREATED)
def create_problem(body: ProblemCreate, db: Session = Depends(get_db)) -> ProblemDetail:
    """Create a new problem in the database and invalidate problems cache."""
    diff = body.difficulty.lower()
    if diff not in ("easy", "medium", "hard"):
        diff = "easy"

    problem = Problem(
        title=body.title.strip(),
        description=body.description.strip(),
        difficulty=diff,
        optimal_time_complexity=body.optimal_time_complexity or "O(n)",
        optimal_space_complexity=body.optimal_space_complexity or "O(1)",
        generator_key=body.generator_key or "two_sum",
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    if body.test_cases:
        for tc in body.test_cases:
            test_case = TestCase(
                problem_id=problem.id,
                input=tc.input,
                expected_output=tc.expected_output,
                comparator_type="exact",
            )
            db.add(test_case)
        db.commit()
        db.refresh(problem)

    # Invalidate problems cache
    cache_service.delete_pattern("problems:*")

    return ProblemDetail.model_validate(problem)


@router.get("/{problem_id}", response_model=ProblemDetail)
def get_problem(problem_id: str, db: Session = Depends(get_db)) -> ProblemDetail:
    """Get single problem detail with Redis caching."""
    clean_id = problem_id.strip().lower()
    cache_key = f"problems:detail:{clean_id}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return ProblemDetail.model_validate(cached)

    # 1. Direct ID lookup
    problem = db.get(Problem, problem_id)

    # 2. Lookup by title or numerical ID string
    if problem is None:
        problem = db.query(Problem).filter(
            (func.lower(Problem.title) == clean_id) |
            (func.lower(Problem.title).like(f"{clean_id}.%")) |
            (func.lower(Problem.title).like(f"%{clean_id}%"))
        ).first()

    if problem is None:
        try:
            uuid.UUID(problem_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=[{"field": "problem_id", "message": "Invalid UUID format for problem_id"}],
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    detail = ProblemDetail.model_validate(problem)
    cache_service.set(cache_key, detail.model_dump(), ttl=settings.cache_ttl_problem_detail)
    # Also cache under the problem's canonical UUID
    if str(problem.id).lower() != clean_id:
        cache_service.set(f"problems:detail:{str(problem.id).lower()}", detail.model_dump(), ttl=settings.cache_ttl_problem_detail)

    return detail

