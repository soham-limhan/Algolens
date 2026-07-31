"""
tests/test_complexity_classifier.py — Unit tests for the complexity classifier.

Uses synthetic (n, runtime_ms) data generated from known mathematical functions
with small noise added — NOT real Java runs. This isolates the classifier logic
from sandbox/hardware variability.
"""
from __future__ import annotations

import math
import random

import pytest

from app.services.benchmark import BenchmarkPoint
from app.services.complexity import ClassificationResult, classify, is_gap


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
