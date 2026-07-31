"""Contains Duplicate scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Contains Duplicate input of size n.
    Format:
        n
        nums[0] nums[1] ... nums[n-1]
    50% chance of having a duplicate (alternating by seed parity).
    """
    rng = random.Random(seed)
    if seed % 2 == 0:
        # Has duplicate
        nums = [rng.randint(1, n // 2) for _ in range(n)]
    else:
        # Unique values
        nums = rng.sample(range(1, n * 2 + 1), n)
    return f"{n}\n{' '.join(map(str, nums))}\n"
