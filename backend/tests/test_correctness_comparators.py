"""
tests/test_correctness_comparators.py — Table-driven unit tests for comparators.

These test the comparator functions directly — no sandbox invocation needed.
"""
from __future__ import annotations

import pytest

from app.services.correctness import _exact, _numeric_tolerance, _sorted_tokens


class TestExactComparator:
    def test_match(self):
        assert _exact("hello", "hello") is True

    def test_mismatch(self):
        assert _exact("hello", "world") is False

    def test_trailing_whitespace_normalized(self):
        assert _exact("0 1\n", "0 1") is True

    def test_whitespace_only_difference(self):
        assert _exact("  hello  \n", "hello") is True

    def test_newline_mismatch(self):
        # Genuinely different content
        assert _exact("hello\nworld", "hello") is False

    def test_multiline_match(self):
        assert _exact("1 6\n8 10\n15 18", "1 6\n8 10\n15 18") is True


class TestSortedTokensComparator:
    def test_same_order(self):
        assert _sorted_tokens("0 1", "0 1") is True

    def test_different_order(self):
        assert _sorted_tokens("0 1", "1 0") is True

    def test_genuinely_different(self):
        assert _sorted_tokens("0 1", "0 2") is False

    def test_different_count(self):
        assert _sorted_tokens("0 1 2", "0 1") is False

    def test_empty(self):
        assert _sorted_tokens("", "") is True


class TestNumericToleranceComparator:
    def test_exact_match(self):
        assert _numeric_tolerance("1.0 2.0", "1.0 2.0") is True

    def test_within_tolerance(self):
        # 1.000005 is within 1e-5 relative of 1.0
        assert _numeric_tolerance("1.0", "1.000005") is True

    def test_outside_tolerance(self):
        assert _numeric_tolerance("1.0", "1.1") is False

    def test_different_count(self):
        assert _numeric_tolerance("1.0 2.0", "1.0") is False

    def test_non_numeric(self):
        assert _numeric_tolerance("hello", "world") is False

    def test_zero_values(self):
        assert _numeric_tolerance("0.0", "0.0") is True
