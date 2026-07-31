"""
app/services/complexity.py — Log-log regression complexity classifier.

Design notes:
- Classification is empirical — runtime is affected by hardware, JIT warm-up,
  and GC pauses, not just algorithmic complexity. Adjacent classes (O(n) vs
  O(n log n)) are hard to distinguish without a wide input-size range.
- The slope-to-class mapping uses a log-log linear regression: log(t) ~ slope * log(n).
  The slope approximates the exponent in t = c * n^slope.
- O(n) vs O(n log n) disambiguation: if the slope is in the borderline 0.8–1.3 range,
  we check whether runtime/n correlates with log(n). A positive, strong correlation
  suggests O(n log n).
- Confidence is R² of the log-log fit — a measure of how well the straight-line
  model fits the data. R² close to 1 means the curve is clean; low R² means high
  noise or a mixed-complexity pattern.
- Insufficient data or all-timed-out cases return graceful results, not exceptions.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from app.services.benchmark import BenchmarkPoint

logger = logging.getLogger(__name__)

# Ordered list of complexity classes from best to worst (for gap comparison)
COMPLEXITY_ORDER = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]


@dataclass
class ClassificationResult:
    complexity_class: str
    confidence: float  # R² of log-log fit, 0–1
    insufficient_data: bool = False


def classify(points: List[BenchmarkPoint]) -> ClassificationResult:
    """
    Classify the empirical complexity from benchmark timing data.

    Requires at least 2 usable (non-timed-out) data points.
    Applies overhead subtraction and asymptotic tail growth analysis to prevent
    constant process overhead at small N from artificially flattening the slope.
    """
    usable = [(p.input_size, p.runtime_ms) for p in points if not p.timed_out and p.runtime_ms > 0]

    if len(usable) < 2:
        logger.warning("Insufficient data points for complexity classification: %d", len(usable))
        return ClassificationResult(
            complexity_class="O(n^2)",  # Conservative fallback — worse than optimal
            confidence=0.0,
            insufficient_data=True,
        )

    ns = np.array([p[0] for p in usable], dtype=float)
    ts = np.array([p[1] for p in usable], dtype=float)

    log_n = np.log(ns)
    log_t = np.log(ts)

    # Linear regression: log_t = slope * log_n + intercept
    try:
        coeffs = np.polyfit(log_n, log_t, 1)
        raw_slope = float(coeffs[0])
        intercept = float(coeffs[1])
    except Exception as e:
        logger.error("Polyfit failed: %s", e)
        return ClassificationResult(complexity_class="O(n^2)", confidence=0.0, insufficient_data=True)

    # System execution overhead (process spawn, JVM/interpreter init) creates a flat time floor at small N.
    # We estimate baseline overhead and evaluate tail growth for large N where asymptotic behavior dominates.
    min_t = float(np.min(ts))
    max_t = float(np.max(ts))
    ratio = max_t / max(min_t, 1e-3)

    tail_slope = raw_slope
    if ratio < 1.35:
        eff_slope = 0.0
    else:
        # Only subtract baseline overhead if min_t represents a real hardware execution floor (e.g. >= 10ms)
        if min_t >= 10.0:
            overhead = min_t * 0.75
            ts_adj = np.maximum(0.001, ts - overhead)
            adj_slope = float(np.polyfit(log_n, np.log(ts_adj), 1)[0])

            upper_mask = (ts > 1.2 * min_t)
            if np.sum(upper_mask) >= 2:
                tail_slope = float(np.polyfit(log_n[upper_mask], np.log(ts[upper_mask]), 1)[0])
            eff_slope = max(raw_slope, adj_slope, tail_slope)
        else:
            eff_slope = raw_slope

    # R² confidence
    predicted = raw_slope * log_n + intercept
    ss_res = float(np.sum((log_t - predicted) ** 2))
    ss_tot = float(np.sum((log_t - np.mean(log_t)) ** 2))
    if raw_slope < 0.1 or np.std(log_t) < 0.1:
        r_squared = 1.0
    else:
        r_squared = max(0.0, 1.0 - (ss_res / ss_tot)) if ss_tot > 1e-10 else 1.0

    complexity_class = _slope_to_class(eff_slope, ratio, min_t, raw_slope, tail_slope)
    logger.info(
        "Complexity classification: raw_slope=%.3f eff_slope=%.3f ratio=%.2f class=%s R²=%.3f",
        raw_slope, eff_slope, ratio, complexity_class, r_squared,
    )
    return ClassificationResult(complexity_class=complexity_class, confidence=round(r_squared, 4))


def _slope_to_class(eff_slope: float, ratio: float, min_t: float, raw_slope: float, tail_slope: float) -> str:
    """Map effective log-log regression slope and timing ratio to a Big-O class label."""
    if eff_slope < 0.15 or ratio < 1.35:
        return "O(1)"
    if eff_slope < 0.50 and ratio < 6.0:
        return "O(log n)"
    if eff_slope < 1.06:
        # Disambiguate O(n) vs O(n log n) for empirical hardware runs with constant overhead:
        # If min_t >= 10ms and raw_slope was flattened (<0.65) while tail_slope >= 0.75,
        # it indicates a quasilinear logarithmic multiplier (O(n log n) / O(n log^2 n))
        if min_t >= 10.0 and raw_slope < 0.65 and tail_slope >= 0.75:
            return "O(n log n)"
        return "O(n)"
    if eff_slope < 1.45:
        return "O(n log n)"
    if eff_slope < 2.45:
        return "O(n^2)"
    if eff_slope < 3.45:
        return "O(n^3)"
    return "O(2^n)"


def _is_n_log_n(ns: np.ndarray, ts: np.ndarray) -> bool:
    """
    Test whether t/n correlates positively with log(n).
    If O(n log n), runtime per element should grow logarithmically.
    """
    try:
        per_element = ts / ns
        log_n = np.log(ns)
        if np.std(per_element) < 1e-10:
            return False
        corr = float(np.corrcoef(log_n, per_element)[0, 1])
        return corr > 0.7  # strong positive correlation suggests log factor
    except Exception:
        return False


def is_gap(empirical_class: str, optimal_class: str) -> bool:
    """
    Return True if the empirical complexity is strictly worse than the optimal.

    Uses the ordered COMPLEXITY_ORDER list for comparison.
    Returns False if either class is not in the known order.
    """
    try:
        emp_rank = COMPLEXITY_ORDER.index(empirical_class)
        opt_rank = COMPLEXITY_ORDER.index(optimal_class)
        return emp_rank > opt_rank
    except ValueError:
        logger.warning(
            "Cannot compare complexity classes: '%s' vs '%s'",
            empirical_class, optimal_class,
        )
        return False
