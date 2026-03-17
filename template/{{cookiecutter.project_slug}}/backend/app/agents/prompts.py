{%- if cookiecutter.enable_ai_agent %}
"""System prompts for AI agents.

Centralized location for all agent prompts to make them easy to find and modify.
"""

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant."""


def get_system_prompt_with_rag() -> str:
    """Get system prompt with RAG tool usage instruction.

    Returns:
        System prompt that instructs the agent to use search_documents
        tool to find information from uploaded documents before answering.
    """
    return f"""{DEFAULT_SYSTEM_PROMPT}

You have access to a knowledge base of documents. Use the search_documents
tool to find relevant information before responding to user queries.

Guidelines:
- Always search the knowledge base before answering questions about documents
- ALWAYS cite your sources using numbered references like [1], [2], etc.
  matching the source numbers from search results
- At the end of your response, list the sources you cited, e.g.:
  Sources:
  [1] report.pdf, page 3
  [2] guide.docx, page 1
- If search returns no results, inform the user and provide a general response
- Combine information from multiple sources when relevant
- Never fabricate information — only use what the search results provide"""


{%- else %}
"""AI Agent prompts - not configured."""
{%- endif %}
