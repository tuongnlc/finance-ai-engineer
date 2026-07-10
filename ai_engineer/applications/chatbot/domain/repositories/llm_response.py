from typing import Protocol
import uuid

from ai_engineer.applications.chatbot.domain.models.llm_response import LLMResponse


class LLMResponseRepository(Protocol):
    async def create(self, response: LLMResponse) -> LLMResponse:
        pass

    async def get_by_id(self, message_id: uuid.UUID) -> LLMResponse | None:
        pass

    async def get_responses_by_conversation_id(
        self, conversation_id: uuid.UUID
    ) -> list[LLMResponse]:
        pass
