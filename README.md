# KnowIT — Production-Inspired RAG Application

KnowIT is a full-stack Retrieval-Augmented Generation (RAG) application built with **FastAPI**, **React**, **PostgreSQL (PGVector)**, and **uv**.

---

## Architecture Overview

* **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, TanStack Query, React Hook Form, Zod
* **Backend**: FastAPI, Async SQLAlchemy, Alembic, `uv` Package & Environment Manager
* **Database**: PostgreSQL 17 + PGVector extension
* **Storage**: AWS S3 Object Storage
* **AI Providers**: Groq LLM API (`llama-3.3-70b-versatile`), Swappable Embedding Provider Abstraction
* **Observability**: Structured `structlog` JSON logs, Promtail, Loki, Grafana dashboard
* **Deployment**: Multi-stage Docker builds, Docker Compose, Traefik Reverse Proxy, GitHub Actions CI/CD

---

## Quick Start with Docker Compose

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Start the full application stack (PostgreSQL + PGVector, Backend, Frontend, Traefik, Loki, Promtail, Grafana):
   ```bash
   docker compose up --build -d
   ```

3. Access the application:
   * **Frontend Application**: `http://localhost` (or `http://localhost:5173`)
   * **Backend API Documentation**: `http://localhost/api/v1/docs` (or `http://localhost:8000/docs`)
   * **Grafana Dashboard**: `http://localhost:3000` (Admin / admin)
   * **Traefik Dashboard**: `http://localhost:8080`

---

## Local Development Setup

### Backend

```bash
cd backend
uv venv
uv sync
uv run uvicorn app.main:app --reload
```

### Run Tests

```bash
cd backend
uv run pytest -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## License

MIT License.
