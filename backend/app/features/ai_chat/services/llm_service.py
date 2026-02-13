"""
LLM Service — orchestrates the RAG pipeline with LangChain + Anthropic Claude.
Supports both synchronous responses and async streaming.
"""

import logging
from collections.abc import AsyncGenerator

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.config import settings
from app.features.ai_chat.services.prompt_templates import SYSTEM_PROMPT
from app.features.ai_chat.services.rag_service import retrieve_context

logger = logging.getLogger(__name__)


def _get_llm() -> ChatAnthropic:
    return ChatAnthropic(
        model=settings.llm_model,
        api_key=settings.anthropic_api_key,
        max_tokens=1024,
        temperature=0.3,
    )


def _build_messages(
    user_message: str,
    context: str,
    chat_history: list[dict] | None = None,
) -> list:
    """Build the message list for the LLM call."""
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(context=context))]

    if chat_history:
        for msg in chat_history[-10:]:  # Keep last 10 messages for context window
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_message))
    return messages


async def generate_response(
    user_message: str,
    chat_history: list[dict] | None = None,
) -> str:
    """Generate a complete response using RAG pipeline."""
    context = retrieve_context(user_message)
    messages = _build_messages(user_message, context, chat_history)

    llm = _get_llm()
    response = await llm.ainvoke(messages)
    return response.content


async def stream_response(
    user_message: str,
    chat_history: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream response tokens using RAG pipeline."""
    context = retrieve_context(user_message)
    messages = _build_messages(user_message, context, chat_history)

    llm = _get_llm()
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
