from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Optional

from ai_engineer.applications.chatbot.backend.schemas.llm_response import (
    LLMResponseRequest,
    LLMResponseResponse,
)
from ai_engineer.frontend.applications.ai_chatbot.integrations.response.llm_response_client import (
    LLMResponseClient,
)


class LLMResponseService:
    """
    Orchestrates llm response creation and retrieval for the chatbot UI.
    """

    def __init__(self, client=None) -> None:
        if client is None:
            client = LLMResponseClient()

        self.client = client

    def create_llm_response(
        self,
        message_id: uuid.UUID | str,
        conversation_id: uuid.UUID | str,
        llm_response: str,
        *,
        content_type: str = "text",
        attachments: Optional[list[dict[str, Any]]] = None,
        llm_response_id: Optional[uuid.UUID] = None,
        created_at: Optional[date] = None,
    ) -> LLMResponseResponse:
        """
        Create a new llm response for the given message and conversation.

        Generates an id and created_at automatically when not provided,
        builds the backend request, and returns the created llm response.
        """
        request = LLMResponseRequest(
            id=llm_response_id or uuid.uuid4(),
            message_id=message_id,
            conversation_id=conversation_id,
            llm_response=llm_response,
            content_type=content_type,
            attachments=attachments,
            created_at=created_at or date.today(),
        )
        return self.client.create_llm_response(request)
