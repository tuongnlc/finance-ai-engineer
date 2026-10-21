from __future__ import annotations

import uuid
from typing import Optional

from ai_engineer.applications.chatbot.backend.schemas.llm_caller import (
    ToolCallingRequest,
    ToolCallingResponse,
)
from ai_engineer.frontend.applications.ai_chatbot.integrations.call_llm.tool_calling import (
    ToolCallingClient,
)


class ToolCallingService:
    """
        When a user send a message in chatbot UI, the query is routed to the
        tool calling endpoint for stock chatbot.
    """

    def __init__(self, client=None) -> None:
        if client is None:
            client = ToolCallingClient()

        self.client = client

    def tool_calling(
        self,
        original_query: str,
        vietnamese_with_diacritics: str,
        question_type: str,
        main_topic: str,
        stock_id: str,
        target_year: str,
        document_type: str,
        optimized_search_query: str,
        *,
        request_id: Optional[uuid.UUID] = None,
    ) -> ToolCallingResponse:
        """
        Run tool calling for a user message.

        Generates a request id automatically when not provided, builds the
        backend request, and returns the tool calling response.
        """
        request = ToolCallingRequest(
            id=request_id or uuid.uuid4(),
            original_query=original_query,
            vietnamese_with_diacritics=vietnamese_with_diacritics,
            question_type=question_type,
            main_topic=main_topic,
            stock_id=stock_id,
            target_year=target_year,
            document_type=document_type,
            optimized_search_query=optimized_search_query,
        )
        return self.client.tool_calling(request)
