# AGENTS.md

This file provides guidance for AI coding agents (Codex, Copilot, Cursor, Zed, OpenCode).

## Project Overview

**{{ cookiecutter.project_name }}** - FastAPI application generated with [Full-Stack AI Agent Template](https://github.com/vstorm-co/full-stack-ai-agent-template).

**Stack:** FastAPI + Pydantic v2
{%- if cookiecutter.use_postgresql %}, PostgreSQL{%- endif %}
{%- if cookiecutter.use_mongodb %}, MongoDB{%- endif %}
{%- if cookiecutter.use_sqlite %}, SQLite{%- endif %}
{%- if cookiecutter.use_jwt %}, JWT auth{%- endif %}
{%- if cookiecutter.enable_redis %}, Redis{%- endif %}
{%- if cookiecutter.enable_ai_agent %}, {{ cookiecutter.ai_framework }} ({{ cookiecutter.llm_provider }}){%- endif %}
{%- if cookiecutter.enable_rag %}, RAG ({{ cookiecutter.vector_store }}){%- endif %}
{%- if cookiecutter.use_frontend %}, Next.js 15{%- endif %}

## Commands

```bash
# Run server
cd backend && uv run uvicorn app.main:app --reload

# Tests & lint
pytest
ruff check . --fix && ruff format .
{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}

# Migrations
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "Description"
{%- endif %}
{%- if cookiecutter.enable_rag %}

# RAG
uv run {{ cookiecutter.project_slug }} rag-ingest /path/to/file.pdf --collection docs
uv run {{ cookiecutter.project_slug }} rag-search "query" --collection docs
{%- endif %}
```

## Project Structure

```
backend/app/
├── api/routes/v1/    # Endpoints
├── services/         # Business logic
├── repositories/     # Data access
├── schemas/          # Pydantic models
├── db/models/        # DB models
{%- if cookiecutter.enable_ai_agent %}
├── agents/           # AI agents
{%- endif %}
{%- if cookiecutter.enable_rag %}
├── rag/              # RAG (embeddings, vector store, ingestion)
{%- endif %}
└── commands/         # CLI commands
```

## Key Conventions

- `db.flush()` in repositories, not `commit()`
- Services raise `NotFoundError`, `AlreadyExistsError`
- Separate `Create`, `Update`, `Response` schemas
- Commands auto-discovered from `app/commands/`
{%- if cookiecutter.enable_rag %}
- Document ingestion via CLI commands only
{%- endif %}

## More Info

- `docs/architecture.md` - Architecture details
- `docs/adding_features.md` - How to add features
- `docs/testing.md` - Testing guide
- `docs/patterns.md` - Code patterns
