-- =====================================================================
-- AlgoLens Database Schema DDL
-- Compatible with PostgreSQL, MySQL, SQLite, and ER diagram tools
-- (e.g., dbdiagram.io, DBeaver, draw.io, MySQL Workbench, pgAdmin)
-- =====================================================================

-- Drop tables if they already exist (in reverse dependency order)
DROP TABLE IF EXISTS forum_likes;
DROP TABLE IF EXISTS forum_replies;
DROP TABLE IF EXISTS forum_threads;
DROP TABLE IF EXISTS benchmark_runs;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS inefficiency_signatures;
DROP TABLE IF EXISTS test_cases;
DROP TABLE IF EXISTS problems;
DROP TABLE IF EXISTS users;

-- =====================================================================
-- 1. USERS TABLE
-- Stores student and learner account credentials and metadata.
-- =====================================================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- =====================================================================
-- 2. PROBLEMS TABLE
-- Stores problem definitions, complexity targets, and generator keys.
-- =====================================================================
CREATE TABLE problems (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL, -- 'easy' | 'medium' | 'hard'
    optimal_time_complexity VARCHAR(30) NOT NULL, -- e.g. 'O(n)', 'O(n log n)'
    optimal_space_complexity VARCHAR(30) NOT NULL, -- e.g. 'O(1)', 'O(n)'
    optimal_solution TEXT, -- Canonical optimal reference code
    generator_key VARCHAR(80) NOT NULL -- Key into Python input generator registry
);

-- =====================================================================
-- 3. TEST_CASES TABLE
-- Stores correctness test suites for each problem.
-- =====================================================================
CREATE TABLE test_cases (
    id VARCHAR(36) PRIMARY KEY,
    problem_id VARCHAR(36) NOT NULL,
    input TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    comparator_type VARCHAR(30) NOT NULL DEFAULT 'exact', -- 'exact' | 'numeric_tolerance' | 'sorted' | 'custom'
    CONSTRAINT fk_test_cases_problem
        FOREIGN KEY (problem_id) REFERENCES problems(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_test_cases_problem_id ON test_cases(problem_id);

-- =====================================================================
-- 4. INEFFICIENCY_SIGNATURES TABLE
-- Known algorithmic anti-patterns and guided hints per problem.
-- =====================================================================
CREATE TABLE inefficiency_signatures (
    id VARCHAR(36) PRIMARY KEY,
    problem_id VARCHAR(36) NOT NULL,
    pattern_type VARCHAR(60) NOT NULL, -- e.g. 'nested_loop_lookup', 'unmemoized_recursion'
    hint_text TEXT NOT NULL,
    CONSTRAINT fk_inefficiency_signatures_problem
        FOREIGN KEY (problem_id) REFERENCES problems(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_inefficiency_signatures_problem_id ON inefficiency_signatures(problem_id);

-- =====================================================================
-- 5. SUBMISSIONS TABLE
-- Tracks code submissions, statuses, empirical complexity, and hints.
-- =====================================================================
CREATE TABLE submissions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    problem_id VARCHAR(36) NOT NULL,
    source_code TEXT NOT NULL,
    language VARCHAR(20) NOT NULL DEFAULT 'java',
    status VARCHAR(30) NOT NULL DEFAULT 'pending', -- 'pending' | 'running_correctness' | 'failed' | 'benchmarking' | 'complete'
    empirical_complexity VARCHAR(30), -- e.g. 'O(n^2)', 'O(n)'
    confidence_score DOUBLE PRECISION, -- Regression R^2 goodness of fit (0.0 to 1.0)
    structural_hint TEXT, -- Hint populated when complexity gap is detected
    failure_detail TEXT, -- Compiler error output or failing test case details
    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_submissions_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_submissions_problem
        FOREIGN KEY (problem_id) REFERENCES problems(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_submissions_user_id ON submissions(user_id);
CREATE INDEX idx_submissions_problem_id ON submissions(problem_id);
CREATE INDEX idx_submissions_status ON submissions(status);

-- =====================================================================
-- 6. BENCHMARK_RUNS TABLE
-- Stores runtime measurements across scaled input sizes (N).
-- =====================================================================
CREATE TABLE benchmark_runs (
    id VARCHAR(36) PRIMARY KEY,
    submission_id VARCHAR(36) NOT NULL,
    input_size INTEGER NOT NULL,
    runtime_ms DOUBLE PRECISION NOT NULL,
    timed_out BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_benchmark_runs_submission
        FOREIGN KEY (submission_id) REFERENCES submissions(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_benchmark_runs_submission_id ON benchmark_runs(submission_id);

-- =====================================================================
-- 7. FORUM_THREADS TABLE
-- Community discussion threads grouped by category.
-- =====================================================================
CREATE TABLE forum_threads (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL, -- e.g. 'General', 'Algorithms', 'Optimization'
    content TEXT NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_forum_threads_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_forum_threads_category ON forum_threads(category);
CREATE INDEX idx_forum_threads_user_id ON forum_threads(user_id);

-- =====================================================================
-- 8. FORUM_REPLIES TABLE
-- Replies posted under forum threads.
-- =====================================================================
CREATE TABLE forum_replies (
    id VARCHAR(36) PRIMARY KEY,
    thread_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_forum_replies_thread
        FOREIGN KEY (thread_id) REFERENCES forum_threads(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_forum_replies_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_forum_replies_thread_id ON forum_replies(thread_id);
CREATE INDEX idx_forum_replies_user_id ON forum_replies(user_id);

-- =====================================================================
-- 9. FORUM_LIKES TABLE
-- Upvotes / likes on forum threads with uniqueness constraint per user.
-- =====================================================================
CREATE TABLE forum_likes (
    id VARCHAR(36) PRIMARY KEY,
    thread_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_thread_user_like UNIQUE (thread_id, user_id),
    CONSTRAINT fk_forum_likes_thread
        FOREIGN KEY (thread_id) REFERENCES forum_threads(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_forum_likes_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_forum_likes_thread_id ON forum_likes(thread_id);
CREATE INDEX idx_forum_likes_user_id ON forum_likes(user_id);
