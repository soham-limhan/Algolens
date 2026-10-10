# AlgoLens 🔍⚡

> **A Complexity-Aware Competitive Coding & Algorithmic Performance Benchmarking Platform**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com)
[![Redis](https://img.shields.io/badge/Redis-Cache-DC382D.svg?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Java](https://img.shields.io/badge/Java-JDK_21-ED8B00.svg?style=flat-square&logo=openjdk&logoColor=white)](https://openjdk.org)
[![C++](https://img.shields.io/badge/C++-C++20-00599C.svg?style=flat-square&logo=c%2B%2B&logoColor=white)](https://isocpp.org)
[![Groq](https://img.shields.io/badge/AI_Powered-Groq_Llama_3-F05032.svg?style=flat-square)](https://groq.com)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Why AlgoLens?](#-why-algolens)
- [Key Features](#-key-features)
- [Supported Languages & Runtimes](#-supported-languages--runtimes)
- [System Architecture & Request Lifecycle](#-system-architecture--request-lifecycle)
- [Algorithmic Complexity Classification](#-algorithmic-complexity-classification)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Method 1: One-Click Quick Launch (Windows)](#method-1-one-click-quick-launch-windows)
  - [Method 2: Docker Compose (Recommended)](#method-2-docker-compose-recommended)
  - [Method 3: Manual Local Setup](#method-3-manual-local-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Security & Sandboxing](#-security--sandboxing)
- [Documentation Index](#-documentation-index)
- [License & Credits](#-license--credits)

---

## 🌟 Overview

**AlgoLens** is an open-source competitive programming and performance benchmarking platform that goes beyond binary pass/fail judging. While standard judges only test whether a submission produces expected output on static test suites, AlgoLens **measures execution runtime across programmatically scaled inputs ($N = 100 \dots 1,000,000$)**, fits empirical growth curves, and determines your algorithm's real-world **Big-O time complexity class**.

If your solution passes all test cases but exhibits suboptimal asymptotic scaling (such as $O(n^2)$ instead of an optimal $O(n)$), AlgoLens detects the complexity gap, reveals non-spoiler structural inefficiency hints, plots interactive empirical runtime curves against theoretical limits, and provides comparative algorithmic deep-dives powered by Groq LLMs.

AlgoLens also features **SQL & MySQL database challenges** with tabular visualizers and diff inspectors, **instant sample test runs**, **high-throughput Redis caching**, an **interactive community forum** with user mentions and threaded discussions, and a **global navigation search** with keyboard shortcuts.

---

## 💡 Why AlgoLens?

| Traditional Online Judges (LeetCode, HackerRank, etc.) | AlgoLens |
|---|---|
| Binary pass/fail verdict (AC, WA, TLE). | Dual-stage evaluation: Functional correctness verification followed by empirical scaling benchmarking. |
| Inefficient $O(n^2)$ solutions pass if test inputs or timeouts are lenient. | Quantifies asymptotic scaling across dynamically scaled inputs ($n = 100 \dots 1,000,000$). |
| Leaves the developer guessing why runtime was high. | Classifies empirical Big-O ($O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$, $O(n^3)$, $O(2^n)$) with $R^2$ confidence. |
| Complete solutions are often spoiled in discussion forums. | Provides non-spoiler structural hints (e.g., "Consider a hash table lookup instead of nested iteration"). |
| Single-language judge or rigid execution without tabular feedback. | Multi-language support (Java, Python, C++, C, JS, SQL, MySQL) with interactive SQL table diffs. |
| Static runtime percentiles dependent on arbitrary server load. | Multi-run warmup-filtered benchmarking with theoretical vs. empirical curve comparisons and execution timeout safeguards. |

---

## ✨ Key Features

- ⚙️ **Dual-Stage Judging Pipeline**:
  - **Stage 1 (Correctness)**: Validates logic against curated edge cases, problem constraints, and custom inputs.
  - **Stage 2 (Empirical Benchmarking)**: Executes compiled code against scaled input batches ($n_1 \dots n_k$) to record execution times across orders of magnitude.
- ⏱️ **Benchmark Timeout & Safety Guard**:
  - Strict total wall-clock budget limit (`BENCHMARK_TOTAL_TIMEOUT_S`, default 10.0s).
  - Early-abort heuristics for consecutive timeouts and budget exhaustion, preventing long-running or non-terminating submissions from blocking workers.
  - Warmup runs and median aggregation across repetitions to filter JIT and system noise.
- 🔍 **Instant Global Search (`Ctrl+K` / `Cmd+K`)**:
  - Real-time search in the navbar across problem titles, tags, and forum discussions.
  - Keyboard navigation (`Up`/`Down`/`Enter`) and quick difficulty and category indicators.
- 📐 **Dual Complexity Classifier (AI + Mathematical Regression)**:
  - **Groq AI Evaluation**: Evaluates AST structure, loop nesting, recursive branching, and empirical points to explain asymptotic behavior and trade-offs.
  - **Log-Log Regression Fallback**: Fits power-law curves ($T(n) = c \cdot n^k$) using ordinary least squares regression, baseline overhead subtraction, tail slope analysis, and $R^2$ goodness-of-fit confidence calculation.
- ⚡ **Instant "Run Code" Mode**:
  - Test sample inputs and view instant correctness verdicts without waiting for full asynchronous asymptotic benchmarking.
- 🌐 **Polyglot & Multi-Language Support**:
  - First-class support for **Java 21**, **Python 3.12+**, **C++ (C++20)**, **C (C11)**, **JavaScript (Node.js)**, **SQL**, and **MySQL**.
  - Context-aware starter code generation for each problem and language.
- 🗄️ **Database & SQL Sandbox Engine**:
  - Dedicated database problems covering joins, window functions, aggregations, self-joins, and subqueries.
  - Built-in SQLite execution engine with MySQL function compatibility shims (`DATEDIFF`, `IF`, `CONCAT`, `MOD`, `NOW`, `CURDATE`).
  - Interactive **SQL Table Visualizer** (`SqlTableOutput`) that renders formatted tables, row counts, and column-by-column expected vs. actual diffs.
- 💡 **Structural Inefficiency Hint Engine**:
  - Pattern matcher that inspects source code AST and structure for redundant nested loops, missing hash indexes, or inefficient lookups without spoiling the solution.
- 🤖 **AI-Powered Groq Engine**:
  - Comparative algorithmic insights powered by Groq LLMs (Llama 3 / GPT-OSS models), breaking down time/space trade-offs, cache locality, and algorithmic paradigms.
- 🚀 **High-Performance Redis Caching**:
  - Caching layer for problem catalogs, problem details, forum threads, user history, and user mentions.
  - Automatic pattern-based cache invalidation on writes with graceful fallback when Redis is offline.
- 🛡️ **Hardened Multi-Layer Sandbox**:
  - Ephemeral Linux containers with CPU quotas (50% single-core cap), memory limits (256MB), process limits (pids=64), wall-clock timeouts, and disabled networking.
  - Automatic fallback to secure local subprocess isolation when running without Docker.
- 💬 **Interactive Community Forum**:
  - Threaded discussions with category filters, popular/newest sorting, and keyword search.
  - Autocomplete user `@mentions`, multi-level nested replies, and like/upvote toggles.
- 📊 **Revamped Submission History & Analytics**:
  - User statistics dashboard tracking unique problems solved, acceptance rates, and language breakdown.
  - Filter by verdict status (`All`, `Accepted`, `Failed`), language, and problem title.
  - In-browser code preview modal with a one-click "Open in Editor" shortcut.
- 🔐 **Production-Grade Auth & Security**:
  - JWT authentication with access/refresh token rotation.
  - Dual email OTP verification: secure OTP verification on **Registration** and **Password Reset** via SMTP with HTML email templates.
  - Interactive profile management with live password strength meters and username updates.
- 🎨 **Unified Modern Dark UI**:
  - Custom Monaco editor theme (`algolens-dark`), responsive split-pane problem detail views, interactive Recharts curves, and styled verdict badges.
- 🚀 **One-Click Local Launcher**:
  - Pre-configured Windows batch scripts (`start-all.bat`) to launch backend and frontend simultaneously in dedicated console windows.

---

## 💻 Supported Languages & Runtimes

| Language | Version / Standard | Compiler / Engine | Compilation / Verification |
|---|---|---|---|
| **Java** | OpenJDK 21 | `javac` / `java` | Compiled with `--release 21 -Xmx256m` |
| **Python** | Python 3.12+ | CPython | Syntax-checked via `py_compile`, executed isolated |
| **C++** | C++20 | `g++` / `clang++` | Optimized build: `-O2 -std=c++20` |
| **C** | C11 | `gcc` / `clang` | Optimized build: `-O2 -std=c11` |
| **JavaScript** | Node.js (ES2022+) | `node` | Syntax-checked via `node --check` |
| **SQL / MySQL** | ANSI SQL / MySQL 8.0+ | SQLite In-Memory Engine | DDL/DML setup isolation with MySQL function shims |

---

## 🏗️ System Architecture & Request Lifecycle

```
                                  ┌───────────────────────────┐
                                  │   React + Vite Frontend   │
                                  │ (Monaco, Global Search,   │
                                  │  Charts, SQL Table Viewer)│
                                  └─────────────┬─────────────┘
                                                │ REST API (JWT)
                                                ▼
                                  ┌───────────────────────────┐
                                  │   FastAPI Application     │
                                  │  - Auth, OTP & Rate Limit │
                                  │  - Pipeline Orchestrator  │
                                  └─────┬───────────────┬─────┘
                                        │               │
                 ┌──────────────────────┴──────┐        │ Cache & Lookups
                 ▼                             ▼        ▼
  ┌─────────────────────────────┐   ┌─────────────────────────────┐
  │     Execution Sandbox       │   │    Redis Caching Layer      │
  │  - Java, Python, C++, C, JS │   │  - Problem Catalog & Detail │
  │  - SQLite / MySQL Sandbox   │   │  - Forum & User Mentions    │
  │  - Ephemeral Docker Cgroup  │   └─────────────────────────────┘
  └──────────────┬──────────────┘               │
                 │ (Passed)                     ▼
                 ▼                  ┌─────────────────────────────┐
  ┌─────────────────────────────┐   │       Database Layer        │
  │    Benchmarking Stage       │   │   PostgreSQL / MySQL / SQLite│
  │   - Scaled Inputs n1..nk    │   │   - Users & Submissions     │
  │   - Timeout Protection      │   │   - Benchmark Data & Forum  │
  │   - Multi-Run Median        │   └─────────────────────────────┘
  └──────────────┬──────────────┘               ▲
                 ▼                              │
  ┌─────────────────────────────┐               │
  │    Complexity Classifier    │ ──────────────┤
  │   - Groq AI Code & Points   │  Persist &    │
  │   - Log-Log OLS Regression  │  Stream via   │
  │   - R² Confidence & Hints   │  API Polling  │
  └─────────────────────────────┘
```

---

## 📈 Algorithmic Complexity Classification

AlgoLens models execution time as a power law:

$$T(n) \approx c \cdot n^k$$

Taking the natural logarithm of both sides yields a linear equation:

$$\ln T(n) = \ln c + k \cdot \ln n$$

By running ordinary least squares linear regression over $(\ln n_i, \ln T_i)$, correcting for constant process overhead at lower input sizes, and evaluating asymptotic tail growth, the engine determines slope $k$:

| Measured Slope ($k$) / Growth | Classified Complexity | Common Examples |
|---|---|---|
| $k < 0.15$ or ratio $< 1.35$ | $O(1)$ | Hash table lookups, constant-time math |
| $k \in [0.15, 0.50)$ and ratio $< 6.0$ | $O(\log n)$ | Binary search, Euclidean GCD |
| $k \in [0.50, 1.06)$ | $O(n)$ | Linear scan, Two Pointers, Sliding Window |
| $k \in [1.06, 1.45)$ | $O(n \log n)$ | Merge Sort, Heap Sort, Divide & Conquer |
| $k \in [1.45, 2.45)$ | $O(n^2)$ | Nested iterations, Bubble Sort |
| $k \in [2.45, 3.45)$ | $O(n^3)$ | Floyd-Warshall, Matrix multiplication |
| $k \ge 3.45$ or exponential | $O(2^n)$ | Unmemoized recursion, subsets |

When Groq AI is enabled, the classifier performs a hybrid evaluation: analyzing source code control flow, recursion trees, and helper functions alongside empirical timing points, providing both an asymptotic class and an explanation of the underlying structural trade-offs.

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework**: React 19 + Vite 6
- **Styling**: CSS Modules, Custom Dark Design System (`index.css`)
- **Code Editor**: Monaco Editor (`@monaco-editor/react`) with custom syntax theme (`monacoTheme.js`)
- **Visualizations**: Recharts (Interactive Line & Scatter Charts)
- **Database Output Viewer**: Custom `SqlTableOutput` with ASCII grid & HTML comparison tables
- **Routing & State**: React Router v7, React Context API, Lucide Icons

### **Backend**
- **Framework**: FastAPI (Python 3.12+)
- **ORM & Database Support**: SQLAlchemy 2.0 supporting:
  - **SQLite** (Default local development)
  - **PostgreSQL 16** (Production deployment)
  - **MySQL 8.0+ / MariaDB** (Production/Enterprise)
- **Caching**: Redis 5.0+ via `redis-py` (with automatic graceful fallback)
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **Analysis Engine**: NumPy (Log-log OLS curve fitting, tail slope, and variance calculations)
- **AI Engine**: Groq Cloud SDK / HTTP client (Llama 3 / GPT-OSS models)
- **Authentication**: PyJWT, Passlib (Bcrypt hashing)
- **Email & OTP System**: Standard `smtplib` / `aiosmtplib` with HTML transactional templates

### **Execution Sandbox & Infrastructure**
- **Isolation**: Ephemeral Docker containers with Linux cgroups (CPU, RAM, PID limits)
- **Language Runtimes**: OpenJDK 21, Python 3.12, GCC/G++ (C11/C++20), Node.js, SQLite3
- **Orchestration**: Docker Compose
- **Server**: Uvicorn (ASGI) & Nginx (Production reverse proxy)

---

## 📁 Project Structure

```
Algolens/
├── start-all.bat                # One-click Windows launcher (FastAPI + Vite)
├── start-backend.bat            # Dedicated backend startup script
├── start-frontend.bat           # Dedicated frontend startup script
├── docker-compose.yml           # Multi-container orchestration (DB, Backend, Frontend)
├── schema.sql                   # PostgreSQL/MySQL database initialization DDL
├── backend/
│   ├── Dockerfile               # Backend API production container definition
│   ├── requirements.txt         # Core dependencies (FastAPI, Redis, SQLAlchemy, etc.)
│   ├── requirements-prod.txt    # Production dependencies
│   ├── .env.example             # Example environment configuration
│   ├── app/
│   │   ├── main.py              # FastAPI application bootstrap, middleware & lifespans
│   │   ├── config.py            # Pydantic env settings (DB, Redis, Sandbox, SMTP, Groq)
│   │   ├── seed.py              # Problem bank & initial data seeder
│   │   ├── database_problems.py # Curated SQL/MySQL problems, schemas & test cases
│   │   ├── auth/                # Security, JWT tokens, bcrypt, OTP handlers
│   │   ├── db/                  # Engine setup (SQLite, Postgres, MySQL) & sessions
│   │   ├── models/              # SQLAlchemy ORM models (User, Problem, Submission, Forum)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── routers/             # API routes (auth, problems, submissions, forum)
│   │   ├── sandbox/             # Multi-language compiler & container executor
│   │   ├── problems_data/       # Scaled generators for algorithmic & SQL problems
│   │   │   ├── registry.py      # Generator registry mapping
│   │   │   └── sql_generators.py# Dynamic SQL test data scaling generators
│   │   └── services/            # Pipeline, benchmark, complexity, Groq, cache, email
│   │       ├── benchmark.py     # Scaled-input benchmarking with timeout guards
│   │       ├── cache.py         # Redis caching service with pattern invalidation
│   │       ├── complexity.py    # AI + log-log regression complexity classifier
│   │       ├── correctness.py   # Multi-language & SQL tabular correctness verifier
│   │       ├── email.py         # SMTP OTP and account creation notification sender
│   │       ├── hints.py         # Structural inefficiency non-spoiler hints
│   │       └── pipeline.py      # Dual-stage submission pipeline orchestrator
│   ├── sandbox/
│   │   └── Dockerfile           # Multi-language execution sandbox base image
│   └── tests/                   # Pytest test suite (12 comprehensive test modules)
│       ├── test_auth_passwords.py
│       ├── test_benchmark_timeout.py
│       ├── test_cache.py
│       ├── test_complexity_classifier.py
│       ├── test_correctness_comparators.py
│       ├── test_database_problems.py
│       ├── test_email.py
│       ├── test_forum.py
│       ├── test_groq_service.py
│       ├── test_multi_sandbox.py
│       ├── test_sandbox_robustness.py
│       ├── test_submission_pipeline_integration.py
│       └── test_validation.py
├── frontend/
│   ├── Dockerfile               # Nginx + React production build
│   ├── package.json             # NPM dependencies & scripts
│   ├── vite.config.js           # Vite build configuration
│   ├── index.html               # Main HTML entry point
│   └── src/
│       ├── App.jsx              # Application router & layout provider
│       ├── api/                 # Axios client with auth interceptors
│       ├── auth/                # AuthContext & session state management
│       ├── components/          # Reusable UI components
│       │   ├── AiInsightsCard.jsx       # Groq AI algorithmic breakdown
│       │   ├── AuthShowcase.jsx         # Visual authentication showcase card
│       │   ├── CodeComparisonPanel.jsx  # Submission vs optimal code diff
│       │   ├── ComplexityChart.jsx      # Recharts empirical vs theoretical curves
│       │   ├── HintCard.jsx             # Non-spoiler structural hints
│       │   ├── Navbar.jsx               # Header with global search (Ctrl+K)
│       │   ├── PasswordStrengthMeter.jsx# Real-time password entropy scoring
│       │   ├── ProfileModal.jsx         # Profile management & password updates
│       │   ├── SqlTableOutput.jsx       # Tabular SQL visualizer & diff viewer
│       │   ├── StreakMap.jsx            # Activity & submission consistency heatmap
│       │   ├── TestCasePanel.jsx        # Test suite runner & custom input runner
│       │   └── VerdictBanner.jsx        # Status banner with complexity metrics
│       ├── pages/               # Landing, ProblemList, Detail, Results, Forum, History
│       └── utils/
│           ├── monacoTheme.js           # Custom Algolens dark theme for Monaco
│           └── starterSnippets.js       # Polyglot starter code generator
└── md_files/                    # In-depth architectural, security, and PRD specifications
```

---

## 🚀 Getting Started

### Prerequisites
- [Python 3.12+](https://python.org)
- [Node.js 18+](https://nodejs.org) and npm
- [OpenJDK 21](https://adoptium.net) (`java` and `javac` available in `PATH`)
- *(Optional)* [Docker Desktop](https://www.docker.com/get-started) (for containerized sandboxing)
- *(Optional)* [Redis](https://redis.io) (for API caching; fallback enabled if unavailable)

---

### Method 1: One-Click Quick Launch (Windows)

If you are developing locally on Windows, launch the complete AlgoLens stack with a single command:

1. **Setup backend environment**:
   ```cmd
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   python -m app.seed
   cd ..
   ```

2. **Install frontend dependencies**:
   ```cmd
   cd frontend
   npm install
   cd ..
   ```

3. **Launch the development environment**:
   Double-click `start-all.bat` or run:
   ```cmd
   start-all.bat
   ```
   This opens two dedicated terminal windows:
   - **Backend API**: `http://localhost:8000` (Docs at `http://localhost:8000/docs`)
   - **Frontend App**: `http://localhost:5173`

---

### Method 2: Docker Compose (Recommended for Full Stack)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/algolens.git
   cd algolens
   ```

2. **Configure environment variables**:
   ```bash
   cp backend/.env.example backend/.env
   ```
   *Edit `backend/.env` to configure your `JWT_SECRET`, database URL, and optional `GROQ_API_KEY`.*

3. **Build the sandbox image**:
   ```bash
   docker build -t algolens-sandbox:latest ./backend/sandbox/
   ```

4. **Launch all services**:
   ```bash
   docker compose up --build
   ```

5. **Access the application**:
   - **Frontend App**: `http://localhost:3000` (or `http://localhost:5173` in dev mode)
   - **Backend API Docs**: `http://localhost:8000/docs`
   - **PostgreSQL**: `localhost:5432`

---

### Method 3: Manual Local Setup

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

# Initialize database & seed curated problems (algorithmic + SQL problems)
python -m app.seed

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
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
| `DATABASE_URL` | `sqlite:///./algolens.db` | Database URI (`sqlite:///...`, `postgresql://...`, or `mysql://...`) |
| `JWT_SECRET` | *(Required)* | Secret key for signing JWT access and refresh tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `30` | Access token lifespan in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan in days |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URI for API caching |
| `REDIS_ENABLED` | `true` | Enable/disable Redis caching (auto-fallbacks if down) |
| `CACHE_TTL_PROBLEMS` | `3600` | Problem bank cache time-to-live (seconds) |
| `CACHE_TTL_PROBLEM_DETAIL` | `3600` | Individual problem detail cache time-to-live (seconds) |
| `CACHE_TTL_FORUM_THREADS` | `300` | Forum threads list cache time-to-live (seconds) |
| `CACHE_TTL_FORUM_DETAIL` | `300` | Forum thread detail cache time-to-live (seconds) |
| `CACHE_TTL_AI_INSIGHTS` | `86400` | AI analysis cache time-to-live (seconds) |
| `CACHE_TTL_USER_HISTORY` | `60` | User history cache time-to-live (seconds) |
| `GROQ_API_KEY` | `""` | API key for Groq Cloud algorithmic evaluation & deep-dives |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Groq AI LLM model identifier |
| `SANDBOX_IMAGE_NAME` | `algolens-sandbox:latest` | Docker image tag for sandbox execution |
| `SANDBOX_MEMORY_MB` | `256` | RAM ceiling per sandboxed execution container |
| `SANDBOX_WALL_TIMEOUT_S` | `10` | Hard timeout limit for individual test code execution |
| `BENCHMARK_INPUT_SIZES` | `100,1000,10000,100000,1000000` | Input size array $n_1 \dots n_k$ |
| `BENCHMARK_REPETITIONS` | `3` | Multi-run iterations per input size for variance reduction |
| `BENCHMARK_WARMUP_RUNS` | `1` | Discarded initial executions before timing |
| `BENCHMARK_TOTAL_TIMEOUT_S` | `10.0` | Global wall-clock budget for entire benchmark run |
| `SUBMISSIONS_RATE_LIMIT_PER_MINUTE` | `5` | Submission rate limit per user |
| `SMTP_ENABLED` | `false` | Enable/disable SMTP email delivery for OTPs |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server host |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USERNAME` | `""` | SMTP authentication username / email |
| `SMTP_PASSWORD` | `""` | SMTP authentication app password |
| `SMTP_FROM_EMAIL` | `noreply@algolens.com` | Sender email address for OTPs and notifications |
| `SMTP_USE_TLS` | `true` | Use STARTTLS for secure email transmission |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000`| Allowed frontend origin URLs |

---

## 📡 API Reference

Explore the interactive OpenAPI Swagger documentation at `http://localhost:8000/docs`.

### Key Endpoints:

| Category | Method | Path | Description |
|---|---|---|---|
| **Auth** | `POST` | `/auth/send-register-otp` | Send email OTP to verify address before registration |
| | `POST` | `/auth/verify-register-otp` | Verify registration OTP code |
| | `POST` | `/auth/register` | Register new user account with verified email OTP |
| | `POST` | `/auth/login` | Authenticate & receive JWT access/refresh token pair |
| | `POST` | `/auth/refresh` | Rotate expired access token using valid refresh token |
| | `POST` | `/auth/forgot-password` | Request password reset OTP via email |
| | `POST` | `/auth/verify-otp` | Verify password reset OTP code |
| | `POST` | `/auth/reset-password` | Set new password after verifying OTP |
| | `GET` | `/auth/me` | Fetch authenticated user's profile |
| | `PATCH` | `/auth/profile` | Update username / profile display information |
| | `POST` | `/auth/change-password` | Change password with current password verification |
| **Problems** | `GET` | `/problems` | List problem bank with difficulty/search filters (Redis cached) |
| | `GET` | `/problems/{id}` | Get problem details, test cases & starter code by ID or title slug |
| | `POST` | `/problems` | Upload / create a custom problem and invalidate cache |
| **Submissions** | `POST` | `/submissions/run` | **Run Code**: Instant test case execution without full benchmark |
| | `POST` | `/submissions` | Submit code for asynchronous judging & empirical benchmarking |
| | `GET` | `/submissions/{id}` | Poll submission status, verdict, runtime, and curve data |
| | `GET` | `/users/{user_id}/history` | Paginated user submission history (Redis cached) |
| | `POST` | `/submissions/{id}/groq-insights` | Request AI-powered comparative algorithmic analysis |
| **Forum** | `GET` | `/forum/threads` | List forum threads (filter by category, search, sort by newest/popular) |
| | `GET` | `/forum/threads/{id}` | Get thread detail with nested threaded replies (Redis cached) |
| | `POST` | `/forum/threads` | Create a new discussion thread |
| | `POST` | `/forum/threads/{id}/like` | Toggle upvote/like on a discussion thread |
| | `POST` | `/forum/threads/{id}/replies` | Post a top-level reply or reply to an existing comment |
| | `GET` | `/forum/users/mentions` | Search registered users for `@username` mentions |

---

## 🧪 Testing

AlgoLens includes a comprehensive pytest test suite covering authentication, database problems, Redis caching, email delivery, forum threads, sandbox execution, timeout budgets, and complexity classification:

```bash
cd backend

# Run entire test suite
pytest

# Run tests with verbose output and summary
pytest -v --tb=short

# Run specific functional test modules
pytest tests/test_benchmark_timeout.py
pytest tests/test_complexity_classifier.py
pytest tests/test_submission_pipeline_integration.py
pytest tests/test_database_problems.py
pytest tests/test_cache.py
pytest tests/test_email.py
pytest tests/test_forum.py
pytest tests/test_groq_service.py
pytest tests/test_sandbox_robustness.py
pytest tests/test_multi_sandbox.py
pytest tests/test_correctness_comparators.py
pytest tests/test_validation.py
pytest tests/test_auth_passwords.py
```

---

## 🔒 Security & Sandboxing

AlgoLens executes arbitrary, user-submitted code in an untrusted execution environment. The isolation layer enforces:

1. **Multi-Language Sandbox Support**:
   - Dedicated compilation and execution pipelines for Java, Python, C++, C, JavaScript, and SQL/MySQL.
2. **Ephemeral Containers**:
   - A clean container is spawned and torn down for each execution; state is never retained across runs.
3. **Network Isolation**:
   - Networking is strictly disabled (`network_mode="none"`), preventing outbound socket connections, SSRF, or data exfiltration.
4. **Resource Quotas**:
   - Memory strictly capped at `256MB` via Docker memory cgroups.
   - CPU quota limited via cgroup CFS scheduler (`cpu_quota=50000`, `cpu_period=100000` = 50% single-core cap).
   - Process limit (`pids_limit=64`) prevents fork bombs and rogue thread spawning.
5. **Execution Budget & Timeouts**:
   - Individual test case executions capped by `SANDBOX_WALL_TIMEOUT_S`.
   - Comprehensive benchmark suites constrained by global wall-clock budgets (`BENCHMARK_TOTAL_TIMEOUT_S`).
6. **Filesystem & Database Constraints**:
   - Read-only root filesystems and restricted temporary directories.
   - SQL queries execute inside ephemeral in-memory SQLite instances with transaction isolation, preventing host filesystem tampering.
7. **Input Sanitization & Static Checks**:
   - Source code size is capped at 64 KB and inspected before compilation to prevent compiler exhaustion attacks.

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

Built as a final-year MCA Capstone Project.
Distributed under the MIT License.
