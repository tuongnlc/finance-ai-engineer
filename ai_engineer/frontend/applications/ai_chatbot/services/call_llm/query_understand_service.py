from __future__ import annotations

import uuid
from typing import Optional

from ai_engineer.applications.chatbot.backend.schemas.llm_caller import (
    LLMCallerRequest,
    LLMCallerResponse,
)
from ai_engineer.frontend.applications.ai_chatbot.integrations.call_llm.query_understand_client import (
    QueryUnderstandClient,
)


class QueryUnderstandService:
    """
        When a user send a message in chatbot UI. The first step is query understand
    """

    def __init__(self, client=None) -> None:
        if client is None:
            client = QueryUnderstandClient()

        self.client = client

    def query_understand(
        self,
        content: str,
        *,
        question_context: Optional[str] = None,
        request_id: Optional[uuid.UUID] = None,
    ) -> LLMCallerResponse:
        """
        Run query understanding for a user message.

        Generates a request id automatically when not provided, builds the
        backend request, and returns the query understanding response.
        """
        request = LLMCallerRequest(
            id=request_id or uuid.uuid4(),
            content=content,
            question_context=question_context,
        )
        return self.client.query_understand(request)
