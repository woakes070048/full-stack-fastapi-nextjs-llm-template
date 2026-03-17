# CLAUDE.md

## Project Overview

**{{ cookiecutter.project_name }}** - FastAPI application generated with [Full-Stack AI Agent Template](https://github.com/vstorm-co/full-stack-ai-agent-template).

**Stack:** FastAPI + Pydantic v2
{%- if cookiecutter.use_postgresql %}, PostgreSQL (async){%- endif %}
{%- if cookiecutter.use_mongodb %}, MongoDB (async){%- endif %}
{%- if cookiecutter.use_sqlite %}, SQLite{%- endif %}
{%- if cookiecutter.use_jwt %}, JWT auth{%- endif %}
{%- if cookiecutter.enable_redis %}, Redis{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_pydantic_ai %}, PydanticAI{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_langchain %}, LangChain{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_langgraph %}, LangGraph{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_crewai %}, CrewAI{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_deepagents %}, DeepAgents{%- endif %}
{%- if cookiecutter.enable_rag %}, RAG ({{ cookiecutter.vector_store }}){%- endif %}
{%- if cookiecutter.use_celery %}, Celery{%- endif %}
{%- if cookiecutter.use_taskiq %}, Taskiq{%- endif %}
{%- if cookiecutter.use_frontend %}, Next.js 15{%- endif %}

## Commands

```bash
# Backend
cd backend
uv run uvicorn app.main:app --reload --port {{ cookiecutter.backend_port }}
pytest
ruff check . --fix && ruff format .
{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}

# Database
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "Description"
{%- endif %}
{%- if cookiecutter.use_frontend %}

# Frontend
cd frontend
bun dev
bun test
{%- endif %}
{%- if cookiecutter.enable_docker %}

# Docker
docker compose up -d
{%- endif %}
{%- if cookiecutter.enable_rag %}

# RAG
uv run {{ cookiecutter.project_slug }} rag-collections
uv run {{ cookiecutter.project_slug }} rag-ingest /path/to/file.pdf --collection docs
uv run {{ cookiecutter.project_slug }} rag-search "query" --collection docs
{%- if cookiecutter.enable_google_drive_ingestion %}
uv run {{ cookiecutter.project_slug }} rag-sync-gdrive --collection docs
{%- endif %}
{%- if cookiecutter.enable_s3_ingestion %}
uv run {{ cookiecutter.project_slug }} rag-sync-s3 --collection docs
{%- endif %}
{%- endif %}
```

## Project Structure

```
backend/app/
├── api/routes/v1/    # HTTP endpoints
├── services/         # Business logic
├── repositories/     # Data access
├── schemas/          # Pydantic models
├── db/models/        # Database models
├── core/config.py    # Settings
{%- if cookiecutter.enable_ai_agent %}
├── agents/           # AI agents
{%- endif %}
{%- if cookiecutter.enable_rag %}
├── rag/              # RAG (embeddings, vector store, ingestion)
{%- endif %}
└── commands/         # CLI commands
```

## Key Conventions

- Use `db.flush()` in repositories (not `commit`)
- Services raise domain exceptions (`NotFoundError`, `AlreadyExistsError`)
- Schemas: separate `Create`, `Update`, `Response` models
- Commands auto-discovered from `app/commands/`
{%- if cookiecutter.enable_rag %}
- Document ingestion via CLI only (not API)
{%- endif %}

## Environment Variables

Key variables in `.env`:
```bash
ENVIRONMENT=local
{%- if cookiecutter.use_postgresql %}
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=secret
{%- endif %}
{%- if cookiecutter.use_jwt %}
SECRET_KEY=change-me-use-openssl-rand-hex-32
{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_openai %}
OPENAI_API_KEY=sk-...
{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_anthropic %}
ANTHROPIC_API_KEY=sk-ant-...
{%- endif %}
{%- if cookiecutter.enable_ai_agent and cookiecutter.use_google %}
GOOGLE_API_KEY=...
{%- endif %}
{%- if cookiecutter.enable_logfire %}
LOGFIRE_TOKEN=your-token
{%- endif %}
{%- if cookiecutter.enable_langsmith %}
LANGCHAIN_API_KEY=your-api-key
{%- endif %}
{%- if cookiecutter.use_milvus %}
MILVUS_HOST=localhost
MILVUS_PORT=19530
{%- endif %}
{%- if cookiecutter.use_qdrant %}
QDRANT_HOST=localhost
QDRANT_PORT=6333
{%- endif %}
```
