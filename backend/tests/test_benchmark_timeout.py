"""
tests/test_benchmark_timeout.py — Unit tests for the 10-second total benchmark budget
and the AI complexity classification fallback.
"""
from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from app.config import Settings
from app.models.problem import Problem, TestCase
from app.models.submission import Submission
from app.sandbox.executor import CompiledSubmission, SandboxResult
from app.services.benchmark import BenchmarkPoint, BenchmarkResult, run_benchmark
from app.services.complexity import ClassificationResult


def test_config_benchmark_total_timeout_s_validation():
    # Valid timeout
    s = Settings(benchmark_total_timeout_s=10.0)
    assert s.benchmark_total_timeout_s == 10.0

    # Invalid timeout <= 0
    with pytest.raises(ValueError, match="BENCHMARK_TOTAL_TIMEOUT_S must be greater than 0"):
        Settings(benchmark_total_timeout_s=0.0)

    with pytest.raises(ValueError, match="BENCHMARK_TOTAL_TIMEOUT_S must be greater than 0"):
        Settings(benchmark_total_timeout_s=-5.0)


def test_run_benchmark_fast_completes_within_budget():
    mock_compiled = MagicMock(spec=CompiledSubmission)
    # Fast runs returning 2.0ms
    mock_compiled.run.return_value = SandboxResult(
        stdout="ok", stderr="", exit_code=0, runtime_ms=2.0, timed_out=False
    )
    generator = lambda n, seed: f"{n}\n"

    result = run_benchmark(
        compiled=mock_compiled,
        generator=generator,
        input_sizes=[100, 1000, 10000],
        repetitions=2,
        warmup_runs=1,
        total_timeout_s=10.0,
    )

    assert isinstance(result, BenchmarkResult)
    assert result.completed_within_budget is True
    assert len(result.points) == 3
    assert all(not p.timed_out for p in result.points)
    assert all(p.runtime_ms == 2.0 for p in result.points)


def test_run_benchmark_exceeding_total_timeout_halts_and_marks_remaining():
    mock_compiled = MagicMock(spec=CompiledSubmission)

    def side_effect(stdin_data, limits):
        # Fast for size 100
        if "100\n" in stdin_data:
            return SandboxResult(stdout="ok", stderr="", exit_code=0, runtime_ms=1.0, timed_out=False)
        # Slow for size 1000, sleep past total budget
        time.sleep(0.4)
        return SandboxResult(stdout="", stderr="", exit_code=124, runtime_ms=0.0, timed_out=True)

    mock_compiled.run.side_effect = side_effect
    generator = lambda n, seed: f"{n}\n"

    # Set total_timeout_s = 0.3s so size 100 succeeds quickly and size 1000 causes total timeout
    result = run_benchmark(
        compiled=mock_compiled,
        generator=generator,
        input_sizes=[100, 1000, 10000],
        repetitions=2,
        warmup_runs=1,
        total_timeout_s=0.30,
    )

    assert isinstance(result, BenchmarkResult)
    assert result.completed_within_budget is False
    assert len(result.points) == 3
    # First point should succeed
    assert result.points[0].input_size == 100
    assert result.points[0].timed_out is False
    # Subsequent points should be marked as timed out
    assert result.points[1].timed_out is True
    assert result.points[2].timed_out is True


def test_pipeline_branches_to_classify_when_within_budget():
    from app.services.pipeline import run_pipeline

    db = MagicMock()
    submission = Submission(
        id="sub-123",
        user_id="user-1",
        problem_id="prob-1",
        source_code="print('hello')",
        language="python",
        status="pending",
    )

    problem = Problem(
        id="prob-1",
        title="Two Sum",
        difficulty="easy",
        description="Test problem",
        generator_key="two_sum",
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(n)",
    )
    problem.test_cases = [TestCase(id="tc-1", problem_id="prob-1", input="1", expected_output="1")]
    problem.inefficiency_signatures = []

    def db_get(model, id_val):
        if model == Submission:
            return submission
        if model == Problem:
            return problem
        return None

    db.get.side_effect = db_get

    with patch("app.services.pipeline.CompiledSubmission") as MockCompiled, \
         patch("app.services.pipeline.run_correctness_check") as mock_correctness, \
         patch("app.services.pipeline.run_benchmark") as mock_benchmark, \
         patch("app.services.pipeline.classify") as mock_classify, \
         patch("app.services.pipeline.classify_with_ai") as mock_classify_ai:

        mock_correctness.return_value = MagicMock(verdict="Accepted", failure_detail=None)

        points = [
            BenchmarkPoint(input_size=100, runtime_ms=1.0, timed_out=False),
            BenchmarkPoint(input_size=1000, runtime_ms=10.0, timed_out=False),
        ]
        # Benchmark completed within budget
        mock_benchmark.return_value = BenchmarkResult(
            points=points, completed_within_budget=True, total_duration_s=0.5
        )
        mock_classify.return_value = ClassificationResult(
            complexity_class="O(n)",
            confidence=0.99,
            reasoning="Empirically verified",
            evaluated_by="empirical_benchmark",
        )

        run_pipeline("sub-123", db)

        # classify should have been called, and classify_with_ai should NOT have been called
        mock_classify.assert_called_once_with(points)
        mock_classify_ai.assert_not_called()
        assert submission.empirical_complexity == "O(n)"


def test_pipeline_branches_to_classify_ai_when_budget_exceeded():
    from app.services.pipeline import run_pipeline

    db = MagicMock()
    submission = Submission(
        id="sub-456",
        user_id="user-1",
        problem_id="prob-1",
        source_code="nested loops",
        language="python",
        status="pending",
    )

    problem = Problem(
        id="prob-1",
        title="Two Sum",
        difficulty="easy",
        description="Test problem",
        generator_key="two_sum",
        optimal_time_complexity="O(n)",
        optimal_space_complexity="O(n)",
    )
    problem.test_cases = [TestCase(id="tc-1", problem_id="prob-1", input="1", expected_output="1")]
    problem.inefficiency_signatures = []

    def db_get(model, id_val):
        if model == Submission:
            return submission
        if model == Problem:
            return problem
        return None

    db.get.side_effect = db_get

    with patch("app.services.pipeline.CompiledSubmission") as MockCompiled, \
         patch("app.services.pipeline.run_correctness_check") as mock_correctness, \
         patch("app.services.pipeline.run_benchmark") as mock_benchmark, \
         patch("app.services.pipeline.classify") as mock_classify, \
         patch("app.services.pipeline.classify_with_ai") as mock_classify_ai:

        mock_correctness.return_value = MagicMock(verdict="Accepted", failure_detail=None)

        points = [
            BenchmarkPoint(input_size=100, runtime_ms=1.0, timed_out=False),
            BenchmarkPoint(input_size=1000, runtime_ms=0.0, timed_out=True),
        ]
        # Benchmark exceeded budget / timed out
        mock_benchmark.return_value = BenchmarkResult(
            points=points, completed_within_budget=False, total_duration_s=10.0
        )
        mock_classify_ai.return_value = ClassificationResult(
            complexity_class="O(n^2)",
            confidence=0.98,
            reasoning="Evaluated via AI due to timeout",
            evaluated_by="ai",
        )

        run_pipeline("sub-456", db)

        # classify_with_ai should have been called, and classify should NOT have been called
        mock_classify.assert_not_called()
        mock_classify_ai.assert_called_once()
        assert submission.empirical_complexity == "O(n^2)"
