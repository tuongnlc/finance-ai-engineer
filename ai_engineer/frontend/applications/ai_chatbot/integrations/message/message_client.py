from __future__ import annotations

import requests
from uuid import UUID
from ai_engineer.frontend.config import get_backend_base_url
from ai_engineer.applications.chatbot.backend.schemas.message import (
    CreateMessageRequest,
    CreateMessageResponse,
 )


class MessageClient:
    """
        Client for Message API

        Create message when user sends a new message
    """
    def __init__(self, base_url: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or get_backend_base_url()).rstrip("/")
        self.timeout = timeout

    def create_message(
        self, request: CreateMessageRequest
    ) -> CreateMessageResponse:
        body = request.model_dump(mode="json")

        response = requests.post(
            f"{self.base_url}/message",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return CreateMessageResponse.model_validate(response.json())
