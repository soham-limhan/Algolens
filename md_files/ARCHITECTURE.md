# AlgoLens — Architecture

## 1. High-Level Design

Three-tier architecture: React frontend → FastAPI application layer → isolated sandbox execution layer, backed by a relational data store. The sandbox layer is deliberately decoupled from the main API process so a runaway or malicious submission can't affect availability for other users.

```
Client (React)
     │
     ▼
API layer (FastAPI) — auth, routing, job orchestration
     │
     ▼
Correctness sandbox — runs vs. fixed test cases
     │  (if all pass)
     ▼
Benchmark sandbox — runs at scaled input sizes n1..nk
     │
     ▼
Complexity classifier — log-log regression fit
     │  (if gap found)
     ▼
Structural hint engine — AST/pattern match
     │
     ▼
Data store — problems, submissions, benchmark runs
     │
     ▼
Response to client — curve, complexity class, hints rendered
```

## 2. Component Responsibilities

| Layer | Responsibility | Key Technologies |
|---|---|---|
| Presentation | Code editor, problem browser, results dashboard, complexity-curve visualization | React, Monaco Editor, Recharts |
| Application / API | Auth, problem management, submission orchestration, feedback assembly | FastAPI, Pydantic, SQLAlchemy |
| Execution Sandbox | Isolated execution of submitted code in disposable Docker containers | Docker (containers, cgroups, network isolation) |
| Analysis Engine | Pattern detection, curve-fitting, complexity classification | Regex/token matching, NumPy |
| Data Store | Problem bank, submission history, complexity reference table | PostgreSQL (Dockerized) |

> **Update (environment change):** Docker + root access are now confirmed available on the college deployment server. The sandbox has been migrated from the original subprocess + OS-resource-limits + Java Security Manager design to real container-based isolation. The original design is kept in `SECURITY.md`'s history for reference, since it's still the right fallback if container access is ever lost — but it is no longer the primary isolation mechanism.

## 3. Folder Structure

```
backend/app/
├── config.py             # pydantic-settings, env-driven
├── db/
│   └── database.py       # engine, SessionLocal, Base, get_db dependency
├── models/                # SQLAlchemy ORM tables
│   ├── user.py
│   ├── problem.py         # Problem, TestCase, InefficiencySignature
│   └── submission.py      # Submission, BenchmarkRun
├── schemas/                # Pydantic request/response models
│   ├── auth.py
│   ├── problem.py
│   └── submission.py
├── auth/
│   ├── security.py        # password hashing, JWT create/decode
│   ├── dependencies.py    # get_current_user
│   └── router.py          # /auth/register, /login, /refresh
├── sandbox/
│   └── executor.py        # CompiledSubmission (see SECURITY.md for detail)
├── problems_data/
│   ├── registry.py        # generator_key -> generate() function map
│   └── <problem>.py       # one scaled-input generator module per problem
├── services/
│   ├── correctness.py     # test-case verification + comparators
│   ├── benchmark.py       # scaled-input benchmarking loop
│   ├── complexity.py      # log-log regression classifier
│   ├── hints.py           # structural inefficiency pattern matcher
│   └── pipeline.py        # orchestrates the full submission flow
├── routers/
│   ├── problems.py
│   └── submissions.py
├── seed.py
└── main.py
```

Why generators live in `problems_data/` as code rather than database rows: a scaled-input generator is executable logic ("produce a random array of size n"), not structured data. Storing it as DB rows would need either a generic interpreter (unnecessary at 8–10 problems) or `eval`-ing stored strings (a real security risk, ironic given the rest of the system exists to safely run untrusted code). See `DATABASE.md` for the full storage-split rationale.

## 4. Data Flow (Request Lifecycle)

1. Client sends `POST /submissions` with problem ID and source code.
2. API creates a `Submission` row (`status=pending`), returns the ID immediately — does not block on execution.
3. A background task runs the **correctness sandbox** against the problem's fixed test cases.
4. Any failing test case → `status=failed`, verdict + failing case detail stored, pipeline stops.
5. All pass → **benchmark sandbox** runs across scaled input sizes, recording runtime at each.
6. **Complexity classifier** fits a log-log regression, produces a class label + confidence score.
7. If empirical class is worse than the problem's known optimum → **structural hint engine** matches against known inefficiency patterns.
8. Results persisted; `status=complete`.
9. Client, polling `GET /submissions/{id}`, renders verdict, curve, classification, and hint.

## 5. Why Correctness and Benchmarking Are Separate Stages

They share the **same underlying sandbox primitive** (`CompiledSubmission`) — this isn't two isolation systems, just two different uses of one:

| Aspect | Correctness stage | Benchmark stage |
|---|---|---|
| Input source | Small, fixed, hand-picked test cases | Programmatically scaled inputs (n = 100…1,000,000) |
| Purpose | Catch logical bugs | Reveal growth/scaling behaviour |
| Timeout | Short, fixed (~2–3s) | Longer, scales with input size |
| A run failing means | The submission is incorrect | Evidence of poor complexity, not necessarily a bug |

Gating benchmarking behind correctness avoids spending 6–8 sandboxed runs on code that doesn't even solve the problem.

## 6. Why Structural Hints Run After Complexity Classification

Both analyses are technically independent, but hint generation only runs when the classifier has already found a gap — an efficiency choice (don't do the extra AST/pattern work when there's nothing to explain), not a technical dependency.

## 7. Scalability & Concurrency

- Submission creation is asynchronous (`BackgroundTasks`); the client polls rather than the request blocking.
- A future job queue (Celery/Redis) is the natural upgrade path if concurrent submissions ever need capping independently of the web server's own concurrency — not implemented in v1, since in-process background tasks are sufficient at this scale.
- The API layer is stateless (JWT-based auth), so it can scale independently of the sandbox execution layer, which is the actual bottleneck resource.

## 8. Known Limitations

- Empirical complexity estimation is approximate — runtime is affected by hardware, JIT warm-up, and GC pauses, not just algorithmic complexity. Adjacent classes (e.g. O(n) vs O(n log n)) can be hard to distinguish without a wide input-size range.
- Scaled-input testing is vulnerable to submissions that special-case known input patterns; per-repetition re-randomization mitigates but doesn't eliminate this.
- Sandbox isolation now uses real Docker containers (filesystem and PID namespaces isolated via the container runtime) — the earlier resource-limit-only design is retained as a documented fallback in `SECURITY.md` in case container access is ever unavailable again.
- Structural hints are regex/token-based, not full AST parsing — can misfire on code that's structurally similar to a known inefficiency but contextually necessary.
- Limited to Java submissions and a curated problem bank with well-defined optimal complexities.

## 9. Future Work

- Multi-language support, now more tractable with per-language Docker images available.
- Consider gVisor or a similar runtime for even stronger isolation than the default Docker runtime, now that root access exists to support it.
- ML-based complexity classification to improve robustness over pure log-log regression.
- LLM-assisted, code-specific inefficiency explanations.
- Personalized practice recommendations from submission history.
- Community-contributed problems with a moderation workflow (see design discussion — requires either restricting community problems to correctness-only judging, or sandboxing community-submitted generators through the same `CompiledSubmission` primitive).
