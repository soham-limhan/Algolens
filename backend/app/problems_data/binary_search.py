"""Binary Search scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Binary Search input of size n (sorted array + target).
    Format:
        n
        nums[0] nums[1] ... nums[n-1]   (sorted ascending)
        target
    50% chance target is present (seed parity).
    """
    rng = random.Random(seed)
    nums = sorted(rng.randint(-10**6, 10**6) for _ in range(n))
    if seed % 2 == 0:
        target = nums[rng.randint(0, n - 1)]
    else:
        # Target likely not in array
        target = rng.randint(-10**6, 10**6)
    return f"{n}\n{' '.join(map(str, nums))}\n{target}\n"
