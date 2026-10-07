from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ai_engineer.applications.chatbot.domain.models.session import Session
from ai_engineer.infrastructure.database.orm_models.session import SessionORM


class PostgresSessionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, session: Session) -> Session:
        session_orm = self._to_orm(session)
        self._session.add(session_orm)
        # await self._session.commit()
        await self._session.flush()
        await self._session.refresh(session_orm)
        return self._to_domain(session_orm)

    def _to_orm(self, session: Session) -> SessionORM:
        return SessionORM(
            id=session.id,
            conversation_id=session.conversation_id,
            created_timestamp=session.created_timestamp,
        )

    def _to_domain(self, session: SessionORM) -> Session:
        return Session(
            id=session.id,
            conversation_id=session.conversation_id,
            created_timestamp=session.created_timestamp,
        )
