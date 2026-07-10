import uuid

from ai_engineer.applications.chatbot.domain.models.llm_response import LLMResponse
from ai_engineer.applications.chatbot.domain.repositories.llm_response import LLMResponseRepository


class LLMResponseService:
    def __init__(self, message_repository: LLMResponseRepository):
        self._message_repository = message_repository

    async def create(self, request) -> LLMResponse:
        llm_response = LLMResponse(
            id = request.id,
            message_id = request.message_id,
            conversation_id = request.conversation_id,
            llm_response = request.llm_response,
            content_type = request.content_type,
            attachments = request.attachments,
            created_at = request.created_at,
        )
        return await self._message_repository.create(llm_response)

    async def get_by_id(self, message_id: uuid.UUID) -> LLMResponse:
        return await self._message_repository.get_by_id(message_id)

    async def get_responses_by_conversation_id(self, conversation_id: uuid.UUID) -> list[LLMResponse]:
        return await self._message_repository.get_responses_by_conversation_id(conversation_id)
