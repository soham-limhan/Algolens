"""Two Sum scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Two Sum input of size n.
    Format:
        n
        nums[0] nums[1] ... nums[n-1]
        target
    """
    rng = random.Random(seed)
    nums = [rng.randint(-10**4, 10**4) for _ in range(n)]
    # Guarantee a solution exists: pick two indices and compute target
    i, j = rng.sample(range(n), 2)
    target = nums[i] + nums[j]
    return f"{n}\n{' '.join(map(str, nums))}\n{target}\n"
