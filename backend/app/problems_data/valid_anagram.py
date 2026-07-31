"""Valid Anagram scaled-input generator."""
from __future__ import annotations
import random
import string


def generate(n: int, seed: int) -> str:
    """
    Generate a Valid Anagram input where n is the string length.
    Format:
        s
        t
    50% anagrams (by seed parity).
    """
    rng = random.Random(seed)
    chars = string.ascii_lowercase
    s = ''.join(rng.choices(chars, k=n))
    if seed % 2 == 0:
        # t is an anagram of s
        t_list = list(s)
        rng.shuffle(t_list)
        t = ''.join(t_list)
    else:
        # t is not an anagram
        t = ''.join(rng.choices(chars, k=n))
    return f"{s}\n{t}\n"
