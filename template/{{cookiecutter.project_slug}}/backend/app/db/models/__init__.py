"""Database models."""
{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}
# ruff: noqa: I001, RUF022 - Imports structured for Jinja2 template conditionals
{%- endif %}
{%- if cookiecutter.use_postgresql or cookiecutter.use_sqlite %}
{%- set models = [] %}
{%- if cookiecutter.use_jwt %}
{%- set _ = models.append("User") %}
from app.db.models.user import User
{%- endif %}
{%- if cookiecutter.enable_session_management and cookiecutter.use_jwt %}
{%- set _ = models.append("Session") %}
from app.db.models.session import Session
{%- endif %}
{%- set _ = models.extend(["Conversation", "Message", "ToolCall"]) %}
from app.db.models.conversation import Conversation, Message, ToolCall
{%- if cookiecutter.enable_webhooks %}
{%- set _ = models.extend(["Webhook", "WebhookDelivery"]) %}
from app.db.models.webhook import Webhook, WebhookDelivery
{%- endif %}
{%- set _ = models.append("ChatFile") %}
from app.db.models.chat_file import ChatFile
{%- set _ = models.append("MessageRating") %}
from app.db.models.message_rating import MessageRating
{%- if cookiecutter.enable_rag %}
{%- set _ = models.append("RAGDocument") %}
from app.db.models.rag_document import RAGDocument
{%- set _ = models.append("SyncLog") %}
from app.db.models.sync_log import SyncLog
{%- set _ = models.append("SyncSource") %}
from app.db.models.sync_source import SyncSource
{%- endif %}
{%- if models %}

__all__ = {{ models }}
{%- endif %}
{%- endif %}
