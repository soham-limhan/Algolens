# AlgoLens — Database

## 1. Entity-Relationship Diagram

```
USER ||--o{ SUBMISSION : makes
PROBLEM ||--o{ SUBMISSION : "submitted for"
PROBLEM ||--o{ TESTCASE : has
PROBLEM ||--o{ INEFFICIENCY_SIGNATURE : has
SUBMISSION ||--o{ BENCHMARK_RUN : produces
```

A user makes many submissions. A problem has many test cases and many inefficiency signatures, and receives many submissions. Each submission produces many benchmark runs — one per scaled input size used during complexity analysis.

(See the project's Word/PDF documentation for the rendered ERD image.)

## 2. Tables

### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | String(36), PK | UUID |
| `name` | String(120) | |
| `email` | String(255), unique, indexed | |
| `password_hash` | String(255) | bcrypt hash — never plaintext |
| `created_at` | DateTime | |

### `problems`

| Column | Type | Notes |
|---|---|---|
| `id` | String(36), PK | UUID |
| `title` | String(200) | |
| `description` | Text | |
| `difficulty` | String(20) | `easy` \| `medium` \| `hard` |
| `optimal_time_complexity` | String(30) | e.g. `"O(n log n)"` |
| `optimal_space_complexity` | String(30) | |
| `generator_key` | String(80) | key into `app/problems_data/registry.py` — **not** the generator itself |

### `test_cases`

| Column | Type | Notes |
|---|---|---|
| `id` | String(36), PK | UUID |
| `problem_id` | String(36), FK → `problems.id` | |
| `input` | Text | raw stdin the submission will receive |
| `expected_output` | Text | |
| `comparator_type` | String(30) | `exact` \| `numeric_tolerance` \| `sorted` \| `custom` (see `TESTING.md`) |

### `inefficiency_signatures`

| Column | Type | Notes |
|---|---|---|
| `id` | String(36), PK | UUID |
| `problem_id` | String(36), FK → `problems.id` | |
| `pattern_type` | String(60) | e.g. `nested_loop_lookup`, `unmemoized_recursion` |
| `hint_text` | Text | shown to the learner when this pattern matches and a complexity gap exists |

### `submissions`

| Column | Type | Notes |
|---|---|---|
| `id` | String(36), PK | UUID |
| `user_id` | String(36), FK → `users.id` | |
| `problem_id` | String(36), FK → `problems.id` | |
| `source_code` | Text | |
| `status` | String(30) | `pending` \| `running_correctness` \| `failed` \| `benchmarking` \| `complete` |
| `empirical_complexity` | String(30), nullable | e.g. `"O(n^2)"` |
| `confidence_score` | Float, nullable | R² of the log-log regression fit, 0–1 |
| `structural_hint` | Text, nullable | populated only when a gap was found |
| `failure_detail` | Text, nullable | compiler output / failing test case detail |
| `submitted_at` | DateTime | |

### `benchmark_runs`

| Column | Type | Notes |
|---|---|---|
| `id` | String(36), PK | UUID |
| `submission_id` | String(36), FK → `submissions.id` | |
| `input_size` | Integer | |
| `runtime_ms` | Float | median of repeated runs at this size |
| `timed_out` | Boolean | true if every repetition at this size failed/timed out |

## 3. Problem Bank Storage Strategy

Problem data is deliberately split between the database and versioned application code:

| Data | Storage | Why |
|---|---|---|
| Problem metadata, optimal complexity | DB row | Structured facts, queried frequently |
| Fixed correctness test cases | DB row (input/output as text) | Small, static data |
| Scaled-input generators | Python module (`app/problems_data/<key>.py`), referenced by `generator_key` | Executable logic — unsafe and unnecessary to store as data or eval-able text |
| Inefficiency signature definitions | DB row (label + hint text) | Structured metadata |
| Inefficiency matching logic | Python code (`app/services/hints.py`) | Executable logic, reused across problems sharing a pattern type |
| Submission history, benchmark runs | DB row | Structured, queried per user/submission |

**Why not store generator logic as data?** A generic data-driven interpreter for "generate a random array of size n" is unnecessary complexity at 8–10 problems, and storing/`eval`-ing arbitrary code strings from the database is a real security risk — especially notable given the rest of the system exists specifically to safely execute untrusted code. Keeping generators as reviewable, testable, version-controlled files avoids both problems.

## 4. Migrations

`Base.metadata.create_all()` is used for schema creation at this project's scope — no Alembic migrations. If the schema needs to evolve after data already exists in a deployed instance, introduce Alembic at that point rather than hand-editing the live database.

## 5. SQLite (dev) vs. PostgreSQL (prod)

Controlled entirely by the `DATABASE_URL` environment variable — no code changes required elsewhere:

```
# Local dev (no Docker needed for quick iteration)
DATABASE_URL=sqlite:///./algolens.db

# Production (college server, via Docker Compose — see DEPLOYMENT.md)
DATABASE_URL=postgresql://algolens:PASSWORD@db:5432/algolens
```

**Environment update**: with Docker now available on the college server, PostgreSQL runs as a Compose service (`db`) rather than being a "maybe, if it can be installed without sudo" possibility. Production deployments should use Postgres, not SQLite — SQLite remains the default for fast local iteration only.
