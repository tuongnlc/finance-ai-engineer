from __future__ import annotations

import requests
from ai_engineer.frontend.config import get_backend_base_url
from ai_engineer.applications.chatbot.backend.schemas.llm_response import (
    LLMResponseRequest,
    LLMResponseResponse,
)


class LLMResponseClient:
    """
        Client for LLM Response API

        Create llm response after the model returns an answer
    """

    def __init__(self, base_url: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or get_backend_base_url()).rstrip("/")
        self.timeout = timeout

    def create_llm_response(
        self, request: LLMResponseRequest
    ) -> LLMResponseResponse:
        body = request.model_dump(mode="json")

        response = requests.post(
            f"{self.base_url}/llm_response/create_llm_response",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return LLMResponseResponse.model_validate(response.json())
