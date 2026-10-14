from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from ai_engineer.applications.chatbot.backend.schemas.message import (
    CreateMessageRequest,
    CreateMessageResponse,
    MessageStatus,
)
from ai_engineer.frontend.applications.ai_chatbot.integrations.message.message_client import (
    MessageClient,
)
from ai_engineer.helpers.timestamp import create_int_timestamp


class MessageService:
    """
    Orchestrates message creation and retrieval for the chatbot UI.
    """

    def __init__(self, client=None) -> None:
        if client is None:
            client = MessageClient()

        self.client = client

    def create_message(
        self,
        conversation_id: uuid.UUID | str,
        content: str,
        *,
        space_id: Optional[str] = None,
        user_id: Optional[str] = None,
        message_url: Optional[str] = None,
        status: Optional[MessageStatus] = None,
        message_id: Optional[uuid.UUID] = None,
        created_timestamp: Optional[int] = None,
        created_at: Optional[date] = None,
    ) -> CreateMessageResponse:
        """
        Create a new message in the given conversation.

        Generates a message id and timestamp automatically when not provided,
        builds the backend request, and returns the created message.
        """
        request = CreateMessageRequest(
            id=message_id or uuid.uuid4(),
            conversation_id=conversation_id,
            content=content,
            space_id=space_id,
            user_id=user_id,
            message_url=message_url,
            status=status,
            created_timestamp=created_timestamp or create_int_timestamp(),
            created_at=created_at or date.today(),
        )
        return self.client.create_message(request)