from typing import Protocol
import uuid

from ai_engineer.applications.chatbot.domain.models.message import Message


class MessageRepository(Protocol):
    async def create(self, message: Message) -> Message:
        pass

    async def get_by_id(self, message_id: uuid.UUID) -> Message:
        pass

    async def update(self, message: Message) -> Message:
        pass

    async def delete(self, conversation_id: uuid.UUID) -> None:
        pass

    async def get_messages_by_conversation_id(self, conversation_id: uuid.UUID) -> list[Message]:
        pass