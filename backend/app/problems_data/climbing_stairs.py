"""Climbing Stairs scaled-input generator."""
from __future__ import annotations
import random


def generate(n: int, seed: int) -> str:
    """
    Generate a Climbing Stairs input.
    n here is the stair count (capped sensibly for memoized recursion).
    Format:
        n
    We cap at 1000 regardless of requested n to avoid integer overflow in
    naive recursive solutions and keep timing meaningful.
    """
    rng = random.Random(seed)
    # Scale: use log of n to stay reasonable
    import math
    stair_n = max(10, min(1000, int(math.log2(n + 1) * 50)))
    return f"{stair_n}\n"
