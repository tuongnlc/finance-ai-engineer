import uuid
from src.applications.chatbot.domain.repositories.conversation import ConversationRepository
from src.applications.chatbot.domain.models.chat import Conversation
from datetime import date


class ConversationService:
    def __init__(self, conversation_repository: ConversationRepository):
        self._conversation_repository = conversation_repository

    async def create_conversation(self, request) -> Conversation:
        conversation = Conversation(
            id = request.id,
            space_id = request.space_id,
            user_id = request.user_id,
            created_timestamp = request.created_timestamp,
            status = 'PENDING',
            created_at = date.today(),
        )
        return await self._conversation_repository.create(conversation)

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation:
        return await self._conversation_repository.get_by_id(conversation_id)