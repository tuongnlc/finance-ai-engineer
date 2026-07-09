from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai_engineer.applications.chatbot.app.conversation_service import ConversationService
from ai_engineer.infrastructure.database.repositories.conversation import PostgresConversationRepository
from ai_engineer.infrastructure.database.session import get_session


def get_conversation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationService:
    conversation_repository = PostgresConversationRepository(session)
    return ConversationService(conversation_repository)
