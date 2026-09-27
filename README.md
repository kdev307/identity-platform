# ISP Management System

A full-stack ISP (Internet Service Provider) management platform. The backend is a Django REST API with JWT authentication and OpenAPI docs; the frontend is a React + TypeScript app built with Vite. Local infrastructure (PostgreSQL, Redis, Mailpit) runs via Docker Compose.

## Tech Stack

| Layer          | Technology                                                        |
| -------------- | ----------------------------------------------------------------- |
| Backend        | Python 3.12+, Django 6, Django REST Framework, SimpleJWT, Celery  |
| API docs       | drf-spectacular (Swagger UI / ReDoc)                              |
| Frontend       | React 19, TypeScript, Vite                                        |
| Database       | PostgreSQL 17                                                     |
| Cache / broker | Redis 8                                                           |
| Mail (dev)     | Mailpit                                                          |
| Tooling        | uv (Python), npm (Node), Docker Compose                          |

## Prerequisites

Install these before you begin:

- [Git](https://git-scm.com/)
- [Docker](https://docs.docker.com/get-docker/) with the Docker Compose plugin (`docker compose`)
- [Node.js 22.x](https://nodejs.org/) and npm
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package/environment manager)
- `curl`

The `doctor` script expects Node.js 22.x and Python 3.12.x specifically.

## Project Structure

```
isp/
├── backend/            # Django REST API
│   ├── apps/           # Django apps (identity, health, common)
│   ├── config/         # Settings, URLs, WSGI/ASGI
│   └── pyproject.toml  # Python dependencies (managed by uv)
├── frontend/           # React + TypeScript + Vite app
├── scripts/            # Dev/setup automation (bash; run via Git Bash on Windows)
├── docker-compose.yml  # PostgreSQL, Redis, RedisInsight, Mailpit
└── .env.example        # Sample environment configuration
```

## Environment Configuration

Copy the example file and adjust values as needed:

```bash
cp .env.example .env
```

The backend reads its own `.env` from `backend/.env`. The following variables are
consumed by Django settings and are **not** in the root `.env.example`, so set them
in `backend/.env` (or export them) before running the backend:

| Variable                     | Purpose                              | Default                                   |
| ---------------------------- | ------------------------------------ | ----------------------------------------- |
| `DJANGO_SECRET_KEY`          | Django secret key                    | insecure dev default                      |
| `DATABASE_URL`               | Database connection string           | `postgresql://isp:isp@localhost:5432/isp` |
| `SWAGGER_API_CONTACT_EMAIL`  | Contact email shown in API docs      | **required, no default**                  |

> Note: `SWAGGER_API_CONTACT_EMAIL` has no default in `config/settings/base.py`, so the
> backend will fail to start until it is set.

## Quick Start

The fastest path uses the automation scripts. They are bash scripts, so run them
with bash: use your terminal on macOS/Linux, or **Git Bash** on Windows (see
[Windows](#windows-support) below).

```bash
# One-time setup: checks tooling, starts infra, installs deps, migrates DB
./scripts/setup.sh

# Start backend + frontend + infra together
./scripts/dev.sh
```

Once running:

- Backend API: http://127.0.0.1:8000
- Frontend: http://localhost:5173
- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Mailpit UI: http://localhost:8025
- RedisInsight: http://localhost:5540

## Manual Setup

If you prefer to run steps yourself instead of using the scripts:

### 1. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, RedisInsight, and Mailpit.

### 2. Backend

```bash
cd backend
uv sync                              # install dependencies
uv run python manage.py migrate      # apply migrations
uv run python manage.py runserver    # start dev server on :8000
```

Create an admin user (optional):

```bash
uv run python manage.py createsuperuser
```

### 3. Frontend

```bash
cd frontend
npm ci                # install dependencies
npm run dev           # start Vite dev server on :5173
```

## API Overview

Base path: `/api/v1/`

| Method | Endpoint                | Description                     | Auth |
| ------ | ----------------------- | ------------------------------- | ---- |
| GET    | `/api/v1/health/`       | Liveness check                  | No   |
| GET    | `/api/v1/health/ready/` | Readiness check (DB)            | No   |
| POST   | `/api/v1/auth/register/`| Register a new user             | No   |
| POST   | `/api/v1/auth/login/`   | Obtain access + refresh tokens  | No   |
| POST   | `/api/v1/auth/refresh/` | Refresh access token            | No   |
| POST   | `/api/v1/auth/logout/`  | Blacklist refresh token         | Yes  |
| GET    | `/api/v1/auth/me/`      | Current user profile            | Yes  |

Authentication uses JWT bearer tokens. Access tokens live for 15 minutes and refresh
tokens for 7 days (rotated and blacklisted on use).

Interactive docs: `/api/docs/` (Swagger) and `/api/redoc/` (ReDoc).

## Testing

Backend tests use pytest with `pytest-django`:

```bash
cd backend
uv run pytest
uv run pytest --cov          # with coverage
```

Frontend linting:

```bash
cd frontend
npm run lint
npm run build                # type-check + production build
```

## Health Check

Run the doctor script to validate your environment (tooling versions, Docker,
infrastructure services, Django config, and frontend build):

```bash
./scripts/doctor.sh
```

## Scripts Reference

| Script                        | Purpose                                                     |
| ----------------------------- | ----------------------------------------------------------- |
| `scripts/setup.sh`            | One-time environment setup (tools, infra, deps, migrations) |
| `scripts/dev.sh`              | Start infra + backend + frontend together                   |
| `scripts/backend.sh`          | Start the Django dev server only                            |
| `scripts/frontend.sh`         | Start the Vite dev server only                              |
| `scripts/infra.sh`            | Start Docker Compose infrastructure                         |
| `scripts/wait-for-services.sh`| Block until infra containers report healthy                 |
| `scripts/doctor.sh`           | Diagnose the local environment                              |

## Windows Support

The automation scripts are bash (`.sh`) and use Unix-only features (`BASH_SOURCE`,
background jobs with `&`, `trap`, `wait -n`), so they do **not** run in `cmd.exe` or
PowerShell. On Windows, run them in **Git Bash** (bundled with
[Git for Windows](https://gitforwindows.org/)), which ships a real bash and resolves
`docker`, `uv`, `npm`, and `curl` from your PATH:

```bash
# From the project root in a Git Bash terminal
./scripts/setup.sh
./scripts/dev.sh
```

### Line endings (important)

The scripts must keep **LF** line endings. Git for Windows defaults to
`core.autocrlf=true`, which would convert them to CRLF on checkout and break bash with:

```
/usr/bin/env: 'bash\r': No such file or directory
```

A committed `.gitattributes` pins `*.sh` (and other text files) to `eol=lf` to prevent
this. If you cloned before that file existed, renormalize once:

```bash
git add --renormalize .
```

### Notes for Git Bash

- Prerequisites (Docker Desktop, Node.js, uv, curl) must be installed and on PATH.
  Docker Desktop provides the `docker compose` command used by the scripts.
- `dev.sh` runs the backend and frontend as background jobs and stops them on
  `Ctrl+C` via a `trap`. This works in Git Bash. If job control ever misbehaves,
  run `./scripts/backend.sh` and `./scripts/frontend.sh` in two separate terminals.
- WSL2 is an alternative if you prefer a full Linux environment, but it is not
  required.