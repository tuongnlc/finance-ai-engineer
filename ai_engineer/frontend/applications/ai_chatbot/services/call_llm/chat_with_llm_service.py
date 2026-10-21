from __future__ import annotations

import uuid
from typing import Optional

from ai_engineer.applications.chatbot.backend.schemas.llm_caller import (
    LLMCallerRequest,
    LLMCallerResponse,
)
from ai_engineer.frontend.applications.ai_chatbot.integrations.call_llm.chat_with_llm_client import (
    ChatWithLLMClient,
)


class ChatWithLLMService:
    """
    Orchestrates the chat-with-LLM step for the chatbot UI.
    """

    def __init__(self, client=None) -> None:
        if client is None:
            client = ChatWithLLMClient()

        self.client = client

    def chat_with_llm(
        self,
        content: str,
        *,
        question_context: Optional[str] = None,
        request_id: Optional[uuid.UUID] = None,
    ) -> LLMCallerResponse:
        """
        Send a user message to the LLM and return its response.

        Generates a request id automatically when not provided, builds the
        backend request, and returns the chat response.
        """
        request = LLMCallerRequest(
            id=request_id or uuid.uuid4(),
            content=content,
            question_context=question_context,
        )
        return self.client.chat_with_llm(request)
