"""
tests/test_complexity_classifier.py — Unit tests for the complexity classifier.

Uses synthetic (n, runtime_ms) data generated from known mathematical functions
with small noise added — NOT real Java runs. This isolates the classifier logic
from sandbox/hardware variability.
"""
from __future__ import annotations

import math
import random

from unittest.mock import MagicMock, patch

import pytest

from app.services.benchmark import BenchmarkPoint
from app.services.complexity import (
    ClassificationResult,
    classify,
    classify_with_ai,
    is_gap,
    normalize_complexity_class,
)


def _make_points(fn, sizes=None, noise=0.05, seed=42):
    """Generate BenchmarkPoints from a mathematical function with small noise."""
    if sizes is None:
        sizes = [100, 1000, 5000, 10000, 50000, 100000]
    rng = random.Random(seed)
    points = []
    for n in sizes:
        t = fn(n) * (1 + rng.uniform(-noise, noise))
        points.append(BenchmarkPoint(input_size=n, runtime_ms=max(0.001, t), timed_out=False))
    return points


class TestClassifyO1:
    def test_constant(self):
        points = _make_points(lambda n: 5.0)
        result = classify(points)
        assert result.complexity_class == "O(1)"
        assert result.confidence > 0.5

class TestClassifyOLogN:
    def test_log(self):
        points = _make_points(lambda n: 2 * math.log2(n))
        result = classify(points)
        assert result.complexity_class == "O(log n)"

class TestClassifyON:
    def test_linear(self):
        points = _make_points(lambda n: 0.001 * n)
        result = classify(points)
        assert result.complexity_class == "O(n)"

    def test_linear_various_constants(self):
        for c in [0.0001, 0.001, 0.01]:
            points = _make_points(lambda n, c=c: c * n)
            result = classify(points)
            assert result.complexity_class == "O(n)", f"c={c}"

class TestClassifyONLogN:
    def test_n_log_n(self):
        points = _make_points(lambda n: 0.0001 * n * math.log2(n))
        result = classify(points)
        assert result.complexity_class in ("O(n log n)", "O(n)"), (
            f"Expected O(n log n) or O(n) for n*log(n), got {result.complexity_class}"
        )

class TestClassifyON2:
    def test_quadratic(self):
        points = _make_points(lambda n: 1e-7 * n ** 2,
                              sizes=[100, 500, 1000, 2000, 5000, 10000])
        result = classify(points)
        assert result.complexity_class == "O(n^2)"

class TestEdgeCases:
    def test_insufficient_data_single_point(self):
        points = [BenchmarkPoint(input_size=100, runtime_ms=5.0, timed_out=False)]
        result = classify(points)
        assert result.insufficient_data is True
        assert result.confidence == 0.0

    def test_insufficient_data_all_timed_out(self):
        points = [
            BenchmarkPoint(input_size=100, runtime_ms=0.0, timed_out=True),
            BenchmarkPoint(input_size=1000, runtime_ms=0.0, timed_out=True),
        ]
        result = classify(points)
        assert result.insufficient_data is True

    def test_empty_points(self):
        result = classify([])
        assert result.insufficient_data is True

class TestIsGap:
    def test_gap_n2_vs_n(self):
        assert is_gap("O(n^2)", "O(n)") is True

    def test_no_gap_n_vs_n(self):
        assert is_gap("O(n)", "O(n)") is False

    def test_no_gap_n_vs_n2(self):
        # Solution is better than optimal — no gap (and this shouldn't happen in practice)
        assert is_gap("O(n)", "O(n^2)") is False

    def test_gap_exponential_vs_linear(self):
        assert is_gap("O(2^n)", "O(n)") is True

    def test_unknown_class(self):
        # Unknown class — should return False gracefully
        assert is_gap("O(unknown)", "O(n)") is False


class TestNormalizeComplexityClass:
    def test_canonical_classes(self):
        for c in ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]:
            assert normalize_complexity_class(c) == c

    def test_uppercase_variants(self):
        assert normalize_complexity_class("O(N)") == "O(n)"
        assert normalize_complexity_class("O(N^2)") == "O(n^2)"
        assert normalize_complexity_class("O(N LOG N)") == "O(n log n)"
        assert normalize_complexity_class("O(LOG N)") == "O(log n)"
        assert normalize_complexity_class("O(2^N)") == "O(2^n)"

    def test_alternative_syntaxes(self):
        assert normalize_complexity_class("O(n*log(n))") == "O(n log n)"
        assert normalize_complexity_class("O(logn)") == "O(log n)"
        assert normalize_complexity_class("quadratic") == "O(n^2)"
        assert normalize_complexity_class("linear") == "O(n)"
        assert normalize_complexity_class("constant") == "O(1)"
        assert normalize_complexity_class("cubic") == "O(n^3)"
        assert normalize_complexity_class("exponential") == "O(2^n)"


class TestClassifyWithAI:
    def test_missing_groq_key_falls_back_to_mathematical(self):
        points = _make_points(lambda n: 0.001 * n)
        with patch("app.config.settings.groq_api_key", ""):
            res = classify_with_ai(
                source_code="def f(n): return n",
                language="python",
                points=points,
                api_key_override="",
            )
            assert res.evaluated_by == "mathematical_fallback"
            assert res.complexity_class == "O(n)"
            assert "mathematical" in (res.reasoning or "").lower()

    def test_empty_source_code_falls_back(self):
        points = _make_points(lambda n: 0.001 * n)
        res = classify_with_ai(
            source_code="   ",
            language="python",
            points=points,
            api_key_override="mock_key",
        )
        assert res.evaluated_by == "mathematical_fallback"

    def test_successful_ai_evaluation(self):
        points = [
            BenchmarkPoint(input_size=100, runtime_ms=0.1, timed_out=False),
            BenchmarkPoint(input_size=1000, runtime_ms=1.1, timed_out=False),
            BenchmarkPoint(input_size=10000, runtime_ms=10.5, timed_out=False),
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"complexity_class": "O(N)", "confidence": 0.98, "reasoning": "Single loop of size N with O(1) operations, supported by linear scaling across benchmark points."}'
                    }
                }
            ]
        }

        with patch("httpx.Client.post", return_value=mock_response):
            res = classify_with_ai(
                source_code="for i in range(len(nums)): print(i)",
                language="python",
                points=points,
                problem_title="Linear Scan",
                optimal_complexity="O(n)",
                api_key_override="mock_key",
            )
            assert res.evaluated_by == "ai"
            assert res.complexity_class == "O(n)"
            assert res.confidence == 0.98
            assert "Single loop" in res.reasoning

    def test_groq_api_error_falls_back_gracefully(self):
        points = _make_points(lambda n: 0.001 * n)
        with patch("httpx.Client.post", side_effect=Exception("Connection timed out")):
            res = classify_with_ai(
                source_code="def solve(nums): return nums[0]",
                language="python",
                points=points,
                api_key_override="mock_key",
            )
            assert res.evaluated_by == "mathematical_fallback"
            assert res.complexity_class in ("O(n)", "O(1)")
            assert res.confidence is not None
