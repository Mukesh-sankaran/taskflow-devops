# TaskFlow

TaskFlow is a small FastAPI todo application built for a college DevOps project. The product itself is intentionally simple so the evaluation can focus on a complete deployment pipeline.

## Project overview

Students and operators can create, edit, complete, reopen, and delete tasks through a Bootstrap UI and a JSON API. PostgreSQL stores the data. Prometheus metrics and a database-aware health check are included so later CI/CD and Kubernetes stages can observe the running service.

## Architecture

The **application** is a FastAPI service with SQLAlchemy models, Jinja2 pages, and a PostgreSQL database.

The **mandatory DevOps deployment architecture** (configured separately from this repository's app code) is:

GitHub → Jenkins CI → Ruff → pytest → Trivy → Docker Build → GHCR → GitHub Kubernetes manifests → Argo CD → Kubernetes (2 replicas) → Prometheus + Grafana.

This repository currently delivers the application, tests, lint configuration, Docker image, and Docker Compose stack. Jenkins, Kubernetes, Argo CD, and cluster monitoring manifests are out of scope here.

```text
Browser / API client
        │
        ▼
   FastAPI (port 8000)
        │
        ▼
   PostgreSQL
```

## Features

- Create, list, edit, and delete tasks
- Mark tasks completed or pending
- Dashboard counts for total, completed, and pending tasks
- JSON API for every task operation
- `/health` checks database connectivity
- `/metrics` exposes Prometheus HTTP counters and duration histograms
- Responsive Bootstrap 5 interface

Each task has `id`, `title`, `description`, `is_completed`, and `created_at`.

## Technology stack

- Python 3.11+
- FastAPI, Pydantic, Jinja2
- PostgreSQL, SQLAlchemy 2.x, psycopg3
- Bootstrap 5
- pytest, Ruff
- Docker, Docker Compose
- prometheus-client

## Installation

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

## Environment configuration

All database access is configured through environment variables. Copy `.env.example` to `.env` and adjust values as needed.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy URL (`postgresql+psycopg://user:password@host:5432/dbname`) |
| `POSTGRES_USER` | Docker Compose PostgreSQL user |
| `POSTGRES_PASSWORD` | Docker Compose PostgreSQL password |
| `POSTGRES_DB` | Docker Compose PostgreSQL database name |

Do not commit `.env`. Tests ignore this value and use an isolated in-memory SQLite database.

## Local execution

Start PostgreSQL (Docker Compose database only is enough):

```bash
docker compose up -d db
```

Then run the API from the project root, with `DATABASE_URL` pointing at localhost:

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000

## Docker execution

```bash
docker compose up --build
```

The app waits until PostgreSQL is healthy, creates tables on startup, and listens on port 8000. PostgreSQL is reachable to the app on the Compose network (not published to the host) and data is stored in the `postgres_data` volume.

Stop the stack with `docker compose down`. Add `-v` only if you intend to delete the database volume.

## API endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/tasks` | List tasks |
| `POST` | `/api/tasks` | Create a task |
| `GET` | `/api/tasks/{task_id}` | Get one task |
| `PATCH` | `/api/tasks/{task_id}` | Update title, description, or completion |
| `DELETE` | `/api/tasks/{task_id}` | Delete a task |
| `GET` | `/health` | Database health check (`200` healthy, `503` unhealthy) |
| `GET` | `/metrics` | Prometheus metrics |
| `GET` | `/` | Web UI |

Create payload:

```json
{
  "title": "Write the lab report",
  "description": "Include architecture diagram"
}
```

Partial update payload:

```json
{
  "is_completed": true
}
```

## Testing

Tests use SQLite and do not require PostgreSQL.

```bash
pytest
```

## Linting

```bash
ruff check .
```

Ruff is configured in `pyproject.toml` and is the linter expected in the Jenkins pipeline.
