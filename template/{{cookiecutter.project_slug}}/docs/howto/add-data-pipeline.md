# How to: Add a Data Pipeline

## Overview

Data pipelines are background jobs that fetch, transform, and store data on a schedule. They use the existing background task system ({{ cookiecutter.background_tasks }}).

## Step-by-Step

### 1. Create the pipeline logic

```python
# app/services/pipelines/sync_products.py
import logging
import httpx

logger = logging.getLogger(__name__)


async def sync_products_from_api():
    """Fetch products from external API and update local database."""
    logger.info("Starting product sync...")

    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/products")
        products = response.json()

    # Process and store
    created, updated = 0, 0
    for product in products:
        # Your DB logic here
        # existing = await repo.get_by_external_id(product["id"])
        # if existing: updated += 1
        # else: created += 1
        pass

    logger.info(f"Product sync complete: {created} created, {updated} updated")
    return {"created": created, "updated": updated}
```

### 2. Create a background task

{%- if cookiecutter.use_celery %}
```python
# app/worker/tasks/pipelines.py
import asyncio
from app.worker.celery_app import celery_app


@celery_app.task(name="sync_products")
def sync_products_task():
    """Celery task for product sync."""
    from app.services.pipelines.sync_products import sync_products_from_api
    return asyncio.run(sync_products_from_api())
```

Schedule it in `celery_app.py`:
```python
celery_app.conf.beat_schedule["sync-products"] = {
    "task": "sync_products",
    "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
}
```
{%- elif cookiecutter.use_taskiq %}
```python
# app/worker/tasks/pipelines.py
from app.worker.taskiq_app import broker


@broker.task
async def sync_products_task():
    """Taskiq task for product sync."""
    from app.services.pipelines.sync_products import sync_products_from_api
    return await sync_products_from_api()
```

Schedule it in `tasks/schedules.py`:
```python
SCHEDULES.append({
    "task": "app.worker.tasks.pipelines:sync_products_task",
    "cron": "0 2 * * *",  # Daily at 2 AM
})
```
{%- elif cookiecutter.use_arq %}
```python
# In app/worker/arq_app.py, add to functions list:
async def sync_products_task(ctx):
    """ARQ task for product sync."""
    from app.services.pipelines.sync_products import sync_products_from_api
    return await sync_products_from_api()

# Add to WorkerSettings:
class WorkerSettings:
    functions = [sync_products_task]
    cron_jobs = [cron(sync_products_task, hour=2, minute=0)]
```
{%- endif %}

### 3. Add a CLI command for manual runs

```python
# app/commands/pipeline.py
import asyncio
import click
from app.commands import command, success, error, info


@command("run-pipeline", help="Run a data pipeline manually")
@click.argument("pipeline_name")
def run_pipeline(pipeline_name: str):
    """Run a data pipeline by name."""
    pipelines = {
        "sync-products": "app.services.pipelines.sync_products:sync_products_from_api",
    }

    if pipeline_name not in pipelines:
        error(f"Unknown pipeline: {pipeline_name}")
        error(f"Available: {', '.join(pipelines.keys())}")
        return

    info(f"Running pipeline: {pipeline_name}")
    module_path, func_name = pipelines[pipeline_name].rsplit(":", 1)
    import importlib
    module = importlib.import_module(module_path)
    func = getattr(module, func_name)
    result = asyncio.run(func())
    success(f"Pipeline complete: {result}")
```

### 4. Run it

```bash
# Manual run via CLI
uv run {{ cookiecutter.project_slug }} cmd run-pipeline sync-products

# Or let the scheduler handle it automatically
{%- if cookiecutter.use_celery %}
make celery-worker   # In one terminal
make celery-beat     # In another terminal
{%- elif cookiecutter.use_taskiq %}
make taskiq-worker
make taskiq-scheduler
{%- endif %}
```

## Tips

- Put pipeline logic in `app/services/pipelines/` — keeps it separate from API services
- Always add a CLI command for manual runs — useful for testing and one-off executions
- Use `logger.info()` for progress tracking
- Add error handling and retry logic for external API calls
- Consider idempotency — pipeline should be safe to re-run
