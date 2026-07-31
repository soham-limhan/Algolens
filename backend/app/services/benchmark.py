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


def run_benchmark(
    compiled: CompiledSubmission,
    generator: Callable[[int, int], str],
    input_sizes: List[int] | None = None,
    repetitions: int | None = None,
    warmup_runs: int | None = None,
) -> List[BenchmarkPoint]:
    """
    Run the compiled submission across scaled input sizes and return timing data.

    Each input size is run `repetitions` times with different random seeds,
    and `warmup_runs` are discarded before timing begins.

    Returns a list of BenchmarkPoint — one per input size. A point with
    timed_out=True means every repetition at that size exceeded the budget.
    """
    if input_sizes is None:
        input_sizes = settings.benchmark_sizes
    if repetitions is None:
        repetitions = settings.benchmark_repetitions
    if warmup_runs is None:
        warmup_runs = settings.benchmark_warmup_runs

    points: List[BenchmarkPoint] = []
    consecutive_timeouts = 0

    for size in input_sizes:
        timeout_s = _timeout_for_size(size)
        limits = SandboxLimits(wall_timeout_s=timeout_s)

        # Warm-up runs — discarded, just to trigger JVM class loading / JIT
        for w in range(warmup_runs):
            seed = -(size + w + 1)  # negative seeds reserved for warmup
            try:
                stdin = generator(size, seed)
                compiled.run(stdin_data=stdin, limits=limits)
            except Exception as e:
                logger.warning("Warmup run error at size %d: %s", size, e)

        # Timed repetitions
        runtimes: List[float] = []
        all_timed_out = True

        for rep in range(repetitions):
            seed = size * 1000 + rep  # unique seed per (size, rep) pair
            try:
                stdin = generator(size, seed)
            except Exception as e:
                logger.warning("Generator error at size %d rep %d: %s", size, rep, e)
                continue

            result = compiled.run(stdin_data=stdin, limits=limits)

            if result.timed_out:
                logger.debug("Timeout at size %d rep %d", size, rep)
            else:
                runtimes.append(result.runtime_ms)
                all_timed_out = False

        if all_timed_out:
            points.append(BenchmarkPoint(input_size=size, runtime_ms=0.0, timed_out=True))
            consecutive_timeouts += 1
            logger.info("Benchmark: all reps timed out at size %d", size)
            # Early stop after 2 consecutive full-timeout sizes — won't get better
            if consecutive_timeouts >= 2:
                logger.info("Early stop: %d consecutive full-timeout sizes", consecutive_timeouts)
                break
        else:
            consecutive_timeouts = 0
            runtimes.sort()
            median = runtimes[len(runtimes) // 2]
            points.append(BenchmarkPoint(input_size=size, runtime_ms=median, timed_out=False))
            logger.debug("Benchmark: size=%d median_ms=%.2f reps=%d", size, median, len(runtimes))

    return points
