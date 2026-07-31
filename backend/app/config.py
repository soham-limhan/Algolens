"""
app/config.py — Environment-driven settings for AlgoLens.

All configuration lives here, sourced from environment variables (or a .env file).
Nothing else in the codebase reads os.environ directly.
"""
from __future__ import annotations

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./algolens.db"

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── Sandbox (Docker container limits) ────────────────────────────────────
    sandbox_image_name: str = "algolens-sandbox:latest"
    sandbox_cpu_quota: int = 50000       # microseconds per cpu_period
    sandbox_cpu_period: int = 100000     # 100ms period → 50% of one CPU core
    sandbox_memory_mb: int = 256
    sandbox_pids_limit: int = 64
    sandbox_wall_timeout_s: int = 10

    # ── Benchmarking ──────────────────────────────────────────────────────────
    benchmark_input_sizes: str = "100,1000,10000,100000,1000000"
    benchmark_repetitions: int = 3
    benchmark_warmup_runs: int = 1

    # ── Submission constraints ────────────────────────────────────────────────
    max_source_code_bytes: int = 65536
    submissions_rate_limit_per_minute: int = 5

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: str = "logs/algolens.log"

    # ── SMTP Email ────────────────────────────────────────────────────────────
    smtp_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@algolens.com"
    smtp_use_tls: bool = True

    # ── Helpers & Validators ──────────────────────────────────────────────────
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v or not (v.startswith("sqlite") or v.startswith("postgres")):
            raise ValueError("DATABASE_URL must be a valid SQLite or PostgreSQL connection string")
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("JWT_SECRET must not be empty")
        return v

    @field_validator("benchmark_input_sizes")
    @classmethod
    def validate_benchmark_input_sizes(cls, v: str) -> str:
        try:
            sizes = [int(s.strip()) for s in v.split(",") if s.strip()]
        except ValueError:
            raise ValueError("BENCHMARK_INPUT_SIZES must be a comma-separated list of integers")
        if not sizes:
            raise ValueError("BENCHMARK_INPUT_SIZES cannot be empty")
        if any(s <= 0 for s in sizes):
            raise ValueError("BENCHMARK_INPUT_SIZES must contain positive integers")
        if sizes != sorted(sizes) or len(sizes) != len(set(sizes)):
            raise ValueError("BENCHMARK_INPUT_SIZES must be in strictly ascending order")
        return v

    @property
    def benchmark_sizes(self) -> List[int]:
        return [int(s.strip()) for s in self.benchmark_input_sizes.split(",")]

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def sandbox_memory_bytes(self) -> int:
        return self.sandbox_memory_mb * 1024 * 1024


settings = Settings()
