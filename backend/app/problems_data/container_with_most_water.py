"""Container With Most Water scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Container With Most Water input of size n.
    Format:
        n
        height[0] height[1] ... height[n-1]
    """
    rng = random.Random(seed)
    heights = [rng.randint(1, 10000) for _ in range(n)]
    return f"{n}\n{' '.join(map(str, heights))}\n"
