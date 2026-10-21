from __future__ import annotations

import requests
from ai_engineer.frontend.config import get_backend_base_url
from ai_engineer.applications.chatbot.backend.schemas.llm_caller import (
    LLMCallerRequest,
    LLMCallerResponse,
)


class QueryUnderstandClient:
    """
        When a user send a message in chatbot UI. The first step is query understand
    """

    def __init__(self, base_url: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or get_backend_base_url()).rstrip("/")
        self.timeout = timeout

    def query_understand(
        self, request: LLMCallerRequest
    ) -> LLMCallerResponse:
        body = request.model_dump(mode="json")

        response = requests.post(
            f"{self.base_url}/call_llm/query_understand/",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return LLMCallerResponse.model_validate(response.json())
