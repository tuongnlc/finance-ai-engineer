from __future__ import annotations

import requests
from uuid import UUID
from ai_engineer.frontend.config import get_backend_base_url
from ai_engineer.applications.chatbot.backend.schemas.conversation import (
    CreateConversationRequest,
    CreateConversationResponse,
    GetConversationResponse,
)


class ConversationClient:
    """
        Client for Conversation API

        Create conversation when user starts a new conversation
    """

    def __init__(self, base_url: str | None = None, timeout: int = 30) -> None:
        self.base_url = (base_url or get_backend_base_url()).rstrip("/")
        self.timeout = timeout

    def create_conversation(
        self, request: CreateConversationRequest
    ) -> CreateConversationResponse:
        body = request.model_dump(mode="json")

        response = requests.post(
            f"{self.base_url}/conversation/create_conversation",
            headers={
                "accept": "*/*",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return CreateConversationResponse.model_validate(response.json())

    def get_conversation_by_id(
        self, conversation_id: UUID | str
    ) -> GetConversationResponse:
        response = requests.get(
            f"{self.base_url}/conversation/conversation/{conversation_id}",
            headers={
                "accept": "*/*",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return GetConversationResponse.model_validate(response.json())
