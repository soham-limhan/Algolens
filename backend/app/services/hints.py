"""
app/services/hints.py — Structural inefficiency pattern detector.

Design notes:
- Pattern detection is regex/token-based, not full AST parsing — can misfire on
  code that's structurally similar to a known inefficiency but contextually necessary.
  This is a known limitation (see ARCHITECTURE.md) accepted for v1.
- Hints only run when the complexity classifier has already found a gap — this is an
  efficiency gate, not a technical dependency. Don't remove the gate.
- Each pattern_type in InefficiencySignature maps to a detector function here.
  Adding a new pattern type is additive: add the function and add it to _DETECTORS.
- hint_text lives in the database (per-problem, specific), not hardcoded here.
  The detector just says whether the pattern is present; the database row provides
  the actual text to show the learner.
"""
from __future__ import annotations

import logging
import re
from typing import Callable, List, Optional

from app.models.problem import InefficiencySignature

logger = logging.getLogger(__name__)


# ── Pattern detectors ─────────────────────────────────────────────────────────

def _detect_nested_loop_lookup(source_code: str) -> bool:
    """
    Detect a nested loop used to search/look up values — the hallmark of O(n²)
    approaches to problems that have O(n) HashMap-based solutions.

    Looks for a for/while loop containing another for/while loop, where the inner
    loop appears to be scanning rather than just iterating structure.
    """
    # Simple heuristic: two or more for/while keywords at different nesting depths
    # that aren't clearly iterator-pattern (like nested for over a matrix row).
    loop_pattern = re.compile(r'\b(for|while)\s*\(', re.MULTILINE)
    matches = list(loop_pattern.finditer(source_code))
    if len(matches) < 2:
        return False

    # Check if second loop appears inside the body of the first
    # (crude: the second match appears after the first's opening paren)
    for i, m in enumerate(matches[:-1]):
        for j in range(i + 1, len(matches)):
            # Both loops exist; check they're not just sequential
            # A rough depth check: count { and } between them
            between = source_code[m.start():matches[j].start()]
            open_count = between.count("{")
            close_count = between.count("}")
            if open_count > close_count:
                # Second loop is inside the first loop's body
                logger.debug("nested_loop_lookup pattern detected")
                return True
    return False


def _detect_unmemoized_recursion(source_code: str) -> bool:
    """
    Detect recursive functions without memoization — a hallmark of O(2^n)
    solutions to problems that have O(n) DP solutions.

    Looks for a method calling itself without a HashMap/array cache.
    """
    # Find method names that appear both in a return type declaration and as a call
    method_call_pattern = re.compile(r'(\w+)\s*\([^)]*\)\s*\+\s*\1\s*\(', re.MULTILINE)
    if method_call_pattern.search(source_code):
        logger.debug("unmemoized_recursion pattern detected (double-call)")
        return True

    # Also check for self-recursive call without Map/memo array in the same class
    # Look for a method name used recursively
    recursive_call = re.compile(r'\breturn\s+\w+\s*\(\s*\w+\s*-\s*1\s*\)', re.MULTILINE)
    if recursive_call.search(source_code):
        # Check if there's a memoization structure (HashMap, int[], dp)
        has_memo = bool(re.search(r'\b(HashMap|memo|cache|dp\s*\[|Map<)', source_code))
        if not has_memo:
            logger.debug("unmemoized_recursion pattern detected (recursive -1 without memo)")
            return True

    return False


# Dict dispatch — adding a new pattern type doesn't require editing existing logic
DETECTORS: dict[str, Callable[[str], bool]] = {
    "nested_loop_lookup": _detect_nested_loop_lookup,
    "unmemoized_recursion": _detect_unmemoized_recursion,
}
_DETECTORS = DETECTORS


# ── Main entry point ──────────────────────────────────────────────────────────

def get_structural_hint(
    source_code: str,
    signatures: List[InefficiencySignature],
) -> Optional[str]:
    """
    Match the source code against known inefficiency patterns for this problem.

    Returns the hint_text of the first matching signature, or None if no
    pattern matches (meaning the code likely uses the efficient approach).

    This function should only be called when a complexity gap has already been
    detected — the caller (pipeline.py) is responsible for that gate.
    """
    for sig in signatures:
        detector = _DETECTORS.get(sig.pattern_type)
        if detector is None:
            logger.warning("No detector implemented for pattern_type '%s'", sig.pattern_type)
            continue
        try:
            if detector(source_code):
                logger.info("Matched inefficiency pattern '%s'", sig.pattern_type)
                return sig.hint_text
        except Exception as e:
            logger.error("Detector '%s' raised an error: %s", sig.pattern_type, e)

    return None
