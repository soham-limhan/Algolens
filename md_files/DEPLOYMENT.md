# AlgoLens — Deployment

## 1. Target Environment

**Environment update**: Docker and root/sudo access are now confirmed available on the college deployment server. This significantly simplifies deployment compared to the original SSH-only, non-root plan — the tiered nohup/cron/systemd approach below is retained as a documented fallback (Section 5) in case Docker access is ever revoked, but the primary deployment path is now **Docker Compose**.

## 2. Primary Deployment Path — Docker Compose

```
docker-compose.yml
├── api           # FastAPI backend
├── db            # PostgreSQL
├── sandbox-base  # pre-built JDK 21 image, built once, reused per submission (not a long-running service)
└── frontend      # React app (served via a lightweight web server, e.g. nginx or a Node static server)
```

### Setup

```bash
git clone <repo> && cd algolens
cp backend/.env.example backend/.env   # fill in real JWT_SECRET, DATABASE_URL pointing at the db service
docker compose build
docker compose up -d
docker compose exec api python -m app.seed
```

### Day-to-day operations

```bash
docker compose ps                   # status
docker compose logs -f api          # tail backend logs
docker compose restart api          # restart just the backend
docker compose down                 # stop everything
docker compose up -d --build        # rebuild and redeploy after a code change
```

### Why this is simpler than the original plan

- **No manual process supervision needed** — `restart: unless-stopped` (or `on-failure`) in `docker-compose.yml` replaces the nohup/cron/systemd tiering that was necessary specifically because process supervision wasn't guaranteed to be available.
- **PostgreSQL is now trivially available** as a Compose service — no longer constrained to "SQLite unless Postgres can somehow be installed without sudo" (see `DATABASE.md`, updated accordingly).
- **The sandbox itself now uses Docker containers** (see `SECURITY.md`) — the deployment host having Docker and the sandbox execution mechanism both using Docker is the same underlying capability, just applied in two places.
- **Reverse proxy** can now be added as another Compose service (e.g. `nginx` or `caddy`) fronting both `api` and `frontend`, rather than deployment needing to work either with or without one existing already.

## 3. Configuration

Same environment variables as before (see `backend/.env.example`), now supplied via `docker-compose.yml`'s `environment:` block or an `.env` file Compose reads automatically:

```bash
DATABASE_URL=postgresql://algolens:CHANGE_ME@db:5432/algolens   # 'db' = the Compose service name, not localhost
JWT_SECRET=<long random string — never commit the real value>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BENCHMARK_INPUT_SIZES=100,1000,10000,100000,1000000
BENCHMARK_REPETITIONS=3
CORS_ORIGINS=https://your-deployed-frontend-url
```

Sandbox-specific resource-limit env vars (`SANDBOX_CPU_SECONDS`, `SANDBOX_MEMORY_MB`, etc.) now map to Docker container resource limits (`cpu_quota`, `mem_limit`) rather than `resource.setrlimit` values — see `SECURITY.md` for the updated sandbox mechanism.

## 4. Logging in Production

```bash
docker compose logs -f api
```

Rotating file logging inside the container (see original design) is still worth keeping in addition to `docker logs`, so log history survives a container restart/recreation rather than only living in the container's ephemeral log buffer — mount a volume for `logs/` if persistence across `docker compose down`/`up` cycles matters.

## 5. Fallback — Non-Docker Deployment (retained for reference)

If Docker access is ever revoked on the college server, the system can fall back to the original SSH-only deployment plan: a `scripts/probe_server.sh` diagnostic step, followed by one of three tiers (raw `nohup` + PID file, crontab watchdog, or `systemd --user`), all running the same `uvicorn app.main:app` command directly against SQLite. These scripts remain in `scripts/deploy/` and are still functional — they simply aren't the primary path anymore. See git history / earlier version of this file for the full walkthrough if this fallback is ever needed.

## 4. Configuration

All environment-driven via `.env` (see `backend/.env.example`):

```bash
DATABASE_URL=sqlite:///./algolens.db     # or postgresql://... if Postgres becomes available
JWT_SECRET=<long random string — never commit the real value>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
SANDBOX_CPU_SECONDS=5
SANDBOX_MEMORY_MB=256
SANDBOX_WALL_TIMEOUT_S=8
BENCHMARK_INPUT_SIZES=100,1000,10000,100000,1000000
BENCHMARK_REPETITIONS=3
CORS_ORIGINS=https://your-deployed-frontend-url
HOST=0.0.0.0
PORT=8000                                 # assigned by whoever manages the college server
```

`uvicorn --proxy-headers` is supported (env/flag toggle) so the app trusts `X-Forwarded-For`/`X-Forwarded-Proto` correctly **if** it ends up behind a reverse proxy later, without breaking anything if it's exposed directly on a raw port in the meantime.

## 6. Database on the College Server

PostgreSQL now runs as a Docker Compose service (`db`) — no longer constrained to SQLite. `DATABASE_URL` points at the Compose service name (`db`), not `localhost`, since containers on the same Compose network resolve each other by service name.

## 7. What's Still Not Part of This Phase

- No Jenkins/CI pipeline yet — this document covers Docker Compose deployment only; Jenkins integration (which can now build and push images, or trigger `docker compose up -d --build` on the server) is a separate, later phase (see `TASKS.md`).
- No orchestration beyond Compose (e.g. Kubernetes) — unnecessary at this project's scale.

## 8. First Real Deployment Checklist

- [ ] Confirm Docker and Docker Compose versions on the college server (`docker --version`, `docker compose version`).
- [ ] Set up `.env` with real `JWT_SECRET` (never reuse the dev value) and real `DATABASE_URL` pointing at the `db` Compose service.
- [ ] `docker compose build && docker compose up -d`.
- [ ] `docker compose exec api python -m app.seed` once, against the real deployment database.
- [ ] Run the manual smoke test from `TESTING.md` Section 7 against the live deployed URL, not just localhost.
- [ ] Re-run `tests/test_sandbox_robustness.py` against the Docker-based sandbox on the actual server — confirm the container-based isolation produces the same expected-failure-mode results the original design was tested against (see `SECURITY.md`).
- [ ] Confirm the pre-built JDK sandbox base image is actually being reused across submissions, not rebuilt per run (check submission latency, especially during the 6–8-run benchmarking stage).
