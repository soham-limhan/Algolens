"""
app/services/pipeline.py — Full submission pipeline orchestration.

Sequence:
  1. Compile (via CompiledSubmission)
  2. Correctness check against fixed test cases — gates everything that follows
  3. If all tests pass: benchmark across scaled input sizes
  4. Classify empirical complexity from timing data
  5. If gap exists (empirical worse than optimal): match structural hint patterns
  6. Persist all results; update Submission.status to 'complete' or 'failed'

Design invariants (from AI_CONTEXT.md / ARCHITECTURE.md):
  - Correctness MUST gate benchmarking. A failing submission produces zero
    BenchmarkRun rows — asserted explicitly in the integration test suite.
  - CompiledSubmission is the ONE sandbox primitive, reused for both correctness
    and benchmarking. No second execution path.
  - Structural hints only run when a gap is detected — efficiency gate, not
    a technical dependency.
  - Status transitions are logged at each stage.
"""
from __future__ import annotations

import logging
from typing import List

from sqlalchemy.orm import Session

from app.models.problem import InefficiencySignature, Problem, TestCase
from app.models.submission import BenchmarkRun, Submission
from app.problems_data.registry import get_generator
from app.sandbox.executor import CompiledSubmission, SandboxLimits
from app.services.benchmark import run_benchmark
from app.services.complexity import ClassificationResult, classify, is_gap
from app.services.correctness import CorrectnessResult, run_correctness_check
from app.services.hints import get_structural_hint

logger = logging.getLogger(__name__)


def _set_status(db: Session, submission: Submission, status: str) -> None:
    submission.status = status
    db.commit()
    logger.info("[submission %s] status → %s", submission.id, status)


def run_pipeline(submission_id: str, db: Session) -> None:
    """
    Execute the full judging pipeline for a submission.

    This function is called as a FastAPI BackgroundTask — it runs in a thread
    and manages its own DB session commit lifecycle.
    """
    submission = db.get(Submission, submission_id)
    if submission is None:
        logger.error("run_pipeline called with unknown submission_id=%s", submission_id)
        return

    problem = db.get(Problem, submission.problem_id)
    if problem is None:
        logger.error("Problem %s not found for submission %s", submission.problem_id, submission_id)
        submission.status = "failed"
        submission.failure_detail = "Internal error: problem not found"
        db.commit()
        return

    logger.info(
        "[submission %s] pipeline start — problem='%s'",
        submission_id, problem.title,
    )

    # ── Stage 1: Compile ────────────────────────────────────────────────────
    _set_status(db, submission, "running_correctness")
    compiled = CompiledSubmission(submission.source_code, language=submission.language)

    test_cases: List[TestCase] = problem.test_cases

    # ── Stage 2: Correctness ────────────────────────────────────────────────
    correctness: CorrectnessResult = run_correctness_check(
        compiled, test_cases, limits=SandboxLimits(wall_timeout_s=5.0)
    )

    if correctness.verdict != "Accepted":
        submission.status = "failed"
        submission.failure_detail = correctness.failure_detail
        db.commit()
        logger.info(
            "[submission %s] failed correctness — verdict=%s",
            submission_id, correctness.verdict,
        )
        compiled.cleanup()
        return

    logger.info("[submission %s] correctness passed — %d test cases", submission_id, len(test_cases))

    # ── Stage 3: Benchmark ──────────────────────────────────────────────────
    _set_status(db, submission, "benchmarking")
    try:
        generator_fn = get_generator(problem.generator_key)
    except KeyError as e:
        logger.error("[submission %s] generator not found: %s", submission_id, e)
        submission.status = "failed"
        submission.failure_detail = f"Internal error: no generator for '{problem.generator_key}'"
        db.commit()
        compiled.cleanup()
        return

    benchmark_points = run_benchmark(compiled, generator_fn)
    compiled.cleanup()

    # Persist BenchmarkRun rows (only created on an Accepted submission — invariant)
    for point in benchmark_points:
        db.add(BenchmarkRun(
            submission_id=submission_id,
            input_size=point.input_size,
            runtime_ms=point.runtime_ms,
            timed_out=point.timed_out,
        ))
    db.commit()
    logger.info("[submission %s] benchmark complete — %d points", submission_id, len(benchmark_points))

    # ── Stage 4: Complexity classification ──────────────────────────────────
    classification: ClassificationResult = classify(benchmark_points)
    submission.empirical_complexity = classification.complexity_class
    submission.confidence_score = classification.confidence

    # ── Stage 5: Structural hints (only when gap exists) ────────────────────
    if is_gap(classification.complexity_class, problem.optimal_time_complexity):
        logger.info(
            "[submission %s] complexity gap — empirical=%s optimal=%s",
            submission_id, classification.complexity_class, problem.optimal_time_complexity,
        )
        signatures: List[InefficiencySignature] = problem.inefficiency_signatures
        hint = get_structural_hint(submission.source_code, signatures)
        submission.structural_hint = hint
        if hint:
            logger.info("[submission %s] structural hint matched", submission_id)
        else:
            logger.info("[submission %s] no structural hint matched", submission_id)
    else:
        logger.info(
            "[submission %s] no complexity gap — empirical=%s optimal=%s",
            submission_id, classification.complexity_class, problem.optimal_time_complexity,
        )

    # ── Stage 6: Finalize ───────────────────────────────────────────────────
    submission.status = "complete"
    db.commit()
    logger.info("[submission %s] pipeline complete", submission_id)
