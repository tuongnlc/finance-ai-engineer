from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.applications.chatbot.domain.models.chat import Conversation
from src.infrastructure.database.models.conversation import ConversationORM


class PostgresConversationRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, conversation: Conversation) -> Conversation:
        conversation_orm = self._to_orm(conversation)
        await self._session.add(conversation_orm)
        # await self._session.commit()
        await self._session.flush()
        await self._session.refresh(conversation_orm)
        return self._to_domain(conversation_orm)

    async def get_by_id(self, conversation_id: str) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationORM).where(ConversationORM.id == conversation_id)
        )
        return self._to_domain(result.scalar_one_or_none())

    async def _to_orm(self, conversation: Conversation) -> ConversationORM:
        return ConversationORM(
            id=conversation.id,
            space_id=conversation.space_id,
            user_id=conversation.user_id,
            created_timestamp=conversation.created_timestamp,
            status=conversation.status,
        )

    async def _to_domain(self, conversation: ConversationORM) -> Conversation:
        return Conversation(
            id=conversation.id,
            space_id=conversation.space_id,
            user_id=conversation.user_id,
            created_timestamp=conversation.created_timestamp,
            status=conversation.status,
        )