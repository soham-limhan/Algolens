"""Merge Intervals scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Merge Intervals input with n intervals.
    Format:
        n
        start[0] end[0]
        start[1] end[1]
        ...
    Intervals are random and may overlap.
    """
    rng = random.Random(seed)
    intervals = []
    for _ in range(n):
        start = rng.randint(0, 10000)
        end = start + rng.randint(1, 1000)
        intervals.append((start, end))

    lines = [str(n)]
    for start, end in intervals:
        lines.append(f"{start} {end}")
    return "\n".join(lines) + "\n"
