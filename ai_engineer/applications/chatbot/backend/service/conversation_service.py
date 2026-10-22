import uuid
from typing import Optional
from ai_engineer.applications.chatbot.backend.domain.repositories.conversation import ConversationRepository
from ai_engineer.applications.chatbot.backend.domain.models.conversation import Conversation
from datetime import date


class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    async def create_conversation(self, request) -> Conversation:
        conversation = Conversation(
            id = request.id,
            session_id = request.session_id,
            title = request.title,
            space_id = request.space_id,
            user_id = request.user_id,
            created_timestamp = request.created_timestamp,
            status = 'PENDING',
            created_at = date.today(),
        )
        return await self._conversation_repository.create(conversation)

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation:
        return await self._conversation_repository.get_by_id(conversation_id)

    async def list_conversations(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Conversation]:
        return await self._conversation_repository.list(
            user_id=user_id,
            status=status,
        )
