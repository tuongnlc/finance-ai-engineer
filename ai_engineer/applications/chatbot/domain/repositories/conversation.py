from typing import Protocol
import uuid

from ai_engineer.applications.chatbot.domain.models.chat import Conversation


class ConversationRepository(Protocol):
    async def create(self, conversation: Conversation) -> Conversation:
        pass

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation:
        pass

    async def update(self, conversation: Conversation) -> Conversation:
        pass

    async def delete(self, conversation_id: uuid.UUID) -> None:
        pass
