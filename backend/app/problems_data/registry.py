"""
app/problems_data/registry.py — Maps generator_key strings to generator functions.

Why this exists in code rather than the database:
  A scaled-input generator is executable logic, not structured data. Storing it as
  DB rows would require either eval()-ing stored strings (a real security risk) or
  a generic interpreter (unnecessary at 8-10 problems). Version-controlled code is
  reviewable, testable, and doesn't introduce eval() anywhere near the database.
"""
from __future__ import annotations

from typing import Callable

from app.problems_data import (
    binary_search,
    climbing_stairs,
    contains_duplicate,
    container_with_most_water,
    maximum_subarray,
    merge_intervals,
    sql_generators,
    two_sum,
    valid_anagram,
)

# Maps generator_key (stored in problems.generator_key) to the generate() function.
# Each generate(n, seed) function returns a stdin string for input size n.
REGISTRY: dict[str, Callable[[int, int], str]] = {
    "two_sum": two_sum.generate,
    "contains_duplicate": contains_duplicate.generate,
    "valid_anagram": valid_anagram.generate,
    "container_with_most_water": container_with_most_water.generate,
    "maximum_subarray": maximum_subarray.generate,
    "climbing_stairs": climbing_stairs.generate,
    "binary_search": binary_search.generate,
    "merge_intervals": merge_intervals.generate,
    "sql_employee": sql_generators.generate_sql_employee,
    "sql_person_address": sql_generators.generate_sql_person_address,
    "sql_customers_orders": sql_generators.generate_sql_customers_orders,
    "sql_scores": sql_generators.generate_sql_scores,
    "sql_weather": sql_generators.generate_sql_weather,
    "sql_generic": sql_generators.generate_sql_generic,
}


def get_generator(key: str) -> Callable[[int, int], str]:
    """Return the generator function for a problem, falling back to default if unmapped."""
    if key not in REGISTRY:
        return REGISTRY["two_sum"]
    return REGISTRY[key]
