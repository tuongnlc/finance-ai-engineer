import uuid
from ai_engineer.applications.chatbot.domain.repositories.message import MessageRepository
from ai_engineer.applications.chatbot.domain.models.message import Message
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
            content_type = request.content_type,
            message_url = request.message_url,
            status = 'PENDING',
            content = request.content,
            attachments = request.attachments,
            created_at = date.today(),

        )
        return await self._message_repository.create(message)

    async def get_by_id(self, message_id: uuid.UUID) -> Message:
        return await self._message_repository.get_by_id(message_id)

    async def get_messages_by_conversation_id(self, conversation_id: uuid.UUID) -> list[Message]:
        return await self._message_repository.get_messages_by_conversation_id(str(conversation_id))
