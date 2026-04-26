{%- if cookiecutter.use_slack or cookiecutter.use_telegram %}
"""Background task handlers for channel event processing."""

import logging
from typing import Any

from app.channels.router import ChannelMessageRouter
{%- if cookiecutter.use_postgresql %}
from app.db.session import get_db_context
{%- elif cookiecutter.use_sqlite %}
from contextlib import contextmanager
from app.db.session import get_db_session
{%- endif %}

logger = logging.getLogger(__name__)


async def process_channel_event(incoming: Any) -> None:
    """Process a channel message event in the background."""
    channel_router = ChannelMessageRouter()
    try:
{%- if cookiecutter.use_postgresql %}
        async with get_db_context() as db:
            await channel_router.route(incoming, db)
{%- elif cookiecutter.use_sqlite %}
        with contextmanager(get_db_session)() as db:
            await channel_router.route(incoming, db)
{%- elif cookiecutter.use_mongodb %}
        await channel_router.route(incoming, None)
{%- endif %}
    except Exception:
        logger.exception("Error processing channel event")
{%- else %}
"""Channel tasks — no channels configured."""
{%- endif %}
