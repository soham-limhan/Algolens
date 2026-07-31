"""
app/seed.py — Idempotent seed script for the AlgoLens problem bank.

Run with: python -m app.seed

Idempotent: safe to re-run — checks for existing rows by title before inserting.
Does NOT duplicate problems if already seeded.
"""
from __future__ import annotations

import logging
import sys

from app.db.database import Base, SessionLocal, engine
from app.models import InefficiencySignature, Problem, TestCase  # noqa: F401 — registers all models

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Problem definitions ───────────────────────────────────────────────────────

PROBLEMS = [
    {
        "title": "Minimum Number of Pushes to Type Word I",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "You are given a string `word` containing distinct lowercase English letters.\n\n"
            "Telephone keypads have keys mapped to distinct collections of letters. You can map the "
            "letters to keys 2 through 9 in any way. Each key can be pressed 1, 2, 3, or 4 times "
            "to type the mapped letters.\n\n"
            "Return the minimum number of pushes needed to type the word after mapping the letters.\n\n"
            "**Input format:**\n"
            "```\nword\n```\n"
            "**Output:** Minimum number of key pushes (integer)."
        ),
        "test_cases": [
            {"input": "abcde\n", "expected_output": "5", "comparator_type": "exact"},
            {"input": "xycdefgh\n", "expected_output": "8", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Two Sum",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "two_sum",
        "description": (
            "Given an array of integers `nums` and an integer `target`, return the "
            "indices of the two numbers that add up to `target`.\n\n"
            "You may assume that each input would have exactly one solution, and "
            "you may not use the same element twice. Return the answer in any order.\n\n"
            "**Input format:**\n"
            "```\n"
            "n\n"
            "nums[0] nums[1] ... nums[n-1]\n"
            "target\n"
            "```\n"
            "**Output:** Two space-separated indices, e.g. `0 1`"
        ),
        "test_cases": [
            {"input": "4\n2 7 11 15\n9\n", "expected_output": "0 1", "comparator_type": "sorted"},
            {"input": "3\n3 2 4\n6\n",     "expected_output": "1 2", "comparator_type": "sorted"},
            {"input": "2\n3 3\n6\n",       "expected_output": "0 1", "comparator_type": "sorted"},
            {"input": "5\n1 5 3 8 2\n3\n", "expected_output": "0 4", "comparator_type": "sorted"},
        ],
        "signatures": [
            {
                "pattern_type": "nested_loop_lookup",
                "hint_text": (
                    "Your solution scans the array with a nested loop to find a matching pair. "
                    "Each element causes a full inner scan — O(n²) overall. "
                    "Consider a single pass with a HashMap: for each element, check if its "
                    "complement (target − current) is already stored."
                ),
            }
        ],
    },
    {
        "title": "Add Two Numbers",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "two_sum",
        "description": (
            "You are given two non-empty linked lists representing two non-negative integers. "
            "The digits are stored in reverse order, and each node contains a single digit. "
            "Add the two numbers and return the sum as a linked list.\n\n"
            "**Input format:**\n"
            "```\n"
            "l1: space separated integers\n"
            "l2: space separated integers\n"
            "```\n"
            "**Output:** Space separated integers of the sum in reverse order."
        ),
        "test_cases": [
            {"input": "2 4 3\n5 6 4\n", "expected_output": "7 0 8", "comparator_type": "exact"},
            {"input": "0\n0\n", "expected_output": "0", "comparator_type": "exact"},
            {"input": "9 9 9\n1\n", "expected_output": "0 0 0 1", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "two_sum",
        "description": (
            "Given a string `s`, find the length of the longest substring without repeating characters.\n\n"
            "**Input format:**\n"
            "```\ns\n```\n"
            "**Output:** Length of longest unique substring (integer)."
        ),
        "test_cases": [
            {"input": "abcabcbb\n", "expected_output": "3", "comparator_type": "exact"},
            {"input": "bbbbb\n", "expected_output": "1", "comparator_type": "exact"},
            {"input": "pwwkew\n", "expected_output": "3", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Median of Two Sorted Arrays",
        "difficulty": "hard",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "binary_search",
        "description": (
            "Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median of the two sorted arrays.\n\n"
            "The overall run time complexity should be `O(log (m+n))`.\n\n"
            "**Input format:**\n"
            "```\nnums1\nnums2\n```\n"
            "**Output:** Median value (float/number)."
        ),
        "test_cases": [
            {"input": "1 3\n2\n", "expected_output": "2.0", "comparator_type": "numeric_tolerance"},
            {"input": "1 2\n3 4\n", "expected_output": "2.5", "comparator_type": "numeric_tolerance"},
        ],
        "signatures": [],
    },
    {
        "title": "Longest Palindromic Substring",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n^2)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "Given a string `s`, return the longest palindromic substring in `s`.\n\n"
            "**Input format:**\n"
            "```\ns\n```\n"
            "**Output:** Palindromic substring."
        ),
        "test_cases": [
            {"input": "babad\n", "expected_output": "bab", "comparator_type": "exact"},
            {"input": "cbbd\n", "expected_output": "bb", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Zigzag Conversion",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "two_sum",
        "description": (
            "The string `PAYPALISHIRING` is written in a zigzag pattern on a given number of rows.\n"
            "Read the string line by line and return the formatted string.\n\n"
            "**Input format:**\n"
            "```\ns\nnumRows\n```\n"
            "**Output:** Formatted string."
        ),
        "test_cases": [
            {"input": "PAYPALISHIRING\n3\n", "expected_output": "PAHNAPLSIIGYIR", "comparator_type": "exact"},
            {"input": "PAYPALISHIRING\n4\n", "expected_output": "PINALSIGYAHRPI", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Reverse Integer",
        "difficulty": "medium",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "Given a signed 32-bit integer `x`, return `x` with its digits reversed. "
            "If reversing `x` causes the value to go outside the signed 32-bit integer range `[-2^31, 2^31 - 1]`, return 0.\n\n"
            "**Input format:**\n"
            "```\nx\n```\n"
            "**Output:** Reversed integer."
        ),
        "test_cases": [
            {"input": "123\n", "expected_output": "321", "comparator_type": "exact"},
            {"input": "-123\n", "expected_output": "-321", "comparator_type": "exact"},
            {"input": "120\n", "expected_output": "21", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "String to Integer (atoi)",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "Implement the `myAtoi(string s)` function, which converts a string to a 32-bit signed integer.\n\n"
            "**Input format:**\n"
            "```\ns\n```\n"
            "**Output:** Integer value."
        ),
        "test_cases": [
            {"input": "42\n", "expected_output": "42", "comparator_type": "exact"},
            {"input": "   -042\n", "expected_output": "-42", "comparator_type": "exact"},
            {"input": "1337c0d3\n", "expected_output": "1337", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Palindrome Number",
        "difficulty": "easy",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "Given an integer `x`, return `true` if `x` is a palindrome, and `false` otherwise.\n\n"
            "**Input format:**\n"
            "```\nx\n```\n"
            "**Output:** `true` or `false`."
        ),
        "test_cases": [
            {"input": "121\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "-121\n", "expected_output": "false", "comparator_type": "exact"},
            {"input": "10\n", "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Regular Expression Matching",
        "difficulty": "hard",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "two_sum",
        "description": (
            "Given an input string `s` and a pattern `p`, implement regular expression matching with support for `.` and `*`.\n\n"
            "**Input format:**\n"
            "```\ns\np\n```\n"
            "**Output:** `true` or `false`."
        ),
        "test_cases": [
            {"input": "aa\na\n", "expected_output": "false", "comparator_type": "exact"},
            {"input": "aa\na*\n", "expected_output": "true", "comparator_type": "exact"},
            {"input": "ab\n.*", "expected_output": "true", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Container With Most Water",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "container_with_most_water",
        "description": (
            "You are given `n` vertical lines where the i-th line has height `height[i]`. "
            "Find two lines that, together with the x-axis, form a container holding the most water.\n\n"
            "Return the maximum amount of water the container can store.\n\n"
            "**Input format:**\n"
            "```\n"
            "n\n"
            "height[0] height[1] ... height[n-1]\n"
            "```\n"
            "**Output:** The maximum water volume (integer)"
        ),
        "test_cases": [
            {"input": "9\n1 8 6 2 5 4 8 3 7\n", "expected_output": "49", "comparator_type": "exact"},
            {"input": "2\n1 1\n",                "expected_output": "1",  "comparator_type": "exact"},
            {"input": "4\n4 3 2 4\n",            "expected_output": "16", "comparator_type": "exact"},
        ],
        "signatures": [
            {
                "pattern_type": "nested_loop_lookup",
                "hint_text": (
                    "Checking every pair of lines is O(n²). The two-pointer technique does "
                    "this in O(n): start with pointers at both ends, compute the current area, "
                    "then move the pointer on the shorter side inward."
                ),
            }
        ],
    },
    {
        "title": "Integer to Roman",
        "difficulty": "medium",
        "optimal_time_complexity": "O(1)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "Seven different symbols represent Roman numerals: I (1), V (5), X (10), L (50), C (100), D (500), M (1000).\n"
            "Given an integer, convert it to a Roman numeral.\n\n"
            "**Input format:**\n"
            "```\nnum\n```\n"
            "**Output:** Roman numeral string."
        ),
        "test_cases": [
            {"input": "3749\n", "expected_output": "MMMDCCXLIX", "comparator_type": "exact"},
            {"input": "58\n", "expected_output": "LVIII", "comparator_type": "exact"},
            {"input": "1994\n", "expected_output": "MCMXCIV", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Roman to Integer",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "two_sum",
        "description": (
            "Given a Roman numeral, convert it to an integer.\n\n"
            "**Input format:**\n"
            "```\ns\n```\n"
            "**Output:** Integer value."
        ),
        "test_cases": [
            {"input": "III\n", "expected_output": "3", "comparator_type": "exact"},
            {"input": "LVIII\n", "expected_output": "58", "comparator_type": "exact"},
            {"input": "MCMXCIV\n", "expected_output": "1994", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Contains Duplicate",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "contains_duplicate",
        "description": (
            "Given an integer array `nums`, return `true` if any value appears at least "
            "twice, or `false` if every element is distinct.\n\n"
            "**Input format:**\n"
            "```\n"
            "n\n"
            "nums[0] nums[1] ... nums[n-1]\n"
            "```\n"
            "**Output:** `true` or `false`"
        ),
        "test_cases": [
            {"input": "4\n1 2 3 1\n",   "expected_output": "true",  "comparator_type": "exact"},
            {"input": "3\n1 2 3\n",     "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Valid Anagram",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "valid_anagram",
        "description": (
            "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, "
            "and `false` otherwise."
        ),
        "test_cases": [
            {"input": "anagram\nnagaram\n", "expected_output": "true",  "comparator_type": "exact"},
            {"input": "rat\ncar\n",         "expected_output": "false", "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Maximum Subarray",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "maximum_subarray",
        "description": (
            "Given an integer array `nums`, find the subarray with the largest sum and return its sum."
        ),
        "test_cases": [
            {"input": "9\n-2 1 -3 4 -1 2 1 -5 4\n", "expected_output": "6",  "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Climbing Stairs",
        "difficulty": "easy",
        "optimal_time_complexity": "O(n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "climbing_stairs",
        "description": (
            "You are climbing a staircase of `n` steps. Each time you can climb 1 or 2 steps. "
            "In how many distinct ways can you climb to the top?"
        ),
        "test_cases": [
            {"input": "2\n",  "expected_output": "2",  "comparator_type": "exact"},
            {"input": "3\n",  "expected_output": "3",  "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Binary Search",
        "difficulty": "easy",
        "optimal_time_complexity": "O(log n)",
        "optimal_space_complexity": "O(1)",
        "generator_key": "binary_search",
        "description": (
            "Given a sorted array of integers `nums` and an integer `target`, return the "
            "index of `target` if it is in `nums`, or -1 if it is not."
        ),
        "test_cases": [
            {"input": "6\n-1 0 3 5 9 12\n9\n",  "expected_output": "4",  "comparator_type": "exact"},
        ],
        "signatures": [],
    },
    {
        "title": "Merge Intervals",
        "difficulty": "medium",
        "optimal_time_complexity": "O(n log n)",
        "optimal_space_complexity": "O(n)",
        "generator_key": "merge_intervals",
        "description": (
            "Given a list of intervals, merge all overlapping intervals and return an array of non-overlapping intervals."
        ),
        "test_cases": [
            {
                "input": "4\n1 3\n2 6\n8 10\n15 18\n",
                "expected_output": "1 6\n8 10\n15 18",
                "comparator_type": "exact",
            },
        ],
        "signatures": [],
    },
]


from app.problems_data.registry import REGISTRY
from app.services.complexity import COMPLEXITY_ORDER
from app.services.hints import DETECTORS

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_COMPARATORS = {"exact", "numeric_tolerance", "sorted", "custom"}


def validate_problem_data(prob: dict) -> None:
    """Sanity-check problem data at seed time and fail loudly if malformed."""
    title = prob.get("title", "")
    if not isinstance(title, str) or not (1 <= len(title.strip()) <= 200):
        raise ValueError(f"Invalid problem title: {title!r}")

    desc = prob.get("description", "")
    if not isinstance(desc, str) or not desc.strip():
        raise ValueError(f"Problem '{title}' missing description")

    diff = prob.get("difficulty")
    if diff not in ALLOWED_DIFFICULTIES:
        raise ValueError(f"Problem '{title}' invalid difficulty: {diff!r}")

    opt_time = prob.get("optimal_time_complexity")
    if opt_time not in COMPLEXITY_ORDER:
        raise ValueError(f"Problem '{title}' invalid optimal_time_complexity: {opt_time!r}")

    opt_space = prob.get("optimal_space_complexity")
    if opt_space not in COMPLEXITY_ORDER:
        raise ValueError(f"Problem '{title}' invalid optimal_space_complexity: {opt_space!r}")

    gen_key = prob.get("generator_key")
    if gen_key not in REGISTRY:
        raise ValueError(f"Problem '{title}' unregistered generator_key: {gen_key!r}")

    for tc in prob.get("test_cases", []):
        comp = tc.get("comparator_type")
        if comp not in ALLOWED_COMPARATORS:
            raise ValueError(f"Problem '{title}' invalid comparator_type: {comp!r}")
        if not tc.get("input") or not str(tc.get("input")).strip():
            raise ValueError(f"Problem '{title}' has empty test case input")
        if not tc.get("expected_output") or not str(tc.get("expected_output")).strip():
            raise ValueError(f"Problem '{title}' has empty test case expected_output")

    for sig in prob.get("signatures", []):
        pat = sig.get("pattern_type")
        if pat not in DETECTORS:
            raise ValueError(f"Problem '{title}' unregistered pattern_type: {pat!r}")


from app.models.forum import ForumThread, ForumReply, ForumLike
from app.models.user import User
from app.auth.security import hash_password


def seed_forum(db) -> None:
    """Populate initial forum threads and replies if no threads exist."""
    if db.query(ForumThread).first():
        logger.info("Forum threads already seeded — skipping forum seed.")
        return

    # Ensure a seed author exists
    author = db.query(User).filter(User.email == "soham@example.com").first()
    if not author:
        author = User(
            name="soham_limhan",
            email="soham@example.com",
            password_hash=hash_password("Password123!"),
        )
        db.add(author)
        db.flush()

    threads_data = [
        {
            "title": "How to optimize DP space complexity from O(N^2) to O(N)?",
            "category": "Algorithms",
            "content": "I'm working on a grid path-finding problem (similar to Unique Paths II) and realized we only ever need the previous row's values to compute the current row. Has anyone written a clean template or gotcha list for this type of dimensional reduction?",
            "replies": [
                "Yes! You can use two arrays (prev and curr), or even a single array if you iterate backwards depending on the transition equation.\n\nFor grid paths: since grid[i][j] = grid[i-1][j] + grid[i][j-1], you can actually do it in-place using a single 1D array of size Width.",
                "Make sure you watch out for base cases! Often when you compress to 1D, your boundary initialization (like row 0 or col 0) needs to be handled carefully in each loop iteration.",
            ],
        },
        {
            "title": "Tips for debugging Time Limit Exceeded (TLE) in Python",
            "category": "General",
            "content": "Python is great for prototyping and readable syntax, but interpreter overhead can easily trigger TLE in tight loop constraints (e.g., N = 10^5). Here are my top rules:\n\n1. Avoid list appends in hot loops — use pre-allocated lists or list comprehensions.\n2. Prefer collections.deque over lists for FIFO queue operations (list pop(0) is O(N)).\n3. Use bitwise operations where applicable.\n4. Avoid global variable lookups; load them into local scope variables inside functions.\n\nWhat other python-specific optimization secrets do you guys use?",
            "replies": [],
        },
        {
            "title": "Are segment trees overkill for static range sum queries?",
            "category": "Questions",
            "content": "For a static array (no updates at all) and many range sum queries, isn't a simple Prefix Sum array optimal? It gives O(1) query time and O(N) preprocessing space/time.\n\nUnder what circumstances would someone still build a Segment Tree or Fenwick Tree (BIT) for a static problem?",
            "replies": [
                "You are absolutely correct. For static range sums, Prefix Sum is optimal. A Segment Tree is definitely overkill and slower (O(log N) vs O(1)).\n\nHowever, if the operator is not invertible (like Range Minimum Query - RMQ), a prefix array won't work directly, though Sparse Tables can still do O(1) query.",
            ],
        },
    ]

    for td in threads_data:
        thread = ForumThread(
            title=td["title"],
            category=td["category"],
            content=td["content"],
            user_id=author.id,
        )
        db.add(thread)
        db.flush()

        for reply_text in td["replies"]:
            reply = ForumReply(
                thread_id=thread.id,
                user_id=author.id,
                content=reply_text,
            )
            db.add(reply)

    logger.info("Forum successfully seeded with default topics and replies.")


def seed() -> None:
    """Populate the problem bank and forum bank. Idempotent."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seeded = 0
        skipped = 0
        for prob_data in PROBLEMS:
            validate_problem_data(prob_data)
            existing = db.query(Problem).filter(Problem.title == prob_data["title"]).first()
            if existing:
                skipped += 1
                logger.info("SKIP   %s (already exists)", prob_data["title"])
                continue

            problem = Problem(
                title=prob_data["title"],
                description=prob_data["description"],
                difficulty=prob_data["difficulty"],
                optimal_time_complexity=prob_data["optimal_time_complexity"],
                optimal_space_complexity=prob_data["optimal_space_complexity"],
                generator_key=prob_data["generator_key"],
            )
            db.add(problem)
            db.flush()  # get problem.id

            for tc in prob_data["test_cases"]:
                db.add(TestCase(
                    problem_id=problem.id,
                    input=tc["input"],
                    expected_output=tc["expected_output"],
                    comparator_type=tc["comparator_type"],
                ))

            for sig in prob_data.get("signatures", []):
                db.add(InefficiencySignature(
                    problem_id=problem.id,
                    pattern_type=sig["pattern_type"],
                    hint_text=sig["hint_text"],
                ))

            seeded += 1
            logger.info("SEEDED %s", prob_data["title"])

        seed_forum(db)

        db.commit()
        logger.info("Seed complete — %d problems seeded, %d skipped.", seeded, skipped)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    sys.exit(0)
