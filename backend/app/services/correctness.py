"""
app/services/correctness.py — Verify a submission's output against fixed test cases.

Design notes:
- Comparators are dispatched via a dict (_COMPARATORS), not an if/elif chain.
  Adding a new comparator type is additive — no change to existing dispatch logic.
- Verdict states are specific (Accepted / Wrong Answer / Compilation Error /
  Runtime Error / Time Limit Exceeded), not a boolean. Collapsing them is the
  class of bug fixed in CHANGELOG.md 0.4.1 — don't do it.
- Correctness gates benchmarking: this service is called first, and benchmarking
  only runs on a fully-Accepted result.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional

from app.models.problem import TestCase
from app.sandbox.executor import CompiledSubmission, SandboxLimits

logger = logging.getLogger(__name__)


@dataclass
class TestCaseOutcome:
    test_case_id: str
    passed: bool
    input: str
    expected: str
    actual: str
    verdict: str  # "Accepted" | "Wrong Answer" | "Runtime Error" | "Time Limit Exceeded"


@dataclass
class CorrectnessResult:
    verdict: str  # Overall: Accepted | Wrong Answer | Compilation Error | Runtime Error | TLE
    failure_detail: Optional[str]
    test_outcomes: List[TestCaseOutcome]


# ── Comparators ───────────────────────────────────────────────────────────────

def _exact(expected: str, actual: str) -> bool:
    """Exact match after stripping trailing whitespace from each line."""
    def _normalize(s: str) -> str:
        return "\n".join(line.rstrip() for line in s.strip().splitlines())
    return _normalize(expected) == _normalize(actual)


def _sorted_tokens(expected: str, actual: str) -> bool:
    """Order-independent token match — both token sets must be identical."""
    return sorted(expected.split()) == sorted(actual.split())


def _numeric_tolerance(expected: str, actual: str, tol: float = 1e-5) -> bool:
    """Floating-point comparison within relative tolerance."""
    try:
        exp_vals = list(map(float, expected.split()))
        act_vals = list(map(float, actual.split()))
        if len(exp_vals) != len(act_vals):
            return False
        return all(
            abs(e - a) <= tol * max(1.0, abs(e)) for e, a in zip(exp_vals, act_vals)
        )
    except ValueError:
        return False


_COMPARATORS = {
    "exact": _exact,
    "sorted": _sorted_tokens,
    "numeric_tolerance": _numeric_tolerance,
}


def _compare(comparator_type: str, expected: str, actual: str) -> bool:
    fn = _COMPARATORS.get(comparator_type)
    if fn is None:
        logger.warning("Unknown comparator type '%s', falling back to exact", comparator_type)
        fn = _exact
    return fn(expected, actual)


# ── Main entry point ──────────────────────────────────────────────────────────

def run_correctness_check(
    compiled: CompiledSubmission,
    test_cases: List[TestCase],
    limits: Optional[SandboxLimits] = None,
) -> CorrectnessResult:
    """
    Run the compiled submission against all fixed test cases.

    Returns a CorrectnessResult with a specific verdict — never a boolean.

    Important: an empty test_cases list is treated as a configuration error,
    not a vacuous Accepted. (Vacuous all() over empty list is the exact failure
    mode from CHANGELOG.md 0.4.1 — this check targets it explicitly.)
    """
    if compiled.compilation_error:
        return CorrectnessResult(
            verdict="Compilation Error",
            failure_detail=compiled.compiler_output,
            test_outcomes=[],
        )

    if not test_cases:
        logger.error("Problem has zero test cases — cannot judge correctness.")
        return CorrectnessResult(
            verdict="Runtime Error",
            failure_detail="Configuration error: this problem has no test cases loaded.",
            test_outcomes=[],
        )

    if limits is None:
        limits = SandboxLimits(wall_timeout_s=5.0)

    outcomes: List[TestCaseOutcome] = []
    first_failure: Optional[str] = None

    for tc in test_cases:
        result = compiled.run(stdin_data=tc.input, limits=limits)

        if result.timed_out:
            verdict = "Time Limit Exceeded"
            actual = ""
            passed = False
        elif result.exit_code != 0:
            verdict = "Runtime Error"
            actual = result.stderr.strip()
            passed = False
        else:
            actual = result.stdout.strip()
            expected = tc.expected_output.strip()
            passed = _compare(tc.comparator_type, expected, actual)
            verdict = "Accepted" if passed else "Wrong Answer"

        outcome = TestCaseOutcome(
            test_case_id=tc.id,
            passed=passed,
            input=tc.input,
            expected=tc.expected_output,
            actual=actual,
            verdict=verdict,
        )
        outcomes.append(outcome)

        if not passed and first_failure is None:
            first_failure = outcome

    failed = [o for o in outcomes if not o.passed]
    if not failed:
        return CorrectnessResult(
            verdict="Accepted",
            failure_detail=None,
            test_outcomes=outcomes,
        )

    # Build failure detail from first failing case
    ff = failed[0]
    detail = (
        f"{len(failed)} of {len(outcomes)} test case(s) failed. "
        f"First failing case — verdict: {ff.verdict}"
    )
    if ff.verdict == "Wrong Answer":
        detail += f", expected: '{ff.expected.strip()}', got: '{ff.actual.strip()}'"
    elif ff.verdict == "Runtime Error":
        detail += f", stderr: {ff.actual[:500]}"

    return CorrectnessResult(
        verdict=ff.verdict,
        failure_detail=detail,
        test_outcomes=outcomes,
    )
