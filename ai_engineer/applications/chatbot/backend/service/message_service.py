from typing import Optional
import uuid
from ai_engineer.applications.chatbot.backend.domain.repositories.message import MessageRepository
from ai_engineer.applications.chatbot.backend.domain.models.message import Message
from datetime import date


class MessageService:
    def __init__(self, message_repository: MessageRepository):
        self._message_repository = message_repository

    async def create_message(self, request) -> Message:
        message = Message(
            id = request.id,
            space_id = request.space_id,
            conversation_id = request.conversation_id,
            user_id = request.user_id,
            created_timestamp = request.created_timestamp,
            message_url = request.message_url,
            status = 'PENDING',
            content = request.content,
            created_at = date.today(),

        )
        return await self._message_repository.create(message)

    async def get_by_id(self, message_id: uuid.UUID) -> Message:
        return await self._message_repository.get_by_id(message_id)

    async def list_messages(
            self, 
            conversation_id: Optional[uuid.UUID] = None, 
            user_id: Optional[str] = None
        ) -> list[Message]:
        return await self._message_repository.list(
            conversation_id=conversation_id, 
            user_id=user_id
        )

