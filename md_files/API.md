# AlgoLens — API Reference

Base URL (local dev): `http://localhost:8000`

All authenticated endpoints require an `Authorization: Bearer <access_token>` header.

## Auth

### `POST /auth/register`

Registers a new user and immediately returns a token pair.

**Request**
```json
{
  "name": "Soham",
  "email": "soham@example.com",
  "password": "at-least-8-characters"
}
```

**Response `201 Created`**
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

**Errors**: `409 Conflict` if email already registered.

---

### `POST /auth/login`

**Request**
```json
{ "email": "soham@example.com", "password": "at-least-8-characters" }
```

**Response `200 OK`**: same shape as register.

**Errors**: `401 Unauthorized` — "Incorrect email or password" (deliberately identical message whether the email doesn't exist or the password is wrong).

---

### `POST /auth/refresh`

Exchanges a valid refresh token for a **new pair** of both tokens (rotation — not just a new access token).

**Request**
```json
{ "refresh_token": "eyJhbGciOi..." }
```

**Response `200 OK`**: new token pair, same shape as register.

**Errors**: `401 Unauthorized` if the refresh token is invalid, expired, or not a refresh-type token.

## Problems

### `GET /problems`

Lists the problem bank. No auth required for this endpoint at the API level (frontend gates the route regardless — see `UI_UX.md`).

**Response `200 OK`**
```json
[
  { "id": "f41c9c09-...", "title": "Two Sum", "difficulty": "easy" },
  { "id": "a72e1d3f-...", "title": "Contains Duplicate", "difficulty": "easy" }
]
```

---

### `GET /problems/{id}`

**Response `200 OK`**
```json
{
  "id": "f41c9c09-...",
  "title": "Two Sum",
  "description": "Given an array of integers nums and an integer target...",
  "difficulty": "easy",
  "optimal_time_complexity": "O(n)",
  "optimal_space_complexity": "O(n)"
}
```

**Errors**: `404 Not Found`.

## Submissions

### `POST /submissions`

Creates a submission and enqueues the judging pipeline **asynchronously**. Requires auth.

**Request**
```json
{
  "problem_id": "f41c9c09-...",
  "source_code": "import java.util.*;\npublic class Solution { ... }"
}
```

**Response `202 Accepted`**
```json
{
  "id": "95430c56-...",
  "status": "pending",
  "empirical_complexity": null,
  "confidence_score": null,
  "structural_hint": null,
  "failure_detail": null,
  "test_results": null,
  "benchmark_curve": null
}
```

Client is expected to poll `GET /submissions/{id}` until `status` reaches a terminal state (`complete` or `failed`).

---

### `GET /submissions/{id}`

Requires auth; returns `404` if the submission doesn't belong to the requesting user.

**Response `200 OK` (while running)**
```json
{ "id": "95430c56-...", "status": "benchmarking", ... }
```

**Response `200 OK` (Accepted, complete)**
```json
{
  "id": "95430c56-...",
  "status": "complete",
  "empirical_complexity": "O(n)",
  "confidence_score": 0.94,
  "structural_hint": null,
  "failure_detail": null,
  "test_results": [
    { "test_case_id": "tc1", "passed": true, "input": "4\n2 7 11 15\n9\n", "expected": "0 1", "actual": "0 1" }
  ],
  "benchmark_curve": [
    { "input_size": 100, "runtime_ms": 2.1, "timed_out": false },
    { "input_size": 1000, "runtime_ms": 4.8, "timed_out": false },
    { "input_size": 10000, "runtime_ms": 41.2, "timed_out": false }
  ]
}
```

**Response `200 OK` (Wrong Answer, failed)**
```json
{
  "id": "95430c56-...",
  "status": "failed",
  "empirical_complexity": null,
  "confidence_score": null,
  "structural_hint": null,
  "failure_detail": "1 of 3 test case(s) failed. First failing case — expected: '0 1', got: '1 2'",
  "test_results": [
    { "test_case_id": "tc1", "passed": false, "input": "4\n2 7 11 15\n9\n", "expected": "0 1", "actual": "1 2" }
  ],
  "benchmark_curve": null
}
```

**Response `200 OK` (Accepted but inefficient, with hint)**
```json
{
  "id": "95430c56-...",
  "status": "complete",
  "empirical_complexity": "O(n^2)",
  "confidence_score": 0.88,
  "structural_hint": "Your solution scans the array with a nested loop to find a pair. Consider a single pass with a HashMap...",
  "failure_detail": null,
  "test_results": [ ... ],
  "benchmark_curve": [ ... ]
}
```

### Verdict / status values

| `status` | Meaning |
|---|---|
| `pending` | Submission created, not yet picked up by the pipeline |
| `running_correctness` | Correctness check in progress |
| `failed` | Compilation error, runtime error, or wrong answer — see `failure_detail` |
| `benchmarking` | Correctness passed, complexity benchmarking in progress |
| `complete` | Fully judged; `empirical_complexity` and (if applicable) `structural_hint` populated |

## Users

### `GET /users/{id}/history`

Requires auth. A user may only fetch their own history (`403` otherwise). Paginated.

**Query params**: `limit` (default 20), `offset` (default 0)

**Response `200 OK`**
```json
[
  {
    "id": "95430c56-...",
    "problem_title": "Two Sum",
    "status": "complete",
    "empirical_complexity": "O(n^2)",
    "confidence_score": 0.88,
    "submitted_at": "2026-07-20T14:32:00Z"
  }
]
```

## Health

### `GET /health`

No auth required.

```json
{ "status": "ok" }
```
