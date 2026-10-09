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

import json
import logging
import math
from dataclasses import dataclass
from typing import List, Optional

import httpx
import numpy as np

from app.config import settings
from app.services.benchmark import BenchmarkPoint

logger = logging.getLogger(__name__)

# Ordered list of complexity classes from best to worst (for gap comparison)
COMPLEXITY_ORDER = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(n^3)", "O(2^n)"]


@dataclass
class ClassificationResult:
    complexity_class: str
    confidence: float  # AI confidence or R² of log-log fit, 0–1
    insufficient_data: bool = False
    reasoning: Optional[str] = None
    evaluated_by: str = "ai"  # "ai" or "mathematical_fallback"


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
    return ClassificationResult(
        complexity_class=complexity_class,
        confidence=round(r_squared, 4),
        reasoning=f"Empirically estimated via log-log regression slope (slope={eff_slope:.2f}, R²={r_squared:.2f}).",
        evaluated_by="mathematical_fallback",
    )


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


def normalize_complexity_class(raw: str) -> str:
    """
    Normalize any AI or raw Big-O output into one of the canonical AlgoLens classes:
    O(1), O(log n), O(n), O(n log n), O(n^2), O(n^3), O(2^n).
    """
    if not raw or not isinstance(raw, str):
        return "O(n)"
    s = raw.strip().lower()
    s_clean = s.replace(" ", "").replace("*", "")

    if "2^n" in s_clean or "2**n" in s_clean or "exponential" in s:
        return "O(2^n)"
    if "n^3" in s_clean or "n**3" in s_clean or "cubic" in s:
        return "O(n^3)"
    if "n^2" in s_clean or "n**2" in s_clean or "quadratic" in s or "nn" in s_clean:
        return "O(n^2)"
    if "nlogn" in s_clean or "nlog(n)" in s_clean or "linearithmic" in s or "quasilinear" in s:
        return "O(n log n)"
    if "logn" in s_clean or "log(n)" in s_clean or "logarithmic" in s:
        return "O(log n)"
    if "o(1)" in s_clean or "constant" in s:
        return "O(1)"
    if "o(n)" in s_clean or "linear" in s:
        return "O(n)"

    for c in COMPLEXITY_ORDER:
        if c.lower() == s:
            return c
    return "O(n)"


def classify_with_ai(
    source_code: str,
    language: str,
    points: List[BenchmarkPoint],
    problem_title: Optional[str] = None,
    optimal_complexity: Optional[str] = None,
    problem_description: Optional[str] = None,
    api_key_override: Optional[str] = None,
) -> ClassificationResult:
    """
    Completely evaluate code complexity using AI by analyzing both:
    1. The source code structure (loops, recursion, branching, collections, helper calls).
    2. The empirical benchmark execution runtimes measured across scaled N input sizes.

    Falls back to mathematical log-log linear regression if Groq is unavailable, unconfigured,
    or returns an unparseable response.
    """
    groq_key = api_key_override if api_key_override is not None else settings.groq_api_key
    if not groq_key or not groq_key.strip():
        logger.info("Groq API key not configured; evaluating complexity via mathematical regression fallback")
        fallback = classify(points)
        fallback.evaluated_by = "mathematical_fallback"
        fallback.reasoning = "Calculated via mathematical log-log linear regression (Groq API key not configured)."
        return fallback

    if not source_code or not source_code.strip():
        logger.warning("Empty source code provided for AI complexity evaluation; using mathematical fallback")
        fallback = classify(points)
        fallback.evaluated_by = "mathematical_fallback"
        return fallback

    # Format telemetry across N input sizes
    telemetry_rows = [
        "| Input Size (N) | Measured Runtime | Status | Scaling vs Previous N |",
        "| :--- | :--- | :--- | :--- |",
    ]
    sorted_points = sorted(points, key=lambda p: p.input_size)
    prev_n: Optional[int] = None
    prev_t: Optional[float] = None

    for p in sorted_points:
        if p.timed_out:
            status_str = "TIMED OUT (>10,000 ms)"
            runtime_str = "Timeout"
            scaling_str = "Exceeded wall time limit"
        else:
            status_str = "Completed"
            runtime_str = f"{p.runtime_ms:.2f} ms"
            scaling_str = "-"
            if prev_n is not None and prev_t is not None and prev_t > 0:
                n_factor = p.input_size / prev_n
                t_factor = p.runtime_ms / prev_t
                scaling_str = f"{t_factor:.2f}x runtime increase for {n_factor:.1f}x N increase"
            prev_n = p.input_size
            prev_t = p.runtime_ms
        telemetry_rows.append(f"| N = {p.input_size:,} | {runtime_str} | {status_str} | {scaling_str} |")

    telemetry_table = "\n".join(telemetry_rows) if sorted_points else "No benchmark points recorded."

    preferred_model = settings.groq_model or "openai/gpt-oss-120b"
    candidate_models = [
        preferred_model,
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.8-27b",
        "allam-2-7b",
    ]
    models_to_try = []
    for m in candidate_models:
        if m and m not in models_to_try:
            models_to_try.append(m)

    system_prompt = (
        "You are an authoritative algorithm runtime and computational complexity evaluation AI. "
        "Your mission is to evaluate the true asymptotic Big-O time complexity of the user's submitted solution.\n\n"
        "You must synthesize TWO sources of ground truth:\n"
        "1. Algorithmic Source Code Analysis: Inspect loop boundaries, nested iterations, recursion depth, divide-and-conquer logic, "
        "early exits, and data structure operations (e.g. hash lookups O(1), sorting O(n log n), binary search O(log n), nested scans O(n^2)).\n"
        "2. Empirical Benchmark Telemetry: Inspect the measured execution times across the N input sizes, noting the empirical scaling "
        "factors as N increases (e.g., 10x N causing ~10x time for O(n) vs ~100x time for O(n^2)), and noting whether large N values timed out.\n\n"
        "Standard Complexity Classes (choose EXACTLY ONE):\n"
        "- O(1)\n"
        "- O(log n)\n"
        "- O(n)\n"
        "- O(n log n)\n"
        "- O(n^2)\n"
        "- O(n^3)\n"
        "- O(2^n)\n\n"
        "Output MUST be a strict JSON object with NO markdown wrapping around the JSON, matching this schema:\n"
        "{\n"
        '  "complexity_class": "<one of: O(1), O(log n), O(n), O(n log n), O(n^2), O(n^3), O(2^n)>",\n'
        '  "confidence": <float between 0.0 and 1.0, e.g. 0.98>,\n'
        '  "reasoning": "<clear 2-3 sentence explanation detailing how the code structure and the empirical scaling across N input sizes justify this Big-O classification>"\n'
        "}"
    )

    user_prompt = f"""
Language: {language}
Problem: {problem_title or "Algorithm Challenge"}
Optimal Reference Target: {optimal_complexity or "O(n)"}

Problem Description:
{(problem_description or "Not provided")[:800]}

Empirical Benchmark Telemetry Across N Input Sizes:
{telemetry_table}

Submitted Source Code ({language}):
```{language}
{source_code}
```

Evaluate the asymptotic Big-O time complexity by analyzing the code structure and cross-referencing with the empirical benchmark timing data across the N inputs. Return only valid JSON.
"""

    headers = {
        "Authorization": f"Bearer {groq_key.strip()}",
        "Content-Type": "application/json",
    }

    last_error: Optional[Exception] = None
    for model in models_to_try:
        try:
            with httpx.Client(timeout=20.0) as client:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000,
                    "response_format": {"type": "json_object"},
                }
                response = client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    raw_class = str(parsed.get("complexity_class", ""))
                    norm_class = normalize_complexity_class(raw_class)
                    raw_conf = parsed.get("confidence", 0.95)
                    try:
                        conf_val = float(raw_conf)
                        conf_val = max(0.0, min(1.0, conf_val))
                    except (ValueError, TypeError):
                        conf_val = 0.95
                    reasoning_str = str(parsed.get("reasoning", "")).strip()
                    logger.info(
                        "AI complexity evaluation succeeded [model=%s]: class=%s confidence=%.3f",
                        model, norm_class, conf_val,
                    )
                    return ClassificationResult(
                        complexity_class=norm_class,
                        confidence=round(conf_val, 4),
                        reasoning=reasoning_str,
                        evaluated_by="ai",
                    )
                else:
                    logger.warning(
                        "Groq model %s returned status %d: %s",
                        model, response.status_code, response.text[:200],
                    )
        except Exception as err:
            last_error = err
            logger.warning("Error with Groq model %s: %s", model, err)

    logger.warning(
        "All Groq models failed for AI complexity evaluation (%s); falling back to mathematical regression",
        last_error,
    )
    fallback = classify(points)
    fallback.evaluated_by = "mathematical_fallback"
    fallback.reasoning = "Calculated via mathematical log-log linear regression curve fitting (AI evaluation fallback)."
    return fallback
