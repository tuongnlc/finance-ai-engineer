from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ai_engineer.applications.chatbot.domain.models.message import Message
from ai_engineer.infrastructure.database.orm_models.message import MessageORM



class PostgresMessageRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, message: Message) -> Message:
        message_orm = self._to_orm(message)
        self._session.add(message_orm)
        # await self._session.commit()
        await self._session.flush()
        await self._session.refresh(message_orm)
        return self._to_domain(message_orm)

    async def get_by_id(self, conversation_id: str) -> Message | None:
        result = await self._session.execute(
            select(MessageORM).where(MessageORM.id == conversation_id)
        )
        message_orm = result.scalar_one_or_none()
        if message_orm is None:
            return None
        return self._to_domain(message_orm)

    def _to_orm(self, message: Message) -> MessageORM:
        return MessageORM(
            id=message.id,
            space_id=message.space_id,
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            created_timestamp=message.created_timestamp,
            content_type=message.content_type,
            message_url=message.message_url,
            status=message.status,
            content=message.content,
            attachments=message.attachments,
            created_at=message.created_at,
        )

    def _to_domain(self, message: MessageORM) -> Message:
        return Message(
            id=message.id,
            space_id=message.space_id,
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            created_timestamp=message.created_timestamp,
            content_type=message.content_type,
            message_url=message.message_url,
            status=message.status,
            created_at=message.created_at,
            content=message.content,
            attachments=message.attachments,
        )
