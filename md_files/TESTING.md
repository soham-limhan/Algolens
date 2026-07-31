# AlgoLens — Testing Strategy

## 1. Test Levels

| Level | What's tested | Speed | Location |
|---|---|---|---|
| Unit | Complexity classifier against synthetic data; comparator logic | Fast | `tests/test_complexity_classifier.py`, `tests/test_correctness_comparators.py` |
| Integration | Full submission pipeline against a real (test) database, actually compiling/running Java | Slow | `tests/test_submission_pipeline_integration.py` (marked `@pytest.mark.integration`) |
| Sandbox robustness | Adversarial submissions against the real sandbox | Slow | `tests/test_sandbox_robustness.py` |
| Manual / smoke | End-to-end flow via running server | Manual | See Section 5 |

Run fast tests during regular development:
```bash
pytest -m "not integration"
```
Run the full suite (including integration and sandbox robustness, both slow since they compile/run real Java) before a deployment or milestone:
```bash
pytest
```

## 2. Unit Tests — Complexity Classifier

`tests/test_complexity_classifier.py` feeds the classifier **synthetic** `(input_size, runtime_ms)` points generated from known mathematical functions (not real Java runs), with a small amount of added noise:

- `runtime = c * n` (several constants `c`) → assert classified as `O(n)`.
- `runtime = c * n^2` → assert `O(n^2)`.
- `runtime = c * n * log(n)` → assert `O(n log n)`.
- `runtime = c * log(n)` → assert `O(log n)`.
- `runtime = c` (constant) → assert `O(1)`.
- Clearly-separated O(n) vs O(n log n) synthetic sets → assert the disambiguation logic (runtime/n correlation with log(n)) actually distinguishes them, not just defaults to one.
- Fewer than 2 usable points → assert a graceful "insufficient data" result, not an exception.
- All points `timed_out=True` → assert graceful handling.

## 3. Unit Tests — Correctness Comparators

`tests/test_correctness_comparators.py`, table-driven, covering each comparator type:

| Comparator | Cases covered |
|---|---|
| `exact` | Matching output; non-matching; whitespace/newline-only differences (should still match after normalization) |
| `numeric_tolerance` | Value just inside the tolerance band (passes); just outside (fails) |
| `sorted` | Order-shuffled tokens (should still match); genuinely different token sets (fails) |

## 4. Integration Tests — Full Pipeline

`tests/test_submission_pipeline_integration.py`, using `TestClient`/`httpx` against an isolated test database:

1. Register a user, log in.
2. Submit a **correct, efficient** solution → poll to `complete` → assert `empirical_complexity` matches (or is one class away from, given real-run noise) the optimum, and `structural_hint` is `None`.
3. Submit a **correct but inefficient** solution (e.g. brute-force Two Sum) → assert empirical complexity is worse than optimal and `structural_hint` is populated.
4. Submit an **incorrect** solution → assert `status=failed`, `failure_detail` populated, and — importantly — **assert zero `BenchmarkRun` rows were created** (proves correctness actually gates benchmarking, not just by design intent).
5. Submit code that **fails to compile** → assert `status=failed`, `failure_detail` contains compiler output, no test-case execution attempted.
6. Assert `GET /users/{id}/history` reflects all of the above with correct statuses, and that a second registered user **cannot** see the first user's history or individual submissions (`403`/`404` as appropriate).

This suite is slow (real `javac`/`java` invocations) — kept separate from the fast unit suite via the `integration` pytest marker.

## 5. Sandbox Robustness Tests

`tests/test_sandbox_robustness.py` — submits deliberately hostile Java programs through `CompiledSubmission` and asserts the **specific expected failure mode** fires, not just "did not succeed" (a generic pass/fail assertion would hide a wrong isolation mechanism firing for the wrong reason):

| Hostile case | Expected failure mode |
|---|---|
| Infinite loop (`while(true){}`) | `timed_out=True`, bounded wall-clock time in the test itself |
| Memory bomb (unbounded array/list growth) | Clean non-zero exit / OOM-related error, not host memory exhaustion |
| Fork/thread bomb | Blocked by `RLIMIT_NPROC` |
| Large stdout spam | Output truncated at the documented cap, not unbounded parent-process memory growth |
| File write outside scratch dir | `SecurityException` from the Java Security Manager policy, surfaced as non-zero exit / stderr content |
| Network access attempt | Blocked by the Security Manager policy |
| Normal correct submission, interleaved with the above | Completely unaffected by a prior hostile submission — proves scratch-dir isolation and cleanup between runs |

Each hostile test logs its own wall-clock time; if any case approaches its configured timeout ceiling, that's flagged as a concurrency-capacity concern for the college server deployment (see `DEPLOYMENT.md`).

## 6. Regression Tests (Correctness Checking Bug Fix)

Added after the empty-submission-passes bug (see `CHANGELOG.md` 0.4.1) — must fail on the pre-fix code, pass after:

1. Empty/whitespace-only submission → `Compilation Error`, not `Accepted`.
2. Submission with wrong class name / missing `main` → `Compilation Error`.
3. Compiles and runs but always returns a fixed wrong answer → `Wrong Answer`, with populated failing-case detail.
4. Compiles but throws an unhandled runtime exception → `Runtime Error`.
5. Genuinely correct submission → `Accepted`, and confirmed as the *only* path producing `BenchmarkRun` rows.
6. Problem with zero test cases loaded (misconfigured data) → explicit error, not a silent `Accepted` default (targets the vacuous-`all()`-over-empty-list failure mode specifically).

## 7. Manual Smoke Test (used at each major milestone)

1. Register → login.
2. Submit a deliberately brute-force (O(n²)) Two Sum solution.
3. Poll until `complete`.
4. Confirm: verdict is `Accepted`, `empirical_complexity` is `O(n^2)`, `structural_hint` is populated and points at the nested-loop pattern.
5. Submit a proper HashMap-based solution to the same problem.
6. Confirm: `empirical_complexity` is `O(n)`, `structural_hint` is `None`.
7. Submit empty code.
8. Confirm: verdict is `Compilation Error` with real compiler output shown — not a silent pass (this is the regression test for 0.4.1, repeated manually against the live app before any deployment).
