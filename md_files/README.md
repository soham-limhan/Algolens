# AlgoLens

**A complexity-aware competitive coding platform.** Submit a Java solution, get judged like a standard online judge (Accepted / Wrong Answer / Runtime Error / Compilation Error / Time Limit Exceeded) — and if your solution is correct but inefficient, see exactly how its measured time complexity compares to the optimal, with a hint pointing at what to reconsider.

Built as a final-year capstone project (MCA).

## Why

Most coding-practice platforms tell you pass/fail and stop there. A brute-force O(n²) solution and an optimal O(n) solution both get a green checkmark. AlgoLens closes that gap: it empirically measures your submission's runtime growth across scaled inputs, classifies its complexity class, and compares it to the problem's known optimum — without ever handing you the answer.

## Features

- Standard online-judge flow: submit Java code, get a real verdict against fixed test cases.
- Sandboxed, isolated execution of untrusted code (no Docker required — built for an SSH-only, non-root server).
- Empirical time-complexity classification via log-log regression on measured runtime data.
- Structural hints (e.g. "consider a HashMap instead of a nested loop") shown only when a genuine complexity gap exists.
- Submission history per user.
- JWT-based authentication with access/refresh token rotation.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Tailwind CSS, Monaco Editor, Recharts |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic v2 |
| Database | PostgreSQL (Docker Compose service, prod) / SQLite (fast local dev) |
| Sandbox | Java (JDK 21) in disposable Docker containers — CPU/memory/pids cgroup limits, network disabled, read-only filesystem |
| Auth | PyJWT, Passlib (bcrypt) |
| Complexity analysis | NumPy (log-log linear regression) |
| Deployment | Docker Compose on the college server (root/Docker confirmed available); Jenkins CI/CD (planned) |

> Docker + root access were confirmed available on the college deployment server after initial planning — the sandbox and deployment both migrated from an original SSH-only, non-root design to Docker-based isolation. See `CHANGELOG.md` for the migration entry and `SECURITY.md` for the retained non-Docker fallback design.

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the full system design and [`DATABASE.md`](./DATABASE.md) for the schema.

## Project Structure

```
backend/
├── app/
│   ├── config.py            # env-based settings
│   ├── db/                  # SQLAlchemy engine/session/base
│   ├── models/               # ORM: User, Problem, TestCase, InefficiencySignature,
│   │                         # Submission, BenchmarkRun
│   ├── schemas/               # Pydantic request/response models
│   ├── auth/                  # login module: hashing, JWT, dependencies, router
│   ├── sandbox/                # CompiledSubmission — the sandbox executor
│   ├── problems_data/          # per-problem scaled-input generators (code, not DB rows)
│   ├── services/                # correctness, benchmark, complexity, hints, pipeline
│   ├── routers/                  # problems, submissions
│   └── main.py                   # app assembly
├── tests/
├── requirements.txt
└── .env.example
frontend/
└── (React app — see UI_UX.md)
```

## Getting Started (local dev)

### Prerequisites
- Python 3.12+
- JDK 21 (`java` and `javac` on PATH)
- Node.js (for the frontend)

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed          # populate the problem bank
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` once running.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Documentation Index

| File | Purpose |
|---|---|
| [`PRD.md`](./PRD.md) | What's being built and why |
| [`TASKS.md`](./TASKS.md) | Feature checklist and progress |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | System design, module breakdown, data flow |
| [`API.md`](./API.md) | Endpoint reference with examples |
| [`DATABASE.md`](./DATABASE.md) | Schema, ERD, relationships |
| [`UI_UX.md`](./UI_UX.md) | Design system, palette, component hierarchy |
| [`CODING_STANDARDS.md`](./CODING_STANDARDS.md) | Naming, formatting, conventions |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Workflow for contributors |
| [`CHANGELOG.md`](./CHANGELOG.md) | Version history |
| [`TESTING.md`](./TESTING.md) | Test strategy and coverage |
| [`DEPLOYMENT.md`](./DEPLOYMENT.md) | Deploying to the college server |
| [`SECURITY.md`](./SECURITY.md) | Auth, sandboxing, and security practices |
| [`AI_CONTEXT.md`](./AI_CONTEXT.md) | Context for AI coding assistants working on this repo |

## License

Academic capstone project — [add license if applicable].
