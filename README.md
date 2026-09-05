# AlgoLens 🔍⚡

> **A Complexity-Aware Competitive Coding & Algorithmic Performance Benchmarking Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Java](https://img.shields.io/badge/Java-JDK_21-ED8B00.svg?style=flat-square&logo=openjdk&logoColor=white)](https://openjdk.org)
[![Groq](https://img.shields.io/badge/AI_Powered-Groq_Llama_3-F05032.svg?style=flat-square)](https://groq.com)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Why AlgoLens?](#-why-algolens)
- [Key Features](#-key-features)
- [System Architecture & Request Lifecycle](#-system-architecture--request-lifecycle)
- [Algorithmic Complexity Classification](#-algorithmic-complexity-classification)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Method 1: Docker Compose (Recommended)](#method-1-docker-compose-recommended)
  - [Method 2: Manual Local Setup](#method-2-manual-local-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Security & Sandboxing](#-security--sandboxing)
- [Documentation Index](#-documentation-index)
- [License & Credits](#-license--credits)

---

## 🌟 Overview

**AlgoLens** is an open-source, next-generation competitive programming platform that goes beyond standard binary pass/fail judging. While traditional judges only test whether a submission produces the expected output for small or static test suites, AlgoLens **empirically measures execution runtime across programmatically scaled inputs**, fits empirical growth curves using log-log regression, and determines your algorithm's real-world **Big-O time complexity class**.

If your solution passes all test cases but exhibits suboptimal asymptotic scaling (e.g., $O(n^2)$ instead of the optimal $O(n)$), AlgoLens detects the complexity gap, reveals structural inefficiency hints, generates interactive performance comparison graphs, and provides AI-powered algorithmic deep-dives via Groq.

---

## 💡 Why AlgoLens?

| Traditional Online Judges (LeetCode, HackerRank, etc.) | AlgoLens |
|---|---|
| Binary pass/fail verdict (AC, WA, TLE). | Two-stage evaluation: Correctness verification followed by empirical scaling benchmarking. |
| Inefficient $O(n^2)$ solutions often pass if test cases or timeouts are lenient. | Quantifies exact asymptotic scaling across scaled input sizes ($n = 100 \dots 1,000,000$). |
| Leaves the developer guessing why runtime was high. | Classifies empirical Big-O ($O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$, $O(2^n)$). |
| Complete solutions are often spoiled in discussion forums. | Provides non-spoiler structural hints (e.g., "Consider a HashMap lookup instead of nested iteration"). |
| Static runtime percentiles dependent on server load. | Multi-run warmup-filtered benchmarking with theoretical vs. empirical curve comparisons. |

---

## ✨ Key Features

- ⚙️ **Dual-Stage Pipeline**:
  - **Stage 1 (Correctness)**: Validates logic against curated edge cases and problem constraints.
  - **Stage 2 (Empirical Benchmarking)**: Executes code against dynamically scaled input batches to record execution times across orders of magnitude.
- 📐 **Empirical Complexity Classifier**: Fits power-law curves ($T(n) = c \cdot n^k$) using log-log ordinary least squares regression to calculate slope $k$, classifying the true empirical Big-O.
- 💡 **Structural Inefficiency Hint Engine**: Pattern matcher that inspects code structure for redundant nested loops, missing hash indexes, or inefficient data structures without spoiling the solution.
- 🤖 **AI-Powered Groq Engine**: Deep comparative algorithmic insights powered by Groq LLMs (Llama 3 / GPT-OSS models), breaking down time/space trade-offs, cache locality, and algorithmic paradigms.
- 🛡️ **Hardened Docker Sandbox**: Untrusted code is compiled and executed in disposable, ephemeral Linux containers with CPU quotas, memory limits (256MB), process limits (pids=64), wall-clock timeouts, and disabled networking.
- 📊 **Interactive Data Visualizations**: Real-time charts rendered using Recharts comparing user runtime curves against optimal theoretical curves.
- 💬 **Community Discussions & Forum**: Markdown-supported threaded discussions, upvoting/downvoting, category filtering, and AI assistant interactions.
- 🔐 **Production-Grade Auth & Security**: JWT authentication with short-lived access tokens and refresh rotation, Bcrypt password hashing, rate limiting, and OTP email verification for secure password recovery.
- 📝 **Dynamic Problem Creator**: Interface to create, test, and upload custom algorithmic problems with test suites and scaling generators.

---

## 🏗️ System Architecture & Request Lifecycle

```
                                  ┌───────────────────────────┐
                                  │   React + Vite Frontend   │
                                  │   (Monaco Editor, Charts) │
                                  └─────────────┬─────────────┘
                                                │ REST API (JWT)
                                                ▼
                                  ┌───────────────────────────┐
                                  │   FastAPI Application     │
                                  │  - Auth & Rate Limiting   │
                                  │  - Background Pipeline    │
                                  └─────────────┬─────────────┘
                                                │
                 ┌──────────────────────────────┴──────────────────────────────┐
                 ▼                                                             ▼
  ┌─────────────────────────────┐                               ┌─────────────────────────────┐
  │     Correctness Stage       │                               │       Database Layer        │
  │   - Fixed Test Cases        │                               │   PostgreSQL / SQLite       │
  │   - Ephemeral Sandbox       │                               │   - Users & Submissions     │
  └──────────────┬──────────────┘                               │   - Benchmark Data & Forum  │
                 │ (Passed)                                     └─────────────────────────────┘
                 ▼                                                             ▲
  ┌─────────────────────────────┐                                              │
  │    Benchmarking Stage       │                                              │
  │   - Scaled Inputs n1..nk    │                                              │
  │   - Runtime Measurements    │                                              │
  └──────────────┬──────────────┘                                              │
                 ▼                                                             │
  ┌─────────────────────────────┐       ┌─────────────────────────────┐        │
  │    Complexity Classifier    │ ───►  │ Structural Hint & Groq AI   │ ───────┘
  │   - Log-Log Regression      │ (Gap) │ - Pattern AST match         │ Persist &
  │   - Empirical Big-O Fit     │       │ - Algorithmic Insights      │ Stream to Client
  └─────────────────────────────┘       └─────────────────────────────┘
```

---

## 📈 Algorithmic Complexity Classification

AlgoLens models execution time as a power law:

$$T(n) \approx c \cdot n^k$$

Taking the natural logarithm of both sides yields a linear equation:

$$\ln T(n) = \ln c + k \cdot \ln n$$

By running linear regression over $(\ln n_i, \ln T_i)$, the engine calculates slope $k$:

| Measured Slope ($k$) / Growth | Classified Complexity | Common Examples |
|---|---|---|
| $k \approx 0$ | $O(1)$ | Hash lookups, math formulas |
| $k \in (0, 0.5)$ | $O(\log n)$ | Binary search, GCD |
| $k \in [0.8, 1.25]$ | $O(n)$ | Linear scan, Two Pointers, Sliding Window |
| $k \in (1.25, 1.65]$ | $O(n \log n)$ | Merge Sort, Heap Sort, Divide & Conquer |
| $k \in (1.65, 2.4]$ | $O(n^2)$ | Nested loops, Bubble Sort |
| $k > 2.4$ or exponential | $O(2^n) \text{ or } O(n^3)$ | Naive recursion, Matrix multiplication |

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework**: React 19 + Vite
- **Styling**: CSS Modules, Tailwind CSS, Responsive Design System
- **Code Editor**: Monaco Editor (`@monaco-editor/react`)
- **Data Visualization**: Recharts (Interactive Line & Scatter Charts)
- **Routing & State**: React Router v7, React Context API, Lucide Icons

### **Backend**
- **Framework**: FastAPI (Python 3.12+)
- **ORM & Database**: SQLAlchemy 2.0, PostgreSQL 16 (Production) / SQLite (Development)
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **Analysis Engine**: NumPy (Log-log OLS curve fitting)
- **AI Engine**: Groq Cloud SDK / HTTP client (Llama 3 / GPT-OSS)
- **Authentication**: PyJWT, Passlib (Bcrypt hashing)
- **Email System**: aiosmtplib (Asynchronous SMTP with OTP support)

### **Execution Sandbox & Infrastructure**
- **Isolation**: Disposable Docker containers with Linux cgroups (CPU/RAM/PIDs limits)
- **Language Runtime**: OpenJDK 21
- **Orchestration**: Docker Compose
- **Reverse Proxy / Production Server**: Nginx (Frontend static + Proxy) & Uvicorn (ASGI)

---

## 📁 Project Structure

```
Algolens/
├── docker-compose.yml           # Multi-container orchestration (DB, Backend, Frontend)
├── schema.sql                   # PostgreSQL database initialization DDL
├── backend/
│   ├── Dockerfile               # Backend API production container definition
│   ├── requirements.txt         # Production & development dependencies
│   ├── .env.example             # Example environment configuration
│   ├── app/
│   │   ├── main.py              # FastAPI application bootstrap & middleware
│   │   ├── config.py            # Pydantic env settings
│   │   ├── seed.py              # Problem bank & initial data seeder
│   │   ├── auth/                # Security, JWT tokens, bcrypt, auth dependencies
│   │   ├── db/                  # Engine setup, session management, declarative base
│   │   ├── models/              # SQLAlchemy ORM models (User, Problem, Submission, Forum)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API routes (auth, problems, submissions, forum)
│   │   ├── sandbox/             # Docker container lifecycle executor
│   │   ├── problems_data/       # Dynamic input generators for scaled benchmarking
│   │   └── services/            # Correctness, benchmark, complexity, Groq AI, hints
│   ├── sandbox/
│   │   └── Dockerfile           # Java 21 execution sandbox base image
│   └── tests/                   # Pytest test suite (unit, integration, sandbox)
├── frontend/
│   ├── Dockerfile               # Nginx + React production build
│   ├── package.json             # NPM dependencies & scripts
│   ├── vite.config.js           # Vite build configuration
│   ├── index.html               # Main HTML entry point
│   └── src/
│       ├── App.jsx              # Application router & layout provider
│       ├── api/                 # Axios / Fetch client wrappers
│       ├── context/             # AuthContext & global states
│       ├── components/          # Reusable UI components (Navbar, Editor, Graphs)
│       └── pages/               # Landing, ProblemList, Detail, Results, Forum, History
└── md_files/                    # In-depth architectural, security, and PRD specifications
```

---

## 🚀 Getting Started

### Prerequisites
- [Docker & Docker Compose](https://www.docker.com/get-started) (Recommended)
- *Or for local manual setup:*
  - Python 3.12+
  - Node.js 18+ and npm
  - OpenJDK 21 (`java` and `javac` available in `PATH`)

---

### Method 1: Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/algolens.git
   cd algolens
   ```

2. **Configure environment variables**:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Edit `backend/.env` to supply your desired `JWT_SECRET` and optional `GROQ_API_KEY`.*

3. **Build the sandbox image**:
   ```bash
   docker build -t algolens-sandbox:latest ./backend/sandbox/
   ```

4. **Launch all services**:
   ```bash
   docker compose up --build
   ```

5. **Access the application**:
   - **Frontend App**: `http://localhost:3000`
   - **Backend API Docs**: `http://localhost:8000/docs`
   - **PostgreSQL**: `localhost:5432`

---

### Method 2: Manual Local Setup

#### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment file
cp .env.example .env

# Initialize database & seed curated problems
python -m app.seed

# Start the development server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

## ⚙️ Environment Variables

Configure these in `backend/.env`:

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://...` / `sqlite:///./algolens.db` | Database connection URI |
| `JWT_SECRET` | *(Required)* | Secret key for signing JWT tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `30` | Access token lifespan |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan |
| `GROQ_API_KEY` | `""` | API key for Groq AI features (optional) |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Groq AI LLM model name |
| `SANDBOX_IMAGE_NAME` | `algolens-sandbox:latest` | Docker image tag for running Java code |
| `SANDBOX_MEMORY_MB` | `256` | RAM ceiling per sandboxed execution |
| `SANDBOX_WALL_TIMEOUT_S` | `10` | Hard timeout limit for code execution |
| `BENCHMARK_INPUT_SIZES` | `100,1000,10000,100000,1000000` | Input size array $n_1 \dots n_k$ |
| `BENCHMARK_REPETITIONS` | `3` | Iterations per input size for variance reduction |
| `SMTP_ENABLED` | `false` | Enable/disable SMTP email delivery for OTPs |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000`| Allowed frontend origins |

---

## 📡 API Reference

Explore the interactive Swagger documentation at `http://localhost:8000/docs`.

### Key Endpoints:

| Category | Method | Path | Description |
|---|---|---|---|
| **Auth** | `POST` | `/auth/register` | Register new user account |
| | `POST` | `/auth/login` | Authenticate & receive access/refresh tokens |
| | `POST` | `/auth/refresh` | Rotate expired access token using refresh token |
| | `POST` | `/auth/forgot-password` | Request password reset OTP via email |
| | `POST` | `/auth/reset-password` | Verify OTP and set new password |
| **Problems** | `GET` | `/problems` | List problem bank with search/difficulty filters |
| | `GET` | `/problems/{id}` | Retrieve problem details and starter code |
| | `POST` | `/problems` | Upload / create a custom problem |
| **Submissions** | `POST` | `/submissions` | Submit code for asynchronous judging & benchmark |
| | `GET` | `/submissions/{id}` | Poll submission status, verdict, and curve data |
| | `GET` | `/submissions/history` | Retrieve user's historical submissions |
| | `POST` | `/submissions/{id}/groq-insights` | Request AI-powered comparative analysis |
| **Forum** | `GET` | `/forum/threads` | List discussion threads by problem/tag |
| | `POST` | `/forum/threads` | Create a discussion topic |
| | `POST` | `/forum/threads/{id}/posts` | Post a comment or reply in a thread |

---

## 🧪 Testing

AlgoLens includes a test suite covering authentication, sandbox execution, regression accuracy, security policies, and rate limits.

```bash
cd backend

# Run entire test suite
pytest

# Run tests with verbose output and coverage
pytest -v --tb=short

# Run specific sandbox or complexity tests
pytest tests/test_sandbox.py
pytest tests/test_complexity.py
```

---

## 🔒 Security & Sandboxing

AlgoLens executes arbitrary, user-submitted code in an untrusted execution environment. The isolation layer enforces:

1. **Ephemeral Containers**: A clean container is spun up and torn down for each execution; state is never retained.
2. **Network Isolation**: Networking is disabled (`network_mode="none"`), preventing socket connections, data exfiltration, or external attacks.
3. **Resource Quotas**:
   - Memory strictly capped at `256MB` via Docker memory cgroups.
   - CPU quota limited via cgroup CFS scheduler (`cpu_quota=50000`, `cpu_period=100000`).
   - Process limit (`pids_limit=64`) prevents fork bombs.
4. **Filesystem Constraints**: Containers run with read-only root filesystems and restricted temporary directories.
5. **Static Code Validation**: Source code size is capped at 64 KB and inspected before compilation.

---

## 📚 Documentation Index

For in-depth technical documents, check the [`md_files/`](./md_files/) directory:

- 📐 [`ARCHITECTURE.md`](./md_files/ARCHITECTURE.md) — Detailed system design, data flow, and components.
- 📋 [`PRD.md`](./md_files/PRD.md) — Product requirements document & project goals.
- 🗄️ [`DATABASE.md`](./md_files/DATABASE.md) — Relational schema, ERD diagrams, and design rationales.
- 🔌 [`API.md`](./md_files/API.md) — Complete endpoint reference with payload examples.
- 🛡️ [`SECURITY.md`](./md_files/SECURITY.md) — Sandboxing mechanics, threat model, and mitigation strategies.
- 🎨 [`UI_UX.md`](./md_files/UI_UX.md) — Design system, color palette, and layout specifications.
- 🧪 [`TESTING.md`](./md_files/TESTING.md) — Testing strategy, test cases, and coverage standards.
- 🚀 [`DEPLOYMENT.md`](./md_files/DEPLOYMENT.md) — Production deployment guidelines with Docker & Nginx.

---

## 📄 License & Credits

Built with ❤️ as a final-year MCA Capstone Project.
Distributed under the MIT License.
