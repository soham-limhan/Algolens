"""Maximum Subarray (Kadane's) scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Maximum Subarray input of size n.
    Format:
        n
        nums[0] nums[1] ... nums[n-1]
    """
    rng = random.Random(seed)
    nums = [rng.randint(-10000, 10000) for _ in range(n)]
    return f"{n}\n{' '.join(map(str, nums))}\n"
