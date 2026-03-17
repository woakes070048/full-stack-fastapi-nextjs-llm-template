{%- if cookiecutter.enable_rag %}
# How to: Add a New RAG Document Source

## Overview

Document sources fetch files from external systems (APIs, cloud storage, etc.) for ingestion into the RAG pipeline. The existing sources are:
- **Local files** — CLI `rag-ingest` command
{%- if cookiecutter.enable_google_drive_ingestion %}
- **Google Drive** — CLI `rag-sync-gdrive`
{%- endif %}
{%- if cookiecutter.enable_s3_ingestion %}
- **S3/MinIO** — CLI `rag-sync-s3`
{%- endif %}

## Step-by-Step

### 1. Create the source class

```python
# app/rag/sources/my_source.py
import logging
from pathlib import Path

from app.rag.sources.base import BaseDocumentSource, SourceFile

logger = logging.getLogger(__name__)


class MySource(BaseDocumentSource):
    """Custom document source."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def list_files(
        self, path: str = "", extensions: list[str] | None = None
    ) -> list[SourceFile]:
        """List available files from the source."""
        # Your API call to list files
        files = []
        # ... fetch from your API ...
        return files

    async def download_file(self, file_id: str, dest_dir: Path) -> Path:
        """Download a file to a local directory."""
        # Your download logic
        dest_path = dest_dir / f"{file_id}.pdf"
        # ... download ...
        return dest_path
```

The `sync()` method is inherited from `BaseDocumentSource` — it handles:
1. `list_files()` → get all files
2. `download_file()` per file → local path
3. `ingestion_service.ingest_file()` → parse, chunk, embed, store

### 2. Add a CLI command

```python
# In app/commands/rag.py, add:
@command("rag-sync-mysource")
@click.option("--collection", "-c", default="documents")
@click.option("--path", "-p", default="")
def rag_sync_mysource(collection: str, path: str):
    """Sync documents from MySource into a RAG collection."""
    from app.rag.sources.my_source import MySource

    _, vector_store, processor, _, ingestion = get_rag_services()
    source = MySource(api_key="your-key")

    async def _sync():
        result = await source.sync(
            collection_name=collection,
            ingestion_service=ingestion,
            path=path,
        )
        success(f"Synced {result.ingested}/{result.total_files} files")
        if result.failed:
            for err in result.errors:
                warning(f"  {err}")

    asyncio.run(_sync())
```

### 3. Use it

```bash
uv run {{ cookiecutter.project_slug }} cmd rag-sync-mysource --collection docs --path "folder-id"
```

## Tips

- Set `source_file.path` to a unique URI (e.g., `mysource://file_id`) for deduplication
- The `sync()` method automatically handles replace/dedup via `IngestionService`
- Add settings to `app/core/config.py` for API keys/credentials
{%- endif %}
