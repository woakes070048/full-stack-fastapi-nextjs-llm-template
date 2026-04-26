{%- if cookiecutter.enable_rag and (cookiecutter.use_postgresql or cookiecutter.use_sqlite) %}
{%- if cookiecutter.use_postgresql %}
"""Sync source service (PostgreSQL async).

Contains business logic for managing RAG sync source configurations
and triggering sync operations.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models.sync_log import SyncLog
from app.db.models.sync_source import SyncSource
from app.rag.connectors import CONNECTOR_REGISTRY
from app.repositories import sync_log as sync_log_repo
from app.repositories import sync_source as sync_source_repo
from app.schemas.sync_source import SyncSourceCreate, SyncSourceUpdate


class SyncSourceService:
    """Service for managing sync source configurations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_sources(
        self,
        is_active: bool | None = None,
    ) -> list[SyncSource]:
        """List all sync sources, optionally filtered by active status."""
        return await sync_source_repo.get_all(self.db, is_active=is_active)

    async def get_source(self, source_id: str) -> SyncSource:
        """Get a sync source by ID.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        source = await sync_source_repo.get_by_id(self.db, UUID(source_id))
        if not source:
            raise NotFoundError(
                message="Sync source not found",
                details={"source_id": source_id},
            )
        return source

    async def create_source(self, data: SyncSourceCreate) -> SyncSource:
        """Create a new sync source.

        Validates the connector type and its configuration before creating.

        Raises:
            ValueError: If connector type is unknown or config is invalid.
        """
        if data.connector_type not in CONNECTOR_REGISTRY:
            raise ValueError(f"Unknown connector type: {data.connector_type}")

        connector_cls = CONNECTOR_REGISTRY[data.connector_type]
        connector = connector_cls()
        is_valid, error = await connector.validate_config(data.config)
        if not is_valid:
            raise ValueError(f"Invalid config: {error}")

        return await sync_source_repo.create(
            self.db,
            name=data.name,
            connector_type=data.connector_type,
            collection_name=data.collection_name,
            config=data.config,
            sync_mode=data.sync_mode,
            schedule_minutes=data.schedule_minutes,
        )

    async def update_source(
        self, source_id: str, data: SyncSourceUpdate
    ) -> SyncSource:
        """Update an existing sync source.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        await self.get_source(source_id)  # verify exists
        updates = data.model_dump(exclude_unset=True)
        source = await sync_source_repo.update(
            self.db, UUID(source_id), **updates
        )
        if source is None:
            raise NotFoundError(message="Sync source not found", details={"source_id": source_id})
        return source

    async def delete_source(self, source_id: str) -> None:
        """Delete a sync source.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        await self.get_source(source_id)  # verify exists
        await sync_source_repo.delete(self.db, UUID(source_id))

    async def trigger_sync(self, source_id: str) -> SyncLog:
        """Trigger a manual sync for a source. Returns the created SyncLog.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        source = await self.get_source(source_id)

        return await sync_log_repo.create(
            self.db,
            source=source.connector_type,
            collection_name=source.collection_name,
            mode=source.sync_mode,
            sync_source_id=source.id,
        )

    async def update_after_sync(
        self,
        source_id: str,
        status: str,
        error: str | None = None,
    ) -> None:
        """Update sync source status after a sync operation completes."""
        await sync_source_repo.update_sync_status(
            self.db,
            UUID(source_id),
            last_sync_at=datetime.now(UTC),
            last_sync_status=status,
            last_error=error,
        )


{%- elif cookiecutter.use_sqlite %}
"""Sync source service (SQLite sync).

Contains business logic for managing RAG sync source configurations
and triggering sync operations.
"""

import asyncio
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.sync_log import SyncLog
from app.db.models.sync_source import SyncSource
from app.rag.connectors import CONNECTOR_REGISTRY
from app.repositories import sync_log as sync_log_repo
from app.repositories import sync_source as sync_source_repo
from app.schemas.sync_source import SyncSourceCreate, SyncSourceUpdate


class SyncSourceService:
    """Service for managing sync source configurations."""

    def __init__(self, db: Session):
        self.db = db

    def list_sources(
        self,
        is_active: bool | None = None,
    ) -> list[SyncSource]:
        """List all sync sources, optionally filtered by active status."""
        return sync_source_repo.get_all(self.db, is_active=is_active)

    def get_source(self, source_id: str) -> SyncSource:
        """Get a sync source by ID.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        source = sync_source_repo.get_by_id(self.db, source_id)
        if not source:
            raise NotFoundError(
                message="Sync source not found",
                details={"source_id": source_id},
            )
        return source

    def create_source(self, data: SyncSourceCreate) -> SyncSource:
        """Create a new sync source.

        Validates the connector type and its configuration before creating.

        Raises:
            ValueError: If connector type is unknown or config is invalid.
        """
        if data.connector_type not in CONNECTOR_REGISTRY:
            raise ValueError(f"Unknown connector type: {data.connector_type}")

        connector_cls = CONNECTOR_REGISTRY[data.connector_type]
        connector = connector_cls()

        # validate_config is async on the base class; for SQLite we run it synchronously
        loop = asyncio.new_event_loop()
        try:
            is_valid, error = loop.run_until_complete(
                connector.validate_config(data.config)
            )
        finally:
            loop.close()

        if not is_valid:
            raise ValueError(f"Invalid config: {error}")

        return sync_source_repo.create(
            self.db,
            name=data.name,
            connector_type=data.connector_type,
            collection_name=data.collection_name,
            config=data.config,
            sync_mode=data.sync_mode,
            schedule_minutes=data.schedule_minutes,
        )

    def update_source(
        self, source_id: str, data: SyncSourceUpdate
    ) -> SyncSource:
        """Update an existing sync source.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        self.get_source(source_id)  # verify exists
        updates = data.model_dump(exclude_unset=True)
        source = sync_source_repo.update(self.db, source_id, **updates)
        if source is None:
            raise NotFoundError(message="Sync source not found", details={"source_id": source_id})
        return source

    def delete_source(self, source_id: str) -> None:
        """Delete a sync source.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        self.get_source(source_id)  # verify exists
        sync_source_repo.delete(self.db, source_id)

    def trigger_sync(self, source_id: str) -> SyncLog:
        """Trigger a manual sync for a source. Returns the created SyncLog.

        Raises:
            NotFoundError: If sync source does not exist.
        """
        source = self.get_source(source_id)

        return sync_log_repo.create(
            self.db,
            source=source.connector_type,
            collection_name=source.collection_name,
            mode=source.sync_mode,
            sync_source_id=source.id,
        )

    def update_after_sync(
        self,
        source_id: str,
        status: str,
        error: str | None = None,
    ) -> None:
        """Update sync source status after a sync operation completes."""
        sync_source_repo.update_sync_status(
            self.db,
            source_id,
            last_sync_at=datetime.now(UTC),
            last_sync_status=status,
            last_error=error,
        )


{%- endif %}
{%- else %}
"""Sync source service - not configured."""
{%- endif %}
