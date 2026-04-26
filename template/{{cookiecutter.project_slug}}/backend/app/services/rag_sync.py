{%- if cookiecutter.enable_rag and cookiecutter.use_postgresql %}
"""RAG sync service (PostgreSQL async).

Contains business logic for managing RAG synchronization operations
and their associated log entries.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.sync_log import SyncLog
from app.repositories import sync_log_repo


class RAGSyncService:
    """Service for RAG sync operation management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_sync_logs(
        self,
        collection_name: str | None = None,
        limit: int = 20,
    ) -> list[SyncLog]:
        """List sync operation logs, optionally filtered by collection."""
        return await sync_log_repo.get_all(self.db, collection_name=collection_name, limit=limit)

    async def get_sync_log(self, sync_id: str) -> SyncLog:
        """Get a sync log by ID.

        Raises:
            NotFoundError: If sync log does not exist.
        """
        log = await sync_log_repo.get_by_id(self.db, UUID(sync_id))
        if not log:
            raise NotFoundError(
                message="Sync log not found",
                details={"sync_id": sync_id},
            )
        return log

    async def create_sync_log(
        self,
        *,
        source: str,
        collection_name: str,
        mode: str,
    ) -> SyncLog:
        """Create a new sync log entry."""
        return await sync_log_repo.create(
            self.db,
            source=source,
            collection_name=collection_name,
            mode=mode,
        )

    async def complete_sync(
        self,
        sync_id: str,
        *,
        status: str,
        total_files: int = 0,
        ingested: int = 0,
        updated: int = 0,
        skipped: int = 0,
        failed: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Mark a sync operation as completed (done or error)."""
        log = await self.get_sync_log(sync_id)
        await sync_log_repo.update_status(
            self.db,
            log.id,
            status=status,
            total_files=total_files,
            ingested=ingested,
            updated=updated,
            skipped=skipped,
            failed=failed,
            error_message=error_message,
            completed_at=datetime.now(UTC),
        )

    async def cancel_sync(self, sync_id: str) -> SyncLog:
        """Cancel a running sync operation.

        Raises:
            NotFoundError: If sync log does not exist.
            ValueError: If sync is not in 'running' state.
        """
        log = await self.get_sync_log(sync_id)
        if log.status != "running":
            raise ValueError("Sync is not running")
        cancelled = await sync_log_repo.update_status(
            self.db,
            log.id,
            status="cancelled",
            completed_at=datetime.now(UTC),
        )
        if cancelled is None:
            raise NotFoundError(message="Sync log not found", details={"sync_id": sync_id})
        return cancelled


{%- elif cookiecutter.enable_rag and cookiecutter.use_sqlite %}
"""RAG sync service (SQLite sync).

Contains business logic for managing RAG synchronization operations
and their associated log entries.
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.sync_log import SyncLog
from app.repositories import sync_log_repo


class RAGSyncService:
    """Service for RAG sync operation management."""

    def __init__(self, db: Session):
        self.db = db

    def list_sync_logs(
        self,
        collection_name: str | None = None,
        limit: int = 20,
    ) -> list[SyncLog]:
        """List sync operation logs, optionally filtered by collection."""
        return sync_log_repo.get_all(self.db, collection_name=collection_name, limit=limit)

    def get_sync_log(self, sync_id: str) -> SyncLog:
        """Get a sync log by ID.

        Raises:
            NotFoundError: If sync log does not exist.
        """
        log = sync_log_repo.get_by_id(self.db, sync_id)
        if not log:
            raise NotFoundError(
                message="Sync log not found",
                details={"sync_id": sync_id},
            )
        return log

    def create_sync_log(
        self,
        *,
        source: str,
        collection_name: str,
        mode: str,
    ) -> SyncLog:
        """Create a new sync log entry."""
        return sync_log_repo.create(
            self.db,
            source=source,
            collection_name=collection_name,
            mode=mode,
        )

    def complete_sync(
        self,
        sync_id: str,
        *,
        status: str,
        total_files: int = 0,
        ingested: int = 0,
        updated: int = 0,
        skipped: int = 0,
        failed: int = 0,
        error_message: str | None = None,
    ) -> None:
        """Mark a sync operation as completed (done or error)."""
        log = self.get_sync_log(sync_id)
        sync_log_repo.update_status(
            self.db,
            log.id,
            status=status,
            total_files=total_files,
            ingested=ingested,
            updated=updated,
            skipped=skipped,
            failed=failed,
            error_message=error_message,
            completed_at=datetime.now(UTC),
        )

    def cancel_sync(self, sync_id: str) -> SyncLog:
        """Cancel a running sync operation.

        Raises:
            NotFoundError: If sync log does not exist.
            ValueError: If sync is not in 'running' state.
        """
        log = self.get_sync_log(sync_id)
        if log.status != "running":
            raise ValueError("Sync is not running")
        cancelled = sync_log_repo.update_status(
            self.db,
            log.id,
            status="cancelled",
            completed_at=datetime.now(UTC),
        )
        if cancelled is None:
            raise NotFoundError(message="Sync log not found", details={"sync_id": sync_id})
        return cancelled


{%- else %}
"""RAG sync service - not configured."""
{%- endif %}
