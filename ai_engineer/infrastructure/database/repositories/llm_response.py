import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engineer.applications.chatbot.domain.models.llm_response import LLMResponse
from ai_engineer.infrastructure.database.orm_models.llm_response import LLMResponseORM



class PostgresLLMResponseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, response: LLMResponse) -> LLMResponse:
        response_orm = self._to_orm(response)
        self._session.add(response_orm)
        # await self._session.commit()
        await self._session.flush()
        await self._session.refresh(response_orm)
        return self._to_domain(response_orm)

    async def get_by_id(self, response_id: str) -> LLMResponse | None:
        result = await self._session.execute(
            select(LLMResponseORM).where(LLMResponseORM.id == response_id)
        )
        response_orm = result.scalar_one_or_none()
        if response_orm is None:
            return None
        return self._to_domain(response_orm)

    async def get_responses_by_conversation_id(self, conversation_id: str) -> list[LLMResponse]:
        result = await self._session.execute(
            select(LLMResponseORM).where(LLMResponseORM.conversation_id == conversation_id)
        )
        response_orms = result.scalars().all()
        return [self._to_domain(response_orm) for response_orm in response_orms]

    def _to_orm(self, response: LLMResponse) -> LLMResponseORM:
        return LLMResponseORM(
            id=response.id,
            message_id=response.message_id,
            conversation_id=response.conversation_id,
            llm_response=response.llm_response,
            content_type=response.content_type,
            attachments=self._serialize_attachments(response.attachments),
            created_at=response.created_at,
        )

    def _to_domain(self, response: LLMResponseORM) -> LLMResponse:
        return LLMResponse(
            id=response.id,
            message_id=response.message_id,
            conversation_id=response.conversation_id,
            llm_response=response.llm_response,
            content_type=response.content_type,
            attachments=self._deserialize_attachments(response.attachments),
            created_at=response.created_at,
        )

    @staticmethod
    def _serialize_attachments(attachments: list[dict] | None) -> str | None:
        if attachments is None:
            return None
        return json.dumps(attachments)

    @staticmethod
    def _deserialize_attachments(attachments: str | None) -> list[dict] | None:
        if not attachments:
            return None
        return json.loads(attachments)
