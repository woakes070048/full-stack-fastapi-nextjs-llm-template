{%- if cookiecutter.enable_rag and cookiecutter.enable_rag_image_description %}
"""LLM-based image description for RAG document processing.

Extracts text descriptions from images using vision-capable LLMs.
The descriptions are appended to page content before chunking,
making image content searchable via text embeddings.
"""

import base64
import logging
from abc import ABC, abstractmethod
from io import BytesIO

from PIL import Image

logger = logging.getLogger(__name__)

IMAGE_DESCRIPTION_PROMPT = (
    "Describe this image in detail. Focus on any text, data, charts, diagrams, "
    "or visual information that would be useful for document search and retrieval. "
    "Be concise but comprehensive."
)

MAX_IMAGE_DIMENSION = 1024


def resize_image(image_bytes: bytes, max_dim: int = MAX_IMAGE_DIMENSION) -> bytes:
    """Resize image to fit within max_dim while preserving aspect ratio."""
    img = Image.open(BytesIO(image_bytes))
    if img.width <= max_dim and img.height <= max_dim:
        return image_bytes
    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


class BaseImageDescriber(ABC):
    """Abstract base for LLM-based image description."""

    @abstractmethod
    async def describe(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        """Generate a text description of an image.

        Args:
            image_bytes: Raw image data.
            mime_type: MIME type of the image.

        Returns:
            Text description of the image content.
        """


{%- if cookiecutter.use_openai %}
class OpenAIImageDescriber(BaseImageDescriber):
    """Image description using OpenAI GPT-4o vision."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def describe(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        resized = resize_image(image_bytes)
        b64 = base64.b64encode(resized).decode("utf-8")
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": IMAGE_DESCRIPTION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI image description failed: {e}")
            return ""
{%- endif %}

{%- if cookiecutter.use_anthropic %}
class AnthropicImageDescriber(BaseImageDescriber):
    """Image description using Anthropic Claude vision."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def describe(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        resized = resize_image(image_bytes)
        b64 = base64.b64encode(resized).decode("utf-8")
        media_type = mime_type if mime_type in ("image/png", "image/jpeg", "image/gif", "image/webp") else "image/png"
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": b64,
                                },
                            },
                            {"type": "text", "text": IMAGE_DESCRIPTION_PROMPT},
                        ],
                    }
                ],
            )
            return response.content[0].text if response.content else ""
        except Exception as e:
            logger.error(f"Anthropic image description failed: {e}")
            return ""
{%- endif %}

{%- if cookiecutter.use_openrouter %}
class OpenRouterImageDescriber(BaseImageDescriber):
    """Image description using OpenRouter (OpenAI-compatible API)."""

    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        self.model = model

    async def describe(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        resized = resize_image(image_bytes)
        b64 = base64.b64encode(resized).decode("utf-8")
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": IMAGE_DESCRIPTION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=300,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenRouter image description failed: {e}")
            return ""
{%- endif %}

{%- if cookiecutter.use_google %}
class GeminiImageDescriber(BaseImageDescriber):
    """Image description using Google Gemini vision."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def describe(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        import asyncio
        from google.genai import types as genai_types
        resized = resize_image(image_bytes)
        try:
            response = await asyncio.to_thread(
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=[
                        genai_types.Part.from_bytes(data=resized, mime_type=mime_type),
                        IMAGE_DESCRIPTION_PROMPT,
                    ],
                )
            )
            return response.text or ""
        except Exception as e:
            logger.error(f"Gemini image description failed: {e}")
            return ""
{%- endif %}
{%- endif %}
