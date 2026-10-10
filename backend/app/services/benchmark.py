"""
app/services/benchmark.py — Scaled-input benchmarking for complexity analysis.

Design notes:
- Uses the SAME CompiledSubmission primitive as correctness checking — not a
  separate execution path. The sandbox invariant (one primitive, reused for two
  purposes) is preserved here.
- Per-repetition input re-randomization (different seed each repetition) reduces
  the ability of a submission to special-case known input patterns.
- Warm-up runs are discarded before timing to reduce JIT warm-up noise.
- Median of repetitions is used rather than mean — more robust to GC pauses and
  OS scheduling noise.
- Early-stop on repeated consecutive timeouts to avoid spending the full benchmark
  budget on a submission that has clearly exceeded the time limit.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, List

from app.config import settings
from app.sandbox.executor import CompiledSubmission, SandboxLimits

logger = logging.getLogger(__name__)

# Timeout budget per input size, scaled loosely by size
_BASE_TIMEOUT_S = 5.0
_MAX_TIMEOUT_S = 30.0


def _timeout_for_size(n: int) -> float:
    """Scale timeout budget with input size — larger inputs get more time."""
    import math
    return min(_MAX_TIMEOUT_S, _BASE_TIMEOUT_S + math.log10(max(n, 1)) * 2)


@dataclass
class BenchmarkPoint:
    input_size: int
    runtime_ms: float
    timed_out: bool


class BenchmarkResult(list):
    """
    Subclass of list containing BenchmarkPoints, with metadata regarding the benchmark execution.
    Can be used as a plain List[BenchmarkPoint] or inspected for completed_within_budget / total_duration_s.
    """
    def __init__(self, points: List[BenchmarkPoint], completed_within_budget: bool, total_duration_s: float):
        super().__init__(points)
        self.points = points
        self.completed_within_budget = completed_within_budget
        self.total_duration_s = total_duration_s


def run_benchmark(
    compiled: CompiledSubmission,
    generator: Callable[[int, int], str],
    input_sizes: List[int] | None = None,
    repetitions: int | None = None,
    warmup_runs: int | None = None,
    total_timeout_s: float | None = None,
) -> BenchmarkResult:
    """
    Run the compiled submission across scaled input sizes and return timing data.

    Enforces a strict global wall-clock time limit (default 10s from settings.benchmark_total_timeout_s).
    If a slow submission takes too long, benchmarking halts immediately and marks remaining sizes as timed out.

    Returns a BenchmarkResult (list of BenchmarkPoint) with completed_within_budget flag.
    """
    if input_sizes is None:
        input_sizes = settings.benchmark_sizes
    if repetitions is None:
        repetitions = settings.benchmark_repetitions
    if warmup_runs is None:
        warmup_runs = settings.benchmark_warmup_runs
    if total_timeout_s is None:
        total_timeout_s = getattr(settings, "benchmark_total_timeout_s", 10.0)

    start_time = time.monotonic()
    points: List[BenchmarkPoint] = []
    consecutive_timeouts = 0
    completed_within_budget = True

    for idx, size in enumerate(input_sizes):
        elapsed = time.monotonic() - start_time
        remaining_total = total_timeout_s - elapsed

        # Check if total budget is exhausted before starting this size
        if remaining_total <= 0.05:
            logger.info(
                "Benchmark total timeout reached (%.2fs >= %.2fs). Aborting size %d and remaining.",
                elapsed, total_timeout_s, size,
            )
            completed_within_budget = False
            for rem_size in input_sizes[idx:]:
                points.append(BenchmarkPoint(input_size=rem_size, runtime_ms=0.0, timed_out=True))
            break

        # Calculate timeout for this size, strictly capped by the remaining total budget
        timeout_s = min(_timeout_for_size(size), remaining_total)
        if timeout_s < 0.1:
            logger.info("Insufficient remaining time budget (%.2fs) for size %d. Marking timed out.", remaining_total, size)
            completed_within_budget = False
            for rem_size in input_sizes[idx:]:
                points.append(BenchmarkPoint(input_size=rem_size, runtime_ms=0.0, timed_out=True))
            break

        # Warm-up runs — discarded, just to trigger JVM class loading / JIT
        warmup_timed_out = False
        for w in range(warmup_runs):
            cur_remaining = total_timeout_s - (time.monotonic() - start_time)
            if cur_remaining <= 0.05:
                warmup_timed_out = True
                completed_within_budget = False
                break

            warmup_limits = SandboxLimits(wall_timeout_s=min(timeout_s, cur_remaining))
            seed = -(size + w + 1)  # negative seeds reserved for warmup
            try:
                stdin = generator(size, seed)
                warmup_result = compiled.run(stdin_data=stdin, limits=warmup_limits)
                if warmup_result.timed_out:
                    logger.debug("Warmup timed out at size %d", size)
                    warmup_timed_out = True
                    break
            except Exception as e:
                logger.warning("Warmup run error at size %d: %s", size, e)

        # If warmup timed out or total budget was exhausted during warmup:
        if warmup_timed_out or (time.monotonic() - start_time >= total_timeout_s):
            points.append(BenchmarkPoint(input_size=size, runtime_ms=0.0, timed_out=True))
            consecutive_timeouts += 1
            completed_within_budget = False
            logger.info("Benchmark: size %d timed out during warmup (elapsed=%.2fs)", size, time.monotonic() - start_time)

            if time.monotonic() - start_time >= total_timeout_s:
                for rem_size in input_sizes[idx + 1:]:
                    points.append(BenchmarkPoint(input_size=rem_size, runtime_ms=0.0, timed_out=True))
                break
            if consecutive_timeouts >= 2:
                logger.info("Early stop: %d consecutive full-timeout sizes", consecutive_timeouts)
                for rem_size in input_sizes[idx + 1:]:
                    points.append(BenchmarkPoint(input_size=rem_size, runtime_ms=0.0, timed_out=True))
                break
            continue

        # Timed repetitions
        runtimes: List[float] = []
        all_timed_out = True

        for rep in range(repetitions):
            cur_remaining = total_timeout_s - (time.monotonic() - start_time)
            if cur_remaining <= 0.05:
                logger.debug("Total timeout reached before rep %d at size %d", rep, size)
                completed_within_budget = False
                break

            rep_limits = SandboxLimits(wall_timeout_s=min(timeout_s, cur_remaining))
            seed = size * 1000 + rep  # unique seed per (size, rep) pair
            try:
                stdin = generator(size, seed)
            except Exception as e:
                logger.warning("Generator error at size %d rep %d: %s", size, rep, e)
                continue

            result = compiled.run(stdin_data=stdin, limits=rep_limits)

            if result.timed_out:
                logger.debug("Timeout at size %d rep %d", size, rep)
            else:
                runtimes.append(result.runtime_ms)
                all_timed_out = False

            if time.monotonic() - start_time >= total_timeout_s:
                completed_within_budget = False
                break

        if all_timed_out:
            points.append(BenchmarkPoint(input_size=size, runtime_ms=0.0, timed_out=True))
            consecutive_timeouts += 1
            completed_within_budget = False
            logger.info("Benchmark: all reps timed out at size %d", size)
            if (time.monotonic() - start_time >= total_timeout_s) or consecutive_timeouts >= 2:
                logger.info(
                    "Benchmark loop terminated early (elapsed=%.2fs, consecutive_timeouts=%d)",
                    time.monotonic() - start_time, consecutive_timeouts,
                )
                for rem_size in input_sizes[idx + 1:]:
                    points.append(BenchmarkPoint(input_size=rem_size, runtime_ms=0.0, timed_out=True))
                break
        else:
            consecutive_timeouts = 0
            runtimes.sort()
            median = runtimes[len(runtimes) // 2]
            points.append(BenchmarkPoint(input_size=size, runtime_ms=median, timed_out=False))
            logger.debug("Benchmark: size=%d median_ms=%.2f reps=%d", size, median, len(runtimes))

            if time.monotonic() - start_time >= total_timeout_s and idx + 1 < len(input_sizes):
                logger.info("Total timeout reached after completing size %d", size)
                completed_within_budget = False
                for rem_size in input_sizes[idx + 1:]:
                    points.append(BenchmarkPoint(input_size=rem_size, runtime_ms=0.0, timed_out=True))
                break

    total_duration_s = time.monotonic() - start_time
    is_fully_completed = (
        completed_within_budget
        and total_duration_s <= total_timeout_s
        and len(points) == len(input_sizes)
        and all(not p.timed_out for p in points)
    )

    return BenchmarkResult(
        points=points,
        completed_within_budget=is_fully_completed,
        total_duration_s=round(total_duration_s, 3),
    )
