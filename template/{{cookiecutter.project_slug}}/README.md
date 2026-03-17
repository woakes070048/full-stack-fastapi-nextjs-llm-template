# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

Generated with [Full-Stack AI Agent Template](https://github.com/vstorm-co/full-stack-ai-agent-template).

## Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI + Pydantic v2 |
{%- if cookiecutter.use_postgresql %}
| **Database** | PostgreSQL (async) |
{%- elif cookiecutter.use_mongodb %}
| **Database** | MongoDB (async) |
{%- elif cookiecutter.use_sqlite %}
| **Database** | SQLite |
{%- endif %}
{%- if cookiecutter.use_jwt %}
| **Auth** | JWT + refresh tokens |
{%- endif %}
{%- if cookiecutter.enable_redis %}
| **Cache** | Redis |
{%- endif %}
{%- if cookiecutter.enable_ai_agent %}
| **AI Framework** | {{ cookiecutter.ai_framework }} ({{ cookiecutter.llm_provider }}) |
{%- endif %}
{%- if cookiecutter.enable_rag %}
| **RAG** | {{ cookiecutter.vector_store }} vector store |
{%- endif %}
{%- if cookiecutter.background_tasks != "none" %}
| **Tasks** | {{ cookiecutter.background_tasks }} |
{%- endif %}
{%- if cookiecutter.use_frontend %}
| **Frontend** | Next.js 15 + React 19 + Tailwind v4 |
{%- endif %}

## Quick Start

```bash
# Install dependencies
make install

{%- if cookiecutter.enable_docker %}
# One-command setup (Docker required)
make quickstart
{%- else %}
# Start the server
make run
{%- endif %}
```

{%- if cookiecutter.enable_docker %}
This will:
1. Install Python dependencies
2. Start all Docker services (database, Redis, vector store, etc.)
{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}
3. Run database migrations
{%- endif %}
{%- if cookiecutter.use_jwt %}
4. Create an admin user (`admin@example.com` / `admin123`)
{%- endif %}
{%- endif %}

**Access:**
- API: http://localhost:{{ cookiecutter.backend_port }}
- Docs: http://localhost:{{ cookiecutter.backend_port }}/docs
{%- if cookiecutter.use_jwt %}
- Admin: http://localhost:{{ cookiecutter.backend_port }}/admin
{%- endif %}
{%- if cookiecutter.use_frontend %}
- Frontend: http://localhost:{{ cookiecutter.frontend_port }} (run `cd frontend && bun dev`)
{%- endif %}

## Manual Setup

If you prefer to set up step by step:

```bash
# 1. Install dependencies
make install

{%- if cookiecutter.use_postgresql and cookiecutter.enable_docker %}
# 2. Start database
make docker-db
{%- endif %}

{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}
# 3. Create and apply migrations
make db-migrate    # Enter: "Initial migration"
make db-upgrade
{%- endif %}

{%- if cookiecutter.use_jwt %}
# 4. Create admin user
make create-admin
{%- endif %}

# 5. Start backend
make run

{%- if cookiecutter.use_frontend %}
# 6. Start frontend (new terminal)
cd frontend && bun install && bun dev
{%- endif %}
```

## Commands

Run `make help` for all available commands. Key ones:

| Command | Description |
|---------|-------------|
| `make run` | Start dev server with hot reload |
| `make test` | Run tests |
| `make lint` | Check code quality |
| `make format` | Auto-format code |
{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}
| `make db-migrate` | Create new migration |
| `make db-upgrade` | Apply migrations |
{%- endif %}
{%- if cookiecutter.use_jwt %}
| `make create-admin` | Create admin user |
{%- endif %}
{%- if cookiecutter.enable_docker %}
| `make quickstart` | Full setup (install + docker + db + admin) |
| `make docker-up` | Start all Docker services |
| `make docker-down` | Stop all services |
{%- endif %}

{%- if cookiecutter.enable_ai_agent %}

## AI Agent

Using **{{ cookiecutter.ai_framework }}** with **{{ cookiecutter.llm_provider }}** provider.

{%- if cookiecutter.use_frontend %}
Chat with the agent at http://localhost:{{ cookiecutter.frontend_port }}/chat
{%- endif %}

### Customize

- **System prompt:** `app/agents/prompts.py`
- **Add tools:** See `docs/howto/add-agent-tool.md`
- **Agent config:** `.env` → `AI_MODEL`, `AI_TEMPERATURE`
{%- endif %}

{%- if cookiecutter.enable_rag %}

## RAG (Knowledge Base)

Using **{{ cookiecutter.vector_store }}** as vector store.

### Ingest documents

```bash
# Local files
uv run {{ cookiecutter.project_slug }} rag-ingest /path/to/docs/ --collection documents --recursive

{%- if cookiecutter.enable_google_drive_ingestion %}
# Google Drive
uv run {{ cookiecutter.project_slug }} rag-sync-gdrive --collection documents --folder-id <id>
{%- endif %}
{%- if cookiecutter.enable_s3_ingestion %}
# S3/MinIO
uv run {{ cookiecutter.project_slug }} rag-sync-s3 --collection documents --prefix docs/
{%- endif %}
```

### Search

```bash
uv run {{ cookiecutter.project_slug }} rag-search "your query" --collection documents
```

### Manage collections

```bash
uv run {{ cookiecutter.project_slug }} rag-collections   # List all
uv run {{ cookiecutter.project_slug }} rag-stats          # Show stats
uv run {{ cookiecutter.project_slug }} rag-drop <name>    # Delete collection
```
{%- endif %}

## Project Structure

```
backend/app/
├── api/routes/v1/        # API endpoints
├── core/config.py        # Settings (from .env)
├── services/             # Business logic
├── repositories/         # Data access
├── schemas/              # Pydantic models
{%- if cookiecutter.use_database %}
├── db/models/            # Database models
{%- endif %}
{%- if cookiecutter.enable_ai_agent %}
├── agents/               # AI agents & tools
{%- endif %}
{%- if cookiecutter.enable_rag %}
├── rag/                  # RAG pipeline (embeddings, vector store, ingestion)
{%- endif %}
├── commands/             # CLI commands (auto-discovered)
{%- if cookiecutter.background_tasks != "none" %}
└── worker/               # Background tasks
{%- else %}
└── ...
{%- endif %}
```

## Guides

| Guide | Description |
|-------|-------------|
| `docs/howto/add-api-endpoint.md` | Add a new API endpoint |
{%- if cookiecutter.enable_ai_agent %}
| `docs/howto/add-agent-tool.md` | Create a new agent tool |
| `docs/howto/customize-agent-prompt.md` | Customize agent behavior |
{%- endif %}
| `docs/howto/add-data-pipeline.md` | Build a data pipeline |
| `docs/howto/add-background-task.md` | Add background tasks |
{%- if cookiecutter.enable_rag %}
| `docs/howto/add-rag-source.md` | Add a new document source |
{%- endif %}

## Environment Variables

All config is in `backend/.env`. Key variables:

```bash
{%- if cookiecutter.use_postgresql %}
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=postgres
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
{%- if cookiecutter.enable_rag %}
RAG_CHUNKING_STRATEGY=recursive  # recursive, markdown, fixed
RAG_HYBRID_SEARCH=false
{%- endif %}
```

See `backend/.env.example` for all available variables.

{%- if cookiecutter.use_frontend %}

## Deployment

### Frontend (Vercel)

```bash
cd frontend
npx vercel --prod
```

Set environment variables in Vercel dashboard:
- `BACKEND_URL` = your backend URL
- `BACKEND_WS_URL` = your backend WebSocket URL
{%- if cookiecutter.use_jwt %}
- `NEXT_PUBLIC_AUTH_ENABLED` = `true`
{%- endif %}
{%- if cookiecutter.enable_rag %}
- `NEXT_PUBLIC_RAG_ENABLED` = `true`
{%- endif %}

### Backend (Docker)

```bash
make docker-prod
```
{%- endif %}

---

*Generated with [Full-Stack AI Agent Template](https://github.com/vstorm-co/full-stack-ai-agent-template) v{{ cookiecutter.generator_version }}*
