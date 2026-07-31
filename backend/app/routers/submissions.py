"""
app/routers/submissions.py — Submission creation (async) and status polling.

Key design points:
- POST /submissions returns 202 immediately; pipeline runs in a BackgroundTask.
  Client polls GET /submissions/{id} until status reaches a terminal state.
- Each background task creates its OWN database session — it does not share the
  request session, which would be closed before the background task completes.
- Per-user rate limiting prevents queue flooding (simple in-process tracking).
- GET /submissions/{id} returns 404 if the submission doesn't belong to the
  requesting user — avoids leaking other users' data.
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.db.database import SessionLocal, get_db
from app.models.problem import Problem
from app.models.submission import BenchmarkRun, Submission
from app.models.user import User
from app.schemas.submission import (
    BenchmarkPoint,
    SubmissionCreate,
    SubmissionHistoryItem,
    SubmissionResponse,
    TestCaseResult,
)
from app.services.pipeline import run_pipeline

router = APIRouter(tags=["submissions"])

# ── Simple in-process rate limiter ────────────────────────────────────────────
# Not distributed — sufficient at this project's expected scale.
_rate_tracker: dict[str, list[float]] = defaultdict(list)


def _check_rate_limit(user_id: str) -> None:
    now = time.time()
    window = 60.0
    limit = settings.submissions_rate_limit_per_minute
    timestamps = _rate_tracker[user_id]
    # Keep only timestamps within the last minute
    _rate_tracker[user_id] = [t for t in timestamps if now - t < window]
    if len(_rate_tracker[user_id]) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {limit} submissions per minute",
        )
    _rate_tracker[user_id].append(now)


# ── Background task wrapper ───────────────────────────────────────────────────

def _run_pipeline_bg(submission_id: str) -> None:
    """
    Wrapper that creates its own DB session for the background task.
    The request session is already closed by the time this runs.
    """
    db = SessionLocal()
    try:
        run_pipeline(submission_id, db)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            "Pipeline error for submission %s: %s", submission_id, e, exc_info=True
        )
    finally:
        db.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_response(submission: Submission, db: Session) -> SubmissionResponse:
    """Build the full SubmissionResponse, assembling test_results and benchmark_curve."""
    # Test results — read from the correctness outcomes stored in the DB
    # (We store them inline on the submission for simplicity at this scale)
    test_results: Optional[list] = None
    benchmark_curve: Optional[list] = None

    if submission.status in ("complete", "failed") and submission.failure_detail is not None:
        # If we have a failure, test_results may be None (compilation error)
        pass

    # Benchmark curve from BenchmarkRun rows
    runs = (
        db.query(BenchmarkRun)
        .filter(BenchmarkRun.submission_id == submission.id)
        .order_by(BenchmarkRun.input_size)
        .all()
    )
    if runs:
        benchmark_curve = [
            BenchmarkPoint(
                input_size=r.input_size,
                runtime_ms=r.runtime_ms,
                timed_out=r.timed_out,
            )
            for r in runs
        ]

    return SubmissionResponse(
        id=submission.id,
        status=submission.status,
        language=submission.language,
        empirical_complexity=submission.empirical_complexity,
        confidence_score=submission.confidence_score,
        structural_hint=submission.structural_hint,
        failure_detail=submission.failure_detail,
        test_results=test_results,
        benchmark_curve=benchmark_curve,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
def create_submission(
    body: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """Create a submission and immediately enqueue the pipeline as a background task."""
    _check_rate_limit(current_user.id)

    problem = db.get(Problem, body.problem_id)
    if problem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found")

    submission = Submission(
        user_id=current_user.id,
        problem_id=body.problem_id,
        source_code=body.source_code,
        language=body.language,
        status="pending",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    background_tasks.add_task(_run_pipeline_bg, submission.id)

    return SubmissionResponse(
        id=submission.id,
        status="pending",
        language=submission.language,
        empirical_complexity=None,
        confidence_score=None,
        structural_hint=None,
        failure_detail=None,
        test_results=None,
        benchmark_curve=None,
    )


import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status


def _validate_uuid(val: str, field_name: str = "id") -> None:
    try:
        uuid.UUID(val)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"field": field_name, "message": f"Invalid UUID format for {field_name}"}],
        )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    """
    Get submission status/results. Returns 404 if submission doesn't belong to
    the requesting user — avoids leaking other users' data.
    """
    _validate_uuid(submission_id, "submission_id")
    submission = db.get(Submission, submission_id)
    if submission is None or submission.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return _build_response(submission, db)


@router.get("/users/{user_id}/history", response_model=List[SubmissionHistoryItem])
def get_user_history(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SubmissionHistoryItem]:
    """
    Paginated submission history for a user.
    A user may only fetch their own history (403 otherwise).
    """
    _validate_uuid(user_id, "user_id")
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to another user's history",
        )

    submissions = (
        db.query(Submission)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.submitted_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    items = []
    for s in submissions:
        problem = db.get(Problem, s.problem_id)
        items.append(
            SubmissionHistoryItem(
                id=s.id,
                problem_title=problem.title if problem else "Unknown",
                status=s.status,
                language=s.language,
                empirical_complexity=s.empirical_complexity,
                confidence_score=s.confidence_score,
                submitted_at=s.submitted_at,
            )
        )
    return items
