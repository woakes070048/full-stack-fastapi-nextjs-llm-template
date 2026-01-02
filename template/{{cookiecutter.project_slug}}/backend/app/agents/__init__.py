{%- if cookiecutter.enable_ai_agent and cookiecutter.use_pydantic_ai %}
"""AI Agents module using PydanticAI.

This module contains agents that handle AI-powered interactions.
Tools are defined in the tools/ subdirectory.
"""

from app.agents.assistant import AssistantAgent, Deps

__all__ = ["AssistantAgent", "Deps"]
{%- elif cookiecutter.enable_ai_agent and cookiecutter.use_langchain %}
"""AI Agents module using LangChain.

This module contains agents that handle AI-powered interactions.
Tools are defined in the tools/ subdirectory.
"""

from app.agents.langchain_assistant import AgentContext, AgentState, LangChainAssistant

__all__ = ["LangChainAssistant", "AgentContext", "AgentState"]
{%- elif cookiecutter.enable_ai_agent and cookiecutter.use_langgraph %}
"""AI Agents module using LangGraph.

This module contains a ReAct agent built with LangGraph.
Tools are defined in the tools/ subdirectory.
"""

from app.agents.langgraph_assistant import AgentContext, AgentState, LangGraphAssistant

__all__ = ["LangGraphAssistant", "AgentContext", "AgentState"]
{%- else %}
"""AI Agents - not configured."""
{%- endif %}
